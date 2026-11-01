#!/bin/bash
# Report the state of build/config/hooks entries (they are symlinks created by WSL).
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$PROJECT/build/logs/hooks.txt"
exec >"$OUT" 2>&1

cd "$PROJECT/build/config/hooks" || exit 1
for f in live/* normal/*; do
    if [ -L "$f" ]; then
        target="$(readlink "$f")"
        if [ -e "$f" ]; then
            size="$(stat -Lc %s "$f")"
            state="resolves"
        else
            size="-"
            state="BROKEN"
        fi
        printf '%-6s %-46s -> %s [%s, %s]\n' "$state" "$f" "$target" "$size" "$(stat -Lc %a "$f" 2>/dev/null || echo -)"
    else
        printf '%-6s %-46s [%s bytes]\n' "file" "$f" "$(stat -c %s "$f")"
    fi
done

echo "== example hooks dir =="
ls -l /usr/share/doc/live-build/examples/hooks/ 2>/dev/null | head -30
echo "DONE"
