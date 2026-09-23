"""
Example FastAPI application using FastAPI Payload Shield decorators.
Demonstrates PayloadShieldEnc.init() configuration and the
PayloadShield.encrypt / .decrypt / .crypt decorators.
"""

import sys
from pathlib import Path

# Prefer the local, in-repo package over any older version pip-installed in
# site-packages when running this script directly (python examples/example_app.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_payloadshield import PayloadShield, PayloadShieldEnc
import uvicorn

# Fixed demo keys (NOT for production use). They are hard-coded so that
# examples/test_all_crypts.py, running in a separate process, can encrypt
# and decrypt using the exact same keys as this server.

# A single base64-encoded 32-byte key works for both "fernet" (expects a
# url-safe base64 32-byte key) and "aes-gcm-256" (accepts raw or base64
# encoded 32-byte key) handlers.
_SYMMETRIC_KEY = "DsNatYFfZhyT8XI/biG1L4k1qMm9trRBNqnRLNcKnu4="

# RSA key pair for the "rsa-hybrid" handler.
_RSA_PRIVATE_PEM = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDGDavTaqFpieF4
FvGZGMu8sfwbLLnlUXGQCNbIHYJWpiikATM1G6P5NGP4jPwUWR6vxWnWogU9Ycgp
f6GSVtfOM8tvnr2oSWC+HM370EIcW5ZzN0O+atNG6VhW8xTk7nR7fYHfg3sTnRmA
51rXEaxM1i6ts0fHk9aGWAbxetgoiqUfhursW3tWig/q+XrqccMsE70m/c2Y/sIj
n0wpqsWZsA8Ta8RE3zs93I0u09Xecbrw3zZpOI55MZ/jyl9ejVqhQl5ii7p01980
oSA7GrMmOodh5UwYGYaXcFEp0zF+IWrGllVvast3rIHLCbRotnUNLaeGeh6v/MU4
neMMW+8lAgMBAAECggEAI/iRr6lbPa7kO4p3QOYnAtOUxV6/OK4tIQrp75ikdpZh
JUBui4PEqVthmOAKXKu/Dg+d5HSy3O4oi5j5wHlzYqk3lsNPEQSaxIy4wLaXe00L
K0vrSudeDjANcmVd8yJ4F4G5F95qeSp8WlQqxIsaLy5rdfLs44uvV+EfCbbVEa+i
ueSNF1k3cTxDgOb9BP7UkzjwtQcJQIsMcBCi0WGuaegC5vvjFphm1DX2782jczch
uZW6KeLj8hhTag++DsfyzD5/CMDnxA6/JIafEMj2hSpFSLWFxqmyMKplQWcT8zoa
FK+ZhTIoJvNjSnZDMktSdQG7/fQnceTQjz0aSV8e9QKBgQDzUuc9d6OZ/Z1kMhtb
yw8k8Gjc7UACbAnaNONVVOa8ewnQ/RxeeAgw5qwOJE39Pvlr/fesASDlga+yvjvE
bKluz1RJLARPzbb8rgRXBs5c814Uh0NNkdVL5Dy1x0+FBu5rn9TEDfmada5Llu51
Mpk4Fi5RcvuX3Ks0u8zH18vMqwKBgQDQXwRlYzRuz9gSkOAPFB5iki4HOAE78mLZ
4svRR3luffBGPQySwuSlM1znyTx1Tk+TN/9PvkrDw9zpi/MKjk/acCbrnNyH50X6
/sGzeSngKhy5VWDhreplnt1dZ8xGPES2RKLv7jwwtFGnhzLC+VLh5XcGE3246idW
B6cn7WiTbwKBgQDBUu8S8Ul1AgHZJ86A4hcIPFK0pXOj+P7i9f5hP/GLcx5bg57U
l/26DKxLGCE2wqAdY00yxjrC3oUgOPD3oXYE6omHEYfjeAiZPhGIq4muZFYtbULW
ELYtdAugSdkuUlGABR9hHdFhHXr759FSIH+IBmeKoxauk88bONL9PMFZvQKBgGmu
d1VQzmwRYF5yOiGLq6mEyHGC1yVnVvl5TLRVEuKWX0HQfssEq+CZv1oTt2UrlbJu
KUBxnAvUD/wnrdnBugBo92Ryh2sqQlT91pJHNpTp5u2cvulXQtXNkCpqlbFdqd/j
ydv0sXRmUC+uo3E98Op/bjGXuyEJKXA5q27Vuz9jAoGBAKOv/kPHo6jd4ZbA4Uo4
wzsoD5r5DXKw0vdVEdN2EK7fgAus+ZZ1mouT4Ro2uXm+lYKSNPC4PkGzQl3eYNno
kdizFxaLKLoSqUYs4f9e5ky9LVUeu4vTe5y9mT51Y7PjK/jLZnjQOsTX4Q8urJnk
WVFMtaTgWqHRJ3uGc7v0BFjX
-----END PRIVATE KEY-----"""

_RSA_PUBLIC_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxg2r02qhaYnheBbxmRjL
vLH8Gyy55VFxkAjWyB2CVqYopAEzNRuj+TRj+Iz8FFker8Vp1qIFPWHIKX+hklbX
zjPLb569qElgvhzN+9BCHFuWczdDvmrTRulYVvMU5O50e32B34N7E50ZgOda1xGs
TNYurbNHx5PWhlgG8XrYKIqlH4bq7Ft7VooP6vl66nHDLBO9Jv3NmP7CI59MKarF
mbAPE2vERN87PdyNLtPV3nG68N82aTiOeTGf48pfXo1aoUJeYou6dNffNKEgOxqz
JjqHYeVMGBmGl3BRKdMxfiFqxpZVb2rLd6yBywm0aLZ1DS2nhnoer/zFOJ3jDFvv
JQIDAQAB
-----END PUBLIC KEY-----"""

# Configure global encryption keys once at startup, shared by all handlers.
PayloadShieldEnc.init({
    "Key": _SYMMETRIC_KEY,
    "PublicKey": _RSA_PUBLIC_PEM,
    "PrivateKey": _RSA_PRIVATE_PEM,
})

app = FastAPI(title="FastAPI Payload Shield Example")

# Add CORS middleware for client testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Example 1: Response Encryption Only - PayloadShield.encrypt
# ============================================================================

@app.get("/api/public/users")
@PayloadShield.encrypt("base64")
async def get_users():
    """
    Returns list of users with encrypted response.
    Client receives: {"encrypted": "base64_encoded_json"}
    """
    return [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
        {"id": 3, "name": "Charlie", "role": "user"},
    ]


@app.get("/api/public/users/{user_id}")
@PayloadShield.encrypt("base64")
async def get_user(user_id: int):
    """
    Returns single user with encrypted response.
    """
    users = {
        1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
        2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
        3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    }
    return users.get(user_id, {"error": "User not found"})


# ============================================================================
# Example 2: Request Decryption Only - PayloadShield.decrypt
# ============================================================================

@app.post("/api/login")
@PayloadShield.decrypt("base64")
async def login(credentials: dict):
    """
    Expects encrypted request: {"encrypted": "base64_json_with_username_password"}
    Returns: {"status": "success/failed", "token": "..."}
    """
    username = credentials.get("username", "")
    password = credentials.get("password", "")

    # Simple authentication (demo only)
    if username == "admin" and password == "password123":
        return {
            "status": "success",
            "message": "Login successful",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "user_id": 1
        }

    return {
        "status": "failed",
        "message": "Invalid username or password"
    }


@app.post("/api/validate-email")
@PayloadShield.decrypt("base64")
async def validate_email(data: dict):
    """
    Expects encrypted request with email address.
    """
    email = data.get("email", "")
    is_valid = "@" in email and "." in email

    return {
        "email": email,
        "is_valid": is_valid,
        "message": "Valid email" if is_valid else "Invalid email format"
    }


# ============================================================================
# Example 3: Both Request Decryption and Response Encryption - PayloadShield.crypt
# ============================================================================

@app.post("/api/update-user/{user_id}")
@PayloadShield.crypt("base64")
async def update_user(user_id: int, data: dict):
    """
    Expects encrypted request with user updates.
    Returns encrypted response with updated user data.
    """
    updated_user = {
        "id": user_id,
        "name": data.get("name", "Unknown"),
        "email": data.get("email", "unknown@example.com"),
        "status": "updated",
        "changes": list(data.keys())
    }
    return updated_user


@app.post("/api/create-post")
@PayloadShield.crypt("base64")
async def create_post(post_data: dict):
    """
    Expects encrypted request with post content.
    Returns encrypted response with created post.
    """
    post = {
        "id": 1,
        "title": post_data.get("title", "Untitled"),
        "content": post_data.get("content", ""),
        "author_id": post_data.get("author_id", 1),
        "created_at": "2024-01-01T00:00:00Z",
        "status": "published"
    }
    return post


@app.post("/api/secure-process")
@PayloadShield.crypt("base64")
async def secure_process(data: dict):
    """
    Uses PayloadShield.crypt("base64") for both encryption and decryption.
    Expects: {"encrypted": "base64_json"}
    Returns: {"encrypted": "base64_json"}
    """
    processed_data = {
        "original_keys": list(data.keys()),
        "processed": True,
        "item_count": len(data),
        "operation_status": "success",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    return processed_data


@app.post("/api/batch-process")
@PayloadShield.crypt("base64")
async def batch_process(items: dict):
    """
    Process batch items with both request and response encryption.
    """
    item_list = items.get("items", [])
    results = []

    for idx, item in enumerate(item_list):
        results.append({
            "index": idx,
            "original": item,
            "processed": str(item).upper(),
            "length": len(str(item))
        })

    return {
        "total_items": len(item_list),
        "processed_items": len(results),
        "results": results,
        "status": "completed"
    }


# ============================================================================
# Example 4: All Encryption Types - Fixed Data & Echo Round-Trip
#
# One pair of endpoints per supported handler ("base64", "fernet",
# "aes-gcm-256", "rsa-hybrid"):
#   GET  /api/{type}/fixed  -> blank request, returns FIXED_DATA encrypted
#   POST /api/{type}/echo   -> decrypts request, re-encrypts the same data
# See examples/test_all_crypts.py for a client that exercises these and
# reports a pass/fail percentage across every encryption type.
# ============================================================================

FIXED_DATA = {"message": "fixed-payload", "value": 42}

ALL_CRYPT_TYPES = ["base64", "fernet", "aes-gcm-256", "rsa-hybrid"]


def _register_crypt_type_routes(crypt_type: str) -> None:
    """Register /api/{crypt_type}/fixed and /api/{crypt_type}/echo routes."""

    @app.get(f"/api/{crypt_type}/fixed", name=f"{crypt_type}_fixed")
    @PayloadShield.encrypt(crypt_type)
    async def get_fixed():
        return FIXED_DATA

    @app.post(f"/api/{crypt_type}/echo", name=f"{crypt_type}_echo")
    @PayloadShield.crypt(crypt_type)
    async def echo(data: dict):
        return data


for _crypt_type in ALL_CRYPT_TYPES:
    _register_crypt_type_routes(_crypt_type)


# ============================================================================
# Example 5: Health Check (No Encryption)
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint without encryption.
    """
    return {"status": "healthy", "service": "fastapi_payloadshield-example"}


if __name__ == "__main__":
    # Note: reload=True requires passing the app as an import string
    # (e.g. "example_app:app") and is not needed to run this demo.
    uvicorn.run(app, host="0.0.0.0", port=8000)

