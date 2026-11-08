import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {decodeReconciledPythonSelection, RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {publishReconciledProject} from '../../src/generation/reconciled-output.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {executeReconciledPythonNativeVerification as execute, executeReconciledPythonVerification as executeComplete, renderPythonNativeVerification, validatePythonNativeVerificationOptions, validatePythonVerificationOptions} from '../../src/verification/reconciled-python-native.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

function fixture(t: any) {
  const f = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(f.source);
  const selection = decodeReconciledPythonSelection({schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/package-root', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  return {...f, graph, plan: planCompiledReconciledPythonProject(graph, selection), options: {python_executable: '/usr/bin/python3', temporary_parent: f.temp}};
}

test('native verifier compiles, observes and imports all13 Python types with exact replay and cleanup, without a false full pass', t => {
  const f = fixture(t), target = path.join(f.temp, 'output');
  publishReconciledProject(f.plan, target);
  const before = fs.readdirSync(f.temp), report = execute(f.graph, f.plan, {...f.options, target_root: target});
  assert.equal(report.native_stage_result, 'pass', JSON.stringify(report.checks));
  assert.equal(report.result, 'not_evaluable');
  assert.equal(report.residue, null);
  const check = (id: string) => report.checks.find(c => c.id === id)!;
  for (const id of ['source-currentness', 'isolated-exact-source-replay', 'strict-native-compilation', 'native-package-imports', 'independent-module-surface-observation', 'exact-output-currentness', 'toolchain-currentness', 'verification-workspace-currentness', 'verification-workspace-cleanup']) assert.equal(check(id).result, 'pass', id);
  assert.equal(check('native-package-imports').evidence.module_count, f.plan.modules.length);
  for (const id of ['selected-generator-semantic-controls', 'cross-generator-behavior', 'source-and-selection-preservation', 'successor-formalization-currentness', 'lean-structural-kernel']) {assert.equal(check(id).result, 'not_evaluable'); assert.equal(check(id).executed, false);}
  assert.deepEqual(fs.readdirSync(f.temp), before);
  assert.equal(renderPythonNativeVerification(report), canonicalJson(report) + '\n');
  assert.throws(() => renderPythonNativeVerification(structuredClone(report)), /registered/);
  t.diagnostic(JSON.stringify({modules: f.plan.modules.length, metatypes: new Set(f.plan.modules.flatMap(m => m.metatypes)).size, workspace: check('isolated-exact-source-replay').evidence, report_bytes: Buffer.byteLength(canonicalJson(report))}));
});

test('complete Python verifier joins all native semantics, shared-source outcomes and finite Lean preservation', t => {
  const lean = process.env.DOMAINSPEC_LEAN;
  assert.ok(lean && path.isAbsolute(lean), 'explicit installed Lean required');
  const f = fixture(t), target = path.join(f.temp, 'complete-output');
  publishReconciledProject(f.plan, target);
  const before = fs.readdirSync(f.temp), options = {...f.options, target_root: target, lean_executable: fs.realpathSync(lean)};
  assert.deepEqual(validatePythonVerificationOptions(options), options);
  const report = executeComplete(f.graph, f.plan, options);
  assert.equal(report.schema_version, 'domainspec.python-complete-verification/v1-candidate');
  assert.equal(report.result, 'pass', JSON.stringify(report.checks.filter(c => c.result !== 'pass')));
  assert.equal(report.native_stage_result, 'pass'); assert.equal(report.residue, null);
  assert.equal(report.semantic_observation, 'bounded-per-node'); assert.equal(report.formal_verification, 'finite-structural-references');
  assert.equal(report.semantic_rows.length, f.graph.nodes.length); assert.ok(report.semantic_rows.every(row => row.result === 'pass' && row.executed));
  assert.ok(report.checks.every(check => check.result === 'pass' && check.executed));
  const cross = report.checks.find(c => c.id === 'cross-generator-behavior')!;
  assert.equal(cross.evidence.scope, 'python-native-versus-shared-source-outcomes');
  assert.equal(report.checks.find(c => c.id === 'source-and-selection-preservation')!.result, 'pass');
  assert.equal(report.checks.find(c => c.id === 'successor-formalization-currentness')!.result, 'pass');
  assert.equal(report.checks.find(c => c.id === 'lean-structural-kernel')!.result, 'pass');
  assert.deepEqual(fs.readdirSync(f.temp), before);

  const rejected = executeComplete(f.graph, f.plan, {...options, lean_executable: '/bin/false'});
  assert.equal(rejected.result, 'fail'); assert.equal(rejected.residue, null);
  assert.equal(rejected.checks.find(c => c.id === 'lean-structural-kernel')!.result, 'fail');
  assert.equal(rejected.checks.find(c => c.id === 'verification-workspace-cleanup')!.result, 'pass');
  assert.throws(() => validatePythonVerificationOptions({...f.options, lean_executable: lean}), /closed options/);
});

test('native verification preserves failures, rejects stale inputs and cleans failed interpreter workspaces', t => {
  const f = fixture(t), before = fs.readdirSync(f.temp);
  const failed = execute(f.graph, f.plan, {...f.options, python_executable: '/bin/false'});
  assert.equal(failed.result, 'fail'); assert.equal(failed.native_stage_result, 'fail');
  assert.equal(failed.checks.find(c => c.id === 'strict-native-compilation')!.result, 'fail');
  assert.equal(failed.checks.find(c => c.id === 'verification-workspace-cleanup')!.result, 'pass');
  assert.deepEqual(fs.readdirSync(f.temp), before);
  const file = path.join(f.source, 'specs/beta/nodes/total.json'); fs.appendFileSync(file, '\n');
  const stale = execute(f.graph, f.plan, f.options);
  assert.equal(stale.result, 'fail');
  assert.equal(stale.checks.find(c => c.id === 'source-currentness')!.result, 'fail');
  assert.equal(stale.checks.find(c => c.id === 'native-package-imports')!.executed, false);
  assert.deepEqual(fs.readdirSync(f.temp), before);
  assert.throws(() => execute(f.graph, structuredClone(f.plan), f.options), /registered/);
  for (const patch of [{python_executable: 'python3'}, {temporary_parent: '/tmp/../tmp'}, {extra: true}, {output_layout: 'domainspec.application-layout/v1'}]) assert.throws(() => validatePythonNativeVerificationOptions({...f.options, ...patch}));
  let reads = 0; const active = {...f.options}; Object.defineProperty(active, 'python_executable', {enumerable: true, get() {reads++; return '/usr/bin/python3';}});
  assert.throws(() => validatePythonNativeVerificationOptions(active)); assert.equal(reads, 0);
});

test('independent native observer rejects compiling inventory substitutions even with fresh artifact hashes', t => {
  const f = fixture(t), root = path.join(f.temp, 'observer');
  for (const a of f.plan.artifacts) {const file = path.join(root, a.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, a.content);}
  const observer = getReconciledSource('python_native_observer');
  const run = (modules: unknown) => spawnSync('/usr/bin/python3', ['-I', '-S', '-B', '-c', observer], {input: JSON.stringify({root, modules}), encoding: 'utf8', timeout: 30000});
  const modified: any = structuredClone(f.plan.modules);
  const row = modified.find((m: any) => m.relative_path.endsWith('/alpha/src/domain/calculations/total.py'));
  const file = path.join(root, row.relative_path), original = fs.readFileSync(file, 'utf8');
  fs.writeFileSync(file, original + '\nextra_binding = 1\n'); row.sha256 = sha256(fs.readFileSync(file));
  const changed = run(modified); assert.notEqual(changed.status, 0); assert.match(changed.stderr, /native binding inventory/);
  fs.writeFileSync(file, original);
  const imports: any = structuredClone(f.plan.modules);
  const owner = imports.find((m: any) => m.imports.some((i: any) => i.dependency !== 'package-initializer'));
  owner.imports = owner.imports.filter((i: any) => i.dependency === 'package-initializer');
  const omitted = run(imports); assert.notEqual(omitted.status, 0); assert.match(omitted.stderr, /native import inventory/);
});

test('cleanup failure invalidates otherwise passing native observations and exposes exact residue', t => {
  const f = fixture(t), remove = fs.rmSync;
  const mocked = t.mock.method(fs, 'rmSync', ((file: fs.PathLike, options: fs.RmOptions) => {
    if (typeof file === 'string' && path.dirname(file) === f.temp && path.basename(file).startsWith('domainspec-python-verify-')) throw Object.assign(new Error('test cleanup failure'), {code: 'EACCES'});
    return remove(file, options);
  }) as typeof fs.rmSync);
  let report: ReturnType<typeof execute>;
  try {report = execute(f.graph, f.plan, f.options);} finally {mocked.mock.restore();}
  assert.equal(report!.result, 'fail'); assert.equal(report!.native_stage_result, 'fail');
  const cleanup = report!.checks.find(c => c.id === 'verification-workspace-cleanup')!;
  assert.equal(cleanup.result, 'fail'); assert.match(cleanup.reason, /test cleanup failure/);
  for (const id of ['strict-native-compilation', 'independent-module-surface-observation', 'native-package-imports']) {
    const observed = report!.checks.find(c => c.id === id)!;
    assert.equal(observed.executed, true); assert.equal(observed.result, 'not_evaluable');
    assert.ok(observed.blocked_by.includes('verification-workspace-cleanup'));
  }
  const residue = fs.readdirSync(f.temp).filter(n => n.startsWith('domainspec-python-verify-'));
  assert.equal(residue.length, 1);
  assert.deepEqual(report!.residue, {workspace_path: path.join(f.temp, residue[0]!), cleanup_required: true});
  remove(path.join(f.temp, residue[0]!), {recursive: true});
});
