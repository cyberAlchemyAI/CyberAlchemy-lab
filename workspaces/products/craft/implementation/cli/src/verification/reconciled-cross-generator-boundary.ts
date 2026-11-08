import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertReconciledProjectPlan, selectReconciledArtifacts, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {inventoryGeneratedModule} from '../generation/generated-module-surface.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';

export const CROSS_GENERATOR_DEFINITION_SHA256 = '35fca382f5cdabbf89db624eff8d4d4732fb1c178554af813d409c2030b44e50';
const fail = (message: string): never => {throw new TypeError('CROSS_GENERATOR_BOUNDARY:' + message);};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(reason);};
const order = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;
const unique = (values: readonly string[]) => [...new Set(values)].sort(order);
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
const registered = new WeakSet<object>();

/** Static dependency denominator, never a native interoperability result. */
export function createCrossGeneratorBoundary(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== CROSS_GENERATOR_DEFINITION_SHA256) fail('definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan);
  const certificate = createCompiledProjectCertificate(graph), resolved = plan.resolved;
  same(certificate, resolved.certificate, 'cross-graph plan');
  same(graph.source_manifest, resolved.semantic_sources, 'source manifest drift');
  same(plan.node_selectors, graph.nodes.map(n => n.selector).sort(order), 'root inventory');
  if (resolved.modules.length > 8192 || plan.node_selectors.length > 256 || resolved.modules.reduce((n, m) => n + m.imports.length, 0) > 65536) fail('inventory limit');

  const sources = new Map(resolved.source_blobs.map(s => [s.sha256, s]));
  for (const s of sources.values()) if (sha256(s.content) !== s.sha256 || Buffer.byteLength(s.content) !== s.size_bytes) fail('source blob drift');
  for (const r of resolved.requests) {
    const {request_sha256, ...identity} = r;
    if (sha256(canonicalJson(identity)) !== request_sha256) fail('request identity');
    if (r.sources.some(s => !sources.has(s.sha256))) fail('request source closure');
  }
  const requests = new Map(resolved.requests.map(r => [r.request_sha256, r]));
  const artifacts = new Map(resolved.artifacts.map(a => [a.relative_path, a]));
  same([...artifacts.keys()].sort(order), resolved.modules.map(m => m.relative_path).sort(order), 'native artifact inventory');
  const nodes = new Map(graph.nodes.map(n => [n.selector, n]));
  const modules = resolved.modules.map(m => {
    const a = artifacts.get(m.relative_path) ?? fail('module artifact missing');
    if (a.sha256 !== m.sha256 || sha256(a.content) !== a.sha256 || Buffer.byteLength(a.content) !== a.size_bytes) fail('artifact bytes');
    const surface = inventoryGeneratedModule(a.content);
    same(surface.exports, m.exports, 'module exports');
    same(surface.imports, m.imports.map(({target_path, target_sha256, dependency, ...imp}) => imp), 'module imports');
    if (!m.request_sha256s.length || m.request_sha256s.some(h => !requests.has(h))) fail('module request ownership');
    if (m.qualified_selectors.some(s => !nodes.has(s))) fail('module source ownership');
    same(m.metatypes, unique(m.qualified_selectors.map(s => nodes.get(s)!.kind)), 'module metatypes');
    return {relative_path: m.relative_path, sha256: m.sha256, qualified_selectors: m.qualified_selectors,
      metatypes: m.metatypes, artifact_role: m.artifact_role, request_sha256s: m.request_sha256s,
      generator_kinds: unique(m.request_sha256s.map(h => requests.get(h)!.kind)), exports: m.exports};
  });
  const moduleByPath = new Map(modules.map(m => [m.relative_path, m]));
  const requestRows = resolved.requests.map(r => ({...r, module_paths: modules.filter(m => m.request_sha256s.includes(r.request_sha256)).map(m => m.relative_path)}));
  if (requestRows.some(r => !r.module_paths.length)) fail('unrepresented request');
  const edges = resolved.modules.flatMap(m => m.imports.map((imp, import_index) => {
    const from = moduleByPath.get(m.relative_path)!;
    let target: typeof from | null = null;
    if (imp.target_path === null) {
      if (imp.specifier !== 'node:crypto' || imp.dependency !== 'node-standard-library' || imp.target_sha256 !== null || imp.namespace || imp.type_only || imp.reexport || imp.names.some(n => n !== 'createHash')) fail('native library boundary');
    } else {
      if ((!imp.specifier.startsWith('./') && !imp.specifier.startsWith('../')) || !imp.specifier.endsWith('.js')) fail('nonleaf import');
      const expected = path.posix.normalize(path.posix.join(path.posix.dirname(m.relative_path), imp.specifier.slice(0, -3) + '.ts'));
      target = moduleByPath.get(expected) ?? fail('unresolved native import');
      if (imp.target_path !== expected || imp.target_sha256 !== target.sha256 || imp.dependency !== 'generated-leaf') fail('native target binding');
      if (imp.names.some(n => !target!.exports.some(e => e.name === n))) fail('unresolved imported name');
    }
    // Complete incidence, not a single chosen owner. Shared ownership cannot hide
    // a different-kind pairing between the importer and its generated target.
    const body = {importer_path: from.relative_path, importer_sha256: from.sha256, import_index, ...imp,
      importer_request_sha256s: from.request_sha256s, target_request_sha256s: target?.request_sha256s ?? [],
      importer_generator_kinds: from.generator_kinds, target_generator_kinds: target?.generator_kinds ?? [],
      importer_selectors: from.qualified_selectors, target_selectors: target?.qualified_selectors ?? [],
      importer_metatypes: from.metatypes, target_metatypes: target?.metatypes ?? [],
      target_exports: target?.exports ?? [],
      shared_request_sha256s: target ? from.request_sha256s.filter(h => target.request_sha256s.includes(h)) : [],
      cross_generator_kind: !!target && from.generator_kinds.some(a => target.generator_kinds.some(b => a !== b)),
      category: !target ? 'native-standard-library' as const : imp.type_only ? 'generated-type-only' as const : 'generated-runtime' as const};
    return {...body, edge_sha256: sha256(canonicalJson(body))};
  }));
  const outgoing = new Map<string, typeof edges>(modules.map(m => [m.relative_path, []]));
  for (const e of edges) outgoing.get(e.importer_path)!.push(e);
  let visits = 0;
  const visit = () => {if (++visits > 1048576) fail('closure visit limit');};
  const roots = plan.node_selectors.map(selector => {
    const owned = modules.filter(m => m.qualified_selectors.includes(selector)).map(m => m.relative_path);
    if (!owned.length) fail('unrepresented root');
    const pending = [...owned], seen = new Set<string>(), selectedEdges = new Set<string>();
    while (pending.length) {
      const p = pending.pop()!;
      if (seen.has(p)) continue;
      visit(); seen.add(p);
      for (const e of outgoing.get(p) ?? fail('closure module missing')) {
        visit(); selectedEdges.add(e.edge_sha256);
        if (e.target_path && !seen.has(e.target_path)) pending.push(e.target_path);
      }
    }
    const module_paths = [...seen].sort(order), publicView = selectReconciledArtifacts(plan, [selector]);
    same(module_paths, publicView.artifacts.map(a => a.relative_path).sort(order), 'public root closure');
    same(module_paths.map(p => ({relative_path: p, sha256: moduleByPath.get(p)!.sha256})), publicView.artifacts.map(a => ({relative_path: a.relative_path, sha256: a.sha256})), 'public root bytes');
    return {selector, metatype: nodes.get(selector)!.kind, owned_module_paths: owned,
      module_paths, edge_sha256s: [...selectedEdges].sort(order), public_view_sha256: publicView.view_sha256};
  });
  const body = {schema_version: 'domainspec.cross-generator-boundary/v1-candidate' as const,
    definition_sha256: CROSS_GENERATOR_DEFINITION_SHA256, graph_sha256: certificate.graph_sha256,
    source_manifest_sha256: graph.source_manifest.manifest_sha256, project_plan_sha256: plan.plan_sha256,
    resolved_plan_sha256: resolved.plan_sha256, source_capsule_sha256: plan.source_capsule_sha256,
    scope: 'resolved-generator-native-imports' as const,
    excluded_composition_plan_sha256: plan.composition?.plan_sha256 ?? null,
    requests: requestRows, modules, edges, roots,
    counts: {requests: requestRows.length, modules: modules.length, imports: edges.length, roots: roots.length,
      shared_modules: modules.filter(m => m.request_sha256s.length > 1).length,
      support_modules: modules.filter(m => m.artifact_role === 'shared-support').length,
      generated_runtime_imports: edges.filter(e => e.category === 'generated-runtime').length,
      generated_type_only_imports: edges.filter(e => e.category === 'generated-type-only').length,
      native_library_imports: edges.filter(e => e.category === 'native-standard-library').length,
      cross_generator_imports: edges.filter(e => e.cross_generator_kind).length,
      cross_generator_runtime_imports: edges.filter(e => e.cross_generator_kind && e.category === 'generated-runtime').length},
    behavior_status: 'not_evaluable' as const, authority_effect: 'none' as const};
  const result = freeze({...body, boundary_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}
export type CrossGeneratorBoundary = ReturnType<typeof createCrossGeneratorBoundary>;
export function assertCrossGeneratorBoundary(value: unknown): asserts value is CrossGeneratorBoundary {
  if (!value || typeof value !== 'object' || !registered.has(value)) fail('registered boundary required');
}
