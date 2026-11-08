import {MINIMAL_VALUE_CONTEXT_SHA256} from '../generation/reconciled-sources.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertWorkflowData, decodeWorkflowOccurrences, freezeWorkflow, workflowList, workflowObject, workflowOperationRefs} from '../typed-backend/workflow-occurrences.js';
import {assertCheckedOperationAction, assertCheckedComposedOperationAction, type CheckedOperationAction, type CheckedComposedOperationAction} from './action-bindings.js';
import {decodeTypedType, decodeValueExpression, type TypedType, type TypedParameter, type ValueExpression} from './contracts.js';
import {createTypedValueChecker} from './value-bindings.js';
import {composedPrecommitStages,type ComposedWorkflowAction,type ComposedPrecommitStage} from './composed-settlement.js';

export const WORKFLOW_BINDINGS_VERSION = 'domainspec.workflow-bindings/v1-candidate';
export const WORKFLOW_BINDING_CONTRACT_SHA256 = '8a6d9f928696c263137edb8a53d3c87c0cc5394090fd1268e02699e2860eac2a';
export const COMPOSED_WORKFLOW_CONTRACT_SHA256 = 'f33b6d4f7dbaf976ed3aa1892f29735ff4ad2fb0a6c77cd2d8c7f7f6bb4d445b';
export type WorkflowValueExpression =
  | Extract<ValueExpression, {op: 'literal' | 'variant'}>
  | Readonly<{op: 'input'; name: string; properties: readonly string[]}>
  | Readonly<{op: 'step-result'; step_id: string; properties: readonly string[]}>
  | Readonly<{op: 'to_set'; value: WorkflowValueExpression}>;
interface CallBinding {
  readonly action_sha256: string;
  readonly arguments: readonly Readonly<{parameter: string; value: WorkflowValueExpression}>[];
  readonly events: readonly Readonly<{parameter: string; input: string}>[];
}
export interface WorkflowBindings {
  readonly schema_version: typeof WORKFLOW_BINDINGS_VERSION;
  readonly selector: string;
  readonly inputs: readonly TypedParameter[];
  readonly event_inputs: readonly Readonly<{name: string; event_ref: string}>[];
  readonly steps: readonly (CallBinding & Readonly<{step_id: string}>)[];
  readonly compensations: readonly (CallBinding & Readonly<{compensation_id: string}>)[];
  readonly result: Readonly<{type: TypedType; value: WorkflowValueExpression}>;
}
export class WorkflowBindingError extends Error {
  constructor(readonly code: string, readonly pointer: string) {super(code + ':' + pointer); this.name = 'WorkflowBindingError';}
}
const fail = (code: string, pointer: string): never => {throw new WorkflowBindingError('WORKFLOW_BINDING_' + code, pointer);};
const parameter = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const occurrence = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const selector = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
function text(v: unknown, pattern: RegExp, pointer: string): string {
  return typeof v === 'string' && v.length <= 256 && pattern.exec(v)?.[0] === v ? v : fail('IDENTIFIER', pointer);
}
function unique(names: readonly string[], pointer: string): void {if (new Set(names).size !== names.length) fail('DUPLICATE', pointer);}
function exact(left: readonly string[], right: readonly string[], pointer: string): void {
  if (canonicalJson([...left].sort()) !== canonicalJson([...right].sort())) fail('COVERAGE', pointer);
}
function expression(v: unknown): WorkflowValueExpression {
  const row = v as Record<string, unknown> | null;
  if (!row || typeof row !== 'object') return fail('EXPRESSION', '/value');
  if (row.op === 'input' || row.op === 'step-result') {
    const key = row.op === 'input' ? 'name' : 'step_id';
    const p = workflowObject(row, ['op', key, 'properties']);
    const name = text(p[key], row.op === 'input' ? parameter : occurrence, '/value/' + key);
    const path = decodeValueExpression({op: 'path', root: 'value', properties: workflowList(p.properties)}, '/value', true);
    if (path.op !== 'path') return fail('EXPRESSION', '/value');
    return row.op === 'input' ? {op: 'input', name, properties: path.properties} : {op: 'step-result', step_id: name, properties: path.properties};
  }
  if (row.op === 'to_set') {const p = workflowObject(row, ['op', 'value']); return {op: 'to_set', value: expression(p.value)};}
  if (row.op !== 'literal' && row.op !== 'variant') return fail('EXPRESSION', '/value/op');
  return decodeValueExpression(row, '/value', true) as Extract<ValueExpression, {op: 'literal' | 'variant'}>;
}

/** Decode an owned compiler binding; the authored Workflow source is unchanged. */
export function decodeWorkflowBindings(value: unknown): WorkflowBindings {
  assertWorkflowData(value);
  const c = workflowObject(value, ['schema_version', 'selector', 'inputs', 'event_inputs', 'steps', 'compensations', 'result']);
  if (c.schema_version !== WORKFLOW_BINDINGS_VERSION) fail('VERSION', '/schema_version');
  const inputs = workflowList(c.inputs).map(v => {const p = workflowObject(v, ['name', 'type']); return {name: text(p.name, parameter, '/inputs/name'), type: decodeTypedType(p.type)};});
  const event_inputs = workflowList(c.event_inputs).map(v => {const p = workflowObject(v, ['name', 'event_ref']); return {name: text(p.name, parameter, '/event_inputs/name'), event_ref: text(p.event_ref, selector, '/event_inputs/event_ref')};});
  unique([...inputs, ...event_inputs].map(p => p.name), '/inputs');
  const call = (v: unknown, id: 'step_id' | 'compensation_id') => {
    const p = workflowObject(v, [id, 'action_sha256', 'arguments', 'events']);
    const args = workflowList(p.arguments).map(v => {const a = workflowObject(v, ['parameter', 'value']); return {parameter: text(a.parameter, parameter, '/arguments/parameter'), value: expression(a.value)};});
    const events = workflowList(p.events).map(v => {const e = workflowObject(v, ['parameter', 'input']); return {parameter: text(e.parameter, parameter, '/events/parameter'), input: text(e.input, parameter, '/events/input')};});
    unique(args.map(a => a.parameter), '/arguments'); unique(events.map(e => e.parameter), '/events');
    return {id: text(p[id], occurrence, '/' + id), action_sha256: text(p.action_sha256, /^[a-f0-9]{64}$/, '/action_sha256'), arguments: args, events};
  };
  const steps = workflowList(c.steps, 1).map(v => {const {id, ...c} = call(v, 'step_id'); return {step_id: id, ...c};});
  const compensations = workflowList(c.compensations).map(v => {const {id, ...c} = call(v, 'compensation_id'); return {compensation_id: id, ...c};});
  unique(steps.map(s => s.step_id), '/steps'); unique(compensations.map(s => s.compensation_id), '/compensations');
  const result = workflowObject(c.result, ['type', 'value']);
  return freezeWorkflow({schema_version: WORKFLOW_BINDINGS_VERSION, selector: text(c.selector, selector, '/selector'), inputs, event_inputs, steps, compensations,
    result: {type: decodeTypedType(result.type), value: expression(result.value)}});
}

const checked = new WeakSet<object>();
export type CheckedWorkflowBindings = ReturnType<typeof compileWorkflowBindings>;
export function assertCheckedWorkflowBindings(value: unknown): asserts value is CheckedWorkflowBindings {
  if (!value || typeof value !== 'object' || !checked.has(value)) fail('UNVALIDATED', '/');
}

/** Static call closure only. Graph edges do not choose recovery or invoke providers. */
export function compileWorkflowBindings(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields|null,
  actions: readonly CheckedOperationAction[], value: unknown, contractSource: string) {
  return compileWorkflowBindingsCore(graph, boundary, fields, actions, value, contractSource, false);
}

/** Explicit composed call closure; intermediate values are not caller inputs. */
export function compileComposedWorkflowBindings(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields,
  actions: readonly ComposedWorkflowAction[], value: unknown, contractSource: string, compositionSource: string) {
  if (typeof compositionSource !== 'string' || sha256(compositionSource) !== COMPOSED_WORKFLOW_CONTRACT_SHA256) fail('COMPOSITION_CONTRACT_DRIFT', '/contract');
  if(!Array.isArray(actions)||Object.getPrototypeOf(actions)!==Array.prototype||actions.length<1||actions.length>256)fail('ACTIONS','/actions');
  const descriptors=Object.getOwnPropertyDescriptors(actions);
  if(Reflect.ownKeys(descriptors).length!==actions.length+1)fail('ACTIONS','/actions');
  const stages=new Map<string,readonly ComposedPrecommitStage[]>(),checkedActions:CheckedComposedOperationAction[]=[];
  for(let i=0;i<actions.length;i++){
    const descriptor=descriptors[String(i)];if(!descriptor||!Object.hasOwn(descriptor,'value')||!descriptor.enumerable)fail('ACTIONS','/actions/'+i);
    const row=descriptor!.value;
    if(!row||typeof row!=='object'||![Object.prototype,null].includes(Object.getPrototypeOf(row)))fail('ACTIONS','/actions/'+i);
    const d=Object.getOwnPropertyDescriptors(row);
    if(Reflect.ownKeys(d).length!==2||!d.action||!d.absence_failures||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))fail('ACTIONS','/actions/'+i);
    const action=d.action!.value;assertCheckedComposedOperationAction(action);
    const precommit=composedPrecommitStages(action,d.absence_failures!.value);
    stages.set(action.bindings.selector,precommit);checkedActions.push(action);
  }
  return compileWorkflowBindingsCore(graph, boundary, fields, checkedActions, value, contractSource, true,stages);
}

function compileWorkflowBindingsCore(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields|null,
  actions: readonly (CheckedOperationAction|CheckedComposedOperationAction)[], value: unknown, contractSource: string, composed: boolean,precommitStages?:ReadonlyMap<string,readonly ComposedPrecommitStage[]>) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if(fields!==null)assertCompiledProjectFields(fields);
  if (typeof contractSource !== 'string' || sha256(contractSource) !== WORKFLOW_BINDING_CONTRACT_SHA256) fail('CONTRACT_DRIFT', '/contract');
  const certificate = createCompiledProjectCertificate(graph);
  if (boundary.certificate.graph_sha256 !== certificate.graph_sha256 || (fields!==null&&fields.certificate.graph_sha256 !== certificate.graph_sha256)) fail('CROSS_GRAPH', '/');
  if (fields!==null&&fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('VALUE_PROFILE', '/fields');
  const bindings = decodeWorkflowBindings(value), node = graph.nodes.find(n => n.selector === bindings.selector);
  if (node?.kind !== 'Workflow') return fail('ROOT', '/selector');
  const source = decodeWorkflowOccurrences(node.body.typed_contract);
  // The action array contains registered objects, not user JSON. Inspect its
  // own descriptors without cloning them or touching an accessor element.
  if (!Array.isArray(actions) || Object.getPrototypeOf(actions) !== Array.prototype) fail('ACTIONS', '/actions');
  const d: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(actions), length = d.length!.value;
  if (length < 1 || length > 256 || Reflect.ownKeys(d).length !== length + 1) fail('ACTIONS', '/actions');
  const providers = new Map<string, CheckedOperationAction|CheckedComposedOperationAction>();
  for (let i = 0; i < length; i++) {
    const p = d[String(i)];
    if (!p || !Object.hasOwn(p, 'value') || !p.enumerable) fail('ACTIONS', '/actions/' + i);
    const a = p!.value;
    if (composed) assertCheckedComposedOperationAction(a); else assertCheckedOperationAction(a);
    if (a.certificate.graph_sha256 !== certificate.graph_sha256 || a.boundary_sha256 !== boundary.boundary_sha256 || a.field_compilation_sha256 !== (fields?.compilation_sha256??null)) fail('STALE_ACTION', '/actions/' + i);
    if (providers.has(a.bindings.selector)) fail('DUPLICATE', '/actions');
    providers.set(a.bindings.selector, a);
  }
  exact([...providers.keys()], workflowOperationRefs(source), '/actions');
  exact(bindings.steps.map(s => s.step_id), source.steps.map(s => s.step_id), '/steps');
  exact(bindings.compensations.map(c => c.compensation_id), source.compensations.map(c => c.compensation_id), '/compensations');
  const checker = createTypedValueChecker(fields?.model.declarations??[], m => fail('TYPE', m));
  bindings.inputs.forEach(p => checker.checkType(p.type)); checker.checkType(bindings.result.type);
  const inputs = new Map(bindings.inputs.map(p => [p.name, p.type]));
  const eventInputs = new Map(bindings.event_inputs.map(p => [p.name, p.event_ref]));
  const evidence = (selector: string) => {
    const n = graph.nodes.find(n => n.selector === selector), e = boundary.domain_graph.nodes.find(n => n.selector === selector);
    if (!n || !e) return fail('SOURCE', selector);
    return {selector, kind: n.kind, source: e.source, body_sha256: sha256(canonicalJson(n.body))};
  };
  const events = bindings.event_inputs.map(p => {
    const event = [...providers.values()].flatMap(a => a.events).find(e => e.target === p.event_ref);
    if (!event) return fail('EVENT_INPUT', '/event_inputs/' + p.name);
    return {...p, contract: event.contract, source: evidence(p.event_ref)};
  });
  const infer = (v: WorkflowValueExpression, available: ReadonlyMap<string, TypedType>): TypedType => {
    if (v.op === 'input' || v.op === 'step-result') {
      const type = v.op === 'input' ? inputs.get(v.name) : available.get(v.step_id);
      if (!type) return fail('UNAVAILABLE_VALUE', v.op === 'input' ? '/inputs/' + v.name : '/steps/' + v.step_id);
      return checker.infer({op: 'path', root: 'value', properties: v.properties}, new Map([['value', type]]));
    }
    if (v.op === 'to_set') {const t = infer(v.value, available); return t.kind === 'list' ? {kind: 'set', element: t.element} : fail('TYPE', 'to_set requires a list');}
    return checker.infer(v, new Map());
  };
  const usedEvents = new Set<string>();
  const bindCall = (call: CallBinding, operation: string, available: ReadonlyMap<string, TypedType>, pointer: string) => {
    const action = providers.get(operation)!;
    if (action.action_sha256 !== call.action_sha256) fail('ACTION_IDENTITY', pointer);
    exact(call.arguments.map(a => a.parameter), action.bindings.inputs.map(p => p.name), pointer + '/arguments');
    exact(call.events.map(e => e.parameter), action.events.map(e => e.parameter), pointer + '/events');
    for (const p of action.bindings.inputs) {
      const arg = call.arguments.find(a => a.parameter === p.name)!;
      if (canonicalJson(infer(arg.value, available)) !== canonicalJson(p.type)) fail('ARGUMENT_TYPE', pointer + '/' + p.name);
    }
    for (const e of action.events) {
      const binding = call.events.find(b => b.parameter === e.parameter)!;
      if (eventInputs.get(binding.input) !== e.target) fail('EVENT_TYPE', pointer + '/' + e.parameter);
      usedEvents.add(binding.input);
    }
    return {operation_ref: operation, action_sha256: action.action_sha256, arguments: call.arguments, events: call.events,
      ...(composed?{precommit_stages:precommitStages!.get(operation)!}:{}),
      signature: {inputs: action.bindings.inputs, events: action.events.map(e => ({parameter: e.parameter, target: e.target, contract: e.contract, source: e.source})), result: action.bindings.result.type},
      failure_continuation: action.failure_continuation, source: action.source};
  };
  const available = new Map<string, TypedType>(), prefixes = new Map<string, ReadonlyMap<string, TypedType>>();
  const steps = source.steps.map(s => {
    const c = bindCall(bindings.steps.find(b => b.step_id === s.step_id)!, s.operation_ref, available, '/steps/' + s.step_id);
    available.set(s.step_id, c.signature.result); prefixes.set(s.step_id, new Map(available));
    return {step_id: s.step_id, ...c};
  });
  const compensations = source.compensations.map(c => ({compensation_id: c.compensation_id, for_step: c.for_step, depends_on: c.depends_on,
    ...bindCall(bindings.compensations.find(b => b.compensation_id === c.compensation_id)!, c.operation_ref, prefixes.get(c.for_step)!, '/compensations/' + c.compensation_id)}));
  exact([...usedEvents], bindings.event_inputs.map(p => p.name), '/event_inputs');
  if (canonicalJson(infer(bindings.result.value, available)) !== canonicalJson(bindings.result.type)) fail('RESULT_TYPE', '/result');
  const body = {schema_version: 'domainspec.checked-workflow-bindings/v1-candidate' as const, bindings, bindings_sha256: sha256(canonicalJson(bindings)),
    ...(composed ? {composition_contract_sha256: COMPOSED_WORKFLOW_CONTRACT_SHA256} : {}),
    contract_sha256: WORKFLOW_BINDING_CONTRACT_SHA256, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256??null,...(fields===null?{minimal_context_sha256:MINIMAL_VALUE_CONTEXT_SHA256}:{}),
    source: evidence(bindings.selector), occurrence_source: source, event_inputs: events, steps, compensations,
    execution: 'not-performed' as const, recovery_policy: 'not-selected' as const, authority_effect: 'none' as const};
  const result = freezeWorkflow({...body, workflow_sha256: sha256(canonicalJson(body))}); checked.add(result); return result;
}
