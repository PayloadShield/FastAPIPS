"""
Example FastAPI application demonstrating every PayloadShield encryption
handler. Also used as a fixture by the automated test suite
(tests/test_all_crypts.py).

Run the server:
    python -m uvicorn main:app --reload

Test with Postman:
    1. Start the server (command above), then open Postman.
    2. Set the base URL to http://127.0.0.1:8000.
    3. On startup this module prints one block per handler with the exact
       GET/POST URLs and a ready-to-paste JSON body - copy those straight
       into a Postman request (Body -> raw -> JSON).
    4. GET routes (e.g. /aes) need no body and return {"encrypted": "..."}.
       POST .../dec and .../cry routes expect {"encrypted": "..."} as the
       raw JSON body; .../cry additionally returns an encrypted response.
"""

import json
from pathlib import Path

from fastapi import FastAPI
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, x25519

from fastapi_payloadshield import PayloadShield, PayloadShieldEnc, get_handler

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0",
)

SYMMETRIC_KEY = "12345678901234567890123456789012"  # 32 bytes

# Maps each handler name to the route prefix registered below, and doubles
# as the canonical list of every built-in encryption type.
ROUTE_PREFIX = {
    "base64": "base",
    "fernet": "fernet",
    "aes-gcm-256": "aes",
    "chacha20-poly1305": "chacha",
    "rsa-hybrid": "rsa",
    "ecdh-aes-gcm": "ecdh",
    "ecies": "ecies",
    "hpke": "hpke",
}
ALL_CRYPT_TYPES = list(ROUTE_PREFIX.keys())


# ----------------------------------------------------------------------------
# Generate (or reuse) the PEM key pairs each asymmetric handler needs.
# ----------------------------------------------------------------------------
def _write_pem_pair_if_missing(private_path: Path, public_path: Path, private_key) -> None:
    """Persist a freshly generated key pair to disk unless both files already exist."""
    if private_path.exists() and public_path.exists():
        return

    private_path.write_text(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")
    )
    public_path.write_text(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")
    )


RSA_PRIVATE_PEM_PATH = BASE_DIR / "private.pem"
RSA_PUBLIC_PEM_PATH = BASE_DIR / "public.pem"
EC_PRIVATE_PEM_PATH = BASE_DIR / "ec_private.pem"
EC_PUBLIC_PEM_PATH = BASE_DIR / "ec_public.pem"
HPKE_PRIVATE_PEM_PATH = BASE_DIR / "hpke_private.pem"
HPKE_PUBLIC_PEM_PATH = BASE_DIR / "hpke_public.pem"

_write_pem_pair_if_missing(
    RSA_PRIVATE_PEM_PATH, RSA_PUBLIC_PEM_PATH,
    rsa.generate_private_key(public_exponent=65537, key_size=2048),
)
_write_pem_pair_if_missing(
    EC_PRIVATE_PEM_PATH, EC_PUBLIC_PEM_PATH,
    ec.generate_private_key(ec.SECP256R1()),
)
_write_pem_pair_if_missing(
    HPKE_PRIVATE_PEM_PATH, HPKE_PUBLIC_PEM_PATH,
    x25519.X25519PrivateKey.generate(),
)

PayloadShieldEnc.init({
    "Key": SYMMETRIC_KEY,                          # fernet, aes-gcm-256, chacha20-poly1305
    "PrivateKey": str(RSA_PRIVATE_PEM_PATH),       # rsa-hybrid (decrypt)
    "PublicKey": str(RSA_PUBLIC_PEM_PATH),         # rsa-hybrid (encrypt)
    "ECPrivateKey": str(EC_PRIVATE_PEM_PATH),      # ecdh-aes-gcm, ecies (decrypt)
    "ECPublicKey": str(EC_PUBLIC_PEM_PATH),        # ecdh-aes-gcm, ecies (encrypt)
    "HPKEPrivateKey": str(HPKE_PRIVATE_PEM_PATH),  # hpke (decrypt)
    "HPKEPublicKey": str(HPKE_PUBLIC_PEM_PATH),    # hpke (encrypt)
})

@app.get("/base")
@PayloadShield.encrypt("base64")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/base/dec")
@PayloadShield.decrypt("base64")
def decrypt_payload(data: dict):
    return data

@app.post("/base/cry")
@PayloadShield.crypt("base64")
def decrypt_payload(data: dict):
    return data


@app.get("/aes")
@PayloadShield.encrypt("aes-gcm-256")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/aes/dec")
@PayloadShield.decrypt("aes-gcm-256")
def decrypt_payload(data: dict):
    return data

@app.post("/aes/cry")
@PayloadShield.crypt("aes-gcm-256")
def decrypt_payload(data: dict):
    return data


@app.get("/fernet")
@PayloadShield.encrypt("fernet")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/fernet/dec")
@PayloadShield.decrypt("fernet")
def decrypt_payload(data: dict):
    return data

@app.post("/fernet/cry")
@PayloadShield.crypt("fernet")
def decrypt_payload(data: dict):
    return data

@app.get("/rsa")
@PayloadShield.encrypt("rsa-hybrid")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/rsa/dec")
@PayloadShield.decrypt("rsa-hybrid")
def decrypt_payload(data: dict):
    return data

@app.post("/rsa/cry")
@PayloadShield.crypt("rsa-hybrid")
def decrypt_payload(data: dict):
    return data

@app.get("/chacha")
@PayloadShield.encrypt("chacha20-poly1305")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/chacha/dec")
@PayloadShield.decrypt("chacha20-poly1305")
def decrypt_payload(data: dict):
    return data

@app.post("/chacha/cry")
@PayloadShield.crypt("chacha20-poly1305")
def decrypt_payload(data: dict):
    return data

@app.get("/ecdh")
@PayloadShield.encrypt("ecdh-aes-gcm")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/ecdh/dec")
@PayloadShield.decrypt("ecdh-aes-gcm")
def decrypt_payload(data: dict):
    return data

@app.post("/ecdh/cry")
@PayloadShield.crypt("ecdh-aes-gcm")
def decrypt_payload(data: dict):
    return data

@app.get("/ecies")
@PayloadShield.encrypt("ecies")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/ecies/dec")
@PayloadShield.decrypt("ecies")
def decrypt_payload(data: dict):
    return data

@app.post("/ecies/cry")
@PayloadShield.crypt("ecies")
def decrypt_payload(data: dict):
    return data

@app.get("/hpke")
@PayloadShield.encrypt("hpke")
def root():
    return {
        "message": "Hello, PayloadShield!"
    }

@app.post("/hpke/dec")
@PayloadShield.decrypt("hpke")
def decrypt_payload(data: dict):
    return data

@app.post("/hpke/cry")
@PayloadShield.crypt("hpke")
def decrypt_payload(data: dict):
    return data

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ----------------------------------------------------------------------------
# Postman quick-start: print a ready-to-paste request per handler on startup.
# ----------------------------------------------------------------------------
def _print_postman_examples() -> None:
    sample_payload = {"message": "hello", "id": 1}
    config = PayloadShieldEnc.get_config()

    print("\n" + "=" * 70)
    print("Postman quick start - base URL http://127.0.0.1:8000")
    print("=" * 70)
    for crypt_type in ALL_CRYPT_TYPES:
        prefix = ROUTE_PREFIX[crypt_type]
        encrypted = get_handler(crypt_type).encode(sample_payload, config)
        body = json.dumps({"encrypted": encrypted})

        print(f"\n[{crypt_type}]")
        print(f"  GET  /{prefix}            -> {{\"encrypted\": \"...\"}}")
        print(f"  POST /{prefix}/dec  body: {body}")
        print(f"  POST /{prefix}/cry  body: {body}")
    print("\n" + "=" * 70 + "\n")


_print_postman_examples()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)