# Vulnsec Academy — Privesc Lab 02: Clockwork

Second Linux privilege-escalation lab. SSH is given. **No useful sudo.** A root cron runs a world-writable script.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.208`
- SSH: `r.crane` / `Tick-208`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

Cron is every minute. After you overwrite the script, wait.

## Student scope

You are authorised against a single Northline operator node.

- Target: `10.23.54.208`
- Atlas: `http://127.0.0.1:8888`
- SSH: `r.crane` / `Tick-208`
- Deliverable: user flag and root flag

`sudo -l` will not save you. Look at scheduled jobs and file permissions.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.208`
- SSH 22, HTTP 80 notice
- User r.crane, no sudo
- Root cron every minute: /usr/local/bin/yard-rotate.sh (world-writable)
- Intended path: overwrite script → SUID bash in /tmp (no reverse shell required)
- no-new-privileges:false so SUID works
- User/cron baked at image build

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
