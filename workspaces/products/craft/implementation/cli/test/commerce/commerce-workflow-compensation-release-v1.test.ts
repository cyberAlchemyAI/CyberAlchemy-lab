/** A generated-schema Commerce fixture exercises original release compensation,
 * observation, and the source-ordered next step. */
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
import {createCommerceIdentityComponentOwner} from '../../src/commerce/commerce-identity-component.js';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.js';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.js';

const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url)),candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;
const structural=(value:any):any=>Array.isArray(value)?value.map(structural):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([key,child])=>[key,structural(child)])):value;

test('original ReleaseReservation compensates and commits ReleaseApplied before cancel-payment',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-compensation-fixture-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture),paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline),models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models),assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let ordersStorage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined,
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
  const lines=[{sku:'sku-one',quantity:1n}];
  const identityCalls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline),
   observationOperation=plans.bindOperation('Orders.RecordCheckoutObservation'),
   observationPlan=plans.inspectOperation(observationOperation).plan,
   sourceCalls=identityCalls.paths(observationPlan).map(callPath=>identityCalls.bind(observationPlan,callPath)),
   cancelOperation=plans.bindOperation('Orders.CancelOrder'),
   cancelPlan=plans.inspectOperation(cancelOperation).plan,
   cancelCalls=identityCalls.paths(cancelPlan).map(callPath=>identityCalls.bind(cancelPlan,callPath));
  const reservationCall=sourceCalls.find(call=>{
   const binding=identityCalls.inspect(call);
   return binding.observation.method==='commandId'&&binding.parameters[0]?.literal?.value==='inventory.reservation';
  }),linesCall=sourceCalls.find(call=>identityCalls.inspect(call).observation.method==='stockLinesFingerprint'),
   captureCall=cancelCalls.find(call=>identityCalls.inspect(call).observation.method==='captureFingerprint');
  assert.ok(reservationCall&&linesCall&&captureCall,'fixture identities must come from original captured source calls');
  const identityComponent=createCommerceIdentityComponentOwner(identityCalls,stage,source,domain,baseline),
   identityDirectory=path.join(root,'fixture-identity');mkdirSync(identityDirectory);
  const identity=await identityComponent.materialize([reservationCall,linesCall,captureCall],identityDirectory);
  const reservationIdResult=identityComponent.evaluateBoundParameters(identity,reservationCall,['inventory.reservation',orderId]),
   linesFingerprintResult=identityComponent.evaluateBoundParameters(identity,linesCall,[lines]),
   captureFingerprintResult=identityComponent.evaluateBoundParameters(identity,captureCall,
    ['cmd_fixture_capture_one',orderId,100n,'USD']);
  assert.equal(reservationIdResult.ok,true);assert.equal(linesFingerprintResult.ok,true);
  assert.equal(captureFingerprintResult.ok,true);
  const reservationId=reservationIdResult.value as string,linesFingerprint=linesFingerprintResult.value as string,
   captureFingerprint=captureFingerprintResult.value as string;
  identityComponent.dispose(identity);for(const call of [...sourceCalls,...cancelCalls])identityCalls.dispose(call);
  plans.disposeOperation(observationOperation);plans.disposeOperation(cancelOperation);
  const reservation={reservationId,orderId,lines,linesFingerprint,
   reserveCommandId:'cmd_fixture_reserve_one',lastCommandId:'cmd_fixture_reserve_one',status:'Reserved',version:1n};
  const order={id:orderId,customerId:'customer-one',quoteId:'quote-one',currency:'USD',payableMinor:100n,
   lines,status:'Cancelling',version:1n};
  const progress={orderId,state:'Cancelling',reserveCommandId:'cmd_fixture_reserve_one',
   captureAttemptKey:'cmd_fixture_capture_one',allocateCommandId:'cmd_fixture_allocate_one',
   releaseCommandId:'cmd_fixture_release_one',confirmCommandId:'cmd_fixture_confirm_one',
   cancelCommandId:'cmd_fixture_cancel_one',reserveResult:{kind:'some',value:reservation},reserveRejected:{kind:'none'},
   paymentResult:{kind:'some',value:{attemptKey:'cmd_fixture_capture_one',orderId,amountMinor:100n,
    currency:'USD',requestFingerprint:captureFingerprint,status:'Declined',
    providerReference:{kind:'some',value:'provider-decline-one'},version:1n}},
   allocationResult:{kind:'none'},releaseResult:{kind:'none'},
   captureDispatched:true,workerOwner:{kind:'none'},workerEpoch:0n,version:1n};
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
  process.stderr.write('compensation-release phase=generated-schema-fixture-seeded\n');
  if(process.env.CRAFT_COMPENSATION_FIXTURE_PREFLIGHT==='1')return;
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,
   path.join(root,'auth'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,
   domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  process.stderr.write('compensation-release phase=auth-and-selection-ready\n');
  const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
  const ingress=await ordersStorage.enqueueCommittedWorkflowEvent(binding,occurrenceId);
  assert.equal(ingress.kind,'enqueued','generated-schema outbox fixture must create the original Workflow Inbox and WorkSchedule');
  process.stderr.write('compensation-release phase=inbox-enqueued\n');
  const schedule=ordersStorage.claimVacantWorkSchedule(binding,occurrenceId);
  assert.equal(schedule.kind,'claimed','original vacant WorkSchedule must yield one native committed claim');
  process.stderr.write('compensation-release phase=schedule-claimed\n');
  if(schedule.kind==='claimed'){
   worker=createCommerceWorkerContextOwnerV1(binding,ordersStorage);
   const context=worker.registerCommittedClaim(schedule.claim);
   const journal=ordersStorage.prepareClaimJournal(binding,schedule.claim);
   assert.equal(journal.kind,'prepared','source claim driver must commit its original Prepared StepJournal');
   if(journal.kind==='prepared'){
    const recorded=ordersStorage.inspectClaimJournal(journal.journal);
    const claimEntryId=recorded.target_entry_id,claimEntry=auth.bindEntry(claimEntryId),claimDefinition=auth.inspectEntry(claimEntry);
    const claimFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-claim-worker',evidence:'claim-worker-evidence',valid_for_seconds:7200,
     session:'claim-worker-session',routes:[{entry:claimEntryId,permission:claimDefinition.access.auth_permission}]});
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
      process.stderr.write('compensation-release phase=claim-runner-ready\n');
      try{
       const claimed=await claimRunner.run(started.invocation);
       assert.equal(claimed.kind,'returned','generated ClaimCheckoutWork must commit the source-owned progress claim');
       const receipts=claimed.commits as readonly object[];assert.equal(receipts.length,1);
       progressClaim=worker.registerCommittedProgressClaim(context,claimRunner,selected,started.invocation,receipts[0]!);
      }finally{claimRunner.dispose();}
      assert.ok(progressClaim);
      process.stderr.write('compensation-release phase=claim-progress-committed\n');
      const snapshotEntryId='Orders.ReadCheckoutSnapshotEntry',snapshotEntry=auth.bindEntry(snapshotEntryId),
       snapshotDefinition=auth.inspectEntry(snapshotEntry);
      const snapshotFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-snapshot-worker',evidence:'snapshot-worker-evidence',valid_for_seconds:7200,
       session:'snapshot-worker-session',routes:[{entry:snapshotEntryId,permission:snapshotDefinition.access.auth_permission}]});
      const snapshotActor=registerCommerceEntryFixtureActorV1(auth,snapshotFixture.handle,{subject:'service-snapshot-worker',
       evidence:'snapshot-worker-evidence',principal_kind:'service',service_id:'orders',scope:snapshotDefinition.access.auth_permission.scope});
      try{
       const snapshotInput={orderId},snapshotWire=Buffer.from(JSON.stringify(snapshotInput));
       const snapshotStart=await selected.beginWorkerRead(snapshotActor,snapshotEntryId,snapshotWire,snapshotInput,
        ordersStorage,binding,journal.journal,worker,context);
       assert.equal(snapshotStart.ok,true,'fresh worker Query Entry must admit the original committed progress owner');
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
           process.stderr.write('compensation-release phase=workflow-snapshot-witnessed\n');
           const resumes=createCommerceWorkflowResumeSelectorV1(binding,worker);
           try{
            const selectedCase=resumes.select(original.value,context),decision=resumes.inspectSelection(selectedCase);
            assert.equal(decision.outcome,'selected');
            assert.deepEqual(decision.action,{kind:'step',target:'release'});
            const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
            const identityDirectory=path.join(root,'workflow-step-identity');mkdirSync(identityDirectory);
            const identities=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,calls,
             stage,source,domain,baseline,identityDirectory);
            try{
             const identity=identities.derive(resumes,selectedCase,snapshots,witnessed.handle);
             assert.ok(progressClaim);
             const committedStep=ordersStorage.prepareWorkflowStepJournal(binding,schedule.claim,progressClaim,identities,identity);
             assert.equal(committedStep.kind,'prepared','source selected release step must commit its original Prepared journal');
             process.stderr.write('compensation-release phase=workflow-journal-prepared\n');
             const causalDirectory=path.join(root,'workflow-causal-projection');mkdirSync(causalDirectory);
             const causal=await createCommerceWorkflowCausalProjectionOwnerV1(binding,semantics,semantic,calls,
              stage,source,domain,baseline,causalDirectory);
             try{
              const projectedCall=causal.derive(identities,identity,resumes,selectedCase,snapshots,witnessed.handle);
              process.stderr.write('compensation-release phase=workflow-causal-projected\n');
             if(committedStep.kind==='prepared'){
              const dispatched=ordersStorage.markWorkflowStepDispatched(binding,committedStep.journal,identities,identity);
              assert.equal(dispatched.kind,'dispatched','original StepJournal must be durably Dispatched before remote call');
              if(dispatched.kind==='dispatched'){
               process.stderr.write('compensation-release phase=workflow-journal-dispatched\n');
               const protectedCall=createCommerceWorkflowProtectedCallBindingV1(binding,ordersStorage,
                dispatched.journal,causal,projectedCall),protectedView=protectedCall.inspect();
               const inventoryRoot=path.join(root,'inventory-store'),inventoryStorage=await createCommerceServiceStorageOwnerV1(
                sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'inventory',inventoryRoot);
               let inventoryDb:DatabaseSync|undefined,remoteOwner:Awaited<ReturnType<typeof createCommerceWorkflowRemoteResultOwnerV1>>|undefined,observationRunner:Awaited<ReturnType<typeof createCommerceGeneratedOperationRuntimeV1>>|undefined;
               try{
                const inventoryService=sqlite.bindService('inventory'),inventoryBundle=sqlite.materialize(inventoryService,
                 path.join(root,'inventory-fixture-repository')),inventoryData=await sqlite.loadDataComponent(inventoryBundle),
                 inventoryPhysical=deriveCommerceSqlitePhysicalLayoutV1(inventoryData),
                 stockTable=inventoryPhysical.tables.find(row=>row.entity==='Inventory.Stock'),
                 reservationTable=inventoryPhysical.tables.find(row=>row.entity==='Inventory.Reservation');
                assert.ok(stockTable&&reservationTable);
                inventoryDb=new DatabaseSync(path.join(inventoryRoot,'store.sqlite'));
                inventoryDb.prepare(stockTable.insert_sql).run(...inventoryPhysical.encode('Inventory.Stock',
                 {sku:'sku-one',onHand:20n,reserved:1n,allocated:0n,version:1n}).bindings);
                inventoryDb.prepare(reservationTable.insert_sql).run(...inventoryPhysical.encode('Inventory.Reservation',reservation).bindings);
                inventoryDb.close();inventoryDb=undefined;
                const releaseEntry=auth.bindEntry(protectedView.entry_id),releaseDefinition=auth.inspectEntry(releaseEntry),
                 releaseSubject='service-orders',releaseEvidence='release-workflow-evidence';
                try{
                 const releaseFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:releaseSubject,evidence:releaseEvidence,valid_for_seconds:7200,
                  session:'release-workflow-session',routes:[{entry:protectedView.entry_id,permission:releaseDefinition.access.auth_permission}]}),
                  releaseActor=registerCommerceEntryFixtureActorV1(auth,releaseFixture.handle,{subject:releaseSubject,evidence:releaseEvidence,
                   principal_kind:'service',service_id:'orders',scope:releaseDefinition.access.auth_permission.scope});
                 try{
                  const releaseInput=protectedView.arguments,releaseWire=Buffer.from(JSON.stringify(releaseInput,
                   (_key,value)=>typeof value==='bigint'?String(value):value));
                  const started=await selected.beginWorkflowServiceStep(releaseActor,protectedView.entry_id,
                   releaseWire,releaseInput,protectedCall);
                  assert.equal(started.ok,true,'fresh Auth and original Dispatched journal must admit release');
                  if(started.ok){
                   const branches=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,semantic,domain,baseline);
                   try{
                    remoteOwner=await createCommerceWorkflowRemoteResultOwnerV1(sources,capture,stage,source,domain,baseline,
                     plans,selected,inventoryStorage,started.invocation,path.join(root,'inventory-release-operation'),
                     protectedCall,branches,identities,identity,snapshots,witnessed.handle);
                    const released=await remoteOwner.execute();
                    assert.equal(released.kind,'returned','original protected ReleaseReservation must produce an opaque result');
                    if(released.kind!=='returned')return;
                    process.stderr.write('compensation-release phase=remote-result-returned\n');
                    const branch=remoteOwner.select(released.handle);
                    assert.equal(branch.outcome,'selected');
                    assert.equal(branch.step_name,'release');
                    assert.deepEqual(branch.action,{kind:'step',target:'cancel-payment'});
                    assert.ok(branch.observation,'selected source branch must produce the observation');
                    process.stderr.write('compensation-release phase=source-branch-selected\n');
                    const proposals=createCommerceWorkflowObservationProposalOwnerV1(binding,semantics,semantic,
                     remoteOwner,released.handle,snapshots,witnessed.handle,worker,context);
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
                     process.stderr.write('compensation-release phase=observation-proposal-admitted\n');
                     const observationEntry=auth.bindEntry(admitted.entry_id),
                      observationDefinition=auth.inspectEntry(observationEntry);
                     const observationFixture=seedCommerceAuthFixtureDatabaseV1(native,{valid_for_seconds:7200,
                      subject:'service-observation-worker',evidence:'observation-worker-evidence',
                      session:'observation-worker-session',routes:[{entry:admitted.entry_id,
                       permission:observationDefinition.access.auth_permission}]});
                     const observationActor=registerCommerceEntryFixtureActorV1(auth,observationFixture.handle,{
                      subject:'service-observation-worker',evidence:'observation-worker-evidence',
                      principal_kind:'service',service_id:'orders',
                      scope:observationDefinition.access.auth_permission.scope});
                     try{
                      const observationInput=admitted.input,
                       observationWire=Buffer.from(JSON.stringify(observationInput,
                        (_key,value)=>typeof value==='bigint'?String(value):value));
                      const authorized=await selected.beginWorkflowObservation(observationActor,admitted.entry_id,
                       observationWire,observationInput,ordersStorage,binding,admission,worker,context);
                      assert.equal(authorized.ok,true,'fresh Orders worker Auth must authorize the original observation');
                      if(authorized.ok){
                       process.stderr.write('compensation-release phase=observation-authorized\n');
                       try{
                        observationRunner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,
                         domain,baseline,plans,selected,ordersStorage,authorized.invocation,
                         path.join(root,'orders-observation-operation'));
                        process.stderr.write('compensation-release phase=observation-runner-ready\n');
                        const committed=await observationRunner.run(authorized.invocation);
                        assert.equal(committed.kind,'returned','generated RecordCheckoutObservation must atomically commit');
                        process.stderr.write('compensation-release phase=observation-committed\n');
                        if(committed.kind==='returned'){
                         assert.equal((committed.value as {fresh:boolean}).fresh,true);
                         assert.equal(committed.commits.length,1);
                        }
                        const committedOrder=ordersStorage.inspectStoredRecord('Orders.Order',0,{id:orderId}) as
                         {version:bigint;status:unknown}|null;
                        const committedProgress=ordersStorage.inspectStoredRecord(binding.inspect().workflow.durable_state,
                         0,{orderId}) as {version:bigint;state:unknown;cancelCommandId:string;
                          reserveResult:{kind:string}}|null;
                        assert.ok(committedOrder);assert.ok(committedProgress);
                        assert.equal(committedOrder.version,proposed.order_version+1n);
                        assert.equal(committedProgress.version,proposed.progress_version+1n);
                        assert.deepEqual(structural(committedOrder.status),structural(committedProgress.state));
                        assert.equal(committedProgress.reserveResult.kind,'some');
                        assert.equal((committedProgress as any).releaseResult.kind,'some');
                        assert.equal(committedProgress.state,'Cancelling');
                        assert.equal((inventoryStorage.inspectStoredRecord('Inventory.Stock',0,{sku:'sku-one'}) as any)?.reserved,0n);
                        assert.equal((inventoryStorage.inspectStoredRecord('Inventory.Reservation',0,{reservationId}) as any)?.status,'Released');
                        const continued=snapshots.read();
                        assert.equal(continued.kind,'snapshot','generated worker Query must read the committed compensation state');
                        if(continued.kind==='snapshot'){
                         const next=resumes.select(snapshots.inspect(continued.handle).value,context),
                          nextDecision=resumes.inspectSelection(next);
                         assert.equal(nextDecision.outcome,'selected');
                         assert.deepEqual(nextDecision.action,{kind:'step',target:'cancel-payment'},
                          'source resume ordering must advance only after committed ReleaseApplied');
                         const cancelIdentity=identities.derive(resumes,next,snapshots,continued.handle),
                          cancelJournal=ordersStorage.prepareWorkflowStepJournal(binding,schedule.claim,
                           progressClaim,identities,cancelIdentity);
                         assert.equal(cancelJournal.kind,'prepared',
                          'the same committed worker must prepare the source-selected cancel-payment step');
                         process.stderr.write('compensation-release phase=cancel-journal-prepared\n');
                         if(cancelJournal.kind==='prepared'){
                          const cancelCausal=causal.derive(identities,cancelIdentity,resumes,next,
                           snapshots,continued.handle),
                           cancelDispatched=ordersStorage.markWorkflowStepDispatched(binding,
                            cancelJournal.journal,identities,cancelIdentity);
                          assert.equal(cancelDispatched.kind,'dispatched',
                           'the original cancel-payment StepJournal must dispatch before the local service call');
                          if(cancelDispatched.kind==='dispatched'){
                           const cancelCall=createCommerceWorkflowProtectedCallBindingV1(binding,ordersStorage,
                            cancelDispatched.journal,causal,cancelCausal),cancelView=cancelCall.inspect();
                           assert.equal(cancelView.step_name,'cancel-payment');
                           assert.equal(cancelView.entry_id,'Orders.CancelOrderEntry');
                           assert.equal(cancelView.command_id,committedProgress.cancelCommandId);
                           process.stderr.write('compensation-release phase=cancel-call-bound\n');
                           const paymentsRoot=path.join(root,'payments-store'),paymentsStorage=await createCommerceServiceStorageOwnerV1(
                            sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,
                            assemblyOwner,assembly,'payments',paymentsRoot);
                           let paymentsDb:DatabaseSync|undefined;
                           try{
                            const paymentsService=sqlite.bindService('payments'),paymentsBundle=sqlite.materialize(
                             paymentsService,path.join(root,'payments-fixture-repository')),
                             paymentsData=await sqlite.loadDataComponent(paymentsBundle),
                             paymentsPhysical=deriveCommerceSqlitePhysicalLayoutV1(paymentsData),
                             attemptTable=paymentsPhysical.tables.find(row=>row.entity==='Payments.PaymentAttempt');
                            assert.ok(attemptTable);
                            paymentsDb=new DatabaseSync(path.join(paymentsRoot,'store.sqlite'));
                            paymentsDb.prepare(attemptTable.insert_sql).run(...paymentsPhysical.encode('Payments.PaymentAttempt',{
                             attemptKey:'cmd_fixture_capture_one',orderId,amountMinor:100n,currency:'USD',
                             requestFingerprint:captureFingerprint,status:'Declined',dispatchState:'Dispatched',
                             providerReference:{kind:'some',value:'provider-decline-one'},
                             priorDefinitive:{kind:'some',value:{status:'Declined',providerReference:'provider-decline-one'}},
                             version:1n,
                            }).bindings);
                            paymentsDb.close();paymentsDb=undefined;
                            const paymentRead=plans.bindRead('Payments.ReadPayment'),
                             reservationRead=plans.bindRead('Inventory.ReadReservation');
                            const paymentCodec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,
                             baseline,plans,paymentRead),reservationCodec=await createCommerceSourceQueryOutputCodecV1(
                             stage,source,domain,baseline,plans,reservationRead);
                            const paymentQuery=createCommerceSourceQueryRuntimeV1(stage,source,plans,paymentRead,
                             domain,baseline,paymentsStorage,paymentCodec),
                             reservationQuery=createCommerceSourceQueryRuntimeV1(stage,source,plans,reservationRead,
                              domain,baseline,inventoryStorage,reservationCodec);
                            try{
                             const serviceActors:ReturnType<typeof registerCommerceEntryFixtureActorV1>[]=[];
                             for(const entryId of ['Payments.ReadPaymentEntry','Inventory.ReadReservationEntry']){
                              const entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry);
                              try{
                               const evidence='cancel-evidence-'+entryId.replaceAll('.','-'),
                                fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-orders',evidence,valid_for_seconds:7200,
                                 session:'cancel-session-'+entryId.replaceAll('.','-'),
                                 routes:[{entry:entryId,permission:definition.access.auth_permission}]}),
                                actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject:'service-orders',
                                 evidence,principal_kind:'service',service_id:'orders',
                                 scope:definition.access.auth_permission.scope});
                               selected.registerServiceActor(entryId,actor);serviceActors.push(actor);
                              }finally{auth.disposeEntry(entry);}
                             }
                             const cancelEntry=auth.bindEntry(cancelView.entry_id),cancelDefinition=auth.inspectEntry(cancelEntry);
                             try{
                              const cancelFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-orders',valid_for_seconds:7200,
                               evidence:'cancel-order-evidence',session:'cancel-order-session',
                               routes:[{entry:cancelView.entry_id,permission:cancelDefinition.access.auth_permission}]}),
                               cancelActor=registerCommerceEntryFixtureActorV1(auth,cancelFixture.handle,{
                                subject:'service-orders',evidence:'cancel-order-evidence',principal_kind:'service',
                                service_id:'orders',scope:cancelDefinition.access.auth_permission.scope});
                              try{
                               const cancelInput=cancelView.arguments,cancelWire=Buffer.from(JSON.stringify(cancelInput,
                                (_key,value)=>typeof value==='bigint'?String(value):value)),
                                authorized=await selected.beginWorkflowWorkerStep(cancelActor,cancelView.entry_id,
                                 cancelWire,cancelInput,ordersStorage,binding,cancelCall,worker,context);
                               assert.equal(authorized.ok,true,'fresh worker Auth must admit source-selected CancelOrder');
                               if(authorized.ok){
                                try{
                                 const cancelResult=await createCommerceWorkflowRemoteResultOwnerV1(sources,capture,
                                  stage,source,domain,baseline,plans,selected,ordersStorage,authorized.invocation,
                                  path.join(root,'orders-cancel-operation'),cancelCall,branches,identities,
                                  cancelIdentity,snapshots,continued.handle,{externalQueries:[paymentQuery,reservationQuery]});
                                 try{
                                  const cancelled=await cancelResult.execute();
                                  assert.equal(cancelled.kind,'returned',
                                   'source-selected CancelOrder must finish after fresh delegated evidence reads');
                                  if(cancelled.kind==='returned'){
                                   const nativeResult=cancelResult.inspect(cancelled.handle);
                                   assert.equal(nativeResult.committed_same_service,true,
                                    'terminal eligibility requires the original same-service native commit');
                                   assert.ok(nativeResult.native_commits>0,
                                    'terminal eligibility requires a nonempty native commit receipt set');
                                   const terminalBranch=cancelResult.select(cancelled.handle);
                                   assert.equal(terminalBranch.outcome,'selected',
                                    'the original committed CancelOrder result must select its authored branch');
                                   assert.deepEqual(terminalBranch.action,{kind:'finish',target:'cancelled'});
                                   assert.equal(terminalBranch.observation,null,
                                    'the terminal branch retains the original journal without an invented observation');
                                   const finalOrder=ordersStorage.inspectStoredRecord('Orders.Order',0,{id:orderId}) as
                                    {version:bigint;status:unknown}|null;
                                   const finalProgress=ordersStorage.inspectStoredRecord(binding.inspect().workflow.durable_state,
                                    0,{orderId}) as {version:bigint;state:unknown}|null;
                                   assert.ok(finalOrder);assert.ok(finalProgress);
                                   assert.equal(finalOrder.status,'Cancelled');
                                   assert.equal(finalProgress.state,'Cancelled');
                                   assert.equal(finalOrder.version,committedOrder.version+1n);
                                   assert.equal(finalProgress.version,committedProgress.version+1n);
                                  }
                                  process.stderr.write('compensation-release phase=cancel-result-returned\n');
                                 }finally{cancelResult.dispose();}
                                }finally{selected.retire(authorized.invocation);}
                               }
                              }finally{auth.disposeActor(cancelActor);}
                             }finally{auth.disposeEntry(cancelEntry);for(const actor of serviceActors)auth.disposeActor(actor);}
                            }finally{paymentQuery.dispose();reservationQuery.dispose();paymentCodec.dispose();
                             reservationCodec.dispose();plans.disposeRead(paymentRead);plans.disposeRead(reservationRead);}
                           }finally{paymentsDb?.close();paymentsStorage.close();}
                          }
                         }
                        }
                        assert.throws(()=>admission.inspect(),code('StaleSnapshot'));
                       }finally{observationRunner?.dispose();selected.retire(authorized.invocation);}
                      }
                     }finally{auth.disposeActor(observationActor);auth.disposeEntry(observationEntry);}
                    }finally{proposals.dispose();}
                   }finally{remoteOwner?.dispose();branches.dispose();selected.retire(started.invocation);}
                  }
                 }finally{auth.disposeActor(releaseActor);}
                }finally{auth.disposeEntry(releaseEntry);}
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
 }finally{worker?.dispose();ordersDb?.close();selected?.dispose();auth?.dispose();await native?.dispose();ordersStorage?.close();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
