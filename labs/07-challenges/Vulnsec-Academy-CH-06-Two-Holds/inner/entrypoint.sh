#!/bin/bash
set -euo pipefail
cp /app/sshd_config /etc/ssh/sshd_config
exec /usr/sbin/sshd -D
