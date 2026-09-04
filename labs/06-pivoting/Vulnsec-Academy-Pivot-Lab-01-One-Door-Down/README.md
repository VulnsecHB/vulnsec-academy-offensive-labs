# Vulnsec Academy — Pivot Lab 01: One Door Down

SSH local port forward (`-L`) through an edge foothold to an internal HTTP desk.

## Start
```bash
chmod +x scripts/*.sh
./scripts/start.sh
```
- Atlas: `http://127.0.0.1:8888`
- Foothold SSH: `10.23.54.240` (`p.keel` / `Berth-240`)
- Hidden: `10.24.10.12` (not reachable from Kali)

```bash
ssh -L 8000:10.24.10.12:80 p.keel@10.23.54.240
curl http://127.0.0.1:8000/
```

## Student scope

Authorised against the Northline edge node only.
- Atlas: `http://127.0.0.1:8888`
- SSH: `p.keel@10.23.54.240` password `Berth-240`
- Reach the yard desk that the edge can see and Kali cannot.

## Environment architecture

- Edge 10.23.54.240 (SSH) dual-homed to 10.24.10.1
- Hidden 10.24.10.12 HTTP, internal docker net
- Host DROP to 10.24.10.0/24 via DOCKER-USER
- AllowTcpForwarding yes
- Flag PIV{one_door_down}

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
