#!/usr/bin/env python3
"""Objectively characterise an AETHER desktop screenshot.

Prints overall brightness, the taskbar band, and the bright icon clusters
(their x-centres) so the dock layout can be verified without a human eye:
launcher on the left, centred pinned apps, system tray/clock on the right.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def cluster_x_centres(image: Image.Image, bottom_band: int = 120):
    width, height = image.size
    top = max(0, height - bottom_band)
    region = image.crop((0, top, width, height)).convert("L")
    pixels = region.load()
    counts = [0] * width
    for y in range(region.height):
        for x in range(width):
            if pixels[x, y] >= 100:
                counts[x] += 1

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
                if end - start >= 6:
                    clusters.append((start, end))
                start = None
                gap = 0
    if start is not None:
        clusters.append((start, width - 1))
    return clusters


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGB")
    width, height = image.size
    grey = image.convert("L")
    pixels = list(grey.getdata())
    mean = sum(pixels) / len(pixels)
    dark = sum(1 for p in pixels if p < 8) / len(pixels)
    bright = sum(1 for p in pixels if p >= 200) / len(pixels)

    print(f"size={width}x{height}")
    print(f"mean={mean:.1f} dark={dark:.3%} bright={bright:.3%}")

    # Taskbar band brightness.
    band = image.crop((0, max(0, height - 120), width, height)).convert("L")
    band_pixels = list(band.getdata())
    band_mean = sum(band_pixels) / len(band_pixels)
    print(f"taskbar_band_mean={band_mean:.1f}")

    clusters = cluster_x_centres(image)
    print(f"icon_clusters={len(clusters)}")
    for i, (left, right) in enumerate(clusters):
        cx = (left + right) // 2
        print(f"  cluster{i}: x=[{left},{right}] cx={cx} rel={cx / width:.3f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
