# Vulnsec Academy — SQLi Lab 01: Broken Gate

Discover the staff portal on `10.23.54.0/24`, open the Northline login, force the authentication gate with SQL injection, and recover the administrator flag.

Atlas Mission Control guides the investigation. It never scans or exploits the target for you.

## Requirements

- Kali Linux or another Linux host with **Docker Engine** and Docker Compose v2
- See [Linux Docker setup](#linux-docker-setup)

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

Then open Mission Control at `http://127.0.0.1:8888`.

The target has a **static** address on `10.23.54.0/24`. Discover it with host scanning. Do not read `.lab.env`.

```bash
./scripts/status.sh
./scripts/reset.sh
./scripts/stop.sh
```

## Rules

- Scan only `10.23.54.0/24`
- Known gateway: `10.23.54.1`
- Expected service: TCP 80
- Manual investigation only in this lab (no sqlmap)

## Layout

| Path | Role |
| --- | --- |
| `mission-control/` | Atlas portal |
| `target/` | Northline Staff Access (vulnerable login) |
| `scripts/` | start / stop / reset / status |
| README — Student scope | In-scope rules |

## Student scope

You are authorized to investigate a single internal subnet belonging to Northline Operations.

- Authorized scope: `10.23.54.0/24`
- Known gateway: `10.23.54.1`
- Expected service: HTTP on TCP 80
- The staff portal uses a static address on that subnet. Discover it yourself.

Stay inside the supplied range. Do not scan other networks. Do not use Docker inspection or open `.lab.env` to learn the target IP.

Deliverable: the administrator flag from the staff portal, submitted in Atlas Mission Control.

## Environment architecture

- `lab01` network: `10.23.54.0/24`, gateway `10.23.54.1`, internal-only
- Target: static `10.23.54.47`, HTTP on port 80
- Mission Control: published only on `127.0.0.1:8888`
- Runtime state: `runtime/lab-state.json` (not for students)
- Login query is intentionally concatenated so authentication SQLi is possible
- Admin is the first `users` row so `' OR 1=1--` yields an administrator session

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
