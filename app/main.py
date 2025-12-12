from fastapi import FastAPI, HTTPException
import os
import time
from crypto_utils import load_private_key, decrypt_seed, generate_totp_code, verify_totp_code

app = FastAPI()

DATA_PATH = "/data/seed.txt"


# -------------------------------
# 1. POST /decrypt-seed
# -------------------------------
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: dict):
    try:
        encrypted_seed = payload.get("encrypted_seed")
        if not encrypted_seed:
            raise HTTPException(status_code=400, detail="Missing encrypted_seed")

        private_key = load_private_key()

        # Decrypt seed
        hex_seed = decrypt_seed(encrypted_seed, private_key)

        # Ensure /data exists (inside Docker volume)
        os.makedirs("/data", exist_ok=True)

        # Save seed persistently
        with open(DATA_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        return {"error": "Decryption failed"}


# -------------------------------
# 2. GET /generate-2fa
# -------------------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # Load seed
    with open(DATA_PATH, "r") as f:
        hex_seed = f.read().strip()

    # Generate TOTP code
    code = generate_totp_code(hex_seed)

    # Remaining seconds in 30-sec window
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


# -------------------------------
# 3. POST /verify-2fa
# -------------------------------
@app.post("/verify-2fa")
def verify_2fa(payload: dict):
    code = payload.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # Load seed
    with open(DATA_PATH, "r") as f:
        hex_seed = f.read().strip()

    # Verify with ±30 sec window
    is_valid = verify_totp_code(hex_seed, code)

    return {"valid": is_valid}
