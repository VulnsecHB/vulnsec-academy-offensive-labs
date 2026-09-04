#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd -- "$script_dir/.." && pwd)"
env_file="$lab_dir/.lab.env"
state_file="$lab_dir/runtime/lab-state.json"
cd -- "$lab_dir"
if [[ ! -f "$env_file" ]]; then
  echo "Lab 01 is already stopped."
  exit 0
fi
docker compose --env-file "$env_file" down --remove-orphans
rm -f -- "$env_file" "$state_file"
echo "Lab 01 stopped and its runtime configuration was removed."
