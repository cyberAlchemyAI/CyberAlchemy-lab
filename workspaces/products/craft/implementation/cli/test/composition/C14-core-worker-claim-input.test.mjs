import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner} from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {createCommerceTestAuthNativeV1} from '../support/commerce-auth-native-variant-v1.ts';
import {registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';
import {assertCoreCommercePreparedWorkerStep} from '../../src/generic/core-commerce-worker-continuation.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
// The native Auth fixture must outlive the complete generated replay on a
// shared test host. Expiry behavior is tested separately.
const authFixtureLifetimeSeconds=43200;

test('C14 committed Commerce WorkSchedule yields generated claim and source-selected observed reserve step',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-claim-input-'));
 let owner,native,selected,entry,input,actor,snapshotActor,stepActor,executor,snapshot,continuation,runner,preparedStep,session,snapshotWitness;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  console.error('C14 claim input: actual five-service assembly ready');
  const ordersRoot=path.join(work,'generated','runtime','orders');
  const component=await import(pathToFileURL(path.join(ordersRoot,'repository','service-repositories.js')).href);
  const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
  const orderId='claim-input-order-one',occurrenceId='evt_'+('c'.repeat(64));
  const order={id:orderId,customerId:'customer-one',quoteId:'quote-one',currency:'USD',payableMinor:100n,
   lines:[{sku:'sku-one',quantity:1n}],status:'AwaitingStock',version:1n};
  const progress={orderId,state:'AwaitingStock',reserveCommandId:'cmd_claim_reserve_one',
   captureAttemptKey:'cmd_claim_capture_one',allocateCommandId:'cmd_claim_allocate_one',
   releaseCommandId:'cmd_claim_release_one',confirmCommandId:'cmd_claim_confirm_one',
   cancelCommandId:'cmd_claim_cancel_one',reserveResult:{kind:'none'},reserveRejected:{kind:'none'},
   paymentResult:{kind:'none'},allocationResult:{kind:'none'},releaseResult:{kind:'none'},
   captureDispatched:false,workerOwner:{kind:'none'},workerEpoch:0n,version:1n};
  const metadata={eventId:occurrenceId,producer:'orders',aggregateId:orderId,aggregateVersion:1n,
   ordinal:0n,correlationId:orderId,commandId:'cmd_claim_place_one'};
  const outbox={eventId:occurrenceId,event:{metadata,orderId},state:'Ready',version:1n};
  const db=new DatabaseSync(path.join(ordersRoot,'store.sqlite'));
  try{
   for(const [entity,value] of [['Orders.Order',order],['Orders.OrderPlacedOutbox',outbox]]){
    const table=physical.tables.find(row=>row.entity===entity);
    assert.ok(table,'generated source schema must contain '+entity);
    db.prepare(table.insert_sql).run(...physical.encode(entity,value).bindings);
   }
  }finally{db.close();}
  console.error('C14 claim input: original generated-schema fixture seeded');
  const ingress=owner.openWorkflowIngress('Orders.Checkout.Checkout');
  assert.throws(()=>ingress.reclaimQuiescent(occurrenceId),/whole-process reopen required/);
  assert.equal((await ingress.enqueue(occurrenceId)).kind,'enqueued');
  const scheduled=ingress.claim(occurrenceId);
  assert.equal(scheduled.kind,'claimed');
  console.error('C14 claim input: original inbox and WorkSchedule committed');
  assert.deepEqual(ingress.inspectClaimInput(scheduled.claim),
   {kind:'not-ready',reason:'durable-progress-missing',authority_effect:'none'});
  const progressTable=physical.tables.find(row=>row.entity==='Orders.CheckoutProgress');
  assert.ok(progressTable);
  const progressDb=new DatabaseSync(path.join(ordersRoot,'store.sqlite'));
  try{progressDb.prepare(progressTable.insert_sql).run(...physical.encode('Orders.CheckoutProgress',progress).bindings);}
  finally{progressDb.close();}
  const result=ingress.inspectClaimInput(scheduled.claim);
  assert.equal(result.kind,'ready');
  assert.equal(result.entry,'Orders.ClaimCheckoutWorkEntry');
  assert.equal(result.operation,'Orders.ClaimCheckoutWork');
  assert.equal(result.service,'orders');
  assert.deepEqual({...result.parameters},{orderId,expectedProgressVersion:1n});
  assert.equal(result.source_capture_sha256,owner.inspect().source_capture_sha256);
  assert.match(result.qualification,/generated-CAS-required/);
  assert.throws(()=>ingress.inspectClaimInput({...scheduled.claim}),/ForeignOwner|original committed/i);
  console.error('C14 claim input: source-selected closed argument record ready');
  native=await createCommerceTestAuthNativeV1(path.join(work,'native-auth'));
  selected=await owner.openSelectedEntryAuth(native);
  entry=selected.auth.bindEntry(result.entry);
  assert.equal(selected.auth.inspectEntry(entry).invokes.module+'.'+selected.auth.inspectEntry(entry).invokes.name,result.operation);
  const wire=selected.auth.encodeEntryArguments(entry,result.parameters);
  input=selected.auth.prepareInput(entry,wire);
  assert.equal(selected.auth.matchesPreparedInput(input,result.parameters),true);
  assert.equal(selected.auth.matchesPreparedInput(input,{...result.parameters,expectedProgressVersion:2n}),false);
  assert.throws(()=>selected.auth.encodeEntryArguments(entry,{...result.parameters,forged:true}),/InputRejected/);
  const permission=selected.auth.inspectEntry(entry).access.auth_permission;
  const snapshotRequirement=owner.inspectWorkerActorRequirements('Orders.Checkout.Checkout')
   .find(row=>row.usage==='snapshot');
  assert.ok(snapshotRequirement,'checked Workflow must select its worker snapshot Entry');
  assert.equal(snapshotRequirement.auth_permission.scope,permission.scope);
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'claim-worker-orders',
   evidence:'claim-worker-orders-evidence',session:'claim-worker-orders-session',
   valid_for_seconds:authFixtureLifetimeSeconds,
   routes:[{entry:result.entry,permission}]});
  actor=registerCommerceEntryFixtureActorV1(selected.auth,fixture.handle,{subject:'claim-worker-orders',
   evidence:'claim-worker-orders-evidence',principal_kind:'service',service_id:'orders',scope:permission.scope});
  executor=owner.openWorkflowClaimExecutor('Orders.Checkout.Checkout');
  assert.ok(executor.bindActor(actor).includes(result.entry));
  snapshot=owner.openWorkflowSnapshotQuery('Orders.Checkout.Checkout');
  assert.equal(snapshot.inspect().entry,snapshotRequirement.entry);
  console.error('C14 claim input: fresh native service actor selected; starting generated claim CAS');
  const executed=await executor.run(scheduled.claim);
  assert.equal(executed.kind,'claimed-progress');
  session=executed.session;
  assert.equal(session.inspect().progress_claim_qualified,true);
  const committed=owner.serviceStorage('orders').inspectStoredRecord('Orders.CheckoutProgress',0,{orderId});
  assert.ok(committed);
  assert.equal(committed.version,2n);
  assert.equal(committed.workerEpoch,1n);
  assert.equal(committed.workerOwner.kind,'some');
  assert.equal(committed.workerOwner.value,session.context.workerId);
  const snapshotFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'snapshot-worker-orders',
   evidence:'snapshot-worker-orders-evidence',session:'snapshot-worker-orders-session',
   valid_for_seconds:authFixtureLifetimeSeconds,
   routes:[{entry:snapshotRequirement.entry,permission:snapshotRequirement.auth_permission}]});
  snapshotActor=registerCommerceEntryFixtureActorV1(selected.auth,snapshotFixture.handle,{subject:'snapshot-worker-orders',
   evidence:'snapshot-worker-orders-evidence',principal_kind:'service',service_id:'orders',
   scope:snapshotRequirement.auth_permission.scope});
  assert.ok(snapshot.bindActor(snapshotActor).includes(snapshotRequirement.entry));
  await assert.rejects(snapshot.run({...session}),/original generated Workflow progress-claim session required/);
  snapshotWitness=await snapshot.run(session);
  assert.equal(snapshotWitness.kind,'snapshot');
  assert.equal(snapshotWitness.handle.kind,'original-worker-snapshot/v1-candidate');
  assert.equal(snapshotWitness.inspection.order_id,orderId);
  assert.equal(snapshotWitness.inspection.value.order.id,orderId);
  assert.equal(snapshotWitness.inspection.value.progress.orderId,orderId);
  assert.equal(snapshotWitness.inspection.value.progress.workerOwner.value,session.context.workerId);
  assert.deepEqual(snapshotWitness.snapshots.recheck(snapshotWitness.handle),snapshotWitness.inspection);
  console.error('C14 claim input: original worker snapshot witness retained and rechecked');
  continuation=owner.openWorkflowContinuation('Orders.Checkout.Checkout');
  const next=await continuation.prepareNext(session,snapshotWitness);
  assert.equal(next.kind,'prepared-step','source resume must prepare its original first step');
  preparedStep=next;
  assert.equal(preparedStep.decision.persisted_state,'AwaitingStock');
  assert.deepEqual(preparedStep.decision.action,{kind:'step',target:'reserve'});
  assert.equal(preparedStep.identity_inspection.target_entry_id,'Inventory.ReserveStockEntry');
  assert.equal(preparedStep.identity_inspection.progress_version,2n);
  const stepJournal=owner.serviceStorage('orders').inspectWorkflowStepJournal(preparedStep.journal);
  assert.equal(stepJournal.phase,'Prepared');
  assert.equal(stepJournal.step_name,'reserve');
  assert.equal(stepJournal.command_id,preparedStep.identity_inspection.command_id);
  assert.equal(stepJournal.request_fingerprint,preparedStep.identity_inspection.request_fingerprint);
  assertCoreCommercePreparedWorkerStep(preparedStep);
  assert.throws(()=>assertCoreCommercePreparedWorkerStep({...preparedStep}),/original prepared Workflow step required/);
  console.error('C14 claim input: source-selected reserve journal Prepared without dispatch');
  const inventoryRoot=path.join(work,'generated','runtime','inventory');
  const inventoryComponent=await import(pathToFileURL(path.join(inventoryRoot,'repository','service-repositories.js')).href);
  const inventoryPhysical=deriveCommerceSqlitePhysicalLayoutV1(inventoryComponent.commerceRepositoryData);
  const stockTable=inventoryPhysical.tables.find(row=>row.entity==='Inventory.Stock');
  assert.ok(stockTable,'generated source schema must contain Inventory.Stock');
  const inventoryDb=new DatabaseSync(path.join(inventoryRoot,'store.sqlite'));
  try{inventoryDb.prepare(stockTable.insert_sql).run(...inventoryPhysical.encode('Inventory.Stock',
   {sku:'sku-one',onHand:20n,reserved:0n,allocated:0n,version:1n}).bindings);}
  finally{inventoryDb.close();}
  const workerRequirements=owner.inspectWorkerActorRequirements('Orders.Checkout.Checkout');
  const remoteRequirement=workerRequirements.find(row=>row.usage==='remote'&&row.step==='reserve');
  const observationRequirement=workerRequirements.find(row=>row.usage==='observation');
  assert.ok(remoteRequirement);assert.ok(observationRequirement);
  assert.equal(remoteRequirement.entry,preparedStep.identity_inspection.target_entry_id);
  assert.equal(remoteRequirement.caller_service,observationRequirement.caller_service);
  assert.equal(remoteRequirement.auth_permission.scope,observationRequirement.auth_permission.scope);
  const stepFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'reserve-worker-orders',
   evidence:'reserve-worker-orders-evidence',session:'reserve-worker-orders-session',
   valid_for_seconds:authFixtureLifetimeSeconds,
   routes:[{entry:remoteRequirement.entry,permission:remoteRequirement.auth_permission},
    {entry:observationRequirement.entry,permission:observationRequirement.auth_permission}]});
  stepActor=registerCommerceEntryFixtureActorV1(selected.auth,stepFixture.handle,{
   subject:'reserve-worker-orders',evidence:'reserve-worker-orders-evidence',
   principal_kind:'service',service_id:remoteRequirement.caller_service,
   scope:remoteRequirement.auth_permission.scope});
  runner=owner.openWorkflowStepRunner('Orders.Checkout.Checkout');
  const boundStepEntries=runner.bindActor(stepActor);
  assert.ok(boundStepEntries.includes(remoteRequirement.entry));
  assert.ok(boundStepEntries.includes(observationRequirement.entry));
  console.error('C14 claim input: source-selected reserve dispatch and generated observation starting');
  const observed=await runner.run(session,snapshotWitness,preparedStep);
  assert.equal(observed.kind,'observed',
   `original reserve result must commit generated observation: ${JSON.stringify(observed)}`);
  assert.equal(observed.step,'reserve');
  assert.equal(observed.remote_entry,remoteRequirement.entry);
  assert.equal(observed.observation_entry,observationRequirement.entry);
  assert.equal(observed.commits,1);
  const committedOrder=owner.serviceStorage('orders').inspectStoredRecord('Orders.Order',0,{id:orderId});
  const committedProgress=owner.serviceStorage('orders').inspectStoredRecord('Orders.CheckoutProgress',0,{orderId});
  assert.ok(committedOrder);assert.ok(committedProgress);
  assert.equal(committedOrder.version,2n);
  assert.equal(committedProgress.version,3n);
  assert.equal(committedProgress.reserveResult.kind,'some');
  assert.equal(committedOrder.status,committedProgress.state);
  const durableJournal=owner.serviceStorage('orders').inspectStoredRecord(ingress.inspect().journal_entity,0,{
   consumerEntryId:stepJournal.consumer_entry_id,occurrenceId:stepJournal.occurrence_id,
   stepName:'reserve',commandId:stepJournal.command_id});
  assert.ok(durableJournal,'the original source StepJournal must remain durable');
  assert.equal(durableJournal.phase,'Observed');
  assert.equal(durableJournal.version,3n);
  assert.equal(durableJournal.observation.kind,'some');
  assert.equal(durableJournal.observation.value.kind,'ReserveApplied');
  assert.deepEqual(durableJournal.observation.value.reservation,committedProgress.reserveResult.value);
  assert.equal(durableJournal.workerOwner,session.context.workerId);
  assert.equal(durableJournal.commandId,stepJournal.command_id);
  assert.equal(durableJournal.requestFingerprint,stepJournal.request_fingerprint);
  console.error('C14 claim input: generated reserve and observation committed; original journal retained');
  assert.deepEqual(await executor.run(scheduled.claim),
   {kind:'not-ready',reason:'prior-owner-changed',authority_effect:'none'});
  assert.equal(owner.inspect().complete_application,true);
  console.error('C14 claim input: checked Entry, fresh Auth, and original generated CAS committed');
 }finally{
  preparedStep?.dispose();runner?.close();continuation?.close();snapshotWitness?.dispose?.();session?.dispose();snapshot?.close();executor?.close();
  if(stepActor)try{selected.auth.disposeActor(stepActor);}catch{}
  if(snapshotActor)try{selected.auth.disposeActor(snapshotActor);}catch{}
  if(actor)try{selected.auth.disposeActor(actor);}catch{}
  if(input)try{selected.auth.disposeInput(input);}catch{}
  if(entry)try{selected.auth.disposeEntry(entry);}catch{}
  owner?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
