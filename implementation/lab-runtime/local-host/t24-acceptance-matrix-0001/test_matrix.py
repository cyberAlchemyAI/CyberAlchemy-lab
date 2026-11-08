import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).with_name("matrix.py")
spec = importlib.util.spec_from_file_location("t24_matrix", MODULE)
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)


class MatrixTests(unittest.TestCase):
    def test_exact_inventory_and_conservative_claims(self):
        result = matrix.build()
        self.assertEqual([r["id"] for r in result["rows"]], [f"AC{i:02d}" for i in range(1, 14)])
        self.assertEqual((result["original_tasks_accounted"], result["original_units_accounted"]), (46, 63))
        self.assertTrue(all(r["original_acceptance"] == "PENDING" for r in result["rows"]))
        self.assertFalse(result["human_owner_pilot_observed"])
        self.assertFalse(result["canonical_admission_or_release_effect"])
        self.assertEqual(result["original_acceptance_pass_count"], 0)
        self.assertIn("T19", next(r for r in result["rows"] if r["id"] == "AC07")["state_reported_local_task_status"])
        self.assertTrue(all(not r["local_task_completion_verified_by_this_matrix"] for r in result["rows"]))

    def test_saved_matrix_rebuilds_byte_identically(self):
        generated = json.dumps(matrix.build(), sort_keys=True, indent=2) + "\n"
        self.assertEqual(MODULE.with_name("MATRIX.json").read_text(), generated)

    def test_missing_clause_refuses(self):
        original = matrix.read

        def changed(root, relative):
            raw = original(root, relative)
            if relative == matrix.PRODUCT:
                return raw.replace(b"### AC12", b"### AX12")
            return raw

        with patch.object(matrix, "read", changed), self.assertRaisesRegex(ValueError, "Product acceptance source changed"):
            matrix.build()

    def test_unsupported_completion_refuses(self):
        original = matrix.read

        def changed(root, relative):
            raw = original(root, relative)
            if relative == matrix.STATE:
                state = json.loads(raw)
                state["tasks"][0]["status"] = "green-by-claim"
                return json.dumps(state).encode()
            return raw

        with patch.object(matrix, "read", changed), self.assertRaisesRegex(ValueError, "invalid local task status"):
            matrix.build()

    def test_existing_evidence_mutation_changes_binding(self):
        original = matrix.read
        baseline = matrix.build()
        evidence = next(iter(baseline["rows"][0]["state_reported_evidence_bindings"].values()))[0]["path"]

        def changed(root, relative):
            raw = original(root, relative)
            return raw + b"changed" if relative == evidence else raw

        with patch.object(matrix, "read", changed):
            mutated = matrix.build()
        self.assertNotEqual(baseline, mutated)
        self.assertEqual(mutated["original_acceptance_pass_count"], 0)

    def test_absolute_evidence_path_refuses(self):
        original = matrix.read

        def changed(root, relative):
            raw = original(root, relative)
            if relative == matrix.STATE:
                state = json.loads(raw)
                state["tasks"][0]["evidence"] = ["/etc/hosts"]
                return json.dumps(state).encode()
            return raw

        with patch.object(matrix, "read", changed), self.assertRaisesRegex(ValueError, "noncanonical input path"):
            matrix.build()

    def test_changed_task_mapping_refuses(self):
        original = matrix.read

        def changed(root, relative):
            raw = original(root, relative)
            if relative == f"{matrix.TASKS}/T19.md":
                return raw.replace(b"AC06", b"AC01")
            return raw

        with patch.object(matrix, "read", changed), self.assertRaisesRegex(ValueError, "local task contract set changed"):
            matrix.build()


if __name__ == "__main__":
    unittest.main()
