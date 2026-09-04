# Vulnsec Academy Offensive Lab Range v1.0.1

Initial public range release containing 28 isolated Docker-based student packages.

## Included modules

- Operator Foundations
- Reconnaissance
- Service Misconfigurations
- SQL Injection
- Password Attacks
- Linux Privilege Escalation
- Network Pivoting
- Integrated Challenges

## Downloads

- Select an individual `Student-Kit-v1.0.1.zip` for one exercise.
- Select `Vulnsec-Academy-Complete-Lab-Range-v1.0.1.zip` for the complete collection.
- Use `SHA256SUMS.txt` to verify downloaded files.

## Requirements

The range requires Kali Linux, another Linux host, or Kali/Ubuntu under WSL2 with Docker Engine and Docker Compose v2 inside the Linux environment. Run one package at a time because Atlas uses `127.0.0.1:8888` throughout the range.

Read the selected package README before starting. Its **Student scope**, **Environment architecture** and **Linux Docker setup** sections contain the information previously split across multiple files.

## Consolidation

- Night Wharf is published as Challenge 02.
- Each package now uses one consolidated README.
- Redundant per-package documentation and ignore files were removed.
- Unsupported host launchers and instructions were removed; the range supports native Linux and native-engine WSL2 environments.
- All runtime code, Compose definitions, targets and intentional challenge fixtures were preserved.

## Licence

- Software and executable lab components use PolyForm Noncommercial 1.0.0.
- Standalone documentation and educational content use CC BY-NC-SA 4.0.
- Public attribution uses the pseudonymous creator identity Vulnsec Academy.
- Every standalone Student Kit includes the licence and project notice files.

## Safety

These intentionally vulnerable environments are for controlled, authorized education only. Do not expose the targets to the public internet or use the techniques against third-party systems without explicit permission.
