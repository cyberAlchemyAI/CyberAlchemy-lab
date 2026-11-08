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
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../../src/typed-operation/workflow-bindings.ts';
import {selectWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_CONTRACT_SHA256, WORKFLOW_RECOVERY_POLICY_VERSION} from '../../src/typed-operation/workflow-recovery.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustWorkflow, RUST_WORKFLOW_CONTRACT_SHA256, RUST_WORKFLOW_PROTOCOL, RUST_WORKFLOW_SELECTION_VERSION} from '../../src/generation/configured-rust-workflows.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo', packagePath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation');
const read = (name: string) => fs.readFileSync(path.join(packagePath, name), 'utf8');
function fixture(t: any) {
  const source = pythonAllTypesFixture(t), graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: ['alpha:order'], bindings: []}, getReconciledSource('field'));
  const action = compileOperationActionBindings(graph, boundary, fields, source.operations[0], getReconciledSource('operation_action'));
  const authored = source.workflows[0], workflow = compileWorkflowBindings(graph, boundary, fields, [action], {schema_version: WORKFLOW_BINDINGS_VERSION, selector: authored.selector, inputs: authored.inputs, event_inputs: authored.event_inputs, steps: authored.steps.map((step: any) => ({...step, action_sha256: action.action_sha256})), compensations: [], result: authored.result}, getReconciledSource('workflow_binding'));
  const recoverySource = read('workflow-recovery-policy-contract.json'), policy = selectWorkflowRecoveryPolicy(workflow, {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256, contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, dependency_semantics: 'needed-compensations-only', tie_break: 'reverse-completion'}, recoverySource);
  const selection = {schema_version: RUST_WORKFLOW_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', workflow, policy, actions: [action], factories: source.factories};
  const sources = {rust_contract: read('rust-workflow-generation-contract.json'), outcome_contract: read('workflow-outcome-contract.json'), recovery_contract: recoverySource, operations: {rust_contract: read('rust-operation-generation-contract.json'), rule_contract: getReconciledSource('rust_rule'), factory_contract: getReconciledSource('rust_factory'), event_contract: read('rust-event-generation-contract.json')}};
  return {...source, graph, boundary, fields, action, workflow, policy, selection, sources, plan: planConfiguredRustWorkflow(graph, boundary, fields, selection, sources)};
}
function crate(root: string, plan: ReturnType<typeof planConfiguredRustWorkflow>, main: string) {
  fs.mkdirSync(path.join(root, 'src'), {recursive: true}); fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-workflow-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const artifact of plan.artifacts) {const marker = artifact.relative_path.indexOf('/src/'); const file = path.join(root, 'src', artifact.relative_path.slice(marker + 5)); fs.mkdirSync(path.dirname(file), {recursive: true}); fs.writeFileSync(file, artifact.content);}
  const modules = (part: string) => plan.artifacts.filter(row => row.relative_path.includes(`/${part}/`)).map(row => path.basename(row.relative_path, '.rs')).filter((value, index, rows) => rows.indexOf(value) === index).map(value => `pub mod ${value};`).join('');
  const mode = rustSelectorModule('alpha:mode'); if (!plan.artifacts.some(row => row.relative_path.endsWith(`/${mode}.rs`))) {fs.mkdirSync(path.join(root, 'src/domain/types'), {recursive: true}); fs.writeFileSync(path.join(root, `src/domain/types/${mode}.rs`), '#[derive(Copy,Clone,Debug,PartialEq,Eq,Hash)] pub enum Mode{On,Off}\n');}
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod types{${modules('domain/types')}pub mod ${mode};}pub mod rules{${modules('domain/rules')}}pub mod events{${modules('domain/events')}}}mod application{pub mod operations{${modules('application/operations')}}pub mod workflows{${modules('application/workflows')}}}\n${main}\n`);
}
const blockOn = `fn block_on<F:std::future::Future>(future:F)->F::Output{struct Noop;impl std::task::Wake for Noop{fn wake(self:std::sync::Arc<Self>){} }let w=std::task::Waker::from(std::sync::Arc::new(Noop));let mut c=std::task::Context::from_waker(&w);let mut f=Box::pin(future);loop{match f.as_mut().poll(&mut c){std::task::Poll::Ready(v)=>return v,std::task::Poll::Pending=>std::thread::yield_now()}}}`;

test('Rust Workflow planner binds checked Operations and recovery policy deterministically', t => {
  const f = fixture(t), repeat = planConfiguredRustWorkflow(f.graph, f.boundary, f.fields, f.selection, f.sources), module = f.plan.modules[0]!, output = f.plan.artifacts.find(row => row.relative_path === module.relative_path)!.content;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_WORKFLOW_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_WORKFLOW_PROTOCOL); assert.deepEqual(module.operation_dependencies, ['alpha:post']); assert.equal(module.compensation_execution, false); assert.match(output, /await/); assert.match(output, /ReconciliationRequired/); assert.doesNotMatch(output, /rollback|compensat.*await/i);
});

test('generated Rust Workflow awaits its Operation and preserves committed, rejected and indeterminate outcomes', t => {
  const f = fixture(t), root = path.join(f.temp, 'workflow-crate'), operation = rustSelectorModule('alpha:post'), workflow = rustSelectorModule('alpha:flow'), order = rustSelectorModule('alpha:order'), money = rustSelectorModule('alpha:money'), mode = rustSelectorModule('alpha:mode'), posted = rustSelectorModule('alpha:posted');
  crate(root, f.plan, `use application::operations::${operation} as op;use application::workflows::${workflow} as wf;use domain::types::${order} as o;use domain::types::${money} as m;use domain::events::${posted} as e;#[derive(Clone)]struct Tx{receipt:op::CommitReceipt}impl op::PostTransaction for Tx{async fn rollback(&mut self)->Result<(),op::OperationPortError>{Ok(())}async fn commit(&mut self,_:op::PostBatch)->Result<op::CommitReceipt,op::OperationPortError>{Ok(self.receipt)}}struct Store{receipt:op::CommitReceipt}impl op::PostStore for Store{type Transaction=Tx;async fn begin(&self)->Result<Tx,op::OperationPortError>{Ok(Tx{receipt:self.receipt})}}${blockOn}fn notice(id:&str)->e::PostedInput{e::PostedInput{occurrence:e::PostedOccurrenceInput{event_id:id.to_owned()},occurred_at:"2026-09-15T00:00:00Z".to_owned(),payload:e::PostedPayloadInput{}}}fn main(){let money=m::create_money_factory().create(m::MoneyInput{amount:1}).unwrap();let order=o::create_order_factory().create(o::OrderInput{id:"order-1".to_owned(),amount:1,money,mode:domain::types::${mode}::Mode::On}).unwrap();for (index,receipt) in [op::CommitReceipt::Committed,op::CommitReceipt::Rejected,op::CommitReceipt::Indeterminate].into_iter().enumerate(){let store=Store{receipt};let result=block_on(wf::execute(&order,&notice(&format!("event-{index}")),&store));match(index,result){(0,wf::FlowOutcome::Succeeded(value))=>assert_eq!(value.id(),"order-1"),(1,wf::FlowOutcome::Stopped{disposition:wf::FailureDisposition::Rejected,recovery:wf::RecoveryDisposition::NotRequired,..})=>{},(2,wf::FlowOutcome::Stopped{disposition:wf::FailureDisposition::Indeterminate,recovery:wf::RecoveryDisposition::ReconciliationRequired,..})=>{},_=>panic!("wrong outcome")}}}`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Workflow rejects missing Operation Store dependencies', t => {
  const f = fixture(t), root = path.join(f.temp, 'workflow-compile-fail'), workflow = rustSelectorModule('alpha:flow'); crate(root, f.plan, `${blockOn}struct Missing;fn main(){let order=todo!();let notice=todo!();let _=block_on(application::workflows::${workflow}::execute(order,notice,&Missing));}`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /PostStore/);
});

test('Rust Workflow planner rejects source drift, active data and cloned checked objects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'workflow', {enumerable: true, get() {reads++; return f.workflow;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, workflow: structuredClone(f.workflow)}, {...f.selection, policy: structuredClone(f.policy)}, {...f.selection, actions: []}, {...f.selection, module_root: '../escape'}]) assert.throws(() => planConfiguredRustWorkflow(f.graph, f.boundary, f.fields, selection as any, f.sources));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustWorkflow(f.graph, f.boundary, f.fields, f.selection, {...f.sources, rust_contract: f.sources.rust_contract + '\n'}));
});
