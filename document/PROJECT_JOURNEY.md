# Project Journey: From Plain Repository to Published PyPI Package

This document describes, step by step, how this repository evolved from a
plain FastAPI project into `fastapi_payloadshield` — a published, pluggable
encryption/decryption decorator package for FastAPI.

## 1. Starting Point

The repository began as a plain FastAPI project with a requirement:

> Add base64 encryption/decryption to request/response payloads using a
> decorator, with **no changes required at the route level** — just add the
> decorator.

## 2. v1 — Static Base64 Decorators

A first version implemented three simple decorators: `encrypt_response`,
`decrypt_request`, and `crypto_middleware`, hard-coded to base64.

## 3. v2 — Pluggable Encryption

To make adding new encryption types easy, the package introduced:

- `EncryptionHandler` (ABC) with `encode()`/`decode()`.
- A handler registry (`register_handler`, `get_handler`).
- Decorator factories `PayloadShieldEnc(type)`, `PayloadShieldDec(type)`,
  `PayloadShield(type)` accepting an `encryption_type` string.
- Backward-compatible aliases for the v1 decorator names.

## 4. Project Organization & Licensing

- All `*.md` docs (except `README.md`) moved into `document/`.
- License changed from MIT to Apache-2.0.
- `MANIFEST.in`, `publish.batch`, `publish.sh` added for packaging/release.

## 5. Naming Consistency

The PyPI package name and Python import name went through several
iterations before settling on a single consistent name:

| Stage | PyPI name | Python module |
|---|---|---|
| Initial | `fastapi-base64-crypto` | `fastapi_base64_crypto` |
| Intermediate | `fastapi-shield` | `fastapi_shield` |
| **Final** | `fastapi-payloadshield` | `fastapi_payloadshield` |

Each rename required renaming the package directory, updating every import
across code/docs, updating `setup.py`/`pyproject.toml`, and reinstalling in
editable mode (`pip install -e .`) to clear stale `.pth` entries left by
previous names.

## 6. v3 — Breaking API Redesign (current)

The decorator/init API was redesigned from scratch, with **no backward
compatibility**:

- Removed entirely: `encrypt_response`, `decrypt_request`,
  `crypto_middleware`, and the old `PayloadShieldEnc(type)` /
  `PayloadShieldDec(type)` / `PayloadShield(type)` factory functions.
- New decorator API: `PayloadShield.encrypt(type)`,
  `PayloadShield.decrypt(type)`, `PayloadShield.crypt(type)` — static
  methods on a `PayloadShield` class.
- New global key configuration: `PayloadShieldEnc.init({"Key": ...,
  "PrivateKey": ..., "PublicKey": ...})`, called once at startup. Every
  handler pulls the keys it needs from this shared config at call time.
  `PrivateKey`/`PublicKey` accept either a file path or raw PEM content.
- Handler signatures standardized to `encode(data, config)` /
  `decode(encoded_data, config)` so every handler (built-in or custom)
  receives the same global config dict.
- New built-in handlers: `fernet` (symmetric), `aes-gcm-256` (symmetric,
  rewritten on top of the `cryptography` library instead of pycryptodome),
  and `rsa-hybrid` (RSA-OAEP wrapping an AES-256-GCM payload key) — in
  addition to the original `base64` handler.
- Added a pytest suite (`tests/`) covering handler roundtrips, key
  configuration, and decorator behavior via FastAPI's `TestClient`.
- Consolidated `document/` down to `DEVELOPMENT.md`, `PUBLISHING_GUIDE.md`,
  and this file — removed docs that only described the now-removed v1/v2
  API surface to avoid duplicated/obsolete guidance. `README.md` is the
  single source of truth for the current public API.

## 7. Publishing to PyPI

Build and release process (`document/PUBLISHING_GUIDE.md`):

1. Clean `build/`, `dist/`, `*.egg-info/`.
2. `pip install --upgrade build twine`
3. `python -m build`
4. `twine check dist/*`
5. `twine upload --config-file <pypirc-path> dist/*`

### Security note

A PyPI API token was at one point shared in plaintext (chat message and a
local config file). Any token exposed this way should be treated as
compromised and rotated immediately via the PyPI account's API token
settings — tokens must never be committed to the repository.

## 8. Current End State

- Package: PyPI name `fastapi_payloadshield`, Python import name
  `fastapi_payloadshield` (consistent).
- Public API: `PayloadShieldEnc.init(...)` for configuration;
  `PayloadShield.encrypt/decrypt/crypt(type)` decorators.
- Built-in handlers: `base64`, `fernet`, `aes-gcm-256`, `rsa-hybrid`.
- Fully pluggable via `register_handler(name, handler)`.
