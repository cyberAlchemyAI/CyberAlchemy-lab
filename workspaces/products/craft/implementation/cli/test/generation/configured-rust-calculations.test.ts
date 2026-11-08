import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planConfiguredRustCalculations, RUST_CALCULATION_CONTRACT_SHA256, RUST_CALCULATION_PROTOCOL, RUST_CALCULATION_SELECTION_VERSION} from '../../src/generation/configured-rust-calculations.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-calculation-generation-contract.json');
const scalar = {kind: 'scalar', name: 'UInt64'};

function fixture(t: any) {
  const source = pythonAllTypesFixture(t), featurePath = path.join(source.source, 'specs/alpha/feature.json');
  const feature = JSON.parse(fs.readFileSync(featurePath, 'utf8'));
  const expression = (op: string) => ({op, left: {op: 'input', name: 'left'}, right: {op: 'input', name: 'right'}});
  for (const [id, op, rounding] of [['add', 'add', 'reject'], ['subtract', 'subtract', 'reject'], ['divide', 'divide', 'reject'], ['ceil', 'divide', 'ceil']] as const) {
    feature.nodes.push(id);
    source.write(`specs/alpha/nodes/${id}.json`, {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: id, kind: 'Calculation', body: {description: id, inputs: ['left', 'right'], typed_contract: {schema_version: 'domainspec.typed-calculation/v2', ontology_calculation: `FIXTURE-${id.toUpperCase()}-TOTAL`, inputs: [{name: 'left', type: scalar}, {name: 'right', type: scalar}], result: scalar, division_rounding: rounding, expression: expression(op)}}});
  }
  fs.writeFileSync(featurePath, JSON.stringify(feature, null, 2) + '\n');
  const graph = loadCompiledProjectGraph(source.source), roots = ['alpha:add', 'alpha:ceil', 'alpha:divide', 'alpha:legacy-total', 'alpha:subtract', 'alpha:total'];
  const selection = {schema_version: RUST_CALCULATION_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots};
  const contract = fs.readFileSync(contractPath, 'utf8');
  return {...source, graph, selection, contract, plan: planConfiguredRustCalculations(graph, selection, contract)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustCalculations>, main: string) {
  fs.mkdirSync(path.join(root, 'src/generated'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-calculation-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  const modules: string[] = [];
  for (const module of plan.modules) {
    const name = rustSelectorModule(module.selector), output = plan.artifacts.find(row => row.relative_path === module.relative_path)!;
    fs.writeFileSync(path.join(root, `src/generated/${name}.rs`), output.content); modules.push(`pub mod ${name};`);
  }
  fs.writeFileSync(path.join(root, 'src/generated/mod.rs'), modules.join('\n') + '\n');
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod generated;\nfn main(){${main}}\n`);
}

test('Rust Calculation planner is deterministic and preserves exact checked semantics', t => {
  const f = fixture(t), repeat = planConfiguredRustCalculations(f.graph, f.selection, f.contract);
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.modules.length, 6); assert.equal(f.plan.contract_sha256, RUST_CALCULATION_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_CALCULATION_PROTOCOL);
  assert.deepEqual(f.plan.selection.roots, [...f.selection.roots].sort());
  const total = f.plan.modules.find(row => row.selector === 'alpha:total')!, output = f.plan.artifacts.find(row => row.relative_path === total.relative_path)!;
  assert.match(output.content, /Ok\(18446744073709551615u64\)/); assert.match(output.content, /Result<u64, CalculationError>/);
  assert.ok(f.plan.artifacts.every(row => row.sha256.length === 64 && row.size_bytes === Buffer.byteLength(row.content)));
});

test('generated Rust Calculations compile and execute success and every arithmetic failure', t => {
  const f = fixture(t), root = path.join(f.temp, 'calculation-crate');
  const module = (id: string) => `generated::${rustSelectorModule('alpha:' + id)}::${id}`;
  crate(root, f.plan, `let max=u64::MAX; let one=1u64; assert_eq!(${module('add')}(&max,&one).unwrap_err().code(),"DOMAINSPEC_CALCULATION_OVERFLOW"); assert_eq!(${module('subtract')}(&one,&max).unwrap_err().code(),"DOMAINSPEC_CALCULATION_UNDERFLOW"); let zero=0u64; assert_eq!(${module('divide')}(&max,&zero).unwrap_err().code(),"DOMAINSPEC_CALCULATION_DIVIDE_BY_ZERO"); let five=5u64; let two=2u64; assert_eq!(${module('divide')}(&five,&two).unwrap_err().code(),"DOMAINSPEC_CALCULATION_INEXACT"); assert_eq!(${module('ceil')}(&five,&two).unwrap(),3); assert_eq!(generated::${rustSelectorModule('alpha:total')}::total().unwrap(),u64::MAX);`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Calculation signatures reject non-UInt64 calls at compile time', t => {
  const f = fixture(t), root = path.join(f.temp, 'calculation-compile-fail');
  crate(root, f.plan, `let bad=String::from("1"); let one=1u64; let _=generated::${rustSelectorModule('alpha:add')}::add(&bad,&one);`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'});
  assert.notEqual(bad.status, 0); assert.match(bad.stderr, /expected `&u64`, found `&String`/);
});

test('Rust Calculation planner rejects drift, active data, duplicate and wrong-kind roots before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:add', 'alpha:add']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}]) assert.throws(() => planConfiguredRustCalculations(f.graph, selection as any, f.contract));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustCalculations(f.graph, f.selection, f.contract + '\n'));
});
