# FastAPI Payload Shield

Pluggable FastAPI decorators for encrypting and decrypting request and
response payloads. Configure your keys once, then annotate any route with
`@PayloadShield.encrypt`, `@PayloadShield.decrypt`, or `@PayloadShield.crypt`.

> **Breaking change (v3.0.0)**: the old `encrypt_response` /
> `decrypt_request` / `crypto_middleware` decorators and the old
> `PayloadShieldEnc("base64")` factory function have been removed. There is
> no backward-compatible alias — see [Migrating to v3](#migrating-to-v3)
> below.

## Key Features

- **Pluggable encryption**: base64, Fernet, AES-GCM-256, and Hybrid RSA+AES
  ship out of the box; register your own with `register_handler(...)`.
- **One-time key configuration**: `PayloadShieldEnc.init({...})` sets keys
  globally for all decorators.
- **Route-agnostic**: no changes needed to your route logic besides adding a
  decorator.
- **Async-friendly**: works with FastAPI's async route handlers.

## Installation

```bash
pip install fastapi_payloadshield
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_payloadshield import PayloadShield, PayloadShieldEnc

# Configure encryption keys once, at startup.
PayloadShieldEnc.init({
    "Key": "my-symmetric-key",
})

app = FastAPI()

@app.get("/api/data")
@PayloadShield.encrypt("base64")
async def get_data():
    return {"message": "hello", "data": "world"}

@app.post("/api/process")
@PayloadShield.decrypt("base64")
async def process_data(data: dict):
    return {"received": data, "status": "success"}

@app.post("/api/secure")
@PayloadShield.crypt("base64")
async def secure_endpoint(data: dict):
    return {"processed": data}
```

## Initialization: `PayloadShieldEnc.init(...)`

Call once before serving requests. Every decorator reads this shared
configuration at call time.

```python
PayloadShieldEnc.init({
    "Key": key,               # symmetric key: fernet, aes-gcm-256
    "PrivateKey": "string",   # RSA/hybrid private key (file path or PEM content)
    "PublicKey": "string",    # RSA/hybrid public key (file path or PEM content)
})
```

| Field | Used by | Accepts |
|---|---|---|
| `Key` | `fernet`, `aes-gcm-256` | Raw key string. `aes-gcm-256` requires the key to resolve to exactly 32 bytes (UTF-8 or base64 encoded). |
| `PrivateKey` | `rsa-hybrid` (decrypt) | File path to a PEM file, or the raw PEM content. |
| `PublicKey` | `rsa-hybrid` (encrypt) | File path to a PEM file, or the raw PEM content. |

Only set the fields required by the encryption types you actually use.

## Decorators

All three live on the `PayloadShield` class and take an `encryption_type`
(default `"base64"`).

### `@PayloadShield.encrypt(encryption_type)`

Encrypts the response payload only.

```python
@app.get("/api/users")
@PayloadShield.encrypt("base64")
async def get_users():
    return [{"id": 1, "name": "Alice"}]

# Response: {"encrypted": "W3siaWQiOiAxLCAibmFtZSI6ICJBbGljZSJ9XQ=="}
```

### `@PayloadShield.decrypt(encryption_type)`

Decrypts the request payload only; the route receives the decrypted dict.

```python
@app.post("/api/login")
@PayloadShield.decrypt("base64")
async def login(credentials: dict):
    return {"status": "success"}

# Expects: {"encrypted": "base64_encoded_json"}
```

### `@PayloadShield.crypt(encryption_type)`

Decrypts the request and encrypts the response.

```python
@app.post("/api/secure")
@PayloadShield.crypt("base64")
async def secure_endpoint(data: dict):
    return {"processed": data}

# Expects: {"encrypted": "encrypted_data"}
# Returns: {"encrypted": "encrypted_data"}
```

## Built-in Encryption Handlers

| Name | Algorithm | Keys required | Security |
|---|---|---|---|
| `base64` | Base64 encoding | none | None — obfuscation only |
| `fernet` | Fernet (AES-128-CBC + HMAC) | `Key` | Symmetric, authenticated |
| `aes-gcm-256` | AES-256-GCM | `Key` (32 bytes) | Symmetric, authenticated |
| `rsa-hybrid` | RSA-OAEP + AES-256-GCM | `PublicKey` (encrypt), `PrivateKey` (decrypt) | Asymmetric/hybrid |

## Custom Handlers

Implement `EncryptionHandler` and register it — every decorator can then
use it by name.

```python
from typing import Any, Dict, Optional
from fastapi_payloadshield import EncryptionHandler, register_handler, PayloadShield

class MyHandler(EncryptionHandler):
    def encode(self, data: Any, config: Optional[Dict[str, Any]] = None) -> str:
        ...

    def decode(self, encoded_data: str, config: Optional[Dict[str, Any]] = None) -> Any:
        ...

register_handler("my-handler", MyHandler())

@app.post("/api/custom")
@PayloadShield.crypt("my-handler")
async def custom_endpoint(data: dict):
    return data
```

`config` is the dict returned by `PayloadShieldEnc.get_config()` — pull out
whatever keys your handler needs (`Key`, `PrivateKey`, `PublicKey`).

## How It Works

**Request decryption**: client sends `{"encrypted": "..."}` → decorator
decodes it with the configured handler → route receives the plain dict.

**Response encryption**: route returns a dict → decorator encodes it with
the configured handler → client receives `{"encrypted": "..."}`.

## Errors

| Situation | Behavior |
|---|---|
| Request decryption fails | `400` response: `{"error": "Failed to decrypt request: ..."}` |
| Unknown `encryption_type` | `ValueError` raised when the decorator is applied: `Encryption handler '<name>' not found. Available handlers: ...` |
| Missing required key (e.g. no `Key` set for `fernet`) | `ValueError` raised when encoding/decoding: `... requires 'Key' to be set via PayloadShieldEnc.init(...)` |

## Migrating to v3

| Removed (v2) | Replacement (v3) |
|---|---|
| `PayloadShieldEnc("base64")` (decorator factory) | `PayloadShield.encrypt("base64")` |
| `PayloadShieldDec("base64")` | `PayloadShield.decrypt("base64")` |
| `PayloadShield("base64")` (function call) | `PayloadShield.crypt("base64")` |
| `encrypt_response`, `decrypt_request`, `crypto_middleware` | Use the decorators above |
| No key configuration API | `PayloadShieldEnc.init({...})` |

There is no compatibility shim — update all call sites to the new API.

## Testing

```bash
# Run the example app
python examples/example_app.py

# Exercise it with the sample client
python examples/test_client.py

# Run the test suite
pytest
```

## Requirements

- Python 3.7+
- FastAPI 0.68+
- Starlette 0.19+
- cryptography 41+

## Project Layout

- `fastapi_payloadshield/` - Main package
  - `__init__.py` - Public exports
  - `config.py` - `PayloadShieldEnc` key configuration
  - `decorators.py` - `PayloadShield` decorators
  - `crypto.py` - Handler registry (`register_handler`, `get_handler`)
  - `EncryptionHandler.py`, `Base64EncryptionHandler.py`,
    `FernetEncryptionHandler.py`, `AESGCM256EncryptionHandler.py`,
    `HybridRSAEncryptionHandler.py` - Built-in handlers
- `examples/` - `example_app.py` demo app and `test_client.py` sample client
- `tests/` - pytest suite for handlers, config, and decorators
- `document/` - Additional guides (see [document/](document/))

## License

Apache-2.0 - See [LICENSE](LICENSE) for details.

