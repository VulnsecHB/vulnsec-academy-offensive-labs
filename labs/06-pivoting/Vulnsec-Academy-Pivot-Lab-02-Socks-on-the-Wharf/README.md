# Vulnsec Academy — Pivot Lab 02: Socks on the Wharf

SSH dynamic SOCKS (`-D`) + proxychains. Scan an inner host that has more than one port.

## Start
```bash
chmod +x scripts/*.sh
./scripts/start.sh
```
- Atlas: `http://127.0.0.1:8888`
- Foothold: `n.wharf@10.23.54.247` / `Socks-247`
- Inner: `10.24.10.21` (80 decoy, 8088 flag)

```bash
ssh -D 9050 n.wharf@10.23.54.247
# proxychains.conf: socks5 127.0.0.1 9050
proxychains nmap -sT -Pn -p 80,8088 10.24.10.21
proxychains curl http://10.24.10.21:8088/
```

## Student scope

- Atlas: `http://127.0.0.1:8888`
- SSH: `n.wharf@10.23.54.247` password `Socks-247`
- Scan 10.24.10.21 through SOCKS. Flag is not on port 80.

## Environment architecture

- Edge 10.23.54.247 / inner NIC 10.24.10.2
- Inner 10.24.10.21 ports 80 + 8088
- Flag PIV{socks_on_the_wharf} on 8088

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
