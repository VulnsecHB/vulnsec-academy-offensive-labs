# Vulnsec Academy — SMB Lab 01: Open Share

First SMB lab. Guest share, read-only. Pull the yard ledger.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.74`
- Service: SMB 139/445 (guest)

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

Tools stay on Kali: `nmap`, `smbclient`.

## Student scope

You are authorised against a single Northline records host.

- Target: `10.23.54.74`
- Atlas: `http://127.0.0.1:8888`
- Expected: SMB on 139/445
- Deliverable: flag from the yard ledger

Guest list and get only. Ignore IPC$. Do not attack the Samba version.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.74`
- Samba standalone, map to guest = Bad User
- Share `records` at `/srv/samba/records`, guest ok, read only
- Files: README.txt, yard-ledger.txt
- Flag: `SMB{open_share_yard}`
- HTTP 80 records notice only

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
