#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd -- "$script_dir/.." && pwd)"
cd -- "$lab_dir"
if [[ -z "$(docker compose ps -q 2>/dev/null || true)" ]]; then
  echo "Lab 03 is not running."
  exit 0
fi
docker compose ps
if curl --noproxy '*' --fail --silent --max-time 2 http://127.0.0.1:8888/healthz >/dev/null 2>&1; then
  echo "Mission Control is responding on http://127.0.0.1:8888"
else
  echo "Mission Control is not responding yet."
fi
