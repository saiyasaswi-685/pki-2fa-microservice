# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64, os, time
import pyotp
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

app = FastAPI()
SEED_PATH = "/data/seed.txt"

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

def load_private_key():
    with open("student_private.pem", "rb") as f:
        return load_pem_private_key(f.read(), password=None)

@app.post("/decrypt-seed")
async def decrypt_seed(req: DecryptRequest):
    try:
        private_key = load_private_key()
        ct = base64.b64decode(req.encrypted_seed)
        decrypted = private_key.decrypt(
            ct,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        hex_seed = decrypted.decode("utf-8").strip()
        if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
            raise Exception("Invalid seed format")
        os.makedirs("/data", exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(hex_seed)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Decryption failed", "reason": str(e)})

@app.get("/generate-2fa")
async def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    with open(SEED_PATH) as f:
        hex_seed = f.read().strip()
    try:
        seed_bytes = bytes.fromhex(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Invalid seed stored"})
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(base32_seed)  # SHA1, 30s, 6 digits by default
    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail={"error": "Missing code"})
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    with open(SEED_PATH) as f:
        hex_seed = f.read().strip()
    try:
        seed_bytes = bytes.fromhex(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Invalid seed stored"})
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(base32_seed)
    valid = totp.verify(req.code, valid_window=1)
    return {"valid": valid}
