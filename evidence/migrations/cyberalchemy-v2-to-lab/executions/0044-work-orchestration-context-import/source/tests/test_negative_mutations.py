#!/usr/bin/env python3
"""Hostile mutation tests for the bounded composite work package."""

from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = PACKAGE_ROOT / "scripts/validate.py"
SPEC = importlib.util.spec_from_file_location("work_orchestration_validate", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class WorkOrchestrationNegativeMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.package = Path(self.temp.name) / "work-orchestration"
        shutil.copytree(PACKAGE_ROOT, self.package)
        self.original_package_root = VALIDATOR.PACKAGE_ROOT
        VALIDATOR.PACKAGE_ROOT = self.package

    def tearDown(self) -> None:
        VALIDATOR.PACKAGE_ROOT = self.original_package_root
        self.temp.cleanup()

    def load(self, relative: str) -> dict:
        return json.loads((self.package / relative).read_text(encoding="utf-8"))

    def save(self, relative: str, value: dict) -> None:
        (self.package / relative).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def assert_blocked(self, mutation) -> None:
        mutation()
        result = VALIDATOR.validate()
        self.assertEqual("BLOCK", result["status"], result)
        self.assertTrue(result["errors"], result)

    def test_baseline_passes(self) -> None:
        result = VALIDATOR.validate()
        self.assertEqual("PASS", result["status"], result)
        self.assertEqual(1, result["counts"]["product_capabilities"], result)

    def test_source_digest_drift_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("sources.json")
            value["sources"][0]["sha256"] = "0" * 64
            self.save("sources.json", value)
        self.assert_blocked(mutate)

    def test_product_identity_change_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("product-capability.json")
            value["capability_id"] = "CA2-CAP-OTHER"
            self.save("product-capability.json", value)
        self.assert_blocked(mutate)

    def test_second_product_capability_node_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("nodes.json")
            duplicate = copy.deepcopy(next(item for item in value["nodes"] if item["role"] == "product_capability"))
            duplicate["id"] = "WO-CAP-SECOND"
            value["nodes"].append(duplicate)
            self.save("nodes.json", value)
        self.assert_blocked(mutate)

    def test_unknown_relation_endpoint_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("relations.json")
            value["relations"][0]["target"] = "WO-MISSING"
            self.save("relations.json", value)
        self.assert_blocked(mutate)

    def test_selected_implementation_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("product-capability-support.json")
            value["realization_binding"]["implementation_ref"] = "cyberAlchemy-v2/work-orchestration/runtime"
            self.save("product-capability-support.json", value)
        self.assert_blocked(mutate)

    def test_authority_inflation_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("nodes.json")
            value["nodes"][0]["authority_effect"] = "granted"
            self.save("nodes.json", value)
        self.assert_blocked(mutate)

    def test_missing_history_residue_blocks(self) -> None:
        def mutate() -> None:
            value = self.load("residue.json")
            value["residue"] = [item for item in value["residue"] if item["residue_id"] != "CAP-RES-WORK-ORCH-HISTORY-OWNER"]
            self.save("residue.json", value)
        self.assert_blocked(mutate)

    def test_domainspec_surface_blocks(self) -> None:
        def mutate() -> None:
            (self.package / "domainspec").mkdir()
        self.assert_blocked(mutate)

    def test_unknown_operator_obligation_cannot_disappear(self) -> None:
        def mutate() -> None:
            value = self.load("product-capability-support.json")
            value["obligation_registry"]["obligations"] = [
                item for item in value["obligation_registry"]["obligations"]
                if item["obligation_id"] != "WO-OBL-UNKNOWN-FAILS-CLOSED"
            ]
            self.save("product-capability-support.json", value)
        self.assert_blocked(mutate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
