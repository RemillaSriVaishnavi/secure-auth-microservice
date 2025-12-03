key_path = "student_public.pem"

with open(key_path, "r") as f:
    pem = f.read()

# Convert newline characters to \n
pem_single_line = pem.replace("\n", "\\n")

print("Formatted Public Key ↓")
print(pem_single_line)
