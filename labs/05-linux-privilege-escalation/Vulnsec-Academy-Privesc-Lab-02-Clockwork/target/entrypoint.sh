#!/bin/bash
set -euo pipefail
mkdir -p /run/sshd /var/run
cron
/usr/sbin/sshd
exec python3 /app/app.py
