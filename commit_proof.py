import base64
import subprocess
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# -----------------------------------
# Load Student Private Key
# -----------------------------------
def load_private_key():
    with open("student_private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


# -----------------------------------
# Load Instructor Public Key
# -----------------------------------
def load_instructor_public_key():
    with open("instructor_public.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())


# -----------------------------------
# Sign Commit Hash (RSA-PSS-SHA256)
# -----------------------------------
def sign_message(message: str, private_key) -> bytes:
    msg_bytes = message.encode("utf-8")  # IMPORTANT: ASCII string bytes
    signature = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature


# -----------------------------------
# Encrypt Signature using Instructor Public Key (RSA-OAEP-SHA256)
# -----------------------------------
def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


# -----------------------------------
# MAIN PROCESS
# -----------------------------------
def main():
    # 1. Get latest commit hash
    commit_hash = (
        subprocess.check_output(["git", "log", "-1", "--format=%H"])
        .decode()
        .strip()
    )

    print("Commit Hash:", commit_hash)

    # 2. Load keys
    private_key = load_private_key()
    instructor_pub = load_instructor_public_key()

    # 3. Sign hash
    signature = sign_message(commit_hash, private_key)

    # 4. Encrypt signature
    encrypted_sig = encrypt_with_public_key(signature, instructor_pub)

    # 5. Base64 encode
    encrypted_sig_b64 = base64.b64encode(encrypted_sig).decode()

    print("\nEncrypted Signature (Base64):")
    print(encrypted_sig_b64)


if __name__ == "__main__":
    main()
