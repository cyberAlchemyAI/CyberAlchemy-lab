import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, PACKAGE, load
from check import evaluate, validate_record, read_input


class InvariantEvaluation(unittest.TestCase):
    def setUp(self):
        self.rule = load(PACKAGE / "fixtures/valid/invariant.json")
        self.observation = load(ROOT / "examples/satisfied.json")

    def test_all_checks_required_for_satisfaction(self):
        result = evaluate(self.rule, self.observation)
        self.assertEqual(result["state"], "satisfied")
        self.assertTrue(result["observation_complete"])

    def test_single_violation_is_reported(self):
        self.observation["values"]["nodes"] = 814
        self.assertEqual(evaluate(self.rule, self.observation)["state"], "violated")

    def test_missing_never_becomes_success(self):
        del self.observation["values"]["documents"]
        result = evaluate(self.rule, self.observation)
        self.assertEqual(result["state"], "not-evaluable")
        self.assertFalse(result["observation_complete"])

    def test_violation_and_incomplete_evidence_both_survive(self):
        del self.observation["values"]["documents"]
        self.observation["values"]["nodes"] = 814
        result = evaluate(self.rule, self.observation)
        self.assertEqual(result["state"], "violated")
        self.assertFalse(result["observation_complete"])
        self.assertIn("not-evaluable", [x["state"] for x in result["checks"]])

    def test_mismatched_scope_and_subject_are_not_evaluable(self):
        for key in ["scope_ref", "subject_ref"]:
            observation = copy.deepcopy(self.observation); observation[key] = "wrong"
            result = evaluate(self.rule, observation)
            self.assertEqual(result["state"], "not-evaluable")
            self.assertTrue(all(x["state"] == "not-evaluable" for x in result["checks"]))

    def test_no_boolean_string_null_or_float_coercion(self):
        for value in [True, "815", None, 815.0, [], {}]:
            with self.subTest(value=value):
                self.observation["values"]["nodes"] = value
                self.assertEqual(evaluate(self.rule, self.observation)["state"], "not-evaluable")

    def test_integer_bounds_and_large_values(self):
        large = 10 ** 100
        for operator in ["equals", "at-least", "at-most"]:
            self.rule["checks"] = [{"check_id": "large", "field": "n", "operator": operator, "expected": large}]
            self.observation["values"] = {"n": large}
            self.assertEqual(evaluate(self.rule, self.observation)["state"], "satisfied")
            self.observation["values"]["n"] += -1 if operator == "at-least" else 1
            self.assertEqual(evaluate(self.rule, self.observation)["state"], "violated")

    def test_duplicate_check_ids_fail_even_with_different_fields(self):
        self.rule["checks"][1]["check_id"] = self.rule["checks"][0]["check_id"]
        with self.assertRaisesRegex(ValueError, "Duplicate check identity"):
            validate_record(self.rule)

    def test_expected_float_is_not_coerced(self):
        self.rule["checks"][0]["expected"] = 815.0
        with self.assertRaisesRegex(ValueError, "without coercion"):
            validate_record(self.rule)

    def test_code_like_operator_is_never_executed(self):
        self.rule["checks"][0]["operator"] = "__import__('os').system('false')"
        with self.assertRaises(ValueError):
            evaluate(self.rule, self.observation)

    def test_inputs_are_not_mutated_and_result_grants_no_effect(self):
        before = copy.deepcopy((self.rule, self.observation))
        result = evaluate(self.rule, self.observation)
        self.assertEqual(before, (self.rule, self.observation))
        self.assertEqual(result["authority_effect"], "none")
        self.assertFalse(result["enforcement_performed"])

    def test_cli_exit_codes_distinguish_outcomes(self):
        for name, code, state in [("satisfied", 0, "satisfied"), ("violated", 1, "violated"), ("missing", 2, "not-evaluable")]:
            result = subprocess.run([sys.executable, str(ROOT / "check.py"), str(PACKAGE / "fixtures/valid/invariant.json"), str(ROOT / f"examples/{name}.json")], capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertEqual(json.loads(result.stdout)["state"], state)

    def test_duplicate_json_keys_and_nan_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            for data in ['{"nodes": 815, "nodes": 814}', '{"nodes": NaN}']:
                path.write_text(data)
                with self.assertRaises(ValueError):
                    read_input(path)


if __name__ == "__main__":
    unittest.main()
