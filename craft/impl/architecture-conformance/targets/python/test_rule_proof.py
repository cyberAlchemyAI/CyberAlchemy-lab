import json
from pathlib import Path
import unittest

from rule_proof import RuleProofError, build_proof, inspect_source, mutate_source


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[5]


class PythonRuleProofTest(unittest.TestCase):
    def test_full_native_proof_is_complete(self) -> None:
        proof = build_proof(REPOSITORY_ROOT)
        self.assertEqual(proof["summary"]["accounting"]["positive"], {
            "declared": 3, "passed": 3, "failed": 0, "unaccounted": 0,
        })
        self.assertEqual(proof["summary"]["accounting"]["mutations"], {
            "declared": 3, "killed": 3, "survived": 0, "unaccounted": 0,
        })
        self.assertTrue(proof["runtime"]["workspace"]["isolated"])

    def test_dynamic_and_import_hook_forms_fail_closed(self) -> None:
        hostiles = [
            ("import importlib\ndef can_settle_payout(input: dict) -> bool:\n    return True\n", "PY_RULE_IMPORT_UNSUPPORTED"),
            ("def can_settle_payout(input: dict) -> bool:\n    return __import__('os') is not None\n", "PY_RULE_EXPRESSION_UNSUPPORTED"),
            ("async def can_settle_payout(input: dict) -> bool:\n    return True\n", "PY_RULE_MODULE_SHAPE_UNSUPPORTED"),
        ]
        for source, code in hostiles:
            with self.subTest(code=code):
                inspected = inspect_source(source, "can_settle_payout")
                self.assertFalse(inspected["supported"])
                self.assertIn(code, inspected["diagnostics"])

    def test_mutator_rejects_unsupported_base(self) -> None:
        with self.assertRaises(RuleProofError) as caught:
            mutate_source("def can_settle_payout(input):\n return bool(input)\n", "can_settle_payout", "wrong-result")
        self.assertEqual(caught.exception.code, "PY_RULE_MUTATION_BASE_UNSUPPORTED")


if __name__ == "__main__":
    unittest.main()
