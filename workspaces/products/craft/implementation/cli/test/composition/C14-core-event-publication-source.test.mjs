/** Original Commerce Event publication source and native authority boundary.
 * The seeded outbox is deliberately insufficient to prove a generated producer
 * commit or to publish. A separate end-to-end test must reach ConfirmOrder.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCommerceApplicationAssemblyV1}
 from '../../src/commerce/commerce-application-assembly-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1}
 from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 checked Event publication refuses an outbox without its generated ConfirmOrder journal',
 {skip:process.env.CRAFT_C14_EVENT_PUBLICATION_SOURCE_RUN!=='1'},async()=>{
  const work=mkdtempSync(path.join('/var/tmp','craft-c14-event-publication-'));
  let assembly;
  try{
   assembly=await createCommerceApplicationAssemblyV1(source,path.join(work,'generated'));
   const producer=await assembly.openServiceStorage('orders');
   await assembly.openServiceStorage('fulfillment');
   const selected=assembly.openCrossServiceEvent('Fulfillment.OnOrderConfirmed');
   const publication=selected.publication.inspect(),plan=selected.producerSource.inspect();
   assert.equal(publication.publication_machine,'Shop.Events.OutboxPublication');
   assert.equal(publication.publication_signal,'ConsumerCommitted');
   assert.equal(publication.outbox_entity,'Orders.OrderConfirmedOutbox');
   assert.equal(publication.entry,'Fulfillment.OnOrderConfirmed');
   assert.equal(publication.producer_operation,'Orders.ConfirmOrder');
   assert.equal(plan.entry,'Orders.ConfirmOrderEntry');
   assert.equal(plan.transaction,'ConfirmCheckout');
   assert.equal(plan.outbox_binding,'outbox');
   assert.equal(plan.event_binding,'confirmed');
   assert.equal(plan.action_binding,'actionReceipt');
   assert.equal(plan.source_capture_sha256,publication.source_capture_sha256);
   const eventId='evt_'+('e'.repeat(64)),orderId='unproven-order';
   const event={metadata:{eventId,producer:'orders',aggregateId:orderId,
    aggregateVersion:2n,ordinal:0n,correlationId:orderId,commandId:'cmd_unproven'},
    orderId,customerId:'unproven-customer',lines:[{sku:'sku-unproven',quantity:1n}],
    payableMinor:100n,currency:'USD',reservationId:'reservation-unproven',
    reservationVersion:1n,paymentAttemptKey:'payment-unproven',
    providerReference:'provider-unproven'};
   const component=await import(pathToFileURL(path.join(work,'generated','orders',
    'repository','service-repositories.js')).href);
   const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData),
    table=physical.tables.find(row=>row.entity==='Orders.OrderConfirmedOutbox');
   assert.ok(table);
   const db=new DatabaseSync(path.join(work,'generated','orders','store.sqlite'));
   try{db.prepare(table.insert_sql).run(...physical.encode(table.entity,
    {eventId,event,state:'Ready',version:1n}).bindings);}finally{db.close();}
   const ready=selected.relay.readReady(eventId);
   assert.equal(ready.kind,'ready');
   const proposal=selected.publication.prepare(ready.occurrence);
   assert.equal(selected.publication.inspectCandidate(proposal).expected_version,1n);
   assert.throws(()=>selected.provenance.inspectRecorded(ready.occurrence),
    /original bounded producer Event record required|original producer command is not durably recorded/);
   assert.throws(()=>producer.reconcileEventPublication({
    kind:'original-native-event-publication-attempt/v1-candidate'}),
    /original native Event publication attempt required/);
   assert.deepEqual(await selected.reconcilePublished(eventId),
    {kind:'conflict',authority_effect:'none'});
   const outbox=producer.inspectStoredRecord('Orders.OrderConfirmedOutbox',0,{eventId});
   assert.equal(outbox.state,'Ready');
   assert.equal(outbox.version,1n);
  }finally{assembly?.close();rmSync(work,{recursive:true,force:true});}
 });
