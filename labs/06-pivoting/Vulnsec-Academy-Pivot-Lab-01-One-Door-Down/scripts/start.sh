#!/usr/bin/env bash
set -Eeuo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd -- "$script_dir/.." && pwd)"
env_file="$lab_dir/.lab.env"
runtime_dir="$lab_dir/runtime"
state_file="$runtime_dir/lab-state.json"
compose_log="$(mktemp)"
HIDDEN_NET="10.24.10.0/24"

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
  echo "Error: curl is required to verify Mission Control from the host." >&2
  exit 1
fi


if [[ -f "$env_file" ]]; then
  docker compose --env-file "$env_file" down --remove-orphans >/dev/null 2>&1 || true
  rm -f -- "$env_file"
else
  docker compose down --remove-orphans >/dev/null 2>&1 || true
fi

mkdir -p -- "$runtime_dir"
rm -f -- "$state_file"

if command -v ss >/dev/null 2>&1 && ss -ltnH | awk '{print $4}' | grep -Eq '(^|:)8888$'; then
  echo "Error: TCP port 8888 is already in use. Stop the other lab first." >&2
  exit 1
fi

echo "Starting Pivot Lab 01 — One Door Down..."

target_ip="10.23.54.240"
printf 'TARGET_IP=%s\n' "$target_ip" > "$env_file"

if ! docker compose up -d --build foothold inner >"$compose_log" 2>&1; then
  echo "Error: Docker could not start the lab hosts." >&2
  cat "$compose_log" >&2
  rm -f -- "$env_file"
  exit 1
fi

for svc in foothold inner; do
  container_id="$(docker compose ps -q "$svc")"
  health="starting"
  for _ in {1..40}; do
    health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}starting{{end}}' "$container_id" 2>/dev/null || true)"
    [[ "$health" == "healthy" ]] && break
    sleep 1
  done
  if [[ "${health:-starting}" != "healthy" ]]; then
    echo "Error: $svc started but did not become healthy." >&2
    docker compose logs --no-color "$svc" >&2
    exit 1
  fi
done

# Host must not reach the hidden net; same-bridge container traffic is L2 and still works.
ipt() { if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then sudo iptables "$@"; else iptables "$@"; fi; }
if ipt -S DOCKER-USER >/dev/null 2>&1; then
  ipt -C DOCKER-USER -d "$HIDDEN_NET" -j DROP >/dev/null 2>&1 || ipt -I DOCKER-USER -d "$HIDDEN_NET" -j DROP
else
  echo "Warning: could not add a DOCKER-USER drop for $HIDDEN_NET. If curl to 10.24.10.12 works from Kali, run: sudo iptables -I DOCKER-USER -d $HIDDEN_NET -j DROP" >&2
fi

session_id="$(date +%s)-$(shuf -i 100000-999999 -n 1)"
printf '{"session_id":"%s","target_ip":"%s","port":22}\n' \
  "$session_id" "$target_ip" > "$state_file"

if ! docker compose up -d --build mission-control >"$compose_log" 2>&1; then
  echo "Error: Docker could not start Mission Control." >&2
  cat "$compose_log" >&2
  exit 1
fi

portal_id="$(docker compose ps -q mission-control)"
for _ in {1..40}; do
  portal_health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}starting{{end}}' "$portal_id" 2>/dev/null || true)"
  if [[ "$portal_health" == "healthy" ]] && curl --noproxy '*' --fail --silent --max-time 2 http://127.0.0.1:8888/healthz >/dev/null 2>&1; then
    echo "Lab 01 is ready."
    echo "Mission Control: http://127.0.0.1:8888"
    echo "Foothold SSH: $target_ip:22"
    echo "Hidden staff desk: 10.24.10.12 (not reachable from Kali)"
    exit 0
  fi
  sleep 1
done

echo "Error: Mission Control is not reachable from the host on 127.0.0.1:8888." >&2
docker compose ps >&2
docker compose logs --no-color mission-control >&2
exit 1
