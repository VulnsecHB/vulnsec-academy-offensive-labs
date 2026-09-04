#!/bin/bash
set -euo pipefail

if ! id r.crane >/dev/null 2>&1; then
  useradd -m -s /bin/bash -d /home/r.crane r.crane
fi
echo 'r.crane:Tick-208' | chpasswd

echo 'LPE{clockwork_tick}' > /home/r.crane/user.txt
echo 'LPE{clockwork_root}' > /root/root.txt
chmod 644 /home/r.crane/user.txt
chmod 400 /root/root.txt
chown r.crane:r.crane /home/r.crane/user.txt

cat > /usr/local/bin/yard-rotate.sh << 'EOF'
#!/bin/bash
echo "$(date -Iseconds) yard rotate ok" >> /var/log/yard-rotate.log
EOF
chmod 777 /usr/local/bin/yard-rotate.sh
chown root:root /usr/local/bin/yard-rotate.sh

printf '* * * * * root /bin/bash /usr/local/bin/yard-rotate.sh\n' > /etc/cron.d/yard-rotate
chmod 644 /etc/cron.d/yard-rotate

touch /var/log/yard-rotate.log
chmod 644 /var/log/yard-rotate.log

ssh-keygen -A
