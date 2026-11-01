# AETHER OS VM Testing

All desktop tests run in disposable QEMU virtual machines under WSL2. The ISO
is attached read-only; no host disk or partition is touched.

## Oracle VirtualBox review profile

On Windows, run this from the project root in PowerShell to create and register
a separate review VM using the current Aether Welcome test ISO:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\create-virtualbox-test-vm.ps1
```

The execution-policy override applies only to that PowerShell process; it does
not change the machine's policy.

The script verifies the ISO against its adjacent SHA-256 manifest and refuses
to overwrite an existing profile folder or modify a registered VM with the
same name. It creates `AetherOS Beta Review` under `build\virtualbox` with
4 GB RAM, 2 CPUs, 128 MB video memory, UEFI firmware, NAT networking, and a
new 32 GB dynamically allocated VDI. The ISO is attached as virtual DVD; the
VDI is the only virtual hard disk. No host disk passthrough, shared folders,
or USB devices are configured. The VM is created but not started.

Open the VM in VirtualBox Manager and start it. The live session can be
reviewed without installing; if you choose to test the installer, verify its
target is the VM's 32 GB VDI before confirming partitioning. The profile uses
the current `aether-welcome-test2.iso`; its generic KDE Welcome Center still
appears at startup, and installed first-run persistence remains unverified.
This profile does not make the image a beta release or establish hardware
compatibility.

## Requirements

Inside the Debian 13 build environment:

```bash
sudo apt-get install qemu-system-x86 ovmf python3-pil
```

`/dev/kvm` is used when available, with QEMU falling back to software
emulation otherwise.

## QEMU session helper

`tests/qemu_session.py` boots one ISO, keeps the VM alive between commands, and
exposes screenshots and input through QMP:

```bash
python3 tests/qemu_session.py start --iso build/live-image-amd64.iso
python3 tests/qemu_session.py wait --require-desktop
python3 tests/qemu_session.py shot desktop
python3 tests/qemu_session.py click 960 1040
python3 tests/qemu_session.py key alt f2
python3 tests/qemu_session.py type konsole
python3 tests/qemu_session.py stop
```

Add `--uefi` to `start` to boot through OVMF instead of SeaBIOS. Screenshots
are written as PNG files to `tests/results/`. The helper connects to QEMU's
QMP socket with the standard library only; input events use absolute
coordinates from the guest framebuffer, so clicks are resolution-independent.

## Taskbar smoke test

`tests/taskbar_vm_test.py` automates the taskbar acceptance check:

```bash
python3 tests/taskbar_vm_test.py --bios --iso build/live-image-amd64.aether-taskbar-test.iso
python3 tests/taskbar_vm_test.py --uefi --iso build/live-image-amd64.aether-taskbar-test.iso
```

The test:

1. Boots the live image and waits for a stable Plasma desktop.
2. Locates the bright icon clusters in the taskbar band.
3. Clicks the centre pinned application and checks that a window appears.
4. Clicks the same running icon and checks that the desktop returns.
5. Clicks again and checks that the window is restored.
6. Launches a second pinned application and closes both windows.

Screenshots and a QEMU log are stored in `tests/results/taskbar-bios/` and
`tests/results/taskbar-uefi/`.

## Graphical greeter check

`tests/greeter_vm_test.py` boots the live ISO, switches to LightDM, checks for
the centered login prompt, and authenticates the live account before confirming
that Plasma returns. Run it in both firmware modes:

```bash
python3 tests/greeter_vm_test.py --bios --iso build/live-image-amd64.aether-taskbar-test13.iso
python3 tests/greeter_vm_test.py --uefi --iso build/live-image-amd64.aether-taskbar-test13.iso
```

The standard live boot uses automatic login; this test checks the greeter and
authentication by switching away from the already-running live session.

## Limitations

Taskbar and greeter tests use read-only ISO media and no virtual disk.
Installation testing is a separate manual run: create a new disposable QCOW2
disk, attach only that disk to QEMU, and verify its exact device and size in the
installer before proceeding. Require explicit approval before confirming any
partition-table or formatting changes. The installer path has been verified
in both BIOS and UEFI QEMU using separate disposable QCOW2 disks.
For the UEFI repeat-boot check, attach the installed disk through QEMU's SATA
controller and avoid booting from the installer media; this makes firmware
fall through to the installed disk. Real hardware and other firmware
implementations remain unverified.

## Aether Welcome first-run check

The GTK Aether Welcome guide is configured to start on an installed user's
first Plasma login, skip live sessions, and save completion in
`~/.config/aether/welcome-completed`. The `aether-welcome-test2.iso` guide was
manually opened in a UEFI live QEMU session and its Welcome and setup pages
rendered. However, KDE's generic Welcome Center still appeared automatically
at live startup despite the suppression configuration. Investigate this
competing startup path, then install only to an explicitly approved disposable
VM disk and verify first-login launch, action links, completion persistence,
and absence on the next login. Do not count first-run integration as verified
until those installed-session checks pass; no host disk may be attached.
