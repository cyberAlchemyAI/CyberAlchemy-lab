from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from jsonschema import ValidationError


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("t10_source_retention_models", HERE / "select_models.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class SourceRetentionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.reader, cls.route, cls.rows, cls.originals = m.selected_inputs()
        cls.saved = json.loads(cls.source.exact(m.ROOT, {"path": m.ROUTE_RESULT[0],
                                                     "sha256": m.ROUTE_RESULT[1]}))
        cls.schema = json.loads(cls.source.exact(m.ROOT, {"path": m.ROUTE_SCHEMA[0],
                                                      "sha256": m.ROUTE_SCHEMA[1]}))

    def test_three_distinct_relation_backed_models(self):
        result = m.build()
        self.assertEqual([entry["member_index"] for entry in result["entries"]], [24, 25, 26])
        self.assertEqual(result["selected_governed_model_representations"], 3)
        self.assertEqual(len({entry["documents"]["model"]["node_id"] for entry in result["entries"]}), 3)
        self.assertEqual(len({entry["documents"]["typed_relation"]["payload"]["qualifiers"]["binding_ref"]
                              for entry in result["entries"]}), 3)
        self.assertEqual(result["source_projection"]["disposition_counts"],
                         {"adapt": 88, "reference": 43, "block": 9})
        self.assertFalse(result["source_import_or_archive_replay_executed"])
        self.assertFalse(result["public_body_export_allowed"])
        self.assertFalse(result["owner_access_authority_verified"])
        self.assertEqual(result["selected_source_effects"], 0)
        self.assertEqual(result["original_members_admitted"], 0)
        self.assertFalse(result["T10_complete"])

    def test_changed_route_source_refuses(self):
        with patch.object(m, "ROUTE", (m.ROUTE[0], "0" * 64)):
            with self.assertRaisesRegex(ValueError, "selected executable source changed"):
                m.selected_inputs()

    def test_changed_route_receipt_refuses(self):
        with patch.object(m, "ROUTE_RESULT", (m.ROUTE_RESULT[0], "0" * 64)):
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                m.selected_inputs()

    def test_changed_original_refusal_or_owner_outcome_refuses(self):
        row = self.rows[1]
        original = self.originals[1]
        disposition = self.source.body(m.ROOT, row["original_disposition_binding"])
        choice = self.source.body(m.ROOT, row["review_choice_binding"])
        for field, value in (("admission_or_runtime_use_allowed", True),
                             ("actual_owner_outcome", "admit")):
            changed = deepcopy(disposition)
            changed[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "refusal differs"):
                m.validate_original_member(25, row, original, changed, choice)

    def changed_route(self, field, value):
        route, saved = deepcopy(self.route), deepcopy(self.saved)
        route[field] = value
        saved["routes"][field] = value
        return route, saved

    def test_public_export_refuses_even_with_matching_receipt(self):
        route, saved = deepcopy(self.route), deepcopy(self.saved)
        route["source_projection"]["public_body_export_allowed"] = True
        saved["routes"]["source_projection"]["public_body_export_allowed"] = True
        with self.assertRaises(ValidationError):
            m.validate_route(route, saved, self.rows, self.schema)

    def test_archive_replay_refuses_even_with_matching_receipt(self):
        route, saved = self.changed_route("source_import_or_archive_replay_executed", True)
        with self.assertRaises(ValidationError):
            m.validate_route(route, saved, self.rows, self.schema)

    def test_wrong_archive_digest_refuses(self):
        route, saved = deepcopy(self.route), deepcopy(self.saved)
        route["source_projection"]["archive_sha256"] = "0" * 64
        saved["routes"]["source_projection"]["archive_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ceiling differs"):
            m.validate_route(route, saved, self.rows, self.schema)

    def test_wrong_disposition_binding_refuses(self):
        route, saved = deepcopy(self.route), deepcopy(self.saved)
        route["o06_disposition_binding"]["sha256"] = "0" * 64
        saved["routes"]["o06_disposition_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ceiling differs"):
            m.validate_route(route, saved, self.rows, self.schema)

    def test_private_source_policy_denials(self):
        source, rows = self.source, self.rows
        disposition = source.body(m.ROOT, rows[0]["original_target_bindings"][0])
        policy = source.body(m.ROOT, rows[1]["original_target_bindings"][0])
        core_binding, manifest_binding, archive_binding = rows[2]["original_target_bindings"]
        core = source.body(m.ROOT, core_binding)
        manifest = source.body(m.ROOT, manifest_binding)
        o05 = source.body(m.ROOT, self.route["o05_receipt_binding"])
        for field, value in (("body_import", True), ("public_export", True),
                             ("semantic_admission", True), ("execution", True),
                             ("source_retirement", True),
                             ("source_owner_and_access_authority_verified", True)):
            changed = deepcopy(policy)
            changed[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "private-use or authority ceiling differs"):
                source.link_source(disposition, changed, core, manifest, archive_binding["sha256"], o05,
                                   core_binding, manifest_binding, archive_binding)

    def test_each_document_relation_refusal(self):
        for index, row, original in zip(m.NAMES, self.rows, self.originals):
            model, implementation, relation = m.documents(index, row, original)
            m.verify(self.reader, self.route, index, row, original, model, implementation, relation)
            changed = deepcopy(relation)
            changed["payload"]["qualifiers"]["binding_ref"] = "wrong#sha256=" + "0" * 64
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "relation or private-use ceiling differs"):
                m.verify(self.reader, self.route, index, row, original, model, implementation, changed)

    def test_wrong_schema_valid_implementation_kind_refuses(self):
        model, implementation, relation = m.documents(24, self.rows[0], self.originals[0])
        implementation["payload"]["implementation_kind"] = "other"
        with self.assertRaisesRegex(ValueError, "relation or private-use ceiling differs"):
            m.verify(self.reader, self.route, 24, self.rows[0], self.originals[0],
                     model, implementation, relation)

    def test_schema_valid_relation_extra_link_refuses(self):
        model, implementation, relation = m.documents(24, self.rows[0], self.originals[0])
        relation["relation_refs"] = [{"relation_kind_ref": "relation.instance-of",
                                      "direction": "source", "counterpart_kind": "governed-model",
                                      "counterpart_ref": model["node_id"]}]
        with self.assertRaisesRegex(ValueError, "relation or private-use ceiling differs"):
            m.verify(self.reader, self.route, 24, self.rows[0], self.originals[0],
                     model, implementation, relation)

    def test_false_authority_refuses(self):
        model, implementation, relation = m.documents(25, self.rows[1], self.originals[1])
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            m.verify(self.reader, self.route, 25, self.rows[1], self.originals[1],
                     model, implementation, relation)

    def test_optimized_output_matches(self):
        normal = m.build()
        child = subprocess.run([sys.executable, "-O", "-B", str(HERE / "select_models.py")],
                               capture_output=True, text=True, timeout=90, check=True)
        self.assertEqual(json.loads(child.stdout), normal)


if __name__ == "__main__":
    unittest.main()
