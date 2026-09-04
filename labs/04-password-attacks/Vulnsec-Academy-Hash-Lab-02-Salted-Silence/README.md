# Vulnsec Academy — Hash Lab 02: Salted Silence

Second hash-cracking lab. Salted sha512crypt. Wordlist alone may miss — apply a rule.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.237`

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

```bash
john --format=sha512crypt --wordlist=rockyou.txt --rules hashes.txt
hashcat -m 1800 hashes.txt rockyou.txt -j 'c $1'
```

## Student scope

You are authorised against a single Northline night-lock host.

- Target: `10.23.54.237`
- Atlas: `http://127.0.0.1:8888`
- Recover m.quay’s password from the salted export and open the lock desk.

MD5 mode from lab 01 will not work. Crack offline.

## Environment architecture

- Target: static `10.23.54.237`
- HTTP 80
- Dump: `/export/shadow.n1` (sha512crypt $6$)
- Operator m.quay password Sunshine1 (sunshine + capitalize + append 1)
- Flag HASH{salted_silence}
- John sha512crypt / hashcat -m 1800 + rule c $1

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
