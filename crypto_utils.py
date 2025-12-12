import base64
import pyotp
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


def load_private_key():
    """Load your RSA private key from PEM file."""
    with open("student_private.pem", "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
        )


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """Decrypt encrypted seed using RSA-OAEP SHA-256."""

    # 1. Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # 2. RSA/OAEP decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3. Convert bytes → string
    hex_seed = decrypted_bytes.decode().strip()

    # 4. Validate: must be 64-char hex
    if len(hex_seed) != 64:
        raise ValueError("Decrypted seed is not 64 characters long")

    allowed = "0123456789abcdef"
    if not all(c in allowed for c in hex_seed.lower()):
        raise ValueError("Decrypted seed contains invalid characters")

    return hex_seed


# ------------------------------
# TOTP IMPLEMENTATION (STEP 6)
# ------------------------------

def hex_to_base32(hex_seed: str) -> str:
    """Convert 64-char hex seed → base32"""
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    """Generate a 6-digit TOTP code using SHA-1 & 30s period."""
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)  # SHA-1 default
    return totp.now()   # returns a string like "123456"


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """Verify a TOTP code with ±30s window tolerance."""
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)
