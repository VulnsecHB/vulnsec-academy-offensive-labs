#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd -- "$script_dir/.." && pwd)"
env_file="$lab_dir/.lab.env"
state_file="$lab_dir/runtime/lab-state.json"
cd -- "$lab_dir"
docker compose down --remove-orphans >/dev/null 2>&1 || true
rm -f -- "$env_file" "$state_file"
echo "Lab 01 stopped and its runtime configuration was removed."
