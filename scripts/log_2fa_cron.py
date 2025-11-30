#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

import base64
from datetime import datetime, timezone
import os
import sys

try:
    import pyotp
except ImportError:
    print("pyotp not installed", file=sys.stderr)
    sys.exit(1)

SEED_PATH = "/data/seed.txt"

def get_hex_seed():
    try:
        with open(SEED_PATH, "r") as f:
            s = f.read().strip()
            if len(s) == 64 and all(c in "0123456789abcdef" for c in s):
                return s
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"error reading seed: {e}", file=sys.stderr)
    return None

def generate_totp(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    return totp.now()

def main():
    hex_seed = get_hex_seed()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if not hex_seed:
        print(f"{timestamp} - 2FA Code: <no-seed>", flush=True)
        return
    try:
        code = generate_totp(hex_seed)
        print(f"{timestamp} - 2FA Code: {code}", flush=True)
    except Exception as e:
        print(f"{timestamp} - 2FA Code: <error: {e}>", flush=True)

if __name__ == "__main__":
    main()
