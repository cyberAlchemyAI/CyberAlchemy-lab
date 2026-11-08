import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test, {type TestContext} from 'node:test';
import {decodeNamedInterface, checkInterfacePublicClosure, NAMED_INTERFACE_DEFINITION_SHA256} from '../../src/typed-backend/interface.ts';
import {renderNamedInterfaceSource} from '../../src/generation/named-interface-source.ts';
import {loadCompiledProjectGraph, selectCompiledProjectNode, decodeBody} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const root = path.resolve(import.meta.dirname, '../../../..');
const scalar = (name = 'String'): any => ({kind: 'scalar', name});
const local = (contract_id: string): any => ({kind: 'contract', contract_id});
const wrap = (kind: string, element: any): any => ({kind, element});
const field = (name: string, type: any): any => ({name, ontology_field: 'TEST-PUBLIC#' + name, meaning: name + ' public value.', type});
function contract(): any {
  const response = {contract_id: 'response', ontology_contract: 'TEST-RESPONSE', fields: [field('id', scalar()), field('total', scalar('UInt64')), field('memo', wrap('optional', scalar())), field('tags', wrap('set', scalar())), field('lines', wrap('list', scalar('UInt64'))),
    field('choice', {kind: 'sum', variants: [{name: 'None', ontology_variant: 'TEST-CHOICE#None', payload: null}, {name: 'Some', ontology_variant: 'TEST-CHOICE#Some', payload: local('detail')}]})]};
  return {schema_version: 'domainspec.typed-interface/v1', ontology_interface: 'TEST-SETTLEMENT-API', boundary_kind: 'external',
    version_policy: {schema_version: 'domainspec.interface-version-policy/v1', mode: 'backward', direction: 'consumer-to-provider', provider_version: '1.2.0'},
    contracts: [{contract_id: 'request', ontology_contract: 'TEST-REQUEST', fields: [field('id', scalar())]}, response,
      {...structuredClone(response), contract_id: 'shadow-response', ontology_contract: 'TEST-SHADOW-RESPONSE'},
      {contract_id: 'detail', ontology_contract: 'TEST-DETAIL', fields: [field('amount', scalar('UInt64'))]},
      {contract_id: 'empty', ontology_contract: 'TEST-EMPTY', fields: []}],
    operations: [{operation_id: 'settle', operation_ref: 'alpha:settle', request: local('request'), result: local('response')},
      {operation_id: 'find', operation_ref: 'alpha:find', request: scalar('UInt64'), result: wrap('optional', local('response'))}]};
}
function fixture(t: TestContext, source = contract()) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-named-interface-'));
  t.after(() => fs.rmSync(folder, {recursive: true, force: true}));
  fs.cpSync(path.join(root, 'impl/cli/fixtures/input-roots/canonical-project'), folder, {recursive: true});
  const read = (relative: string) => JSON.parse(fs.readFileSync(path.join(folder, relative), 'utf8'));
  const write = (relative: string, value: unknown) => fs.writeFileSync(path.join(folder, relative), JSON.stringify(value, null, 2) + '\n');
  const feature = read('specs/alpha/feature.json'); feature.nodes.push('find'); feature.edges.push('api-exposes-find');
  write('specs/alpha/feature.json', feature);
  write('specs/alpha/nodes/find.json', {schema_version: 'domainspec.node/v1', node_id: 'find', feature_id: 'alpha', kind: 'Query', body: {description: 'Find settlement.', reads: ['customer']}});
  write('specs/alpha/edges/api-exposes-find.json', {schema_version: 'domainspec.edge/v1', edge_id: 'api-exposes-find', feature_id: 'alpha', relationship: 'exposes', source_node_id: 'settlement-api', target_node_id: 'find', scope: 'feature'});
  const api = read('specs/alpha/nodes/settlement-api.json'); api.body = {description: 'Named public boundary.', typed_contract: source}; write('specs/alpha/nodes/settlement-api.json', api);
  return {folder, read, write, graph: () => loadCompiledProjectGraph(folder)};
}
function native(t: TestContext, sources: Record<string, string>) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-named-interface-native-'));
  t.after(() => fs.rmSync(folder, {recursive: true, force: true}));
  for (const [name, content] of Object.entries(sources)) fs.writeFileSync(path.join(folder, name + '.ts'), content);
  const chain = JSON.parse(fs.readFileSync(path.resolve(root, '../../toolchains/node-typescript/toolchain.json'), 'utf8'));
  const image = nativeToolchainImage(chain.container_image);
  try {
    execFileSync('docker', ['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', `${process.getuid!()}:${process.getgid!()}`, '--mount', `type=bind,source=${folder},target=${folder}`, '--workdir', folder, image, 'tsc', '--ignoreConfig', '--strict', '--noUncheckedIndexedAccess', '--declaration', '--target', 'ES2022', '--module', 'commonjs', '--outDir', path.join(folder, 'js'), ...Object.keys(sources).map(n => n + '.ts')], {stdio: 'pipe'});
  } catch (error: any) {throw new Error(String(error.stdout) + String(error.stderr));}
  const require = createRequire(import.meta.url);
  return (name: string): any => require(path.join(folder, 'js', name + '.js'));
}
const response = () => ({id: 'settlement-1', total: '18446744073709551615', tags: ['z', 'a'], lines: ['2', '2', '1'], choice: {variant: 'Some', payload: {amount: '9007199254740993'}}});

test('named public source is closed, owned, definition-bound and preserves shared contract identity', () => {
  const source = contract(), decoded = decodeNamedInterface(source);
  assert.deepEqual(decoded, source); assert.notEqual(decoded, source);
  assert.equal(Object.isFrozen(decoded.contracts[0]!.fields), true);
  assert.equal(sha256(fs.readFileSync(path.join(root, 'development/reconciliation-v1/profile-compiler-reconciliation/named-interface-contract.json'), 'utf8')), NAMED_INTERFACE_DEFINITION_SHA256);
  for (const mutate of [
    (c: any) => c.extra = true, (c: any) => c.schema_version = 'future', (c: any) => c.version_policy.provider_version = '1',
    (c: any) => c.contracts.push(c.contracts[0]), (c: any) => c.contracts[0].identity = 'id', (c: any) => c.contracts[0].fields.push(c.contracts[0].fields[0]),
    (c: any) => c.operations[0].result = local('missing'), (c: any) => c.contracts[0].fields[0].type = local('request'),
    (c: any) => c.operations.push(c.operations[0]), (c: any) => c.contracts[0].fields[0].type = wrap('optional', wrap('optional', scalar())),
  ]) {const c = contract(); mutate(c); assert.throws(() => decodeNamedInterface(c));}
  let calls = 0; const c = contract(); Object.defineProperty(c.contracts[0].fields[0], 'type', {get() {calls++; return scalar();}, enumerable: true});
  assert.throws(() => decodeNamedInterface(c)); assert.equal(calls, 0);
  const sparse = contract(); delete sparse.contracts[1]; assert.throws(() => decodeNamedInterface(sparse));
});

test('checked graph retains exact exposes closure; legacy generation, runtime and proof reject the successor', t => {
  const f = fixture(t), graph = f.graph(), node = selectCompiledProjectNode(graph, 'alpha:settlement-api');
  assert.deepEqual(graph.nodes.filter(n => n.kind === 'Interface').map(n => n.selector), ['alpha:settlement-api']);
  for (const language of ['typescript', 'python', 'rust'] as const) assert.throws(() => planInstantiation(node, language), /MTCLI_INTERFACE_PROFILE_REQUIRED/);
  assert.throws(() => createMetaTypeFormalizationProjection(graph), /named public contracts|successor formalization/);
  assert.throws(() => runInMemoryProject(f.folder, {schema_version: 'domainspec.runtime-invocation/v1', invocation_id: 'named-interface', provider: 'in-memory-v1', steps: [{step_id: 'api', selector: node.feature_id + ':' + node.node_id, input: {requested_version: '1.2.0'}}]}), /typed Interface requires/);
  const feature = f.read('specs/alpha/feature.json'); feature.edges = feature.edges.filter((e: string) => e !== 'api-exposes-find'); f.write('specs/alpha/feature.json', feature);
  assert.throws(() => f.graph(), /lacks an exposes/);
});

test('native structural interface shares one response, while normalization is pure exact and deeply owned', async t => {
  const authored = contract(); authored.contracts[0].fields[0].meaning = 'Preserve RULE_INPUT and INTERFACE_VALUE as authored language.';
  const f = fixture(t, authored), graph = f.graph(), before = canonicalJson(graph), rendered = renderNamedInterfaceSource(graph, 'alpha:settlement-api');
  assert.equal(canonicalJson(graph), before); assert.deepEqual(renderNamedInterfaceSource(graph, 'alpha:settlement-api'), rendered);
  assert.equal(rendered.content.includes('class '), false);
  const load = native(t, {api: rendered.content}), api = load('api'), input = response();
  const value = api.publicContracts.response.normalize(input);
  assert.equal(value.total, 18446744073709551615n); assert.equal(value.choice.payload.amount, 9007199254740993n);
  assert.deepEqual(value.lines, [2n, 2n, 1n]); assert.deepEqual(value.tags, ['a', 'z']); assert.equal(value.memo, null);
  assert.ok(Object.isFrozen(value.choice.payload)); assert.ok(Object.isFrozen(value.tags));
  input.id = 'changed'; assert.equal(value.id, 'settlement-1');
  assert.equal(api.endpointValues.settle.result, api.publicContracts.response);
  assert.deepEqual(api.endpointValues.find.result.normalize(response()), value); assert.equal(api.endpointValues.find.result.normalize(null), null);
  assert.notEqual(api.publicContracts.response.key(value), api.publicContracts['shadow-response'].key(value));
  assert.deepEqual(api.publicContracts.empty.normalize({}), {});
  assert.equal(api.acceptsVersion('1.2.0'), true); assert.equal(api.acceptsVersion('1.3.0'), false);
  assert.equal(api.descriptor.contract.operations.length, 2);
  assert.deepEqual(api.descriptor, rendered.descriptor);
  let calls = 0; const port = {settle: async () => {calls++; return value;}, find: async () => value};
  assert.equal(calls, 0); assert.equal(await port.settle(), value); assert.equal(calls, 1);
});

test('native contract normalizers reject coercion, accessors, extra fields, duplicate sets and invalid sums', t => {
  const api = native(t, {api: renderNamedInterfaceSource(fixture(t).graph(), 'alpha:settlement-api').content})('api');
  for (const mutation of [
    (x: any) => x.extra = true, (x: any) => x.total = Number.MAX_SAFE_INTEGER + 1, (x: any) => x.total = '18446744073709551616',
    (x: any) => x.tags = ['a', 'a'], (x: any) => x.choice = {variant: 'None', payload: 1}, (x: any) => x.choice = {variant: 'Some'},
    (x: any) => delete x.lines, (x: any) => x.lines = [, 1],
  ]) {const x = response(); mutation(x); assert.throws(() => api.publicContracts.response.normalize(x), /INTERFACE_VALUE/);}
  let reads = 0; const x = response(); Object.defineProperty(x, 'total', {get() {reads++; return '1';}, enumerable: true});
  assert.throws(() => api.publicContracts.response.normalize(x)); assert.equal(reads, 0);
  assert.throws(() => api.publicContracts.empty.normalize({unexpected: true}));
});

test('native consumer types preserve contract names, member signatures, exact values and readonly fields', t => {
  const source = renderNamedInterfaceSource(fixture(t).graph(), 'alpha:settlement-api').content;
  native(t, {api: source, consumer: `import type {Interface, PublicContracts} from './api';
declare const value:PublicContracts['response'];
const port:Interface={settle:async request=>{const id:string=request.id;return value;},find:async id=>{const exact:bigint=id;return null;}};
const shared:Promise<PublicContracts['response']>=port.settle({id:'x'});
// @ts-expect-error exact endpoint cannot take a coercible string
port.find('1');
// @ts-expect-error public value has no Entity identity function
value.identity();
// @ts-expect-error deeply readonly result
value.lines.push(1n);
// @ts-expect-error exact value is bigint
const lost:number=value.total;
// @ts-expect-error members are readonly arrow-valued properties
port.find=async()=>null;
// @ts-expect-error contract IDs are source identities
type Missing=PublicContracts['Response'];
`});
});

test('public source changes are causal and same-shaped contract identities remain distinct under compiling mutations', t => {
  const f = fixture(t), source = renderNamedInterfaceSource(f.graph(), 'alpha:settlement-api').content;
  const mutants = {
    precision: source.replaceAll('BigInt(input)', 'BigInt(Number(input))'),
    set: source.replace('if(new Set(rows.map(row=>row.key)).size!==rows.length)', 'if(false)'),
    identity: source.replaceAll('rulePart("shadow-response")', 'rulePart("response")'),
  };
  for (const changed of Object.values(mutants)) assert.notEqual(changed, source);
  const load = native(t, {original: source, ...mutants});
  assert.throws(() => load('precision').publicContracts.response.normalize(response()));
  assert.doesNotThrow(() => load('set').publicContracts.response.normalize({...response(), tags: ['a', 'a']}));
  const api = load('identity'), value = api.publicContracts.response.normalize(response());
  assert.equal(api.publicContracts.response.key(value), api.publicContracts['shadow-response'].key(value));
  const before = renderNamedInterfaceSource(f.graph(), 'alpha:settlement-api');
  const data = f.read('specs/alpha/nodes/settlement-api.json'); data.body.typed_contract.version_policy.provider_version = '1.3.0'; f.write('specs/alpha/nodes/settlement-api.json', data);
  const after = renderNamedInterfaceSource(f.graph(), 'alpha:settlement-api');
  assert.notEqual(before.descriptor.contract_sha256, after.descriptor.contract_sha256); assert.notEqual(before.sha256, after.sha256);
});

test('public domain references reject direct and transitive internal Entity snapshots and unresolved values', () => {
  const c = contract(); c.contracts[0].fields[0].type = {kind: 'named', selector: 'alpha:private'};
  const decoded = decodeNamedInterface(c);
  assert.throws(() => checkInterfacePublicClosure(decoded, []), /unresolved domain value/);
  const entity: any = {selector: 'alpha:private', kind: 'Entity', contract: {properties: []}};
  assert.throws(() => checkInterfacePublicClosure(decoded, [entity]), /Entity snapshot leak/);
  c.contracts[0].fields[0].type = {kind: 'named', selector: 'alpha:wrapper'};
  const wrapper: any = {selector: 'alpha:wrapper', kind: 'Value Object', contract: {properties: [{type: {kind: 'named', selector: 'alpha:private'}}]}};
  assert.throws(() => checkInterfacePublicClosure(decodeNamedInterface(c), [wrapper, entity]), /Entity snapshot leak/);
});

test('shared Value Object and Enum values require the same checked exact field graph', t => {
  const c = contract(); c.contracts[0].fields[0].type = {kind: 'named', selector: 'alpha:money'};
  const f = fixture(t, c), feature = f.read('specs/alpha/feature.json'); feature.nodes.push('money', 'public-status'); f.write('specs/alpha/feature.json', feature);
  f.write('specs/alpha/nodes/public-status.json', {schema_version: 'domainspec.node/v1', node_id: 'public-status', feature_id: 'alpha', kind: 'Enum', body: {
    description: 'Shared public status.', values: ['Ready', 'Waiting'], typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'TEST-STATUS', variants: [
      {name: 'Ready', ontology_variant: 'TEST-STATUS#Ready', payload: null}, {name: 'Waiting', ontology_variant: 'TEST-STATUS#Waiting', payload: scalar('UInt64')},
    ]},
  }});
  f.write('specs/alpha/nodes/money.json', {schema_version: 'domainspec.node/v1', node_id: 'money', feature_id: 'alpha', kind: 'Value Object', body: {
    description: 'Shared amount value.', fields: ['units', 'status'], invariant_refs: ['beta:can-complete-settlement'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-MONEY', properties: [
      {name: 'units', ontology_property: 'TEST-MONEY#units', type: scalar('UInt64'), cardinality: 'one', identity: false, meaning: 'Exact units.'},
      {name: 'status', ontology_property: 'TEST-MONEY#status', type: {kind: 'named', selector: 'alpha:public-status'}, cardinality: 'one', identity: false, meaning: 'Status value.'},
    ]},
  }});
  const graph = f.graph(), graph_sha256 = createCompiledProjectCertificate(graph).graph_sha256;
  const definition = fs.readFileSync(path.join(root, 'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'), 'utf8');
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, graph_sha256, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, roots: ['alpha:money'], bindings: []}, definition);
  assert.throws(() => renderNamedInterfaceSource(graph, 'alpha:settlement-api'), /unresolved domain value/);
  const rendered = renderNamedInterfaceSource(graph, 'alpha:settlement-api', fields), api = native(t, {api: rendered.content})('api');
  assert.deepEqual(api.endpointValues.settle.request.normalize({id: {units: '9007199254740993', status: {variant: 'Waiting', payload: '2'}}}), {id: {units: 9007199254740993n, status: {variant: 'Waiting', payload: 2n}}});
  assert.equal(api.descriptor.field_compilation_sha256, fields.compilation_sha256);
  assert.equal(api.descriptor.invariant_execution, 'not-performed');
  assert.throws(() => renderNamedInterfaceSource(structuredClone(graph), 'alpha:settlement-api', fields), /unvalidated/);
  assert.throws(() => renderNamedInterfaceSource(graph, 'alpha:settlement-api', structuredClone(fields)), /unvalidated|unchecked|compiled|snapshot/i);
  const changed = f.read('specs/alpha/nodes/settlement-api.json'); changed.body.typed_contract.version_policy.provider_version = '2.0.0'; f.write('specs/alpha/nodes/settlement-api.json', changed);
  assert.throws(() => renderNamedInterfaceSource(f.graph(), 'alpha:settlement-api', fields), /cross-graph/);
});

test('legacy unqualified Mappings cannot flatten a named-contract Interface', t => {
  const f = fixture(t), feature = f.read('specs/alpha/feature.json'); feature.nodes.push('legacy-map'); feature.edges.push('legacy-map-maps-api'); f.write('specs/alpha/feature.json', feature);
  f.write('specs/alpha/nodes/legacy-map.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: 'legacy-map', kind: 'Mapping', body: {
    description: 'Unsupported implicit public-contract target.', source: 'alpha:customer', target: 'alpha:settlement-api', direction: 'outbound', totality: 'partial',
    fields: [{source_field: 'customer-id', target_field: 'id', conversion: 'string', default_value: null, required: true}],
  }});
  f.write('specs/alpha/edges/legacy-map-maps-api.json', {schema_version: 'domainspec.edge/v1', edge_id: 'legacy-map-maps-api', feature_id: 'alpha', relationship: 'maps', source_node_id: 'legacy-map', target_node_id: 'settlement-api', scope: 'feature'});
  assert.throws(() => f.graph(), (error: unknown) => (error as {code: string}).code === 'MTCLI_INTERFACE_MAPPING_PROFILE_REQUIRED');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
