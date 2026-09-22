# FastAPI Payload Shield

Lightweight FastAPI decorators for automatic encryption/decryption of request and response payloads. **Supports pluggable encryption handlers** - easily add new encryption types like AES, Fernet, or custom algorithms!

## 🎯 Key Features

- 🔒 **Flexible Encryption**: Multiple encryption types (base64, AES, Fernet, custom)
- 🔓 **Automatic Decryption**: Decrypt incoming requests automatically
- 📝 **JSON-Friendly**: Works seamlessly with JSON requests and responses
- 🎯 **Route-Agnostic**: No changes needed to your existing route logic
- ⚡ **Lightweight**: Minimal dependencies and overhead
- 🚀 **Easy Integration**: Just add decorators to your routes
- 🧩 **Pluggable**: Create custom encryption handlers easily

## Installation

### From Local Development
```bash
cd FastAPIPS
pip install -e .
```

### From PyPI (when published)
```bash
pip install fastapi-shield
```

## Quick Start

### Basic Usage with Base64

```python
from fastapi import FastAPI
from fastapi_shield import PayloadShieldEnc, PayloadShieldDec, PayloadShield

app = FastAPI()

# Encrypt response only
@app.get("/api/data")
@PayloadShieldEnc("base64")
async def get_data():
    return {"message": "hello", "data": "world"}

# Decrypt request only
@app.post("/api/process")
@PayloadShieldDec("base64")
async def process_data(data: dict):
    return {"received": data, "status": "success"}

@app.post("/api/secure")
@PayloadShield("base64")
async def secure_endpoint(data: dict):
    return {"processed": data}
```

## Decorators

### `@PayloadShieldEnc(encryption_type)`

Encrypts the response payload.

```python
@app.get("/api/users")
@PayloadShieldEnc("base64")
async def get_users():
    return [{"id": 1, "name": "Alice"}]

# Response: {"encrypted": "W3siaWQiOiAxLCAibmFtZSI6ICJBbGljZSJ9XQ=="}
```

### `@PayloadShieldDec(encryption_type)`

Decrypts the request payload.

```python
@app.post("/api/login")
@PayloadShieldDec("base64")
async def login(credentials: dict):
    return {"status": "success"}

# Expects: {"encrypted": "base64_encoded_json"}
```

### `@PayloadShield(encryption_type)`

Combined encryption and decryption

```python
@app.post("/api/secure")
@PayloadShield("base64")
async def secure_endpoint(data: dict):
    return {"processed": data}

# Expects: {"encrypted": "encrypted_data"}
# Returns: {"encrypted": "encrypted_data"}
```

## Advanced Example: Multiple Encryption Types

```python
from fastapi import FastAPI
from fastapi_shield import PayloadShield, register_handler, EncryptionHandler
from cryptography.fernet import Fernet
import json

app = FastAPI()

# Create Fernet handler
class FernetHandler(EncryptionHandler):
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encode(self, data):
        return self.cipher.encrypt(json.dumps(data).encode()).decode()
    
    def decode(self, encoded_data):
        return json.loads(self.cipher.decrypt(encoded_data.encode()))

# Register
key = Fernet.generate_key()
register_handler("fernet", FernetHandler(key))

# Use different encryption for different endpoints
@app.post("/api/public")
@PayloadShield("base64")  # Light encryption
async def public_endpoint(data: dict):
    return data

@app.post("/api/private")
@PayloadShield("fernet")  # Strong encryption
async def private_endpoint(data: dict):
    return data
```

## How It Works

### Request Decryption Flow
1. Client sends: `{"encrypted": "encrypted_data"}`
2. `@PayloadShieldDec` decorator intercepts
3. Decrypts using specified handler
4. Route receives: `{"key": "value"}` (normal dict)

### Response Encryption Flow
1. Route returns: `{"key": "value"}`
2. `@PayloadShieldEnc` decorator intercepts
3. Encrypts using specified handler
4. Client receives: `{"encrypted": "encrypted_data"}`

## Testing

### Run Example Application
```bash
python examples/example_app.py
```

### Run Test Client
```bash
python examples/test_client.py
```

### Manual Test with cURL

```bash
# Encrypt test data
echo '{"username":"admin"}' | base64
# eyJ1c2VybmFtZSI6ImFkbWluIn0=

# Send encrypted request
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"encrypted":"eyJ1c2VybmFtZSI6ImFkbWluIn0="}'
```

### Testing with Python
```python
import requests
import json
import base64

# Encode request
data = {"username": "admin", "password": "secret"}
json_str = json.dumps(data)
encrypted = base64.b64encode(json_str.encode()).decode()

# Send request
response = requests.post(
    "http://localhost:8000/api/login",
    json={"encrypted": encrypted}
)

# Decode response
encrypted_response = response.json()["encrypted"]
decrypted = json.loads(base64.b64decode(encrypted_response).decode())
print(decrypted)
# {'status': 'success', 'token': 'abc123'}
```

## Creating Custom Encryption Handlers

See [CUSTOM_HANDLERS.md](CUSTOM_HANDLERS.md) for detailed guide on:

- Creating custom handlers
- Fernet encryption example
- AES encryption example
- Best practices
- Performance tips
- Security considerations

## Backward Compatibility

Old decorator names still work:

```python
from fastapi_shield import encrypt_response, decrypt_request, crypto_middleware

# These are equivalent to:
# PayloadShieldEnc("base64")
# PayloadShieldDec("base64")
# PayloadShield("base64")

@app.get("/api/data")
@encrypt_response
async def get_data():
    return {"data": "value"}
```

## API Reference

### Decorators

| Decorator | Purpose |
|-----------|---------|
| `PayloadShieldEnc(type)` | Encrypt response |
| `PayloadShieldDec(type)` | Decrypt request |
| `PayloadShield(type)` | Both encrypt & decrypt |

### Functions

| Function | Purpose |
|----------|---------|
| `register_handler(name, handler)` | Register custom encryption handler |
| `get_handler(name)` | Get handler by name |
| `EncryptionHandler` | Base class for handlers |

### Built-in Handlers

| Handler | Type | Security | Use Case |
|---------|------|----------|----------|
| `base64` | Encoding | None | Obfuscation, development |

## Error Handling

The decorators include built-in error handling:

```python
# Invalid encrypted data
# Response: {"error": "Failed to decrypt request: ..."}

# Missing encryption handler  
# Response: ValueError: Encryption handler 'xyz' not found. Available: base64, fernet
```

## Performance Considerations

- **Caching**: Handler instances are cached
- **Compression**: Consider compressing before encryption for large payloads
- **Async**: All operations are async-friendly

## Requirements

- Python 3.7+
- FastAPI 0.68+
- Starlette 0.19+

## Files Included

- `fastapi_shield/` - Main package
  - `__init__.py` - Exports decorators and handlers
  - `crypto.py` - Encryption handlers
  - `decorators.py` - FastAPI decorators
- `examples/` - Working examples
  - `example_app.py` - Full-featured demo
  - `test_client.py` - Test/client script
- `README.md` - This file
- `QUICKSTART.md` - Quick start guide
- `CUSTOM_HANDLERS.md` - Creating custom handlers
- `DEVELOPMENT.md` - Development guide

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Areas for contribution:

1. New encryption handlers (AES, Fernet, etc.)
2. Performance optimizations
3. Documentation improvements
4. Test coverage
5. Examples

## Support

- 📖 Full guide: [README.md](README.md)
- ⚡ Quick start: [QUICKSTART.md](QUICKSTART.md)
- 🧩 Custom handlers: [CUSTOM_HANDLERS.md](CUSTOM_HANDLERS.md)
- 🛠️ Development: [DEVELOPMENT.md](DEVELOPMENT.md)

---

**Happy encrypting!** 🔒

## Why Payload Shield?

This package was designed with extensibility in mind. Unlike static encryption libraries, Payload Shield lets you:

- Mix and match encryption types in the same app
- Add new encryption types without touching core code
- Keep route logic clean and simple
- Support multiple security levels

Perfect for:
- Building multi-tier security APIs
- Migrating from one encryption to another
- Testing different encryption strategies
- Production systems requiring flexible crypto
