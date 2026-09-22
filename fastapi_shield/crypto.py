"""
Crypto utilities with pluggable encryption handlers
Supports multiple encryption types (base64, AES, etc.)
"""

import base64
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Union


# ============================================================================
# Abstract Encryption Handler Interface
# ============================================================================

class EncryptionHandler(ABC):
    """
    Abstract base class for encryption handlers.
    Implement this to add support for new encryption types.
    """
    
    @abstractmethod
    def encode(self, data: Any) -> str:
        """
        Encode data to encrypted string.
        
        Args:
            data: Dictionary or JSON serializable object
            
        Returns:
            Encrypted string
        """
        pass
    
    @abstractmethod
    def decode(self, encoded_data: str) -> Any:
        """
        Decode encrypted string to data.
        
        Args:
            encoded_data: Encrypted string
            
        Returns:
            Decoded dictionary or object
            
        Raises:
            ValueError: If data cannot be decoded
        """
        pass


# ============================================================================
# Base64 Encryption Handler
# ============================================================================

class Base64EncryptionHandler(EncryptionHandler):
    """
    Base64 encoding/decoding handler.
    Note: Base64 is encoding, not encryption. Use for obfuscation only.
    """
    
    def encode(self, data: Any) -> str:
        """Encode data to base64 string."""
        if isinstance(data, dict):
            json_str = json.dumps(data)
        else:
            json_str = str(data)
        
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    def decode(self, encoded_data: str) -> Any:
        """Decode base64 string to data."""
        try:
            decoded_bytes = base64.b64decode(encoded_data.encode('utf-8'))
            decoded_str = decoded_bytes.decode('utf-8')
            return json.loads(decoded_str)
        except Exception as e:
            raise ValueError(f"Failed to decode base64 data: {str(e)}")


# ============================================================================
# Handler Registry & Factory
# ============================================================================

_HANDLERS = {
    "base64": Base64EncryptionHandler(),
}


def register_handler(name: str, handler: EncryptionHandler) -> None:
    """
    Register a new encryption handler.
    
    Example:
        from cryptography.fernet import Fernet
        
        class FernetEncryptionHandler(EncryptionHandler):
            def __init__(self, key):
                self.cipher = Fernet(key)
            
            def encode(self, data):
                # implementation
                pass
            
            def decode(self, encoded_data):
                # implementation
                pass
        
        key = Fernet.generate_key()
        register_handler("fernet", FernetEncryptionHandler(key))
    """
    _HANDLERS[name.lower()] = handler


def get_handler(name: str) -> EncryptionHandler:
    """
    Get a registered encryption handler by name.
    
    Args:
        name: Name of the handler (e.g., "base64", "aes", "fernet")
        
    Returns:
        EncryptionHandler instance
        
    Raises:
        ValueError: If handler not found
    """
    handler_name = name.lower()
    if handler_name not in _HANDLERS:
        available = ", ".join(_HANDLERS.keys())
        raise ValueError(
            f"Encryption handler '{name}' not found. "
            f"Available handlers: {available}"
        )
    return _HANDLERS[handler_name]


# ============================================================================
# Legacy Utility Functions (for backward compatibility)
# ============================================================================

def encode_base64(data: Any) -> str:
    """
    Encode data to base64 string.
    
    Args:
        data: Dictionary or JSON serializable object
        
    Returns:
        Base64 encoded string
    """
    handler = get_handler("base64")
    return handler.encode(data)


def decode_base64(encoded_data: str) -> Union[Dict, Any]:
    """
    Decode base64 string to data.
    
    Args:
        encoded_data: Base64 encoded string
        
    Returns:
        Decoded dictionary or object
        
    Raises:
        ValueError: If data cannot be decoded
    """
    handler = get_handler("base64")
    return handler.decode(encoded_data)


def encode_response(data: Any, handler: EncryptionHandler = None) -> Dict[str, str]:
    """
    Encode response data with encryption handler.
    
    Args:
        data: Response data to encode
        handler: EncryptionHandler instance (uses base64 if None)
        
    Returns:
        Dictionary with 'encrypted' key containing encoded data
    """
    if handler is None:
        handler = get_handler("base64")
    
    return {
        "encrypted": handler.encode(data)
    }


def decode_request(encoded_data: str, handler: EncryptionHandler = None) -> Any:
    """
    Decode request data with encryption handler.
    
    Args:
        encoded_data: Encrypted request data
        handler: EncryptionHandler instance (uses base64 if None)
        
    Returns:
        Decoded request data
    """
    if handler is None:
        handler = get_handler("base64")
    
    return handler.decode(encoded_data)
