import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertCheckedWorkflowRecoveryPolicy, type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';

export const WORKFLOW_CONTROLS_DEFINITION_SHA256 = '9c37ffedfea88175b9b35f1507a2169a2102e82c8c419b7056a72bddf2101ae2';
const outcomeContract = '0a7cb5a92bbec1bc5003dd5a6ba70ebc184a8316ad617f2a362b5d9de82ba607';
const digest = (value: unknown) => sha256(canonicalJson(value));
const fail = (reason: string): never => {throw new TypeError('WORKFLOW_REFERENCE:' + reason);};
const text = (v: unknown): v is string => typeof v === 'string' && v.length > 0 && v.length <= 2048;
const identity = (v: unknown): string => typeof v === 'string' && v.length <= 256 && /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(v)?.[0] === v ? v : fail('invalid identity');

// Read descriptors, never caller accessors. Only freshly owned metadata reaches freeze.
function fields(value: unknown): Map<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return fail('plain metadata required');
  const proto = Object.getPrototypeOf(value);
  if (proto !== null && proto !== Object.prototype) return fail('plain metadata required');
  const keys = Reflect.ownKeys(value);
  if (keys.length > 8) return fail('metadata capacity');
  const result = new Map<string, unknown>();
  for (const key of keys) {
    const d = Object.getOwnPropertyDescriptor(value, key);
    if (typeof key !== 'string' || !d?.enumerable || !Object.hasOwn(d, 'value')) return fail('inert metadata required');
    result.set(key, d.value);
  }
  return result;
}
function closed(row: Map<string, unknown>, names: readonly string[]) {
  if (row.size !== names.length || names.some(k => !row.has(k))) fail('closed metadata required');
  return row;
}
function list(value: unknown, max: number): unknown[] {
  if (!Array.isArray(value)) return fail('event array required');
  const length = Object.getOwnPropertyDescriptor(value, 'length')?.value;
  if (!Number.isInteger(length) || length < 0 || length > max || length > 128) return fail('event capacity');
  if (Reflect.ownKeys(value).length !== length + 1) return fail('dense event array required');
  return Array.from({length}, (_, i) => {
    const d = Object.getOwnPropertyDescriptor(value, String(i));
    if (!d?.enumerable || !Object.hasOwn(d, 'value')) return fail('inert event array required');
    return d.value;
  });
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const v of Object.values(value)) freeze(v);
    Object.freeze(value);
  }
  return value;
}
export interface WorkflowSettlementReference {
  readonly commit_status: 'committed' | 'not-committed' | 'indeterminate';
  readonly origin: 'returned' | 'invalid-return' | 'threw' | 'not-started';
  readonly status: 'committed' | 'failed' | 'rejected' | 'indeterminate' | null;
  readonly stage: string | null;
  readonly code: string | null;
  readonly continuation: string | null;
  readonly cleanup_failed: boolean | null;
  readonly result_validation: 'not-performed';
}
function unknown(origin: 'invalid-return' | 'threw'): WorkflowSettlementReference {
  return Object.freeze({commit_status: 'indeterminate', origin, status: null, stage: null, code: null,
    continuation: null, cleanup_failed: null, result_validation: 'not-performed'});
}

/** Independent table-based metadata oracle. The committed value is deliberately opaque. */
export function inspectWorkflowSettlementReference(value: unknown, continuation: string): WorkflowSettlementReference {
  if (!text(continuation)) return fail('invalid continuation');
  try {
    const row = fields(value), status = row.get('status');
    if (status === 'committed') {
      closed(row, ['status', 'value']);
      return Object.freeze({commit_status: 'committed', origin: 'returned', status, stage: null, code: null,
        continuation: null, cleanup_failed: null, result_validation: 'not-performed'});
    }
    closed(row, ['status', 'stage', 'code', 'continuation', 'cleanupFailed']);
    if (status !== 'failed' && status !== 'rejected' && status !== 'indeterminate') return unknown('invalid-return');
    const stage = row.get('stage'), code = row.get('code'), cleanup = row.get('cleanupFailed');
    if (!text(stage) || !text(code) || row.get('continuation') !== continuation || typeof cleanup !== 'boolean') return unknown('invalid-return');
    const simple: Record<string, readonly string[]> = {
      input: ['failed/OPERATION_INPUT'], begin: ['failed/BEGIN_FAILED'],
      commit: ['rejected/COMMIT_REJECTED', 'indeterminate/COMMIT_INDETERMINATE', 'indeterminate/INVALID_COMMIT_RECEIPT', 'indeterminate/COMMIT_UNCERTAIN']
    };
    const allowed = Object.hasOwn(simple, stage) ? !cleanup && simple[stage]!.includes(status + '/' + code) :
      ['read', 'guard', 'write-validation', 'event', 'result'].includes(stage) && (
        status === 'failed' && (code === 'OPERATION_FAILED' || stage === 'read' && ['READ_NOT_FOUND', 'READ_IDENTITY_MISMATCH'].includes(code)) ||
        stage === 'guard' && status === 'rejected' && /^RULE_REJECTED:[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/.test(code));
    if (!allowed) return unknown('invalid-return');
    return Object.freeze({commit_status: status === 'indeterminate' ? 'indeterminate' : 'not-committed', origin: 'returned', status,
      stage, code, continuation, cleanup_failed: cleanup, result_validation: 'not-performed'});
  } catch {return unknown('invalid-return');}
}

/** Pure expected metadata from checked source. No production evaluator, planner or template is used. */
export function createWorkflowOutcomeReference(policy: CheckedWorkflowRecoveryPolicy, definitionSource: string) {
  assertCheckedWorkflowRecoveryPolicy(policy);
  if (typeof definitionSource !== 'string' || sha256(definitionSource) !== WORKFLOW_CONTROLS_DEFINITION_SHA256) fail('definition drift');
  const workflow = policy.workflow;
  const steps = workflow.occurrence_source.steps.map(source => {
    const checked = workflow.steps.find(s => s.step_id === source.step_id)!;
    const binding = workflow.bindings.steps.find(s => s.step_id === source.step_id)!;
    return {step_id: source.step_id, operation_ref: source.operation_ref, action_sha256: binding.action_sha256,
      continuation: checked.failure_continuation};
  });
  function recovery(completed: string[], failed: string, commit: 'not-committed' | 'indeterminate', executionId: string, failureId: string) {
    const journal = {schema_version: 'domainspec.workflow-failure-journal/v1-candidate', workflow_execution_id: executionId,
      failure_occurrence_id: failureId, completed_step_ids: completed, failed_step_id: failed, failed_commit_status: commit};
    const common = {schema_version: 'domainspec.workflow-recovery-evaluation/v1-candidate' as const, workflow_sha256: workflow.workflow_sha256,
      policy_sha256: policy.policy_sha256, journal, journal_sha256: digest(journal), commit_evidence: 'caller-supplied' as const,
      intent_registration: 'not-performed' as const, compensation_execution: false as const, authority_effect: 'none' as const};
    if (commit === 'indeterminate') return {...common, status: 'reconciliation-required' as const, workflow_evaluation_result: null,
      recovery_intent: null, unknown_step_id: failed};
    const source = workflow.occurrence_source.compensations.filter(c => completed.includes(c.for_step));
    const needed = new Set(source.map(c => c.compensation_id));
    const rows = source.map(c => {
      const b = workflow.bindings.compensations.find(b => b.compensation_id === c.compensation_id)!;
      const checked = workflow.compensations.find(b => b.compensation_id === c.compensation_id)!;
      return {compensation_id: c.compensation_id, for_step: c.for_step, operation_ref: c.operation_ref, action_sha256: b.action_sha256,
        depends_on: c.depends_on.filter(id => needed.has(id)).sort(), inactive_dependencies: c.depends_on.filter(id => !needed.has(id)).sort(),
        arguments: b.arguments, events: b.events, failure_continuation: checked.failure_continuation};
    });
    // Kahn's algorithm on the needed graph, with completion priority only in the ready queue.
    const pending = new Map(rows.map(r => [r.compensation_id, r.depends_on.length]));
    const dependents = new Map(rows.map(r => [r.compensation_id, rows.filter(other => other.depends_on.includes(r.compensation_id))]));
    const ready = rows.filter(r => pending.get(r.compensation_id) === 0), ordered: typeof rows = [];
    while (ready.length) {
      ready.sort((a, b) => completed.indexOf(b.for_step) - completed.indexOf(a.for_step));
      const row = ready.shift()!; ordered.push(row);
      for (const next of dependents.get(row.compensation_id)!) {
        const count = pending.get(next.compensation_id)! - 1; pending.set(next.compensation_id, count);
        if (count === 0) ready.push(next);
      }
    }
    if (ordered.length !== rows.length) return fail('cyclic checked dependency graph');
    if (!ordered.length) return {...common, status: 'evaluated' as const, workflow_evaluation_result: 'not-required' as const, recovery_intent: null};
    const completed_step_journal_digest = digest({schema_version: 'domainspec.workflow-completed-prefix/v1-candidate', workflow_sha256: workflow.workflow_sha256,
      workflow_execution_id: executionId, steps: steps.slice(0, completed.length).map(({continuation: _continuation, ...s}) => s)});
    const plan_digest = digest({schema_version: 'domainspec.workflow-recovery-plan/v3-candidate', policy_sha256: policy.policy_sha256, plan: ordered});
    const body = {schema_version: 'domainspec.workflow-recovery-intent/v3-candidate' as const, workflow_selector: workflow.bindings.selector,
      workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256, workflow_execution_id: executionId,
      failure_occurrence_id: failureId, failed_step_id: failed, completed_step_journal_digest, plan_digest};
    const intent_id = digest(body);
    return {...common, status: 'evaluated' as const, workflow_evaluation_result: 'recovery-required' as const,
      recovery_intent: {...body, intent_id, semantic_status: 'required' as const, plan: ordered.map(row => ({...row,
        invocation_identity: digest({schema_version: 'domainspec.compensation-invocation/v2-candidate', intent_id, plan_digest,
          compensation_id: row.compensation_id, operation_ref: row.operation_ref, action_sha256: row.action_sha256})}))}};
  }
  function evaluate(request: unknown) {
    const r = closed(fields(request), ['workflow_execution_id', 'failure_occurrence_id', 'events', 'local_error']);
    const executionId = identity(r.get('workflow_execution_id'));
    const failureId = r.get('failure_occurrence_id') === null ? null : identity(r.get('failure_occurrence_id'));
    const localError = r.get('local_error');
    if (localError !== null && localError !== 'committed-result-invalid' && localError !== 'result-materialization-failed') fail('invalid local error');
    let stopped = false;
    const observations = list(r.get('events'), steps.length).map((event, i) => {
      if (stopped) return fail('event after terminal failure');
      const e = fields(event), kind = e.get('kind');
      closed(e, kind === 'returned' ? ['step_id', 'kind', 'outcome'] : ['step_id', 'kind']);
      const step = steps[i]!;
      if (e.get('step_id') !== step.step_id) return fail('exact source prefix required');
      let settlement: WorkflowSettlementReference;
      if (kind === 'returned') settlement = inspectWorkflowSettlementReference(e.get('outcome'), step.continuation);
      else if (kind === 'threw') settlement = unknown('threw');
      else if (kind === 'not-started') settlement = Object.freeze({commit_status: 'not-committed', origin: 'not-started', status: null,
        stage: 'argument-materialization', code: 'ARGUMENT_MATERIALIZATION_FAILED', continuation: null, cleanup_failed: null, result_validation: 'not-performed'});
      else return fail('invalid event kind');
      stopped = settlement.commit_status !== 'committed';
      const {continuation: _continuation, ...sourceStep} = step;
      const body = {schema_version: 'domainspec.workflow-step-observation/v1-candidate' as const, contract_sha256: outcomeContract,
        workflow_sha256: workflow.workflow_sha256, ...sourceStep, settlement, evidence: 'caller-supplied' as const, authority_effect: 'none' as const};
      return {...body, observation_sha256: digest(body)};
    });
    const completed = observations.filter(o => o.settlement.commit_status === 'committed').map(o => o.step_id);
    const common = {schema_version: 'domainspec.workflow-outcome-evaluation/v1-candidate' as const, workflow_sha256: workflow.workflow_sha256,
      policy_sha256: policy.policy_sha256, workflow_execution_id: executionId, failure_occurrence_id: failureId, completed_step_ids: completed,
      observations, evidence: 'caller-supplied' as const, result_validation: 'not-performed' as const, execution: 'not-performed' as const, authority_effect: 'none' as const};
    const last = observations.at(-1);
    if (last && last.settlement.commit_status !== 'committed') {
      if (failureId === null || localError !== null) return fail('terminal failure identity or local error mismatch');
      const plan = recovery(completed, last.step_id, last.settlement.commit_status, executionId, failureId);
      return freeze({...common, status: 'forward-stopped' as const, failure: last.settlement, local_error: null, recovery_status: plan.status, recovery: plan});
    }
    if (localError !== null) {
      if (failureId === null || !completed.length || localError === 'result-materialization-failed' && completed.length !== steps.length) return fail('local error position or identity mismatch');
      return freeze({...common, status: 'orchestration-error' as const, failure: null, local_error: localError, recovery_status: 'not-evaluable' as const, recovery: null});
    }
    if (failureId !== null) return fail('failure identity without failure');
    return freeze({...common, status: completed.length === steps.length ? 'forward-complete' as const : 'awaiting-next-step' as const,
      failure: null, local_error: null, recovery_status: 'not-evaluated' as const, recovery: null});
  }
  return Object.freeze({workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256, evaluate});
}
