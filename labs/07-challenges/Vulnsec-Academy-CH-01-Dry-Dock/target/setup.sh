#!/bin/bash
set -euo pipefail

useradd -m -s /bin/bash -d /home/m.holden m.holden
echo 'm.holden:sunshine' | chpasswd

echo 'CH{dry_dock_user}' > /home/m.holden/user.txt
chmod 644 /home/m.holden/user.txt
chown m.holden:m.holden /home/m.holden/user.txt

echo 'CH{dry_dock_root}' > /root/root.txt
chmod 400 /root/root.txt

printf 'm.holden ALL=(root) NOPASSWD: /usr/bin/tar\n' > /etc/sudoers.d/mholden
chmod 440 /etc/sudoers.d/mholden

ssh-keygen -A
mkdir -p /var/run/vsftpd/empty /run/sshd
