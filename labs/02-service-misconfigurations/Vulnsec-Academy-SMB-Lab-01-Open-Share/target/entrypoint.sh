#!/bin/bash
set -euo pipefail
mkdir -p /var/lib/samba/private /run/samba
nmbd -D || true
smbd -D
exec python3 /app/app.py
