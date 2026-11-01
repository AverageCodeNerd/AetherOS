import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_live_iso


REPORT = """\
Volume Id    : AETHER_OS_13
El Torito boot img :   1 BIOS  y none 0x0000 0x00 4 3365
El Torito boot img :   2 UEFI  y none 0x0000 0x00 6656 1701
El Torito img path :   1 /isolinux/isolinux.bin
El Torito img path :   2 /boot/grub/efi.img
/live/filesystem.squashfs
"""


class VerifyLiveIsoTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.directory = Path(self.temp_dir.name)
        self.iso = self.directory / "live-image-amd64.hybrid.iso"
        self.iso.write_bytes(b"test ISO bytes")
        self.manifest = self.directory / f"{self.iso.name}.sha256"
        digest = hashlib.sha256(self.iso.read_bytes()).hexdigest()
        self.manifest.write_text(f"{digest} *{self.iso.name}\n", encoding="utf-8")

    @patch("verify_live_iso.subprocess.run")
    def test_accepts_valid_checksum_and_boot_markers(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=REPORT, stderr=""
        )
        verify_live_iso.verify(self.iso, self.manifest)
        self.assertEqual(run.call_args.args[0][0], "xorriso")

    @patch("verify_live_iso.subprocess.run")
    def test_rejects_checksum_mismatch_before_inspecting_iso(self, run):
        self.manifest.write_text(f"{'0' * 64} *{self.iso.name}\n", encoding="utf-8")
        with self.assertRaisesRegex(verify_live_iso.VerificationError, "SHA-256 mismatch"):
            verify_live_iso.verify(self.iso, self.manifest)
        run.assert_not_called()

    @patch("verify_live_iso.subprocess.run")
    def test_rejects_missing_uefi_entry(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=REPORT.replace("2 UEFI", "2 OTHER"), stderr=""
        )
        with self.assertRaisesRegex(verify_live_iso.VerificationError, "UEFI"):
            verify_live_iso.verify(self.iso, self.manifest)

    @patch("verify_live_iso.subprocess.run")
    def test_rejects_missing_live_root_filesystem(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=REPORT.replace("/live/filesystem.squashfs", ""),
            stderr="",
        )
        with self.assertRaisesRegex(
            verify_live_iso.VerificationError, "live root filesystem"
        ):
            verify_live_iso.verify(self.iso, self.manifest)

    @patch("verify_live_iso.subprocess.run")
    def test_reports_xorriso_failure(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=2, stdout="", stderr="unable to read image"
        )
        with self.assertRaisesRegex(verify_live_iso.VerificationError, "exit 2"):
            verify_live_iso.verify(self.iso, self.manifest)


if __name__ == "__main__":
    unittest.main()
