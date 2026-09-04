#!/bin/bash
set -euo pipefail
cp /app/smb.conf /etc/samba/smb.conf
cp /app/sshd_config /etc/ssh/sshd_config
cp /app/vsftpd.conf /etc/vsftpd.conf
cp /app/banner /etc/ssh/banner
smbd -D
nmbd -D || true
vsftpd /etc/vsftpd.conf
/usr/sbin/sshd
exec python3 /app/app.py
