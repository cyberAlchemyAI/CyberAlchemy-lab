import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertWorkflowData, freezeWorkflow, workflowList, workflowObject} from '../typed-backend/workflow-occurrences.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings} from './workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy, planSelectedWorkflowRecovery, WORKFLOW_FAILURE_JOURNAL_VERSION, type CheckedWorkflowRecoveryPolicy} from './workflow-recovery.js';
import type {ComposedPrecommitStage} from './composed-settlement.js';

export const WORKFLOW_OUTCOME_CONTRACT_SHA256 = '0a7cb5a92bbec1bc5003dd5a6ba70ebc184a8316ad617f2a362b5d9de82ba607';
export const WORKFLOW_OUTCOME_JOURNAL_VERSION = 'domainspec.workflow-outcome-journal/v1-candidate';
type CommitStatus = 'committed' | 'not-committed' | 'indeterminate';
export interface OperationSettlement {
  readonly commit_status: CommitStatus;
  readonly origin: 'returned' | 'invalid-return' | 'threw' | 'not-started';
  readonly status: 'committed' | 'failed' | 'rejected' | 'indeterminate' | null;
  readonly stage: string | null;
  readonly code: string | null;
  readonly continuation: string | null;
  readonly cleanup_failed: boolean | null;
  readonly result_validation: 'not-performed';
}
const fail = (m: string): never => {throw Object.assign(new TypeError('WORKFLOW_OUTCOME:' + m), {code: 'WORKFLOW_OUTCOME'});};
function own(value: unknown, names: readonly string[]): Record<string, PropertyDescriptor> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return fail('plain object required');
  const proto = Object.getPrototypeOf(value);
  if (proto !== Object.prototype && proto !== null) return fail('plain object required');
  const keys = Reflect.ownKeys(value);
  if (keys.length !== names.length || keys.some(k => typeof k !== 'string' || !names.includes(k))) return fail('closed fields required');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Object.values(d).some(p => !Object.hasOwn(p, 'value') || !p.enumerable)) return fail('inert fields required');
  return d;
}
const text = (v: unknown): v is string => typeof v === 'string' && v.length > 0 && v.length <= 2048;
const identity = (v: unknown): string => typeof v === 'string' && v.length <= 256 && /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(v)?.[0] === v ? v : fail('invalid identity');
const unknown = (origin: 'invalid-return' | 'threw'): OperationSettlement => Object.freeze({commit_status: 'indeterminate', origin,
  status: null, stage: null, code: null, continuation: null, cleanup_failed: null, result_validation: 'not-performed'});

/** Inspect metadata only: never traverse or freeze a committed value. This is
 * caller evidence, not authentication of a provider or validation of its result.
 */
export function inspectOperationSettlement(value: unknown, expectedContinuation: string): OperationSettlement {
  return inspectSettlement(value,expectedContinuation,[]);
}
function inspectSettlement(value: unknown, expectedContinuation: string,precommit:readonly ComposedPrecommitStage[]): OperationSettlement {
  if (!text(expectedContinuation)) return fail('invalid expected continuation');
  try {
    const statusDescriptor = value && typeof value === 'object' ? Object.getOwnPropertyDescriptor(value, 'status') : undefined;
    if (!statusDescriptor || !Object.hasOwn(statusDescriptor, 'value') || !statusDescriptor.enumerable) return unknown('invalid-return');
    if (statusDescriptor.value === 'committed') {
      own(value, ['status', 'value']);
      return Object.freeze({commit_status: 'committed', origin: 'returned', status: 'committed', stage: null, code: null,
        continuation: null, cleanup_failed: null, result_validation: 'not-performed'});
    }
    const d = own(value, ['status', 'stage', 'code', 'continuation', 'cleanupFailed']);
    const status = d.status!.value, stage = d.stage!.value, code = d.code!.value, cleanup = d.cleanupFailed!.value;
    if (!text(stage) || !text(code) || d.continuation!.value !== expectedContinuation || typeof cleanup !== 'boolean') return unknown('invalid-return');
    let valid = false;
    if (stage === 'commit') {
      valid = !cleanup && (status === 'rejected' && code === 'COMMIT_REJECTED' ||
        status === 'indeterminate' && ['COMMIT_INDETERMINATE', 'INVALID_COMMIT_RECEIPT', 'COMMIT_UNCERTAIN'].includes(code));
    } else if (stage === 'input') valid = status === 'failed' && code === 'OPERATION_INPUT' && !cleanup;
    else if (stage === 'begin') valid = status === 'failed' && code === 'BEGIN_FAILED' && !cleanup;
    else if (['read', 'guard', 'write-validation', 'event', 'result'].includes(stage)) {
      valid = status === 'failed' && code === 'OPERATION_FAILED' ||
        stage === 'read' && status === 'failed' && ['READ_NOT_FOUND', 'READ_IDENTITY_MISMATCH'].includes(code) ||
        stage === 'guard' && status === 'rejected' && /^RULE_REJECTED:[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/.test(code);
    }
    if (!valid) valid=status==='failed'&&precommit.some(row=>row.stage===stage&&row.codes.includes(code));
    if (!valid) return unknown('invalid-return');
    return Object.freeze({commit_status: status === 'indeterminate' ? 'indeterminate' : 'not-committed', origin: 'returned',
      status, stage, code, continuation: expectedContinuation, cleanup_failed: cleanup, result_validation: 'not-performed'});
  } catch {return unknown('invalid-return');}
}

const observations = new WeakSet<object>();
export type CheckedWorkflowStepObservation = ReturnType<typeof observeWorkflowStep>;
export function observeWorkflowStep(workflow: CheckedWorkflowBindings, stepId: string, event: unknown, contractSource: string) {
  assertCheckedWorkflowBindings(workflow);
  if (typeof contractSource !== 'string' || sha256(contractSource) !== WORKFLOW_OUTCOME_CONTRACT_SHA256) return fail('contract drift');
  const step = workflow.steps.find(s => s.step_id === stepId) ?? fail('unknown step');
  // Event wrapper belongs to the caller. A malformed wrapper is not an observed
  // failed call and cannot be used to claim non-commit.
  const kind = event && typeof event === 'object' ? Object.getOwnPropertyDescriptor(event, 'kind') : undefined;
  if (!kind || !Object.hasOwn(kind, 'value') || !kind.enumerable) return fail('invalid event kind');
  let settlement: OperationSettlement;
  if (kind.value === 'returned') {
    const e = own(event, ['kind', 'outcome']);
    settlement = inspectSettlement(e.outcome!.value, step.failure_continuation,step.precommit_stages??[]);
  } else if (kind.value === 'threw') {
    own(event, ['kind']); settlement = unknown('threw');
  } else if (kind.value === 'not-started') {
    own(event, ['kind']);
    settlement = Object.freeze({commit_status: 'not-committed', origin: 'not-started', status: null, stage: 'argument-materialization',
      code: 'ARGUMENT_MATERIALIZATION_FAILED', continuation: null, cleanup_failed: null, result_validation: 'not-performed'});
  } else return fail('unsupported event');
  const body = {schema_version: 'domainspec.workflow-step-observation/v1-candidate' as const, contract_sha256: WORKFLOW_OUTCOME_CONTRACT_SHA256,
    workflow_sha256: workflow.workflow_sha256, step_id: step.step_id, operation_ref: step.operation_ref, action_sha256: step.action_sha256,
    settlement, evidence: 'caller-supplied' as const, authority_effect: 'none' as const};
  const result = freezeWorkflow({...body, observation_sha256: sha256(canonicalJson(body))});
  observations.add(result); return result;
}

/** Project exact ordered observations to the existing recovery policy. A full
 * committed prefix does not establish a valid final Workflow result.
 */
export function evaluateWorkflowOutcomeJournal(policy: CheckedWorkflowRecoveryPolicy, value: unknown) {
  assertCheckedWorkflowRecoveryPolicy(policy); assertWorkflowData(value);
  const j = workflowObject(value, ['schema_version', 'workflow_execution_id', 'failure_occurrence_id', 'observations', 'local_error']);
  if (j.schema_version !== WORKFLOW_OUTCOME_JOURNAL_VERSION) return fail('unsupported journal');
  const executionId = identity(j.workflow_execution_id);
  const failureId = j.failure_occurrence_id === null ? null : identity(j.failure_occurrence_id);
  if (j.local_error !== null && j.local_error !== 'committed-result-invalid' && j.local_error !== 'result-materialization-failed') return fail('unsupported local error');
  const workflow = policy.workflow, rows: CheckedWorkflowStepObservation[] = [];
  for (const [i, v] of workflowList(j.observations).entries()) {
    if (!v || typeof v !== 'object' || !observations.has(v)) return fail('unregistered observation');
    const row = v as CheckedWorkflowStepObservation, step = workflow.steps[i];
    if (!step || row.workflow_sha256 !== workflow.workflow_sha256 || row.step_id !== step.step_id ||
      row.operation_ref !== step.operation_ref || row.action_sha256 !== step.action_sha256) return fail('observation must match exact source prefix');
    if (rows.length && rows.at(-1)!.settlement.commit_status !== 'committed') return fail('observation after terminal failure');
    rows.push(row);
  }
  const last = rows.at(-1), failed = last && last.settlement.commit_status !== 'committed' ? last : null;
  const completed = rows.filter(r => r.settlement.commit_status === 'committed').map(r => r.step_id);
  const common = {schema_version: 'domainspec.workflow-outcome-evaluation/v1-candidate' as const,
    workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256, workflow_execution_id: executionId,
    failure_occurrence_id: failureId, completed_step_ids: completed, observations: rows,
    evidence: 'caller-supplied' as const, result_validation: 'not-performed' as const, execution: 'not-performed' as const,
    authority_effect: 'none' as const};
  if (failed) {
    if (failureId === null || j.local_error !== null) return fail('terminal forward failure requires one failure identity and no local error');
    const journal = {schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION, workflow_execution_id: executionId, failure_occurrence_id: failureId,
      completed_step_ids: completed, failed_step_id: failed.step_id, failed_commit_status: failed.settlement.commit_status};
    const recovery = planSelectedWorkflowRecovery(policy, journal);
    return freezeWorkflow({...common, status: 'forward-stopped' as const, failure: failed.settlement, local_error: null,
      recovery_status: recovery.status, recovery});
  }
  if (j.local_error !== null) {
    if (failureId === null || !completed.length || j.local_error === 'result-materialization-failed' && completed.length !== workflow.steps.length) return fail('local error position or failure identity mismatch');
    return freezeWorkflow({...common, status: 'orchestration-error' as const, failure: null, local_error: j.local_error,
      recovery_status: 'not-evaluable' as const, recovery: null});
  }
  if (failureId !== null) return fail('failure identity without failure');
  return freezeWorkflow({...common, status: completed.length === workflow.steps.length ? 'forward-complete' as const : 'awaiting-next-step' as const,
    failure: null, local_error: null, recovery_status: 'not-evaluated' as const, recovery: null});
}
