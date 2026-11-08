import importlib.util
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w08_models", HERE / "select_models.py")
MODELS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODELS)


class W08DesignModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODELS.build()

    def test_ten_distinct_designs_and_twenty_eight_transitions(self):
        result = self.result
        self.assertEqual([x["member_index"] for x in result["entries"]], list(range(4, 14)))
        self.assertEqual(result["selected_governed_model_representations"], 10)
        self.assertEqual(result["design_transition_count"], 28)
        self.assertEqual(result["workflow_transitions_executed"], 0)
        self.assertEqual(result["original_members_admitted"], 0)
        self.assertFalse(result["T10_complete"])
        self.assertEqual(len({x["documents"]["model"]["node_id"] for x in result["entries"]}), 10)
        self.assertEqual(len({x["documents"]["typed_relation"]["payload"]["qualifiers"]["binding_ref"]
                              for x in result["entries"]}), 10)

    def test_schema_rejects_false_executable_design(self):
        schema = json.loads((HERE / "design-route.schema.json").read_text())
        route = MODELS.selected_inputs()[1][0]
        changed = dict(route, admitted_or_executable=True)
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(changed)

    def test_cross_document_misbindings_refuse(self):
        reader, routes, originals = MODELS.selected_inputs()
        route, original = routes[0], originals[0]
        mutations = (
            lambda m, i, r: m["relation_refs"][0].__setitem__("direction", "source"),
            lambda m, i, r: i["relation_refs"][0].__setitem__("counterpart_ref", "governed-model:wrong"),
            lambda m, i, r: r["payload"]["source"].__setitem__("version_ref", "implementation:wrong@local.1"),
            lambda m, i, r: r["payload"]["qualifiers"].__setitem__("parent_version_ref", "governed-model:wrong@local.1"),
        )
        for mutate in mutations:
            model, implementation, relation = MODELS.documents(original, route)
            mutate(model, implementation, relation)
            with self.assertRaisesRegex(ValueError, "representation join differs"):
                MODELS.verify(reader, route, original, model, implementation, relation)

    def test_changed_route_source_refuses(self):
        with patch.object(MODELS, "ROUTE_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "selected executable source changed"):
                MODELS.build()

    def test_matrix_row_claim_change_refuses(self):
        matrix = json.loads((MODELS.ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json").read_text())
        row = matrix["rows"][4]
        original = json.loads((MODELS.ROOT / row["original_body_binding"]["path"]).read_text())
        route = MODELS.module(MODELS.ROUTE, MODELS.ROUTE_SHA, "_w08_negative").design_routes(MODELS.ROOT)[0]
        for field, value in (("selected_representation", {"node_id": "model:other"}),
                             ("actual_owner_outcome", "admit"),
                             ("exact_grounded_relation_selected", {"relation": "other"})):
            changed = deepcopy(row)
            changed[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "unselected refused design"):
                MODELS.validate_original_selection(changed, original, route)

    def test_optimized_output_matches(self):
        child = subprocess.run([sys.executable, "-O", "-B", str(HERE / "select_models.py")],
                               capture_output=True, text=True, timeout=120, check=True)
        self.assertEqual(json.loads(child.stdout), self.result)


if __name__ == "__main__":
    unittest.main()
