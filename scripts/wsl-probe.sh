#!/bin/bash
# Probe: sudo non-interactive availability + previous build timing.
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$PROJECT/build/logs/probe.txt"
exec >"$OUT" 2>&1

echo "== sudo =="
if sudo -n true 2>/dev/null; then echo "sudo: passwordless"; else echo "sudo: password required"; fi
echo "== sudo -l =="
sudo -n -l 2>&1 | tail -5

echo "== build log timing =="
LOG="$PROJECT/build/logs/lb-build.log"
ls -l "$LOG" 2>/dev/null
head -3 "$LOG" 2>/dev/null
echo "..."
tail -5 "$LOG" 2>/dev/null
echo "== log line count =="
wc -l "$LOG" 2>/dev/null

echo "== cache present? =="
sudo -n ls -d /var/cache/live-build 2>&1 | head -3
ls -d /var/tmp/aether-os-build.* 2>/dev/null | head

echo "== free disk =="
df -h / | tail -1
echo "DONE"
