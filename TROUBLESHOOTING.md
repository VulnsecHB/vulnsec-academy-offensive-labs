# Troubleshooting

## Docker cannot be reached

Typical message:

```text
Cannot connect to the Docker daemon
```

Check:

```bash
docker info
sudo systemctl status docker
```

Start the Docker service when required:

```bash
sudo systemctl start docker
```

## Docker Compose v2 is missing

Check:

```bash
docker compose version
```

The range expects the Compose v2 plugin. The legacy `docker-compose` command is not a substitute for the package scripts.

## Atlas port 8888 is already in use

Stop the previously selected package with its own stop script:

```bash
./scripts/stop.sh
```

To identify a listener on Linux:

```bash
ss -ltnp | grep ':8888'
```

Do not edit every Compose file to use a different Atlas port. The course material assumes `http://127.0.0.1:8888`.

## Target address is unreachable

1. Confirm that the selected package is healthy with `scripts/status.sh`.
2. Confirm that Docker Engine is running inside the same Linux or WSL2 environment.
3. Check the Docker networks with `docker network ls`.
4. Confirm that a VPN has not installed a conflicting route for the package subnet.
5. Do not test unrelated addresses; use only the package scope.

## Permission denied on a shell script

```bash
chmod +x scripts/*.sh
```

Then run the script from the package root:

```bash
./scripts/start.sh
```

## A previous attempt changed the target

Use the selected package's reset script:

```bash
./scripts/reset.sh
./scripts/start.sh
```

If the problem remains, stop the package and review its Compose logs. Do not manually delete files from the target until the lab has been reset and reproduced.

## Support report

Include:

- Exact package name
- Repository or Student Kit version
- Operating system and version
- Docker and Compose versions
- Output of the package status script
- The command that failed
- The error text

Do not include completed flags or full solutions in public issue titles.
