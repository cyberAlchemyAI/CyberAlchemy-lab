import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {planCompiledReconciledPythonProject, getPythonDataVerificationContext} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {createQuerySemanticCases} from '../../src/verification/reconciled-query-controls.ts';
import {createMappingSemanticCases} from '../../src/verification/reconciled-mapping-controls.ts';

test('Python data semantics reuse every shared case for filters, limits, collections and legacy/default Mapping', t => {
  const f = pythonAllTypesFixture(t);
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(f.source, p), 'utf8'));
  const scalar = (name = 'String') => ({kind: 'scalar', name});
  const order = read('specs/alpha/nodes/order.json');
  for (const [name, type, cardinality] of [['memo', {kind: 'optional', element: scalar()}, 'optional'], ['tags', {kind: 'set', element: scalar('Bool')}, 'many-unique']] as const) {
    order.body.fields.push(name); order.body.typed_contract.properties.push({name, type, cardinality, identity: false, meaning: name, ontology_property: 'FIXTURE-ORDER#' + name});
  }
  f.write('specs/alpha/nodes/order.json', order);
  const query = read('specs/alpha/nodes/find.json');
  Object.assign(query.body.typed_contract, {inputs: [{name: 'min', type: scalar('UInt64')}], filter: {op: 'gte', left: {kind: 'field', name: 'amount'}, right: {kind: 'parameter', name: 'min'}}, order_by: {field: 'amount', direction: 'desc'}, limit: 2, projection: ['id', 'amount', 'memo', 'tags', 'money', 'mode']});
  f.write('specs/alpha/nodes/find.json', query);
  const feature = read('specs/alpha/feature.json');
  const mapping = (id: string, contract: unknown, legacy = false) => {
    feature.nodes.push(id); feature.edges.push(id + '-maps-order');
    f.write('specs/alpha/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Mapping', body: {description: id, target: 'alpha:order', ...(legacy ? {source: 'alpha:order'} : {}), typed_contract: contract}});
    f.write('specs/alpha/edges/' + id + '-maps-order.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: id + '-maps-order', relationship: 'maps', source_node_id: id, target_node_id: 'order', scope: 'feature'});
  };
  for (const defaults of [false, true]) mapping(defaults ? 'legacy-default' : 'legacy-projection', {schema_version: 'domainspec.typed-mapping/v1', ontology_mapping: defaults ? 'FIXTURE-DEFAULT' : 'FIXTURE-PROJECTION', source: 'alpha:order', target: 'alpha:order', total: false, fields: [{target: 'memo', source: 'memo', default: defaults ? {type: 'String', value: 'absent-only'} : null}]}, true);
  mapping('input-default', {schema_version: 'domainspec.typed-mapping/v2', ontology_mapping: 'FIXTURE-INPUT-DEFAULT', inputs: [{name: 'memo', type: {kind: 'optional', element: scalar()}}, {name: 'tags', type: {kind: 'list', element: scalar('Bool')}}], target: 'alpha:order', total: false,
    fields: [{target: 'memo', value: {op: 'path', root: 'memo', properties: []}, default: {op: 'literal', type: 'String', value: 'nullish'}}, {target: 'tags', value: {op: 'to_set', value: {op: 'path', root: 'tags', properties: []}}, default: null}]});
  f.write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'nested/commerce', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  const controls = createPythonSemanticControls(graph, plan), data = getPythonDataVerificationContext(plan);
  assert.throws(() => getPythonDataVerificationContext(structuredClone(plan)), /registered/);
  assert.equal(canonicalJson(data).includes('"artifacts"'), false);
  const ready = controls.rows.filter(r => r.state === 'ready' && ['Query', 'Mapping'].includes(r.kind));
  assert.equal(ready.length, 6);
  for (const row of ready) {
    assert.equal(row.state, 'ready'); if (row.state !== 'ready') throw new Error('test requires ready row');
    const node = graph.nodes.find(n => n.selector === row.selector)!;
    const shared = row.kind === 'Query' ? createQuerySemanticCases(node, graph) : createMappingSemanticCases(node, graph);
    if ((row as any).adapter === 'python-public-mapping') assert.deepEqual(row.cases.slice(1), shared.cases.map(c => c.expected.kind === 'error' ? {...c, expected: {kind: 'error', name: 'TypeError', message: 'MAPPING_INPUT'}} : c));
    else assert.deepEqual(row.cases, shared.cases);
    assert.ok(row.cases.some(c => c.expected.kind === 'value'));
    assert.ok(row.cases.some(c => c.expected.kind === 'error'));
  }
  const before = fs.readdirSync(f.temp), report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: f.temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  assert.equal(report.semantic_rows!.filter(r => r.result === 'pass').length, 24);
  assert.ok(report.semantic_rows!.filter(r => ['Query', 'Mapping'].includes(r.kind) && r.result === 'pass').every(r => r.compiling_substitutions === 2));
  assert.equal(report.semantic_rows!.find(r => r.selector === 'alpha:summary')!.result, 'pass');
  assert.deepEqual(fs.readdirSync(f.temp), before);
  t.diagnostic(JSON.stringify({nodes: controls.rows.length, cases: controls.case_count, data_cases: ready.reduce((n, r) => n + (r.state === 'ready' ? r.cases.length : 0), 0), controls_bytes: Buffer.byteLength(canonicalJson(controls))}));
});
