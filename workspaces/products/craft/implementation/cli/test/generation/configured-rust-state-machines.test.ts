import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_CONTRACT_SHA256, COMPOSITION_BOUNDARY_VERSION} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustStateMachines, RUST_STATE_MACHINE_CONTRACT_SHA256, RUST_STATE_MACHINE_PROTOCOL, RUST_STATE_MACHINE_SELECTION_VERSION} from '../../src/generation/configured-rust-state-machines.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-state-machine-generation-contract.json');

function fixture(t: any) {
  const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['alpha:order'], bindings: []}, getReconciledSource('field'));
  const selection = {schema_version: RUST_STATE_MACHINE_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots: ['alpha:lifecycle'], boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256};
  const sources = {rust_contract: fs.readFileSync(contractPath, 'utf8'), rule_contract: getReconciledSource('rust_rule')};
  return {...source, graph, boundary, fields, selection, sources, plan: planConfiguredRustStateMachines(graph, boundary, fields, selection, sources)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustStateMachines>, main: string) {
  fs.mkdirSync(path.join(root, 'src'), {recursive: true}); fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-state-machine-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const artifact of plan.artifacts) {const marker = artifact.relative_path.indexOf('/src/'); const file = path.join(root, 'src', artifact.relative_path.slice(marker + 5)); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);}
  const modules = (part: string) => plan.artifacts.filter(row => row.relative_path.includes(`/${part}/`)).map(row => path.basename(row.relative_path, '.rs')).map(value => `pub mod ${value};`).join('');
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod rules{${modules('domain/rules')}}pub mod state_machines{${modules('domain/state_machines')}}}\nfn main(){${main}}\n`);
}

test('Rust State Machine planner emits deterministic pure reducer and exact dependencies', t => {
  const f = fixture(t), repeat = planConfiguredRustStateMachines(f.graph, f.boundary, f.fields, f.selection, f.sources), module = f.plan.modules[0]!, output = f.plan.artifacts.find(row => row.relative_path === module.relative_path)!.content;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_STATE_MACHINE_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_STATE_MACHINE_PROTOCOL); assert.deepEqual(module.rule_dependencies, ['alpha:allowed']); assert.deepEqual(module.event_dependencies, ['alpha:posted']);
  assert.match(output, /pub fn reduce/); assert.match(output, /TransitionOutcome/); assert.doesNotMatch(output, /publish|persist|async fn/);
});

test('generated Rust State Machine preserves guarded transition and no-transition outcomes', t => {
  const f = fixture(t), root = path.join(f.temp, 'state-machine-crate'), module = rustSelectorModule('alpha:lifecycle');
  crate(root, f.plan, `use domain::state_machines::${module}::*;assert_eq!(INITIAL_STATE,State::Draft);match reduce(State::Draft,Trigger::AlphaPosted,&true){TransitionOutcome::Transitioned{state,transition_id,output_intents}=>{assert_eq!(state,State::Posted);assert_eq!(transition_id,"post");assert!(output_intents.is_empty())},_=>panic!()};assert!(matches!(reduce(State::Draft,Trigger::AlphaPosted,&false),TransitionOutcome::Rejected{reason:RejectionReason::Guard,..}));assert!(matches!(reduce(State::Posted,Trigger::AlphaPosted,&true),TransitionOutcome::Rejected{reason:RejectionReason::NoTransition,..}));`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust State Machine is closed over undeclared states', t => {
  const f = fixture(t), root = path.join(f.temp, 'state-machine-compile-fail'), module = rustSelectorModule('alpha:lifecycle'); crate(root, f.plan, `let _=domain::state_machines::${module}::State::Missing;`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /no variant.*named `Missing`/);
});

test('Rust State Machine planner rejects drift, active data and stale selections', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:lifecycle', 'alpha:lifecycle']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustStateMachines(f.graph, f.boundary, f.fields, selection as any, f.sources));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustStateMachines(f.graph, f.boundary, f.fields, f.selection, {...f.sources, rust_contract: f.sources.rust_contract + '\n'}));
});
