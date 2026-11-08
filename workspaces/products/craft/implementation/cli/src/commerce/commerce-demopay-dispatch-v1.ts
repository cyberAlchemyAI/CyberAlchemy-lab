/** Protected DemoPay-v1 Capture dispatch. Only an exact fresh generated
 * MarkDispatched commit may cross the injected byte port, once.
 * Open Questions: docs/COMMERCE-NATIVE-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteV1} from './commerce-demopay-source-site-v1.js';
import {createCommerceDemoPayIntentWitnessOwnerV1,type CommerceDemoPayIntentWitnessV1} from './commerce-demopay-intent-witness-v1.js';
import {createCommerceDemoPayWireOwnerV1,type DemoPayCommerceRawBytePortV1,type DemoPayCommerceObservationV1,type DemoPayCommerceWireResponseV1} from './commerce-demopay-wire-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,type CommerceServiceStorageFreshExecutionV1} from './commerce-service-storage-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {assertCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1} from './commerce-generated-operation-runtime-v1.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {OperationCallV1,EffectPlanV1,TransactionPlanV1,TransactionStepV1,FlowExprV1} from './commerce-data-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-demopay-source-site-v1'+ext,'commerce-demopay-intent-witness-v1'+ext,'commerce-demopay-wire-v1'+ext,'commerce-service-storage-v1'+ext,'commerce-selected-entry-auth-v1'+ext,'commerce-generated-operation-runtime-v1'+ext]);
const headers=Object.freeze({'content-type':'application/json; charset=utf-8','demopay-protocol':'1'});
export class CommerceDemoPayDispatchErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceDemoPayDispatchErrorV1';}}
const bad=(code:string):never=>{throw new CommerceDemoPayDispatchErrorV1(code);};
export interface CommerceDemoPayDispatchPermitV1 {readonly kind:'original-demopay-capture-dispatch-permit/v1-candidate'}
export interface CommerceDemoPayDispatchOwnerV1 {
 prepare(execution:CommerceServiceStorageFreshExecutionV1,runtime:CommerceGeneratedOperationRuntimeV1,selected:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string):CommerceDemoPayDispatchPermitV1;
 send(permit:CommerceDemoPayDispatchPermitV1,deadlineMs?:number):Promise<DemoPayCommerceObservationV1>;
 inspect(witness:CommerceDemoPayIntentWitnessV1,deadlineMs?:number):Promise<DemoPayCommerceObservationV1>;
 assertCurrent():void;dispose():void;
}
type Permit={execution:CommerceServiceStorageFreshExecutionV1;runtime:CommerceGeneratedOperationRuntimeV1;selected:CommerceSelectedEntryAuthOwnerV1;invocation:CommerceOperationInvocationHandle;transactionPath:string};
const owners=new WeakSet<object>();
export function assertCommerceDemoPayDispatchOwnerV1(owner:CommerceDemoPayDispatchOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();
}
function sourceAt(plan:EffectPlanV1,sourcePath:string):unknown {
 if(typeof sourcePath!=='string'||!/^\$(?:\.[A-Za-z_][A-Za-z_0-9]*|\[[0-9]+\])+$/.test(sourcePath)||sourcePath.length>8192)bad('UnknownSourcePath');
 let node:unknown=plan;const parts=sourcePath.slice(1).match(/\.[A-Za-z_][A-Za-z_0-9]*|\[[0-9]+\]/g)??[];
 for(const part of parts){if(!node||typeof node!=='object')bad('UnknownSourcePath');node=(node as Record<string,unknown>)[part[0]==='.'?part.slice(1):part.slice(1,-1)];}
 return node;
}
function sourceRequest(plan:EffectPlanV1,sourcePath:string,transactionPath:string):void {
 const call=sourceAt(plan,sourcePath) as OperationCallV1;
 if(!call||call.target!=='Shop.DemoPay.Capture'||call.entry!==null||call.role!=='Operation'||call.authorization!=='original-local-context-forwarding-required')bad('ForeignSite');
 const tx=sourceAt(plan,transactionPath) as TransactionPlanV1;
 const read=plan.body.find(s=>s.kind==='read'&&s.entity==='Payments.PaymentAttempt');
 const readName=read?.kind==='read'&&read.call===null&&read.key!==null?read.name:bad('ForeignRead');
 const txIndex=/^\$\.body\[(\d+)\]\.transaction$/.exec(transactionPath),callIndex=/^\$\.body\[(\d+)\]\.call$/.exec(sourcePath);
 const txPosition=txIndex?Number(txIndex[1]):bad('ForeignSourceOrder'),callPosition=callIndex?Number(callIndex[1]):bad('ForeignSourceOrder');
 const readIndex=plan.body.indexOf(read!);
 if(readIndex<0||readIndex>=txPosition||txPosition>=callPosition)bad('ForeignSourceOrder');
 const field=(e:FlowExprV1,name:string)=>e.op==='field'&&e.field===name&&e.value.op==='var'&&e.value.name===readName;
 const variant=(e:FlowExprV1,name:string)=>e.op==='enum_value'&&e.variant===name;
 const isPrepared=(e:FlowExprV1)=>e.op==='binary'&&e.operator==='eq'&&
  (field(e.left,'dispatchState')&&variant(e.right,'Prepared')||field(e.right,'dispatchState')&&variant(e.left,'Prepared'));
 if(!plan.body.slice(readIndex+1,txPosition).some(step=>step.kind==='guard'&&isPrepared(step.condition.expression)))bad('ForeignPreparedGuard');
 const mutation=tx?.body?.find((step:TransactionStepV1)=>step.kind==='mutation'&&step.operation==='update'&&step.target==='Payments.PaymentAttempt');
 const update=mutation?.kind==='mutation'?mutation:bad('ForeignTransaction');
 if(!tx||tx.name!=='MarkDispatched'||!tx.participants?.includes('Payments.PaymentAttempt')||
  update.original_row!=='required-for-exact-key-and-store'||update.version_validation!=='original-row+expected-version+exact-one-increment-before-write'||
  !update.expected_version||!field(update.expected_version.expression,'version'))bad('ForeignTransaction');
 const assigned=(name:string)=>update.fields.find(item=>item.name===name)?.value.expression;
 const next=assigned('version');
 if(!assigned('status')||!variant(assigned('status')!,'Pending')||!assigned('dispatchState')||!variant(assigned('dispatchState')!,'Dispatched')||
  !next||next.op!=='binary'||next.operator!=='add'||!field(next.left,'version')||next.right.op!=='literal'||next.right.value!=='1')bad('ForeignDispatchMutation');
 const expected=['attemptKey','orderId','amountMinor','currency'];
 if(call.arguments.length!==expected.length||call.arguments.some((argument,i)=>argument.parameter!==expected[i]||argument.value.expression.op!=='field'||argument.value.expression.value.op!=='var'||argument.value.expression.value.name!==readName||argument.value.expression.field!==expected[i]))bad('ForeignRequestProjection');
}

/** The permit contains an exact native execution, never a caller request.
 * `send` consumes its commit synchronously before creating the first promise. */
export function createCommerceDemoPayDispatchOwnerV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 plans:CommerceLocalPlanOwnerV1,sites:CommerceDemoPaySourceSiteOwnerV1,
 captureSite:CommerceDemoPaySourceSiteV1,inspectSite:CommerceDemoPaySourceSiteV1,
 storage:CommerceServiceStorageOwnerV1,port:DemoPayCommerceRawBytePortV1,
):CommerceDemoPayDispatchOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCommerceLocalPlanOwnerV1(plans);assertCommerceDemoPaySourceSiteOwnerV1(sites);assertCommerceServiceStorageOwnerV1(storage);pin.assertCurrent();
 const original=sources.inspect(capture),captureView=sites.inspect(captureSite),inspectView=sites.inspect(inspectSite),store=storage.inspect();
 if(captureView.method!=='Capture'||captureView.target!=='Shop.DemoPay.Capture'||inspectView.method!=='InspectCapture'||
  captureView.service!==store.service||captureView.source_capture_sha256!==store.source_capture_sha256||captureView.selected_family_sha256!==store.family_sha256||
  inspectView.source_capture_sha256!==store.source_capture_sha256||inspectView.selected_family_sha256!==store.family_sha256||original.capture_sha256!==store.source_capture_sha256)bad('ForeignSite');
 const witnesses=createCommerceDemoPayIntentWitnessOwnerV1(sites,storage),wire=createCommerceDemoPayWireOwnerV1(sources,capture,sites,captureSite,inspectSite,port);
 const permits=new WeakMap<object,Permit>();let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();sources.assertCurrent(capture);plans.assertCurrent();sites.assertCurrent();storage.assertCurrent();wire.assertCurrent();witnesses.assertCurrent();};
 const owner:CommerceDemoPayDispatchOwnerV1=Object.freeze({
  prepare(execution:CommerceServiceStorageFreshExecutionV1,runtime:CommerceGeneratedOperationRuntimeV1,selected:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string){
   current();assertCommerceGeneratedOperationRuntimeV1(runtime);assertCommerceSelectedEntryAuthOwnerV1(selected);runtime.assertStorage(storage);
   const view=selected.inspectInvocation(invocation),operation=selected.operation(invocation),plan=plans.inspectOperation(operation);
   selected.assertSelectedLocalChild(invocation,view.entry,captureView.parent_operation);
   if(view.operation!==captureView.parent_operation||view.service!==store.service||view.source_sha256!==store.source_capture_sha256||
    selected.inspect().family_sha256!==store.family_sha256||plan.plan_sha256!==captureView.parent_plan_sha256||plan.operation!==captureView.parent_operation||
    plan.source_capture_sha256!==store.source_capture_sha256||!plan.transactions.some(t=>t.path===transactionPath))bad('ForeignInvocation');
   sourceRequest(plan.plan,captureView.source_path,transactionPath);
   // Only the storage owner can turn this exact native outcome into a commit;
   // merely preparing the permit does not inspect a row or claim authority.
   const permit=Object.freeze({kind:'original-demopay-capture-dispatch-permit/v1-candidate' as const});
   permits.set(permit,{execution,runtime,selected,invocation,transactionPath});return permit;
  },
  send(permit:CommerceDemoPayDispatchPermitV1,deadlineMs=5000){
   current();const row=(permit&&typeof permit==='object'?permits.get(permit):undefined)??bad('ForeignPermit');
   permits.delete(permit);if(!Number.isSafeInteger(deadlineMs)||deadlineMs<1||deadlineMs>30000)bad('InvalidDeadline');
   // This call is synchronous, one-shot, and occurs before the first await or
   // invocation of the injected byte port. Reopen/foreign results fail here.
   storage.consumeFreshCommit(row.execution,row.runtime,row.selected,row.invocation,row.transactionPath);
   const view=row.selected.inspectInvocation(row.invocation),parameters=row.selected.parameters(row.invocation),attemptKey=parameters.attemptKey,orderId=parameters.orderId,requestFingerprint=parameters.requestFingerprint;
   if(view.operation!==captureView.parent_operation||view.service!==store.service||
    typeof attemptKey!=='string'||typeof orderId!=='string'||typeof requestFingerprint!=='string')bad('ForeignInvocation');
   const record=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:attemptKey as string});
   if(!record||typeof record!=='object'||Array.isArray(record))bad('MissingIntent');
   const attempt=record as Record<string,unknown>;
   if(attempt.attemptKey!==attemptKey||attempt.orderId!==orderId||attempt.requestFingerprint!==requestFingerprint||
    typeof attempt.amountMinor!=='bigint'||attempt.currency!=='USD')bad('ForeignRequest');
   const request=Object.freeze({attemptKey:attempt.attemptKey as string,orderId:attempt.orderId as string,amountMinor:attempt.amountMinor as bigint,currency:'USD' as const,requestFingerprint:attempt.requestFingerprint as string});
   const witness=witnesses.observe(captureSite,request,'Dispatched'),evidence=witnesses.inspect(witness);
   if(evidence.site!==captureView.source_path||evidence.target!=='Shop.DemoPay.Capture'||evidence.store_id!==store.store_id||evidence.dispatch_state!=='Dispatched')bad('ForeignIntent');
   const wireRequest=Object.freeze({attemptKey:request.attemptKey,orderId:request.orderId,amountMinor:request.amountMinor.toString(),currency:'USD' as const});
   const body=wire.encodeCapture(wireRequest),controller=new AbortController();
   const outbound=Object.freeze({origin:'https://demopay.invalid' as const,method:'POST' as const,path:'/v1/capture' as const,headers,body,signal:controller.signal});
   return (async():Promise<DemoPayCommerceObservationV1>=>{
    let timer:ReturnType<typeof setTimeout>|undefined,response:DemoPayCommerceWireResponseV1;
    try{response=await Promise.race([port.exchange(outbound),new Promise<never>((_,reject)=>{timer=setTimeout(()=>{controller.abort();reject(new CommerceDemoPayDispatchErrorV1('Timeout'));},deadlineMs);})]);}
    catch(error){current();witnesses.inspect(witness);return Object.freeze({kind:'unresolved',reason:error instanceof CommerceDemoPayDispatchErrorV1&&error.code==='Timeout'?'timeout':'transport'});}
    finally{if(timer)clearTimeout(timer);}
    current();witnesses.inspect(witness);const observed=wire.parseCapture(wireRequest,response);
    return observed.kind==='observed'&&!observed.matches_request?Object.freeze({kind:'unresolved',reason:'malformed'}):observed;
   })();
  },
  inspect(witness:CommerceDemoPayIntentWitnessV1,deadlineMs?:number){current();return wire.inspect(witnesses,witness,deadlineMs);},
  assertCurrent:current,dispose(){if(disposed)return;disposed=true;wire.dispose();witnesses.dispose();},
 });owners.add(owner);current();return owner;
}
