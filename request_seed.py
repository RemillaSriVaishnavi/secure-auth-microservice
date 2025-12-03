import json
import requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"
STUDENT_ID = "23A91A05I4"
GITHUB_REPO_URL = "https://github.com/RemillaSriVaishnavi/secure-auth-microservice"

# 1. Read public key file (keep actual newlines)
with open("student_public.pem", "r") as f:
    public_key = f.read().strip()

payload = {
    "student_id": STUDENT_ID,
    "github_repo_url": GITHUB_REPO_URL,
    "public_key": public_key
}

# 2. Send POST request
response = requests.post(API_URL, json=payload, timeout=10)
data = response.json()
print("Response:", data)

# 3. Save encrypted seed safely
if data.get("encrypted_seed"):
    with open("encrypted_seed.txt", "w") as f:
        f.write(data["encrypted_seed"])
    print("encrypted_seed.txt saved successfully.")
else:
    print("Failed to get encrypted seed. Check the error above.")
