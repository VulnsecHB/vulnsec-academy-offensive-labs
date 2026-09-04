# Quick start

## 1. Prepare the host

Use Kali Linux, another Linux host, or Kali/Ubuntu under WSL2 with Docker Engine and Docker Compose v2 inside the Linux environment. Read [REQUIREMENTS.md](REQUIREMENTS.md) and the selected package README's **Linux Docker setup** section.

Confirm the environment:

```bash
docker --version
docker compose version
docker info
```

## 2. Choose one package

Start with Class 00, then follow the order in [LAB-CATALOG.md](LAB-CATALOG.md).

```bash
cd labs/00-foundations/Vulnsec-Academy-Class-00-Operator-Foundations
```

## 3. Start Atlas and the target

```bash
chmod +x scripts/*.sh
./scripts/start.sh
```

Open `http://127.0.0.1:8888`.

Class 00 has no target. Every actual lab provides its authorized scope in the **Student scope** section of its README.

## 4. Check health

```bash
./scripts/status.sh
```

Do not begin until the package reports the expected services as healthy.

## 5. Reset or stop

Reset the selected environment to its initial state:

```bash
./scripts/reset.sh
```

Stop it before starting another package:

```bash
./scripts/stop.sh
```

Only one package can use Atlas port `8888` at a time.
