"""
Automated pass/fail report across every built-in encryption handler.

For each crypt type ("base64", "fernet", "aes-gcm-256", "rsa-hybrid"):
  1. Fixed-data check: GET /api/{type}/fixed with a blank request and
     confirm the decrypted response matches the server's known FIXED_DATA.
  2. Echo check: encrypt a second, different payload, POST it to
     /api/{type}/echo, and confirm the decrypted response matches what
     was sent.

Prints a pass/fail percentage summary and asserts a 100% pass rate.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from example_app import (  # noqa: E402
    ALL_CRYPT_TYPES,
    FIXED_DATA,
    _RSA_PRIVATE_PEM,
    _RSA_PUBLIC_PEM,
    _SYMMETRIC_KEY,
    app,
)
from fastapi_payloadshield import get_handler  # noqa: E402
from fastapi_payloadshield import PayloadShieldEnc  # noqa: E402

SECOND_DATA = {"user": "alice", "roles": ["admin", "editor"], "active": True}

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_global_key_config():
    """
    PayloadShieldEnc holds process-wide state, and other test modules call
    PayloadShieldEnc.init(...) at import time. Re-apply this module's keys
    before every test so route handlers (which read the global config) stay
    in sync with the config used to encrypt/decrypt in the test itself.
    """
    PayloadShieldEnc.init({
        "Key": _SYMMETRIC_KEY,
        "PublicKey": _RSA_PUBLIC_PEM,
        "PrivateKey": _RSA_PRIVATE_PEM,
    })
    yield


def _config_for(crypt_type: str) -> dict:
    return {
        "Key": _SYMMETRIC_KEY,
        "PublicKey": _RSA_PUBLIC_PEM,
        "PrivateKey": _RSA_PRIVATE_PEM,
    }


def _run_all_checks() -> list:
    """Returns a list of (crypt_type, check_name, passed, detail) tuples."""
    results = []

    for crypt_type in ALL_CRYPT_TYPES:
        handler = get_handler(crypt_type)
        config = _config_for(crypt_type)

        # Check 1: blank request -> server returns FIXED_DATA encrypted.
        try:
            response = client.get(f"/api/{crypt_type}/fixed")
            decrypted = handler.decode(response.json()["encrypted"], config)
            passed = decrypted == FIXED_DATA
            detail = "" if passed else f"expected {FIXED_DATA}, got {decrypted}"
        except Exception as exc:  # noqa: BLE001 - capture failure, keep going
            passed = False
            detail = str(exc)
        results.append((crypt_type, "fixed_data_match", passed, detail))

        # Check 2: encrypt SECOND_DATA, echo round trip, decrypt and compare.
        try:
            encrypted_request = handler.encode(SECOND_DATA, config)
            response = client.post(
                f"/api/{crypt_type}/echo",
                json={"encrypted": encrypted_request},
            )
            decrypted = handler.decode(response.json()["encrypted"], config)
            passed = decrypted == SECOND_DATA
            detail = "" if passed else f"expected {SECOND_DATA}, got {decrypted}"
        except Exception as exc:  # noqa: BLE001
            passed = False
            detail = str(exc)
        results.append((crypt_type, "echo_round_trip", passed, detail))

    return results


def _print_report(results: list) -> float:
    total = len(results)
    passed_count = sum(1 for *_, passed, _ in results if passed)

    print("\n" + "=" * 70)
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
    print(f"Total checks: {total} | Passed: {passed_count} | Failed: {total - passed_count}")
    print(f"Pass rate: {percentage:.1f}%")
    print("=" * 70)
    return percentage


def test_all_crypt_types_pass_rate():
    results = _run_all_checks()
    percentage = _print_report(results)
    failures = [r for r in results if not r[2]]
    assert not failures, f"{len(failures)} check(s) failed: {failures}"
    assert percentage == 100.0


@pytest.mark.parametrize("crypt_type", ["base64", "fernet", "aes-gcm-256", "rsa-hybrid"])
def test_fixed_data_matches_for_each_crypt_type(crypt_type):
    handler = get_handler(crypt_type)
    config = _config_for(crypt_type)
    response = client.get(f"/api/{crypt_type}/fixed")
    assert response.status_code == 200
    decrypted = handler.decode(response.json()["encrypted"], config)
    assert decrypted == FIXED_DATA


@pytest.mark.parametrize("crypt_type", ["base64", "fernet", "aes-gcm-256", "rsa-hybrid"])
def test_echo_round_trip_for_each_crypt_type(crypt_type):
    handler = get_handler(crypt_type)
    config = _config_for(crypt_type)
    encrypted_request = handler.encode(SECOND_DATA, config)
    response = client.post(f"/api/{crypt_type}/echo", json={"encrypted": encrypted_request})
    assert response.status_code == 200
    decrypted = handler.decode(response.json()["encrypted"], config)
    assert decrypted == SECOND_DATA
