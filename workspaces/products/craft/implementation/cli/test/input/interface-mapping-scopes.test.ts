import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, {type TestContext} from 'node:test';
import {loadCompiledProjectGraph, type CompiledProjectGraph} from '../../src/input/project-model.ts';
import {inspectInterfaceMappingScopes, INTERFACE_MAPPING_SCOPES_DEFINITION_SHA256} from '../../src/input/interface-mapping-scopes.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const fixture = path.resolve(import.meta.dirname, '../../fixtures/input-roots/canonical-project');
function root(t: TestContext) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'domainspec-interface-scopes-'));
  fs.cpSync(fixture, folder, {recursive: true});
  t.after(() => fs.rmSync(folder, {recursive: true, force: true}));
  return folder;
}
function write(folder: string, relative: string, value: unknown) {
  fs.writeFileSync(path.join(folder, relative), JSON.stringify(value, null, 2) + '\n');
}
function read(folder: string, relative: string) {
  return JSON.parse(fs.readFileSync(path.join(folder, relative), 'utf8'));
}
function register(folder: string, node: string, edge: string) {
  const feature = read(folder, 'specs/alpha/feature.json');
  feature.nodes.push(node); feature.edges.push(edge);
  write(folder, 'specs/alpha/feature.json', feature);
}
const apiPath = 'specs/alpha/nodes/settlement-api.json';
function addMapping(folder: string, inbound: boolean, field: string) {
  const id = inbound ? 'request-map' : 'response-map';
  const target = inbound ? 'customer' : 'settlement-api';
  write(folder, `specs/alpha/nodes/${id}.json`, {schema_version: 'domainspec.node/v1', node_id: id, feature_id: 'alpha', kind: 'Mapping', body: {
    description: 'Inspect explicit legacy mapping field scope.', source: `alpha:${inbound ? 'settlement-api' : 'customer'}`, target: `alpha:${target}`,
    direction: inbound ? 'inbound' : 'outbound', totality: 'partial', fields: [{source_field: inbound ? field : 'customer-id', target_field: inbound ? 'customer-id' : field,
      conversion: 'string', default_value: null, required: true}],
  }});
  write(folder, `specs/alpha/edges/${id}-maps-${target}.json`, {schema_version: 'domainspec.edge/v1', edge_id: `${id}-maps-${target}`, feature_id: 'alpha', relationship: 'maps', source_node_id: id, target_node_id: target, scope: 'feature'});
  register(folder, id, `${id}-maps-${target}`);
}
function duplicateEndpoints(folder: string, sameType = false, reverse = false) {
  const operation = read(folder, 'specs/alpha/nodes/settle.json');
  write(folder, 'specs/alpha/nodes/inspect.json', {...operation, node_id: 'inspect'});
  write(folder, 'specs/alpha/edges/settlement-api-exposes-inspect.json', {
    schema_version: 'domainspec.edge/v1', edge_id: 'settlement-api-exposes-inspect', feature_id: 'alpha', relationship: 'exposes', source_node_id: 'settlement-api', target_node_id: 'inspect', scope: 'feature',
  });
  register(folder, 'inspect', 'settlement-api-exposes-inspect');
  const field = (name: string) => ({field_id: 'status', type_ref: {kind: 'primitive', name: sameType ? 'string' : name}, required: true});
  const api = read(folder, apiPath);
  api.body.operations = [
    {operation_id: 'settle', operation_ref: 'alpha:settle', request: [field('string')], result: [field('boolean')]},
    {operation_id: 'inspect', operation_ref: 'alpha:inspect', request: [field('integer')], result: [field('uuid')]},
  ];
  if (reverse) api.body.operations.reverse();
  write(folder, apiPath, api);
}

test('scope inspection binds the definition and checked source without writes or effects', t => {
  const folder = root(t);
  addMapping(folder, true, 'customer-id');
  addMapping(folder, false, 'customer-id');
  const graph = loadCompiledProjectGraph(folder), before = canonicalJson(graph);
  const report = inspectInterfaceMappingScopes(graph);
  const definition = fs.readFileSync(path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/interface-mapping-scopes-contract.json'), 'utf8');
  assert.equal(sha256(definition), INTERFACE_MAPPING_SCOPES_DEFINITION_SHA256);
  assert.equal(report.interface_count, 1);
  assert.equal(report.endpoint_count, 3);
  assert.equal(report.legacy_mapping_count, 2);
  assert.deepEqual(report.ambiguities, []);
  assert.deepEqual(report.uses.map(u => u.scope), ['resolved', 'resolved']);
  assert.deepEqual(new Set(report.uses.map(u => u.endpoint_role)), new Set(['source', 'target']));
  assert.equal(report.uses[0]!.candidates[0]!.source.pointer, '/body/operations/0/request/0');
  assert.equal(report.migration_performed, false);
  assert.equal(report.authority_effect, 'none');
  assert.equal(canonicalJson(graph), before);
  assert.deepEqual(inspectInterfaceMappingScopes(graph), report);
  const {report_sha256, ...body} = report;
  assert.equal(report_sha256, sha256(canonicalJson(body)));
  assert.equal(Object.isFrozen(report.uses[0]!.candidates[0]!.field.type_ref), true);
  assert.equal(Reflect.set(report.uses[0]!.candidates[0]!.field, 'required', false), false);
  assert.equal(canonicalJson(loadCompiledProjectGraph(folder)), before);
});

test('member and request/result scope do not collapse under duplicate spelling or source reordering', t => {
  const reports = [false, true].map(reverse => {
    const folder = root(t); duplicateEndpoints(folder, false, reverse);
    addMapping(folder, true, 'status'); addMapping(folder, false, 'status');
    return inspectInterfaceMappingScopes(loadCompiledProjectGraph(folder));
  });
  for (const report of reports) {
    assert.equal(report.endpoint_count, 4);
    assert.equal(report.ambiguities.length, 1);
    assert.equal(report.ambiguities[0]!.differing_declarations, true);
    assert.equal(report.uses.length, 2);
    assert.equal(report.uses.every(u => u.scope === 'ambiguous' && u.candidates.length === 4), true);
    assert.deepEqual(new Set(report.ambiguities[0]!.candidates.map(c => c.side)), new Set(['request', 'result']));
    assert.deepEqual(new Set(report.ambiguities[0]!.candidates.map(c => c.operation_id)), new Set(['settle', 'inspect']));
  }
  const endpoints = (r: typeof reports[number]) => r.ambiguities[0]!.candidates.map(({source, ...value}) => canonicalJson(value)).sort();
  assert.deepEqual(endpoints(reports[0]!), endpoints(reports[1]!));
  assert.notEqual(reports[0]!.graph_sha256, reports[1]!.graph_sha256);
  assert.notEqual(reports[0]!.report_sha256, reports[1]!.report_sha256);
});

test('equal types do not make distinct endpoints identical; required flags are retained', t => {
  const folder = root(t); duplicateEndpoints(folder, true); addMapping(folder, true, 'status');
  const before = inspectInterfaceMappingScopes(loadCompiledProjectGraph(folder));
  assert.equal(before.ambiguities[0]!.differing_declarations, false);
  assert.equal(before.uses[0]!.scope, 'ambiguous');
  const api = read(folder, apiPath); api.body.operations[0].request[0].required = false; write(folder, apiPath, api);
  const after = inspectInterfaceMappingScopes(loadCompiledProjectGraph(folder));
  assert.equal(after.ambiguities[0]!.differing_declarations, true);
  assert.equal(after.ambiguities[0]!.candidates.filter(c => !c.field.required).length, 1);
  assert.notEqual(before.report_sha256, after.report_sha256);
});

test('forged and cloned snapshots reject before inspecting caller-controlled graph fields', () => {
  const graph = loadCompiledProjectGraph(fixture);
  assert.throws(() => inspectInterfaceMappingScopes(structuredClone(graph)), /MTCLI_COMPILED_SNAPSHOT|unvalidated/);
  let reads = 0;
  const forged = Object.defineProperty({}, 'nodes', {get() {reads++; throw Error('getter evaluated');}});
  assert.throws(() => inspectInterfaceMappingScopes(forged as CompiledProjectGraph), /unvalidated/);
  assert.equal(reads, 0);
});

test('the real legacy graph checker retains its order-sensitive identity Mapping behavior', t => {
  for (const reverse of [false, true]) {
    const folder = root(t); duplicateEndpoints(folder, false, reverse); addMapping(folder, true, 'status');
    const relative = 'specs/alpha/nodes/request-map.json', mapping = read(folder, relative);
    mapping.body.fields[0].conversion = 'identity'; write(folder, relative, mapping);
    if (reverse) assert.throws(() => loadCompiledProjectGraph(folder), (error: unknown) => (error as {code: string}).code === 'MTCLI_MAPPING_TYPE');
    else {
      const report = inspectInterfaceMappingScopes(loadCompiledProjectGraph(folder));
      assert.equal(report.uses[0]!.scope, 'ambiguous');
      assert.equal(report.uses[0]!.candidates.length, 4);
    }
  }
});

test('typed Mappings are explicitly uninspected, not silently treated as checked legacy fields', t => {
  const folder = root(t);
  write(folder, 'specs/alpha/nodes/account.json', {schema_version: 'domainspec.node/v1', node_id: 'account', feature_id: 'alpha', kind: 'Entity', body: {
    description: 'A typed account identity.', fields: ['id'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'TEST-ACCOUNT', properties: [
      {ontology_property: 'TEST-ACCOUNT#id', name: 'id', type: {kind: 'scalar', name: 'String'}, cardinality: 'one', identity: true, meaning: 'Account identity.'},
    ]},
  }});
  write(folder, 'specs/alpha/nodes/account-map.json', {schema_version: 'domainspec.node/v1', node_id: 'account-map', feature_id: 'alpha', kind: 'Mapping', body: {
    description: 'Explicit typed Mapping, outside legacy field inspection.', target: 'alpha:account', typed_contract: {schema_version: 'domainspec.typed-mapping/v2', ontology_mapping: 'TEST-ACCOUNT-MAP',
      inputs: [{name: 'id', type: {kind: 'scalar', name: 'String'}}], target: 'alpha:account', total: true,
      fields: [{target: 'id', value: {op: 'path', root: 'id', properties: []}, default: null}]},
  }});
  write(folder, 'specs/alpha/edges/account-map-maps-account.json', {schema_version: 'domainspec.edge/v1', edge_id: 'account-map-maps-account', feature_id: 'alpha', relationship: 'maps', source_node_id: 'account-map', target_node_id: 'account', scope: 'feature'});
  register(folder, 'account-map', 'account-map-maps-account');
  const feature = read(folder, 'specs/alpha/feature.json'); feature.nodes.push('account'); write(folder, 'specs/alpha/feature.json', feature);
  const report = inspectInterfaceMappingScopes(loadCompiledProjectGraph(folder));
  assert.deepEqual(report.uninspected_typed_mappings, ['alpha:account-map']);
  assert.equal(report.legacy_mapping_count, 0);
  assert.deepEqual(report.uses, []);
});
