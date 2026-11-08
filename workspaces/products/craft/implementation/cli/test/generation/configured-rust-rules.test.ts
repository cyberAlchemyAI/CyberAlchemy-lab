import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustRules, RUST_RULE_CONTRACT_SHA256, RUST_RULE_PROTOCOL, RUST_RULE_SELECTION_VERSION} from '../../src/generation/configured-rust-rules.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-rule-generation-contract.json');

function fixture(t: any) {
  const authored = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(authored.source), certificate = createCompiledProjectCertificate(graph);
  const dataRoots = graph.nodes.filter(node => ['Entity', 'Value Object', 'Enum'].includes(node.kind)).map(node => node.selector).sort();
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: dataRoots, bindings: []}, getReconciledSource('field'));
  const roots = graph.nodes.filter(node => node.kind === 'Rule').map(node => node.selector).sort();
  const selection = {schema_version: RUST_RULE_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots, field_compilation_sha256: fields.compilation_sha256};
  const contract = fs.readFileSync(contractPath, 'utf8');
  return {...authored, graph, fields, selection, contract, plan: planConfiguredRustRules(graph, fields, selection, contract)};
}

test('Rust Rule planner emits one borrowed pure function per checked Rule', t => {
  const f = fixture(t); assert.equal(f.plan.modules.length, 4); assert.equal(f.plan.protocol_id, RUST_RULE_PROTOCOL); assert.equal(f.plan.contract_sha256, RUST_RULE_CONTRACT_SHA256);
  assert.deepEqual(planConfiguredRustRules(f.graph, f.fields, f.selection, f.contract), f.plan);
  const id = f.plan.artifacts.find(row => row.relative_path.includes(rustSelectorModule('alpha:id-valid')))!.content;
  const allowed = f.plan.artifacts.find(row => row.relative_path.includes(rustSelectorModule('alpha:allowed')))!.content;
  assert.match(id, /pub fn id_valid\(id: &String\) -> bool/); assert.match(id, /&\(String::from\(""\)\) < id/);
  assert.match(allowed, /pub fn allowed\(value: &bool\) -> bool/); assert.doesNotMatch(allowed, /unsafe|std::fs|std::env/);
});

test('generated Rust Rules compile together and execute exact truth cases', t => {
  const f = fixture(t), root = path.join(f.temp, 'rules-crate'), role = path.join(root, 'src/domain/rules'); fs.mkdirSync(role, {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-rule-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const module of f.plan.modules) fs.writeFileSync(path.join(role, rustSelectorModule(module.selector) + '.rs'), f.plan.artifacts.find(row => row.relative_path === module.relative_path)!.content);
  fs.writeFileSync(path.join(role, 'mod.rs'), f.plan.modules.map(module => `pub mod ${rustSelectorModule(module.selector)};`).join('\n') + '\n');
  fs.mkdirSync(path.join(root, 'src/domain'), {recursive: true}); fs.writeFileSync(path.join(root, 'src/domain/mod.rs'), 'pub mod rules;\n');
  fs.writeFileSync(path.join(root, 'src/lib.rs'), 'pub mod domain;\n#[cfg(test)] mod tests { use super::domain::rules; #[test] fn cases(){ assert!(rules::f5_alpha_n7_allowed::allowed(&true)); assert!(!rules::f5_alpha_n7_allowed::allowed(&false)); assert!(rules::f5_alpha_n8_id_valid::id_valid(&"A".to_owned())); assert!(!rules::f5_alpha_n8_id_valid::id_valid(&"".to_owned())); assert!(rules::f5_alpha_n12_amount_valid::amount_valid(&u64::MAX)); } }\n');
  execFileSync(cargo, ['test', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('Rust Rule planner rejects non-Rule, stale and active selections', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:order']}, {...f.selection, roots: []}, {...f.selection, roots: [f.selection.roots[0], f.selection.roots[0]]}, {...f.selection, field_compilation_sha256: null}]) assert.throws(() => planConfiguredRustRules(f.graph, f.fields, selection as any, f.contract));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustRules(f.graph, f.fields, f.selection, f.contract + '\n'));
});
