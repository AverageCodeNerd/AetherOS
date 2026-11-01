# AETHER OS — Debian Baseline

**Decided:** 2026-10-28

## Chosen base

- **Debian 13 (trixie)** — current stable release.
- Initial release: 13.0 on 2025-08-09; latest point release 13.7 on 2026-09-12.
- Full support EOL: 2028-08-09; LTS to 2030-06-30; ELTS to 2035-06-30.
- Architecture: amd64 (x86_64) — matches the host/WSL2 environment and primary target.
- Wayland-first desktop architecture; original Aether Shell built around proven components (not KDE/GNOME default).

## Build environment

- Host: Windows 10.0.26300 (x86_64).
- WSL2 available; distro `Debian` (Debian 13 trixie, kernel 6.18.54-microsoft-standard-WSL2).
- Available in WSL2: `qemu-system-x86_64`, `xorriso`.
- Missing in WSL2 (to install once sudo password is available): `debootstrap`, `live-build`, `lb`, `qemu-utils`, `git`, `python3`, `node`, `cargo`, `go`.
- No passwordless sudo (user `eddie` requires password).

## Next steps

1. Install Debian build tooling in WSL2 (`sudo apt-get install debootstrap live-build qemu-utils git python3 nodejs`).
2. Research Debian trixie installation media + package repos; document in docs/ARCHITECTURE.md.
3. Begin live-build configuration under `build/`.