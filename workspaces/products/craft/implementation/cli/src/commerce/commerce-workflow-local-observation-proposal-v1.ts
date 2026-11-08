/** Source-selected local Workflow observation data. This owner derives the
 * original observation from a live worker snapshot; it cannot authorize an
 * Entry or commit an Operation. The observation admission owner must recheck
 * this proposal before fresh Auth and at the native invocation boundary.
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
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1}
 from './commerce-worker-context-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceWorkflowExpressionOwnerV1,type CommerceWorkflowExpressionOwnerV1,
 type CommerceWorkflowExpressionHandleV1} from './commerce-workflow-expression-v1.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,
 type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {createCommerceWorkflowResumeSelectorV1} from './commerce-workflow-resume-v1.js';
import {inspectCommerceWorkflowObservationPlanV1} from './commerce-workflow-observation-proposal-v1.js';
import {projectCommerceWorkflowValueToNativeV1} from './commerce-workflow-value-native-v1.js';

export class CommerceWorkflowLocalObservationProposalErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowLocalObservationProposalErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowLocalObservationProposalErrorV1(code);};
const codePin=pinCoreImplementation(import.meta.url,[]);
const field=(value:unknown,name:string):unknown=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InvalidStoredRecord');
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidStoredRecord');
 return descriptor!.value;
};

export interface CommerceWorkflowLocalObservationProposalInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly consumer_entry_id:string;readonly occurrence_id:string;readonly step_name:string;
 readonly entry_id:string;readonly target:string;readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;
 readonly order_version:bigint;readonly progress_version:bigint;
 readonly input:Readonly<{orderId:string;expectedOrderVersion:bigint;
  expectedProgressVersion:bigint;observation:unknown}>;
 readonly causal_projection:Readonly<{progress:unknown}>;
 readonly next_action:Readonly<{kind:'step';target:string}>;
 readonly qualification:'original-local-step-observation-proposal;native-admission-fresh-auth-and-atomic-commit-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowLocalObservationProposalV1 {
 inspect():CommerceWorkflowLocalObservationProposalInspectionV1;
 recheck():CommerceWorkflowLocalObservationProposalInspectionV1;
 assertCurrent():void;
 dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowLocalObservationProposalV1(
 owner:CommerceWorkflowLocalObservationProposalV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');
 owner.assertCurrent();
}

/** The caller supplies only opaque handles from the original owners. Resume
 * selection, source expression, observation input and causal progress are
 * derived again here. A copied inspection has no owner authority. */
export function createCommerceWorkflowLocalObservationProposalV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 storage:CommerceServiceStorageOwnerV1,
 workers:CommerceWorkerContextOwnerV1,worker:CommerceWorkerContextV1,
 snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
 expressions:CommerceWorkflowExpressionOwnerV1,expression:CommerceWorkflowExpressionHandleV1,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
):CommerceWorkflowLocalObservationProposalV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceServiceStorageOwnerV1(storage);assertCommerceWorkerContextOwnerV1(workers);
 assertCommerceWorkflowSnapshotOwnerV1(snapshots);assertCommerceWorkflowExpressionOwnerV1(expressions);
 assertCommerceComputationDomainOwner(domain);
 const source=binding.inspect(),checked=semantics.inspect(semantic),store=storage.inspect(),
  sourceDomain=domain.inspect(baseline),
  observation=source.workflow.drivers.find(row=>row.kind==='observation');
 if(!observation)throw new CommerceWorkflowLocalObservationProposalErrorV1('ForeignSource');
 if(source.owner_service!==store.service||
  checked.source_capture_sha256!==source.source_capture_sha256||
  store.source_capture_sha256!==source.source_capture_sha256||
  sourceDomain.source_capture_sha256!==source.source_capture_sha256)bad('ForeignSource');
 const entry=checked.entries.find(row=>row.id===observation.call.entry);
 if(!entry)bad('ForeignSource');
 const plan=inspectCommerceWorkflowObservationPlanV1(source.workflow,entry!);
 if(plan.target!==observation.call.target||plan.owner_service!==store.service||
  plan.causal_binding!=='causal')bad('UnsupportedObservationEntry');
 const resumes=createCommerceWorkflowResumeSelectorV1(binding,workers);
 let selection:ReturnType<typeof resumes.select>|undefined;
 let initialSelectionInspection:ReturnType<typeof resumes.inspectSelection>|undefined;
 let disposed=false;
 const derive=():CommerceWorkflowLocalObservationProposalInspectionV1=>{
  if(disposed)bad('DisposedOwner');
  codePin.assertCurrent();
  binding.assertCurrent();semantics.assertCurrent(semantic);storage.assertCurrent();
  domain.assertCurrent(baseline);
  workers.assertContextCurrent(worker);snapshots.assertCurrent();expressions.assertCurrent();
  const currentStore=storage.inspect(),currentWorker=workers.inspectContext(worker),
   currentSnapshot=snapshots.recheck(snapshot),expressed=expressions.inspect(expression);
  if(currentStore.store_id!==store.store_id||currentStore.schema_sha256!==store.schema_sha256||
   currentWorker.workflow!==source.workflow.name||currentSnapshot.workflow!==source.workflow.name||
   expressed.workflow!==source.workflow.name||
   currentWorker.source_capture_sha256!==source.source_capture_sha256||
   currentSnapshot.source_capture_sha256!==source.source_capture_sha256||
   expressed.source_capture_sha256!==source.source_capture_sha256||
   domain.inspect(baseline).source_capture_sha256!==source.source_capture_sha256||
   currentWorker.store_id!==store.store_id||currentSnapshot.store_id!==store.store_id||
   currentWorker.consumer_entry_id!==source.workflow.input_entry||
   currentWorker.order_id!==currentSnapshot.order_id||
   currentWorker.worker_id!==currentSnapshot.worker_id||
   currentWorker.worker_epoch!==currentSnapshot.worker_epoch||
   !currentWorker.progress_claim_qualified)bad('ForeignWorkerSnapshot');
  workers.assertOrder(worker,currentWorker.order_id);
  let stepName:string,stepIndex:number,next:string;
  {
   const selected=resumes.select(currentSnapshot.value,worker),decision=resumes.inspectSelection(selected),
    action=decision.action;
   if(decision.outcome!=='selected'||action?.kind!=='step')
    throw new CommerceWorkflowLocalObservationProposalErrorV1('NoSelectedLocalStep');
   stepName=action.target;
   stepIndex=source.workflow.steps.findIndex(row=>row.name===stepName);
   const step=source.workflow.steps[stepIndex];
   if(!step||step.kind!=='local-observation')
    throw new CommerceWorkflowLocalObservationProposalErrorV1('UnsupportedLocalStep');
   if(step.commit_before!==step.next||
    !step.requirements.includes('unknown-inspects-original-observation-before-provider-dispatch')||
    !step.requirements.includes('fresh-acknowledged-local-commit-or-original-never-dispatched-journal-evidence')||
    !step.requirements.includes('snapshot-reread-and-state-match-before-next')||
    expressed.path!=='$.steps['+stepIndex+'].observe'||expressed.callsites.length!==0)
    bad('UnsupportedLocalStep');
   next=step.next;
   resumes.assertSelectionCurrent(selected);
   selection=selected;
   initialSelectionInspection=decision;
  }
  const observed=projectCommerceWorkflowValueToNativeV1(
   expressions.evaluate(expression,{snapshot:currentSnapshot.value}),
   expressed.result,domain.inspect(baseline).contract.values),
   order=storage.inspectStoredRecord('Orders.Order',0,{id:currentWorker.order_id}),
   progress=storage.inspectStoredRecord(source.workflow.durable_state,0,{orderId:currentWorker.order_id});
  // Snapshot custody copies source-typed records to null-prototype data; the
  // repository codec may use ordinary dictionaries for the same exact values.
  if(!order||!progress||field(order,'id')!==currentWorker.order_id||
   field(progress,'orderId')!==currentWorker.order_id||
   field(progress,'version')!==currentSnapshot.progress_version||
   field(progress,'workerEpoch')!==currentWorker.worker_epoch||
   !worker.owns(field(progress,'workerOwner') as Parameters<CommerceWorkerContextV1['owns']>[0],
    currentWorker.worker_epoch)||
   !isDeepStrictEqual(field(currentSnapshot.value,'order'),order,{skipPrototype:true})||
   !isDeepStrictEqual(field(currentSnapshot.value,'progress'),progress,{skipPrototype:true}))bad('StaleWorkerState');
  const orderVersion=field(order,'version');
   if(typeof orderVersion!=='bigint'||orderVersion<1n)
    throw new CommerceWorkflowLocalObservationProposalErrorV1('InvalidStoredRecord');
  const input=coreFreeze({orderId:currentWorker.order_id,expectedOrderVersion:orderVersion,
   expectedProgressVersion:currentSnapshot.progress_version,observation:observed});
  // The second original Query read closes the window across local record
  // checks. Fresh Auth and the generated Operation repeat their own custody.
  snapshots.recheck(snapshot);workers.assertContextCurrent(worker);
  return coreFreeze({workflow:source.workflow.name,source_capture_sha256:source.source_capture_sha256,
   store_id:store.store_id,consumer_entry_id:currentWorker.consumer_entry_id,
   occurrence_id:currentWorker.occurrence_id,step_name:stepName!,entry_id:plan.entry_id,
   target:plan.target,order_id:currentWorker.order_id,worker_id:currentWorker.worker_id,
   worker_epoch:currentWorker.worker_epoch,order_version:orderVersion,
   progress_version:currentSnapshot.progress_version,input,causal_projection:coreFreeze({progress}),
   next_action:coreFreeze({kind:'step' as const,target:next!}),
   qualification:'original-local-step-observation-proposal;native-admission-fresh-auth-and-atomic-commit-required' as const,
   authority_effect:'none' as const});
 };
 const initial=(()=>{try{return derive();}catch(error){resumes.dispose();throw error;}})();
 // Only inert data derived from the immutable original snapshot are retained.
 // Every inspection still rereads the original Query, physical owners and rows.
 const refresh=()=>{
  if(disposed)bad('DisposedOwner');
  codePin.assertCurrent();
  binding.assertCurrent();semantics.assertCurrent(semantic);storage.assertCurrent();
  domain.assertCurrent(baseline);
  workers.assertContextCurrent(worker);snapshots.assertCurrent();expressions.assertCurrent();
  const currentStore=storage.inspect(),currentWorker=workers.inspectContext(worker),
   currentSnapshot=snapshots.recheck(snapshot),expressed=expressions.inspect(expression);
  if(currentStore.store_id!==store.store_id||currentStore.schema_sha256!==store.schema_sha256||
   currentStore.source_capture_sha256!==source.source_capture_sha256||
   currentWorker.workflow!==initial.workflow||currentSnapshot.workflow!==initial.workflow||
   expressed.workflow!==initial.workflow||
   currentWorker.source_capture_sha256!==initial.source_capture_sha256||
   currentSnapshot.source_capture_sha256!==initial.source_capture_sha256||
   expressed.source_capture_sha256!==initial.source_capture_sha256||
   domain.inspect(baseline).source_capture_sha256!==initial.source_capture_sha256||
   currentWorker.store_id!==initial.store_id||currentSnapshot.store_id!==initial.store_id||
   currentWorker.consumer_entry_id!==initial.consumer_entry_id||
   currentWorker.consumer_entry_id!==source.workflow.input_entry||
   currentWorker.occurrence_id!==initial.occurrence_id||
   currentWorker.order_id!==initial.order_id||currentSnapshot.order_id!==initial.order_id||
   currentWorker.worker_id!==initial.worker_id||currentSnapshot.worker_id!==initial.worker_id||
   currentWorker.worker_epoch!==initial.worker_epoch||currentSnapshot.worker_epoch!==initial.worker_epoch||
   currentSnapshot.progress_version!==initial.progress_version||
   !currentWorker.progress_claim_qualified)bad('ForeignWorkerSnapshot');
  const stepIndex=source.workflow.steps.findIndex(row=>row.name===initial.step_name),
   step=source.workflow.steps[stepIndex];
  if(!step||step.kind!=='local-observation'||step.next!==initial.next_action.target||
   step.commit_before!==step.next||
   !step.requirements.includes('unknown-inspects-original-observation-before-provider-dispatch')||
   !step.requirements.includes('fresh-acknowledged-local-commit-or-original-never-dispatched-journal-evidence')||
   !step.requirements.includes('snapshot-reread-and-state-match-before-next')||
   expressed.path!=='$.steps['+stepIndex+'].observe'||expressed.callsites.length!==0)
   bad('UnsupportedLocalStep');
  workers.assertOrder(worker,currentWorker.order_id);
  resumes.assertSelectionCurrent(selection!);
  // The selector's checked AST is retained, but its source-ordered native
  // guard is reevaluated against the current original worker on every check.
  const refreshedSelection=resumes.select(currentSnapshot.value,worker),
   decision=resumes.inspectSelection(refreshedSelection);
  if(decision.outcome!=='selected'||decision.action?.kind!=='step'||
   decision.action.target!==initial.step_name||
   decision.source_case_index!==initialSelectionInspection!.source_case_index)
   bad('NoSelectedLocalStep');
  resumes.assertSelectionCurrent(refreshedSelection);
  const order=storage.inspectStoredRecord('Orders.Order',0,{id:currentWorker.order_id}),
   progress=storage.inspectStoredRecord(source.workflow.durable_state,0,{orderId:currentWorker.order_id});
  if(!order||!progress||field(order,'id')!==currentWorker.order_id||
   field(progress,'orderId')!==currentWorker.order_id||
   field(progress,'version')!==currentSnapshot.progress_version||
   field(progress,'workerEpoch')!==currentWorker.worker_epoch||
   !worker.owns(field(progress,'workerOwner') as Parameters<CommerceWorkerContextV1['owns']>[0],
    currentWorker.worker_epoch)||
   !isDeepStrictEqual(field(currentSnapshot.value,'order'),order,{skipPrototype:true})||
   !isDeepStrictEqual(field(currentSnapshot.value,'progress'),progress,{skipPrototype:true})||
   !isDeepStrictEqual(initial.causal_projection.progress,progress,{skipPrototype:true}))bad('StaleWorkerState');
  const orderVersion=field(order,'version');
  if(typeof orderVersion!=='bigint'||orderVersion<1n)
   throw new CommerceWorkflowLocalObservationProposalErrorV1('InvalidStoredRecord');
  if(orderVersion!==initial.order_version||initial.input.orderId!==currentWorker.order_id||
   initial.input.expectedOrderVersion!==orderVersion||
   initial.input.expectedProgressVersion!==currentSnapshot.progress_version)bad('StaleWorkerState');
  // Preserve the actual second original Query read and final worker custody.
  snapshots.recheck(snapshot);workers.assertContextCurrent(worker);
 };
 const inspect=()=>{refresh();return initial;};
 const owner:CommerceWorkflowLocalObservationProposalV1=Object.freeze({
  inspect,recheck:inspect,assertCurrent:refresh,
  dispose(){if(!disposed){disposed=true;resumes.dispose();}},
 });
 owners.add(owner);return owner;
}
