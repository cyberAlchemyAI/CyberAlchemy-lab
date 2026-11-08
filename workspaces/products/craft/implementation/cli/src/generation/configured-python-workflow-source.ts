import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy, planSelectedWorkflowRecovery, WORKFLOW_FAILURE_JOURNAL_VERSION, type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';
import {WORKFLOW_OUTCOME_CONTRACT_SHA256} from '../typed-operation/workflow-outcomes.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';
import {pythonFrozenLiteral} from './configured-python-calculation-source.js';
import {createPythonReadTypes} from './configured-python-read-types.js';
import {PYTHON_WORKFLOW_SETTLEMENT} from './python-workflow-settlement-source.js';

export interface PythonWorkflowImport {readonly selector: string; readonly module: string; readonly symbol: string; readonly local: string; readonly action_sha256: string; readonly descriptor_sha256: string;}
const fail = (reason: string): never => {throw new TypeError('PYTHON_WORKFLOW_SOURCE:' + reason);};

function metadataTypes(w: CheckedWorkflowBindings) {
  const types = createPythonReadTypes(null, fail);
  const shape = (name: string, fields: Record<string, string>, optional: string[] = []) => types.record(name, Object.entries(fields).map(([name, t]) => ({name, input: t, native: t, optional: optional.includes(name)})));
  const none = '_Literal["none"]', evidence = '_Literal["caller-supplied"]', unperformed = '_Literal["not-performed"]';
  shape('_Settlement', {commit_status: '_Literal["committed", "not-committed", "indeterminate"]', origin: '_Literal["returned", "invalid-return", "threw", "not-started"]', status: '_Literal["committed", "failed", "rejected", "indeterminate"] | None', stage: 'str | None', code: 'str | None', continuation: 'str | None', cleanup_failed: 'bool | None', result_validation: unperformed});
  shape('_Observation', {schema_version: '_Literal["domainspec.workflow-step-observation/v1-candidate"]', contract_sha256: 'str', workflow_sha256: 'str', step_id: 'str', operation_ref: 'str', action_sha256: 'str', settlement: '_Settlement', evidence, authority_effect: none, observation_sha256: 'str'});
  shape('_FailureJournal', {schema_version: '_Literal["domainspec.workflow-failure-journal/v1-candidate"]', workflow_execution_id: 'str', failure_occurrence_id: 'str', completed_step_ids: 'tuple[str, ...]', failed_step_id: 'str', failed_commit_status: '_Literal["not-committed", "indeterminate"]'});
  shape('_RecoveryRow', {compensation_id: 'str', for_step: 'str', operation_ref: 'str', action_sha256: 'str', depends_on: 'tuple[str, ...]', inactive_dependencies: 'tuple[str, ...]', arguments: 'tuple[object, ...]', events: 'tuple[object, ...]', failure_continuation: 'str', invocation_identity: 'str'});
  shape('_RecoveryIntent', {schema_version: '_Literal["domainspec.workflow-recovery-intent/v3-candidate"]', workflow_selector: 'str', workflow_sha256: 'str', policy_sha256: 'str', workflow_execution_id: 'str', failure_occurrence_id: 'str', failed_step_id: 'str', completed_step_journal_digest: 'str', plan_digest: 'str', intent_id: 'str', semantic_status: '_Literal["required"]', plan: 'tuple[_RecoveryRow, ...]'});
  shape('_RecoveryEvaluation', {schema_version: '_Literal["domainspec.workflow-recovery-evaluation/v1-candidate"]', workflow_sha256: 'str', policy_sha256: 'str', journal: '_FailureJournal', journal_sha256: 'str', commit_evidence: evidence, intent_registration: unperformed, compensation_execution: '_Literal[False]', authority_effect: none, status: '_Literal["evaluated", "reconciliation-required"]', workflow_evaluation_result: '_Literal["not-required", "recovery-required"] | None', recovery_intent: '_RecoveryIntent | None', unknown_step_id: 'str'}, ['unknown_step_id']);
  shape('WorkflowEvaluation', {schema_version: '_Literal["domainspec.workflow-outcome-evaluation/v1-candidate"]', workflow_sha256: 'str', policy_sha256: 'str', workflow_execution_id: 'str', failure_occurrence_id: 'str | None', completed_step_ids: 'tuple[str, ...]', observations: 'tuple[_Observation, ...]', evidence, result_validation: unperformed, execution: unperformed, authority_effect: none, status: '_Literal["forward-stopped", "orchestration-error", "forward-complete", "awaiting-next-step"]', failure: '_Settlement | None', local_error: '_Literal["committed-result-invalid", "result-materialization-failed"] | None', recovery_status: '_Literal["evaluated", "reconciliation-required", "not-evaluable", "not-evaluated"]', recovery: '_RecoveryEvaluation | None'});
  const bindings = w.compensations.map((c, i) => shape('_Binding' + i, {intent_id: 'str', plan_digest: 'str', invocation_identity: 'str', compensation_id: `_Literal[${q(c.compensation_id)}]`, operation_ref: `_Literal[${q(c.operation_ref)}]`, action_sha256: `_Literal[${q(c.action_sha256)}]`, arguments: '_material._Arguments' + (w.steps.length + i)}).native);
  shape('RecoveryBindings', {schema_version: '_Literal["domainspec.workflow-recovery-bindings/v1-candidate"]', intent_id: 'str', plan_digest: 'str', bindings: 'tuple[' + (bindings.join(' | ') || '_Never') + ', ...]', compensation_execution: '_Literal[False]', authority_effect: none});
  return types.source();
}

export function renderPythonWorkflow(w: CheckedWorkflowBindings, policy: CheckedWorkflowRecoveryPolicy, materialPath: string, imports: readonly PythonWorkflowImport[]): string {
  assertCheckedWorkflowBindings(w); assertCheckedWorkflowRecoveryPolicy(policy); if (policy.workflow !== w) fail('policy identity');
  const templates = w.steps.map((failed, i) => {
    const planned = planSelectedWorkflowRecovery(policy, {schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION, workflow_execution_id: 'compile-execution', failure_occurrence_id: 'compile-failure', completed_step_ids: w.steps.slice(0, i).map(s => s.step_id), failed_step_id: failed.step_id, failed_commit_status: 'not-committed'});
    return {steps: w.steps.slice(0, i).map(s => ({step_id: s.step_id, operation_ref: s.operation_ref, action_sha256: s.action_sha256})), plan: planned.recovery_intent?.plan.map(({invocation_identity: _id, ...row}) => row) ?? [], plan_digest: planned.recovery_intent?.plan_digest ?? null};
  });
  const wf = {hash: w.workflow_sha256, selector: w.bindings.selector, steps: w.steps.map(s => ({step_id: s.step_id, operation_ref: s.operation_ref, action_sha256: s.action_sha256}))};
  const split = materialPath.lastIndexOf('.'), materialImport = 'from ' + materialPath.slice(0, split) + ' import ' + materialPath.slice(split + 1) + ' as _material\n';
  const header = `from __future__ import annotations
from asyncio import CancelledError as _CancelledError
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, Never as _Never, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast, get_args as _get_args
from hashlib import sha256 as _sha256
from json import dumps as _json_dumps
from re import fullmatch as _fullmatch
` + materialImport + `from ${materialPath} import WorkflowInput, WorkflowValue\n` + imports.map((r, i) => `from ${r.module} import ${r.symbol} as ${r.local}, _BoundOperation as _Operation${i}, OperationOutcome as _Outcome${i}, OperationDependencies as _Dependencies${i}\n`).join('');
  const types = metadataTypes(w) + `
WorkflowIdentity = _TypedDict("WorkflowIdentity", {"workflow_execution_id": str, "failure_occurrence_id": str})
WorkflowDependencies = _TypedDict("WorkflowDependencies", {${imports.map((r, i) => q(r.selector) + ': _Dependencies' + i).join(', ')}})

@_dataclass(frozen=True, slots=True)
class WorkflowSuccess:
    status: _Literal["succeeded"]
    value: WorkflowValue
    evaluation: WorkflowEvaluation
    recovery_bindings: None = None

@_dataclass(frozen=True, slots=True)
class WorkflowStopped:
    status: _Literal["forward-stopped", "orchestration-error"]
    evaluation: WorkflowEvaluation
    bindings_status: _Literal["ready", "not-required", "not-evaluable", "failed"]
    recovery_bindings: RecoveryBindings | None

WorkflowOutcome = WorkflowSuccess | WorkflowStopped
_WF = ${pythonFrozenLiteral(wf)}
_POLICY = ${q(policy.policy_sha256)}
_OUTCOME_CONTRACT = ${q(WORKFLOW_OUTCOME_CONTRACT_SHA256)}
_PREFIXES = ${pythonFrozenLiteral(templates)}
`;
  const prepare = `
def _prepare_bindings(input, results, intent):
    bindings = []
    for row in intent["plan"]:
` + w.compensations.map(c => `        if row["compensation_id"] == ${q(c.compensation_id)}:\n            if row["operation_ref"] != ${q(c.operation_ref)} or row["action_sha256"] != ${q(c.action_sha256)}:\n                _fail("compensation identity")\n            bindings.append(dict(intent_id=intent["intent_id"], plan_digest=intent["plan_digest"], invocation_identity=row["invocation_identity"], compensation_id=${q(c.compensation_id)}, operation_ref=${q(c.operation_ref)}, action_sha256=${q(c.action_sha256)}, arguments=_material.compensations[${q(c.compensation_id)}].arguments(input, results)))\n            continue\n`).join('') + `        _fail("unknown compensation")
    return _freeze(dict(schema_version="domainspec.workflow-recovery-bindings/v1-candidate", intent_id=intent["intent_id"], plan_digest=intent["plan_digest"], bindings=bindings, compensation_execution=False, authority_effect="none"))

def _stopped(input, results, observations, ids, local_error=None):
    evaluation = _evaluate(observations, ids, local_error)
    recovery = evaluation["recovery"]
    intent = recovery["recovery_intent"] if recovery else None
    if intent is None:
        return WorkflowStopped("orchestration-error" if local_error else "forward-stopped", evaluation, "not-required" if recovery and recovery["workflow_evaluation_result"] == "not-required" else "not-evaluable", None)
    try:
        return WorkflowStopped("forward-stopped", evaluation, "ready", _prepare_bindings(input, results, intent))
    except (Exception, _CancelledError):
        return WorkflowStopped("forward-stopped", evaluation, "failed", None)
`;
  const execute = `
async def execute(parameters: WorkflowInput, execution_identity: WorkflowIdentity, dependencies: WorkflowDependencies) -> WorkflowOutcome:
    e = _own(execution_identity, ("workflow_execution_id", "failure_occurrence_id"))
    ids = _MappingProxyType({"workflow_execution_id": _identity(e["workflow_execution_id"]), "failure_occurrence_id": _identity(e["failure_occurrence_id"])})
    input = _material.capture(parameters)
    d = _own(dependencies, (${imports.map(r => q(r.selector) + ',').join(' ')}))
` + imports.map((r, i) => `    call${i} = ${r.local}\n    _imported(call${i}, _Operation${i}, ${q(r.selector)}, ${q(r.action_sha256)}, ${q(r.descriptor_sha256)})\n    dep${i} = d[${q(r.selector)}]\n    outcomes${i} = _get_args(_Outcome${i})\n`).join('') + `    results = []
    observations = []
` + w.steps.map((s, n) => {
    const i = imports.findIndex(r => r.selector === s.operation_ref && r.action_sha256 === s.action_sha256); if (i < 0) fail('missing forward import');
    return `    try:\n        args${n} = _material.steps[${q(s.step_id)}].operation_input(input, results)\n    except (Exception, _CancelledError):\n        observations.append(_observe(${n}, _not_started()))\n        return _stopped(input, results, observations, ids)\n    try:\n        raw${n} = await call${i}(args${n}, dep${i})\n    except (Exception, _CancelledError):\n        observations.append(_observe(${n}, _unknown("threw")))\n        return _stopped(input, results, observations, ids)\n    settlement${n} = _settlement(raw${n}, ${q(s.failure_continuation)}, outcomes${i})\n    observations.append(_observe(${n}, settlement${n}))\n    if settlement${n}["commit_status"] != "committed":\n        return _stopped(input, results, observations, ids)\n    try:\n        results.append(_material.capture_result(input, ${q(s.step_id)}, _operation_data(raw${n}, outcomes${i})["value"]))\n    except (Exception, _CancelledError):\n        return _stopped(input, results, observations, ids, "committed-result-invalid")\n`;
  }).join('') + `    try:
        value = _material.result(input, results)
    except (Exception, _CancelledError):
        return _stopped(input, results, observations, ids, "result-materialization-failed")
    return WorkflowSuccess("succeeded", value, _evaluate(observations, ids, None))
`;
  return header + '\n' + types + PYTHON_WORKFLOW_SETTLEMENT + prepare + execute;
}

export function renderPythonWorkflowBinding(provider: string, callable: string, descriptor: unknown): string {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${provider} import execute as _execute, WorkflowInput, WorkflowValue, WorkflowIdentity, WorkflowDependencies, WorkflowOutcome, WorkflowEvaluation, RecoveryBindings

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundWorkflow:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    async def __call__(self, parameters: WorkflowInput, execution_identity: WorkflowIdentity, dependencies: WorkflowDependencies) -> WorkflowOutcome:
        return await _execute(parameters, execution_identity, dependencies)

${callable} = _BoundWorkflow()
__all__ = [${q(callable)}, "WorkflowInput", "WorkflowValue", "WorkflowIdentity", "WorkflowDependencies", "WorkflowOutcome", "WorkflowEvaluation", "RecoveryBindings"]
`;
}
