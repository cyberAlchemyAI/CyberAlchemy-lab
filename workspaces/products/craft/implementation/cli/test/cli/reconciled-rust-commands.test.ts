import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {runCli, loadCompiledProjectGraph, planCompiledReconciledRustProject, verifyCompiledReconciledRustProject, RECONCILED_RUST_COMPILATION_VERSION, RECONCILED_RUST_PROFILE} from '../../src/index.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {pythonAllTypesFixture} from '../generation/reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
function prepared(t: any) {
  const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source);
  const selection = {schema_version: RECONCILED_RUST_COMPILATION_VERSION, profile_id: RECONCILED_RUST_PROFILE, language: 'rust' as const, module_root: 'generated/domain', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: source.factories, operations: source.operations, workflows: source.workflows};
  const selectionFile = path.join(source.temp, 'rust-selection.json'); fs.writeFileSync(selectionFile, JSON.stringify(selection));
  return {...source, graph, selection, selectionFile, plan: planCompiledReconciledRustProject(graph, selection)};
}
function cli(args: string[]) {const out: string[] = [], error: string[] = []; const code = runCli(args, {stdout: value => out.push(value), stderr: value => error.push(value)}); return {code, out: out.length ? JSON.parse(out.join('')) : null, error: error.length ? JSON.parse(error.join('')) : null};}
function command(f: ReturnType<typeof prepared>, name: string, target: string, extra: string[] = []) {return [name, f.source, '--language', 'rust', '--target-root', target, ...extra, '--compilation-selection', f.selectionFile];}

test('Rust selected build, artifact verification and stronger Cargo verification share one exact plan', t => {
  const f = prepared(t), target = path.join(f.temp, 'rust-build');
  const built = cli(command(f, 'build', target)); assert.equal(built.code, 0, JSON.stringify(built.error)); assert.equal(built.out.result, 'pass');
  const current = cli(command(f, 'verify', target)); assert.equal(current.code, 0, JSON.stringify(current.error)); assert.equal(current.out.verification_scope, 'artifact-currentness');
  const verified = cli(['verify-project', f.source, '--target-root', target, '--cargo-executable', cargo, '--temporary-parent', f.temp, '--compilation-selection', f.selectionFile]);
  assert.equal(verified.code, 0, JSON.stringify(verified.error)); assert.equal(verified.out.result, 'pass'); assert.deepEqual(verified.out.checks.map((row: any) => row.id), ['exact-output-currentness', 'source-and-module-shape', 'cargo-metadata', 'cargo-check']);
  assert.equal(verified.out.project_plan_sha256, f.plan.plan_sha256); assert.deepEqual(fs.readdirSync(f.temp).filter(name => name.startsWith('domainspec-rust-verify-')), []);
  const api = verifyCompiledReconciledRustProject(f.graph, f.selection, {cargo_executable: cargo, temporary_parent: f.temp, target_root: target}); assert.equal(api.result, 'pass'); assert.equal(api.project_plan_sha256, f.plan.plan_sha256);
});

test('Rust project/node entry points retain the whole checked Cargo crate and reject wrong verification tools', t => {
  const f = prepared(t), projectTarget = path.join(f.temp, 'rust-project'), nodeTarget = path.join(f.temp, 'rust-node');
  const project = cli(['instantiate-project', f.source, '--languages', 'rust', '--target-root', projectTarget, '--compilation-selection', f.selectionFile]); assert.equal(project.code, 0, JSON.stringify(project.error));
  const node = cli(['instantiate', f.source, '--language', 'rust', '--node', 'alpha:flow', '--target-root', nodeTarget, '--compilation-selection', f.selectionFile]); assert.equal(node.code, 0, JSON.stringify(node.error));
  assert.equal(fs.readFileSync(path.join(projectTarget, 'generated/domain/Cargo.toml'), 'utf8'), fs.readFileSync(path.join(nodeTarget, 'generated/domain/Cargo.toml'), 'utf8'));
  assert.equal(cli(command(f, 'verify', nodeTarget, ['--node', 'alpha:flow'])).code, 0);
  const missing = cli(['verify-project', f.source, '--target-root', projectTarget, '--compilation-selection', f.selectionFile]); assert.notEqual(missing.code, 0);
  const wrong = cli(['verify-project', f.source, '--target-root', projectTarget, '--typescript-root', f.temp, '--node-type-root', f.temp, '--lean-executable', cargo, '--compilation-selection', f.selectionFile]); assert.notEqual(wrong.code, 0);
  assert.deepEqual(fs.readdirSync(f.temp).filter(name => name.startsWith('domainspec-rust-verify-')), []);
});

test('Rust application layout publishes and verifies the same crate under the selected envelope', t => {
  const f = prepared(t), target = path.join(f.temp, 'rust-application'), layout = 'domainspec.application-layout/v1';
  const built = cli(command(f, 'build', target, ['--output-layout', layout])); assert.equal(built.code, 0, JSON.stringify(built.error));
  assert.ok(fs.existsSync(path.join(target, 'domain/rust/src/generated/domain/Cargo.toml')));
  const verified = cli(['verify-project', f.source, '--target-root', target, '--cargo-executable', cargo, '--temporary-parent', f.temp, '--output-layout', layout, '--compilation-selection', f.selectionFile]);
  assert.equal(verified.code, 0, JSON.stringify(verified.error)); assert.equal(verified.out.result, 'pass');
});

test('the actual CLI process builds and verifies the selected Rust crate', t => {
  const f = prepared(t), target = path.join(f.temp, 'rust-process'), main = path.resolve(import.meta.dirname, '../../src/cli/main.ts');
  const invoke = (args: string[]) => JSON.parse(execFileSync(process.execPath, [...process.execArgv, main, ...args], {encoding: 'utf8'}));
  const built = invoke(command(f, 'build', target)); assert.equal(built.result, 'pass');
  const verified = invoke(['verify-project', f.source, '--target-root', target, '--cargo-executable', cargo, '--temporary-parent', f.temp, '--compilation-selection', f.selectionFile]);
  assert.equal(verified.result, 'pass'); assert.equal(verified.project_plan_sha256, f.plan.plan_sha256); assert.deepEqual(fs.readdirSync(f.temp).filter(name => name.startsWith('domainspec-rust-verify-')), []);
});
