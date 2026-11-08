/** Process-local acknowledgement of an original generated local observation.
 * This fact is not an Entry permission or provider dispatch permit. The native
 * step journal, original snapshot and fresh Auth remain separate owners.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,type CommerceFreshLocalObservationCommitV1} from './commerce-service-storage-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1} from './commerce-worker-context-v1.js';
import {assertCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1} from './commerce-generated-operation-runtime-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
export interface CommerceWorkflowFreshLocalSuccessorV1 {readonly kind:'original-fresh-local-workflow-successor/v1-candidate'}
export interface CommerceWorkflowFreshLocalSuccessorInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;
 readonly progress_version:bigint;readonly persisted_state:string;readonly local_step:string;readonly next_step:string;
 readonly qualification:'original-released-fresh-local-commit;native-step-journal-and-fresh-auth-required';readonly authority_effect:'none';
}
const pin=pinCoreImplementation(import.meta.url,[]);
const bad=(code:string):never=>{const error=new Error(code);Object.assign(error,{code});throw error;};
const same=(a:unknown,b:unknown)=>isDeepStrictEqual(a,b,{skipPrototype:true});
const record=(value:unknown):Readonly<Record<string,unknown>>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InvalidLocalSuccessorSnapshot');
 for(const key of Reflect.ownKeys(value as object)){const descriptor=Object.getOwnPropertyDescriptor(value as object,key);if(typeof key!=='string'||!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidLocalSuccessorSnapshot');}
 return value as Readonly<Record<string,unknown>>;
};
type State={binding:CommerceWorkflowCoordinationBindingV1;storage:CommerceServiceStorageOwnerV1;
 workers:CommerceWorkerContextOwnerV1;worker:CommerceWorkerContextV1;receipt:object;commit:CommerceFreshLocalObservationCommitV1;
 disposed:boolean;claim:object|null};
const states=new WeakMap<object,State>(),issuedReceipts=new WeakSet<object>();
const owned=(handle:CommerceWorkflowFreshLocalSuccessorV1)=>{
 pin.assertCurrent();const state=handle&&typeof handle==='object'?states.get(handle):undefined;
 if(!state)bad('ForeignLocalSuccessor');if(state!.disposed)bad('DisposedLocalSuccessor');return state!;
};
function refresh(state:State):CommerceWorkflowFreshLocalSuccessorInspectionV1 {
 pin.assertCurrent();state.binding.assertCurrent();state.storage.assertCurrent();state.workers.assertContextCurrent(state.worker);
 const source=state.binding.inspect(),store=state.storage.inspect(),worker=state.workers.inspectContext(state.worker),commit=state.storage.inspectFreshLocalObservationCommit(state.receipt),local=commit.binding;
 if(!same(commit,state.commit)||source.workflow.name!==local.workflow||source.source_capture_sha256!==local.source_capture_sha256||
  store.store_id!==local.store_id||store.source_capture_sha256!==local.source_capture_sha256||worker.workflow!==local.workflow||
  worker.store_id!==local.store_id||worker.source_capture_sha256!==local.source_capture_sha256||worker.consumer_entry_id!==local.consumer_entry_id||
  worker.occurrence_id!==local.occurrence_id||worker.order_id!==local.order_id||worker.worker_id!==local.worker_id||worker.worker_epoch!==local.worker_epoch||!worker.progress_claim_qualified)
  bad('ForeignLocalSuccessor');
 const step=source.workflow.steps.find(step=>step.name===local.local_step),next=source.workflow.steps.find(step=>step.name===local.next_step),observation=source.workflow.drivers.find(driver=>driver.kind==='observation');
 if(step?.kind!=='local-observation'||step.next!==local.next_step||step.commit_before!==local.next_step||next?.kind!=='remote'||
  !step.requirements.includes('fresh-acknowledged-local-commit-or-original-never-dispatched-journal-evidence')||
  observation?.call.entry!==local.observation_entry_id||observation.call.target!==commit.operation)bad('ForeignLocalSuccessor');
 for(const row of commit.rows){
  const current=state.storage.inspectStoredRecord(row.entity,row.key_index,row.key);
  if(!same(current,row.value))bad('StaleLocalSuccessor');
 }
 const progressRows=commit.rows.filter(row=>row.entity===source.workflow.durable_state);
 if(progressRows.length!==1)bad('InvalidLocalSuccessorSnapshot');
 const progress=record(progressRows[0]!.value),owner=record(progress.workerOwner);
 if(progress.orderId!==local.order_id||typeof progress.version!=='bigint'||progress.version<=local.expected_progress_version||
  progress.workerEpoch!==local.worker_epoch||typeof progress.state!=='string'||owner.kind!=='some'||owner.value!==local.worker_id)bad('StaleLocalSuccessor');
 state.workers.assertContextCurrent(state.worker);state.binding.assertCurrent();
 return coreFreeze({workflow:local.workflow,source_capture_sha256:local.source_capture_sha256,store_id:local.store_id,
  order_id:local.order_id,worker_id:local.worker_id,worker_epoch:local.worker_epoch,progress_version:progress.version as bigint,
  persisted_state:progress.state as string,local_step:local.local_step,next_step:local.next_step,
  qualification:'original-released-fresh-local-commit;native-step-journal-and-fresh-auth-required' as const,authority_effect:'none' as const});
}
export function createCommerceWorkflowFreshLocalSuccessorV1(binding:CommerceWorkflowCoordinationBindingV1,
 storage:CommerceServiceStorageOwnerV1,workers:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,
 runtime:CommerceGeneratedOperationRuntimeV1,invocation:CommerceOperationInvocationHandle,result:unknown):CommerceWorkflowFreshLocalSuccessorV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceServiceStorageOwnerV1(storage);assertCommerceWorkerContextOwnerV1(workers);assertCommerceGeneratedOperationRuntimeV1(runtime);runtime.assertStorage(storage);
 const released=runtime.inspectFreshLocalObservationReturn(invocation,result);
 if(issuedReceipts.has(released.receipt))bad('ReusedLocalAcknowledgement');
 const state:State={binding,storage,workers,worker,receipt:released.receipt,commit:released.commit,disposed:false,claim:null};refresh(state);
 const handle:CommerceWorkflowFreshLocalSuccessorV1=Object.freeze({kind:'original-fresh-local-workflow-successor/v1-candidate'});
 issuedReceipts.add(released.receipt);states.set(handle,state);return handle;
}
export function assertCommerceWorkflowFreshLocalSuccessorSnapshotV1(handle:CommerceWorkflowFreshLocalSuccessorV1,
 binding:CommerceWorkflowCoordinationBindingV1,workers:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,snapshot:unknown):CommerceWorkflowFreshLocalSuccessorInspectionV1 {
 const state=owned(handle);if(state.binding!==binding||state.workers!==workers||state.worker!==worker)bad('ForeignLocalSuccessor');
 const view=refresh(state),source=binding.inspect(),value=record(snapshot),progress=state.commit.rows.find(row=>row.entity===source.workflow.durable_state);
 if(!progress||!same(value.progress,progress.value)||!state.commit.rows.some(row=>row.entity!==source.workflow.durable_state&&same(value.order,row.value)))bad('StaleLocalSuccessor');
 return view;
}
export function claimCommerceWorkflowFreshLocalSuccessorV1(handle:CommerceWorkflowFreshLocalSuccessorV1,
 binding:CommerceWorkflowCoordinationBindingV1,workers:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,snapshot:unknown,selection:object):CommerceWorkflowFreshLocalSuccessorInspectionV1 {
 const state=owned(handle);if(state.claim)bad('ReusedLocalSuccessor');
 const view=assertCommerceWorkflowFreshLocalSuccessorSnapshotV1(handle,binding,workers,worker,snapshot);
 state.claim=selection;return view;
}
export function recheckCommerceWorkflowFreshLocalSuccessorV1(handle:CommerceWorkflowFreshLocalSuccessorV1,selection:object):void {
 const state=owned(handle);if(state.claim!==selection)bad('ForeignLocalSuccessor');refresh(state);
}
export function disposeCommerceWorkflowFreshLocalSuccessorV1(handle:CommerceWorkflowFreshLocalSuccessorV1):void {
 const state=handle&&typeof handle==='object'?states.get(handle):undefined;if(!state)bad('ForeignLocalSuccessor');state!.disposed=true;
}
