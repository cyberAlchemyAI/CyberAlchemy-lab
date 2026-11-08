/** Read-only admission of one original worker observation proposal.
 * The caller cannot supply observation input or causal data. This check does
 * not authorize an Entry, mint an invocation, or commit an Operation.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from './commerce-core-semantic-owner.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from './commerce-service-storage-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1}
 from './commerce-worker-context-v1.js';
import {assertCommerceWorkflowObservationProposalOwnerV1,inspectCommerceWorkflowObservationPlanV1,
 type CommerceWorkflowObservationProposalOwnerV1,type CommerceWorkflowObservationProposalHandleV1,
 type CommerceWorkflowObservationProposalInspectionV1}
 from './commerce-workflow-observation-proposal-v1.js';

export class CommerceWorkflowObservationAdmissionErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowObservationAdmissionErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowObservationAdmissionErrorV1(code);};
const codePin=pinCoreImplementation(import.meta.url,[]);
const field=(value:unknown,name:string):unknown=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InvalidStoredRecord');
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidStoredRecord');
 return descriptor!.value;
};

export interface CommerceWorkflowObservationAdmissionBaseInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;
 readonly entry_id:'Orders.RecordCheckoutObservationEntry';
 readonly target:'Orders.RecordCheckoutObservation';readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;
 readonly input:CommerceWorkflowObservationProposalInspectionV1['input'];
 readonly causal_projection:CommerceWorkflowObservationProposalInspectionV1['causal_projection'];
 readonly qualification:'current-original-proposal-and-worker-observation-data;fresh-auth-and-atomic-commit-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowObservationAdmissionInspectionV1
 extends CommerceWorkflowObservationAdmissionBaseInspectionV1 {
 readonly step_name:string;readonly remote_entry_id:string;
 readonly command_id:string;readonly request_fingerprint:string;
 readonly progress_version:bigint;
}
export interface CommerceWorkflowObservationAdmissionV1 {
 inspect():CommerceWorkflowObservationAdmissionInspectionV1;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
/** Recognition checks the issuing owner and its current source/store/worker,
 * never an inspection copied into an object with the same methods. */
export function assertCommerceWorkflowObservationAdmissionV1(
 owner:CommerceWorkflowObservationAdmissionV1,
):CommerceWorkflowObservationAdmissionInspectionV1 {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');
 return owner.inspect();
}

/** Every inspection rechecks the opaque proposal and the live storage rows.
 * The returned object is data only and is never an Entry authority. */
export function createCommerceWorkflowObservationAdmissionV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 storage:CommerceServiceStorageOwnerV1,
 proposals:CommerceWorkflowObservationProposalOwnerV1,
 proposal:CommerceWorkflowObservationProposalHandleV1,
 workers:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1,
):CommerceWorkflowObservationAdmissionV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceServiceStorageOwnerV1(storage);assertCommerceWorkflowObservationProposalOwnerV1(proposals);
 assertCommerceWorkerContextOwnerV1(workers);codePin.assertCurrent();
 const source=binding.inspect(),checked=semantics.inspect(semantic),store=storage.inspect(),
  observation=source.workflow.drivers.find(driver=>driver.kind==='observation'),
  entry=checked.entries.find(row=>row.id==='Orders.RecordCheckoutObservationEntry');
 if(!entry)bad('ForeignSource');
 if(checked.source_capture_sha256!==source.source_capture_sha256||
  store.source_capture_sha256!==source.source_capture_sha256||store.service!=='orders'||
  source.owner_service!=='orders'||source.workflow.durable_state!=='Orders.CheckoutProgress'||
  !observation||observation.call.entry!==entry!.id)
  bad('ForeignSource');
 const plan=inspectCommerceWorkflowObservationPlanV1(source.workflow,entry!);
 if(plan.entry_id!=='Orders.RecordCheckoutObservationEntry'||
  plan.target!=='Orders.RecordCheckoutObservation'||plan.causal_binding!=='causal')
  bad('UnsupportedObservationEntry');

 const inspect=():CommerceWorkflowObservationAdmissionInspectionV1=>{
  codePin.assertCurrent();binding.assertCurrent();semantics.assertCurrent(semantic);
  const actualStore=storage.inspect(),currentWorker=workers.inspectContext(workerContext),
   proposed=proposals.recheck(proposal);
  if(actualStore.store_id!==store.store_id||actualStore.schema_sha256!==store.schema_sha256||
   actualStore.source_capture_sha256!==source.source_capture_sha256||
   proposed.workflow!==source.workflow.name||currentWorker.workflow!==source.workflow.name||
   proposed.source_capture_sha256!==source.source_capture_sha256||
   currentWorker.source_capture_sha256!==source.source_capture_sha256||
   proposed.store_id!==store.store_id||currentWorker.store_id!==store.store_id||
   proposed.consumer_entry_id!==source.workflow.input_entry||
   currentWorker.consumer_entry_id!==proposed.consumer_entry_id||
   currentWorker.occurrence_id!==proposed.occurrence_id||
   currentWorker.order_id!==proposed.order_id||
   currentWorker.worker_id!==proposed.worker_id||
   currentWorker.worker_epoch!==proposed.worker_epoch||
   !currentWorker.progress_claim_qualified||
   proposed.entry_id!==plan.entry_id||proposed.target!==plan.target||
   proposed.qualification!=='original-result-selected-observation-proposal;fresh-auth-and-atomic-commit-required'||
   proposed.authority_effect!=='none')bad('ForeignProposal');
  workers.assertOrder(workerContext,proposed.order_id);
  const order=storage.inspectStoredRecord('Orders.Order',0,{id:proposed.order_id}),
   progress=storage.inspectStoredRecord(source.workflow.durable_state,0,{orderId:proposed.order_id});
  if(!order||!progress||field(order,'id')!==proposed.order_id||
   field(order,'version')!==proposed.order_version||
   field(progress,'orderId')!==proposed.order_id||
   field(progress,'version')!==proposed.progress_version||
   field(progress,'workerEpoch')!==proposed.worker_epoch||
   !workerContext.owns(field(progress,'workerOwner') as Parameters<CommerceWorkerContextV1['owns']>[0],
    proposed.worker_epoch))bad('StaleWorkerState');
  if(proposed.input.orderId!==proposed.order_id||
   proposed.input.expectedOrderVersion!==proposed.order_version||
   proposed.input.expectedProgressVersion!==proposed.progress_version||
   // Snapshot custody copies records into null-prototype dictionaries. The
   // repository codec may return the same typed record with ordinary nested
   // dictionaries; compare fields and values while ignoring only prototypes.
   !isDeepStrictEqual(proposed.causal_projection.progress,progress,{skipPrototype:true}))bad('StaleProposal');
  // A second recheck closes over the same original proposal and worker after
  // the storage reads; the later Auth/invocation/commit must still recheck.
  proposals.recheck(proposal);workers.assertContextCurrent(workerContext);
  return coreFreeze({workflow:proposed.workflow,source_capture_sha256:proposed.source_capture_sha256,
   store_id:proposed.store_id,consumer_entry_id:proposed.consumer_entry_id,
   occurrence_id:proposed.occurrence_id,
   entry_id:'Orders.RecordCheckoutObservationEntry' as const,
   target:'Orders.RecordCheckoutObservation' as const,order_id:proposed.order_id,
   worker_id:proposed.worker_id,worker_epoch:proposed.worker_epoch,
   step_name:proposed.step_name,remote_entry_id:proposed.remote_entry_id,
   command_id:proposed.command_id,request_fingerprint:proposed.request_fingerprint,
   progress_version:proposed.progress_version,
   input:proposed.input,causal_projection:proposed.causal_projection,
   qualification:'current-original-proposal-and-worker-observation-data;fresh-auth-and-atomic-commit-required' as const,
   authority_effect:'none' as const});
 };
 inspect();const owner:CommerceWorkflowObservationAdmissionV1=Object.freeze({inspect,assertCurrent(){inspect();}});
 owners.add(owner);return owner;
}
