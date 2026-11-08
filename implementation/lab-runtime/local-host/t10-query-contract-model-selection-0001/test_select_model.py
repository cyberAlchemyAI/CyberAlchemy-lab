from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_query_model", HERE / "select_model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class QueryModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader, cls.row, cls.original, cls.route, cls.query = m.selected_inputs()
        cls.model, cls.implementation, cls.relation = m.documents(cls.original)

    def check(self, model=None, implementation=None, relation=None, route=None, query=None):
        m.verify_documents(m.ROOT, self.reader, self.original,
                           model if model is not None else deepcopy(self.model),
                           implementation if implementation is not None else deepcopy(self.implementation),
                           relation if relation is not None else deepcopy(self.relation),
                           route if route is not None else deepcopy(self.route),
                           query if query is not None else deepcopy(self.query))

    def test_selected_consumers_and_model(self):
        self.check()
        output = m.build()
        self.assertEqual(output["member_index"], 21)
        self.assertEqual(output["route_question_count"], 5)
        self.assertEqual(len(set(output["source_cuts"].values())), 3)
        self.assertEqual(output["o03_cold_validated_scopes"], ["current-specialist-owner", "historical-d73-slice"])
        self.assertFalse(output["original_member_admitted"])

    def test_changed_route_source_refused(self):
        old = m.ROUTE
        try:
            m.ROUTE = (old[0], "0" * 64)
            with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                m.run_consumers(m.ROOT, self.reader)
        finally:
            m.ROUTE = old

    def test_changed_cold_answer_receipt_refused(self):
        old = m.O03_RESULT
        try:
            m.O03_RESULT = (old[0], "0" * 64)
            with self.assertRaisesRegex(ValueError, "changed selected bytes"):
                m.run_consumers(m.ROOT, self.reader)
        finally:
            m.O03_RESULT = old

    def test_route_executes_captured_buffer(self):
        real = self.reader.read_pinned
        def substituted(root, path, digest, **kw):
            raw = real(root, path, digest, **kw)
            return raw + b'\nraise RuntimeError("injected route buffer")\n' if path == m.ROUTE[0] else raw
        with patch.object(self.reader, "read_pinned", side_effect=substituted):
            with self.assertRaisesRegex(ValueError, "injected route buffer"):
                m.run_consumers(m.ROOT, self.reader)

    def test_o03_verifier_executes_captured_buffer(self):
        real = self.reader.read_pinned
        def substituted(root, path, digest, **kw):
            raw = real(root, path, digest, **kw)
            return raw + b'\nraise RuntimeError("injected O03 buffer")\n' if path == m.O03_VERIFY[0] else raw
        with patch.object(self.reader, "read_pinned", side_effect=substituted):
            with self.assertRaisesRegex(ValueError, "injected O03 buffer"):
                m.run_consumers(m.ROOT, self.reader)

    def test_conflated_source_cuts_refused(self):
        route = deepcopy(self.route)
        route["source_cuts"]["historical-D73"] = route["source_cuts"]["current-D75"]
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(route=route)

    def test_wrong_model_contract_refused(self):
        model = deepcopy(self.model)
        model["payload"]["contract_ref"] = "implementation/elsewhere.json"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(model=model)

    def test_wrong_relation_endpoint_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["source"]["ref"] = "implementation:unrelated"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(relation=relation)

    def test_wrong_relation_qualifier_refused(self):
        relation = deepcopy(self.relation)
        relation["payload"]["qualifiers"]["binding_ref"] = "implementation/elsewhere.json#sha256=" + "0" * 64
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(relation=relation)

    def test_wrong_implementation_schema_refused(self):
        implementation = deepcopy(self.implementation)
        implementation["payload"]["conforms_to_schema_refs"] = ["implementation/elsewhere.json"]
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(implementation=implementation)

    def test_wrong_reciprocal_direction_refused(self):
        model = deepcopy(self.model)
        model["relation_refs"][0]["direction"] = "source"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            self.check(model=model)

    def test_false_admission_refused(self):
        model = deepcopy(self.model)
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            self.check(model=model)


if __name__ == "__main__":
    unittest.main()
