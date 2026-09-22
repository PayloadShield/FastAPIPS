"""
Tests for encryption handlers: base64, fernet, aes-gcm-256, rsa-hybrid.
"""

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from fastapi_payloadshield import (
    Base64EncryptionHandler,
    FernetEncryptionHandler,
    AESGCM256EncryptionHandler,
    HybridRSAEncryptionHandler,
)

SAMPLE_DATA = {"message": "hello", "count": 3, "nested": {"a": 1}}


def test_base64_roundtrip():
    handler = Base64EncryptionHandler()
    encoded = handler.encode(SAMPLE_DATA, config={})
    assert handler.decode(encoded, config={}) == SAMPLE_DATA


def test_base64_invalid_data_raises():
    handler = Base64EncryptionHandler()
    with pytest.raises(ValueError):
        handler.decode("not-valid-base64!!", config={})


def test_fernet_roundtrip():
    handler = FernetEncryptionHandler()
    key = Fernet.generate_key().decode("utf-8")
    config = {"Key": key}
    encoded = handler.encode(SAMPLE_DATA, config)
    assert handler.decode(encoded, config) == SAMPLE_DATA


def test_fernet_missing_key_raises():
    handler = FernetEncryptionHandler()
    with pytest.raises(ValueError):
        handler.encode(SAMPLE_DATA, config={})


def test_aes_gcm_256_roundtrip():
    handler = AESGCM256EncryptionHandler()
    config = {"Key": "0123456789abcdef0123456789abcdef"}  # 32 bytes
    encoded = handler.encode(SAMPLE_DATA, config)
    assert handler.decode(encoded, config) == SAMPLE_DATA


def test_aes_gcm_256_invalid_key_length_raises():
    handler = AESGCM256EncryptionHandler()
    with pytest.raises(ValueError):
        handler.encode(SAMPLE_DATA, config={"Key": "too-short"})


def test_rsa_hybrid_roundtrip():
    handler = HybridRSAEncryptionHandler()

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    encode_config = {"PublicKey": public_pem}
    decode_config = {"PrivateKey": private_pem}

    encoded = handler.encode(SAMPLE_DATA, encode_config)
    assert handler.decode(encoded, decode_config) == SAMPLE_DATA
