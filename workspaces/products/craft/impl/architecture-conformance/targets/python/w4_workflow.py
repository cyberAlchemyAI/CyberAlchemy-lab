"""Python Workflow candidate: explicit ordered Operation/Workflow steps."""
from dataclasses import dataclass
from typing import Awaitable, Callable, Literal

StepId = Literal["validate", "decide", "persist", "publish"]

@dataclass(frozen=True)
class WorkflowStep:
    step_id: StepId
    run: Callable[[], Awaitable[None]]
    compensation_id: str | None = None
    compensate: Callable[[], Awaitable[None]] | None = None

@dataclass(frozen=True)
class WorkflowResult:
    outcome: Literal["settlement-completed", "settlement-failed"]
    trace: tuple[StepId, ...]
    failed_step_id: StepId | None
    compensations: tuple[str, ...]

async def run_settlement_workflow(steps: tuple[WorkflowStep, ...]) -> WorkflowResult:
    order: tuple[StepId, ...] = ("validate", "decide", "persist", "publish")
    ids = tuple(step.step_id for step in steps)
    missing = next((step_id for step_id in order if step_id not in ids), None)
    if missing is not None:
        raise KeyError(f"ARCH_WORKFLOW_STEP_MISSING:{missing}")
    if len(steps) != len(order) or len(set(ids)) != len(ids) or any(step_id not in order for step_id in ids):
        raise ValueError("ARCH_WORKFLOW_STEP_SET_INVALID")
    for step in steps:
        compensation_valid = (
            step.compensation_id == "rollback-settlement" and step.compensate is not None
            if step.step_id == "persist"
            else step.compensation_id is None and step.compensate is None
        )
        if not compensation_valid:
            raise ValueError(f"ARCH_WORKFLOW_COMPENSATION_CONTRACT_INVALID:{step.step_id}")
    by_id = {step.step_id: step for step in steps}
    trace: list[StepId] = []
    completed: list[WorkflowStep] = []
    try:
        for step_id in order:
            step = by_id[step_id]
            await step.run()
            trace.append(step_id)
            completed.append(step)
        return WorkflowResult("settlement-completed", tuple(trace), None, ())
    except Exception:
        compensations: list[str] = []
        for step in reversed(completed):
            if step.compensate is not None:
                if step.compensation_id is None:
                    raise RuntimeError(f"ARCH_WORKFLOW_COMPENSATION_ID_MISSING:{step.step_id}")
                await step.compensate()
                compensations.append(step.compensation_id)
        failed_step_id = next((step_id for step_id in order if step_id not in trace), None)
        return WorkflowResult("settlement-failed", tuple(trace), failed_step_id, tuple(compensations))
