#!/usr/bin/env bash
set -e

# ensure mount points exist
mkdir -p /data /cron

# start cron daemon
service cron start || /etc/init.d/cron start || cron

sleep 1

# Load main cronfile (heartbeat + rotation)
if [ -f /app/cron/cronfile ]; then
  crontab /app/cron/cronfile
fi

# Load 2FA cron job
if [ -f /app/cron/2fa-cron ]; then
  # merge 2fa cron entries with existing crontab
  (crontab -l; cat /app/cron/2fa-cron) | crontab -
fi

# Print final crontab for debugging
echo "------ ACTIVE CRONTAB ------"
crontab -l
echo "----------------------------"

# Start API
exec uvicorn api:app --host 0.0.0.0 --port 8080 --log-level info
