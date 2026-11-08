"""Focused retained W09 case/audit/review route and counterevidence tests."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_w09_evidence", HERE / "route.py")
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)


def sample():
    matrix = route.body(route.ROOT, route.MATRIX)
    row = matrix["rows"][28]
    receipt = route.body(route.ROOT, row["original_target_bindings"][0])
    review = route.body(route.ROOT, row["original_target_bindings"][1])
    audit = route.body(route.ROOT, receipt["audit_binding"])
    cases = [route.body(route.ROOT, binding) for binding in review["selected_case_bindings"]]
    return receipt, audit, review, cases


class W09Evidence(unittest.TestCase):
    def test_01_exact_three_cases_and_counterevidence(self):
        value = route.receipt()
        self.assertEqual(value["route"]["index"], 28)
        self.assertEqual([row["audit_result"] for row in value["route"]["case_audit_review_rows"]],
                         ["FLAG", "FLAG", "PASS"])
        self.assertEqual(value["selected_governed_model_representations"], 0)
        self.assertFalse(value["T10_complete"])

    def test_02_changed_bytes_and_linked_parent_refuse(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real" / "case.json").write_bytes(b'{}')
            binding = {"path": "real/case.json", "sha256": hashlib.sha256(b'{}').hexdigest()}
            self.assertEqual(route.exact(root, binding), b'{}')
            (root / "real" / "case.json").write_bytes(b'{"changed":true}')
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                route.exact(root, binding)
            (root / "alias").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                route.exact(root, {**binding, "path": "alias/case.json"})

    def test_03_swapped_case_or_review_selection_refuse(self):
        receipt, audit, review, cases = sample()
        changed = deepcopy(review)
        changed["selected_case_bindings"][0], changed["selected_case_bindings"][1] = \
            changed["selected_case_bindings"][1], changed["selected_case_bindings"][0]
        with self.assertRaisesRegex(ValueError, "case selection"):
            route.link_cases(receipt, audit, changed, cases)

    def test_04_changed_domain_or_facts_refuse(self):
        receipt, audit, review, cases = sample()
        changed = deepcopy(cases)
        changed[0]["domain"] = "research"
        with self.assertRaisesRegex(ValueError, "case→audit"):
            route.link_cases(receipt, audit, review, changed)
        changed = deepcopy(audit)
        changed["cases"][1]["facts"]["changed"] = True
        with self.assertRaisesRegex(ValueError, "case→audit"):
            route.link_cases(receipt, changed, review, cases)

    def test_05_counterevidence_cannot_be_promoted_to_pass(self):
        receipt, audit, review, cases = sample()
        changed = deepcopy(audit)
        changed["cases"][0]["result"] = "PASS"
        with self.assertRaisesRegex(ValueError, "case→audit"):
            route.link_cases(receipt, changed, review, cases)

    def test_06_lesson_and_canonical_claims_refuse(self):
        receipt, audit, review, cases = sample()
        changed = deepcopy(review)
        changed["new_scoped_Lesson_use"] = "permanent current Lesson permission"
        with self.assertRaisesRegex(ValueError, "review ceiling"):
            route.link_cases(receipt, audit, changed, cases)
        changed = deepcopy(receipt)
        changed["canonical_effects_applied"] = 1
        with self.assertRaisesRegex(ValueError, "posture differs"):
            route.link_cases(changed, audit, review, cases)

    def test_07_changed_historical_only_binding_refuses(self):
        receipt, audit, review, cases = sample()
        for binding in review["historical_only"]:
            self.assertIn(binding, receipt["files"])
            route.exact(route.ROOT, binding)
        changed = deepcopy(review)
        changed["historical_only"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "review ceiling differs"):
            route.link_cases(receipt, audit, changed, cases)


if __name__ == "__main__":
    unittest.main()
