# Changelog

All notable repository and Student Kit changes should be recorded here.

## [1.0.1] — Unreleased

### Changed

- Consolidated every package's student brief, architecture and Linux Docker setup into its README
- Updated launch-script help messages to point to the consolidated README
- Renamed Night Wharf from its working SQLi Lab 05 identity to Challenge 02
- Moved Night Wharf into the integrated-challenges catalogue
- Expanded the root `.gitignore` to cover runtime state, generated environment files and Python cache files
- Added pseudonymous noncommercial software and educational-content licensing under the Vulnsec Academy identity
- Added release packaging that places the licence and project notice files in every standalone Student Kit
- Standardized the complete range for native Linux and native-engine WSL2 environments

### Removed

- Removed the five Buffer Overflow training packages pending a future binary exploitation release
- Removed the Iron Canary challenge because its attack path depended on Buffer Overflow exploitation

- 34 repeated `STUDENT-BRIEF.md` files after merging their content
- 34 repeated `SETUP-NATIVE-DOCKER.md` files after merging their content
- 34 repeated `docs/ARCHITECTURE.md` files after merging their content
- 34 redundant per-package `.gitignore` files
- 34 ineffective package-root `.dockerignore` files
- 33 empty-directory `.gitkeep` placeholders
- 137 unsupported platform-specific lifecycle and release scripts
- Unsupported host setup and troubleshooting instructions

### Preserved

- All Docker Compose definitions
- All Bash lifecycle scripts
- All Atlas Mission Control code
- All target, foothold, inner-network and challenge content
- Intentional lab flags, credentials and SSH-key fixtures

## [1.0.0] — Internal preservation build

### Added

- One repository structure for 34 supplied Vulnsec Academy packages
- Nine ordered learning modules
- Root quick-start, requirements, troubleshooting, security and ethical-use documentation
- Complete lab catalogue
- Repository validation and release-packaging tools
- Preservation-first cleanup guidance

### Preserved

- Original per-package names
- Original target and Atlas contents
- Original Bash lifecycle scripts
- Original student briefs, setup notes and architecture files

### Catalogue note

- Night Wharf still used its SQLi Lab 05 working identity in this internal build.
