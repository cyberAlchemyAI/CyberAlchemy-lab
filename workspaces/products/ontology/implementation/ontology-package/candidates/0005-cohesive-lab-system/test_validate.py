#!/usr/bin/env python3

import copy
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cohesive_validate", HERE / "validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CohesiveOntologyValidationTests(unittest.TestCase):
    def setUp(self):
        self.model = MODULE.load_json(MODULE.MODEL_PATH)
        self.candidate = MODULE.load_json(MODULE.CANDIDATE_PATH)

    def errors(self, model=None, candidate=None):
        return MODULE.validate_model(
            model or self.model,
            candidate or self.candidate,
            check_files=False,
        )

    def test_valid_candidate_passes(self):
        self.assertEqual([], MODULE.validate_model(self.model, self.candidate))

    def test_rejects_source_digest_drift(self):
        model = copy.deepcopy(self.model)
        model["sources"][0]["sha256"] = "0" * 64
        errors = MODULE.validate_model(model, self.candidate)
        self.assertTrue(any("digest drift" in item for item in errors))

    def test_rejects_duplicate_component(self):
        model = copy.deepcopy(self.model)
        model["components"].append(copy.deepcopy(model["components"][0]))
        self.assertTrue(any("duplicate identities" in item for item in self.errors(model)))

    def test_rejects_dangling_relation(self):
        model = copy.deepcopy(self.model)
        model["relations"][0]["target"] = "MISSING"
        self.assertTrue(any("unknown target" in item for item in self.errors(model)))

    def test_rejects_authority_inflation(self):
        model = copy.deepcopy(self.model)
        model["authority_effect"] = "admit"
        self.assertTrue(any("authority-effect" in item for item in self.errors(model)))

    def test_rejects_duplicate_identity_collapse(self):
        model = copy.deepcopy(self.model)
        model["query_contract"]["duplicate_ontology_identity_behavior"] = "pick-first"
        self.assertTrue(any("duplicate identities" in item for item in self.errors(model)))

    def test_rejects_vacuous_bridge(self):
        model = copy.deepcopy(self.model)
        bridge = next(item for item in model["relations"] if item["type"] == "realized_by")
        bridge["source_refs"].remove("SRC-D65-SYSTEM-ADMISSION")
        self.assertTrue(any("bridge-evidence" in item for item in self.errors(model)))

    def test_rejects_canonical_truth_collapse(self):
        model = copy.deepcopy(self.model)
        model["canonical_truth_contract"]["composition_rule"] = "The root is the replay source."
        self.assertTrue(any("root must not become replay source" in item for item in self.errors(model)))

    def test_rejects_disconnected_component(self):
        model = copy.deepcopy(self.model)
        isolated = "CAL-ONTOLOGY-PACKAGE-ARTIFACT-TYPE-V1"
        model["relations"] = [
            item for item in model["relations"] if item["source"] != isolated and item["target"] != isolated
        ]
        self.assertTrue(any("disconnected" in item for item in self.errors(model)))


if __name__ == "__main__":
    unittest.main()
