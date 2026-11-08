"""Actual D75 selector and local relation-backed representation checks."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_d75_model_selection", HERE / "select_model.py")
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class D75ModelSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row, cls.original, cls.disposition, cls.selections = subject.actual_selections()
        cls.model, cls.implementation, cls.relation = subject.make_documents(
            cls.original, cls.selections["d75"])

    def check(self, model=None, implementation=None, relation=None, selection=None):
        subject.verify_documents(subject.ROOT, model or self.model,
                                 implementation or self.implementation,
                                 relation or self.relation,
                                 selection or self.selections["d75"])

    def test_01_actual_d75_selection_and_d74_counterexample(self):
        self.assertEqual(self.selections["d75"]["expected_cut"], "decision:0075")
        self.assertEqual(self.selections["d74"]["expected_cut"], "decision:0074")
        self.assertEqual(self.selections["d74"]["executable_manifest_sha256"],
                         self.selections["d75"]["executable_manifest_sha256"])
        self.assertNotEqual(self.selections["d74"]["profile_sha256"],
                            self.selections["d75"]["profile_sha256"])
        self.assertEqual(self.original["relation_refs"], [])
        self.assertFalse(self.disposition["admission_or_runtime_use_allowed"])
        self.check()

    def test_02_d74_and_wrong_profile_digest_refused(self):
        with self.assertRaisesRegex(ValueError, "D75 selector binding required"):
            subject.make_documents(self.original, self.selections["d74"])
        choices = json.loads(subject.original_context()[3])
        choices["selections"][1]["profile_sha256"] = "0" * 64
        source_hash = next(b["sha256"] for b in self.disposition["code_bindings"]
                           if b["path"] == (subject.PACKAGE / "lab_runtime/profiles.py").as_posix())
        child = subprocess.run([sys.executable, "-I", "-B", str(HERE / "selector_worker.py"),
                                str(subject.ROOT), source_hash],
                               input=json.dumps(choices).encode(), capture_output=True, check=False)
        self.assertNotEqual(child.returncode, 0)
        self.assertIn(b"selected material digest mismatch", child.stderr)

    def test_03_wrong_endpoint_or_generic_implementation_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["source"]["ref"] = "implementation:cyberalchemy-lab:repeatable-operation"
        with self.assertRaisesRegex(ValueError, "classification or reciprocal binding differs"):
            self.check(relation=relation)
        relation = deepcopy(self.relation)
        relation["payload"]["target"]["version_ref"] = "wrong-parent"
        with self.assertRaisesRegex(ValueError, "classification or reciprocal binding differs"):
            self.check(relation=relation)

    def test_04_wrong_qualifier_and_relation_kind_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["qualifiers"]["binding_ref"] = "old-D74-binding"
        with self.assertRaisesRegex(ValueError, "classification or reciprocal binding differs"):
            self.check(relation=relation)
        relation = deepcopy(self.relation)
        relation["payload"]["relation_kind_ref"] = "relation.realizes"
        with self.assertRaises(Exception):
            self.check(relation=relation)

    def test_05_empty_relation_or_admission_refused(self):
        model = deepcopy(self.model)
        model["relation_refs"] = []
        with self.assertRaises(Exception):
            self.check(model=model)
        model = deepcopy(self.model)
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            self.check(model=model)

    def test_06_selected_receipt_has_one_bounded_model(self):
        result = subject.build()
        self.assertEqual(result["selected_governed_model_representations"], 1)
        self.assertEqual(result["member_index"], 3)
        self.assertEqual(result["authority_effect"], "none")
        self.assertFalse(result["original_member_admitted"])
        self.assertFalse(result["T10_complete"])

    def test_07_parent_symlink_and_changed_pinned_bytes_refuse(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real" / "input.json").write_bytes(b"{}")
            expected = hashlib.sha256(b"{}").hexdigest()
            self.assertEqual(subject.read_pinned(root, "real/input.json", expected), b"{}")
            (root / "linked").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "linked"):
                subject.read_pinned(root, "linked/input.json", expected)
            (root / "real" / "input.json").write_bytes(b'{"x":1}')
            with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                subject.read_pinned(root, "real/input.json", expected)

    def test_08_preloaded_false_module_cannot_replace_isolated_original(self):
        fake = ModuleType("lab_runtime.profiles")
        fake.select = lambda *_args, **_kwargs: None
        previous = sys.modules.get("lab_runtime.profiles")
        sys.modules["lab_runtime.profiles"] = fake
        try:
            _, _, _, observed = subject.actual_selections()
            self.assertEqual(observed["d75"]["profile_sha256"],
                             "bb8ab4538a524031924d8fa5c3352c2f9bc1cd66893c39222615160d0c9fd302")
        finally:
            if previous is None:
                sys.modules.pop("lab_runtime.profiles", None)
            else:
                sys.modules["lab_runtime.profiles"] = previous

    def test_09_changed_selector_schema_pin_refused(self):
        with self.assertRaisesRegex(ValueError, "changed selected bytes: .*source-profile.schema.json"):
            subject.actual_selections(source_schema_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
