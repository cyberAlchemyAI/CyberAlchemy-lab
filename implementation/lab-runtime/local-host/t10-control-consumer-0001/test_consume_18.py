import copy
import unittest

from jsonschema import Draft202012Validator

from consume import read_pinned
from consume_18 import (BASE, CONTROL, CONTROL_SHA256, MANIFEST_SHA256,
                        NODE_EVENT, RELATION_EVENT, SOURCE_SELECTION,
                        SOURCE_SELECTION_SHA256, consume, event, selected_schemas,
                        verify_witnesses)


class NativePropertyConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control = read_pinned({"path": CONTROL, "sha256": CONTROL_SHA256})
        cls.manifest = read_pinned({"path": BASE + "manifest.json", "sha256": MANIFEST_SHA256})
        cls.core = read_pinned({"path": BASE + "core.json", "sha256": cls.manifest["core_sha256"]})
        files = {row["path"]: row["sha256"] for row in cls.manifest["files"]}
        cls.snapshot = read_pinned({"path": BASE + "native.snapshot", "sha256": files["native.snapshot"]})
        cls.selection = read_pinned({"path": SOURCE_SELECTION, "sha256": SOURCE_SELECTION_SHA256})
        cls.node = event(cls.snapshot, NODE_EVENT)
        cls.relation = event(cls.snapshot, RELATION_EVENT)

    def test_two_actual_native_events_pass(self):
        self.assertEqual(consume()["result"], "PASS")

    def test_replaced_relation_schema_refuses(self):
        control = copy.deepcopy(self.control)
        control["control_bindings"][1] = control["control_bindings"][0]
        with self.assertRaisesRegex(ValueError, "schema pair"):
            selected_schemas(control)

    def test_false_runtime_permission_refuses(self):
        control = copy.deepcopy(self.control)
        control["native_or_runtime_use_allowed"] = True
        with self.assertRaisesRegex(ValueError, "control posture"):
            selected_schemas(control)

    def test_corrupt_embedded_event_refuses(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["files"][NODE_EVENT]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "event bytes"):
            event(snapshot, NODE_EVENT)

    def test_missing_node_version_fails_actual_schema(self):
        node_schema, _ = selected_schemas(self.control)
        node = copy.deepcopy(self.node)
        del node["version_ref"]
        self.assertFalse(Draft202012Validator(node_schema).is_valid(node))

    def test_changed_node_source_digest_refuses(self):
        node = copy.deepcopy(self.node)
        node["record_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "node source witness"):
            verify_witnesses(node, self.relation, self.core, self.selection, self.snapshot)

    def test_changed_relation_source_digest_refuses(self):
        relation = copy.deepcopy(self.relation)
        relation["record_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "relation source witness"):
            verify_witnesses(self.node, relation, self.core, self.selection, self.snapshot)

    def test_changed_relation_endpoint_refuses(self):
        relation = copy.deepcopy(self.relation)
        relation["target_version_ref"] = "source:unknown@candidate.1"
        with self.assertRaisesRegex(ValueError, "endpoint version"):
            verify_witnesses(self.node, relation, self.core, self.selection, self.snapshot)

    def test_existing_but_wrong_endpoint_refuses(self):
        relation = copy.deepcopy(self.relation)
        alternate = next(row["version_ref"] for row in self.core["record_index"]
                         if row["kind"] == "source" and row["version_ref"] not in
                         (relation["source_version_ref"], relation["target_version_ref"]))
        relation["target_version_ref"] = alternate
        with self.assertRaisesRegex(ValueError, "endpoint version"):
            verify_witnesses(self.node, relation, self.core, self.selection, self.snapshot)

    def test_fabricated_kind_containing_real_label_refuses(self):
        relation = copy.deepcopy(self.relation)
        relation["relation_kind_ref"] = "fabricated-notserves-but-matches"
        with self.assertRaisesRegex(ValueError, "relation kind"):
            verify_witnesses(self.node, relation, self.core, self.selection, self.snapshot)


if __name__ == "__main__":
    unittest.main()
