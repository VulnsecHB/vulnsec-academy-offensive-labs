# Vulnsec Academy — FTP Lab 01: Open Hatch

First FTP lab. Anonymous listing is on. Get the inbound sheet.

## Start

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

- Atlas: `http://127.0.0.1:8888`
- Target: `10.23.54.67`
- Service: FTP 21 (anonymous)

Stop any other Vulnsec lab first. Linux Docker Engine — [Linux Docker setup](#linux-docker-setup).

Tools stay on Kali: `nmap`, `ftp`.

## Student scope

You are authorised against a single Northline hatch host.

- Target: `10.23.54.67`
- Atlas: `http://127.0.0.1:8888`
- Expected: FTP on 21
- Deliverable: flag from the inbound manifest

HTTP 80 is a notice. Do not hunt a writeable upload.

Stay on the assigned host.

## Environment architecture

- Target: static `10.23.54.67`
- vsftpd, anonymous_enable=YES, no_anon_password=YES
- PASV 30000-30009, pasv_address=10.23.54.67
- Files: `/srv/ftp/README.txt`, `/srv/ftp/inbound-manifest.txt`
- Flag: `FTP{open_hatch_anon}`
- HTTP 80 contractor notice only

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
