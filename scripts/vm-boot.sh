#!/bin/bash
# Boot the AETHER taskbar ISO in QEMU (BIOS or UEFI), wait for the desktop,
# capture an initial screenshot, and leave the VM running for follow-up input.
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT"

FIRMWARE="${1:-bios}"
case "$FIRMWARE" in
  bios) UEFI_ARG="" ;;
  uefi) UEFI_ARG="--uefi" ;;
  *) echo "usage: $0 [bios|uefi]" >&2; exit 2 ;;
esac

ISO="$PROJECT/build/live-image-amd64.aether-taskbar-test.iso"
OUTDIR="$PROJECT/tests/results/taskbar-$FIRMWARE"
LOG="$PROJECT/build/logs/vm-$FIRMWARE-boot.txt"

: >"$LOG"
exec >>"$LOG" 2>&1

echo "== stop stale session =="
python3 tests/qemu_session.py --state "/var/tmp/aether-taskbar-$FIRMWARE.json" stop 2>/dev/null || true

echo "== start $FIRMWARE VM =="
python3 tests/qemu_session.py --state "/var/tmp/aether-taskbar-$FIRMWARE.json" \
  start --iso "$ISO" --outdir "$OUTDIR" $UEFI_ARG

echo "== boot menu =="
sleep 15
python3 tests/qemu_session.py --state "/var/tmp/aether-taskbar-$FIRMWARE.json" key ret

echo "== wait for desktop =="
sleep 75

echo "== screenshot =="
python3 tests/qemu_session.py --state "/var/tmp/aether-taskbar-$FIRMWARE.json" shot 01-desktop

echo "BOOT_OK $FIRMWARE"
