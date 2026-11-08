from pathlib import Path
import tempfile
import unittest
from unittest import mock

import package as P


class CleanSourceGuardPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = P.build()

    def test_deterministic_archive_and_full_clean_guard(self):
        result = P.verify(self.archive)
        self.assertEqual(result["archive_sha256"],
                         "d974183567e6c0d4b453e70a57c2cae9ce97544044d2de6b611604a848726aca")
        self.assertEqual(result["positive"]["verified_files"], 207)
        self.assertEqual(result["missing"]["status"], "REFUSED")
        self.assertEqual(result["changed"]["status"], "REFUSED")
        self.assertFalse(result["current_service_operation_executed"])

    def test_archive_mutation_refused(self):
        changed = bytearray(self.archive)
        changed[-20] ^= 1
        with self.assertRaises(ValueError):
            P.verify(bytes(changed))

    def test_selected_source_digest_change_refused(self):
        with self.assertRaisesRegex(ValueError, "selected source changed"):
            P.selected(P.PROFILE, "0" * 64)

    def test_unrelated_guard_error_does_not_satisfy_negative(self):
        class BrokenGuard:
            @staticmethod
            def _verify_files(*_):
                raise ValueError("unrelated guard error")
        with mock.patch.object(P, "guard_module", return_value=BrokenGuard()):
            for mutation in ("missing", "changed"):
                with self.subTest(mutation=mutation):
                    with self.assertRaisesRegex(ValueError, "unrelated guard error"):
                        P.extract_and_check(self.archive, mutation=mutation)

    def test_linked_input_or_archive_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original"
            original.write_bytes(b"data")
            link = root / "linked"
            link.symlink_to(original)
            with self.assertRaises(OSError):
                P.read_regular(link)
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(root, target_is_directory=True)
            with self.assertRaises(OSError):
                P.read_regular(linked_parent / "original")

    def test_no_replace_archive_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "archive"
            P.write_new(output, b"first")
            with self.assertRaises(FileExistsError):
                P.write_new(output, b"second")
            self.assertEqual(P.read_regular(output), b"first")
            pending = root / "pending"
            with mock.patch.object(P.os, "link", side_effect=OSError("publish refused")):
                with self.assertRaisesRegex(OSError, "publish refused"):
                    P.write_new(pending, b"complete")
            self.assertFalse(pending.exists())
            self.assertEqual(sorted(root.iterdir()), [output])


if __name__ == "__main__":
    unittest.main()
