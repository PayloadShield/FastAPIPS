# Quick Start Guide

## Installation

### Option 1: Install from Local Directory
```bash
cd FastAPIPS
pip install -e .
```

### Option 2: Install with Development Dependencies
```bash
pip install -e ".[dev]"
```

### Option 3: Install Requirements
```bash
pip install -r requirements.txt
```

## Quick Example

### 1. Create a Simple FastAPI App

Create a file named `main.py`:

```python
from fastapi import FastAPI
from fastapi_base64_crypto import encrypt_response, decrypt_request

app = FastAPI()

@app.get("/api/hello")
@encrypt_response
async def hello():
    return {"message": "Hello, World!"}

@app.post("/api/echo")
@decrypt_request
async def echo(data: dict):
    return {"received": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Run the Server
```bash
python main.py
```

Server starts at `http://localhost:8000`

### 3. Test with cURL

#### Encrypt a message first:
```bash
# Linux/Mac
echo '{"text": "hello"}' | base64
# eyJ0ZXh0IjogImhlbGxvIn0=

# PowerShell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes('{"text": "hello"}'))
# eyJ0ZXh0IjogImhlbGxvIn0=
```

#### Test GET (encrypted response):
```bash
curl http://localhost:8000/api/hello
# Response: {"encrypted":"eyJtZXNzYWdlIjogIkhlbGxvLCBXb3JsZCEifQ=="}
```

#### Test POST (encrypted request):
```bash
curl -X POST http://localhost:8000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"encrypted":"eyJ0ZXh0IjogImhlbGxvIn0="}'
# Response: {"received":{"text":"hello"}}
```

### 4. Test with Python

```python
import requests
import base64
import json

BASE_URL = "http://localhost:8000"

# Test GET with response encryption
response = requests.get(f"{BASE_URL}/api/hello")
encrypted = response.json()["encrypted"]
decrypted = json.loads(base64.b64decode(encrypted).decode())
print(decrypted)  # {'message': 'Hello, World!'}

# Test POST with request encryption
data = {"text": "hello"}
json_str = json.dumps(data)
encrypted_data = base64.b64encode(json_str.encode()).decode()

response = requests.post(
    f"{BASE_URL}/api/echo",
    json={"encrypted": encrypted_data}
)
print(response.json())  # {'received': {'text': 'hello'}}
```

## Running Examples

### Start Example Server
```bash
python examples/example_app.py
```

### Run Client Tests
```bash
python examples/test_client.py
```

## File Structure

```
FastAPIPS/
├── fastapi_base64_crypto/       # Main package
│   ├── __init__.py              # Package exports
│   ├── crypto.py                # Encryption/decryption functions
│   └── decorators.py            # Decorator implementations
├── examples/
│   ├── example_app.py           # Example FastAPI app
│   └── test_client.py           # Test client script
├── setup.py                     # Setup configuration
├── pyproject.toml               # Modern Python config
├── README.md                    # Full documentation
├── QUICKSTART.md                # This file
├── requirements.txt             # Dependencies
├── .gitignore                   # Git ignore rules
└── LICENSE                      # MIT License
```

## Decorators

### @encrypt_response
Encrypts the response with base64 encoding.

```python
@app.get("/api/data")
@encrypt_response
async def get_data():
    return {"message": "hello"}

# Response: {"encrypted": "eyJtZXNzYWdlIjogImhlbGxvIn0="}
```

### @decrypt_request
Decrypts the request from base64 encoding.

```python
@app.post("/api/data")
@decrypt_request
async def post_data(data: dict):
    # data is automatically decrypted
    return {"received": data}

# Expects: {"encrypted": "base64_encoded_json"}
```

### @crypto_middleware
Combined decorator for both encryption and decryption.

```python
@app.post("/api/secure")
@crypto_middleware
async def secure_endpoint(data: dict):
    return {"processed": data}
```

## Common Issues

### "Module not found" Error
Make sure the package is installed:
```bash
pip install -e .
```

### Import Error
Verify FastAPI is installed:
```bash
pip install fastapi uvicorn
```

### Port Already in Use
Change the port when running:
```bash
python -m uvicorn main:app --port 8001
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [examples/example_app.py](examples/example_app.py) for more use cases
3. Run [examples/test_client.py](examples/test_client.py) to test all features
4. Customize decorators for your specific needs

## Support

For issues or questions:
1. Check the README.md documentation
2. Review examples in the examples/ folder
3. Open an issue on GitHub

Happy coding! 🚀
