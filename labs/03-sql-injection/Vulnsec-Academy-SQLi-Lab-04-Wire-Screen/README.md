# Vulnsec Academy — SQLi Lab 04: Wire Screen

Reach the Northline Yard Access portal at a static address. A perimeter filter blocks ordinary SQL keywords. Use **sqlmap with a tamper script** to bypass the screen, dump the desk accounts, and sign in as the yard marshal for the flag.

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
- Target: `10.23.54.121`

Stop any earlier SQLi lab first — Atlas always binds `8888`.

```bash
./scripts/status.sh
./scripts/reset.sh
./scripts/stop.sh
```

## Rules

- Target: `10.23.54.121`
- Expected service: TCP 80
- Automation is in scope — **sqlmap `--tamper` is the intended tool**

## Layout

| Path | Role |
| --- | --- |
| `mission-control/` | Atlas portal |
| `target/` | Northline Yard Access (WAF + SQLi) |
| `scripts/` | start / stop / reset / status |
| README — Student scope | In-scope rules |

## Student scope

You are authorized to investigate a single Northline Yard Access host.

- Target: `10.23.54.121`
- Expected service: HTTP on TCP 80
- Atlas Mission Control: `http://127.0.0.1:8888`
- Automation: sqlmap is in scope, including tamper scripts

A perimeter screen sits in front of the pass lookup. Default keyword payloads will be blocked. Bypass the filter — do not attack hosts outside this address.

Deliverable: the marshal flag from the yard desk, submitted in Atlas Mission Control.

## Environment architecture

- Target: static `10.23.54.121`, HTTP on port 80
- Mission Control: published only on `127.0.0.1:8888`
- Perimeter screen blocks spaced SQL keywords (`UNION `, `' OR `, `' AND `)
- Comment-wrapped tokens (`UNION/**/SELECT`) are allowed — `space2comment` is the intended bypass
- Pass lookup concatenates `pass` into `WHERE pass_id = '{q}'`
- Desk login is parameterized — dumped credentials are required
- Marshal is the only role that can open the sealed gate log (flag)

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
