import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings, type WorkflowValueExpression} from '../typed-operation/workflow-bindings.js';
import type {TypedType, ValueExpression} from '../typed-operation/contracts.js';
import {createOperationValueReference, operationReferenceFields} from './reconciled-operation-values.js';
import {eventReferenceIdentity} from '../generation/event-reference-identity.js';

export const WORKFLOW_VALUES_DEFINITION_SHA256 = '2cfde9cbe6ef8979eaa2f7b79007f2fdd768f0bd0c246c9018b4c5ae59d9cf4c';
const fail = (message: string): never => {throw new TypeError('WORKFLOW_VALUE_REFERENCE:' + message);};
type Input = Readonly<Record<string, any>>;
type Result = Readonly<{step_id: string; action_sha256: string; value: any}>;
type Bound = Readonly<{type: TypedType; value: any}>;
function freeze<T>(v: T): T {
  if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);}
  return v;
}
/** Own descriptor capture is separate from semantic normalization and never invokes ordinary accessors. */
function snapshot(raw: unknown): any {
  let visits = 0;
  const copy = (v: unknown, depth: number): any => {
    if (++visits > 20000 || depth > 64) return fail('capture capacity');
    if (v === null || ['string', 'boolean', 'bigint'].includes(typeof v) || typeof v === 'number' && Number.isFinite(v)) return v;
    if (!v || typeof v !== 'object') return fail('inert value required');
    const array = Array.isArray(v), proto = Object.getPrototypeOf(v);
    if (array ? proto !== Array.prototype : proto !== Object.prototype && proto !== null) return fail('ordinary container required');
    const keys = Reflect.ownKeys(v);
    if (keys.length > 2048) return fail('capture key capacity');
    if (array) {
      const n = Object.getOwnPropertyDescriptor(v, 'length')!.value;
      if (!Number.isInteger(n) || n < 0 || n > 1024 || keys.length !== n + 1) return fail('dense bounded array required');
      return Array.from({length: n}, (_, i) => {
        const d = Object.getOwnPropertyDescriptor(v, String(i));
        if (!d?.enumerable || !Object.hasOwn(d, 'value')) return fail('inert element required');
        return copy(d.value, depth + 1);
      });
    }
    return Object.fromEntries(keys.map(k => {
      const d = Object.getOwnPropertyDescriptor(v, k);
      if (typeof k !== 'string' || !d?.enumerable || !Object.hasOwn(d, 'value')) return fail('inert member required');
      return [k, copy(d.value, depth + 1)];
    }));
  };
  return copy(raw, 0);
}

/** Event input only: generated occurredAt remains absent and no clock is called. */
function eventInput(graph: CompiledProjectGraph, contract: CheckedWorkflowBindings['event_inputs'][number]['contract'], value: any) {
  const generated = contract.occurred_at_policy === 'generated';
  operationReferenceFields(value, generated ? ['occurrence', 'payload'] : ['occurrence', 'payload', 'occurredAt']);
  const field = (type: {kind: string; name?: string; selector?: string}, v: any): any => {
    if (type.kind === 'reference') {
      const scalar = eventReferenceIdentity(graph, type.selector!, reason => fail(reason)).scalar;
      if (scalar === 'String') return typeof v === 'string' && v.length ? v : fail('nonempty Event reference required');
      if (typeof v === 'number' && !Number.isSafeInteger(v) || typeof v === 'string' && !/^(?:0|[1-9][0-9]*)$/.test(v) || !['bigint', 'number', 'string'].includes(typeof v)) return fail('exact Event UInt64 reference required');
      const n = BigInt(v); return n >= 0n && n <= 18446744073709551615n ? n : fail('Event UInt64 reference range');
    }
    if (type.name === 'uuid' || type.name === 'timestamp') return typeof v === 'string' && v.length ? v : fail('nonempty Event text required');
    if (type.name === 'string') return typeof v === 'string' ? v : fail('Event string required');
    if (type.name === 'boolean') return typeof v === 'boolean' ? v : fail('Event boolean required');
    if (type.name === 'decimal') return typeof v === 'number' && Number.isFinite(v) ? v : fail('finite Event decimal required');
    if (type.name !== 'integer') return fail('unknown checked Event scalar');
    if (typeof v === 'number' && !Number.isSafeInteger(v) || typeof v === 'string' && !/^(?:0|-[1-9][0-9]*|[1-9][0-9]*)$/.test(v) || !['bigint', 'number', 'string'].includes(typeof v)) return fail('exact signed Event integer required');
    const n = BigInt(v); return n >= -9223372036854775808n && n <= 9223372036854775807n ? n : fail('Event integer range');
  };
  const id = contract.occurrence_id;
  operationReferenceFields(value.occurrence, [id.field_id]);
  operationReferenceFields(value.payload, contract.payload.map(p => p.field_id), contract.payload.filter(p => p.required).map(p => p.field_id));
  return {occurrence: {[id.field_id]: field(id.type_ref, value.occurrence[id.field_id])},
    payload: Object.fromEntries(contract.payload.filter(p => Object.hasOwn(value.payload, p.field_id)).map(p => [p.field_id, field(p.type_ref, value.payload[p.field_id])])),
    ...(generated ? {} : {occurredAt: field({kind: 'primitive', name: 'timestamp'}, value.occurredAt)})};
}

/** Independent checked-source value interpreter, not a generator or Workflow executor. */
export function createWorkflowValueReference(graph: CompiledProjectGraph, workflow: CheckedWorkflowBindings, definition: string) {
  assertCompiledProjectSnapshot(graph); assertCheckedWorkflowBindings(workflow);
  if (typeof definition !== 'string' || sha256(definition) !== WORKFLOW_VALUES_DEFINITION_SHA256) fail('definition drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (canonicalJson(workflow.certificate) !== canonicalJson(certificate)) fail('source certificate mismatch');
  const values = createOperationValueReference(graph), captures = new WeakSet<object>(), owners = new WeakMap<object, Input>();
  const inputs = workflow.bindings.inputs, steps = workflow.occurrence_source.steps;
  const assertInput = (v: unknown): Input => v && typeof v === 'object' && captures.has(v) ? v as Input : fail('unregistered input');
  function capture(raw: unknown): Input {
    const data = snapshot(raw);
    operationReferenceFields(data, [...inputs.map(p => p.name), ...workflow.event_inputs.map(p => p.name)]);
    const input = freeze(Object.fromEntries([...inputs.map(p => [p.name, values.normalize(p.type, data[p.name])]),
      ...workflow.event_inputs.map(p => [p.name, eventInput(graph, p.contract, data[p.name])])]));
    captures.add(input); return input;
  }
  function captureResult(input: Input, stepId: string, raw: unknown): Result {
    assertInput(input);
    const step = workflow.steps.find(s => s.step_id === stepId) ?? fail('unknown result occurrence');
    const result = freeze({step_id: step.step_id, action_sha256: step.action_sha256, value: values.normalize(step.signature.result, snapshot(raw))});
    owners.set(result, input); return result;
  }
  function scope(input: Input, results: readonly Result[], min: number, max: number): Map<string, Bound> {
    assertInput(input);
    if (!Array.isArray(results) || Object.getPrototypeOf(results) !== Array.prototype) return fail('result array required');
    const length = Object.getOwnPropertyDescriptor(results, 'length')!.value;
    if (length < min || length > max || Reflect.ownKeys(results).length !== length + 1) return fail('exact result prefix required');
    const env = new Map(inputs.map(p => ['input:' + p.name, {type: p.type, value: input[p.name]}]));
    for (let i = 0; i < length; i++) {
      const d = Object.getOwnPropertyDescriptor(results, String(i));
      if (!d?.enumerable || !Object.hasOwn(d, 'value')) return fail('inert result prefix required');
      const row = d.value;
      if (!row || typeof row !== 'object' || owners.get(row) !== input) return fail('cross-capture or forged result');
      if (row.step_id !== steps[i]!.step_id) return fail('reordered result occurrence');
      const step = workflow.steps.find(s => s.step_id === row.step_id)!;
      env.set('result:' + row.step_id, {type: step.signature.result, value: row.value});
    }
    return env;
  }
  function expression(e: WorkflowValueExpression): ValueExpression {
    switch (e.op) {
      case 'input': return {op: 'path', root: 'input:' + e.name, properties: e.properties};
      case 'step-result': return {op: 'path', root: 'result:' + e.step_id, properties: e.properties};
      case 'to_set': return {op: 'to_set', value: expression(e.value)};
      default: return e;
    }
  }
  function call(input: Input, results: readonly Result[], id: string, compensation: boolean) {
    const source = compensation ? workflow.occurrence_source.compensations.find(c => c.compensation_id === id) : steps.find(s => s.step_id === id);
    if (!source) return fail('unknown call occurrence');
    const before = compensation ? steps.findIndex(s => s.step_id === (source as {for_step: string}).for_step) + 1 : steps.findIndex(s => s.step_id === id);
    const env = scope(input, results, before, compensation ? steps.length : before);
    const binding = compensation ? workflow.bindings.compensations.find(c => c.compensation_id === id)! : workflow.bindings.steps.find(c => c.step_id === id)!;
    return freeze(Object.fromEntries([...binding.arguments.map(a => [a.parameter, values.value(expression(a.value), env).value]),
      ...binding.events.map(e => [e.parameter, input[e.input]])]));
  }
  function result(input: Input, results: readonly Result[]) {
    const env = scope(input, results, steps.length, steps.length);
    return freeze(values.normalize(workflow.bindings.result.type, values.value(expression(workflow.bindings.result.value), env).value));
  }
  return Object.freeze({workflow_sha256: workflow.workflow_sha256, capture, captureResult, result,
    forward: (input: Input, id: string, results: readonly Result[]) => call(input, results, id, false),
    compensation: (input: Input, id: string, results: readonly Result[]) => call(input, results, id, true)});
}
