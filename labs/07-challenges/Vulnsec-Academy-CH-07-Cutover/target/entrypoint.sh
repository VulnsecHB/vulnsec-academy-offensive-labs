#!/bin/bash
set -euo pipefail
cp /app/sshd_config /etc/ssh/sshd_config
cp /app/smb.conf /etc/samba/smb.conf
cp /app/vsftpd.conf /etc/vsftpd.conf
smbd -D
vsftpd /etc/vsftpd.conf
/usr/sbin/sshd
exec python3 /app/app.py
