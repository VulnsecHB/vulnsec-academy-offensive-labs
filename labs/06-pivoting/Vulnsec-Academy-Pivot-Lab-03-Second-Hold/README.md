# Vulnsec Academy — Pivot Lab 03: Second Hold

Double hop. ProxyJump (`-J`) then a local forward to a third network.

## Start
```bash
chmod +x scripts/*.sh
./scripts/start.sh
```
- Atlas: `http://127.0.0.1:8888`
- Hop 1: `r.hold@10.23.54.254` / `Jump-254`
- Hop 2: `k.well@10.24.10.30` / `Deep-Hold` (written on hop 1)
- Vault: `10.24.20.5`

```bash
ssh -J r.hold@10.23.54.254 -L 8000:10.24.20.5:80 k.well@10.24.10.30
curl http://127.0.0.1:8000/
```

## Student scope

- Atlas: `http://127.0.0.1:8888`
- Hop 1: `r.hold@10.23.54.254` password `Jump-254`
- Find hop 2 on the foothold. The vault is one net deeper.

## Environment architecture

- Hop 1 10.23.54.254 + 10.24.10.3
- Hop 2 10.24.10.30 + 10.24.20.1
- Vault 10.24.20.5
- Flag PIV{second_hold}

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
