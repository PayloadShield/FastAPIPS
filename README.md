# FastAPI Base64 Crypto

A lightweight Python package that provides decorators for automatic base64 encryption/decryption of request and response payloads in FastAPI applications. No route changes required!

## Features

- 🔒 **Automatic Encryption**: Encrypt responses with a single decorator
- 🔓 **Automatic Decryption**: Decrypt requests with a single decorator
- 📝 **JSON-Friendly**: Works seamlessly with JSON requests and responses
- 🎯 **Route-Agnostic**: No changes needed to your existing route logic
- ⚡ **Lightweight**: Minimal dependencies and overhead
- 🚀 **Easy Integration**: Just add decorators to your routes

## Installation

### From PyPI (once published)
```bash
pip install fastapi-base64-crypto
```

### From Local Development
```bash
cd FastAPIPS
pip install -e .
```

## Quick Start

### Basic Usage

```python
from fastapi import FastAPI
from fastapi_base64_crypto import encrypt_response, decrypt_request

app = FastAPI()

# Encrypt response only
@app.get("/api/data")
@encrypt_response
async def get_data():
    return {"message": "hello", "data": "world"}

# Decrypt request only
@app.post("/api/process")
@decrypt_request
async def process_data(data: dict):
    # data is automatically decrypted from base64
    return {"received": data, "status": "success"}

# Both decrypt request and encrypt response
@app.post("/api/secure")
@encrypt_response
@decrypt_request
async def secure_endpoint(data: dict):
    # Automatically handles both encryption and decryption
    return {"processed": data}
```

## API Reference

### `@encrypt_response`

Automatically encrypts the response payload with base64 encoding.

**Example:**
```python
@app.get("/api/endpoint")
@encrypt_response
async def my_endpoint():
    return {"key": "value"}

# Response sent to client:
# {
#   "encrypted": "eyJrZXkiOiAidmFsdWUifQ=="
# }
```

### `@decrypt_request`

Automatically decrypts the request payload from base64 encoding.

**Request format:**
```json
{
  "encrypted": "eyJkYXRhIjogInZhbHVlIn0="
}
```

**Example:**
```python
@app.post("/api/endpoint")
@decrypt_request
async def my_endpoint(data: dict):
    # data is automatically decoded
    return {"received": data}
```

### `@crypto_middleware`

Combined decorator that applies both encryption and decryption.

**Example:**
```python
@app.post("/api/secure")
@crypto_middleware
async def secure_endpoint(data: dict):
    return {"processed": data}
```

## How It Works

### Request Decryption
1. Client sends: `{"encrypted": "base64_encoded_json"}`
2. Decorator decodes the base64 string
3. Decorator parses JSON and passes to route function
4. Route function receives normal JSON data

### Response Encryption
1. Route function returns: `{"key": "value"}`
2. Decorator encodes the response as JSON string
3. Decorator base64 encodes the JSON string
4. Response sent as: `{"encrypted": "base64_string"}`

## Example Usage

### Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_base64_crypto import encrypt_response, decrypt_request, crypto_middleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example 1: GET with response encryption
@app.get("/api/users/{user_id}")
@encrypt_response
async def get_user(user_id: int):
    return {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }

# Example 2: POST with request decryption
@app.post("/api/login")
@decrypt_request
async def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")
    
    if username == "admin" and password == "secret":
        return {"status": "success", "token": "abc123"}
    return {"status": "failed", "message": "Invalid credentials"}

# Example 3: PUT with both encryption and decryption
@app.put("/api/users/{user_id}")
@encrypt_response
@decrypt_request
async def update_user(user_id: int, data: dict):
    updated_data = {
        "id": user_id,
        "name": data.get("name"),
        "email": data.get("email"),
        "status": "updated"
    }
    return updated_data

# Example 4: Using combined middleware
@app.post("/api/secure-process")
@crypto_middleware
async def secure_process(data: dict):
    processed = {
        "original": data,
        "processed": True,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    return processed

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Testing with cURL

```bash
# Encrypt a payload first
echo '{"username": "admin", "password": "secret"}' | base64

# Expected output (your base64): eyJ1c2VybmFtZSI6ICJhZG1pbiIsICJwYXNzd29yZCI6ICJzZWNyZXQifQ==

# Send POST request with encrypted payload
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"encrypted": "eyJ1c2VybmFtZSI6ICJhZG1pbiIsICJwYXNzd29yZCI6ICJzZWNyZXQifQ=="}'

# Response will be encrypted
# {"encrypted": "eyJzdGF0dXMiOiAic3VjY2VzcyIsICJ0b2tlbiI6ICJhYmMxMjMifQ=="}

# Decode response
echo "eyJzdGF0dXMiOiAic3VjY2VzcyIsICJ0b2tlbiI6ICJhYmMxMjMifQ==" | base64 -d
# {"status": "success", "token": "abc123"}
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

## Error Handling

The decorators include built-in error handling:

```python
# If decryption fails
# Response: {"error": "Failed to decrypt request: ..."}

# If encryption fails
# Response: {"error": "Failed to encrypt response: ..."}
```

## Decorator Order

When using both decorators, apply `@decrypt_request` before `@encrypt_response`:

```python
@app.post("/api/endpoint")
@encrypt_response      # Applied second
@decrypt_request       # Applied first
async def endpoint(data: dict):
    return {"result": data}
```

## Requirements

- Python 3.7+
- FastAPI 0.68+
- Starlette 0.19+

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This package is designed for simple base64 encryption/decryption. For production-grade encryption, consider using cryptographic libraries like `cryptography` or `PyCryptodome` for AES encryption instead.
