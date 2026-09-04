#!/bin/bash
set -euo pipefail
cp /app/sshd_config /etc/ssh/sshd_config
/usr/sbin/sshd
exec python3 /app/app.py
