from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

from remaining_types.operation_v1 import complete_settlement_operation


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "remaining_types" / "operation_v1.py"
HOSTILES = (
    HERE.parent.parent / "families" / "state-changing-action" / "hostiles"
)
CLOSURE = "return-await-cancel-close-dispose-finalizer-quiescence"


class Harness:
    def __init__(self, allowed: bool = True, fail_write: bool = False):
        self.allowed = allowed
        self.fail_write = fail_write
        self.trace: list[str] = []
        self.guard_input: dict[str, object] | None = None
        self.rollback_count = 0

    def guard(self, guard_id, input_data):
        self.trace.append(f"guard:{guard_id}")
        self.guard_input = dict(input_data)
        return {"allowed": self.allowed}

    def read(self, target_id, settlement_id):
        self.trace.append(f"read:{target_id}")
        if target_id == "settlement.read.settlement-by-id":
            return {"settlement_id": settlement_id}
        return {"account_id": "account-001"}

    def begin_atomic(self):
        self.trace.append("atomic:begin")

        def write(target_id, _value):
            self.trace.append(f"write:{target_id}")
            if self.fail_write and target_id == (
                "settlement.write.settlement-status"
            ):
                raise RuntimeError("write failed")

        def commit(mode):
            self.trace.append(f"atomic:commit:{mode}")

        def rollback():
            self.rollback_count += 1
            self.trace.append("atomic:rollback")

        return {"write": write, "commit": commit, "rollback": rollback}

    def external_effect(self, target_id, event):
        self.trace.append(f"effect:{target_id}")
        self.trace.append(f'event:{event["event_type"]}')

    def close(self, closure, failure_code):
        if failure_code is not None:
            self.trace.append("outcome:failure")
        self.trace.append(f"continuation:{closure}")

    def ports(self):
        return {
            "guard": self.guard,
            "read": self.read,
            "begin_atomic": self.begin_atomic,
            "external_effect": self.external_effect,
            "close": self.close,
        }


class PythonOperationV1Test(unittest.TestCase):
    def test_committed_success_has_exact_observable_order(self) -> None:
        harness = Harness()
        input_data = {
            "settlement_id": "settlement-001",
            "expected_state_version": 7,
        }
        result = complete_settlement_operation(input_data, harness.ports())
        harness.trace.append("outcome:success")

        self.assertEqual(harness.guard_input, input_data)
        self.assertEqual(harness.trace, [
            "guard:rule.can-settle-payout",
            "read:settlement.read.settlement-by-id",
            "read:settlement.read.payout-account",
            "atomic:begin",
            "write:settlement.write.payout-record",
            "write:settlement.write.settlement-status",
            "atomic:commit:all-or-nothing",
            "effect:event-store.append.PayoutCreated",
            "event:PayoutCreated",
            f"continuation:{CLOSURE}",
            "outcome:success",
        ])
        self.assertEqual(result, {
            "kind": "success",
            "value": {
                "settlement_id": "settlement-001",
                "payout_id": "account-001:settlement-001",
                "status": "committed",
            },
            "failure_code": None,
            "exactly_once_distributed_delivery_claimed": False,
        })

    def test_rejected_guard_starts_no_transition(self) -> None:
        harness = Harness(allowed=False)
        result = complete_settlement_operation({
            "settlement_id": "settlement-001",
            "expected_state_version": 6,
        }, harness.ports())

        self.assertEqual(harness.trace, [
            "guard:rule.can-settle-payout",
            "outcome:failure",
            f"continuation:{CLOSURE}",
        ])
        self.assertEqual(result["kind"], "failure")
        self.assertEqual(result["value"], None)
        self.assertEqual(result["failure_code"], "guard-rejected")

    def test_write_failure_rolls_back_without_external_effect(self) -> None:
        harness = Harness(fail_write=True)
        result = complete_settlement_operation({
            "settlement_id": "settlement-001",
            "expected_state_version": 7,
        }, harness.ports())

        self.assertEqual(result["failure_code"], "write-failed")
        self.assertEqual(result["value"], None)
        self.assertEqual(harness.rollback_count, 1)
        self.assertNotIn(
            "effect:event-store.append.PayoutCreated",
            harness.trace,
        )

    def test_classifies_all_five_s1_residues_from_native_fields(self) -> None:
        expected = {
            "before-state-write-failure.json":
                "RMT_S1_BEFORE_STATE_WRITE_FAILURE",
            "between-state-and-outbox-failure.json":
                "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH",
            "missing-member.json": "RMT_S1_MISSING_MEMBER",
            "mixed-commit.json": "RMT_S1_MIXED_COMMIT",
            "rollback-after-commit.json": "RMT_S1_ROLLBACK_AFTER_COMMIT",
        }
        for file_name, code in expected.items():
            fixture = json.loads(
                (HOSTILES / file_name).read_text(encoding="utf8")
            )
            residue = {**fixture["baseline"], **fixture["mutation"]}
            result = complete_settlement_operation(
                {"s1_residue": residue},
                {},
            )
            self.assertEqual(result["failure_code"], code)
            self.assertEqual(result["kind"], "failure")

    def test_rejects_incoherent_s1_residue_without_label_oracle(self) -> None:
        fixture = json.loads((
            HOSTILES / "before-state-write-failure.json"
        ).read_text(encoding="utf8"))
        residue = {**fixture["baseline"], **fixture["mutation"]}
        residue["transaction_aborted"] = False
        result = complete_settlement_operation(
            {"s1_residue": residue},
            {},
        )
        self.assertEqual(
            result["failure_code"],
            "RMT_OP_S1_RESIDUE_INCOHERENT",
        )

    def test_source_is_one_closed_synchronous_function(self) -> None:
        module = ast.parse(SOURCE.read_text(encoding="utf8"))
        self.assertEqual(len(module.body), 1)
        function = module.body[0]
        self.assertIs(type(function), ast.FunctionDef)
        self.assertEqual(function.name, "complete_settlement_operation")
        self.assertEqual(
            [argument.arg for argument in function.args.args],
            ["input_data", "ports"],
        )
        self.assertFalse(any(isinstance(node, (
            ast.Import,
            ast.ImportFrom,
            ast.AsyncFunctionDef,
            ast.Await,
            ast.Yield,
            ast.YieldFrom,
            ast.Global,
            ast.Nonlocal,
        )) for node in ast.walk(function)))


if __name__ == "__main__":
    unittest.main()
