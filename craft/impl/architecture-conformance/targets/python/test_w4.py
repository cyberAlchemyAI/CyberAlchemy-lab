import asyncio
import unittest

from w4_state_machine import (
    SettlementState,
    SettlementTrigger,
    transition_settlement_lifecycle,
)
from w4_workflow import WorkflowStep, run_settlement_workflow


class W4Tests(unittest.TestCase):
    def test_state_machine_returns_effect_intents_without_executing_them(self) -> None:
        result = transition_settlement_lifecycle(SettlementState.PENDING, SettlementTrigger.CONFIRM)
        self.assertEqual(result.next_state, SettlementState.SETTLED)
        self.assertEqual(result.effect_intents, ("persist-settlement", "append-settlement-created"))
        rejected = transition_settlement_lifecycle(SettlementState.PENDING, SettlementTrigger.REJECT)
        self.assertEqual((rejected.next_state, rejected.effect_intents), (SettlementState.FAILED, ("record-rejection",)))
        self.assertFalse(transition_settlement_lifecycle(SettlementState.SETTLED, SettlementTrigger.CONFIRM).accepted)

    def test_workflow_executes_exact_order(self) -> None:
        calls: list[str] = []

        def step(step_id: str) -> WorkflowStep:
            async def run() -> None:
                calls.append(step_id)
            async def compensate() -> None:
                calls.append("undo-persist")
            return WorkflowStep(step_id, run, "rollback-settlement", compensate) if step_id == "persist" else WorkflowStep(step_id, run)  # type: ignore[arg-type]

        result = asyncio.run(run_settlement_workflow(tuple(step(item) for item in ("validate", "decide", "persist", "publish"))))
        self.assertEqual(result.outcome, "settlement-completed")
        self.assertEqual(calls, ["validate", "decide", "persist", "publish"])

    def test_workflow_compensates_completed_steps_after_failure(self) -> None:
        calls: list[str] = []

        async def okay() -> None:
            calls.append("validate")

        async def undo() -> None:
            calls.append("undo-persist")

        async def decide() -> None:
            calls.append("decide")

        async def persist() -> None:
            calls.append("persist")

        async def fail_publish() -> None:
            raise RuntimeError("publication failed")

        result = asyncio.run(run_settlement_workflow((
            WorkflowStep("validate", okay), WorkflowStep("decide", decide),
            WorkflowStep("persist", persist, "rollback-settlement", undo), WorkflowStep("publish", fail_publish),
        )))
        self.assertEqual(result.outcome, "settlement-failed")
        self.assertEqual(result.failed_step_id, "publish")
        self.assertEqual(result.compensations, ("rollback-settlement",))
        self.assertEqual(calls, ["validate", "decide", "persist", "undo-persist"])

    def test_workflow_rejects_duplicate_steps_before_execution(self) -> None:
        calls: list[str] = []

        async def run() -> None:
            calls.append("ran")

        async def undo() -> None:
            calls.append("undo")

        with self.assertRaisesRegex(ValueError, "ARCH_WORKFLOW_STEP_SET_INVALID"):
            asyncio.run(run_settlement_workflow((
                WorkflowStep("validate", run), WorkflowStep("decide", run),
                WorkflowStep("persist", run, "rollback-settlement", undo),
                WorkflowStep("persist", run, "rollback-settlement", undo),
                WorkflowStep("publish", run),
            )))
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
