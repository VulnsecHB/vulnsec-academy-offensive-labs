#!/bin/bash
set -euo pipefail
cp /app/smb.conf /etc/samba/smb.conf
smbd -F
