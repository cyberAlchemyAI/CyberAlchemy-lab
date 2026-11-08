from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("o02_models", HERE / "select_models.py")
MODELS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODELS)


class O02LocalModelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODELS.build()

    def test_four_distinct_source_bound_classifications(self):
        result = self.result
        self.assertEqual([entry["member_index"] for entry in result["entries"]], [16, 17, 19, 20])
        self.assertEqual(len({entry["contract_ref"] for entry in result["entries"]}), 4)
        self.assertEqual(result["native_observed"]["confidence_level"], "not-assessed")
        self.assertFalse(result["native_observed"]["global_edge_selected"])
        self.assertFalse(result["native_replayed_this_run"])
        self.assertEqual(result["original_members_admitted"], 0)
        self.assertFalse(result["T10_complete"])

    def test_schema_refuses_inflated_native_confidence(self):
        schema = json.loads((HERE / "native-route.schema.json").read_text())
        route = MODELS.module(MODELS.ROUTE, MODELS.ROUTE_SHA, "_o02_schema_test").routes(MODELS.ROOT)
        route["observed"]["confidence_level"] = "verified"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(route)

    def test_original_selection_mutations_refuse(self):
        route = MODELS.module(MODELS.ROUTE, MODELS.ROUTE_SHA, "_o02_selection_test").routes(MODELS.ROOT)
        matrix = json.loads((MODELS.ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json").read_text())
        row = matrix["rows"][16]
        original = json.loads((MODELS.ROOT / row["original_body_binding"]["path"]).read_text())
        for field, value in (("selected_representation", {"node_id": "other"}),
                             ("actual_owner_outcome", "admit"),
                             ("exact_grounded_relation_selected", {"relation": "other"})):
            changed = deepcopy(row)
            changed[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "original member selection differs"):
                MODELS.validate_member(changed, original, route, 16)

    def test_schema_valid_relation_misbindings_refuse(self):
        reader, _, rows, originals = MODELS.selected_inputs()
        row, original = rows[0], originals[0]
        mutations = (
            lambda m, i, r: m["relation_refs"][0].__setitem__("direction", "source"),
            lambda m, i, r: i["payload"].__setitem__("implementation_kind", "other"),
            lambda m, i, r: r.__setitem__("node_id", "typed-relation:other"),
            lambda m, i, r: r["payload"]["source"].__setitem__("version_ref", "implementation:other@1"),
            lambda m, i, r: r["payload"]["qualifiers"].__setitem__("parent_version_ref", "governed-model:other@1"),
            lambda m, i, r: r["payload"].__setitem__("relation_evidence_refs", ["other"]),
        )
        for mutate in mutations:
            model, implementation, relation = MODELS.documents(row, original)
            mutate(model, implementation, relation)
            with self.assertRaisesRegex(ValueError, "representation join differs"):
                MODELS.verify(reader, row, original, model, implementation, relation)

    def test_changed_selected_route_source_refuses(self):
        with patch.object(MODELS, "ROUTE_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "selected executable bytes changed"):
                MODELS.build()

    def test_optimized_output_matches(self):
        child = subprocess.run([sys.executable, "-O", "-B", str(HERE / "select_models.py")],
                               capture_output=True, text=True, timeout=90, check=True)
        self.assertEqual(json.loads(child.stdout), self.result)


if __name__ == "__main__":
    unittest.main()
