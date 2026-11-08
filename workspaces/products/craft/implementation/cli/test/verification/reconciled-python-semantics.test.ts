import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {planCompiledReconciledPythonProject, getPythonCalculationVerificationContext} from '../../src/generation/reconciled-python-project.ts';
import {RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {executeReconciledPythonSemanticVerification as execute} from '../../src/verification/reconciled-python-native.ts';
import {createPythonSemanticControls} from '../../src/verification/reconciled-python-semantic-controls.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

function selected(f: {factories: unknown[]; operations: unknown[]; workflows: unknown[]}) {
  return {schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/package-root', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows};
}
function fixture(t: any) {
  const f = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(f.source), plan = planCompiledReconciledPythonProject(graph, selected(f));
  return {...f, graph, plan, options: {python_executable: '/usr/bin/python3', temporary_parent: f.temp}};
}

test('source-bound Python semantic execution covers integrated nodes without concealing other metatypes', t => {
  const f = fixture(t), before = fs.readdirSync(f.temp), controls = createPythonSemanticControls(f.graph, f.plan);
  assert.equal(controls.rows.length, 21); assert.equal(controls.rows.filter(r => r.state === 'ready').length, 21);
  assert.throws(() => getPythonCalculationVerificationContext(structuredClone(f.plan)), /registered/);
  assert.throws(() => createPythonSemanticControls(f.graph, structuredClone(f.plan)), /registered/);
  assert.equal(canonicalJson(getPythonCalculationVerificationContext(f.plan)).includes('"artifacts"'), false);
  const report = execute(f.graph, f.plan, f.options);
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.residue, null);
  const rows = report.semantic_rows!;
  assert.deepEqual(rows.filter(r => r.result === 'pass').map(r => r.selector).sort(), ['alpha:adjust', 'alpha:allowed', 'alpha:amount-valid', 'alpha:answer', 'alpha:api', 'alpha:choose', 'alpha:find', 'alpha:flow', 'alpha:id-valid', 'alpha:legacy-total', 'alpha:lifecycle', 'alpha:mode', 'alpha:money', 'alpha:order', 'alpha:post', 'alpha:posted', 'alpha:summary', 'alpha:total', 'beta:allowed', 'beta:mode', 'beta:total']);
  assert.equal(rows.filter(r => r.result === 'not_evaluable' && !r.executed).length, 0);
  const check = report.checks.find(c => c.id === 'selected-generator-semantic-controls')!;
  assert.equal(check.result, 'pass'); assert.equal(check.executed, true); assert.equal(check.evidence.passed_nodes, 21);
  assert.deepEqual(fs.readdirSync(f.temp), before);
  t.diagnostic(JSON.stringify({nodes: rows.length, executed: 21, cases: controls.case_count, control_bytes: Buffer.byteLength(canonicalJson(controls)), copied_bytes: report.checks.find(c => c.id === 'isolated-exact-source-replay')!.evidence.bytes}));
});

test('native semantic verifier executes source-derived arithmetic outcomes and rejects false expected results', t => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds-python-semantic-arithmetic-')); t.after(() => fs.rmSync(temp, {recursive: true}));
  const source = path.join(temp, 'source');
  const write = (p: string, v: unknown) => {const file = path.join(source, p); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, JSON.stringify(v));};
  const input = (name: string) => ({op: 'input', name}), literal = (value: string) => ({op: 'literal', value});
  const binary = (op: string, left: unknown = input('left'), right: unknown = input('right')) => ({op, left, right});
  const expressions = {add: binary('add'), subtract: binary('subtract'), multiply: binary('multiply'), floor: binary('divide'), ceil: binary('divide'), reject: binary('divide'),
    intermediate: binary('subtract', binary('add'), input('right')), order: binary('add', binary('subtract', literal('0'), literal('1')), binary('divide', literal('1'), literal('0'))),
    identity: input('left'), constant: literal('18446744073709551615')};
  write('project.json', {schema_version: 'domainspec.project/v1', project_id: 'semantic-arithmetic', features: ['math'], cross_feature_edges: []});
  write('specs/math/feature.json', {schema_version: 'domainspec.feature/v1', feature_id: 'math', nodes: Object.keys(expressions), edges: []});
  for (const [id, expression] of Object.entries(expressions)) {
    const names = id === 'constant' ? [] : ['left', 'right', 'unused'];
    write('specs/math/nodes/' + id + '.json', {schema_version: 'domainspec.node/v1', feature_id: 'math', node_id: id, kind: 'Calculation', body: {description: id, inputs: names,
      typed_contract: {schema_version: 'domainspec.typed-calculation/v2', ontology_calculation: 'FIXTURE-' + id.toUpperCase(), inputs: names.map(name => ({name, type: {kind: 'scalar', name: 'UInt64'}})), result: {kind: 'scalar', name: 'UInt64'}, division_rounding: id === 'floor' || id === 'ceil' ? id : 'reject', expression}}});
  }
  const graph = loadCompiledProjectGraph(source), plan = planCompiledReconciledPythonProject(graph, selected({factories: [], operations: [], workflows: []}));
  const controls = createPythonSemanticControls(graph, plan);
  const errors = new Set(controls.rows.flatMap(r => r.state === 'ready' ? r.cases.flatMap(c => c.expected.kind === 'error' ? [c.expected.message] : []) : []));
  assert.deepEqual([...errors].sort(), ['CALCULATION_DIVIDE_BY_ZERO', 'CALCULATION_INEXACT', 'CALCULATION_INPUT', 'CALCULATION_OVERFLOW', 'CALCULATION_UNDERFLOW']);
  const report = execute(graph, plan, {python_executable: '/usr/bin/python3', temporary_parent: temp});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.checks.find(c => c.id === 'selected-generator-semantic-controls')!.result, 'pass');
  assert.equal(report.result, 'not_evaluable'); assert.equal(report.semantic_rows!.length, 10);
  assert.ok(report.semantic_rows!.every(r => r.result === 'pass' && r.compiling_substitutions === 2));
  const root = path.join(temp, 'mutant-input');
  for (const a of plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const changed = structuredClone(controls), row = changed.rows.find(r => r.state === 'ready')!;
  if (row.state !== 'ready') throw new Error('test requires ready row');
  row.cases[0]!.expected = {kind: 'value', value: 'incorrect'};
  const script = "__name__ = 'observer'\n" + getReconciledSource('python_calculation_observer') + "\n__name__ = '__main__'\n" + getReconciledSource('python_calculation_semantics');
  const result = spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', script], {input: JSON.stringify({root, controls: changed}), encoding: 'utf8', timeout: 30000});
  assert.notEqual(result.status, 0); assert.match(result.stderr, /semantic outcome/);
  t.diagnostic(JSON.stringify({calculations: 10, cases: controls.case_count, compiling_substitutions: 20}));
});

test('semantic observations cannot survive failed workspace cleanup', t => {
  const f = fixture(t), remove = fs.rmSync;
  const mocked = t.mock.method(fs, 'rmSync', ((file: fs.PathLike, options: fs.RmOptions) => {
    if (typeof file === 'string' && path.dirname(file) === f.temp && path.basename(file).startsWith('domainspec-python-verify-')) throw new Error('semantic cleanup failure');
    return remove(file, options);
  }) as typeof fs.rmSync);
  let report: ReturnType<typeof execute>;
  try {report = execute(f.graph, f.plan, f.options);} finally {mocked.mock.restore();}
  assert.equal(report!.result, 'fail'); assert.ok(report!.residue);
  const performed = report!.semantic_rows!.filter(r => r.executed);
  assert.equal(performed.length, 21);
  assert.ok(performed.every(r => r.result === 'not_evaluable' && r.blocked_by?.includes('verification-workspace-cleanup')));
  remove(report!.residue!.workspace_path!, {recursive: true});
});
