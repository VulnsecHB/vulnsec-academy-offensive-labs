# Vulnsec Academy — SQLi Lab 03: Quiet Ledger

Reach the Northline Finance supplier ledger at a static address. The invoice lookup does not print rows or SQL errors — only whether a reference exists. Use **sqlmap** (boolean-blind) to dump the desk accounts, then sign in as the controller for the flag.

Atlas Mission Control guides the investigation. It never runs sqlmap for you.

## Requirements

- Kali Linux or another Linux host with **Docker Engine** and Docker Compose v2
- See [Linux Docker setup](#linux-docker-setup)
- `sqlmap` (preinstalled on Kali)

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

Then open Mission Control at `http://127.0.0.1:8888`.

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.104`

Stop Lab 01 or Lab 02 first — Atlas always binds `8888`.

```bash
./scripts/status.sh
./scripts/reset.sh
./scripts/stop.sh
```

## Rules

- Target: `10.23.54.104`
- Expected service: TCP 80
- Automation is in scope — **sqlmap is the intended tool**

## Layout

| Path | Role |
| --- | --- |
| `mission-control/` | Atlas portal |
| `target/` | Northline Finance ledger |
| `scripts/` | start / stop / reset / status |
| README — Student scope | In-scope rules |

## Student scope

You are authorized to investigate a single Northline Finance host.

- Target: `10.23.54.104`
- Expected service: HTTP on TCP 80
- Atlas Mission Control: `http://127.0.0.1:8888`
- Automation: sqlmap is in scope

The public invoice lookup will not print database rows. Infer the data.

Stay on the assigned host. Do not scan unrelated networks.

Deliverable: the controller flag from the finance desk, submitted in Atlas Mission Control.

## Environment architecture

- Target: static `10.23.54.104`, HTTP on port 80
- Mission Control: published only on `127.0.0.1:8888`
- Invoice lookup concatenates `ref` into `WHERE ref = '{q}'`
- The page only changes between "on file" and "not found" (boolean-blind)
- SQL errors are swallowed — no DBMS banner
- Desk login is parameterized — dumped credentials are required
- Controller is the only role that can open the clearance note (flag)

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
