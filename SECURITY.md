# Security policy

## Intended vulnerabilities

Authentication weaknesses, unsafe permissions, vulnerable application logic, exposed services, deliberately weak credentials and similar conditions may be intentional parts of the range. These normally belong in course discussion rather than a security report.

## Report privately

Treat the following as potentially unintended and do not disclose the technical details in a normal public issue:

- A container escape or modification of the host outside the selected package directory
- Binding a deliberately vulnerable service to a non-loopback host interface unexpectedly
- A real credential, token, personal key or unrelated secret included in the repository
- A dependency or launcher behavior that creates material risk beyond the isolated lab

Use GitHub's private vulnerability-reporting or security-advisory feature after the repository is published. Until that feature is configured, keep the repository private while the concern is investigated.

## Ordinary bugs

Broken builds, unclear instructions, unavailable target services and incorrect answers may be reported with the issue template. Remove flags, passwords recovered during an exercise and complete solution chains from public issue titles.
