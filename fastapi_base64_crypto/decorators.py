"""
Decorators for automatic base64 encryption/decryption in FastAPI
"""

from functools import wraps
from typing import Callable, Any
from fastapi import Request
from fastapi.responses import JSONResponse
from .crypto import encode_response, decode_request


def decrypt_request(func: Callable) -> Callable:
    """
    Decorator to automatically decrypt base64 encoded request payload.
    
    The decorator expects the request body to be a JSON object with an 'encrypted' key
    containing the base64 encoded data. It decodes this and passes the original data
    to the route function.
    
    Usage:
        @app.post("/api/endpoint")
        @decrypt_request
        async def my_route(data: dict):
            # data will be automatically decoded from base64
            return {"message": "success"}
    
    Returns:
        Decorator function
    """
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
                    # Decode the encrypted data
                    decrypted_data = decode_request(body["encrypted"])
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


def encrypt_response(func: Callable) -> Callable:
    """
    Decorator to automatically encrypt response payload with base64.
    
    The decorator intercepts the response and wraps it in a JSON object with
    an 'encrypted' key containing the base64 encoded response.
    
    Usage:
        @app.get("/api/endpoint")
        @encrypt_response
        async def my_route():
            return {"message": "hello", "data": "world"}
    
    Returns:
        Decorator function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        
        # Handle different response types
        if isinstance(result, dict):
            encrypted = encode_response(result)
        else:
            encrypted = encode_response({"data": result})
        
        return JSONResponse(content=encrypted)
    
    return wrapper


# Combination decorator for both encryption and decryption
def crypto_middleware(func: Callable) -> Callable:
    """
    Combined decorator for both request decryption and response encryption.
    
    Usage:
        @app.post("/api/endpoint")
        @crypto_middleware
        async def my_route(data: dict):
            # Automatically decrypts incoming request and encrypts response
            return {"message": "success"}
    
    Returns:
        Decorator function
    """
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
                    decrypted_data = decode_request(body["encrypted"])
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
            encrypted = encode_response(result)
        else:
            encrypted = encode_response({"data": result})
        
        return JSONResponse(content=encrypted)
    
    return wrapper
