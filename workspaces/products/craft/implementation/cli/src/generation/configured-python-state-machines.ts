import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertStateMachineData, checkTypedStateMachine, decodeTypedStateMachineContract, freezeStateMachine, stateMachineFail, stateMachineObject, STATE_MACHINE_CONTRACT_SHA256, type TypedStateMachineContract} from '../typed-backend/state-machine.js';
import type {TypedRuleContract} from '../typed-operation/contracts.js';
import {pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {planConfiguredPythonRules, PYTHON_STRUCTURED_RULE_VERSION, PYTHON_RULE_SOURCE_DIGESTS, type PythonStructuredRuleSources} from './configured-python-rules.js';
import {STRUCTURED_RULE_CONTRACT_SHA256} from './configured-rules.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {renderPythonFactSupport} from './configured-python-fact-source.js';
import {renderPythonStateMachine, renderPythonStateMachineBinding} from './configured-python-state-machine-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_STATE_MACHINE_VERSION = 'domainspec.configured-python-state-machines-selection/v1-candidate';
export interface PythonStateMachineSelection {
  readonly schema_version: typeof PYTHON_STATE_MACHINE_VERSION;
  readonly language: 'python';
  readonly module_root: string;
  readonly roots: readonly string[];
  readonly boundary_sha256: string;
  readonly field_compilation_sha256: string | null;
}
export interface PythonStateMachineSources {readonly state_machine_contract: string; readonly rules: PythonStructuredRuleSources;}
const fail = stateMachineFail;

/** Plans native enum transition functions, not Event construction or execution. */
export function planConfiguredPythonStateMachines(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: PythonStateMachineSelection, sources: PythonStateMachineSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields !== null) assertCompiledProjectFields(fields);
  assertStateMachineData(selection); assertStateMachineData(sources);
  stateMachineObject(selection, ['schema_version', 'language', 'module_root', 'roots', 'boundary_sha256', 'field_compilation_sha256']);
  stateMachineObject(sources, ['state_machine_contract', 'rules']);
  stateMachineObject(sources.rules, [...Object.keys(PYTHON_RULE_SOURCE_DIGESTS), 'structured_contract', 'field_contract']);
  if (selection.schema_version !== PYTHON_STATE_MACHINE_VERSION || selection.language !== 'python') fail('unsupported Python generator selection');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings', 'math', 're'].includes(segments[0]!)) fail('module root shadows standard library');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 128 || new Set(selection.roots).size !== selection.roots.length) fail('nonempty unique roots required');
  for (const selector of selection.roots) {if (typeof selector !== 'string' || selector.split(':').length !== 2) fail('selector required'); selector.split(':').forEach(pythonPortableIdentifier);}
  const root = segments.map(pythonSnake).join('/'), certificate = createCompiledProjectCertificate(graph);
  if (boundary.certificate.graph_sha256 !== certificate.graph_sha256 || selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null) || fields && (fields.certificate.graph_sha256 !== certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION)) fail('stale or cross-graph selection');
  if (typeof sources.state_machine_contract !== 'string' || sha256(sources.state_machine_contract) !== STATE_MACHINE_CONTRACT_SHA256) fail('source drift:state_machine_contract');
  const ruleDigests = {...PYTHON_RULE_SOURCE_DIGESTS, structured_contract: STRUCTURED_RULE_CONTRACT_SHA256, field_contract: EXACT_FIELD_CONTRACT_SHA256};
  // Guardless machines still pin the selected source meaning; no fabricated Rule.
  for (const key of Object.keys(ruleDigests) as (keyof typeof ruleDigests)[]) if (typeof sources.rules[key] !== 'string' || sha256(sources.rules[key]) !== ruleDigests[key]) fail('source drift:' + key);
  const cell = JSON.parse(sources.rules.configuration).types.find((t: {kind: string}) => t.kind === 'State Machine');
  if (cell?.role !== 'domain/state-machines' || canonicalJson(cell.blocked_by) !== '["DSR-011","DSR-016"]') fail('State Machine configuration');
  const overlay = JSON.parse(sources.rules.python).representation_overlays.find((p: {contract_id: string}) => p.contract_id === 'state-machine.profile-representation');
  if (overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === 'python.bound-state-machine/v1')?.form_id !== 'python.enum-transition-function') fail('State Machine profile');
  const roots = [...selection.roots].sort(), contracts = new Map<string, TypedStateMachineContract>();
  const nodes = graph.nodes.map(n => ({selector: n.selector, kind: n.kind, rule: n.kind === 'Rule' && n.body.typed_contract ? n.body.typed_contract as TypedRuleContract : null}));
  for (const selector of roots) {
    const node = graph.nodes.find(n => n.selector === selector);
    if (node?.kind !== 'State Machine' || !node.body.typed_contract) fail('versioned State Machine required; migrate legacy explicitly:' + selector);
    const c = decodeTypedStateMachineContract(node!.body.typed_contract); checkTypedStateMachine(c, fields?.model.declarations ?? [], nodes); contracts.set(selector, c);
  }
  const ruleRoots = [...new Set([...contracts.values()].flatMap(c => c.transitions.flatMap(t => t.guard ? [t.guard.selector] : [])))].sort();
  const rulesFor = (roots: string[]) => roots.length ? planConfiguredPythonRules(graph, {schema_version: PYTHON_STRUCTURED_RULE_VERSION, language: 'python', module_root: selection.module_root, roots}, sources.rules) : null;
  const rulePlan = rulesFor(ruleRoots), artifacts = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string) => {
    const prior = artifacts.get(relative_path); if (prior && prior.content !== content) fail('artifact collision:' + relative_path);
    const a = {relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)}; artifacts.set(relative_path, a); return a;
  };
  rulePlan?.artifacts.forEach(a => add(a.relative_path, a.content));
  const support = [add(root + '/runtime/values.py', renderPythonValueSupport()), add(root + '/runtime/facts.py', renderPythonFactSupport())];
  const evidence = (selector: string) => {
    const node = graph.nodes.find(n => n.selector === selector) ?? fail('missing node'), bound = boundary.domain_graph.nodes.find(n => n.selector === selector) ?? fail('unbound node');
    return {selector, kind: node.kind, source: bound.source, body_sha256: sha256(canonicalJson(node.body))};
  };
  const modules = roots.map(selector => {
    const c = contracts.get(selector)!, [feature, node] = selector.split(':') as [string, string];
    const relative_path = `${root}/features/${pythonSnake(feature)}/src/domain/state_machines/${pythonSnake(node)}.py`, provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py');
    const ownRoots = [...new Set(c.transitions.flatMap(t => t.guard ? [t.guard.selector] : []))].sort(), ownRules = canonicalJson(ownRoots) === canonicalJson(ruleRoots) ? rulePlan : rulesFor(ownRoots);
    const imports = ownRoots.map((selector, i) => {
      const m = rulePlan?.modules.find(m => m.selector === selector) ?? fail('missing Rule module');
      return {selector, module: pythonRelativeModule(provider_path, m.relative_path), symbol: m.callable, local: '_condition' + i};
    });
    const runtime = pythonRelativeModule(provider_path, root + '/runtime/values.py').replace(/\.values$/, '');
    const provider = add(provider_path, renderPythonStateMachine(c, fields?.model ?? null, imports, runtime)), callable = 'transition_' + pythonSnake(node);
    const events = [...new Set(c.transitions.flatMap(t => [t.trigger_event_ref, ...t.output_intents.map(o => o.event_ref)]))].sort();
    const body = {schema_version: 'domainspec.generated-python-state-machine-descriptor/v1-candidate', protocol_id: 'python.bound-state-machine/v1', selector, source: evidence(selector), contract: c, contract_sha256: sha256(canonicalJson(c)), definition_sha256: STATE_MACHINE_CONTRACT_SHA256,
      event_dependencies: events.map(evidence), rule_plan_sha256: ownRules?.plan_sha256 ?? null, rule_dependencies: imports.map(i => {const m = rulePlan!.modules.find(m => m.selector === i.selector)!; return {selector: i.selector, path: m.relative_path, sha256: artifacts.get(m.relative_path)!.sha256};}),
      field_model_sha256: fields?.model.model_sha256 ?? null, return_semantics: 'transition-or-rejection', effect_contract: 'none', trigger_semantics: 'explicit-event-input-symbol', output_semantics: 'ordered-unexecuted-intents',
      runtime: support.map(a => ({id: a.relative_path.split('/').at(-1)!, sha256: a.sha256})), provider: {sha256: provider.sha256}, authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))}, provider_import = pythonRelativeModule(relative_path, provider_path);
    add(relative_path, renderPythonStateMachineBinding(provider_import, callable, descriptor));
    return {selector, relative_path, provider_path, provider_import, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), callable, imports, descriptor};
  });
  for (const file of [...artifacts.keys()]) {const parts = file.split('/'); for (let i = 1; i < parts.length; i++) {const init = parts.slice(0, i).join('/') + '/__init__.py'; if (!artifacts.has(init)) add(init, '');}}
  const body = {schema_version: 'domainspec.configured-python-state-machines-plan/v1-candidate', selection: {...selection, roots}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    source_digests: {contract: STATE_MACHINE_CONTRACT_SHA256, ...ruleDigests}, rule_plan: rulePlan, modules, artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none'};
  return freezeStateMachine({...body, plan_sha256: sha256(canonicalJson(body))});
}
