import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Load private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

# Read encrypted seed
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    # 1. Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    
    # 2. RSA/OAEP Decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 3. Decode bytes to UTF-8 string
    hex_seed = decrypted_bytes.decode('utf-8')
    
    # 4. Validate
    if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Decrypted seed is invalid!")
    
    # 5. Return
    return hex_seed

# Decrypt
hex_seed = decrypt_seed(encrypted_seed_b64, private_key)
print("Decrypted seed:", hex_seed)

# Optional: save to /data/seed.txt (inside Docker, you may need to adjust path)
with open("/data/seed.txt", "w") as f:
    f.write(hex_seed)
