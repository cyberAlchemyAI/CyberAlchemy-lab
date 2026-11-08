import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy, type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';
import {assertCheckedOperationAction, type CheckedOperationAction} from '../typed-operation/action-bindings.js';
import type {FactoryBinding} from '../generation/configured-factories.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createWorkflowBinding} from './reconciled-workflow-binding.js';
import {createWorkflowValueReference} from './reconciled-workflow-value-reference.js';
import {createWorkflowOutcomeReference, inspectWorkflowSettlementReference} from './reconciled-workflow-outcome-reference.js';
import {createBoundEffectfulOperationReference, type OperationEffectFixture} from './reconciled-operation-effect-reference.js';
import {operationReferenceValue, OperationReferenceUnsupported, type OperationFixtureMode} from './reconciled-operation-reference.js';
import {captureOperationRecipe, operationReferenceFields} from './reconciled-operation-values.js';
import {operationValueRecipe} from './reconciled-operation-cases.js';
import type {FactRecipe} from './reconciled-rule-facts.js';

export const WORKFLOW_EXECUTION_DEFINITION_SHA256 = '249e27ade987fb2d1e7b2030d048329b0b9526d402051256bacbab75a2c38127';
export interface WorkflowExecutionCase {
  readonly input: FactRecipe;
  readonly identity: Readonly<{workflow_execution_id: string; failure_occurrence_id: string}>;
  readonly steps: readonly (OperationEffectFixture & Readonly<{step_id: string; mode: OperationFixtureMode}>)[];
  readonly capture: boolean;
}
export class WorkflowExecutionCapacity extends Error {}
const fail = (m: string): never => {throw new TypeError('WORKFLOW_EXECUTION_REFERENCE:' + m);};
const modes = new Set(['committed', 'rejected', 'indeterminate', 'begin-throw', 'commit-throw', 'rollback-throw', 'receipt-empty', 'receipt-unknown', 'receipt-extra', 'receipt-null', 'receipt-getter', 'receipt-inherited', 'receipt-symbol', 'receipt-hidden', 'receipt-array', 'receipt-undefined']);
const names = (rows: readonly {slot: string}[]) => rows.map(r => r.slot).sort();
const equal = (a: unknown, b: unknown) => canonicalJson(a) === canonicalJson(b);
function inert(value: unknown): any {
  let visits = 0, bytes = 0;
  const charge = (n: number) => {bytes += n; if (bytes > 8388608) throw new WorkflowExecutionCapacity('Workflow case bytes exceed 8 MiB');};
  const textBytes = (v: string) => {
    if (v.length > 8388608) throw new WorkflowExecutionCapacity('Workflow case text exceeds 8 MiB');
    return Buffer.byteLength(JSON.stringify(v));
  };
  const walk = (v: unknown, depth = 0): any => {
    if (++visits > 65536 || depth > 128) throw new WorkflowExecutionCapacity('Workflow case structure exceeds capacity');
    if (v === null || typeof v === 'string' || typeof v === 'boolean' || typeof v === 'number' && Number.isFinite(v)) {charge(typeof v === 'string' ? textBytes(v) : Buffer.byteLength(JSON.stringify(v))); return v;}
    if (!v || typeof v !== 'object') return fail('inert case value');
    const array = Array.isArray(v), proto = Object.getPrototypeOf(v), keys = Reflect.ownKeys(v);
    if (array ? proto !== Array.prototype : proto !== Object.prototype && proto !== null) return fail('plain case container');
    if (keys.length > 65536) throw new WorkflowExecutionCapacity('Workflow case key capacity');
    if (array) {
      const n = Object.getOwnPropertyDescriptor(v, 'length')!.value;
      if (keys.length !== n + 1) return fail('dense case array');
      charge(2 + Math.max(0, n - 1));
      return Array.from({length: n}, (_, i) => {
        const p = Object.getOwnPropertyDescriptor(v, String(i));
        if (!p?.enumerable || !Object.hasOwn(p, 'value')) return fail('inert case element');
        return walk(p.value, depth + 1);
      });
    }
    charge(2 + Math.max(0, keys.length - 1));
    return Object.fromEntries(keys.map(k => {
      const p = Object.getOwnPropertyDescriptor(v, k)!;
      if (typeof k !== 'string' || !p.enumerable || !Object.hasOwn(p, 'value')) return fail('inert case member');
      charge(textBytes(k) + 1);
      return [k, walk(p.value, depth + 1)];
    }));
  };
  const result = walk(value);
  if (Buffer.byteLength(canonicalJson(result)) > 8388608) throw new WorkflowExecutionCapacity('Workflow case bytes exceed 8 MiB');
  return result;
}
/** Decode only values emitted by the independent Operation oracle, never native output. */
function expectedValue(tagged: any): any {
  const [tag, value] = tagged;
  if (tag === 'null') return null;
  if (tag === 'bigint') return BigInt(value);
  if (['string', 'boolean', 'number'].includes(tag)) return value;
  if (tag === 'array') return value.map(expectedValue);
  if (tag === 'record') return Object.fromEntries(value.map(([k, v]: [string, any]) => [k, expectedValue(v)]));
  return fail('unexpected oracle value');
}

export function createWorkflowExecutionReference(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledProjectPlan,
  definitions: Readonly<{execution: string; binding: string; values: string; outcomes: string}>) {
  // Definitions are inert byte inputs; no caller accessors participate in source binding.
  const d = inert(definitions); operationReferenceFields(d, ['execution', 'binding', 'values', 'outcomes']);
  if (typeof d.execution !== 'string' || sha256(d.execution) !== WORKFLOW_EXECUTION_DEFINITION_SHA256) fail('definition drift');
  const binding = createWorkflowBinding(node, graph, plan, d.binding);
  const oracle = createBoundWorkflowExecutionReference(graph, binding.workflow, binding.policy,
    binding.operations.map(o => o.action), plan.selection.factories, {execution: d.execution, values: d.values, outcomes: d.outcomes});
  return Object.freeze({...oracle, binding});
}

/** Shared source interpreter. Native adapters bind their own registered plan;
 * no generated module or native execution supplies expected behavior here. */
export function createBoundWorkflowExecutionReference(graph: CompiledProjectGraph, workflow: CheckedWorkflowBindings,
  policy: CheckedWorkflowRecoveryPolicy, actions: readonly CheckedOperationAction[], factories: readonly FactoryBinding[],
  definitions: Readonly<{execution: string; values: string; outcomes: string}>, receiptValidation: 'exception-derived' | 'native-explicit' = 'exception-derived') {
  assertCompiledProjectSnapshot(graph); assertCheckedWorkflowBindings(workflow); assertCheckedWorkflowRecoveryPolicy(policy);
  const d = inert(definitions); operationReferenceFields(d, ['execution', 'values', 'outcomes']);
  if (typeof d.execution !== 'string' || sha256(d.execution) !== WORKFLOW_EXECUTION_DEFINITION_SHA256) fail('definition drift');
  if (!['exception-derived', 'native-explicit'].includes(receiptValidation)) fail('receipt validation boundary');
  const certificate = createCompiledProjectCertificate(graph);
  if (!equal(workflow.certificate, certificate) || policy.workflow !== workflow) fail('source Workflow/policy identity');
  if (!Array.isArray(actions) || Object.getPrototypeOf(actions) !== Array.prototype) fail('source actions');
  const descriptors: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(actions), length = descriptors.length!.value;
  const required = new Map([...workflow.steps, ...workflow.compensations].map(s => [s.operation_ref, s.action_sha256]));
  if (length !== required.size || Reflect.ownKeys(descriptors).length !== length + 1) fail('exact action closure');
  const selected: CheckedOperationAction[] = [], seen = new Set<string>();
  for (let i = 0; i < length; i++) {
    const p = descriptors[String(i)];
    if (!p?.enumerable || !Object.hasOwn(p, 'value')) fail('inert source action');
    const action = p!.value; assertCheckedOperationAction(action);
    if (!equal(action.certificate, certificate) || action.boundary_sha256 !== workflow.boundary_sha256 ||
        action.field_compilation_sha256 !== workflow.field_compilation_sha256 ||
        required.get(action.bindings.selector) !== action.action_sha256 || seen.has(action.bindings.selector)) fail('source action binding');
    seen.add(action.bindings.selector); selected.push(action);
  }
  const values = createWorkflowValueReference(graph, workflow, d.values), outcomes = createWorkflowOutcomeReference(policy, d.outcomes);
  const operations = new Map(selected.map(action => [action.bindings.selector, createBoundEffectfulOperationReference(graph, action, factories)]));
  function captureCase(raw: unknown): WorkflowExecutionCase {
    const c = inert(raw); operationReferenceFields(c, ['input', 'identity', 'steps', 'capture']);
    operationReferenceFields(c.identity, ['workflow_execution_id', 'failure_occurrence_id']);
    if (typeof c.capture !== 'boolean' || Object.values(c.identity).some(v => typeof v !== 'string')) fail('case primitive metadata');
    if (!c.input || typeof c.input !== 'object' || Array.isArray(c.input)) fail('input recipe');
    if (!Array.isArray(c.steps) || c.steps.length !== workflow.steps.length || c.steps.length > 128) fail('exact source occurrences');
    const availability = new Map<string, string>();
    c.steps.forEach((s: any, i: number) => {
      operationReferenceFields(s, ['step_id', 'mode', 'reads', 'clocks']);
      if (s.step_id !== workflow.steps[i]!.step_id || !modes.has(s.mode) || !Array.isArray(s.reads) || !Array.isArray(s.clocks)) fail('source occurrence or mode');
      const action = operations.get(workflow.steps[i]!.operation_ref)!.action;
      for (const r of s.reads) {operationReferenceFields(r, ['slot', 'value', 'throws'], ['slot', 'value']); if (typeof r.slot !== 'string' || Object.hasOwn(r, 'throws') && typeof r.throws !== 'boolean') fail('read fixture');}
      for (const clock of s.clocks) {operationReferenceFields(clock, ['slot', 'value', 'mode'], ['slot', 'value']); if (typeof clock.slot !== 'string' || !['return', 'throw', 'missing'].includes(clock.mode ?? 'return') || clock.value !== null && !['string', 'number'].includes(typeof clock.value)) fail('clock fixture');}
      if (!equal(names(s.reads), action.reads.map(r => r.slot).sort()) || !equal(names(s.clocks), action.events.filter(e => e.contract.occurred_at_policy === 'generated').map(e => e.slot).sort())) fail('exact effect slots');
      const missing = canonicalJson(s.clocks.filter((c: any) => c.mode === 'missing').map((c: any) => c.slot).sort()), prior = availability.get(action.bindings.selector);
      if (prior !== undefined && prior !== missing) fail('captured clock availability differs across repeated Operation');
      availability.set(action.bindings.selector, missing);
    });
    return freezeWorkflow(c);
  }
  function expected(raw: unknown) {
    const c = captureCase(raw), port_trace: string[] = [], batches: unknown[] = [], read_requests: unknown[] = [], clock_calls: string[] = [];
    const finish = (outcome: unknown, rejected = false) => {
      const result = {rejected, outcome: rejected ? null : operationReferenceValue(outcome), port_trace, batches, read_requests, clock_calls,
        settled_while_pending: false, overlapping_ports: false, getter_reads: 0, input_changed: false, read_changed: false};
      if (Buffer.byteLength(canonicalJson(result)) > 8388608) throw new WorkflowExecutionCapacity('Workflow expectation exceeds 8 MiB');
      return freezeWorkflow(result);
    };
    let input: ReturnType<typeof values.capture>;
    try {
      if (Object.values(c.identity).some(v => v.length > 256 || /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(v)?.[0] !== v)) return finish(null, true);
      input = values.capture(captureOperationRecipe(c.input));
    } catch (e) {if (e instanceof OperationReferenceUnsupported || e instanceof WorkflowExecutionCapacity) throw e; if (!(e instanceof TypeError)) throw e; return finish(null, true);}
    const results: ReturnType<typeof values.captureResult>[] = [], events: any[] = [];
    const evaluation = (failed: boolean, local_error: string | null = null) => outcomes.evaluate({...c.identity, failure_occurrence_id: failed ? c.identity.failure_occurrence_id : null, events, local_error});
    const stopped = (local: string | null = null) => {
      const e = evaluation(true, local), intent = e.recovery?.recovery_intent;
      if (!intent) return finish({status: local ? 'orchestration-error' : 'forward-stopped', evaluation: e, bindings_status: e.recovery?.workflow_evaluation_result === 'not-required' ? 'not-required' : 'not-evaluable', recovery_bindings: null});
      try {
        const rows = intent.plan.map(row => ({intent_id: intent.intent_id, plan_digest: intent.plan_digest, invocation_identity: row.invocation_identity,
          compensation_id: row.compensation_id, operation_ref: row.operation_ref, action_sha256: row.action_sha256, arguments: values.compensation(input, row.compensation_id, results)}));
        return finish({status: 'forward-stopped', evaluation: e, bindings_status: 'ready', recovery_bindings: {schema_version: 'domainspec.workflow-recovery-bindings/v1-candidate', intent_id: intent.intent_id, plan_digest: intent.plan_digest, bindings: rows, compensation_execution: false, authority_effect: 'none'}});
      } catch (e) {if (!(e instanceof TypeError)) throw e; return finish({status: 'forward-stopped', evaluation: evaluation(true), bindings_status: 'failed', recovery_bindings: null});}
    };
    for (const [i, step] of workflow.steps.entries()) {
      let args: unknown;
      try {args = values.forward(input, step.step_id, results);} catch (e) {if (!(e instanceof TypeError)) throw e; events.push({step_id: step.step_id, kind: 'not-started'}); return stopped();}
      const observation = operations.get(step.operation_ref)!.expected(operationValueRecipe(args), c.steps[i]!, c.steps[i]!.mode);
      port_trace.push(...observation.trace.map(p => step.step_id + ':' + p));
      batches.push(...observation.batches.map(value => ({step_id: step.step_id, value})));
      read_requests.push(...observation.read_requests.map(value => ({step_id: step.step_id, value})));
      clock_calls.push(...observation.clock_calls.map(slot => step.step_id + ':' + slot));
      const rawOutcome = expectedValue(observation.outcome);
      // Preserve native explicit receipt validation before hashing observations
      // and deriving recovery metadata. Default source/TypeScript cases stay intact.
      if (receiptValidation === 'native-explicit' && c.steps[i]!.mode.startsWith('receipt-') &&
          rawOutcome.stage === 'commit' && rawOutcome.code === 'COMMIT_UNCERTAIN') rawOutcome.code = 'INVALID_COMMIT_RECEIPT';
      events.push({step_id: step.step_id, kind: 'returned', outcome: rawOutcome});
      if (inspectWorkflowSettlementReference(rawOutcome, step.failure_continuation).commit_status !== 'committed') return stopped();
      try {results.push(values.captureResult(input, step.step_id, rawOutcome.value));} catch (e) {if (!(e instanceof TypeError)) throw e; return stopped('committed-result-invalid');}
    }
    let value: unknown;
    try {value = values.result(input, results);} catch (e) {if (!(e instanceof TypeError)) throw e; return stopped('result-materialization-failed');}
    return finish({status: 'succeeded', value, evaluation: evaluation(false), recovery_bindings: null});
  }
  return Object.freeze({workflow, policy, actions: Object.freeze(selected), captureCase, expected});
}
