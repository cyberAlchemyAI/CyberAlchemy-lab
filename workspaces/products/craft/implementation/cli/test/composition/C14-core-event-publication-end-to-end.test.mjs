/** Full generated Commerce producer→receiver→publication acceptance.
 * This is opt-in while the source-selected Workflow terminal path is being
 * completed. A seeded outbox cannot satisfy this test.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner}
 from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {createCommerceTestAuthNativeV1}
 from '../support/commerce-auth-native-variant-v1.ts';
import {registerCommerceEntryFixtureActorV1}
 from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1}
 from '../support/commerce-auth-fixture-provider-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1}
 from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
const headers={'content-type':'application/json; charset=utf-8','demopay-protocol':'1'};
const startedAt=process.hrtime.bigint();
const phase=(name)=>console.error('C14 Event full path phase='+name+
 ' elapsed_s='+Number((process.hrtime.bigint()-startedAt)/1000000000n));

async function generatedPhysical(root,service){
 const component=await import(pathToFileURL(path.join(root,'runtime',service,
  'repository','service-repositories.js')).href);
 return deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
}
function insertGenerated(root,service,physical,entity,value){
 const table=physical.tables.find(row=>row.entity===entity);assert.ok(table);
 const db=new DatabaseSync(path.join(root,'runtime',service,'store.sqlite'));
 try{db.prepare(table.insert_sql).run(...physical.encode(entity,value).bindings);}finally{db.close();}
}
function replaceGeneratedForNegative(root,service,physical,entity,value,key){
 const table=physical.tables.find(row=>row.entity===entity);assert.ok(table);
 const quote=name=>'"'+name.replaceAll('"','""')+'"';
 const names=[...table.columns.map(column=>column.sql_name),'_craft_row',
  ...table.keys.map((_,index)=>'_craft_key_'+index)];
 const encoded=physical.encode(entity,value),originalKey=physical.key(entity,0,key)[0];
 const sql='UPDATE '+quote(table.physical_name)+' SET '+
  names.map(name=>quote(name)+'=?').join(',')+' WHERE "_craft_key_0"=?';
 const db=new DatabaseSync(path.join(root,'runtime',service,'store.sqlite'));
 try{assert.equal(db.prepare(sql).run(...encoded.bindings,originalKey).changes,1);}
 finally{db.close();}
}
function readGenerated(root,service,physical,entity){
 const table=physical.tables.find(row=>row.entity===entity);assert.ok(table);
 const db=new DatabaseSync(path.join(root,'runtime',service,'store.sqlite'));
 try{return db.prepare('SELECT * FROM "'+table.physical_name+'"').all()
  .map(row=>physical.decode(entity,row));}finally{db.close();}
}
function capturedDemoPay(){
 const captures=new Map();
 return {async exchange(request){
  assert.equal(request.origin,'https://demopay.invalid');
  assert.equal(request.method,'POST');
  const input=JSON.parse(Buffer.from(request.body).toString('utf8'));
  const existing=captures.get(input.attemptKey);
  if(request.path==='/v1/capture/inspect'&&!existing)
   return {status:404,headers,body:Buffer.from(JSON.stringify({...input,
    status:'UnknownKey',providerReference:null}))};
  assert.ok(request.path==='/v1/capture'||request.path==='/v1/capture/inspect');
  const result=existing??{...input,status:'Captured',
   providerReference:'demopay-'+input.attemptKey};
  captures.set(input.attemptKey,result);
  return {status:200,headers,body:Buffer.from(JSON.stringify(result))};
 }};
}

test('C14 generated ConfirmOrder commits an Event, receiver consumes once, producer publishes and reopens',
 {skip:process.env.CRAFT_C14_EVENT_FULL_RUN!=='1'},async()=>{
 const work=mkdtempSync(path.join('/var/tmp','craft-c14-event-full-')),
  firstRoot=path.join(work,'first'),reopenedRoot=path.join(work,'reopened');
 let owner,reopened,native,http,delivery,auth,successful=false;
 const actors=[];
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,firstRoot);
  assert.equal(owner.inspect().services.length,5);
  phase('five-service-generated');
  native=await createCommerceTestAuthNativeV1(path.join(work,'auth'));
  const generated=await import(pathToFileURL(path.join(firstRoot,'artifacts','application.mjs')).href);
  http=await generated.createGeneratedCommerceApplication(owner,native);
  auth=http.auth;
  const post=owner.selectHttpRoute('POST','/orders');assert.equal(post.kind,'matched');
  const postEntry=http.auth.bindEntry(post.route.entry),
   postPermission=http.auth.inspectEntry(postEntry).access.auth_permission;
  try{
   const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'full-customer',
    evidence:'full-customer-evidence',session:'full-customer-session',valid_for_seconds:43200,
    routes:[{entry:post.route.entry,permission:postPermission}]});
   const customer=registerCommerceEntryFixtureActorV1(http.auth,fixture.handle,{subject:'full-customer',
    evidence:'full-customer-evidence',principal_kind:'customer',service_id:null,
    scope:postPermission.scope});actors.push(customer);
   const queryRequirements=http.serviceActorRequirements,
    workerRequirements=http.inspectWorkerActorRequirements('Orders.Checkout.Checkout');
   const requirements=[...queryRequirements,...workerRequirements];
   const routes=[...new Map(requirements.filter(row=>row.caller_service==='orders')
    .map(row=>[row.entry,{entry:row.entry,
     permission:'auth_permission' in row?row.auth_permission:row.permission}])).values()];
   assert.ok(routes.some(row=>row.entry==='Orders.ConfirmOrderEntry'));
   assert.ok(routes.some(row=>row.entry==='Fulfillment.OnOrderConfirmed')===false);
   owner.openDemoPayDispatch(capturedDemoPay());
   const assigned=new Set();
   const routesByScope=new Map();
   for(const route of routes){const scope=route.permission.scope;
    const group=routesByScope.get(scope)??[];group.push(route);routesByScope.set(scope,group);}
   for(const [index,[scope,group]] of [...routesByScope].entries()){
    const subject='full-orders-service-'+index,evidence='full-orders-evidence-'+index;
    const serviceFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,
     session:'full-orders-session-'+index,valid_for_seconds:43200,routes:group});
    const actor=registerCommerceEntryFixtureActorV1(http.auth,serviceFixture.handle,
     {subject,evidence,principal_kind:'service',service_id:'orders',
      scope});actors.push(actor);
    if(queryRequirements.some(row=>row.caller_service==='orders'&&row.scope===scope))
     for(const entry of http.bindServiceActor(actor))assigned.add(entry);
    if(workerRequirements.some(row=>row.caller_service==='orders'&&row.auth_permission.scope===scope))
     for(const entry of http.bindWorkerActor('Orders.Checkout.Checkout',actor))assigned.add(entry);
   }
   assert.ok(assigned.has('Orders.ConfirmOrderEntry'));
   const catalog=await generatedPhysical(firstRoot,'catalog'),
    inventory=await generatedPhysical(firstRoot,'inventory'),
    orders=await generatedPhysical(firstRoot,'orders');
   insertGenerated(firstRoot,'catalog',catalog,'Catalog.Quote',{
    id:'full-quote',customerId:'full-customer',currency:'USD',
    lines:[{sku:'full-sku',quantity:1n,unitPriceMinor:100n}],
    discountMinor:0n,taxMinor:0n,shippingMinor:0n,
    expiresAtEpochMs:4102444800000n,version:1n});
   insertGenerated(firstRoot,'inventory',inventory,'Inventory.Stock',{
    sku:'full-sku',onHand:20n,reserved:0n,allocated:0n,version:1n});
   phase('source-generated-quote-and-stock-ready');
   const accepted=await http.handle(new Request('http://localhost/orders',{method:'POST',
    headers:{'content-type':'application/json'},
    body:JSON.stringify({quoteId:'full-quote',checkoutKey:'full-checkout'})}),customer);
   assert.equal(accepted.status,202);
   const body=await accepted.json(),orderId=body.value.orderId;
   assert.equal(body.kind,'accepted');assert.equal(typeof orderId,'string');
   phase('generated-place-order-committed');
   const page=await http.relayWorkflowPage('Orders.Checkout.Checkout',null,8);
   assert.equal(page.results.length,1);assert.equal(page.results[0].outcome.kind,'enqueued');
   const originalOccurrence=page.results[0].occurrence_id;
   phase('generated-workflow-pass-started');
   const workflow=await http.runWorkflow('Orders.Checkout.Checkout',originalOccurrence);
   assert.equal(workflow.kind,'cycle-result');
   assert.equal(workflow.result.kind,'finished',JSON.stringify(workflow.result));
   assert.equal(workflow.result.terminal,'confirmed');
   assert.equal(workflow.result.order_id,orderId);
   phase('generated-confirm-order-committed');
   const outboxes=readGenerated(firstRoot,'orders',orders,'Orders.OrderConfirmedOutbox');
   assert.equal(outboxes.length,1);
   const outbox=outboxes[0],eventId=outbox.eventId;
   assert.equal(outbox.event.orderId,orderId);assert.equal(outbox.state,'Ready');
   assert.deepEqual(http.scanReadyEventPage('Fulfillment.OnOrderConfirmed',null,8),
    {occurrence_ids:[eventId],next_cursor:null});
   const selected=owner.openCrossServiceEvent('Fulfillment.OnOrderConfirmed');
   assert.deepEqual(selected.relay.readReady('evt_'+('f'.repeat(64))),
    {kind:'not-ready',authority_effect:'none'});
   const ready=selected.relay.readReady(eventId);assert.equal(ready.kind,'ready');
   const proof=selected.provenance.inspectRecorded(ready.occurrence);
   assert.equal(selected.provenance.inspectProof(proof).provenance,'persisted-command-replay');
   // A Ready row with the same occurrence ID but different Event content cannot
   // inherit the original producer command. Restore the exact logical row for
   // the positive delivery path after both source-bound negatives reject it.
   replaceGeneratedForNegative(firstRoot,'orders',orders,
    'Orders.OrderConfirmedOutbox',
    {...outbox,event:{...outbox.event,customerId:'changed-customer'}},{eventId});
   assert.throws(()=>selected.relay.inspectOccurrence(ready.occurrence),
    /cross-service Event occurrence changed/);
   const changed=selected.relay.readReady(eventId);assert.equal(changed.kind,'ready');
   assert.throws(()=>selected.provenance.inspectRecorded(changed.occurrence));
   replaceGeneratedForNegative(firstRoot,'orders',orders,
    'Orders.OrderConfirmedOutbox',outbox,{eventId});
   assert.equal(selected.relay.inspectOccurrence(ready.occurrence).occurrence_id,eventId);
   delivery=selected.openDelivery();
   const requirement=delivery.inspectActorRequirement();
   const eventFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'full-event-orders',
    evidence:'full-event-evidence',session:'full-event-session',valid_for_seconds:43200,
    routes:[{entry:requirement.entry,permission:requirement.auth_permission}]});
   const eventActor=registerCommerceEntryFixtureActorV1(http.auth,eventFixture.handle,
    {subject:'full-event-orders',evidence:'full-event-evidence',principal_kind:'service',
     service_id:'orders',scope:requirement.auth_permission.scope});actors.push(eventActor);
   const candidate=selected.publication.prepare(ready.occurrence);
   // Proof custody rejects a copied object on its own, before receiver ACK
   // handling can affect the result. Publication separately rejects both
   // substituted proof and substituted ACK while the outbox remains Ready.
   assert.throws(()=>selected.provenance.inspectProof({...proof}),
    /original producer|original generated|original bounded producer/);
   await assert.rejects(selected.publish({candidate,proof:{...proof},delivery,
    acknowledgement:{kind:'original-event-persisted-receiver-acknowledgement/v1-candidate'}}),
    /original producer|original generated|original bounded producer/);
   await assert.rejects(selected.publish({candidate,proof,delivery,
    acknowledgement:{kind:'original-event-persisted-receiver-acknowledgement/v1-candidate'}}),
    /original generated Event receiver acknowledgement required/);
   assert.equal(owner.serviceStorage('fulfillment').countStoredRecords('Fulfillment.ShipmentInbox'),0n);
   assert.equal(owner.serviceStorage('fulfillment').countStoredRecords('Fulfillment.Shipment'),0n);
   assert.equal(owner.serviceStorage('orders').inspectStoredRecord(
    'Orders.OrderConfirmedOutbox',0,{eventId}).state,'Ready');
   // The application-level Event pass owns the original producer proof,
   // first receiver commit and publication sequence. Its caller supplies only the
   // occurrence identity and the authorized service actor.
   const eventPass=owner.openSelectedEventPass('Fulfillment.OnOrderConfirmed');
   assert.deepEqual(eventPass.inspect(),{
    entry:'Fulfillment.OnOrderConfirmed',event:'Shop.Events.OrderConfirmed',
    outbox:'Orders.OrderConfirmedOutbox',inbox:'Fulfillment.ShipmentInbox',
    producer_service:'orders',receiver_service:'fulfillment',
    source_capture_sha256:owner.inspect().source_capture_sha256,
    qualification:'source-selected-in-process-event-delivery-and-publication'});
   assert.equal(eventPass.inspectActorRequirement().entry,'Fulfillment.OnOrderConfirmed');
   const committed=await http.runEvent('Fulfillment.OnOrderConfirmed',eventId,eventActor);
   assert.equal(committed.kind,'publication-result');
   const published=committed.result;
   assert.equal(published.kind,'published');
   assert.equal(published.occurrence_id,eventId);
   assert.equal(published.version,2n);
   assert.equal(owner.serviceStorage('fulfillment').countStoredRecords('Fulfillment.ShipmentInbox'),1n);
   assert.equal(owner.serviceStorage('fulfillment').countStoredRecords('Fulfillment.Shipment'),1n);
   phase('generated-fulfillment-receiver-committed-and-published');
   assert.equal(owner.serviceStorage('orders').inspectStoredRecord(
    'Orders.OrderConfirmedOutbox',0,{eventId}).state,'Published');
   assert.equal((await selected.reconcilePublished(eventId)).kind,'recorded');
   assert.deepEqual(http.scanReadyEventPage('Fulfillment.OnOrderConfirmed',null,8),
    {occurrence_ids:[],next_cursor:null});
   const replay=await http.runEvent('Fulfillment.OnOrderConfirmed',eventId,eventActor);
   assert.equal(replay.kind,'publication-result');
   assert.equal(replay.result.kind,'recorded');
   await assert.rejects(selected.publish({candidate,proof,delivery,
    acknowledgement:{kind:'original-event-persisted-receiver-acknowledgement/v1-candidate'}}));
   assert.equal(owner.serviceStorage('orders').inspectStoredRecord(
    'Orders.OrderConfirmedOutbox',0,{eventId}).version,2n);
   assert.equal(owner.serviceStorage('fulfillment').countStoredRecords('Fulfillment.ShipmentInbox'),1n);
   assert.equal(owner.serviceStorage('fulfillment').countStoredRecords('Fulfillment.Shipment'),1n);
   phase('native-producer-publication-committed');
   delivery.close();delivery=undefined;
   for(const actor of actors)auth.disposeActor(actor);
   actors.length=0;
   auth.disposeEntry(postEntry);
   http.close();http=undefined;
   owner.close();owner=undefined;
   await native.dispose();native=undefined;
   const services=Object.fromEntries(['catalog','orders','payments','inventory','fulfillment']
    .map(id=>[id,{mode:'reopen',directory:path.join(firstRoot,'runtime',id)}]));
   reopened=await createCoreCommerceServiceArtifactOwner(source,reopenedRoot,{services});
   const reopenedEvent=reopened.openCrossServiceEvent('Fulfillment.OnOrderConfirmed');
   const recovered=await reopenedEvent.reconcilePublished(eventId);
   assert.equal(recovered.kind,'recorded');
   assert.equal(recovered.version,2n);
   assert.equal(reopened.serviceStorage('fulfillment').countStoredRecords('Fulfillment.ShipmentInbox'),1n);
   assert.equal(reopened.serviceStorage('orders').inspectStoredRecord(
    'Orders.OrderConfirmedOutbox',0,{eventId}).state,'Published');
   // The reopened owner receives only the occurrence ID; the original ACK,
   // publication attempt and return receipt are absent from this process.
   phase('reopened-native-command-and-row-reconciled');
   successful=true;
  }finally{if(http)try{auth.disposeEntry(postEntry);}catch{}}
 }finally{
  delivery?.close();
  if(http)for(const actor of actors)try{http.auth.disposeActor(actor);}catch{}
  http?.close();owner?.close();reopened?.close();await native?.dispose();
  if(successful)rmSync(work,{recursive:true,force:true});
  else console.error('C14 Event full path diagnostic fixture retained at '+work);
 }
});
