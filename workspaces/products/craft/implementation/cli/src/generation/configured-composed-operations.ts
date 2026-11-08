import path from 'node:path';
import { assertCompiledProjectSnapshot, type CompiledProjectGraph } from '../input/project-model.js';
import { assertCompiledCompositionBoundary, type CompiledCompositionBoundary } from '../input/composition-boundary.js';
import { assertCompiledProjectFields, type CompiledProjectFields } from '../input/compiled-field-model.js';
import { createCompiledProjectCertificate } from '../compilation/certificate.js';
import { assertCheckedComposedOperationAction, type CheckedComposedOperationAction } from '../typed-operation/action-bindings.js';
import { assertInterfaceData } from '../typed-backend/interface.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import { getReconciledSource as source, RECONCILED_SOURCE_CAPSULE_SHA256 } from './reconciled-sources.js';
import { planConfiguredRules, STRUCTURED_RULE_VERSION } from './configured-rules.js';
import { planConfiguredFactories, STRUCTURED_FACTORY_VERSION, type FactoryBinding } from './configured-factories.js';
import { planConfiguredAlgebraicEnums, ALGEBRAIC_ENUM_VERSION } from './configured-algebraic-enums.js';
import { planConfiguredEvents, CONFIGURED_EVENT_VERSION, EVENT_VALUE_PROFILE } from './configured-events.js';
import { planConfiguredQueries, CONFIGURED_QUERY_VERSION } from './configured-queries.js';
import { planConfiguredMappings, CONFIGURED_MAPPING_VERSION } from './configured-mappings.js';
import { planConfiguredPublicBoundaries, CONFIGURED_PUBLIC_BOUNDARIES_VERSION } from './configured-public-boundaries.js';
import { renderConfiguredComposedOperation } from './configured-operation-source.js';
import type { OperationAbsenceFailure } from './composed-operation-values.js';
import { EXACT_UINT64_PROFILE } from './exact-uint64.js';
import type { PlannedArtifact } from './contracts.js';

export const COMPOSED_OPERATION_SELECTION_VERSION = 'domainspec.configured-composed-operations-selection/v1-candidate';
export const COMPOSED_OPERATION_GENERATION_SHA256 = '277649b65efc5fb8a39bedab056c5e78b4930a8c22b0870f72374d4e962a8026';
export interface ComposedOperationSelection {
  readonly schema_version: typeof COMPOSED_OPERATION_SELECTION_VERSION;
  readonly language: 'typescript'; readonly module_root: string;
  readonly actions: readonly Readonly<{ action: CheckedComposedOperationAction; absence_failures: readonly OperationAbsenceFailure[] }>[];
  readonly factories: readonly FactoryBinding[];
}
const fail = (reason: string): never => { throw new TypeError('DS_COMPOSED_OPERATION_PLAN:' + reason); };
const freeze = <T>(value: T): T => { if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); } return value; };
const closed = (value: unknown, keys: readonly string[]): void => {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('plain object required');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(descriptors).length !== keys.length || Reflect.ownKeys(descriptors).some(k => typeof k !== 'string' || !keys.includes(k)) || Object.values(descriptors).some(d => !Object.hasOwn(d, 'value') || !d.enumerable)) fail('closed inert fields required');
};
const dense = (value: unknown): readonly unknown[] => {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) return fail('dense array required');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (value.length < 1 || value.length > 128 || Reflect.ownKeys(descriptors).length !== value.length + 1) fail('action array bounds');
  for (let i = 0; i < value.length; i++) { const d = descriptors[String(i)]; if (!d || !Object.hasOwn(d, 'value') || !d.enumerable) fail('inert action entries required'); }
  return value;
};
const reserved = new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul ' + Array.from({ length: 9 }, (_, i) => `com${i + 1} lpt${i + 1}`).join(' ')).split(' '));
const portable = (value: string) => typeof value === 'string' && value.length <= 128 && /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(value)?.[0] === value && !reserved.has(value);
const sorted = (values: readonly string[]) => [...new Set(values)].sort();
const literal = (value: unknown): string => Array.isArray(value) ? 'Object.freeze([' + value.map(literal).join(',') + '])' : value && typeof value === 'object' ? 'Object.freeze({' + Object.entries(value).map(([k, v]) => '[' + JSON.stringify(k) + ']:' + literal(v)).join(',') + '})' : JSON.stringify(value);
const checked = new WeakSet<object>();
export type ConfiguredComposedOperationsPlan = ReturnType<typeof planConfiguredComposedOperations>;
export function assertConfiguredComposedOperationsPlan(value: unknown): asserts value is ConfiguredComposedOperationsPlan {
  if (!value || typeof value !== 'object' || !checked.has(value)) fail('unvalidated plan');
}

/** Plan immutable artifacts from exact checked meaning. No writes or execution. */
export function planConfiguredComposedOperations(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: ComposedOperationSelection, contractSource: string) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'module_root', 'actions', 'factories']);
  if (selection.schema_version !== COMPOSED_OPERATION_SELECTION_VERSION || selection.language !== 'typescript') fail('unsupported selection');
  if (typeof contractSource !== 'string' || sha256(contractSource) !== COMPOSED_OPERATION_GENERATION_SHA256) fail('contract drift');
  if (typeof selection.module_root !== 'string' || !selection.module_root.split('/').every(portable)) fail('unsafe module root');
  const certificate = createCompiledProjectCertificate(graph);
  if (boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('cross-graph context');
  const actions = dense(selection.actions).map(raw => {
    closed(raw, ['action', 'absence_failures']); const row = raw as ComposedOperationSelection['actions'][number];
    assertCheckedComposedOperationAction(row.action); assertInterfaceData(row.absence_failures);
    if (!Array.isArray(row.absence_failures)) fail('absence array required');
    row.absence_failures.forEach(f => closed(f, ['binding', 'code']));
    const a = row.action;
    if (a.certificate.graph_sha256 !== certificate.graph_sha256 || a.boundary_sha256 !== boundary.boundary_sha256 || a.field_compilation_sha256 !== fields.compilation_sha256) fail('stale action');
    if (a.bindings.selector.split(':').length !== 2 || !a.bindings.selector.split(':').every(portable)) fail('unsafe selector');
    return { action: a, absence_failures: [...structuredClone(row.absence_failures)].sort((a, b) => a.binding < b.binding ? -1 : a.binding > b.binding ? 1 : 0) };
  }).sort((a, b) => a.action.bindings.selector < b.action.bindings.selector ? -1 : a.action.bindings.selector > b.action.bindings.selector ? 1 : 0);
  if (new Set(actions.map(a => a.action.bindings.selector)).size !== actions.length) fail('duplicate action');
  const common = { configuration: source('configuration'), base: source('base'), typescript: source('typescript') };
  const ruleSources = { ...common, rule_contract: source('rule'), collection_contract: source('rule_collection'), predicate_contract: source('rule_predicate'), numeric_contract: source('rule_numeric'), exact_contract: source('rule_exact'), literal_contract: source('rule_literal'), structured_contract: source('rule_structured'), field_contract: source('field') };
  const factorySources = { ...ruleSources, factory_contract: source('factory'), enum_provider: source('enum_provider') };
  const layout = { language: 'typescript' as const, module_root: selection.module_root };
  const exact = { ...layout, value_profile: EXACT_UINT64_PROFILE, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256 };
  const enumOnly = fields.model.declarations.every(d => d.kind === 'Enum');
  const factories = enumOnly ? null : planConfiguredFactories(graph, fields, { schema_version: STRUCTURED_FACTORY_VERSION, ...layout, field_compilation_sha256: fields.compilation_sha256, rule_selection: { schema_version: STRUCTURED_RULE_VERSION, value_profile: EXACT_UINT64_PROFILE }, factories: selection.factories }, factorySources);
  const algebraic = enumOnly ? planConfiguredAlgebraicEnums(graph, fields, { schema_version: ALGEBRAIC_ENUM_VERSION, ...layout, field_compilation_sha256: fields.compilation_sha256, factories: selection.factories }, { standalone_contract: source('standalone_sum'), factories: factorySources }) : null;
  const providers = factories ?? { modules: [], sum_modules: algebraic?.sum_modules ?? [], enum_components: algebraic?.components ?? [] };
  const config = JSON.parse(common.configuration), profile = JSON.parse(common.typescript);
  const cell = config.types.find((c: { kind: string }) => c.kind === 'Operation');
  const protocol = profile.representation_overlays.find((p: { contract_id: string }) => p.contract_id === 'operation.profile-representation')?.candidate_protocols.find((p: { protocol_id: string }) => p.protocol_id === 'typescript.bound-operation/v1');
  if (cell?.role !== 'application/operations' || protocol?.form_id !== 'typescript.bound-operation-function') fail('Operation profile mismatch');
  const artifacts = new Map<string, PlannedArtifact>();
  const add = (artifact: PlannedArtifact) => {
    if (artifact.sha256 !== sha256(artifact.content) || artifact.size_bytes !== Buffer.byteLength(artifact.content)) fail('artifact digest mismatch');
    const key = artifact.relative_path.toLowerCase(), old = artifacts.get(key);
    if (old && (old.relative_path !== artifact.relative_path || old.content !== artifact.content)) fail('artifact collision:' + artifact.relative_path);
    artifacts.set(key, artifact); return artifact;
  };
  const emit = (relative_path: string, content: string) => add({ relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content) });
  (factories?.artifacts ?? algebraic?.artifacts ?? []).forEach(add);
  const modules = actions.map(({ action, absence_failures }) => {
    const selector = action.bindings.selector, [feature, id] = selector.split(':') as [string, string];
    const relative_path = `${selection.module_root}/features/${feature}/src/${cell.role}/${id}.ts`, provider_path = relative_path.replace(/\.ts$/, '.provider.ts');
    const rel = (target: string) => { const p = path.posix.relative(path.posix.dirname(provider_path), target).replace(/\.ts$/, '.js'); return p.startsWith('.') ? p : './' + p; };
    const rules = planConfiguredRules(graph, { schema_version: STRUCTURED_RULE_VERSION, ...layout, value_profile: EXACT_UINT64_PROFILE, roots: sorted(action.guards.map(g => g.selector)) }, ruleSources);
    const eventRoots = sorted(action.events.map(e => e.target));
    const events = eventRoots.length ? planConfiguredEvents(graph, boundary, { schema_version: CONFIGURED_EVENT_VERSION, ...layout, value_profile: EVENT_VALUE_PROFILE, boundary_sha256: boundary.boundary_sha256, roots: eventRoots }, { ...common, event_contract: source('event') }) : null;
    const connections = action.value_composition.references.connections;
    const queryRoots = sorted(connections.filter(c => c.binding.kind === 'query').map(c => c.binding.selector));
    const mappingRoots = sorted(connections.filter(c => c.contract.schema_version === 'domainspec.typed-mapping/v2').map(c => c.binding.selector));
    const publicRoots = sorted([...connections.filter(c => c.contract.schema_version === 'domainspec.typed-mapping/v3').map(c => c.binding.selector), ...action.value_composition.public_contracts.map(i => i.selector)]);
    const queries = queryRoots.length ? planConfiguredQueries(boundary, fields, { schema_version: CONFIGURED_QUERY_VERSION, ...exact, roots: queryRoots }, { ...common, query_contract: source('query') }) : null;
    const mappings = mappingRoots.length ? planConfiguredMappings(boundary, fields, { schema_version: CONFIGURED_MAPPING_VERSION, ...exact, roots: mappingRoots }, { ...common, mapping_contract: source('mapping') }) : null;
    const publics = publicRoots.length ? planConfiguredPublicBoundaries(graph, boundary, fields, { schema_version: CONFIGURED_PUBLIC_BOUNDARIES_VERSION, ...layout, value_profile: EXACT_UINT64_PROFILE, roots: publicRoots }, { ...common, generation_contract: source('public_boundary'), public_mapping_contract: source('public_mapping_value_object'), interface_contract: source('interface') }) : null;
    for (const plan of [rules, events, queries, mappings, publics]) plan?.artifacts.forEach(add);
    const ruleImports = action.guards.map((g, i) => { const m = rules.modules.find(m => m.selector === g.selector) ?? fail('missing Rule module'); return { selector: g.selector, path: rel(m.relative_path), symbol: m.callable, local: 'guard' + i }; });
    const eventImports = eventRoots.map((selector, i) => { const m = events!.modules.find(m => m.selector === selector) ?? fail('missing Event module'); return { selector, path: rel(m.relative_path), symbol: m.callable, local: 'makeEvent' + i }; });
    const valueImports = sorted(connections.map(c => c.binding.selector)).map((selector, i) => {
      const row = connections.find(c => c.binding.selector === selector)!;
      const m = queries?.modules.find(m => m.selector === selector) ?? mappings?.modules.find(m => m.selector === selector) ?? publics?.modules.find(m => m.selector === selector) ?? fail('missing value module');
      const contract_sha256 = 'contract_sha256' in m.descriptor ? m.descriptor.contract_sha256 : sha256(canonicalJson(m.descriptor.contract));
      if (contract_sha256 !== row.contract_sha256) fail('planned value contract drift');
      return { selector, kind: row.binding.kind, path: rel(m.relative_path), symbol: m.callable, local: 'valueCall' + i, contract_sha256, artifact_sha256: artifacts.get(m.relative_path.toLowerCase())!.sha256 };
    });
    const publicImports = (publics?.interfaces ?? []).map((api, i) => ({ selector: api.selector, path: rel(api.relative_path), local: 'valuePublic' + i, contract_sha256: api.descriptor.contract_sha256, artifact_sha256: api.artifact_sha256 }));
    const provider = emit(provider_path, renderConfiguredComposedOperation(action, fields.model, providers, provider_path, ruleImports, eventImports, { values: valueImports, public_values: publicImports, absence_failures }));
    const descriptorBody = {
      schema_version: 'domainspec.generated-composed-operation-descriptor/v1-candidate' as const, selector,
      action_sha256: action.action_sha256, composition_sha256: action.value_composition.types_sha256,
      definition_sha256: COMPOSED_OPERATION_GENERATION_SHA256, source_capsule_sha256: RECONCILED_SOURCE_CAPSULE_SHA256,
      graph_sha256: certificate.graph_sha256, field_compilation_sha256: fields.compilation_sha256,
      value_imports: valueImports, absence_failures, provider_sha256: provider.sha256,
      dependency_plans: { rules: rules.plan_sha256, events: events?.plan_sha256 ?? null, queries: queries?.plan_sha256 ?? null, mappings: mappings?.plan_sha256 ?? null, public_boundaries: publics?.plan_sha256 ?? null, factories: factories?.plan_sha256 ?? algebraic?.plan_sha256 ?? null },
      execution_obligations: action.execution_obligations, effect_contract: 'state-and-outbox', provider_durability_claim: false, publication: false, authority_effect: 'none' as const,
    };
    const descriptor = { ...descriptorBody, descriptor_sha256: sha256(canonicalJson(descriptorBody)) };
    const callable = 'operation' + id.split('-').map(s => s[0]!.toUpperCase() + s.slice(1)).join('');
    emit(relative_path, `import {execute} from ${JSON.stringify('./' + id + '.provider.js')};\nexport type {OperationInput,OperationValue,OperationOutcome,OperationDependencies,OperationBatch,Transaction,CommitReceipt,ReadRequest,QuerySourceRequest,WriteIntent,EventIntent} from ${JSON.stringify('./' + id + '.provider.js')};\nexport const ${callable}=Object.freeze(Object.assign(execute,{descriptor:${literal(descriptor)}}));\n`);
    return { selector, relative_path, provider_path, callable, descriptor };
  });
  const body = { schema_version: 'domainspec.configured-composed-operations-plan/v1-candidate' as const,
    selection: { ...selection, actions, factories: factories?.selection.factories ?? algebraic?.selection.factories ?? [] }, certificate,
    boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256,
    definition_sha256: COMPOSED_OPERATION_GENERATION_SHA256, source_capsule_sha256: RECONCILED_SOURCE_CAPSULE_SHA256,
    modules, artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : a.relative_path > b.relative_path ? 1 : 0),
    execution: 'not-performed' as const, authority_effect: 'none' as const };
  const result = freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) }); checked.add(result); return result;
}
