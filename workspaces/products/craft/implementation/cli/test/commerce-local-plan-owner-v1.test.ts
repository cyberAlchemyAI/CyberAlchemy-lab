/** Actual source property/state/version/failure closure and original plan custody.
 * No store, business callback or native mutation executor is constructed.
 * Open Questions: docs/COMMERCE-LOCAL-PLANS-V1.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,cpSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCoreCommerceEffectContracts} from '../src/commerce/commerce-core-role-contracts.js';
import {createCommerceLocalPlanOwnerV1,assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),base=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC15'),candidate=path.join(repo,'examples/ecommerce-target-candidate');
let owner:CommerceLocalPlanOwnerV1,foreign:CommerceLocalPlanOwnerV1,root:string,sourceRoot:string,sourceOwner:any,capture:any,semanticOwner:any,semantic:any,stage:any,source:any,domain:any,baseline:any,sourceTexts:any[],assets:any[],original:any;
const code=(c:string)=>(e:any)=>e?.diagnostics?.[0]?.code===c;
before(async()=>{
 root=mkdtempSync(path.join(base,'local-plan-controls-'));sourceRoot=path.join(root,'source');cpSync(candidate,sourceRoot,{recursive:true,force:false,errorOnExist:true});
 sourceOwner=createCoreCommerceSourceOwner();capture=sourceOwner.prepare(sourceRoot);const actual=sourceOwner.inspect(capture),paths=new Set(actual.reconstruction.modules.map((m:any)=>m.path));sourceTexts=actual.files.filter((f:any)=>paths.has(f.path));assets=actual.files.filter((f:any)=>f.path.endsWith('.json'));
 semanticOwner=createCoreCommerceSemanticOwner(sourceOwner);semantic=semanticOwner.check(capture);original=semanticOwner.inspect(semantic);stage=createCoreCommerceStageSourceOwner(sourceOwner,semanticOwner);source=await stage.prepare(sourceRoot,'application.alch');domain=createCommerceComputationDomainOwner(stage,source);const limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8'));baseline=domain.check(createCoreCommerceComputationContract(sourceTexts,'Orders.PayableTotal',limits.computation.limits));
 owner=createCommerceLocalPlanOwnerV1(sourceOwner,capture,semanticOwner,semantic,stage,source,domain,baseline);foreign=createCommerceLocalPlanOwnerV1(sourceOwner,capture,semanticOwner,semantic,stage,source,domain,baseline);
});
after(()=>{owner?.dispose();foreign?.dispose();});
test('actual PlaceOrder plan closes all declared creates and Event fields without executing',()=>{
 assertCommerceLocalPlanOwnerV1(owner);const h=owner.bindOperation('Orders.PlaceOrder'),v=owner.inspectOperation(h);assert.equal(v.execution,'not-performed');assert.equal(v.plan.protocol,null);assert.equal(v.source.artifact.path,'services/orders.alch');const tx=v.transactions.find(t=>t.plan.name==='AcceptCheckout')!;assert.ok(tx);assert.deepEqual(tx.plan.participants,['Orders.Order','Orders.CheckoutProgress','Orders.ReplayRecord','Orders.OrderPlacedOutbox']);assert.ok(tx.mutations.some(m=>m.operation==='record-event'&&m.target==='Shop.Events.OrderPlaced'&&m.source.artifact.path==='contracts/events.alch'));for(const m of tx.mutations)assert.deepEqual([...m.assigned_fields].sort(),Object.keys(m.record.fields).sort());const t=owner.bindTransaction(h,tx.path);assert.deepEqual(owner.inspectTransaction(t),tx);assert.throws(()=>foreign.inspectOperation(h),code('ForeignOwner'));assert.throws(()=>owner.inspectTransaction({...t}),code('ForeignOwner'));assert.throws(()=>owner.inspectOperation({...h}),code('ForeignOwner'));
});
test('new factories reject cloned source semantic stage and domain owners',()=>{
 for(const parents of [[{...sourceOwner},capture,semanticOwner,semantic,stage,source,domain,baseline],[sourceOwner,capture,{...semanticOwner},semantic,stage,source,domain,baseline],[sourceOwner,capture,semanticOwner,semantic,{...stage},source,domain,baseline],[sourceOwner,capture,semanticOwner,semantic,stage,source,{...domain},baseline]])assert.throws(()=>createCommerceLocalPlanOwnerV1(...parents as Parameters<typeof createCommerceLocalPlanOwnerV1>),code('ForeignOwner'));
});
test('local query preserves actual customer ownership predicate and source result type',()=>{
 const h=owner.bindRead('Orders.GetOrder'),v=owner.inspectRead(h);assert.equal(v.execution,'not-performed');assert.equal(v.plan.kind,'local');if(v.plan.kind!=='local')return;assert.equal(v.plan.sources[0]?.entity,'Orders.Order');assert.ok(JSON.stringify(v.plan.predicate).includes('customerId'));assert.ok(JSON.stringify(v.plan.predicate).includes('customer'));assert.equal(v.plan.output.kind,'optional');assert.throws(()=>foreign.inspectRead(h),code('ForeignOwner'));assert.throws(()=>owner.checkRead({...v.plan,effects:'create'}as any),code('InvalidContract'));
});
test('actual state transition and expected versions retain pure proposal and native validation boundaries',()=>{
 const h=owner.bindOperation('Orders.RecordCheckoutObservation'),v=owner.inspectOperation(h),tx=v.transactions.find(t=>t.plan.name==='RecordObservation')!;assert.ok(tx);assert.equal(tx.mutations.length,2);for(const m of tx.mutations){assert.equal(m.original_row_required,true);assert.equal(m.expected_version_required,true);assert.equal(m.next_version_check,'original-row+expected-version+exact-one-increment-before-write');assert.ok(m.assigned_fields.includes('version'));}assert.ok(v.pure_call_paths.length>0);assert.ok(JSON.stringify(v.plan).includes('transition'));assert.equal(tx.handler_execution,'original-native-disposition-required;never-label-inferred');assert.equal(tx.provisional_aliases,'escape-only-after-original-commit');
});
test('source contract snapshots cannot add a field discard a version handler or change result',()=>{
 const p=owner.inspectOperation(owner.bindOperation('Orders.PlaceOrder')).plan;
 for(const mutate of [(x:any)=>{x.authorized=true;},(x:any)=>{x.result={kind:'scalar',name:'Bool'};},(x:any)=>{const tx=x.body.find((s:any)=>s.kind==='transaction').transaction;tx.body.find((s:any)=>s.kind==='mutation').fields.pop();},(x:any)=>{x.body.find((s:any)=>s.kind==='transaction').transaction.handlers=[];}]){const x=JSON.parse(JSON.stringify(p));mutate(x);assert.throws(()=>owner.checkOperation(x),code('InvalidContract'));}
});
test('original source pure-call binding is usable and disposed with its parent Operation',()=>{
 const h=owner.bindOperation('Orders.PlaceOrder'),v=owner.inspectOperation(h),pair=owner.bindPureCall(h,v.pure_call_paths[0]!);assert.ok(pair.owner.inspect(pair.handle).caller==='Orders.PlaceOrder');owner.disposeOperation(h);assert.throws(()=>owner.inspectOperation(h),code('DisposedOwner'));assert.throws(()=>pair.owner.assertCurrent(pair.handle),code('DisposedOwner'));
});
test('conformance replay and native protocols cannot be upgraded into invocable local plans',()=>{
 const protocols=original.effects.filter((p:any)=>p.protocol!==null);assert.ok(protocols.length>=2);for(const p of protocols)assert.throws(()=>owner.checkOperation(p),code('UnsupportedCapability'));
});
function sourceEdit(before:string,after:string){let changed=false;const rows=sourceTexts.map(row=>{if(row.path!=='services/orders.alch')return row;assert.ok(row.text.includes(before),'selected actual source fragment absent');changed=true;return {...row,text:row.text.replace(before,after)};});assert.equal(changed,true);return rows;}
test('actual .alch reconstruction rejects omitted create and Event fields',()=>{
 for(const [a,b]of [['      payableMinor <- payableMinor\n',''],['    record-event placed OrderPlaced:\n      metadata <- placedMetadata\n      orderId <- orderId','    record-event placed OrderPlaced:\n      metadata <- placedMetadata']])assert.throws(()=>createCoreCommerceEffectContracts(sourceEdit(a!,b!),assets),code('MissingMapping'));
});
test('actual .alch reconstruction rejects absent next version and mistyped expected version',()=>{
 assert.throws(()=>createCoreCommerceEffectContracts(sourceEdit('      version <- checked-add(order.version, 1)\n',''),assets),code('MissingMapping'));
 assert.throws(()=>createCoreCommerceEffectContracts(sourceEdit('expected-version expectedOrderVersion:','expected-version true:'),assets),code('TypeMismatch'));
});
test('actual .alch reconstruction rejects unguarded transition state and outside-participant mutation',()=>{
 assert.throws(()=>createCoreCommerceEffectContracts(sourceEdit('  requires proposal.tag == "transition" on-false reject invalid-checkout-transition\n',''),assets),code('InvalidContract'));
 assert.throws(()=>createCoreCommerceEffectContracts(sourceEdit('atomic-participants Order, CheckoutProgress, ReplayRecord, OrderPlacedOutbox','atomic-participants Order, CheckoutProgress, ReplayRecord'),assets),code('InvalidContract'));
});
test('actual .alch reconstruction rejects unknown-commit mutation and mismatched successful result',()=>{
 const originalOrders=sourceTexts.find(r=>r.path==='services/orders.alch').text,at=originalOrders.indexOf('operation ConfirmOrder:');assert.ok(at>0);const suffix=originalOrders.slice(at).replace('    on-unknown-commit fail outcome-unknown','    on-unknown-commit return ConfirmOrder(orderId = orderId, expectedOrderVersion = expectedOrderVersion, expectedProgressVersion = expectedProgressVersion)');
 assert.throws(()=>createCoreCommerceEffectContracts(sourceTexts.map(r=>r.path==='services/orders.alch'?{...r,text:originalOrders.slice(0,at)+suffix}:r),assets),code('InvalidContract'));
 assert.throws(()=>createCoreCommerceEffectContracts(sourceEdit('  returns receipt\n','  returns payableMinor\n'),assets),code('TypeMismatch'));
});
test('disposed original read/Operation handles and owner cannot issue transactions',()=>{
 const h=owner.bindOperation('Orders.PlaceOrder'),v=owner.inspectOperation(h),t=owner.bindTransaction(h,v.transactions[0]!.path);owner.disposeOperation(h);assert.throws(()=>owner.inspectTransaction(t),code('DisposedOwner'));const q=owner.bindRead('Orders.GetOrder');owner.disposeRead(q);assert.throws(()=>owner.inspectRead(q),code('DisposedOwner'));foreign.dispose();assert.throws(()=>foreign.bindRead('Orders.GetOrder'),code('DisposedOwner'));
});
test('changed physical source config invalidates original local plans before any execution',()=>{
 const h=owner.bindOperation('Orders.PlaceOrder'),q=owner.bindRead('Orders.GetOrder'),v=owner.inspectOperation(h),pair=owner.bindPureCall(h,v.pure_call_paths[0]!),file=path.join(sourceRoot,'contracts/context.json');writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>owner.inspectOperation(h),code('StaleOwner'));assert.throws(()=>owner.inspectRead(q),code('StaleOwner'));assert.throws(()=>owner.assertCurrent(),code('StaleOwner'));assert.doesNotThrow(()=>owner.dispose());assert.throws(()=>owner.assertCurrent(),code('DisposedOwner'));assert.throws(()=>pair.owner.assertCurrent(pair.handle),code('StaleOwner'));
});
