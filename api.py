from fastapi import FastAPI, HTTPException, Request
import base64
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp
import time

app = FastAPI()
SEED_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "student_private.pem"

# Helper: Decrypt seed
def decrypt_seed_b64(encrypted_seed_b64: str) -> str:
    if not os.path.exists(PRIVATE_KEY_PATH):
        raise HTTPException(status_code=500, detail="Private key missing")
    
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    hex_seed = decrypted_bytes.decode("utf-8")
    if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
        raise HTTPException(status_code=500, detail="Invalid decrypted seed")
    return hex_seed

# Endpoint 1: Decrypt seed
@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request: Request):
    data = await request.json()
    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        raise HTTPException(status_code=400, detail="Missing encrypted_seed")
    
    try:
        hex_seed = decrypt_seed_b64(encrypted_seed)
        # Save seed to file
        with open(SEED_PATH, "w") as f:
            f.write(hex_seed)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Decryption failed")

# Endpoint 2: Generate 2FA TOTP
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    
    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()
    
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    code = totp.now()
    
    # Calculate remaining seconds in period
    valid_for = 30 - (int(time.time()) % 30)
    
    return {"code": code, "valid_for": valid_for}

# Endpoint 3: Verify 2FA TOTP
@app.post("/verify-2fa")
async def verify_2fa(request: Request):
    data = await request.json()
    code = data.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    
    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()
    
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    valid = totp.verify(code, valid_window=1)  # ±30s
    return {"valid": valid}
