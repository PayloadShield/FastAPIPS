"""
Client script to test the FastAPI Payload Shield decorators
This script demonstrates how to:
1. Encrypt data before sending as request
2. Decrypt data received as response
"""

import requests
import json
import base64


class Base64CryptoClient:
    """Helper client for interacting with encrypted APIs"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    @staticmethod
    def encrypt_data(data: dict) -> str:
        """Encrypt data to base64"""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted: str) -> dict:
        """Decrypt base64 data"""
        decoded_bytes = base64.b64decode(encrypted.encode())
        return json.loads(decoded_bytes.decode())
    
    def get_encrypted(self, endpoint: str) -> dict:
        """GET request expecting encrypted response"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n📤 GET {url}")
        
        response = self.session.get(url)
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            encrypted_response = response.json()
            decrypted = self.decrypt_data(encrypted_response["encrypted"])
            print(f"🔓 Decrypted Response:")
            print(json.dumps(decrypted, indent=2))
            return decrypted
        else:
            print(f"❌ Error: {response.text}")
            return None
    
    def post_encrypted(self, endpoint: str, data: dict) -> dict:
        """POST request with encrypted data expecting encrypted response"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n📤 POST {url}")
        print(f"📝 Request Data:")
        print(json.dumps(data, indent=2))
        
        encrypted_request = self.encrypt_data(data)
        print(f"🔒 Encrypted Request: {encrypted_request}")
        
        response = self.session.post(url, json={"encrypted": encrypted_request})
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            encrypted_response = response.json()
            print(f"🔒 Encrypted Response: {encrypted_response['encrypted']}")
            
            decrypted = self.decrypt_data(encrypted_response["encrypted"])
            print(f"🔓 Decrypted Response:")
            print(json.dumps(decrypted, indent=2))
            return decrypted
        else:
            print(f"❌ Error: {response.text}")
            return None
    
    def post_encrypted_request_only(self, endpoint: str, data: dict) -> dict:
        """POST request with encrypted data"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n📤 POST {url}")
        print(f"📝 Request Data:")
        print(json.dumps(data, indent=2))
        
        encrypted_request = self.encrypt_data(data)
        print(f"🔒 Encrypted Request: {encrypted_request}")
        
        response = self.session.post(url, json={"encrypted": encrypted_request})
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response (not encrypted):")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None


def main():
    """Test all examples"""
    
    client = Base64CryptoClient()
    
    print("=" * 70)
    print("🔐 FastAPI Base64 Crypto - Client Test Examples")
    print("=" * 70)
    
    # ========================================================================
    # Test 1: Response Encryption Only
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: Response Encryption Only (GET /api/public/users)")
    print("=" * 70)
    client.get_encrypted("/api/public/users")
    
    print("\n" + "-" * 70)
    print("TEST 1B: Response Encryption Only (GET /api/public/users/1)")
    print("-" * 70)
    client.get_encrypted("/api/public/users/1")
    
    # ========================================================================
    # Test 2: Request Decryption Only
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: Request Decryption Only (POST /api/login)")
    print("=" * 70)
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    client.post_encrypted_request_only("/api/login", login_data)
    
    print("\n" + "-" * 70)
    print("TEST 2B: Invalid Login")
    print("-" * 70)
    invalid_login = {
        "username": "invalid",
        "password": "wrong"
    }
    client.post_encrypted_request_only("/api/login", invalid_login)
    
    print("\n" + "-" * 70)
    print("TEST 2C: Email Validation (POST /api/validate-email)")
    print("-" * 70)
    email_data = {
        "email": "test@example.com"
    }
    client.post_encrypted_request_only("/api/validate-email", email_data)
    
    # ========================================================================
    # Test 3: Both Request Decryption and Response Encryption
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: Both Encryption & Decryption (POST /api/update-user/1)")
    print("=" * 70)
    update_data = {
        "name": "Alice Updated",
        "email": "alice.new@example.com",
        "status": "active"
    }
    client.post_encrypted("/api/update-user/1", update_data)
    
    print("\n" + "-" * 70)
    print("TEST 3B: Create Post (POST /api/create-post)")
    print("-" * 70)
    post_data = {
        "title": "My Encrypted Post",
        "content": "This is a secure post content",
        "author_id": 1
    }
    client.post_encrypted("/api/create-post", post_data)
    
    # ========================================================================
    # Test 4: Using Combined Middleware
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 4: Combined Middleware (POST /api/secure-process)")
    print("=" * 70)
    process_data = {
        "operation": "analyze",
        "target": "document",
        "parameters": ["param1", "param2"]
    }
    client.post_encrypted("/api/secure-process", process_data)
    
    # ========================================================================
    # Test 5: Batch Processing
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 5: Batch Processing (POST /api/batch-process)")
    print("=" * 70)
    batch_data = {
        "items": ["item1", "item2", "item3", "item4"]
    }
    client.post_encrypted("/api/batch-process", batch_data)
    
    # ========================================================================
    # Test 6: Health Check (No Encryption)
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 6: Health Check (GET /health - No Encryption)")
    print("=" * 70)
    print("\n📤 GET http://localhost:8000/health")
    response = client.session.get("http://localhost:8000/health")
    print(f"📥 Status: {response.status_code}")
    print(f"📥 Response:")
    print(json.dumps(response.json(), indent=2))
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server at http://localhost:8000")
        print("   Make sure the server is running:")
        print("   python examples/example_app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
