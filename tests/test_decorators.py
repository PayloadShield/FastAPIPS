"""
Tests for PayloadShield decorators and PayloadShieldEnc initialization.
"""

import base64
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_payloadshield import PayloadShield, PayloadShieldEnc

PayloadShieldEnc.init({"Key": "test-symmetric-key"})

app = FastAPI()


@app.get("/encrypt-only")
@PayloadShield.encrypt("base64")
async def encrypt_only():
    return {"message": "hello"}


@app.post("/decrypt-only")
@PayloadShield.decrypt("base64")
async def decrypt_only(data: dict):
    return {"received": data}


@app.post("/crypt")
@PayloadShield.crypt("base64")
async def crypt_both(data: dict):
    return {"echo": data}


client = TestClient(app)


def _b64_encode(payload: dict) -> str:
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


def _b64_decode(encoded: str) -> dict:
    return json.loads(base64.b64decode(encoded.encode("utf-8")).decode("utf-8"))


def test_encrypt_only_wraps_response():
    response = client.get("/encrypt-only")
    assert response.status_code == 200
    body = response.json()
    assert "encrypted" in body
    assert _b64_decode(body["encrypted"]) == {"message": "hello"}


def test_decrypt_only_reads_encrypted_request():
    payload = {"username": "admin", "password": "secret"}
    response = client.post("/decrypt-only", json={"encrypted": _b64_encode(payload)})
    assert response.status_code == 200
    assert response.json() == {"received": payload}


def test_crypt_round_trips_request_and_response():
    payload = {"name": "Alice"}
    response = client.post("/crypt", json={"encrypted": _b64_encode(payload)})
    assert response.status_code == 200
    body = response.json()
    assert "encrypted" in body
    assert _b64_decode(body["encrypted"]) == {"echo": payload}
