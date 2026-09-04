#!/bin/bash
set -euo pipefail

[ -e /bin/rbash ] || ln -sf /bin/bash /bin/rbash

if ! id j.reeves >/dev/null 2>&1; then
  useradd -m -s /bin/rbash -d /home/j.reeves j.reeves
fi
echo 'j.reeves:Dockline-1904' | chpasswd

mkdir -p /home/j.reeves/bin
for cmd in ls cat echo pwd date awk whoami; do
  src="$(command -v "$cmd")"
  ln -sfn "$src" "/home/j.reeves/bin/$cmd"
done

cat > /home/j.reeves/.bash_profile <<'EOF'
export PATH=/home/j.reeves/bin
umask 077
EOF
: > /home/j.reeves/.bashrc
echo 'SQLI{night_wharf_user_reeves}' > /home/j.reeves/user.txt
echo 'SQLI{night_wharf_root_hold}' > /root/root.txt
chmod 400 /root/root.txt
chmod 444 /home/j.reeves/user.txt
chmod 444 /home/j.reeves/.bash_profile /home/j.reeves/.bashrc
chmod 555 /home/j.reeves/bin
chown -R j.reeves:j.reeves /home/j.reeves

printf 'j.reeves ALL=(root) NOPASSWD: /usr/bin/find\n' > /etc/sudoers.d/jreeves
chmod 440 /etc/sudoers.d/jreeves

ssh-keygen -A
