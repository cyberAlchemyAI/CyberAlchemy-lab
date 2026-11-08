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
import {planWorkflowRecovery} from '../../../architecture-conformance/targets/typescript/workflow-compensation-v1.ts';
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
const journal = (completed_step_ids: string[] = ['first'], failed_commit_status = 'not-committed'): any => ({
  schema_version: WORKFLOW_FAILURE_JOURNAL_VERSION, workflow_execution_id: 'run-one', failure_occurrence_id: 'failure-one',
  completed_step_ids, failed_step_id: ['first', 'second', 'third', 'fourth'][completed_step_ids.length], failed_commit_status,
});
const frozen = (v: any) => {if (v && typeof v === 'object') {assert.ok(Object.isFrozen(v)); Object.values(v).forEach(frozen);}};

test('Selected partial recovery omits an inactive ordering dependency and keeps its authored evidence', t => {
  const f = fixture(t), j = journal(), before = canonicalJson(j), r = f.plan(j);
  assert.equal(r.status, 'evaluated'); assert.equal(r.workflow_evaluation_result, 'recovery-required');
  assert.equal(r.recovery_intent!.semantic_status, 'required');
  assert.deepEqual(r.recovery_intent!.plan.map(p => p.compensation_id), ['first']);
  assert.deepEqual(r.recovery_intent!.plan[0]!.depends_on, []);
  assert.deepEqual(r.recovery_intent!.plan[0]!.inactive_dependencies, ['second']);
  assert.deepEqual(f.workflow.compensations[0]!.depends_on, ['second']);
  assert.equal(canonicalJson(j), before); assert.equal(Object.isFrozen(j), false); frozen(r);
  assert.equal(r.compensation_execution, false); assert.equal(r.intent_registration, 'not-performed'); assert.equal(r.commit_evidence, 'caller-supplied');
  assert.deepEqual(r.recovery_intent!.plan[0]!.arguments, f.workflow.compensations[0]!.arguments);
  assert.deepEqual(r.recovery_intent!.plan[0]!.events, f.workflow.compensations[0]!.events);
});

test('Active ordering constraints are honored while unconstrained actions have a deterministic tie-break', t => {
  const f = fixture(t), j = journal(['first', 'second']);
  const ordered = f.plan(j); assert.deepEqual(ordered.recovery_intent!.plan.map(p => p.compensation_id), ['second', 'first']);
  assert.deepEqual(ordered.recovery_intent!.plan[1]!.depends_on, ['second']);
  f.sourceWorkflow.compensations[0].depends_on = [];
  const independent = f.build().plan(j); assert.deepEqual(independent.recovery_intent!.plan.map(p => p.compensation_id), ['second', 'first']);
  assert.ok(independent.recovery_intent!.plan.every(p => p.depends_on.length === 0));
  assert.notEqual(ordered.recovery_intent!.plan_digest, independent.recovery_intent!.plan_digest);
  f.sourceWorkflow.compensations[1].depends_on = ['first'];
  const opposite = f.build().plan(j); assert.deepEqual(opposite.recovery_intent!.plan.map(p => p.compensation_id), ['first', 'second']);
  f.sourceWorkflow.compensations.reverse();
  assert.deepEqual(f.build().plan(j).recovery_intent!.plan.map(p => p.compensation_id), ['first', 'second']);
});

test('Indeterminate forward commits stop before any recovery evaluation or immutable intent', t => {
  const f = fixture(t);
  for (const prefix of [[], ['first'], ['first', 'second']]) {
    const r = f.plan(journal(prefix, 'indeterminate'));
    assert.equal(r.status, 'reconciliation-required'); assert.equal(r.workflow_evaluation_result, null); assert.equal(r.recovery_intent, null);
    assert.equal(r.unknown_step_id, journal(prefix).failed_step_id); assert.equal(r.compensation_execution, false);
    assert.equal(Object.hasOwn(r, 'plan'), false); frozen(r);
  }
  assert.equal(f.plan(journal([], 'not-committed')).workflow_evaluation_result, 'not-required');
  f.sourceWorkflow.compensations = []; const noRecovery = f.build();
  assert.equal(noRecovery.plan(journal(['first'])).workflow_evaluation_result, 'not-required');
  assert.equal(noRecovery.plan(journal(['first'], 'indeterminate')).status, 'reconciliation-required');
});

test('Only the exact confirmed source prefix and immediately following failed step are accepted', t => {
  const f = fixture(t);
  for (const change of [(j: any) => j.completed_step_ids = ['second'], (j: any) => j.completed_step_ids = ['first', 'first'],
    (j: any) => j.failed_step_id = 'first', (j: any) => j.failed_step_id = 'third', (j: any) => j.failed_step_id = 'missing',
    (j: any) => {j.completed_step_ids = ['first', 'second', 'third']; j.failed_step_id = 'fourth';},
    (j: any) => j.completed_step_ids = ['first', 'missing'], (j: any) => j.failed_commit_status = 'failed',
    (j: any) => j.failed_commit_status = 'committed', (j: any) => j.failed_commit_status = 'rejected']) {
    const j = journal(); change(j); assert.throws(() => f.plan(j));
  }
});

test('Policy selection is explicit, source-bound and cannot be cloned or switched to a permissive fallback', t => {
  const f = fixture(t), initial = canonicalJson(f.selection);
  assertCheckedWorkflowRecoveryPolicy(f.policy); assert.equal(sha256(policyContract), WORKFLOW_RECOVERY_CONTRACT_SHA256);
  assert.equal(canonicalJson(f.selection), initial); assert.equal(Object.isFrozen(f.selection), false); frozen(f.policy);
  for (const mutate of [(s: any) => s.schema_version += '-future', (s: any) => s.dependency_semantics = 'mandatory',
    (s: any) => s.tie_break = 'parallel', (s: any) => s.workflow_sha256 = '0'.repeat(64), (s: any) => s.contract_sha256 = '0'.repeat(64),
    (s: any) => s.extra = true]) {
    const s = structuredClone(f.selection); mutate(s); assert.throws(() => selectWorkflowRecoveryPolicy(f.workflow, s, policyContract));
  }
  assert.throws(() => selectWorkflowRecoveryPolicy(f.workflow, f.selection, policyContract + ' '));
  assert.throws(() => selectWorkflowRecoveryPolicy(structuredClone(f.workflow), f.selection, policyContract));
  assert.throws(() => planSelectedWorkflowRecovery(structuredClone(f.policy), journal()), /unvalidated policy/);
  f.definitions[0].guards[0].arguments[0].value.value = false; const changed = f.build();
  assert.throws(() => selectWorkflowRecoveryPolicy(changed.workflow, f.selection, policyContract), /stale Workflow/);
});

test('Closed inert policy and journal decoding reject accessors, hidden fields and resource abuse without calls', t => {
  const f = fixture(t); let reads = 0;
  const badSelection = {...f.selection, get tie_break() {reads++; return 'reverse-completion';}};
  assert.throws(() => selectWorkflowRecoveryPolicy(f.workflow, badSelection, policyContract));
  const getter = {...journal(), get failed_commit_status() {reads++; return 'not-committed';}}; assert.throws(() => f.plan(getter));
  const hidden = journal(); Object.defineProperty(hidden, 'failed_step_id', {enumerable: false}); assert.throws(() => f.plan(hidden));
  for (const j of [{...journal(), extra: true}, {...journal(), [Symbol()]: true}, {...journal(), completed_step_ids: new Array(4294967295)},
    {...journal(), completed_step_ids: Array(129).fill('first')}, {...journal(), workflow_execution_id: 'run\n'},
    {...journal(), failed_step_id: {toString() {reads++; return 'second';}}}]) assert.throws(() => decodeWorkflowFailureJournal(j));
  const cycle = journal(); cycle.completed_step_ids = cycle; assert.throws(() => f.plan(cycle));
  assert.equal(reads, 0);
});

test('Repeated recovery Operations retain distinct occurrences, action pins and deterministic invocation identities', t => {
  const f = fixture(t), j = journal(['first', 'second']), first = f.plan(j), plan = first.recovery_intent!.plan;
  assert.equal(plan[0]!.operation_ref, plan[1]!.operation_ref); assert.equal(plan[0]!.action_sha256, plan[1]!.action_sha256);
  assert.notEqual(plan[0]!.compensation_id, plan[1]!.compensation_id); assert.notEqual(plan[0]!.invocation_identity, plan[1]!.invocation_identity);
  assert.deepEqual(f.plan(j), first);
  const ids = new Set([first.recovery_intent!.intent_id]);
  for (const key of ['workflow_execution_id', 'failure_occurrence_id']) {
    const modified = {...j, [key]: 'other-one'}, r = f.plan(modified);
    ids.add(r.recovery_intent!.intent_id); assert.notEqual(r.recovery_intent!.plan[0]!.invocation_identity, plan[0]!.invocation_identity);
  }
  assert.equal(ids.size, 3);
  f.definitions[1].result.value = {op: 'path', root: 'order', properties: []};
  f.definitions[1].guards[0].arguments[0].value.value = false;
  const differentAction = f.build().plan(j); assert.notEqual(differentAction.recovery_intent!.intent_id, first.recovery_intent!.intent_id);
  assert.notEqual(differentAction.recovery_intent!.plan[0]!.action_sha256, plan[0]!.action_sha256);
});

test('No recovery requirement is distinct from unresolved planning and from completed recovery', t => {
  const f = fixture(t), none = f.plan(journal([])), needed = f.plan(journal()), unknown = f.plan(journal([], 'indeterminate'));
  assert.equal(none.status, 'evaluated'); assert.equal(none.workflow_evaluation_result, 'not-required'); assert.equal(none.recovery_intent, null);
  assert.equal(needed.recovery_intent!.semantic_status, 'required');
  assert.equal(unknown.status, 'reconciliation-required'); assert.equal(unknown.workflow_evaluation_result, null);
  assert.notEqual(none.journal_sha256, unknown.journal_sha256);
  assert.equal(JSON.stringify([none, needed, unknown]).includes('"satisfied"'), false);
});

test('Legacy strict missing-dependency behavior is preserved separately from the selected new policy', t => {
  const f = fixture(t);
  const legacy = {workflowId: 'flow', workflowExecutionId: 'run-one', failureOccurrenceId: 'failure-one', failedStepId: 'second',
    completedStepIds: ['first'], orchestratedOperationIds: ['undo-first', 'undo-second'],
    mappings: [{stepId: 'first', operationId: 'undo-first', dependsOn: ['undo-second']}, {stepId: 'second', operationId: 'undo-second', dependsOn: []}]};
  assert.throws(() => planWorkflowRecovery(legacy), (e: any) => e.code === 'RECOVERY_DEPENDENCY_INVALID');
  assert.equal(f.plan(journal()).workflow_evaluation_result, 'recovery-required');
});

test('Selected graph is induced: removing inactive vertices does not fabricate transitive prerequisites', t => {
  const f = fixture(t);
  f.sourceWorkflow.steps.push({step_id: 'fourth', operation_ref: 'commerce:post'});
  f.sourceWorkflow.compensations[0].depends_on = ['third'];
  f.sourceWorkflow.compensations.push({compensation_id: 'third', for_step: 'third', operation_ref: 'commerce:release', depends_on: ['second']});
  const updated = f.build();
  const partial = updated.plan(journal(['first', 'second']));
  assert.deepEqual(partial.recovery_intent!.plan.map(p => [p.compensation_id, p.depends_on]), [['second', []], ['first', []]]);
  assert.deepEqual(partial.recovery_intent!.plan[1]!.inactive_dependencies, ['third']);
  const all = updated.plan(journal(['first', 'second', 'third']));
  assert.deepEqual(all.recovery_intent!.plan.map(p => p.compensation_id), ['second', 'third', 'first']);
});

test('Every three-compensation graph and failure prefix agrees with an independent permutation oracle', t => {
  const f = fixture(t), ids = ['first', 'second', 'third'];
  f.sourceWorkflow.steps.push({step_id: 'fourth', operation_ref: 'commerce:post'});
  f.sourceWorkflow.compensations.push({compensation_id: 'third', for_step: 'third', operation_ref: 'commerce:release', depends_on: []});
  const edges = ids.flatMap(a => ids.filter(b => b !== a).map(b => [a, b]));
  const permutations = (items: string[]): string[][] => items.length ? items.flatMap((x, i) => permutations(items.filter((_, j) => i !== j)).map(rest => [x, ...rest])) : [[]];
  const obeys = (order: string[], selectedEdges: string[][]) => selectedEdges.every(([a, b]) => order.indexOf(b!) < order.indexOf(a!));
  let valid = 0, rejected = 0, prefixes = 0;
  for (let mask = 0; mask < 64; mask++) {
    const chosen = edges.filter((_, i) => (mask & (1 << i)) !== 0);
    for (const c of f.sourceWorkflow.compensations) c.depends_on = chosen.filter(([a]) => a === c.compensation_id).map(([, b]) => b);
    const possible = permutations(ids).filter(p => obeys(p, chosen));
    if (!possible.length) {assert.throws(() => f.build(), /cyclic compensation dependency/); rejected++; continue;}
    const current = f.build(); valid++;
    for (let count = 0; count <= 3; count++) {
      const active = ids.slice(0, count), activeEdges = chosen.filter(([a, b]) => active.includes(a!) && active.includes(b!));
      const orders = permutations(active).filter(p => obeys(p, activeEdges));
      // Highest completion rank at the first difference implements the specified
      // tie-break independently of the production ready-node traversal.
      orders.sort((a, b) => {for (let i = 0; i < a.length; i++) {const d = ids.indexOf(b[i]!) - ids.indexOf(a[i]!); if (d) return d;} return 0;});
      const r = current.plan(journal(active)); prefixes++;
      assert.deepEqual(r.recovery_intent?.plan.map(p => p.compensation_id) ?? [], orders[0]);
      for (const p of r.recovery_intent?.plan ?? []) {
        assert.deepEqual(p.depends_on, chosen.filter(([a, b]) => a === p.compensation_id && active.includes(b!)).map(([, b]) => b).sort());
        assert.deepEqual(p.inactive_dependencies, chosen.filter(([a, b]) => a === p.compensation_id && !active.includes(b!)).map(([, b]) => b).sort());
      }
    }
  }
  assert.equal(valid, 25); assert.equal(rejected, 39); assert.equal(prefixes, 100);
});
