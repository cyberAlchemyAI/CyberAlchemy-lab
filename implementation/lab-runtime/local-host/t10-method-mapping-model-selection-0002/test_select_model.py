from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_method_model", HERE / "select_model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MethodMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader, cls.row, cls.original, cls.schema_binding, cls.observed = m.selected_inputs()
        cls.model, cls.implementation, cls.relation = m.documents(cls.original, cls.schema_binding)
        impact = json.loads(cls.reader.read_pinned(m.ROOT, **cls.row["original_target_bindings"][0]))
        cls.proposal = impact["endpoint_proposals"][2]
        cls.schema = json.loads(cls.reader.read_pinned(m.ROOT, **cls.schema_binding))
        cls.method = json.loads(cls.reader.read_pinned(m.ROOT, *m.METHOD))
        cls.manifest = json.loads(cls.reader.read_pinned(m.ROOT, *m.MANIFEST))
        cls.receipt = json.loads(cls.reader.read_pinned(m.ROOT, *m.RECEIPT))
        cls.inspection = json.loads(cls.reader.read_pinned(m.ROOT, *m.INSPECTION))

    def consume(self, proposal=None, method=None, manifest=None, receipt=None, inspection=None):
        return m.run_consumer(m.ROOT, self.reader,
                              self.proposal if proposal is None else proposal,
                              self.schema,
                              self.method if method is None else method,
                              self.manifest if manifest is None else manifest,
                              self.receipt if receipt is None else receipt,
                              self.inspection if inspection is None else inspection,
                              self.schema_binding)

    def check(self, model=None, implementation=None, relation=None):
        m.verify_documents(m.ROOT, self.reader, self.original, self.schema_binding,
                           self.observed,
                           deepcopy(self.model) if model is None else model,
                           deepcopy(self.implementation) if implementation is None else implementation,
                           deepcopy(self.relation) if relation is None else relation)

    def catalog(self, inspection):
        return inspection["observations"]["joined"]["candidate_catalog"][
            "method:lab-governed-state-inspection@1.0.0-candidate.1"]

    def test_selected_local_pair(self):
        self.check()
        output = m.build()
        self.assertEqual(output["member_index"], 2)
        self.assertEqual(output["observed"]["candidate_endpoint_ref"],
                         "method:lab-governed-state-inspection")
        self.assertEqual(output["observed"]["candidate_endpoint_version_ref"],
                         "method:lab-governed-state-inspection@1.0.0-candidate.1")
        self.assertTrue(output["observed"]["inspection_join_cold_checked"])
        self.assertFalse(output["original_member_admitted"])
        self.assertFalse(output["T10_complete"])

    def test_changed_consumer_pin_refused(self):
        old = m.CONSUMER
        try:
            m.CONSUMER = (old[0], "0" * 64)
            with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                self.consume()
        finally:
            m.CONSUMER = old

    def test_captured_consumer_buffer_is_executed(self):
        real = self.reader.read_pinned

        def changed(root, path, digest, **kw):
            raw = real(root, path, digest, **kw)
            return raw + b'\nraise RuntimeError("captured consumer buffer")\n' if path == m.CONSUMER[0] else raw

        with patch.object(self.reader, "read_pinned", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "captured consumer buffer"):
                self.consume()

    def test_wrong_selector_refused(self):
        proposal = deepcopy(self.proposal)
        proposal["identity_selector"] = "/name"
        with self.assertRaisesRegex(ValueError, "mapping proposal differs"):
            self.consume(proposal=proposal)

    def test_changed_method_identity_refused(self):
        method = deepcopy(self.method)
        method["method_id"] = "method:other"
        with self.assertRaisesRegex(ValueError, "carrier posture differs"):
            self.consume(method=method)

    def test_invalid_method_carrier_refused(self):
        method = deepcopy(self.method)
        method.pop("method_id")
        with self.assertRaisesRegex(ValueError, "record invalid"):
            self.consume(method=method)

    def test_wrong_manifest_source_pin_refused(self):
        manifest = deepcopy(self.manifest)
        next(x for x in manifest["files"] if x["path"] == m.METHOD[0])["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "file pin differs"):
            self.consume(manifest=manifest)

    def test_wrong_receipt_inspection_pin_refused(self):
        receipt = deepcopy(self.receipt)
        next(x for x in receipt["files"] if x["path"] == m.INSPECTION[0])["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "file pin differs"):
            self.consume(receipt=receipt)

    def test_wrong_receipt_manifest_pin_refused(self):
        receipt = deepcopy(self.receipt)
        receipt["candidate_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "posture differs"):
            self.consume(receipt=receipt)

    def test_wrong_catalog_kind_refused(self):
        inspection = deepcopy(self.inspection)
        self.catalog(inspection)["semantic_kind"] = "product"
        with self.assertRaisesRegex(ValueError, "catalog row absent or ambiguous"):
            self.consume(inspection=inspection)

    def test_wrong_catalog_version_refused(self):
        inspection = deepcopy(self.inspection)
        self.catalog(inspection)["version_ref"] = "method:lab-governed-state-inspection@other"
        with self.assertRaisesRegex(ValueError, "identity differs"):
            self.consume(inspection=inspection)

    def test_wrong_catalog_record_refused(self):
        inspection = deepcopy(self.inspection)
        self.catalog(inspection)["record"]["name"] = "changed"
        with self.assertRaisesRegex(ValueError, "identity differs"):
            self.consume(inspection=inspection)

    def test_false_catalog_admission_refused(self):
        inspection = deepcopy(self.inspection)
        self.catalog(inspection)["effective_state"] = "admitted"
        with self.assertRaisesRegex(ValueError, "identity differs"):
            self.consume(inspection=inspection)

    def test_wrong_relation_endpoint_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["target"]["ref"] = "governed-model:other"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(relation=relation)

    def test_wrong_relation_direction_refused(self):
        model = deepcopy(self.model)
        model["relation_refs"][0]["direction"] = "source"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(model=model)

    def test_wrong_model_contract_refused(self):
        model = deepcopy(self.model)
        model["payload"]["contract_ref"] = "other"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(model=model)

    def test_schema_valid_classification_mutations_refused(self):
        mutations = (
            lambda a, b, c: c.__setitem__("node_id", "typed-relation:other"),
            lambda a, b, c: b["payload"].__setitem__("implementation_kind", "different-kind"),
            lambda a, b, c: c["payload"].__setitem__("relation_evidence_refs", ["other"]),
            lambda a, b, c: c.__setitem__("owner_ref", "role:other"),
            lambda a, b, c: b.__setitem__("scope_ref", "project:other"),
            lambda a, b, c: c["payload"].__setitem__("relation_lifecycle_state", "active"),
            lambda a, b, c: c["payload"]["source"].__setitem__("version_ref", "implementation:other@local.1"),
            lambda a, b, c: c["payload"]["qualifiers"].__setitem__("parent_version_ref", "governed-model:other@local.1"),
        )
        for mutate in mutations:
            model, implementation, relation = (
                deepcopy(self.model), deepcopy(self.implementation), deepcopy(self.relation))
            mutate(model, implementation, relation)
            with self.assertRaisesRegex(ValueError, "classification differs"):
                self.check(model=model, implementation=implementation, relation=relation)

    def test_false_admission_refused(self):
        model = deepcopy(self.model)
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            self.check(model=model)


if __name__ == "__main__":
    unittest.main()
