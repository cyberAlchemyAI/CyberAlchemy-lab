import type {CommerceWorkflowFreshLocalSuccessorV1} from '../commerce/commerce-workflow-fresh-local-successor-v1.js';
/** Continue one original worker from a live source-owned snapshot. Resume
 * selection is inert; only the native storage owner may prepare the selected
 * step journal. No provider dispatch or observation is inferred here.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceWorkflowStepJournalV1,type CommerceWorkflowStepJournalResultV1} from '../commerce/commerce-service-storage-v1.js';
import {createCommerceWorkflowResumeSelectorV1,type CommerceWorkflowResumeSelectorV1,
 type CommerceWorkflowResumeSelectionV1,type CommerceWorkflowResumeInspectionV1} from '../commerce/commerce-workflow-resume-v1.js';
import {createCommerceIdentityCallOwner} from '../commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,
 type CommerceWorkflowStepIdentityHandleV1,type CommerceWorkflowStepIdentityInspectionV1}
 from '../commerce/commerce-workflow-step-identity-v1.js';
import {assertCommerceWorkflowJournalProgressVersionV1}
 from '../commerce/commerce-workflow-prepared-journal-projection-v1.js';
import {inspectCommerceWorkflowTerminalV1,type CommerceWorkflowTerminalResultV1}
 from '../commerce/commerce-workflow-terminal-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import type {CoreCommerceStageSourceOwner} from '../commerce/commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from '../commerce/commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from '../commerce/commerce-computation-domain.js';
import {assertCoreCommerceClaimedWorkerSession,type CoreCommerceClaimedWorkerSession} from './core-commerce-worker-claim-executor.js';
import {assertCoreCommerceWorkerSnapshotWitness,type CoreCommerceWorkerSnapshotWitness} from './core-commerce-worker-snapshot-query.js';

type UnpreparedStep=Exclude<CommerceWorkflowStepJournalResultV1,{kind:'prepared'}>;
export interface CoreCommercePreparedWorkerStep {
 readonly kind:'prepared-step';
 readonly decision:CommerceWorkflowResumeInspectionV1;
 readonly resumes:CommerceWorkflowResumeSelectorV1;
 readonly selection:CommerceWorkflowResumeSelectionV1;
 readonly identities:CommerceWorkflowStepIdentityOwnerV1;
 readonly identity:CommerceWorkflowStepIdentityHandleV1;
 readonly identity_inspection:CommerceWorkflowStepIdentityInspectionV1;
 readonly journal:CommerceWorkflowStepJournalV1;
 readonly snapshots:CoreCommerceWorkerSnapshotWitness['snapshots'];
 readonly snapshot:CoreCommerceWorkerSnapshotWitness['handle'];
 readonly qualification:'source-selected-remote-step-and-original-Prepared-journal;dispatch-pending';
 assertCurrent():void;
 dispose():void;
}
export type CoreCommerceWorkerContinuationResult=CoreCommercePreparedWorkerStep|
 CommerceWorkflowTerminalResultV1|
 Readonly<{kind:'suspended';decision:CommerceWorkflowResumeInspectionV1;authority_effect:'none'}>|
 Readonly<{kind:'local-observation-needed';decision:CommerceWorkflowResumeInspectionV1;
  step:string;authority_effect:'none'}>|
 Readonly<{kind:'journal-state';decision:CommerceWorkflowResumeInspectionV1;
  journal:UnpreparedStep;authority_effect:'none'}>;
export interface CoreCommerceWorkerContinuation {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;store_id:string;
  qualification:'source-selected-resume-and-step-preparation-only;dispatch-pending'}>;
 prepareNext(session:CoreCommerceClaimedWorkerSession,
  witness:CoreCommerceWorkerSnapshotWitness,successor?:CommerceWorkflowFreshLocalSuccessorV1):Promise<CoreCommerceWorkerContinuationResult>;
 assertCurrent():void;
 close():void;
}
const preparedSteps=new WeakSet<object>();
export function assertCoreCommercePreparedWorkerStep(step:CoreCommercePreparedWorkerStep):void {
 if(!step||typeof step!=='object'||!preparedSteps.has(step))
  throw new Error('original prepared Workflow step required');
 step.assertCurrent();
}

export function createCoreCommerceWorkerContinuation(input:Readonly<{
 assembly:CommerceApplicationAssemblyV1;
 binding:CommerceWorkflowCoordinationBindingV1;
 storage:CommerceServiceStorageOwnerV1;
 sources:CoreCommerceSourceOwner;
 capture:CoreCommerceSourceCapture;
 semantics:CoreCommerceSemanticOwner;
 semantic:CoreCommerceSemanticCapture;
 stage:CoreCommerceStageSourceOwner;
 source:CommerceSourceHandle;
 domain:CommerceComputationDomainOwner;
 baseline:CommerceComputationDomainHandle;
 directoryRoot:string;
}>):CoreCommerceWorkerContinuation {
 const {assembly,binding,storage,sources,capture,semantics,semantic,stage,source,domain,baseline,directoryRoot}=input;
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);
 if(typeof directoryRoot!=='string'||!path.isAbsolute(directoryRoot)||path.normalize(directoryRoot)!==directoryRoot)
  throw new Error('absolute original worker continuation directory required');
 const selected=binding.inspect(),store=storage.inspect();
 if(selected.owner_service!==store.service||selected.source_capture_sha256!==store.source_capture_sha256||
  assembly.inspect().source_capture_sha256!==selected.source_capture_sha256)
  throw new Error('worker continuation requires one original Workflow/service/source');
 const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
 const leases=new Set<()=>void>();
 let closed=false,number=0;
 const current=()=>{
  if(closed)throw new Error('worker continuation closed');
  assembly.assertCurrent();binding.assertCurrent();storage.assertCurrent();
  if(storage.inspect().store_id!==store.store_id||binding.inspect().source_capture_sha256!==selected.source_capture_sha256)
   throw new Error('worker continuation source or store changed');
 };
 const owner:CoreCommerceWorkerContinuation=Object.freeze({
  inspect(){current();return Object.freeze({workflow:selected.workflow.name,
   source_capture_sha256:selected.source_capture_sha256,store_id:store.store_id,
   qualification:'source-selected-resume-and-step-preparation-only;dispatch-pending' as const});},
  async prepareNext(session:CoreCommerceClaimedWorkerSession,
   witness:CoreCommerceWorkerSnapshotWitness,successor?:CommerceWorkflowFreshLocalSuccessorV1):Promise<CoreCommerceWorkerContinuationResult>{
   current();assertCoreCommerceClaimedWorkerSession(session);assertCoreCommerceWorkerSnapshotWitness(witness);
   storage.assertWorkScheduleClaimCurrent(session.claim);
   storage.assertWorkerProgressClaimCurrent(session.progress_claim);
   const worker=session.worker.inspectContext(session.context),claim=storage.inspectWorkScheduleClaim(session.claim),
    progress=storage.inspectWorkerProgressClaim(session.progress_claim),snapshot=witness.snapshots.recheck(witness.handle);
   if(!worker.progress_claim_qualified||claim.store_id!==store.store_id||
    claim.workflow!==selected.workflow.name||claim.order_id!==worker.order_id||
    claim.worker_id!==worker.worker_id||progress.worker_id!==worker.worker_id||
    snapshot.workflow!==selected.workflow.name||snapshot.source_capture_sha256!==selected.source_capture_sha256||
    snapshot.store_id!==store.store_id||snapshot.order_id!==worker.order_id||
    snapshot.worker_id!==worker.worker_id||snapshot.worker_epoch!==worker.worker_epoch)
    throw new Error('original current worker and snapshot witness must share one committed progress claim');
   assertCommerceWorkflowJournalProgressVersionV1(progress.progress_version,snapshot.progress_version);
   const resumes=createCommerceWorkflowResumeSelectorV1(binding,session.worker);
   let identities:CommerceWorkflowStepIdentityOwnerV1|undefined,retained=false;
   try{
    const selection=successor?resumes.selectLocalSuccessor(snapshot.value,session.context,successor):
     resumes.select(snapshot.value,session.context),decision=resumes.inspectSelection(selection);
    if(decision.outcome==='suspend-same-persisted-state')
     return Object.freeze({kind:'suspended' as const,decision,authority_effect:'none' as const});
    const action=decision.action;
    if(decision.outcome==='selected'&&action?.kind==='finish')
     return inspectCommerceWorkflowTerminalV1({sources,capture,semantics,semantic,binding,
      domain,baseline,storage,snapshots:witness.snapshots,snapshot:witness.handle,
      resumes,selection});
    if(decision.outcome!=='selected'||action?.kind!=='step')
     throw new Error('selected Workflow continuation requires one original remote step');
    const selectedStep=selected.workflow.steps.find(row=>row.name===action.target);
    if(!selectedStep)throw new Error('source-selected Workflow step is absent');
    if(selectedStep.kind==='local-observation')
     return Object.freeze({kind:'local-observation-needed' as const,decision,
      step:selectedStep.name,authority_effect:'none' as const});
    if(selectedStep.kind!=='remote')
     throw new Error('selected Workflow review step requires a separate original owner');
    identities=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,calls,
     stage,source,domain,baseline,path.join(directoryRoot,'identity-'+(++number)));
    const identity=identities.derive(resumes,selection,witness.snapshots,witness.handle),
     identityInspection=identities.inspect(identity);
    if(identityInspection.step_name!==action.target||
     identityInspection.workflow!==selected.workflow.name||
     identityInspection.store_id!==store.store_id||
     identityInspection.worker_id!==worker.worker_id)
     throw new Error('source-selected step identity differs from current WorkerContext');
    const result=storage.prepareWorkflowStepJournal(binding,session.claim,session.progress_claim,identities,identity);
    if(result.kind!=='prepared')return Object.freeze({kind:'journal-state' as const,decision,
     journal:result,authority_effect:'none' as const});
    let disposed=false;
    const release=()=>{if(disposed)return;disposed=true;leases.delete(release);
     try{identities?.dispose();}finally{resumes.dispose();}};
    const prepared:CoreCommercePreparedWorkerStep=Object.freeze({kind:'prepared-step' as const,decision,
     resumes,selection,identities,identity,identity_inspection:identityInspection,journal:result.journal,
     snapshots:witness.snapshots,snapshot:witness.handle,
     qualification:'source-selected-remote-step-and-original-Prepared-journal;dispatch-pending' as const,
     assertCurrent(){if(disposed)throw new Error('prepared Workflow step disposed');
      storage.assertWorkflowStepJournalCurrent(result.journal);identities!.recheck(identity);
      witness.snapshots.recheck(witness.handle);},dispose:release});
    preparedSteps.add(prepared);leases.add(release);retained=true;return prepared;
   }finally{if(!retained){identities?.dispose();resumes.dispose();}}
  },
  assertCurrent:current,
  close(){if(closed)return;closed=true;for(const release of [...leases])release();},
 });
 current();return owner;
}
