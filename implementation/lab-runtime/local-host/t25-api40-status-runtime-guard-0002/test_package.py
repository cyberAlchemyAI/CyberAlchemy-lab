import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

import package as P


class StatusRuntimeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob = P.read_regular(P.ARCHIVE)

    def test_cold_selected_archive_and_fresh_child(self):
        result = P.verify(self.blob)
        self.assertEqual(result["archive_sha256"],
                         "4318ef5de10c3c364b222b8978c896377db5b8a8664ddef27cc7a873887578fe")
        self.assertEqual(result["positive"], {"status": "PASS", "verified_files": 7})
        self.assertEqual(result["full_source_guard_rows_omitted"], 201)
        self.assertEqual(result["missing"]["status"], "REFUSED")
        self.assertEqual(result["changed"]["status"], "REFUSED")
        self.assertFalse(result["original_service_executed"])

    def test_archive_excludes_flagged_full_source_rows(self):
        with zipfile.ZipFile(io.BytesIO(self.blob)) as archive:
            names = archive.namelist()
            self.assertEqual(len(names), 9)
            for name in P.UNSAFE_OMITTED:
                self.assertNotIn("files/" + name, names)
            self.assertEqual(len([name for name in names if name.startswith("files/")]), 7)

    def test_archive_and_guard_origin_mutation_refused(self):
        damaged = bytearray(self.blob)
        damaged[-20] ^= 1
        with self.assertRaises(ValueError):
            P.verify(bytes(damaged))
        with mock.patch.object(P, "GUARD_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "technical guard changed"):
                P.selected_guard()

    def test_byte_bootstrap_refuses_changed_code_before_side_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "marker"
            changed = ("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('bad')\n").encode()
            child = subprocess.run([sys.executable, "-I", "-B", "-c", P.BOOT,
                                    P.GUARD_SHA, str(root / "unselected.py"), str(root), "0" * 64],
                                   input=changed, capture_output=True, timeout=10)
            self.assertNotEqual(child.returncode, 0)
            self.assertFalse(marker.exists())

    def test_selected_privacy_class_rejects_secret_assignment(self):
        scanner, prior = P.privacy_scanner()
        with self.assertRaises(ValueError):
            scanner.scan_public("files/runtime/config.py", b"api_key = populated\n", prior)

    def test_no_replace_and_linked_output_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "candidate"
            P.write_new(output, b"first")
            with self.assertRaises(FileExistsError):
                P.write_new(output, b"second")
            self.assertEqual(P.read_regular(output), b"first")
            linked = root / "linked"
            linked.symlink_to(output)
            with self.assertRaises(OSError):
                P.read_regular(linked)


if __name__ == "__main__":
    unittest.main()
