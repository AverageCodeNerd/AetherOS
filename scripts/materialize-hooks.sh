#!/bin/bash
# Replace live-build hook symlinks with real copies so the repository is
# self-contained, portable to Windows git, and reproducible without live-build's
# packaging directory being present.
set -eu

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS="$PROJECT/build/config/hooks"
REPORT="$PROJECT/build/logs/hooks-materialized.txt"

: >"$REPORT"
converted=0
for f in "$HOOKS"/live/*.hook.chroot "$HOOKS"/normal/*.hook.chroot; do
    [ -L "$f" ] || continue
    source="$(readlink -f "$f")"
    if [ ! -f "$source" ]; then
        printf 'MISSING %s -> %s\n' "$f" "$source" >>"$REPORT"
        continue
    fi
    tmp="$f.aether-new"
    cp --dereference -- "$source" "$tmp"
    chmod 0755 "$tmp"
    rm -f -- "$f"
    mv -- "$tmp" "$f"
    printf 'OK %s (%s bytes)\n' "${f#"$HOOKS"/}" "$(stat -c %s "$f")" >>"$REPORT"
    converted=$((converted + 1))
done

printf 'converted=%d\n' "$converted" >>"$REPORT"
printf 'remaining symlinks=%s\n' "$(find "$HOOKS" -type l | wc -l)" >>"$REPORT"
