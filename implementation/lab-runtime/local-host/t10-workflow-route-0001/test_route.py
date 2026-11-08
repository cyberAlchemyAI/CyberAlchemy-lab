"""Causal local checks for W08 design routes and four observed candidate outputs."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("t10_workflow_route", HERE / "route.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


class Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((R.ROOT / R.MATRIX).read_bytes())

    def documents(self, index: int):
        row = self.matrix["rows"][index]
        original = R.body(R.ROOT, row["original_body_binding"])
        disposition = R.body(R.ROOT, row["original_disposition_binding"])
        choice = R.body(R.ROOT, row["review_choice_binding"])
        w08 = R.body(R.ROOT, row["original_target_bindings"][0])
        definition = R.body(R.ROOT, row["original_target_bindings"][1])
        return row, original, disposition, choice, w08, definition

    def test_saved_route_and_claim_ceiling(self):
        result = json.loads((HERE / "RESULT-0002.json").read_bytes())
        self.assertEqual(result, R.receipt())
        self.assertEqual(result["design_route_count"], 10)
        self.assertEqual(result["design_transition_count"], 28)
        self.assertEqual(result["actual_candidate_member_count"], 2)
        self.assertEqual(result["actual_candidate_transition_count"], 4)
        self.assertEqual(result["unobserved_w08_member_indices"], [4, 5, 7, 8, 9, 10, 11, 13])
        self.assertFalse(result["T10_complete"])
        self.assertEqual(result["selected_governed_model_representations"], 0)

    def test_all_ten_designs_close_on_original_contracts(self):
        rows = R.design_routes()
        self.assertEqual([row["index"] for row in rows], list(range(4, 14)))
        self.assertEqual(sum(len(row["transition_refs"]) for row in rows), 28)
        self.assertTrue(all(row["admitted_or_executable"] is False for row in rows))

    def test_changed_selected_body_bytes_refuse(self):
        binding = self.matrix["rows"][6]["original_body_binding"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / binding["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes((R.ROOT / binding["path"]).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                R.exact(root, binding)

    def test_wrong_member_kind_refuses(self):
        row, original, disposition, choice, w08, definition = self.documents(6)
        altered = copy.deepcopy(original)
        altered["kind"] = "workflow"
        with self.assertRaisesRegex(ValueError, "original refused model meaning differs"):
            R.validate_design(row, altered, disposition, choice, w08, definition, w08)

    def test_wrong_transition_direction_refuses(self):
        row, original, disposition, choice, w08, definition = self.documents(12)
        altered = copy.deepcopy(w08)
        altered["transitions"][1]["from_state"] = "evaluated"
        with self.assertRaisesRegex(ValueError, "transition semantics"):
            R.validate_design(row, original, disposition, choice, altered, definition, altered)

    def test_wrong_output_kind_refuses(self):
        routes = R.design_routes()
        first = json.loads((R.ROOT / R.T31_1 / "run-0001/RESULT.json").read_bytes())
        second = json.loads((R.ROOT / R.T31_2 / "run-0001/RESULT.json").read_bytes())
        altered = copy.deepcopy(second)
        altered["new_output_transitions"][0]["output_artifact_refs"][0]["carrier_ref"] = "cal.artifact-type.finding/v1"
        with self.assertRaisesRegex(ValueError, "actual output kind differs"):
            R.actual_routes(R.ROOT, routes, first, altered)

    def test_wrong_relation_counterpart_refuses_without_cartesian_expansion(self):
        row, _, _, _, w08, _ = self.documents(6)
        signature = copy.deepcopy(w08["transitions"][2]["selected_relation_signatures"][0])
        relation = R.body(R.ROOT, signature["relation_binding"])
        self.assertEqual(row["member_ref"], "protocol:W08:workflow:engineering")
        signature["target_kind"] = "product"
        with self.assertRaisesRegex(ValueError, "wrong relation kind, direction, counterpart"):
            R.validate_relation(signature, relation)

    def test_changed_actual_producer_output_refuses_cold_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first"
            second = root / "second"
            shutil.copytree(R.ROOT / R.T31_1 / "run-0001", first)
            shutil.copytree(R.ROOT / R.T31_2 / "run-0001", second)
            target = second / "engineering/workflow/generated-output.json"
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "actual T31 producer/consumer replay refused"):
                R.verify_t31(R.ROOT, first, second)

    def test_symlinked_selected_parent_refuses(self):
        binding = self.matrix["rows"][6]["original_body_binding"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relative = Path(binding["path"])
            real = root / "real"
            real.mkdir()
            (real / relative.name).write_bytes((R.ROOT / relative).read_bytes())
            current = root
            for part in relative.parts[:-2]:
                current /= part
                current.mkdir()
            (current / relative.parts[-2]).symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "unsafe parent"):
                R.exact(root, binding)


if __name__ == "__main__":
    unittest.main()
