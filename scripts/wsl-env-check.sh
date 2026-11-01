#!/bin/bash
# Environment probe for the AETHER OS Debian 13 build environment.
# Writes a plain-text report to build/logs/env-check.txt.
set -u
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$PROJECT/build/logs/env-check.txt"
mkdir -p "$PROJECT/build/logs"
exec >"$OUT" 2>&1

echo "== identity =="
whoami
id

echo "== os =="
. /etc/os-release
echo "PRETTY_NAME=$PRETTY_NAME"
echo "VERSION=$VERSION"

echo "== kernel =="
uname -a

echo "== tooling =="
for t in lb debootstrap qemu-system-x86_64 qemu-img xorriso git python3 node npm 7z; do
    printf '%-22s %s\n' "$t" "$(command -v "$t" || echo MISSING)"
done

echo "== qemu version =="
qemu-system-x86_64 --version 2>/dev/null | head -2

echo "== ovmf =="
ls -1 /usr/share/OVMF/ 2>/dev/null | head -10

echo "== kvm =="
ls -l /dev/kvm 2>&1
grep -c -E 'vmx|svm' /proc/cpuinfo 2>/dev/null || true

echo "== project root =="
ls -la "$PROJECT"

echo "== existing isos =="
ls -la "$PROJECT"/build/*.iso 2>/dev/null

echo "== disk =="
df -h / /mnt/c 2>/dev/null

echo "== memory =="
free -h

echo "== git =="
git -C "$PROJECT" status --short 2>&1 | head -5

echo "DONE"
