# Creating Custom Encryption Handlers

The FastAPI Payload Shield package uses a pluggable architecture that makes it easy to add new encryption types without modifying the core code.

## Architecture Overview

The package is built on three key components:

1. **EncryptionHandler** (ABC) - Base class defining the encryption interface
2. **Handler Registry** - Stores registered encryption handlers by name
3. **Decorators** - Use handlers to encrypt/decrypt payloads

## Creating a Custom Encryption Handler

### Step 1: Define Your Handler Class

Inherit from `EncryptionHandler` and implement two methods:

```python
from fastapi_base64_crypto import EncryptionHandler
import json
from typing import Any

class CustomEncryptionHandler(EncryptionHandler):
    """Your custom encryption handler"""
    
    def encode(self, data: Any) -> str:
        """
        Encrypt the data to a string.
        
        Args:
            data: The data to encrypt (dict, list, etc.)
            
        Returns:
            Encrypted string
        """
        # Convert to JSON
        json_str = json.dumps(data)
        
        # TODO: Apply your encryption logic
        encrypted = your_encryption_logic(json_str)
        
        return encrypted
    
    def decode(self, encoded_data: str) -> Any:
        """
        Decrypt the string back to data.
        
        Args:
            encoded_data: The encrypted string
            
        Returns:
            Decrypted data (dict, list, etc.)
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            # TODO: Apply your decryption logic
            decrypted_str = your_decryption_logic(encoded_data)
            
            # Parse JSON
            return json.loads(decrypted_str)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
```

### Step 2: Register Your Handler

Before using your custom handler, register it with the package:

```python
from fastapi_base64_crypto import register_handler
from fastapi import FastAPI

app = FastAPI()

# Create an instance of your handler
my_handler = CustomEncryptionHandler()

# Register it
register_handler("custom", my_handler)

# Now you can use it in decorators
@app.get("/api/secure")
@PayloadShieldEnc("custom")
async def secure_endpoint():
    return {"message": "secure"}
```

## Complete Examples

### Example 1: AES Encryption Handler

```python
from cryptography.fernet import Fernet
from fastapi_base64_crypto import EncryptionHandler, register_handler
import json
from typing import Any

class FernetEncryptionHandler(EncryptionHandler):
    """
    Fernet (symmetric encryption) handler.
    Uses cryptography library for strong encryption.
    """
    
    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
        print(f"Fernet key: {key.decode()}")  # Save this key!
    
    def encode(self, data: Any) -> str:
        json_str = json.dumps(data)
        encrypted = self.cipher.encrypt(json_str.encode())
        return encrypted.decode()
    
    def decode(self, encoded_data: str) -> Any:
        try:
            decrypted = self.cipher.decrypt(encoded_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            raise ValueError(f"Fernet decryption failed: {str(e)}")

# Usage
fernet_handler = FernetEncryptionHandler()
register_handler("fernet", fernet_handler)
```

### Example 2: AES Encryption Handler

```python
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import json
from fastapi_base64_crypto import EncryptionHandler, register_handler
from typing import Any

class AESEncryptionHandler(EncryptionHandler):
    """
    AES (Advanced Encryption Standard) handler.
    Uses PyCryptodome for strong block cipher encryption.
    """
    
    def __init__(self, key: bytes = None):
        if key is None:
            key = get_random_bytes(32)  # 256-bit key
        if len(key) not in (16, 24, 32):
            raise ValueError("Key must be 16, 24, or 32 bytes")
        self.key = key
        print(f"AES key: {base64.b64encode(key).decode()}")  # Save this!
    
    def encode(self, data: Any) -> str:
        json_str = json.dumps(data)
        plaintext = json_str.encode()
        
        # Generate random IV
        iv = get_random_bytes(16)
        
        # Create cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Encrypt with padding
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        
        # Return IV + ciphertext as base64
        encrypted = base64.b64encode(iv + ciphertext).decode()
        return encrypted
    
    def decode(self, encoded_data: str) -> Any:
        try:
            # Decode from base64
            encrypted = base64.b64decode(encoded_data.encode())
            
            # Extract IV and ciphertext
            iv = encrypted[:16]
            ciphertext = encrypted[16:]
            
            # Create cipher and decrypt
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            return json.loads(plaintext.decode())
        except Exception as e:
            raise ValueError(f"AES decryption failed: {str(e)}")

# Usage
aes_handler = AESEncryptionHandler()
register_handler("aes", aes_handler)
```

### Example 3: Custom JSON + Obfuscation Handler

```python
from fastapi_base64_crypto import EncryptionHandler, register_handler
import json
import base64
from typing import Any

class ObfuscationHandler(EncryptionHandler):
    """
    Simple obfuscation handler (NOT for security).
    Useful for hiding data from casual inspection only.
    """
    
    def __init__(self, salt: str = "my_secret_salt"):
        self.salt = salt
    
    def encode(self, data: Any) -> str:
        json_str = json.dumps(data)
        
        # Add salt before base64
        salted = self.salt + json_str + self.salt
        
        # XOR with salt
        obfuscated = self._xor_encode(salted)
        
        return base64.b64encode(obfuscated.encode()).decode()
    
    def decode(self, encoded_data: str) -> Any:
        try:
            # Decode from base64
            obfuscated = base64.b64decode(encoded_data.encode()).decode()
            
            # XOR to get back
            salted = self._xor_decode(obfuscated)
            
            # Remove salt
            json_str = salted[len(self.salt):-len(self.salt)]
            
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Obfuscation decode failed: {str(e)}")
    
    def _xor_encode(self, data: str) -> str:
        key = (self.salt * ((len(data) // len(self.salt)) + 1))[:len(data)]
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, key))
    
    def _xor_decode(self, data: str) -> str:
        return self._xor_encode(data)  # XOR is symmetric

# Usage
obfuscation_handler = ObfuscationHandler()
register_handler("obfuscation", obfuscation_handler)
```

## Using Multiple Encryption Types

You can register and use multiple encryption types in the same application:

```python
from fastapi import FastAPI
from fastapi_base64_crypto import (
    PayloadShieldEnc, PayloadShieldDec, PayloadShield,
    register_handler
)

app = FastAPI()

# Register handlers
fernet_handler = FernetEncryptionHandler()
aes_handler = AESEncryptionHandler()

register_handler("fernet", fernet_handler)
register_handler("aes", aes_handler)

# Use different types for different endpoints
@app.get("/api/light-security")
@PayloadShieldEnc("base64")
async def light_security():
    return {"data": "base64 only"}

@app.post("/api/medium-security")
@PayloadShield("fernet")
async def medium_security(data: dict):
    return {"processed": data}

@app.post("/api/high-security")
@PayloadShield("aes")
async def high_security(data: dict):
    return {"processed": data}
```

## Best Practices

1. **Key Management**
   - Never hardcode keys in your code
   - Use environment variables or key management services
   - Rotate keys regularly
   - Store backup keys securely

2. **Error Handling**
   - Always raise `ValueError` on decryption failure
   - Include descriptive error messages
   - Don't leak sensitive information in errors

3. **Performance**
   - Cache handler instances (create once, reuse many times)
   - Consider compression before encryption
   - Be mindful of large payloads

4. **Testing**
   - Test encode/decode round-trips
   - Test error handling with invalid data
   - Test performance with various payload sizes

5. **Security**
   - Use proven cryptographic libraries
   - Avoid rolling your own crypto
   - Keep dependencies updated
   - Validate all inputs

## Example: Full Application with Custom Handler

```python
from fastapi import FastAPI
from fastapi_base64_crypto import PayloadShield, register_handler
from cryptography.fernet import Fernet
import os

app = FastAPI()

# Get key from environment
fernet_key = os.getenv("FERNET_KEY", Fernet.generate_key()).encode()

# Create and register handler
from fastapi_base64_crypto import EncryptionHandler
import json
from typing import Any

class MyFernetHandler(EncryptionHandler):
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encode(self, data: Any) -> str:
        return self.cipher.encrypt(json.dumps(data).encode()).decode()
    
    def decode(self, encoded_data: str) -> Any:
        try:
            return json.loads(self.cipher.decrypt(encoded_data.encode()))
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

handler = MyFernetHandler(fernet_key)
register_handler("fernet", handler)

# Use in routes
@app.post("/api/secure")
@PayloadShield("fernet")
async def secure_endpoint(data: dict):
    return {"processed": data, "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Troubleshooting

### Handler Not Found Error
```
ValueError: Encryption handler 'xyz' not found. Available handlers: base64, fernet
```

**Solution**: Make sure you've called `register_handler()` before using the decorator.

### Decryption Fails
Make sure:
1. Handler is registered with the correct name
2. Encoder and decoder use the same key
3. No data corruption in transmission
4. Payload hasn't been modified

### Performance Issues
- Use streaming for large payloads
- Consider compression before encryption
- Cache handler instances
- Profile with `cProfile`

## Contributing New Handlers

To contribute a handler to the package:

1. Create a well-documented handler class
2. Add tests
3. Submit a PR with examples
4. Include documentation

Happy encrypting! 🔒
