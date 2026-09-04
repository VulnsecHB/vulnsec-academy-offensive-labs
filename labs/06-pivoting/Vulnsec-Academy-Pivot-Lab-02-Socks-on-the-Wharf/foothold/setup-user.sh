#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash n.wharf
echo 'n.wharf:Socks-247' | chpasswd
cat > /home/n.wharf/note.txt << 'EOF'
Scan the inner host 10.24.10.21 through a SOCKS. Do not -L every port.
EOF
chown n.wharf:n.wharf /home/n.wharf/note.txt
ssh-keygen -A
