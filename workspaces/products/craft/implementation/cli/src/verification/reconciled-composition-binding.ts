import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';

export const COMPOSITION_BINDING_DEFINITION_SHA256 = 'b2bbf4f1c7ea8c3d54d5c3eddf70c4b689ec060da32b8b0e67b9a24ce153dc84';
const fail = (message: string): never => {throw new TypeError('COMPOSITION_BINDING:' + message);};
const same = (a: unknown, b: unknown, reason: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(reason);};
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
const order = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;
export interface CompositionImport {readonly specifier: string; readonly imported: string; readonly local: string;}
export interface CompositionModule {readonly relative_path: string; readonly source_sha256: string; readonly exports: readonly string[]; readonly imports: readonly CompositionImport[];}
const specifier = (from: string, to: string) => {const s = path.posix.relative(path.posix.dirname(from), to).replace(/\.ts$/, '.js'); return s.startsWith('.') ? s : './' + s;};
const registered = new WeakSet<object>();

/** Source identity and configured paths supply expectations, not emitted descriptors. */
export function createCompositionBinding(graph: CompiledProjectGraph, plan: ReconciledProjectPlan, id: string, definition: string) {
  if (typeof definition !== 'string' || sha256(definition) !== COMPOSITION_BINDING_DEFINITION_SHA256) fail('definition drift');
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan);
  const certificate = createCompiledProjectCertificate(graph);
  same(certificate, plan.resolved.certificate, 'cross-graph plan');
  same(graph.source_manifest, plan.resolved.semantic_sources, 'source manifest drift');
  if (graph.compositions?.length !== 1 || !plan.composition || plan.composition.compositions.length !== 1) fail('exactly one source composition required');
  const composition = graph.compositions!.find(c => c.id === id) ?? fail('source composition ID');
  if (composition.source.model.endpoint.target !== 'node-http') fail('unsupported target');
  const selected = plan.composition!.compositions.find(c => c.id === id) ?? fail('selected composition ID');
  const prefix = 'compositions/' + id + '/', behavior_path = prefix + 'behavior.mjs', adapter_path = prefix + 'core-api.ts';
  same(selected.behavior_path, behavior_path, 'behavior path'); same(selected.adapter_path, adapter_path, 'adapter path');
  same(selected.source_sha256, sha256(canonicalJson(composition.source)), 'composition source identity');
  const role = JSON.parse(getReconciledSource('configuration')).types.find((r: any) => r.kind === 'Calculation')?.role;
  if (role !== 'domain/calculations') fail('configured Calculation role');
  const artifacts = new Map([...plan.resolved.artifacts, ...plan.composition!.artifacts].map(a => [a.relative_path, a]));
  const artifact = (p: string) => {const a = artifacts.get(p) ?? fail('missing artifact:' + p); if (a.sha256 !== sha256(a.content) || a.size_bytes !== Buffer.byteLength(a.content)) fail('artifact bytes:' + p); return a;};
  const modules = new Map<string, CompositionModule>();
  const add = (relative_path: string, exports: string[], imports: CompositionImport[]) => {
    const row = {relative_path, source_sha256: artifact(relative_path).sha256, exports: exports.sort(order), imports};
    if (modules.has(relative_path)) same(modules.get(relative_path), row, 'inconsistent shared module');
    modules.set(relative_path, row);
  };
  const adapterImports: CompositionImport[] = [];
  const bridges = Object.entries(composition.source.core_bindings as Record<string, {selector: string; fields: Record<string, string>}>).sort(([a], [b]) => order(a, b)).map(([name, b]) => {
    const node = graph.nodes.find(n => n.selector === b.selector) ?? fail('unknown core owner');
    const calculation = Object.hasOwn(composition.source.contract.calculations, name);
    const names: string[] = calculation ? composition.source.contract.calculations[name] : Object.keys(b.fields).sort(order);
    let native_target: {relative_path: string; sha256: string; export_name: string} | null = null;
    if (calculation) {
      if (node.kind !== 'Calculation' || (node.body.typed_contract as any).schema_version !== 'domainspec.typed-calculation/v1') fail('unsupported Calculation owner');
      const relative_path = `${plan.selection.module_root}/features/${node.feature_id}/src/${role}/${node.node_id}.ts`;
      const provider = relative_path.replace(/\.ts$/, '.provider.ts');
      const callable = 'calculate' + node.node_id.split('-').map(s => s[0]!.toUpperCase() + s.slice(1)).join('');
      for (const p of [relative_path, provider]) {
        const selectedModule = plan.resolved.modules.find(m => m.relative_path === p) ?? fail('selected Calculation module:' + p);
        same(selectedModule.qualified_selectors, [node.selector], 'Calculation ownership');
        if (!selectedModule.request_sha256s.some(h => plan.resolved.requests.some(r => r.request_sha256 === h && r.kind === 'calculations-v1' && (r.selection as any).roots.includes(node.selector)))) fail('Calculation selection ownership');
      }
      add(provider, ['calculate'], []);
      add(relative_path, [callable], [{specifier: specifier(relative_path, provider), imported: 'calculate', local: 'calculate'}]);
      adapterImports.push({specifier: specifier(adapter_path, relative_path), imported: callable, local: 'calculation' + adapterImports.length});
      native_target = {relative_path, sha256: artifact(relative_path).sha256, export_name: callable};
    }
    return {name, selector: b.selector, role: calculation ? 'calculation-call' as const : 'structural-record' as const,
      contract_sha256: sha256(canonicalJson(node.body.typed_contract)), arguments: names.map(authored_name => ({authored_name, core_name: b.fields[authored_name]!})), native_target};
  });
  same(bridges, selected.bindings, 'source-derived bridges differ from selected metadata');
  add(adapter_path, ['evaluateCalculation'], adapterImports);
  add(behavior_path, ['execute', 'validateInput'], []);
  for (const [name, content] of Object.entries(composition.artifacts)) same(artifact(prefix + name).content, content, 'source composition artifact:' + name);
  const inventory = [...Object.keys(composition.artifacts).map(p => prefix + p), adapter_path].sort(order);
  same(inventory, selected.artifact_paths, 'composition artifact inventory');
  for (const m of modules.values()) {
    if (m.relative_path === behavior_path) continue; // Independently parsed in both audit phases.
    const selectedModule = m.relative_path === adapter_path ? plan.composition!.modules.find(x => x.relative_path === m.relative_path) : plan.resolved.modules.find(x => x.relative_path === m.relative_path);
    if (!selectedModule) fail('selected surface missing');
    same(selectedModule!.exports.filter(e => e.kind === 'value').map(e => e.name).sort(order), m.exports, 'selected exports');
    same(selectedModule!.imports.flatMap(i => i.names.map(imported => ({specifier: i.specifier, imported}))), m.imports.map(({specifier, imported}) => ({specifier, imported})), 'selected imports');
  }
  const body = {schema_version: 'domainspec.composition-verification-binding/v1-candidate' as const, definition_sha256: COMPOSITION_BINDING_DEFINITION_SHA256,
    id, graph_sha256: certificate.graph_sha256, source_manifest_sha256: graph.source_manifest.manifest_sha256,
    composition_source_sha256: sha256(canonicalJson(composition.source)), authored_text_sha256: sha256(composition.source.source_text), contract_sha256: sha256(canonicalJson(composition.source.contract)),
    resolved_plan_sha256: plan.resolved.plan_sha256, composition_plan_sha256: plan.composition!.plan_sha256, behavior_path, adapter_path, bridges,
    artifacts: inventory.map(relative_path => ({relative_path, sha256: artifact(relative_path).sha256})),
    modules: [...modules.values()].sort((a, b) => order(a.relative_path, b.relative_path)), authority_effect: 'none' as const};
  const result = freeze({...body, binding_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}
export type CompositionVerificationBinding = ReturnType<typeof createCompositionBinding>;
export function assertCompositionBinding(value: unknown): asserts value is CompositionVerificationBinding {
  if (!value || typeof value !== 'object' || !registered.has(value)) fail('registered binding required');
}
