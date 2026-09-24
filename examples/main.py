from fastapi import FastAPI
from fastapi_payloadshield import PayloadShield, PayloadShieldEnc

#
# python -m uvicorn main:app --reload
# pip install -e .
#

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0",
)

key = "12345678901234567890123456789012"

PayloadShieldEnc.init({
    "Key": key,               # symmetric key: fernet, aes-gcm-256
    "PrivateKey": "private.pem",   # RSA/hybrid private key (file path or PEM content)
    "PublicKey": "public.pem",    # RSA/hybrid public key (file path or PEM content)
})

@app.get("/base")
@PayloadShield.encrypt("base64")
def root():
    return {
        "message": "Hello, FastAPI!"
    }

@app.post("/base/dec")
@PayloadShield.decrypt("base64")
def decrypt_payload(data: dict):
    return data

@app.post("/base/cry")
@PayloadShield.crypt("base64")
def decrypt_payload(data: dict):
    return data


@app.get("/aes")
@PayloadShield.encrypt("aes-gcm-256")
def root():
    return {
        "message": "Hello, FastAPI!"
    }

@app.post("/aes/dec")
@PayloadShield.decrypt("aes-gcm-256")
def decrypt_payload(data: dict):
    return data

@app.post("/aes/cry")
@PayloadShield.crypt("aes-gcm-256")
def decrypt_payload(data: dict):
    return data


@app.get("/fernet")
@PayloadShield.encrypt("fernet")
def root():
    return {
        "message": "Hello, FastAPI!"
    }

@app.post("/fernet/dec")
@PayloadShield.decrypt("fernet")
def decrypt_payload(data: dict):
    return data

@app.post("/fernet/cry")
@PayloadShield.crypt("fernet")
def decrypt_payload(data: dict):
    return data

@app.get("/rsa")
@PayloadShield.encrypt("rsa-hybrid")
def root():
    return {
        "message": "Hello, FastAPI!"
    }

@app.post("/rsa/dec")
@PayloadShield.decrypt("rsa-hybrid")
def decrypt_payload(data: dict):
    return data

@app.post("/rsa/cry")
@PayloadShield.crypt("rsa-hybrid")
def decrypt_payload(data: dict):
    return data

@app.get("/chacha")
@PayloadShield.encrypt("chacha20-poly1305")
def root():
    return {
        "message": "Hello, FastAPI!"
    }

@app.post("/chacha/dec")
@PayloadShield.decrypt("chacha20-poly1305")
def decrypt_payload(data: dict):
    return data

@app.post("/chacha/cry")
@PayloadShield.crypt("chacha20-poly1305")
def decrypt_payload(data: dict):
    return data

@app.get("/health")
def health():
    return {
        "status": "ok"
    }