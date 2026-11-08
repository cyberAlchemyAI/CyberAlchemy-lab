import {sha256, canonicalJson} from '../input/source-manifest.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph, type FieldSpec} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {eventReferenceIdentity, type EventReferenceIdentity} from './event-reference-identity.js';
import type {ValueExpression} from '../typed-operation/contracts.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings, type WorkflowValueExpression} from '../typed-operation/workflow-bindings.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
import {createStructuredValueExpressionRenderer, type BoundValue} from './configured-value-expressions.js';
import {renderEventValueSupport, type EventSource} from './configured-event-source.js';

export const WORKFLOW_MATERIALIZATION_CONTRACT_SHA256 = '88d7a46aa61a28b371de4e468163a2c36c1da1d8ca83c14c77584fb2061a54a4';
const q = JSON.stringify;
const fail = (m: string): never => {throw new TypeError('WORKFLOW_MATERIALIZATION:' + m);};
function frozenLiteral(v: unknown): string {
  if (Array.isArray(v)) return 'Object.freeze([' + v.map(frozenLiteral).join(',') + '])';
  if (v && typeof v === 'object') return 'Object.freeze({' + Object.entries(v).map(([k, x]) => '[' + q(k) + ']:' + frozenLiteral(x)).join(',') + '})';
  return JSON.stringify(v);
}
function eventInputSource(c: EventSource, name: string, identities: ReadonlyMap<string, EventReferenceIdentity>): string {
  const typedReferences = [...identities.values()].some(identity => identity.scalar === 'UInt64');
  const fields = [...c.payload].sort((a, b) => a.field_id < b.field_id ? -1 : 1);
  const native = (f: FieldSpec, input: boolean): string => f.type_ref.kind === 'reference' ?
    (identities.get(f.type_ref.selector)!.scalar === 'UInt64' && input ? 'bigint|number|string' :
      'EventRef<' + q(f.type_ref.selector) + (typedReferences ? ',' + (identities.get(f.type_ref.selector)!.scalar === 'UInt64' ? 'bigint' : 'string') : '') + '>') :
    ({string: 'string', boolean: 'boolean', integer: input ? 'bigint|number|string' : 'bigint', decimal: 'number', timestamp: 'string', uuid: 'string'})[f.type_ref.name];
  const normalize = (f: FieldSpec, expr: string) => (f.type_ref.kind === 'reference' ? (identities.get(f.type_ref.selector)!.scalar === 'UInt64' ? 'eventUInt64' : 'eventText') :
    ({string: 'eventString', boolean: 'eventBoolean', integer: 'eventInteger', decimal: 'eventDecimal', timestamp: 'eventText', uuid: 'eventText'})[f.type_ref.name]) + '(' + expr + ')';
  const generated = c.occurred_at_policy === 'generated', id = q(c.occurrence_id.field_id);
  const shape = (input: boolean) => 'Readonly<{occurrence:Readonly<{' + id + ':' + native(c.occurrence_id, input) + '}>;' +
    (generated ? '' : 'occurredAt:string;') + 'payload:Readonly<{' + fields.map(f => 'readonly ' + q(f.field_id) + (f.required ? '' : '?') + ':' + native(f, input)).join(';') + '}>}>';
  const names = generated ? ['occurrence', 'payload'] : ['occurrence', 'occurredAt', 'payload'];
  return 'type ' + name + 'Input=' + shape(true) + ';\ntype ' + name + '=' + shape(false) + ';\n' +
    'const capture' + name + '=(input:unknown):' + name + '=>{\n' +
    '  const d=eventData(input,' + q(names) + ',' + q(names) + ');\n' +
    '  const o=eventData(d.occurrence!.value,[' + id + '],[' + id + ']);\n' +
    '  const p=eventData(d.payload!.value,' + q(fields.map(f => f.field_id)) + ',' + q(fields.filter(f => f.required).map(f => f.field_id)) + ');\n' +
    '  return Object.freeze({occurrence:Object.freeze({[' + id + ']:' + normalize(c.occurrence_id, 'o[' + id + ']!.value') + '}),' +
    (generated ? '' : 'occurredAt:eventText(d.occurredAt!.value),') + 'payload:Object.freeze({' +
    fields.map(f => {
      const value = '[' + q(f.field_id) + ']:' + normalize(f, 'p[' + q(f.field_id) + ']!.value');
      return f.required ? value : '...(Object.hasOwn(p,' + q(f.field_id) + ')?{' + value + '}:{})';
    }).join(',') + '})});\n};\n';
}
const captureSupport = 'const materialFail=():never=>{throw new TypeError("WORKFLOW_VALUE");};\n' +
  'const captureData=(input:unknown):unknown=>{\n  let count=0;\n' +
  '  const copy=(v:unknown,depth:number):unknown=>{\n' +
  '    if(++count>20000||depth>64)return materialFail();\n' +
  '    if(v===null||typeof v==="string"||typeof v==="boolean"||typeof v==="bigint"||typeof v==="number"&&Number.isFinite(v))return v;\n' +
  '    if(!v||typeof v!=="object")return materialFail();\n' +
  '    const array=Array.isArray(v),proto=Object.getPrototypeOf(v);\n' +
  '    if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)return materialFail();\n' +
  '    const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);if(keys.length>2048)return materialFail();\n' +
  '    if(array){const length=d.length!.value;if(length>1024||keys.length!==length+1)return materialFail();const result:unknown[]=[];for(let i=0;i<length;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,"value")||!p.enumerable)return materialFail();result.push(copy(p.value,depth+1));}return Object.freeze(result);}\n' +
  '    const result:Record<string,unknown>=Object.create(null);\n' +
  '    for(const k of keys){const p=d[k as string];if(typeof k!=="string"||!p||!Object.hasOwn(p,"value")||!p.enumerable)return materialFail();result[k]=copy(p.value,depth+1);}return Object.freeze(result);\n' +
  '  };return copy(input,0);\n};\n';

/** Standalone native pure boundary module. No dispatch, clocks or type interpreter. */
export function renderWorkflowMaterialization(graph: CompiledProjectGraph, workflow: CheckedWorkflowBindings, fields: CompiledProjectFields|null, contractSource: string) {
  assertCompiledProjectSnapshot(graph); assertCheckedWorkflowBindings(workflow); if(fields!==null)assertCompiledProjectFields(fields);
  if (canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(workflow.certificate)) return fail('source certificate mismatch');
  if ((fields!==null&&(fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || fields.certificate.graph_sha256 !== workflow.certificate.graph_sha256)) ||
    (fields?.compilation_sha256??null) !== workflow.field_compilation_sha256) return fail('stale or incompatible fields');
  if (typeof contractSource !== 'string' || sha256(contractSource) !== WORKFLOW_MATERIALIZATION_CONTRACT_SHA256) return fail('contract drift');
  const values = createStructuredValueRenderer(fields?.model??null, fail), b = workflow.bindings;
  let sequence = 0;
  const lower = createStructuredValueExpressionRenderer(values, fields?.model??null, () => 'projection' + sequence++, fail);
  const convert = (v: WorkflowValueExpression): ValueExpression => {
    if (v.op === 'input') return {op: 'path', root: 'input:' + v.name, properties: v.properties};
    if (v.op === 'step-result') return {op: 'path', root: 'result:' + v.step_id, properties: v.properties};
    if (v.op === 'to_set') return {op: 'to_set', value: convert(v.value)};
    return v;
  };
  const inputs = b.inputs.map(p => ({...p, value: values.ensure(p.type)}));
  const eventTypes = workflow.event_inputs.map((e, i) => ({...e, native: 'E' + i}));
  const resultTypes = workflow.steps.map(s => ({...s, value: values.ensure(s.signature.result)}));
  const resultValue = values.ensure(b.result.type);
  const baseScope = new Map<string, BoundValue>(inputs.map(p => ['input:' + p.name, {type: p.type, code: 'input[' + q(p.name) + ']'}]));
  const scope = (count: number) => {
    const s = new Map(baseScope);
    for (const r of resultTypes.slice(0, count)) s.set('result:' + r.step_id, {type: r.signature.result, code: '(r[' + q(r.step_id) + '] as ' + r.value.native + ')'});
    return s;
  };
  const shape = (native: boolean) => [...inputs.map(p => 'readonly ' + q(p.name) + ':' + p.value[native ? 'native' : 'input']),
    ...eventTypes.map(e => 'readonly ' + q(e.name) + ':' + e.native + (native ? '' : 'Input'))].join(';');
  const names = [...inputs.map(p => p.name), ...eventTypes.map(e => e.name)];
  const declarations = 'export type WorkflowInput=Readonly<{' + shape(false) + '}>;\nexport type CapturedInput=Readonly<{' + shape(true) + '}>;\n' +
    'export type StepId=' + workflow.steps.map(s => q(s.step_id)).join('|') + ';\n' +
    'export type CapturedResult=' + resultTypes.map(r => 'Readonly<{step_id:' + q(r.step_id) + ';action_sha256:' + q(r.action_sha256) + ';value:' + r.value.native + '}>').join('|') + ';\n' +
    'const inputs=new WeakSet<object>();const resultInputs=new WeakMap<object,CapturedInput>();\n' +
    'const assertInput=(input:CapturedInput):void=>{if(!input||typeof input!=="object"||!inputs.has(input))materialFail();};\n' +
    'export const capture=(value:WorkflowInput):CapturedInput=>{\n' +
    '  const d=ruleData(captureData(value),' + q(names) + ');if(Object.keys(d).length!==' + names.length + ')return materialFail();\n' +
    '  const input=Object.freeze({' + [...inputs.map(p => '[' + q(p.name) + ']:' + p.value.protocol + '.normalize(d[' + q(p.name) + ']!.value)'),
      ...eventTypes.map(e => '[' + q(e.name) + ']:capture' + e.native + '(d[' + q(e.name) + ']!.value)')].join(',') + '});inputs.add(input);return input;\n};\n' +
    'export const captureResult=(input:CapturedInput,stepId:StepId,raw:unknown):CapturedResult=>{\n  assertInput(input);\n' +
    resultTypes.map(r => '  if(stepId===' + q(r.step_id) + '){const value=' + r.value.protocol + '.normalize(captureData(raw));const row=Object.freeze({step_id:' + q(r.step_id) + ' as const,action_sha256:' + q(r.action_sha256) + ' as const,value});resultInputs.set(row,input);return row;}\n').join('') +
    '  return materialFail();\n};\n' +
    'const prefix=(input:CapturedInput,results:readonly CapturedResult[],min:number,max:number):Record<string,unknown>=>{\n' +
    '  assertInput(input);if(!Array.isArray(results)||Object.getPrototypeOf(results)!==Array.prototype)return materialFail();\n' +
    '  const d:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(results),length=d.length!.value;\n' +
    '  if(length<min||length>max||Reflect.ownKeys(d).length!==length+1)return materialFail();\n' +
    '  const ids=' + q(workflow.steps.map(s => s.step_id)) + ',r:Record<string,unknown>=Object.create(null);\n' +
    '  for(let i=0;i<length;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,"value")||!p.enumerable)return materialFail();const row=p.value;if(!row||typeof row!=="object"||resultInputs.get(row)!==input||row.step_id!==ids[i])return materialFail();r[row.step_id]=row.value;}return r;\n};\n';
  type Call = CheckedWorkflowBindings['steps'][number];
  const call = (c: Call, count: number, compensation: boolean): string => {
    const env = scope(count), args = c.arguments.map(a => ({...a, value: lower(convert(a.value), env)}));
    const readsResults = args.some(argument => argument.value.code.includes('(r['));
    const output = [...args.map(a => 'readonly ' + q(a.parameter) + ':' + values.ensure(a.value.type).native),
      ...c.events.map(e => 'readonly ' + q(e.parameter) + ':' + (eventTypes.find(t => t.name === e.input) ?? fail('missing Event input')).native)].join(';');
    return 'Object.freeze({operation_ref:' + q(c.operation_ref) + ',action_sha256:' + q(c.action_sha256) + ',arguments:(input:CapturedInput,results:readonly CapturedResult[]):Readonly<{' + output + '}>=>{\n' +
      '  ' + (readsResults ? 'const r=' : '') + 'prefix(input,results,' + count + ',' + (compensation ? workflow.steps.length : count) + ');\n' +
      '  return Object.freeze({' + [...args.map(a => '[' + q(a.parameter) + ']:' + a.value.code),
        ...c.events.map(e => '[' + q(e.parameter) + ']:input[' + q(e.input) + ']')].join(',') + '});\n}})';
  };
  const steps = 'export const steps=Object.freeze({' + workflow.steps.map((s, i) => '[' + q(s.step_id) + ']:' + call(s, i, false)).join(',') + '});\n';
  const compensations = 'export const compensations=Object.freeze({' + workflow.compensations.map(c => '[' + q(c.compensation_id) + ']:' +
    call({...c, step_id: c.for_step}, workflow.steps.findIndex(s => s.step_id === c.for_step) + 1, true)).join(',') + '});\n';
  const final = lower(convert(b.result.value), scope(workflow.steps.length));
  const result = 'export const result=(input:CapturedInput,results:readonly CapturedResult[]):' + resultValue.native + '=>{\n' +
    '  ' + (final.code.includes('(r[') ? 'const r=' : '') + 'prefix(input,results,' + workflow.steps.length + ',' + workflow.steps.length + ');\n' +
    '  return ' + resultValue.protocol + '.normalize(' + final.code + ');\n};\n';
  const descriptor = freezeWorkflow({schema_version: 'domainspec.workflow-materialization-descriptor/v1-candidate',
    workflow_sha256: workflow.workflow_sha256, field_compilation_sha256: fields?.compilation_sha256??null,
    contract_sha256: WORKFLOW_MATERIALIZATION_CONTRACT_SHA256, selector: b.selector,
    steps: workflow.steps.map(s => ({step_id: s.step_id, operation_ref: s.operation_ref, action_sha256: s.action_sha256})),
    compensations: workflow.compensations.map(c => ({compensation_id: c.compensation_id, for_step: c.for_step, operation_ref: c.operation_ref, action_sha256: c.action_sha256})),
    effect_contract: 'pure-typed-materialization', invariant_execution: 'not-performed', commit_evidence: 'not-established',
    event_construction: 'not-performed', authority_effect: 'none'});
  const eventFields = eventTypes.flatMap(event => [event.contract.occurrence_id, ...event.contract.payload]);
  const referenceSelectors = [...new Set(eventFields.flatMap(field => field.type_ref.kind === 'reference' ? [field.type_ref.selector] : []))];
  const identities = new Map(referenceSelectors.map(selector => [selector, eventReferenceIdentity(graph, selector, fail)]));
  const content = values.source().replaceAll('RULE_INPUT', 'WORKFLOW_VALUE') + (eventTypes.length ? renderEventValueSupport(eventFields, identities) : '') +
    eventTypes.map(e => eventInputSource(e.contract, e.native, identities)).join('') + captureSupport + declarations + steps + compensations + result +
    'export const descriptor=' + frozenLiteral(descriptor) + ';\n';
  return freezeWorkflow({content, sha256: sha256(content), descriptor, descriptor_sha256: sha256(canonicalJson(descriptor))});
}
