import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertWorkflowData, freezeWorkflow, workflowList, workflowObject} from '../typed-backend/workflow-occurrences.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings} from './workflow-bindings.js';

export const WORKFLOW_RECOVERY_POLICY_VERSION = 'domainspec.workflow-recovery-policy/v1-candidate';
export const WORKFLOW_FAILURE_JOURNAL_VERSION = 'domainspec.workflow-failure-journal/v1-candidate';
export const WORKFLOW_RECOVERY_CONTRACT_SHA256 = '194b34af821696ec129c5894333929670efe9f8acea708c662c55a9e11d4b48f';
export interface WorkflowRecoverySelection {
  readonly schema_version: typeof WORKFLOW_RECOVERY_POLICY_VERSION;
  readonly workflow_sha256: string;
  readonly contract_sha256: typeof WORKFLOW_RECOVERY_CONTRACT_SHA256;
  readonly dependency_semantics: 'needed-compensations-only';
  readonly tie_break: 'reverse-completion';
}
export interface WorkflowFailureJournal {
  readonly schema_version: typeof WORKFLOW_FAILURE_JOURNAL_VERSION;
  readonly workflow_execution_id: string;
  readonly failure_occurrence_id: string;
  readonly completed_step_ids: readonly string[];
  readonly failed_step_id: string;
  readonly failed_commit_status: 'not-committed' | 'indeterminate';
}
const fail = (reason: string): never => {throw Object.assign(new TypeError('WORKFLOW_RECOVERY:' + reason), {code: 'WORKFLOW_RECOVERY'});};
const digest = (value: unknown) => sha256(canonicalJson(value));
const local = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
function identity(value: unknown): string {
  return typeof value === 'string' && value.length <= 256 && local.exec(value)?.[0] === value ? value : fail('invalid identity');
}
const policies = new WeakSet<object>();
export type CheckedWorkflowRecoveryPolicy = ReturnType<typeof selectWorkflowRecoveryPolicy>;
export function assertCheckedWorkflowRecoveryPolicy(value: unknown): asserts value is CheckedWorkflowRecoveryPolicy {
  if (!value || typeof value !== 'object' || !policies.has(value)) fail('unvalidated policy');
}

/** Select new semantics explicitly without rewriting the source or old planners. */
export function selectWorkflowRecoveryPolicy(workflow: CheckedWorkflowBindings, value: unknown, contractSource: string) {
  assertCheckedWorkflowBindings(workflow); assertWorkflowData(value);
  const s = workflowObject(value, ['schema_version', 'workflow_sha256', 'contract_sha256', 'dependency_semantics', 'tie_break']);
  if (s.schema_version !== WORKFLOW_RECOVERY_POLICY_VERSION || s.dependency_semantics !== 'needed-compensations-only' || s.tie_break !== 'reverse-completion') fail('unsupported policy');
  if (s.contract_sha256 !== WORKFLOW_RECOVERY_CONTRACT_SHA256 || typeof contractSource !== 'string' || sha256(contractSource) !== WORKFLOW_RECOVERY_CONTRACT_SHA256) fail('contract drift');
  if (s.workflow_sha256 !== workflow.workflow_sha256) fail('stale Workflow');
  const selection: WorkflowRecoverySelection = {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256,
    contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion'};
  const body = {schema_version: 'domainspec.checked-workflow-recovery-policy/v1-candidate' as const, selection, workflow,
    unknown_commit: 'reconciliation-required' as const, compensation_execution: 'external-only' as const, authority_effect: 'none' as const};
  const result = freezeWorkflow({...body, policy_sha256: digest(body)}); policies.add(result); return result;
}

export function decodeWorkflowFailureJournal(value: unknown): WorkflowFailureJournal {
  assertWorkflowData(value);
  const j = workflowObject(value, ['schema_version', 'workflow_execution_id', 'failure_occurrence_id', 'completed_step_ids', 'failed_step_id', 'failed_commit_status']);
  if (j.schema_version !== WORKFLOW_FAILURE_JOURNAL_VERSION) fail('unsupported journal');
  const failed_commit_status = j.failed_commit_status;
  if (failed_commit_status !== 'not-committed' && failed_commit_status !== 'indeterminate') return fail('unknown commit classification');
  const completed_step_ids = workflowList(j.completed_step_ids).map(identity);
  if (new Set(completed_step_ids).size !== completed_step_ids.length) fail('duplicate completed step');
  return freezeWorkflow({schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION, workflow_execution_id: identity(j.workflow_execution_id),
    failure_occurrence_id: identity(j.failure_occurrence_id), completed_step_ids, failed_step_id: identity(j.failed_step_id), failed_commit_status});
}

/** Pure candidate planning against caller-supplied commit observations. This does
 * not verify provider truth, register an intent, dispatch, retry, or waive guards.
 */
export function planSelectedWorkflowRecovery(policy: CheckedWorkflowRecoveryPolicy, value: unknown) {
  assertCheckedWorkflowRecoveryPolicy(policy);
  const journal = decodeWorkflowFailureJournal(value), workflow = policy.workflow;
  const failureIndex = journal.completed_step_ids.length;
  if (journal.completed_step_ids.some((id, i) => workflow.steps[i]?.step_id !== id) || workflow.steps[failureIndex]?.step_id !== journal.failed_step_id) fail('journal must be the exact completed prefix and next failed step');
  const common = {schema_version: 'domainspec.workflow-recovery-evaluation/v1-candidate' as const, workflow_sha256: workflow.workflow_sha256,
    policy_sha256: policy.policy_sha256, journal, journal_sha256: digest(journal), commit_evidence: 'caller-supplied' as const,
    intent_registration: 'not-performed' as const, compensation_execution: false as const, authority_effect: 'none' as const};
  if (journal.failed_commit_status === 'indeterminate') {
    return freezeWorkflow({...common, status: 'reconciliation-required' as const, workflow_evaluation_result: null, recovery_intent: null,
      unknown_step_id: journal.failed_step_id});
  }
  const completed = new Map(journal.completed_step_ids.map((id, i) => [id, i]));
  const selected = workflow.compensations.filter(c => completed.has(c.for_step));
  const active = new Set(selected.map(c => c.compensation_id));
  const remaining = selected.map(c => ({compensation_id: c.compensation_id, for_step: c.for_step,
    operation_ref: c.operation_ref, action_sha256: c.action_sha256,
    depends_on: c.depends_on.filter(id => active.has(id)).sort(),
    inactive_dependencies: c.depends_on.filter(id => !active.has(id)).sort(),
    arguments: c.arguments, events: c.events, failure_continuation: c.failure_continuation,
    completion_index: completed.get(c.for_step)!})).sort((a, b) => b.completion_index - a.completion_index);
  type PlanRow = Omit<(typeof remaining)[number], 'completion_index'>;
  const ordered: PlanRow[] = [], emitted = new Set<string>();
  while (remaining.length) {
    const index = remaining.findIndex(c => c.depends_on.every(id => emitted.has(id)));
    if (index < 0) return fail('cyclic active dependencies');
    const [{completion_index: _index, ...next}] = remaining.splice(index, 1) as [NonNullable<(typeof remaining)[number]>];
    ordered.push(next); emitted.add(next.compensation_id);
  }
  if (!ordered.length) return freezeWorkflow({...common, status: 'evaluated' as const, workflow_evaluation_result: 'not-required' as const, recovery_intent: null});
  const completed_step_journal_digest = digest({schema_version: 'domainspec.workflow-completed-prefix/v1-candidate', workflow_sha256: workflow.workflow_sha256,
    workflow_execution_id: journal.workflow_execution_id, steps: journal.completed_step_ids.map(id => {
      const step = workflow.steps.find(s => s.step_id === id)!; return {step_id: id, operation_ref: step.operation_ref, action_sha256: step.action_sha256};
    })});
  const plan_digest = digest({schema_version: 'domainspec.workflow-recovery-plan/v3-candidate', policy_sha256: policy.policy_sha256, plan: ordered});
  const intentBody = {schema_version: 'domainspec.workflow-recovery-intent/v3-candidate' as const, workflow_selector: workflow.bindings.selector,
    workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256, workflow_execution_id: journal.workflow_execution_id,
    failure_occurrence_id: journal.failure_occurrence_id, failed_step_id: journal.failed_step_id, completed_step_journal_digest, plan_digest};
  const intent_id = digest(intentBody);
  const plan = ordered.map(row => ({...row, invocation_identity: digest({schema_version: 'domainspec.compensation-invocation/v2-candidate', intent_id, plan_digest,
    compensation_id: row.compensation_id, operation_ref: row.operation_ref, action_sha256: row.action_sha256})}));
  return freezeWorkflow({...common, status: 'evaluated' as const, workflow_evaluation_result: 'recovery-required' as const,
    recovery_intent: {...intentBody, intent_id, semantic_status: 'required' as const, plan}});
}
