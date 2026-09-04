#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash r.hold
echo 'r.hold:Jump-254' | chpasswd
cat > /home/r.hold/well.txt << 'EOF'
Second hop:
  k.well@10.24.10.30
  password: Deep-Hold
The flag is not on that box.
EOF
chown r.hold:r.hold /home/r.hold/well.txt
ssh-keygen -A
