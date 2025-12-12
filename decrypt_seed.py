from crypto_utils import load_private_key, decrypt_seed

# Read encrypted seed from file
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed = f.read().strip()

# Load private key
private_key = load_private_key()

# Decrypt
hex_seed = decrypt_seed(encrypted_seed, private_key)

print("Decrypted hex seed:", hex_seed)
print("Length:", len(hex_seed))
