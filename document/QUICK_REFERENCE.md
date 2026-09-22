# Quick Reference - New Decorator Architecture

## 🎯 Three Main Decorators

### 1. PayloadShieldEnc("encryption_type")
**Encrypts Response Only**

```python
@app.get("/api/users")
@PayloadShieldEnc("base64")
async def get_users():
    return {"users": [...]}
# Response: {"encrypted": "base64_encoded_json"}
```

### 2. PayloadShieldDec("encryption_type")
**Decrypts Request Only**

```python
@app.post("/api/login")
@PayloadShieldDec("base64")
async def login(credentials: dict):
    return {"token": "..."}
# Expects: {"encrypted": "base64_encoded_json"}
# Returns: {"token": "..."}
```

### 3. PayloadShield("encryption_type")
**Both Encrypt & Decrypt**

```python
@app.post("/api/secure")
@PayloadShield("base64")
async def secure_endpoint(data: dict):
    return {"result": data}
# Expects: {"encrypted": "base64_encoded_json"}
# Response: {"encrypted": "base64_encoded_json"}
```

---

## 🔒 Supported Encryption Types

| Type | Usage | Security |
|------|-------|----------|
| `"base64"` | `@PayloadShield("base64")` | None (encoding only) |
| `"fernet"` | Register first (see below) | Strong |
| `"aes"` | Register first (see below) | Strong |
| Custom | Register your own | Depends |

---

## 📝 How to Add Custom Encryption

### Step 1: Create Handler Class
```python
from fastapi_payloadshield import EncryptionHandler
import json

class MyHandler(EncryptionHandler):
    def encode(self, data):
        # Encrypt and return string
        json_str = json.dumps(data)
        return your_encrypt_logic(json_str)
    
    def decode(self, encoded_data):
        # Decrypt and return data
        json_str = your_decrypt_logic(encoded_data)
        return json.loads(json_str)
```

### Step 2: Register Handler
```python
from fastapi_payloadshield import register_handler

handler = MyHandler()
register_handler("my-handler", handler)
```

### Step 3: Use in Decorators
```python
@app.post("/api/endpoint")
@PayloadShield("my-handler")
async def endpoint(data: dict):
    return data
```

---

## 🛠️ Complete Example with Fernet

```python
from fastapi import FastAPI
from fastapi_payloadshield import PayloadShield, EncryptionHandler, register_handler
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

# Use
@app.post("/api/secure")
@PayloadShield("fernet")
async def secure_endpoint(data: dict):
    return {"processed": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🔄 Multiple Encryption Types in One App

```python
from fastapi_payloadshield import PayloadShield, register_handler

# Register different handlers
register_handler("base64", Base64Handler())
register_handler("fernet", FernetHandler(key))
register_handler("aes", AESHandler(key))

# Use different encryption for different endpoints
@app.post("/api/public")
@PayloadShield("base64")  # Light
async def public_api(data: dict):
    return data

@app.post("/api/private")
@PayloadShield("fernet")  # Medium
async def private_api(data: dict):
    return data

@app.post("/api/critical")
@PayloadShield("aes")  # Strong
async def critical_api(data: dict):
    return data
```

---

## ✅ Testing Encrypted Endpoints

### With cURL
```bash
# Encrypt payload
echo '{"username":"admin"}' | base64

# Send request
curl -X POST http://localhost:8000/api/login \
  -d '{"encrypted":"eyJ1c2VybmFtZSI6ImFkbWluIn0="}'

# Decode response
echo "ENCRYPTED_RESPONSE" | base64 -d
```

### With Python
```python
import requests
import json
import base64

# Encode
data = {"username": "admin", "password": "secret"}
encrypted = base64.b64encode(json.dumps(data).encode()).decode()

# Send
response = requests.post(
    "http://localhost:8000/api/login",
    json={"encrypted": encrypted}
)

# Decode
result = json.loads(
    base64.b64decode(response.json()["encrypted"]).decode()
)
print(result)
```

---

## 🚀 Key Features

| Feature | Old API | New API |
|---------|---------|---------|
| Response Encrypt | `@encrypt_response` | `@PayloadShieldEnc("base64")` |
| Request Decrypt | `@decrypt_request` | `@PayloadShieldDec("base64")` |
| Both | `@crypto_middleware` | `@PayloadShield("base64")` |
| Custom Types | Not possible | ✅ Yes |
| Multiple Types | Not supported | ✅ Yes |
| Backward Compat | N/A | ✅ Yes |

---

## 📚 Available Functions

### Decorators
- `PayloadShieldEnc(type)` - Encrypt response
- `PayloadShieldDec(type)` - Decrypt request
- `PayloadShield(type)` - Both

### Handler Management
- `register_handler(name, handler)` - Register custom handler
- `get_handler(name)` - Get handler by name
- `EncryptionHandler` - Base class for handlers

### Legacy (Still Works)
- `encrypt_response` - Old decorator name
- `decrypt_request` - Old decorator name
- `crypto_middleware` - Old decorator name

---

## 🔐 Handler Implementation Template

```python
from fastapi_payloadshield import EncryptionHandler
import json
from typing import Any

class YourHandler(EncryptionHandler):
    """
    Your custom encryption handler.
    Implement encode() and decode() methods.
    """
    
    def __init__(self, key):
        """Initialize with your encryption key/config"""
        self.key = key
    
    def encode(self, data: Any) -> str:
        """
        Encrypt data to string.
        
        Args:
            data: Any JSON-serializable object
        
        Returns:
            Encrypted string
        """
        json_str = json.dumps(data)
        # TODO: Apply your encryption
        encrypted = your_encryption_lib.encrypt(json_str, self.key)
        return encrypted
    
    def decode(self, encoded_data: str) -> Any:
        """
        Decrypt string to data.
        
        Args:
            encoded_data: Encrypted string
        
        Returns:
            Decrypted data (dict, list, etc.)
        
        Raises:
            ValueError: If decryption fails
        """
        try:
            # TODO: Apply your decryption
            json_str = your_encryption_lib.decrypt(encoded_data, self.key)
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
```

---

## 🎓 Common Patterns

### Pattern 1: Single Encryption Type
```python
@app.post("/api/endpoint")
@PayloadShield("base64")
async def endpoint(data: dict):
    return data
```

### Pattern 2: Different Encryption Per Tier
```python
@app.post("/api/public")
@PayloadShield("base64")
async def public(data: dict):
    return data

@app.post("/api/private")
@PayloadShield("fernet")
async def private(data: dict):
    return data
```

### Pattern 3: Encryption Only
```python
@app.get("/api/data")
@PayloadShieldEnc("base64")
async def get_data():
    return {"data": "value"}
```

### Pattern 4: Decryption Only
```python
@app.post("/api/process")
@PayloadShieldDec("base64")
async def process(data: dict):
    return {"status": "ok"}
```

### Pattern 5: No Encryption (Mix Encrypted & Unencrypted)
```python
@app.get("/health")
async def health():  # No decorator
    return {"status": "healthy"}

@app.post("/api/secure")
@PayloadShield("base64")
async def secure(data: dict):
    return data
```

---

## 🐛 Troubleshooting

**"Encryption handler 'xyz' not found"**
```python
# Register the handler first!
from fastapi_payloadshield import register_handler
register_handler("xyz", XYZHandler())
```

**"Failed to decrypt request"**
- Check data is valid encrypted format
- Ensure correct handler type is used
- Verify handler key is correct

**"Module not found"**
```bash
pip install -e .
```

---

## 📖 Learn More

- Full docs: [README.md](README.md)
- Custom handlers guide: [CUSTOM_HANDLERS.md](CUSTOM_HANDLERS.md)
- Refactoring details: [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- Quick start: [QUICKSTART.md](QUICKSTART.md)

---

**Ready to secure your APIs?** 🔒
