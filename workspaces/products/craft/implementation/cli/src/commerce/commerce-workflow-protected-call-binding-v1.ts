/** Data-only join of a durable Dispatched step and its checked causal Entry
 * projection. Fresh Auth and an original target invocation are still required.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkflowDispatchedStepJournalV1} from './commerce-service-storage-v1.js';
import {assertCommerceWorkflowCausalProjectionOwnerV1,type CommerceWorkflowCausalProjectionOwnerV1,
 type CommerceWorkflowCausalProjectionHandleV1} from './commerce-workflow-causal-projection-v1.js';
import type {CommerceWorkflowStepIdentityOwnerV1,CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import type {CommerceWorkflowSnapshotOwnerV1,CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';

export class CommerceWorkflowProtectedCallBindingErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowProtectedCallBindingErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowProtectedCallBindingErrorV1(code);};

export interface CommerceWorkflowProtectedCallInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly caller_service:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;
 readonly step_name:string;readonly entry_id:string;readonly target:string;
 readonly role:'Operation'|'Query';readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly command_id:string;readonly request_fingerprint:string;
 readonly arguments:Readonly<Record<string,unknown>>;
 readonly causal_projection:Readonly<Record<string,unknown>>;
 readonly phase:'Dispatched';
 readonly qualification:'native-dispatched-step-and-original-causal-entry-data;fresh-auth-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowProtectedCallBindingV1 {
 /** Construction-time data only; consumable once before the next microtask.
  * Every later Auth, runtime and effect boundary must call recheck(). */
 initial():CommerceWorkflowProtectedCallInspectionV1;
 inspect():CommerceWorkflowProtectedCallInspectionV1;
 recheck():CommerceWorkflowProtectedCallInspectionV1;
 claimOriginalCall():CommerceWorkflowProtectedCallInspectionV1;
 /** Identity only; recheck() must still run at each admission and effect boundary. */
 hasExactCausalSources(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):boolean;
}
const bindings=new WeakSet<object>();
// A Dispatched handle is issued only by the native Prepared -> Dispatched
// commit. It is process-local and never reconstructed from a stored row after
// reopen. One original call may consume it; later attempts must inspect the
// recorded outcome instead of dispatching the original command again.
const claimedOriginalCalls=new WeakSet<object>();
export function assertCommerceWorkflowProtectedCallBindingV1(
 binding:CommerceWorkflowProtectedCallBindingV1,
):CommerceWorkflowProtectedCallInspectionV1 {
 if(!binding||typeof binding!=='object'||!bindings.has(binding))bad('ForeignOwner');
 return binding.recheck();
}

export function createCommerceWorkflowProtectedCallBindingV1(
 workflow:CommerceWorkflowCoordinationBindingV1,storage:CommerceServiceStorageOwnerV1,
 journal:CommerceWorkflowDispatchedStepJournalV1,causal:CommerceWorkflowCausalProjectionOwnerV1,
 projection:CommerceWorkflowCausalProjectionHandleV1,
):CommerceWorkflowProtectedCallBindingV1 {
 assertCommerceWorkflowCoordinationBindingV1(workflow);assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkflowCausalProjectionOwnerV1(causal);
 const storeMetadata=storage.inspect();
 const inspectCurrent=():CommerceWorkflowProtectedCallInspectionV1=>{
  // The frozen store metadata was captured from this branded owner. The
  // dispatched journal inspection below fully rechecks that owner, its store
  // epoch, original receipts, and native row on every admission/effect path.
  const source=workflow.inspect(),store=storeMetadata,committed=storage.inspectDispatchedWorkflowStepJournal(journal),
   call=causal.recheck(projection),step=source.workflow.steps.find(row=>row.name===committed.step_name);
  if(!step||step.kind!=='remote'||step.call.entry!==committed.target_entry_id||
   source.workflow.name!==committed.workflow||source.owner_service!==store.service||
   source.workflow.input_entry!==committed.consumer_entry_id||
   source.source_capture_sha256!==committed.source_capture_sha256||
   source.source_capture_sha256!==call.source_capture_sha256||
   store.source_capture_sha256!==source.source_capture_sha256||
   store.store_id!==committed.store_id||store.store_id!==call.store_id||
   committed.phase!=='Dispatched'||committed.authority_effect!=='none'||
   call.workflow!==committed.workflow||call.step_name!==committed.step_name||
   call.entry_id!==committed.target_entry_id||call.order_id!==committed.order_id||
   call.worker_id!==committed.worker_id||call.worker_epoch!==committed.worker_epoch||
   call.progress_version!==committed.progress_version||
   call.command_id!==committed.command_id||
   call.request_fingerprint!==committed.request_fingerprint||call.authority_effect!=='none')
   bad('ForeignOwner');
  const remote=step?.kind==='remote'?step:bad('ForeignOwner');
  return coreFreeze({workflow:committed.workflow,source_capture_sha256:committed.source_capture_sha256,
   store_id:committed.store_id,caller_service:source.workflow.owner,
   consumer_entry_id:committed.consumer_entry_id,
   occurrence_id:committed.occurrence_id,step_name:committed.step_name,entry_id:committed.target_entry_id,
   target:remote.call.target,role:remote.call.role,
   order_id:committed.order_id,worker_id:committed.worker_id,worker_epoch:committed.worker_epoch,
   progress_version:committed.progress_version,command_id:committed.command_id,
   request_fingerprint:committed.request_fingerprint,arguments:call.arguments,
   causal_projection:call.projection,phase:'Dispatched' as const,
   qualification:'native-dispatched-step-and-original-causal-entry-data;fresh-auth-required' as const,
   authority_effect:'none' as const});
 };
 const initial=inspectCurrent();
 let initialAvailable=true;
 queueMicrotask(()=>{initialAvailable=false;});
 const takeInitial=()=>{
  if(!initialAvailable)bad('StaleOwner');
  initialAvailable=false;
  return initial;
 };
 const recheck=()=>{
  const current=inspectCurrent();
  if(!isDeepStrictEqual(current,initial))bad('StaleOwner');
  return initial;
 };
 const claimOriginalCall=()=>{
  const current=recheck();
  if(claimedOriginalCalls.has(journal))bad('AlreadyDispatched');
  claimedOriginalCalls.add(journal);
  return current;
 };
 const owner:CommerceWorkflowProtectedCallBindingV1=Object.freeze({initial:takeInitial,inspect:recheck,
  recheck,claimOriginalCall,
  hasExactCausalSources(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
   snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1){
   if(!bindings.has(owner))bad('ForeignOwner');
   return causal.hasExactSourceHandles(projection,identities,identity,snapshots,snapshot);
  }});
 bindings.add(owner);return owner;
}
