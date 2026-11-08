/** A generated-schema Commerce fixture exercises original result, proposal, Auth, and observation commit. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,mkdtempSync,mkdirSync,rmSync} from 'node:fs';
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
import {createCommerceSqliteFamilyOwnerV1} from '../../src/commerce/commerce-sqlite-family-v1.js';
import {createCommerceServiceStorageOwnerV1,type CommerceWorkerProgressClaimV1} from '../../src/commerce/commerce-service-storage-v1.js';
import {createCommerceSourceQueryOutputCodecV1} from '../../src/commerce/commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1} from '../../src/commerce/commerce-source-query-runtime-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1} from '../../src/commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceGeneratedOperationRuntimeV1} from '../../src/commerce/commerce-generated-operation-runtime-v1.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1} from '../../src/commerce/commerce-worker-context-v1.js';
import {createCommerceWorkflowSnapshotOwnerV1} from '../../src/commerce/commerce-workflow-snapshot-v1.js';
import {createCommerceWorkflowResumeSelectorV1} from '../../src/commerce/commerce-workflow-resume-v1.js';
import {createCommerceIdentityCallOwner} from '../../src/commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowStepIdentityOwnerV1} from '../../src/commerce/commerce-workflow-step-identity-v1.js';
import {createCommerceWorkflowCausalProjectionOwnerV1} from '../../src/commerce/commerce-workflow-causal-projection-v1.js';
import {createCommerceWorkflowProtectedCallBindingV1} from '../../src/commerce/commerce-workflow-protected-call-binding-v1.js';
import {createCommerceWorkflowBranchSelectionOwnerV1} from '../../src/commerce/commerce-workflow-branch-selection-v1.js';
import {createCommerceWorkflowRemoteResultOwnerV1} from '../../src/commerce/commerce-workflow-remote-result-v1.js';
import {createCommerceWorkflowObservationProposalOwnerV1} from '../../src/commerce/commerce-workflow-observation-proposal-v1.js';
import {createCommerceWorkflowObservationAdmissionV1} from '../../src/commerce/commerce-workflow-observation-admission-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.js';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.js';

const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url)),candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;
const structural=(value:any):any=>Array.isArray(value)?value.map(structural):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([key,child])=>[key,structural(child)])):value;

test('original ReserveStock result reaches selected branch and atomic Orders observation',async()=>{
 const recoveryChildRoot=process.env.CRAFT_COMMERCE_RECOVERY_CHILD_ROOT;
 const recoveryCrashPoint=process.env.CRAFT_COMMERCE_RECOVERY_CRASH_POINT??'before-effect';
 const root=recoveryChildRoot??mkdtempSync(path.join(tmpdir(),'commerce-observation-fixture-'));
 if(recoveryChildRoot)assert.ok(path.isAbsolute(root)&&path.normalize(root)===root&&
  root.startsWith(path.join(tmpdir(),'commerce-recovery-child-')),
  'recovery child must use a fresh absolute Commerce test directory');
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture),paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline),models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models),assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let successful=false,ordersStorage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined,
  native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined,
  auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined,
  selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined,
  ordersDb:DatabaseSync|undefined,worker:CommerceWorkerContextOwnerV1|undefined;
 try{
  const sqlite=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,
   plans,families,assemblyOwner.family(assembly));
  const ordersRoot=path.join(root,'orders-store');
  ordersStorage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,
   baseline,plans,families,assemblyOwner,assembly,'orders',ordersRoot);
  const ordersService=sqlite.bindService('orders'),ordersBundle=sqlite.materialize(ordersService,
   path.join(root,'orders-fixture-repository'));
  const ordersData=await sqlite.loadDataComponent(ordersBundle),
   ordersPhysical=deriveCommerceSqlitePhysicalLayoutV1(ordersData);
  const orderId='fixture-order-one',occurrenceId='evt_'+('a'.repeat(64));
  const order={id:orderId,customerId:'customer-one',quoteId:'quote-one',currency:'USD',payableMinor:100n,
   lines:[{sku:'sku-one',quantity:1n}],status:'AwaitingStock',version:1n};
  const progress={orderId,state:'AwaitingStock',reserveCommandId:'cmd_fixture_reserve_one',
   captureAttemptKey:'cmd_fixture_capture_one',allocateCommandId:'cmd_fixture_allocate_one',
   releaseCommandId:'cmd_fixture_release_one',confirmCommandId:'cmd_fixture_confirm_one',
   cancelCommandId:'cmd_fixture_cancel_one',reserveResult:{kind:'none'},reserveRejected:{kind:'none'},
   paymentResult:{kind:'none'},allocationResult:{kind:'none'},releaseResult:{kind:'none'},
   captureDispatched:false,workerOwner:{kind:'none'},workerEpoch:0n,version:1n};
  const metadata={eventId:occurrenceId,producer:'orders',aggregateId:orderId,aggregateVersion:1n,
   ordinal:0n,correlationId:orderId,commandId:'cmd_fixture_place_one'};
  const outbox={eventId:occurrenceId,event:{metadata,orderId},state:'Ready',version:1n};
  ordersDb=new DatabaseSync(path.join(ordersRoot,'store.sqlite'));
  for(const [entity,value] of [['Orders.Order',order],['Orders.CheckoutProgress',progress],
    ['Orders.OrderPlacedOutbox',outbox]] as const){
   const table=ordersPhysical.tables.find(row=>row.entity===entity);
   assert.ok(table,'generated physical schema must contain '+entity);
   ordersDb.prepare(table.insert_sql).run(...ordersPhysical.encode(entity,value).bindings);
  }
  ordersDb.close();ordersDb=undefined;
  process.stderr.write('observation-positive phase=generated-schema-fixture-seeded\n');
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,
   path.join(root,'auth'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,
   domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  process.stderr.write('observation-positive phase=auth-and-selection-ready\n');
  const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
  const ingress=await ordersStorage.enqueueCommittedWorkflowEvent(binding,occurrenceId);
  assert.equal(ingress.kind,'enqueued','generated-schema outbox fixture must create the original Workflow Inbox and WorkSchedule');
  process.stderr.write('observation-positive phase=inbox-enqueued\n');
  const schedule=ordersStorage.claimVacantWorkSchedule(binding,occurrenceId);
  assert.equal(schedule.kind,'claimed','original vacant WorkSchedule must yield one native committed claim');
  process.stderr.write('observation-positive phase=schedule-claimed\n');
  if(schedule.kind==='claimed'){
   worker=createCommerceWorkerContextOwnerV1(binding,ordersStorage);
   const context=worker.registerCommittedClaim(schedule.claim);
   const journal=ordersStorage.prepareClaimJournal(binding,schedule.claim);
   assert.equal(journal.kind,'prepared','source claim driver must commit its original Prepared StepJournal');
   if(journal.kind==='prepared'){
    const recorded=ordersStorage.inspectClaimJournal(journal.journal);
    const claimEntryId=recorded.target_entry_id,claimEntry=auth.bindEntry(claimEntryId),claimDefinition=auth.inspectEntry(claimEntry);
    const claimFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-claim-worker',evidence:'claim-worker-evidence',
     session:'claim-worker-session',valid_for_seconds:7200,
     routes:[{entry:claimEntryId,permission:claimDefinition.access.auth_permission}]});
    const claimActor=registerCommerceEntryFixtureActorV1(auth,claimFixture.handle,{subject:'service-claim-worker',evidence:'claim-worker-evidence',
     principal_kind:'service',service_id:'orders',scope:claimDefinition.access.auth_permission.scope});
    try{
     const progress=ordersStorage.inspectStoredRecord(binding.inspect().workflow.durable_state,0,{orderId}) as {version:bigint}|null;
     assert.ok(progress);
     const claimInput={orderId,expectedProgressVersion:progress.version};
     const wire=Buffer.from(JSON.stringify(claimInput,(_key,value)=>typeof value==='bigint'?String(value):value));
     const started=await selected.beginWorker(claimActor,claimEntryId,wire,claimInput,ordersStorage,binding,journal.journal,worker,context);
     assert.equal(started.ok,true,'fresh native Auth plus original claim journal must admit the worker Entry');
     if(started.ok){
      let progressClaim:CommerceWorkerProgressClaimV1|undefined;
      const claimRunner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,baseline,plans,selected,ordersStorage,
       started.invocation,path.join(root,'claim-operation'));
      process.stderr.write('observation-positive phase=claim-runner-ready\n');
      try{
       const claimed=await claimRunner.run(started.invocation);
       assert.equal(claimed.kind,'returned','generated ClaimCheckoutWork must commit the source-owned progress claim');
       const receipts=claimed.commits as readonly object[];assert.equal(receipts.length,1);
       progressClaim=worker.registerCommittedProgressClaim(context,claimRunner,selected,started.invocation,receipts[0]!);
      }finally{claimRunner.dispose();}
      assert.ok(progressClaim);
      process.stderr.write('observation-positive phase=claim-progress-committed\n');
      const snapshotEntryId='Orders.ReadCheckoutSnapshotEntry',snapshotEntry=auth.bindEntry(snapshotEntryId),
       snapshotDefinition=auth.inspectEntry(snapshotEntry);
      const snapshotFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-snapshot-worker',evidence:'snapshot-worker-evidence',
       session:'snapshot-worker-session',valid_for_seconds:7200,
       routes:[{entry:snapshotEntryId,permission:snapshotDefinition.access.auth_permission}]});
      const snapshotActor=registerCommerceEntryFixtureActorV1(auth,snapshotFixture.handle,{subject:'service-snapshot-worker',
       evidence:'snapshot-worker-evidence',principal_kind:'service',service_id:'orders',scope:snapshotDefinition.access.auth_permission.scope});
      try{
       const snapshotInput={orderId},snapshotWire=Buffer.from(JSON.stringify(snapshotInput));
       const snapshotStart=await selected.beginWorkerRead(snapshotActor,snapshotEntryId,snapshotWire,snapshotInput,
        ordersStorage,binding,journal.journal,worker,context);
       assert.equal(snapshotStart.ok,true,'fresh worker Query Entry must admit the original committed progress owner: '+
        (snapshotStart.ok?'admitted':snapshotStart.code));
       if(snapshotStart.ok){
        const read=plans.bindRead('Orders.ReadCheckoutSnapshot'),snapshotCodec=await createCommerceSourceQueryOutputCodecV1(
         stage,source,domain,baseline,plans,read),snapshotQuery=createCommerceSourceQueryRuntimeV1(
         stage,source,plans,read,domain,baseline,ordersStorage,snapshotCodec);
        try{
         const snapshots=createCommerceWorkflowSnapshotOwnerV1(binding,ordersStorage,worker,context,
          snapshotQuery,selected,snapshotStart.invocation);
         try{
          const witnessed=snapshots.read();
          assert.equal(witnessed.kind,'snapshot','source Worker Query must mint an original snapshot witness');
          if(witnessed.kind==='snapshot'){
           const original=snapshots.inspect(witnessed.handle);
           process.stderr.write('observation-positive phase=workflow-snapshot-witnessed\n');
           const progressEntity='Orders.CheckoutProgress',progressTable=ordersPhysical.tables.find(row=>row.entity===progressEntity);
           assert.ok(progressTable,'generated physical schema must contain the progress record');
           const originalProgress=ordersStorage.inspectStoredRecord(progressEntity,0,{orderId}) as Record<string,unknown>|null;
           assert.ok(originalProgress,'the original generated claim must have a durable Progress row');
           const progressColumns=[...progressTable.columns.map(column=>column.sql_name),'_craft_row',
            ...progressTable.keys.map((_key,index)=>'_craft_key_'+index)];
           const quote=(name:string)=>'"'+name.replaceAll('"','""')+'"';
           const updateProgress='UPDATE '+quote(progressTable.physical_name)+' SET '+progressColumns.map(name=>quote(name)+'=?').join(', ')+
            ' WHERE "_craft_key_0"=?';
           const originalEncoded=ordersPhysical.encode(progressEntity,originalProgress as any);
           const primaryKey=originalEncoded.bindings[progressTable.columns.length+1];
           assert.ok(primaryKey instanceof Uint8Array,'generated Progress primary key must be encoded');
           const writeProgress=(value:Record<string,unknown>)=>{
            const encoded=ordersPhysical.encode(progressEntity,value as any);
            const db=new DatabaseSync(path.join(ordersRoot,'store.sqlite'));
            try{assert.equal(db.prepare(updateProgress).run(...encoded.bindings,primaryKey).changes,1,
             'the exact generated Progress row must be updated');}finally{db.close();}
           };
           const owner=originalProgress.workerOwner as {kind:string;value?:string};
           assert.equal(owner.kind,'some','the generated claim must establish a worker owner');
           try{
            writeProgress({...originalProgress,workerOwner:{kind:'some',value:'foreign-worker'}});
            assert.throws(()=>snapshots.recheck(witnessed.handle),
             error=>code('StaleOwner')(error)||code('StaleClaim')(error)||code('ForeignWorkerSnapshot')(error),
             'wrong durable Progress worker owner must reject the original snapshot');
            writeProgress({...originalProgress,workerEpoch:(originalProgress.workerEpoch as bigint)+1n});
            assert.throws(()=>snapshots.recheck(witnessed.handle),
             error=>code('StaleOwner')(error)||code('StaleClaim')(error)||code('ForeignWorkerSnapshot')(error),
             'wrong durable Progress worker epoch must reject the original snapshot');
           }finally{writeProgress(originalProgress);}
           assert.deepEqual(snapshots.recheck(witnessed.handle),original,
            'restoring the exact original generated Progress row must restore the snapshot');
           assert.throws(()=>worker.assertContextCurrent(Object.freeze({...context})),code('ForeignOwner'),
            'a copied WorkerContext must not acquire the original private worker claim');
           const resumes=createCommerceWorkflowResumeSelectorV1(binding,worker);
           try{
            const selectedCase=resumes.select(original.value,context),decision=resumes.inspectSelection(selectedCase);
            assert.equal(decision.outcome,'selected');
            assert.deepEqual(decision.action,{kind:'step',target:'reserve'});
            const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
            const identityDirectory=path.join(root,'workflow-step-identity');mkdirSync(identityDirectory);
            const identities=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,calls,
             stage,source,domain,baseline,identityDirectory);
            try{
             const identity=identities.derive(resumes,selectedCase,snapshots,witnessed.handle);
             assert.ok(progressClaim);
             const committedStep=ordersStorage.prepareWorkflowStepJournal(binding,schedule.claim,progressClaim,identities,identity);
             assert.equal(committedStep.kind,'prepared','source selected reserve step must commit its original Prepared journal');
             process.stderr.write('observation-positive phase=workflow-journal-prepared\n');
             const causalDirectory=path.join(root,'workflow-causal-projection');mkdirSync(causalDirectory);
             const causal=await createCommerceWorkflowCausalProjectionOwnerV1(binding,semantics,semantic,calls,
              stage,source,domain,baseline,causalDirectory);
             try{
              const projectedCall=causal.derive(identities,identity,resumes,selectedCase,snapshots,witnessed.handle);
              process.stderr.write('observation-positive phase=workflow-causal-projected\n');
             if(committedStep.kind==='prepared'){
              const dispatched=ordersStorage.markWorkflowStepDispatched(binding,committedStep.journal,identities,identity);
              assert.equal(dispatched.kind,'dispatched','original StepJournal must be durably Dispatched before remote call');
              if(dispatched.kind==='dispatched'){
               process.stderr.write('observation-positive phase=workflow-journal-dispatched\n');
               if(recoveryChildRoot&&recoveryCrashPoint==='before-effect'){
                process.stderr.write('observation-positive phase=recovery-child-ready\n');
                await new Promise<void>(()=>{setInterval(()=>{},1000);});
               }
               const protectedCall=createCommerceWorkflowProtectedCallBindingV1(binding,ordersStorage,
                dispatched.journal,causal,projectedCall),protectedView=protectedCall.initial();
               const inventoryRoot=path.join(root,'inventory-store'),inventoryStorage=await createCommerceServiceStorageOwnerV1(
                sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'inventory',inventoryRoot);
               let inventoryDb:DatabaseSync|undefined,remoteOwner:Awaited<ReturnType<typeof createCommerceWorkflowRemoteResultOwnerV1>>|undefined,observationRunner:Awaited<ReturnType<typeof createCommerceGeneratedOperationRuntimeV1>>|undefined;
               try{
                const inventoryService=sqlite.bindService('inventory'),inventoryBundle=sqlite.materialize(inventoryService,
                 path.join(root,'inventory-fixture-repository')),inventoryData=await sqlite.loadDataComponent(inventoryBundle),
                 inventoryPhysical=deriveCommerceSqlitePhysicalLayoutV1(inventoryData),stockTable=inventoryPhysical.tables.find(row=>row.entity==='Inventory.Stock');
                assert.ok(stockTable);
                inventoryDb=new DatabaseSync(path.join(inventoryRoot,'store.sqlite'));
                inventoryDb.prepare(stockTable.insert_sql).run(...inventoryPhysical.encode('Inventory.Stock',
                 {sku:'sku-one',onHand:20n,reserved:0n,allocated:0n,version:1n}).bindings);
                inventoryDb.close();inventoryDb=undefined;
                const reserveEntry=auth.bindEntry(protectedView.entry_id),reserveDefinition=auth.inspectEntry(reserveEntry),
                 reserveSubject='service-orders',reserveEvidence='reserve-workflow-evidence';
                try{
                 const reserveFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:reserveSubject,evidence:reserveEvidence,
                  session:'reserve-workflow-session',valid_for_seconds:7200,
                  routes:[{entry:protectedView.entry_id,permission:reserveDefinition.access.auth_permission}]}),
                  reserveActor=registerCommerceEntryFixtureActorV1(auth,reserveFixture.handle,{subject:reserveSubject,evidence:reserveEvidence,
                   principal_kind:'service',service_id:'orders',scope:reserveDefinition.access.auth_permission.scope});
                 try{
                  const reserveInput=protectedView.arguments,reserveWire=Buffer.from(JSON.stringify(reserveInput,
                   (_key,value)=>typeof value==='bigint'?String(value):value));
                  const admissionStartedAt=performance.now();
                  const started=await selected.beginWorkflowServiceStep(reserveActor,protectedView.entry_id,
                   reserveWire,reserveInput,protectedCall).finally(()=>process.stderr.write(
                    'observation-positive admission_ms='+Math.round(performance.now()-admissionStartedAt)+'\n'));
                  assert.equal(started.ok,true,'fresh Auth and original Dispatched journal must admit reserve: '+
                   (started.ok?'admitted':started.code));
                  if(started.ok){
                   const branches=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,semantic,domain,baseline);
                   try{
                    remoteOwner=await createCommerceWorkflowRemoteResultOwnerV1(sources,capture,stage,source,domain,baseline,
                     plans,selected,inventoryStorage,started.invocation,path.join(root,'inventory-reserve-operation'),
                     protectedCall,branches,identities,identity,snapshots,witnessed.handle);
                    const reserved=await remoteOwner.execute();
                    assert.equal(reserved.kind,'returned','original protected ReserveStock must produce an opaque result');
                    if(reserved.kind!=='returned')return;
                    process.stderr.write('observation-positive phase=remote-result-returned\n');
                    if(recoveryChildRoot&&recoveryCrashPoint==='after-effect'){
                     const command=inventoryStorage.inspectStoredRecord('Inventory.StockCommandRecord',0,
                      {commandId:protectedView.command_id}) as {outcome:{kind:string}}|null;
                     const stock=inventoryStorage.inspectStoredRecord('Inventory.Stock',0,{sku:'sku-one'}) as
                      {reserved:bigint;version:bigint}|null;
                     const journal=ordersStorage.inspectStoredRecord(binding.inspect().journal_entity,0,{
                      consumerEntryId:protectedView.consumer_entry_id,occurrenceId:protectedView.occurrence_id,
                      stepName:protectedView.step_name,commandId:protectedView.command_id}) as
                      {phase:string;version:bigint}|null;
                     assert.equal(command?.outcome.kind,'Applied');
                     assert.equal(stock?.reserved,1n);
                     assert.equal(stock?.version,2n);
                     assert.equal(journal?.phase,'Dispatched');
                     assert.equal(journal?.version,2n);
                     process.stderr.write('observation-positive phase=recovery-after-effect-ready\n');
                     await new Promise<void>(()=>{setInterval(()=>{},1000);});
                    }
                    const branch=remoteOwner.select(reserved.handle);
                    assert.equal(branch.outcome,'selected');
                    assert.equal(branch.step_name,'reserve');
                    assert.ok(branch.observation,'selected source branch must produce the observation');
                    process.stderr.write('observation-positive phase=source-branch-selected\n');
                    const proposals=createCommerceWorkflowObservationProposalOwnerV1(binding,semantics,semantic,
                     remoteOwner,reserved.handle,snapshots,witnessed.handle,worker,context);
                    try{
                     const proposal=proposals.propose(),proposed=proposals.inspect(proposal);
                     assert.equal(proposed.entry_id,'Orders.RecordCheckoutObservationEntry');
                     assert.equal(proposed.input.orderId,orderId);
                     const admission=createCommerceWorkflowObservationAdmissionV1(binding,semantics,semantic,
                      ordersStorage,proposals,proposal,worker,context);
                     const admitted=admission.inspect();
                     assert.equal(admitted.entry_id,proposed.entry_id);
                     assert.equal(admitted.qualification,
                      'current-original-proposal-and-worker-observation-data;fresh-auth-and-atomic-commit-required');
                     assert.equal(admitted.authority_effect,'none');
                     process.stderr.write('observation-positive phase=observation-proposal-admitted\n');
                     const observationEntry=auth.bindEntry(admitted.entry_id),
                      observationDefinition=auth.inspectEntry(observationEntry);
                     const observationFixture=seedCommerceAuthFixtureDatabaseV1(native,{
                      subject:'service-observation-worker',evidence:'observation-worker-evidence',
                      session:'observation-worker-session',valid_for_seconds:7200,
                      routes:[{entry:admitted.entry_id,
                       permission:observationDefinition.access.auth_permission}]});
                     const observationActor=registerCommerceEntryFixtureActorV1(auth,observationFixture.handle,{
                      subject:'service-observation-worker',evidence:'observation-worker-evidence',
                      principal_kind:'service',service_id:'orders',
                      scope:observationDefinition.access.auth_permission.scope});
                     try{
                      const observationInput=admitted.input,
                       observationWire=Buffer.from(JSON.stringify(observationInput,
                        (_key,value)=>typeof value==='bigint'?String(value):value));
                      // Public workflow records and codec copies may have different
                      // prototypes. A changed source-typed value must still reject.
                      await assert.rejects(()=>selected.beginWorkflowObservation(observationActor,admitted.entry_id,
                       observationWire,{...observationInput,expectedOrderVersion:observationInput.expectedOrderVersion+1n},
                       ordersStorage,binding,admission,worker,context),code('ForeignAuthorizedInput'),
                       'changed parameters cannot reuse the original authorized wire');
                      const authorized=await selected.beginWorkflowObservation(observationActor,admitted.entry_id,
                       observationWire,observationInput,ordersStorage,binding,admission,worker,context);
                      assert.equal(authorized.ok,true,'fresh Orders worker Auth must authorize the original observation');
                      if(authorized.ok){
                       process.stderr.write('observation-positive phase=observation-authorized\n');
                       try{
                        observationRunner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,
                         domain,baseline,plans,selected,ordersStorage,authorized.invocation,
                         path.join(root,'orders-observation-operation'));
                        process.stderr.write('observation-positive phase=observation-runner-ready\n');
                        const committed=await observationRunner.run(authorized.invocation);
                        assert.equal(committed.kind,'returned','generated RecordCheckoutObservation must atomically commit');
                        process.stderr.write('observation-positive phase=observation-committed\n');
                        if(committed.kind==='returned'){
                         assert.equal((committed.value as {fresh:boolean}).fresh,true);
                         assert.equal(committed.commits.length,1);
                        }
                        const committedOrder=ordersStorage.inspectStoredRecord('Orders.Order',0,{id:orderId}) as
                         {version:bigint;status:unknown}|null;
                        const committedProgress=ordersStorage.inspectStoredRecord(binding.inspect().workflow.durable_state,
                         0,{orderId}) as {version:bigint;state:unknown;reserveResult:{kind:string}}|null;
                        assert.ok(committedOrder);assert.ok(committedProgress);
                        assert.equal(committedOrder.version,proposed.order_version+1n);
                        assert.equal(committedProgress.version,proposed.progress_version+1n);
                        assert.deepEqual(structural(committedOrder.status),structural(committedProgress.state));
                        assert.equal(committedProgress.reserveResult.kind,'some');
                        const observedJournal=ordersStorage.inspectStoredRecord(binding.inspect().journal_entity,0,{
                         consumerEntryId:protectedView.consumer_entry_id,occurrenceId:protectedView.occurrence_id,
                         stepName:protectedView.step_name,commandId:protectedView.command_id}) as
                         {phase:string;version:bigint;observation:{kind:string}}|null;
                        assert.ok(observedJournal,'generated observation must atomically advance the original step journal');
                        assert.equal(observedJournal.phase,'Observed');
                        assert.equal(observedJournal.version,3n);
                        assert.equal(observedJournal.observation.kind,'some');
                        assert.throws(()=>admission.inspect(),code('StaleSnapshot'));
                        assert.throws(()=>identities.recheck(identity),code('StaleSnapshot'),
                         'the original step identity must reject its pre-observation snapshot');
                        snapshots.dispose();
                        assert.throws(()=>identities.recheck(identity),code('DisposedOwner'),
                         'retiring the original snapshot owner must invalidate the step identity');
                        worker.dispose();
                        assert.throws(()=>worker.assertContextCurrent(context),code('DisposedOwner'),
                         'a retired WorkerContext owner must reject its own original worker');
                        successful=true;
                       }finally{observationRunner?.dispose();selected.retire(authorized.invocation);}
                      }
                     }finally{auth.disposeActor(observationActor);auth.disposeEntry(observationEntry);}
                    }finally{proposals.dispose();}
                   }finally{remoteOwner?.dispose();branches.dispose();selected.retire(started.invocation);}
                  }
                 }finally{auth.disposeActor(reserveActor);}
                }finally{auth.disposeEntry(reserveEntry);}
               }finally{inventoryDb?.close();inventoryStorage.close();}
              }
             }
             }finally{causal.dispose();}
            }finally{identities.dispose();}
           }finally{resumes.dispose();}
          }
         }finally{snapshots.dispose();}
        }finally{snapshotQuery.dispose();snapshotCodec.dispose();plans.disposeRead(read);selected.retire(snapshotStart.invocation);}
       }
      }finally{auth.disposeActor(snapshotActor);auth.disposeEntry(snapshotEntry);}
      selected.retire(started.invocation);
     }
    }finally{auth.disposeActor(claimActor);auth.disposeEntry(claimEntry);}
   }
  }
  sqlite.dispose();
 }finally{worker?.dispose();ordersDb?.close();selected?.dispose();auth?.dispose();await native?.dispose();ordersStorage?.close();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);
  if(!recoveryChildRoot){
   if(successful)rmSync(root,{recursive:true,force:true});
   else process.stderr.write('observation-positive diagnostic fixture retained at '+root+'\n');
  }
 }
});
