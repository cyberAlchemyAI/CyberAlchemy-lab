import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {spawnSync} from 'node:child_process';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {decodeReconciledPythonSelection, RECONCILED_PYTHON_COMPILATION_VERSION, RECONCILED_PYTHON_PROFILE} from '../../src/generation/reconciled-python-selection.ts';
import {planCompiledReconciledPythonProject} from '../../src/generation/reconciled-python-project.ts';
import {decodeSelectedReconciledCompilation, planSelectedReconciledProject, planCompiledSelectedReconciledProject, selectSelectedReconciledArtifacts, PYTHON_CLI_EXTENSION_SHA256} from '../../src/generation/selected-reconciled-project.ts';
import {planProjectBuild, planCompiledProjectBuild, publishProjectBuild, verifyProjectBuild} from '../../src/generation/project-build.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {planProjectInstantiation} from '../../src/generation/project-instantiation.ts';
import {publishInstantiation} from '../../src/generation/publish-instantiation.ts';
import {publishReconciledProject, verifyReconciledProject, createReconciledOutputReceipt, readReconciledCompilationSelection} from '../../src/generation/reconciled-output.ts';
import {APPLICATION_LAYOUT} from '../../src/generation/output-layout.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {RECONCILED_COMPILATION_VERSION, RECONCILED_TYPESCRIPT_PROFILE, planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {runCli} from '../../src/cli/main.ts';

function fixture(t: any) {
  const f = pythonAllTypesFixture(t);
  const selection = decodeReconciledPythonSelection({schema_version: RECONCILED_PYTHON_COMPILATION_VERSION, profile_id: RECONCILED_PYTHON_PROFILE, language: 'python', module_root: 'relocated/package-root', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: f.factories, operations: f.operations, workflows: f.workflows});
  const file = path.join(f.temp, 'selection.json'); fs.writeFileSync(file, JSON.stringify(selection));
  return {...f, selection, file, graph: loadCompiledProjectGraph(f.source)};
}
function cli(args: string[]) {
  const out: string[] = [], err: string[] = [];
  const code = runCli(args, {stdout: s => out.push(s), stderr: s => err.push(s)});
  return {code, out: out.length ? JSON.parse(out.join('')) : null, error: err.join('')};
}
function args(f: ReturnType<typeof fixture>, command: string, target: string, node?: string) {
  return [command, f.source, '--compilation-selection', f.file, command === 'instantiate-project' ? '--languages' : '--language', 'python', '--target-root', target, ...(node ? ['--node', node] : [])];
}
function native(root: string, plan: ReturnType<typeof planCompiledReconciledPythonProject>) {
  const result = spawnSync('/usr/bin/python3', ['-I', '-B', path.join(import.meta.dirname, 'reconciled-python-runtime.py')], {input: JSON.stringify({root, plan}), encoding: 'utf8', timeout: 30000});
  assert.equal(result.status, 0, result.stderr); assert.equal(JSON.parse(result.stdout).joined_behavior, true);
}

test('Python public source/snapshot builds share exact plans, receipts and native behavior in both layouts', t => {
  const f = fixture(t), baseline = canonicalJson(f.graph), direct = planCompiledReconciledPythonProject(f.graph, f.selection);
  assert.deepEqual(readReconciledCompilationSelection(f.file), f.selection);
  assert.deepEqual(planCompiledSelectedReconciledProject(f.graph, f.selection), direct);
  for (const layout of [undefined, APPLICATION_LAYOUT.id]) {
    const plan = planProjectBuild(f.source, 'python', undefined, layout, f.selection);
    assert.deepEqual(plan, planCompiledProjectBuild(f.graph, 'python', undefined, layout, f.selection));
    assert.deepEqual(plan.project, direct);
    const target = path.join(f.temp, layout ? 'application' : 'plain');
    const published = publishProjectBuild(plan, target);
    assert.deepEqual(published.receipt, plan.receipt);
    assert.equal(plan.language_extension_sha256, PYTHON_CLI_EXTENSION_SHA256);
    assert.equal(plan.receipt.language_extension_sha256, PYTHON_CLI_EXTENSION_SHA256);
    assert.equal(verifyProjectBuild(f.source, 'python', target, undefined, layout, f.selection).result, 'pass');
    for (const key of ['native_compilation', 'semantic_observation', 'formal_verification'] as const) assert.equal(plan.receipt[key], 'not-performed');
    const prefix = layout ? 'domain/python/src/' : '';
    assert.deepEqual(plan.artifacts.map(a => a.relative_path), direct.artifacts.map(a => prefix + a.relative_path));
    native(path.join(target, prefix), direct);
    const changed = path.join(target, plan.artifacts.find(a => a.size_bytes > 0)!.relative_path);
    fs.appendFileSync(changed, '\n# modified\n');
    assert.equal(verifyReconciledProject(direct, target, null, layout).result, 'fail');
  }
  assert.equal(canonicalJson(loadCompiledProjectGraph(f.source)), baseline);
  fs.renameSync(f.source, f.source + '-moved');
  assert.deepEqual(planCompiledProjectBuild(f.graph, 'python', undefined, undefined, f.selection).project, direct);
});

test('Python real CLI build and public project/node commands retain native import closure and currentness scope', t => {
  const f = fixture(t), plan = planCompiledReconciledPythonProject(f.graph, f.selection);
  const target = path.join(f.temp, 'real-cli');
  const raw = spawnSync(process.execPath, [...process.execArgv, path.resolve(import.meta.dirname, '../../src/cli/main.ts'), ...args(f, 'build', target)], {encoding: 'utf8', timeout: 30000});
  assert.equal(raw.status, 0, raw.stderr); assert.equal(JSON.parse(raw.stdout).result, 'pass'); native(target, plan);
  assert.equal(cli(args(f, 'verify', target)).code, 0);
  const project = cli(args(f, 'instantiate-project', path.join(f.temp, 'project')));
  assert.equal(project.code, 0, project.error); assert.deepEqual(project.out.receipt, createReconciledOutputReceipt(plan));
  const nodeTarget = path.join(f.temp, 'node'), result = cli(args(f, 'instantiate', nodeTarget, 'alpha:summary'));
  assert.equal(result.code, 0, result.error);
  const node = planInstantiation('alpha:summary', 'python', null, undefined, plan), apiTarget = path.join(f.temp, 'api-node');
  assert.deepEqual(publishInstantiation(node, apiTarget).receipt, result.out.receipt);
  assert.equal(cli(args(f, 'verify', nodeTarget, 'alpha:summary')).code, 0);
  assert.equal(cli(args(f, 'verify', nodeTarget)).code, 1);
  const view = selectSelectedReconciledArtifacts(plan, ['alpha:summary']);
  assert.ok(view.artifacts.some(a => a.relative_path.includes('/interfaces/')));
  assert.ok(!view.artifacts.some(a => a.relative_path.includes('/workflows/')));
  const imported = spawnSync('/usr/bin/python3', ['-I', '-B', '-c', 'import sys, importlib\nsys.path.insert(0, sys.argv[1])\nfor name in sys.argv[2:]: importlib.import_module(name)', nodeTarget, ...view.modules.map(m => m.relative_path.slice(0, -3).replaceAll('/', '.'))], {encoding: 'utf8', timeout: 30000});
  assert.equal(imported.status, 0, imported.stderr);
  const before = fs.readFileSync(path.join(nodeTarget, result.out.receipt_path));
  assert.notEqual(cli(args(f, 'instantiate', nodeTarget, 'alpha:summary')).code, 0);
  assert.deepEqual(fs.readFileSync(path.join(nodeTarget, result.out.receipt_path)), before);
});

test('Python stronger verify-project executes complete verification for application layout', t => {
  const f = fixture(t), plan = planCompiledReconciledPythonProject(f.graph, f.selection);
  const lean = process.env.DOMAINSPEC_LEAN; assert.ok(lean && path.isAbsolute(lean), 'explicit installed Lean required');
  const target = path.join(f.temp, 'stronger-application'); publishReconciledProject(plan, target, null, APPLICATION_LAYOUT.id);
  const stronger = cli(['verify-project', f.source, '--compilation-selection', f.file, '--target-root', target, '--python-executable', '/usr/bin/python3', '--temporary-parent', f.temp, '--lean-executable', fs.realpathSync(lean), '--output-layout', APPLICATION_LAYOUT.id]);
  assert.equal(stronger.code, 0, stronger.error); assert.equal(stronger.out.result, 'pass');
  assert.equal(stronger.out.schema_version, 'domainspec.python-complete-verification/v1-candidate');
  assert.equal(stronger.out.formal_verification, 'finite-structural-references');
  assert.ok(stronger.out.checks.every((check: any) => check.result === 'pass' && check.executed));
});

test('Python dispatch rejects unsupported selections, forged plans and conflicting options before effects', t => {
  const f = fixture(t), plan = planCompiledReconciledPythonProject(f.graph, f.selection), target = path.join(f.temp, 'absent');
  for (const patch of [{language: 'rust'}, {profile_id: RECONCILED_TYPESCRIPT_PROFILE}, {value_profile: EXACT_UINT64_PROFILE}, {schema_version: RECONCILED_COMPILATION_VERSION}]) assert.throws(() => planSelectedReconciledProject('/missing-source', {...f.selection, ...patch}), error => !String(error).includes('ENOENT'));
  assert.throws(() => planProjectBuild('/missing-source', 'typescript', undefined, undefined, f.selection), /conflicts/);
  assert.throws(() => planProjectBuild('/missing-source', 'python', EXACT_UINT64_PROFILE, undefined, f.selection), /conflicts/);
  assert.throws(() => planProjectInstantiation('/missing-source', ['python', 'typescript'], f.selection), /single selected language/);
  assert.throws(() => planInstantiation('alpha:summary', 'python', null, undefined, structuredClone(plan)), /registered/);
  let effects = 0;
  const active = {...f.selection}; Object.defineProperty(active, 'language', {enumerable: true, get() {effects++; return 'python';}});
  assert.throws(() => decodeSelectedReconciledCompilation(active)); assert.equal(effects, 0);
  assert.notEqual(cli(args(f, 'build', target).map(s => s === 'python' ? 'typescript' : s)).code, 0);
  assert.notEqual(cli([...args(f, 'verify', target, 'alpha:summary'), '--output-layout', APPLICATION_LAYOUT.id]).code, 0);
  const wrongTools = cli(['verify-project', f.source, '--compilation-selection', f.file, '--target-root', target, '--typescript-root', '/missing-ts', '--node-type-root', '/missing-types', '--lean-executable', '/missing-lean']);
  assert.notEqual(wrongTools.code, 0); assert.match(wrongTools.error, /unique known valued options/);
  assert.equal(fs.existsSync(target), false);
  assert.deepEqual(fs.readdirSync(f.temp).filter(p => p.startsWith('.domainspec-')), []);
});

test('language dispatch preserves existing TypeScript plan and receipt bytes', t => {
  const f = fixture(t);
  const selection = {...f.selection, schema_version: RECONCILED_COMPILATION_VERSION, profile_id: RECONCILED_TYPESCRIPT_PROFILE, language: 'typescript', value_profile: EXACT_UINT64_PROFILE, module_root: 'application'};
  const direct = planCompiledReconciledProject(f.graph, selection), selected = planCompiledSelectedReconciledProject(f.graph, selection);
  assert.deepEqual(selected, direct);
  assert.equal(Object.hasOwn(createReconciledOutputReceipt(selected), 'language_extension_sha256'), false);
  assert.deepEqual(createReconciledOutputReceipt(selected), createReconciledOutputReceipt(direct));
});
