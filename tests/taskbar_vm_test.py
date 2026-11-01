#!/usr/bin/env python3
"""Boot the AETHER live ISO and verify the taskbar's real window behavior.

The test launches a window by clicking a pinned dock icon, minimizes it by
clicking the running icon, restores it, and checks the screen changes with
pixel comparisons. Run it from the repository root inside the build VM:

    python3 tests/taskbar_vm_test.py --iso build/live-image-amd64.iso --bios
    python3 tests/taskbar_vm_test.py --iso build/live-image-amd64.iso --uefi
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops

SESSION = Path(__file__).with_name("qemu_session.py")


def run_session(state: Path, *arguments: str, timeout: float = 300) -> str:
    command = [sys.executable, str(SESSION), "--state", str(state), *arguments]
    completed = subprocess.run(
        command, check=False, capture_output=True, text=True, timeout=timeout
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{' '.join(command)} failed ({completed.returncode}):\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    return completed.stdout.strip()


def capture(state: Path, outdir: Path, name: str) -> Path:
    output = run_session(state, "shot", name)
    path = Path(output.strip().splitlines()[-1])
    if not path.is_file():
        raise RuntimeError(f"Screenshot was not created: {output}")
    return path


def bright_clusters(image: Image.Image, bottom_band: int = 110):
    """Return bright icon clusters in the bottom band as (x, y, width, height)."""
    width, height = image.size
    top = max(0, height - bottom_band)
    region = image.crop((0, top, width, height)).convert("L")
    pixels = region.load()
    counts = [0] * width
    rows = [0] * region.height
    for y in range(region.height):
        for x in range(width):
            if pixels[x, y] >= 100:
                counts[x] += 1
                rows[y] += 1

    clusters = []
    start = None
    gap = 0
    for x, count in enumerate(counts):
        if count >= 2:
            if start is None:
                start = x
            gap = 0
        elif start is not None:
            gap += 1
            if gap > 10:
                end = x - gap
                if end - start >= 8:
                    clusters.append([start, end])
                start = None
                gap = 0
    if start is not None:
        clusters.append([start, width - 1])

    results = []
    for left, right in clusters:
        mask_pixels = [
            (x, y)
            for y in range(region.height)
            for x in range(left, right + 1)
            if pixels[x, y] >= 100
        ]
        if len(mask_pixels) < 12:
            continue
        xs = [x for x, _ in mask_pixels]
        ys = [y for _, y in mask_pixels]
        results.append(
            {
                "left": left,
                "right": right,
                "cx": sum(xs) // len(xs),
                "cy": top + sum(ys) // len(ys),
                "bright": len(mask_pixels),
            }
        )
    return results


def pick_dock_icons(image: Image.Image):
    width, height = image.size
    clusters = bright_clusters(image)
    central = [
        cluster
        for cluster in clusters
        if 0.30 * width <= cluster["cx"] <= 0.70 * width
        and cluster["cy"] >= height - 100
    ]
    central.sort(key=lambda cluster: cluster["cx"])
    if len(central) >= 3:
        selected = central[:3]
    else:
        selected = [cluster for cluster in clusters if cluster["cx"] == min(
            clusters, key=lambda item: abs(item["cx"] - width / 2)
        )["cx"]]
    return clusters, central, selected


def changed_fraction(first: Image.Image, second: Image.Image, box) -> float:
    left = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
    cropped = left.crop(box).convert("L")
    pixels = list(cropped.getdata())
    if not pixels:
        return 0.0
    return sum(1 for value in pixels if value > 14) / len(pixels)


def check(label: str, condition: bool, detail: str) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}: {detail}")
    if not condition:
        raise AssertionError(f"{label}: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iso", default="build/live-image-amd64.aether-taskbar-test.iso")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bios", action="store_true")
    group.add_argument("--uefi", action="store_true")
    parser.add_argument("--outdir", default="tests/results")
    parser.add_argument("--memory", type=int, default=4096)
    args = parser.parse_args()

    firmware = "uefi" if args.uefi else "bios"
    outdir = Path(args.outdir).resolve() / f"taskbar-{firmware}"
    outdir.mkdir(parents=True, exist_ok=True)
    state = Path(f"/var/tmp/aether-taskbar-{firmware}.json")

    run_session(state, "stop", "--keep-state", timeout=30) if state.exists() else None

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
        print(run_session(state, "wait", "--timeout", "240", "--interval", "8",
                          "--require-desktop"))

        desktop = capture(state, outdir, "01-desktop")
        image = Image.open(desktop).convert("RGB")
        width, height = image.size
        clusters, central, selected = pick_dock_icons(image)
        print(f"Screen {width}x{height}; icon clusters: {json.dumps(clusters)}")
        print(f"Central clusters: {json.dumps(central)}")
        check("three dock icons detected", len(selected) >= 3,
              f"{len(selected)} candidate icons")
        middle = selected[len(selected) // 2]
        icon_x, icon_y = middle["cx"], middle["cy"]
        print(f"Clicking dock icon at {icon_x},{icon_y}")

        center_box = (
            int(width * 0.05),
            int(height * 0.05),
            int(width * 0.95),
            int(height * 0.75),
        )

        run_session(state, "click", str(icon_x), str(icon_y), timeout=30)
        time.sleep(7)
        opened = capture(state, outdir, "02-window-open")
        open_diff = changed_fraction(image, Image.open(opened), center_box)
        check("clicking the pinned icon opens a window", open_diff > 0.04,
              f"{open_diff:.1%} of the desktop changed")

        run_session(state, "click", str(icon_x), str(icon_y), timeout=30)
        time.sleep(4)
        minimized = capture(state, outdir, "03-window-minimized")
        minimize_diff = changed_fraction(image, Image.open(minimized), center_box)
        check("clicking the active icon minimizes the window", minimize_diff < 0.01,
              f"{minimize_diff:.1%} differs from the desktop")

        run_session(state, "click", str(icon_x), str(icon_y), timeout=30)
        time.sleep(4)
        restored = capture(state, outdir, "04-window-restored")
        restore_diff = changed_fraction(image, Image.open(restored), center_box)
        check("clicking the minimized icon restores the window", restore_diff > 0.04,
              f"{restore_diff:.1%} of the desktop changed")

        if len(central) >= 3:
            dolphin = central[0]
            run_session(state, "click", str(dolphin["cx"]), str(dolphin["cy"]),
                        timeout=30)
            time.sleep(7)
            dolphin_shot = capture(state, outdir, "05-second-app")
            dolphin_diff = changed_fraction(
                Image.open(restored), Image.open(dolphin_shot), center_box
            )
            check("a second pinned application launches", dolphin_diff > 0.04,
                  f"{dolphin_diff:.1%} of the desktop changed")
            run_session(state, "key", "alt", "f4", timeout=30)
            time.sleep(2)
            run_session(state, "key", "alt", "f4", timeout=30)
            time.sleep(2)

        capture(state, outdir, "06-final")
        print("Taskbar smoke test passed.")
        return 0
    finally:
        run_session(state, "stop", timeout=30)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # noqa: BLE001 - report the test failure clearly
        print(f"Taskbar smoke test failed: {error}", file=sys.stderr)
        sys.exit(1)
