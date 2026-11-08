import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import test, {type TestContext} from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredPythonPublicMappings, PYTHON_PUBLIC_MAPPING_VERSION} from '../../src/generation/configured-python-public-mappings.ts';
import {renderPythonPublicMapping} from '../../src/generation/configured-python-public-mapping-source.ts';
import {qualifyPublicType} from '../../src/typed-backend/mapping-public.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {resolvePythonModules, selectPythonModuleClosure} from '../../src/generation/resolved-python-modules.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), pkg = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes = (p: string) => fs.readFileSync(p, 'utf8');
const sources = {configuration: bytes(path.join(pkg, 'configuration.json')), base: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  python: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')),
  interface_contract: bytes(path.join(pkg, 'named-interface-contract.json')), version_contract: bytes(path.join(pkg, 'interface-version-policy-contract.json')),
  field_contract: bytes(path.join(project, 'development/reconciliation-v1/contracts/exact-field-and-reference-model.json')),
  public_mapping_contract: bytes(path.join(pkg, 'public-mapping-contract.json')), generation_contract: bytes(path.join(pkg, 'public-boundary-generation-contract.json'))};
const boundaryContract = bytes(path.join(project, 'development/reconciliation-v1/contracts/composition-boundary.json'));
const scalar = (name = 'String'): any => ({kind: 'scalar', name});
const wrap = (kind: string, element: any): any => ({kind, element});
const local = (contract_id: string): any => ({kind: 'contract', contract_id});
const ref = (contract_id: string, api = 'api'): any => ({kind: 'contract', interface_selector: 'commerce:' + api, contract_id});
const named = (): any => ({kind: 'named', selector: 'commerce:order'});
const at = (root: string, ...properties: string[]): any => ({op: 'path', root, properties});
const field = (name: string, type: any) => ({name, ontology_field: 'TEST-PUBLIC#' + name, meaning: 'Public ' + name + '; RULE_INPUT stays authored.', type});
const bind = (target: string, value: any, fallback: any = null) => ({target, value, default: fallback});
const input = (name: string, type: any, use: any = null) => ({name, type, use});
const use = (operation_id: string, side = 'result', api = 'api') => ({interface_selector: 'commerce:' + api, operation_id, side});
const choice: any = {kind: 'sum', variants: [{name: 'None', ontology_variant: 'TEST-CHOICE#None', payload: null}, {name: 'Detail', ontology_variant: 'TEST-CHOICE#Detail', payload: local('detail')}]};
function api(id: string): any {
  return {schema_version: 'domainspec.typed-interface/v1', ontology_interface: 'TEST-' + id.toUpperCase(), boundary_kind: 'external',
    version_policy: {schema_version: 'domainspec.interface-version-policy/v1', mode: 'exact', direction: 'consumer-to-provider', provider_version: '1.0.0'},
    contracts: [{contract_id: 'detail', ontology_contract: 'TEST-DETAIL', fields: [field('amount', scalar('UInt64')), field('label', scalar())]},
      {contract_id: 'response', ontology_contract: 'TEST-RESPONSE', fields: [field('id', scalar()), field('lines', wrap('list', local('detail'))), field('unique', wrap('set', local('detail'))), field('choice', choice)]},
      {contract_id: 'summary', ontology_contract: 'TEST-SUMMARY', fields: [field('id', scalar()), field('total', scalar('UInt64')), field('memo', scalar()), field('details', wrap('list', local('detail'))), field('dedup', wrap('set', local('detail'))), field('amounts', wrap('list', scalar('UInt64'))), field('unique_amounts', wrap('set', scalar('UInt64'))), field('amounts_from_set', wrap('set', scalar('UInt64'))), field('choice', choice)]},
      {contract_id: 'empty', ontology_contract: 'TEST-EMPTY', fields: []}],
    operations: [{operation_id: 'find', operation_ref: 'commerce:' + (id === 'api' ? '' : 'other-') + 'find', request: scalar(), result: local('response')}, {operation_id: 'summarize', operation_ref: 'commerce:' + (id === 'api' ? '' : 'other-') + 'summarize', request: scalar(), result: local('summary')}]};
}
function fixture(t: TestContext, domain = true) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-public-mapping-')); t.after(() => fs.rmSync(folder, {recursive: true, force: true}));
  const source = path.join(folder, 'source'), nodes: string[] = [], edges: string[] = [];
  const write = (p: string, v: unknown) => {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, JSON.stringify(v));};
  const node = (id: string, kind: string, body: any) => {nodes.push(id); write('specs/commerce/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: {description: id, ...body}});};
  const edge = (id: string, relationship: string, from: string, to: string) => {edges.push(id); write('specs/commerce/edges/' + id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id: id, relationship, source_node_id: from, target_node_id: to, scope: 'feature'});};
  node('order', 'Entity', {fields: ['id', 'amount'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-ORDER', properties: ['id', 'amount'].map(name => ({name, ontology_property: 'TEST-ORDER#' + name, meaning: name, type: scalar(name === 'id' ? 'String' : 'UInt64'), cardinality: 'one', identity: name === 'id'}))}});
  for (const id of ['find', 'summarize', 'other-find', 'other-summarize']) node(id, 'Query', {reads: ['order']});
  for (const id of ['api', 'other-api']) {node(id, 'Interface', {typed_contract: api(id)}); for (const member of ['find', 'summarize']) edge(id + '-' + member, 'exposes', id, (id === 'api' ? '' : 'other-') + member);}
  const inputs = [input('response', ref('response'), use('find')), input('order_total', scalar('UInt64')), input('memo', wrap('optional', scalar())), input('fallback', scalar()), ...(domain ? [input('order', named())] : [])];
  const full: any = {schema_version: 'domainspec.typed-mapping/v3', ontology_mapping: 'TEST-FULL', inputs, target: ref('summary'), target_use: use('summarize'), total: true, fields: [
    bind('id', domain ? at('order', 'TEST-ORDER#id') : at('response', 'TEST-PUBLIC#id')), bind('total', at('order_total')), bind('memo', at('memo'), at('fallback')),
    bind('details', at('response', 'TEST-PUBLIC#lines')), bind('dedup', {op: 'to_set', value: at('response', 'TEST-PUBLIC#lines')}),
    bind('amounts', at('response', 'TEST-PUBLIC#lines', 'TEST-PUBLIC#amount')), bind('unique_amounts', {op: 'to_set', value: at('response', 'TEST-PUBLIC#lines', 'TEST-PUBLIC#amount')}),
    bind('amounts_from_set', at('response', 'TEST-PUBLIC#unique', 'TEST-PUBLIC#amount')), bind('choice', at('response', 'TEST-PUBLIC#choice'))]};
  const contracts: Record<string, any> = {
    full, partial: {...full, ontology_mapping: 'TEST-PARTIAL', total: false, fields: [bind('id', at('response', 'TEST-PUBLIC#id'))]},
    empty: {...full, ontology_mapping: 'TEST-EMPTY-MAP', inputs: [], target: ref('empty'), target_use: null, fields: []},
    foreign: {...full, ontology_mapping: 'TEST-FOREIGN', inputs: [input('foreign', ref('response', 'other-api'), use('find', 'result', 'other-api'))], total: false, fields: [bind('id', at('foreign', 'TEST-PUBLIC#id'))]},
    sum: {...full, ontology_mapping: 'TEST-SUM', inputs: [input('choice', qualifyPublicType(choice, 'commerce:api'))], total: false, fields: [bind('choice', at('choice'))]},
  };
  if (domain) {
    contracts.domain = {...full, ontology_mapping: 'TEST-DOMAIN', target: named(), target_use: null, fields: [bind('id', at('response', 'TEST-PUBLIC#id')), bind('amount', at('order_total'))]};
    contracts['domain-only'] = {...contracts.domain, ontology_mapping: 'TEST-DOMAIN-ONLY', inputs: [input('order', named()), input('order_total', scalar('UInt64'))], fields: [bind('id', at('order', 'TEST-ORDER#id')), bind('amount', at('order_total'))]};
    contracts['domain-empty'] = {...contracts['domain-only'], ontology_mapping: 'TEST-DOMAIN-EMPTY', inputs: [], total: false, fields: []};
  }
  for (const [id, contract] of Object.entries(contracts)) {const target = contract.target.kind === 'named' ? 'order' : 'api'; node('map-' + id, 'Mapping', {target: 'commerce:' + target, typed_contract: contract}); edge('map-' + id + '-target', 'maps', 'map-' + id, target);}
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'public-mapping', features: ['commerce'], cross_feature_edges: []}); write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges});
  const graph = loadCompiledProjectGraph(source), graph_sha256 = createCompiledProjectCertificate(graph).graph_sha256;
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256}, boundaryContract);
  const fields = domain ? compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256, roots: ['commerce:order'], bindings: []}, sources.field_contract) : null;
  const selection: any = {schema_version: PYTHON_PUBLIC_MAPPING_VERSION, language: 'python', boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null, module_root: 'commerce', roots: Object.keys(contracts).map(id => 'commerce:map-' + id)};
  const plan = (s = selection, src = sources) => planConfiguredPythonPublicMappings(graph, boundary, fields, s, src);
  return {folder, source, graph, boundary, fields, contracts, selection, plan};
}
type Plan = ReturnType<typeof planConfiguredPythonPublicMappings>;
function observe(f: ReturnType<typeof fixture>, plan: Plan, original = plan) {
  const interfaces = Object.fromEntries(original.mappings.flatMap(m => m.interfaces.map(i => [i.source.selector, {contract: i.contract, source: {relative_path: i.source.relative_path, sha256: i.source.sha256}}])));
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', path.join(import.meta.dirname, 'python-public-mapping-observer.py')], {encoding: 'utf8', maxBuffer: 4 * 1024 * 1024,
    input: JSON.stringify({root: path.join(f.folder, 'native'), plan, selection: original.selection, mappings: original.mappings, interfaces, model: f.fields?.model ?? null,
      certificate: original.certificate, graph_sha256: original.certificate.graph_sha256, boundary_sha256: original.boundary_sha256, field_compilation_sha256: original.field_compilation_sha256, source_digests: original.source_digests})});
  return result;
}
function native(f: ReturnType<typeof fixture>, plans: Plan[], mutate?: (file: string, content: string) => string, audit = true) {
  const root = path.join(f.folder, 'native');
  if (audit && !mutate) for (const plan of plans) {
    const modules = resolvePythonModules(plan.artifacts, plan.selection.module_root.replaceAll('-', '_'));
    assert.equal(modules.length, plan.artifacts.length);
    for (const module of plan.modules) {const closure = selectPythonModuleClosure(modules, [module.relative_path]); assert.ok(closure.some(m => m.relative_path === module.provider_path));}
  }
  for (const p of plans) for (const a of p.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, mutate ? mutate(a.relative_path, a.content) : a.content);}
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', path.join(project, 'impl/cli/test/generation/python-public-mapping-runtime.py')], {encoding: 'utf8', input: JSON.stringify({root, plans, domain: f.fields !== null}), maxBuffer: 4 * 1024 * 1024});
  if (audit && !mutate && result.status === 0) for (const plan of plans) {const observed = observe(f, plan); assert.equal(observed.status, 0, observed.stdout + observed.stderr); assert.equal(JSON.parse(observed.stdout).whole_source, true);}
  return result;
}

test('Python public Mapping binds checked source, Interface dependencies, configuration and exact candidate identities', t => {
  const f = fixture(t), before = canonicalJson(f.graph), p = f.plan(); assert.deepEqual(f.plan(), p); assert.equal(canonicalJson(f.graph), before);
  assert.deepEqual(p.interfaces.map(i => i.selector), ['commerce:api', 'commerce:other-api']);
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content)); assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  const only = f.plan({...f.selection, roots: ['commerce:map-domain-only', 'commerce:map-domain-empty']}); assert.equal(only.interfaces.length, 0); assert.equal(only.artifacts.some(a => a.relative_path.includes('/interfaces/')), false);
  for (const patch of [{language: 'typescript'}, {roots: []}, {roots: ['commerce:api']}, {roots: ['commerce:map-full', 'commerce:map-full']}, {module_root: 'typing'}, {module_root: '../outside'}, {module_root: 'commerce\n'}, {extra: 1}, {boundary_sha256: '0'.repeat(64)}, {field_compilation_sha256: null}]) assert.throws(() => f.plan({...f.selection, ...patch}));
  for (const key of Object.keys(sources)) assert.throws(() => f.plan(f.selection, {...sources, [key]: (sources as any)[key] + ' '}), /source drift/);
  let effects = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {effects++; return [];} }); assert.throws(() => f.plan(active)); assert.equal(effects, 0);
  assert.throws(() => planConfiguredPythonPublicMappings(structuredClone(f.graph), f.boundary, f.fields, f.selection, sources));
  assert.throws(() => renderPythonPublicMapping(structuredClone(p.mappings[0]!), f.fields, [], '...runtime'), /unregistered Mapping/);
  fs.renameSync(f.source, f.source + '-moved'); assert.deepEqual(f.plan(), p);
});

test('native public Mapping preserves exact Interface types and explicit pure projection across minimal, domain and relocated packages', t => {
  for (const domain of [false, true]) {const f = fixture(t, domain); const plans = [f.plan(), f.plan({...f.selection, module_root: 'relocated/package-root'})]; if (domain) plans.push(f.plan({...f.selection, module_root: 'domain-only', roots: ['commerce:map-domain-only', 'commerce:map-domain-empty']})); const result = native(f, plans); assert.equal(result.status, 0, result.stdout + result.stderr);}
});

test('public Mapping runtime detects native path, numeric, input normalization and optional fallback regressions', t => {
  const f = fixture(t), plan = f.plan();
  const changes = [
    (s: string) => s.replace('v1 = p1', 'v1 = 1'),
    (s: string) => s.replace('v0 = p4["id"]', 'v0 = p0["id"]'),
    (s: string) => s.replace('if v2 is None:', 'if not v2:'),
    (s: string) => s.replace(/p4 = _fact_type[0-9]+\.normalize\(parameters\["order"\]\)/, 'p4 = parameters["order"]'),
  ];
  for (const change of changes) {let changed = false; const result = native(f, [plan], (file, content) => {if (!file.endsWith('/_providers/map_full.py')) return content; const next = change(content); assert.notEqual(next, content, 'mutation selector must match'); changed = true; return next;}); assert.equal(changed, true); assert.notEqual(result.status, 0, 'SEMANTIC_MUTANT_SURVIVED'); assert.match(result.stderr, /AssertionError|MAPPING_INPUT/);}
});

test('Python public Mapping rejects wrong Interface imports at generation and native import boundaries', t => {
  const f = fixture(t), plan = f.plan(), checked = plan.mappings.find(m => m.selector === 'commerce:map-full')!;
  const module = plan.modules.find(m => m.selector === checked.selector)!;
  const imports = module.descriptor.imports.map((i, n) => ({...i, alias: '_api' + n, descriptor: plan.interfaces.find(api => api.selector === i.selector)!.descriptor}));
  for (const patch of [{selector: 'commerce:other-api'}, {contract_sha256: '0'.repeat(64)}, {graph_sha256: '0'.repeat(64)}, {field_compilation_sha256: null}]) assert.throws(() => renderPythonPublicMapping(checked, f.fields, imports.map(i => ({...i, descriptor: {...i.descriptor, ...patch}})), '...runtime'), /descriptor mismatch/);
  assert.throws(() => renderPythonPublicMapping(checked, f.fields, [], '...runtime'), /exact Interface imports/);
  const swapped = native(f, [plan], (file, content) => file.endsWith('/_providers/map_full.py') ? content.replace('import api as _api0', 'import other_api as _api0') : content);
  assert.notEqual(swapped.status, 0); assert.match(swapped.stderr, /MAPPING_INTERFACE_BINDING/);
  const drifted = native(f, [plan], (file, content) => file.endsWith('/interfaces/api.py') ? content.replace(/("graph_sha256"\s*:\s*)"[a-f0-9]+"/, '$1"' + '0'.repeat(64) + '"') : content);
  assert.notEqual(drifted.status, 0); assert.match(drifted.stderr, /MAPPING_INTERFACE_BINDING/);
});

test('whole-source public Mapping observer rejects runtime-passing controls with refreshed artifact and descriptor hashes', t => {
  const f = fixture(t), original = f.plan();
  const controls = [
    {label: 'extra callable', suffix: '/_providers/map_full.py', change: (s: string) => s + '\ndef hidden():\n    return 1\n'},
    {label: 'extra import', suffix: '/_providers/map_full.py', change: (s: string) => s + '\nimport os as _unused_os\n'},
    {label: 'unreachable effect', suffix: '/_providers/map_full.py', change: (s: string) => s.replace('    return _cast(_ReadModel,', '    if False:\n        print("hidden")\n    return _cast(_ReadModel,')},
    {label: 'weakened parameter annotation', suffix: '/_providers/map_full.py', change: (s: string) => s.replace('"fallback": str', '"fallback": object')},
    {label: 'disabled Interface guard', suffix: '/_providers/map_full.py', change: (s: string) => s.replace(/if (_api0\.descriptor[^\n]+):/, 'if False and ($1):')},
    {label: 'extra binding method', suffix: '/mappings/map_full.py', change: (s: string) => s.replace('    @property', '    def hidden(self):\n        return 1\n\n    @property')},
    {label: 'package initializer', suffix: '/mappings/__init__.py', change: (s: string) => s + 'hidden_state = 1\n'},
    {label: 'support addition', suffix: '/runtime/facts.py', change: (s: string) => s + '\ndef hidden():\n    return 1\n'},
    {label: 'Interface addition', suffix: '/interfaces/api.py', change: (s: string) => s + '\ndef hidden():\n    return 1\n'},
  ];
  for (const control of controls) {
    const candidate = structuredClone(original) as any;
    const artifact = candidate.artifacts.find((a: any) => a.relative_path.endsWith(control.suffix)); assert.ok(artifact, control.label);
    const previous = artifact.content; artifact.content = control.change(previous); assert.notEqual(artifact.content, previous, control.label);
    const refresh = (a: any) => {a.sha256 = sha256(a.content); a.size_bytes = Buffer.byteLength(a.content);}; refresh(artifact);
    const replacements = new Map<string, string>();
    for (const api of candidate.interfaces) {const a = candidate.artifacts.find((a: any) => a.relative_path === api.relative_path); replacements.set(api.artifact_sha256, a.sha256); api.artifact_sha256 = a.sha256;}
    for (const module of candidate.modules) {
      const descriptor = module.descriptor, oldDescriptor = descriptor.descriptor_sha256, oldProvider = descriptor.provider_sha256;
      descriptor.provider_sha256 = candidate.artifacts.find((a: any) => a.relative_path === module.provider_path).sha256;
      replacements.set(oldProvider, descriptor.provider_sha256);
      for (const i of descriptor.imports) i.artifact_sha256 = replacements.get(i.artifact_sha256) ?? i.artifact_sha256;
      const {descriptor_sha256, ...body} = descriptor; descriptor.descriptor_sha256 = sha256(canonicalJson(body)); replacements.set(oldDescriptor, descriptor.descriptor_sha256);
      const wrapper = candidate.artifacts.find((a: any) => a.relative_path === module.relative_path);
      for (const [before, after] of replacements) if (before !== after) wrapper.content = wrapper.content.replaceAll(before, after);
      refresh(wrapper);
    }
    const {plan_sha256, ...body} = candidate; candidate.plan_sha256 = sha256(canonicalJson(body));
    const runtime = native(f, [candidate], undefined, false); assert.equal(runtime.status, 0, control.label + ': must survive runtime\n' + runtime.stderr);
    const result = observe(f, candidate, original); assert.notEqual(result.status, 0, control.label + ': observer must reject');
    assert.match(result.stderr, /PYTHON_PUBLIC_MAPPING_OBSERVER:(AST|nonempty initializer|support bytes)/, control.label + ': reject source, not stale metadata');
  }
});
