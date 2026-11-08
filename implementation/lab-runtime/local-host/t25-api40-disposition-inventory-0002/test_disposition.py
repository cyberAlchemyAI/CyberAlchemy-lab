import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import disposition as D


class DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = D.selected(D.PROFILE, D.PROFILE_SHA)
        cls.original = D.selected(D.ORIGINAL, D.ORIGINAL_SHA)
        cls.candidate = D.selected(D.CANDIDATE, D.CANDIDATE_SHA)

    def test_frozen_cold_rebuild(self):
        document = D.build()
        self.assertEqual(D.regular_unlinked(D.OUTPUT), document)
        rows = D.parse(document)["rows"]
        summary = D.parse(document)["summary"]
        self.assertEqual(len(rows), 33424)
        self.assertEqual(summary["profile_rows"], 33424)
        self.assertEqual(sum(r["disposition"] == "archive-byte-selected" for r in rows), 684)
        self.assertEqual(sum(r["disposition"] == "unresolved" for r in rows), 32740)
        self.assertTrue(all(r["portable_install_verified"] is False and
                            r["runtime_consumption_verified"] is False for r in rows))

    def test_exact_archive_names_not_prefix_guesses(self):
        rows = D.classify(self.profile, self.original, self.candidate)
        chosen = [r for r in rows if r["archive_member"]]
        self.assertEqual(sum(r["archive_member"].startswith("api40/") for r in chosen), 3)
        self.assertEqual(sum(r["archive_member"].startswith("META/original-public-inputs.zip!files/")
                             for r in chosen), 681)

    def test_profile_digest_mutation_refused(self):
        changed = copy.deepcopy(self.profile)
        path = self.original["files"][0]["path"]
        target = next(row for row in changed["files"] if row["path"] == path)
        target["sha256"] = "0" * 64 if target["sha256"] != "0" * 64 else "1" * 64
        with self.assertRaisesRegex(ValueError, "overlap changed"):
            D.classify(changed, self.original, self.candidate)

    def test_duplicate_and_extra_profile_rows_refused(self):
        changed = copy.deepcopy(self.profile)
        changed["files"][-1] = copy.deepcopy(changed["files"][0])
        with self.assertRaisesRegex(ValueError, "duplicate or reorder"):
            D.profile_rows(changed)
        changed = copy.deepcopy(self.profile)
        changed["files"].append({"path": "z-extra", "sha256": "0" * 64})
        with self.assertRaisesRegex(ValueError, "shape/count"):
            D.profile_rows(changed)

    def test_archive_selection_mutation_refused(self):
        changed = copy.deepcopy(self.candidate)
        changed["archive_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "inventory changed"):
            D.archive_selection(self.original, changed)
        changed = copy.deepcopy(self.original)
        changed["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "overlap changed"):
            D.classify(self.profile, changed, self.candidate)

    def test_output_symlink_and_repeat_write_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.write_bytes(b"unchanged")
            link = root / "link"
            link.symlink_to(target)
            with self.assertRaises(OSError):
                D.regular_unlinked(link)
            with self.assertRaises(FileExistsError):
                D.write_new(link, b"bad")
            self.assertEqual(target.read_bytes(), b"unchanged")
            output = root / "new"
            D.write_new(output, b"first")
            with self.assertRaises(FileExistsError):
                D.write_new(output, b"second")
            self.assertEqual(output.read_bytes(), b"first")

    def test_symlink_ancestor_refused_for_read_and_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"
            real.mkdir()
            (real / "selected").write_bytes(b"protected")
            link = root / "linked"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaises(OSError):
                D.regular_unlinked(link / "selected")
            with self.assertRaises(OSError):
                D.write_new(link / "created", b"bad")
            self.assertFalse((real / "created").exists())

    def test_failed_publication_leaves_no_partial_frozen_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "frozen"
            with mock.patch.object(D.os, "link", side_effect=OSError("simulated publish failure")):
                with self.assertRaisesRegex(OSError, "publish failure"):
                    D.write_new(output, b"complete")
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_post_link_fsync_failure_has_complete_uncertain_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "frozen"
            real_fsync = D.os.fsync
            calls = 0
            def fail_second(descriptor):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated directory fsync failure")
                return real_fsync(descriptor)
            with mock.patch.object(D.os, "fsync", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "directory fsync failure"):
                    D.write_new(output, b"complete")
            self.assertEqual(D.regular_unlinked(output), b"complete")
            self.assertEqual(list(root.iterdir()), [output])
            with self.assertRaises(FileExistsError):
                D.write_new(output, b"replacement")

    def test_selected_binding_change_refused(self):
        with self.assertRaisesRegex(ValueError, "selected bytes changed"):
            D.selected(D.PROFILE, "0" * 64)


if __name__ == "__main__":
    unittest.main()
