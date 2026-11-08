/** The checked profile selects one original local transaction and its typed
 * generated scope bindings. It grants no store claim, frame or provider effect. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../src/commerce/commerce-binding-assembly-v1.js';
import {inspectCommerceTransactionSourceScopeV1} from '../src/commerce/commerce-sqlite-transaction-owner-v1.js';
import {createCommerceCommandIdentityBindingOwnerV1,checkCommerceCommandIdentityProfileShapeV1,checkCommerceCommandIdentityScopeV1,deriveCommerceCommandTransactionNamespaceV1} from '../src/commerce/commerce-command-identity-binding-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('captured profile command identity binds exact selected transaction and typed generated scope only',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-command-binding-')),sourceRoot=path.join(root,'source');
 cpSync(candidate,sourceRoot,{recursive:true});
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(sourceRoot),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(sourceRoot,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(sourceRoot,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblies=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblies.assembly();
 let owner:ReturnType<typeof createCommerceCommandIdentityBindingOwnerV1>|undefined;
 try{
  owner=createCommerceCommandIdentityBindingOwnerV1(sources,capture,semantics,semantic,domain,baseline,plans,assemblies,assembly);
  const op=plans.bindOperation('Payments.DispatchOriginalCapture'),operation=plans.inspectOperation(op),transaction=operation.transactions.find(t=>t.plan.name==='MarkDispatched');assert.ok(transaction);
  const bound=owner.bind('Payments.CapturePaymentEntry',op,transaction.path),view=owner.inspect(bound);
  assert.equal(view.invocation_kind,'selected-local-child');
  assert.equal(view.operation.module+'.'+view.operation.name,operation.operation);
  assert.equal(view.transaction_path,transaction.path);assert.equal(view.service,'payments');
  assert.equal(view.transaction_namespace_sha256,deriveCommerceCommandTransactionNamespaceV1(operation.operation,'MarkDispatched'));
  assert.equal(view.root_entry,'Payments.CapturePaymentEntry');assert.equal(view.journal_entry,'Payments.CapturePaymentEntry');
  assert.equal(view.command_id_binding,'attemptKey');assert.equal(view.fingerprint_binding,'requestFingerprint');
  assert.equal(view.profile_path,'profiles/selection.json');assert.equal(view.authority_effect,'none');
  assert.equal((owner as any).claimCommand,undefined);assert.equal((owner as any).apply,undefined);
  const scope=inspectCommerceTransactionSourceScopeV1(plans,op,transaction.path),names=new Set(scope.map(v=>v.name));
  assert.ok(names.has('attemptKey'));assert.ok(names.has('requestFingerprint'));assert.ok(names.has('intent'));
  const rootOp=plans.bindOperation('Payments.CapturePayment'),rootPlan=plans.inspectOperation(rootOp),prepare=rootPlan.transactions.find(t=>t.plan.name==='PrepareCapture');assert.ok(prepare);
  const rootBound=owner.bind('Payments.CapturePaymentEntry',rootOp,prepare.path),rootView=owner.inspect(rootBound);
  assert.throws(()=>plans.bindOperation('Shop.DemoPay.Capture'),code('UnsupportedCapability'));
  assert.equal(rootView.invocation_kind,'selected-root');assert.equal(rootView.service,view.service);
  assert.equal(rootView.journal_entry,view.journal_entry);assert.equal(rootView.transaction_path,prepare.path);
  assert.equal(rootView.transaction_namespace_sha256,deriveCommerceCommandTransactionNamespaceV1(rootPlan.operation,'PrepareCapture'));
  assert.notEqual(rootView.transaction_namespace_sha256,view.transaction_namespace_sha256);
  const rootScope=inspectCommerceTransactionSourceScopeV1(plans,rootOp,prepare.path),rootNames=new Set(rootScope.map(v=>v.name));
  assert.ok(rootNames.has('attemptKey'));assert.ok(rootNames.has('requestFingerprint'));
  for(const [entry,operationName,transactionName,commandPath,fingerprintPath] of [
   ['Inventory.ReserveStockEntry','Inventory.StartStockCommand','PrepareStockCommand','commandId','requestFingerprint'],
   ['Inventory.AllocateStockEntry','Inventory.StartStockCommand','PrepareStockCommand','commandId','requestFingerprint'],
   ['Inventory.ReleaseReservationEntry','Inventory.StartStockCommand','PrepareStockCommand','commandId','requestFingerprint'],
   ['Inventory.ReserveStockEntry','Inventory.RejectStockCommand','RejectStock','command.commandId','command.requestFingerprint'],
   ['Inventory.AllocateStockEntry','Inventory.RejectStockCommand','RejectStock','command.commandId','command.requestFingerprint'],
   ['Inventory.ReleaseReservationEntry','Inventory.RejectStockCommand','RejectStock','command.commandId','command.requestFingerprint'],
   ['Inventory.ReserveStockEntry','Inventory.ReserveStock','ReserveAllLines','commandId','requestFingerprint'],
   ['Inventory.AllocateStockEntry','Inventory.AllocateStock','AllocateAllLines','commandId','requestFingerprint'],
   ['Inventory.ReleaseReservationEntry','Inventory.ReleaseReservation','ReleaseAllLines','commandId','requestFingerprint'],
   ['Orders.PlaceOrderEntry','Orders.PlaceOrder','AcceptCheckout','checkoutKey','fingerprint'],
   ['Orders.ConfirmOrderEntry','Orders.ConfirmOrder','ConfirmCheckout','progress.confirmCommandId','requestFingerprint'],
   ['Orders.CancelOrderEntry','Orders.CancelOrder','CancelCheckout','progress.cancelCommandId','requestFingerprint'],
   ['Orders.RecordCheckoutObservationEntry','Orders.RecordCheckoutObservation','RecordObservation','observationIdentity.commandId','observationIdentity.requestFingerprint'],
   ['Fulfillment.OnOrderConfirmed','Fulfillment.CreateShipment','RecordRepeatedOrderOccurrence','confirmed.metadata.eventId','eventFingerprint'],
   ['Fulfillment.OnOrderConfirmed','Fulfillment.CreateShipment','RequestShipment','confirmed.metadata.eventId','eventFingerprint'],
  ] as const){
   const selected=plans.bindOperation(operationName),named=plans.inspectOperation(selected).transactions.find(t=>t.plan.name===transactionName);assert.ok(named);
   const inspected=owner.inspect(owner.bind(entry,selected,named.path));
   assert.equal(inspected.root_entry,entry);assert.equal(inspected.journal_entry,entry);
   assert.equal(inspected.command_id_binding,commandPath);assert.equal(inspected.fingerprint_binding,fingerprintPath);
  }
  const customerOp=plans.bindOperation('Orders.PlaceOrder'),accept=plans.inspectOperation(customerOp).transactions.find(t=>t.plan.name==='AcceptCheckout');assert.ok(accept);
  assert.equal(owner.inspect(owner.bind('Orders.PlaceOrderEntry',customerOp,accept.path)).principal_scope,'authenticated-principal');
  for(const [name,transactionName] of [['Orders.ClaimCheckoutWork','ClaimWork']] as const){
   const unbound=plans.bindOperation(name),named=plans.inspectOperation(unbound).transactions.find(t=>t.plan.name===transactionName);assert.ok(named);
   assert.throws(()=>owner!.bind('Orders.ClaimCheckoutWorkEntry',unbound,named.path),code('MissingMapping'));
  }
  assert.throws(()=>owner!.inspect({...bound}),code('ForeignOwner'));
  assert.throws(()=>owner!.bind('Payments.NoSuchEntry',op,transaction.path),code('MissingMapping'));
  assert.throws(()=>owner!.bind(view.root_entry,rootOp,'$.body[999].transaction'),code('MissingMapping'));
  assert.throws(()=>inspectCommerceTransactionSourceScopeV1(plans,op,'$.body[999].transaction'),code('UnknownSourcePath'));
  const raw=JSON.parse(readFileSync(path.join(sourceRoot,'profiles/selection.json'),'utf8')).command_identity_bindings;
  const checked=checkCommerceCommandIdentityProfileShapeV1(raw),row=checked.bindings.find(b=>b.invocation_kind==='selected-local-child')!;
  assert.equal(checked.bindings.length,20);
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[null]}),code('InvalidContract'));
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[new Proxy({}, {})]}),code('InvalidContract'));
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[]}),code('InvalidContract'));
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[row,row]}),code('DuplicateSymbol'));
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[{...row,claim:'retry-any'}]}),code('InvalidContract'));
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[{...row,invocation_kind:'anything'}]}),code('InvalidContract'));
  assert.throws(()=>checkCommerceCommandIdentityScopeV1({...row,command_id_binding:'intent'},scope,domain.inspect(baseline).contract.values.refinements),code('TypeMismatch'));
  assert.throws(()=>checkCommerceCommandIdentityScopeV1({...row,fingerprint_binding:'attemptKey'},scope,domain.inspect(baseline).contract.values.refinements),code('InvalidContract'));
  assert.throws(()=>checkCommerceCommandIdentityScopeV1({...row,command_id_binding:'missingBinding'},scope,domain.inspect(baseline).contract.values.refinements),code('UnknownFrameBinding'));
  const values=domain.inspect(baseline).contract.values;
  const nested=checked.bindings.find(b=>b.operation.name==='RejectStockCommand')!;
  const rejectOp=plans.bindOperation('Inventory.RejectStockCommand'),rejectTx=plans.inspectOperation(rejectOp).transactions.find(t=>t.plan.name==='RejectStock')!;
  const rejectScope=inspectCommerceTransactionSourceScopeV1(plans,rejectOp,rejectTx.path);
  assert.equal(checkCommerceCommandIdentityScopeV1(nested,rejectScope,values.refinements,values.records).fingerprint_binding,'command.requestFingerprint');
  assert.throws(()=>checkCommerceCommandIdentityScopeV1({...nested,fingerprint_binding:'command.noSuchField'},rejectScope,values.refinements,values.records),code('UnknownFrameBinding'));
  assert.throws(()=>checkCommerceCommandIdentityScopeV1({...nested,fingerprint_binding:null},rejectScope,values.refinements,values.records),code('AmbiguousFingerprint'));
  assert.throws(()=>checkCommerceCommandIdentityScopeV1({...nested,fingerprint_binding:null},[{name:'command',type:{kind:'refinement',name:'Shop.Values.Identifier'}}],values.refinements,values.records),code('MissingFingerprint'));
  assert.throws(()=>checkCommerceCommandIdentityProfileShapeV1({...raw,bindings:[{...row,root_entry:null}]}),code('InvalidContract'));
 }finally{owner?.dispose();assemblies.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
