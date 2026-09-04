#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash k.well
echo 'k.well:Deep-Hold' | chpasswd
cat > /home/k.well/vault.txt << 'EOF'
Vault HTTP is on the deep net:
  http://10.24.20.5/
Kali has no route there. Forward through this hop.
EOF
chown k.well:k.well /home/k.well/vault.txt
ssh-keygen -A
