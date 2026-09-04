#!/bin/bash
set -euo pipefail

if ! id s.quay >/dev/null 2>&1; then
  useradd -m -s /bin/bash -d /home/s.quay s.quay
fi
echo 's.quay:Tide-214' | chpasswd

echo 'LPE{setuid_tide_user}' > /home/s.quay/user.txt
echo 'LPE{setuid_tide_root}' > /root/root.txt
chmod 644 /home/s.quay/user.txt
chmod 400 /root/root.txt
chown s.quay:s.quay /home/s.quay/user.txt

cp /usr/bin/env /usr/local/bin/yard-report
chown root:root /usr/local/bin/yard-report
chmod 4755 /usr/local/bin/yard-report

ssh-keygen -A
