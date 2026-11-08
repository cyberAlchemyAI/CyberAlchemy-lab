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
import {planConfiguredPythonInterfaces, PYTHON_INTERFACE_VERSION} from '../../src/generation/configured-python-interfaces.ts';
import {acceptsInterfaceVersion} from '../../src/typed-backend/interface-version-policy.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const project = path.resolve(import.meta.dirname, '../../../..'), pkg = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes = (p: string) => fs.readFileSync(p, 'utf8');
const sources = {configuration: bytes(path.join(pkg, 'configuration.json')),
  base: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  python: bytes(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')),
  interface_contract: bytes(path.join(pkg, 'named-interface-contract.json')), version_contract: bytes(path.join(pkg, 'interface-version-policy-contract.json')),
  field_contract: bytes(path.join(project, 'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'))};
const boundaryContract = bytes(path.join(project, 'development/reconciliation-v1/contracts/composition-boundary.json'));
const scalar = (name = 'String'): any => ({kind: 'scalar', name});
const local = (contract_id: string): any => ({kind: 'contract', contract_id});
const wrap = (kind: string, element: any): any => ({kind, element});
const field = (name: string, type: any) => ({name, type, ontology_field: 'TEST-PUBLIC#' + name, meaning: 'Public ' + name + '; preserve RULE_INPUT literal.'});
const property = (name: string, type: any) => ({name, type, ontology_property: 'TEST-MONEY#' + name, identity: false, cardinality: 'one', meaning: name});
function contract(): any {
  const response = {contract_id: 'response', ontology_contract: 'TEST-RESPONSE', fields: [field('id', scalar()), field('total', scalar('UInt64')), field('enabled', scalar('Bool')),
    field('memo', wrap('optional', scalar())), field('tags', wrap('set', scalar())), field('lines', wrap('list', scalar('UInt64'))),
    field('choice', {kind: 'sum', variants: [{name: 'None', ontology_variant: 'TEST-CHOICE#None', payload: null}, {name: 'Some', ontology_variant: 'TEST-CHOICE#Some', payload: local('detail')}]})]};
  return {schema_version: 'domainspec.typed-interface/v1', ontology_interface: 'TEST-API', boundary_kind: 'external',
    version_policy: {schema_version: 'domainspec.interface-version-policy/v1', mode: 'backward', direction: 'consumer-to-provider', provider_version: '1.2.0'},
    contracts: [{contract_id: 'request', ontology_contract: 'TEST-REQUEST', fields: [field('id', scalar())]}, response,
      {...structuredClone(response), contract_id: 'shadow-response', ontology_contract: 'TEST-SHADOW'},
      {contract_id: 'detail', ontology_contract: 'TEST-DETAIL', fields: [field('amount', scalar('UInt64'))]}, {contract_id: 'empty', ontology_contract: 'TEST-EMPTY', fields: []}],
    operations: [{operation_id: 'submit-order', operation_ref: 'alpha:settle', request: local('request'), result: local('response')},
      {operation_id: 'find', operation_ref: 'alpha:find', request: scalar('UInt64'), result: wrap('optional', local('response'))}]};
}
function fixture(t: TestContext, domain: boolean | 'entity' = false, policy?: any) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-interface-')); t.after(() => fs.rmSync(folder, {recursive: true, force: true}));
  const source = path.join(folder, 'source'); fs.cpSync(path.join(project, 'impl/cli/fixtures/input-roots/canonical-project'), source, {recursive: true});
  const read = (p: string) => JSON.parse(bytes(path.join(source, p)));
  const write = (p: string, v: unknown) => fs.writeFileSync(path.join(source, p), JSON.stringify(v));
  const feature = read('specs/alpha/feature.json'), authored = contract(); if (policy) authored.version_policy = policy;
  const node = (id: string, kind: string, body: any) => {feature.nodes.push(id); write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind, body: {description: id, ...body}});};
  node('find', 'Query', {reads: ['customer']}); feature.edges.push('api-exposes-find');
  write('specs/alpha/edges/api-exposes-find.json', {schema_version: 'domainspec.edge/v1', edge_id: 'api-exposes-find', feature_id: 'alpha', relationship: 'exposes', source_node_id: 'settlement-api', target_node_id: 'find', scope: 'feature'});
  if (domain) {
    node('money-valid', 'Rule', {predicate: 'structured:domainspec.typed-rule/v1', typed_contract: {schema_version: 'domainspec.typed-rule/v1', ontology_rule: 'TEST-MONEY-VALID', parameters: [{name: 'amount', type: scalar('UInt64')}], expression: {op: 'eq', left: {op: 'literal', type: 'Bool', value: true}, right: {op: 'literal', type: 'Bool', value: false}}}});
    node('money', domain === 'entity' ? 'Entity' : 'Value Object', {fields: ['amount', 'currency'], ...(domain === 'entity' ? {} : {invariant_refs: ['alpha:money-valid']}), typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-MONEY', properties: [{...property('amount', scalar('UInt64')), identity: domain === 'entity'}, property('currency', scalar())]}});
    node('status', 'Enum', {values: ['Ready', 'Draft'], typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'TEST-STATUS', variants: [{name: 'Ready', ontology_variant: 'TEST-STATUS#Ready', payload: null}, {name: 'Draft', ontology_variant: 'TEST-STATUS#Draft', payload: {kind: 'named', selector: 'alpha:money'}}]}});
    authored.contracts.find((c: any) => c.contract_id === 'detail').fields.push(field('money', {kind: 'named', selector: 'alpha:money'}), field('status', {kind: 'named', selector: 'alpha:status'}));
  }
  const api = read('specs/alpha/nodes/settlement-api.json'); api.body = {description: 'Public API', typed_contract: authored}; write('specs/alpha/nodes/settlement-api.json', api); write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(source), graph_sha256 = createCompiledProjectCertificate(graph).graph_sha256;
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256}, boundaryContract);
  const fields = domain ? compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256, roots: ['alpha:money', 'alpha:status'], bindings: []}, sources.field_contract) : null;
  const selection: any = {schema_version: PYTHON_INTERFACE_VERSION, language: 'python', boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null, module_root: 'commerce', roots: ['alpha:settlement-api']};
  const plan = (s = selection, src = sources) => planConfiguredPythonInterfaces(graph, boundary, fields, s, src);
  return {folder, graph, boundary, fields, selection, plan, authored};
}
type Plan = ReturnType<typeof planConfiguredPythonInterfaces>;
const response = (domain: boolean): any => ({id: 'order-1', total: '18446744073709551615', enabled: true, tags: ['z', 'a'], lines: ['2', '2', '1'], choice: {variant: 'Some', payload: {amount: '9007199254740993', ...(domain ? {money: {amount: '9007199254740993', currency: 'GBP'}, status: {variant: 'Draft', payload: {amount: 0, currency: 'USD'}}} : {})}}});
function observe(f: ReturnType<typeof fixture>, plan: Plan) {
  const interfaces = Object.fromEntries(f.graph.nodes.filter(n => n.kind === 'Interface' && n.body.typed_contract).map(n => {
    const relative_path = `specs/${n.feature_id}/nodes/${n.node_id}.json`;
    return [n.selector, {contract: n.body.typed_contract, source: {relative_path, sha256: f.graph.source_manifest.sources.find(s => s.relative_path === relative_path)!.sha256}}];
  }));
  return spawnSync('/usr/bin/python3', ['-I', '-B', path.join(project, 'impl/cli/test/generation/python-interface-observer.py')], {encoding: 'utf8', input: JSON.stringify({root: path.join(f.folder, 'native'), plan, interfaces, model: f.fields?.model ?? null, graph_sha256: f.boundary.certificate.graph_sha256, boundary_sha256: f.boundary.boundary_sha256, field_compilation_sha256: f.fields?.compilation_sha256 ?? null}), maxBuffer: 4 * 1024 * 1024});
}
function native(f: ReturnType<typeof fixture>, plans: Plan[], mutate?: (file: string, content: string) => string, audit = true) {
  const root = path.join(f.folder, 'native');
  for (const p of plans) for (const a of p.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, mutate ? mutate(a.relative_path, a.content) : a.content);}
  const vectors: unknown[] = [null, true, 12, '', '1.2', '01.2.0', '1.02.0', '1.2.00', '1.2.0\n', '1.2.0 ', '１.2.0', '1.2.0-alpha', '1.2.0+build', '1..0'];
  for (const major of ['0', '1', '2', '9'.repeat(64)]) for (const minor of ['0', '1', '2', '3', '9'.repeat(64)]) for (const patch of ['0', '1', '9'.repeat(64)]) vectors.push(`${major}.${minor}.${patch}`);
  vectors.push('1.' + '1'.repeat(65) + '.0');
  const policy = f.authored.version_policy;
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', path.join(project, 'impl/cli/test/generation/python-interface-runtime.py')], {encoding: 'utf8', input: JSON.stringify({root, modules: plans.flatMap(p => p.modules), response: response(f.fields !== null), versions: vectors.map(value => ({value, accepted: acceptsInterfaceVersion(policy, value)})), model: f.fields?.model ?? null}), maxBuffer: 4 * 1024 * 1024});
  if (result.status === 0 && audit) for (const plan of plans) {const observed = observe(f, plan); assert.equal(observed.status, 0, observed.stdout + observed.stderr); assert.equal(JSON.parse(observed.stdout).whole_source, true);}
  return result;
}

test('Python Interface plans bind source/graph/profile, relocate deterministically and reject active or forged selections', t => {
  const f = fixture(t), before = canonicalJson(f.graph), p = f.plan(); assert.deepEqual(f.plan(), p); assert.equal(canonicalJson(f.graph), before);
  assert.equal(Object.isFrozen(p.modules[0]!.descriptor.contract.contracts[0]!.fields), true);
  for (const a of p.artifacts) {assert.equal(a.sha256, sha256(a.content)); assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  const {plan_sha256, ...body} = p; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  for (const patch of [{language: 'rust'}, {roots: []}, {roots: ['alpha:settlement-api', 'alpha:settlement-api']}, {roots: ['alpha:customer']}, {module_root: '../outside'}, {module_root: 'typing'}, {module_root: 'commerce\n'}, {boundary_sha256: '0'.repeat(64)}, {field_compilation_sha256: '0'.repeat(64)}, {extra: true}]) assert.throws(() => f.plan({...f.selection, ...patch}));
  let effects = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {effects++; return ['alpha:settlement-api'];}}); assert.throws(() => f.plan(active)); assert.equal(effects, 0);
  const sparse = {...f.selection, roots: new Array(1)}; assert.throws(() => f.plan(sparse));
  for (const key of Object.keys(sources)) assert.throws(() => f.plan(f.selection, {...sources, [key]: (sources as any)[key] + ' '}), /source drift/);
  assert.throws(() => planConfiguredPythonInterfaces(structuredClone(f.graph), f.boundary, f.fields, f.selection, sources));
  const other = fixture(t, false, {...f.authored.version_policy, provider_version: '1.2.1'}); assert.throws(() => planConfiguredPythonInterfaces(other.graph, f.boundary, null, f.selection, sources), /cross-graph/);
  const domain = fixture(t, true);
  assert.throws(() => planConfiguredPythonInterfaces(domain.graph, domain.boundary, null, {...domain.selection, field_compilation_sha256: null}, sources), /unresolved domain value/);
  assert.throws(() => planConfiguredPythonInterfaces(domain.graph, domain.boundary, structuredClone(domain.fields), domain.selection, sources));
  assert.throws(() => fixture(t, 'entity').plan(), /Entity snapshot leak/);
});

test('native Python Interface preserves public identity, immutable exact values, names and structural async typing in minimal and domain contexts', t => {
  for (const domain of [false, true]) {const f = fixture(t, domain); const result = native(f, [f.plan(), f.plan({...f.selection, module_root: 'relocated/package-root'})]); assert.equal(result.status, 0, result.stdout + result.stderr);}
});

test('Python Interface implements exact and backward version policies without numeric precision loss or coercion', t => {
  for (const mode of ['exact', 'backward']) for (const version of ['1.2.0', '1.' + '9'.repeat(64) + '.' + '9'.repeat(64)]) {
    const f = fixture(t, false, {schema_version: 'domainspec.interface-version-policy/v1', mode, direction: 'consumer-to-provider', provider_version: version}); const result = native(f, [f.plan()]); assert.equal(result.status, 0, result.stdout + result.stderr);
  }
});

test('native Interface controls detect identity collapse, list/set confusion, wrong async signature and permissive versions', t => {
  const f = fixture(t), p = f.plan();
  const changes = [
    (s: string) => s.replace('_facts.record_fact("alpha:settlement-api", "shadow-response",', '_facts.record_fact("alpha:settlement-api", "response",'),
    (s: string) => s.replace(/(_facts.sequence_fact\([^\n]+), False\)/, '$1, True)'),
    (s: string) => s.replaceAll('_Awaitable[', 'list['),
    (s: string) => s.replace('return parts[0] == provider[0] and ', 'return '),
  ];
  for (const change of changes) {let changed = false; const result = native(f, [p], (file, content) => {if (!file.endsWith('/settlement_api.py')) return content; const next = change(content); assert.notEqual(next, content); changed = true; return next;}); assert.equal(changed, true); assert.notEqual(result.status, 0, 'SEMANTIC_MUTANT_SURVIVED'); assert.match(result.stderr, /AssertionError|INTERFACE_VALUE/);}
});

test('whole-source Interface observation rejects runtime-passing changes with refreshed artifact and plan hashes', t => {
  const changes: [string, (s: string) => string][] = [
    ['module', s => s + '\ndef hidden():\n    return 42\n'],
    ['module', s => s + '\nimport os as _undeclared_import\n'],
    ['module', s => s + '\nif False:\n    print("unreachable effect")\n'],
    ['module', s => s.replace('            return self._protocol.normalize(value)', '            if value is self:\n                print("hidden effect")\n            return self._protocol.normalize(value)')],
    ['module', s => s.replace(/("_Public[0-9]+Input", \{"id": )str/, '$1int')],
    ['initializer', s => s + 'unclaimed_state = 1\n'],
    ['support', s => s + '\ndef unclaimed_support():\n    return None\n'],
  ];
  for (const [target, change] of changes) {
    const f = fixture(t, true), plan = structuredClone(f.plan());
    const a = plan.artifacts.find(a => target === 'initializer' ? a.relative_path === 'commerce/__init__.py' : target === 'support' ? a.relative_path.endsWith('/runtime/facts.py') : a.relative_path.endsWith('/settlement_api.py'))!;
    const prior = a.content; a.content = change(a.content); assert.notEqual(a.content, prior, 'mutation must change bytes'); a.sha256 = sha256(a.content); a.size_bytes = Buffer.byteLength(a.content);
    if (target === 'module') plan.modules[0]!.artifact_sha256 = a.sha256;
    const {plan_sha256: _, ...body} = plan; plan.plan_sha256 = sha256(canonicalJson(body));
    const runtime = native(f, [plan], undefined, false); assert.equal(runtime.status, 0, runtime.stdout + runtime.stderr);
    const observed = observe(f, plan); assert.notEqual(observed.status, 0, 'RUNTIME_PASSING_SOURCE_MUTANT_SURVIVED'); assert.match(observed.stderr, /PYTHON_INTERFACE_OBSERVER:(AST|nonempty package initializer|support bytes)/);
  }
});
