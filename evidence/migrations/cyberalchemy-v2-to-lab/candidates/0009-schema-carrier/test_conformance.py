import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, PACKAGE, load
from check import check_graph, validate_schema, read_input


class GraphConformance(unittest.TestCase):
    def setUp(self):
        self.schema = load(PACKAGE / "fixtures/valid/schema-record.json")
        self.graph = load(ROOT / "examples/conforming.json")

    def codes(self):
        return {x["code"] for x in check_graph(self.schema, self.graph)["errors"]}

    def test_conformance_does_not_prove_truth_or_authority(self):
        result = check_graph(self.schema, self.graph)
        self.assertTrue(result["conforms"])
        self.assertFalse(result["truth_assessed"])
        self.assertFalse(result["occupants_executed"])
        self.assertEqual(result["authority_effect"], "none")

    def test_missing_wrong_and_unexpected_fields(self):
        self.graph["nodes"][0]["fields"] = {"extra": True}
        self.assertTrue({"missing-field", "unexpected-field"} <= self.codes())
        self.graph["nodes"][0]["fields"] = {"title": 42}
        self.assertIn("wrong-field-type", self.codes())

    def test_constraints_and_connection_errors_both_reported(self):
        self.graph["nodes"][0]["fields"]["title"] = False
        self.graph["relations"] = []
        self.assertTrue({"wrong-field-type", "multiplicity"} <= self.codes())

    def test_relation_only_schema_needs_no_value_constraints(self):
        self.schema["constraints"] = []
        self.graph["nodes"][0]["fields"] = {"unconstrained": [1, 2]}
        self.assertTrue(check_graph(self.schema, self.graph)["conforms"])
        self.graph["relations"] = []
        self.assertIn("multiplicity", self.codes())

    def test_value_only_schema_needs_no_relations(self):
        self.schema["relations"] = []; self.schema["connection_rules"] = []
        self.graph["relations"] = []
        self.assertTrue(check_graph(self.schema, self.graph)["conforms"])
        self.graph["nodes"][0]["fields"]["title"] = 7
        self.assertIn("wrong-field-type", self.codes())

    def test_source_maximum_connections(self):
        self.graph["nodes"].append({"id": "owner-2", "kind": "owner", "fields": {"name": "Second"}})
        self.graph["relations"].append({"id": "edge-2", "kind": "owned-by", "source": "candidate-1", "target": "owner-2"})
        self.assertIn("multiplicity", self.codes())

    def test_target_minimum_and_maximum(self):
        self.schema["connection_rules"][0]["min_per_target"] = 1
        self.graph["nodes"].append({"id": "unused-owner", "kind": "owner", "fields": {"name": "Unused"}})
        self.assertIn("multiplicity", self.codes())
        self.graph["nodes"].pop()
        self.schema["connection_rules"][0]["max_per_target"] = 1
        self.graph["nodes"].append({"id": "candidate-2", "kind": "artifact", "fields": {"title": "Second"}})
        self.graph["relations"].append({"id": "edge-2", "kind": "owned-by", "source": "candidate-2", "target": "owner-1"})
        self.assertIn("multiplicity", self.codes())

    def test_wrong_endpoint_kind_does_not_satisfy_minimum(self):
        self.graph["relations"][0]["target"] = "candidate-1"
        self.assertTrue({"wrong-endpoint-kind", "multiplicity"} <= self.codes())

    def test_missing_endpoint(self):
        self.graph["relations"][0]["target"] = "absent"
        self.assertTrue({"missing-endpoint", "multiplicity"} <= self.codes())

    def test_duplicate_node_and_relation_ids(self):
        self.graph["nodes"].append(copy.deepcopy(self.graph["nodes"][0]))
        self.graph["relations"].append(copy.deepcopy(self.graph["relations"][0]))
        self.assertTrue({"duplicate-node", "duplicate-relation"} <= self.codes())

    def test_unknown_kinds_and_relations(self):
        self.graph["nodes"][0]["kind"] = "unknown"
        self.graph["relations"][0]["kind"] = "unknown"
        self.assertTrue({"unknown-kind", "unknown-relation"} <= self.codes())

    def test_boolean_and_float_are_not_integer_fields(self):
        self.schema["constraints"][0]["fields"][0]["value_type"] = "integer"
        for value in [True, 1.0, "1"]:
            self.graph["nodes"][0]["fields"]["title"] = value
            self.assertIn("wrong-field-type", self.codes())
        self.graph["nodes"][0]["fields"]["title"] = 10 ** 100
        self.assertTrue(check_graph(self.schema, self.graph)["conforms"])

    def test_scope_and_relative_level_are_bound(self):
        self.graph["scope_ref"] = "other"
        self.graph["level_ref"] = "other"
        self.assertTrue({"scope-mismatch", "level-mismatch"} <= self.codes())

    def test_schema_reference_closure(self):
        for field in ["source_kind", "target_kind", "relation_ref"]:
            schema = copy.deepcopy(self.schema); schema["connection_rules"][0][field] = "unknown"
            with self.assertRaises(ValueError):
                validate_schema(schema)
        self.schema["constraints"][0]["kind_ref"] = "unknown"
        with self.assertRaises(ValueError):
            validate_schema(self.schema)

    def test_duplicate_field_declarations_and_reversed_bounds(self):
        schema = copy.deepcopy(self.schema)
        schema["constraints"][0]["fields"].append(copy.deepcopy(schema["constraints"][0]["fields"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate name"):
            validate_schema(schema)
        self.schema["connection_rules"][0]["min_per_source"] = 2
        with self.assertRaisesRegex(ValueError, "Reversed multiplicity"):
            validate_schema(self.schema)

    def test_unsupported_path_equations_are_rejected(self):
        self.schema["path_equations"] = ["a;b=c"]
        with self.assertRaises(ValueError):
            validate_schema(self.schema)

    def test_occupant_text_is_data_not_code(self):
        self.graph["nodes"][0]["fields"]["title"] = "__import__('os').system('false')"
        before = copy.deepcopy((self.schema, self.graph))
        self.assertTrue(check_graph(self.schema, self.graph)["conforms"])
        self.assertEqual(before, (self.schema, self.graph))

    def test_cli_codes_and_duplicate_input_keys(self):
        for name, code in [("conforming", 0), ("wrong-field", 1), ("missing-connection", 1)]:
            result = subprocess.run([sys.executable, str(ROOT / "check.py"), str(PACKAGE / "fixtures/valid/schema-record.json"), str(ROOT / f"examples/{name}.json")], capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["conforms"], code == 0)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"; path.write_text('{"nodes":[],"nodes":[1]}')
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                read_input(path)


if __name__ == "__main__":
    unittest.main()
