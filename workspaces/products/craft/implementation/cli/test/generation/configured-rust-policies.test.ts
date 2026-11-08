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
import {planConfiguredRustPolicies, RUST_POLICY_CONTRACT_SHA256, RUST_POLICY_PROTOCOL, RUST_POLICY_SELECTION_VERSION} from '../../src/generation/configured-rust-policies.ts';
import {RUST_RULE_SELECTION_VERSION} from '../../src/generation/configured-rust-rules.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-policy-generation-contract.json');

function fixture(t: any) {
  const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['alpha:order'], bindings: []}, getReconciledSource('field'));
  const selection = {schema_version: RUST_POLICY_SELECTION_VERSION, language: 'rust' as const, rule_selection: RUST_RULE_SELECTION_VERSION, module_root: 'relocated/domain', roots: ['alpha:choose'], boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256};
  const sources = {rust_contract: fs.readFileSync(contractPath, 'utf8'), rule_contract: getReconciledSource('rust_rule')};
  return {...source, graph, boundary, fields, selection, sources, plan: planConfiguredRustPolicies(graph, boundary, fields, selection, sources)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustPolicies>, main: string) {
  fs.mkdirSync(path.join(root, 'src/domain/rules'), {recursive: true}); fs.mkdirSync(path.join(root, 'src/domain/policies'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-policy-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const artifact of plan.artifacts) {
    const relative = artifact.relative_path.includes('/rules/') ? `src/domain/rules/${path.basename(artifact.relative_path)}` : `src/domain/policies/${path.basename(artifact.relative_path)}`;
    fs.writeFileSync(path.join(root, relative), artifact.content);
  }
  const rules = plan.rule_dependencies.map(rule => `pub mod ${rustSelectorModule(rule.selector)};`).join(''), policies = plan.modules.map(policy => `pub mod ${rustSelectorModule(policy.selector)};`).join('');
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod rules{${rules}}pub mod policies{${policies}}}\nfn main(){${main}}\n`);
}

test('Rust Policy planner binds separate Rules and typed strategy identities deterministically', t => {
  const f = fixture(t), repeat = planConfiguredRustPolicies(f.graph, f.boundary, f.fields, f.selection, f.sources), module = f.plan.modules[0]!, output = f.plan.artifacts.find(row => row.relative_path === module.relative_path)!;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_POLICY_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_POLICY_PROTOCOL); assert.deepEqual(module.targets, ['alpha:post', 'alpha:total']);
  assert.equal(f.plan.rule_dependencies.length, 1); assert.equal(f.plan.rule_dependencies[0]!.selector, 'alpha:allowed'); assert.match(output.content, /crate::domain::rules::/); assert.doesNotMatch(output.content, /application::operations|domain::calculations/);
});

test('generated Rust Policy executes declared Rule branches and returns inert exact target identities', t => {
  const f = fixture(t), root = path.join(f.temp, 'policy-crate'), policy = rustSelectorModule('alpha:choose');
  crate(root, f.plan, `use domain::policies::${policy}::choose;assert_eq!(choose(&true).selector(),"alpha:post");assert_eq!(choose(&false).selector(),"alpha:total");`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Policy strategy cannot be treated as an executable target', t => {
  const f = fixture(t), root = path.join(f.temp, 'policy-compile-fail'), policy = rustSelectorModule('alpha:choose');
  crate(root, f.plan, `let target=domain::policies::${policy}::choose(&true);target();`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /expected function, found `ChooseStrategy`/);
});

test('Rust Policy planner rejects drift, active data, stale inputs and wrong roots before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, rule_selection: 'future'}, {...f.selection, roots: ['alpha:choose', 'alpha:choose']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustPolicies(f.graph, f.boundary, f.fields, selection as any, f.sources));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustPolicies(f.graph, f.boundary, f.fields, f.selection, {...f.sources, rust_contract: f.sources.rust_contract + '\n'}));
});
