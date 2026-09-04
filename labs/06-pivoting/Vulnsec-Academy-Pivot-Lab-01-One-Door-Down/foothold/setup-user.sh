#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash p.keel
echo 'p.keel:Berth-240' | chpasswd
cat > /home/p.keel/note.txt << 'EOF'
Yard desk is not on this box.
Staff HTTP: 10.24.10.12
You cannot reach it from the operator laptop. Tunnel.
EOF
chown p.keel:p.keel /home/p.keel/note.txt
ssh-keygen -A
