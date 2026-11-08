import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {planReconciledRustProject, RUST_PROJECT_DEFINITION_SHA256} from '../../src/generation/reconciled-rust-project.ts';
import {RECONCILED_RUST_COMPILATION_VERSION, RECONCILED_RUST_PROFILE} from '../../src/generation/reconciled-rust-selection.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
function fixture(t: any) {
  const source = pythonAllTypesFixture(t), selection = {schema_version: RECONCILED_RUST_COMPILATION_VERSION, profile_id: RECONCILED_RUST_PROFILE, language: 'rust' as const, module_root: 'generated/domain', layout_version: RESOLVED_ARTIFACT_LAYOUT, field_bindings: [], factories: source.factories, operations: source.operations, workflows: source.workflows};
  return {...source, selection, plan: planReconciledRustProject(source.source, selection)};
}
function materialize(root: string, plan: ReturnType<typeof planReconciledRustProject>) {for (const artifact of plan.artifacts) {assert.equal(artifact.sha256, sha256(artifact.content)); const file = path.join(root, artifact.relative_path); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);}}

test('reconciled Rust project accounts for all 13 metatypes and plans one deterministic dependency-free crate', t => {
  const f = fixture(t), repeat = planReconciledRustProject(f.source, f.selection); assert.deepEqual(repeat, f.plan); assert.equal(f.plan.definition_sha256, RUST_PROJECT_DEFINITION_SHA256); assert.equal(f.plan.cargo.dependency_count, 0); assert.equal(f.plan.metatype_accounting.length, 13); assert.ok(f.plan.metatype_accounting.every(row => row.count > 0)); assert.equal(f.plan.modules.length, f.plan.node_selectors.length); assert.deepEqual(f.plan.modules.map(row => row.selector).sort(), f.plan.node_selectors); assert.equal(f.plan.authority_effect, 'none'); assert.equal(f.plan.output_effect, 'none');
});

test('complete reconciled Rust project compiles as its generated Cargo library', t => {
  const f = fixture(t), root = path.join(f.temp, 'complete-rust'); materialize(root, f.plan); const crate = path.join(root, f.selection.module_root);
  execFileSync(cargo, ['check', '--quiet', '--offline', '--locked'], {cwd: crate, stdio: 'pipe'});
  assert.ok(fs.existsSync(path.join(crate, 'Cargo.lock'))); assert.match(fs.readFileSync(path.join(crate, 'src/lib.rs'), 'utf8'), /pub mod domain/); assert.match(fs.readFileSync(path.join(crate, 'src/application/mod.rs'), 'utf8'), /workflows/);
});

test('complete Rust project has explicit collision-free module wiring for every selected node', t => {
  const f = fixture(t), paths = f.plan.modules.map(row => row.relative_path); assert.equal(new Set(paths).size, paths.length); for (const module of f.plan.modules) {const artifact = f.plan.artifacts.find(row => row.relative_path === module.relative_path); assert.ok(artifact, module.selector); assert.match(artifact!.content, new RegExp(module.selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));}
  for (const role of ['types', 'rules', 'calculations', 'policies', 'events', 'state_machines']) assert.ok(f.plan.artifacts.some(row => row.relative_path.endsWith(`/domain/${role}/mod.rs`)));
  for (const role of ['queries', 'mappings', 'operations', 'workflows', 'interfaces']) assert.ok(f.plan.artifacts.some(row => row.relative_path.endsWith(`/application/${role}/mod.rs`)));
});

test('reconciled Rust project rejects implicit selection, incomplete bindings and source-contract substitution', t => {
  const f = fixture(t); for (const patch of [{language: 'python'}, {profile_id: 'rust'}, {module_root: '../escape'}, {factories: []}, {operations: []}, {workflows: []}]) assert.throws(() => planReconciledRustProject(f.source, {...f.selection, ...patch})); assert.ok(getReconciledSource('rust_project').includes('exact 13-of-13 accounting'));
});
