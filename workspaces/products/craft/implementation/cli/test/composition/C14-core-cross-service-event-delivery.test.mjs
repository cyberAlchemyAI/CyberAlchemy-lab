import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCommerceApplicationAssemblyV1} from '../../src/commerce/commerce-application-assembly-v1.ts';
import {produceCommerceAuthNativeOwnerV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';
import {createCoreCommerceEventDelivery} from '../../src/generic/core-commerce-event-delivery.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 authored Commerce Event route and publication proposal reject stale outbox state before native ingress',async()=>{
 const work=mkdtempSync(path.join('/var/tmp','craft-c14-cross-event-'));
 let assembly,native,relay,admission,publication,acknowledgement;
 try{
  assembly=await createCommerceApplicationAssemblyV1(source,path.join(work,'generated'));
  const producer=await assembly.openServiceStorage('orders');
  const receiver=await assembly.openServiceStorage('fulfillment');
  const eventId='evt_'+('e'.repeat(64)),orderId='cross-event-order-one';
  const event={metadata:{eventId,producer:'orders',aggregateId:orderId,aggregateVersion:2n,
   ordinal:0n,correlationId:orderId,commandId:'cmd_confirm_cross_event_one'},
   orderId,customerId:'customer-one',lines:[{sku:'sku-one',quantity:1n}],
   payableMinor:100n,currency:'USD',reservationId:'reserve-one',reservationVersion:1n,
   paymentAttemptKey:'payment-one',providerReference:'provider-one'};
  const component=await import(pathToFileURL(path.join(work,'generated','orders','repository','service-repositories.js')).href);
  const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
  const table=physical.tables.find(row=>row.entity==='Orders.OrderConfirmedOutbox');
  assert.ok(table,'original generated orders schema must contain the selected Event outbox');
  const db=new DatabaseSync(path.join(work,'generated','orders','store.sqlite'));
  const earlierId='evt_'+('a'.repeat(64)),publishedId='evt_'+('d'.repeat(64));
  const foreignId='evt_'+('f'.repeat(64));
  try{
   db.prepare(table.insert_sql).run(...physical.encode(table.entity,
    {eventId:earlierId,event:{...event,metadata:{...event.metadata,eventId:earlierId}},
     state:'Ready',version:1n}).bindings);
   db.prepare(table.insert_sql).run(...physical.encode(table.entity,
    {eventId:publishedId,event:{...event,metadata:{...event.metadata,eventId:publishedId}},
     state:'Published',version:2n}).bindings);
   db.prepare(table.insert_sql).run(...physical.encode(table.entity,
    {eventId,event,state:'Ready',version:1n}).bindings);
  }finally{db.close();}
  let receiverCommit;
  ({relay,admission,publication,acknowledgement,receiverCommit}=
   assembly.openCrossServiceEvent('Fulfillment.OnOrderConfirmed'));
  const selected=relay.inspect();
  assert.equal(selected.route.producer_operation,'Orders.ConfirmOrder');
  assert.equal(selected.route.consumer_inbox_entity,'Fulfillment.ShipmentInbox');
  assert.equal(selected.route.permission,'fulfillment.create');
  const ack=acknowledgement.inspect();
  assert.equal(ack.source.entry,'Fulfillment.OnOrderConfirmed');
  assert.equal(ack.source.operation,'Fulfillment.CreateShipment');
  assert.equal(ack.source.inbox_entity,'Fulfillment.ShipmentInbox');
  assert.equal(ack.receiver_service,'fulfillment');
  assert.ok(ack.source.candidates.length>=2,'first and repeated occurrence paths must retain inbox commits');
  assert.equal(ack.authority_effect,'none');
  const discovered=[],pages=[];let cursor=null;
  do{
   const page=relay.scanReady(cursor,1);
   discovered.push(...page.occurrence_ids);pages.push(page);cursor=page.next_cursor;
  }while(cursor!==null);
  assert.deepEqual(discovered,[earlierId,eventId]);
  assert.equal(pages.length,3,'cursor advances over a published row without returning it');
  assert.deepEqual(pages[1].occurrence_ids,[]);
  assert.throws(()=>relay.scanReady(null,0),/InputType/);
  assert.throws(()=>relay.scanReady('not-a-cursor',1),/InputType/);
  const changedDb=new DatabaseSync(path.join(work,'generated','orders','store.sqlite'));
  try{changedDb.prepare(table.insert_sql).run(...physical.encode(table.entity,
   {eventId:foreignId,event:{...event,metadata:{...event.metadata,eventId:foreignId,producer:'payments'}},
    state:'Ready',version:1n}).bindings);}
  finally{changedDb.close();}
  assert.throws(()=>relay.scanReady(null,64),/producer outbox differs from selected Event identity/);
  const ready=relay.readReady(eventId);assert.equal(ready.kind,'ready');
  assert.throws(()=>relay.readReady(foreignId),/producer outbox differs from selected Event identity/);
  const publicationScope=publication.inspect();
  assert.equal(publicationScope.native_family,'EventInboxOutbox');
  assert.equal(publicationScope.outbox_identity_field,'eventId');
  assert.equal(publicationScope.ready_state,'Ready');
  assert.equal(publicationScope.published_state,'Published');
  const candidate=publication.prepare(ready.occurrence);
  const proposed=publication.inspectCandidate(candidate);
  assert.equal(proposed.authority_effect,'none');
  assert.equal(proposed.occurrence_id,eventId);
  assert.equal(proposed.expected_version,1n);
  assert.equal(proposed.next_version,2n);
  assert.throws(()=>publication.inspectCandidate({...candidate}),/original Event publication candidate required/);
  const persisted=relay.inspectOccurrence(ready.occurrence);
  assert.equal(persisted.event.metadata.eventId,eventId);
  assert.equal(persisted.event.metadata.producer,'orders');
  assert.equal(persisted.event.orderId,orderId);
  const ticket=admission.prepare(ready.occurrence),bound=admission.inspectTicket(ticket);
  assert.equal(bound.entry,'Fulfillment.OnOrderConfirmed');
  assert.equal(bound.operation,'Fulfillment.CreateShipment');
  assert.equal(bound.parameters.confirmed.metadata.eventId,eventId);
  assert.equal(bound.parameters.confirmed.orderId,orderId);
  assert.throws(()=>admission.inspectTicket({...ticket}),/original Event ingress ticket required/);
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  const selectedAuth=await assembly.openSelectedEntryAuth(native);
  assert.throws(()=>createCoreCommerceEventDelivery({assembly,auth:selectedAuth.auth,
   selected:selectedAuth.entries,producer,receiver,relay,admission,acknowledgement,
   receiverCommit:{...receiverCommit}}),/original Event receiver commit owner required/);
  const delivery=createCoreCommerceEventDelivery({assembly,auth:selectedAuth.auth,
   selected:selectedAuth.entries,producer,receiver,relay,admission,acknowledgement,receiverCommit});
  assert.equal(delivery.inspectActorRequirement().entry,'Fulfillment.OnOrderConfirmed');
  delivery.close();
  const updated=physical.encode(table.entity,{eventId,event,state:'Published',version:2n});
  const columns=[...table.columns.map(column=>column.sql_name),'_craft_row',
   ...table.keys.map((_,index)=>`_craft_key_${index}`)];
  const quote=name=>'"'+name.replaceAll('"','""')+'"';
  const update='UPDATE '+quote(table.physical_name)+' SET '+
   columns.map(column=>quote(column)+'=?').join(',')+' WHERE "_craft_key_0"=?';
  const changed=new DatabaseSync(path.join(work,'generated','orders','store.sqlite'));
  try{assert.equal(changed.prepare(update).run(...updated.bindings,
   ...physical.key(table.entity,0,{eventId})).changes,1);}
  finally{changed.close();}
  assert.throws(()=>publication.inspectCandidate(candidate),
   /committed producer outbox differs from selected Event identity/);
  assembly.close();assembly=null;
  assert.throws(()=>acknowledgement.assertCurrent(),/Event acknowledgement selection closed/);
  assert.throws(()=>receiverCommit.assertCurrent(),/Event receiver commit owner closed/);
  assert.throws(()=>publication.assertCurrent(),/Event publication owner closed/);
  assert.throws(()=>admission.assertCurrent(),/Event ingress admission closed/);
  assert.throws(()=>relay.assertCurrent(),/cross-service Event relay closed/);
 }finally{
  acknowledgement?.close();publication?.close();admission?.close();relay?.close();assembly?.close();
  await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
