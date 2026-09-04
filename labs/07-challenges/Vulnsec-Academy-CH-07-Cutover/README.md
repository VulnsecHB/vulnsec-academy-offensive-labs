# Vulnsec Academy — Challenge 07 Cutover

Flag-only Atlas. No class, no investigation quiz.

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: http://127.0.0.1:8888
- Edge: `10.23.54.185`
- Scope: 10.23.54.185 and any second NIC you find

Stop other Vulnsec labs first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

## Student scope

- Edge: `10.23.54.185`
- Atlas: http://127.0.0.1:8888
- Atlas accepts **user** and **root** flags only.
- Wander. Extra shares, vhosts, and hosts are real.

Stay on the assigned range.

## Environment architecture

- Edge `10.23.54.185`
- Flags `CH{cutover_user}` / `CH{cutover_root}`
- Hidden: 10.24.30.0/24
- Services: target bonus

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
