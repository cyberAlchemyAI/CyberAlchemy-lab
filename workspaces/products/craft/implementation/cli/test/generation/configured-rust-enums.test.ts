import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustEnums, RUST_ALGEBRAIC_SUM_PROTOCOL, RUST_ENUM_CONTRACT_SHA256, RUST_ENUM_PROTOCOL, RUST_ENUM_SELECTION_VERSION} from '../../src/generation/configured-rust-enums.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-enum-generation-contract.json');

function fixture(t: any) {
  const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source);
  const certificate = createCompiledProjectCertificate(graph);
  const roots = graph.nodes.filter(node => ['Entity', 'Value Object', 'Enum'].includes(node.kind)).map(node => node.selector).sort();
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots, bindings: []}, getReconciledSource('field'));
  const selection = {schema_version: RUST_ENUM_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', field_compilation_sha256: fields.compilation_sha256, roots: ['alpha:answer', 'alpha:mode', 'beta:mode']};
  const contract = fs.readFileSync(contractPath, 'utf8');
  return {...source, graph, fields, selection, contract, plan: planConfiguredRustEnums(fields, selection, contract)};
}

function crate(root: string, source: string, main: string) {
  fs.mkdirSync(path.join(root, 'src'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-enum-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  fs.writeFileSync(path.join(root, 'src/generated.rs'), source);
  fs.writeFileSync(path.join(root, 'src/main.rs'), 'mod generated;\nuse generated::*;\nfn main(){' + main + '}\n');
}

test('Rust Enum planner preserves unit and payload meanings and is deterministic', t => {
  const f = fixture(t), repeat = planConfiguredRustEnums(f.fields, f.selection, f.contract);
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.modules.length, 3); assert.equal(f.plan.contract_sha256, RUST_ENUM_CONTRACT_SHA256);
  const unit = f.plan.modules.find(module => module.selector === 'alpha:mode')!;
  const sum = f.plan.modules.find(module => module.selector === 'alpha:answer')!;
  assert.equal(unit.protocol_id, RUST_ENUM_PROTOCOL); assert.equal(unit.unit, true);
  assert.equal(sum.protocol_id, RUST_ALGEBRAIC_SUM_PROTOCOL); assert.equal(sum.unit, false);
  assert.deepEqual(unit.variants.map(variant => variant.name), ['On', 'Off']);
  assert.equal(sum.variants.find(variant => variant.name === 'Amount')!.native_payload, 'u64');
  assert.match(f.plan.artifacts.find(row => row.relative_path === unit.relative_path)!.content, /derive\(Copy, Clone, Debug, PartialEq, Eq, Hash\)/);
  assert.match(f.plan.artifacts.find(row => row.relative_path === sum.relative_path)!.content, /Amount\(u64\)/);
  assert.ok(f.plan.artifacts.every(row => row.sha256.length === 64 && row.size_bytes === Buffer.byteLength(row.content)));
});

test('generated unit Enum compiles and executes exact wire round trips', t => {
  const f = fixture(t), module = f.plan.modules.find(row => row.selector === 'alpha:mode')!, output = f.plan.artifacts.find(row => row.relative_path === module.relative_path)!;
  const root = path.join(f.temp, 'unit-crate'); crate(root, output.content, 'for wire in ["On","Off"] { let value=parse_mode(wire).unwrap(); assert_eq!(emit_mode(value),wire); } let failure=parse_mode("Other").unwrap_err(); assert_eq!(failure.code,"DOMAINSPEC_ENUM_UNKNOWN_WIRE"); assert_eq!(failure.wire_value,"Other");');
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated payload sum compiles, preserves payload equality, and rejects wrong payload types', t => {
  const f = fixture(t), module = f.plan.modules.find(row => row.selector === 'alpha:answer')!, output = f.plan.artifacts.find(row => row.relative_path === module.relative_path)!;
  const root = path.join(f.temp, 'sum-crate'); crate(root, output.content, 'let left=Answer::Amount(7); let right=Answer::Amount(7); assert_eq!(left,right); assert_eq!(answer_variant(&left),"Amount"); assert_ne!(left,Answer::None);');
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
  fs.writeFileSync(path.join(root, 'src/main.rs'), 'mod generated; use generated::*; fn main(){ let _ = Answer::Amount("7".to_owned()); }\n');
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'});
  assert.notEqual(bad.status, 0); assert.match(bad.stderr, /expected `u64`, found `String`/);
});

test('Rust Enum planner rejects stale, active, duplicate and non-Enum inputs before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:mode', 'alpha:mode']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustEnums(f.fields, selection as any, f.contract));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustEnums(f.fields, f.selection, f.contract + '\n'));
});
