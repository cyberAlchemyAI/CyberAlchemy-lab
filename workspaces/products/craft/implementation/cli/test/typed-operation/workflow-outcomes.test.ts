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
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {WORKFLOW_OCCURRENCES_VERSION} from '../../src/typed-backend/workflow-occurrences.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {selectWorkflowRecoveryPolicy, planSelectedWorkflowRecovery, decodeWorkflowFailureJournal, assertCheckedWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_FAILURE_JOURNAL_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../../src/typed-operation/workflow-recovery.ts';

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
const policyContract = read('profile-compiler-reconciliation/workflow-recovery-policy-contract.json');
const at = (root: string) => ({op: 'path', root, properties: []});
const literal = (type: string, value: any) => ({op: 'literal', type, value});

function baseFixture(t: any) {
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
  return {temp, source, write, node, save, workflow, definitions, edges, compile, ...compile()};
}

function fixture(t: any) {
  const f = baseFixture(t);
  f.workflow.steps.push({step_id: 'third', operation_ref: 'commerce:post'});
  const build = () => {
    if (!f.workflow.compensations.length) {
      const i = f.edges.indexOf('flow-release'); if (i >= 0) f.edges.splice(i, 1);
    }
    f.save(); const c = f.compile(), b = c.bindings;
    const stepTemplates = structuredClone(b.steps), compTemplates = structuredClone(b.compensations);
    b.steps = f.workflow.steps.map((s: any, i: number) => ({...structuredClone(stepTemplates[i === 0 ? 0 : 1]), step_id: s.step_id}));
    b.compensations = f.workflow.compensations.map((s: any) => {
      const call = {...structuredClone(compTemplates[s.for_step === 'first' ? 0 : 1]), compensation_id: s.compensation_id};
      call.arguments[0].value = result(s.for_step); return call;
    });
    const used = new Set([...b.steps, ...b.compensations].flatMap((c: any) => c.events.map((e: any) => e.input)));
    b.event_inputs = b.event_inputs.filter((i: any) => used.has(i.name));
    const refs = new Set([...f.workflow.steps, ...f.workflow.compensations].map((s: any) => s.operation_ref));
    const workflow = compileWorkflowBindings(c.graph, c.boundary, c.fields, c.actions.filter(a => refs.has(a.bindings.selector)), b, contract);
    const selection: any = {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256,
      contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion'};
    const policy = selectWorkflowRecoveryPolicy(workflow, selection, policyContract);
    return {...c, workflow, selection, policy, plan: (j: any) => planSelectedWorkflowRecovery(policy, j)};
  };
  return {...f, sourceWorkflow: f.workflow, build, ...build()};
}
import {inspectOperationSettlement, observeWorkflowStep, evaluateWorkflowOutcomeJournal, WORKFLOW_OUTCOME_JOURNAL_VERSION, WORKFLOW_OUTCOME_CONTRACT_SHA256} from '../../src/typed-operation/workflow-outcomes.ts';
const outcomeContract = read('profile-compiler-reconciliation/workflow-outcome-contract.json');
const failure = (status = 'failed', stage = 'read', code = 'OPERATION_FAILED', cleanupFailed = false): any =>
  ({status, stage, code, continuation: 'return-post-error', cleanupFailed});
const inspect = (v: unknown) => inspectOperationSettlement(v, 'return-post-error');
const envelope = (observations: any[], failureId: string | null = null, local_error: string | null = null): any => ({
  schema_version: WORKFLOW_OUTCOME_JOURNAL_VERSION, workflow_execution_id: 'run-one',
  failure_occurrence_id: failureId, observations, local_error,
});
const observe = (f: ReturnType<typeof fixture>, index: number, outcome: any = {status: 'committed', value: 'result'}) =>
  observeWorkflowStep(f.workflow, f.workflow.steps[index]!.step_id, {kind: 'returned', outcome}, outcomeContract);
const frozen = (v: any): void => {if (v && typeof v === 'object') {assert(Object.isFrozen(v)); Object.values(v).forEach(frozen);}};

test('Operation settlement metadata preserves every generated failure stage and cleanup distinction', () => {
  const cases = [
    failure('failed', 'input', 'OPERATION_INPUT'), failure('failed', 'begin', 'BEGIN_FAILED'),
    ...['read', 'guard', 'write-validation', 'event', 'result'].flatMap(stage => [failure('failed', stage), failure('failed', stage, 'OPERATION_FAILED', true)]),
    ...['READ_NOT_FOUND', 'READ_IDENTITY_MISMATCH'].map(code => failure('failed', 'read', code)),
    failure('rejected', 'guard', 'RULE_REJECTED:commerce:allowed'),
    failure('rejected', 'guard', 'RULE_REJECTED:commerce:allowed', true),
    failure('rejected', 'commit', 'COMMIT_REJECTED'),
  ];
  for (const v of cases) {
    const r = inspect(v); assert.equal(r.commit_status, 'not-committed', JSON.stringify(v));
    assert.equal(r.status, v.status); assert.equal(r.stage, v.stage); assert.equal(r.code, v.code);
    assert.equal(r.cleanup_failed, v.cleanupFailed); assert.equal(r.continuation, v.continuation); frozen(r);
    assert(!Object.isFrozen(v));
  }
  for (const code of ['COMMIT_UNCERTAIN', 'COMMIT_INDETERMINATE', 'INVALID_COMMIT_RECEIPT']) {
    const r = inspect(failure('indeterminate', 'commit', code)); assert.equal(r.commit_status, 'indeterminate'); assert.equal(r.code, code);
  }
});

test('A committed envelope is not a validated result and never traverses or freezes caller payloads', () => {
  let calls = 0;
  const payload: any = {amount: 18446744073709551615n, get nested() {calls++; throw Error('do not read');}};
  payload.self = payload;
  for (const value of [payload, undefined, null, Symbol('unvalidated'), () => calls++]) {
    const r = inspect({status: 'committed', value});
    assert.equal(r.commit_status, 'committed'); assert.equal(r.result_validation, 'not-performed');
    assert.equal(Object.hasOwn(r, 'value'), false);
  }
  assert.equal(calls, 0); assert(!Object.isFrozen(payload));
});

test('Malformed returns and impossible failure combinations are unknown, never invented precommit failures', () => {
  const bad = [null, undefined, false, [], {}, {status: 'committed'}, {status: 'committed', value: 1, extra: true},
    {...failure(), continuation: 'other-action'}, {...failure(), cleanupFailed: 'false'},
    failure('failed', 'commit', 'OPERATION_FAILED'), failure('indeterminate', 'read', 'OPERATION_FAILED'),
    failure('rejected', 'read', 'RULE_REJECTED:commerce:allowed'), failure('failed', 'input', 'OPERATION_INPUT', true),
    failure('rejected', 'commit', 'COMMIT_REJECTED', true), failure('failed', 'unknown', 'OPERATION_FAILED'),
    failure('failed', 'begin', 'NEW_CODE'), {...failure(), code: 'x'.repeat(3000)}];
  let calls = 0;
  bad.push({get status() {calls++; return 'failed';}}, {status: 'committed', get value() {calls++; return 1;}});
  bad.push(Object.defineProperty(failure(), 'code', {get() {calls++; return 'OPERATION_FAILED';}}));
  bad.push(Object.defineProperty(failure(), 'hidden', {value: 1}));
  bad.push({...failure(), [Symbol('extra')]: 1}, Object.assign(Object.create({}), failure()));
  const revoked = Proxy.revocable({}, {}); revoked.revoke(); bad.push(revoked.proxy);
  for (const v of bad) {const r = inspect(v); assert.equal(r.commit_status, 'indeterminate'); assert.equal(r.origin, 'invalid-return');}
  assert.equal(calls, 0);
});

test('Exact occurrence observations and policy projection preserve every source failure prefix', t => {
  const f = fixture(t);
  for (let n = 0; n < f.workflow.steps.length; n++) {
    const prefix = Array.from({length: n}, (_, i) => observe(f, i));
    for (const [raw, unknown] of [[failure(), false], [failure('rejected', 'commit', 'COMMIT_REJECTED'), false],
      [failure('indeterminate', 'commit', 'COMMIT_UNCERTAIN'), true], [{status: 'failed'}, true]] as const) {
      const terminal = observe(f, n, raw), input = envelope([...prefix, terminal], 'failure-one');
      const r = evaluateWorkflowOutcomeJournal(f.policy, input); frozen(r);
      assert.equal(r.status, 'forward-stopped'); assert.deepEqual(r.completed_step_ids, f.workflow.steps.slice(0, n).map(s => s.step_id));
      assert.equal(r.recovery!.journal.failed_step_id, f.workflow.steps[n]!.step_id);
      assert.equal(r.recovery_status, unknown ? 'reconciliation-required' : 'evaluated');
      if (unknown) assert.equal(r.recovery!.recovery_intent, null);
      else assert.deepEqual(r.recovery, f.plan({schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION,
        workflow_execution_id: 'run-one', failure_occurrence_id: 'failure-one',
        completed_step_ids: f.workflow.steps.slice(0, n).map(s => s.step_id),
        failed_step_id: f.workflow.steps[n]!.step_id, failed_commit_status: 'not-committed'}));
      assert(!Object.isFrozen(input)); assert(!Object.isFrozen(input.observations));
    }
  }
});

test('Thrown calls and not-started argument preparation keep different evidence and recovery meaning', t => {
  const f = fixture(t), first = observe(f, 0);
  const threw = observeWorkflowStep(f.workflow, 'second', {kind: 'threw'}, outcomeContract);
  const notStarted = observeWorkflowStep(f.workflow, 'second', {kind: 'not-started'}, outcomeContract);
  const unknown = evaluateWorkflowOutcomeJournal(f.policy, envelope([first, threw], 'failure-one'));
  const known = evaluateWorkflowOutcomeJournal(f.policy, envelope([first, notStarted], 'failure-one'));
  assert.equal(unknown.recovery_status, 'reconciliation-required'); assert.equal(unknown.failure!.origin, 'threw');
  assert.equal(known.recovery_status, 'evaluated'); assert.equal(known.failure!.origin, 'not-started');
  assert.equal(known.failure!.status, null); assert.equal(known.failure!.continuation, null);
  assert.deepEqual(known.recovery!.recovery_intent!.plan.map(c => c.compensation_id), ['first']);
  assert.equal(known.recovery!.compensation_execution, false);
});

test('Awaiting a step, forward completion and postcommit result errors are not Workflow success or not-required recovery', t => {
  const f = fixture(t), all = f.workflow.steps.map((_, i) => observe(f, i));
  for (let n = 0; n <= all.length; n++) {
    const r = evaluateWorkflowOutcomeJournal(f.policy, envelope(all.slice(0, n)));
    assert.equal(r.status, n === all.length ? 'forward-complete' : 'awaiting-next-step');
    assert.equal(r.result_validation, 'not-performed'); assert.equal(r.recovery_status, 'not-evaluated'); assert.equal(r.recovery, null);
  }
  for (let n = 1; n <= all.length; n++) {
    const r = evaluateWorkflowOutcomeJournal(f.policy, envelope(all.slice(0, n), 'failure-one', 'committed-result-invalid'));
    assert.equal(r.status, 'orchestration-error'); assert.equal(r.recovery_status, 'not-evaluable');
    assert.equal(r.recovery, null); assert.equal(r.completed_step_ids.length, n);
    assert.equal(Object.hasOwn(r, 'failed_step_id'), false);
  }
  const r = evaluateWorkflowOutcomeJournal(f.policy, envelope(all, 'failure-one', 'result-materialization-failed'));
  assert.equal(r.completed_step_ids.length, 3); assert.equal(r.recovery, null);
  assert.throws(() => evaluateWorkflowOutcomeJournal(f.policy, envelope(all.slice(0, 1), 'failure-one', 'result-materialization-failed')));
  assert.throws(() => evaluateWorkflowOutcomeJournal(f.policy, envelope([], 'failure-one', 'committed-result-invalid')));
});

test('Journal rejects reordering, duplicate or later observations, cloned brands, stale policy and invalid failure identity', t => {
  const f = fixture(t), a = observe(f, 0), b = observe(f, 1), failed = observe(f, 1, failure());
  for (const j of [envelope([b]), envelope([a, a]), envelope([a, failed, observe(f, 2)], 'failure-one'),
    envelope([structuredClone(a)]), envelope([a], 'failure-one'), envelope([a, failed]),
    envelope([a, failed], 'failure-one', 'committed-result-invalid'), envelope([a, failed], 'bad\n'),
    {...envelope([a]), schema_version: 'unknown'}, {...envelope([a]), extra: true}]) {
    assert.throws(() => evaluateWorkflowOutcomeJournal(f.policy, j));
  }
  assert.throws(() => evaluateWorkflowOutcomeJournal(structuredClone(f.policy), envelope([a])));
  const other = fixture(t); other.sourceWorkflow.compensations[0].depends_on = []; const changed = other.build();
  assert.throws(() => evaluateWorkflowOutcomeJournal(changed.policy, envelope([a])));
  assert.throws(() => observeWorkflowStep(structuredClone(f.workflow), 'first', {kind: 'threw'}, outcomeContract));
  assert.throws(() => observeWorkflowStep(f.workflow, 'missing', {kind: 'threw'}, outcomeContract));
  assert.throws(() => observeWorkflowStep(f.workflow, 'first', {kind: 'threw'}, outcomeContract + ' '));
  assert.equal(sha256(outcomeContract), WORKFLOW_OUTCOME_CONTRACT_SHA256);
});

test('Inert envelope and observation ownership checks reject accessors, cycles and sparse resource abuse', t => {
  const f = fixture(t), a = observe(f, 0); let calls = 0;
  const accessor = Object.defineProperty([a], '0', {get() {calls++; return a;}});
  const cyclic: any = envelope([a]); cyclic.extra = cyclic;
  for (const j of [{...envelope([]), get observations() {calls++; return [a];}},
    envelope(accessor), envelope(new Array(2)), envelope(Array(129).fill(a)), cyclic]) assert.throws(() => evaluateWorkflowOutcomeJournal(f.policy, j));
  assert.throws(() => observeWorkflowStep(f.workflow, 'first', {get kind() {calls++; return 'not-started';}}, outcomeContract));
  assert.throws(() => observeWorkflowStep(f.workflow, 'first', {kind: 'not-started', outcome: failure()}, outcomeContract));
  assert.equal(calls, 0); frozen(a); assert.equal(a.evidence, 'caller-supplied');
});

test('Repeated Operation observations retain occurrence identity and deterministic evidence without replay claims', t => {
  const f = fixture(t), a = observe(f, 0), b = observe(f, 1);
  assert.equal(a.operation_ref, b.operation_ref); assert.equal(a.action_sha256, b.action_sha256);
  assert.notEqual(a.observation_sha256, b.observation_sha256); assert.deepEqual(a, observe(f, 0));
  const rows = [a, observe(f, 1, failure('failed', 'read', 'READ_NOT_FOUND', true))];
  const j = envelope(rows, 'failure-one'), r = evaluateWorkflowOutcomeJournal(f.policy, j);
  assert.deepEqual(r, evaluateWorkflowOutcomeJournal(f.policy, j)); assert.equal(r.failure!.cleanup_failed, true);
  const changed = evaluateWorkflowOutcomeJournal(f.policy, {...j, failure_occurrence_id: 'failure-two'});
  assert.notEqual(changed.recovery!.recovery_intent!.intent_id, r.recovery!.recovery_intent!.intent_id);
  assert.equal(r.recovery!.intent_registration, 'not-performed');
});

