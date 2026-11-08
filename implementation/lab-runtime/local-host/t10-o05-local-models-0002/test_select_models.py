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
spec = importlib.util.spec_from_file_location("o05_local_models", HERE / "select_models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)


class O05LocalModelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader, cls.rows, cls.originals, cls.observed = models.selected_inputs()
        cls.route = models.selected_module(models.ROUTE, "_t10_o05_test_route")
        cls.receipt_binding = {"path": models.O05[0], "sha256": models.O05[1]}
        cls.result = models.build()

    def altered_read(self, selected_path, alter):
        actual = self.reader.read_pinned

        def read(root, path, sha256, **other):
            raw = actual(root, path, sha256, **other)
            if path == selected_path:
                body = json.loads(raw)
                alter(body)
                return json.dumps(body).encode()
            return raw

        return read

    def observe(self, read):
        return self.route.observe(read, models.ROOT, self.rows[0], self.rows[1],
                                  self.receipt_binding)

    def test_exact_two_local_models_and_receipt(self):
        result = self.result
        self.assertEqual([x["member_index"] for x in result["entries"]], [22, 23])
        self.assertEqual(len({x["contract_ref"] for x in result["entries"]}), 2)
        self.assertEqual(result["observed"]["vocabulary"]["edge_directions"],
                         {"directed": 49, "symmetric": 1})
        self.assertEqual(result["observed"]["vocabulary"]["predicate_count"], 20)
        generator = result["observed"]["generator"]
        self.assertEqual(generator["output_carrier_ref"], "cal.artifact-type.generated-output/v2")
        member22 = result["entries"][0]["documents"]["implementation"]
        self.assertEqual(member22["payload"]["execution_entrypoint_ref"],
                         generator["code_binding"]["path"])
        self.assertEqual(member22["payload"]["conforms_to_schema_refs"],
                         [generator["output_schema_binding"]["path"]])
        member23 = result["entries"][1]["documents"]["implementation"]
        self.assertEqual(member23["payload"]["execution_entrypoint_ref"], models.ROUTE[0])
        self.assertEqual(result["original_members_admitted"], 0)
        self.assertFalse(result["generator_rerun_this_run"])
        self.assertFalse(result["T10_complete"])
        self.assertEqual(result["authority_effect"], "none")

    def test_output_schema_refuses_global_or_inflated_claim(self):
        schema = json.loads(self.reader.read_pinned(models.ROOT, *models.OUTPUT_SCHEMA))
        wrong = deepcopy(self.observed)
        wrong["vocabulary"]["global_typed_relations_created"] = 1
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(wrong)

    def test_source_only_scope_refuses_execution(self):
        path = models.MEMBERS[22][1]
        read = self.altered_read(path, lambda body: body.__setitem__("source_execution_allowed", True))
        with self.assertRaisesRegex(ValueError, "source-only scope"):
            self.observe(read)

    def test_profile_refuses_predicate_loss(self):
        path = models.MEMBERS[23][1]
        read = self.altered_read(path, lambda body: body["predicates"].pop())
        with self.assertRaisesRegex(ValueError, "local vocabulary"):
            self.observe(read)

    def test_receipt_refuses_false_reproducibility(self):
        path = models.O05[0]
        read = self.altered_read(path,
                                 lambda body: body["observations"]["repeated_build"].__setitem__("result", "FAIL"))
        with self.assertRaisesRegex(ValueError, "repeated/cold evidence"):
            self.observe(read)

    def test_generator_output_contract_and_record_substitutions_refuse(self):
        generator = self.observed["generator"]
        path = generator["output_record_binding"]["path"]
        read = self.altered_read(path, lambda body: body["payload"].__setitem__("generator_ref", "unselected"))
        with self.assertRaisesRegex(ValueError, "generated-output contract or generator"):
            self.observe(read)
        read = self.altered_read(path, lambda body: body["payload"].__setitem__("output_digest", "sha256:" + "0" * 64))
        with self.assertRaisesRegex(ValueError, "generated-output contract or generator"):
            self.observe(read)
        read = self.altered_read(path, lambda body: body.__setitem__("authority_effect", "applied"))
        with self.assertRaises((ValidationError, ValueError)):
            self.observe(read)
        profile = models.MEMBERS[23][1]
        read = self.altered_read(profile,
            lambda body: body["output_carrier"]["schema_binding"].__setitem__("sha256", "0" * 64))
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.observe(read)

    def test_edge_refuses_global_and_direction_substitutions(self):
        manifest = json.loads(self.reader.read_pinned(models.ROOT,
            "implementation/lab-ontology/candidates/v1/migration/candidate/0001/manifest.json",
            "d4228ac71001acc4061431882dfa8c0155edf87d859bbf84527307580cb81214"))
        edge = next(x for x in manifest["files"] if x["path"].startswith("records/ontology-edge/"))
        path = self.route.PACKAGE + edge["path"]
        read = self.altered_read(path, lambda body: body["payload"].__setitem__("global_typed_relation_binding", {"ref": "global"}))
        with self.assertRaisesRegex(ValueError, "global/authority meaning"):
            self.observe(read)
        read = self.altered_read(path, lambda body: body["payload"].__setitem__("direction", "symmetric"))
        with self.assertRaisesRegex(ValueError, "edge direction"):
            self.observe(read)

    def test_relation_cross_document_misbindings_refuse_both_members(self):
        for row, original in zip(self.rows, self.originals):
            for field, alter in (
                ("target_version", lambda a, b, c: c["payload"]["target"].__setitem__("version_ref", "governed-model:other@1")),
                ("reciprocal", lambda a, b, c: b["relation_refs"][0].__setitem__("counterpart_ref", "governed-model:other")),
                ("relation_owner", lambda a, b, c: c.__setitem__("owner_ref", "role:other")),
                ("implementation_kind", lambda a, b, c: b["payload"].__setitem__("implementation_kind", "other")),
            ):
                with self.subTest(index=row["index"], field=field):
                    model, implementation, relation = models.documents(row, original, self.observed)
                    alter(model, implementation, relation)
                    with self.assertRaisesRegex(ValueError, "representation join differs"):
                        models.verify(self.reader, row, original, model, implementation, relation, self.observed)

    def test_generator_model_requires_actual_implementation_output_and_binding(self):
        row, original = self.rows[0], self.originals[0]
        for field, alter in (
            ("entrypoint", lambda a, b, c: b["payload"].__setitem__("execution_entrypoint_ref", models.ROUTE[0])),
            ("output_schema", lambda a, b, c: b["payload"].__setitem__("conforms_to_schema_refs", [models.OUTPUT_SCHEMA[0]])),
            ("relation_binding", lambda a, b, c: c["payload"]["qualifiers"].__setitem__("binding_ref", models.MEMBERS[22][1])),
            ("missing_output_evidence", lambda a, b, c: b["evidence_refs"].remove(self.observed["generator"]["output_record_binding"]["path"])),
        ):
            with self.subTest(field=field):
                docs = models.documents(row, original, self.observed)
                alter(*docs)
                with self.assertRaisesRegex(ValueError, "representation join differs"):
                    models.verify(self.reader, row, original, *docs, self.observed)

    def test_changed_route_source_refuses(self):
        with patch.object(models, "ROUTE", (models.ROUTE[0], "0" * 64)):
            with self.assertRaisesRegex(ValueError, "selected executable bytes changed"):
                models.build()

    def test_optimized_result_matches(self):
        child = subprocess.run([sys.executable, "-O", "-B", str(HERE / "select_models.py")],
                               capture_output=True, text=True, timeout=90, check=True)
        self.assertEqual(json.loads(child.stdout), self.result)


if __name__ == "__main__":
    unittest.main()
