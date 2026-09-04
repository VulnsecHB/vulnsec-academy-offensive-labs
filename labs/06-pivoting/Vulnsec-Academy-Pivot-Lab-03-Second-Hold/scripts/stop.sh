#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd -- "$script_dir/.." && pwd)"
env_file="$lab_dir/.lab.env"
state_file="$lab_dir/runtime/lab-state.json"
cd -- "$lab_dir"
docker compose down --remove-orphans >/dev/null 2>&1 || true
rm -f -- "$env_file" "$state_file"
ipt() { if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then sudo iptables "$@"; else iptables "$@"; fi; }
ipt -D DOCKER-USER -d 10.24.10.0/24 -j DROP >/dev/null 2>&1 || true
ipt -D DOCKER-USER -d 10.24.20.0/24 -j DROP >/dev/null 2>&1 || true
echo "Lab 03 stopped and its runtime configuration was removed."
