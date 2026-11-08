/** Whole-process recovery of an original Dispatched Commerce Workflow step.
 * The child uses the positive integration path through generated claim and
 * original StepJournal, then is killed before its protected remote call. The
 * successor records uncertainty and runs the source-selected reconciliation
 * Query without repeating the original remote command.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn,type ChildProcessWithoutNullStreams} from 'node:child_process';
import {existsSync,mkdtempSync,readFileSync,realpathSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../../src/commerce/commerce-binding-assembly-v1.js';
import {createCommerceServiceStorageOwnerV1} from '../../src/commerce/commerce-service-storage-v1.js';
import {createCommerceSourceQueryOutputCodecV1} from '../../src/commerce/commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1} from '../../src/commerce/commerce-source-query-runtime-v1.js';
import {createCommerceTestAuthNativeV1} from '../support/commerce-auth-native-variant-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1} from '../../src/commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceGeneratedOperationRuntimeV1} from '../../src/commerce/commerce-generated-operation-runtime-v1.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkerContextOwnerV1} from '../../src/commerce/commerce-worker-context-v1.js';
import {createCommerceWorkflowSnapshotOwnerV1} from '../../src/commerce/commerce-workflow-snapshot-v1.js';
import {createCommerceWorkflowResumeSelectorV1} from '../../src/commerce/commerce-workflow-resume-v1.js';
import {createCommerceIdentityCallOwner} from '../../src/commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowStepIdentityOwnerV1} from '../../src/commerce/commerce-workflow-step-identity-v1.js';
import {createCommerceWorkflowBranchSelectionOwnerV1} from '../../src/commerce/commerce-workflow-branch-selection-v1.js';
import {createCommerceWorkflowCausalProjectionOwnerV1} from '../../src/commerce/commerce-workflow-causal-projection-v1.js';
import {createCommerceWorkflowProtectedCallBindingV1} from '../../src/commerce/commerce-workflow-protected-call-binding-v1.js';
import {createCommerceWorkflowQueryResultOwnerV1} from '../../src/commerce/commerce-workflow-query-result-v1.js';
import {createCommerceWorkflowObservationProposalOwnerV1} from '../../src/commerce/commerce-workflow-observation-proposal-v1.js';
import {createCommerceWorkflowObservationAdmissionV1} from '../../src/commerce/commerce-workflow-observation-admission-v1.js';
import {selectCommerceWorkflowRecoveryDecisionV1} from '../../src/commerce/commerce-workflow-recovery-decision-v1.js';
import {createCommerceWorkflowRecoveryObservationProposalOwnerV1} from '../../src/commerce/commerce-workflow-recovery-observation-proposal-v1.js';
import {createCommerceWorkflowRecoveryObservationAdmissionV1} from '../../src/commerce/commerce-workflow-recovery-observation-admission-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const childFile=fileURLToPath(new URL('./commerce-workflow-observation-positive-v1.test.ts',import.meta.url));
const occurrenceId='evt_'+('a'.repeat(64));
const orderId='fixture-order-one';
type RecoveryCrashPoint='before-effect'|'after-effect';
const diagnosticCopy=process.env.CRAFT_COMMERCE_RECOVERY_DIAGNOSTIC_COPY;
const caseSelection=process.env.CRAFT_COMMERCE_RECOVERY_CASE;
if(caseSelection!==undefined&&!['before-effect','after-effect'].includes(caseSelection))
 throw new Error('recovery case selector must be before-effect or after-effect');

async function waitReady(child:ChildProcessWithoutNullStreams,crashPoint:RecoveryCrashPoint):Promise<void>{
 const ready=crashPoint==='after-effect'?'recovery-after-effect-ready':'recovery-child-ready';
 await new Promise<void>((resolve,reject)=>{
  let output='';
  let stdout='';
  const lastPhase=()=>[...output.matchAll(/observation-positive phase=([^\s]+)/g)].at(-1)?.[1]??'none';
  const cleanup=()=>{
   clearTimeout(timer);child.stderr.off('data',onData);child.stdout.off('data',onStdout);child.off('exit',onExit);child.off('error',onError);
  };
  const onStdout=(chunk:Buffer)=>{stdout=(stdout+chunk.toString()).slice(-8192);};
  const onData=(chunk:Buffer)=>{
   output=(output+chunk.toString()).slice(-8192);
   if(output.includes('observation-positive phase='+ready)){
    cleanup();resolve();
   }
  };
  const onExit=(exitCode:number|null,signal:NodeJS.Signals|null)=>{
   cleanup();reject(new Error(`recovery child exited before original dispatch: ${exitCode} ${signal}; last phase=${lastPhase()}; stderr=${output}; stdout=${stdout}`));
  };
  const onError=(error:Error)=>{
   cleanup();reject(new Error(`recovery child failed at phase=${lastPhase()}: ${error.message}`,{cause:error}));
  };
  const timer=setTimeout(()=>{
   cleanup();reject(new Error(`recovery child did not reach original dispatch within 90 minutes; last phase=${lastPhase()}; stderr=${output}`));
  },90*60*1000);
  child.stderr.on('data',onData);child.stdout.on('data',onStdout);child.once('exit',onExit);child.once('error',onError);
 });
}
async function waitExit(child:ChildProcessWithoutNullStreams):Promise<void>{
 if(child.exitCode!==null||child.signalCode!==null)return;
 await new Promise<void>(resolve=>child.once('exit',()=>resolve()));
}

async function exerciseWholeProcessRecovery(crashPoint:RecoveryCrashPoint):Promise<void>{
 const root=diagnosticCopy??mkdtempSync(path.join(tmpdir(),'commerce-recovery-child-'));
 let child:ChildProcessWithoutNullStreams|undefined,successful=false;
 try{
  if(diagnosticCopy){
   assert.equal(crashPoint,'after-effect');
   assert.ok(path.isAbsolute(root)&&path.normalize(root)===root&&realpathSync(root)===root,
    'diagnostic replay requires a real absolute working-copy root');
   assert.ok(!path.basename(root).startsWith('commerce-observation-diagnostic-'),
    'the immutable diagnostic original cannot be used as a replay working copy');
   assert.ok(existsSync(path.join(root,'.craft-recovery-disposable-copy')),
    'explicit disposable-copy marker is required before diagnostic replay');
   assert.ok(existsSync(path.join(root,'orders-store','store.sqlite'))&&
    existsSync(path.join(root,'inventory-store','store.sqlite')),
    'diagnostic copy must contain both original durable service stores');
   process.stderr.write('workflow-recovery phase=diagnostic-copy-replay\n');
  }else{
   child=spawn(process.execPath,['--import','tsx',childFile],{
    cwd:path.dirname(path.dirname(childFile)),
    env:{...process.env,CRAFT_COMMERCE_RECOVERY_CHILD_ROOT:root,
     CRAFT_COMMERCE_RECOVERY_CRASH_POINT:crashPoint},
    stdio:['pipe','pipe','pipe'],
   });
   await waitReady(child,crashPoint);
   child.kill('SIGKILL');await waitExit(child);
  }
  assert.equal(existsSync(path.join(root,'inventory-store')),crashPoint==='after-effect',
   'crash point must distinguish the durable Inventory effect from pre-dispatch');
  process.stderr.write('workflow-recovery phase='+
   (diagnosticCopy?'diagnostic-source-opened':'predecessor-killed')+'\n');

  const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture),
   paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
  const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),
   stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
  const domain=createCommerceComputationDomainOwner(stage,source),
   limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,
   baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
  const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline),
   models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),
   families=createCommerceFamilyOwnerV5(models),assemblyOwner=createCommerceBindingAssemblyOwnerV1(
    sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
  let storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined;
  let native:Awaited<ReturnType<typeof createCommerceTestAuthNativeV1>>|undefined;
  let auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined;
  let selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined;
  let worker:ReturnType<typeof createCommerceWorkerContextOwnerV1>|undefined;
  try{
   storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,
    baseline,plans,families,assemblyOwner,assembly,'orders',path.join(root,'orders-store'),'reopen');
   native=await createCommerceTestAuthNativeV1(path.join(root,'successor-native-auth'));
   auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,
    path.join(root,'successor-auth'));
   selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,
    domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'successor-selected'));
   const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
   const reclaimed=storage.reclaimQuiescentWorkSchedule(binding,occurrenceId);
   assert.equal(reclaimed.kind,'claimed','successor must obtain native quiescent-predecessor proof');
   if(reclaimed.kind!=='claimed')return;
   const recovered=storage.inspectWorkScheduleClaim(reclaimed.claim);
   assert.equal(recovered.predecessor_proof,'quiescent');
   assert.equal(recovered.prior_worker_epoch,1n);
   assert.equal(recovered.worker_epoch,2n);
   worker=createCommerceWorkerContextOwnerV1(binding,storage);
   const context=worker.registerCommittedClaim(reclaimed.claim);
   let progressClaim:ReturnType<typeof worker.registerCommittedProgressClaim>|undefined;
   const claimJournal=storage.prepareClaimJournal(binding,reclaimed.claim);
   assert.equal(claimJournal.kind,'prepared');
   if(claimJournal.kind!=='prepared')return;
   process.stderr.write('workflow-recovery phase=successor-reclaimed\n');

   const claimEntryId=storage.inspectClaimJournal(claimJournal.journal).target_entry_id,
    claimEntry=auth.bindEntry(claimEntryId),claimDefinition=auth.inspectEntry(claimEntry);
   const claimFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'recovery-claim-worker',
    evidence:'recovery-claim-evidence',session:'recovery-claim-session',valid_for_seconds:7200,
    routes:[{entry:claimEntryId,permission:claimDefinition.access.auth_permission}]});
   const claimActor=registerCommerceEntryFixtureActorV1(auth,claimFixture.handle,{subject:'recovery-claim-worker',
    evidence:'recovery-claim-evidence',principal_kind:'service',service_id:'orders',
    scope:claimDefinition.access.auth_permission.scope});
   try{
    const progress=storage.inspectStoredRecord(binding.inspect().workflow.durable_state,0,{orderId}) as {version:bigint}|null;
    assert.ok(progress);
    const claimInput={orderId,expectedProgressVersion:progress.version},
     claimWire=Buffer.from(JSON.stringify(claimInput,(_key,value)=>typeof value==='bigint'?String(value):value));
    const started=await selected.beginWorker(claimActor,claimEntryId,claimWire,claimInput,
     storage,binding,claimJournal.journal,worker,context);
    assert.equal(started.ok,true);
    if(!started.ok)return;
    const runner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,
     baseline,plans,selected,storage,started.invocation,path.join(root,'successor-claim-operation'));
    try{
     const outcome=await runner.run(started.invocation);
     assert.equal(outcome.kind,'returned');
     if(outcome.kind!=='returned')return;
     assert.equal(outcome.commits.length,1);
     progressClaim=worker.registerCommittedProgressClaim(context,runner,selected,started.invocation,outcome.commits[0]!);
    }finally{runner.dispose();selected.retire(started.invocation);}
    process.stderr.write('workflow-recovery phase=successor-progress-committed\n');
   }finally{auth.disposeActor(claimActor);auth.disposeEntry(claimEntry);}

   const snapshotEntryId='Orders.ReadCheckoutSnapshotEntry',snapshotEntry=auth.bindEntry(snapshotEntryId),
    snapshotDefinition=auth.inspectEntry(snapshotEntry);
   const snapshotFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'recovery-snapshot-worker',
    evidence:'recovery-snapshot-evidence',session:'recovery-snapshot-session',valid_for_seconds:7200,
    routes:[{entry:snapshotEntryId,permission:snapshotDefinition.access.auth_permission}]});
   const snapshotActor=registerCommerceEntryFixtureActorV1(auth,snapshotFixture.handle,{
    subject:'recovery-snapshot-worker',evidence:'recovery-snapshot-evidence',principal_kind:'service',
    service_id:'orders',scope:snapshotDefinition.access.auth_permission.scope});
   try{
    const snapshotInput={orderId},snapshotWire=Buffer.from(JSON.stringify(snapshotInput));
    const started=await selected.beginWorkerRead(snapshotActor,snapshotEntryId,snapshotWire,snapshotInput,
     storage,binding,claimJournal.journal,worker,context);
    assert.equal(started.ok,true);
    if(!started.ok)return;
    const read=plans.bindRead('Orders.ReadCheckoutSnapshot'),codec=await createCommerceSourceQueryOutputCodecV1(
     stage,source,domain,baseline,plans,read),query=createCommerceSourceQueryRuntimeV1(
     stage,source,plans,read,domain,baseline,storage,codec);
    try{
     const snapshots=createCommerceWorkflowSnapshotOwnerV1(binding,storage,worker,context,query,selected,started.invocation);
     try{
      const witnessed=snapshots.read();assert.equal(witnessed.kind,'snapshot');
      if(witnessed.kind!=='snapshot')return;
      const resumes=createCommerceWorkflowResumeSelectorV1(binding,worker);
      try{
       const cancellation=resumes.inspectSourceCases().filter(row=>row.state==='Cancelling');
       assert.deepEqual(cancellation.map(row=>({guarded:row.guarded,action:row.action})),[
        {guarded:true,action:{kind:'step',target:'cancel-stock'}},
        {guarded:true,action:{kind:'step',target:'release'}},
        {guarded:true,action:{kind:'step',target:'cancel-payment'}},
       ],'the recovered owner must retain the source-ordered compensation cases');
       const selection=resumes.select(snapshots.inspect(witnessed.handle).value,context),
        chosen=resumes.inspectSelection(selection);
       assert.deepEqual(chosen.action,{kind:'step',target:'reserve'});
       const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
       const identities=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,calls,
        stage,source,domain,baseline,path.join(root,'successor-step-identity'));
       try{
        const identity=identities.derive(resumes,selection,snapshots,witnessed.handle),
         branches=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,semantic,domain,baseline);
        try{
         const decision=selectCommerceWorkflowRecoveryDecisionV1(binding,storage,reclaimed.claim,
          identities,identity,snapshots,witnessed.handle,branches);
         assert.equal(decision.kind,'dispatched-reconcile');
         assert.equal(decision.reason,'dispatched-unknown-result');
         assert.deepEqual(decision.action,{kind:'step',target:'reconcile-stock'});
         assert.equal(decision.command_id,'cmd_fixture_reserve_one');
         assert.equal(decision.predecessor_worker_epoch,1n);
         assert.equal(decision.current_worker_epoch,2n);
         assert.equal(decision.authority_effect,'none');
         assert.equal(decision.original_journal,'retain');
         assert.equal(existsSync(path.join(root,'inventory-store')),crashPoint==='after-effect',
          'recovery decision must not change the Inventory effect');
         process.stderr.write('workflow-recovery phase=dispatched-reconciliation-selected\n');
         const proposals=createCommerceWorkflowRecoveryObservationProposalOwnerV1(binding,semantics,semantic,
          decision,snapshots,witnessed.handle,worker,context);
         try{
          const proposal=proposals.propose(),admission=createCommerceWorkflowRecoveryObservationAdmissionV1(
           binding,semantics,semantic,storage,proposals,proposal,worker,context),observed=admission.inspect();
          assert.equal(observed.entry_id,'Orders.RecordCheckoutObservationEntry');
          assert.equal(observed.original_journal,'retain');
          const observationEntry=auth.bindEntry(observed.entry_id),
           observationDefinition=auth.inspectEntry(observationEntry);
          const observationFixture=seedCommerceAuthFixtureDatabaseV1(native,{
           subject:'recovery-observation-worker',evidence:'recovery-observation-evidence',
           session:'recovery-observation-session',valid_for_seconds:7200,
           routes:[{entry:observed.entry_id,
            permission:observationDefinition.access.auth_permission}]});
          const observationActor=registerCommerceEntryFixtureActorV1(auth,observationFixture.handle,{
           subject:'recovery-observation-worker',evidence:'recovery-observation-evidence',
           principal_kind:'service',service_id:'orders',scope:observationDefinition.access.auth_permission.scope});
          try{
           const input=observed.input,wire=Buffer.from(JSON.stringify(input,
            (_key,value)=>typeof value==='bigint'?String(value):value));
           const started=await selected.beginWorkflowObservation(observationActor,observed.entry_id,
            wire,input,storage,binding,admission,worker,context);
           assert.equal(started.ok,true,'fresh successor Auth must admit the source reconciliation observation');
           if(!started.ok)return;
           try{
            const runner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,
             domain,baseline,plans,selected,storage,started.invocation,
             path.join(root,'successor-observation-operation'));
            try{
             const result=await runner.run(started.invocation);
             assert.equal(result.kind,'returned','recovered observation must commit through generated Orders Operation');
             assert.equal(result.commits.length,1);
             process.stderr.write('workflow-recovery phase=successor-observation-committed\n');
            }finally{runner.dispose();}
           }finally{selected.retire(started.invocation);}
          }finally{auth.disposeActor(observationActor);auth.disposeEntry(observationEntry);}
         }finally{proposals.dispose();}
         const journal=storage.inspectStoredRecord(binding.inspect().journal_entity,0,{
          consumerEntryId:decision.consumer_entry_id,occurrenceId:decision.occurrence_id,
          stepName:decision.step_name,commandId:decision.command_id}) as
          {phase:string;version:bigint;observation:{kind:string}}|null;
         assert.ok(journal,'original predecessor StepJournal must survive the successor transaction');
         assert.equal(journal.phase,'Observed');assert.equal(journal.version,3n);
         assert.equal(journal.observation.kind,'some');
         const progressAfter=storage.inspectStoredRecord(binding.inspect().workflow.durable_state,0,{orderId}) as
          {version:bigint;state:string;reserveResult:{kind:string}}|null;
         assert.ok(progressAfter);
         assert.equal(progressAfter.version,decision.progress_version+1n);
         assert.equal(progressAfter.state,'StockUncertain');
         assert.equal(progressAfter.reserveResult.kind,'none',
          'unknown predecessor effect cannot be recorded as a successful reservation');
         assert.equal(existsSync(path.join(root,'inventory-store')),crashPoint==='after-effect',
          'successor must reconcile without repeating ReserveStock');
         assert.ok(progressClaim,'generated claim must retain the successor progress owner');
         const freshSnapshotFixture=seedCommerceAuthFixtureDatabaseV1(native,{
          subject:'recovery-fresh-snapshot-worker',evidence:'recovery-fresh-snapshot-evidence',
          session:'recovery-fresh-snapshot-session',valid_for_seconds:7200,
          routes:[{entry:snapshotEntryId,permission:snapshotDefinition.access.auth_permission}]}),
          freshSnapshotActor=registerCommerceEntryFixtureActorV1(auth,freshSnapshotFixture.handle,{
           subject:'recovery-fresh-snapshot-worker',evidence:'recovery-fresh-snapshot-evidence',
           principal_kind:'service',service_id:'orders',scope:snapshotDefinition.access.auth_permission.scope});
         try{
         const freshStart=await selected.beginWorkerRead(freshSnapshotActor,snapshotEntryId,snapshotWire,
          snapshotInput,storage,binding,claimJournal.journal,worker,context);
         assert.equal(freshStart.ok,true,'recovery must read a fresh StockUncertain snapshot');
         if(!freshStart.ok)return;
         try{
          const freshSnapshots=createCommerceWorkflowSnapshotOwnerV1(binding,storage,worker,context,
           query,selected,freshStart.invocation);
          try{
           const fresh=freshSnapshots.read();
           assert.equal(fresh.kind,'snapshot');
           if(fresh.kind!=='snapshot')return;
           const freshResumes=createCommerceWorkflowResumeSelectorV1(binding,worker);
           try{
            const freshSelection=freshResumes.select(freshSnapshots.inspect(fresh.handle).value,context),
             freshDecision=freshResumes.inspectSelection(freshSelection);
            assert.equal(freshDecision.outcome,'selected');
            assert.deepEqual(freshDecision.action,{kind:'step',target:'reconcile-stock'});
            process.stderr.write('workflow-recovery phase=fresh-reconciliation-selected\n');
            const freshIdentities=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,
             calls,stage,source,domain,baseline,path.join(root,'successor-reconcile-identity'));
            try{
             const freshIdentity=freshIdentities.derive(freshResumes,freshSelection,freshSnapshots,fresh.handle),
              prepared=storage.prepareWorkflowStepJournal(binding,reclaimed.claim,progressClaim,
               freshIdentities,freshIdentity);
             assert.equal(prepared.kind,'prepared','reconciliation Query needs its own original StepJournal');
             if(prepared.kind!=='prepared')return;
             const causal=await createCommerceWorkflowCausalProjectionOwnerV1(binding,semantics,semantic,
              calls,stage,source,domain,baseline,path.join(root,'successor-reconcile-causal'));
             try{
              const projection=causal.derive(freshIdentities,freshIdentity,freshResumes,freshSelection,
               freshSnapshots,fresh.handle),dispatched=storage.markWorkflowStepDispatched(binding,
                prepared.journal,freshIdentities,freshIdentity);
              assert.equal(dispatched.kind,'dispatched');
              if(dispatched.kind!=='dispatched')return;
              const protectedCall=createCommerceWorkflowProtectedCallBindingV1(binding,storage,
               dispatched.journal,causal,projection),call=protectedCall.initial();
              assert.equal(call.entry_id,'Inventory.ReconcileStockEntry');
              assert.equal(call.role,'Query');
              const inventoryRoot=crashPoint==='after-effect'?path.join(root,'inventory-store'):
               path.join(root,'successor-reconcile-inventory-store');
              const inventory=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,
               stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'inventory',
               inventoryRoot,crashPoint==='after-effect'?'reopen':'create');
              try{
               const effectBefore=inventory.inspectStoredRecord('Inventory.StockCommandRecord',0,
                {commandId:decision.command_id}) as {outcome:{kind:string};version:bigint}|null;
               const stockBefore=inventory.inspectStoredRecord('Inventory.Stock',0,{sku:'sku-one'}) as
                {reserved:bigint;version:bigint}|null;
               if(crashPoint==='after-effect'){
                assert.equal(effectBefore?.outcome.kind,'Applied',
                 'reopened Inventory must retain the original committed command');
                assert.ok(effectBefore);
                assert.equal(effectBefore.version,2n);
                assert.equal(stockBefore?.reserved,1n);
                assert.ok(stockBefore);
                assert.equal(stockBefore.version,2n);
               }else{
                assert.equal(effectBefore,null,'pre-effect predecessor cannot have a command outcome');
                assert.equal(stockBefore,null);
               }
               const entry=auth.bindEntry(call.entry_id),definition=auth.inspectEntry(entry);
               try{
                const fixture=seedCommerceAuthFixtureDatabaseV1(native,{
                 subject:'recovery-reconcile-worker',evidence:'recovery-reconcile-evidence',
                 session:'recovery-reconcile-session',valid_for_seconds:7200,
                 routes:[{entry:call.entry_id,permission:definition.access.auth_permission}]});
                const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{
                 subject:'recovery-reconcile-worker',evidence:'recovery-reconcile-evidence',
                 principal_kind:'service',service_id:'orders',scope:definition.access.auth_permission.scope});
                try{
                 const wire=auth.encodeEntryArguments(entry,call.arguments),
                  admitted=await selected.beginWorkflowServiceStep(actor,call.entry_id,wire,
                   call.arguments,protectedCall);
                 assert.equal(admitted.ok,true,'fresh Auth must admit only the source-selected reconciliation Query');
                 if(!admitted.ok)return;
                 const queryBranches=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,
                  semantic,domain,baseline);
                 try{
                  const result=await createCommerceWorkflowQueryResultOwnerV1(semantics,semantic,stage,
                   source,domain,baseline,plans,selected,inventory,admitted.invocation,protectedCall,
                   queryBranches,freshIdentities,freshIdentity,freshSnapshots,fresh.handle);
                  try{
                   const executed=result.execute();
                   assert.equal(executed.kind,'returned','source-delegated reconciliation Query must return');
                   if(executed.kind!=='returned')return;
                   const branch=result.select(executed.handle);
                   assert.equal(branch.outcome,'selected');
                   assert.equal(branch.step_name,'reconcile-stock');
                   assert.equal(branch.channel,'variant');
                   assert.equal(branch.variant,crashPoint==='after-effect'?'Applied':'Unknown');
                   if(crashPoint==='after-effect'){
                    assert.deepEqual(branch.action,{kind:'step',target:'mark-capture-dispatched'});
                    assert.equal((branch.observation as {kind?:string}|null)?.kind,'ReserveApplied');
                   }else{
                    assert.equal(branch.action?.kind,'suspend');
                    assert.equal(branch.observation,null,'Unknown reconciliation cannot invent ReserveApplied');
                   }
                   assert.equal(branch.authority_effect,'none');
                   process.stderr.write('workflow-recovery phase=reconciliation-'+
                    (crashPoint==='after-effect'?'applied-selected':'unknown-suspended')+'\n');
                   if(crashPoint==='after-effect'){
                    const proposals=createCommerceWorkflowObservationProposalOwnerV1(binding,
                     semantics,semantic,result,executed.handle,freshSnapshots,fresh.handle,worker,context);
                    try{
                     const proposal=proposals.propose(),admission=createCommerceWorkflowObservationAdmissionV1(
                      binding,semantics,semantic,storage,proposals,proposal,worker,context),
                      observed=admission.inspect(),observationEntry=auth.bindEntry(observed.entry_id),
                      observationDefinition=auth.inspectEntry(observationEntry);
                     try{
                      const fixture=seedCommerceAuthFixtureDatabaseV1(native,{
                       subject:'recovery-applied-observation-worker',
                       evidence:'recovery-applied-observation-evidence',
                       session:'recovery-applied-observation-session',valid_for_seconds:7200,
                       routes:[{entry:observed.entry_id,
                        permission:observationDefinition.access.auth_permission}]});
                      const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{
                       subject:'recovery-applied-observation-worker',
                       evidence:'recovery-applied-observation-evidence',principal_kind:'service',
                       service_id:'orders',scope:observationDefinition.access.auth_permission.scope});
                      try{
                       const input=observed.input,wire=Buffer.from(JSON.stringify(input,
                        (_key,value)=>typeof value==='bigint'?String(value):value));
                       const authorized=await selected.beginWorkflowObservation(actor,observed.entry_id,
                        wire,input,storage,binding,admission,worker,context);
                       assert.equal(authorized.ok,true,
                        'reopened Inventory result must still need fresh Orders Auth');
                       if(authorized.ok){
                        try{
                         const runner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,
                          source,domain,baseline,plans,selected,storage,authorized.invocation,
                          path.join(root,'successor-applied-observation-operation'));
                         try{
                          const committed=await runner.run(authorized.invocation);
                          assert.equal(committed.kind,'returned');
                          if(committed.kind==='returned')assert.equal(committed.commits.length,1);
                         }finally{runner.dispose();}
                        }finally{selected.retire(authorized.invocation);}
                       }
                      }finally{auth.disposeActor(actor);}
                     }finally{auth.disposeEntry(observationEntry);}
                    }finally{proposals.dispose();}
                    const resumed=storage.inspectStoredRecord(binding.inspect().workflow.durable_state,0,
                     {orderId}) as {version:bigint;state:string;reserveResult:{kind:string}}|null;
                    assert.ok(resumed);
                    assert.equal(resumed.version,decision.progress_version+2n);
                    assert.equal(resumed.state,'AwaitingPayment');
                    assert.equal(resumed.reserveResult.kind,'some');
                    process.stderr.write('workflow-recovery phase=reconciliation-applied-observed\n');
                   }
                  }finally{result.dispose();}
                 }finally{queryBranches.dispose();selected.retire(admitted.invocation);}
                }finally{auth.disposeActor(actor);}
               }finally{auth.disposeEntry(entry);}
               const effectAfter=inventory.inspectStoredRecord('Inventory.StockCommandRecord',0,
                {commandId:decision.command_id}) as {outcome:{kind:string};version:bigint}|null;
               const stockAfter=inventory.inspectStoredRecord('Inventory.Stock',0,{sku:'sku-one'}) as
                {reserved:bigint;version:bigint}|null;
               assert.deepEqual(effectAfter,effectBefore,
                'reconciliation Query must not create or replay the original command');
               assert.deepEqual(stockAfter,stockBefore,
                'reconciliation Query must not change the committed stock effect');
              }finally{inventory.close();}
              const reconcileJournal=storage.inspectStoredRecord(binding.inspect().journal_entity,0,{
               consumerEntryId:decision.consumer_entry_id,occurrenceId:decision.occurrence_id,
               stepName:'reconcile-stock',commandId:call.command_id}) as
               {phase:string;version:bigint;observation:{kind:string}}|null;
              assert.ok(reconcileJournal);
              assert.equal(reconcileJournal.phase,crashPoint==='after-effect'?'Observed':'Dispatched');
              assert.equal(reconcileJournal.version,crashPoint==='after-effect'?3n:2n);
              assert.equal(reconcileJournal.observation.kind,crashPoint==='after-effect'?'some':'none');
             }finally{causal.dispose();}
            }finally{freshIdentities.dispose();}
           }finally{freshResumes.dispose();}
          }finally{freshSnapshots.dispose();}
         }finally{selected.retire(freshStart.invocation);}
         }finally{auth.disposeActor(freshSnapshotActor);}
        }finally{branches.dispose();}
       }finally{identities.dispose();}
      }finally{resumes.dispose();}
     }finally{snapshots.dispose();}
    }finally{query.dispose();codec.dispose();plans.disposeRead(read);selected.retire(started.invocation);}
   }finally{auth.disposeActor(snapshotActor);auth.disposeEntry(snapshotEntry);}
  }finally{worker?.dispose();selected?.dispose();auth?.dispose();await native?.dispose();storage?.close();
   assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);}
  successful=true;
 }finally{if(child&&child.exitCode===null&&child.signalCode===null){child.kill('SIGKILL');await waitExit(child);}
  if(successful&&!diagnosticCopy)rmSync(root,{recursive:true,force:true});
  else if(!successful)process.stderr.write('workflow-recovery diagnostic fixture retained at '+root+'\n');}
}

test('reopen after killed dispatch records uncertainty and suspends on original reconciliation Query',
 {skip:Boolean(diagnosticCopy)||caseSelection==='after-effect'},
 async()=>exerciseWholeProcessRecovery('before-effect'));
test('reopen after committed Inventory effect reconciles the original command without replay',
 {skip:caseSelection==='before-effect'},async()=>exerciseWholeProcessRecovery('after-effect'));
