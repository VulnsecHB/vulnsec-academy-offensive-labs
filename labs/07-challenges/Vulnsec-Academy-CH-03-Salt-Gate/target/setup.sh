#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash -d /home/n.briggs n.briggs
echo 'n.briggs:Password1' | chpasswd
echo 'CH{salt_gate_user}' > /home/n.briggs/user.txt
echo 'CH{salt_gate_root}' > /root/root.txt
chmod 400 /root/root.txt
chown n.briggs:n.briggs /home/n.briggs/user.txt
chmod 644 /home/n.briggs/user.txt
PHP_BIN="$(command -v php || true)"
if [[ -n "$PHP_BIN" ]]; then
  cp "$PHP_BIN" /usr/local/bin/php
  chown root:root /usr/local/bin/php
  chmod 4755 /usr/local/bin/php
fi
ssh-keygen -A
mkdir -p /run/sshd
