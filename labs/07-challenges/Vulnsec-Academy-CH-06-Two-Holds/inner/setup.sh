#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash p.moss
passwd -l p.moss
mkdir -p /home/p.moss/.ssh
cp /app/keys/authorized_keys /home/p.moss/.ssh/authorized_keys
echo 'CH{two_holds_user}' > /home/p.moss/user.txt
echo 'CH{two_holds_root}' > /root/root.txt
chmod 400 /root/root.txt
chown -R p.moss:p.moss /home/p.moss
chmod 644 /home/p.moss/user.txt /home/p.moss/.ssh/authorized_keys
printf 'p.moss ALL=(root) NOPASSWD: /usr/bin/zip\n' > /etc/sudoers.d/pmoss
chmod 440 /etc/sudoers.d/pmoss
ssh-keygen -A
mkdir -p /run/sshd
echo 'Northline inner hold' > /etc/ssh/banner
