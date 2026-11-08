from copy import deepcopy
import json
from pathlib import Path
import unittest

import select_model as m


HERE = Path(__file__).resolve().parent


class QueryResidueModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (cls.parent, cls.reader, cls.row, cls.original, cls.route,
         cls.query, cls.proposal, cls.links) = m.selected_inputs()
        cls.model, cls.implementation, cls.relation = m.documents(cls.parent, cls.original)

    def test_selected_five_link_model(self):
        m.verify_documents(self.parent, self.reader, self.original, self.route, self.links,
                           self.model, self.implementation, self.relation)
        observed = m.build()
        self.assertEqual(json.loads((HERE / "RESULT.json").read_bytes()), observed)
        self.assertEqual(observed["member_index"], 27)
        self.assertEqual(len(observed["links"]), 5)
        self.assertEqual(len(set(observed["source_cuts"].values())), 3)
        self.assertFalse(observed["original_member_admitted"])

    def test_changed_selected_query_consumer_refuses(self):
        old = m.QUERY_MODEL_SHA
        try:
            m.QUERY_MODEL_SHA = "0" * 64
            with self.assertRaisesRegex(ValueError, "selected query consumer source changed"):
                m.build()
        finally:
            m.QUERY_MODEL_SHA = old

    def test_changed_proposal_source_cut_refuses(self):
        proposal = deepcopy(self.proposal)
        proposal["current-D75"]["questions"]["lifecycle-D75"]["source_snapshot"]["source_cut_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source cut differs"):
            m.join_proposal(proposal, self.route)

    def test_changed_gap_count_refuses(self):
        proposal = deepcopy(self.proposal)
        proposal["native-O05"]["questions"]["native-source-lineage"]["gaps"].pop()
        with self.assertRaisesRegex(ValueError, "producer/consumer link differs"):
            m.join_proposal(proposal, self.route)

    def test_missing_question_refuses(self):
        proposal = deepcopy(self.proposal)
        proposal["historical-D73"]["questions"].pop("provenance")
        with self.assertRaisesRegex(ValueError, "producer/consumer link differs"):
            m.join_proposal(proposal, self.route)

    def test_conflated_cut_refuses(self):
        route = deepcopy(self.route)
        route["source_cuts"]["native-O05"] = route["source_cuts"]["current-D75"]
        with self.assertRaisesRegex(ValueError, "source cuts conflated"):
            m.join_proposal(self.proposal, route)

    def test_duplicate_route_question_cannot_hide_missing_question(self):
        route = deepcopy(self.route)
        rows = route["producer_consumer_questions"]
        provenance = next(i for i, row in enumerate(rows) if row["question"] == "provenance")
        authority = next(row for row in rows if row["question"] == "authority")
        rows[provenance] = deepcopy(authority)
        with self.assertRaisesRegex(ValueError, "complete five-question residue join required"):
            m.join_proposal(self.proposal, route)

    def test_wrong_relation_endpoint_refuses(self):
        relation = deepcopy(self.relation)
        relation["payload"]["target"]["ref"] = "governed-model:other"
        with self.assertRaisesRegex(ValueError, "classification differs"):
            m.verify_documents(self.parent, self.reader, self.original, self.route, self.links,
                               self.model, self.implementation, relation)

    def test_false_authority_refuses(self):
        model = deepcopy(self.model)
        model["authority_effect"] = "admit"
        with self.assertRaises(Exception):
            m.verify_documents(self.parent, self.reader, self.original, self.route, self.links,
                               model, self.implementation, self.relation)


if __name__ == "__main__":
    unittest.main()
