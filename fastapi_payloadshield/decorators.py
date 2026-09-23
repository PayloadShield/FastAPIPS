"""
Decorators for automatic payload encryption/decryption in FastAPI.
Supports multiple encryption types via the pluggable EncryptionHandler
interface. Configure keys globally with PayloadShieldEnc.init(...) before
using any of these decorators.
"""

import inspect
from functools import wraps
from typing import Any, Callable

from fastapi import Request
from fastapi.responses import JSONResponse

from .config import PayloadShieldEnc
from .crypto import get_handler

_INJECTED_REQUEST_PARAM = "__payloadshield_request__"


def _prepare_request_injection(func: Callable) -> str:
    """
    Ensure the route function's signature (as seen by FastAPI) includes a
    ``Request`` parameter, and return the keyword name it will arrive under.

    FastAPI resolves a route's parameters purely from the function
    signature and always invokes it with keyword arguments, so a decorator
    cannot rely on scanning positional ``args`` to find the ``Request``
    object. If the original function doesn't already declare a
    ``request: Request`` parameter, a synthetic keyword-only one is
    appended to the signature FastAPI sees; the wrapper strips it back out
    before calling the real function.
    """
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        if param.annotation is Request:
            return name

    new_params = list(sig.parameters.values()) + [
        inspect.Parameter(
            _INJECTED_REQUEST_PARAM,
            kind=inspect.Parameter.KEYWORD_ONLY,
            annotation=Request,
        )
    ]
    func.__signature__ = sig.replace(parameters=new_params)
    return _INJECTED_REQUEST_PARAM


def _replace_body_kwarg(kwargs: dict, original_body: Any, decrypted_data: Any) -> dict:
    """Replace the kwarg matching the raw request body with decrypted data."""
    for key, value in kwargs.items():
        if isinstance(value, dict) and value == original_body:
            kwargs[key] = decrypted_data
            break
    return kwargs


def _wrap_encrypted(data: Any) -> dict:
    """Normalize a route's return value into a dict payload before encoding."""
    return data if isinstance(data, dict) else {"data": data}


class PayloadShield:
    """
    Namespace of decorator factories for encrypting/decrypting FastAPI
    request and response payloads.

    Usage:
        PayloadShieldEnc.init({"Key": "..."})

        @app.get("/api/endpoint")
        @PayloadShield.encrypt("base64")
        async def route(): ...

        @app.post("/api/endpoint")
        @PayloadShield.decrypt("base64")
        async def route(data: dict): ...

        @app.post("/api/endpoint")
        @PayloadShield.crypt("base64")
        async def route(data: dict): ...
    """

    @staticmethod
    def encrypt(encryption_type: str = "base64") -> Callable:
        """
        Decorator that encrypts the route's response payload only.

        The response is wrapped as ``{"encrypted": "<encoded-data>"}``.
        """
        handler = get_handler(encryption_type)

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                config = PayloadShieldEnc.get_config()
                encoded = handler.encode(_wrap_encrypted(result), config)
                return JSONResponse(content={"encrypted": encoded})

            return wrapper

        return decorator

    @staticmethod
    def decrypt(encryption_type: str = "base64") -> Callable:
        """
        Decorator that decrypts the incoming request payload only.

        Expects the request body to be ``{"encrypted": "<encoded-data>"}``.
        """
        handler = get_handler(encryption_type)

        def decorator(func: Callable) -> Callable:
            request_kwarg = _prepare_request_injection(func)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.pop(request_kwarg)
                body = await request.json()
                if isinstance(body, dict) and "encrypted" in body:
                    config = PayloadShieldEnc.get_config()
                    try:
                        decrypted = handler.decode(body["encrypted"], config)
                    except Exception as e:
                        return JSONResponse(
                            status_code=400,
                            content={"error": f"Failed to decrypt request: {str(e)}"},
                        )
                    kwargs = _replace_body_kwarg(kwargs, body, decrypted)

                return await func(*args, **kwargs)

            wrapper.__signature__ = func.__signature__
            return wrapper

        return decorator

    @staticmethod
    def crypt(encryption_type: str = "base64") -> Callable:
        """
        Decorator that decrypts the incoming request payload and encrypts
        the outgoing response payload using the same encryption type.
        """
        handler = get_handler(encryption_type)

        def decorator(func: Callable) -> Callable:
            request_kwarg = _prepare_request_injection(func)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                config = PayloadShieldEnc.get_config()
                request: Request = kwargs.pop(request_kwarg)
                body = await request.json()
                if isinstance(body, dict) and "encrypted" in body:
                    try:
                        decrypted = handler.decode(body["encrypted"], config)
                    except Exception as e:
                        return JSONResponse(
                            status_code=400,
                            content={"error": f"Failed to decrypt request: {str(e)}"},
                        )
                    kwargs = _replace_body_kwarg(kwargs, body, decrypted)

                result = await func(*args, **kwargs)
                encoded = handler.encode(_wrap_encrypted(result), config)
                return JSONResponse(content={"encrypted": encoded})

            wrapper.__signature__ = func.__signature__
            return wrapper

        return decorator

