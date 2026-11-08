import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { type TestContext } from 'node:test';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { alchToolchain } from '../helpers/local-toolchain.ts';
import { loadCompiledProjectGraph } from '../../src/input/project-model.ts';
import { createCompiledProjectCertificate } from '../../src/compilation/certificate.ts';
import { compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256 } from '../../src/input/composition-boundary.ts';
import { compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256 } from '../../src/input/compiled-field-model.ts';
import { compileOperationValueReferences, assertReferencedOperationValueComposition } from '../../src/typed-operation/value-composition-references.ts';
import { assertCheckedOperationAction, OPERATION_ACTION_BINDINGS_VERSION, compileOperationActionBindings, compileComposedOperationActionBindings, assertCheckedComposedOperationAction } from '../../src/typed-operation/action-bindings.ts';
import { OPERATION_VALUE_COMPOSITION_VERSION } from '../../src/typed-operation/value-composition.ts';
import { canonicalJson, sha256 } from '../../src/input/source-manifest.ts';
import { compileOperationValueTypes, assertTypedOperationValueComposition } from '../../src/typed-operation/value-composition-types.ts';
import { renderConfiguredComposedOperation, type OperationCompositionImports } from '../../src/generation/configured-operation-source.ts';
import { renderConfiguredQuery } from '../../src/generation/configured-query-source.ts';
import { renderConfiguredMapping } from '../../src/generation/configured-mapping-source.ts';
import { renderStructuredRule } from '../../src/generation/configured-rule-values.ts';
import { renderConfiguredFactory } from '../../src/generation/configured-factory-source.ts';
import { planConfiguredComposedOperations, assertConfiguredComposedOperationsPlan, COMPOSED_OPERATION_SELECTION_VERSION } from '../../src/generation/configured-composed-operations.ts';
import { compileComposedOperation, planComposedOperations, compileComposedWorkflow, planComposedWorkflow, planCompiledComposedReconciledProject, decodeComposedReconciledCompilationSelection, selectReconciledArtifacts } from '../../src/index.ts';
import { compileComposedWorkflowBindings, compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION } from '../../src/typed-operation/workflow-bindings.ts';
import { selectWorkflowRecoveryPolicy, planSelectedWorkflowRecovery, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256, WORKFLOW_FAILURE_JOURNAL_VERSION } from '../../src/typed-operation/workflow-recovery.ts';
import { planConfiguredComposedWorkflow } from '../../src/generation/configured-workflows.ts';
import { getReconciledSource } from '../../src/generation/reconciled-sources.ts';
import { observeWorkflowStep, inspectOperationSettlement } from '../../src/typed-operation/workflow-outcomes.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const sourceContract = fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/operation-value-composition-contract.json'), 'utf8');
const actionContract = fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/operation-action-contract.json'), 'utf8');
const composedGenerationContract = fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/composed-operation-generation-contract.json'), 'utf8');
const composedWorkflowContract = fs.readFileSync(path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation/composed-workflow-contract.json'), 'utf8');
const boundaryContract = fs.readFileSync(path.join(project, 'development/reconciliation-v1/contracts/composition-boundary.json'), 'utf8');
const fieldContract = fs.readFileSync(path.join(project, 'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'), 'utf8');
const scalar = { kind: 'scalar', name: 'String' };
const at = (root: string) => ({ op: 'path', root, properties: [] });
function fixture(t: TestContext) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-value-references-')); t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const nodes: string[] = [], edges: string[] = [];
  const write = (name: string, value: unknown) => { const file = path.join(root, name); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify(value) + '\n'); };
  const node = (id: string, kind: string, body: any) => { if (!nodes.includes(id)) nodes.push(id); write(`specs/commerce/nodes/${id}.json`, { schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: { description: id, ...body } }); };
  const edge = (id: string, relationship: string, from: string, to: string) => { edges.push(id); write(`specs/commerce/edges/${id}.json`, { schema_version: 'domainspec.edge/v1', edge_id: id, feature_id: 'commerce', relationship, source_node_id: from, target_node_id: to, scope: 'feature' }); };
  for (const id of ['order', 'other']) node(id, 'Entity', { fields: ['id'], typed_contract: { schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-' + id.toUpperCase(), properties: [{ ontology_property: 'FIXTURE-' + id.toUpperCase() + '#id', name: 'id', type: scalar, cardinality: 'one', identity: true, meaning: 'identity' }] } });
  node('allowed', 'Rule', { predicate: 'allowed' });
  const operationBody = { reads: ['orders'], writes: [], effects: [], guard: 'allowed', failure_continuation: 'return-error' };
  node('submit', 'Operation', operationBody);
  const query: any = { schema_version: 'domainspec.typed-query/v2', ontology_query: 'FIXTURE-FIND', source: 'commerce:order', inputs: [{ name: 'id', type: scalar }], filter: null, projection: ['id'], order_by: null, limit: null, result_cardinality: 'optional' };
  node('find', 'Query', { reads: ['commerce:order'], typed_contract: query });
  node('copy', 'Mapping', { target: 'commerce:order', typed_contract: { schema_version: 'domainspec.typed-mapping/v2', ontology_mapping: 'FIXTURE-COPY', inputs: [{ name: 'id', type: scalar }], target: 'commerce:order', fields: [{ target: 'id', value: at('id'), default: null }], total: true } });
  edge('submit-order', 'reads', 'submit', 'order'); edge('find-order', 'reads', 'find', 'order'); edge('copy-order', 'maps', 'copy', 'order'); edge('allowed-submit', 'enforces', 'allowed', 'submit');
  const save = () => { write('project.json', { schema_version: 'domainspec.project/v1', project_id: 'value-references', features: ['commerce'], cross_feature_edges: [] }); write('specs/commerce/feature.json', { schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges }); }; save();
  const composition: any = { schema_version: OPERATION_VALUE_COMPOSITION_VERSION, operation_ref: 'commerce:submit', bindings: [
    { kind: 'query', name: 'found', selector: 'commerce:find', source_slot: 'orders', arguments: [{ parameter: 'id', value: at('request') }], absence: 'preserve' },
    { kind: 'mapping', name: 'copied', selector: 'commerce:copy', arguments: [{ parameter: 'id', value: at('request') }] },
  ] };
  const action: any = { schema_version: OPERATION_ACTION_BINDINGS_VERSION, selector: 'commerce:submit', inputs: [{ name: 'request', type: scalar }], reads: [], guards: [{ selector: 'commerce:allowed', arguments: [] }], writes: [], events: [], result: { type: scalar, value: at('request') }, atomicity: 'state-and-outbox', continuation: 'awaited-settlement' };
  const compile = () => {
    const graph = loadCompiledProjectGraph(root), certificate = createCompiledProjectCertificate(graph);
    const boundary = compileCompositionBoundary(graph, { schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256 }, boundaryContract);
    const fields = compileSelectedProjectFields(graph, { schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['commerce:order', 'commerce:other'], bindings: [] }, fieldContract);
    return { graph, boundary, fields, check: (c = composition, a = action, contract = sourceContract) => compileOperationValueReferences(graph, boundary, fields, c, a, contract) };
  };
  return { root, node, edge, save, operationBody, query, composition, action, compile, ...compile() };
}

test('composition references bind exact graph, contracts, named calls and collection slots without executable custody', t => {
  const f = fixture(t), before = JSON.stringify(f.composition), checked = f.check();
  assertReferencedOperationValueComposition(checked);
  assert.deepEqual(f.check(), checked); assert.equal(JSON.stringify(f.composition), before);
  assert.deepEqual(checked.source_slots, [{ slot: 'orders', target: 'commerce:order', mode: 'collection' }]);
  assert.equal(checked.connections.length, 2); assert.equal(checked.validation_stage, 'references-only');
  assert.equal(checked.execution, 'not-performed'); assert.equal(checked.authority_effect, 'none');
  assert.throws(() => assertCheckedOperationAction(checked));
  assert.throws(() => assertReferencedOperationValueComposition(structuredClone(checked)));
  const { references_sha256, ...body } = checked; assert.equal(references_sha256, sha256(canonicalJson(body)));
  const frozen = (v: any) => { if (v && typeof v === 'object') { assert.ok(Object.isFrozen(v)); Object.values(v).forEach(frozen); } }; frozen(checked);
  const reordered = structuredClone(f.composition); reordered.bindings.reverse(); assert.deepEqual(f.check(reordered), checked);
  const changed = structuredClone(f.composition); changed.bindings[0].absence = 'require-present'; assert.notEqual(f.check(changed).references_sha256, checked.references_sha256);
});

test('wrong roles, missing roots, argument coverage, slot ownership and missing Operation reads reject', t => {
  const f = fixture(t);
  const cases: Array<(c: any, a: any) => void> = [
    c => c.operation_ref = 'commerce:order', c => c.bindings[0].selector = 'commerce:order',
    c => c.bindings[1].selector = 'commerce:find', c => c.bindings[0].source_slot = 'invented',
    c => c.bindings[0].arguments[0].parameter = 'unknown', c => c.bindings[1].arguments = [],
    c => c.bindings[1].arguments[0].value = at('missing'),
    c => { c.bindings[0].name = 'request'; c.bindings[0].arguments[0].value = { op: 'literal', type: 'String', value: 'id' }; },
    (_, a) => a.events.push({ slot: 'event', target: 'commerce:order', parameter: 'copied' }),
    (c, a) => { a.events.push({ slot: 'event', target: 'commerce:order', parameter: 'event_input' }); c.bindings[0].arguments[0].value = at('event_input'); },
    (_, a) => a.reads.push({ slot: 'orders', target: 'commerce:order', parameter: 'current', key: at('request') }),
  ];
  for (const mutate of cases) { const c = structuredClone(f.composition), a = structuredClone(f.action); mutate(c, a); assert.throws(() => f.check(c, a), /OPERATION_VALUE_REFERENCES/); }
  f.node('submit', 'Operation', { ...f.operationBody, reads: [] }); assert.throws(() => f.compile().check(), /slot coverage/);
  f.node('submit', 'Operation', f.operationBody); f.edge('submit-other', 'reads', 'submit', 'other'); f.save(); assert.throws(() => f.compile().check(), /relationship coverage/);
});

test('optional versus list contract and cross-graph or altered evidence remain distinct', t => {
  const f = fixture(t), first = f.check();
  assert.throws(() => f.check(f.composition, f.action, sourceContract + ' '), /contract drift/);
  for (const [g, b, fields] of [[structuredClone(f.graph), f.boundary, f.fields], [f.graph, structuredClone(f.boundary), f.fields], [f.graph, f.boundary, structuredClone(f.fields)]] as const) {
    assert.throws(() => compileOperationValueReferences(g, b, fields, f.composition, f.action, sourceContract));
  }
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, result_cardinality: 'list' } });
  const next = f.compile(); assert.notEqual(next.check().references_sha256, first.references_sha256);
  assert.throws(() => compileOperationValueReferences(next.graph, f.boundary, next.fields, f.composition, f.action, sourceContract), /cross-graph/);
  assert.throws(() => compileOperationValueReferences(next.graph, next.boundary, f.fields, f.composition, f.action, sourceContract), /cross-graph/);
  const required = structuredClone(f.composition); required.bindings[0].absence = 'require-present'; assert.throws(() => next.check(required), /optional Query/);
});

const named = (selector = 'commerce:order') => ({ kind: 'named', selector });
const fieldPath = (root: string, property = 'FIXTURE-ORDER#id') => ({ op: 'path', root, properties: [property] });
function orderWithState(f: ReturnType<typeof fixture>) {
  f.node('order', 'Entity', { fields: ['id', 'state'], typed_contract: { schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-ORDER', properties: [
    { ontology_property: 'FIXTURE-ORDER#id', name: 'id', type: scalar, cardinality: 'one', identity: true, meaning: 'identity' },
    { ontology_property: 'FIXTURE-ORDER#state', name: 'state', type: scalar, cardinality: 'one', identity: false, meaning: 'state' },
  ] } });
  f.node('copy', 'Mapping', { target: 'commerce:order', typed_contract: { schema_version: 'domainspec.typed-mapping/v2', ontology_mapping: 'FIXTURE-COPY', inputs: [{ name: 'id', type: scalar }], target: 'commerce:order', fields: [{ target: 'id', value: at('id'), default: null }], total: false } });
}
function typed(f: ReturnType<typeof fixture>, composition = f.composition, action = f.action) {
  const current = f.compile(); return compileOperationValueTypes(current.graph, current.fields, current.check(composition, action));
}

test('typed preparation preserves optional/list/set and partial projections without granting action custody', t => {
  const f = fixture(t); orderWithState(f);
  const first = typed(f), output = (name: string) => first.values.find(v => v.name === name)!.output;
  assertTypedOperationValueComposition(first); assert.throws(() => assertCheckedOperationAction(first));
  assert.throws(() => assertTypedOperationValueComposition(structuredClone(first)));
  assert.deepEqual(output('found'), { kind: 'optional', element: { kind: 'projection', owner: named(), fields: ['id'] } });
  assert.deepEqual(output('copied'), { kind: 'projection', owner: named(), fields: ['id'] });
  assert.ok(Object.isFrozen(first.values[0]!.output)); assert.deepEqual(typed(f), first);
  const { types_sha256, ...body } = first; assert.equal(types_sha256, sha256(canonicalJson(body)));
  const required = structuredClone(f.composition); required.bindings[0].absence = 'require-present';
  required.bindings[1].arguments[0].value = fieldPath('found');
  const connected = typed(f, required); assert.deepEqual(connected.values.map(v => v.name), ['found', 'copied']);
  required.bindings.reverse(); assert.deepEqual(typed(f, required), connected);
  required.bindings.find((b: any) => b.kind === 'mapping').arguments[0].value = fieldPath('found', 'FIXTURE-ORDER#state');
  assert.throws(() => typed(f, required), /unprojected field/);
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, result_cardinality: 'list' } });
  const list = typed(f); assert.equal(list.values.find(v => v.name === 'found')!.output.kind, 'list');
  assert.notEqual(list.types_sha256, first.types_sha256);
});

test('typed arguments reject implicit optional unwrap, partial Entity substitution and wrong nominal identity', t => {
  const f = fixture(t); orderWithState(f);
  const c = structuredClone(f.composition); c.bindings[1].arguments[0].value = fieldPath('found');
  assert.throws(() => typed(f, c), /no implicit optional traversal/);
  c.bindings[0].absence = 'require-present';
  f.node('copy', 'Mapping', { target: 'commerce:order', typed_contract: { schema_version: 'domainspec.typed-mapping/v2', ontology_mapping: 'FIXTURE-COPY', inputs: [{ name: 'id', type: named() }], target: 'commerce:order', fields: [{ target: 'id', value: fieldPath('id'), default: null }], total: false } });
  c.bindings[1].arguments[0].value = at('found'); assert.throws(() => typed(f, c), /argument type mismatch/);
  const a = structuredClone(f.action); a.inputs.push({ name: 'other', type: named('commerce:other') });
  c.bindings[1].arguments[0].value = at('other'); assert.throws(() => typed(f, c, a), /argument type mismatch/);
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, projection: ['id', 'state'] } });
  c.bindings[1].arguments[0].value = at('found');
  assert.deepEqual(typed(f, c).values.find(v => v.name === 'found')!.output, named());
  const bad = structuredClone(c); bad.bindings[0].arguments[0].value = { op: 'literal', type: 'Bool', value: true };
  assert.throws(() => typed(f, bad), /argument type mismatch:found\/id/);
});

test('collection field projections require explicit list-to-set conversion and never collapse to scalar', t => {
  const f = fixture(t);
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, result_cardinality: 'list' } });
  // A collection argument can remain unused by the Mapping; declared input type
  // checking must still apply rather than optimizing the named call away.
  f.node('copy', 'Mapping', { target: 'commerce:order', typed_contract: { schema_version: 'domainspec.typed-mapping/v2', ontology_mapping: 'FIXTURE-COPY', inputs: [{ name: 'id', type: { kind: 'set', element: scalar } }], target: 'commerce:order', fields: [{ target: 'id', value: { op: 'literal', type: 'String', value: 'fixed' }, default: null }], total: true } });
  const c = structuredClone(f.composition); c.bindings[1].arguments[0].value = fieldPath('found');
  assert.throws(() => typed(f, c), /argument type mismatch/);
  c.bindings[1].arguments[0].value = { op: 'to_set', value: fieldPath('found') };
  const result = typed(f, c); assert.deepEqual(result.values[1]!.arguments[0]!.type, { kind: 'set', element: scalar });
  c.bindings[1].arguments[0].value = { op: 'to_set', value: at('request') }; assert.throws(() => typed(f, c), /to_set requires list/);
});

test('public Mapping chains keep qualified contract identity and ontology fields', t => {
  const f = fixture(t);
  const api: any = { schema_version: 'domainspec.typed-interface/v1', ontology_interface: 'FIXTURE-API', boundary_kind: 'external', version_policy: { schema_version: 'domainspec.interface-version-policy/v1', mode: 'backward', direction: 'consumer-to-provider', provider_version: '1.0.0' }, contracts: ['response', 'shadow'].map(contract_id => ({ contract_id, ontology_contract: 'FIXTURE-' + contract_id.toUpperCase(), fields: [{ name: 'id', ontology_field: 'FIXTURE-PUBLIC#id', meaning: 'identity', type: scalar }] })), operations: [{ operation_id: 'find', operation_ref: 'commerce:find', request: scalar, result: { kind: 'contract', contract_id: 'response' } }] };
  f.node('api', 'Interface', { typed_contract: api }); f.edge('api-find', 'exposes', 'api', 'find');
  const publicType = { kind: 'contract', interface_selector: 'commerce:api', contract_id: 'response' };
  const outgoing: any = { schema_version: 'domainspec.typed-mapping/v3', ontology_mapping: 'FIXTURE-OUTGOING', inputs: [{ name: 'order', type: named(), use: null }], target: publicType, target_use: null, fields: [{ target: 'id', value: fieldPath('order'), default: null }], total: true };
  const incoming: any = { schema_version: 'domainspec.typed-mapping/v3', ontology_mapping: 'FIXTURE-INCOMING', inputs: [{ name: 'response', type: publicType, use: null }], target: named(), target_use: null, fields: [{ target: 'id', value: fieldPath('response', 'FIXTURE-PUBLIC#id'), default: null }], total: true };
  f.node('outgoing', 'Mapping', { target: 'commerce:api', typed_contract: outgoing }); f.edge('outgoing-api', 'maps', 'outgoing', 'api');
  f.node('incoming', 'Mapping', { target: 'commerce:order', typed_contract: incoming }); f.edge('incoming-order', 'maps', 'incoming', 'order'); f.save();
  const c = structuredClone(f.composition); c.bindings.push(
    { kind: 'mapping', name: 'public_value', selector: 'commerce:outgoing', arguments: [{ parameter: 'order', value: at('copied') }] },
    { kind: 'mapping', name: 'restored', selector: 'commerce:incoming', arguments: [{ parameter: 'response', value: at('public_value') }] },
  );
  const result = typed(f, c); assert.deepEqual(result.values.find(v => v.name === 'public_value')!.output, publicType);
  assert.deepEqual(result.values.find(v => v.name === 'restored')!.output, named());
  incoming.inputs[0].type = { ...publicType, contract_id: 'shadow' }; f.node('incoming', 'Mapping', { target: 'commerce:order', typed_contract: incoming });
  assert.throws(() => typed(f, c), /argument type mismatch:restored\/response/);
});

test('typed composition rejects forged references and stale graph or field evidence', t => {
  const f = fixture(t), refs = f.check();
  assert.throws(() => compileOperationValueTypes(f.graph, f.fields, structuredClone(refs)), /unvalidated reference/);
  assert.throws(() => compileOperationValueTypes(structuredClone(f.graph), f.fields, refs));
  assert.throws(() => compileOperationValueTypes(f.graph, structuredClone(f.fields), refs));
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, result_cardinality: 'list' } }); const next = f.compile();
  assert.throws(() => compileOperationValueTypes(next.graph, next.fields, refs), /cross-graph/);
  assert.throws(() => compileOperationValueTypes(f.graph, next.fields, refs), /cross-graph/);
});

test('Query predicate types are checked beyond field-name resolution', t => {
  const f = fixture(t);
  const filter = { op: 'eq', left: { kind: 'field', name: 'id' }, right: { kind: 'literal', type: 'Bool', value: true } };
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, filter } });
  // Existing graph checks names; the composition type stage must not mistake
  // that evidence for comparison-type correctness.
  const current = f.compile(); const references = current.check();
  assert.throws(() => compileOperationValueTypes(current.graph, current.fields, references), /Query comparison type mismatch/);
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, filter: { ...filter, right: { kind: 'parameter', name: 'id' } } } });
  assertTypedOperationValueComposition(typed(f));
});

function composedFixture(t: TestContext) {
  const f = fixture(t);
  f.node('allowed', 'Rule', { predicate: 'structured:domainspec.typed-rule/v2', typed_contract: { schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-ALLOWED', parameters: [{ name: 'order', type: named() }], expression: { op: 'eq', left: fieldPath('order'), right: { op: 'literal', type: 'String', value: 'allowed' } } } });
  f.node('submit', 'Operation', { ...f.operationBody, writes: ['order-state'] });
  f.composition.bindings[0].absence = 'require-present'; f.composition.bindings[1].arguments[0].value = fieldPath('found');
  f.action.guards[0].arguments = [{ parameter: 'order', value: at('found') }];
  f.action.writes = [{ slot: 'order-state', target: 'commerce:order', mode: 'replace', value: at('copied') }];
  f.action.result = { type: named(), value: at('copied') };
  const joined = (c = f.composition, a = f.action, contract = actionContract) => {
    const current = f.compile(), typed = compileOperationValueTypes(current.graph, current.fields, current.check(c, a));
    return compileComposedOperationActionBindings(current.graph, current.boundary, current.fields, typed, contract);
  };
  return { ...f, joined };
}

test('composed action guards the Query value and writes/returns the Mapping without inventing caller inputs', t => {
  const f = composedFixture(t), action = f.joined(); assertCheckedComposedOperationAction(action);
  assert.throws(() => assertCheckedOperationAction(action)); assert.throws(() => assertCheckedComposedOperationAction(structuredClone(action)));
  assert.deepEqual(action.bindings.inputs.map(p => p.name), ['request']); assert.deepEqual(action.reads, []);
  assert.deepEqual(action.guards[0]!.arguments[0]!.value, at('found')); assert.deepEqual(action.writes[0]!.value, at('copied'));
  assert.deepEqual(action.bindings.result.value, at('copied'));
  assert.deepEqual(action.value_composition.values.map(v => v.name), ['found', 'copied']);
  assert.equal(action.execution, 'not-performed'); assert.equal(action.authority_effect, 'none');
  assert.equal(Object.isFrozen(action.value_composition.consumers), true);
  const { action_sha256, ...body } = action; assert.equal(action_sha256, sha256(canonicalJson(body)));
  const current = f.compile(); assert.throws(() => compileOperationActionBindings(current.graph, current.boundary, current.fields, f.action, actionContract), /COVERAGE/);
  assert.deepEqual(f.joined(), action);
  const altered = structuredClone(f.composition); altered.bindings[1].arguments[0].value = at('request');
  assert.notEqual(f.joined(altered).action_sha256, action.action_sha256);
});

test('composed action rejects incompatible guards, partial writes, optional results and missing effect coverage', t => {
  const f = composedFixture(t);
  for (const [mutate, code] of [
    [(a: any) => a.guards[0].arguments[0].value = at('request'), 'GUARD_ARGUMENT_TYPE'],
    [(a: any) => a.guards[0].arguments = [], 'GUARD_ARGUMENTS'],
    [(a: any) => a.writes[0].value = at('request'), 'WRITE_VALUE_TYPE'],
    [(a: any) => a.result.type = scalar, 'RESULT_TYPE'],
    [(a: any) => a.writes = [], 'COVERAGE'],
    [(a: any) => a.writes[0].mode = 'create', 'COVERAGE'],
  ] as const) { const a = structuredClone(f.action); mutate(a); assert.throws(() => f.joined(f.composition, a), new RegExp(code)); }
  const missing = structuredClone(f.action); missing.result.value = at('not_declared'); assert.throws(() => f.joined(f.composition, missing), /unknown value root/);
  const optional = structuredClone(f.composition); optional.bindings[0].absence = 'preserve'; optional.bindings[1].arguments[0].value = at('request');
  assert.throws(() => f.joined(optional), /GUARD_ARGUMENT_TYPE/);
  orderWithState(f);
  // Scalar guard permits the partial Query's selected id; the omitted state
  // must still prevent the Mapping's partial result from becoming a write.
  f.node('allowed', 'Rule', { predicate: 'structured:domainspec.typed-rule/v2', typed_contract: { schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-ALLOWED', parameters: [{ name: 'order', type: scalar }], expression: { op: 'eq', left: at('order'), right: at('order') } } });
  const a = structuredClone(f.action); a.guards[0].arguments[0].value = fieldPath('found');
  assert.throws(() => f.joined(f.composition, a), /WRITE_VALUE_TYPE/);
});

test('composed action retains Event coverage and rejects cross-graph or forged typed evidence', t => {
  const f = composedFixture(t), current = f.compile(), preparation = compileOperationValueTypes(current.graph, current.fields, current.check());
  assert.throws(() => compileComposedOperationActionBindings(current.graph, current.boundary, current.fields, structuredClone(preparation), actionContract), /unvalidated typed/);
  assert.throws(() => f.joined(f.composition, f.action, actionContract + ' '), /CONTRACT_DRIFT/);
  f.node('posted', 'Event', { event_type: 'posted', version: '1', occurrence_id: { field_id: 'occurrence-id', type_ref: { kind: 'primitive', name: 'uuid' }, required: true }, occurred_at_policy: 'required', payload: [{ field_id: 'order-id', type_ref: { kind: 'reference', selector: 'commerce:order' }, required: true }] });
  f.node('submit', 'Operation', { ...f.operationBody, writes: ['order-state'], effects: ['posted-fact'] }); f.edge('submit-posted', 'produces', 'submit', 'posted'); f.save();
  assert.throws(() => f.joined(), /COVERAGE/);
  const action = structuredClone(f.action); action.events = [{ slot: 'posted-fact', target: 'commerce:posted', parameter: 'posted_input' }];
  const result = f.joined(f.composition, action); assert.equal(result.events[0]!.target, 'commerce:posted');
  assert.deepEqual(result.bindings.inputs.map(p => p.name), ['request']);
  const next = f.compile(); assert.throws(() => compileComposedOperationActionBindings(next.graph, next.boundary, next.fields, preparation, actionContract), /CROSS_GRAPH/);
  assert.throws(() => compileComposedOperationActionBindings(current.graph, next.boundary, current.fields, preparation, actionContract), /CROSS_GRAPH/);
});

function nativeComposition(t: TestContext, guardExpected = 'allowed') {
  const f = composedFixture(t);
  f.node('allowed', 'Rule', { predicate: 'structured:domainspec.typed-rule/v2', typed_contract: { schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-ALLOWED', parameters: [{ name: 'order', type: named() }], expression: { op: 'eq', left: fieldPath('order'), right: { op: 'literal', type: 'String', value: guardExpected } } } });
  // Stored id and request differ in the success case. No keyed-lookup
  // substitute can implement this query's declared filter.
  f.node('find', 'Query', { reads: ['commerce:order'], typed_contract: { ...f.query, filter: { op: 'eq', left: { kind: 'field', name: 'id' }, right: { kind: 'literal', type: 'String', value: 'allowed' } } } });
  const current = f.compile(), action = f.joined(), model = current.fields.model;
  const dependencies: OperationCompositionImports = {
    values: action.value_composition.references.connections.map((row, i) => ({ selector: row.binding.selector, kind: row.binding.kind, path: row.binding.kind === 'query' ? './query.js' : './mapping.js', symbol: row.binding.kind === 'query' ? 'query' : 'map', local: 'valueCall' + i, contract_sha256: row.contract_sha256 })),
    public_values: [], absence_failures: [{ binding: 'found', code: 'ORDER_NOT_FOUND' }],
  };
  const factory = { selector: 'commerce:order', relative_path: 'factory.ts', callable: 'createOrderFactory' };
  const rules = [{ selector: 'commerce:allowed', path: './rule.js', symbol: 'allowed', local: 'guard0' }];
  const render = (selected = dependencies) => renderConfiguredComposedOperation(action, model, { modules: [factory] }, 'operation.ts', rules, [], selected);
  const code = render();
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-composed-native-')); t.after(() => fs.rmSync(folder, { recursive: true, force: true }));
  const query = action.value_composition.references.connections.find(c => c.binding.kind === 'query')!.contract;
  const mapping = action.value_composition.references.connections.find(c => c.binding.kind === 'mapping')!.contract;
  if (query.schema_version !== 'domainspec.typed-query/v2' || mapping.schema_version !== 'domainspec.typed-mapping/v2') throw Error('fixture version');
  const files = {
    'operation.ts': code,
    'query.ts': renderConfiguredQuery(query, model).content,
    'mapping.ts': renderConfiguredMapping(mapping, model).content,
    'rule.ts': renderStructuredRule(action.guards[0]!.contract, { selector: 'commerce:allowed', relative_path: 'rule.ts', callable: 'allowed', closure_sha256: sha256(canonicalJson(action.guards[0]!.contract)), imports: [] }, model),
    'factory.ts': renderConfiguredFactory({ ...factory, kind: 'Entity', name: 'Order', protocol_id: 'typescript.owned-value-component/v1', fields: [{ name: 'id', tag: 'String', identity: true }], imports: [], base_validators: [], extensions: [], component_protocol_sha256: sha256('fixture-entity-component') }),
  };
  for (const [file, content] of Object.entries(files)) fs.writeFileSync(path.join(folder, file), content);
  const toolchain = alchToolchain();
  const compile = () => { try { execFileSync(process.execPath, [toolchain, 'tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--target', 'ES2022', '--module', 'commonjs', '--outDir', 'js', ...Object.keys(files)], { cwd: folder, encoding: 'utf8' }); } catch (error: any) { throw new Error(String(error.stdout) + String(error.stderr)); } };
  compile(); const execute = createRequire(import.meta.url)(path.join(folder, 'js/operation.js')).execute;
  return { folder, code, files, compile, execute, render, dependencies, action, model, factory, rules };
}

test('native composed operation executes named Query/Mapping before guards and commits the computed value', async t => {
  const n = nativeComposition(t), trace: string[] = [], batches: any[] = [];
  const result = await n.execute({ request: 'not-the-stored-id' }, { store: { begin: async () => {
    trace.push('begin'); return {
      read: async () => { throw Error('must not replace Query with keyed read'); },
      querySource: async (request: any) => { trace.push('query-source'); assert.deepEqual(request, { slot: 'orders', target: 'commerce:order' }); return [{ id: 'ignored' }, { id: 'allowed' }]; },
      rollback: async () => { trace.push('rollback'); },
      commit: async (batch: any) => { trace.push('commit'); assert.ok(Object.isFrozen(batch) && Object.isFrozen(batch.writes[0].value)); batches.push(batch); return { status: 'committed' }; },
    };
  } } });
  assert.deepEqual(result, { status: 'committed', value: { id: 'allowed' } });
  assert.deepEqual(trace, ['begin', 'query-source', 'commit']);
  assert.deepEqual(batches, [{ writes: [{ slot: 'order-state', target: 'commerce:order', mode: 'replace', value: { id: 'allowed' } }], events: [] }]);
  assert.equal(n.code.includes('eval('), false); assert.equal(n.code.includes('value_composition'), false);
});

test('native composed failures preserve cardinality, validate before filtering and never retry uncertain commit', async t => {
  const n = nativeComposition(t);
  const cases = [
    { rows: [], status: 'failed', code: 'ORDER_NOT_FOUND', commits: 0, rollbacks: 1 },
    { rows: [{ id: 'allowed' }, { id: 'allowed' }], status: 'failed', code: 'QUERY_CARDINALITY', commits: 0, rollbacks: 1 },
    { rows: [{ id: 'allowed' }, { id: 23 }], status: 'failed', code: 'OPERATION_FAILED', commits: 0, rollbacks: 1 },
    { rows: [{ id: 'allowed' }], commit: 'reject', status: 'rejected', code: 'COMMIT_REJECTED', commits: 1, rollbacks: 0 },
    { rows: [{ id: 'allowed' }], commit: 'throw', status: 'indeterminate', code: 'COMMIT_UNCERTAIN', commits: 1, rollbacks: 0 },
    { rows: [{ id: 'allowed' }], sourceThrows: true, status: 'failed', code: 'OPERATION_FAILED', commits: 0, rollbacks: 1 },
    { rows: [], cleanupThrows: true, status: 'failed', code: 'ORDER_NOT_FOUND', commits: 0, rollbacks: 1 },
  ];
  for (const c of cases) {
    let commits = 0, rollbacks = 0, reads = 0;
    const result = await n.execute({ request: 'input' }, { store: { begin: async () => ({
      read: async () => { throw Error('unexpected keyed read'); },
      querySource: async () => { reads++; if (c.sourceThrows) throw Error('source unavailable'); return c.rows; },
      rollback: async () => { rollbacks++; if (c.cleanupThrows) throw Error('cleanup failed'); }, commit: async () => { commits++; if (c.commit === 'throw') throw Error('ack lost'); return { status: c.commit === 'reject' ? 'rejected' : 'committed' }; },
    }) } });
    assert.equal(result.status, c.status); assert.equal(result.code, c.code); assert.equal(commits, c.commits); assert.equal(rollbacks, c.rollbacks); assert.equal(reads, 1);
    assert.equal(result.cleanupFailed, !!c.cleanupThrows);
  }
});

test('native composed guard rejection occurs after value preparation and before commit', async t => {
  const n = nativeComposition(t, 'different-required-id'), trace: string[] = [];
  const result = await n.execute({ request: 'input' }, { store: { begin: async () => ({
    read: async () => { throw Error('unexpected keyed read'); },
    querySource: async () => { trace.push('query'); return [{ id: 'allowed' }]; },
    rollback: async () => { trace.push('rollback'); }, commit: async () => { trace.push('commit'); return { status: 'committed' }; },
  }) } });
  assert.equal(result.status, 'rejected'); assert.equal(result.code, 'RULE_REJECTED:commerce:allowed'); assert.equal(result.stage, 'guard');
  assert.deepEqual(trace, ['query', 'rollback']);
});

test('composed source requires exact dependencies and explicit absence outcomes', t => {
  const n = nativeComposition(t);
  for (const mutate of [
    (d: any) => d.values.pop(), (d: any) => d.values[0].contract_sha256 = '0'.repeat(64),
    (d: any) => d.values[0].local = 'injected();', (d: any) => d.values[0].kind = 'unknown',
    (d: any) => d.values[0].path += '\n', (d: any) => d.values[0].symbol += '\n',
    (d: any) => d.absence_failures = [], (d: any) => d.absence_failures[0].binding = 'unknown',
    (d: any) => d.absence_failures[0].code = 'unsafe\ncode',
  ]) { const dependencies = structuredClone(n.dependencies); mutate(dependencies); assert.throws(() => n.render(dependencies), /DS_COMPOSED_OPERATION/); }
  assert.throws(() => renderConfiguredComposedOperation(structuredClone(n.action), n.model, { modules: [n.factory] }, 'operation.ts', n.rules, [], n.dependencies), /UNVALIDATED_COMPOSITION/);
  const forged = structuredClone(n.model); (forged.declarations[0]!.contract as any).ontology_node = 'FORGED-NODE';
  assert.throws(() => renderConfiguredComposedOperation(n.action, forged, { modules: [n.factory] }, 'operation.ts', n.rules, [], n.dependencies), /field model mismatch/);
});

function plannedComposition(f: ReturnType<typeof composedFixture>) {
  // The profile requires explicit factory validators. This fixture supplies one;
  // the planner must not fabricate defaults for empty owner selections.
  f.node('valid-id', 'Rule', { predicate: 'structured:domainspec.typed-rule/v2', typed_contract: { schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-VALID-ID', parameters: [{ name: 'id', type: scalar }], expression: { op: 'eq', left: at('id'), right: at('id') } } }); f.save();
  const current = f.compile(), action = f.joined();
  const selection = { schema_version: COMPOSED_OPERATION_SELECTION_VERSION, language: 'typescript' as const, module_root: 'generated', actions: [{ action, absence_failures: [{ binding: 'found', code: 'ORDER_NOT_FOUND' }] }], factories: ['commerce:order', 'commerce:other'].map(selector => ({ selector, base_validators: [{ rule: 'commerce:valid-id', arguments: [{ parameter: 'id', field: 'id' }] }], extensions: [] })) };
  const plan = (s = selection, contract = composedGenerationContract) => planConfiguredComposedOperations(current.graph, current.boundary, current.fields, s, contract);
  return { ...current, selection, plan };
}
function loadPlannedComposition(t: TestContext, plan: { artifacts: readonly {relative_path:string;content:string}[]; modules: readonly {relative_path:string;callable:string}[] }, inspect = false) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-composed-plan-native-')); t.after(() => fs.rmSync(folder, { recursive: true, force: true }));
  for (const artifact of plan.artifacts) { const file = path.join(folder, artifact.relative_path); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, artifact.content); }
  const toolchain = alchToolchain();
  const types = createRequire(import.meta.url).resolve('@types/node/package.json', {paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))});
  try { execFileSync(process.execPath, [toolchain, 'tsc', '--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', path.dirname(path.dirname(types)), '--target', 'ES2022', '--module', 'commonjs', '--outDir', 'js', '--rootDir', '.', ...plan.artifacts.map(a => a.relative_path)], { cwd: folder, encoding: 'utf8' }); } catch (error: any) { throw new Error(String(error.stdout) + String(error.stderr)); }
  const require=createRequire(import.meta.url), entry=path.join(folder,'js',plan.modules[0]!.relative_path.replace(/\.ts$/,'.js'));
  const run=require(entry)[plan.modules[0]!.callable];
  return inspect?{run,provider:require(entry.replace(/\.js$/,'.provider.js'))}:run;
}

test('composed Workflow executes named-value Operations and preserves failure recovery without automatic compensation', async t => {
  const f = composedFixture(t);
  f.node('flow', 'Workflow', { typed_contract: { schema_version: 'domainspec.workflow-occurrences/v1', ontology_workflow: 'FIXTURE-FLOW',
    steps: [{ step_id: 'first', operation_ref: 'commerce:submit' }, { step_id: 'second', operation_ref: 'commerce:submit' }],
    compensations: [{ compensation_id: 'undo-first', for_step: 'first', operation_ref: 'commerce:submit', depends_on: [] }] } });
  f.edge('flow-submit', 'orchestrates', 'flow', 'submit'); f.save();
  const fixture = plannedComposition(f), action = fixture.selection.actions[0]!.action, operationPlan = fixture.plan();
  const bindings = { schema_version: WORKFLOW_BINDINGS_VERSION, selector: 'commerce:flow', inputs: [{ name: 'request', type: scalar }], event_inputs: [],
    steps: [
      { step_id: 'first', action_sha256: action.action_sha256, arguments: [{ parameter: 'request', value: { op: 'input', name: 'request', properties: [] } }], events: [] },
      { step_id: 'second', action_sha256: action.action_sha256, arguments: [{ parameter: 'request', value: { op: 'step-result', step_id: 'first', properties: ['FIXTURE-ORDER#id'] } }], events: [] },
    ], compensations: [{ compensation_id: 'undo-first', action_sha256: action.action_sha256, arguments: [{ parameter: 'request', value: { op: 'step-result', step_id: 'first', properties: ['FIXTURE-ORDER#id'] } }], events: [] }],
    result: { type: named(), value: { op: 'step-result', step_id: 'second', properties: [] } } };
  const check = (value: unknown = bindings, actions = fixture.selection.actions, contract = composedWorkflowContract) => compileComposedWorkflowBindings(fixture.graph, fixture.boundary, fixture.fields, actions, value, getReconciledSource('workflow_binding'), contract);
  const workflow = check();
  assert.throws(() => compileWorkflowBindings(fixture.graph, fixture.boundary, fixture.fields, [action] as any, bindings, getReconciledSource('workflow_binding')), /UNVALIDATED/);
  assert.throws(() => check(bindings, structuredClone(fixture.selection.actions)), /UNVALIDATED/);
  assert.throws(() => check(bindings, fixture.selection.actions, composedWorkflowContract + ' '), /CONTRACT_DRIFT/);
  assert.throws(() => check(bindings, [{action,absence_failures:[]}]), /explicit absence coverage/);
  let getters=0; const hostile:any=[]; Object.defineProperty(hostile,'0',{enumerable:true,get(){getters++;return fixture.selection.actions[0];}});
  assert.throws(()=>check(bindings,hostile),/ACTIONS/);assert.equal(getters,0);
  const stale = structuredClone(bindings); stale.steps[0]!.action_sha256 = '0'.repeat(64);
  assert.throws(() => check(stale), /ACTION_IDENTITY/);
  const policy = selectWorkflowRecoveryPolicy(workflow, { schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256, contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion' }, getReconciledSource('workflow_recovery'));
  const selection = { schema_version: 'domainspec.composed-workflow-selection/v1-candidate' as const, language: 'typescript' as const, module_root: fixture.selection.module_root, workflow, policy, operation_plan: operationPlan };
  const plan = planConfiguredComposedWorkflow(fixture.graph, fixture.boundary, fixture.fields, selection, composedWorkflowContract);
  assert.deepEqual(compileComposedWorkflow(fixture.graph,fixture.boundary,fixture.fields,fixture.selection.actions,bindings),workflow);
  assert.deepEqual(planComposedWorkflow(fixture.graph,fixture.boundary,fixture.fields,selection),plan);
  assert.deepEqual(plan, planConfiguredComposedWorkflow(fixture.graph, fixture.boundary, fixture.fields, selection, composedWorkflowContract));
  assert.equal(Object.hasOwn(plan.selection, 'operation_plan'), false, 'selection pins the plan hash instead of duplicating its complete artifacts');
  assert.equal(plan.artifacts.length, operationPlan.artifacts.length + 3);
  assert.throws(() => planConfiguredComposedWorkflow(fixture.graph, fixture.boundary, fixture.fields, { ...selection, operation_plan: structuredClone(operationPlan) }, composedWorkflowContract), /unvalidated plan/);
  assert.throws(() => planConfiguredComposedWorkflow(fixture.graph, fixture.boundary, fixture.fields, { ...selection, module_root: 'different' }, composedWorkflowContract), /stale composed operation plan/);
  const alternate=fixture.plan({...fixture.selection,actions:[{action,absence_failures:[{binding:'found',code:'OTHER_ABSENCE'}]}]});
  assert.throws(()=>planConfiguredComposedWorkflow(fixture.graph,fixture.boundary,fixture.fields,{...selection,operation_plan:alternate},composedWorkflowContract),/settlement vocabulary mismatch/);
  const native = loadPlannedComposition(t, plan, true),run=native.run, ids = { workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one' };
  const strip=(row:any)=>{const {action_sha256,...rest}=row;return rest;};
  const projectSelection={schema_version:'domainspec.reconciled-compilation/v2-candidate',profile_id:'domainspec.reconciled-typescript/v2-candidate',language:'typescript',module_root:fixture.selection.module_root,
    layout_version:'domainspec.existing-profile-layout/v1-candidate',value_profile:'domainspec.typescript-exact-uint64/v1',field_bindings:[],factories:fixture.selection.factories,operations:[f.action],
    value_compositions:[{composition:f.composition,absence_failures:fixture.selection.actions[0]!.absence_failures}],
    workflows:[{...bindings,steps:bindings.steps.map(strip),compensations:bindings.compensations.map(strip),recovery:{dependency_semantics:'needed-compensations-only',tie_break:'reverse-completion'}}]};
  // Workflow source selection carries no generated schema or action digest.
  delete (projectSelection.workflows[0] as any).schema_version;
  const projectPlan=planCompiledComposedReconciledProject(fixture.graph,projectSelection),view=selectReconciledArtifacts(projectPlan);
  assert.deepEqual(planCompiledComposedReconciledProject(fixture.graph,projectSelection),projectPlan);
  for(const node of fixture.graph.nodes)assert.ok(view.modules.some(m=>m.qualified_selectors.includes(node.selector)),node.selector);
  const rootView=selectReconciledArtifacts(projectPlan,['commerce:flow']);
  assert.ok(rootView.artifacts.some(a=>a.relative_path.endsWith('/queries/find.ts')));
  assert.ok(rootView.artifacts.some(a=>a.relative_path.endsWith('/mappings/copy.ts')));
  assert.throws(()=>decodeComposedReconciledCompilationSelection({...projectSelection,value_compositions:[]}),/coverage/);
  assert.throws(()=>decodeComposedReconciledCompilationSelection({...projectSelection,value_compositions:[...projectSelection.value_compositions,...projectSelection.value_compositions]}),/coverage/);
  assert.throws(()=>planCompiledComposedReconciledProject(structuredClone(fixture.graph),projectSelection));
  const projectRun=loadPlannedComposition(t,{artifacts:view.artifacts,modules:plan.modules});
  const projectResult=await projectRun({request:'incoming'},ids,{'commerce:submit':{store:{begin:async()=>({read:async()=>{throw Error('wrong port');},querySource:async()=>[{id:'allowed'}],commit:async()=>({status:'committed'}),rollback:async()=>{throw Error('unexpected rollback');}})}}});
  assert.equal(projectResult.status,'succeeded');assert.deepEqual(projectResult.value,{id:'allowed'});
  for(const [stage,code,valid]of [
    ['query-source:found','OPERATION_FAILED',true],['query:commerce:find','QUERY_CARDINALITY',true],['query:commerce:find','ORDER_NOT_FOUND',true],
    ['mapping:commerce:copy','OPERATION_FAILED',true],['query:commerce:find','OTHER_ABSENCE',false],['query-source:found','ORDER_NOT_FOUND',false],['mapping:commerce:missing','OPERATION_FAILED',false],
  ] as const)for(const status of ['failed','rejected'] as const)for(const cleanupFailed of [false,true]){
    const outcome={status,stage,code,continuation:action.failure_continuation,cleanupFailed};
    const expected=observeWorkflowStep(workflow,'first',{kind:'returned',outcome},getReconciledSource('workflow_outcome')).settlement;
    assert.equal(expected.commit_status,valid&&status==='failed'?'not-committed':'indeterminate');
    assert.deepEqual(native.provider.inspectOperationSettlement(outcome,action.failure_continuation,workflow.steps[0]!.precommit_stages),expected);
    assert.equal(inspectOperationSettlement(outcome,action.failure_continuation).commit_status,'indeterminate','legacy inspector must not gain a permissive prefix rule');
  }
  for (const scenario of ['success', 'absence', 'cardinality', 'uncertain'] as const) {
    let begins = 0; const calls: string[] = [];
    const result = await run({ request: 'incoming' }, ids, { 'commerce:submit': { store: { begin: async () => {
      const index = begins++; calls.push('begin:' + index);
      return { read: async () => { throw Error('wrong port'); }, querySource: async () => {
        calls.push('query:' + index); return index === 1 && scenario === 'absence' ? [] : index === 1 && scenario === 'cardinality' ? [{ id: 'allowed' }, { id: 'allowed' }] : [{ id: 'allowed' }];
      }, commit: async () => { calls.push('commit:' + index); if (index === 1 && scenario === 'uncertain') throw Error('unknown commit'); return { status: 'committed' }; }, rollback: async () => { calls.push('rollback:' + index); } };
    } } } });
    assert.equal(begins, 2, 'neither retry nor automatic compensation is dispatched');
    if (scenario === 'success') {
      assert.equal(result.status, 'succeeded'); assert.deepEqual(result.value, { id: 'allowed' });
      assert.deepEqual(calls, ['begin:0', 'query:0', 'commit:0', 'begin:1', 'query:1', 'commit:1']);
    } else {
      assert.equal(result.status, 'forward-stopped');
      const expected = planSelectedWorkflowRecovery(policy, { schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION, ...ids, completed_step_ids: ['first'], failed_step_id: 'second', failed_commit_status: scenario === 'uncertain' ? 'indeterminate' : 'not-committed' });
      assert.deepEqual(result.evaluation.recovery, expected);
      if (scenario === 'uncertain') { assert.equal(result.recovery_bindings, null); assert.equal(calls.at(-1), 'commit:1'); }
      else { assert.equal(result.recovery_bindings.bindings[0].action_sha256, action.action_sha256); assert.equal(calls.at(-1), 'rollback:1'); }
    }
  }
});

test('public composition API uses packaged contracts and preserves checked native artifacts', async t => {
  const f = composedFixture(t), fixture = plannedComposition(f);
  const action = compileComposedOperation(fixture.graph, fixture.boundary, fixture.fields, f.composition, f.action);
  assertCheckedComposedOperationAction(action);
  assert.deepEqual(action, fixture.selection.actions[0]!.action);
  const selection = { ...fixture.selection, actions: [{ ...fixture.selection.actions[0]!, action }] };
  const plan = planComposedOperations(fixture.graph, fixture.boundary, fixture.fields, selection);
  assert.deepEqual(plan, fixture.plan());
  assert.throws(() => planComposedOperations(fixture.graph, fixture.boundary, fixture.fields, structuredClone(selection)), /UNVALIDATED_COMPOSITION/);
  assert.throws(() => compileComposedOperation(structuredClone(fixture.graph), fixture.boundary, fixture.fields, f.composition, f.action));
  const run = loadPlannedComposition(t, plan);
  const result = await run({ request: 'incoming' }, { store: { begin: async () => ({ read: async () => { throw Error('wrong port'); }, querySource: async () => [{ id: 'allowed' }], rollback: async () => { throw Error('unexpected rollback'); }, commit: async () => ({ status: 'committed' }) }) } });
  assert.deepEqual(result, { status: 'committed', value: { id: 'allowed' } });
});

test('composed planner selects genuine profile dependencies and its complete artifacts compile and execute', async t => {
  const f = composedFixture(t), fixture = plannedComposition(f), plan = fixture.plan(); assertConfiguredComposedOperationsPlan(plan);
  assert.deepEqual(fixture.plan(), plan); assert.throws(() => assertConfiguredComposedOperationsPlan(structuredClone(plan)));
  assert.equal(Object.isFrozen(plan.artifacts), true); assert.equal(Object.isFrozen(fixture.selection), false);
  assert.equal(new Set(plan.artifacts.map(a => a.relative_path)).size, plan.artifacts.length);
  for (const artifact of plan.artifacts) { assert.equal(artifact.sha256, sha256(artifact.content)); assert.equal(artifact.size_bytes, Buffer.byteLength(artifact.content)); }
  const wrapper = plan.artifacts.find(a => a.relative_path === plan.modules[0]!.relative_path)!;
  assert.ok(wrapper.size_bytes < 16000); assert.equal(wrapper.content.includes('domain_graph'), false); assert.equal(wrapper.content.includes('typed_contract'), false);
  const run = loadPlannedComposition(t, plan), batches: any[] = [];
  const result = await run({ request: 'incoming' }, { store: { begin: async () => ({ read: async () => { throw Error('wrong port'); }, querySource: async () => [{ id: 'allowed' }], rollback: async () => { throw Error('unexpected rollback'); }, commit: async (batch: any) => { batches.push(batch); return { status: 'committed' }; } }) } });
  assert.deepEqual(result, { status: 'committed', value: { id: 'allowed' } }); assert.equal(batches[0].writes[0].value.id, 'allowed');
  assert.equal(run.descriptor.composition_sha256, fixture.selection.actions[0]!.action.value_composition.types_sha256);
});

test('composed planner fails closed on source drift, forged selections and unsafe roots without caller mutation', t => {
  const fixture = plannedComposition(composedFixture(t));
  assert.throws(() => fixture.plan(fixture.selection, composedGenerationContract + ' '), /contract drift/);
  assert.throws(() => fixture.plan({ ...fixture.selection, module_root: '../escape' }), /unsafe module root/);
  assert.throws(() => fixture.plan(structuredClone(fixture.selection)), /UNVALIDATED_COMPOSITION/);
  assert.throws(() => fixture.plan({ ...fixture.selection, actions: [...fixture.selection.actions, ...fixture.selection.actions] }), /duplicate action/);
  assert.throws(() => fixture.plan({ ...fixture.selection, factories: [] }), /FACTORY/);
  assert.throws(() => fixture.plan({ ...fixture.selection, actions: [{ ...fixture.selection.actions[0]!, absence_failures: [] }] }), /absence failure coverage/);
  let calls = 0; const getter = { ...fixture.selection, get module_root() { calls++; return 'generated'; } };
  assert.throws(() => fixture.plan(getter), /inert/); assert.equal(calls, 0);
  const sparse = [...fixture.selection.actions]; delete sparse[0]; assert.throws(() => fixture.plan({ ...fixture.selection, actions: sparse }), /action array bounds/);
});

test('planned public Mapping chain executes with qualified Interface modules and no Entity snapshot substitution', async t => {
  const f = composedFixture(t);
  const publicType = { kind: 'contract', interface_selector: 'commerce:api', contract_id: 'response' };
  f.node('api', 'Interface', { typed_contract: { schema_version: 'domainspec.typed-interface/v1', ontology_interface: 'FIXTURE-API', boundary_kind: 'external', version_policy: { schema_version: 'domainspec.interface-version-policy/v1', mode: 'backward', direction: 'consumer-to-provider', provider_version: '1.0.0' }, contracts: [{ contract_id: 'response', ontology_contract: 'FIXTURE-RESPONSE', fields: [{ name: 'public_id', ontology_field: 'FIXTURE-PUBLIC#publicId', meaning: 'public identity', type: scalar }] }], operations: [{ operation_id: 'find', operation_ref: 'commerce:find', request: scalar, result: { kind: 'contract', contract_id: 'response' } }] } });
  f.edge('api-find', 'exposes', 'api', 'find');
  f.node('outgoing', 'Mapping', { target: 'commerce:api', typed_contract: { schema_version: 'domainspec.typed-mapping/v3', ontology_mapping: 'FIXTURE-OUTGOING', inputs: [{ name: 'order', type: named(), use: null }], target: publicType, target_use: null, fields: [{ target: 'public_id', value: fieldPath('order'), default: null }], total: true } });
  f.node('incoming', 'Mapping', { target: 'commerce:order', typed_contract: { schema_version: 'domainspec.typed-mapping/v3', ontology_mapping: 'FIXTURE-INCOMING', inputs: [{ name: 'response', type: publicType, use: null }], target: named(), target_use: null, fields: [{ target: 'id', value: fieldPath('response', 'FIXTURE-PUBLIC#publicId'), default: null }], total: true } });
  f.edge('outgoing-api', 'maps', 'outgoing', 'api'); f.edge('incoming-order', 'maps', 'incoming', 'order'); f.save();
  f.composition.bindings.push(
    { kind: 'mapping', name: 'public_value', selector: 'commerce:outgoing', arguments: [{ parameter: 'order', value: at('copied') }] },
    { kind: 'mapping', name: 'restored', selector: 'commerce:incoming', arguments: [{ parameter: 'response', value: at('public_value') }] },
  );
  f.action.result.value = at('restored'); f.action.writes[0].value = at('restored');
  const plan = plannedComposition(f).plan(), run = loadPlannedComposition(t, plan);
  assert.ok(plan.artifacts.some(a => a.relative_path.endsWith('/interfaces/api.ts')));
  const result = await run({ request: 'incoming' }, { store: { begin: async () => ({ read: async () => { throw Error('wrong port'); }, querySource: async () => [{ id: 'allowed' }], rollback: async () => {}, commit: async () => ({ status: 'committed' }) }) } });
  assert.deepEqual(result, { status: 'committed', value: { id: 'allowed' } });
  assert.equal(plan.modules[0]!.descriptor.value_imports.length, 4);
});

test('composed artifact bytes are stable across batch order and shared dependencies are emitted once', t => {
  const f = composedFixture(t);
  f.node('submit-again', 'Operation', { ...f.operationBody, writes: ['order-state'] });
  f.edge('again-order', 'reads', 'submit-again', 'order'); f.edge('allowed-again', 'enforces', 'allowed', 'submit-again'); f.save();
  const fixture = plannedComposition(f), single = fixture.plan();
  const composition = structuredClone(f.composition); composition.operation_ref = 'commerce:submit-again';
  const action = structuredClone(f.action); action.selector = 'commerce:submit-again';
  const typed = compileOperationValueTypes(fixture.graph, fixture.fields, fixture.check(composition, action));
  const second = compileComposedOperationActionBindings(fixture.graph, fixture.boundary, fixture.fields, typed, actionContract);
  const selection = { ...fixture.selection, actions: [...fixture.selection.actions, { action: second, absence_failures: [{ binding: 'found', code: 'ORDER_NOT_FOUND' }] }] };
  const batch = fixture.plan(selection), reverse = fixture.plan({ ...selection, actions: [...selection.actions].reverse() });
  assert.deepEqual(reverse, batch);
  for (const file of [single.modules[0]!.relative_path, single.modules[0]!.provider_path]) assert.deepEqual(batch.artifacts.find(a => a.relative_path === file), single.artifacts.find(a => a.relative_path === file));
  assert.equal(batch.artifacts.length, single.artifacts.length + 2);
  assert.equal(batch.artifacts.filter(a => a.relative_path.endsWith('/queries/find.ts')).length, 1);
  const stale = structuredClone(fixture.graph); assert.throws(() => planConfiguredComposedOperations(stale, fixture.boundary, fixture.fields, selection, composedGenerationContract));
});
