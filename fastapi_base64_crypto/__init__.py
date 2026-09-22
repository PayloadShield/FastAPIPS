"""
FastAPI Payload Shield Package
Provides decorators for automatic encryption/decryption of request/response payloads
with pluggable encryption handlers (base64, AES, Fernet, etc.)
"""

# Decorators
from .decorators import (
    PayloadShieldEnc,
    PayloadShieldDec,
    PayloadShield,
    # Backward compatibility
    encrypt_response,
    decrypt_request,
    crypto_middleware,
)

# Encryption handlers and utilities
from .crypto import (
    EncryptionHandler,
    Base64EncryptionHandler,
    register_handler,
    get_handler,
)

__version__ = "2.0.0"
__author__ = "Ganesh Kandu"

__all__ = [
    # New decorator names
    "PayloadShieldEnc",
    "PayloadShieldDec",
    "PayloadShield",
    # Backward compatibility
    "encrypt_response",
    "decrypt_request",
    "crypto_middleware",
    # Encryption handlers
    "EncryptionHandler",
    "Base64EncryptionHandler",
    "register_handler",
    "get_handler",
]
