#!/usr/bin/env python3
import os, base64, pyotp, datetime

SEED_PATH = "/data/seed.txt"

def main():
    try:
        if not os.path.exists(SEED_PATH):
            print("Seed not found", flush=True)
            return
        with open(SEED_PATH) as f:
            hex_seed = f.read().strip()
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
        totp = pyotp.TOTP(base32_seed)
        code = totp.now()
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - 2FA Code: {code}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()
