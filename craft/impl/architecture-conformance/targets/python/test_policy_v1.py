from __future__ import annotations

import ast
from pathlib import Path
import unittest

from remaining_types.policy_v1 import select_settlement_route


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "remaining_types" / "policy_v1.py"


class PythonPolicyV1Test(unittest.TestCase):
    def test_returns_owner_declared_strategy_identities(self) -> None:
        cases = (
            (5000, 10000, False, False, "settlement.route.standard"),
            (5000, 10000, True, False, "settlement.route.expedited"),
            (5000, 10000, True, True, "settlement.route.manual-review"),
            (15000, 10000, True, False, "settlement.route.standard"),
            (5000, 4000, True, False, "settlement.route.standard"),
        )
        for amount, limit, expedite, manual, expected in cases:
            with self.subTest(expected=expected):
                selected = select_settlement_route({
                    "amount_minor": amount,
                    "expedite_limit_minor": limit,
                    "expedite_requested": expedite,
                    "manual_review_required": manual,
                })
                self.assertIs(type(selected), str)
                self.assertEqual(selected, expected)

    def test_source_is_one_selector_without_calls_or_ambient_reads(self) -> None:
        module = ast.parse(SOURCE.read_text(encoding="utf8"))
        functions = [
            node for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(len(functions), 1)
        selector = functions[0]
        self.assertIs(type(selector), ast.FunctionDef)
        self.assertEqual(selector.name, "select_settlement_route")
        self.assertEqual(len(selector.body), 1)
        self.assertIsInstance(selector.body[0], ast.Return)
        self.assertFalse(any(isinstance(node, ast.Call) for node in ast.walk(selector)))
        self.assertFalse(any(
            isinstance(node, (ast.Await, ast.Yield, ast.YieldFrom, ast.Global,
                              ast.Nonlocal, ast.Attribute))
            for node in ast.walk(selector)
        ))


if __name__ == "__main__":
    unittest.main()
