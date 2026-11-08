import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCheckedOperationAction, type CheckedOperationAction} from '../typed-operation/action-bindings.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {planConfiguredPythonRules, PYTHON_STRUCTURED_RULE_VERSION, type PythonStructuredRuleSources} from './configured-python-rules.js';
import {planConfiguredPythonFactories, PYTHON_FACTORY_VERSION, PYTHON_REFERENCE_FACTORY_VERSION} from './configured-python-factories.js';
import {STRUCTURED_FACTORY_CONTRACT_SHA256, REFERENCE_FIELD_FACTORY_CONTRACT_SHA256, type FactoryBinding} from './configured-factories.js';
import {planConfiguredPythonAlgebraicEnums, PYTHON_ALGEBRAIC_ENUM_VERSION} from './configured-python-algebraic-enums.js';
import {planConfiguredPythonEvents, PYTHON_EVENT_VERSION, type PythonEventSources} from './configured-python-events.js';
import {EVENT_VALUE_PROFILE, EVENT_CONTRACT_SHA256} from './configured-events.js';
import {OPERATION_GENERATION_CONTRACT_SHA256} from './configured-operations.js';
import {pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {renderPythonOperation, renderPythonOperationBinding} from './configured-python-operation-source.js';
import {MINIMAL_VALUE_CONTEXT_SHA256} from './reconciled-sources.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_OPERATION_VERSION = 'domainspec.configured-python-operations-selection/v1-candidate';
export interface PythonOperationSelection {
  readonly schema_version: typeof PYTHON_OPERATION_VERSION;
  readonly language: 'python';
  readonly module_root: string;
  readonly actions: readonly CheckedOperationAction[];
  readonly factories: readonly FactoryBinding[];
}
export interface PythonOperationSources {
  readonly operation_contract: string;
  readonly factory_contract: string;
  readonly reference_contract?: string;
  readonly rules: PythonStructuredRuleSources;
  readonly events: PythonEventSources;
}
const fail = (reason: string): never => {throw Error('DS_PYTHON_OPERATION:' + reason);};
const freeze = <T>(v: T): T => {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);} return v;};
function closed(v: unknown, keys: readonly string[]) {
  if (!v || typeof v !== 'object' || Array.isArray(v) || ![Object.prototype, null].includes(Object.getPrototypeOf(v))) fail('plain object required');
  const d = Object.getOwnPropertyDescriptors(v);
  if (Reflect.ownKeys(d).length !== keys.length || Reflect.ownKeys(d).some(k => typeof k !== 'string' || !keys.includes(k)) || Object.values(d).some(p => !Object.hasOwn(p, 'value') || !p.enumerable)) fail('closed inert object required');
}
function dense(v: unknown, min: number): unknown[] {
  if (!Array.isArray(v) || Object.getPrototypeOf(v) !== Array.prototype) return fail('plain array required');
  const d: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(v), length = d.length!.value;
  if (length < min || length > 128 || Reflect.ownKeys(d).length !== length + 1) fail('bounded dense array required');
  return Array.from({length}, (_, i) => {const p = d[String(i)]; if (!p || !Object.hasOwn(p, 'value') || !p.enumerable) return fail('inert array required'); return p.value;});
}

/** Source-only native Python orchestration from already checked action meaning.
 * The explicit transaction provider still owns atomicity/isolation/durability. */
export function planConfiguredPythonOperations(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: PythonOperationSelection, sources: PythonOperationSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields !== null) assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'module_root', 'actions', 'factories']);
  closed(sources, ['operation_contract', 'factory_contract', 'rules', 'events', ...(Object.hasOwn(sources, 'reference_contract') ? ['reference_contract'] : [])]);
  closed(sources.rules, ['configuration', 'base', 'python', 'rule_contract', 'collection_contract', 'predicate_contract', 'numeric_contract', 'exact_contract', 'literal_contract', 'structured_contract', 'field_contract']);
  closed(sources.events, ['configuration', 'base', 'python', 'event_contract']);
  if (selection.schema_version !== PYTHON_OPERATION_VERSION || selection.language !== 'python') fail('unsupported selection');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings', 'math', 're', 'asyncio', 'concurrent', 'socket', 'selectors', 'signal', 'threading', 'subprocess', 'logging', 'inspect'].includes(segments[0]!)) fail('module root shadows standard library');
  const root = segments.map(pythonSnake).join('/');
  for (const [name, expected] of Object.entries({operation_contract: OPERATION_GENERATION_CONTRACT_SHA256, factory_contract: STRUCTURED_FACTORY_CONTRACT_SHA256})) {
    const source = sources[name as 'operation_contract' | 'factory_contract']; if (typeof source !== 'string' || sha256(source) !== expected) fail('source drift:' + name);
  }
  if (sources.reference_contract !== undefined && (typeof sources.reference_contract !== 'string' || sha256(sources.reference_contract) !== REFERENCE_FIELD_FACTORY_CONTRACT_SHA256)) fail('source drift:reference_contract');
  for (const key of ['configuration', 'base', 'python'] as const) if (sources.rules[key] !== sources.events[key]) fail('dependency source mismatch:' + key);
  if (typeof sources.events.event_contract !== 'string' || sha256(sources.events.event_contract) !== EVENT_CONTRACT_SHA256) fail('source drift:event_contract');
  const certificate = createCompiledProjectCertificate(graph);
  if (boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields && fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('cross-graph context');
  const actions = dense(selection.actions, 1).map(action => {
    assertCheckedOperationAction(action);
    if (action.certificate.graph_sha256 !== certificate.graph_sha256 || action.boundary_sha256 !== boundary.boundary_sha256 || action.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null)) fail('stale or cross-graph action');
    action.bindings.selector.split(':').forEach(pythonPortableIdentifier); return action;
  }).sort((a, b) => a.bindings.selector < b.bindings.selector ? -1 : 1);
  if (new Set(actions.map(a => a.bindings.selector)).size !== actions.length) fail('duplicate action');
  const ruleRoots = [...new Set(actions.flatMap(a => a.guards.map(g => g.selector)))].sort();
  const rulesFor = (roots: string[]) => planConfiguredPythonRules(graph, {schema_version: PYTHON_STRUCTURED_RULE_VERSION, language: 'python', module_root: selection.module_root, roots}, sources.rules);
  const rules = rulesFor(ruleRoots), enumOnly = fields !== null && fields.model.declarations.every(d => d.kind === 'Enum');
  if ((!fields || enumOnly) && dense(selection.factories, 0).length) fail('no factories in absent or Enum-only context');
  const references = !!fields?.model.bindings.length;
  if (references && sources.reference_contract === undefined) fail('reference factory contract required');
  const factories = fields && !enumOnly ? planConfiguredPythonFactories(graph, fields, {schema_version: references ? PYTHON_REFERENCE_FACTORY_VERSION : PYTHON_FACTORY_VERSION, language: 'python', module_root: selection.module_root, field_compilation_sha256: fields.compilation_sha256, factories: selection.factories}, {...sources.rules, factory_contract: sources.factory_contract, ...(references ? {reference_contract: sources.reference_contract!} : {})}) : null;
  const algebraic = fields && enumOnly ? planConfiguredPythonAlgebraicEnums(graph, fields, {schema_version: PYTHON_ALGEBRAIC_ENUM_VERSION, language: 'python', module_root: selection.module_root, field_compilation_sha256: fields.compilation_sha256}, {configuration: sources.rules.configuration, base: sources.rules.base, python: sources.rules.python, field_contract: sources.rules.field_contract}) : null;
  const eventRoots = [...new Set(actions.flatMap(a => a.events.map(e => e.target)))].sort();
  const eventsFor = (roots: string[]) => roots.length ? planConfiguredPythonEvents(graph, boundary, {schema_version: PYTHON_EVENT_VERSION, language: 'python', module_root: selection.module_root, value_profile: EVENT_VALUE_PROFILE, boundary_sha256: boundary.boundary_sha256, roots}, sources.events) : null;
  const events = eventsFor(eventRoots);
  const cell = JSON.parse(sources.rules.configuration).types.find((t: {kind: string}) => t.kind === 'Operation');
  if (cell?.role !== 'application/operations' || canonicalJson(cell.blocked_by) !== '["DSR-011"]') fail('Operation configuration');
  const overlay = JSON.parse(sources.rules.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'operation.profile-representation');
  if (overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === 'python.bound-operation/v1')?.form_id !== 'python.bound-operation-function') fail('Operation profile');
  const artifacts = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string) => {
    const prior = artifacts.get(relative_path); if (prior && prior.content !== content) fail('artifact collision:' + relative_path);
    const a = {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}; artifacts.set(relative_path, a); return a;
  };
  for (const a of [...rules.artifacts, ...(factories?.artifacts ?? algebraic?.artifacts ?? []), ...(events?.artifacts ?? [])]) add(a.relative_path, a.content);
  const target = (selector: string): string => {
    const d = fields?.model.declarations.find(d => d.selector === selector) ?? fail('missing value declaration');
    if (d.kind !== 'Enum') return factories?.modules.find(m => m.selector === selector)?.relative_path ?? fail('missing factory');
    const [feature, node] = selector.split(':') as [string, string];
    const file = `${root}/features/${pythonSnake(feature)}/src/domain/enums/${pythonSnake(node)}${d.contract.variants.some(v => v.payload !== null) ? '_sum' : ''}.py`;
    if (!artifacts.has(file)) fail('missing Enum component'); return file;
  };
  const modules = actions.map(action => {
    const ownRuleRoots = [...new Set(action.guards.map(g => g.selector))].sort(), ownEventRoots = [...new Set(action.events.map(e => e.target))].sort();
    const ownRules = canonicalJson(ownRuleRoots) === canonicalJson(ruleRoots) ? rules : rulesFor(ownRuleRoots), ownEvents = canonicalJson(ownEventRoots) === canonicalJson(eventRoots) ? events : eventsFor(ownEventRoots);
    const selector = action.bindings.selector, [feature, node] = selector.split(':') as [string, string];
    const relative_path = `${root}/features/${pythonSnake(feature)}/src/${cell.role}/${pythonSnake(node)}.py`, provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py'), callable = 'operation_' + pythonSnake(node);
    const rule_imports = action.guards.map((g, i) => {const m = rules.modules.find(m => m.selector === g.selector) ?? fail('missing Rule'); return {selector: g.selector, module: pythonRelativeModule(provider_path, m.relative_path), symbol: m.callable, local: '_guard' + i};});
    const event_imports = ownEventRoots.map((selector, i) => {const m = events?.modules.find(m => m.selector === selector) ?? fail('missing Event'); return {selector, module: pythonRelativeModule(provider_path, m.relative_path), symbol: m.callable, local: '_make_event' + i};});
    const runtime = pythonRelativeModule(provider_path, `${root}/runtime/values.py`).replace(/\.values$/, '');
    const provider = add(provider_path, renderPythonOperation(action, fields?.model ?? null, provider_path, target, rule_imports, event_imports, runtime));
    const body = {schema_version: 'domainspec.generated-python-operation-descriptor/v1-candidate', protocol_id: 'python.bound-operation/v1', selector, source: action.source, action_sha256: action.action_sha256, bindings: action.bindings,
      source_compatibility: 'explicit-action-bindings-not-legacy-typed-v1', value_profile: EXACT_UINT64_PROFILE, return_semantics: 'awaited-explicit-outcome', effect_contract: 'state-and-outbox', continuation: 'awaited-settlement',
      rule_plan_sha256: ownRules.plan_sha256, factory_plan_sha256: factories?.plan_sha256 ?? null, event_plan_sha256: ownEvents?.plan_sha256 ?? null, field_model_sha256: fields?.model.model_sha256 ?? null,
      ...(factories ? {} : {minimal_context_sha256: MINIMAL_VALUE_CONTEXT_SHA256, ...(algebraic ? {algebraic_plan_sha256: algebraic.plan_sha256} : {})}),
      execution_obligations: action.execution_obligations, transaction_provider: 'explicit-external-dependency', provider_durability_claim: false, publication: false, primary_callable_count: 1, provider: {sha256: provider.sha256}, authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))}, provider_import = pythonRelativeModule(relative_path, provider_path);
    add(relative_path, renderPythonOperationBinding(provider_import, callable, descriptor));
    return {selector, relative_path, provider_path, provider_import, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), callable, rule_imports, event_imports, descriptor};
  });
  for (const file of [...artifacts.keys()]) {const parts = file.split('/'); for (let i = 1; i < parts.length; i++) {const init = parts.slice(0, i).join('/') + '/__init__.py'; if (!artifacts.has(init)) add(init, '');}}
  const body = {schema_version: 'domainspec.configured-python-operations-plan/v1-candidate', selection: {...selection, actions, factories: factories?.selection.factories ?? []}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    operation_contract_sha256: OPERATION_GENERATION_CONTRACT_SHA256, rule_plan: rules, factory_plan: factories, algebraic_plan: algebraic, event_plan: events, modules, artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
