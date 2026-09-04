# Vulnsec Academy — Class 00: Operator Foundations

Lecture Atlas. **No target.** Read the tools, then start the eight labs.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

Atlas: `http://127.0.0.1:8888`

Stop any lab that is already using `8888`.

After the class, the range order is:

1. First Sweep → 2. Odd Berth → 3. Unlisted Door → 4. Nested Hold  
5. Borrowed Bin → 6. Clockwork → 7. Setuid Tide → 8. Loud Enumerator

## Student scope

This is a class, not a lab. There is no host to attack.

- Atlas: `http://127.0.0.1:8888`
- Read every tool card: purpose, command, example output
- Then start **Recon Lab 01 — First Sweep**

Do not skip the class and jump into linPEAS.

## Environment architecture

- Atlas only. No target container, no 10.23.54.x
- Three views: Briefing, Toolkit, Range
- No questions, no walkthrough lock

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
