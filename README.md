# Vulnsec Academy Offensive Security Labs

An isolated Docker-based training range containing **28 student packages** across reconnaissance, service misconfigurations, SQL injection, password attacks, Linux privilege escalation, network pivoting, and integrated challenges.

These environments are intentionally vulnerable. Run them only on a system you own and only for authorized education.

## Repository contents

| Module | Packages | Focus |
| --- | ---: | --- |
| 00 — Foundations | 1 | Operator tools and range workflow |
| 01 — Reconnaissance | 4 | Nmap, service discovery and content discovery |
| 02 — Service misconfigurations | 4 | SSH, FTP, SMB and restricted shells |
| 03 — SQL injection | 4 | Manual SQLi, sqlmap, blind SQLi and filter bypass |
| 04 — Password attacks | 2 | Hash identification, John and Hashcat |
| 05 — Linux privilege escalation | 4 | Sudo, cron, SUID, capabilities and enumeration |
| 06 — Pivoting | 3 | SSH local forwarding, SOCKS and multi-hop access |
| 07 — Challenges | 6 | Flag-only integrated assessments and full attack chains |

See [LAB-CATALOG.md](LAB-CATALOG.md) for the complete ordered catalogue.

## Important operating model

- Run **one Vulnsec package at a time**. Every Atlas interface binds to `127.0.0.1:8888`.
- Run the lifecycle scripts from the selected package, not from the repository root.
- The complete range supports Kali Linux, another Linux host, or Kali/Ubuntu under WSL2 with a native Docker Engine and Docker Compose v2 inside the Linux environment.
- The attacking Linux environment must be able to reach the static private lab subnets directly.
- Do not scan networks outside the scope stated in the selected package's README.

## Quick start

Open the folder for the package you want to run:

```bash
cd labs/01-reconnaissance/Vulnsec-Academy-Recon-Lab-01-First-Sweep
chmod +x scripts/*.sh
./scripts/start.sh
```

Then open Atlas:

```text
http://127.0.0.1:8888
```

Lifecycle commands:

```bash
./scripts/status.sh
./scripts/reset.sh
./scripts/stop.sh
```

Read [QUICKSTART.md](QUICKSTART.md) and [REQUIREMENTS.md](REQUIREMENTS.md) before starting the range.

## Downloading the range

GitHub supports two intended distribution methods:

1. Download or clone this repository for the complete collection.
2. Download an individual versioned Student Kit from the repository's Releases page.

The same versioned Student Kit ZIP should be attached to the matching Udemy lecture. This keeps GitHub and Udemy downloads identical.

Release archives are generated with:

```bash
./scripts/validate-repository.sh
./scripts/build-release.sh 1.0.1
```

Generated files appear under `_release-assets/v1.0.1/`. That directory is intentionally excluded from Git so ZIP binaries do not inflate repository history.

## Licence

- Software, Docker environments, scripts and configuration are available under the [PolyForm Noncommercial License 1.0.0](LICENSE).
- Standalone documentation and educational content are available under [CC BY-NC-SA 4.0](LICENSE-CONTENT.md).
- Attribution is to **Vulnsec Academy**, the creator's pseudonymous publishing identity. A legal name is not required.
- The licences do not grant permission to use Vulnsec Academy branding in a way that implies sponsorship, affiliation or endorsement. See [NOTICE](NOTICE).

Students may download, run, study, modify and share the material for permitted noncommercial purposes. Commercial training, resale or commercial repackaging requires separate permission.

## Support and responsible disclosure

- Ordinary setup problems: use the GitHub issue template and include the package name, operating system, Docker version, package version and `status` output.
- Potential unintended container escape, host exposure or leaked real secret: follow [SECURITY.md](SECURITY.md) and do not publish sensitive details in a normal issue.
- Common setup failures are covered in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Repository status

This repository contains the consolidated Vulnsec Academy v1.0.1 offensive-security lab range. Each package keeps one complete README containing its instructions, scope, architecture and Linux Docker setup. See [CHANGELOG.md](CHANGELOG.md) for version history and [SECURITY.md](SECURITY.md) for responsible disclosure instructions.

## Safety notice

These labs are designed solely for controlled, local and authorized environments. The techniques must not be used against systems, services or networks without explicit permission. See [ETHICAL-USE.md](ETHICAL-USE.md).
