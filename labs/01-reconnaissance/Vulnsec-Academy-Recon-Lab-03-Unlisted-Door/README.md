# Vulnsec Academy — Recon Lab 03: Unlisted Door

First web-fuzzing lab. The public site does not link the prize. Directory-bust it.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.31`

Stop any other Vulnsec lab first. Linux Docker Engine — see [Linux Docker setup](#linux-docker-setup).

Intended tool: `gobuster` (ffuf is fine). Wordlist: `dirb/common.txt` or equivalent.

## Student scope

You are authorised against a single Northline web host.

- Target: `10.23.54.31`
- Atlas: `http://127.0.0.1:8888`
- Tool: gobuster (or ffuf)
- Directory discovery is in scope. Do not scan other hosts.

The public pages are not the whole site.

## Environment architecture

- Target: static `10.23.54.31`
- HTTP 80 only
- Public pages do not link `/internal/`
- robots.txt lists decoys `/backup/` and `/intranet-old/` (404)
- `/internal/` holds identifier UD-3104
- Teaching objective: gobuster + common.txt

## Linux Docker setup

This package supports Kali Linux or another Linux host with Docker Engine and Docker Compose v2. Run one Vulnsec package at a time.

Install Docker Engine and the Compose v2 plugin using your Linux distribution’s official packages. Ensure the Docker service is running and your user can access it.

Verify the installation:

```bash
docker info
docker compose version
```

From this package directory:

```bash
chmod +x scripts/*.sh
./scripts/start.sh
./scripts/status.sh
```

When finished:

```bash
./scripts/stop.sh
```

Keep the environment local and do not expose intentionally vulnerable services to untrusted networks.
