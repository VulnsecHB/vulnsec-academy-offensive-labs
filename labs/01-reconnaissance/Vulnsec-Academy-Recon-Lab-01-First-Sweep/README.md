# Vulnsec Academy — Recon Lab 01: First Sweep

First nmap lab. One assigned host. Read the scan. Confirm what is open. There is no exploit.

## Requirements

- Kali Linux or another Linux host with **Docker Engine** and Docker Compose v2
- See [Linux Docker setup](#linux-docker-setup)
- `nmap`

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.12`

Stop any other Vulnsec lab first — Atlas always binds `8888`.

```bash
./scripts/status.sh
./scripts/reset.sh
./scripts/stop.sh
```

## Student scope

You are authorised against a single Northline lodge host.

- Target: `10.23.54.12`
- Atlas: `http://127.0.0.1:8888`
- Tool: nmap
- There is no vulnerability to exploit. Read the scan, then open the web page.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.12`
- Services: SSH 22, HTTP 80
- No vulnerability. Teaching objective is reading nmap -sV
- Lodge identifier LS-0412 is printed on the public page
- Atlas: five progressive questions + locked walkthrough

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
