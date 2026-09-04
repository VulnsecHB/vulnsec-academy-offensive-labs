#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash -d /home/c.drake c.drake
echo 'c.drake:harbour21' | chpasswd
echo 'CH{inner_tide_user}' > /home/c.drake/user.txt
chown c.drake:c.drake /home/c.drake/user.txt
chmod 644 /home/c.drake/user.txt
ssh-keygen -A
mkdir -p /run/sshd
echo 'Northline Edge 151' > /etc/ssh/banner
