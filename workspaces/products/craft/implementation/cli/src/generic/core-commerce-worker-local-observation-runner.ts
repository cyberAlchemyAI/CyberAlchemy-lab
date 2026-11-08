/** Execute one checked local Workflow observation through fresh worker Entry
 * Auth and the generated Operation, then reread the persisted snapshot before
 * allowing its source-declared successor. No provider call occurs here.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1}
 from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from '../commerce/commerce-service-storage-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,
 type CommerceAuthActorV1} from '../commerce/commerce-entry-context-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1}
 from '../commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceWorkflowLocalObservationProposalV1}
 from '../commerce/commerce-workflow-local-observation-proposal-v1.js';
import {createCommerceWorkflowLocalObservationAdmissionV1}
 from '../commerce/commerce-workflow-local-observation-admission-v1.js';
import {createCommerceWorkflowFreshLocalSuccessorV1,assertCommerceWorkflowFreshLocalSuccessorSnapshotV1,disposeCommerceWorkflowFreshLocalSuccessorV1,type CommerceWorkflowFreshLocalSuccessorV1}
 from '../commerce/commerce-workflow-fresh-local-successor-v1.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture}
 from '../commerce/commerce-core-semantic-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle}
 from '../commerce/commerce-computation-domain.js';
import {createCoreCommerceWorkerActorRegistry} from './core-commerce-worker-actor-registry.js';
import {assertCoreCommerceClaimedWorkerSession,type CoreCommerceClaimedWorkerSession}
 from './core-commerce-worker-claim-executor.js';
import {assertCoreCommerceWorkerSnapshotWitness,type CoreCommerceWorkerSnapshotWitness}
 from './core-commerce-worker-snapshot-query.js';
import type {CoreCommerceWorkerSnapshotQuery} from './core-commerce-worker-snapshot-query.js';
import type {CoreCommerceWorkerLocalObservationSelector}
 from './core-commerce-worker-local-observation.js';

export type CoreCommerceLocalObservationResult=
 Readonly<{kind:'observed';step:string;next:string;observation_entry:string;
  source_capture_sha256:string;commits:1;successor:CommerceWorkflowFreshLocalSuccessorV1;
  qualification:'generated-local-observation-committed-and-successor-snapshot-reread'}>|
 Readonly<{kind:'entry-denied';status:401|403;code:'unauthorized'|'forbidden';authority_effect:'none'}>|
 Readonly<{kind:'observation-not-completed';runtime_outcome:'failed'|'rejected'|'indeterminate';
  commit_disposition:'not-proven'}>|
 Readonly<{kind:'committed-needs-reread';reason:'query-rejected'|'query-failed'|'query-denied'|'successor-mismatch';
  commits:1;next:string}>;

export interface CoreCommerceWorkerLocalObservationRunner {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;store_id:string;
  qualification:'source-selected-local-observation;fresh-auth-generated-commit-and-reread'}>;
 bindActor(actor:CommerceAuthActorV1):readonly string[];
 run(session:CoreCommerceClaimedWorkerSession,
  snapshot:CoreCommerceWorkerSnapshotWitness):Promise<CoreCommerceLocalObservationResult>;
 assertCurrent():void;
 close():void;
}

export function createCoreCommerceWorkerLocalObservationRunner(input:Readonly<{
 assembly:CommerceApplicationAssemblyV1;
 binding:CommerceWorkflowCoordinationBindingV1;
 storage:CommerceServiceStorageOwnerV1;
 auth:CommerceEntryContextOwnerV1;
 selected:CommerceSelectedEntryAuthOwnerV1;
 semantics:CoreCommerceSemanticOwner;
 semantic:CoreCommerceSemanticCapture;
 domain:CommerceComputationDomainOwner;
 baseline:CommerceComputationDomainHandle;
 selector:CoreCommerceWorkerLocalObservationSelector;
 snapshotQuery:CoreCommerceWorkerSnapshotQuery;
}>):CoreCommerceWorkerLocalObservationRunner {
 const {assembly,binding,storage,auth,selected,semantics,semantic,domain,baseline,
  selector,snapshotQuery}=input;
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(storage);assertCommerceEntryContextOwnerV1(auth);
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 const workflow=binding.inspect(),store=storage.inspect(),application=assembly.inspect(),
  checkedDomain=domain.inspect(baseline);
 if(workflow.owner_service!==store.service||workflow.source_capture_sha256!==store.source_capture_sha256||
  application.source_capture_sha256!==workflow.source_capture_sha256||
  checkedDomain.source_capture_sha256!==workflow.source_capture_sha256||
  selector.inspect().workflow!==workflow.workflow.name||
  snapshotQuery.inspect().workflow!==workflow.workflow.name)
  throw new Error('local observation runner requires one original source and producer store');
 const actors=createCoreCommerceWorkerActorRegistry(assembly,auth,workflow.workflow.name);
 const requirements=actors.inspect().requirements;
 let closed=false;
 const current=()=>{
  if(closed)throw new Error('local observation runner closed');
  assembly.assertCurrent();binding.assertCurrent();storage.assertCurrent();
  auth.assertCurrent();selected.assertCurrent();domain.assertCurrent(baseline);
  selector.assertCurrent();snapshotQuery.assertCurrent();
 };
 const owner:CoreCommerceWorkerLocalObservationRunner=Object.freeze({
  inspect(){current();return Object.freeze({workflow:workflow.workflow.name,
   source_capture_sha256:workflow.source_capture_sha256,store_id:store.store_id,
   qualification:'source-selected-local-observation;fresh-auth-generated-commit-and-reread' as const});},
  bindActor(actor:CommerceAuthActorV1){current();return actors.bind(actor);},
  async run(session:CoreCommerceClaimedWorkerSession,
   snapshot:CoreCommerceWorkerSnapshotWitness):Promise<CoreCommerceLocalObservationResult>{
   current();assertCoreCommerceClaimedWorkerSession(session);
   assertCoreCommerceWorkerSnapshotWitness(snapshot);
   const witness=selector.select(session,snapshot);
   try{
    const local=witness.inspect(),proposal=createCommerceWorkflowLocalObservationProposalV1(
     binding,semantics,semantic,storage,session.worker,session.context,
     witness.snapshots,witness.snapshot,witness.expression_owner,witness.expression,
     domain,baseline);
    try{
     const admission=createCommerceWorkflowLocalObservationAdmissionV1(
      binding,semantics,semantic,storage,proposal,session.worker,session.context),
      admitted=admission.inspect();
     if(admitted.local_step!==local.step||admitted.next_step!==local.next||
      admitted.order_id!==local.order_id||admitted.worker_id!==local.worker_id||
      admitted.worker_epoch!==local.worker_epoch||
      admitted.source_capture_sha256!==local.source_capture_sha256||
      admitted.store_id!==local.store_id)
      throw new Error('local observation admission differs from original selected step');
     const matching=requirements.filter(row=>row.usage==='observation'&&row.entry===admitted.entry_id);
     if(matching.length!==1||matching[0]!.target!==admitted.target||
      matching[0]!.target_service!==store.service)
      throw new Error('local observation lacks one exact worker Entry requirement');
     const actor=actors.actorFor('observation'),entry=auth.bindEntry(admitted.entry_id);
     let wire:Uint8Array;
     try{wire=auth.encodeEntryArguments(entry,admitted.input);}
     finally{auth.disposeEntry(entry);}
     const authorized=await selected.beginWorkflowObservation(actor,admitted.entry_id,wire!,
      admitted.input,storage,binding,admission,session.worker,session.context);
     if(!authorized.ok)return Object.freeze({kind:'entry-denied' as const,
      status:authorized.status,code:authorized.code,authority_effect:'none' as const});
     let opened=false;
     try{
      const runtime=await assembly.openGeneratedOperation(authorized.invocation);opened=true;
      const outcome=await runtime.run(authorized.invocation);
      if(outcome.kind!=='returned'){
       if(outcome.kind!=='failed'&&outcome.kind!=='rejected'&&outcome.kind!=='indeterminate')
        throw new Error('generated local observation returned unsupported outcome');
       return Object.freeze({kind:'observation-not-completed' as const,
        runtime_outcome:outcome.kind,commit_disposition:'not-proven' as const});
      }
      if(!Array.isArray(outcome.commits)||outcome.commits.length!==1||
       !outcome.commits[0]||typeof outcome.commits[0]!=='object')
       throw new Error('generated local observation requires one committed native receipt');
      const reread=await snapshotQuery.run(session);
      if(reread.kind!=='snapshot')return Object.freeze({kind:'committed-needs-reread' as const,
       reason:reread.kind==='entry-denied'?'query-denied' as const:
        reread.kind==='rejected'?'query-rejected' as const:'query-failed' as const,
       commits:1 as const,next:local.next});
      let successor:CommerceWorkflowFreshLocalSuccessorV1|undefined;
      try{
       successor=createCommerceWorkflowFreshLocalSuccessorV1(binding,storage,session.worker,session.context,
        runtime,authorized.invocation,outcome);
       const decision=assertCommerceWorkflowFreshLocalSuccessorSnapshotV1(successor,binding,
        session.worker,session.context,reread.snapshots.recheck(reread.handle).value);
       if(decision.local_step!==local.step||decision.next_step!==local.next)
        throw new Error('fresh local successor differs from original source-selected step');
      }catch(error){if(successor)disposeCommerceWorkflowFreshLocalSuccessorV1(successor);throw error;}
      finally{reread.dispose();}
      return Object.freeze({kind:'observed' as const,step:local.step,next:local.next,
       observation_entry:admitted.entry_id,source_capture_sha256:workflow.source_capture_sha256,
       commits:1 as const,successor:successor!,
       qualification:'generated-local-observation-committed-and-successor-snapshot-reread' as const});
     }finally{
      try{if(opened)assembly.releaseGeneratedOperation(authorized.invocation);}
      finally{selected.retire(authorized.invocation);}
     }
    }finally{proposal.dispose();}
   }finally{witness.dispose();}
  },
  assertCurrent:current,close(){closed=true;},
 });
 current();return owner;
}
