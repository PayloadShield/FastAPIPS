"""
Example FastAPI application using FastAPI Payload Shield decorators.
Demonstrates PayloadShieldEnc.init() configuration and the
PayloadShield.encrypt / .decrypt / .crypt decorators.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_payloadshield import PayloadShield, PayloadShieldEnc
import uvicorn

# Configure global encryption keys once at startup.
PayloadShieldEnc.init({
    "Key": "my-demo-symmetric-key",
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
# Example 4: Health Check (No Encryption)
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint without encryption.
    """
    return {"status": "healthy", "service": "fastapi_payloadshield-example"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

