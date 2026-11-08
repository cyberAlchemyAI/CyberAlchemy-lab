/** Original Catalog Query row is released only through selected Entry access. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,mkdtempSync,mkdirSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../src/commerce/commerce-binding-assembly-v1.js';
import {createCommerceSqliteFamilyOwnerV1} from '../src/commerce/commerce-sqlite-family-v1.js';
import {createCommerceServiceStorageOwnerV1,type CommerceWorkerProgressClaimV1} from '../src/commerce/commerce-service-storage-v1.js';
import {createCommerceSourceQueryOutputCodecV1} from '../src/commerce/commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1} from '../src/commerce/commerce-source-query-runtime-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1} from '../src/commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceGeneratedOperationRuntimeV1} from '../src/commerce/commerce-generated-operation-runtime-v1.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1} from '../src/commerce/commerce-worker-context-v1.js';
import {createCommerceWorkflowSnapshotOwnerV1} from '../src/commerce/commerce-workflow-snapshot-v1.js';
import {createCommerceWorkflowResumeSelectorV1} from '../src/commerce/commerce-workflow-resume-v1.js';
import {createCommerceIdentityCallOwner} from '../src/commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowStepArgumentsOwnerV1} from '../src/commerce/commerce-workflow-step-arguments-v1.js';
import {createCommerceWorkflowStepIdentityOwnerV1} from '../src/commerce/commerce-workflow-step-identity-v1.js';
import {createCommerceWorkflowPreparedJournalProjectionV1} from '../src/commerce/commerce-workflow-prepared-journal-projection-v1.js';
import {createCommerceWorkflowCausalProjectionOwnerV1} from '../src/commerce/commerce-workflow-causal-projection-v1.js';
import {createCommerceWorkflowProtectedCallBindingV1} from '../src/commerce/commerce-workflow-protected-call-binding-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;
const structural=(value:any):any=>Array.isArray(value)?value.map(structural):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([key,child])=>[key,structural(child)])):value;

test('selected Catalog Query retains genuine row until original delegated access passes',async t=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-query-selected-row-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture),paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline),models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models),assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined,ordersStorage:typeof storage,runner:Awaited<ReturnType<typeof createCommerceGeneratedOperationRuntimeV1>>|undefined,native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined,auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined,selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined,db:DatabaseSync|undefined,ordersDb:DatabaseSync|undefined,worker:CommerceWorkerContextOwnerV1|undefined;
 try{
  const storageRoot=path.join(root,'catalog-store');
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'catalog',storageRoot);
  const read=plans.bindRead('Catalog.ReadQuote'),codec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,read),query=createCommerceSourceQueryRuntimeV1(stage,source,plans,read,domain,baseline,storage,codec);
  assert.throws(()=>query.execute({quoteId:'quote-one',customerId:'customer-one'}),code('ScopedQueryGuardRequired'));
  assert.throws(()=>codec.copy({kind:'some',value:{id:'quote-one'}} as any),code('InvalidQueryOutput'));
  const sqlite=createCommerceSqliteFamilyOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner.family(assembly));
  const service=sqlite.bindService('catalog'),bundle=sqlite.materialize(service,path.join(root,'catalog-fixture-repository')),data=await sqlite.loadDataComponent(bundle),physical=deriveCommerceSqlitePhysicalLayoutV1(data),table=physical.tables.find((row:any)=>row.entity==='Catalog.Quote');
  assert.ok(table);db=new DatabaseSync(path.join(storageRoot,'store.sqlite'));
  const quote={id:'quote-one',customerId:'customer-one',currency:'USD',lines:[{sku:'sku-one',quantity:1n,unitPriceMinor:100n}],discountMinor:0n,taxMinor:0n,shippingMinor:0n,expiresAtEpochMs:4102444800000n,version:1n};
  const stored=physical.encode('Catalog.Quote',quote);db.prepare(table.insert_sql).run(...stored.bindings);
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  const placeId='Orders.PlaceOrderEntry',placeEntry=auth.bindEntry(placeId),placeDefinition=auth.inspectEntry(placeEntry),subject='customer-one',evidence='query-customer-evidence';
  const placeFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'query-customer-session',routes:[{entry:placeId,permission:placeDefinition.access.auth_permission}]}),placeActor=registerCommerceEntryFixtureActorV1(auth,placeFixture.handle,{subject,evidence,principal_kind:'customer',service_id:null,scope:placeDefinition.access.auth_permission.scope});
  const placeInput={quoteId:'quote-one',checkoutKey:'checkout-one'},placed=await selected.begin(placeActor,placeId,Buffer.from(JSON.stringify(placeInput)),placeInput);
  assert.equal(placed.ok,true);if(!placed.ok)return;
  const catalogId='Catalog.ReadQuoteEntry',catalogEntry=auth.bindEntry(catalogId),catalogDefinition=auth.inspectEntry(catalogEntry),serviceSubject='service-orders',serviceEvidence='query-service-evidence';
  const catalogFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:serviceSubject,evidence:serviceEvidence,session:'query-service-session',routes:[{entry:catalogId,permission:catalogDefinition.access.auth_permission}]}),catalogActor=registerCommerceEntryFixtureActorV1(auth,catalogFixture.handle,{subject:serviceSubject,evidence:serviceEvidence,principal_kind:'service',service_id:'orders',scope:catalogDefinition.access.auth_permission.scope});
  selected.registerServiceActor(catalogId,catalogActor);
  const readPath=selected.delegatedReadCallPath(placed.invocation,catalogId),catalog=await selected.beginDelegatedQuery(placed.invocation,readPath);
  assert.equal(catalog.ok,true);if(!catalog.ok)return;
  assert.throws(()=>query.select({...selected} as any,catalog.invocation),code('ForeignOwner'));
  const witness=query.select(selected,catalog.invocation);
  assert.throws(()=>query.releaseSelected({...witness},selected,catalog.invocation),code('ForeignOwner'));
  assert.throws(()=>query.releaseSelected(witness,selected,placed.invocation),code('ForeignOwner'));
  const result=query.releaseSelected(witness,selected,catalog.invocation);
  assert.equal(result.kind,'returned');if(result.kind==='returned')assert.deepEqual(structural(result.value),{kind:'some',value:quote});
  assert.throws(()=>query.releaseSelected(witness,selected,catalog.invocation),code('AlreadyConsumed'));
  selected.retire(catalog.invocation);
  process.stderr.write('orders-external-read phase=catalog-guard-passed\n');
  ordersStorage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'orders',path.join(root,'orders-store'));
  process.stderr.write('orders-external-read phase=orders-store-open\n');
  runner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,baseline,plans,selected,ordersStorage,placed.invocation,path.join(root,'orders-operation'),{externalQueries:[query]});
  process.stderr.write('orders-external-read phase=generated-runner-open\n');
  const placedResult=await runner.run(placed.invocation);
  t.diagnostic('generated Orders.PlaceOrder result '+JSON.stringify(placedResult,(_key,value)=>typeof value==='bigint'?String(value):value));
  assert.equal(placedResult.kind,'returned','generated Orders read and source control must reach a returned outcome');
  if(placedResult.kind!=='returned')return;
  const orderId=(placedResult.value as {orderId:string}).orderId;
  const ordersService=sqlite.bindService('orders'),ordersBundle=sqlite.materialize(ordersService,path.join(root,'orders-fixture-repository'));
  const ordersData=await sqlite.loadDataComponent(ordersBundle),ordersPhysical=deriveCommerceSqlitePhysicalLayoutV1(ordersData);
  const outboxTable=ordersPhysical.tables.find((row:any)=>row.entity==='Orders.OrderPlacedOutbox');assert.ok(outboxTable);
  ordersDb=new DatabaseSync(path.join(root,'orders-store/store.sqlite'));
  const outboxRows=ordersDb.prepare('SELECT * FROM "'+outboxTable.physical_name+'"').all();
  assert.equal(outboxRows.length,1,'generated PlaceOrder must commit one original OrderPlaced outbox row');
  const outbox=ordersPhysical.decode('Orders.OrderPlacedOutbox',outboxRows[0]) as {eventId:string;event:{orderId:string}};
  assert.equal(outbox.event.orderId,orderId);
  const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
  const ingress=await ordersStorage.enqueueCommittedWorkflowEvent(binding,outbox.eventId);
  assert.equal(ingress.kind,'enqueued','original producer outbox must create the Workflow Inbox and WorkSchedule');
  const repeated=await ordersStorage.enqueueCommittedWorkflowEvent(binding,outbox.eventId);
  assert.equal(repeated.kind,'recorded','replayed ingress must retain the same technical rows');
  const schedule=ordersStorage.claimVacantWorkSchedule(binding,outbox.eventId);
  assert.equal(schedule.kind,'claimed','original vacant WorkSchedule must yield one native committed claim');
  if(schedule.kind==='claimed'){
   worker=createCommerceWorkerContextOwnerV1(binding,ordersStorage);
   const context=worker.registerCommittedClaim(schedule.claim),inspection=worker.inspectContext(context);
   worker.assertOrder(context,orderId);assert.equal(inspection.order_id,orderId);
   assert.equal(context.isOrdersWorker(),true);
   assert.equal(context.provesVacantOrQuiescentPredecessor({kind:'none'},0n),true);
   assert.equal(context.owns({kind:'some',value:context.workerId},inspection.worker_epoch),false);
   assert.equal(context.provesNeverDispatched('inventory.reserve'),false);
   const journal=ordersStorage.prepareClaimJournal(binding,schedule.claim);
   assert.equal(journal.kind,'prepared','source claim driver must commit its original Prepared StepJournal');
   if(journal.kind==='prepared'){
    const recorded=ordersStorage.inspectClaimJournal(journal.journal);
    assert.equal(recorded.order_id,orderId);assert.equal(recorded.target_entry_id,'Orders.ClaimCheckoutWorkEntry');
    assert.equal(recorded.worker_id,context.workerId);assert.equal(recorded.phase,'Prepared');
    assert.throws(()=>ordersStorage!.inspectClaimJournal({...journal.journal}),code('ForeignOwner'));
    assert.equal(ordersStorage.prepareClaimJournal(binding,schedule.claim).kind,'recorded');
    const claimEntryId=recorded.target_entry_id,claimEntry=auth.bindEntry(claimEntryId),claimDefinition=auth.inspectEntry(claimEntry);
    const claimFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-claim-worker',evidence:'claim-worker-evidence',
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
      assert.equal(selected.inspectInvocation(started.invocation).actual_business_resource_owners_qualified,true);
      assert.deepEqual(selected.principalIdentity(started.invocation),{kind:'service',id:'orders',authority_effect:'none'});
      const nativePaths=new Map<string,string>();
      const visit=(value:unknown,at:string):void=>{
       if(!value||typeof value!=='object')return;
       if(!Array.isArray(value)&&(value as {op?:unknown}).op==='native_observation')
        nativePaths.set(String((value as {method?:unknown}).method),at);
       if(Array.isArray(value))value.forEach((item,index)=>visit(item,at+'['+index+']'));
       else for(const [key,item] of Object.entries(value))visit(item,at+'.'+key);
      };
      visit(plans.inspectOperation(plans.bindOperation('Orders.ClaimCheckoutWork')).plan,'$');
      const ownsPath=nativePaths.get('owns'),predecessorPath=nativePaths.get('provesVacantOrQuiescentPredecessor');
      assert.ok(ownsPath);assert.ok(predecessorPath);
      assert.equal(selected.workerObservation(started.invocation,ownsPath,[{kind:'none'},0n]),false);
      assert.equal(selected.workerObservation(started.invocation,predecessorPath,[{kind:'none'},0n]),true);
      assert.equal(selected.workerObservation(started.invocation,predecessorPath,[{kind:'some',value:'foreign'},0n]),false);
      assert.throws(()=>selected!.workerObservation({...started.invocation},predecessorPath,[{kind:'none'},0n]),code('ForeignOwner'));
      const wrongInput={...claimInput,orderId:'different-order'},wrongWire=Buffer.from(JSON.stringify(wrongInput,(_key,value)=>typeof value==='bigint'?String(value):value));
      await assert.rejects(()=>selected!.beginWorker(claimActor,claimEntryId,wrongWire,wrongInput,ordersStorage!,binding,journal.journal,worker!,context),code('ForeignAuthorizedInput'));
      assert.deepEqual(selected.workerCommandIdentity(started.invocation,plans.inspectOperation(plans.bindOperation('Orders.ClaimCheckoutWork')).transactions[0]!.path),
       {journal_entry:claimEntryId,command_id:recorded.command_id,request_fingerprint:recorded.request_fingerprint});
      let progressClaim:CommerceWorkerProgressClaimV1|undefined;
      const claimRunner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,baseline,plans,selected,ordersStorage,
       started.invocation,path.join(root,'claim-operation'));
      try{
       const claimed=await claimRunner.run(started.invocation);
       t.diagnostic('generated Orders.ClaimCheckoutWork result '+JSON.stringify(claimed,(_key,value)=>typeof value==='bigint'?String(value):value));
       assert.equal(claimed.kind,'returned','generated ClaimCheckoutWork must commit the source-owned progress claim');
       const currentProgress=ordersStorage.inspectStoredRecord(binding.inspect().workflow.durable_state,0,{orderId}) as
        {workerOwner:{kind:string;value?:string};workerEpoch:bigint;version:bigint}|null;
       assert.ok(currentProgress);
       assert.deepEqual(structural(currentProgress.workerOwner),{kind:'some',value:context.workerId});
       assert.equal(currentProgress.workerEpoch,inspection.worker_epoch);
       assert.equal(currentProgress.version,claimInput.expectedProgressVersion+1n);
       const receipts=claimed.commits as readonly object[];assert.equal(receipts.length,1);
       progressClaim=worker.registerCommittedProgressClaim(context,claimRunner,selected,started.invocation,receipts[0]!);
       assert.equal(ordersStorage.inspectWorkerProgressClaim(progressClaim).progress_version,currentProgress.version);
       assert.equal(worker.inspectContext(context).progress_claim_qualified,true);
       assert.equal(context.owns({kind:'some',value:context.workerId},inspection.worker_epoch),true);
       assert.equal(context.owns({kind:'some',value:'other-worker'},inspection.worker_epoch),false);
       assert.equal(context.owns({kind:'some',value:context.workerId},inspection.worker_epoch+1n),false);
       assert.throws(()=>worker!.registerCommittedProgressClaim(context,claimRunner,selected!,started.invocation,receipts[0]!),code('DuplicateSymbol'));
      }finally{claimRunner.dispose();}
      assert.ok(progressClaim);
      process.stderr.write('orders-external-read phase=claim-progress-committed\n');
      const snapshotEntryId='Orders.ReadCheckoutSnapshotEntry',snapshotEntry=auth.bindEntry(snapshotEntryId),
       snapshotDefinition=auth.inspectEntry(snapshotEntry);
      const snapshotFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-snapshot-worker',evidence:'snapshot-worker-evidence',
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
         const snapshot=snapshotQuery.executeWorker(selected,snapshotStart.invocation);
         assert.equal(snapshot.kind,'returned','source-declared worker snapshot Query must return the current order and progress');
         if(snapshot.kind==='returned'){
          const value=snapshot.value as {order:{id:string};progress:{orderId:string;workerOwner:{kind:string;value?:string};workerEpoch:bigint}};
          assert.equal(value.order.id,orderId);assert.equal(value.progress.orderId,orderId);
          assert.deepEqual(structural(value.progress.workerOwner),{kind:'some',value:context.workerId});
          assert.equal(value.progress.workerEpoch,inspection.worker_epoch);
         }
         const snapshots=createCommerceWorkflowSnapshotOwnerV1(binding,ordersStorage,worker,context,
          snapshotQuery,selected,snapshotStart.invocation);
         try{
          const witnessed=snapshots.read();
          assert.equal(witnessed.kind,'snapshot','source Worker Query must mint an original snapshot witness');
          if(witnessed.kind==='snapshot'){
           const original=snapshots.inspect(witnessed.handle);
           process.stderr.write('orders-external-read phase=workflow-snapshot-witnessed\n');
           assert.equal(original.order_id,orderId);
           assert.equal(original.progress_version,ordersStorage.inspectWorkerProgressClaim(progressClaim).progress_version);
           assert.deepEqual(snapshots.recheck(witnessed.handle),original);
           assert.throws(()=>snapshots.inspect({...witnessed.handle}),code('ForeignOwner'));
           const resumes=createCommerceWorkflowResumeSelectorV1(binding,worker);
           try{
            const selectedCase=resumes.select(original.value,context),decision=resumes.inspectSelection(selectedCase);
            assert.equal(decision.outcome,'selected');
            assert.deepEqual(decision.action,{kind:'step',target:'reserve'});
            assert.equal(decision.progress_version,original.progress_version);
            assert.equal(decision.authority_effect,'none');
            assert.throws(()=>resumes.inspectSelection({...selectedCase}),code('ForeignOwner'));
            const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
            const argumentDirectory=path.join(root,'workflow-step-arguments');mkdirSync(argumentDirectory);
            const stepArguments=await createCommerceWorkflowStepArgumentsOwnerV1(binding,semantics,semantic,calls,
             stage,source,domain,baseline,argumentDirectory);
            try{
             const evaluated=stepArguments.evaluate(resumes,selectedCase,snapshots,witnessed.handle);
             const step=stepArguments.inspect(evaluated);
             assert.equal(step.step,'reserve');
             assert.equal(step.entry,'Inventory.ReserveStockEntry');
             assert.equal(step.order_id,orderId);
             assert.equal(step.progress_version,original.progress_version);
             assert.equal(step.authority_effect,'none');
             assert.throws(()=>stepArguments.inspect({...evaluated}),code('ForeignOwner'));
            }finally{stepArguments.dispose();}
            const identityDirectory=path.join(root,'workflow-step-identity');mkdirSync(identityDirectory);
            const identities=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,calls,
             stage,source,domain,baseline,identityDirectory);
            try{
             const identity=identities.derive(resumes,selectedCase,snapshots,witnessed.handle),view=identities.inspect(identity);
             assert.equal(view.step_name,'reserve');
             assert.equal(view.target_entry_id,'Inventory.ReserveStockEntry');
             assert.equal(view.order_id,orderId);
             assert.equal(view.store_id,ordersStorage.inspect().store_id);
             assert.equal(view.worker_id,context.workerId);
             assert.equal(view.worker_epoch,inspection.worker_epoch);
             assert.equal(view.progress_version,original.progress_version);
             assert.equal(view.command_id,(original.value as {progress:{reserveCommandId:string}}).progress.reserveCommandId);
             assert.match(view.request_fingerprint,/^[a-f0-9]{64}$/);
             assert.deepEqual(identities.recheck(identity),view);
             assert.throws(()=>identities.inspect({...identity}),code('ForeignOwner'));
             assert.ok(progressClaim);
             const projected=createCommerceWorkflowPreparedJournalProjectionV1(binding,ordersStorage,
              schedule.claim,progressClaim,identities,identity),prepared=projected.inspect();
             assert.equal(prepared.step_name,'reserve');
             assert.equal(prepared.command_id,view.command_id);
             assert.equal(prepared.request_fingerprint,view.request_fingerprint);
             assert.equal(prepared.progress_version,original.progress_version);
             assert.equal(prepared.authority_effect,'none');
             assert.deepEqual(projected.inspectRecordedRow(prepared.prepared).phase,'Prepared');
             const committedStep=ordersStorage.prepareWorkflowStepJournal(binding,schedule.claim,progressClaim,identities,identity);
             assert.equal(committedStep.kind,'prepared','source selected reserve step must commit its original Prepared journal');
             process.stderr.write('orders-external-read phase=workflow-journal-prepared\n');
             if(committedStep.kind==='prepared'){
              const journalView=ordersStorage.inspectWorkflowStepJournal(committedStep.journal);
              assert.equal(journalView.command_id,view.command_id);
              assert.equal(journalView.request_fingerprint,view.request_fingerprint);
              assert.equal(journalView.phase,'Prepared');
              assert.equal(ordersStorage.prepareWorkflowStepJournal(binding,schedule.claim,progressClaim,identities,identity).kind,'recorded');
              assert.throws(()=>ordersStorage.inspectWorkflowStepJournal({...committedStep.journal}),code('ForeignOwner'));
             }
             const causalDirectory=path.join(root,'workflow-causal-projection');mkdirSync(causalDirectory);
             const causal=await createCommerceWorkflowCausalProjectionOwnerV1(binding,semantics,semantic,calls,
              stage,source,domain,baseline,causalDirectory);
             try{
              const projectedCall=causal.derive(identities,identity,resumes,selectedCase,snapshots,witnessed.handle),
               call=causal.inspect(projectedCall);
              assert.equal(call.entry_id,'Inventory.ReserveStockEntry');
              assert.equal(call.order_id,orderId);
              assert.equal(call.projection.reserveCommandId,view.command_id);
              assert.equal(call.projection.orderId,orderId);
              assert.equal(call.authority_effect,'none');
              assert.deepEqual(causal.recheck(projectedCall),call);
              assert.throws(()=>causal.inspect({...projectedCall}),code('ForeignOwner'));
              process.stderr.write('orders-external-read phase=workflow-causal-projected\n');
             if(committedStep.kind==='prepared'){
              const dispatched=ordersStorage.markWorkflowStepDispatched(binding,committedStep.journal,identities,identity);
              assert.equal(dispatched.kind,'dispatched','original StepJournal must be durably Dispatched before remote call');
              if(dispatched.kind==='dispatched'){
               const dispatchView=ordersStorage.inspectDispatchedWorkflowStepJournal(dispatched.journal);
               assert.equal(dispatchView.phase,'Dispatched');
               assert.equal(dispatchView.command_id,view.command_id);
               assert.equal(dispatchView.request_fingerprint,view.request_fingerprint);
               assert.equal(dispatchView.worker_id,context.workerId);
               assert.equal(dispatchView.authority_effect,'none');
               process.stderr.write('orders-external-read phase=workflow-journal-dispatched\n');
               assert.throws(()=>ordersStorage.inspectDispatchedWorkflowStepJournal({...dispatched.journal}),code('ForeignOwner'));
               assert.throws(()=>ordersStorage.assertWorkflowStepJournalCurrent(committedStep.journal),code('StaleOwner'));
               const recorded=ordersStorage.prepareWorkflowStepJournal(binding,schedule.claim,progressClaim,identities,identity);
               assert.deepEqual(recorded,{kind:'recorded',phase:'Dispatched'});
               const protectedCall=createCommerceWorkflowProtectedCallBindingV1(binding,ordersStorage,
                dispatched.journal,causal,projectedCall),protectedView=protectedCall.inspect();
               assert.equal(protectedView.entry_id,'Inventory.ReserveStockEntry');
               assert.equal(protectedView.caller_service,'orders');
               assert.equal(protectedView.command_id,view.command_id);
               assert.deepEqual(protectedCall.recheck(),protectedView);
               const inventoryRoot=path.join(root,'inventory-store'),inventoryStorage=await createCommerceServiceStorageOwnerV1(
                sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'inventory',inventoryRoot);
               let inventoryDb:DatabaseSync|undefined,inventoryRunner:Awaited<ReturnType<typeof createCommerceGeneratedOperationRuntimeV1>>|undefined;
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
                  session:'reserve-workflow-session',routes:[{entry:protectedView.entry_id,permission:reserveDefinition.access.auth_permission}]}),
                  reserveActor=registerCommerceEntryFixtureActorV1(auth,reserveFixture.handle,{subject:reserveSubject,evidence:reserveEvidence,
                   principal_kind:'service',service_id:'orders',scope:reserveDefinition.access.auth_permission.scope});
                 try{
                  const reserveInput=protectedView.arguments,reserveWire=Buffer.from(JSON.stringify(reserveInput,
                   (_key,value)=>typeof value==='bigint'?String(value):value));
                  const started=await selected.beginWorkflowServiceStep(reserveActor,protectedView.entry_id,
                   reserveWire,reserveInput,protectedCall);
                  assert.equal(started.ok,true,'fresh Auth and original Dispatched journal must admit reserve');
                  if(started.ok){
                   inventoryRunner=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,baseline,
                    plans,selected,inventoryStorage,started.invocation,path.join(root,'inventory-reserve-operation'),
                    {workflowProtectedCall:protectedCall});
                   const reserved=await inventoryRunner.run(started.invocation);
                   assert.equal(reserved.kind,'returned','generated ReserveStock must run from the protected Workflow call');
                   if(reserved.kind==='returned')assert.equal((reserved.value as {kind:string}).kind,'Applied');
                   process.stderr.write('orders-external-read phase=inventory-reserve-applied\n');
                   await assert.rejects(()=>inventoryRunner!.run(started.invocation),code('AlreadyDispatched'));
                   selected.retire(started.invocation);
                  }
                 }finally{auth.disposeActor(reserveActor);}
                }finally{auth.disposeEntry(reserveEntry);}
               }finally{inventoryRunner?.dispose();inventoryDb?.close();inventoryStorage.close();}
              }
             }
             }finally{causal.dispose();}
            }finally{identities.dispose();}
           }finally{resumes.dispose();}
          }
         }finally{snapshots.dispose();}
         assert.throws(()=>snapshotQuery.executeWorker(selected,{...snapshotStart.invocation}),code('ForeignOwner'));
        }finally{snapshotQuery.dispose();snapshotCodec.dispose();plans.disposeRead(read);selected.retire(snapshotStart.invocation);}
       }
      }finally{auth.disposeActor(snapshotActor);auth.disposeEntry(snapshotEntry);}
      selected.retire(started.invocation);
      assert.equal(context.owns({kind:'some',value:context.workerId},inspection.worker_epoch),true);
     }
    }finally{auth.disposeActor(claimActor);auth.disposeEntry(claimEntry);}
   }
  }
  selected.retire(placed.invocation);auth.disposeActor(catalogActor);auth.disposeEntry(catalogEntry);auth.disposeActor(placeActor);auth.disposeEntry(placeEntry);
  query.dispose();codec.dispose();sqlite.dispose();
 }finally{worker?.dispose();runner?.dispose();ordersDb?.close();db?.close();selected?.dispose();auth?.dispose();await native?.dispose();ordersStorage?.close();storage?.close();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
