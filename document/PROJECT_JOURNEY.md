# Project Journey: From Plain Repository to Published PyPI Package

This document describes, step by step, how this repository evolved from a plain
FastAPI project into `fastapi-payloadshield` — a published, pluggable
encryption/decryption decorator package for FastAPI — and exactly how it was
built and shipped to PyPI.

---

## 1. Starting Point

The repository began as a plain FastAPI project with a requirement:

> Add base64 encryption/decryption to request/response payloads using a
> decorator, with **no changes required at the route level** — just add the
> decorator.

At this stage there was no dedicated package, no pluggable architecture, and
no publishing setup — just application code.

---

## 2. Building the Core Package

### 2.1 Static Base64 Decorators (v1.0.0)

A first version implemented three simple decorators:

- `encrypt_response` — encodes the JSON response body as base64
- `decrypt_request` — decodes an incoming base64-encoded request body
- `crypto_middleware` — combines both behaviors

These worked but were hard-coded to base64 only.

### 2.2 Making Encryption Pluggable (v2.0.0)

The user asked: **"Keep code in such way adding new encryption should be
easy."** This required a real extensibility model instead of hard-coded
base64 logic. The design introduced:

- **`EncryptionHandler` (ABC)** — an abstract base class in `crypto.py` with
  two abstract methods: `encode(data)` and `decode(encoded_data)`.
- **`Base64EncryptionHandler`** — the default concrete implementation using
  `base64` + `json` serialization.
- **Handler registry** — a module-level `_HANDLERS` dict plus:
  - `register_handler(name, handler)` — plug in a new encryption type
  - `get_handler(name)` — look up a handler, raising `ValueError` if missing
- **Decorator factories** in `decorators.py`:
  - `PayloadShieldEnc(encryption_type)` — encrypts the response only
  - `PayloadShieldDec(encryption_type)` — decrypts the request only
  - `PayloadShield(encryption_type)` — does both

Each decorator factory accepts an `encryption_type: str` (e.g. `"base64"`)
and resolves the handler via the registry at call time — so adding a new
cipher (Fernet, AES, custom obfuscation, etc.) means writing one class and
calling `register_handler(...)`, with **zero changes to route code**.

Backward-compatible aliases were kept so old code didn't break:

```python
encrypt_response = PayloadShieldEnc("base64")
decrypt_request  = PayloadShieldDec("base64")
crypto_middleware = PayloadShield("base64")
```

### 2.3 Supporting Material

- `examples/example_app.py` — a demo FastAPI app with 6 endpoint groups
  showing every decorator variant.
- `examples/test_client.py` — a `Base64CryptoClient` helper script that
  encrypts requests and decrypts responses to exercise the demo app end to
  end.
- Documentation guides explaining the architecture and how to add custom
  handlers (Fernet, AES, obfuscation examples), quick references, and a
  development guide.

---

## 3. Project Organization & Licensing

Once the core package was stable, the project was reorganized for
publication:

1. **Documentation moved** — every `*.md` file except `README.md` was moved
   into a new `document/` folder, keeping the repository root clean while
   preserving `README.md` as the entry point.
2. **License changed** — from MIT to **Apache-2.0**, updated in the
   `LICENSE` file, `setup.py`, and `pyproject.toml`.
3. **`MANIFEST.in` updated** — to include the `document/` folder,
   `README.md`, `LICENSE`, and `pyproject.toml` in the source distribution.
4. **Publishing scripts added**:
   - `publish.batch` — Windows build + upload script
   - `publish.sh` — Unix/macOS/Linux equivalent
   Both clean old build artifacts, build the wheel/sdist, verify with
   `twine check`, and upload with `twine upload`.

---

## 4. Naming Consistency: PyPI Name vs. Python Module Name

The project went through several naming iterations to land on a name that
was available on PyPI and consistent between the **PyPI package name** and
the **Python import name**:

| Stage | PyPI package name        | Python module (import name) |
|-------|---------------------------|------------------------------|
| Initial | `fastapi-base64-crypto`  | `fastapi_base64_crypto`      |
| Intermediate | `fastapi-shield`   | `fastapi_shield`              |
| **Final** | `fastapi-payloadshield` | `fastapi_payloadshield`     |

Each rename required:

- Renaming the actual package directory on disk (e.g.
  `fastapi_base64_crypto/` → `fastapi_shield/` → `fastapi_payloadshield/`).
- Updating every `from <old_name> import ...` statement across:
  - `examples/example_app.py`, `examples/__init__.py`
  - `README.md` and every file in `document/`
  - `setup.py` (`name=`) and `pyproject.toml` (`[project].name`,
    `[tool.setuptools].packages`, `[tool.setuptools.package-data]`)
  - `publish.batch` / `publish.sh` (install instructions and PyPI URLs)
- Reinstalling the package in editable mode (`pip install -e .`) so the
  interpreter's `.pth` / import machinery picked up the new module name.
  Stale `__editable__.<old-name>-*.pth` files left over from earlier renames
  caused `ModuleNotFoundError` at `uvicorn` startup until they were removed
  and the package was reinstalled fresh under the new name.

---

## 5. Building and Publishing to PyPI

The final publish was performed against the `fastapi-payloadshield` name
using the project's virtual environment (`.venv`):

1. **Clean** old `build/`, `dist/`, and `*.egg-info/` artifacts.
2. **Install/upgrade tooling**: `pip install --upgrade build twine`.
3. **Build**: `python -m build` → produces
   `fastapi_payloadshield-1.0.0-py3-none-any.whl` and
   `fastapi_payloadshield-1.0.0.tar.gz` in `dist/`.
4. **Validate**: `twine check dist/*` to confirm metadata/README render
   correctly before upload.
5. **Upload**: `twine upload --config-file <path-to-pypirc> dist/*`, using a
   `.pypirc`-style file with:
   ```ini
   [distutils]
   index-servers =
       pypi

   [pypi]
     repository = https://upload.pypi.org/legacy/
     username = __token__
     password = <PyPI API token>
   ```
6. **Result**: the package went live at
   <https://pypi.org/project/fastapi-payloadshield/1.0.0/>.

### Security note on the API token

During this process a live PyPI API token was pasted directly into chat and
into a plaintext config file. Any token that is shared in plaintext (chat,
logs, screenshots) should be treated as compromised — the recommended
remediation is to **revoke and regenerate the token** from the PyPI account
settings and update the local credentials file with the new value. Tokens
should never be committed to the repository or shared outside a secrets
manager / password-protected local file.

---

## 6. End Result

Starting from a plain FastAPI repo, the project now has:

- A pluggable encryption architecture (`EncryptionHandler` + registry +
  `PayloadShieldEnc` / `PayloadShieldDec` / `PayloadShield` decorators).
- Backward-compatible legacy decorator names.
- Clean root directory with all guides under `document/`, Apache-2.0
  licensing, and reusable `publish.batch` / `publish.sh` scripts.
- A consistently named package — PyPI name `fastapi-payloadshield`, Python
  import name `fastapi_payloadshield` — published and installable via:

  ```bash
  pip install fastapi-payloadshield
  ```
