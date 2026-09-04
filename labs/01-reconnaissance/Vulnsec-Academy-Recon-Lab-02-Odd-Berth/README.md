# Vulnsec Academy — Recon Lab 02: Odd Berth

Second nmap lab. Same idea as First Sweep, except the web service is **not** on port 80.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.19`

Stop any other Vulnsec lab first. Linux Docker Engine — see [Linux Docker setup](#linux-docker-setup).

## Student scope

You are authorised against a single Northline berth host.

- Target: `10.23.54.19`
- Atlas: `http://127.0.0.1:8888`
- Tool: nmap
- Do not assume the web service is on TCP 80. Widen the port list if 80 is closed.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.19`
- SSH 22, HTTP **8088**, nothing on 80
- No vulnerability
- Teaching objective: do not assume port 80; use -p- or a wider list
- Berth identifier BC-1908 is on the HTTP page

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
