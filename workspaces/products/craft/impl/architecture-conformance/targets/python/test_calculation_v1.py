from __future__ import annotations

import ast
from pathlib import Path
import unittest

from remaining_types.calculation_v1 import calculate_net_settlement


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "remaining_types" / "calculation_v1.py"


class PythonCalculationV1Test(unittest.TestCase):
    def test_returns_owner_declared_values(self) -> None:
        cases = (
            (125000, 2500, 122500),
            (5000, 0, 5000),
            (0, 0, 0),
            (1000000000, 125000, 999875000),
        )
        for gross, fee, expected in cases:
            with self.subTest(gross=gross, fee=fee):
                result = calculate_net_settlement(gross, fee)
                self.assertIs(type(result), int)
                self.assertEqual(result, expected)

    def test_source_has_one_public_calculation_and_one_subtraction(self) -> None:
        module = ast.parse(SOURCE.read_text(encoding="utf8"))
        functions = [
            node for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(len(functions), 1)
        function = functions[0]
        self.assertIs(type(function), ast.FunctionDef)
        self.assertEqual(function.name, "calculate_net_settlement")
        self.assertEqual(len(function.body), 1)
        self.assertIsInstance(function.body[0], ast.Return)
        self.assertIsInstance(function.body[0].value, ast.BinOp)
        self.assertIsInstance(function.body[0].value.op, ast.Sub)


if __name__ == "__main__":
    unittest.main()
