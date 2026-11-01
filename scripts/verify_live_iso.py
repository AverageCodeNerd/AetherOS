#!/usr/bin/env python3
"""Verify the checksum, boot structure, and live payload of the built AETHER OS ISO."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ISO = ROOT / "build" / "live-image-amd64.hybrid.iso"
EXPECTED_VOLUME_ID = "AETHER_OS_13"
MANIFEST_LINE = re.compile(r"([0-9a-fA-F]{64}) [ *]([^\r\n]+)")


class VerificationError(Exception):
    """Raised when an artifact does not meet the verifier's requirements."""


def verify_checksum(iso: Path, manifest: Path) -> None:
    if not iso.is_file():
        raise VerificationError(f"ISO file not found: {iso}")
    if not manifest.is_file():
        raise VerificationError(f"Checksum manifest not found: {manifest}")

    lines = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line]
    if len(lines) != 1:
        raise VerificationError(f"Expected exactly one checksum entry in {manifest}")

    match = MANIFEST_LINE.fullmatch(lines[0])
    if not match or Path(match.group(2)).name != iso.name:
        raise VerificationError(
            f"Checksum manifest must contain one SHA-256 entry for {iso.name}"
        )

    expected = match.group(1).lower()
    digest = hashlib.sha256()
    with iso.open("rb") as image:
        for chunk in iter(lambda: image.read(1024 * 1024), b""):
            digest.update(chunk)

    actual = digest.hexdigest()
    if actual != expected:
        raise VerificationError(
            f"SHA-256 mismatch for {iso.name}: expected {expected}, got {actual}"
        )


def inspect_iso(iso: Path) -> None:
    command = [
        "xorriso",
        "-indev",
        str(iso),
        "-pvd_info",
        "-report_el_torito",
        "plain",
        "-find",
        "/",
        "-name",
        "filesystem.squashfs",
        "-exec",
        "echo",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as error:
        raise VerificationError(f"Could not run xorriso: {error}") from error

    report = result.stdout + result.stderr
    if result.returncode:
        detail = "\n".join(report.splitlines()[-10:])
        raise VerificationError(
            f"xorriso could not inspect {iso} (exit {result.returncode}):\n{detail}"
        )

    checks = (
        (
            re.search(
                rf"^\s*Volume Id\s*:\s*{re.escape(EXPECTED_VOLUME_ID)}\s*$",
                report,
                re.MULTILINE,
            ),
            f"expected ISO volume ID {EXPECTED_VOLUME_ID}",
        ),
        (
            re.search(r"El Torito boot img\s*:\s*\d+\s+BIOS\b", report),
            "BIOS El Torito boot entry",
        ),
        (
            re.search(r"El Torito boot img\s*:\s*\d+\s+UEFI\b", report),
            "UEFI El Torito boot entry",
        ),
        (
            re.search(
                r"El Torito img path\s*:\s*\d+\s+/isolinux/isolinux\.bin\b",
                report,
            ),
            "BIOS boot image at /isolinux/isolinux.bin",
        ),
        (
            re.search(
                r"El Torito img path\s*:\s*\d+\s+/boot/grub/efi\.img\b",
                report,
            ),
            "UEFI boot image at /boot/grub/efi.img",
        ),
        (
            re.search(r"['\"]?/live/filesystem\.squashfs['\"]?(?:\s|$)", report),
            "live root filesystem at /live/filesystem.squashfs",
        ),
    )
    missing = [description for found, description in checks if not found]
    if missing:
        raise VerificationError("ISO is missing required markers: " + "; ".join(missing))


def verify(iso: Path, manifest: Path) -> None:
    verify_checksum(iso, manifest)
    inspect_iso(iso)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iso",
        type=Path,
        default=DEFAULT_ISO,
        help=f"ISO image to verify (default: {DEFAULT_ISO})",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="SHA-256 manifest (default: <ISO path>.sha256)",
    )
    args = parser.parse_args(argv)
    iso = args.iso.resolve()
    manifest = (args.manifest or Path(f"{iso}.sha256")).resolve()

    try:
        verify(iso, manifest)
    except (OSError, UnicodeError, VerificationError) as error:
        print(f"ISO verification failed: {error}", file=sys.stderr)
        return 1

    print(f"ISO verification passed: {iso}")
    print(
        f"SHA-256, {EXPECTED_VOLUME_ID}, BIOS/UEFI boot entries, and live rootfs verified."
    )
    print("This check does not verify VM boot, installation, or installed-system behavior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
