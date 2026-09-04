#!/bin/bash
set -euo pipefail
mkdir -p /run/sshd
/usr/sbin/sshd
exec sleep infinity
