import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {commerceCorpusRoot, commerceSourceRoot, loadCommerceCorpus, writeArtifacts} from '../helpers/reconciled-commerce-corpus.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {
  compileSelectedProjectFields,
  EXACT_FIELD_CONTRACT_SHA256,
  EXACT_PROJECT_FIELD_SELECTION_VERSION,
} from '../../src/input/compiled-field-model.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';

const node = process.execPath;
const tsc = path.resolve(import.meta.dirname, '../../../node_modules/.bin/tsc');
const typeRoots = path.resolve(import.meta.dirname, '../../../node_modules/@types');
const python = '/usr/bin/python3';
const cargo = process.env.CARGO ?? 'cargo';

function workspace(t: test.TestContext, prefix: string): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  return root;
}

const fileHash = (file: string): string => createHash('sha256').update(fs.readFileSync(file)).digest('hex');

test('R13 corpus is one lawful current graph represented completely by all three native planners', () => {
  const corpus = loadCommerceCorpus();
  assert.equal(corpus.graph.nodes.length, 21);
  assert.equal(corpus.graph.relationships.length, 14);
  assert.equal(new Set(corpus.graph.nodes.map(row => row.kind)).size, 13);
  assert.equal(corpus.scenarios.scenarios.length, 22);
  assert.equal(new Set(corpus.scenarios.scenarios.map((row: any) => row.scenario_id)).size, 22);
  assert.deepEqual(corpus.graph.nodes.map(row => row.selector).sort(), corpus.plans.typescript.node_selectors);
  assert.deepEqual(corpus.graph.nodes.map(row => row.selector).sort(), corpus.plans.python.node_selectors);
  assert.deepEqual(corpus.graph.nodes.map(row => row.selector).sort(), corpus.plans.rust.node_selectors);
  assert.deepEqual(
    [corpus.plans.typescript.resolved.modules.length, corpus.plans.python.modules.length, corpus.plans.rust.modules.length],
    [36, 81, 21],
  );
  assert.ok(corpus.plans.typescript.resolved.modules.some(row => row.relative_path.includes('/billing/') && row.qualified_selectors.includes('billing:total')));
  assert.ok(corpus.plans.python.modules.some(row => row.relative_path.includes('/billing/') && row.qualified_selectors?.includes('billing:total')));
  assert.ok(corpus.plans.rust.modules.some(row => row.selector === 'billing:total'));
  for (const plan of Object.values(corpus.plans)) {
    assert.equal(plan.source_capsule_sha256, '9886ea42053d5c0b918123649317776214b5e92139161f2602e11dde796cffe8');
    assert.equal(plan.checking_scope, 'whole-project');
  }
});

test('R13 qualification accounts for the exact current corpus without missing scenarios', () => {
  const corpus = loadCommerceCorpus();
  const qualification = JSON.parse(fs.readFileSync(path.resolve(commerceCorpusRoot, '../../R13-QUALIFICATION.json'), 'utf8'));
  assert.equal(qualification.result, 'pass');
  assert.equal(qualification.authority_effect, 'none');
  assert.deepEqual(qualification.denominators, {scenarios: 22, passed: 22, failed: 0, missing: 0, languages: 3, metatypes: 13});
  assert.deepEqual(qualification.scenarios.map((row: any) => row.id), corpus.scenarios.scenarios.map((row: any) => row.scenario_id));
  assert.ok(qualification.scenarios.every((row: any) => row.result === 'pass' && row.evidence.length > 0));
  assert.equal(qualification.source.scenarios_sha256, fileHash(path.join(commerceCorpusRoot, 'scenarios.json')));
  assert.equal(qualification.source.values_sha256, fileHash(path.join(commerceCorpusRoot, 'values.json')));
  assert.equal(qualification.source.selection_sha256, fileHash(path.join(commerceCorpusRoot, 'selection.json')));
  assert.deepEqual(
    [qualification.plans.typescript.plan_sha256, qualification.plans.python.plan_sha256, qualification.plans.rust.plan_sha256],
    [corpus.plans.typescript.plan_sha256, corpus.plans.python.plan_sha256, corpus.plans.rust.plan_sha256],
  );
  assert.ok(Object.values(corpus.plans).every(plan => plan.source_capsule_sha256 === qualification.source.compiler_source_capsule_sha256));
});

test('R13 current source baseline rejects every canonical source mutation independently', t => {
  const corpus = loadCommerceCorpus();
  const mutations: readonly [string, (value: any) => void, RegExp][] = [
    ['specs/commerce/nodes/order.json', value => {value.body.typed_contract.properties.find((row: any) => row.name === 'customer').type.selector = 'billing:missing';}, /missing|unknown|unresolved|not found/i],
    ['specs/commerce/nodes/summary.json', value => {value.body.typed_contract.fields[1].value = {op: 'call', selector: 'commerce:total', arguments: []};}, /MAPPING|VALUE|unknown|op/i],
    ['specs/commerce/nodes/flow.json', value => {value.body.typed_contract.steps[1].step_id = 'first';}, /duplicate|unique|occurrence/i],
    ['specs/commerce/edges/summary-maps-api.json', value => {value.relationship = 'calculates-for-mapping';}, /unknown relationship:calculates-for-mapping/],
  ];
  for (const [relative, mutate, expected] of mutations) {
    const root = workspace(t, 'domainspec-r13-negative-'), source = path.join(root, 'source');
    fs.cpSync(commerceSourceRoot, source, {recursive: true});
    const file = path.join(source, relative), value = JSON.parse(fs.readFileSync(file, 'utf8'));
    mutate(value);
    fs.writeFileSync(file, JSON.stringify(value));
    assert.throws(() => loadCompiledProjectGraph(source), expected, relative);
  }
  const certificate = createCompiledProjectCertificate(corpus.graph);
  const bindings = corpus.selections.typescript.field_bindings;
  assert.throws(() => compileSelectedProjectFields(corpus.graph, {
    schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION,
    contract_sha256: EXACT_FIELD_CONTRACT_SHA256,
    graph_sha256: certificate.graph_sha256,
    roots: ['commerce:order'],
    bindings: [{...bindings[0], projection: ['name']}],
  }, getReconciledSource('field')), /IDENTITY|TYPE/);
});

test('R13 generated TypeScript executes the cross-feature calculation and explicit mapping pipeline', t => {
  const corpus = loadCommerceCorpus(), root = workspace(t, 'domainspec-r13-ts-'), source = path.join(root, 'source'), dist = path.join(root, 'dist');
  writeArtifacts(source, corpus.plans.typescript.resolved.artifacts);
  fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({type: 'module'}));
  const harness = `// @ts-nocheck
import {calculateTotal as netTotal} from './commerce-corpus/features/commerce/src/domain/calculations/total.js';
import {calculateTotal as feeTotal} from './commerce-corpus/features/billing/src/domain/calculations/total.js';
import {mappingSummary} from './commerce-corpus/features/commerce/src/application/mappings/summary.js';
import {queryFind as queryOrders} from './commerce-corpus/features/commerce/src/application/queries/find.js';
import {queryFind as queryBilling} from './commerce-corpus/features/billing/src/application/queries/find.js';
import {policyDispatch} from './commerce-corpus/features/commerce/src/domain/policies/dispatch.js';
import {transitionLifecycle} from './commerce-corpus/features/commerce/src/domain/state-machines/lifecycle.js';
import {eventPosted} from './commerce-corpus/features/commerce/src/domain/events/posted.js';
import {eventReleased} from './commerce-corpus/features/commerce/src/domain/events/released.js';
import {Priority} from './commerce-corpus/features/commerce/src/domain/enums/priority.js';
import {PriorityValueComponent} from './commerce-corpus/features/commerce/src/domain/enums/priority.component.js';
import {operationPerform} from './commerce-corpus/features/commerce/src/application/operations/perform.js';
import {workflowFlow} from './commerce-corpus/features/commerce/src/application/workflows/flow.js';
const values=${JSON.stringify(corpus.values)};
const net=netTotal({gross:'100',adjustment:'7'}),fee=feeTotal({gross:'2',adjustment:'3'});
const response=mappingSummary({order:values.order,net,fee});
if(response.id!==1n||response.net!==93n||response.fee!==5n)throw Error('pipeline');
const swapped=mappingSummary({order:values.order,net:fee,fee:net});if(swapped.net!==5n||swapped.fee!==93n)throw Error('same-type occurrence swap');
let underflow=false;try{netTotal({gross:'0',adjustment:'1'});}catch(e){underflow=String(e).includes('UNDERFLOW');}if(!underflow)throw Error('underflow');
const orders=queryOrders(values.query_orders,{}),billing=queryBilling(values.billing_customers,{});
if(orders[0].billing_customer_id!==2n||billing[0].name!=='Billing customer')throw Error('query');
if(policyDispatch({amount:'1'})!=='commerce:perform'||policyDispatch({amount:'0'})!=='commerce:undo')throw Error('policy');
if(PriorityValueComponent.fromVariant('Urgent').variant!==Priority.Urgent)throw Error('enum');
let unknownEnum=false;try{PriorityValueComponent.fromVariant('Unknown');}catch{unknownEnum=true;}if(!unknownEnum)throw Error('unknown enum');
const transitioned=transitionLifecycle('draft','commerce:posted',{amount:'1'}),guarded=transitionLifecycle('draft','commerce:posted',{amount:'0'}),illegal=transitionLifecycle('draft','commerce:released',{amount:'1'});
if(transitioned.status!=='transitioned'||transitioned.output_intents.map(x=>x.slot).join(',')!=='confirmation,audit'||guarded.reason!=='guard'||illegal.reason!=='no-transition')throw Error('state');
const posted=eventPosted(values.events.post_first),postedTwo=eventPosted(values.events.post_second),released=eventReleased(values.events.undo_first,()=> '2026-09-13T13:00:00Z');
if(posted.occurrence['event-id']===postedTwo.occurrence['event-id']||released.occurredAt!=='2026-09-13T13:00:00Z')throw Error('event');
const store=(receipts)=>{const state={receipts:[...receipts],commits:0,rollbacks:0,batches:[]};return {state,dependencies:{store:{begin:async()=>({read:async()=>null,commit:async batch=>{state.commits++;state.batches.push(batch);return {status:state.receipts.shift()??'committed'};},rollback:async()=>{state.rollbacks++;}})}}};};
const committed=store(['committed']),op=await operationPerform({amount:values.order,notice_input:values.events.post_first},committed.dependencies);
if(op.status!=='committed'||committed.state.commits!==1||committed.state.batches[0].writes.length!==1||committed.state.batches[0].events.length!==1)throw Error('operation commit');
const guardedStore=store(['committed']),guardOrder={...values.order,money:{quantity:'100'}},guardOutcome=await operationPerform({amount:guardOrder,notice_input:values.events.post_first},guardedStore.dependencies);
if(guardOutcome.status!=='rejected'||guardedStore.state.commits!==0||guardedStore.state.rollbacks!==1)throw Error('operation guard');
const uncertain=store(['indeterminate']),uncertainOutcome=await operationPerform({amount:values.order,notice_input:values.events.post_first},uncertain.dependencies);
if(uncertainOutcome.status!=='indeterminate'||uncertain.state.commits!==1)throw Error('operation uncertainty');
const workflowInput={...values.workflow.inputs,...values.workflow.event_inputs};
const successStore=store(['committed','committed','committed','committed']);
const success=await workflowFlow(workflowInput,{workflow_execution_id:'wf-ok',failure_occurrence_id:'none'},{'commerce:perform':successStore.dependencies});
if(success.status!=='succeeded'||successStore.state.commits!==4)throw Error('workflow success');
const failedStore=store(['committed','committed','committed','rejected']);
const failed=await workflowFlow(workflowInput,{workflow_execution_id:'wf-fail',failure_occurrence_id:'last-failure'},{'commerce:perform':failedStore.dependencies});
if(failed.status!=='forward-stopped'||failed.bindings_status!=='ready'||failed.recovery_bindings.bindings.map(x=>x.compensation_id).join(',')!=='undo-third,undo-second,undo-first')throw Error('workflow recovery');
const uncertainStore=store(['committed','indeterminate']);
const stopped=await workflowFlow(workflowInput,{workflow_execution_id:'wf-unknown',failure_occurrence_id:'second-unknown'},{'commerce:perform':uncertainStore.dependencies});
if(stopped.status!=='forward-stopped'||stopped.bindings_status!=='not-evaluable'||stopped.evaluation.failure.commit_status!=='indeterminate'||stopped.evaluation.recovery_status!=='reconciliation-required')throw Error('workflow uncertainty');
console.log(JSON.stringify({language:'typescript',pipeline:{id:String(response.id),net:String(response.net),fee:String(response.fee)},queries:[orders.length,billing.length],policy:['commerce:perform','commerce:undo'],state:['transitioned','guard'],operation:['committed','rejected','indeterminate'],workflow:['succeeded','recovery-required','reconciliation-required'],event:posted.occurrence['event-id']}));
`;
  const harnessFile = path.join(source, 'commerce-harness.ts'); fs.writeFileSync(harnessFile, harness);
  const files: string[] = [];
  const walk = (folder: string) => {for (const entry of fs.readdirSync(folder, {withFileTypes: true})) {const file = path.join(folder, entry.name); if (entry.isDirectory()) walk(file); else if (file.endsWith('.ts')) files.push(file);}};
  walk(source);
  execFileSync(tsc, ['--ignoreConfig', '--strict', '--skipLibCheck', '--types', 'node', '--typeRoots', typeRoots, '--target', 'ES2022', '--module', 'NodeNext', '--rootDir', source, '--outDir', dist, ...files], {encoding: 'utf8'});
  const result = JSON.parse(execFileSync(node, [path.join(dist, 'commerce-harness.js')], {encoding: 'utf8'}));
  assert.deepEqual(result.pipeline, {id: '1', net: '93', fee: '5'});
  assert.deepEqual(result.operation, ['committed', 'rejected', 'indeterminate']);
  assert.deepEqual(result.workflow, ['succeeded', 'recovery-required', 'reconciliation-required']);
});

test('R13 generated Python executes the cross-feature calculation and explicit mapping pipeline', t => {
  const corpus = loadCommerceCorpus(), root = workspace(t, 'domainspec-r13-python-');
  writeArtifacts(root, corpus.plans.python.artifacts);
  execFileSync(python, ['-I', '-S', '-B', '-m', 'compileall', '-q', path.join(root, 'commerce_corpus')], {encoding: 'utf8'});
  const values = JSON.stringify(JSON.stringify(corpus.values));
  const harness = `import asyncio
import json
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from commerce_corpus.features.commerce.src.domain.calculations.total import calculate_total as net_total
from commerce_corpus.features.billing.src.domain.calculations.total import calculate_total as fee_total
from commerce_corpus.features.commerce.src.application.mappings.summary import mapping_summary
from commerce_corpus.features.commerce.src.application.queries.find import query_find as query_orders
from commerce_corpus.features.billing.src.application.queries.find import query_find as query_billing
from commerce_corpus.features.commerce.src.domain.policies.dispatch import policy_dispatch
from commerce_corpus.features.commerce.src.domain.state_machines.lifecycle import transition_lifecycle, State, Trigger
from commerce_corpus.features.commerce.src.domain.events.posted import event_posted
from commerce_corpus.features.commerce.src.domain.events.released import event_released
from commerce_corpus.features.commerce.src.domain.enums.priority import Priority, parse_priority
from commerce_corpus.features.commerce.src.application.operations.perform import operation_perform
from commerce_corpus.features.commerce.src.application.workflows.flow import workflow_flow

values = json.loads(${values})

class Tx:
    def __init__(self, state): self.state = state
    async def read(self, request): return None
    async def commit(self, batch):
        self.state["commits"] += 1
        self.state["batches"].append(batch)
        return {"status": self.state["receipts"].pop(0) if self.state["receipts"] else "committed"}
    async def rollback(self): self.state["rollbacks"] += 1

class Store:
    def __init__(self, receipts):
        self.state = {"receipts": list(receipts), "commits": 0, "rollbacks": 0, "batches": []}
    async def begin(self): return Tx(self.state)

async def main():
    net = net_total({"gross": "100", "adjustment": "7"})
    fee = fee_total({"gross": "2", "adjustment": "3"})
    response = mapping_summary({"order": values["order"], "net": net, "fee": fee})
    assert response["id"] == 1 and response["net"] == 93 and response["fee"] == 5
    swapped = mapping_summary({"order": values["order"], "net": fee, "fee": net})
    assert swapped["net"] == 5 and swapped["fee"] == 93
    underflow = False
    try: net_total({"gross": "0", "adjustment": "1"})
    except Exception as error: underflow = "UNDERFLOW" in str(error)
    assert underflow
    orders = query_orders(values["query_orders"], {})
    billing = query_billing(values["billing_customers"], {})
    assert orders[0]["billing_customer_id"] == 2 and billing[0]["name"] == "Billing customer"
    assert policy_dispatch({"amount": "1"}) == "commerce:perform"
    assert policy_dispatch({"amount": "0"}) == "commerce:undo"
    assert parse_priority("Urgent") is Priority.Urgent
    unknown_enum = False
    try: parse_priority("Unknown")
    except Exception: unknown_enum = True
    assert unknown_enum
    transitioned = transition_lifecycle(State.DRAFT, Trigger.COMMERCE__POSTED, {"amount": "1"})
    guarded = transition_lifecycle(State.DRAFT, Trigger.COMMERCE__POSTED, {"amount": "0"})
    illegal = transition_lifecycle(State.DRAFT, Trigger.COMMERCE__RELEASED, {"amount": "1"})
    assert transitioned.status == "transitioned"
    assert [row["slot"] for row in transitioned.output_intents] == ["confirmation", "audit"]
    assert guarded.reason == "guard" and illegal.reason == "no-transition"
    posted = event_posted(values["events"]["post_first"])
    posted_two = event_posted(values["events"]["post_second"])
    released = event_released(values["events"]["undo_first"], lambda: "2026-09-13T13:00:00Z")
    assert posted.occurrence["event-id"] != posted_two.occurrence["event-id"] and released.occurredAt == "2026-09-13T13:00:00Z"

    committed = Store(["committed"])
    outcome = await operation_perform({"amount": values["order"], "notice_input": values["events"]["post_first"]}, {"store": committed})
    assert outcome.status == "committed" and committed.state["commits"] == 1
    assert len(committed.state["batches"][0].writes) == 1 and len(committed.state["batches"][0].events) == 1
    guard_order = json.loads(json.dumps(values["order"]))
    guard_order["money"] = {"quantity": "100"}
    guard_store = Store(["committed"])
    guard_outcome = await operation_perform({"amount": guard_order, "notice_input": values["events"]["post_first"]}, {"store": guard_store})
    assert guard_outcome.status == "rejected" and guard_store.state["commits"] == 0 and guard_store.state["rollbacks"] == 1
    uncertain = Store(["indeterminate"])
    uncertain_outcome = await operation_perform({"amount": values["order"], "notice_input": values["events"]["post_first"]}, {"store": uncertain})
    assert uncertain_outcome.status == "indeterminate" and uncertain.state["commits"] == 1

    workflow_input = {**values["workflow"]["inputs"], **values["workflow"]["event_inputs"]}
    success_store = Store(["committed", "committed", "committed", "committed"])
    success = await workflow_flow(workflow_input, {"workflow_execution_id": "wf-ok", "failure_occurrence_id": "none"}, {"commerce:perform": {"store": success_store}})
    assert success.status == "succeeded" and success_store.state["commits"] == 4
    failed_store = Store(["committed", "committed", "committed", "rejected"])
    failed = await workflow_flow(workflow_input, {"workflow_execution_id": "wf-fail", "failure_occurrence_id": "last-failure"}, {"commerce:perform": {"store": failed_store}})
    assert failed.status == "forward-stopped" and failed.bindings_status == "ready"
    compensation_ids = [row["compensation_id"] for row in failed.recovery_bindings["bindings"]]
    assert compensation_ids == ["undo-third", "undo-second", "undo-first"]
    uncertain_store = Store(["committed", "indeterminate"])
    stopped = await workflow_flow(workflow_input, {"workflow_execution_id": "wf-unknown", "failure_occurrence_id": "second-unknown"}, {"commerce:perform": {"store": uncertain_store}})
    assert stopped.status == "forward-stopped" and stopped.bindings_status == "not-evaluable"
    assert stopped.evaluation["failure"]["commit_status"] == "indeterminate"
    assert stopped.evaluation["recovery_status"] == "reconciliation-required"
    print(json.dumps({
        "language": "python",
        "pipeline": {"id": str(response["id"]), "net": str(response["net"]), "fee": str(response["fee"])},
        "queries": [len(orders), len(billing)],
        "policy": ["commerce:perform", "commerce:undo"],
        "state": ["transitioned", "guard"],
        "operation": ["committed", "rejected", "indeterminate"],
        "workflow": ["succeeded", "recovery-required", "reconciliation-required"],
        "event": posted.occurrence["event-id"],
    }, separators=(",", ":")))

asyncio.run(main())
`;
  const harnessFile = path.join(root, 'commerce_harness.py');
  fs.writeFileSync(harnessFile, harness);
  const result = JSON.parse(execFileSync(python, ['-I', '-S', '-B', harnessFile], {cwd: root, encoding: 'utf8'}));
  assert.deepEqual(result.pipeline, {id: '1', net: '93', fee: '5'});
  assert.deepEqual(result.operation, ['committed', 'rejected', 'indeterminate']);
  assert.deepEqual(result.workflow, ['succeeded', 'recovery-required', 'reconciliation-required']);
});

test('R13 generated Rust executes the cross-feature calculation and explicit mapping pipeline', t => {
  const corpus = loadCommerceCorpus(), root = workspace(t, 'domainspec-r13-rust-'), crate = path.join(root, 'commerce-corpus');
  writeArtifacts(root, corpus.plans.rust.artifacts);
  const bin = path.join(crate, 'src', 'bin');
  fs.mkdirSync(bin, {recursive: true});
  const harness = `use r13_commerce_candidate as ds;
use ds::domain::types::f8_commerce_n5_money::{Money, MoneyInput, create_money_factory};
use ds::domain::types::f8_commerce_n8_customer::{Customer, CustomerInput, create_customer_factory};
use ds::domain::types::f8_commerce_n5_order::{Order, OrderInput, create_order_factory};
use ds::domain::types::f8_commerce_n6_choice::Choice;
use ds::domain::types::f8_commerce_n8_priority::{Priority, parse_priority};
use ds::domain::events::f8_commerce_n6_posted::{EventRefF8CommerceN5Order as PostedRef, PostedInput, PostedOccurrenceInput, PostedPayloadInput, create_posted};
use ds::domain::events::f8_commerce_n8_released::{EventRefF8CommerceN5Order as ReleasedRef, ReleasedInput, ReleasedOccurrenceInput, ReleasedPayloadInput, create_released};
use ds::application::operations::f8_commerce_n7_perform::{CommitReceipt, OperationPortError, PerformBatch, PerformOutcome, PerformStore, PerformTransaction};
use ds::application::workflows::f8_commerce_n4_flow::{FlowExecution, FlowOutcome, RecoveryDisposition};
use std::cell::RefCell;
use std::collections::{BTreeSet, VecDeque};
use std::future::Future;
use std::pin::pin;
use std::rc::Rc;
use std::task::{Context, Poll, Waker};

fn block_on<F: Future>(future: F) -> F::Output {
    let waker = Waker::noop();
    let mut context = Context::from_waker(waker);
    let mut future = pin!(future);
    loop { match future.as_mut().poll(&mut context) { Poll::Ready(value) => return value, Poll::Pending => std::thread::yield_now() } }
}

fn money(quantity: u64, note: Option<&str>) -> Money {
    create_money_factory().create(MoneyInput { quantity, note: note.map(str::to_owned) }).unwrap()
}
fn customer(id: u64, name: &str) -> Customer {
    create_customer_factory().create(CustomerInput { id, name: name.to_owned() }).unwrap()
}
fn order(money_quantity: u64, labels: Vec<&str>) -> Order {
    create_order_factory().create(OrderInput {
        id: 1,
        customer: customer(2, "Customer"),
        money: money(money_quantity, None),
        choice: Choice::Some(money(7, None)),
        labels: labels.into_iter().map(str::to_owned).collect(),
        lines: vec![money(3, None), money(9, Some(""))],
        billing_customer_id: 2,
        tags: ["a".to_owned(), "b".to_owned()].into_iter().collect::<BTreeSet<_>>(),
    }).unwrap()
}
fn posted(number: u32) -> PostedInput {
    PostedInput {
        occurrence: PostedOccurrenceInput { event_id: format!("00000000-0000-4000-8000-{number:012}") },
        occurred_at: "2026-09-13T12:00:00Z".to_owned(),
        payload: PostedPayloadInput { delta: Some(i64::MIN), order_id: PostedRef::new(1), ratio: Some(1.5) },
    }
}
fn released(number: u32) -> ReleasedInput {
    ReleasedInput {
        occurrence: ReleasedOccurrenceInput { event_id: format!("00000000-0000-4000-8000-{number:012}") },
        payload: ReleasedPayloadInput { delta: Some(i64::MIN), order_id: ReleasedRef::new(1), ratio: Some(1.5) },
    }
}

#[derive(Default)]
struct StoreState { receipts: VecDeque<CommitReceipt>, commits: usize, rollbacks: usize, batches: usize }
#[derive(Clone)]
struct Store(Rc<RefCell<StoreState>>);
struct Tx(Rc<RefCell<StoreState>>);
impl Store {
    fn new(receipts: impl IntoIterator<Item=CommitReceipt>) -> Self {
        Self(Rc::new(RefCell::new(StoreState { receipts: receipts.into_iter().collect(), ..StoreState::default() })))
    }
}
impl PerformTransaction for Tx {
    async fn rollback(&mut self) -> Result<(), OperationPortError> { self.0.borrow_mut().rollbacks += 1; Ok(()) }
    async fn commit(&mut self, batch: PerformBatch) -> Result<CommitReceipt, OperationPortError> {
        assert_eq!(batch.order_state.target, "commerce:order");
        assert_eq!(batch.notice.target, "commerce:posted");
        let mut state = self.0.borrow_mut(); state.commits += 1; state.batches += 1;
        Ok(state.receipts.pop_front().unwrap_or(CommitReceipt::Committed))
    }
}
impl PerformStore for Store {
    type Transaction = Tx;
    async fn begin(&self) -> Result<Self::Transaction, OperationPortError> { Ok(Tx(self.0.clone())) }
}

struct CommerceReader(Vec<Order>);
impl ds::application::queries::f8_commerce_n4_find::FindReader for CommerceReader {
    async fn read_find(&self) -> Result<Vec<Order>, ds::application::queries::f8_commerce_n4_find::QueryError> { Ok(self.0.clone()) }
}
struct BillingReader(Vec<ds::domain::types::f7_billing_n8_customer::Customer>);
impl ds::application::queries::f7_billing_n4_find::FindReader for BillingReader {
    async fn read_find(&self) -> Result<Vec<ds::domain::types::f7_billing_n8_customer::Customer>, ds::application::queries::f7_billing_n4_find::QueryError> { Ok(self.0.clone()) }
}

fn main() {
    let amount = order(3, vec!["a", "a", "b"]);
    let before = order(1, vec![]);
    let net = ds::domain::calculations::f8_commerce_n5_total::total(&100, &7).unwrap();
    let fee = ds::domain::calculations::f7_billing_n5_total::total(&2, &3).unwrap();
    let response = ds::application::mappings::f8_commerce_n7_summary::summary(&amount, &net, &fee);
    assert_eq!((response.id, response.net, response.fee), (1, 93, 5));
    let swapped = ds::application::mappings::f8_commerce_n7_summary::summary(&amount, &fee, &net);
    assert_eq!((swapped.net, swapped.fee), (5, 93));
    assert!(ds::domain::calculations::f8_commerce_n5_total::total(&0, &1).is_err());
    assert!(ds::application::interfaces::f8_commerce_n3_api::accepts_consumer_version("1.0.0"));
    assert!(!ds::application::interfaces::f8_commerce_n3_api::accepts_consumer_version("2.0.0"));
    assert_eq!(ds::domain::policies::f8_commerce_n8_dispatch::dispatch(&1).selector(), "commerce:perform");
    assert_eq!(ds::domain::policies::f8_commerce_n8_dispatch::dispatch(&0).selector(), "commerce:undo");
    assert_eq!(parse_priority("Urgent").unwrap(), Priority::Urgent);
    assert!(parse_priority("Unknown").is_err());

    use ds::domain::state_machines::f8_commerce_n9_lifecycle::{reduce, State, Trigger, TransitionOutcome, RejectionReason};
    match reduce(State::Draft, Trigger::CommercePosted, &1) {
        TransitionOutcome::Transitioned { output_intents, .. } => assert_eq!(output_intents.iter().map(|row| row.slot).collect::<Vec<_>>(), vec!["confirmation", "audit"]),
        _ => panic!("expected transition"),
    }
    assert!(matches!(reduce(State::Draft, Trigger::CommercePosted, &0), TransitionOutcome::Rejected { reason: RejectionReason::Guard, .. }));
    assert!(matches!(reduce(State::Draft, Trigger::CommerceReleased, &1), TransitionOutcome::Rejected { reason: RejectionReason::NoTransition, .. }));
    let event = create_posted(posted(1)).unwrap(); let event_two = create_posted(posted(2)).unwrap();
    let released_event = create_released(released(5), &|| "2026-09-13T13:00:00Z".to_owned()).unwrap();
    assert_ne!(event.occurrence().event_id(), event_two.occurrence().event_id());
    assert_eq!(released_event.occurred_at(), "2026-09-13T13:00:00Z");
    assert_eq!(event.payload().order_id().value(), 1);
    assert_eq!(released_event.payload().order_id().value(), 1);

    let commerce_rows = block_on(ds::application::queries::f8_commerce_n4_find::find(&CommerceReader(vec![amount.clone()]))).unwrap();
    let billing_customer = ds::domain::types::f7_billing_n8_customer::create_customer_factory().create(ds::domain::types::f7_billing_n8_customer::CustomerInput { id: 2, name: "Billing customer".to_owned() }).unwrap();
    let billing_rows = block_on(ds::application::queries::f7_billing_n4_find::find(&BillingReader(vec![billing_customer]))).unwrap();
    assert_eq!((commerce_rows[0].billing_customer_id, billing_rows[0].name.as_str()), (2, "Billing customer"));

    let committed = Store::new([CommitReceipt::Committed]);
    assert!(matches!(block_on(ds::application::operations::f8_commerce_n7_perform::perform(&amount, posted(1), &committed)), PerformOutcome::Committed(_)));
    assert_eq!((committed.0.borrow().commits, committed.0.borrow().batches), (1, 1));
    let rejected = Store::new([CommitReceipt::Committed]);
    assert!(matches!(block_on(ds::application::operations::f8_commerce_n7_perform::perform(&order(100, vec![]), posted(1), &rejected)), PerformOutcome::Rejected { .. }));
    assert_eq!((rejected.0.borrow().commits, rejected.0.borrow().rollbacks), (0, 1));
    let uncertain = Store::new([CommitReceipt::Indeterminate]);
    assert!(matches!(block_on(ds::application::operations::f8_commerce_n7_perform::perform(&amount, posted(1), &uncertain)), PerformOutcome::Indeterminate { .. }));

    let post_first = posted(1); let post_second = posted(2); let post_third = posted(3); let post_last = posted(4);
    let undo_first = released(5); let undo_second = released(6); let undo_third = released(7);
    let clock = || "2026-09-13T12:00:00Z".to_owned();
    let success_store = Store::new([CommitReceipt::Committed, CommitReceipt::Committed, CommitReceipt::Committed, CommitReceipt::Committed]);
    let success = block_on(ds::application::workflows::f8_commerce_n4_flow::execute(FlowExecution {
        amount: &amount, before: &before,
        post_first: &post_first, post_second: &post_second, post_third: &post_third, post_last: &post_last,
        undo_first: &undo_first, undo_second: &undo_second, undo_third: &undo_third,
        clock_undo_first: &clock, clock_undo_second: &clock, clock_undo_third: &clock,
        store_perform: &success_store,
    }));
    assert!(matches!(success, FlowOutcome::Succeeded(_)));
    assert_eq!(success_store.0.borrow().commits, 4);
    let failed_store = Store::new([CommitReceipt::Committed, CommitReceipt::Committed, CommitReceipt::Committed, CommitReceipt::Rejected]);
    let failed = block_on(ds::application::workflows::f8_commerce_n4_flow::execute(FlowExecution {
        amount: &amount, before: &before,
        post_first: &post_first, post_second: &post_second, post_third: &post_third, post_last: &post_last,
        undo_first: &undo_first, undo_second: &undo_second, undo_third: &undo_third,
        clock_undo_first: &clock, clock_undo_second: &clock, clock_undo_third: &clock,
        store_perform: &failed_store,
    }));
    match failed {
        FlowOutcome::Stopped { recovery: RecoveryDisposition::Required(rows), .. } => assert_eq!(rows.iter().map(|row| row.compensation_id).collect::<Vec<_>>(), vec!["undo-third", "undo-second", "undo-first"]),
        _ => panic!("expected recovery"),
    }
    let unknown_store = Store::new([CommitReceipt::Committed, CommitReceipt::Indeterminate]);
    let unknown = block_on(ds::application::workflows::f8_commerce_n4_flow::execute(FlowExecution {
        amount: &amount, before: &before,
        post_first: &post_first, post_second: &post_second, post_third: &post_third, post_last: &post_last,
        undo_first: &undo_first, undo_second: &undo_second, undo_third: &undo_third,
        clock_undo_first: &clock, clock_undo_second: &clock, clock_undo_third: &clock,
        store_perform: &unknown_store,
    }));
    assert!(matches!(unknown, FlowOutcome::Stopped { recovery: RecoveryDisposition::ReconciliationRequired, .. }));
    println!(r#"{{"language":"rust","pipeline":{{"id":"1","net":"93","fee":"5"}},"queries":[1,1],"policy":["commerce:perform","commerce:undo"],"state":["transitioned","guard"],"operation":["committed","rejected","indeterminate"],"workflow":["succeeded","recovery-required","reconciliation-required"],"event":"00000000-0000-4000-8000-000000000001"}}"#);
}
`;
  fs.writeFileSync(path.join(bin, 'commerce_harness.rs'), harness);
  const target = path.join(root, 'target');
  const result = JSON.parse(execFileSync(cargo, ['run', '--offline', '--locked', '--quiet', '--bin', 'commerce_harness'], {cwd: crate, env: {...process.env, CARGO_TARGET_DIR: target}, encoding: 'utf8'}));
  assert.deepEqual(result.pipeline, {id: '1', net: '93', fee: '5'});
  assert.deepEqual(result.operation, ['committed', 'rejected', 'indeterminate']);
  assert.deepEqual(result.workflow, ['succeeded', 'recovery-required', 'reconciliation-required']);
});
