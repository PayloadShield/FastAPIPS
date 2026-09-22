"""
Decorators for automatic payload encryption/decryption in FastAPI
Supports multiple encryption types via pluggable EncryptionHandler interface
"""

from functools import wraps
from typing import Callable, Any, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from .crypto import (
    EncryptionHandler,
    get_handler,
    encode_response,
    decode_request,
)


# ============================================================================
# PayloadShieldEnc - Response Encryption Decorator
# ============================================================================

def PayloadShieldEnc(encryption_type: str = "base64"):
    """
    Decorator to automatically encrypt response payload.
    
    The decorator intercepts the response and wraps it in a JSON object with
    an 'encrypted' key containing the encrypted response.
    
    Args:
        encryption_type: Type of encryption to use (default: "base64")
                        Options: "base64", "aes", "fernet", etc.
                        Register custom handlers with register_handler()
    
    Usage:
        @app.get("/api/endpoint")
        @PayloadShieldEnc("base64")
        async def my_route():
            return {"message": "hello", "data": "world"}
        
        # Response: {"encrypted": "base64_encoded_data"}
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        handler = get_handler(encryption_type)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Handle different response types
            if isinstance(result, dict):
                encrypted = encode_response(result, handler)
            else:
                encrypted = encode_response({"data": result}, handler)
            
            return JSONResponse(content=encrypted)
        
        return wrapper
    
    return decorator


# ============================================================================
# PayloadShieldDec - Request Decryption Decorator
# ============================================================================

def PayloadShieldDec(encryption_type: str = "base64"):
    """
    Decorator to automatically decrypt encrypted request payload.
    
    The decorator expects the request body to be a JSON object with an 'encrypted' key
    containing the encrypted data. It decodes this and passes the original data
    to the route function.
    
    Args:
        encryption_type: Type of encryption to use (default: "base64")
                        Options: "base64", "aes", "fernet", etc.
                        Register custom handlers with register_handler()
    
    Usage:
        @app.post("/api/endpoint")
        @PayloadShieldDec("base64")
        async def my_route(data: dict):
            # data will be automatically decrypted
            return {"message": "success"}
        
        # Expects: {"encrypted": "encrypted_data"}
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        handler = get_handler(encryption_type)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if first argument is a Request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                try:
                    body = await request.json()
                    if isinstance(body, dict) and "encrypted" in body:
                        # Decrypt the encrypted data
                        decrypted_data = decode_request(body["encrypted"], handler)
                        # Replace the request body in kwargs
                        for key, value in kwargs.items():
                            if isinstance(value, dict) and value == body:
                                kwargs[key] = decrypted_data
                                break
                except Exception as e:
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Failed to decrypt request: {str(e)}"}
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# ============================================================================
# PayloadShield - Combined Encryption & Decryption Decorator
# ============================================================================

def PayloadShield(encryption_type: str = "base64"):
    """
    Combined decorator for both request decryption and response encryption.
    
    Automatically handles both incoming encrypted requests and outgoing encrypted responses.
    
    Args:
        encryption_type: Type of encryption to use (default: "base64")
                        Options: "base64", "aes", "fernet", etc.
                        Register custom handlers with register_handler()
    
    Usage:
        @app.post("/api/endpoint")
        @PayloadShield("base64")
        async def my_route(data: dict):
            # Automatically decrypts incoming request and encrypts response
            return {"message": "success"}
        
        # Expects: {"encrypted": "encrypted_data"}
        # Returns: {"encrypted": "encrypted_data"}
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        handler = get_handler(encryption_type)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Handle request decryption
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                try:
                    body = await request.json()
                    if isinstance(body, dict) and "encrypted" in body:
                        decrypted_data = decode_request(body["encrypted"], handler)
                        for key, value in kwargs.items():
                            if isinstance(value, dict) and value == body:
                                kwargs[key] = decrypted_data
                                break
                except Exception as e:
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Failed to decrypt request: {str(e)}"}
                    )
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Handle response encryption
            if isinstance(result, dict):
                encrypted = encode_response(result, handler)
            else:
                encrypted = encode_response({"data": result}, handler)
            
            return JSONResponse(content=encrypted)
        
        return wrapper
    
    return decorator


# ============================================================================
# Backward Compatibility - Old Decorator Names
# ============================================================================

def encrypt_response(func: Callable) -> Callable:
    """
    Deprecated: Use PayloadShieldEnc("base64") instead.
    
    Decorator to automatically encrypt response payload with base64.
    """
    return PayloadShieldEnc("base64")(func)


def decrypt_request(func: Callable) -> Callable:
    """
    Deprecated: Use PayloadShieldDec("base64") instead.
    
    Decorator to automatically decrypt base64 encoded request payload.
    """
    return PayloadShieldDec("base64")(func)


def crypto_middleware(func: Callable) -> Callable:
    """
    Deprecated: Use PayloadShield("base64") instead.
    
    Combined decorator for both request decryption and response encryption.
    """
    return PayloadShield("base64")(func)
