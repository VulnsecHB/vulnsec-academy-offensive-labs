# Vulnsec Academy — SSH Lab 01: Left Key

First SSH-key lab. A low operator can read another user’s private key.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.60`
- SSH: `s.crane` / `Crane-Lock-60`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

Tools stay on Kali: `ssh`, `scp`, `chmod`.

## Student scope

You are authorised against a single Northline operator node.

- Target: `10.23.54.60`
- Atlas: `http://127.0.0.1:8888`
- SSH: `s.crane` / `Crane-Lock-60`
- Deliverable: flag from the second account

Do not brute the second user. Look at files you can already read.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.60`
- SSH 22 + HTTP 80 notice
- s.crane password: Crane-Lock-60
- n.quay: password locked, PubkeyAuthentication only
- Misconfig: `/home/n.quay/.ssh/id_rsa` mode 644, `.ssh` 755
- Flag: `SSH{left_key_quay}` in `/home/n.quay/user.txt`
- StrictModes no so the world-readable key still authenticates n.quay

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
