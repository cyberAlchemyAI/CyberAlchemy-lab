import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_CONTRACT_SHA256, COMPOSITION_BOUNDARY_VERSION} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings} from '../../src/typed-operation/action-bindings.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustOperations, RUST_OPERATION_CONTRACT_SHA256, RUST_OPERATION_PROTOCOL, RUST_OPERATION_SELECTION_VERSION} from '../../src/generation/configured-rust-operations.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-operation-generation-contract.json');

function fixture(t: any, qualifiedSlot = false) {
  const source = pythonAllTypesFixture(t);
  if (qualifiedSlot) {
    const operationPath = path.join(source.source, 'specs/alpha/nodes/post.json');
    const operationNode = JSON.parse(fs.readFileSync(operationPath, 'utf8'));
    operationNode.body.effects = ['alpha:posted'];
    fs.writeFileSync(operationPath, JSON.stringify(operationNode, null, 2) + '\n');
    source.operations[0].events[0].slot = 'alpha:posted';
  }
  const graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['alpha:order'], bindings: []}, getReconciledSource('field'));
  const action = compileOperationActionBindings(graph, boundary, fields, source.operations[0], getReconciledSource('operation_action'));
  const selection = {schema_version: RUST_OPERATION_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, actions: [action], factories: source.factories};
  const sources = {rust_contract: fs.readFileSync(contractPath, 'utf8'), rule_contract: getReconciledSource('rust_rule'), factory_contract: getReconciledSource('rust_factory'), event_contract: fs.readFileSync(path.join(path.dirname(contractPath), 'rust-event-generation-contract.json'), 'utf8')};
  return {...source, graph, boundary, fields, action, selection, sources, plan: planConfiguredRustOperations(graph, boundary, fields, selection, sources)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustOperations>, main: string) {
  fs.mkdirSync(path.join(root, 'src'), {recursive: true}); fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-operation-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const artifact of plan.artifacts) {const marker = artifact.relative_path.indexOf('/src/'); if (marker < 0) continue; const file = path.join(root, 'src', artifact.relative_path.slice(marker + 5)); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);}
  const typeModules = plan.artifacts.filter(row => row.relative_path.includes('/domain/types/')).map(row => path.basename(row.relative_path, '.rs'));
  const mode = rustSelectorModule('alpha:mode'); if (!typeModules.includes(mode)) {fs.mkdirSync(path.join(root, 'src/domain/types'), {recursive: true}); fs.writeFileSync(path.join(root, `src/domain/types/${mode}.rs`), '#[derive(Copy,Clone,Debug,PartialEq,Eq,Hash)] pub enum Mode{On,Off}\n'); typeModules.push(mode);}
  const modules = (part: string) => plan.artifacts.filter(row => row.relative_path.includes(`/${part}/`)).map(row => path.basename(row.relative_path, '.rs')).filter((value, index, rows) => rows.indexOf(value) === index).map(value => `pub mod ${value};`).join('');
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod types{${typeModules.map(value => `pub mod ${value};`).join('')}}pub mod rules{${modules('domain/rules')}}pub mod events{${modules('domain/events')}}}mod application{pub mod operations{${modules('application/operations')}}}\n${main}\n`);
}

const blockOn = `fn block_on<F:std::future::Future>(future:F)->F::Output{struct Noop;impl std::task::Wake for Noop{fn wake(self:std::sync::Arc<Self>){} }let w=std::task::Waker::from(std::sync::Arc::new(Noop));let mut c=std::task::Context::from_waker(&w);let mut f=Box::pin(future);loop{match f.as_mut().poll(&mut c){std::task::Poll::Ready(v)=>return v,std::task::Poll::Pending=>std::thread::yield_now()}}}`;

test('Rust Operation planner binds checked action, Rule, factory and Event closures deterministically', t => {
  const f = fixture(t), repeat = planConfiguredRustOperations(f.graph, f.boundary, f.fields, f.selection, f.sources), module = f.plan.modules[0]!, output = f.plan.artifacts.find(row => row.relative_path === module.relative_path)!;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_OPERATION_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_OPERATION_PROTOCOL); assert.equal(module.action_sha256, f.action.action_sha256); assert.deepEqual(module.event_dependencies, ['alpha:posted']); assert.deepEqual(module.factory_dependencies, ['alpha:order']);
  assert.match(output.content, /async fn commit/); assert.match(output.content, /COMMIT_UNCERTAIN/); assert.match(output.content, /create_posted/); assert.match(f.plan.artifacts.find(row => row.relative_path.includes('/domain/types/') && row.content.includes('pub struct Order '))!.content, /pub fn validate/);
});

test('generated Rust Operation commits one typed batch and preserves all terminal commit dispositions', t => {
  const f = fixture(t), root = path.join(f.temp, 'operation-crate'), operation = rustSelectorModule('alpha:post'), order = rustSelectorModule('alpha:order'), money = rustSelectorModule('alpha:money'), mode = rustSelectorModule('alpha:mode'), posted = rustSelectorModule('alpha:posted');
  crate(root, f.plan, `use application::operations::${operation} as op;use domain::types::${order} as o;use domain::types::${money} as m;use domain::events::${posted} as e;use std::rc::Rc;use std::cell::Cell;#[derive(Clone)]struct Tx{receipt:Option<op::CommitReceipt>,commits:Rc<Cell<u32>>,rollbacks:Rc<Cell<u32>>}impl op::PostTransaction for Tx{async fn rollback(&mut self)->Result<(),op::OperationPortError>{self.rollbacks.set(self.rollbacks.get()+1);Ok(())}async fn commit(&mut self,batch:op::PostBatch)->Result<op::CommitReceipt,op::OperationPortError>{self.commits.set(self.commits.get()+1);assert_eq!(batch.notice.target,"alpha:posted");assert_eq!(batch.notice.value.event_type(),"posted");self.receipt.ok_or(op::OperationPortError)}}struct Store{tx:Tx}impl op::PostStore for Store{type Transaction=Tx;async fn begin(&self)->Result<Tx,op::OperationPortError>{Ok(self.tx.clone())}}${blockOn}fn event(id:&str)->e::PostedInput{e::PostedInput{occurrence:e::PostedOccurrenceInput{event_id:id.to_owned()},occurred_at:"2026-09-15T00:00:00Z".to_owned(),payload:e::PostedPayloadInput{}}}fn main(){let money=m::create_money_factory().create(m::MoneyInput{amount:1}).unwrap();let order=o::create_order_factory().create(o::OrderInput{id:"order-1".to_owned(),amount:1,money,mode:domain::types::${mode}::Mode::On}).unwrap();for (index,receipt) in [Some(op::CommitReceipt::Committed),Some(op::CommitReceipt::Rejected),Some(op::CommitReceipt::Indeterminate),None].into_iter().enumerate(){let commits=Rc::new(Cell::new(0));let rollbacks=Rc::new(Cell::new(0));let store=Store{tx:Tx{receipt,commits:commits.clone(),rollbacks:rollbacks.clone()}};let result=block_on(op::post(&order,event(&format!("event-{index}")),&store));assert_eq!(commits.get(),1);assert_eq!(rollbacks.get(),0);match (index,result){(0,op::PostOutcome::Committed(value))=>assert_eq!(value.id(),order.id()),(1,op::PostOutcome::Rejected{code,..})=>assert_eq!(code,"COMMIT_REJECTED"),(2,op::PostOutcome::Indeterminate{code,..})=>assert_eq!(code,"COMMIT_INDETERMINATE"),(3,op::PostOutcome::Indeterminate{code,..})=>assert_eq!(code,"COMMIT_UNCERTAIN"),_=>panic!("wrong outcome")}}}`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Operation preserves qualified semantic slots through collision-resistant native names', t => {
  const f = fixture(t, true);
  const module = f.plan.artifacts.find(row => row.relative_path.includes('/application/operations/'))!;
  assert.match(module.content, /pub f5_alpha_n6_posted: EventIntent/);
  assert.match(module.content, /f5_alpha_n6_posted: EventIntent \{ target: "alpha:posted"/);
});

test('generated Rust Operation rejects stores that do not implement its explicit port', t => {
  const f = fixture(t), root = path.join(f.temp, 'operation-compile-fail'), operation = rustSelectorModule('alpha:post');
  crate(root, f.plan, `${blockOn}struct Missing;fn main(){let order=todo!();let event=todo!();let _=block_on(application::operations::${operation}::post(order,event,&Missing));}`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /trait bound `Missing: PostStore` is not satisfied/);
});

test('Rust Operation planner rejects drift, active data, cloned actions and stale inputs before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'actions', {enumerable: true, get() {reads++; return f.selection.actions;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, actions: [structuredClone(f.action)]}, {...f.selection, actions: [f.action, f.action]}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}, {...f.selection, field_compilation_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustOperations(f.graph, f.boundary, f.fields, selection as any, f.sources));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustOperations(f.graph, f.boundary, f.fields, f.selection, {...f.sources, rust_contract: f.sources.rust_contract + '\n'}));
});
