import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {inventoryGeneratedModule} from './generated-module-surface.js';
import {findReconciledSourceByDigest} from './reconciled-sources.js';
import type {PlannedArtifact} from './contracts.js';
import {planConfiguredRules} from './configured-rules.js';
import {planConfiguredFactories} from './configured-factories.js';
import {planConfiguredEnums} from './configured-enums.js';
import {planConfiguredAlgebraicEnums} from './configured-algebraic-enums.js';
import {planConfiguredCalculations} from './configured-calculations.js';
import {planConfiguredCalculationsV2} from './configured-calculations-v2.js';
import {planConfiguredQueries} from './configured-queries.js';
import {planConfiguredMappings} from './configured-mappings.js';
import {planConfiguredPolicies} from './configured-policies.js';
import {planConfiguredEvents} from './configured-events.js';
import {planConfiguredOperations} from './configured-operations.js';
import {planConfiguredWorkflow,planConfiguredComposedWorkflow} from './configured-workflows.js';
import {planConfiguredComposedOperations} from './configured-composed-operations.js';
import {planConfiguredStateMachines} from './configured-state-machines.js';
import {planConfiguredPublicBoundaries} from './configured-public-boundaries.js';

export const RESOLVED_ARTIFACT_SELECTION_VERSION = 'domainspec.resolved-artifact-selection/v1-candidate';
export const RESOLVED_ARTIFACT_CONTRACT_SHA256 = 'f82cab846efe2165776e89bf845a677af6209537d1855ba9db7a780c1b5e3212';
export const RESOLVED_ARTIFACT_LAYOUT = 'domainspec.existing-profile-layout/v1-candidate';
export const COMPOSED_PROJECT_CONTRACT_SHA256='15795f5e18f1bbf04a29ecce1ed941cf8e8bb7e59275d6bc34d57597b159620d';
export const RESOLVED_COMPOSED_SELECTION_VERSION='domainspec.resolved-artifact-selection/v2-candidate';
export type ResolvedGeneratorRequest =
  | Readonly<{kind: 'rules'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredRules>[1]; sources: Parameters<typeof planConfiguredRules>[2]}>
  | Readonly<{kind: 'factories'; fields: CompiledProjectFields; selection: Parameters<typeof planConfiguredFactories>[2]; sources: Parameters<typeof planConfiguredFactories>[3]}>
  | Readonly<{kind: 'enums'; fields: CompiledProjectFields; selection: Parameters<typeof planConfiguredEnums>[1]; sources: Parameters<typeof planConfiguredEnums>[2]}>
  | Readonly<{kind: 'algebraic-enums'; fields: CompiledProjectFields; selection: Parameters<typeof planConfiguredAlgebraicEnums>[2]; sources: Parameters<typeof planConfiguredAlgebraicEnums>[3]}>
  | Readonly<{kind: 'calculations-v1'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredCalculations>[1]; sources: Parameters<typeof planConfiguredCalculations>[2]}>
  | Readonly<{kind: 'calculations-v2'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredCalculationsV2>[1]; sources: Parameters<typeof planConfiguredCalculationsV2>[2]}>
  | Readonly<{kind: 'queries'; fields: CompiledProjectFields; selection: Parameters<typeof planConfiguredQueries>[2]; sources: Parameters<typeof planConfiguredQueries>[3]}>
  | Readonly<{kind: 'mappings'; fields: CompiledProjectFields; selection: Parameters<typeof planConfiguredMappings>[2]; sources: Parameters<typeof planConfiguredMappings>[3]}>
  | Readonly<{kind: 'policies'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredPolicies>[3]; sources: Parameters<typeof planConfiguredPolicies>[4]}>
  | Readonly<{kind: 'events'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredEvents>[2]; sources: Parameters<typeof planConfiguredEvents>[3]}>
  | Readonly<{kind: 'operations'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredOperations>[3]; sources: Parameters<typeof planConfiguredOperations>[4]}>
  | Readonly<{kind: 'workflows'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredWorkflow>[3]; sources: Parameters<typeof planConfiguredWorkflow>[4]}>
  | Readonly<{kind:'composed-operations';fields:CompiledProjectFields;selection:Parameters<typeof planConfiguredComposedOperations>[3];sources:string}>
  | Readonly<{kind:'composed-workflows';fields:CompiledProjectFields;selection:Parameters<typeof planConfiguredComposedWorkflow>[3];sources:string}>
  | Readonly<{kind: 'state-machines'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredStateMachines>[3]; sources: Parameters<typeof planConfiguredStateMachines>[4]}>
  | Readonly<{kind: 'public-boundaries'; fields: CompiledProjectFields | null; selection: Parameters<typeof planConfiguredPublicBoundaries>[3]; sources: Parameters<typeof planConfiguredPublicBoundaries>[4]}>;
export interface ResolvedArtifactSelection {
  readonly schema_version: typeof RESOLVED_ARTIFACT_SELECTION_VERSION;
  readonly language: 'typescript';
  readonly layout_version: typeof RESOLVED_ARTIFACT_LAYOUT;
  readonly module_root: string;
  readonly graph_sha256: string;
  readonly boundary_sha256: string;
  readonly requests: readonly ResolvedGeneratorRequest[];
}
export type ResolvedComposedArtifactSelection=Omit<ResolvedArtifactSelection,'schema_version'>&{readonly schema_version:typeof RESOLVED_COMPOSED_SELECTION_VERSION};
const versions = {
  "rules": "domainspec.configured-rules-selection/v8-candidate",
  "factories": "domainspec.configured-factories-selection/v12-candidate",
  "enums": "domainspec.configured-enums-selection/v2-candidate",
  "algebraic-enums": "domainspec.configured-algebraic-enums-selection/v1-candidate",
  "calculations-v1": "domainspec.configured-calculations-selection/v1-candidate",
  "calculations-v2": "domainspec.configured-calculations-selection/v2-candidate",
  "queries": "domainspec.configured-queries-selection/v1-candidate",
  "mappings": "domainspec.configured-mappings-selection/v1-candidate",
  "policies": "domainspec.configured-policies-selection/v1-candidate",
  "events": "domainspec.configured-events-selection/v1-candidate",
  "operations": "domainspec.configured-operations-selection/v1-candidate",
  "workflows": "domainspec.configured-workflow-selection/v1-candidate",
  "composed-operations":"domainspec.configured-composed-operations-selection/v1-candidate",
  "composed-workflows":"domainspec.composed-workflow-selection/v1-candidate",
  "state-machines": "domainspec.configured-state-machines-selection/v1-candidate",
  "public-boundaries": "domainspec.configured-public-boundaries-selection/v1-candidate"
} as const;
const fail = (message: string): never => {throw new TypeError('DS_RESOLVED_ARTIFACT_PLAN:' + message);};
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('plain object');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(descriptors).length !== keys.length || Reflect.ownKeys(descriptors).some(k => typeof k !== 'string' || !keys.includes(k)) ||
    Object.values(descriptors).some(d => !Object.hasOwn(d, 'value') || !d.enumerable)) fail('closed inert object');
}
const fields = (r: ResolvedGeneratorRequest): CompiledProjectFields => r.fields ?? fail('required field closure:' + r.kind);
function generate(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, r: ResolvedGeneratorRequest) {
  switch (r.kind) {
    case 'rules': return planConfiguredRules(graph, r.selection, r.sources);
    case 'factories': return planConfiguredFactories(graph, fields(r), r.selection, r.sources);
    case 'enums': return planConfiguredEnums(fields(r), r.selection, r.sources);
    case 'algebraic-enums': return planConfiguredAlgebraicEnums(graph, fields(r), r.selection, r.sources);
    case 'calculations-v1': return planConfiguredCalculations(boundary, r.selection, r.sources);
    case 'calculations-v2': return planConfiguredCalculationsV2(boundary, r.selection, r.sources);
    case 'queries': return planConfiguredQueries(boundary, fields(r), r.selection, r.sources);
    case 'mappings': return planConfiguredMappings(boundary, fields(r), r.selection, r.sources);
    case 'policies': return planConfiguredPolicies(graph, boundary, r.fields, r.selection, r.sources);
    case 'events': return planConfiguredEvents(graph, boundary, r.selection, r.sources);
    case 'operations': return planConfiguredOperations(graph, boundary, r.fields, r.selection, r.sources);
    case 'workflows': return planConfiguredWorkflow(graph, boundary, r.fields, r.selection, r.sources);
    case 'composed-operations':return planConfiguredComposedOperations(graph,boundary,r.fields,r.selection,r.sources);
    case 'composed-workflows':return planConfiguredComposedWorkflow(graph,boundary,r.fields,r.selection,r.sources);
    case 'state-machines': return planConfiguredStateMachines(graph, boundary, r.fields, r.selection, r.sources);
    case 'public-boundaries': return planConfiguredPublicBoundaries(graph, boundary, r.fields, r.selection, r.sources);
  }
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}
const compare = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;
const snapshots = new WeakSet<object>();
export type ResolvedArtifactPlan = ReturnType<typeof planResolvedArtifacts>;
export function assertResolvedArtifactPlan(value: unknown): asserts value is ResolvedArtifactPlan {
  if (!value || typeof value !== 'object' || !snapshots.has(value)) fail('unregistered resolved plan');
}

/** Pure composition: generators own native locations and source meaning.
 * No caller-authored artifact or provider callback is accepted as a checked plan.
 */
export function planResolvedArtifacts(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, selection: ResolvedArtifactSelection, definition: string) {
  return planResolvedArtifactsCore(graph,boundary,selection,definition,null);
}
export function planResolvedComposedArtifacts(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,selection:ResolvedComposedArtifactSelection,definition:string,extension:string){
  if(typeof extension!=='string'||sha256(extension)!==COMPOSED_PROJECT_CONTRACT_SHA256)fail('composed definition drift');
  return planResolvedArtifactsCore(graph,boundary,selection,definition,extension);
}
function planResolvedArtifactsCore(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,selection:ResolvedArtifactSelection|ResolvedComposedArtifactSelection,definition:string,extension:string|null){
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary);
  closed(selection, ['schema_version', 'language', 'layout_version', 'module_root', 'graph_sha256', 'boundary_sha256', 'requests']);
  if (selection.schema_version !== (extension===null?RESOLVED_ARTIFACT_SELECTION_VERSION:RESOLVED_COMPOSED_SELECTION_VERSION) || selection.language !== 'typescript' || selection.layout_version !== RESOLVED_ARTIFACT_LAYOUT) fail('selection version');
  if (typeof definition !== 'string' || sha256(definition) !== RESOLVED_ARTIFACT_CONTRACT_SHA256) fail('definition drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.graph_sha256 !== certificate.graph_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || selection.boundary_sha256 !== boundary.boundary_sha256) fail('stale graph or boundary');
  if (typeof selection.module_root !== 'string' || !selection.module_root.split('/').every(s => /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(s)?.[0] === s)) fail('module root');
  if (!Array.isArray(selection.requests) || Object.getPrototypeOf(selection.requests) !== Array.prototype) fail('requests');
  const descriptors: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(selection.requests);
  const count = descriptors.length!.value as number;
  if (!Number.isSafeInteger(count) || count < 1 || count > 256 || Reflect.ownKeys(descriptors).length !== count + 1) fail('bounded dense requests');
  const requests: ResolvedGeneratorRequest[] = [];
  for (let i = 0; i < count; i++) {
    const d = descriptors[String(i) as keyof typeof descriptors] as PropertyDescriptor | undefined;
    if (!d || !Object.hasOwn(d, 'value') || !d.enumerable) fail('inert request');
    const r = d!.value as ResolvedGeneratorRequest;
    closed(r, ['kind', 'fields', 'selection', 'sources']);
    if (typeof r.kind !== 'string' || !Object.hasOwn(versions, r.kind)) fail('unknown generator');
    if(extension===null&&(r.kind==='composed-operations'||r.kind==='composed-workflows'))fail('composed generator requires v2 selection');
    // Keep registered checked objects intact; never revive checked identities from JSON.
    assertInterfaceData(r.selection); assertInterfaceData(r.sources);
    if (r.selection.schema_version !== versions[r.kind] || r.selection.language !== 'typescript' || r.selection.module_root !== selection.module_root) fail('conflicting generator selection');
    if (r.fields !== null) {
      assertCompiledProjectFields(r.fields);
      if (r.fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || r.fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('stale or nonexact fields');
    }
    requests.push(r);
  }
  const sourceBlobs = new Map<string, string>([[RESOLVED_ARTIFACT_CONTRACT_SHA256, definition]]);
  if(extension!==null)sourceBlobs.set(COMPOSED_PROJECT_CONTRACT_SHA256,extension);
  const records = requests.map(r => {
    const child = generate(graph, boundary, r), sourceBindings: {pointer: string; sha256: string}[] = [];
    const pin = (value: unknown, pointer: string): void => {
      if (typeof value === 'string') {
        const digest = sha256(value), prior = sourceBlobs.get(digest);
        if (prior !== undefined && prior !== value) fail('source digest collision');
        sourceBlobs.set(digest, value); sourceBindings.push({pointer, sha256: digest}); return;
      }
      if (!value || typeof value !== 'object' || Array.isArray(value)) return fail('source bundle requires byte strings');
      for (const [k, v] of Object.entries(value).sort(([a], [b]) => compare(a, b))) pin(v, pointer + '/' + k.replace(/~/g, '~0').replace(/\//g, '~1'));
    };
    pin(r.sources, '');
    // Checked constructors carry definition digests, not mutable development paths.
    // Record matching compiler-selected bytes without reviving or trusting a caller hash.
    const checkedSources = new Map<string,string>();
    const collect = (value: unknown): void => {
      if (!value || typeof value !== 'object') return;
      for (const [key, item] of Object.entries(value)) {
        if ((key.endsWith('sha256') || key.endsWith('_contract')) && typeof item === 'string') {
          const selected = findReconciledSourceByDigest(item);
          if (selected) checkedSources.set(selected.id, selected.content);
        } else if (item && typeof item === 'object') collect(item);
      }
    };
    collect(r.selection); collect(r.fields); collect(child);
    for (const [id, content] of [...checkedSources].sort(([a],[b])=>compare(a,b))) pin(content,'/checked-definitions/'+id);
    const identity = {kind: r.kind, selection: structuredClone(child.selection), field_compilation_sha256: r.fields?.compilation_sha256 ?? null, sources: sourceBindings, child_plan_sha256: child.plan_sha256};
    return {identity, request_sha256: sha256(canonicalJson(identity)), child};
  }).sort((a, b) => compare(a.request_sha256, b.request_sha256));
  if (new Set(records.map(r => r.request_sha256)).size !== records.length) fail('duplicate generator request');
  const files = new Map<string, {artifact: PlannedArtifact; requests: string[]}>();
  const casePaths = new Map<string, string>();
  for (const record of records) for (const a of record.child.artifacts) {
    const p = a.relative_path;
    if (typeof p !== 'string' || !p.startsWith(selection.module_root + '/') || path.posix.normalize(p) !== p || p.includes('\\') || !p.endsWith('.ts')) fail('unsafe native artifact path');
    if (sha256(a.content) !== a.sha256 || Buffer.byteLength(a.content) !== a.size_bytes) fail('artifact content binding');
    const alias = casePaths.get(p.toLowerCase()); if (alias && alias !== p) fail('case-fold artifact collision');
    casePaths.set(p.toLowerCase(), p);
    const previous = files.get(p);
    if (previous) {
      if (previous.artifact.sha256 !== a.sha256 || previous.artifact.content !== a.content) fail('conflicting definition:' + p);
      previous.requests.push(record.request_sha256);
    } else files.set(p, {artifact: {...a}, requests: [record.request_sha256]});
  }
  const paths = [...files.keys()].sort(compare);
  const owners = new Map<string, Set<string>>(), nodes = new Map(graph.nodes.map(n => [n.selector, n]));
  const collectOwners = (value: unknown): void => {
    if (!value || typeof value !== 'object') return;
    const row = value as Record<string, unknown>;
    if (typeof row.selector === 'string' && nodes.has(row.selector)) {
      for (const key of ['relative_path', 'provider_path', 'material_path', 'definition_path']) {
        const p = row[key];
        if (typeof p === 'string' && files.has(p)) {
          const selected = owners.get(p) ?? new Set<string>(); selected.add(row.selector); owners.set(p, selected);
        }
      }
    }
    Object.values(row).forEach(collectOwners);
  };
  records.forEach(r => collectOwners(r.child));
  for (const p of paths) {
    let parent = path.posix.dirname(p);
    while (parent !== '.') {if (casePaths.has(parent.toLowerCase())) fail('file-directory collision'); parent = path.posix.dirname(parent);}
  }
  const surfaces = new Map(paths.map(p => {
    try {return [p, inventoryGeneratedModule(files.get(p)!.artifact.content)] as const;}
    catch (error) {return fail('native surface:' + p + ':' + String(error));}
  }));
  const modules = paths.map(p => {
    const row = files.get(p)!, surface = surfaces.get(p)!;
    const imports = surface.imports.map(imp => {
      if (imp.specifier === 'node:crypto') {
        if (imp.names.some(n => n !== 'createHash') || imp.namespace || imp.type_only || imp.reexport) fail('unselected node:crypto binding');
        return {...imp, target_path: null, target_sha256: null, dependency: 'node-standard-library' as const};
      }
      if (!imp.specifier.startsWith('./') && !imp.specifier.startsWith('../') || !imp.specifier.endsWith('.js')) fail('nonleaf import:' + imp.specifier);
      const target = path.posix.normalize(path.posix.join(path.posix.dirname(p), imp.specifier.slice(0, -3) + '.ts'));
      const resolved = files.get(target) ?? fail('unresolved import:' + p + ':' + imp.specifier);
      if (imp.names.some(name => !surfaces.get(target)!.exports.some(e => e.name === name))) fail('unresolved native export:' + target);
      return {...imp, target_path: target, target_sha256: resolved.artifact.sha256, dependency: 'generated-leaf' as const};
    });
    const qualified_selectors = [...(owners.get(p) ?? [])].sort(compare);
    return {relative_path: p, sha256: row.artifact.sha256, qualified_selectors,
      metatypes: [...new Set(qualified_selectors.map(s => nodes.get(s)!.kind))].sort(compare),
      artifact_role: qualified_selectors.length ? 'domain-module' as const : 'shared-support' as const,
      request_sha256s: [...new Set(row.requests)].sort(compare), exports: surface.exports, imports};
  });
  const body = {
    schema_version: 'domainspec.resolved-artifact-plan/v1-candidate' as const,
    selection: {schema_version: selection.schema_version, language: selection.language, layout_version: selection.layout_version, module_root: selection.module_root},
    certificate, boundary_sha256: boundary.boundary_sha256, definition_sha256: RESOLVED_ARTIFACT_CONTRACT_SHA256,
    ...(extension!==null?{composition_contract_sha256:COMPOSED_PROJECT_CONTRACT_SHA256}:{}),
    semantic_sources: structuredClone(graph.source_manifest),
    requests: records.map(r => ({...r.identity, request_sha256: r.request_sha256})),
    source_blobs: [...sourceBlobs].sort(([a], [b]) => compare(a, b)).map(([sha256, content]) => ({sha256, content, size_bytes: Buffer.byteLength(content)})),
    modules, artifacts: paths.map(p => files.get(p)!.artifact),
    verification_obligations: ['strict-native-compilation', 'independent-module-surface-observation', 'selected-generator-semantic-controls', 'cross-generator-behavior', 'safe-output-separate-from-planning'],
    authority_effect: 'none' as const, output_effect: 'none' as const,
  };
  const plan = freeze({...body, plan_sha256: sha256(canonicalJson(body))});
  snapshots.add(plan); return plan;
}
