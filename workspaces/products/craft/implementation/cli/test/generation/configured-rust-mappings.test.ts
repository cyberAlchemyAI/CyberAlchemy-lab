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
import {planConfiguredRustMappings, RUST_MAPPING_CONTRACT_SHA256, RUST_MAPPING_PROTOCOL, RUST_MAPPING_SELECTION_VERSION, RUST_PUBLIC_MAPPING_PROTOCOL} from '../../src/generation/configured-rust-mappings.ts';
import {renderRustExternalPropertyTypes, rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-mapping-generation-contract.json');

function fixture(t: any) {
  const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['alpha:order'], bindings: []}, getReconciledSource('field'));
  const selection = {schema_version: RUST_MAPPING_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots: ['alpha:summary', 'alpha:adjust'], boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256};
  const sources = {rust_contract: fs.readFileSync(contractPath, 'utf8'), public_mapping_contract: getReconciledSource('public_mapping')};
  return {...source, graph, boundary, fields, selection, sources, plan: planConfiguredRustMappings(graph, boundary, fields, selection, sources)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustMappings>, main: string) {
  const order = rustSelectorModule('alpha:order'), api = rustSelectorModule('alpha:api');
  fs.mkdirSync(path.join(root, 'src/domain/types'), {recursive: true}); fs.mkdirSync(path.join(root, 'src/application/interfaces'), {recursive: true}); fs.mkdirSync(path.join(root, 'src/application/mappings'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-mapping-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  fs.writeFileSync(path.join(root, `src/domain/types/${order}.rs`), '#[derive(Clone,Debug,PartialEq,Eq)] pub struct Order{id:String,amount:u64}\nimpl Order{pub fn new(id:&str,amount:u64)->Self{Self{id:id.to_owned(),amount}} pub fn id(&self)->&String{&self.id} pub fn amount(&self)->&u64{&self.amount}}\n');
  fs.writeFileSync(path.join(root, `src/application/interfaces/${api}.rs`), '#[derive(Clone,Debug,PartialEq,Eq)] pub struct Response{pub id:String,pub total:u64}\n');
  for (const module of plan.modules) fs.writeFileSync(path.join(root, `src/application/mappings/${rustSelectorModule(module.selector)}.rs`), plan.artifacts.find(row => row.relative_path === module.relative_path)!.content);
  const mappingModules = plan.modules.map(module => `pub mod ${rustSelectorModule(module.selector)};`).join('');
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod types{pub mod ${order};}} mod application{pub mod interfaces{pub mod ${api};}pub mod mappings{${mappingModules}}}\nfn main(){${main}}\n`);
}

test('Rust Mapping planner separates internal projection and public Interface result deterministically', t => {
  const f = fixture(t), repeat = planConfiguredRustMappings(f.graph, f.boundary, f.fields, f.selection, f.sources), adjust = f.plan.modules.find(row => row.selector === 'alpha:adjust')!, summary = f.plan.modules.find(row => row.selector === 'alpha:summary')!;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_MAPPING_CONTRACT_SHA256); assert.equal(adjust.protocol_id, RUST_MAPPING_PROTOCOL); assert.equal(summary.protocol_id, RUST_PUBLIC_MAPPING_PROTOCOL);
  assert.equal(adjust.result, 'AdjustProjection'); assert.equal(summary.result, `crate::application::interfaces::${rustSelectorModule('alpha:api')}::Response`); assert.equal(summary.public_total, true);
  for (const output of f.plan.artifacts) {assert.doesNotMatch(output.content, /Calculation|calculate_/); assert.match(output.content, /Clone::clone/);}
});

test('Rust external Mapping projections fully qualify set support types', () => {
  const rendered = renderRustExternalPropertyTypes('alpha:order', [{name: 'tags', type: {kind: 'set', element: {kind: 'scalar', name: 'String'}}}]);
  assert.equal(rendered.get('tags'), 'std::collections::BTreeSet<String>');
});

test('generated Rust Mappings execute explicit internal and public projections without hidden calls', t => {
  const f = fixture(t), root = path.join(f.temp, 'mapping-crate'), adjust = rustSelectorModule('alpha:adjust'), summary = rustSelectorModule('alpha:summary'), order = rustSelectorModule('alpha:order');
  crate(root, f.plan, `use domain::types::${order}::Order;let total=41u64;let patch=application::mappings::${adjust}::adjust(&total);assert_eq!(patch.amount,41);let order=Order::new("order-1",2);let response=application::mappings::${summary}::summary(&order,&total);assert_eq!(response.id,"order-1");assert_eq!(response.total,41);assert_eq!(*order.amount(),2);`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Mapping results cannot masquerade as their target Entity', t => {
  const f = fixture(t), root = path.join(f.temp, 'mapping-compile-fail'), adjust = rustSelectorModule('alpha:adjust'), order = rustSelectorModule('alpha:order');
  crate(root, f.plan, `let total=1u64;let _:domain::types::${order}::Order=application::mappings::${adjust}::adjust(&total);`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /expected `Order`, found `AdjustProjection`/);
});

test('Rust Mapping planner rejects drift, active data, stale inputs and wrong roots before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:adjust', 'alpha:adjust']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustMappings(f.graph, f.boundary, f.fields, selection as any, f.sources));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustMappings(f.graph, f.boundary, f.fields, f.selection, {...f.sources, rust_contract: f.sources.rust_contract + '\n'}));
});
