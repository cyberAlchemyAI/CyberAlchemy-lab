#!/usr/bin/env python3

import copy
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).with_name("validate.py")
SPEC = importlib.util.spec_from_file_location("candidate_validate", MODULE_PATH)
VALIDATE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATE)


class CandidateValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = VALIDATE.load_json(VALIDATE.CANDIDATE_PATH)
        cls.binding = VALIDATE.load_json(VALIDATE.BINDING_PATH)

    def assert_rejected(self, candidate=None, binding=None):
        with self.assertRaises(VALIDATE.ValidationFailure):
            VALIDATE.validate_documents(candidate or self.candidate, binding or self.binding, check_files=False)

    def test_exact_documents_pass(self):
        self.assertEqual(len(VALIDATE.validate_documents(self.candidate, self.binding)), 4)

    def test_candidate_authority_inflation_fails(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["authority_effect"] = "admit-runtime"
        self.assert_rejected(candidate=candidate)

    def test_runtime_adoption_inflation_fails(self):
        binding = copy.deepcopy(self.binding)
        binding["runtime_source"]["adopted"] = True
        self.assert_rejected(binding=binding)

    def test_initial_cut_drift_fails(self):
        binding = copy.deepcopy(self.binding)
        binding["implementation"]["initial_cut"]["node_subjects"] = 15
        self.assert_rejected(binding=binding)

    def test_acceptance_material_removal_fails(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["acceptance_material"].pop()
        self.assert_rejected(candidate=candidate)


if __name__ == "__main__":
    unittest.main()
