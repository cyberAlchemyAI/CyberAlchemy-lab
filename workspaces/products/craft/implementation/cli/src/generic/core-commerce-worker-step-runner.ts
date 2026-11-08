/** Execute one source-selected remote Workflow step through the original
 * journal, causal Entry, native Auth, generated target Operation, branch, and
 * generated observation Operation. This is one step, not a whole worker loop.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from '../commerce/commerce-service-storage-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceAuthActorV1} from '../commerce/commerce-entry-context-v1.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from '../commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceIdentityCallOwner} from '../commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowCausalProjectionOwnerV1} from '../commerce/commerce-workflow-causal-projection-v1.js';
import {createCommerceWorkflowProtectedCallBindingV1} from '../commerce/commerce-workflow-protected-call-binding-v1.js';
import {createCommerceWorkflowBranchSelectionOwnerV1} from '../commerce/commerce-workflow-branch-selection-v1.js';
import {createCommerceWorkflowRemoteResultOwnerV1,type CommerceWorkflowRemoteExecutionV1} from '../commerce/commerce-workflow-remote-result-v1.js';
import type {CommerceDemoPayDispatchOwnerV1} from '../commerce/commerce-demopay-dispatch-v1.js';
import {createCommerceWorkflowQueryResultOwnerV1,type CommerceWorkflowQueryExecutionV1} from '../commerce/commerce-workflow-query-result-v1.js';
import {createCommerceWorkflowObservationProposalOwnerV1} from '../commerce/commerce-workflow-observation-proposal-v1.js';
import {createCommerceWorkflowObservationAdmissionV1} from '../commerce/commerce-workflow-observation-admission-v1.js';
import {createCommerceSourceQueryOutputCodecV1,type CommerceSourceQueryOutputCodecV1} from '../commerce/commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1,type CommerceSourceQueryRuntimeV1} from '../commerce/commerce-source-query-runtime-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import type {CoreCommerceStageSourceOwner} from '../commerce/commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from '../commerce/commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from '../commerce/commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1,CommerceLocalReadHandleV1} from '../commerce/commerce-local-plan-owner-v1.js';
import {selectCoreCommerceExternalQueries} from './core-commerce-external-query-selection.js';
import {createCoreCommerceWorkerActorRegistry} from './core-commerce-worker-actor-registry.js';
import {assertCoreCommerceClaimedWorkerSession,type CoreCommerceClaimedWorkerSession} from './core-commerce-worker-claim-executor.js';
import {assertCoreCommerceWorkerSnapshotWitness,type CoreCommerceWorkerSnapshotWitness} from './core-commerce-worker-snapshot-query.js';
import {assertCoreCommercePreparedWorkerStep,type CoreCommercePreparedWorkerStep} from './core-commerce-worker-continuation.js';

export type CoreCommerceWorkerStepResult=
 Readonly<{kind:'observed';step:string;remote_entry:string;observation_entry:string;
  source_capture_sha256:string;next_action:unknown;commits:number;
  qualification:'original-remote-result-and-generated-observation-committed'}>|
 Readonly<{kind:'terminal-ready';step:string;remote_entry:string;next_action:unknown;
  commits:0;authority_effect:'none';
  qualification:'original-protected-query-inspected-existing-commit;fresh-terminal-snapshot-required'}>|
 Readonly<{kind:'terminal-ready';step:string;remote_entry:string;next_action:unknown;
  commits:number;authority_effect:'committed';
  qualification:'original-generated-same-service-commit;fresh-terminal-snapshot-required'}>|
 Readonly<{kind:'journal-state';state:'not-ready'|'conflict'|'unavailable'|'indeterminate';authority_effect:'none'}>|
 Readonly<{kind:'entry-denied';stage:'remote'|'observation';status:401|403;
  code:'unauthorized'|'forbidden';journal_phase:'Dispatched';authority_effect:'none'}>|
 Readonly<{kind:'remote-not-completed';runtime_outcome:'failed'|'rejected'|'indeterminate';
  journal_phase:'Dispatched';authority_effect:'none'|'committed'|'indeterminate'}>|
 Readonly<{kind:'branch-suspended';journal_phase:'Dispatched';authority_effect:'none'}>|
 Readonly<{kind:'observation-not-completed';runtime_outcome:'failed'|'rejected'|'indeterminate';
  journal_phase:'Dispatched';authority_effect:'none'}>;

export interface CoreCommerceWorkerStepRunner {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;store_id:string;
  qualification:'one-original-remote-step-through-generated-observation;worker-loop-pending'}>;
 bindActor(actor:CommerceAuthActorV1):readonly string[];
 run(session:CoreCommerceClaimedWorkerSession,witness:CoreCommerceWorkerSnapshotWitness,
  prepared:CoreCommercePreparedWorkerStep):Promise<CoreCommerceWorkerStepResult>;
 assertCurrent():void;
 close():void;
}

export function createCoreCommerceWorkerStepRunner(input:Readonly<{
 assembly:CommerceApplicationAssemblyV1;
 binding:CommerceWorkflowCoordinationBindingV1;
 producerStorage:CommerceServiceStorageOwnerV1;
 serviceStores:ReadonlyMap<string,CommerceServiceStorageOwnerV1>;
 auth:CommerceEntryContextOwnerV1;
 selected:CommerceSelectedEntryAuthOwnerV1;
 sources:CoreCommerceSourceOwner;
 capture:CoreCommerceSourceCapture;
 semantics:CoreCommerceSemanticOwner;
 semantic:CoreCommerceSemanticCapture;
 stage:CoreCommerceStageSourceOwner;
 source:CommerceSourceHandle;
 domain:CommerceComputationDomainOwner;
 baseline:CommerceComputationDomainHandle;
 plans:CommerceLocalPlanOwnerV1;
  demoPayDispatch?:CommerceDemoPayDispatchOwnerV1;
 directoryRoot:string;
}>):CoreCommerceWorkerStepRunner {
 const {assembly,binding,producerStorage,serviceStores,auth,selected,sources,capture,
   semantics,semantic,stage,source,domain,baseline,plans,demoPayDispatch,directoryRoot}=input;
 assertCommerceApplicationAssemblyV1(assembly);assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceServiceStorageOwnerV1(producerStorage);assertCommerceEntryContextOwnerV1(auth);
 assertCommerceSelectedEntryAuthOwnerV1(selected);
 if(typeof directoryRoot!=='string'||!path.isAbsolute(directoryRoot)||path.normalize(directoryRoot)!==directoryRoot)
  throw new Error('absolute original worker step directory required');
 const workflow=binding.inspect(),producer=producerStorage.inspect(),application=assembly.inspect();
 if(workflow.owner_service!==producer.service||workflow.source_capture_sha256!==producer.source_capture_sha256||
  application.source_capture_sha256!==workflow.source_capture_sha256)
  throw new Error('worker step requires exact original Workflow, source, and producer store');
 const actors=createCoreCommerceWorkerActorRegistry(assembly,auth,workflow.workflow.name);
 const requirements=actors.inspect().requirements;
 const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
 let closed=false,serial=0;
 const current=()=>{
  if(closed)throw new Error('worker step runner closed');
  // Actor registry rechecks this exact assembly and Auth owner.
  binding.assertCurrent();producerStorage.assertCurrent();
  selected.assertCurrent();actors.assertCurrent();
 };
 const owner:CoreCommerceWorkerStepRunner=Object.freeze({
  inspect(){current();return Object.freeze({workflow:workflow.workflow.name,
   source_capture_sha256:workflow.source_capture_sha256,store_id:producer.store_id,
   qualification:'one-original-remote-step-through-generated-observation;worker-loop-pending' as const});},
  bindActor(actor:CommerceAuthActorV1){current();return actors.bind(actor);},
  async run(session:CoreCommerceClaimedWorkerSession,witness:CoreCommerceWorkerSnapshotWitness,
   prepared:CoreCommercePreparedWorkerStep):Promise<CoreCommerceWorkerStepResult>{
   current();assertCoreCommerceClaimedWorkerSession(session);
   assertCoreCommerceWorkerSnapshotWitness(witness);assertCoreCommercePreparedWorkerStep(prepared);
   if(prepared.snapshots!==witness.snapshots||prepared.snapshot!==witness.handle||
    prepared.identity_inspection.workflow!==workflow.workflow.name||
    prepared.identity_inspection.worker_id!==session.context.workerId||
    prepared.identity_inspection.store_id!==producer.store_id)
    throw new Error('prepared step, snapshot, and original worker session differ');
   const action=prepared.decision.action;
   if(prepared.decision.outcome!=='selected'||action?.kind!=='step')
    throw new Error('original selected remote Workflow step required');
   const remoteRequirement=requirements.filter(row=>row.usage==='remote'&&row.step===action.target);
   if(remoteRequirement.length!==1||remoteRequirement[0]!.entry!==prepared.identity_inspection.target_entry_id||
    remoteRequirement[0]!.caller_service!==producer.service)
    throw new Error('source-selected remote step lacks exact protected Entry requirement');
   const causal=await createCommerceWorkflowCausalProjectionOwnerV1(binding,semantics,semantic,calls,
    stage,source,domain,baseline,path.join(directoryRoot,'causal-'+(++serial)));
   try{
    const projection=causal.derive(prepared.identities,prepared.identity,prepared.resumes,prepared.selection,
     witness.snapshots,witness.handle);
    const dispatched=producerStorage.markWorkflowStepDispatched(binding,prepared.journal,
     prepared.identities,prepared.identity);
    if(dispatched.kind!=='dispatched')return Object.freeze({kind:'journal-state' as const,
     state:dispatched.kind,authority_effect:'none' as const});
    const protectedCall=createCommerceWorkflowProtectedCallBindingV1(binding,producerStorage,
     dispatched.journal,causal,projection),call=protectedCall.initial();
    const target=serviceStores.get(remoteRequirement[0]!.target_service);
    if(!target)throw new Error('source-selected remote service storage not open');
    assertCommerceServiceStorageOwnerV1(target);
    const targetView=target.inspect();
    if(targetView.service!==remoteRequirement[0]!.target_service||
     targetView.source_capture_sha256!==workflow.source_capture_sha256||
     call.entry_id!==remoteRequirement[0]!.entry||call.target!==remoteRequirement[0]!.target||
     (call.role!=='Operation'&&call.role!=='Query'))
     throw new Error('protected remote Entry requires a selected original Operation or Query service');
    const actor=actors.actorFor('remote',action.target);
    const remoteEntry=auth.bindEntry(call.entry_id);
    let remoteWire:Uint8Array;
    let workerLifetime:ReturnType<typeof auth.inspectEntry>['access']['worker_lifetime'];
    try{
     workerLifetime=auth.inspectEntry(remoteEntry).access.worker_lifetime;
     remoteWire=auth.encodeEntryArguments(remoteEntry,call.arguments);
    }
    finally{auth.disposeEntry(remoteEntry);}
    if(workerLifetime!=='not-applicable'&&workerLifetime!=='requires-original-local-worker-owner')
     throw new Error('source-selected remote Entry has unsupported worker lifetime');
    if(workerLifetime==='requires-original-local-worker-owner'&&targetView.service!==producer.service)
     throw new Error('source-selected worker Entry must target its original worker service');
    const started=workerLifetime==='requires-original-local-worker-owner'?
     await selected.beginWorkflowWorkerStep(actor,call.entry_id,remoteWire!,call.arguments,
      producerStorage,binding,protectedCall,session.worker,session.context):
     await selected.beginWorkflowServiceStep(actor,call.entry_id,remoteWire!,call.arguments,protectedCall);
    if(!started.ok)return Object.freeze({kind:'entry-denied' as const,stage:'remote' as const,
     status:started.status,code:started.code,journal_phase:'Dispatched' as const,authority_effect:'none' as const});
    const branches=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,semantic,domain,baseline);
    let remote:Awaited<ReturnType<typeof createCommerceWorkflowRemoteResultOwnerV1>>|undefined;
    let query:Awaited<ReturnType<typeof createCommerceWorkflowQueryResultOwnerV1>>|undefined;
    const externalQueries:{read:CommerceLocalReadHandleV1;codec:CommerceSourceQueryOutputCodecV1;
     query:CommerceSourceQueryRuntimeV1}[]=[];
    try{
     let branch;
     let operationResult:CommerceWorkflowRemoteExecutionV1|undefined;
     let queryResult:CommerceWorkflowQueryExecutionV1|undefined;
     if(call.role==='Operation'){
      const plan=plans.inspectOperation(selected.operation(started.invocation)).plan;
      const dependencies=selectCoreCommerceExternalQueries(plan,
       stage.moduleContracts(source).flatMap(module=>module.entries),[...serviceStores.keys()]);
      for(const dependency of dependencies){
       const queryStore=serviceStores.get(dependency.target_service);
       if(!queryStore)throw new Error('source-selected external Query service storage not open');
       const read=plans.bindRead(dependency.query);
       let codec:CommerceSourceQueryOutputCodecV1;
       try{codec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,read);}
       catch(error){plans.disposeRead(read);throw error;}
       let queryRuntime:CommerceSourceQueryRuntimeV1;
       try{queryRuntime=createCommerceSourceQueryRuntimeV1(stage,source,plans,read,
        domain,baseline,queryStore,codec);}
       catch(error){codec.dispose();plans.disposeRead(read);throw error;}
       externalQueries.push({read,codec,query:queryRuntime});
      }
      const ports={
       ...(targetView.service==='payments'&&demoPayDispatch?{demoPayDispatch}:{}),
       ...(externalQueries.length?{externalQueries:externalQueries.map(resource=>resource.query)}:{}),
      };
      remote=await createCommerceWorkflowRemoteResultOwnerV1(sources,capture,stage,source,domain,baseline,
       plans,selected,target,started.invocation,path.join(directoryRoot,'remote-'+serial),protectedCall,
        branches,prepared.identities,prepared.identity,witness.snapshots,witness.handle,
        Object.keys(ports).length?ports:undefined);
      operationResult=await remote.execute();
      if(operationResult.kind!=='returned')return Object.freeze({kind:'remote-not-completed' as const,
       runtime_outcome:operationResult.runtime_outcome,journal_phase:'Dispatched' as const,
       authority_effect:operationResult.authority_effect});
      branch=remote.select(operationResult.handle);
     }else{
      query=await createCommerceWorkflowQueryResultOwnerV1(semantics,semantic,stage,source,domain,baseline,
       plans,selected,target,started.invocation,protectedCall,branches,prepared.identities,prepared.identity,
       witness.snapshots,witness.handle);
      queryResult=query.execute();
      if(queryResult.kind!=='returned')return Object.freeze({kind:'remote-not-completed' as const,
       runtime_outcome:queryResult.query_outcome,journal_phase:'Dispatched' as const,authority_effect:'none' as const});
      branch=query.select(queryResult.handle);
     }
     if(call.role==='Query'&&query&&queryResult?.kind==='returned'&&
      branch.outcome==='selected'&&branch.observation===null&&branch.channel==='variant'&&
      branch.variant==='Recorded'&&branch.action?.kind==='finish'){
      const inspected=query.inspect(queryResult.handle);
      if(inspected.result_kind!=='returned'||inspected.workflow!==workflow.workflow.name||
       inspected.step_name!==call.step_name||inspected.target_entry_id!==call.entry_id||
       inspected.source_capture_sha256!==workflow.source_capture_sha256)
       throw new Error('terminal Query must retain its original protected result');
      return Object.freeze({kind:'terminal-ready' as const,step:call.step_name,
       remote_entry:call.entry_id,next_action:branch.action,commits:0 as const,
       authority_effect:'none' as const,
       qualification:'original-protected-query-inspected-existing-commit;fresh-terminal-snapshot-required' as const});
     }
     if(call.role==='Operation'&&remote&&operationResult?.kind==='returned'&&
      branch.outcome==='selected'&&branch.observation===null&&branch.action?.kind==='finish'){
      const inspected=remote.inspect(operationResult.handle);
      if(!inspected.committed_same_service||inspected.native_commits<1||
       inspected.result_kind!=='returned'||inspected.workflow!==workflow.workflow.name||
       inspected.step_name!==call.step_name||inspected.target_entry_id!==call.entry_id||
       inspected.source_capture_sha256!==workflow.source_capture_sha256)
       throw new Error('terminal Operation requires its original same-service native commit');
      return Object.freeze({kind:'terminal-ready' as const,step:call.step_name,
       remote_entry:call.entry_id,next_action:branch.action,commits:inspected.native_commits,
       authority_effect:'committed' as const,
       qualification:'original-generated-same-service-commit;fresh-terminal-snapshot-required' as const});
     }
     if(branch.outcome!=='selected'||!branch.observation)
      return Object.freeze({kind:'branch-suspended' as const,journal_phase:'Dispatched' as const,authority_effect:'none' as const});
     const proposals=call.role==='Query'?
      query&&queryResult?.kind==='returned'?
       createCommerceWorkflowObservationProposalOwnerV1(binding,semantics,semantic,query,queryResult.handle,
        witness.snapshots,witness.handle,session.worker,session.context):
       undefined:
      remote&&operationResult?.kind==='returned'?
       createCommerceWorkflowObservationProposalOwnerV1(binding,semantics,semantic,remote,operationResult.handle,
        witness.snapshots,witness.handle,session.worker,session.context):
       undefined;
     if(!proposals)throw new Error('selected protected result requires an original Query or Operation owner');
     try{
      const proposal=proposals.propose(),proposed=proposals.inspect(proposal),
       admission=createCommerceWorkflowObservationAdmissionV1(binding,semantics,semantic,
        producerStorage,proposals,proposal,session.worker,session.context),admitted=admission.inspect();
      const observationRequirement=requirements.filter(row=>row.usage==='observation'&&row.entry===admitted.entry_id);
      if(observationRequirement.length!==1||observationRequirement[0]!.target!==admitted.target||
       observationRequirement[0]!.target_service!==producer.service)
       throw new Error('source-selected observation lacks exact worker Entry requirement');
      const observationActor=actors.actorFor('observation');
      const observationEntry=auth.bindEntry(admitted.entry_id);
      let observationWire:Uint8Array;
      try{observationWire=auth.encodeEntryArguments(observationEntry,admitted.input);}
      finally{auth.disposeEntry(observationEntry);}
      const authorized=await selected.beginWorkflowObservation(observationActor,admitted.entry_id,
       observationWire!,admitted.input,producerStorage,binding,admission,session.worker,session.context);
      if(!authorized.ok)return Object.freeze({kind:'entry-denied' as const,stage:'observation' as const,
       status:authorized.status,code:authorized.code,journal_phase:'Dispatched' as const,authority_effect:'none' as const});
      let opened=false;
      try{
       const runtime=await assembly.openGeneratedOperation(authorized.invocation);opened=true;
       const outcome=await runtime.run(authorized.invocation);
       if(outcome.kind!=='returned'){
        if(outcome.kind!=='failed'&&outcome.kind!=='rejected'&&outcome.kind!=='indeterminate')
         throw new Error('generated observation returned an unsupported outcome');
        return Object.freeze({kind:'observation-not-completed' as const,
         runtime_outcome:outcome.kind,journal_phase:'Dispatched' as const,authority_effect:'none' as const});
       }
       if(!Array.isArray(outcome.commits)||outcome.commits.length!==1||
        !outcome.commits[0]||typeof outcome.commits[0]!=='object')
        throw new Error('generated observation must return one committed native receipt');
       return Object.freeze({kind:'observed' as const,step:call.step_name,remote_entry:call.entry_id,
        observation_entry:admitted.entry_id,source_capture_sha256:workflow.source_capture_sha256,
        next_action:proposed.next_action,commits:outcome.commits.length,
        qualification:'original-remote-result-and-generated-observation-committed' as const});
      }finally{
       try{if(opened)assembly.releaseGeneratedOperation(authorized.invocation);}
       finally{selected.retire(authorized.invocation);}
      }
     }finally{proposals.dispose();}
    }finally{
     try{remote?.dispose();}finally{
      try{query?.dispose();}finally{
       for(const resource of externalQueries.reverse()){
        try{resource.query.dispose();}finally{try{resource.codec.dispose();}
         finally{plans.disposeRead(resource.read);}}
       }
       branches.dispose();selected.retire(started.invocation);
      }
     }
    }
   }finally{causal.dispose();}
  },
  assertCurrent:current,close(){closed=true;},
 });
 current();return owner;
}
