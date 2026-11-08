"""Executable W08 consumer and relation-backed model selection tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_workflow_model", HERE / "select_model.py")
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


def consumer_module():
    path = subject.ROOT / subject.CONSUMER["path"]
    spec = importlib.util.spec_from_file_location("t10_original_workflow_consumer", path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class WorkflowModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared, cls.row, cls.original, cls.observed = subject.selected_inputs()
        cls.model, cls.implementation, cls.relation = subject.documents(cls.original)

    def check(self, model=None, implementation=None, relation=None, observed=None):
        subject.verify_documents(subject.ROOT, self.shared,
                                 model if model is not None else self.model,
                                 implementation if implementation is not None else self.implementation,
                                 relation if relation is not None else self.relation,
                                 observed if observed is not None else self.observed)

    def test_01_actual_consumer_selects_one_local_representation(self):
        self.check()
        result = subject.build()
        self.assertEqual(result["member_index"], 14)
        self.assertEqual(result["selected_governed_model_representations"], 1)
        self.assertEqual(result["consumer_result"]["result"], "PASS")
        self.assertEqual(result["authority_effect"], "none")
        self.assertFalse(result["original_member_admitted"])
        self.assertFalse(result["T10_complete"])
        self.assertEqual(self.original["relation_refs"], [])

    def test_02_schema_valid_run_with_wrong_producer_lineage_refused(self):
        consumer = consumer_module()
        control = json.loads(self.shared.read_pinned(subject.ROOT, **subject.CONTROL))
        run = json.loads(self.shared.read_pinned(subject.ROOT, **subject.RUN))
        producer = json.loads(self.shared.read_pinned(subject.ROOT, **subject.T31_RESULT))
        consumer.validate_run(consumer.selected_validator(control), run)
        changed = deepcopy(producer)
        selected = next(row for row in changed["new_output_transitions"]
                        if row["transition_ref"] == "transition:research:executed")
        selected["workflow_run_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "T31 output lineage mismatch"):
            consumer.verify_lineage(changed, subject.RUN["sha256"])

    def test_03_wrong_control_or_source_pin_refused(self):
        with self.assertRaisesRegex(ValueError, "changed selected bytes"):
            self.shared.read_pinned(subject.ROOT, subject.MATRIX_SCHEMA_BINDINGS[1]["path"], "0" * 64)
        with self.assertRaisesRegex(ValueError, "changed selected bytes"):
            self.shared.read_pinned(subject.ROOT, subject.T31_RESULT["path"], "0" * 64)
        with self.assertRaisesRegex(ValueError, "changed selected bytes"):
            self.shared.read_pinned(subject.ROOT, subject.PREPARATION["path"], "0" * 64)

    def test_04_wrong_endpoint_or_relation_kind_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["source"]["ref"] = "implementation:cyberalchemy-lab:repeatable-operation"
        with self.assertRaisesRegex(ValueError, "classification or producer binding differs"):
            self.check(relation=relation)
        relation = deepcopy(self.relation)
        relation["payload"]["relation_kind_ref"] = "relation.realizes"
        with self.assertRaises(Exception):
            self.check(relation=relation)

    def test_05_wrong_parent_or_consumer_binding_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["qualifiers"]["parent_version_ref"] = "wrong-model"
        with self.assertRaisesRegex(ValueError, "classification or producer binding differs"):
            self.check(relation=relation)
        implementation = deepcopy(self.implementation)
        implementation["payload"]["execution_entrypoint_ref"] = "other.py"
        with self.assertRaisesRegex(ValueError, "classification or producer binding differs"):
            self.check(implementation=implementation)

    def test_06_missing_relation_or_false_admission_refused(self):
        model = deepcopy(self.model)
        model["relation_refs"] = []
        with self.assertRaises(Exception):
            self.check(model=model)
        model = deepcopy(self.model)
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            self.check(model=model)

    def test_07_changed_model_rule_or_consumer_evidence_refused(self):
        model = deepcopy(self.model)
        model["payload"]["rule_refs"][1] = "unrelated-schema#"
        with self.assertRaisesRegex(ValueError, "classification or producer binding differs"):
            self.check(model=model)
        implementation = deepcopy(self.implementation)
        implementation["evidence_refs"][1] = "unrelated-run.json"
        with self.assertRaisesRegex(ValueError, "classification or producer binding differs"):
            self.check(implementation=implementation)
        relation = deepcopy(self.relation)
        relation["payload"]["relation_evidence_refs"][1] = "unrelated-run.json"
        with self.assertRaisesRegex(ValueError, "classification or producer binding differs"):
            self.check(relation=relation)


if __name__ == "__main__":
    unittest.main()
