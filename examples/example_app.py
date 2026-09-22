"""
Example FastAPI application using FastAPI Payload Shield decorators
Demonstrates PayloadShieldEnc, PayloadShieldDec, and PayloadShield decorators
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_payloadshield import PayloadShieldEnc, PayloadShieldDec, PayloadShield
import uvicorn

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
# Example 1: Response Encryption Only - PayloadShieldEnc
# ============================================================================

@app.get("/api/public/users")
@PayloadShieldEnc("base64")
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
@PayloadShieldEnc("base64")
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
# Example 2: Request Decryption Only - PayloadShieldDec
# ============================================================================

@app.post("/api/login")
@PayloadShieldDec("base64")
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
@PayloadShieldDec("base64")
async def validate_email(data: dict):
    """
    Expects encrypted request with email address.
    Returns validation result (encrypted by default, but we don't use decorator here)
    """
    email = data.get("email", "")
    is_valid = "@" in email and "." in email
    
    return {
        "email": email,
        "is_valid": is_valid,
        "message": "Valid email" if is_valid else "Invalid email format"
    }


# ============================================================================
# Example 3: Both Request Decryption and Response Encryption - PayloadShield
# ============================================================================

@app.post("/api/update-user/{user_id}")
@PayloadShield("base64")
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
@PayloadShield("base64")
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


# ============================================================================
# Example 4: Using PayloadShield Combined Decorator
# ============================================================================

@app.post("/api/secure-process")
@PayloadShield("base64")
async def secure_process(data: dict):
    """
    Uses @PayloadShield("base64") for both encryption and decryption in one decorator.
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


# ============================================================================
# Example 5: Health Check (No Encryption)
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint without encryption.
    """
    return {"status": "healthy", "service": "fastapi_payloadshield-example"}


# ============================================================================
# Example 6: Multiple Operations with Encryption
# ============================================================================

@app.post("/api/batch-process")
@PayloadShield("base64")
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
# Startup prints
# ============================================================================

print("🚀 FastAPI Payload Shield Example Started")
print("📝 Using Decorators:")
print("  PayloadShieldEnc('base64')       - Encrypt response only")
print("  PayloadShieldDec('base64')       - Decrypt request only")
print("  PayloadShield('base64')          - Both encrypt & decrypt")
print("\n📝 Endpoints:")
print("  GET  /api/public/users           - Get all users (encrypted response)")
print("  GET  /api/public/users/{id}      - Get single user (encrypted response)")
print("  POST /api/login                  - Login (encrypted request)")
print("  POST /api/validate-email         - Validate email (encrypted request)")
print("  POST /api/update-user/{id}       - Update user (encrypted request/response)")
print("  POST /api/create-post            - Create post (encrypted request/response)")
print("  POST /api/secure-process         - Secure process (encrypted request/response)")
print("  POST /api/batch-process          - Batch process (encrypted request/response)")
print("  GET  /health                     - Health check (no encryption)")
print("\n💡 To use a different encryption type, pass it to the decorator:")
print("  @PayloadShieldEnc('aes')         - AES encryption (when registered)")
print("  @PayloadShieldEnc('fernet')      - Fernet encryption (when registered)")
print("\n📚 Swagger UI: http://localhost:8000/docs")
print("📖 ReDoc: http://localhost:8000/redoc")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
