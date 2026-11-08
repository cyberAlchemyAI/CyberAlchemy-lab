/** Original private WorkerContext projection from a committed technical claim.
 * A WorkSchedule claim permits the vacant-predecessor check, but ownership of
 * CheckoutProgress and any step dispatch require later original receipts.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,type CommerceWorkScheduleClaimV1,type CommerceWorkerProgressClaimV1} from './commerce-service-storage-v1.js';
import type {CommerceGeneratedOperationRuntimeV1} from './commerce-generated-operation-runtime-v1.js';
import type {CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-workflow-coordination-binding-v1'+ext,'commerce-service-storage-v1'+ext]);
const where={path:'worker-context',start:0,end:0};
type OptionalIdentifier={readonly kind:'none'}|{readonly kind:'some';readonly value:string};

/** A frozen projection recognized only by its issuing owner. Neither the
 * methods nor the workerId field can mint a command or a remote-call permit. */
export interface CommerceWorkerContextV1 {
 readonly workerId:string;
 owns(owner:OptionalIdentifier,epoch:bigint):boolean;
 isOrdersWorker():boolean;
 provesVacantOrQuiescentPredecessor(owner:OptionalIdentifier,epoch:bigint):boolean;
 provesNeverDispatched(commandId:string):boolean;
}
export interface CommerceWorkerContextInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly schedule_version:bigint;
 readonly prior_worker_owner:OptionalIdentifier;readonly prior_worker_epoch:bigint;
 readonly predecessor_proof:'vacant'|'quiescent';
 readonly progress_claim_qualified:boolean;readonly step_journal_qualified:false;
 readonly qualification:'committed-work-schedule-claim-only;generated-progress-claim-and-step-journal-pending'|'committed-work-schedule-and-progress-claim;step-dispatch-pending';
 readonly authority_effect:'none';
}
export interface CommerceWorkerContextOwnerV1 {
 registerCommittedClaim(claim:CommerceWorkScheduleClaimV1):CommerceWorkerContextV1;
 registerCommittedProgressClaim(context:CommerceWorkerContextV1,runtime:CommerceGeneratedOperationRuntimeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,receipt:object):CommerceWorkerProgressClaimV1;
 inspectContext(context:CommerceWorkerContextV1):CommerceWorkerContextInspectionV1;
 /** Call before attaching a context to any generated Workflow/Operation frame. */
 assertOrder(context:CommerceWorkerContextV1,orderId:string):void;
 assertContextCurrent(context:CommerceWorkerContextV1):void;
 assertCurrent():void;
 dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkerContextOwnerV1(owner:CommerceWorkerContextOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original private WorkerContext owner required');
 owner.assertCurrent();
}
export function createCommerceWorkerContextOwnerV1(binding:CommerceWorkflowCoordinationBindingV1,storage:CommerceServiceStorageOwnerV1):CommerceWorkerContextOwnerV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceServiceStorageOwnerV1(storage);pin.assertCurrent();
 const workflow=binding.inspect(),store=storage.inspect();
 if(workflow.owner_service!==store.service||workflow.source_capture_sha256!==store.source_capture_sha256)
  fail('ForeignOwner',where,'Workflow and technical claim require the same source-selected service store');
 const worker=workflow.workflow.contexts.filter(context=>context.binding==='worker');
 const claimDriver=workflow.workflow.drivers.filter(driver=>driver.kind==='claim');
 if(worker.length!==1||worker[0]!.abi!=='craft.commerce-worker-context/v1-candidate'||claimDriver.length!==1||
    claimDriver[0]!.call.role!=='Operation'||claimDriver[0]!.call.entry.length===0)
  fail('InvalidContract',where,'checked private worker context and claim Entry required');
 const contexts=new WeakMap<object,{claim:CommerceWorkScheduleClaimV1;commitReceipt:object;inspection:CommerceWorkerContextInspectionV1;progressClaim:CommerceWorkerProgressClaimV1|null}>();
 let disposed=false;
 const current=()=>{
  if(disposed)fail('DisposedOwner',where,'WorkerContext owner retired');
  pin.assertCurrent();
  const now=binding.inspect(),actual=storage.inspect();
  if(now.workflow.name!==workflow.workflow.name||now.owner_service!==workflow.owner_service||now.source_capture_sha256!==workflow.source_capture_sha256||
     actual.store_id!==store.store_id||actual.service!==store.service||actual.source_capture_sha256!==store.source_capture_sha256)
   fail('StaleOwner',where,'original Workflow or target store changed');
 };
 const live=(context:CommerceWorkerContextV1)=>{
  current();const row=context&&typeof context==='object'?contexts.get(context):undefined;
  if(!row)fail('ForeignOwner',where,'original registered WorkerContext required');
  storage.assertWorkScheduleClaimCurrent(row.claim);
  if(row.progressClaim)storage.assertWorkerProgressClaimCurrent(row.progressClaim);
  const claim=storage.inspectWorkScheduleClaim(row.claim);
  if(claim.store_id!==row.inspection.store_id||claim.workflow!==row.inspection.workflow||claim.worker_id!==row.inspection.worker_id||
     claim.worker_epoch!==row.inspection.worker_epoch||claim.schedule_version!==row.inspection.schedule_version||
     claim.order_id!==row.inspection.order_id||claim.occurrence_id!==row.inspection.occurrence_id||
     claim.consumer_entry_id!==row.inspection.consumer_entry_id||claim.source_capture_sha256!==row.inspection.source_capture_sha256||
     claim.predecessor_proof!==row.inspection.predecessor_proof||
     claim.prior_worker_epoch!==row.inspection.prior_worker_epoch||
     claim.prior_worker_owner.kind!==row.inspection.prior_worker_owner.kind||
     (claim.prior_worker_owner.kind==='some'&&row.inspection.prior_worker_owner.kind==='some'&&
      claim.prior_worker_owner.value!==row.inspection.prior_worker_owner.value)||
     claim.commit_receipt!==row.commitReceipt)
   fail('StaleOwner',where,'committed WorkSchedule claim no longer matches original WorkerContext');
  return {row,claim};
 };
 const owner:CommerceWorkerContextOwnerV1=Object.freeze({
  registerCommittedClaim(claim:CommerceWorkScheduleClaimV1){
   current();storage.assertWorkScheduleClaimCurrent(claim);const view=storage.inspectWorkScheduleClaim(claim);
   if(view.workflow!==workflow.workflow.name||view.source_capture_sha256!==workflow.source_capture_sha256||view.store_id!==store.store_id||
      view.consumer_entry_id!==workflow.workflow.input_entry||
      !(view.predecessor_proof==='vacant'&&view.prior_worker_owner.kind==='none'||
        view.predecessor_proof==='quiescent'&&view.prior_worker_owner.kind==='some')||
      typeof view.order_id!=='string'||!view.order_id||typeof view.occurrence_id!=='string'||!view.occurrence_id||
      typeof view.worker_id!=='string'||!view.worker_id||typeof view.worker_epoch!=='bigint'||typeof view.prior_worker_epoch!=='bigint'||
      typeof view.schedule_version!=='bigint'||view.worker_epoch!==view.prior_worker_epoch+1n)
    fail('ForeignOwner',where,'exact committed vacant WorkSchedule claim required');
   const inspection:CommerceWorkerContextInspectionV1=coreFreeze({workflow:view.workflow,source_capture_sha256:view.source_capture_sha256,
    store_id:view.store_id,consumer_entry_id:view.consumer_entry_id,occurrence_id:view.occurrence_id,order_id:view.order_id,
    worker_id:view.worker_id,worker_epoch:view.worker_epoch,schedule_version:view.schedule_version,
    prior_worker_owner:view.prior_worker_owner,prior_worker_epoch:view.prior_worker_epoch,
    predecessor_proof:view.predecessor_proof,
    progress_claim_qualified:false,step_journal_qualified:false,
    qualification:'committed-work-schedule-claim-only;generated-progress-claim-and-step-journal-pending',authority_effect:'none'});
   const context:CommerceWorkerContextV1=Object.freeze({
    workerId:view.worker_id,
    owns(this:CommerceWorkerContextV1,candidate:OptionalIdentifier,epoch:bigint){
     if(this!==context)fail('ForeignOwner',where,'original WorkerContext receiver required');
     const {row}=live(context);if(!row.progressClaim)return false;
     const progress=storage.inspectWorkerProgressClaim(row.progressClaim),owner=candidate&&typeof candidate==='object'&&!Array.isArray(candidate)?candidate:null;
     return !!owner&&Object.keys(owner).length===2&&owner.kind==='some'&&owner.value===progress.worker_id&&
      typeof epoch==='bigint'&&epoch===progress.worker_epoch;
    },
    isOrdersWorker(this:CommerceWorkerContextV1){if(this!==context)fail('ForeignOwner',where,'original WorkerContext receiver required');live(context);return true;},
    provesVacantOrQuiescentPredecessor(this:CommerceWorkerContextV1,prior:OptionalIdentifier,epoch:bigint){
     if(this!==context)fail('ForeignOwner',where,'original WorkerContext receiver required');
     const {claim}=live(context);
     const prototype=prior!==null&&typeof prior==='object'?Object.getPrototypeOf(prior):undefined;
     if(prior===null||typeof prior!=='object'||Array.isArray(prior)||
      (prototype!==Object.prototype&&prototype!==null)||typeof epoch!=='bigint'||
      epoch!==claim.prior_worker_epoch)return false;
     if(claim.predecessor_proof==='vacant')return Object.keys(prior).length===1&&prior.kind==='none';
     return claim.predecessor_proof==='quiescent'&&claim.prior_worker_owner.kind==='some'&&
      Object.keys(prior).length===2&&prior.kind==='some'&&prior.value===claim.prior_worker_owner.value;
    },
    provesNeverDispatched(this:CommerceWorkerContextV1,_commandId:string){if(this!==context)fail('ForeignOwner',where,'original WorkerContext receiver required');live(context);return false;},
   });
   contexts.set(context,{claim,commitReceipt:view.commit_receipt,inspection,progressClaim:null});return context;
  },
  registerCommittedProgressClaim(context:CommerceWorkerContextV1,runtime:CommerceGeneratedOperationRuntimeV1,
   selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,receipt:object){
   const {row}=live(context);
   if(row.progressClaim)fail('DuplicateSymbol',where,'WorkerContext already has a committed progress claim');
   const claim=storage.registerCommittedWorkerProgressClaim(binding,row.claim,runtime,selectedAuth,invocation,receipt),
    progress=storage.inspectWorkerProgressClaim(claim);
   if(progress.workflow!==row.inspection.workflow||progress.source_capture_sha256!==row.inspection.source_capture_sha256||
    progress.store_id!==row.inspection.store_id||progress.order_id!==row.inspection.order_id||
    progress.worker_id!==row.inspection.worker_id||progress.worker_epoch!==row.inspection.worker_epoch)
    fail('ForeignOwner',where,'committed progress claim must match the exact WorkerContext');
   row.progressClaim=claim;return claim;
  },
  inspectContext(context:CommerceWorkerContextV1){const {row}=live(context);return row.progressClaim?coreFreeze({...row.inspection,
   progress_claim_qualified:true as const,qualification:'committed-work-schedule-and-progress-claim;step-dispatch-pending' as const}):row.inspection;},
  assertOrder(context:CommerceWorkerContextV1,orderId:string){
   const {row}=live(context);
   if(typeof orderId!=='string'||orderId!==row.inspection.order_id)fail('ForeignOwner',where,'WorkerContext order must match its committed WorkSchedule');
  },
  assertContextCurrent(context:CommerceWorkerContextV1){live(context);},
  assertCurrent:current,
  dispose(){disposed=true;},
 });
 owners.add(owner);current();return owner;
}
