# Vulnsec Academy — Privesc Lab 04: Loud Enumerator

Last Linux privilege-escalation lab. SSH is given. **linPEAS is not on the box.** Transfer it from Kali, read the output, ignore the kernel, take the capability.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.221`
- SSH: `l.peel` / `Loud-221`
- Gateway (Kali, from the target): usually `10.23.54.1`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

This lab network is **not** internal. The target must be able to curl your attacking host.

See [tools/README.txt](tools/README.txt) for fetching linPEAS / linuxprivchecker.

## Student scope

You are authorised against a single Northline operator node.

- Target: `10.23.54.221`
- Atlas: `http://127.0.0.1:8888`
- SSH: `l.peel` / `Loud-221`
- Deliverable: user flag and root flag

There is no linPEAS on the target. Serve it from Kali (`python3 -m http.server`) and pull it with `curl`. Read the colour. Kernel CVEs are a decoy in this container. linuxprivchecker is an optional second enumerator — same transfer.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.221`
- SSH 22, HTTP 80 notice
- User l.peel, no sudo
- Network is NOT internal — target can reach Kali at 10.23.54.1
- Real path: cap_setuid+ep on CPython (linPEAS Capabilities)
- Kernel / LES output is a decoy — do not run kernel PoCs
- Tools are not pre-installed; transfer from Kali
- curl + wget on the target
- no-new-privileges:false so capabilities work

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
