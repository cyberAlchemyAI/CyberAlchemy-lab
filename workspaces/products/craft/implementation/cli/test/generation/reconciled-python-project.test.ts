import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledPythonProject, planReconciledPythonProject, selectReconciledPythonArtifacts, assertReconciledPythonProjectPlan} from '../../src/generation/reconciled-python-project.ts';
import {decodeReconciledPythonSelection, RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

function fixture(t: any) {
  const f = pythonAllTypesFixture(t);
  const selection = {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'commerce', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows};
  return {...f, selection, graph: loadCompiledProjectGraph(f.source)};
}
const kinds = ['Calculation', 'Entity', 'Enum', 'Event', 'Interface', 'Mapping', 'Operation', 'Policy', 'Query', 'Rule', 'State Machine', 'Value Object', 'Workflow'];

test('Python whole-project plan joins all13 metatypes without changing checked source or duplicating shared artifacts', t => {
  const f = fixture(t), before = canonicalJson(f.graph);
  const plan = planCompiledReconciledPythonProject(f.graph, f.selection);
  t.diagnostic(JSON.stringify({nodes: plan.node_selectors.length, generator_requests: plan.requests.length, artifacts: plan.artifacts.length, generated_bytes: plan.artifacts.reduce((n, a) => n + a.size_bytes, 0)}));
  assert.deepEqual(planReconciledPythonProject(f.source, f.selection), plan);
  assert.deepEqual(planCompiledReconciledPythonProject(f.graph, f.selection), plan);
  assert.equal(canonicalJson(f.graph), before); assertReconciledPythonProjectPlan(plan);
  assert.deepEqual([...new Set(plan.modules.flatMap(m => m.metatypes))].sort(), kinds);
  assert.deepEqual([...new Set(plan.modules.flatMap(m => m.qualified_selectors))].sort(), f.graph.nodes.map(n => n.selector).sort());
  assert.equal(new Set(plan.artifacts.map(a => a.relative_path)).size, plan.artifacts.length);
  for (const a of plan.artifacts) {assert.equal(a.sha256, sha256(a.content)); assert.equal(a.size_bytes, Buffer.byteLength(a.content));}
  const {plan_sha256, ...body} = plan; assert.equal(plan_sha256, sha256(canonicalJson(body)));
  fs.renameSync(f.source, f.source + '-moved'); assert.deepEqual(planCompiledReconciledPythonProject(f.graph, f.selection), plan);
});

test('all13 joined Python package imports natively; node projection retains providers and required initializers', t => {
  const f = fixture(t);
  for (const module_root of ['commerce', 'relocated/package-root']) {
    const plan = planCompiledReconciledPythonProject(f.graph, {...f.selection, module_root});
    const target = path.join(f.temp, module_root.replaceAll('/', '-'));
    for (const a of plan.artifacts) {const file = path.join(target, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
    const result = spawnSync('/usr/bin/python3', ['-I', '-B', path.join(import.meta.dirname, 'reconciled-python-runtime.py')], {encoding: 'utf8', input: JSON.stringify({root: target, plan}), maxBuffer: 4 * 1024 * 1024});
    assert.equal(result.status, 0, result.stdout + result.stderr);
    t.diagnostic(module_root + ': ' + result.stdout.trim());
    const projected = selectReconciledPythonArtifacts(plan, ['alpha:summary']);
    assert.ok(projected.artifacts.some(a => a.relative_path.endsWith('/_providers/summary.py')));
    assert.ok(projected.artifacts.some(a => a.relative_path.endsWith('/interfaces/api.py')));
    assert.ok(!projected.artifacts.some(a => a.relative_path.endsWith('/workflows/flow.py')));
    const nodeRoot = path.join(target, 'node-output');
    for (const a of projected.artifacts) {const file = path.join(nodeRoot, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
    const code = 'import sys, importlib\nsys.path.insert(0, sys.argv[1])\nfor name in sys.argv[2:]: importlib.import_module(name)\n';
    const native = spawnSync('/usr/bin/python3', ['-I', '-B', '-c', code, nodeRoot, ...projected.modules.map(m => m.relative_path.slice(0, -3).replaceAll('/', '.'))], {encoding: 'utf8'});
    assert.equal(native.status, 0, native.stderr);
  }
});

test('Python project selection rejects forged identities, incomplete authored coverage and wrong language before source reads', t => {
  const f = fixture(t);
  for (const patch of [{language: 'typescript'}, {profile_id: 'legacy'}, {value_profile: 'number'}, {module_root: '../outside'}, {module_root: 'root\n'}, {operations: []}, {factories: []}, {workflows: []}, {factories: [...f.factories, f.factories[0]]}]) assert.throws(() => planCompiledReconciledPythonProject(f.graph, {...f.selection, ...patch}));
  assert.throws(() => planCompiledReconciledPythonProject(structuredClone(f.graph), f.selection));
  assert.throws(() => planReconciledPythonProject('/missing-source', {...f.selection, language: 'rust'}), /explicit Python/);
  const plan = planCompiledReconciledPythonProject(f.graph, f.selection);
  assert.throws(() => selectReconciledPythonArtifacts(structuredClone(plan)), /registered Python/);
  for (const roots of [[], ['alpha:missing'], ['alpha:summary', 'alpha:summary']]) assert.throws(() => selectReconciledPythonArtifacts(plan, roots));
  let effects = 0; const active = {...f.selection}; Object.defineProperty(active, 'factories', {enumerable: true, get() {effects++; return [];}});
  assert.throws(() => decodeReconciledPythonSelection(active)); assert.equal(effects, 0);
});

test('joined native behavior rejects compiling provider substitutions without trusting plan hashes', t => {
  const f = fixture(t), plan = planCompiledReconciledPythonProject(f.graph, f.selection);
  const target = path.join(f.temp, 'mutants');
  const controls = [
    {suffix: '/alpha/src/domain/calculations/_providers/total.py', change: (s: string) => s.replace('18446744073709551615', '7')},
    {suffix: '/alpha/src/application/mappings/_providers/summary.py', change: (s: string) => s.replace('v1 = p1', 'v1 = 7')},
    {suffix: '/alpha/src/domain/policies/_providers/choose.py', change: (s: string) => s.replace('return "alpha:post"', 'return "alpha:total"')},
  ];
  for (const control of controls) {
    let changed = false;
    for (const a of plan.artifacts) {
      let content = a.content;
      if (a.relative_path.endsWith(control.suffix)) {content = control.change(content); assert.notEqual(content, a.content, 'mutation must match'); changed = true;}
      const file = path.join(target, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, content);
    }
    assert.ok(changed, control.suffix);
    const result = spawnSync('/usr/bin/python3', ['-I', '-B', path.join(import.meta.dirname, 'reconciled-python-runtime.py')], {encoding: 'utf8', input: JSON.stringify({root: target, plan}), maxBuffer: 4 * 1024 * 1024});
    assert.notEqual(result.status, 0, 'JOIN_MUTANT_SURVIVED:' + control.suffix); assert.match(result.stderr, /AssertionError/);
  }
});
