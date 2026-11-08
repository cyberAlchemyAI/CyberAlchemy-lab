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
import {planConfiguredRustQueries, RUST_QUERY_CONTRACT_SHA256, RUST_QUERY_PROTOCOL, RUST_QUERY_SELECTION_VERSION} from '../../src/generation/configured-rust-queries.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-query-generation-contract.json');

function fixture(t: any, optional = false) {
  const source = pythonAllTypesFixture(t), featurePath = path.join(source.source, 'specs/alpha/feature.json'), orderPath = path.join(source.source, 'specs/alpha/nodes/order.json');
  const feature = JSON.parse(fs.readFileSync(featurePath, 'utf8')), order = JSON.parse(fs.readFileSync(orderPath, 'utf8'));
  order.body.fields.push('label'); order.body.typed_contract.properties.push({name: 'label', type: {kind: 'scalar', name: 'String'}, identity: false, cardinality: 'one', meaning: 'label', ontology_property: 'FIXTURE-ORDER#label'}); source.write('specs/alpha/nodes/order.json', order);
  feature.nodes.push('ranked'); feature.edges.push('ranked-reads-order');
  source.write('specs/alpha/nodes/ranked.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: 'ranked', kind: 'Query', body: {description: 'ranked', reads: ['alpha:order'], typed_contract: {schema_version: 'domainspec.typed-query/v1', ontology_query: 'FIXTURE-RANKED-ORDER', source: 'alpha:order', inputs: [{name: 'minimum', type: {kind: 'scalar', name: 'UInt64'}}], filter: {op: 'gte', left: {kind: 'field', name: 'amount'}, right: {kind: 'parameter', name: 'minimum'}}, projection: ['id', 'label', 'amount'], order_by: {field: 'label', direction: 'asc'}, limit: 2}}});
  source.write('specs/alpha/edges/ranked-reads-order.json', {schema_version: 'domainspec.edge/v1', feature_id: 'alpha', edge_id: 'ranked-reads-order', relationship: 'reads', source_node_id: 'ranked', target_node_id: 'order', scope: 'feature'});
  fs.writeFileSync(featurePath, JSON.stringify(feature, null, 2) + '\n');
  if (optional) {
    const file = 'specs/alpha/nodes/ranked.json';
    const query = JSON.parse(fs.readFileSync(path.join(source.source, file), 'utf8'));
    Object.assign(query.body.typed_contract, {schema_version:'domainspec.typed-query/v2',result_cardinality:'optional',limit:null});
    source.write(file, query);
  }
  const graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['alpha:order'], bindings: []}, getReconciledSource('field'));
  const selection = {schema_version: RUST_QUERY_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots: ['alpha:ranked'], boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256};
  const contract = fs.readFileSync(contractPath, 'utf8');
  return {...source, graph, boundary, fields, selection, contract, plan: planConfiguredRustQueries(boundary, fields, selection, contract)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustQueries>, main: string) {
  const module = plan.modules[0]!, output = plan.artifacts[0]!, queryModule = rustSelectorModule(module.selector), typeModule = rustSelectorModule(module.source);
  fs.mkdirSync(path.join(root, 'src/domain/types'), {recursive: true}); fs.mkdirSync(path.join(root, 'src/application/queries'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-query-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  fs.writeFileSync(path.join(root, `src/domain/types/${typeModule}.rs`), '#[derive(Clone,Debug,PartialEq,Eq)] pub struct Order{id:String,label:String,amount:u64}\nimpl Order{pub fn new(id:&str,label:&str,amount:u64)->Self{Self{id:id.to_owned(),label:label.to_owned(),amount}} pub fn id(&self)->&String{&self.id} pub fn label(&self)->&String{&self.label} pub fn amount(&self)->&u64{&self.amount}}\n');
  fs.writeFileSync(path.join(root, `src/application/queries/${queryModule}.rs`), output.content);
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod types{pub mod ${typeModule};}} mod application{pub mod queries{pub mod ${queryModule};}}\n${main}\n`);
}

const blockOn = `fn block_on<F:std::future::Future>(future:F)->F::Output{struct Noop;impl std::task::Wake for Noop{fn wake(self:std::sync::Arc<Self>){} }let w=std::task::Waker::from(std::sync::Arc::new(Noop));let mut c=std::task::Context::from_waker(&w);let mut f=Box::pin(future);loop{match f.as_mut().poll(&mut c){std::task::Poll::Ready(v)=>return v,std::task::Poll::Pending=>std::thread::yield_now()}}}`;

test('Rust Query planner binds the checked Entity and is deterministic', t => {
  const f = fixture(t), repeat = planConfiguredRustQueries(f.boundary, f.fields, f.selection, f.contract), module = f.plan.modules[0]!, output = f.plan.artifacts[0]!;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_QUERY_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_QUERY_PROTOCOL); assert.equal(module.source, 'alpha:order');
  assert.deepEqual(module.projection.map(field => field.name), ['id', 'label', 'amount']); assert.match(output.content, /async fn read_ranked/); assert.match(output.content, /encode_utf16/); assert.match(output.content, /selected\.truncate\(2\)/);
});

test('generated Rust Query executes its async reader, filter, UTF-16 order, limit and projection', t => {
  const f = fixture(t), root = path.join(f.temp, 'query-crate'), q = rustSelectorModule('alpha:ranked'), ty = rustSelectorModule('alpha:order');
  crate(root, f.plan, `use application::queries::${q}::*; use domain::types::${ty}::Order; struct Reader; impl ${f.plan.modules[0]!.reader} for Reader { async fn read_ranked(&self,minimum:&u64)->Result<Vec<Order>,QueryError>{assert_eq!(*minimum,2);Ok(vec![Order::new("private","\\u{e000}",3),Order::new("low","0",1),Order::new("emoji","😀",4),Order::new("ascii","a",2)])}} ${blockOn} fn main(){let rows=block_on(ranked(&Reader,&2)).unwrap();assert_eq!(rows.len(),2);assert_eq!(rows[0].id,"ascii");assert_eq!(rows[1].id,"emoji");assert_eq!(rows[1].amount,4);}`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Query rejects an undeclared reader at compile time', t => {
  const f = fixture(t), root = path.join(f.temp, 'query-compile-fail'), q = rustSelectorModule('alpha:ranked');
  crate(root, f.plan, `use application::queries::${q}::ranked; struct Missing; ${blockOn} fn main(){let _=block_on(ranked(&Missing,&2));}`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /trait bound `Missing: RankedReader` is not satisfied/);
});

test('optional Rust Query distinguishes no match, one match, cardinality failure and reader failure', t => {
  const f = fixture(t, true), root = path.join(f.temp, 'optional-query'), q = rustSelectorModule('alpha:ranked'), ty = rustSelectorModule('alpha:order');
  assert.equal(f.plan.modules[0]!.protocol_id, 'rust.bound-query/v2-candidate');
  crate(root, f.plan, `use application::queries::${q}::*; use domain::types::${ty}::Order;
struct Reader(u8); impl ${f.plan.modules[0]!.reader} for Reader {
async fn read_ranked(&self,_minimum:&u64)->Result<Vec<Order>,QueryError>{
if self.0==3{return Err(QueryError::READ);} let mut rows=vec![Order::new("low","low",1)];
for _ in 0..self.0 {rows.push(Order::new("max","max",u64::MAX));} Ok(rows)}}
${blockOn}
fn main(){assert_eq!(DOMAINSPEC_PROTOCOL_ID,"rust.bound-query/v2-candidate");
assert!(block_on(ranked(&Reader(0),&2)).unwrap().is_none());
let one=block_on(ranked(&Reader(1),&2)).unwrap().unwrap();assert_eq!(one.amount,u64::MAX);
assert_eq!(block_on(ranked(&Reader(2),&2)).unwrap_err().code,"QUERY_CARDINALITY");
assert_eq!(block_on(ranked(&Reader(3),&2)).unwrap_err(),QueryError::READ);}`);
  execFileSync(cargo, ['run','--quiet','--offline'], {cwd:root,stdio:'pipe'});
});

test('Rust Query planner rejects drift, active data, stale inputs and wrong roots before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:ranked', 'alpha:ranked']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustQueries(f.boundary, f.fields, selection as any, f.contract));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustQueries(f.boundary, f.fields, f.selection, f.contract + '\n'));
});
