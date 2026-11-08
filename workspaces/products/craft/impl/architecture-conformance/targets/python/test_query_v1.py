from __future__ import annotations

import ast
from pathlib import Path
import unittest

from remaining_types.query_v1 import read_complete_settlement


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "remaining_types" / "query_v1.py"


class PythonQueryV1Test(unittest.TestCase):
    def test_reads_exact_targets_in_order_and_returns_closed_view(self) -> None:
        trace: list[tuple[str, str]] = []
        fixtures = {
            "settlement.read.settlement-by-id": {
                "settlement_status": "complete",
                "gross_amount_minor": 125000,
            },
            "settlement.read.payout-by-settlement": {
                "payout_id": "payout-001",
                "payout_status": "recorded",
            },
        }

        def read(target_id: str, settlement_id: str) -> dict[str, object]:
            trace.append((target_id, settlement_id))
            return fixtures[target_id]

        result = read_complete_settlement(
            {"settlement_id": "settlement-001"},
            read,
        )

        self.assertEqual(trace, [
            ("settlement.read.settlement-by-id", "settlement-001"),
            ("settlement.read.payout-by-settlement", "settlement-001"),
        ])
        self.assertEqual(result, {
            "settlement_id": "settlement-001",
            "settlement_status": "complete",
            "gross_amount_minor": 125000,
            "payout_id": "payout-001",
            "payout_status": "recorded",
        })

    def test_source_is_one_exact_synchronous_query_function(self) -> None:
        module = ast.parse(SOURCE.read_text(encoding="utf8"))
        self.assertEqual(len(module.body), 1)
        function = module.body[0]
        self.assertIs(type(function), ast.FunctionDef)
        self.assertEqual(function.name, "read_complete_settlement")
        self.assertEqual([argument.arg for argument in function.args.args], [
            "input_data",
            "read",
        ])
        self.assertEqual(len(function.body), 3)
        self.assertFalse(any(isinstance(node, (
            ast.AsyncFunctionDef,
            ast.Await,
            ast.Yield,
            ast.YieldFrom,
            ast.Global,
            ast.Nonlocal,
        )) for node in ast.walk(function)))


if __name__ == "__main__":
    unittest.main()
