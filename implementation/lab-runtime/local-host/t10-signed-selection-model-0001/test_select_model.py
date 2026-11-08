"""Executable historical W07 selection and local model classification checks."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_signed_selection_model", HERE / "select_model.py")
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class SignedSelectionModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins, cls.row, cls.original, cls.actual = subject.selected_inputs()
        cls.model, cls.implementation, cls.relation = subject.documents(cls.original)

    def check(self, model=None, implementation=None, relation=None, actual=None):
        subject.verify_documents(subject.ROOT, self.pins,
                                 model if model is not None else self.model,
                                 implementation if implementation is not None else self.implementation,
                                 relation if relation is not None else self.relation,
                                 actual if actual is not None else self.actual)

    def test_01_real_signed_consumer_selects_one_local_model(self):
        self.check()
        result = subject.build()
        self.assertEqual(result["selected_governed_model_representations"], 1)
        self.assertEqual(result["consumer_result"]["case_count"], 4)
        self.assertEqual([w["domain"] for w in result["consumer_result"]["signature_verified_witnesses"]],
                         ["engineering", "research"])
        self.assertEqual(self.original["relation_refs"], [])
        self.assertFalse(result["original_member_admitted"])
        self.assertFalse(result["T10_complete"])

    def test_02_changed_signed_witness_result_refused_by_real_consumer(self):
        source = subject.ROOT / subject.CONSUMER["path"]
        subject.import_bytes(source, subject.CONSUMER["sha256"])
        spec = importlib.util.spec_from_file_location("t10_signed_w07_consumer_test", source)
        consumer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(consumer)
        selection = consumer.strict_json(consumer.pinned({"path": consumer.SELECTION,
                                                           "sha256": consumer.SELECTION_SHA256}))
        witness = selection["signed_coupling_witnesses"][0]
        signed_result = consumer.strict_json(consumer.pinned(witness["result_binding"]))
        changed = deepcopy(signed_result)
        changed["result"] = "PASS" if signed_result["result"] != "PASS" else "FAIL"
        with self.assertRaisesRegex(ValueError, "signed witness result"):
            consumer.verify_witness(witness, result=changed)

    def test_03_changed_selected_bytes_refused(self):
        for binding in (subject.SELECTION, subject.W07, subject.PREPARATION, subject.RESULT):
            with self.subTest(binding=binding["path"]):
                with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                    self.pins.read_pinned(subject.ROOT, binding["path"], "0" * 64)

    def test_04_wrong_relation_endpoint_or_binding_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["source"]["ref"] = "implementation:other"
        with self.assertRaises(Exception):
            self.check(relation=relation)
        relation = deepcopy(self.relation)
        relation["payload"]["qualifiers"]["binding_ref"] = "other-consumer"
        with self.assertRaises(Exception):
            self.check(relation=relation)

    def test_05_wrong_rule_or_evidence_refused(self):
        model = deepcopy(self.model)
        model["payload"]["rule_refs"] = ["unrelated-selection#"]
        with self.assertRaises(Exception):
            self.check(model=model)
        implementation = deepcopy(self.implementation)
        implementation["evidence_refs"][2] = "other-receipt.json"
        with self.assertRaises(Exception):
            self.check(implementation=implementation)
        implementation = deepcopy(self.implementation)
        implementation["payload"]["conforms_to_schema_refs"] = [subject.SELECTION["path"]]
        with self.assertRaises(Exception):
            self.check(implementation=implementation)

    def test_06_empty_relation_or_authority_refused(self):
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
            with self.assertRaisesRegex(ValueError, "linked or nonregular import origin"):
                subject.import_bytes(root / "linked/source.py", subject.digest(b"pass\n"))


if __name__ == "__main__":
    unittest.main()
