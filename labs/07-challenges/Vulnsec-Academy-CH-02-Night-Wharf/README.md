# Vulnsec Academy — Challenge 02: Night Wharf

Challenge lab. Full kill chain — reconnaissance, a hidden web surface, credential recovery, remote access, and privilege escalation. Atlas Mission Control only accepts the **user flag** and the **root flag**. There is no question trail.

## Requirements

- Kali Linux or another Linux host with **Docker Engine** and Docker Compose v2
- See [Linux Docker setup](#linux-docker-setup)
- Typical Kali tools: nmap, a directory fuzzer, sqlmap, ssh, a browser

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

Then open Mission Control at `http://127.0.0.1:8888`.

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.163`

Stop any other Vulnsec lab first — Atlas always binds `8888`.

```bash
./scripts/status.sh
./scripts/reset.sh
./scripts/stop.sh
```

## Rules

- Target: `10.23.54.163` only
- All services on that host are in scope
- Directory discovery, SQLi automation, and local privilege escalation are in scope
- Do not scan unrelated networks

## Layout

| Path | Role |
| --- | --- |
| `mission-control/` | Atlas portal (flag drop + locked walkthrough) |
| `target/` | Night Wharf host |
| `scripts/` | start / stop / reset / status |
| README — Student scope | In-scope rules |

## Student scope

You are authorized against a single Northline field host.

- Target: `10.23.54.163`
- Atlas Mission Control: `http://127.0.0.1:8888`
- Deliverable: **user flag** and **root flag**

The public site is not the whole surface. Enumeration is part of the job. Atlas will not walk you through each finding.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.163`
- Services: HTTP 80, SSH 22
- Public marketing site on `/` — no linked exploit
- Decoy paths from robots.txt
- Hidden /remote/api (directory discovery required)
- API `id` parameter is concatenated SQL
- Desk login on decoy intranet is parameterized
- SSH user lives in a restricted shell
- After escape, a GTFOBins sudo rule reaches root
- Atlas accepts only user.txt and root.txt values

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
