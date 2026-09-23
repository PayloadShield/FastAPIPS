"""
Client script that exercises every built-in encryption handler
("base64", "fernet", "aes-gcm-256", "rsa-hybrid") against a running
examples/example_app.py server and reports a pass/fail percentage.

For each crypt type, two checks are performed:
  1. Fixed-data check: call GET /api/{type}/fixed with a blank request and
     confirm the decrypted response matches the server's known FIXED_DATA.
  2. Echo check: encrypt a second, different payload, POST it to
     /api/{type}/echo, and confirm the decrypted response matches what
     was sent.

Run the server first:
    python examples/example_app.py
Then run this script:
    python examples/test_all_crypts.py
"""

import base64
import json
import sys
from pathlib import Path

import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Prefer the local, in-repo package/module over any older version pip-installed
# in site-packages when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE_URL = "http://localhost:8000"

# The known fixed payload returned by GET /api/{type}/fixed in example_app.py
FIXED_DATA = {"message": "fixed-payload", "value": 42}

# A different payload used to exercise the encrypt/decrypt round trip.
SECOND_DATA = {"user": "alice", "roles": ["admin", "editor"], "active": True}

CRYPT_TYPES = ["base64", "fernet", "aes-gcm-256", "rsa-hybrid"]


class ClientEncryptor:
    """Client-side encode/decode helpers mirroring the server's handlers.

    The client must independently be able to decrypt what the server sent
    and encrypt what it wants to send, so it holds its own copy of the
    shared keys. In a real deployment these keys would be distributed out
    of band (e.g. secrets manager); here we simply hard-code demo keys and
    print instructions to keep the server and client keys in sync.
    """

    def __init__(self, symmetric_key: str, public_pem: str = None, private_pem: str = None):
        self.symmetric_key = symmetric_key
        self.public_pem = public_pem
        self.private_pem = private_pem

    def encode(self, crypt_type: str, data: dict) -> str:
        payload = json.dumps(data).encode("utf-8")
        if crypt_type == "base64":
            return base64.b64encode(payload).decode("utf-8")
        if crypt_type == "fernet":
            return Fernet(self.symmetric_key.encode("utf-8")).encrypt(payload).decode("utf-8")
        if crypt_type == "aes-gcm-256":
            key = self._aes_key()
            nonce = __import__("os").urandom(12)
            ciphertext = AESGCM(key).encrypt(nonce, payload, None)
            return base64.b64encode(nonce + ciphertext).decode("utf-8")
        if crypt_type == "rsa-hybrid":
            public_key = serialization.load_pem_public_key(self.public_pem.encode("utf-8"))
            aes_key = __import__("os").urandom(32)
            nonce = __import__("os").urandom(12)
            ciphertext = AESGCM(aes_key).encrypt(nonce, payload, None)
            encrypted_key = public_key.encrypt(
                aes_key,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
            )
            bundle = {
                "key": base64.b64encode(encrypted_key).decode("utf-8"),
                "nonce": base64.b64encode(nonce).decode("utf-8"),
                "data": base64.b64encode(ciphertext).decode("utf-8"),
            }
            return base64.b64encode(json.dumps(bundle).encode("utf-8")).decode("utf-8")
        raise ValueError(f"Unknown crypt type: {crypt_type}")

    def decode(self, crypt_type: str, encoded: str) -> dict:
        if crypt_type == "base64":
            return json.loads(base64.b64decode(encoded.encode("utf-8")).decode("utf-8"))
        if crypt_type == "fernet":
            payload = Fernet(self.symmetric_key.encode("utf-8")).decrypt(encoded.encode("utf-8"))
            return json.loads(payload.decode("utf-8"))
        if crypt_type == "aes-gcm-256":
            key = self._aes_key()
            raw = base64.b64decode(encoded.encode("utf-8"))
            nonce, ciphertext = raw[:12], raw[12:]
            payload = AESGCM(key).decrypt(nonce, ciphertext, None)
            return json.loads(payload.decode("utf-8"))
        if crypt_type == "rsa-hybrid":
            private_key = serialization.load_pem_private_key(self.private_pem.encode("utf-8"), password=None)
            bundle = json.loads(base64.b64decode(encoded.encode("utf-8")))
            aes_key = private_key.decrypt(
                base64.b64decode(bundle["key"]),
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
            )
            payload = AESGCM(aes_key).decrypt(base64.b64decode(bundle["nonce"]), base64.b64decode(bundle["data"]), None)
            return json.loads(payload.decode("utf-8"))
        raise ValueError(f"Unknown crypt type: {crypt_type}")

    def _aes_key(self) -> bytes:
        key_bytes = self.symmetric_key.encode("utf-8")
        decoded = base64.b64decode(key_bytes)
        if len(decoded) == 32:
            return decoded
        raise ValueError("AES-256 key must resolve to exactly 32 bytes")


def run_checks(encryptor: ClientEncryptor) -> list:
    """Run the fixed-data and echo checks for every crypt type.

    Returns a list of (crypt_type, check_name, passed, detail) tuples.
    """
    results = []

    for crypt_type in CRYPT_TYPES:
        # Check 1: blank request -> server returns FIXED_DATA encrypted.
        try:
            response = requests.get(f"{BASE_URL}/api/{crypt_type}/fixed")
            response.raise_for_status()
            decrypted = encryptor.decode(crypt_type, response.json()["encrypted"])
            passed = decrypted == FIXED_DATA
            detail = "" if passed else f"expected {FIXED_DATA}, got {decrypted}"
        except Exception as exc:  # noqa: BLE001 - report failures, don't crash the run
            passed = False
            detail = str(exc)
        results.append((crypt_type, "fixed_data_match", passed, detail))

        # Check 2: encrypt SECOND_DATA, echo round trip, decrypt and compare.
        try:
            encrypted_request = encryptor.encode(crypt_type, SECOND_DATA)
            response = requests.post(
                f"{BASE_URL}/api/{crypt_type}/echo",
                json={"encrypted": encrypted_request},
            )
            response.raise_for_status()
            decrypted = encryptor.decode(crypt_type, response.json()["encrypted"])
            passed = decrypted == SECOND_DATA
            detail = "" if passed else f"expected {SECOND_DATA}, got {decrypted}"
        except Exception as exc:  # noqa: BLE001
            passed = False
            detail = str(exc)
        results.append((crypt_type, "echo_round_trip", passed, detail))

    return results


def print_report(results: list) -> None:
    total = len(results)
    passed_count = sum(1 for *_ , passed, _ in results if passed)
    failed_count = total - passed_count

    print("=" * 70)
    print("Crypt Type Test Report")
    print("=" * 70)
    for crypt_type, check_name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        line = f"[{status}] {crypt_type:<12} {check_name}"
        if detail:
            line += f" -- {detail}"
        print(line)

    percentage = (passed_count / total * 100) if total else 0.0
    print("-" * 70)
    print(f"Total checks: {total} | Passed: {passed_count} | Failed: {failed_count}")
    print(f"Pass rate: {percentage:.1f}%")
    print("=" * 70)


def main() -> None:
    # example_app.py hard-codes fixed demo keys precisely so that this
    # script (running in a separate process) can decrypt/encrypt using the
    # exact same keys as the server, without importing/re-running the app.
    from example_app import _SYMMETRIC_KEY, _RSA_PUBLIC_PEM, _RSA_PRIVATE_PEM

    encryptor = ClientEncryptor(
        symmetric_key=_SYMMETRIC_KEY,
        public_pem=_RSA_PUBLIC_PEM,
        private_pem=_RSA_PRIVATE_PEM,
    )

    try:
        results = run_checks(encryptor)
    except requests.exceptions.ConnectionError:
        print("Error: could not connect to server at", BASE_URL)
        print("Make sure the server is running: python examples/example_app.py")
        return

    print_report(results)


if __name__ == "__main__":
    main()
