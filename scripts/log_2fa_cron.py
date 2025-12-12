import os
import time
from crypto_utils import generate_totp_code

SEED_PATH = "/data/seed.txt"
LOG_PATH = "/cron/last_code.txt"

def main():
    if not os.path.exists(SEED_PATH):
        with open(LOG_PATH, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Seed not found\n")
        return

    try:
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_PATH, "a") as f:
            f.write(f"{timestamp} - 2FA Code: {code}\n")

    except Exception as e:
        with open(LOG_PATH, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error: {str(e)}\n")


if __name__ == "__main__":
    main()
