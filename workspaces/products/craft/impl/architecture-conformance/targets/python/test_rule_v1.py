from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import unittest

from remaining_types.rule_v1 import RULE_V1_DELEGATE, evaluate_rule_v1


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "remaining_types" / "rule_v1.py"


class PythonRuleV1Test(unittest.TestCase):
    def test_declared_cases_are_boolean_deterministic_and_effect_free(self) -> None:
        cases = [
            ({
                "requestId": "request-001",
                "amount": 12500,
                "existingSettlementId": None,
            }, True),
            ({
                "requestId": "request-002",
                "amount": 12500,
                "existingSettlementId": "settlement-001",
            }, False),
            ({
                "requestId": "request-003",
                "amount": 0,
                "existingSettlementId": None,
            }, False),
        ]
        for input_data, expected in cases:
            snapshot = deepcopy(input_data)
            first = evaluate_rule_v1(input_data)
            second = evaluate_rule_v1(input_data)
            self.assertIs(type(first), bool)
            self.assertEqual(first, expected)
            self.assertEqual(second, expected)
            self.assertEqual(input_data, snapshot)

    def test_declares_the_existing_python_provider_as_delegate(self) -> None:
        self.assertEqual(RULE_V1_DELEGATE, {
            "rule_id": "can-settle-payout",
            "realization_id": "rule.python.function-v1",
            "provider_id": "python-rule-v1",
            "authority_effect": "none",
        })

    def test_source_is_a_thin_imported_delegate_without_ambient_effects(self) -> None:
        source = SOURCE.read_text(encoding="utf8")
        module = ast.parse(source)
        functions = [node for node in module.body
                     if isinstance(node, ast.FunctionDef)]
        self.assertEqual([function.name for function in functions],
                         ["evaluate_rule_v1"])
        function = functions[0]
        calls = [node for node in ast.walk(function)
                 if isinstance(node, ast.Call)]
        self.assertEqual(len(calls), 1)
        self.assertIs(type(calls[0].func), ast.Name)
        self.assertEqual(calls[0].func.id, "can_settle_payout")
        for forbidden in ["open(", "socket", "subprocess", "requests."]:
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
