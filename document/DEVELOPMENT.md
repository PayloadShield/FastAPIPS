# Development Guide

## Project Structure

```
FastAPIPS/
├── fastapi_payloadshield/           # Main package directory
│   ├── __init__.py                  # Package initialization & exports
│   ├── crypto.py                    # Base64 encoding/decoding utilities
│   └── decorators.py                # FastAPI decorators for encryption/decryption
│
├── examples/                        # Example implementations
│   ├── example_app.py               # Full-featured example FastAPI app
│   └── test_client.py               # Client script to test the API
│
├── setup.py                         # Classic setup configuration (pip installable)
├── pyproject.toml                   # Modern Python project configuration
├── requirements.txt                 # Development & runtime dependencies
├── README.md                        # Comprehensive documentation
├── QUICKSTART.md                    # Quick start guide
├── MANIFEST.in                      # Files to include in distribution
├── .gitignore                       # Git ignore patterns
└── LICENSE                          # MIT License
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
python examples/example_app.py
```

Then in another terminal, run the test client:
```bash
python examples/test_client.py
```

### Option 2: Manual Testing with cURL
```bash
# Terminal 1: Start server
python examples/example_app.py

# Terminal 2: Test endpoints
curl http://localhost:8000/api/public/users
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"encrypted":"eyJ1c2VybmFtZSI6ICJhZG1pbiIsICJwYXNzd29yZCI6ICJwYXNzd29yZDEyMyJ9"}'
```

## Package Components

### 1. `crypto.py` - Utilities
- `encode_base64(data)` - Encode data to base64
- `decode_base64(encoded_data)` - Decode base64 to data
- `encode_response(data)` - Wrap response in encryption format
- `decode_request(encoded_data)` - Decode request format

### 2. `decorators.py` - Decorators
- `@encrypt_response` - Encrypts response payload
- `@decrypt_request` - Decrypts request payload
- `@crypto_middleware` - Combined encryption/decryption

## Adding New Features

### Add a New Decorator
1. Edit `fastapi_payloadshield/decorators.py`
2. Add your decorator function
3. Export it in `fastapi_payloadshield/__init__.py`

Example:
```python
# In decorators.py
def my_new_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Your logic here
        return await func(*args, **kwargs)
    return wrapper

# In __init__.py
from .decorators import my_new_decorator
__all__ = [..., "my_new_decorator"]
```

### Add New Crypto Functions
1. Edit `fastapi_payloadshield/crypto.py`
2. Add your function
3. Export if needed in `__init__.py`

## Publishing to PyPI

### 1. Update Version
Edit version in:
- `setup.py`
- `pyproject.toml`
- `fastapi_payloadshield/__init__.py`

### 2. Install Build Tools
```bash
pip install build twine
```

### 3. Build Package
```bash
python -m build
```

### 4. Upload to PyPI
```bash
# Test PyPI first (optional)
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

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

## Creating Tests

Create a `tests/` directory with pytest tests:

```python
# tests/test_crypto.py
import pytest
from fastapi_payloadshield.crypto import encode_base64, decode_base64

def test_encode_decode():
    data = {"key": "value"}
    encoded = encode_base64(data)
    decoded = decode_base64(encoded)
    assert decoded == data
```

Run tests:
```bash
pytest
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
- [Base64 RFC 4648](https://tools.ietf.org/html/rfc4648)
- [Setuptools Documentation](https://setuptools.readthedocs.io/)

## License

MIT License - See LICENSE file for details
