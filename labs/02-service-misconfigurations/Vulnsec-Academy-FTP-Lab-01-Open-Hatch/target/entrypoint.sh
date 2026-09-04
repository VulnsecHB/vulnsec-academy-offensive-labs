#!/bin/bash
set -euo pipefail
mkdir -p /var/run/vsftpd/empty
vsftpd /etc/vsftpd.conf
exec python3 /app/app.py
