"""Focused producer/consumer and refusal checks for T10 21/27."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t10_query_residue_route", HERE / "route.py")
route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route)


def sample():
    matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
    query, residue = matrix["rows"][21], matrix["rows"][27]
    contract = route.body(route.ROOT, query["original_target_bindings"][1])
    proposal = route.body(route.ROOT, residue["original_target_bindings"][0])["native-O05"]
    result = route.body(route.ROOT, proposal["result_binding"])["questions"]["native-source-lineage"]
    chosen = proposal["questions"]["native-source-lineage"]
    response = route.body(route.ROOT, chosen["response_binding"])
    return query, chosen, result, response, contract


class QueryResidue(unittest.TestCase):
    def test_01_exact_three_cut_producer_consumer_route(self):
        value = route.receipt()
        observed = value["route"]
        self.assertEqual(observed["members"], [21, 27])
        self.assertEqual(len(observed["producer_consumer_questions"]), 5)
        self.assertEqual(len(set(observed["source_cuts"].values())), 3)
        self.assertEqual(value["selected_governed_model_representations"], 0)
        self.assertFalse(value["T10_complete"])

    def test_02_changed_bytes_and_symlink_parent_refuse(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "actual").mkdir()
            (root / "actual" / "result.json").write_bytes(b'{}')
            binding = {"path": "actual/result.json", "sha256": hashlib.sha256(b'{}').hexdigest()}
            self.assertEqual(route.exact(root, binding), b'{}')
            (root / "actual" / "result.json").write_bytes(b'{"changed":true}')
            with self.assertRaisesRegex(ValueError, "changed bytes"):
                route.exact(root, binding)
            (root / "alias").symlink_to(root / "actual", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                route.exact(root, {**binding, "path": "alias/result.json"})

    def test_03_wrong_original_kind_or_selection_refuses(self):
        query, _, _, _, _ = sample()
        bad = deepcopy(query)
        bad["selected_representation"] = {"kind": "governed-model"}
        with self.assertRaisesRegex(ValueError, "selected model claim changed"):
            route.original_row(route.ROOT, bad, 21)
        bad = deepcopy(query)
        bad["original_body_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "changed bytes"):
            route.original_row(route.ROOT, bad, 21)

    def test_04_changed_later_consumer_binding_refuses(self):
        _, proposal, result, response, contract = sample()
        changed = deepcopy(proposal)
        changed["response_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "producer/consumer response binding differs"):
            route.semantic_link("native-O05", "native-source-lineage", changed, result, response,
                                contract, result["response_binding"])

    def test_05_changed_gaps_or_partition_refuses(self):
        _, proposal, result, response, contract = sample()
        changed = deepcopy(proposal)
        changed["gaps"] = []
        with self.assertRaisesRegex(ValueError, "query projection differs"):
            route.semantic_link("native-O05", "native-source-lineage", changed, result, response,
                                contract, result["response_binding"])
        changed = deepcopy(result)
        changed["counts"]["mapped"] -= 1
        with self.assertRaisesRegex(ValueError, "partition differs"):
            route.semantic_link("native-O05", "native-source-lineage", proposal, changed, response,
                                contract, result["response_binding"])

    def test_06_historical_as_current_and_wrong_query_contract_refuse(self):
        _, proposal, result, response, contract = sample()
        changed = deepcopy(response)
        changed["freshness"]["state"] = "historical"
        with self.assertRaisesRegex(ValueError, "scope, currentness, or partition differs"):
            route.semantic_link("native-O05", "native-source-lineage", proposal, result, changed,
                                contract, result["response_binding"])
        changed = deepcopy(contract)
        changed["query_ids"] = ["other"]
        with self.assertRaisesRegex(ValueError, "scope, currentness, or partition differs"):
            route.semantic_link("native-O05", "native-source-lineage", proposal, result, response,
                                changed, result["response_binding"])

    def test_07_producer_receipt_must_pin_consumed_response(self):
        query, proposal, _, _, _ = sample()
        receipt_binding = next(b for b in query["original_evidence_bindings"]
                               if b["path"].endswith("/receipts/query-coverage.json"))
        receipt = route.body(route.ROOT, receipt_binding)
        selection = route.body(route.ROOT, route.O03_SELECTION)
        required = query["original_target_bindings"][1:4] + [proposal["response_binding"]]
        route.producer_bindings(receipt, selection, required)
        changed = deepcopy(receipt)
        changed["files"] = [row for row in changed["files"]
                            if row["path"] != proposal["response_binding"]["path"]]
        with self.assertRaisesRegex(ValueError, "producer does not pin consumed bytes"):
            route.producer_bindings(changed, selection, required)

    def test_08_changed_producer_semantic_digest_refuses(self):
        _, proposal, result, response, contract = sample()
        changed = deepcopy(result)
        changed["response_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "semantic response digest differs"):
            route.semantic_link("native-O05", "native-source-lineage", proposal, changed, response,
                                contract, result["response_binding"])

    def test_09_swapped_friendly_question_refuses(self):
        _, proposal, result, response, contract = sample()
        changed = deepcopy(response)
        changed["query"]["query_id"] = "authority-explanation"
        with self.assertRaisesRegex(ValueError, "scope, currentness, or partition differs"):
            route.semantic_link("native-O05", "native-source-lineage", proposal, result, changed,
                                contract, result["response_binding"])

    def test_10_changed_producer_selection_and_historical_swap_refuse(self):
        matrix = route.body(route.ROOT, {"path": route.MATRIX, "sha256": route.MATRIX_SHA})
        contract = route.body(route.ROOT, matrix["rows"][21]["original_target_bindings"][1])
        all_proposals = route.body(route.ROOT, matrix["rows"][27]["original_target_bindings"][0])
        group = all_proposals["historical-D73"]
        result = route.body(route.ROOT, group["result_binding"])
        changed_result = deepcopy(result)
        changed_result["selection_binding"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "producer result posture differs"):
            route.producer_result(changed_result, "historical-d73-slice", ("authority", "lifecycle", "provenance"))
        authority = group["questions"]["authority"]
        response = route.body(route.ROOT, authority["response_binding"])
        changed_response = deepcopy(response)
        changed_response["query"]["query_id"] = "capability-provenance"
        with self.assertRaisesRegex(ValueError, "scope, currentness, or partition differs"):
            route.semantic_link("historical-D73", "authority", authority, result["questions"]["authority"],
                                changed_response, contract, authority["response_binding"])


if __name__ == "__main__":
    unittest.main()
