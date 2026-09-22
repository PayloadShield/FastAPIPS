"""
FastAPI Base64 Crypto Package
Provides decorators for automatic base64 encryption/decryption of request/response payloads
"""

from .decorators import encrypt_response, decrypt_request

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = ["encrypt_response", "decrypt_request"]
