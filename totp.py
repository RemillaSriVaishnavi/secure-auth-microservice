import base64
import pyotp

# Read hex seed
with open("seed.txt", "r") as f:
    hex_seed = f.read().strip()  # 64-character hex string

def generate_totp_code(hex_seed: str) -> str:
    # 1. Convert hex seed to bytes
    seed_bytes = bytes.fromhex(hex_seed)
    
    # 2. Convert bytes to base32
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # 3. Create TOTP object
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    
    # 4. Generate current TOTP code
    code = totp.now()
    
    return code

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    
    # Verify code with ±valid_window periods (default ±30s)
    return totp.verify(code, valid_window=valid_window)

# Generate code
totp_code = generate_totp_code(hex_seed)
print("Current TOTP code:", totp_code)

# Optional: verify immediately
is_valid = verify_totp_code(hex_seed, totp_code)
print("Verification result:", is_valid)
