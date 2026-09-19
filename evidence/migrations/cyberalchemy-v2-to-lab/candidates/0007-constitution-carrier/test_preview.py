import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, PACKAGE, load
from check import preview, validate_record, read_input


class ConstitutionPreview(unittest.TestCase):
    def setUp(self):
        self.rulebook = load(PACKAGE / "fixtures/valid/constitution.json")
        self.subject = load(ROOT / "examples/matching.json")

    def test_matching_does_not_adopt_or_govern(self):
        result = preview(self.rulebook, self.subject)
        self.assertEqual(result["matching_rules"], ["preserve-counts", "preserve-meaning"])
        self.assertFalse(result["governs"])
        self.assertFalse(result["adoption_verified"])
        self.assertFalse(result["enforcement_performed"])
        self.assertTrue(all(not x["validation_executed"] for x in result["rules"]))

    def test_missing_attribute_is_indeterminate(self):
        self.subject["attributes"] = {}
        result = preview(self.rulebook, self.subject)
        self.assertEqual(result["matching_rules"], [])
        self.assertEqual(len(result["indeterminate_rules"]), 2)

    def test_wrong_attribute_does_not_match(self):
        self.subject["attributes"]["runtime_ref"] = "runtime:other"
        self.assertEqual(preview(self.rulebook, self.subject)["matching_rules"], [])

    def test_scope_and_kind_boundaries(self):
        for key in ["scope_ref", "subject_kind"]:
            subject = copy.deepcopy(self.subject); subject[key] = "outside"
            result = preview(self.rulebook, subject)
            self.assertFalse(result["scope_matches"])
            self.assertEqual(result["matching_rules"], [])

    def test_known_nonmatch_dominates_missing_selector(self):
        self.rulebook["selectors"].append({"selector_id": "epoch", "attribute": "epoch", "equals": "001"})
        self.rulebook["rules"][0]["selector_ids"].append("epoch")
        self.subject["attributes"]["runtime_ref"] = "wrong"
        self.assertEqual(preview(self.rulebook, self.subject)["rules"][0]["selector_state"], "does-not-match")

    def test_explicit_order_preserves_both_rules(self):
        self.rulebook["precedence"].reverse()
        result = preview(self.rulebook, self.subject)
        self.assertEqual(result["matching_rules"], ["preserve-meaning", "preserve-counts"])
        self.assertEqual(len(result["rules"]), 2)

    def test_precedence_must_cover_rules_once(self):
        for order in [["preserve-counts"], ["preserve-counts", "preserve-counts"]]:
            self.rulebook["precedence"] = order
            with self.assertRaises(ValueError):
                validate_record(self.rulebook)

    def test_duplicates_and_dangling_references_rejected(self):
        for field, value in [("selectors", [copy.deepcopy(self.rulebook["selectors"][0])] * 2),
                             ("rules", [copy.deepcopy(self.rulebook["rules"][0])] * 2)]:
            rulebook = copy.deepcopy(self.rulebook); rulebook[field] = value
            with self.assertRaises(ValueError):
                validate_record(rulebook)
        self.rulebook["rules"][0]["selector_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "Unknown rule selector"):
            validate_record(self.rulebook)

    def test_policy_reference_closure(self):
        self.rulebook["policies"][0]["rule_ids"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "Unknown policy rule"):
            validate_record(self.rulebook)

    def test_deterministic_rule_requires_binding(self):
        self.rulebook["rules"][0]["validation_binding_id"] = None
        with self.assertRaisesRegex(ValueError, "requires an exact validation binding"):
            validate_record(self.rulebook)

    def test_review_cannot_masquerade_as_execution(self):
        self.rulebook["rules"][1]["validation_binding_id"] = "import-counts"
        with self.assertRaisesRegex(ValueError, "cannot claim an executable binding"):
            validate_record(self.rulebook)

    def test_stale_binding_is_rejected(self):
        self.rulebook["validation_bindings"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            validate_record(self.rulebook)

    def test_binding_path_cannot_escape_lab(self):
        for name in ["../other/file.json", "/tmp/file.json"]:
            self.rulebook["validation_bindings"][0]["path"] = name
            with self.assertRaisesRegex(ValueError, "local relative path"):
                validate_record(self.rulebook)

    def test_binding_scope_must_match(self):
        self.rulebook["scope_ref"] = "different"
        with self.assertRaisesRegex(ValueError, "Binding scope differs"):
            validate_record(self.rulebook)

    def test_self_adoption_claim_rejected(self):
        for key, value in [("status", "adopted"), ("authority_effect", "govern"), ("adoption_verified", True)]:
            rulebook = copy.deepcopy(self.rulebook); rulebook[key] = value
            with self.assertRaises(ValueError):
                validate_record(rulebook)

    def test_input_objects_unchanged(self):
        before = copy.deepcopy((self.rulebook, self.subject))
        preview(self.rulebook, self.subject)
        self.assertEqual(before, (self.rulebook, self.subject))

    def test_cli_and_duplicate_input_keys(self):
        result = subprocess.run([sys.executable, str(ROOT / "check.py"), str(PACKAGE / "fixtures/valid/constitution.json"), str(ROOT / "examples/matching.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(json.loads(result.stdout)["governs"])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "subject.json"; path.write_text('{"scope_ref":"one","scope_ref":"two"}')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                read_input(path)


if __name__ == "__main__":
    unittest.main()
