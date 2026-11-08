/** Focused receiver execution from a typed persisted OrderConfirmed fixture.
 * The separate full Workflow replay must still prove producer commit provenance.
 * Set CRAFT_C14_EVENT_RECEIVER_RUN=1 after the selected Event Auth and generated
 * acknowledgement seams are integrated. No local hosting is involved.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCommerceApplicationAssemblyV1} from '../../src/commerce/commerce-application-assembly-v1.ts';
// Default remains the original fresh source producer; installed replay may
// explicitly select the genuine packaged component through the shared helper.
import {createCommerceTestAuthNativeV1 as produceCommerceAuthNativeOwnerV1} from '../support/commerce-auth-native-variant-v1.ts';
import {registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';
import {createCoreCommerceEventDelivery} from '../../src/generic/core-commerce-event-delivery.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 selected Event Entry commits receiver inbox/result once and replays the same occurrence',
 {skip:process.env.CRAFT_C14_EVENT_RECEIVER_RUN!=='1'},async()=>{
  const work=mkdtempSync(path.join('/var/tmp','craft-c14-event-receiver-'));
  let assembly,native,delivery,auth,firstActor,replayActor,wrongActor;
  try{
   assembly=await createCommerceApplicationAssemblyV1(source,path.join(work,'generated'));
   const producer=await assembly.openServiceStorage('orders');
   const receiver=await assembly.openServiceStorage('fulfillment');
   const eventId='evt_'+('d'.repeat(64)),orderId='receiver-order-one';
   const event={metadata:{eventId,producer:'orders',aggregateId:orderId,aggregateVersion:2n,
    ordinal:0n,correlationId:orderId,commandId:'cmd_confirm_receiver_one'},
    orderId,customerId:'receiver-customer-one',lines:[{sku:'sku-one',quantity:1n}],
    payableMinor:100n,currency:'USD',reservationId:'reserve-one',reservationVersion:1n,
    paymentAttemptKey:'payment-one',providerReference:'provider-one'};
   const component=await import(pathToFileURL(path.join(work,'generated','orders','repository','service-repositories.js')).href);
   const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData),
    table=physical.tables.find(row=>row.entity==='Orders.OrderConfirmedOutbox');
   assert.ok(table,'generated Orders schema must contain the original outbox');
   const db=new DatabaseSync(path.join(work,'generated','orders','store.sqlite'));
   try{db.prepare(table.insert_sql).run(...physical.encode(table.entity,
    {eventId,event,state:'Ready',version:1n}).bindings);}finally{db.close();}
   const {relay,admission,acknowledgement,receiverCommit}=assembly.openCrossServiceEvent('Fulfillment.OnOrderConfirmed');
   const ready=relay.readReady(eventId);assert.equal(ready.kind,'ready');
   native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
   const selected=await assembly.openSelectedEntryAuth(native);auth=selected.auth;
   delivery=createCoreCommerceEventDelivery({assembly,auth,selected:selected.entries,
    producer,receiver,relay,admission,acknowledgement,receiverCommit});
   const requirement=delivery.inspectActorRequirement();
   assert.equal(requirement.entry,'Fulfillment.OnOrderConfirmed');
   assert.equal(requirement.caller_service,'orders');
   assert.equal(requirement.target_service,'fulfillment');
   assert.equal(requirement.permission,'fulfillment.create');
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentInbox'),0n);
   assert.equal(receiver.countStoredRecords('Fulfillment.Shipment'),0n);
   assert.deepEqual(await delivery.deliver(ready.occurrence,null),
    {kind:'denied',status:401,authority_effect:'none'});
   await assert.rejects(delivery.deliver({...ready.occurrence},null),
    /original cross-service outbox occurrence required/);
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentInbox'),0n);
   const first=seedCommerceAuthFixtureDatabaseV1(native,{subject:'receiver-orders-service',
    evidence:'receiver-orders-evidence',session:'receiver-orders-session',
    routes:[{entry:requirement.entry,permission:requirement.auth_permission}]});
   wrongActor=registerCommerceEntryFixtureActorV1(auth,first.handle,{subject:'receiver-orders-service',
    evidence:'receiver-orders-evidence',principal_kind:'service',service_id:'payments',
    scope:requirement.auth_permission.scope});
   assert.deepEqual(await delivery.deliver(ready.occurrence,wrongActor),
    {kind:'denied',status:403,authority_effect:'none'});
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentInbox'),0n);
   firstActor=registerCommerceEntryFixtureActorV1(auth,first.handle,{subject:'receiver-orders-service',
    evidence:'receiver-orders-evidence',principal_kind:'service',service_id:'orders',
    scope:requirement.auth_permission.scope});
   console.error('C14 Event receiver: native orders actor ready; starting generated CreateShipment');
   const committed=await delivery.deliver(ready.occurrence,firstActor);
   console.error('C14 Event receiver: generated CreateShipment returned',committed.kind);
   assert.equal(committed.kind,'receiver-committed');
   assert.equal(committed.occurrence_id,eventId);
   assert.equal(committed.qualification,
    'original-consumer-inbox-and-result-commit;producer-publication-pending');
   const inbox=receiver.inspectStoredRecord('Fulfillment.ShipmentInbox',0,
    {consumerEntryId:requirement.entry,occurrenceId:eventId});
   assert.ok(inbox);
   assert.equal(inbox.orderId,orderId);
   assert.deepEqual(inbox.receipt,committed.receipt);
   assert.equal(committed.receipt.orderId,orderId);
   assert.equal(committed.receipt.sourceOccurrenceId,eventId);
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentInbox'),1n);
   assert.equal(receiver.countStoredRecords('Fulfillment.Shipment'),1n);
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentRequestedOutbox'),1n);
   const replay=seedCommerceAuthFixtureDatabaseV1(native,{subject:'receiver-orders-replay',
    evidence:'receiver-orders-replay-evidence',session:'receiver-orders-replay-session',
    routes:[{entry:requirement.entry,permission:requirement.auth_permission}]});
   replayActor=registerCommerceEntryFixtureActorV1(auth,replay.handle,{subject:'receiver-orders-replay',
    evidence:'receiver-orders-replay-evidence',principal_kind:'service',service_id:'orders',
    scope:requirement.auth_permission.scope});
   const repeated=await delivery.deliver(ready.occurrence,replayActor);
   assert.equal(repeated.kind,'receiver-committed');
   assert.deepEqual(repeated.receipt,committed.receipt);
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentInbox'),1n);
   assert.equal(receiver.countStoredRecords('Fulfillment.Shipment'),1n);
   assert.equal(receiver.countStoredRecords('Fulfillment.ShipmentRequestedOutbox'),1n);
  }finally{
   delivery?.close();
   if(replayActor)try{auth.disposeActor(replayActor);}catch{}
   if(firstActor)try{auth.disposeActor(firstActor);}catch{}
   if(wrongActor)try{auth.disposeActor(wrongActor);}catch{}
   assembly?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
  }
 });
