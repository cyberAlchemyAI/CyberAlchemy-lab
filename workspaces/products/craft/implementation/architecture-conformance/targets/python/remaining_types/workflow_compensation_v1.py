"""First-class Python Workflow recovery profile for canonical D36, D37, and D40."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Callable, Literal

WorkflowRecoveryResult = Literal["not-required", "recovery-required"]
RecoveryFailureContinuation = Literal["retry", "escalate", "terminal-failure"]
_IDENTITY = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


class WorkflowRecoveryError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code


@dataclass(frozen=True)
class RecoveryOperationMapping:
    step_id: str
    operation_id: str | None
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecoveryPlanEntry:
    plan_occurrence_id: str
    step_id: str
    operation_id: str
    depends_on: tuple[str, ...]
    invocation_identity: str


@dataclass(frozen=True)
class RecoveryIntent:
    schema_version: Literal["domainspec.workflow-recovery-intent/v2"]
    intent_id: str
    workflow_id: str
    workflow_execution_id: str
    failure_occurrence_id: str
    failed_step_id: str
    completed_step_journal_digest: str
    plan_digest: str
    semantic_status: Literal["required"]
    plan: tuple[RecoveryPlanEntry, ...]


@dataclass(frozen=True)
class WorkflowRecoveryDecision:
    schema_version: Literal["domainspec.workflow-recovery-decision/v1"]
    workflow_evaluation_result: WorkflowRecoveryResult
    recovery_intent: RecoveryIntent | None


@dataclass(frozen=True)
class RecoveryOperationBinding:
    workflow_id: str
    operation_id: str
    failure_continuation: RecoveryFailureContinuation
    invoke: Callable[[str], tuple[bool, str | None]]


@dataclass(frozen=True)
class RecoveryInvocationReport:
    schema_version: Literal["domainspec.workflow-recovery-in-process-report/v1"]
    outcome: Literal["succeeded", "failed"]
    executed_plan_occurrence_ids: tuple[str, ...]
    failed_plan_occurrence_id: str | None
    failure_continuation: RecoveryFailureContinuation | None
    reason: str | None
    recovery_intent_semantic_status: Literal["required"]
    durable_terminal_disposition: None


def _reject(code: str, message: str) -> None:
    raise WorkflowRecoveryError(code, message)


def _require_identity(value: str, label: str) -> None:
    if _IDENTITY.fullmatch(value) is None:
        _reject("RECOVERY_IDENTITY_INVALID", f"{label}:{value}")


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _journal_material(completed_step_ids: tuple[str, ...]) -> str:
    return "\n".join(("domainspec.workflow-completed-step-journal/v1", *completed_step_ids))


def _plan_material(entries: list[tuple[str, str, str, tuple[str, ...]]]) -> str:
    lines = ["domainspec.workflow-recovery-plan/v1"]
    lines.extend("|".join((occurrence, step, operation, ",".join(dependencies))) for occurrence, step, operation, dependencies in entries)
    return "\n".join(lines)


def _invocation_identity(intent_id: str, plan_digest: str, operation_id: str, plan_occurrence_id: str) -> str:
    return _digest("\n".join((
        "domainspec.compensation-invocation-identity/v1",
        intent_id,
        plan_digest,
        operation_id,
        plan_occurrence_id,
    )))


def plan_workflow_recovery(
    *,
    workflow_id: str,
    workflow_execution_id: str,
    failure_occurrence_id: str,
    failed_step_id: str,
    completed_step_ids: tuple[str, ...],
    orchestrated_operation_ids: tuple[str, ...],
    mappings: tuple[RecoveryOperationMapping, ...],
) -> WorkflowRecoveryDecision:
    for label, value in (
        ("workflow_id", workflow_id),
        ("workflow_execution_id", workflow_execution_id),
        ("failure_occurrence_id", failure_occurrence_id),
        ("failed_step_id", failed_step_id),
    ):
        _require_identity(value, label)
    if len(set(completed_step_ids)) != len(completed_step_ids):
        _reject("RECOVERY_COMPLETED_STEP_DUPLICATE", "completed step IDs must be unique")

    orchestrated: set[str] = set()
    for operation_id in orchestrated_operation_ids:
        _require_identity(operation_id, "orchestrated_operation_id")
        if operation_id in orchestrated:
            _reject("RECOVERY_ORCHESTRATION_DUPLICATE", operation_id)
        orchestrated.add(operation_id)

    by_step: dict[str, RecoveryOperationMapping] = {}
    for mapping in mappings:
        _require_identity(mapping.step_id, "mapping.step_id")
        if mapping.step_id in by_step:
            _reject("RECOVERY_MAPPING_DUPLICATE", mapping.step_id)
        if mapping.operation_id is not None:
            _require_identity(mapping.operation_id, "mapping.operation_id")
        if len(set(mapping.depends_on)) != len(mapping.depends_on):
            _reject("RECOVERY_DEPENDENCY_DUPLICATE", mapping.step_id)
        for dependency in mapping.depends_on:
            _require_identity(dependency, "mapping.depends_on")
        by_step[mapping.step_id] = mapping

    selected: list[tuple[str, str, str, tuple[str, ...]]] = []
    for completion_index, step_id in enumerate(completed_step_ids, start=1):
        _require_identity(step_id, "completed_step_id")
        mapping = by_step.get(step_id)
        if mapping is None or mapping.operation_id is None:
            continue
        if mapping.operation_id not in orchestrated:
            _reject("RECOVERY_OPERATION_NOT_ORCHESTRATED", f"{workflow_id}:{mapping.operation_id}")
        selected.append((f"{step_id}-{mapping.operation_id}-{completion_index}", step_id, mapping.operation_id, mapping.depends_on))
    selected.reverse()

    if not selected:
        return WorkflowRecoveryDecision("domainspec.workflow-recovery-decision/v1", "not-required", None)

    occurrences_by_operation: dict[str, list[str]] = {}
    for occurrence, _, operation, _ in selected:
        occurrences_by_operation.setdefault(operation, []).append(occurrence)

    pending: list[tuple[str, str, str, tuple[str, ...]]] = []
    for occurrence, step, operation, dependency_operations in selected:
        dependencies: list[str] = []
        for dependency in dependency_operations:
            occurrences = occurrences_by_operation.get(dependency, [])
            if dependency == operation or len(occurrences) != 1:
                code = "RECOVERY_DEPENDENCY_AMBIGUOUS" if len(occurrences) > 1 else "RECOVERY_DEPENDENCY_INVALID"
                _reject(code, f"{operation}:depends-on:{dependency}")
            dependencies.append(occurrences[0])
        pending.append((occurrence, step, operation, tuple(dependencies)))

    ordered: list[tuple[str, str, str, tuple[str, ...]]] = []
    emitted: set[str] = set()
    while pending:
        index = next((index for index, entry in enumerate(pending) if all(dependency in emitted for dependency in entry[3])), -1)
        if index < 0:
            _reject("RECOVERY_DEPENDENCY_CYCLE", "recovery Operation dependency graph is cyclic")
        entry = pending.pop(index)
        ordered.append(entry)
        emitted.add(entry[0])

    completed_step_journal_digest = _digest(_journal_material(completed_step_ids))
    plan_digest = _digest(_plan_material(ordered))
    intent_id = _digest("\n".join((
        "domainspec.workflow-recovery-intent/v2",
        workflow_execution_id,
        failure_occurrence_id,
        failed_step_id,
        completed_step_journal_digest,
        plan_digest,
    )))
    plan = tuple(RecoveryPlanEntry(
        occurrence,
        step,
        operation,
        dependencies,
        _invocation_identity(intent_id, plan_digest, operation, occurrence),
    ) for occurrence, step, operation, dependencies in ordered)
    intent = RecoveryIntent(
        "domainspec.workflow-recovery-intent/v2",
        intent_id,
        workflow_id,
        workflow_execution_id,
        failure_occurrence_id,
        failed_step_id,
        completed_step_journal_digest,
        plan_digest,
        "required",
        plan,
    )
    return WorkflowRecoveryDecision("domainspec.workflow-recovery-decision/v1", "recovery-required", intent)


def _verify_intent(intent: RecoveryIntent) -> None:
    entries: list[tuple[str, str, str, tuple[str, ...]]] = []
    emitted: set[str] = set()
    for entry in intent.plan:
        if entry.plan_occurrence_id in emitted:
            _reject("RECOVERY_PLAN_OCCURRENCE_DUPLICATE", entry.plan_occurrence_id)
        if any(dependency not in emitted for dependency in entry.depends_on):
            _reject("RECOVERY_PLAN_ORDER_INVALID", entry.plan_occurrence_id)
        emitted.add(entry.plan_occurrence_id)
        entries.append((entry.plan_occurrence_id, entry.step_id, entry.operation_id, entry.depends_on))
    if _digest(_plan_material(entries)) != intent.plan_digest:
        _reject("RECOVERY_PLAN_DIGEST_MISMATCH", intent.plan_digest)
    observed_intent_id = _digest("\n".join((
        "domainspec.workflow-recovery-intent/v2",
        intent.workflow_execution_id,
        intent.failure_occurrence_id,
        intent.failed_step_id,
        intent.completed_step_journal_digest,
        intent.plan_digest,
    )))
    if observed_intent_id != intent.intent_id:
        _reject("RECOVERY_INTENT_ID_MISMATCH", observed_intent_id)
    for entry in intent.plan:
        expected = _invocation_identity(intent.intent_id, intent.plan_digest, entry.operation_id, entry.plan_occurrence_id)
        if entry.invocation_identity != expected:
            _reject("RECOVERY_INVOCATION_IDENTITY_MISMATCH", entry.plan_occurrence_id)


def execute_workflow_recovery(intent: RecoveryIntent, bindings: tuple[RecoveryOperationBinding, ...]) -> RecoveryInvocationReport:
    _verify_intent(intent)
    required = {entry.operation_id for entry in intent.plan}
    registry: dict[str, RecoveryOperationBinding] = {}
    for binding in bindings:
        if binding.workflow_id != intent.workflow_id:
            _reject("RECOVERY_BINDING_WORKFLOW_MISMATCH", f"{binding.workflow_id}:{binding.operation_id}")
        if binding.operation_id not in required:
            _reject("RECOVERY_BINDING_UNDECLARED", binding.operation_id)
        if binding.operation_id in registry:
            _reject("RECOVERY_BINDING_DUPLICATE", binding.operation_id)
        registry[binding.operation_id] = binding
    for operation_id in required:
        if operation_id not in registry:
            _reject("RECOVERY_BINDING_MISSING", operation_id)

    executed: list[str] = []
    for entry in intent.plan:
        binding = registry[entry.operation_id]
        try:
            ok, reason = binding.invoke(entry.invocation_identity)
        except Exception as error:  # the report records an in-process failure, never a D44 disposition
            ok, reason = False, str(error)
        if not ok:
            return RecoveryInvocationReport(
                "domainspec.workflow-recovery-in-process-report/v1",
                "failed",
                tuple(executed),
                entry.plan_occurrence_id,
                binding.failure_continuation,
                reason or "recovery-operation-failed",
                "required",
                None,
            )
        executed.append(entry.plan_occurrence_id)
    return RecoveryInvocationReport(
        "domainspec.workflow-recovery-in-process-report/v1",
        "succeeded",
        tuple(executed),
        None,
        None,
        None,
        "required",
        None,
    )
