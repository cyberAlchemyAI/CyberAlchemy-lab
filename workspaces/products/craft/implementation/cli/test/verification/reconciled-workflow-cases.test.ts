import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import test from 'node:test';
import {workflowFixture, nativeWorkflow, workflowProject, stepIds} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, scalar, named, list, set, optional} from '../helpers/workflow-values.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject, selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {createWorkflowCases, WorkflowCasesUnavailable, WORKFLOW_CASES_DEFINITION_SHA256, isWorkflowCasesCapacity} from '../../src/verification/reconciled-workflow-cases.ts';
import {createWorkflowExecutionReference} from '../../src/verification/reconciled-workflow-execution-reference.ts';
import {WORKFLOW_FIXTURE_RUNNER} from '../../src/verification/reconciled-workflow-fixture.ts';

const base = path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions: any = Object.fromEntries(Object.entries({execution: 'semantic-workflow-execution-contract.json', binding: 'semantic-workflow-binding-contract.json', values: 'semantic-workflow-values-contract.json', outcomes: 'semantic-workflow-controls-contract.json'}).map(([k, p]) => [k, fs.readFileSync(path.join(base, p), 'utf8')]));
const definition = fs.readFileSync(path.join(base, 'semantic-workflow-cases-contract.json'), 'utf8');
const modes = ['committed', 'rejected', 'indeterminate', 'begin-throw', 'commit-throw', 'rollback-throw', 'receipt-empty', 'receipt-unknown', 'receipt-extra', 'receipt-null', 'receipt-getter', 'receipt-inherited', 'receipt-symbol', 'receipt-hidden', 'receipt-array', 'receipt-undefined'];
const field = (v: any, name: string) => v?.[0] === 'record' ? v[1].find((r: any) => r[0] === name)?.[1] : undefined;
function context(f: ReturnType<typeof workflowFixture>) {
  const plan = planCompiledReconciledProject(f.graph, f.selection), node = f.graph.nodes.find(n => n.kind === 'Workflow')!;
  return {plan, node, build: () => createWorkflowCases(node, f.graph, plan, definitions, definition), oracle: createWorkflowExecutionReference(node, f.graph, plan, definitions)};
}
function expand(suite: ReturnType<typeof createWorkflowCases>, row: typeof suite.cases[number]): any {
  const recipe = (r: any): any => r.tag === 'ref' ? recipe(suite.recipes[Number(r.value)]) : {...r,
    ...(r.base ? {base: recipe(r.base)} : {}), ...(r.input ? {input: recipe(r.input)} : {}), ...(r.payload ? {payload: recipe(r.payload)} : {}),
    ...(r.items ? {items: r.items.map(recipe)} : {}), ...(r.fields ? {fields: Object.fromEntries(Object.entries(r.fields).map(([k, v]) => [k, recipe(v)]))} : {})};
  const c = JSON.parse(row.values[0]!);
  return {...c, input: recipe(suite.recipes[c.input]), steps: c.steps.map((s: any) => ({...s, reads: s.reads.map((r: any) => ({...r, value: recipe(suite.recipes[r.value])}))}))};
}
async function checkAll(f: ReturnType<typeof workflowFixture>, t: Parameters<typeof workflowFixture>[0]) {
  const c = context(f), suite = c.build(), native = nativeWorkflow({...f, nativePlan: () => selectReconciledArtifacts(c.plan)});
  const file = path.join(native.root, 'finite-workflow-fixture.mjs'); fs.writeFileSync(file, WORKFLOW_FIXTURE_RUNNER);
  const {observeWorkflowFixture} = await import(pathToFileURL(file).href);
  for (const row of suite.cases) {
    const input = c.oracle.captureCase(expand(suite, row)), expected = JSON.parse((row.expected as any).value);
    assert.deepEqual(c.oracle.expected(input), expected, 'recipe/reference roundtrip ' + row.id);
    assert.deepEqual(await observeWorkflowFixture(native.run, c.oracle.binding.workflow.steps, input), expected, 'native ' + row.id + ' ' + Object.keys(suite.coverage).filter(k => suite.coverage[k] === row.id).join(','));
  }
  assert.ok(Object.isFrozen(suite.cases) && Object.isFrozen(suite.coverage));
  assert.ok(suite.cases.length <= 4095); assert.ok(Buffer.byteLength(canonicalJson(suite)) <= 8388608);
  assert.deepEqual(new Set(Object.values(suite.coverage)), new Set(suite.cases.map(c => c.id)));
  t.diagnostic(JSON.stringify({cases: suite.cases.length, dimensions: Object.keys(suite.coverage).length, attempts: suite.search.attempts}));
  return {...c, suite};
}
function edit(f: ReturnType<typeof workflowFixture>) {
  const root = path.join(f.root, 'source');
  return {read: (p: string) => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8')), write: (p: string, v: unknown) => fs.writeFileSync(path.join(root, p), JSON.stringify(v)), reload: () => loadCompiledProjectGraph(root)};
}

test('source-derived scalar suite covers all settlement occurrences and is deterministic against unchanged native code', async t => {
  const f = workflowFixture(t), {suite, build, oracle} = await checkAll(f, t);
  assert.equal(sha256(definition), WORKFLOW_CASES_DEFINITION_SHA256);
  assert.equal(canonicalJson(build()), canonicalJson(suite));
  for (const id of stepIds) for (const mode of modes) assert.ok(suite.coverage['settlement/' + id + '/' + mode]);
  const row = suite.cases.find(c => c.id === suite.coverage.baseline)!;
  assert.equal(field(oracle.expected(expand(suite, row)).outcome, 'status')[1], 'succeeded');
  assert.notEqual(suite.coverage['recovery-identity/failure_occurrence_id/"identity-two"'], suite.coverage['settlement/last/rejected']);
});

test('generated finite cases preserve constrained recovery and no-compensation source', async t => {
  for (const opts of [{dependencies: [[], ['undo-first'], ['undo-second']]}, {noCompensations: true}]) await checkAll(workflowFixture(t, opts), t);
});

test('owned records, enums, collections, sums and optionals derive complete bounded native suites', async t => {
  const sum = {kind: 'sum', variants: [{name: 'None', ontology_variant: 'TEST-SUM#None', payload: null}, {name: 'Some', ontology_variant: 'TEST-SUM#Some', payload: scalar()}]};
  for (const type of [named('customer'), named('choice'), optional(scalar()), list(scalar('String')), set(scalar('Bool')), sum]) await checkAll(workflowValuesFixture(t, {type}), t);
});

test('Event inputs and required/generated policies are exercised from source, including compensation-only Events', async t => {
  const {suite} = await checkAll(workflowValuesFixture(t, {type: scalar(), events: true}), t);
  for (const name of ['post', 'undo']) for (const field of ['order-id', 'delta', 'ratio']) assert.ok(suite.coverage['event/' + name + '/payload/' + field + '/missing-field']);
  assert.ok(!Object.keys(suite.coverage).some(k => k.startsWith('clock/')), 'generated compensation clock is not a forward effect');
});

test('read identities follow prior results; state/outbox and clock failures stay reachable at each occurrence', async t => {
  const base = workflowValuesFixture(t, {type: scalar(), events: true}), e = edit(base), selection: any = structuredClone(base.selection), feature = e.read('specs/commerce/feature.json');
  for (const op of selection.operations) {
    const id = op.selector.split(':')[1], p = 'specs/commerce/nodes/' + id + '.json', n = e.read(p);
    n.body.reads = ['current-customer']; n.body.writes = ['customer-state']; e.write(p, n);
    const edge_id = id + '-reads-customer'; feature.edges.push(edge_id);
    e.write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship: 'reads', source_node_id: id, target_node_id: 'customer', scope: 'feature'});
    op.reads = [{slot: 'current-customer', target: 'commerce:customer', parameter: 'current', key: {op: 'path', root: 'amount', properties: []}}];
    op.writes = [{slot: 'customer-state', target: 'commerce:customer', mode: 'replace', value: {op: 'path', root: 'current', properties: []}}];
    op.result.value = {op: 'literal', type: 'UInt64', value: '11'};
  }
  const posted = e.read('specs/commerce/nodes/posted.json'); posted.body.occurred_at_policy = 'generated'; e.write('specs/commerce/nodes/posted.json', posted); e.write('specs/commerce/feature.json', feature);
  const {suite, oracle} = await checkAll({...base, graph: e.reload(), selection}, t);
  for (const id of stepIds) {assert.ok(suite.coverage['read/' + id + '/current-customer/absent']); assert.ok(suite.coverage['clock/' + id + '/notice/missing']);}
  const row = suite.cases.find(c => c.id === suite.coverage.baseline)!, input = expand(suite, row), observed = oracle.expected(input);
  assert.equal(observed.read_requests.length, 4); assert.equal(observed.batches.length, 4); assert.equal(observed.clock_calls.length, 4);
  for (const r of observed.read_requests.slice(1) as any[]) assert.deepEqual(field(r.value, 'key'), ['bigint', '11']);
  assert.notDeepEqual(field((observed.read_requests[0] as any).value, 'key'), ['bigint', '11']);
  for (const id of stepIds) {
    const c = expand(suite, suite.cases.find(c => c.id === suite.coverage['clock/' + id + '/notice/missing'])!);
    assert.ok(c.steps.every((s: any) => s.clocks[0].mode === 'missing'));
  }
});

test('selected Rule literals seed success without changing Rules; no witness rejects the entire suite', async t => {
  for (const allowed of [true, false]) {
    const f = workflowFixture(t), e = edit(f), p = 'specs/commerce/nodes/allowed.json', rule = e.read(p);
    rule.body.typed_contract.expression = {op: 'eq', left: allowed ? {op: 'path', root: 'value', properties: []} : {op: 'literal', type: 'UInt64', value: '0'}, right: {op: 'literal', type: 'UInt64', value: '73129'}};
    e.write(p, rule); const bytes = fs.readFileSync(path.join(f.root, 'source', p), 'utf8');
    if (allowed) {
      const {suite, oracle} = await checkAll({...f, graph: e.reload()}, t);
      const row = suite.cases.find(c => c.id === suite.coverage.baseline)!;
      assert.deepEqual(field(oracle.expected(expand(suite, row)).outcome, 'value'), ['bigint', '73129']);
    } else assert.throws(() => context({...f, graph: e.reload()}).build(), e => isWorkflowCasesCapacity(e) && /no complete success witness.*not an unsatisfiability proof/.test(e.message));
    assert.equal(fs.readFileSync(path.join(f.root, 'source', p), 'utf8'), bytes);
  }
});

test('definition drift and whole-suite byte capacity cannot return a partial prefix', t => {
  const f = workflowFixture(t), c = context(f);
  assert.throws(() => createWorkflowCases(c.node, f.graph, c.plan, definitions, definition + '\n'), /definition drift/);
  assert.equal(isWorkflowCasesCapacity(new TypeError('source defect')), false);
  const e = edit(f), p = 'specs/commerce/nodes/flow.json', flow = e.read(p), selection: any = structuredClone(f.selection);
  const ids = [...stepIds, ...Array.from({length: 124}, (_, i) => 'step-' + i)];
  flow.body.typed_contract.steps = ids.map(step_id => ({step_id, operation_ref: 'commerce:perform'})); e.write(p, flow);
  selection.workflows[0].steps = ids.map((step_id, i) => ({step_id, arguments: [{parameter: 'amount', value: i ? {op: 'step-result', step_id: ids[i - 1], properties: []} : {op: 'input', name: 'amount', properties: []}}], events: []}));
  assert.throws(() => context({...f, graph: e.reload(), selection}).build(), e => e instanceof WorkflowCasesUnavailable && /serialized suite exceeds 8 MiB/.test(e.message));
});

test('generated suites distinguish strict-compiling value, await and outbox mutants', async t => {
  const variants = [
    {name: 'value', event: false, file: '/flow.provider.ts', from: 'material.result(input,results)', to: '0n'},
    {name: 'await', event: false, file: '/flow.provider.ts', from: 'raw=await call0(args,dep0)', to: 'raw=call0(args,dep0)'},
    {name: 'outbox', event: true, file: '/perform.provider.ts', from: 'events:Object.freeze([Object.freeze({slot:"notice",target:"commerce:posted",value:event0})])', to: 'events:Object.freeze([])'}
  ];
  for (const v of variants) {
    const f = v.event ? workflowValuesFixture(t, {type: scalar(), events: true}) : workflowFixture(t), c = context(f), suite = c.build(); let changes = 0;
    const native = nativeWorkflow({...f, nativePlan: () => selectReconciledArtifacts(c.plan)}, (p, s) => {const next = p.endsWith(v.file) ? s.replace(v.from, v.to) : s; if (next !== s) changes++; return next;});
    assert.equal(changes, 1);
    const file = path.join(native.root, 'finite-mutant-fixture.mjs'); fs.writeFileSync(file, WORKFLOW_FIXTURE_RUNNER);
    const {observeWorkflowFixture} = await import(pathToFileURL(file).href); let detected = false;
    for (const row of suite.cases) {
      const expected = JSON.parse((row.expected as any).value); let actual: any;
      try {actual = await observeWorkflowFixture(native.run, c.oracle.binding.workflow.steps, c.oracle.captureCase(expand(suite, row)));} catch (e) {actual = {error: String(e)};}
      if (canonicalJson(actual) === canonicalJson(expected)) continue;
      detected = true;
      if (v.name === 'outbox') {assert.deepEqual(actual.outcome, expected.outcome); assert.notDeepEqual(actual.batches, expected.batches);}
      if (v.name === 'await') assert.equal(actual.settled_while_pending, true);
      if (v.name === 'value') assert.notEqual(row.id, suite.coverage.baseline, 'automatic positive samples, not the zero baseline, catch this mutant');
      break;
    }
    assert.ok(detected, v.name + ' strict-compiling mutant distinguished');
  }
});

test('distinct forward Operations and prior-result paths generate complete native suites', async t => {
  const f = workflowFixture(t), e = edit(f), feature = e.read('specs/commerce/feature.json'), op = e.read('specs/commerce/nodes/perform.json');
  op.node_id = 'other'; op.body.failure_continuation = 'return-other-error'; e.write('specs/commerce/nodes/other.json', op); feature.nodes.push('other');
  for (const [from, relationship] of [['allowed', 'enforces'], ['flow', 'orchestrates']]) {
    const edge_id = from + '-' + relationship + '-other'; feature.edges.push(edge_id);
    e.write('specs/commerce/edges/' + edge_id + '.json', {schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id, relationship, source_node_id: from, target_node_id: 'other', scope: 'feature'});
  }
  const flow = e.read('specs/commerce/nodes/flow.json'); flow.body.typed_contract.steps[1].operation_ref = 'commerce:other'; flow.body.typed_contract.steps[3].operation_ref = 'commerce:other';
  e.write('specs/commerce/nodes/flow.json', flow); e.write('specs/commerce/feature.json', feature);
  const selection: any = structuredClone(f.selection), action = structuredClone(selection.operations[0]);
  action.selector = 'commerce:other'; action.result.value = {op: 'literal', type: 'UInt64', value: '11'}; selection.operations.push(action);
  await checkAll({...f, graph: e.reload(), selection}, t);
});

test('authored literal, variant, projection and list-to-set expressions retain source-derived inputs', async t => {
  for (const options of [{type: scalar(), expression: 'literal'}, {type: named('choice'), expression: 'variant'}, {type: set(scalar('Bool')), expression: 'to_set'}, {type: list(scalar()), expression: 'projection'}] as const) {
    const f = workflowValuesFixture(t, options);
    if (options.expression !== 'projection') {await checkAll(f, t); continue;}
    // The deeply nested Order-list fixture exceeds the existing structural
    // expansion bound. Keep that rejection, and prove projection with a bounded
    // two-field Entity instead; do not silently truncate the original suite.
    assert.throws(() => context(f).build(), e => isWorkflowCasesCapacity(e) && /fact expansion exceeded/.test(e.message));
    const selection: any = structuredClone(f.selection);
    selection.workflows[0].inputs.find((p: any) => p.name === 'raw').type = list(named('customer'));
    selection.workflows[0].steps[0].arguments[0].value.properties = ['TEST-CUSTOMER#id'];
    await checkAll({...f, selection}, t);
  }
});
