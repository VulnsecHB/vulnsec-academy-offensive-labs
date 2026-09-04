# Vulnsec Academy — Privesc Lab 01: Borrowed Bin

First Linux privilege-escalation lab. SSH is given. `sudo -l`, then GTFOBins.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.201`
- SSH: `k.vale` / `Shelf-201`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

Look up the allowed binary on [gtfobins.github.io](https://gtfobins.github.io/).

## Student scope

You are authorised against a single Northline operator node.

- Target: `10.23.54.201`
- Atlas: `http://127.0.0.1:8888`
- SSH: `k.vale` / `Shelf-201`
- Deliverable: user flag and root flag

Start with `sudo -l`. Do not guess binaries. Use GTFOBins.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.201`
- SSH 22 (password), HTTP 80 (notice only)
- User k.vale, sudo NOPASSWD `/usr/bin/less`
- user.txt in home, root.txt in /root
- User and sudoers baked at image build (not at container start)
- no-new-privileges:false so sudo works

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
