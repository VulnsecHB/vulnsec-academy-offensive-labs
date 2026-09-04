#!/bin/bash
set -euo pipefail

if ! id l.peel >/dev/null 2>&1; then
  useradd -m -s /bin/bash -d /home/l.peel l.peel
fi
echo 'l.peel:Loud-221' | chpasswd

echo 'LPE{loud_enumerator_user}' > /home/l.peel/user.txt
echo 'LPE{loud_enumerator_root}' > /root/root.txt
chmod 644 /home/l.peel/user.txt
chmod 400 /root/root.txt
chown l.peel:l.peel /home/l.peel/user.txt

# Decoy: MOTD claims an old kernel. uname -r is the truth; do not run kernel PoCs.
cat > /etc/motd << 'EOF'
Northline enumerator node
Build note: kernel 4.4.0-dirty (see LES). Do not reboot.
EOF

# Decoy: user-level cron, not root.
printf '* * * * * l.peel echo heartbeat >> /tmp/heartbeat.log\n' > /etc/cron.d/heartbeat
chmod 644 /etc/cron.d/heartbeat

# Real path: file capabilities on CPython.
py="$(readlink -f /usr/local/bin/python3)"
setcap cap_setuid+ep "$py"
getcap "$py"

ssh-keygen -A
