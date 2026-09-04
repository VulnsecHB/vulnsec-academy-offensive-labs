#!/usr/bin/env bash
set -Eeuo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd -- "$script_dir/.." && pwd)"
runtime_dir="$lab_dir/runtime"
state_file="$runtime_dir/lab-state.json"
compose_log="$(mktemp)"

cleanup() { rm -f -- "$compose_log"; }
trap cleanup EXIT
cd -- "$lab_dir"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: Docker is not installed or is not available in this terminal." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Error: Docker Compose v2 is not available." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Error: the Docker Engine service is not running or this terminal cannot access it." >&2
  exit 1
fi
if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required to verify Atlas from the host." >&2
  exit 1
fi

docker compose down --remove-orphans >/dev/null 2>&1 || true
mkdir -p -- "$runtime_dir"

if command -v ss >/dev/null 2>&1 && ss -ltnH | awk '{print $4}' | grep -Eq '(^|:)8888$'; then
  echo "Error: TCP port 8888 is already in use. Stop the other lab first." >&2
  exit 1
fi

session_id="$(date +%s)-$(shuf -i 100000-999999 -n 1)"
printf '{"session_id":"%s","mode":"class"}\n' "$session_id" > "$state_file"

echo "Starting Class 00 — Operator Foundations..."
if ! docker compose up -d --build mission-control >"$compose_log" 2>&1; then
  echo "Error: Docker could not start Atlas." >&2
  cat "$compose_log" >&2
  exit 1
fi

portal_id="$(docker compose ps -q mission-control)"
for _ in {1..40}; do
  portal_health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}starting{{end}}' "$portal_id" 2>/dev/null || true)"
  if [[ "$portal_health" == "healthy" ]] && curl --noproxy '*' --fail --silent --max-time 2 http://127.0.0.1:8888/healthz >/dev/null 2>&1; then
    echo "Class 00 is ready."
    echo "Atlas: http://127.0.0.1:8888"
    echo "No target — this is the lecture. Labs start with First Sweep."
    exit 0
  fi
  sleep 1
done

echo "Error: Atlas is not reachable from the host on 127.0.0.1:8888." >&2
docker compose ps >&2
docker compose logs --no-color mission-control >&2
exit 1
