import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {createWorkflowValueReference, WORKFLOW_VALUES_DEFINITION_SHA256} from '../../src/verification/reconciled-workflow-value-reference.ts';
import {createWorkflowOutcomeReference} from '../../src/verification/reconciled-workflow-outcome-reference.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {workflowDefinition, stepIds, settlementProvider} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, nativeWorkflowValues, workflowValuesDefinition, workflowValuesDefinitionPath, scalar, named, list, set, optional, money, order, eventParameters} from '../helpers/workflow-values.ts';

const reference = (f: ReturnType<typeof workflowValuesFixture>) => createWorkflowValueReference(f.graph, f.workflow, workflowValuesDefinition);
function frozen(v: any): void {if (v && typeof v === 'object') {assert.ok(Object.isFrozen(v)); Object.values(v).forEach(frozen);}}
function comparePath(f: ReturnType<typeof workflowValuesFixture>, material: any, raw: any) {
  const ref = reference(f), expected = ref.capture(raw), actual = material.capture(raw), er: any[] = [], ar: any[] = [];
  assert.deepEqual(actual, expected); frozen(actual); frozen(expected);
  for (const id of stepIds) {
    const args = ref.forward(expected, id, er);
    const got: typeof args = material.steps[id].arguments(actual, ar);
    assert.deepEqual(got, args); frozen(got); frozen(args);
    er.push(ref.captureResult(expected, id, args.amount)); ar.push(material.captureResult(actual, id, got.amount));
    assert.deepEqual(ar.at(-1), er.at(-1));
    for (const c of f.workflow.compensations.filter(c => stepIds.indexOf(c.for_step) < er.length)) {
      assert.deepEqual(material.compensations[c.compensation_id].arguments(actual, ar), ref.compensation(expected, c.compensation_id, er));
    }
  }
  assert.deepEqual(material.result(actual, ar), ref.result(expected, er)); frozen(material.result(actual, ar));
  return {ref, expected, actual, er, ar};
}

test('typed reference pins its source and definition before reading any caller value', t => {
  const f = workflowValuesFixture(t), ref = reference(f);
  assert.equal(sha256(workflowValuesDefinition), WORKFLOW_VALUES_DEFINITION_SHA256);
  for (const [file, digest] of Object.entries(JSON.parse(workflowValuesDefinition).extends)) assert.equal(sha256(fs.readFileSync(path.join(path.dirname(workflowValuesDefinitionPath), file), 'utf8')), digest);
  assert.throws(() => createWorkflowValueReference({...f.graph}, f.workflow, workflowValuesDefinition));
  assert.throws(() => createWorkflowValueReference(f.graph, {...f.workflow}, workflowValuesDefinition));
  assert.throws(() => createWorkflowValueReference(f.graph, f.workflow, workflowValuesDefinition + '\n'), /definition drift/);
  const other = workflowValuesFixture(t, {events: true});
  assert.throws(() => createWorkflowValueReference(other.graph, f.workflow, workflowValuesDefinition), /certificate mismatch/);
  assert.equal(ref.workflow_sha256, f.workflow.workflow_sha256);
});

test('native materialization matches every primitive and nested named/optional/list/set/sum form', t => {
  const cases: [any, any[]][] = [
    [scalar(), ['0', '18446744073709551615', 9007199254740991, 9007199254740993n]],
    [scalar('String'), ['', 'β😀', 'é', 'e\u0301']], [scalar('Bool'), [true, false]],
    [optional(list(scalar())), [null, [], ['3', '1', '3']]],
    [named('money'), [money(), {quantity: '9', note: null}, {quantity: '1', note: 'hello'}]],
    [named('order'), [order(), order('5', 'other')]],
    [named('choice'), [{variant: 'None'}, {variant: 'Some', payload: money()}]],
    [list(named('order')), [[order('2', 'a'), order('1'), order('2', 'b')]]],
    [set(named('order')), [[order('2'), order('1')]]],
    [set(named('money')), [[money('9'), money('3')]]],
    [{kind: 'sum', variants: [{name: 'Empty', ontology_variant: 'TEST-INLINE#Empty', payload: null}, {name: 'Orders', ontology_variant: 'TEST-INLINE#Orders', payload: list(named('order'))}]}, [{variant: 'Empty'}, {variant: 'Orders', payload: [order()]}]]
  ];
  for (const [type, samples] of cases) {
    const f = workflowValuesFixture(t, {type}), n = nativeWorkflowValues(f);
    for (const amount of samples) comparePath(f, n.material, {amount});
  }
});

test('explicit set, projection, literal and named variant expressions preserve source semantics', t => {
  for (const row of [
    {type: set(named('order')), expression: 'to_set' as const, raw: {amount: [], raw: [order('2', 'first'), order('1'), order('2', 'later')]}, check: (v: any) => {assert.equal(v.length, 2); assert.equal(v.find((x: any) => x.id === 2n).labels[0], 'first');}},
    {type: list(scalar()), expression: 'projection' as const, raw: {amount: [], raw: [order('2'), order('1'), order('2')]}, check: (v: any) => assert.deepEqual(v, [2n, 1n, 2n])},
    {type: scalar(), expression: 'literal' as const, raw: {amount: '1'}, check: (v: any) => assert.equal(v, 18446744073709551615n)},
    {type: named('choice'), expression: 'variant' as const, raw: {amount: {variant: 'Some', payload: money()}}, check: (v: any) => assert.deepEqual(v, {variant: 'None'})}
  ]) {
    const f = workflowValuesFixture(t, row), n = nativeWorkflowValues(f), c = comparePath(f, n.material, row.raw);
    row.check(c.ref.result(c.expected, c.er));
  }
});

test('Event input preserves signed integers, optional absence and generated-time omission without constructing an Event', t => {
  const f = workflowValuesFixture(t, {events: true}), n = nativeWorkflowValues(f);
  const c = comparePath(f, n.material, {amount: order(), ...eventParameters()});
  assert.equal(c.expected.post.payload.delta, -9223372036854775808n);
  assert.equal(Object.hasOwn(c.expected.undo, 'occurredAt'), false);
  assert.equal(Object.hasOwn(c.expected.undo.payload, 'delta'), false);
  assert.equal(Object.hasOwn(c.expected.post, 'type'), false);
  for (const changed of [
    (v: any) => v.post.payload.delta = '9223372036854775808',
    (v: any) => v.post.payload.delta = '-0',
    (v: any) => v.post.payload.ratio = Infinity,
    (v: any) => v.undo.occurredAt = 'invented',
    (v: any) => delete v.post.occurredAt,
    (v: any) => v.post.occurrence['event-id'] = '',
    (v: any) => v.post.payload['order-id'] = '',
    (v: any) => v.undo.payload.delta = undefined
  ]) {
    const raw = {amount: order(), ...eventParameters()}; changed(raw);
    assert.throws(() => c.ref.capture(raw)); assert.throws(() => n.material.capture(raw));
  }
});

test('capture rejects hostile descriptors and value drift without getters, coercion or mutable aliases', t => {
  const f = workflowValuesFixture(t), n = nativeWorkflowValues(f), ref = reference(f);
  let effects = 0; const trap = () => {effects++; throw Error('side effect');};
  const raw = {amount: order()}, a = ref.capture(raw), b = n.material.capture(raw);
  raw.amount.labels[0] = 'changed'; raw.amount.money.quantity = '0';
  assert.equal(a.amount.labels[0], 'one'); assert.deepEqual(a, b); assert.equal(Object.isFrozen(raw.amount), false);
  const bad = [null, [], Object.create({amount: order()}), {...raw, extra: 1}, {amount: undefined},
    {amount: {...order(), id: {toString: trap}}}, {amount: {...order(), id: '18446744073709551616'}},
    {amount: {...order(), labels: new Array(1)}}, {amount: {...order(), labels: new Array(1025).fill('x')}},
    Object.defineProperty({amount: order()}, 'amount', {get: trap}),
    Object.defineProperty({amount: order()}, 'amount', {enumerable: false}),
    {amount: Object.defineProperty(order(), 'money', {get: trap})}, {amount: {...order(), [Symbol('hidden')]: 1}}];
  const cycle: any = order(); cycle.money = cycle; bad.push({amount: cycle});
  for (const v of bad) {assert.throws(() => ref.capture(v)); assert.throws(() => n.material.capture(v));}
  const inert = Object.assign(Object.create(null), {amount: order()}); assert.deepEqual(ref.capture(inert), n.material.capture(inert));
  assert.equal(effects, 0);
});

test('result custody rejects forged, cross-capture, future, reordered and accessor slots at every prefix', t => {
  const f = workflowValuesFixture(t), n = nativeWorkflowValues(f), ref = reference(f);
  const input = ref.capture({amount: order()}), nativeInput = n.material.capture({amount: order()});
  const other = ref.capture({amount: order()}), nativeOther = n.material.capture({amount: order()});
  const rows = stepIds.map(id => ref.captureResult(input, id, order())), nativeRows = stepIds.map(id => n.material.captureResult(nativeInput, id, order()));
  for (let i = 0; i < 4; i++) {
    assert.deepEqual(ref.forward(input, stepIds[i]!, rows.slice(0, i)), n.material.steps[stepIds[i]!].arguments(nativeInput, nativeRows.slice(0, i)));
    assert.throws(() => ref.forward(input, stepIds[i]!, rows.slice(0, i + 1)));
    assert.throws(() => n.material.steps[stepIds[i]!].arguments(nativeInput, nativeRows.slice(0, i + 1)));
  }
  const refBad = [[{...rows[0]}], [rows[1]], [ref.captureResult(other, 'first', order())], new Array(1)];
  const nativeBad = [[{...nativeRows[0]}], [nativeRows[1]], [n.material.captureResult(nativeOther, 'first', order())], new Array(1)];
  let effects = 0; const trap = () => {effects++; throw Error();};
  refBad.push(Object.defineProperty([rows[0]], '0', {get: trap})); nativeBad.push(Object.defineProperty([nativeRows[0]], '0', {get: trap}));
  refBad.push([{get step_id() {return trap();}}]); nativeBad.push([{get step_id() {return trap();}}]);
  for (let i = 0; i < refBad.length; i++) {assert.throws(() => ref.forward(input, 'second', refBad[i] as any)); assert.throws(() => n.material.steps.second.arguments(nativeInput, nativeBad[i]));}
  assert.throws(() => ref.result(input, rows.slice(0, 3))); assert.throws(() => n.material.result(nativeInput, nativeRows.slice(0, 3)));
  assert.throws(() => ref.compensation(input, 'undo-third', rows.slice(0, 2))); assert.throws(() => n.material.compensations['undo-third'].arguments(nativeInput, nativeRows.slice(0, 2)));
  assert.throws(() => ref.captureResult({...input}, 'first', order())); assert.throws(() => n.material.captureResult({...nativeInput}, 'first', order()));
  assert.equal(effects, 0); assert.equal(Object.isFrozen(rows), false); rows.forEach(frozen);
});

test('structural materialization does not silently enforce business rules owned by Operations', async t => {
  const f = workflowValuesFixture(t, {type: named('money')}), n = nativeWorkflowValues(f), ref = reference(f), raw = {amount: money('0')};
  assert.deepEqual(ref.capture(raw), n.material.capture(raw));
  const store = settlementProvider();
  const actual = await n.run(raw, {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, {'commerce:perform': store.dependency});
  assert.equal(actual.status, 'forward-stopped'); assert.equal(actual.evaluation.failure.stage, 'result');
  assert.equal(actual.evaluation.failure.commit_status, 'not-committed'); assert.deepEqual(store.trace, ['begin:0', 'rollback:0']);
  assert.equal(store.commits.length, 0);
});

test('set identity and sum shape are rejected without collapsing ordered list occurrences', t => {
  for (const row of [
    {type: set(named('order')), bad: [order('1', 'first'), order('1', 'different-state')]},
    {type: set(named('money')), bad: [money('3'), {quantity: 3n, note: null}]},
    {type: named('choice'), bad: {variant: 'None', payload: null}},
    {type: named('choice'), bad: {variant: 'Some'}},
    {type: optional(scalar()), bad: undefined}
  ]) {
    const f = workflowValuesFixture(t, row), n = nativeWorkflowValues(f), ref = reference(f);
    assert.throws(() => ref.capture({amount: row.bad})); assert.throws(() => n.material.capture({amount: row.bad}));
  }
});

test('exact numeric carriers reject trailing newline text at domain and Event boundaries', t => {
  const f = workflowValuesFixture(t, {type: scalar(), events: true}), n = nativeWorkflowValues(f), ref = reference(f);
  const valid = {amount: '1', ...eventParameters()};
  assert.deepEqual(n.material.capture(valid), ref.capture(valid), 'valid numeric and Event witnesses reach capture');
  for (const raw of [{...structuredClone(valid), amount: '1\n'}, {...structuredClone(valid), post: {...valid.post, payload: {...valid.post.payload, delta: '-1\n'}}}]) {
    assert.throws(() => n.material.capture(raw), 'native exact syntax');
    assert.throws(() => ref.capture(raw), 'reference exact syntax');
  }
});

test('actual typed Workflow failure prefixes retain independently materialized recovery bindings', async t => {
  const f = workflowValuesFixture(t, {events: true}), n = nativeWorkflowValues(f), ref = reference(f), raw = {amount: order(), ...eventParameters()};
  const input = ref.capture(raw), results: any[] = [];
  for (const step of stepIds) results.push(ref.captureResult(input, step, ref.forward(input, step, results).amount));
  const outcomes = createWorkflowOutcomeReference(f.policy, workflowDefinition);
  for (let failure = 0; failure < 4; failure++) for (const mode of ['reject', 'indeterminate', 'throw-before', 'throw-after']) {
    const store = settlementProvider(failure, mode);
    const actual = await n.run(raw, {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, {'commerce:perform': store.dependency});
    const outcome = {status: mode === 'reject' ? 'rejected' : 'indeterminate', stage: 'commit',
      code: mode === 'reject' ? 'COMMIT_REJECTED' : mode === 'indeterminate' ? 'COMMIT_INDETERMINATE' : 'COMMIT_UNCERTAIN', continuation: 'return-perform-error', cleanupFailed: false};
    const expected = outcomes.evaluate({workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one', local_error: null,
      events: [...stepIds.slice(0, failure).map(step_id => ({step_id, kind: 'returned', outcome: {status: 'committed', value: null}})), {step_id: stepIds[failure], kind: 'returned', outcome}]});
    assert.deepEqual(actual.evaluation, expected); assert.equal(store.count(), failure + 1);
    const intent = expected.recovery!.recovery_intent;
    if (!intent) {assert.equal(actual.recovery_bindings, null); continue;}
    assert.equal(actual.bindings_status, 'ready'); assert.equal(actual.recovery_bindings.intent_id, intent.intent_id);
    assert.deepEqual(actual.recovery_bindings.bindings.map((b: any) => b.compensation_id), intent.plan.map(p => p.compensation_id));
    for (const binding of actual.recovery_bindings.bindings) {
      assert.deepEqual(binding.arguments, ref.compensation(input, binding.compensation_id, results.slice(0, failure)));
      assert.equal(binding.invocation_identity, intent.plan.find(p => p.compensation_id === binding.compensation_id)!.invocation_identity);
      frozen(binding.arguments);
    }
  }
});

const until = async (predicate: () => boolean) => {for (let i = 0; i < 512 && !predicate(); i++) await Promise.resolve(); assert.ok(predicate(), 'bounded deferred fixture did not advance');};
test('real generated calls retain captured typed values and dependencies and await each begin and commit', async t => {
  const f = workflowValuesFixture(t, {events: true}), n = nativeWorkflowValues(f), ref = reference(f);
  const raw = {amount: order(), ...eventParameters()}, input = ref.capture(raw), expectedRows: any[] = [], begins: ((tx: any) => void)[] = [], commits: ((receipt: any) => void)[] = [], batches: any[] = [];
  const deps: any = {'commerce:perform': {store: {begin: () => new Promise(resolve => begins.push(resolve))}}};
  let settled = false;
  const pending = n.run(raw, {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, deps).then((v: any) => {settled = true; return v;});
  raw.amount.money.quantity = '0'; raw.amount.labels[0] = 'changed'; raw.post.payload.delta = '7'; deps['commerce:perform'] = null;
  for (let i = 0; i < 4; i++) {
    await until(() => begins.length === i + 1); assert.equal(settled, false); assert.equal(commits.length, i);
    const args = ref.forward(input, stepIds[i]!, expectedRows);
    begins[i]!({read: () => {throw Error('undeclared read');}, rollback: () => {throw Error('unexpected rollback');}, commit: (batch: any) => {batches.push(batch); return new Promise(resolve => commits.push(resolve));}});
    await until(() => commits.length === i + 1); assert.equal(begins.length, i + 1); assert.equal(settled, false);
    assert.equal(batches[i].events[0].value.payload.delta, args.notice_input.payload.delta);
    commits[i]!({status: 'committed'}); expectedRows.push(ref.captureResult(input, stepIds[i]!, args.amount));
  }
  const actual = await pending;
  assert.equal(actual.status, 'succeeded'); assert.deepEqual(actual.value, ref.result(input, expectedRows)); frozen(actual.value);
  const metadata = createWorkflowOutcomeReference(f.policy, workflowDefinition).evaluate({workflow_execution_id: 'execution-one', failure_occurrence_id: null, local_error: null,
    events: stepIds.map(step_id => ({step_id, kind: 'returned', outcome: {status: 'committed', value: null}}))});
  assert.deepEqual(actual.evaluation, metadata); assert.equal(begins.length, 4); assert.equal(batches.length, 4);
});

test('compiling materialization mutants disagree on values, prefixes, custody and freezing', t => {
  const f = workflowValuesFixture(t, {type: scalar()}), ref = reference(f);
  const mutations = [
    ['input value', 'ruleUInt64.normalize(d["amount"]!.value)', '1n', 'capture'],
    ['committed result value', 'ruleUInt64.normalize(captureData(raw))', '1n', 'result-slot'],
    ['wrong argument source', '(r["first"] as bigint)', 'input["amount"]', 'forward'],
    ['forged result accepted', 'resultInputs.get(row)!==input||', '', 'forged'],
    ['reordered result accepted', 'row.step_id!==ids[i]', 'false', 'reordered'],
    ['future result accepted', 'length>max||', '', 'future'],
    ['unfrozen arguments', 'return Object.freeze({["amount"]:input["amount"]});', 'return {["amount"]:input["amount"]};', 'freeze'],
    ['wrong final result', '(r["last"] as bigint)', '(r["third"] as bigint)', 'final']
  ];
  const observe = (run: () => any) => {try {const value = run(); return {value, frozen: value && typeof value === 'object' ? Object.isFrozen(value) : null};} catch {return {error: 'rejected'};}};
  for (const [name, before, after, action] of mutations) {
    let changed = 0;
    const n = nativeWorkflowValues(f, (file, code) => {
      if (!file.endsWith('/workflows/flow.material.ts')) return code;
      assert.ok(code.includes(before!), name); changed++; return code.replaceAll(before!, after!);
    });
    assert.equal(changed, 1);
    const expected = ref.capture({amount: '3'}), actual = n.material.capture({amount: '3'});
    const er = stepIds.map((id, i) => ref.captureResult(expected, id, String(i + 5))), ar = stepIds.map((id, i) => n.material.captureResult(actual, id, String(i + 5)));
    const a = () => action === 'capture' ? actual : action === 'result-slot' ? ar[0] : action === 'final' ? n.material.result(actual, ar) :
      action === 'freeze' ? n.material.steps.first.arguments(actual, []) : n.material.steps.second.arguments(actual,
        action === 'forged' ? [{...ar[0]}] : action === 'reordered' ? [ar[1]] : action === 'future' ? ar.slice(0, 2) : [ar[0]]);
    const e = () => action === 'capture' ? expected : action === 'result-slot' ? er[0] : action === 'final' ? ref.result(expected, er) :
      action === 'freeze' ? ref.forward(expected, 'first', []) : ref.forward(expected, 'second',
        action === 'forged' ? [{...er[0]}] as any : action === 'reordered' ? [er[1]!] : action === 'future' ? er.slice(0, 2) : [er[0]!]);
    assert.notDeepEqual(observe(a), observe(e), name);
  }
});
