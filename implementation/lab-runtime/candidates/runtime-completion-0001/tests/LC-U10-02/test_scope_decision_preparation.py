"""Meaningful refusal checks for inert LC-U10-02 preparation."""

import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).with_name("build_scope_decision_preparation.py")
spec = importlib.util.spec_from_file_location("scope_decisions", MODULE_PATH)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class ScopeDecisionPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = subject.build()

    def test_all_original_routes_are_inert_and_individual(self):
        self.assertEqual(subject.validate_preparation(self.good)["route_count"], 230)
        rows = self.good["rows"]
        self.assertEqual(len({r["selection_index"] for r in rows}), 230)
        self.assertEqual(len({r["member_ref"] for r in rows}), 230)
        self.assertTrue(all(r["selected_alternative"] is None and r["current_grant_binding"] is None for r in rows))
        self.assertTrue(all(r["body_scope_ref"] != subject.PROJECT for r in rows))

    def test_omission_refused(self):
        forged = copy.deepcopy(self.good)
        forged["rows"].pop()
        with self.assertRaisesRegex(ValueError, "worksheet differs"):
            subject.validate_preparation(forged)

    def test_forged_scope_and_grant_refused(self):
        for field, value in (("body_scope_ref", subject.PROJECT), ("current_grant_binding", {"approved": True}), ("selected_alternative", "exact-domain-native-consumer")):
            with self.subTest(field=field):
                forged = copy.deepcopy(self.good)
                forged["rows"][0][field] = value
                with self.assertRaisesRegex(ValueError, "worksheet differs"):
                    subject.validate_preparation(forged)

    def test_drifted_source_bytes_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            (root / "input.json").write_bytes(b"changed")
            stale = hashlib.sha256(b"original").hexdigest()
            with self.assertRaisesRegex(ValueError, "source drift"):
                subject.read_binding({"path": "input.json", "sha256": stale}, root)

    def test_path_alias_and_escape_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            (root / "input.json").write_bytes(b"{}")
            (root / "alias.json").symlink_to("input.json")
            digest = hashlib.sha256(b"{}").hexdigest()
            for path in ("alias.json", "../input.json", "/input.json"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    subject.read_binding({"path": path, "sha256": digest}, root)

    def test_writer_refuses_aliased_parent_and_existing_leaf(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            owned = root / "owned"
            external = root / "external"
            owned.mkdir()
            external.mkdir()
            (owned / "alias").symlink_to(external, target_is_directory=True)
            escaped = external / "escaped.json"
            with self.assertRaises(OSError):
                subject.write_new(owned / "alias" / escaped.name, {"safe": True})
            self.assertFalse(escaped.exists())
            target = owned / "once.json"
            subject.write_new(target, {"safe": True})
            original = target.read_bytes()
            with self.assertRaises(FileExistsError):
                subject.write_new(target, {"safe": False})
            self.assertEqual(target.read_bytes(), original)

    def test_reader_refuses_same_byte_alias_swapped_at_final_open(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            source = root / "input.json"
            outside = root / "outside.json"
            source.write_bytes(b"{}")
            outside.write_bytes(b"{}")
            digest = hashlib.sha256(b"{}").hexdigest()
            original_open = subject.os.open
            swapped = False

            def swap_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if path == "input.json" and "dir_fd" in kwargs and not swapped:
                    source.unlink()
                    source.symlink_to(outside)
                    swapped = True
                return original_open(path, flags, *args, **kwargs)

            with mock.patch.object(subject.os, "open", side_effect=swap_before_open):
                with self.assertRaises(ValueError):
                    subject.read_binding({"path": "input.json", "sha256": digest}, root)
            self.assertTrue(swapped)


if __name__ == "__main__":
    unittest.main()
