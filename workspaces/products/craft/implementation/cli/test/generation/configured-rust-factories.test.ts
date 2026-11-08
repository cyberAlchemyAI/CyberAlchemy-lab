import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustEnums, RUST_ENUM_SELECTION_VERSION} from '../../src/generation/configured-rust-enums.ts';
import {planConfiguredRustRules, RUST_RULE_SELECTION_VERSION} from '../../src/generation/configured-rust-rules.ts';
import {planConfiguredRustFactories, RUST_ENTITY_PROTOCOL, RUST_FACTORY_CONTRACT_SHA256, RUST_FACTORY_SELECTION_VERSION, RUST_VALUE_OBJECT_PROTOCOL} from '../../src/generation/configured-rust-factories.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const definitionRoot = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation');
const read = (name: string) => fs.readFileSync(path.join(definitionRoot, name), 'utf8');

function fixture(t: any) {
  const authored = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(authored.source), certificate = createCompiledProjectCertificate(graph), module_root = 'relocated/domain';
  const dataRoots = graph.nodes.filter(node => ['Entity', 'Value Object', 'Enum'].includes(node.kind)).map(node => node.selector).sort();
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: dataRoots, bindings: []}, getReconciledSource('field'));
  const ruleRoots = graph.nodes.filter(node => node.kind === 'Rule').map(node => node.selector).sort();
  const rules = planConfiguredRustRules(graph, fields, {schema_version: RUST_RULE_SELECTION_VERSION, language: 'rust', module_root, roots: ruleRoots, field_compilation_sha256: fields.compilation_sha256}, read('rust-rule-generation-contract.json'));
  const enums = planConfiguredRustEnums(fields, {schema_version: RUST_ENUM_SELECTION_VERSION, language: 'rust', module_root, field_compilation_sha256: fields.compilation_sha256, roots: graph.nodes.filter(node => node.kind === 'Enum').map(node => node.selector).sort()}, read('rust-enum-generation-contract.json'));
  const selection = {schema_version: RUST_FACTORY_SELECTION_VERSION, language: 'rust' as const, module_root, field_compilation_sha256: fields.compilation_sha256, factories: authored.factories};
  const contract = read('rust-owned-factory-generation-contract.json'), factories = planConfiguredRustFactories(graph, fields, rules, selection, contract);
  return {...authored, graph, fields, rules, enums, selection, contract, factories, module_root};
}

function writeCrate(f: ReturnType<typeof fixture>, suffix: string, testSource: string) {
  const root = path.join(f.temp, suffix), prefix = f.module_root + '/'; fs.mkdirSync(path.join(root, 'src/domain/types'), {recursive: true}); fs.mkdirSync(path.join(root, 'src/domain/rules'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-factory-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const artifact of [...f.enums.artifacts, ...f.rules.artifacts, ...f.factories.artifacts]) {const relative = artifact.relative_path.slice(prefix.length); const file = path.join(root, relative); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);}
  const typeModules = [...f.enums.modules, ...f.factories.modules].map(row => rustSelectorModule(row.selector)).sort();
  fs.writeFileSync(path.join(root, 'src/domain/types/mod.rs'), typeModules.map(name => `pub mod ${name};`).join('\n') + '\n');
  fs.writeFileSync(path.join(root, 'src/domain/rules/mod.rs'), f.rules.modules.map(row => `pub mod ${rustSelectorModule(row.selector)};`).sort().join('\n') + '\n');
  fs.writeFileSync(path.join(root, 'src/domain/mod.rs'), 'pub mod rules;\npub mod types;\n');
  fs.writeFileSync(path.join(root, 'src/lib.rs'), 'pub mod domain;\n' + testSource);
  return root;
}

test('Rust factory planner keeps Entity identity and Value Object tuple semantics distinct', t => {
  const f = fixture(t); assert.equal(f.factories.modules.length, 2); assert.equal(f.factories.contract_sha256, RUST_FACTORY_CONTRACT_SHA256);
  assert.equal(f.factories.modules.find(row => row.selector === 'alpha:order')!.protocol_id, RUST_ENTITY_PROTOCOL);
  assert.equal(f.factories.modules.find(row => row.selector === 'alpha:money')!.protocol_id, RUST_VALUE_OBJECT_PROTOCOL);
  const entity = f.factories.artifacts.find(row => row.relative_path.includes(rustSelectorModule('alpha:order')))!.content;
  assert.match(entity, /impl PartialEq for Order/); assert.match(entity, /self\.id == other\.id/); assert.doesNotMatch(entity, /derive\(Clone, Debug, PartialEq, Eq, Hash\)\]\npub struct Order \{/);
  const value = f.factories.artifacts.find(row => row.relative_path.includes(rustSelectorModule('alpha:money')))!.content;
  assert.match(value, /derive\(Clone, Debug, PartialEq, Eq, Hash\)/); assert.deepEqual(planConfiguredRustFactories(f.graph, f.fields, f.rules, f.selection, f.contract), f.factories);
});

test('generated Rust factories compile and execute validation, identity-only Eq/Hash, and complete value equality', t => {
  const f = fixture(t), source = `#[cfg(test)] mod tests {\nuse super::domain::types::{f5_alpha_n4_mode::Mode, f5_alpha_n5_money::{create_money_factory, MoneyInput}, f5_alpha_n5_order::{create_order_factory, OrderInput}};\nuse std::hash::{Hash,Hasher};\n#[test] fn semantics(){\n let money=create_money_factory().create(MoneyInput{amount:7}).unwrap(); let other=create_money_factory().create(MoneyInput{amount:8}).unwrap(); assert_ne!(money,other);\n let first=create_order_factory().create(OrderInput{id:"same".to_owned(),amount:7,money:money.clone(),mode:Mode::On}).unwrap();\n let second=create_order_factory().create(OrderInput{id:"same".to_owned(),amount:99,money:other,mode:Mode::Off}).unwrap(); assert_eq!(first,second);\n let mut a=std::collections::hash_map::DefaultHasher::new(); let mut b=std::collections::hash_map::DefaultHasher::new(); first.hash(&mut a); second.hash(&mut b); assert_eq!(a.finish(),b.finish());\n let invalid=create_order_factory().create(OrderInput{id:"".to_owned(),amount:1,money,mode:Mode::On}).unwrap_err(); assert_eq!(invalid.failures,vec!["alpha:id-valid"]);\n}\n}\n`;
  const root = writeCrate(f, 'factory-crate', source); execFileSync(cargo, ['test', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('private snapshots cannot bypass the Rust factory', t => {
  const f = fixture(t), root = writeCrate(f, 'private-crate', ''); fs.mkdirSync(path.join(root, 'tests'), {recursive: true});
  fs.writeFileSync(path.join(root, 'tests/bypass.rs'), 'use rust_factory_check::domain::types::f5_alpha_n5_money::Money; #[test] fn bypass(){ let _ = Money{amount:7}; }\n');
  const result = spawnSync(cargo, ['check', '--quiet', '--offline', '--tests'], {cwd: root, encoding: 'utf8'});
  assert.notEqual(result.status, 0); assert.match(result.stderr, /field `amount` of struct `Money` is private/);
});

test('Rust factory planner rejects incomplete/stale bindings and missing Rule modules', t => {
  const f = fixture(t);
  for (const selection of [{...f.selection, factories: []}, {...f.selection, language: 'python'}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}, {...f.selection, factories: [f.selection.factories[0], f.selection.factories[0]]}]) assert.throws(() => planConfiguredRustFactories(f.graph, f.fields, f.rules, selection as any, f.contract));
  assert.throws(() => planConfiguredRustFactories(f.graph, f.fields, {...f.rules, schema_version: 'forged'} as any, f.selection, f.contract));
  assert.throws(() => planConfiguredRustFactories(f.graph, f.fields, f.rules, f.selection, f.contract + '\n'));
});
