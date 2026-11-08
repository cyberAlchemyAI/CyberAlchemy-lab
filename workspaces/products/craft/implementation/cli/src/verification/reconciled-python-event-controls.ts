import type {CompiledProjectGraph} from '../input/project-model.js';
import {getPythonEventVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createEventSemanticCases} from './reconciled-event-controls.js';

export function createPythonEventControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  const module = getPythonEventVerificationContext(plan).find(m => m.selector === node.selector);
  if (!module || module.descriptor.contract_sha256 !== sha256(canonicalJson(node.body))) throw new TypeError('DS_PYTHON_EVENT_CONTROLS:source binding');
  const binding = {id: 'case-0', mode: 'event-descriptor', format: 'string' as const, values: [], expected: {kind: 'value' as const, value: canonicalJson(module.descriptor)}};
  const referenceScalars = new Map(module.reference_imports.map(reference => [reference.selector, reference.identity.scalar] as const));
  const shared = createEventSemanticCases(node, binding, referenceScalars);
  if (shared.state !== 'ready') return shared;
  const baseline = shared.cases.find(c => c.mode === 'event')!;
  const cases = [...shared.cases];
  const extra = (target: 'occurrence' | 'payload', field: string, kind: string, value: string, valid: boolean) => {
    const recipe = JSON.parse(baseline.values[0]!), expected = JSON.parse((baseline.expected as {value: string}).value);
    recipe.input[target][field] = {kind, value};
    if (valid) expected.result.values[0][target][field] = {kind: 'number', value: String(Number(value))};
    else {expected.result = {kind: 'error', name: 'TypeError', message: 'EVENT_INPUT', same_clock_error: false}; expected.clock_calls = 0;}
    cases.push({id: 'case-' + cases.length, mode: 'event-native-carrier', format: 'string', values: [canonicalJson(recipe)], expected: {kind: 'value', value: canonicalJson(expected)}});
  };
  for (const [target, fields] of [['occurrence', [module.descriptor.occurrence_id]], ['payload', module.descriptor.payload]] as const) for (const f of fields) {
    if (f.type_ref.kind !== 'primitive') continue;
    if (f.type_ref.name === 'decimal') for (const value of ['0', '1', '-1', '9007199254740993', (2n ** 1024n).toString()]) extra(target, f.field_id, 'python-int', value, Number.isFinite(Number(value)));
    if (f.type_ref.name === 'integer') for (const value of ['0', '1']) extra(target, f.field_id, 'python-float', value, false);
  }
  if (cases.length > 4096 || Buffer.byteLength(canonicalJson(cases)) > 8388608) return {selector: node.selector, kind: 'Event' as const, state: 'not_evaluable' as const, reason: 'bounded native Event case capacity exceeded'};
  const references = Object.fromEntries(module.descriptor.references.map(r => {
    const target = graph.nodes.find(n => n.selector === r.selector)!;
    if (!target || target.kind !== r.kind || sha256(canonicalJson(target.body)) !== r.body_sha256) throw new TypeError('DS_PYTHON_EVENT_CONTROLS:reference binding');
    return [r.selector, {kind: target.kind, body: target.body}];
  }));
  return {...shared, cases, adapter: 'python-event' as const, module, source: node.body, references};
}
