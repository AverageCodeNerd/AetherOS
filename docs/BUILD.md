# AETHER OS Build Workflow

This project is built around Debian live-build so the distribution can be generated as a bootable ISO from a reproducible config.

## Prerequisites

- Debian 13 (trixie) in WSL2
- `sudo` access with a valid local password
- Internet access for package downloads

## Install build tooling

From the project root:

```bash
./scripts/bootstrap-wsl-build.sh
```

This installs the Debian package tooling required for a live ISO build, including `debootstrap`, `live-build`, `qemu-utils`, `xorriso`, Git, Python, and Node.js.

## Build the ISO

```bash
./scripts/build-live-iso.sh
```

The script stages live-build's inputs in a temporary directory under `/var/tmp`, avoiding live-build's restriction on working paths containing spaces. It runs `lb clean` and `lb build` there, writes the log to `build/logs/lb-build.log`, and copies the resulting ISO into `build/`. The auto-configuration selects Debian trixie amd64 and a hybrid BIOS/UEFI image; `noauto` prevents recursive execution of `auto/config`. During the build only, it prefers IPv4 for Wget downloads (including bootstrap and package post-install downloads), then removes the temporary configuration from both the build host and image chroot. This does not change networking in the live system.

To keep an existing image untouched while building a test variant, set a new filename (the build refuses to overwrite an existing custom output):

```bash
sudo env AETHER_ISO_OUTPUT_NAME=live-image-amd64.xfce-panel-test.iso ./scripts/build-live-iso.sh
```

The script writes a matching SHA-256 manifest beside each copied ISO.

## Verify the ISO

After a build, run the artifact verifier from the project root inside WSL2:

```bash
python3 scripts/verify_live_iso.py
```

The verifier checks the ISO against its adjacent `.sha256` manifest, then uses `xorriso` to confirm the `AETHER_OS_13` volume ID, BIOS and UEFI El Torito entries, and the live root filesystem. To inspect another ISO, pass `--iso PATH`; pass `--manifest PATH` when its checksum manifest is not at `<ISO path>.sha256`.

This is an artifact-structure check only. It does not boot a VM, test installation, or verify behavior after installation. Run the focused verifier tests with:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## QEMU smoke-test results

On 2026-10-28, the original ISO was run in QEMU 10.0.13 under WSL2 with a read-only ISO drive and no virtual hard disk. BIOS and UEFI both reached the Debian live boot menu. Selecting the BIOS live entry reached the Debian 13 text login on tty7; a live-user console login worked. An earlier greetd/gtkgreet/Sway test image did not show a usable greeter or desktop and was replaced by XFCE4 on Xorg with LightDM.

The XFCE test images were booted read-only in QEMU with no virtual disk. BIOS and UEFI firmware both showed the live desktop after enabling VT7 through `aether-activate-graphical-vt.service`.

On 2026-10-30, `build/live-image-amd64.aether-taskbar-test2.iso` passed the artifact verifier and booted to the Plasma desktop in QEMU 10.0.13 using KVM under both BIOS and UEFI firmware. The ISO was read-only and no virtual disk was attached. Screenshots in both modes showed the launcher on the left, three pinned Aether Dock icons centered, and the system tray and clock on the right.

On 2026-11-01, `build/live-image-amd64.aether-taskbar-test9.iso` passed checksum and BIOS/UEFI boot-structure verification, then reached the Plasma desktop in BIOS QEMU using KVM with read-only ISO media and no virtual disk. The Aether Dock settings dialog showed the three configured launcher IDs. Dolphin launched from the dock; clicking its active task minimized the window and clicking again restored it.

`build/live-image-amd64.aether-taskbar-test11.iso` adds the original Aether icon theme as the KDE and LightDM default, with custom launcher, Dolphin, terminal, and System Settings icons. A first-session action applies the Aether wallpaper once and records completion so later user wallpaper choices are preserved. BIOS QEMU testing visually confirmed the Aether wallpaper and custom dock icons. UEFI boot of this image and graphical greeter rendering remain unverified.

`build/live-image-amd64.aether-taskbar-test13.iso` passed checksum and BIOS/UEFI boot-structure verification. With KVM, read-only ISO media, and no virtual disk, it reached the Plasma desktop in both BIOS and UEFI QEMU. Automated UEFI checks confirmed dock icons, pinned-app launch, minimize/restore, and launching a second pinned app. BIOS interaction confirmed that a user could replace the pins with `applications:org.kde.konsole.desktop`, apply the change, reopen settings and see the value retained, then launch Konsole from the updated dock. Pin editing and launching are verified within the live session only. Switching to the LightDM greeter from the live desktop displayed its centered login prompt and authenticated the live account (`user` / `live`) in both BIOS and UEFI. Fresh live boots still auto-login, so this does not verify a password prompt during initial boot.

The configured Debian Live Installer was run in BIOS and UEFI QEMU using separate, explicitly created sparse 32 GiB QCOW2 disks: `/var/tmp/aether-taskbar-test13-install.qcow2` and `/var/tmp/aether-taskbar-test13-install-uefi.qcow2`. Only the relevant disposable disk was attached during each installation; no host disk was attached. Guided partitioning created an ext4 root and swap for BIOS, and a FAT32 EFI System Partition, ext4 root, and swap for UEFI. Both installed systems reached LightDM, accepted their temporary test accounts, and reached Plasma; both authenticated again from the same disk in a second QEMU session. For UEFI boot checks, the installed disk was attached through QEMU's SATA controller with read-only non-bootable media present, so the firmware fell through to the disk. These results verify BIOS and UEFI installation and repeat-boot paths in disposable QEMU VMs only. Real hardware and other firmware implementations remain unverified. Fresh live boots still auto-login, so this does not verify a password prompt during initial live boot.

`build/aether-welcome-test2.iso` includes the GTK Aether Welcome guide and passed the checksum and BIOS/UEFI structure verifier. In UEFI QEMU with read-only ISO media and no virtual disk, it reached the live desktop; manually launching Aether Welcome rendered its Welcome page and setup navigation. KDE's generic Welcome Center still appeared automatically in the live session despite the configured suppression, so replacing that competing startup path remains unresolved. The installed first-run autostart and per-user completion flow have not been tested.

## Validation notes

- Confirm the host is Debian 13 and `lb` is present.
- Run the verifier after creating or copying an ISO artifact.
- Build variants without replacing existing artifacts by setting `AETHER_ISO_OUTPUT_NAME` to a new `.iso` filename; the build script also writes that image's SHA-256 manifest. Run each image in a disposable VM; use an explicitly created, disposable virtual disk for installer testing.
- Keep package lists and custom hooks under `build/` so the configuration remains reproducible.

The current scope is the functional build foundation; the full Aether Shell and application suite remain to be implemented incrementally on top of this base.
