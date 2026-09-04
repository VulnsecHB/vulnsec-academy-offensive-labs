# Requirements

## Core requirements

- 64-bit computer with hardware virtualization enabled
- Kali Linux, another Linux host, or Kali/Ubuntu under WSL2
- Docker Engine running inside the same Linux or WSL2 environment
- Docker Compose v2 (`docker compose`, not legacy `docker-compose`)
- `curl`
- Bash for the `.sh` lifecycle scripts
- A modern browser for Atlas

Individual packages may require additional tools such as Nmap, Gobuster, ffuf, sqlmap, John the Ripper, Hashcat, ProxyChains, SSH, FTP or smbclient. The package README identifies the intended toolset.

## Suggested capacity

- At least 4 CPU threads
- At least 8 GB system RAM
- At least 10 GB free storage for Docker images and build cache

More capacity may be required when other virtual machines are running simultaneously.

## Networking note

Most packages place targets on static private Docker subnets such as `10.23.54.0/24` and additional pivot networks. The attacking Linux or WSL2 environment must be able to route directly to those subnets.

Class 00 publishes only Atlas on `127.0.0.1:8888` and has no private target. It uses the same Linux lifecycle model as every other package.

## Verify before opening a support issue

```bash
docker --version
docker compose version
docker info
curl --version
```

Also run the selected package's `scripts/status.sh` and retain the output.
