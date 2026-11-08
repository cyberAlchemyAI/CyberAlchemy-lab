import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {createWorkflowOutcomeReference, inspectWorkflowSettlementReference, WORKFLOW_CONTROLS_DEFINITION_SHA256} from '../../src/verification/reconciled-workflow-outcome-reference.ts';
import {inspectOperationSettlement, observeWorkflowStep, evaluateWorkflowOutcomeJournal, WORKFLOW_OUTCOME_JOURNAL_VERSION} from '../../src/typed-operation/workflow-outcomes.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {workflowFixture, nativeWorkflow, settlementProvider, workflowDefinition, workflowDefinitionPath, workflowProject, stepIds} from '../helpers/workflow-verification.ts';

const continuation = 'return-perform-error';
const committed = (value: unknown = 3n) => ({status: 'committed', value});
const rejected = () => ({status: 'rejected', stage: 'commit', code: 'COMMIT_REJECTED', continuation, cleanupFailed: false});
const request = (count: number, terminal?: unknown, kind = 'returned'): any => ({workflow_execution_id: 'execution-one',
  failure_occurrence_id: terminal !== undefined || kind !== 'returned' ? 'failure-one' : null, local_error: null,
  events: [...stepIds.slice(0, count).map(step_id => ({step_id, kind: 'returned', outcome: committed()})),
    ...(terminal !== undefined || kind !== 'returned' ? [{step_id: stepIds[count], kind, ...(kind === 'returned' ? {outcome: terminal} : {})}] : [])]});
function production(f: ReturnType<typeof workflowFixture>, r: any) {
  const observations = r.events.map(({step_id, ...event}: any) => observeWorkflowStep(f.workflow, step_id, event, getReconciledSource('workflow_outcome')));
  return evaluateWorkflowOutcomeJournal(f.policy, {schema_version: WORKFLOW_OUTCOME_JOURNAL_VERSION, workflow_execution_id: r.workflow_execution_id,
    failure_occurrence_id: r.failure_occurrence_id, observations, local_error: r.local_error});
}

test('reference pins its definition and existing contracts without importing production behavior', t => {
  assert.equal(sha256(workflowDefinition), WORKFLOW_CONTROLS_DEFINITION_SHA256);
  for (const [file, digest] of Object.entries(JSON.parse(workflowDefinition).source_contracts)) assert.equal(sha256(fs.readFileSync(path.join(path.dirname(workflowDefinitionPath), file), 'utf8')), digest, file);
  const code = fs.readFileSync(path.join(workflowProject, 'impl/cli/src/verification/reconciled-workflow-outcome-reference.ts'), 'utf8');
  const imports = [...code.matchAll(/^import .* from '([^']+)';$/gm)].map(m => m[1]);
  assert.deepEqual(imports, ['../input/source-manifest.js', '../typed-operation/workflow-recovery.js']);
  assert.doesNotMatch(code, /\b(?:inspectOperationSettlement|observeWorkflowStep|evaluateWorkflowOutcomeJournal|planSelectedWorkflowRecovery|planConfiguredWorkflow|eval|require)\s*\(/);
  const f = workflowFixture(t);
  assert.throws(() => createWorkflowOutcomeReference(f.policy, workflowDefinition + '\n'), /definition drift/);
  assert.throws(() => createWorkflowOutcomeReference({...f.policy}, workflowDefinition), /unvalidated policy/);
  let reads = 0;
  assert.throws(() => createWorkflowOutcomeReference({get workflow() {reads++; throw Error();}} as any, workflowDefinition), /unvalidated policy/);
  assert.equal(reads, 0);
  assert.equal(f.graph.nodes.some(n => n.kind === 'Entity' || n.kind === 'Value Object'), false);
});

test('settlement table preserves every stage, uncertainty and cleanup combination independently', () => {
  const stages = ['input', 'begin', 'read', 'guard', 'write-validation', 'event', 'result', 'commit', 'other'];
  const codes = ['OPERATION_INPUT', 'BEGIN_FAILED', 'OPERATION_FAILED', 'READ_NOT_FOUND', 'READ_IDENTITY_MISMATCH', 'RULE_REJECTED:commerce:allowed', 'COMMIT_REJECTED', 'COMMIT_INDETERMINATE', 'INVALID_COMMIT_RECEIPT', 'COMMIT_UNCERTAIN', 'OTHER'];
  let accepted = 0;
  for (const stage of stages) for (const code of codes) for (const status of ['failed', 'rejected', 'indeterminate']) for (const cleanupFailed of [false, true]) {
    const raw = {stage, code, status, cleanupFailed, continuation};
    const result = inspectWorkflowSettlementReference(raw, continuation);
    assert.deepEqual(result, inspectOperationSettlement(raw, continuation));
    if (result.origin === 'returned') accepted++;
  }
  assert.equal(accepted, 22);
  assert.equal(inspectWorkflowSettlementReference(rejected(), continuation).commit_status, 'not-committed');
  assert.equal(inspectWorkflowSettlementReference({...rejected(), cleanupFailed: true}, continuation).commit_status, 'indeterminate');
  assert.throws(() => inspectWorkflowSettlementReference(committed(), ''), /invalid continuation/);
});

test('hostile metadata invokes no getters or coercion and committed payload stays opaque and unfrozen', t => {
  let effects = 0;
  const trip = () => {effects++; throw Error('touched');};
  const payload: any = {get nested() {return trip();}}; payload.cycle = payload;
  const proxy = new Proxy({}, {ownKeys: trip, get: trip, getPrototypeOf: trip, preventExtensions: trip});
  for (const value of [payload, proxy, 18446744073709551615n, undefined, Symbol('opaque')]) {
    const result = inspectWorkflowSettlementReference(committed(value), continuation);
    assert.equal(result.commit_status, 'committed'); assert.ok(Object.isFrozen(result));
  }
  const bad = [null, [], new Date(), Object.create(rejected()), {...rejected(), extra: true}, {...rejected(), continuation: 'wrong'},
    {...rejected(), status: {toString: trip}}, {...rejected(), stage: {toString: trip}}, {...rejected(), code: {toString: trip}},
    {...rejected(), stage: 'x'.repeat(2049)}, {...rejected(), [Symbol('extra')]: 1},
    Object.defineProperty(rejected(), 'status', {get: trip}), Object.defineProperty(rejected(), 'code', {enumerable: false}),
    Object.defineProperty(committed(), 'value', {get: trip})];
  for (const value of bad) {
    assert.equal(inspectWorkflowSettlementReference(value, continuation).origin, 'invalid-return');
    assert.deepEqual(inspectWorkflowSettlementReference(value, continuation), inspectOperationSettlement(value, continuation));
  }
  const f = workflowFixture(t), r = request(4); r.events.forEach((e: any) => e.outcome = committed(payload));
  const evaluation = createWorkflowOutcomeReference(f.policy, workflowDefinition).evaluate(r);
  assert.equal(evaluation.status, 'forward-complete'); assert.ok(Object.isFrozen(evaluation.observations));
  assert.equal(Object.isFrozen(payload), false); assert.equal(effects, 0);
  payload.changed = true;
});

test('every prefix, terminal kind and committed local error retains exact occurrences and identities', t => {
  const f = workflowFixture(t), ref = createWorkflowOutcomeReference(f.policy, workflowDefinition);
  for (let n = 0; n <= 4; n++) {
    const r = request(n), evaluation = ref.evaluate(r);
    assert.deepEqual(evaluation, production(f, r));
    assert.deepEqual(evaluation.completed_step_ids, stepIds.slice(0, n));
    assert.equal(evaluation.status, n === 4 ? 'forward-complete' : 'awaiting-next-step');
    assert.equal(new Set(evaluation.observations.map(o => o.operation_ref)).size, n ? 1 : 0);
    assert.equal(new Set(evaluation.observations.map(o => o.observation_sha256)).size, n);
    if (n) {
      const local = {...r, failure_occurrence_id: 'failure-one', local_error: 'committed-result-invalid'};
      assert.deepEqual(ref.evaluate(local), production(f, local));
      assert.equal(ref.evaluate(local).recovery, null);
    }
    if (n < 4) for (const terminal of [request(n, rejected()), request(n, null), request(n, undefined, 'threw'), request(n, undefined, 'not-started')]) {
      const e = ref.evaluate(terminal); assert.deepEqual(e, production(f, terminal));
      assert.equal(e.status, 'forward-stopped'); assert.deepEqual(e.completed_step_ids, stepIds.slice(0, n));
    }
  }
  const local = {...request(4), failure_occurrence_id: 'failure-one', local_error: 'result-materialization-failed'};
  assert.deepEqual(ref.evaluate(local), production(f, local));
  const r = request(3, rejected()), a = ref.evaluate(r).recovery!.recovery_intent!;
  for (const key of ['workflow_execution_id', 'failure_occurrence_id']) {
    const b = ref.evaluate({...r, [key]: 'another-occurrence'}).recovery!.recovery_intent!;
    assert.notEqual(a.intent_id, b.intent_id); assert.notEqual(a.plan[0]!.invocation_identity, b.plan[0]!.invocation_identity);
    assert.equal(a.plan_digest, b.plan_digest);
  }
});

test('request custody rejects malformed arrays, wrappers, identities, reordering and successors after failure', t => {
  const ref = createWorkflowOutcomeReference(workflowFixture(t).policy, workflowDefinition);
  const malformed = [null, {}, {...request(0), extra: 1}, {...request(0), workflow_execution_id: 'execution\n'},
    {...request(0), workflow_execution_id: 'a'.repeat(257)}, {...request(0), failure_occurrence_id: 'orphan'},
    {...request(0), local_error: 'committed-result-invalid', failure_occurrence_id: 'failure-one'},
    {...request(1), local_error: 'result-materialization-failed', failure_occurrence_id: 'failure-one'},
    {...request(1, rejected()), local_error: 'committed-result-invalid'}, {...request(1, rejected()), failure_occurrence_id: null},
    {...request(1), events: new Array(1)}, {...request(0), events: new Array(129)},
    {...request(2), events: request(2).events.reverse()}, {...request(2), events: [request(1).events[0], request(1).events[0]]},
    {...request(1, rejected()), events: [...request(1, rejected()).events, request(3).events[2]]},
    {...request(1), events: [{step_id: 'first', kind: 'other'}]}, {...request(1), events: [{step_id: 'first', kind: 'threw', outcome: 1}]}];
  let effects = 0; const getter = () => {effects++; throw Error('getter');};
  malformed.push(Object.defineProperty(request(0), 'events', {get: getter}));
  malformed.push({...request(1), events: Object.defineProperty([1], '0', {get: getter})});
  malformed.push({...request(1), events: [Object.defineProperty({step_id: 'first'}, 'kind', {get: getter, enumerable: true})]});
  for (const r of malformed) assert.throws(() => ref.evaluate(r), /WORKFLOW_REFERENCE:/);
  assert.equal(effects, 0);
});

test('all three-node DAGs and declaration permutations preserve the needed induced graph', t => {
  const names = ['undo-first', 'undo-second', 'undo-third'];
  const edges = names.flatMap((_, a) => names.flatMap((_, b) => a === b ? [] : [[a, b]]));
  const permutations = [[0,1,2], [0,2,1], [1,0,2], [1,2,0], [2,0,1], [2,1,0]];
  let dags = 0, cyclic = 0;
  for (let mask = 0; mask < 64; mask++) {
    const deps = names.map(() => [] as string[]);
    edges.forEach(([a,b], bit) => {if (mask & (1 << bit)) deps[a!]!.push(names[b!]!);});
    // Exhaustive permutations are a separate oracle for this finite graph, not the reference's Kahn algorithm.
    const legal = permutations.filter(p => p.every(i => deps[i]!.every(d => p.indexOf(names.indexOf(d)) < p.indexOf(i))));
    if (!legal.length) {cyclic++; assert.throws(() => workflowFixture(t, {dependencies: deps}), /cycl/i); continue;}
    dags++;
    for (const declarationOrder of permutations) {
      const f = workflowFixture(t, {dependencies: deps, declarationOrder}), ref = createWorkflowOutcomeReference(f.policy, workflowDefinition);
      for (let n = 0; n < 4; n++) {
        const r = request(n, rejected()), result = ref.evaluate(r); assert.deepEqual(result, production(f, r));
        const plan = result.recovery!.recovery_intent?.plan ?? [];
        assert.equal(plan.length, n);
        const possible = permutations.map(p => p.filter(i => i < n)).filter(p => p.every(i => deps[i]!.filter(d => names.indexOf(d) < n).every(d => p.indexOf(names.indexOf(d)) < p.indexOf(i))));
        possible.sort((a,b) => {for (let i = 0; i < n; i++) if (a[i] !== b[i]) return b[i]! - a[i]!; return 0;});
        assert.deepEqual(plan.map(p => p.compensation_id), possible[0]!.map(i => names[i]));
        for (const row of plan) {
          assert.deepEqual(row.depends_on, deps[names.indexOf(row.compensation_id)]!.filter(d => names.indexOf(d) < n).sort());
          assert.deepEqual(row.inactive_dependencies, deps[names.indexOf(row.compensation_id)]!.filter(d => names.indexOf(d) >= n).sort());
        }
      }
    }
  }
  assert.equal(dags, 25); assert.equal(cyclic, 39);
});

test('native generated Workflows match the independent oracle at every settlement position', async t => {
  for (const options of [{}, {dependencies: [[], ['undo-first'], ['undo-second']]}, {noCompensations: true}]) {
    const f = workflowFixture(t, options), native = nativeWorkflow(f), ref = createWorkflowOutcomeReference(f.policy, workflowDefinition);
    for (let n = -1; n < 4; n++) for (const mode of n === -1 ? ['committed'] : ['reject', 'indeterminate', 'malformed', 'throw-before', 'throw-after']) {
      const store = settlementProvider(n, mode);
      const actual = await native.run({amount: '18446744073709551615'}, {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, {'commerce:perform': store.dependency});
      const terminal = n === -1 ? undefined : {...rejected(), status: mode === 'reject' ? 'rejected' : 'indeterminate',
        code: mode === 'reject' ? 'COMMIT_REJECTED' : mode === 'indeterminate' ? 'COMMIT_INDETERMINATE' : mode === 'malformed' ? 'INVALID_COMMIT_RECEIPT' : 'COMMIT_UNCERTAIN'};
      const expected = ref.evaluate(request(n === -1 ? 4 : n, terminal));
      assert.deepEqual(actual.evaluation, expected, JSON.stringify({options, n, mode}));
      assert.equal(store.count(), n === -1 ? 4 : n + 1);
      assert.deepEqual(store.trace, Array.from({length: store.count()}, (_, i) => ['begin:' + i, 'commit:' + i]).flat());
      assert.equal(store.commits.length, n === -1 ? 4 : n + (mode === 'throw-after' ? 1 : 0));
      if (n === -1) {assert.equal(actual.status, 'succeeded'); assert.equal(actual.value, 18446744073709551615n);}
      if (mode !== 'reject') assert.equal(actual.recovery_bindings, null);
    }
  }
});

test('independent expectation detects settlement, occurrence, recovery and digest observation mutations', t => {
  const f = workflowFixture(t), expected = createWorkflowOutcomeReference(f.policy, workflowDefinition).evaluate(request(3, rejected()));
  const mutations = [
    (v: any) => v.observations[0].settlement.commit_status = 'not-committed',
    (v: any) => v.observations[1].step_id = 'first',
    (v: any) => v.completed_step_ids.reverse(),
    (v: any) => v.recovery.recovery_intent.plan.reverse(),
    (v: any) => v.recovery.recovery_intent.plan[0].invocation_identity = '0'.repeat(64),
    (v: any) => v.recovery.recovery_intent.plan_digest = '0'.repeat(64),
    (v: any) => v.recovery.compensation_execution = true,
    (v: any) => v.recovery.recovery_intent = null
  ];
  for (const mutate of mutations) {const v = structuredClone(expected); mutate(v); assert.throws(() => assert.deepEqual(v, expected));}
});

test('compiling generated-provider mutations are rejected by the independent metadata oracle', async t => {
  const f = workflowFixture(t), ref = createWorkflowOutcomeReference(f.policy, workflowDefinition);
  const mutations = [
    ['unawaited call', 'raw=await call0(args,dep0)', 'raw=call0(args,dep0)'],
    ['collapsed occurrence', 'observe(1,', 'observe(0,'],
    ['reversed completed prefix', "observations.filter(r=>r.settlement.commit_status==='committed').map(r=>r.step_id)", "observations.filter(r=>r.settlement.commit_status==='committed').map(r=>r.step_id).reverse()"],
    ['missing selected recovery', 'if(!template.plan.length)', 'if(template.plan.length>=0)'],
    ['reversed selected plan', 'template.plan.map(row=>', '[...template.plan].reverse().map(row=>'],
    ['wrong invocation identity', "schema_version:'domainspec.compensation-invocation/v2-candidate',intent_id,plan_digest", "schema_version:'domainspec.compensation-invocation/v2-candidate',intent_id:'wrong',plan_digest"],
    ['false known noncommit', "commit_status:status==='indeterminate'?'indeterminate':'not-committed'", "commit_status:status==='indeterminate'?'not-committed':'not-committed'"]
  ];
  for (const [name, before, after] of mutations) {
    let changed = 0;
    const n = nativeWorkflow(f, (file, code) => {
      if (!file.endsWith('/workflows/flow.provider.ts')) return code;
      assert.ok(code.includes(before!), name); changed++;
      return code.replaceAll(before!, after!);
    });
    assert.equal(changed, 1);
    const mode = name === 'false known noncommit' ? 'indeterminate' : 'reject', store = settlementProvider(3, mode);
    const actual = await n.run({amount: '3'}, {workflow_execution_id: 'execution-one', failure_occurrence_id: 'failure-one'}, {'commerce:perform': store.dependency});
    const terminal = mode === 'reject' ? rejected() : {...rejected(), status: 'indeterminate', code: 'COMMIT_INDETERMINATE'};
    assert.notDeepEqual(actual.evaluation, ref.evaluate(request(3, terminal)), name);
  }
});
