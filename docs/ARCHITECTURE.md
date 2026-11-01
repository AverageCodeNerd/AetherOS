# AETHER OS — Architecture

**Decided:** 2026-10-28

## 1. Base system

- Debian 13 (trixie), amd64.
- Boot: hybrid live ISO with syslinux for BIOS and GRUB EFI for UEFI.
- Filesystem: ext4 root, separate /home, swap.
- Init: systemd.
- Display: KDE Plasma 6 with KWin on Xorg as a customizable transition platform while Aether Shell is developed; the goal remains an original shell that is not merely a rebranded Plasma desktop.

## 2. Desktop stack

- Transition desktop: KDE Plasma 6, KWin X11, Xorg, and LightDM. The selected session is `plasmax11`.
- Shell: custom "Aether Shell" (GTK4/Qt6, Rust services).
- First shell component: Aether Dock, a Plasma applet using the task-manager model for pinned application launching, window activation/minimization, and close-on-middle-click. Its settings expose pinned application IDs, icon size, spacing, corner radius, opacity, and accent color. It is an initial component, not yet a replacement for the complete Plasma shell.
- Login: LightDM selects the Plasma X11 session. A delayed systemd service activates the graphical VT after LightDM starts. The XFCE test image was visually confirmed in BIOS and UEFI QEMU boots; KDE and Aether Dock have not yet been boot-tested. The live image auto-logs in, so the graphical greeter and installed-system login remain unverified.
- Theme: centralized theme engine, CSS/GTK theming, icon/cursor packs.

## 3. Application suite

- Aether Files (file manager, GTK4/Rust)
- Aether Store (APT + Flatpak, GTK4/Rust)
- Aether Studio (theming, GTK4)
- Aether Settings (system config, GTK4)
- Aether Monitor (system stats, GTK4)
- Aether Terminal (VTE-based or foot)
- Aether Update (integrated with Store)
- Aether Welcome (first-boot, GTK4)

## 4. Build pipeline

- Tool: Debian live-build (lb).
- Config under build/.
- Output: bootable ISO + installer.
- VM test: qemu-system-x86_64.

## 5. Packaging

- .deb packages for Aether components.
- Flatpak for Store apps.
- Theme packages (.aether-theme).

## 6. Repository layout

See README.md §14.
