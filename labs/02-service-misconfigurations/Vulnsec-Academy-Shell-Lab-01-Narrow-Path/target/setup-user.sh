#!/bin/bash
set -euo pipefail

[ -e /bin/rbash ] || ln -sf /bin/bash /bin/rbash

if ! id l.nash >/dev/null 2>&1; then
  useradd -m -s /bin/rbash -d /home/l.nash l.nash
fi
echo 'l.nash:Nash-Berth-81' | chpasswd

mkdir -p /home/l.nash/bin
# Intentionally no awk — that recipe belongs to Night Wharf.
for cmd in ls cat echo pwd date find whoami; do
  src="$(command -v "$cmd")"
  ln -sfn "$src" "/home/l.nash/bin/$cmd"
done

cat > /home/l.nash/.bash_profile <<'EOF'
export PATH=/home/l.nash/bin
umask 077
EOF
: > /home/l.nash/.bashrc
echo 'SHELL{narrow_user_nash}' > /home/l.nash/user.txt
echo 'SHELL{narrow_root_env}' > /root/root.txt
chmod 400 /root/root.txt
chmod 444 /home/l.nash/user.txt
chmod 444 /home/l.nash/.bash_profile /home/l.nash/.bashrc
chmod 555 /home/l.nash/bin
chown -R l.nash:l.nash /home/l.nash

printf 'l.nash ALL=(root) NOPASSWD: /usr/bin/env\n' > /etc/sudoers.d/lnash
chmod 440 /etc/sudoers.d/lnash

ssh-keygen -A
