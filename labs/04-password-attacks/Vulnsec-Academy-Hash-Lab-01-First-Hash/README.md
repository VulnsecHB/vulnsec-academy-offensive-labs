# Vulnsec Academy — Hash Lab 01: First Hash

First hash-cracking lab. Identify an unsalted hash, crack it offline, log in.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.230`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

Tools stay on Kali: `hashid`, `john`, `hashcat`, `rockyou.txt`.

## Student scope

You are authorised against a single Northline personnel host.

- Target: `10.23.54.230`
- Atlas: `http://127.0.0.1:8888`
- Recover the operator password from the leaked dump and open the staff desk.

Crack offline. Do not attack systems outside this host.

## Environment architecture

- Target: static `10.23.54.230`
- HTTP 80
- Dump: `/backup/roster.dump` (username:md5)
- Operator a.holt password letmein (in rockyou)
- Staff desk flag HASH{first_hash_gate}
- John raw-md5 / hashcat -m 0

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
