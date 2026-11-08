import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings, OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {compileWorkflowBindings, decodeWorkflowBindings, assertCheckedWorkflowBindings, WORKFLOW_BINDINGS_VERSION, WORKFLOW_BINDING_CONTRACT_SHA256} from '../../src/typed-operation/workflow-bindings.ts';
import {WORKFLOW_OCCURRENCES_VERSION} from '../../src/typed-backend/workflow-occurrences.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planWorkflowRecovery} from '../../../architecture-conformance/targets/typescript/workflow-compensation-v1.ts';

const project = path.resolve(import.meta.dirname, '../../../..');
const read = (p: string) => fs.readFileSync(path.join(project, 'development/reconciliation-v1', p), 'utf8');
const contract = read('profile-compiler-reconciliation/workflow-binding-contract.json');
const actionContract = read('profile-compiler-reconciliation/operation-action-contract.json');
const boundaryContract = read('contracts/composition-boundary.json');
const fieldContract = read('contracts/exact-field-and-reference-model.json');
const scalar = (name = 'String') => ({kind: 'scalar', name});
const named = (selector: string) => ({kind: 'named', selector});
const input = (name: string, ...properties: string[]) => ({op: 'input', name, properties});
const result = (step_id: string, ...properties: string[]) => ({op: 'step-result', step_id, properties});
const at = (root: string) => ({op: 'path', root, properties: []});
const literal = (type: string, value: any) => ({op: 'literal', type, value});

function fixture(t: any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-workflow-bindings-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const source = path.join(temp, 'source'), nodes: string[] = [], edges: string[] = [];
  const write = (p: string, v: any) => {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, JSON.stringify(v, null, 2) + '\n');};
  const node = (id: string, kind: string, body: any) => {if (!nodes.includes(id)) nodes.push(id); write('specs/commerce/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'commerce', node_id: id, kind, body: {description: id, ...body}});};
  const edge = (id: string, relationship: string, from: string, to: string) => {if (!edges.includes(id)) edges.push(id); write('specs/commerce/edges/' + id + '.json', {schema_version: 'domainspec.edge/v1', edge_id: id, feature_id: 'commerce', relationship, source_node_id: from, target_node_id: to, scope: 'feature'});};
  node('order', 'Entity', {fields: ['id'], typed_contract: {schema_version: 'domainspec.typed-record/v1', ontology_node: 'FIXTURE-ORDER', properties: [{ontology_property: 'FIXTURE-ORDER#id', name: 'id', type: scalar(), cardinality: 'one', identity: true, meaning: 'order identity'}]}});
  node('allowed', 'Rule', {predicate: 'structured:domainspec.typed-rule/v2', typed_contract: {schema_version: 'domainspec.typed-rule/v2', ontology_rule: 'FIXTURE-ALLOWED', parameters: [{name: 'allowed', type: scalar('Bool')}], expression: {op: 'eq', left: at('allowed'), right: literal('Bool', true)}}});
  for (const id of ['posted', 'released']) node(id, 'Event', {event_type: id, version: '1', occurrence_id: {field_id: 'event-id', type_ref: {kind: 'primitive', name: 'uuid'}, required: true}, occurred_at_policy: id === 'posted' ? 'required' : 'generated', payload: [{field_id: 'order-id', type_ref: {kind: 'reference', selector: 'commerce:order'}, required: true}, {field_id: 'delta', type_ref: {kind: 'primitive', name: 'integer'}, required: false}]});
  const inputs: any[] = [{name: 'order', type: named('commerce:order')}, {name: 'amount', type: scalar('UInt64')}];
  const definitions: any[] = [];
  for (const [id, event] of [['post', 'posted'], ['release', 'released']]) {
    node(id!, 'Operation', {reads: [], writes: [], effects: ['notice'], guard: 'allowed', failure_continuation: 'return-' + id + '-error'});
    edge(id + '-guard', 'enforces', 'allowed', id!); edge(id + '-event', 'produces', id!, event!);
    definitions.push({schema_version: OPERATION_ACTION_BINDINGS_VERSION, selector: 'commerce:' + id, inputs: structuredClone(inputs), reads: [], writes: [], guards: [{selector: 'commerce:allowed', arguments: [{parameter: 'allowed', value: literal('Bool', true)}]}], events: [{slot: 'notice', target: 'commerce:' + event, parameter: 'notice_input'}], result: {type: named('commerce:order'), value: at('order')}, atomicity: 'state-and-outbox', continuation: 'awaited-settlement'});
  }
  const workflow: any = {schema_version: WORKFLOW_OCCURRENCES_VERSION, ontology_workflow: 'FIXTURE-POST-TWICE', steps: [{step_id: 'first', operation_ref: 'commerce:post'}, {step_id: 'second', operation_ref: 'commerce:post'}], compensations: [{compensation_id: 'first', for_step: 'first', operation_ref: 'commerce:release', depends_on: ['second']}, {compensation_id: 'second', for_step: 'second', operation_ref: 'commerce:release', depends_on: []}]};
  const save = () => {
    node('flow', 'Workflow', {typed_contract: workflow});
    write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'workflow-bindings', features: ['commerce'], cross_feature_edges: []});
    write('specs/commerce/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'commerce', nodes, edges});
  };
  edge('flow-post', 'orchestrates', 'flow', 'post'); edge('flow-release', 'orchestrates', 'flow', 'release'); save();
  const compile = () => {
    const graph = loadCompiledProjectGraph(source), certificate = createCompiledProjectCertificate(graph);
    const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, boundaryContract);
    const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['commerce:order'], bindings: []}, fieldContract);
    const actions = definitions.map(d => compileOperationActionBindings(graph, boundary, fields, d, actionContract));
    const call = (id: string, compensation = false): any => ({[compensation ? 'compensation_id' : 'step_id']: id, action_sha256: actions[compensation ? 1 : 0]!.action_sha256,
      arguments: [{parameter: 'order', value: compensation ? result(id) : id === 'first' ? input('order') : result('first')}, {parameter: 'amount', value: input('amount')}],
      events: [{parameter: 'notice_input', input: (compensation ? 'undo_' : 'post_') + id}]});
    const bindings: any = {schema_version: WORKFLOW_BINDINGS_VERSION, selector: 'commerce:flow', inputs: structuredClone(inputs),
      event_inputs: ['first', 'second'].flatMap(id => [{name: 'post_' + id, event_ref: 'commerce:posted'}, {name: 'undo_' + id, event_ref: 'commerce:released'}]),
      steps: [call('first'), call('second')], compensations: [call('first', true), call('second', true)], result: {type: named('commerce:order'), value: result('second')}};
    return {graph, boundary, fields, actions, bindings, check: (b: any = bindings, a = actions, c = contract) => compileWorkflowBindings(graph, boundary, fields, a, b, c)};
  };
  return {temp, source, write, node, save, workflow, definitions, compile, ...compile()};
}
const rejects = (fn: () => unknown, code: string) => assert.throws(fn, new RegExp('WORKFLOW_BINDING_' + code));

test('Workflow calls pin checked actions and retain exact occurrence, Event and result identities', t => {
  const f = fixture(t), before = canonicalJson(f.bindings), w = f.check(); assertCheckedWorkflowBindings(w);
  assert.equal(sha256(contract), WORKFLOW_BINDING_CONTRACT_SHA256); assert.deepEqual(f.check(), w);
  assert.equal(canonicalJson(f.bindings), before); assert.equal(Object.isFrozen(f.bindings), false);
  const frozen = (v: any) => {if (v && typeof v === 'object') {assert.ok(Object.isFrozen(v)); Object.values(v).forEach(frozen);}}; frozen(w);
  const {workflow_sha256, ...body} = w; assert.equal(workflow_sha256, sha256(canonicalJson(body)));
  assert.deepEqual(w.steps.map(s => [s.step_id, s.operation_ref]), [['first', 'commerce:post'], ['second', 'commerce:post']]);
  assert.equal(f.graph.relationships.filter(r => r.relationship === 'orchestrates').length, 2);
  assert.deepEqual(w.compensations[0]!.depends_on, ['second']); assert.equal(w.compensations[0]!.for_step, 'first');
  assert.equal(w.event_inputs[0]!.contract.occurred_at_policy, 'required'); assert.equal(w.event_inputs[1]!.contract.occurred_at_policy, 'generated');
  assert.equal(w.event_inputs[0]!.contract.payload[1]!.type_ref.name, 'integer');
  assert.equal(w.execution, 'not-performed'); assert.equal(w.recovery_policy, 'not-selected');
  rejects(() => assertCheckedWorkflowBindings(structuredClone(w)), 'UNVALIDATED');
  fs.renameSync(f.source, path.join(f.temp, 'moved')); assert.deepEqual(f.check(), w);
});

test('Closed bounded Workflow data and registered action arrays do not invoke ordinary accessors', t => {
  const f = fixture(t); let reads = 0;
  for (const mutate of [(b: any) => b.extra = true, (b: any) => b.schema_version += '-future', (b: any) => b.inputs.push(b.inputs[0]), (b: any) => b.event_inputs[0].name = 'order', (b: any) => b.steps.push(b.steps[0]), (b: any) => b.compensations.push(b.compensations[0]), (b: any) => b.steps[0].arguments.push(b.steps[0].arguments[0]), (b: any) => b.steps[0].events.push(b.steps[0].events[0]), (b: any) => b.steps[0].step_id += '\n', (b: any) => b.steps[0].arguments[0].value = at('order'), (b: any) => b.steps[0].action_sha256 = 'not-a-hash']) {
    const b = structuredClone(f.bindings); mutate(b); assert.throws(() => decodeWorkflowBindings(b));
  }
  const getter = {...f.bindings, get inputs() {reads++; return f.bindings.inputs;}}; assert.throws(() => decodeWorkflowBindings(getter));
  const hidden = structuredClone(f.bindings); Object.defineProperty(hidden, 'selector', {enumerable: false}); assert.throws(() => decodeWorkflowBindings(hidden));
  assert.throws(() => decodeWorkflowBindings({...f.bindings, [Symbol()]: true}));
  assert.throws(() => decodeWorkflowBindings({...f.bindings, steps: new Array(4294967295)}));
  const cyclic = structuredClone(f.bindings); cyclic.result.value = cyclic; assert.throws(() => decodeWorkflowBindings(cyclic));
  const a = [...f.actions]; Object.defineProperty(a, '0', {get() {reads++; return f.actions[0];}, enumerable: true}); rejects(() => f.check(f.bindings, a), 'ACTIONS');
  rejects(() => f.check(f.bindings, Object.assign([...f.actions], {extra: true})), 'ACTIONS');
  assert.equal(reads, 0);
});

test('Exact source call, action, ordinary argument and Event coverage cannot be omitted or widened', t => {
  const f = fixture(t);
  for (const mutate of [(b: any) => b.steps.pop(), (b: any) => b.steps[0].step_id = 'other', (b: any) => b.compensations.pop(), (b: any) => b.steps[0].arguments.pop(), (b: any) => b.steps[0].events = [], (b: any) => b.steps[0].events.push({parameter: 'extra', input: 'post_first'}), (b: any) => b.event_inputs.push({name: 'unused', event_ref: 'commerce:posted'})]) {
    const b = structuredClone(f.bindings); mutate(b); rejects(() => f.check(b), 'COVERAGE');
  }
  rejects(() => f.check(f.bindings, f.actions.slice(0, 1)), 'COVERAGE');
  rejects(() => f.check(f.bindings, [...f.actions, f.actions[0]!]), 'DUPLICATE');
  for (const target of ['commerce:order', 'commerce:missing']) {const b = structuredClone(f.bindings); b.event_inputs[0].event_ref = target; rejects(() => f.check(b), 'EVENT_INPUT');}
  for (const name of ['undo_first', 'order', 'missing']) {const b = structuredClone(f.bindings); b.steps[0].events[0].input = name; rejects(() => f.check(b), 'EVENT_TYPE');}
});

test('Only the guaranteed forward prefix supplies success results, even with later compensation dependencies', t => {
  const f = fixture(t);
  for (const [call, value] of [['first', result('first')], ['first', result('second')], ['second', result('second')], ['second', result('missing')], ['second', input('post_first')]]) {
    const b = structuredClone(f.bindings); b.steps.find((s: any) => s.step_id === call).arguments[0].value = value; rejects(() => f.check(b), 'UNAVAILABLE_VALUE');
  }
  const compensation = structuredClone(f.bindings); compensation.compensations[0].arguments[0].value = result('second'); rejects(() => f.check(compensation), 'UNAVAILABLE_VALUE');
  compensation.compensations[0].arguments[0].value = result('first'); compensation.compensations[1].arguments[0].value = result('first'); assert.ok(f.check(compensation));
  const b = structuredClone(f.bindings); b.result.value = result('commerce:post'); assert.throws(() => f.check(b));
  b.result.value = input('missing'); rejects(() => f.check(b), 'UNAVAILABLE_VALUE');
});

test('Exact native value categories and ontology paths are checked without coercion or hidden calculation', t => {
  const f = fixture(t);
  const b = structuredClone(f.bindings); b.steps[0].arguments[1].value = literal('UInt64', '18446744073709551615'); assert.ok(f.check(b));
  b.steps[0].arguments[1].value.value = '18446744073709551616'; assert.throws(() => f.check(b));
  b.steps[0].arguments[1].value = input('order', 'FIXTURE-ORDER#id'); rejects(() => f.check(b), 'ARGUMENT_TYPE');
  b.steps[0].arguments[1].value = {op: 'calculate', selector: 'commerce:total'}; rejects(() => f.check(b), 'EXPRESSION');
  b.steps[0].arguments[1].value = input('amount'); b.result = {type: scalar(), value: result('second', 'FIXTURE-ORDER#id')}; assert.ok(f.check(b));
  b.result.value.properties = ['id']; assert.throws(() => f.check(b));
  b.result = {type: scalar(), value: result('second')}; rejects(() => f.check(b), 'RESULT_TYPE');
  for (const type of [{kind: 'optional', element: named('commerce:order')}, {kind: 'list', element: named('commerce:order')}, {kind: 'set', element: named('commerce:order')}, {kind: 'sum', variants: [{ontology_variant: 'FIXTURE-RESULT#Empty', name: 'Empty', payload: null}, {ontology_variant: 'FIXTURE-RESULT#Found', name: 'Found', payload: named('commerce:order')}]}]) {
    const c = structuredClone(f.bindings); c.inputs.push({name: 'structured', type}); c.result = {type, value: input('structured')}; assert.deepEqual(f.check(c).bindings.result.type, type);
    c.steps[0].arguments[0].value = input('structured'); rejects(() => f.check(c), 'ARGUMENT_TYPE');
    c.steps[0].arguments[0].value = input('order'); c.result = {type: scalar(), value: input('structured', 'FIXTURE-ORDER#id')}; assert.throws(() => f.check(c));
  }
  const c = structuredClone(f.bindings); c.inputs.push({name: 'orders', type: {kind: 'list', element: named('commerce:order')}});
  c.result = {type: {kind: 'set', element: named('commerce:order')}, value: {op: 'to_set', value: input('orders')}}; assert.ok(f.check(c));
  c.result.value.value = input('order'); rejects(() => f.check(c), 'TYPE');
});

test('Checked object brands, exact action pins and graph/field/definition evidence reject substitution', t => {
  const f = fixture(t); rejects(() => f.check(f.bindings, f.actions, contract + ' '), 'CONTRACT_DRIFT');
  rejects(() => f.check({...f.bindings, selector: 'commerce:order'}), 'ROOT');
  const b = structuredClone(f.bindings); b.steps[0].action_sha256 = f.actions[1]!.action_sha256; rejects(() => f.check(b), 'ACTION_IDENTITY');
  for (const [g, boundary, fields, actions] of [[structuredClone(f.graph), f.boundary, f.fields, f.actions], [f.graph, structuredClone(f.boundary), f.fields, f.actions], [f.graph, f.boundary, structuredClone(f.fields), f.actions], [f.graph, f.boundary, f.fields, structuredClone(f.actions)]]) assert.throws(() => compileWorkflowBindings(g, boundary, fields, actions, f.bindings, contract));
  f.definitions[0].result = {type: scalar(), value: literal('String', 'changed')}; const changed = f.compile(); rejects(() => f.check(f.bindings, changed.actions), 'ACTION_IDENTITY');
  f.workflow.ontology_workflow = 'FIXTURE-OTHER-WORKFLOW'; f.save(); const other = f.compile();
  rejects(() => compileWorkflowBindings(other.graph, f.boundary, f.fields, other.actions, other.bindings, contract), 'CROSS_GRAPH');
  rejects(() => compileWorkflowBindings(other.graph, other.boundary, other.fields, f.actions, other.bindings, contract), 'STALE_ACTION');
});

test('Same-typed occurrence swaps and input changes alter meaning without changing canonical edges', t => {
  const f = fixture(t), first = f.check();
  const b = structuredClone(f.bindings); b.result.value = result('first'); const swapped = f.check(b);
  assert.notEqual(first.workflow_sha256, swapped.workflow_sha256); assert.deepEqual(first.certificate, swapped.certificate);
  b.result.value = result('second'); b.steps[1].arguments[0].value = input('order'); assert.notEqual(first.workflow_sha256, f.check(b).workflow_sha256);
  const edges = canonicalJson(f.graph.relationships); f.workflow.steps.reverse(); f.save(); const reordered = f.compile(); rejects(() => reordered.check(), 'UNAVAILABLE_VALUE');
  const c = structuredClone(reordered.bindings); c.steps.forEach((s: any) => s.arguments[0].value = input('order')); c.compensations.forEach((s: any) => s.arguments[0].value = input('order'));
  const w = reordered.check(c); assert.deepEqual(w.steps.map(s => s.step_id), ['second', 'first']); assert.equal(canonicalJson(reordered.graph.relationships), edges);
  const reverseRows = structuredClone(c); reverseRows.steps.reverse(); reverseRows.compensations.reverse(); const w2 = reordered.check(reverseRows);
  assert.deepEqual(w2.steps, w.steps); assert.deepEqual(w2.compensations, w.compensations);
});

test('Versioned bindings reject legacy Workflow source rather than creating occurrence identities', t => {
  const f = fixture(t);
  f.node('flow', 'Workflow', {steps: ['post'], compensations: ['release']});
  const legacy = f.compile();
  assert.throws(() => legacy.check(), /MTCLI_WORKFLOW_OCCURRENCE/);
  assert.equal(fs.readFileSync(path.join(f.source, 'specs/commerce/nodes/flow.json'), 'utf8').includes('typed_contract'), false);
});

test('A checked dependency can be inactive after a partial failure; existing recovery semantics reject that plan', t => {
  const f = fixture(t); assert.ok(f.check());
  const identity = {workflowId: 'flow', workflowExecutionId: 'run-one', failureOccurrenceId: 'failure-one', failedStepId: 'third', orchestratedOperationIds: ['undo-first', 'undo-second'],
    mappings: [{stepId: 'first', operationId: 'undo-first', dependsOn: ['undo-second']}, {stepId: 'second', operationId: 'undo-second', dependsOn: []}]};
  const complete = planWorkflowRecovery({...identity, completedStepIds: ['first', 'second']});
  assert.deepEqual(complete.recoveryIntent!.plan.map(p => p.operationId), ['undo-second', 'undo-first']);
  assert.throws(() => planWorkflowRecovery({...identity, failedStepId: 'second', completedStepIds: ['first']}), (e: any) => e.code === 'RECOVERY_DEPENDENCY_INVALID');
  // This records a pending meaning choice, not a new default or an executor.
  assert.equal(f.check().recovery_policy, 'not-selected');
});
