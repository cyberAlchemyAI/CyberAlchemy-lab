import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {crossGeneratorPublicFixture} from '../helpers/cross-generator-public.ts';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture} from '../helpers/workflow-values.ts';
import {policyFixture} from '../helpers/cross-generator-policy.ts';
import {stateMachineFixture} from '../helpers/state-machine-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {getCrossGeneratorSource} from '../../src/verification/cross-generator-sources.ts';
import {prepareCrossGeneratorVerification, crossGeneratorPreparationBindings, CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256} from '../../src/verification/reconciled-cross-generator-public.ts';
import {createReconciledSemanticControls, assertReconciledSemanticControlsFor, renderSemanticCases} from '../../src/verification/reconciled-semantic-controls.ts';

test('standalone semantic identity is exact without changing readiness or serialized cases', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const controls = createReconciledSemanticControls(f.graph, plan), before = renderSemanticCases(controls);
  assertReconciledSemanticControlsFor(controls, f.graph, plan);
  assert.equal(renderSemanticCases(controls), before);
  const workflow = controls.rows.find(r => r.kind === 'Workflow')!;
  assert.equal(workflow.state, 'ready');
  if (workflow.state !== 'ready') throw Error('expected scalar Workflow readiness');
  assert.equal(workflow.cases.length, 134);
  assert.throws(() => assertReconciledSemanticControlsFor(structuredClone(controls), f.graph, plan), /registered semantic/);
  assert.throws(() => assertReconciledSemanticControlsFor(controls, structuredClone(f.graph), plan), /foreign semantic/);
  assert.throws(() => assertReconciledSemanticControlsFor(controls, f.graph, structuredClone(plan)), /foreign semantic/);
  const sameGraph = loadCompiledProjectGraph(f.graph.project_root), samePlan = planCompiledReconciledProject(f.graph, f.selection);
  assert.equal(samePlan.plan_sha256, plan.plan_sha256);
  assert.throws(() => assertReconciledSemanticControlsFor(controls, sameGraph, plan), /foreign semantic/);
  assert.throws(() => assertReconciledSemanticControlsFor(controls, f.graph, samePlan), /foreign semantic/);
  let reads = 0; const active = Object.defineProperty({}, 'controls_sha256', {get() {reads++; return controls.controls_sha256;}});
  for (const value of [null, false, active, JSON.parse(JSON.stringify(controls))]) {
    assert.throws(() => assertReconciledSemanticControlsFor(value, f.graph, plan), /registered semantic/);
  }
  assert.equal(reads, 0);
});

test('preparation preserves every request, module, root, typed import and native dependency without claiming execution', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection);
  const p = prepareCrossGeneratorVerification(f.graph, plan), state = crossGeneratorPreparationBindings(p, f.graph, plan), b = state.boundary;
  assert.equal(sha256(getCrossGeneratorSource('public')), CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256);
  assert.deepEqual(p.families.map(f => f.family), ['policy', 'state-machine', 'factory-rule', 'owned-values', 'value-producer', 'operation', 'workflow']);
  assert.ok(p.families.every(f => f.state === 'prepared'));
  assert.deepEqual(p.requests, b.requests); assert.deepEqual(p.modules, b.modules); assert.deepEqual(p.roots, b.roots);
  assert.deepEqual(p.edges.map(({behavior_required, witnesses, selection_status, execution_status, ...edge}) => edge), b.edges);
  assert.ok(p.roots.some(r => !r.edge_sha256s.length), 'zero-edge Rule root retained');
  assert.ok(p.edges.some(e => e.category === 'generated-type-only'));
  assert.ok(p.edges.some(e => e.category === 'native-standard-library'));
  assert.ok(p.edges.every(e => e.execution_status === 'not_evaluable'));
  assert.equal(p.behavior_status, 'not_evaluable'); assert.equal(p.authority_effect, 'none');
  const {preparation_sha256, ...body} = p; assert.equal(sha256(canonicalJson(body)), preparation_sha256);
  assert.ok(Object.isFrozen(p) && Object.isFrozen(p.edges) && Object.isFrozen(state) && Object.isFrozen(state.bindings));
  const workflow = p.rows.find(r => r.family === 'workflow')!;
  assert.equal(workflow.case_count, 133);
  assert.equal(workflow.batch_count, 1);
  assert.ok(workflow.identity_edges.length > 0);
  assert.ok(p.edges.filter(e => workflow.identity_edges.includes(e.edge_sha256)).every(e => e.witnesses.some(w => w.kind === 'original-wrapper-identity-required')));
});

test('cloned, foreign and active inputs cannot be used to substitute preparation or its execution bindings', t => {
  const f = workflowFixture(t), plan = planCompiledReconciledProject(f.graph, f.selection), p = prepareCrossGeneratorVerification(f.graph, plan);
  assert.throws(() => prepareCrossGeneratorVerification(structuredClone(f.graph), plan), /unvalidated or changed/);
  assert.throws(() => prepareCrossGeneratorVerification(f.graph, structuredClone(plan)), /registered/);
  assert.throws(() => crossGeneratorPreparationBindings(structuredClone(p), f.graph, plan), /registered preparation/);
  const other = workflowFixture(t), otherPlan = planCompiledReconciledProject(other.graph, other.selection);
  assert.throws(() => crossGeneratorPreparationBindings(p, other.graph, plan), /foreign/);
  assert.throws(() => crossGeneratorPreparationBindings(p, f.graph, otherPlan), /foreign/);
  let reads = 0; const active: any = {};
  Object.defineProperty(active, 'plan_sha256', {get() {reads++; return plan.plan_sha256;}});
  assert.throws(() => prepareCrossGeneratorVerification(f.graph, active), /registered/);
  assert.equal(reads, 0);
});

test('unavailable Policy rows cannot disappear behind another ready family sharing its Rule edge', t => {
  const f = policyFixture(t), p = prepareCrossGeneratorVerification(f.graph, f.plan);
  assert.equal(p.families.find(f => f.family === 'policy')!.row_count, 5);
  const unavailable = p.rows.find(r => r.family === 'policy' && r.selector === 'alpha:constant')!;
  assert.equal(unavailable.state, 'not_evaluable');
  assert.ok(p.remaining.includes(unavailable));
  assert.deepEqual(unavailable.protocol_edges, []);
  assert.ok(p.rows.some(r => r.family === 'policy' && r.state === 'ready'));
  assert.ok(p.edges.every(e => e.witnesses.every(w => w.selector !== 'alpha:constant')));
  assert.equal(p.behavior_status, 'not_evaluable');
});

test('State Machine coverage remains separate from unguarded and standalone semantic obligations', t => {
  const f = stateMachineFixture(t), p = prepareCrossGeneratorVerification(f.graph, f.plan);
  assert.equal(p.families.find(f => f.family === 'state-machine')!.state, 'prepared');
  assert.equal(p.families.find(f => f.family === 'state-machine')!.row_count, 2);
  const guarded = p.rows.find(r => r.selector === 'alpha:lifecycle')!;
  assert.equal(guarded.state, 'ready');
  assert.ok(guarded.protocol_edges.length > 0);
  assert.ok(p.roots.some(r => r.selector === 'alpha:unrelated'));
  assert.ok(p.rows.every(r => r.selector !== 'alpha:unrelated'), 'standalone Event checks are not State Machine call coverage');
});

test('complete compound Workflow preparation keeps owned values, sum producer, Events and repeated import occurrences in both layouts', t => {
  const f = workflowValuesFixture(t, {events: true});
  for (const module_root of ['domain', 'application/domain']) {
    const plan = planCompiledReconciledProject(f.graph, {...f.selection, module_root});
    const p = prepareCrossGeneratorVerification(f.graph, plan), state = crossGeneratorPreparationBindings(p, f.graph, plan);
    assert.ok(p.families.every(f => f.state === 'prepared'), JSON.stringify(p.families));
    assert.deepEqual(p.remaining, []);
    assert.equal(p.roots.length, 11); assert.equal(p.modules.length, 17); assert.equal(p.edges.length, 42);
    assert.equal(p.rows.filter(r => r.family === 'factory-rule').length, 3);
    assert.equal(p.rows.filter(r => r.family === 'owned-values').length, 3);
    assert.equal(p.rows.filter(r => r.family === 'value-producer').length, 1);
    assert.equal(p.rows.find(r => r.family === 'workflow')!.case_count, 12472);
    assert.equal(p.rows.find(r => r.family === 'workflow')!.batch_count, 4);
    assert.equal(state.bindings.workflow.state, 'prepared');
    if (state.bindings.workflow.state !== 'prepared') throw Error('expected Workflow binding');
    const workflow = state.bindings.workflow.value.controls.rows[0]!;
    assert.equal(workflow.state, 'ready');
    if (workflow.state !== 'ready') throw Error('expected whole Workflow family');
    assert.equal(workflow.cases.reduce((n, c) => n + c.expected.calls.length, 0), 20369);
    const repeated = p.edges.filter(e => e.importer_path.endsWith('/entities/order.ts') && e.target_path?.endsWith('/value-objects/money.ts') && e.category === 'generated-runtime');
    assert.equal(repeated.length, 2); assert.notEqual(repeated[0]!.edge_sha256, repeated[1]!.edge_sha256);
    for (const edge of repeated) assert.ok(edge.witnesses.some(w => w.family === 'owned-values'));
    const wrappers = p.edges.filter(e => /\/events\/(?:posted|released)\.ts$/.test(e.importer_path) && e.category === 'generated-runtime');
    assert.equal(wrappers.length, 2);
    for (const edge of wrappers) assert.ok(edge.witnesses.some(w => w.family === 'operation' && w.kind === 'original-wrapper-identity-required'));
    assert.deepEqual(p.uncovered_required_edges, []);
    assert.equal(p.behavior_status, 'not_evaluable', 'even complete source coverage is not executed evidence');
    t.diagnostic(JSON.stringify({layout: module_root, cases: 12472, calls: 20369, edges: p.edges.length}));
  }
});

test('independent unavailable factory Rule witnesses stay unmet while owned-value and Workflow controls remain selectable', t => {
  const f = workflowValuesFixture(t, {events: true}), file = path.join(f.root, 'source/specs/commerce/nodes/positive.json');
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  raw.body.typed_contract.expression = {op: 'eq', left: {op: 'literal', type: 'Bool', value: true}, right: {op: 'literal', type: 'Bool', value: true}};
  fs.writeFileSync(file, JSON.stringify(raw));
  const graph = loadCompiledProjectGraph(path.join(f.root, 'source')), plan = planCompiledReconciledProject(graph, f.selection), p = prepareCrossGeneratorVerification(graph, plan);
  assert.ok(p.rows.some(r => r.family === 'factory-rule' && r.state === 'not_evaluable'));
  assert.ok(p.rows.some(r => r.family === 'owned-values' && r.state === 'ready'));
  assert.ok(p.rows.some(r => r.family === 'workflow' && r.state === 'ready'));
  assert.ok(p.remaining.some(r => r.family === 'factory-rule'));
  assert.equal(p.behavior_status, 'not_evaluable');
});

test('one compound graph composes all seven nonempty families plus plain Enum initialization', t => {
  const f = crossGeneratorPublicFixture(t), graph = f.graph, plan = planCompiledReconciledProject(graph, f.selection);
  const p = prepareCrossGeneratorVerification(graph, plan);
  assert.ok(p.families.every(f => f.state === 'prepared' && f.row_count > 0), JSON.stringify(p.families));
  assert.ok(p.families.every(f => p.rows.some(r => r.family === f.family && r.state === 'ready')));
  assert.deepEqual(p.remaining, []); assert.deepEqual(p.uncovered_required_edges, []);
  const plain = p.rows.find(r => r.family === 'value-producer' && r.selector === 'commerce:priority')!;
  assert.equal(plain.case_count, 1); assert.equal(plain.protocol_edges.length, 2);
  assert.equal(p.rows.find(r => r.family === 'workflow')!.case_count, 12472);
  assert.equal(p.roots.length, 14);
  assert.equal(p.behavior_status, 'not_evaluable');
  t.diagnostic(JSON.stringify({families: 7, roots: p.roots.length, edges: p.edges.length, remaining: p.remaining.length}));
});
