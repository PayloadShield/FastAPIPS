"""Tests for PayloadShieldEnc.init() key configuration resolution."""

import tempfile
from pathlib import Path

from fastapi_payloadshield import PayloadShieldEnc


def test_init_stores_symmetric_key():
    PayloadShieldEnc.init({"Key": "abc123"})
    assert PayloadShieldEnc.get_config()["Key"] == "abc123"


def test_init_accepts_raw_key_content():
    PayloadShieldEnc.init({"PrivateKey": "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----"})
    assert PayloadShieldEnc.get_config()["PrivateKey"].startswith("-----BEGIN PRIVATE KEY-----")


def test_init_accepts_key_file_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        key_path = Path(tmp_dir) / "public.pem"
        key_path.write_text("-----BEGIN PUBLIC KEY-----\nfake\n-----END PUBLIC KEY-----")

        PayloadShieldEnc.init({"PublicKey": str(key_path)})
        assert PayloadShieldEnc.get_config()["PublicKey"] == key_path.read_text()


def test_init_defaults_missing_keys_to_none():
    PayloadShieldEnc.init({})
    config = PayloadShieldEnc.get_config()
    assert config["Key"] is None
    assert config["PrivateKey"] is None
    assert config["PublicKey"] is None
