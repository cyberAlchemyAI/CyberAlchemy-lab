import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_CONTRACT_SHA256, COMPOSITION_BOUNDARY_VERSION} from '../../src/input/composition-boundary.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustInterfaces, RUST_INTERFACE_CONTRACT_SHA256, RUST_INTERFACE_PROTOCOL, RUST_INTERFACE_SELECTION_VERSION} from '../../src/generation/configured-rust-interfaces.ts';
import {NAMED_INTERFACE_DEFINITION_SHA256} from '../../src/typed-backend/interface.ts';
import {INTERFACE_VERSION_POLICY_DEFINITION_SHA256} from '../../src/typed-backend/interface-version-policy.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {sha256} from '../../src/input/source-manifest.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const packagePath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation');
function source(name: string, hash: string): string {const value = fs.readFileSync(path.join(packagePath, name), 'utf8'); assert.equal(getReconciledSource(name === 'named-interface-contract.json' ? 'interface' : 'interface_version'), value); assert.equal(sha256(value), hash); return value;}

function fixture(t: any) {
  const sourceFixture = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(sourceFixture.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const selection = {schema_version: RUST_INTERFACE_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots: ['alpha:api'], boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: null};
  const sources = {rust_contract: fs.readFileSync(path.join(packagePath, 'rust-interface-generation-contract.json'), 'utf8'), interface_contract: source('named-interface-contract.json', NAMED_INTERFACE_DEFINITION_SHA256), version_contract: source('interface-version-policy-contract.json', INTERFACE_VERSION_POLICY_DEFINITION_SHA256)};
  return {...sourceFixture, graph, boundary, selection, sources, plan: planConfiguredRustInterfaces(graph, boundary, null, selection, sources)};
}
function crate(root: string, plan: ReturnType<typeof planConfiguredRustInterfaces>, main: string) {
  fs.mkdirSync(path.join(root, 'src/application/interfaces'), {recursive: true}); fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-interface-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const module of plan.modules) fs.writeFileSync(path.join(root, `src/application/interfaces/${rustSelectorModule(module.selector)}.rs`), plan.artifacts.find(row => row.relative_path === module.relative_path)!.content);
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod application{pub mod interfaces{${plan.modules.map(module => `pub mod ${rustSelectorModule(module.selector)};`).join('')}}}\n${main}\n`);
}

test('Rust Interface planner emits deterministic structural contracts and an explicit provider trait', t => {
  const f = fixture(t), repeat = planConfiguredRustInterfaces(f.graph, f.boundary, null, f.selection, f.sources), module = f.plan.modules[0]!, output = f.plan.artifacts[0]!.content;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_INTERFACE_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_INTERFACE_PROTOCOL); assert.deepEqual(module.operation_dependencies, ['alpha:find']); assert.match(output, /pub trait ApiProvider/); assert.match(output, /async fn find/); assert.doesNotMatch(output, /server|transport|dispatch/i);
});

test('generated Rust Interface preserves public values and exact backward version behavior', t => {
  const f = fixture(t), root = path.join(f.temp, 'interface-crate'), module = rustSelectorModule('alpha:api');
  crate(root, f.plan, `use application::interfaces::${module}::*;fn main(){let value=Response{id:"order-1".to_owned(),total:7};assert_eq!(value.total,7);assert!(accepts_consumer_version("1.0.0"));assert!(!accepts_consumer_version("1.0.1"));assert!(!accepts_consumer_version("1.00.0"));assert!(!accepts_consumer_version("2.0.0"));}`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Interface rejects providers outside its explicit trait', t => {
  const f = fixture(t), root = path.join(f.temp, 'interface-compile-fail'), module = rustSelectorModule('alpha:api');
  crate(root, f.plan, `use application::interfaces::${module}::*;struct Missing;async fn call<P:ApiProvider>(provider:&P){let _=provider.find(String::new()).await;}fn main(){let _=call(&Missing);}`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /trait bound `Missing: .*ApiProvider` is not satisfied/);
});

test('Rust Interface planner rejects drift, active data, stale selections and non-Interface roots', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: []}, {...f.selection, roots: ['alpha:api', 'alpha:api']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustInterfaces(f.graph, f.boundary, null, selection as any, f.sources));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustInterfaces(f.graph, f.boundary, null, f.selection, {...f.sources, rust_contract: f.sources.rust_contract + '\n'}));
});
