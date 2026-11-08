/** Source-selected, data-only local Workflow observation. The original
 * expression and snapshot owners remain live for a later native admission;
 * this witness cannot authorize an Entry or provider dispatch by itself.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from '../commerce/commerce-service-storage-v1.js';
import {createCommerceWorkflowResumeSelectorV1,type CommerceWorkflowResumeSelectorV1,
 type CommerceWorkflowResumeSelectionV1} from '../commerce/commerce-workflow-resume-v1.js';
import {createCommerceWorkflowExpressionOwnerV1,type CommerceWorkflowExpressionOwnerV1,
 type CommerceWorkflowExpressionHandleV1} from '../commerce/commerce-workflow-expression-v1.js';
import {assertCommerceWorkflowJournalProgressVersionV1}
 from '../commerce/commerce-workflow-prepared-journal-projection-v1.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from '../commerce/commerce-computation-domain.js';
import {assertCoreCommerceClaimedWorkerSession,type CoreCommerceClaimedWorkerSession} from './core-commerce-worker-claim-executor.js';
import {assertCoreCommerceWorkerSnapshotWitness,type CoreCommerceWorkerSnapshotWitness} from './core-commerce-worker-snapshot-query.js';

export interface CoreCommerceLocalObservationWitness {
 readonly kind:'source-selected-local-workflow-observation';
 readonly expression_owner:CommerceWorkflowExpressionOwnerV1;
 readonly expression:CommerceWorkflowExpressionHandleV1;
 readonly snapshots:CoreCommerceWorkerSnapshotWitness['snapshots'];
 readonly snapshot:CoreCommerceWorkerSnapshotWitness['handle'];
 readonly worker:CoreCommerceClaimedWorkerSession['worker'];
 readonly context:CoreCommerceClaimedWorkerSession['context'];
 inspect():Readonly<{workflow:string;step:string;next:string;observation:unknown;
  order_id:string;order_version:bigint;progress_version:bigint;worker_id:string;
  worker_epoch:bigint;source_capture_sha256:string;store_id:string;
  qualification:'checked-local-observation-data-only;native-admission-and-fresh-auth-required';
  authority_effect:'none'}>;
 dispose():void;
}
const originalWitnesses=new WeakSet<object>();
export function assertCoreCommerceLocalObservationWitness(witness:CoreCommerceLocalObservationWitness):void {
 if(!witness||typeof witness!=='object'||!originalWitnesses.has(witness))
  throw new Error('original source-selected local observation witness required');
 witness.inspect();
}
export interface CoreCommerceWorkerLocalObservationSelector {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;store_id:string;
  qualification:'checked-local-observation-selection-only;native-admission-pending'}>;
 select(session:CoreCommerceClaimedWorkerSession,
  snapshot:CoreCommerceWorkerSnapshotWitness):CoreCommerceLocalObservationWitness;
 assertCurrent():void;
 close():void;
}

export function createCoreCommerceWorkerLocalObservationSelector(input:Readonly<{
 assembly:CommerceApplicationAssemblyV1;
 binding:CommerceWorkflowCoordinationBindingV1;
 storage:CommerceServiceStorageOwnerV1;
 semantics:CoreCommerceSemanticOwner;
 semantic:CoreCommerceSemanticCapture;
 domain:CommerceComputationDomainOwner;
 baseline:CommerceComputationDomainHandle;
}>):CoreCommerceWorkerLocalObservationSelector {
 const {assembly,binding,storage,semantics,semantic,domain,baseline}=input;
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);
 const selected=binding.inspect(),store=storage.inspect();
 if(selected.owner_service!==store.service||selected.source_capture_sha256!==store.source_capture_sha256||
  assembly.inspect().source_capture_sha256!==selected.source_capture_sha256)
  throw new Error('local observation requires one original Workflow and producer store');
 const leases=new Set<()=>void>();let closed=false;
 const current=()=>{
  if(closed)throw new Error('local observation selector closed');
  assembly.assertCurrent();binding.assertCurrent();storage.assertCurrent();
 };
 const owner:CoreCommerceWorkerLocalObservationSelector=Object.freeze({
  inspect(){current();return Object.freeze({workflow:selected.workflow.name,
   source_capture_sha256:selected.source_capture_sha256,store_id:store.store_id,
   qualification:'checked-local-observation-selection-only;native-admission-pending' as const});},
  select(session:CoreCommerceClaimedWorkerSession,
   snapshotWitness:CoreCommerceWorkerSnapshotWitness):CoreCommerceLocalObservationWitness{
   current();assertCoreCommerceClaimedWorkerSession(session);
   assertCoreCommerceWorkerSnapshotWitness(snapshotWitness);
   storage.assertWorkScheduleClaimCurrent(session.claim);
   storage.assertWorkerProgressClaimCurrent(session.progress_claim);
   const worker=session.worker.inspectContext(session.context),progress=storage.inspectWorkerProgressClaim(session.progress_claim),
    snapshot=snapshotWitness.snapshots.recheck(snapshotWitness.handle);
   if(!worker.progress_claim_qualified||worker.workflow!==selected.workflow.name||
    snapshot.workflow!==selected.workflow.name||snapshot.source_capture_sha256!==selected.source_capture_sha256||
    snapshot.store_id!==store.store_id||snapshot.order_id!==worker.order_id||
    snapshot.worker_id!==worker.worker_id||snapshot.worker_epoch!==worker.worker_epoch)
    throw new Error('local observation requires the current original worker snapshot');
   assertCommerceWorkflowJournalProgressVersionV1(progress.progress_version,snapshot.progress_version);
   const resumes=createCommerceWorkflowResumeSelectorV1(binding,session.worker);
   let expressions:CommerceWorkflowExpressionOwnerV1|undefined,retained=false;
   try{
    const selection:CommerceWorkflowResumeSelectionV1=resumes.select(snapshot.value,session.context),
     decision=resumes.inspectSelection(selection);
    const action=decision.action;
    if(decision.outcome!=='selected'||action?.kind!=='step')
     throw new Error('source resume did not select a local observation step');
    const stepIndex=selected.workflow.steps.findIndex(row=>row.name===action.target),
     step=selected.workflow.steps[stepIndex];
    if(stepIndex<0||!step||step.kind!=='local-observation'||
     step.commit_before!==step.next||
     !step.requirements.includes('unknown-inspects-original-observation-before-provider-dispatch')||
     !step.requirements.includes('fresh-acknowledged-local-commit-or-original-never-dispatched-journal-evidence')||
     !step.requirements.includes('snapshot-reread-and-state-match-before-next'))
     throw new Error('selected step lacks checked local observation and provider-dispatch guard');
    expressions=createCommerceWorkflowExpressionOwnerV1(binding,semantics,semantic,domain,baseline);
    const expression=expressions.bind('$.steps['+stepIndex+'].observe'),view=expressions.inspect(expression);
    if(view.workflow!==selected.workflow.name||view.source_capture_sha256!==selected.source_capture_sha256||
     view.callsites.length!==0)
     throw new Error('local observation requires a closed source expression without unbound producers');
    const observation=expressions.evaluate(expression,{snapshot:snapshot.value});
    const value=snapshot.value;
    if(!value||typeof value!=='object'||Array.isArray(value))
     throw new Error('original worker snapshot must contain order data');
    const order=(value as Record<string,unknown>).order;
    if(!order||typeof order!=='object'||Array.isArray(order)||
     typeof (order as Record<string,unknown>).version!=='bigint')
     throw new Error('original worker snapshot must contain current Order version');
    const inspection=Object.freeze({workflow:selected.workflow.name,step:step.name,next:step.next,
     observation,order_id:worker.order_id,order_version:(order as {version:bigint}).version,
     progress_version:snapshot.progress_version,worker_id:worker.worker_id,worker_epoch:worker.worker_epoch,
     source_capture_sha256:selected.source_capture_sha256,store_id:store.store_id,
     qualification:'checked-local-observation-data-only;native-admission-and-fresh-auth-required' as const,
     authority_effect:'none' as const});
    let disposed=false;
    const release=()=>{if(disposed)return;disposed=true;leases.delete(release);
     try{expressions?.dispose();}finally{resumes.dispose();}};
    const witness:CoreCommerceLocalObservationWitness=Object.freeze({
     kind:'source-selected-local-workflow-observation' as const,
     expression_owner:expressions,expression,snapshots:snapshotWitness.snapshots,
     snapshot:snapshotWitness.handle,worker:session.worker,context:session.context,
     inspect(){if(disposed)throw new Error('local observation witness disposed');
      current();resumes.assertSelectionCurrent(selection);
      const refreshed=snapshotWitness.snapshots.recheck(snapshotWitness.handle);
      if(refreshed.progress_version!==inspection.progress_version||
       refreshed.worker_id!==inspection.worker_id||refreshed.worker_epoch!==inspection.worker_epoch)
       throw new Error('local observation snapshot changed');
      expressions!.inspect(expression);return inspection;},
     dispose:release,
    });
    originalWitnesses.add(witness);leases.add(release);retained=true;return witness;
   }finally{if(!retained){expressions?.dispose();resumes.dispose();}}
  },
  assertCurrent:current,
  close(){if(closed)return;closed=true;for(const release of [...leases])release();},
 });
 current();return owner;
}
