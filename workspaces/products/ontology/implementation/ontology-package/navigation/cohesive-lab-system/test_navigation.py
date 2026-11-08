#!/usr/bin/env python3
from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path

import materialize
import validate


HERE = Path(__file__).resolve().parent


class AdmittedNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.navigation = validate.load(HERE / "navigation.json")
        cls.expected = materialize.build()

    def test_complete_validation_passes(self) -> None:
        self.assertEqual(validate.validate()["result"], "PASS")

    def test_materialization_is_deterministic(self) -> None:
        self.assertEqual(materialize.build(), materialize.build())
        self.assertEqual(self.navigation, self.expected)

    def test_only_root_authority_state_changes(self) -> None:
        for component in self.navigation["components"]:
            if component["component_id"] == "CAL-LAB-ONTOLOGY-SYSTEM":
                self.assertEqual(component["effective_authority_state"], "admitted-root")
            else:
                self.assertEqual(component["effective_authority_state"], component["source_authority_state"])

    def test_all_residue_is_routed(self) -> None:
        self.assertEqual(len(self.navigation["residue_routes"]), 5)
        self.assertTrue(all(item["owner_route"] and item["route_id"] for item in self.navigation["residue_routes"]))

    def test_review_owner_gaps_are_explicit(self) -> None:
        unresolved = [item for item in self.navigation["review_routes"] if item["route_status"] == "blocked-owner-unresolved"]
        self.assertEqual({item["group_id"] for item in unresolved}, {
            "cav2.governance.continuous-construction",
            "cav2.governance.dependency-kernel",
        })
        self.assertTrue(all(item["owner_resolution_route"] == "CyberAlchemy migration review owner" for item in unresolved))

    def test_child_admission_inflation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.navigation)
        child = next(item for item in mutated["components"] if item["component_id"] != "CAL-LAB-ONTOLOGY-SYSTEM")
        child["effective_authority_state"] = "admitted-root"
        self.assertTrue(any(error.startswith("child-authority-state-changed") for error in validate.semantic_errors(mutated, self.expected)))

    def test_query_routes_runtime_residue(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "query.py"), "route-residue", "CAL-RES-PRODUCT-RUNTIME-REALIZATION-UNPROVEN"],
            cwd=HERE,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Ontology Product runtime owner and D65 integration owner", result.stdout)

    def test_unknown_query_fails_closed(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HERE / "query.py"), "get-component", "missing"],
            cwd=HERE,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("unknown identity", result.stdout)


if __name__ == "__main__":
    unittest.main()
