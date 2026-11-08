import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {workflowFixture, nativeWorkflow, workflowProject, stepIds} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture, named} from '../helpers/workflow-values.ts';
import {createWorkflowBinding, SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256} from '../../src/verification/reconciled-workflow-binding.ts';
import {planCompiledReconciledProject, selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {inventoryGeneratedModule} from '../../src/generation/generated-module-surface.ts';

const definition = fs.readFileSync(path.join(workflowProject, 'development/reconciliation-v1/profile-compiler-reconciliation/semantic-workflow-binding-contract.json'), 'utf8');
const binding = (f: ReturnType<typeof workflowFixture>) => {
  const plan = planCompiledReconciledProject(f.graph, f.selection);
  return {plan, value: createWorkflowBinding(f.graph.nodes.find(n => n.kind === 'Workflow')!, f.graph, plan, definition)};
};

test('Workflow binding pins definition, source brands, graph member and plan certificate', t => {
  const f = workflowFixture(t), {plan, value} = binding(f), node = f.graph.nodes.find(n => n.kind === 'Workflow')!;
  assert.equal(sha256(definition), SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256);
  assert.equal(value.workflow.workflow_sha256, f.workflow.workflow_sha256);
  assert.equal(value.policy.policy_sha256, f.policy.policy_sha256);
  assert.ok(Object.isFrozen(value) && Object.isFrozen(value.descriptor));
  assert.throws(() => createWorkflowBinding(node, f.graph, plan, definition + '\n'), /definition drift/);
  assert.throws(() => createWorkflowBinding({...node}, f.graph, plan, definition), /source Workflow/);
  assert.throws(() => createWorkflowBinding(f.graph.nodes.find(n => n.kind === 'Operation')!, f.graph, plan, definition), /source Workflow/);
  assert.throws(() => createWorkflowBinding(node, {...f.graph}, plan, definition), /unvalidated|snapshot|registered/i);
  assert.throws(() => createWorkflowBinding(node, f.graph, {...plan}, definition), /plan/);
  assert.throws(() => createWorkflowBinding(node, f.graph, structuredClone(plan), definition), /plan/);
  const other = workflowFixture(t, {noCompensations: true});
  assert.throws(() => createWorkflowBinding(other.graph.nodes.find(n => n.kind === 'Workflow')!, other.graph, plan, definition), /cross-graph/);
});

test('Workflow binding retains all occurrence identities but imports only forward Operations', t => {
  const f = workflowFixture(t), {value} = binding(f);
  assert.deepEqual(value.workflow.steps.map(s => s.step_id), stepIds);
  assert.deepEqual(value.operations.map(o => o.action.bindings.selector).sort(), ['commerce:perform', 'commerce:undo']);
  assert.deepEqual(value.descriptor.operation_imports.map(i => i.selector), ['commerce:perform']);
  assert.ok(value.module_paths.some(p => p.endsWith('/perform.ts')));
  assert.ok(!value.module_paths.some(p => /\/undo(?:\.provider)?\.ts$/.test(p)));
  const external = value.native_imports.flatMap(m => m.imports.filter(i => i.target_path === null).map(i => ({owner: m.relative_path, specifier: i.specifier})));
  assert.deepEqual(external, [{owner: value.provider_path, specifier: 'node:crypto'}]);
});

test('independent descriptor agrees with real strict-compiled native Workflow', t => {
  const f = workflowFixture(t), {plan, value} = binding(f);
  const native = nativeWorkflow({...f, nativePlan: () => selectReconciledArtifacts(plan)});
  assert.deepEqual(native.run.descriptor, value.descriptor);
  assert.equal(value.descriptor.material_sha256, sha256(fs.readFileSync(path.join(native.root, value.material_path), 'utf8')));
  assert.equal(value.descriptor.provider_sha256, sha256(fs.readFileSync(path.join(native.root, value.provider_path), 'utf8')));
});

test('typed Entity and Event closure binds actual compiled descriptor without recovery imports', t => {
  const f = workflowValuesFixture(t, {type: named('order'), events: true}), {plan, value} = binding(f);
  const native = nativeWorkflow({...f, nativePlan: () => selectReconciledArtifacts(plan)});
  assert.deepEqual(native.run.descriptor, value.descriptor);
  assert.ok(value.fields !== null);
  assert.ok(value.module_paths.some(p => p.endsWith('/order.ts')));
  assert.ok(!value.module_paths.some(p => /\/undo(?:\.provider)?\.ts$/.test(p)));
});

test('unconstrained and dependency-ordered recovery bind different exact source identities', t => {
  const a = binding(workflowFixture(t)).value;
  const b = binding(workflowFixture(t, {dependencies: [[], ['undo-first'], ['undo-second']]})).value;
  const none = binding(workflowFixture(t, {noCompensations: true})).value;
  assert.notEqual(a.workflow.workflow_sha256, b.workflow.workflow_sha256);
  assert.notEqual(a.policy.policy_sha256, b.policy.policy_sha256);
  assert.equal(none.workflow.compensations.length, 0);
  assert.equal(none.operations.length, 1);
  assert.deepEqual(a.module_paths, b.module_paths);
});

test('multiple Workflow roots retain their separate canonical Operation ownership', t => {
  const f = workflowFixture(t), source = path.join(f.root, 'source'), nodePath = path.join(source, 'specs/commerce/nodes/flow.json');
  const node = JSON.parse(fs.readFileSync(nodePath, 'utf8')); node.node_id = 'other-flow';
  for (const call of [...node.body.typed_contract.steps, ...node.body.typed_contract.compensations]) call.operation_ref = call.operation_ref.replace('commerce:', 'commerce:other-');
  fs.writeFileSync(path.join(source, 'specs/commerce/nodes/other-flow.json'), JSON.stringify(node));
  const featurePath = path.join(source, 'specs/commerce/feature.json'), feature = JSON.parse(fs.readFileSync(featurePath, 'utf8'));
  feature.nodes.push('other-flow');
  for (const target of ['perform', 'undo']) {
    const targetId = 'other-' + target, operation = JSON.parse(fs.readFileSync(path.join(source, 'specs/commerce/nodes/' + target + '.json'), 'utf8'));
    operation.node_id = targetId; feature.nodes.push(targetId);
    fs.writeFileSync(path.join(source, 'specs/commerce/nodes/' + targetId + '.json'), JSON.stringify(operation));
    for (const [from, relationship] of [['other-flow', 'orchestrates'], ['allowed', 'enforces']]) {
      const id = from + '-' + relationship + '-' + targetId; feature.edges.push(id);
      fs.writeFileSync(path.join(source, 'specs/commerce/edges/' + id + '.json'), JSON.stringify({schema_version: 'domainspec.edge/v1', feature_id: 'commerce', edge_id: id, source_node_id: from, target_node_id: targetId, relationship, scope: 'feature'}));
    }
  }
  fs.writeFileSync(featurePath, JSON.stringify(feature));
  const graph = loadCompiledProjectGraph(source), selection = {...f.selection, operations: [...f.selection.operations, ...f.selection.operations.map(o => ({...o, selector: o.selector.replace('commerce:', 'commerce:other-')}))], workflows: [...f.selection.workflows, {...f.selection.workflows[0]!, selector: 'commerce:other-flow'}]};
  const plan = planCompiledReconciledProject(graph, selection);
  const values = graph.nodes.filter(n => n.kind === 'Workflow').map(n => createWorkflowBinding(n, graph, plan, definition));
  assert.equal(values.length, 2);
  for (const v of values) {
    assert.ok(v.module_paths.includes(v.relative_path));
    assert.ok(!v.module_paths.includes(values.find(other => other !== v)!.relative_path));
  }
  assert.notEqual(values[0]!.descriptor.workflow_sha256, values[1]!.descriptor.workflow_sha256);
});

test('compiling descriptor mutations disagree with the independent binding', t => {
  const f = workflowFixture(t), {plan, value} = binding(f), view = selectReconciledArtifacts(plan);
  const cases = [
    ['policy_sha256', '0'.repeat(64)], ['workflow_sha256', '1'.repeat(64)],
    ['operation_plan_sha256', '2'.repeat(64)], ['compensation_execution', true]
  ] as const;
  for (const [key, replacement] of cases) {
    const {descriptor_sha256, ...body} = value.descriptor;
    const alteredHash = sha256(canonicalJson({...body, [key]: replacement}));
    let changed = 0;
    const native = nativeWorkflow({...f, nativePlan: () => view}, (p, content) => {
      if (p !== value.relative_path) return content;
      const previous = JSON.stringify(key) + ']:' + JSON.stringify(value.descriptor[key]);
      assert.ok(content.includes(previous)); changed++;
      return content.replace(previous, JSON.stringify(key) + ']:' + JSON.stringify(replacement)).replace(descriptor_sha256, alteredHash);
    });
    assert.equal(changed, 1);
    const {descriptor_sha256: observedHash, ...observedBody} = native.run.descriptor;
    assert.equal(observedHash, sha256(canonicalJson(observedBody)), 'mutation carries a self-consistent digest');
    assert.notEqual(canonicalJson(native.run.descriptor), canonicalJson(value.descriptor), key);
  }
});

test('compiling compensation import substitution is detected even with an unchanged descriptor', t => {
  const f = workflowFixture(t), {plan, value} = binding(f), view = selectReconciledArtifacts(plan);
  let changed = 0;
  const native = nativeWorkflow({...f, nativePlan: () => view}, (p, content) => {
    if (p !== value.provider_path) return content;
    const next = content.replace('operationPerform as forward0', 'operationUndo as forward0').replace('../operations/perform.js', '../operations/undo.js');
    assert.notEqual(next, content); changed++; return next;
  });
  assert.equal(changed, 1);
  assert.deepEqual(native.run.descriptor, value.descriptor, 'descriptor comparison alone does not establish import custody');
  const actual = inventoryGeneratedModule(fs.readFileSync(path.join(native.root, value.provider_path), 'utf8'));
  assert.ok(actual.imports.some(i => i.specifier.endsWith('/undo.js')));
  assert.notDeepEqual(actual.imports, inventoryGeneratedModule(view.artifacts.find(a => a.relative_path === value.provider_path)!.content).imports);
  assert.notEqual(sha256(fs.readFileSync(path.join(native.root, value.provider_path), 'utf8')), value.descriptor.provider_sha256);
});
