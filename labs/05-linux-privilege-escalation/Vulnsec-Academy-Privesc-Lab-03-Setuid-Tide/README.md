# Vulnsec Academy — Privesc Lab 03: Setuid Tide

Third Linux privilege-escalation lab. SSH is given. **No sudo. No cron.** A SUID binary you look up on GTFOBins.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.214`
- SSH: `s.quay` / `Tide-214`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

```bash
find / -perm -4000 -type f 2>/dev/null
```

Use the **SUID** column on GTFOBins, not Sudo.

## Student scope

You are authorised against a single Northline operator node.

- Target: `10.23.54.214`
- Atlas: `http://127.0.0.1:8888`
- SSH: `s.quay` / `Tide-214`
- Deliverable: user flag and root flag

`sudo -l` will not save you. Find SUID binaries. Identify what the unusual one actually is, then open that GTFOBins page.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.214`
- SSH 22, HTTP 80 notice
- User s.quay, no sudo, no cron
- SUID copy of env at /usr/local/bin/yard-report (4755)
- GTFOBins env → SUID: yard-report /bin/sh -p
- no-new-privileges:false so SUID works
- User/binary baked at image build

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
