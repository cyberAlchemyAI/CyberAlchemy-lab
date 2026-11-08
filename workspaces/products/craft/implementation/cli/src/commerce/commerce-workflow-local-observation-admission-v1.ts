/** Read-only admission for a local Workflow observation selected by the
 * original resume and expression owners. Fresh Entry Auth and a generated
 * native transaction remain required before it has an effect.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from './commerce-core-semantic-owner.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from './commerce-service-storage-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,
 type CommerceWorkerContextV1} from './commerce-worker-context-v1.js';
import {inspectCommerceWorkflowObservationPlanV1}
 from './commerce-workflow-observation-proposal-v1.js';
import {assertCommerceWorkflowLocalObservationProposalV1,
 type CommerceWorkflowLocalObservationProposalV1,
 type CommerceWorkflowLocalObservationProposalInspectionV1}
 from './commerce-workflow-local-observation-proposal-v1.js';
import type {CommerceWorkflowObservationAdmissionBaseInspectionV1}
 from './commerce-workflow-observation-admission-v1.js';

export class CommerceWorkflowLocalObservationAdmissionErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowLocalObservationAdmissionErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowLocalObservationAdmissionErrorV1(code);};
const codePin=pinCoreImplementation(import.meta.url,[]);
const field=(value:unknown,name:string):unknown=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InvalidStoredRecord');
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidStoredRecord');
 return descriptor!.value;
};

export interface CommerceWorkflowLocalObservationAdmissionV1 {
 inspect():CommerceWorkflowObservationAdmissionBaseInspectionV1&Readonly<{
  local_step:string;next_step:string;origin:'source-selected-local-observation';
 }>;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowLocalObservationAdmissionV1(
 owner:CommerceWorkflowLocalObservationAdmissionV1,
):ReturnType<CommerceWorkflowLocalObservationAdmissionV1['inspect']> {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');
 return owner.inspect();
}

/** A proposal's data are rechecked against the live worker and durable rows
 * on every inspection. Its private brand is deliberately distinct from the
 * remote-result observation admission. */
export function createCommerceWorkflowLocalObservationAdmissionV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 storage:CommerceServiceStorageOwnerV1,
 proposal:CommerceWorkflowLocalObservationProposalV1,
 workers:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1,
):CommerceWorkflowLocalObservationAdmissionV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkflowLocalObservationProposalV1(proposal);
 assertCommerceWorkerContextOwnerV1(workers);codePin.assertCurrent();
 const source=binding.inspect(),checked=semantics.inspect(semantic),store=storage.inspect(),
  observation=source.workflow.drivers.find(driver=>driver.kind==='observation'),
  entry=checked.entries.find(row=>row.id===observation?.call.entry);
 if(!entry||checked.source_capture_sha256!==source.source_capture_sha256||
  store.source_capture_sha256!==source.source_capture_sha256||store.service!=='orders'||
  source.owner_service!=='orders'||source.workflow.durable_state!=='Orders.CheckoutProgress')
  bad('ForeignSource');
 const plan=inspectCommerceWorkflowObservationPlanV1(source.workflow,entry!);
 if(plan.entry_id!=='Orders.RecordCheckoutObservationEntry'||
  plan.target!=='Orders.RecordCheckoutObservation'||plan.causal_binding!=='causal')
  bad('UnsupportedObservationEntry');

 const inspect=():ReturnType<CommerceWorkflowLocalObservationAdmissionV1['inspect']>=>{
  codePin.assertCurrent();binding.assertCurrent();semantics.assertCurrent(semantic);
  storage.assertCurrent();workers.assertContextCurrent(workerContext);
  const actualStore=storage.inspect(),currentWorker=workers.inspectContext(workerContext),
   proposed:CommerceWorkflowLocalObservationProposalInspectionV1=proposal.recheck(),
   step=source.workflow.steps.find(row=>row.name===proposed.step_name);
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
   !step||step.kind!=='local-observation'||step.next!==proposed.next_action.target||
   step.commit_before!==step.next||
   proposed.entry_id!==plan.entry_id||proposed.target!==plan.target||
   proposed.next_action.kind!=='step'||
   proposed.qualification!==
    'original-local-step-observation-proposal;native-admission-fresh-auth-and-atomic-commit-required'||
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
   !isDeepStrictEqual(proposed.causal_projection.progress,progress,{skipPrototype:true}))bad('StaleProposal');
  proposal.recheck();workers.assertContextCurrent(workerContext);
  return coreFreeze({workflow:proposed.workflow,source_capture_sha256:proposed.source_capture_sha256,
   store_id:proposed.store_id,consumer_entry_id:proposed.consumer_entry_id,
   occurrence_id:proposed.occurrence_id,
   entry_id:'Orders.RecordCheckoutObservationEntry' as const,
   target:'Orders.RecordCheckoutObservation' as const,order_id:proposed.order_id,
   worker_id:proposed.worker_id,worker_epoch:proposed.worker_epoch,
   input:proposed.input,causal_projection:proposed.causal_projection,
   local_step:proposed.step_name,next_step:proposed.next_action.target,
   origin:'source-selected-local-observation' as const,
   qualification:'current-original-proposal-and-worker-observation-data;fresh-auth-and-atomic-commit-required' as const,
   authority_effect:'none' as const});
 };
 inspect();const owner:CommerceWorkflowLocalObservationAdmissionV1=
  Object.freeze({inspect,assertCurrent(){inspect();}});
 owners.add(owner);return owner;
}
