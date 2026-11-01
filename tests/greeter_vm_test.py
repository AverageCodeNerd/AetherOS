#!/usr/bin/env python3
"""Boot the live ISO, then switch to LightDM to verify the graphical greeter."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskbar_vm_test import bright_clusters, capture, check, run_session


def has_centered_login_prompt(image: Image.Image) -> bool:
    width, height = image.size
    center = image.crop(
        (int(width * 0.40), int(height * 0.40), int(width * 0.60), int(height * 0.65))
    ).convert("RGB")
    pixels = list(center.getdata())
    neutral_panel = sum(
        1
        for red, green, blue in pixels
        if max(red, green, blue) - min(red, green, blue) <= 10
        and 28 <= (red + green + blue) // 3 <= 85
    )
    light_controls = sum(
        1 for red, green, blue in pixels if min(red, green, blue) >= 210
    )
    area = center.width * center.height
    return neutral_panel >= area // 4 and light_controls >= area // 100


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iso", default="build/live-image-amd64.aether-taskbar-test2.iso")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bios", action="store_true")
    group.add_argument("--uefi", action="store_true")
    parser.add_argument("--outdir", default="tests/results")
    parser.add_argument("--memory", type=int, default=4096)
    args = parser.parse_args()

    firmware = "uefi" if args.uefi else "bios"
    outdir = Path(args.outdir).resolve() / f"greeter-{firmware}"
    outdir.mkdir(parents=True, exist_ok=True)
    state = Path(f"/var/tmp/aether-greeter-{firmware}.json")

    if state.exists():
        run_session(state, "stop", "--keep-state", timeout=30)

    start_arguments = [
        "start",
        "--iso",
        str(Path(args.iso).resolve()),
        "--outdir",
        str(outdir),
        "--memory",
        str(args.memory),
    ]
    if args.uefi:
        start_arguments.append("--uefi")
    print(run_session(state, *start_arguments, timeout=60))
    try:
        time.sleep(15)
        run_session(state, "key", "ret", timeout=30)
        time.sleep(30)
        print(
            run_session(
                state,
                "wait",
                "--timeout",
                "240",
                "--interval",
                "8",
                "--require-desktop",
            )
        )

        desktop = capture(state, outdir, "01-desktop")
        desktop_image = Image.open(desktop).convert("RGB")
        desktop_icons = bright_clusters(desktop_image)
        check(
            "desktop has a taskbar before switching",
            len(desktop_icons) >= 3,
            f"{len(desktop_icons)} icon clusters",
        )

        run_session(state, "key", "alt", "f2", timeout=30)
        time.sleep(1.5)
        run_session(state, "type", "dm-tool switch-to-greeter", timeout=30)
        time.sleep(0.4)
        run_session(state, "key", "ret", timeout=30)
        time.sleep(8)

        greeter = capture(state, outdir, "02-greeter")
        greeter_image = Image.open(greeter).convert("RGB")
        greeter_icons = bright_clusters(greeter_image)
        check(
            "the Plasma taskbar is gone after switching to the greeter",
            len(greeter_icons) <= 2,
            f"{len(greeter_icons)} remaining icon clusters",
        )
        check(
            "the centered login prompt is visible",
            has_centered_login_prompt(greeter_image),
            "expected the greeter's neutral login panel and light controls",
        )
        mean_luminance = sum(greeter_image.convert("L").getdata()) / (
            greeter_image.width * greeter_image.height
        )
        check(
            "the greeter is not a black screen",
            mean_luminance > 12,
            f"mean luminance {mean_luminance:.1f}",
        )

        time.sleep(1)
        run_session(state, "type", "user", timeout=30)
        run_session(state, "key", "ret", timeout=30)
        time.sleep(1)
        run_session(state, "type", "live", timeout=30)
        run_session(state, "key", "ret", timeout=30)
        print(
            run_session(
                state,
                "wait",
                "--timeout",
                "180",
                "--interval",
                "5",
                "--require-desktop",
            )
        )
        authenticated = capture(state, outdir, "03-authenticated-desktop")
        authenticated_image = Image.open(authenticated).convert("RGB")
        authenticated_icons = bright_clusters(authenticated_image)
        check(
            "live user can authenticate and return to the desktop",
            len(authenticated_icons) >= 3,
            f"{len(authenticated_icons)} taskbar icon clusters after login",
        )
        print("Greeter smoke test passed.")
        return 0
    finally:
        run_session(state, "stop", timeout=30)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # noqa: BLE001
        print(f"Greeter smoke test failed: {error}", file=sys.stderr)
        sys.exit(1)
