import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {planCompiledReconciledPythonProject, getPythonFactoryVerificationContext} from '../../src/generation/reconciled-python-project.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {createPythonOwnedValueContext} from '../../src/verification/reconciled-python-value-context.ts';
import {createOwnedValueContext, isWitnessUnavailable} from '../../src/verification/reconciled-value-context.ts';

function fixture(t: any) {
  const f = pythonAllTypesFixture(t);
  const feature = JSON.parse(fs.readFileSync(path.join(f.source, 'specs/alpha/feature.json'), 'utf8'));
  feature.nodes.push('bundle');
  const variants = [
    {name: 'Order', ontology_variant: 'FIXTURE-BUNDLE#Order', payload: {kind: 'named', selector: 'alpha:order'}},
    {name: 'Money', ontology_variant: 'FIXTURE-BUNDLE#Money', payload: {kind: 'named', selector: 'alpha:money'}},
    {name: 'Amounts', ontology_variant: 'FIXTURE-BUNDLE#Amounts', payload: {kind: 'list', element: {kind: 'scalar', name: 'UInt64'}}},
    {name: 'Tags', ontology_variant: 'FIXTURE-BUNDLE#Tags', payload: {kind: 'set', element: {kind: 'scalar', name: 'String'}}},
    {name: 'Maybe', ontology_variant: 'FIXTURE-BUNDLE#Maybe', payload: {kind: 'optional', element: {kind: 'scalar', name: 'String'}}},
    {name: 'None', ontology_variant: 'FIXTURE-BUNDLE#None', payload: null},
  ];
  f.write('specs/alpha/nodes/bundle.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: 'bundle', kind: 'Enum', body: {description: 'Owned record and sum dependencies', values: variants.map(v => v.name), typed_contract: {schema_version: 'domainspec.typed-sum/v1', ontology_node: 'FIXTURE-BUNDLE', variants}}});
  f.write('specs/alpha/feature.json', feature);
  const graph = loadCompiledProjectGraph(f.source);
  const selection = {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'native/package-root', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows};
  return {...f, graph, selection, plan: planCompiledReconciledPythonProject(graph, selection)};
}

test('Python owned witnesses preserve shared source values, validators and negative cases using real native closures', t => {
  const f = fixture(t), before = canonicalJson(f.plan);
  const ts = planCompiledReconciledProject(f.graph, {...publicSelection(), factories: f.factories, operations: f.operations, workflows: f.workflows});
  let samples = 0, negatives = 0;
  for (const node of f.graph.nodes.filter(n => ['Entity', 'Value Object', 'Enum'].includes(n.kind))) {
    const python = createPythonOwnedValueContext(node.selector, f.graph, f.plan, true), reference = createOwnedValueContext(node, f.graph, ts, true);
    const actual = python.samples(python.rootShape), expected = reference.samples(reference.rootShape);
    assert.deepEqual(actual, expected, node.selector);
    assert.deepEqual(python.root.kind === 'Enum' ? [] : python.root.probes, reference.root.kind === 'Enum' ? [] : reference.root.probes);
    for (const sample of actual) {
      assert.deepEqual(python.ref(python.rootShape, sample), reference.ref(reference.rootShape, sample));
      const bad = python.negative(python.rootShape, sample);
      assert.deepEqual(bad, reference.negative(reference.rootShape, sample));
      samples++; negatives += bad.length;
    }
    assert.ok(python.module_paths.length > 0);
    assert.ok(python.module_paths.every(p => p.startsWith('native/package_root/') || p === 'native/__init__.py'));
    assert.ok(python.module_paths.every(p => p.endsWith('.py')));
    assert.ok(python.module_paths.includes(python.root.relative_path));
    for (const d of Object.values(python.dependencies)) assert.ok(python.module_paths.includes(d.relative_path));
    assert.equal(python.module_paths.some(p => /\/(operations|workflows|policies)\//.test(p)), false);
  }
  assert.equal(canonicalJson(f.plan), before);
  const context = getPythonFactoryVerificationContext(f.plan);
  assert.equal(context.length, 2); assert.ok(Object.isFrozen(context));
  assert.equal(canonicalJson(context).includes('"artifacts"'), false);
  assert.equal('resolved' in f.plan, false);
  t.diagnostic(JSON.stringify({nodes: f.graph.nodes.length, value_nodes: 6, samples, negatives, factory_metadata_bytes: Buffer.byteLength(canonicalJson(context))}));
});

test('Python owned witness bindings reject unregistered and mismatched inputs, relocate, and survive source removal', t => {
  const f = fixture(t);
  assert.throws(() => getPythonFactoryVerificationContext(structuredClone(f.plan)), /registered/);
  assert.throws(() => createPythonOwnedValueContext('alpha:bundle', f.graph, structuredClone(f.plan)), /registered/);
  assert.throws(() => createPythonOwnedValueContext('alpha:bundle', structuredClone(f.graph), f.plan), /compiled graph is unvalidated/);
  assert.throws(() => createPythonOwnedValueContext('alpha:missing', f.graph, f.plan), /unknown source selector/);
  assert.throws(() => createPythonOwnedValueContext('alpha:total', f.graph, f.plan), /unsupported named witness/);
  const moved = planCompiledReconciledPythonProject(f.graph, {...f.selection, module_root: 'other/deep-root'});
  const left = createPythonOwnedValueContext('alpha:bundle', f.graph, f.plan), right = createPythonOwnedValueContext('alpha:bundle', f.graph, moved);
  assert.deepEqual(left.samples(left.rootShape), right.samples(right.rootShape));
  assert.notDeepEqual(left.module_paths, right.module_paths);
  const file = path.join(f.source, 'specs/alpha/nodes/id-valid.json'), node = JSON.parse(fs.readFileSync(file, 'utf8'));
  node.body.typed_contract.expression = {op: 'eq', left: {op: 'path', root: 'id', properties: []}, right: {op: 'path', root: 'id', properties: []}};
  f.write('specs/alpha/nodes/id-valid.json', node);
  const changed = loadCompiledProjectGraph(f.source);
  assert.throws(() => createPythonOwnedValueContext('alpha:bundle', changed, f.plan), /graph\/plan identity/);
  fs.renameSync(f.source, f.source + '-removed');
  const retained = createPythonOwnedValueContext('alpha:bundle', f.graph, f.plan);
  assert.deepEqual(retained.samples(retained.rootShape), left.samples(left.rootShape));
});

test('unsatisfied Python factory witnesses remain unavailable, not empty passing value sets', t => {
  const f = fixture(t), file = path.join(f.source, 'specs/alpha/nodes/id-valid.json'), node = JSON.parse(fs.readFileSync(file, 'utf8'));
  node.body.typed_contract.expression = {op: 'not', term: {op: 'eq', left: {op: 'path', root: 'id', properties: []}, right: {op: 'path', root: 'id', properties: []}}};
  f.write('specs/alpha/nodes/id-valid.json', node);
  const graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, f.selection);
  for (const selector of ['alpha:order', 'alpha:bundle']) {
    const ctx = createPythonOwnedValueContext(selector, graph, plan);
    assert.throws(() => ctx.samples(ctx.rootShape), error => isWitnessUnavailable(error) && /no satisfying base factory witness/.test(error.message));
  }
});
