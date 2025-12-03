from datetime import datetime

with open("/cron/rotation.log", "a") as f:
    f.write(f"{datetime.utcnow()} - log rotation executed\n")
