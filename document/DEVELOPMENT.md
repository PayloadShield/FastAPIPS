# Development Guide

## Project Structure

```
FastAPIPS/
├── fastapi_payloadshield/           # Main package directory
│   ├── __init__.py                  # Package initialization & exports
│   ├── config.py                    # PayloadShieldEnc key configuration
│   ├── decorators.py                # PayloadShield.encrypt/decrypt/crypt decorators
│   ├── crypto.py                    # Handler registry (register_handler/get_handler)
│   ├── EncryptionHandler.py         # Abstract handler interface
│   ├── Base64EncryptionHandler.py   # base64 handler
│   ├── FernetEncryptionHandler.py   # fernet handler
│   ├── AESGCM256EncryptionHandler.py# aes-gcm-256 handler
│   ├── ChaChaEncryptionHandler.py   # chacha20-poly1305 handler
│   ├── HybridRSAEncryptionHandler.py# rsa-hybrid handler
│   ├── ECDHAESGCMEncryptionHandler.py# ecdh-aes-gcm handler
│   ├── ECIESEncryptionHandler.py    # ecies handler
│   └── HPKEEncryptionHandler.py     # hpke handler
│
├── examples/                        # Example implementations
│   ├── main.py                      # Full-featured example FastAPI app
│   ├── private.pem, public.pem      # Generated RSA keys (rsa-hybrid)
│   ├── ec_private.pem, ec_public.pem        # Generated EC keys (ecdh-aes-gcm, ecies)
│   └── hpke_private.pem, hpke_public.pem    # Generated X25519 keys (hpke)
│
├── tests/                           # pytest suite
│   ├── test_handlers.py             # Handler encode/decode roundtrip tests
│   ├── test_config.py               # PayloadShieldEnc.init() tests
│   └── test_decorators.py           # Decorator + FastAPI TestClient tests
│
├── setup.py                         # Classic setup configuration (pip installable)
├── pyproject.toml                   # Modern Python project configuration
├── requirements.txt                 # Development & runtime dependencies
├── README.md                        # Full API documentation
├── MANIFEST.in                      # Files to include in distribution
├── .gitignore                       # Git ignore patterns
└── LICENSE                          # Apache-2.0 License
```

## Installation for Development

### 1. Clone the Repository
```bash
git clone <repository-url>
cd FastAPIPS
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install in Development Mode
```bash
# Install package with all dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Or install from requirements
pip install -r requirements.txt
```

## Testing the Package

### Option 1: Run Example Application
```bash
cd examples
python -m uvicorn main:app --reload
```

The console prints ready-to-paste Postman requests (URL + JSON body) for
every built-in handler on startup.

### Option 2: Manual Testing with cURL
```bash
# Terminal 1: Start server
cd examples
python -m uvicorn main:app --reload

# Terminal 2: Test endpoints (see the Postman examples printed on startup)
curl http://localhost:8000/health
curl http://localhost:8000/base
```

### Option 3: Run the pytest Suite
```bash
pytest
```

## Package Components

See [../README.md](../README.md) for the full API reference
(`PayloadShieldEnc.init`, `PayloadShield.encrypt/decrypt/crypt`, built-in
handlers, and custom handler registration). This guide only covers
day-to-day development workflows.

## Adding a New Built-in Handler

1. Create `fastapi_payloadshield/MyHandler.py` implementing
   `EncryptionHandler.encode(data, config)` / `.decode(encoded_data, config)`.
2. Register it in `fastapi_payloadshield/crypto.py`'s `_HANDLERS` dict.
3. Export the class from `fastapi_payloadshield/__init__.py`.
4. Add a roundtrip test in `tests/test_handlers.py`.

## Publishing to PyPI

See [PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md) for the full release process.

## Code Style

### Format Code
```bash
black fastapi_payloadshield examples
```

### Lint Code
```bash
flake8 fastapi_payloadshield examples
```

### Type Checking
```bash
mypy fastapi_payloadshield
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## Troubleshooting

### Module Import Errors
```bash
# Reinstall in development mode
pip install -e . --force-reinstall
```

### "No module named 'fastapi'"
```bash
pip install fastapi uvicorn
```

### Version Conflicts
```bash
# Create fresh virtual environment
python -m venv venv_fresh
venv_fresh/Scripts/activate
pip install -r requirements.txt
```

## Useful Commands

```bash
# Check installed version
python -c "import fastapi_payloadshield; print(fastapi_payloadshield.__version__)"

# View package info
pip show fastapi_payloadshield

# Uninstall package
pip uninstall fastapi_payloadshield

# Clean build artifacts
rm -rf build/ dist/ *.egg-info
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Packaging Guide](https://packaging.python.org/)
- [cryptography library](https://cryptography.io/)
- [Setuptools Documentation](https://setuptools.readthedocs.io/)

## License

Apache-2.0 - See [../LICENSE](../LICENSE) for details.


