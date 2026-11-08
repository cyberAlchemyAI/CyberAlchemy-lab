import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w09_select_model", HERE / "select_model.py")
MODEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)


class W09ModelSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODEL.build()

    def test_positive_exact_three_cases_and_relation(self):
        result = self.result
        self.assertEqual(result["member_index"], 28)
        self.assertEqual([r["audit_result"] for r in result["case_audit_review_rows"]],
                         ["FLAG", "FLAG", "PASS"])
        self.assertEqual(result["selected_governed_model_representations"], 1)
        self.assertFalse(result["original_member_admitted"])
        self.assertFalse(result["T10_complete"])
        self.assertEqual(result["authority_effect"], "none")
        documents = result["documents"]
        self.assertEqual(documents["typed_relation"]["payload"]["source"]["ref"],
                         documents["implementation"]["node_id"])
        self.assertEqual(documents["typed_relation"]["payload"]["target"]["ref"],
                         documents["model"]["node_id"])

    def test_output_schema_rejects_suppressed_counterevidence(self):
        schema = json.loads((HERE / "w09-route-result.schema.json").read_text())
        observed = MODEL.pinned_module(MODEL.ROUTE, MODEL.ROUTE_SHA, "route_case").route(MODEL.ROOT)
        observed["case_audit_review_rows"][0]["audit_result"] = "PASS"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(observed)

    def test_wrong_relation_and_contract_refuse(self):
        reader, _, original, observed = MODEL.selected_inputs()
        model, implementation, relation = MODEL.documents(original)
        relation["payload"]["source"]["ref"] = "implementation:wrong"
        with self.assertRaisesRegex(ValueError, "classification|join"):
            MODEL.verify(reader, original, observed, model, implementation, relation)

    def test_schema_valid_relation_misbindings_refuse(self):
        reader, _, original, observed = MODEL.selected_inputs()
        mutations = (
            ("source_version", lambda m, i, r: r["payload"]["source"].__setitem__("version_ref", MODEL.IMPLEMENTATION_VERSION + "-wrong")),
            ("target_version", lambda m, i, r: r["payload"]["target"].__setitem__("version_ref", MODEL.MODEL_VERSION + "-wrong")),
            ("parent_version", lambda m, i, r: r["payload"]["qualifiers"].__setitem__("parent_version_ref", MODEL.MODEL_VERSION + "-wrong")),
            ("model_direction", lambda m, i, r: m["relation_refs"][0].__setitem__("direction", "source")),
            ("implementation_counterpart", lambda m, i, r: i["relation_refs"][0].__setitem__("counterpart_ref", "governed-model:wrong")),
            ("relation_identity", lambda m, i, r: r.__setitem__("node_id", "typed-relation:other")),
            ("implementation_kind", lambda m, i, r: i["payload"].__setitem__("implementation_kind", "different-kind")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                model, implementation, relation = MODEL.documents(original)
                mutate(model, implementation, relation)
                with self.assertRaisesRegex(ValueError, "classification|join"):
                    MODEL.verify(reader, original, observed, model, implementation, relation)
        model, implementation, relation = MODEL.documents(original)
        implementation["payload"]["conforms_to_schema_refs"] = [original["payload"]["contract_ref"]]
        with self.assertRaisesRegex(ValueError, "classification|join"):
            MODEL.verify(reader, original, observed, model, implementation, relation)

    def test_changed_selected_source_refuses(self):
        with patch.object(MODEL, "ROUTE_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "selected source bytes changed"):
                MODEL.build()

    def test_optimized_run_matches(self):
        command = [sys.executable, "-O", "-B", str(HERE / "select_model.py")]
        child = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)
        self.assertEqual(json.loads(child.stdout), self.result)


if __name__ == "__main__":
    unittest.main()
