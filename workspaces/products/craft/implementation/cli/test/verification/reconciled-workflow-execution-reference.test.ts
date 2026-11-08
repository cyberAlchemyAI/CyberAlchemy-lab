import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import test from 'node:test';
import {workflowFixture, nativeWorkflow, workflowProject} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, order, eventParameters} from '../helpers/workflow-values.ts';
import {planCompiledReconciledProject, selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {operationValueRecipe} from '../../src/verification/reconciled-operation-cases.ts';
import {createWorkflowExecutionReference, WorkflowExecutionCapacity, type WorkflowExecutionCase} from '../../src/verification/reconciled-workflow-execution-reference.ts';
import {WORKFLOW_FIXTURE_RUNNER} from '../../src/verification/reconciled-workflow-fixture.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';

const base = path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions = Object.fromEntries(Object.entries({execution: 'semantic-workflow-execution-contract.json', binding: 'semantic-workflow-binding-contract.json', values: 'semantic-workflow-values-contract.json', outcomes: 'semantic-workflow-controls-contract.json'}).map(([k, p]) => [k, fs.readFileSync(path.join(base, p), 'utf8')])) as any;
function reference(f: ReturnType<typeof workflowFixture>) {
  const plan = planCompiledReconciledProject(f.graph, f.selection), node = f.graph.nodes.find(n => n.kind === 'Workflow')!;
  return {plan, oracle: createWorkflowExecutionReference(node, f.graph, plan, definitions)};
}
function row(oracle: ReturnType<typeof createWorkflowExecutionReference>, input: unknown = {amount: '7'}): WorkflowExecutionCase {
  return {input: operationValueRecipe(input), identity: {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, capture: false,
    steps: oracle.binding.workflow.steps.map(step => ({step_id: step.step_id, mode: 'committed', reads: [], clocks: oracle.binding.operations.find(o => o.action.bindings.selector === step.operation_ref)!.action.events.filter(e => e.contract.occurred_at_policy === 'generated').map(e => ({slot: e.slot, value: 'time-' + step.step_id}))}))};
}
async function fixture(f: ReturnType<typeof workflowFixture>, mutate?: (p: string, content: string) => string) {
  const {plan, oracle} = reference(f), native = nativeWorkflow({...f, nativePlan: () => selectReconciledArtifacts(plan)}, mutate);
  const file = path.join(native.root, 'workflow-fixture.mjs'); fs.writeFileSync(file, WORKFLOW_FIXTURE_RUNNER);
  const {observeWorkflowFixture} = await import(pathToFileURL(file).href);
  return {oracle, native, observe: (c: WorkflowExecutionCase) => observeWorkflowFixture(native.run, oracle.binding.workflow.steps, oracle.captureCase(c))};
}
const copy = <T>(v: T): T => structuredClone(v);
const outcomeField = (v: any, field: string) => v.outcome?.[1]?.find((r: any) => r[0] === field)?.[1];

function effectful(t: Parameters<typeof workflowFixture>[0]) {
  const f = workflowValuesFixture(t, {events: true}), source = path.join(f.root, 'source');
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(source, p), 'utf8'));
  const write = (p: string, v: unknown) => fs.writeFileSync(path.join(source, p), JSON.stringify(v));
  const feature = read('specs/commerce/feature.json'), selection: any = copy(f.selection);
  for (const op of selection.operations) {
    const id = op.selector.split(':')[1], node = read('specs/commerce/nodes/' + id + '.json');
    node.body.reads = ['current-order']; node.body.writes = ['order-state']; write('specs/commerce/nodes/' + id + '.json', node);
    const edge_id = id + '-reads-order'; feature.edges.push(edge_id);
    write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship: 'reads', source_node_id: id, target_node_id: 'order', scope: 'feature'});
    op.reads = [{slot: 'current-order', target: 'commerce:order', parameter: 'current', key: {op: 'path', root: 'amount', properties: ['TEST-ORDER#id']}}];
    op.writes = [{slot: 'order-state', target: 'commerce:order', mode: 'replace', value: {op: 'path', root: 'amount', properties: []}}];
    op.result.value = {op: 'path', root: 'current', properties: []};
  }
  const posted = read('specs/commerce/nodes/posted.json'); posted.body.occurred_at_policy = 'generated'; write('specs/commerce/nodes/posted.json', posted);
  write('specs/commerce/feature.json', feature);
  return {...f, graph: loadCompiledProjectGraph(source), selection};
}

test('real Workflow composes typed transactional reads, state/outbox writes and generated clocks', async t => {
  const f = await fixture(effectful(t)), parameters: any = {amount: order(), ...eventParameters()}; delete parameters.post.occurredAt;
  const seed: any = row(f.oracle, parameters);
  seed.steps.forEach((s: any) => s.reads = [{slot: 'current-order', value: operationValueRecipe(order('1', 'read-' + s.step_id))}]);
  assert.deepEqual(await f.observe(seed), f.oracle.expected(seed));
  assert.equal(f.oracle.expected(seed).read_requests.length, 4);
  assert.equal(f.oracle.expected(seed).clock_calls.length, 4);
  assert.equal(f.oracle.expected(seed).batches.length, 4);
  for (let at = 0; at < seed.steps.length; at++) {
    for (const change of [
      (s: any) => s.reads[0].value = {tag: 'null'},
      (s: any) => s.reads[0].throws = true,
      (s: any) => s.reads[0].value = operationValueRecipe(order('2')),
      (s: any) => s.clocks[0].mode = 'throw',
      (s: any) => s.clocks[0].value = '',
      (s: any) => s.mode = 'rejected',
      (s: any) => s.mode = 'commit-throw'
    ]) {const c = copy(seed); change(c.steps[at]); assert.deepEqual(await f.observe(c), f.oracle.expected(c), 'effect failure at ' + at);}
  }
  const missing = copy(seed); missing.steps.forEach((s: any) => s.clocks[0].mode = 'missing');
  assert.deepEqual(await f.observe(missing), f.oracle.expected(missing));
  assert.deepEqual(f.oracle.expected(missing).port_trace, []);
  const incompatible = copy(seed); incompatible.steps[2].clocks[0].mode = 'missing';
  assert.throws(() => f.oracle.captureCase(incompatible), /clock availability/);
  for (const mode of ['getter', 'non-enumerable', 'symbol'] as const) {
    const c = copy(seed); c.steps[1].reads[0].value = {tag: 'bad', base: c.steps[1].reads[0].value, mode, field: 'id'};
    assert.deepEqual(await f.observe(c), f.oracle.expected(c));
  }
});

test('composed Workflow reference and unchanged native Operations agree across every settlement mode and occurrence', async t => {
  const f = await fixture(workflowFixture(t)), seed = row(f.oracle);
  for (const mode of ['committed', 'rejected', 'indeterminate', 'begin-throw', 'commit-throw', 'rollback-throw', 'receipt-empty', 'receipt-unknown', 'receipt-extra', 'receipt-null', 'receipt-getter', 'receipt-inherited', 'receipt-symbol', 'receipt-hidden', 'receipt-array', 'receipt-undefined'] as const) {
    for (let at = 0; at < seed.steps.length; at++) {
      const c: any = copy(seed); c.steps[at].mode = mode;
      assert.deepEqual(await f.observe(c), f.oracle.expected(c), mode + ':' + at);
    }
  }
  assert.equal(outcomeField(f.oracle.expected(seed), 'status')[1], 'succeeded');
  assert.equal(outcomeField(f.oracle.expected(seed), 'value')[0], 'bigint');
});

test('typed Entity and Event values compose through every stopped prefix with exact recovery arguments', async t => {
  const f = await fixture(workflowValuesFixture(t, {events: true})), seed = row(f.oracle, {amount: order(), ...eventParameters()});
  assert.deepEqual(await f.observe(seed), f.oracle.expected(seed));
  for (let at = 0; at < seed.steps.length; at++) for (const mode of ['rejected', 'indeterminate', 'commit-throw'] as const) {
    const c: any = copy(seed); c.steps[at].mode = mode;
    assert.deepEqual(await f.observe(c), f.oracle.expected(c), mode + ':' + at);
  }
  const c: any = copy(seed); c.steps[2].mode = 'rejected';
  assert.equal(outcomeField(f.oracle.expected(c), 'bindings_status')[1], 'ready');
  assert.equal(f.oracle.expected(c).batches.length, 3);
});

test('source input and captured dependency slots survive caller mutation while every port is held', async t => {
  const f = await fixture(workflowValuesFixture(t)), c = {...row(f.oracle, {amount: order()}), capture: true};
  const observed = await f.observe(c);
  assert.deepEqual(observed, f.oracle.expected(c));
  assert.equal(observed.settled_while_pending, false);
  assert.equal(observed.overlapping_ports, false);
  assert.equal(observed.port_trace.filter((p: string) => p.endsWith(':begin')).length, 4);
});

test('invalid source-input recipes reject before effects without reading accessors or inventing settlement', async t => {
  const f = await fixture(workflowFixture(t)), seed = row(f.oracle);
  for (const mode of ['getter', 'non-enumerable', 'missing-field', 'symbol', 'inherited', 'extra', 'null', 'array'] as const) {
    const c = {...seed, input: {tag: 'bad', base: seed.input, mode, field: 'amount'}} as WorkflowExecutionCase;
    const observed = await f.observe(c); assert.deepEqual(observed, f.oracle.expected(c), mode);
    assert.equal(observed.rejected, true); assert.equal(observed.getter_reads, 0); assert.deepEqual(observed.port_trace, []);
  }
  const identity = {...seed, identity: {...seed.identity, workflow_execution_id: 'invalid\n'}};
  assert.deepEqual(await f.observe(identity), f.oracle.expected(identity));
});

test('case custody rejects malformed occurrences, slots, modes, primitives, accessors and capacities', t => {
  const f = workflowFixture(t), {oracle, plan} = reference(f), seed = row(oracle); let reads = 0;
  const bad: any[] = [{...seed, other: true}, {...seed, capture: 'yes'}, {...seed, identity: {...seed.identity, other: true}}, {...seed, steps: seed.steps.slice(1)}];
  for (const edit of [(c: any) => c.steps.reverse(), (c: any) => c.steps[1].step_id = c.steps[0].step_id, (c: any) => c.steps[0].mode = 'other', (c: any) => c.steps[0].reads.push({slot: 'foreign', value: {tag: 'null'}}), (c: any) => c.steps[0].clocks.push({slot: 'foreign', value: 'time'}), (c: any) => delete c.steps[0]]) {const c = copy(seed); edit(c); bad.push(c);}
  bad.push(Object.defineProperty({...seed}, 'input', {enumerable: true, get() {reads++; return seed.input;}}));
  for (const c of bad) assert.throws(() => oracle.captureCase(c));
  assert.equal(reads, 0);
  assert.throws(() => oracle.captureCase({...seed, input: {tag: 'scalar', value: 'x'.repeat(8388608)}}), WorkflowExecutionCapacity);
  assert.throws(() => oracle.captureCase({...seed, input: {tag: 'fields', fields: Object.fromEntries(Array.from({length: 9}, (_, i) => ['field' + i, {tag: 'scalar', value: 'x'.repeat(1048576)}]))}}), WorkflowExecutionCapacity);
  assert.throws(() => oracle.captureCase({...seed, input: {tag: 'scalar', value: 'β'.repeat(4194304)}}), WorkflowExecutionCapacity);
  assert.throws(() => createWorkflowExecutionReference(f.graph.nodes.find(n => n.kind === 'Workflow')!, f.graph, plan, {...definitions, execution: definitions.execution + '\n'}), /definition drift/);
  assert.ok(Object.isFrozen(oracle.captureCase(seed).steps));
});

test('selected recovery order and no-compensation source retain their existing behaviors', async t => {
  for (const options of [{dependencies: [[], ['undo-first'], ['undo-second']]}, {noCompensations: true}]) {
    const f = await fixture(workflowFixture(t, options)), c: any = row(f.oracle); c.steps[3].mode = 'rejected';
    assert.deepEqual(await f.observe(c), f.oracle.expected(c));
  }
});

test('distinct and repeated forward Operations retain independent dependency slots and result flow', async t => {
  const base = workflowFixture(t), source = path.join(base.root, 'source');
  const read = (p: string) => JSON.parse(fs.readFileSync(path.join(source, p), 'utf8'));
  const write = (p: string, v: unknown) => fs.writeFileSync(path.join(source, p), JSON.stringify(v));
  const feature = read('specs/commerce/feature.json'), op = read('specs/commerce/nodes/perform.json');
  op.node_id = 'other'; op.body.failure_continuation = 'return-other-error'; write('specs/commerce/nodes/other.json', op); feature.nodes.push('other');
  for (const [from, relationship] of [['allowed', 'enforces'], ['flow', 'orchestrates']]) {
    const edge_id = from + '-' + relationship + '-other'; feature.edges.push(edge_id);
    write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship, source_node_id: from, target_node_id: 'other', scope: 'feature'});
  }
  const flow = read('specs/commerce/nodes/flow.json');
  flow.body.typed_contract.steps[1].operation_ref = 'commerce:other'; flow.body.typed_contract.steps[3].operation_ref = 'commerce:other';
  write('specs/commerce/nodes/flow.json', flow); write('specs/commerce/feature.json', feature);
  const selection: any = copy(base.selection), action = copy(selection.operations[0]);
  action.selector = 'commerce:other'; action.result.value = {op: 'literal', type: 'UInt64', value: '11'}; selection.operations.push(action);
  const f = await fixture({...base, graph: loadCompiledProjectGraph(source), selection}), seed = {...row(f.oracle), capture: true};
  assert.deepEqual(await f.observe(seed), f.oracle.expected(seed));
  assert.deepEqual(outcomeField(f.oracle.expected(seed), 'value'), ['bigint', '11']);
  for (let at = 0; at < seed.steps.length; at++) for (const mode of ['rejected', 'begin-throw', 'commit-throw'] as const) {
    const c: any = copy(seed); c.steps[at].mode = mode; assert.deepEqual(await f.observe(c), f.oracle.expected(c), mode + ':' + at);
  }
});

test('compiled await and value mutants disagree with independent expected execution', async t => {
  const mutations = [
    (p: string, s: string) => p.endsWith('/flow.provider.ts') ? s.replace('raw=await call0(args,dep0)', 'raw=call0(args,dep0)') : s,
    (p: string, s: string) => p.endsWith('/flow.provider.ts') ? s.replace('material.result(input,results)', '0n') : s,
    (p: string, s: string) => p.endsWith('/perform.provider.ts') ? s.replace('await transaction.commit(', 'transaction.commit(') : s
  ];
  for (const [index, mutate] of mutations.entries()) {
    let changes = 0;
    const f = await fixture(workflowFixture(t), (p, s) => {const next = mutate(p, s); if (next !== s) changes++; return next;});
    assert.ok(changes > 0, 'mutation applied');
    const c = row(f.oracle);
    let actual: unknown;
    try {actual = await f.observe(c);} catch (error) {actual = {error: String(error)};}
    assert.notEqual(canonicalJson(actual), canonicalJson(f.oracle.expected(c)));
    if (index !== 1) assert.equal((actual as any).settled_while_pending, true, 'unsettled port escaped its await');
  }
});

test('compiling state/outbox mutations are detected even when Workflow success and result are unchanged', async t => {
  const mutations = [
    (s: string) => s.replace('value:write0', 'value:result'),
    (s: string) => s.replace('events:Object.freeze([Object.freeze({slot:"notice",target:"commerce:posted",value:event0})])', 'events:Object.freeze([])')
  ];
  for (const mutate of mutations) {
    let changes = 0;
    const f = await fixture(effectful(t), (p, s) => {if (!p.endsWith('/perform.provider.ts')) return s; const next = mutate(s); if (next !== s) changes++; return next;});
    assert.equal(changes, 1);
    const parameters: any = {amount: order(), ...eventParameters()}; delete parameters.post.occurredAt;
    const c: any = row(f.oracle, parameters); c.steps.forEach((s: any) => s.reads = [{slot: 'current-order', value: operationValueRecipe(order('1', 'read-' + s.step_id))}]);
    const observed = await f.observe(c), expected = f.oracle.expected(c);
    assert.deepEqual(observed.outcome, expected.outcome, 'result-only validation would miss this mutation');
    assert.notDeepEqual(observed.batches, expected.batches);
  }
});
