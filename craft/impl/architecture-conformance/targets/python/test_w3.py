import asyncio
import dataclasses
import unittest

from w3 import (
    SettlementRecord,
    complete_settlement,
    evaluate_w3_contract,
    make_settlement_created,
    map_settlement_response,
)


class W3RealizationTest(unittest.TestCase):
    def test_native_mapping_event_and_operation(self) -> None:
        record = SettlementRecord(id="req-1", player_id="player-1", amount=42)
        self.assertEqual(map_settlement_response(record).settlement_id, "req-1")
        event = make_settlement_created(record)
        self.assertEqual(event.occurrence_id, "settlement:req-1")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            event.amount = 10  # type: ignore[misc]

        trace: list[str] = []

        async def commit(_record: SettlementRecord, _event: object) -> None:
            trace.extend(("write", "outbox"))

        response, result_event = asyncio.run(complete_settlement(
            request_id="req-1", player_id="player-1", amount=42,
            existing_settlement_id=None, commit_atomically=commit,
        ))
        self.assertEqual((response.settlement_id, result_event.type), ("req-1", "SettlementCreated"))
        self.assertEqual(trace, ["write", "outbox"])

    def test_operation_uses_one_atomic_commit_boundary(self) -> None:
        attempts: list[str] = []

        async def fail_commit(_record: SettlementRecord, _event: object) -> None:
            attempts.append("atomic-commit")
            raise RuntimeError("COMMIT_FAILED")

        with self.assertRaisesRegex(RuntimeError, "COMMIT_FAILED"):
            asyncio.run(complete_settlement(
                request_id="req-2", player_id="player-1", amount=42,
                existing_settlement_id=None, commit_atomically=fail_commit,
            ))
        self.assertEqual(attempts, ["atomic-commit"])

    def test_descriptor_hostiles(self) -> None:
        mapping = {
            "kind": "Mapping", "source_contract_id": "Record/v1", "target_contract_id": "Response/v1",
            "correspondence": [{"source": "id", "target": "settlement_id", "mode": "direct"}],
            "effect_policy": "none",
        }
        hostile = {
            "kind": "Mapping", "source_contract_id": "Response/v1", "target_contract_id": "Record/v1",
            "observed_correspondence": [], "effects": ["log"],
        }
        self.assertEqual(evaluate_w3_contract(mapping, hostile), (
            "reject", ("ARCH_MAPPING_ENDPOINT_DRIFT", "ARCH_MAPPING_CORRESPONDENCE_DRIFT", "ARCH_MAPPING_EFFECT_UNDECLARED")
        ))

        operation = {"kind": "Operation", "ordered_checkpoints": ["rule", "write", "event"]}
        operation_hostile = {
            "kind": "Operation", "trace": ["write", "rule", "event"],
            "writes": [{"id": "settlement", "state": "restored"}],
            "guard_results": [{"invoked": True, "decision_used": False}], "continuation_closed": False,
        }
        self.assertEqual(evaluate_w3_contract(operation, operation_hostile)[1], (
            "ARCH_OPERATION_ORDER_DRIFT", "ARCH_OPERATION_WRITE_RESTORE",
            "ARCH_OPERATION_GUARD_INVALID", "ARCH_OPERATION_CONTINUATION_OPEN",
        ))

    def test_missing_observer_never_passes(self) -> None:
        self.assertEqual(evaluate_w3_contract({"kind": "Event"}, None)[0], "unsupported")
        self.assertEqual(evaluate_w3_contract({"kind": "Event"}, {"kind": "Mapping"})[0], "indeterminate")


if __name__ == "__main__":
    unittest.main()
