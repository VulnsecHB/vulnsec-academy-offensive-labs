#!/bin/bash
set -euo pipefail

useradd -m -s /bin/bash -d /home/s.crane s.crane
useradd -m -s /bin/bash -d /home/n.quay n.quay
echo 's.crane:Crane-Lock-60' | chpasswd
passwd -l n.quay

mkdir -p /home/n.quay/.ssh
ssh-keygen -t rsa -b 2048 -f /home/n.quay/.ssh/id_rsa -N "" -C "n.quay@northline"
cp /home/n.quay/.ssh/id_rsa.pub /home/n.quay/.ssh/authorized_keys

# Misconfig: world-readable private key and traversable .ssh
chmod 755 /home/n.quay /home/n.quay/.ssh
chmod 644 /home/n.quay/.ssh/id_rsa /home/n.quay/.ssh/id_rsa.pub /home/n.quay/.ssh/authorized_keys
chown -R n.quay:n.quay /home/n.quay

echo 'SSH{left_key_quay}' > /home/n.quay/user.txt
chmod 644 /home/n.quay/user.txt
chown n.quay:n.quay /home/n.quay/user.txt

cat > /home/s.crane/note.txt <<'EOF'
Yard cutover note — s.crane

n.quay's operator key was copied into their home for the berth cutover.
Check the mode on that file before you call it a backup.

SSH as n.quay is key-only. Password is locked.
EOF
chown s.crane:s.crane /home/s.crane/note.txt
chmod 644 /home/s.crane/note.txt

ssh-keygen -A
