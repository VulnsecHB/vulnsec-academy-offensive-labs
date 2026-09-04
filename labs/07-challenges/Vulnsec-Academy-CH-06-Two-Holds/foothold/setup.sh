#!/bin/bash
set -euo pipefail
useradd -m -s /bin/bash j.pike
echo 'j.pike:tidewatch' | chpasswd
echo 'This is the jump. Flags are inner.' > /home/j.pike/NOTE.txt
chown j.pike:j.pike /home/j.pike/NOTE.txt
ssh-keygen -A
mkdir -p /run/sshd
echo 'Northline Jump 172' > /etc/ssh/banner
