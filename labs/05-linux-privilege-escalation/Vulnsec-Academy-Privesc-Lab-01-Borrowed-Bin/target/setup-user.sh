#!/bin/bash
set -euo pipefail

if ! id k.vale >/dev/null 2>&1; then
  useradd -m -s /bin/bash -d /home/k.vale k.vale
fi
echo 'k.vale:Shelf-201' | chpasswd

echo 'LPE{borrowed_bin_shelf}' > /home/k.vale/user.txt
echo 'LPE{borrowed_bin_root}' > /root/root.txt
chmod 644 /home/k.vale/user.txt
chmod 400 /root/root.txt
chown k.vale:k.vale /home/k.vale/user.txt

printf 'k.vale ALL=(root) NOPASSWD: /usr/bin/less\n' > /etc/sudoers.d/kvale
chmod 440 /etc/sudoers.d/kvale

ssh-keygen -A
