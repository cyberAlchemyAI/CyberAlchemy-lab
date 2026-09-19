import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from common import ROOT, SOURCE, KINDS, load, dump
from check import check_instance
import source_rebinding


class PropositionContracts(unittest.TestCase):
    def example(self, kind):
        return load(ROOT / f"artifact-types/{kind}/v1/fixtures/valid/proposition.json")

    def test_high_conviction_does_not_prove_a_premise(self):
        data = self.example("premise")
        self.assertEqual(check_instance(data)["result"], "PASS")
        data["truth_posture"] = "proven"
        self.assertEqual(check_instance(data)["result"], "BLOCK")

    def test_hypothesis_cannot_be_a_working_assumption(self):
        data = self.example("hypothesis")
        data["adopted_to_proceed"] = True
        self.assertEqual(check_instance(data)["result"], "BLOCK")

    def test_hypothesis_requires_a_way_to_disprove_it(self):
        for value in ["", "  "]:
            data = self.example("hypothesis")
            data["falsification_condition"] = value
            self.assertEqual(check_instance(data)["result"], "BLOCK")

    def test_axiom_fanout_requires_distinct_dependents(self):
        data = self.example("axiom")
        data["downstream_refs"] = ["same", "same"]
        self.assertEqual(check_instance(data)["result"], "BLOCK")

    def test_kind_cannot_change_by_relabeling(self):
        for source in KINDS:
            for target in KINDS:
                if source == target:
                    continue
                with self.subTest(source=source, target=target):
                    data = self.example(source)
                    data["artifact_type_ref"] = f"cal.artifact-type.{target}/v1"
                    data["schema_version"] = f"cyberalchemy-lab-{target}/v1"
                    self.assertEqual(check_instance(data)["result"], "BLOCK")

    def test_schema_drift_stops_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "artifact-types/axiom/v1"
            dump(package / "artifact.json", load(ROOT / "artifact-types/axiom/v1/artifact.json"))
            dump(package / "schema.json", {})
            with self.assertRaisesRegex(ValueError, "Schema digest drift"):
                check_instance(self.example("axiom"), root)

    def test_cli_unknown_kind_and_invalid_shape_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "record.json"
            for data in [{"artifact_type_ref": "unknown"}, []]:
                dump(path, data)
                result = subprocess.run([sys.executable, str(ROOT / "check.py"), str(path)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["result"], "BLOCK")

    def test_cli_read_is_nonmutating_and_truth_is_unassessed(self):
        path = ROOT / "artifact-types/premise/v1/fixtures/valid/proposition.json"
        before = path.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / "check.py"), str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["truth_assessed"])
        self.assertEqual(path.read_bytes(), before)

    def test_source_rebinding_rejects_changed_axiom_meaning(self):
        source = (SOURCE / "authority/definitions/DEFINITIONS.md").read_text()
        changed = source.replace("An axiom is a **foundational proposition taken as given**", "An axiom is a **constraint enforced by code**", 1)
        self.assertNotEqual(source, changed)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "DEFINITIONS.md"
            path.write_text(changed)
            with self.assertRaisesRegex(ValueError, "Axiom meaning changed"):
                source_rebinding.build(path)

    def test_source_rebinding_rejects_ambiguous_heading(self):
        source = (SOURCE / "authority/definitions/DEFINITIONS.md").read_text()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "DEFINITIONS.md"
            path.write_text(source + "\n## CAV2-D53: Axiom\n")
            with self.assertRaisesRegex(ValueError, "Axiom heading is ambiguous"):
                source_rebinding.build(path)


if __name__ == "__main__":
    unittest.main()
