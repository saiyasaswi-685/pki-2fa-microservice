from crypto_utils import generate_totp_code, verify_totp_code

hex_seed = "203339e09470952aa4ba8096d15bd2594f9881f9fe3d4c278769de6506f4e91b"

code = generate_totp_code(hex_seed)
print("Generated Code:", code)

print("Valid?", verify_totp_code(hex_seed, code))
