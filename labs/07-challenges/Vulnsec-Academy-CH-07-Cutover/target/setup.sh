#!/bin/bash
set -euo pipefail
[ -e /bin/rbash ] || ln -sf /bin/bash /bin/rbash
useradd -m -s /bin/rbash -d /home/m.solis m.solis
passwd -l m.solis
mkdir -p /home/m.solis/bin /home/m.solis/.ssh
cp /app/keys/authorized_keys /home/m.solis/.ssh/authorized_keys
# Copy of python WITHOUT file caps / suid — escape hatch only
PY="$(command -v python3)"
cp "$PY" /home/m.solis/bin/python3
chmod 755 /home/m.solis/bin/python3
for cmd in ls cat echo pwd date whoami; do
  ln -sfn "$(command -v "$cmd")" "/home/m.solis/bin/$cmd"
done
cat > /home/m.solis/.bash_profile <<'EOF'
export PATH=/home/m.solis/bin
umask 077
EOF
: > /home/m.solis/.bashrc
echo 'CH{cutover_user}' > /home/m.solis/user.txt
echo 'CH{cutover_root}' > /root/root.txt
chmod 400 /root/root.txt
chmod 444 /home/m.solis/user.txt /home/m.solis/.bash_profile /home/m.solis/.bashrc
chown -R m.solis:m.solis /home/m.solis
chmod 555 /home/m.solis/bin
# Real interpreter: SUID + cap_setuid (home copy is a different inode)
chmod 4755 "$PY"
if command -v setcap >/dev/null; then
  setcap cap_setuid+ep "$PY" || true
fi
echo 'Linux cutover 3.13.0-24-generic CVE-2015-1328 overlayfs (decoy)' > /etc/issue
echo 'Kernel bait. Use getcap / find SUID on python3.' > /etc/kernel-cve.note
ssh-keygen -A
mkdir -p /run/sshd /var/run/vsftpd/empty /srv/samba/public /srv/ftp
cp /app/ftp/README.txt /srv/ftp/README.txt
cp /app/smb/empty.txt /srv/samba/public/empty.txt
chmod -R a+rX /srv/ftp /srv/samba
echo 'Northline Cutover' > /etc/ssh/banner
