#!/bin/bash
set -euo pipefail
cp /app/sshd_config /etc/ssh/sshd_config
cp /app/banner /etc/ssh/banner
/usr/sbin/sshd
exec python3 /app/app.py
