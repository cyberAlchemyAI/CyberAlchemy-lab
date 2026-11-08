"""Historical O05 node/relation consumer and local model-selection tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_native_property_model", HERE / "select_model.py")
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class NativePropertyModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader, cls.row, cls.original, cls.actual = subject.selected_inputs()
        cls.model, cls.implementation, cls.relation = subject.documents(cls.original)

    def check(self, model=None, implementation=None, relation=None, actual=None):
        subject.verify_documents(subject.ROOT, self.reader,
                                 model if model is not None else self.model,
                                 implementation if implementation is not None else self.implementation,
                                 relation if relation is not None else self.relation,
                                 actual if actual is not None else self.actual)

    def test_01_actual_two_native_events_select_one_local_model(self):
        self.check()
        result = subject.build()
        self.assertEqual(result["member_index"], 18)
        self.assertEqual(result["selected_governed_model_representations"], 1)
        self.assertEqual(len(result["consumer_result"]["event_sha256"]), 2)
        self.assertFalse(result["original_member_admitted"])
        self.assertFalse(result["T10_complete"])
        self.assertEqual(self.original["relation_refs"], [])

    def test_02_schema_valid_properties_with_wrong_endpoint_witness_refuse(self):
        directory = subject.ROOT / "implementation/lab-runtime/local-host/t10-control-consumer-0001"
        sys.path.insert(0, str(directory))
        try:
            import consume_18 as consumer
            control = json.loads(self.reader.read_pinned(subject.ROOT, **subject.CONTROL))
            node_schema, relation_schema = consumer.selected_schemas(control)
            manifest = consumer.read_pinned(subject.MIGRATION_MANIFEST)
            base = consumer.BASE
            core = consumer.read_pinned({"path": base + "core.json", "sha256": manifest["core_sha256"]})
            files = {row["path"]: row["sha256"] for row in manifest["files"]}
            snapshot = consumer.read_pinned({"path": base + "native.snapshot", "sha256": files["native.snapshot"]})
            selection = consumer.read_pinned(subject.SOURCE_SELECTION)
            node = consumer.event(snapshot, consumer.NODE_EVENT)
            relation = consumer.event(snapshot, consumer.RELATION_EVENT)
            from jsonschema import Draft202012Validator
            self.assertFalse(list(Draft202012Validator(node_schema).iter_errors(node)))
            self.assertFalse(list(Draft202012Validator(relation_schema).iter_errors(relation)))
            changed = deepcopy(selection)
            item = next(row for row in changed["items"]
                        if row.get("record_structure_sha256") == relation["record_sha256"])
            item["source_endpoint_id"] = "unrelated-source-endpoint"
            with self.assertRaisesRegex(ValueError, "relation selected endpoint unresolved"):
                consumer.verify_witnesses(node, relation, core, changed, snapshot)
        finally:
            sys.path.remove(str(directory))

    def test_03_changed_schema_and_preparation_bytes_refused(self):
        for binding in (subject.SCHEMAS[0], subject.SCHEMAS[1], subject.PREPARATION):
            with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                self.reader.read_pinned(subject.ROOT, binding["path"], "0" * 64)

    def test_04_wrong_relation_endpoint_or_qualifier_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["source"]["ref"] = "implementation:cyberalchemy-lab:repeatable-operation"
        with self.assertRaisesRegex(ValueError, "classification or consumer binding differs"):
            self.check(relation=relation)
        relation = deepcopy(self.relation)
        relation["payload"]["qualifiers"]["binding_ref"] = "other-consumer"
        with self.assertRaisesRegex(ValueError, "classification or consumer binding differs"):
            self.check(relation=relation)

    def test_05_wrong_model_rule_or_evidence_refused(self):
        model = deepcopy(self.model)
        model["payload"]["rule_refs"][1] = "unrelated-schema#"
        with self.assertRaisesRegex(ValueError, "classification or consumer binding differs"):
            self.check(model=model)
        implementation = deepcopy(self.implementation)
        implementation["evidence_refs"][2] = "other-selection.json"
        with self.assertRaisesRegex(ValueError, "classification or consumer binding differs"):
            self.check(implementation=implementation)

    def test_06_empty_relation_and_false_admission_refused(self):
        model = deepcopy(self.model)
        model["relation_refs"] = []
        with self.assertRaises(Exception):
            self.check(model=model)
        model = deepcopy(self.model)
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            self.check(model=model)

    def test_07_equal_byte_linked_import_ancestor_refused(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real" / "source.py").write_bytes(b"pass\n")
            (root / "linked").symlink_to(root / "real", target_is_directory=True)
            expected = subject.digest(b"pass\n")
            with self.assertRaisesRegex(ValueError, "linked or nonregular import origin"):
                subject.import_source_bytes(root / "linked/source.py", expected)


if __name__ == "__main__":
    unittest.main()
