# Vulnsec Academy — Recon Lab 04: Nested Hold

Second fuzzing lab. Find the unlisted folder, then fuzz **inside it** with file extensions.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.38`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

```bash
gobuster dir -u http://10.23.54.38 -w /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://10.23.54.38/archive -w /usr/share/wordlists/dirb/common.txt -x bak,old,txt
```

## Student scope

You are authorised against a single Northline records host.

- Target: `10.23.54.38`
- Atlas: `http://127.0.0.1:8888`
- Tool: gobuster (or ffuf)
- Fuzz the root, then fuzz whatever folder you find. Backup extensions are in scope.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.38`
- HTTP 80
- Public site does not link `/archive/`
- `/archive/` is a closed splash (no file listing)
- Prize file: `/archive/notes.bak` (needs -x bak,old,txt)
- Identifier NH-3802

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
