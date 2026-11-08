import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner} from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {produceCommerceAuthNativeOwnerV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';
import {registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 source-selected POST accepts a generated Catalog quote through native Auth and returns 202',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-core-http-accepted-'));
 let owner,native,http,customerActor,getActor,serviceActor,customerEntry,customerGetEntry,serviceEntry;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  console.error('C14 accepted: five-service artifact ready');
  const workerActors=owner.inspectWorkerActorRequirements('Orders.Checkout.Checkout');
  assert.ok(workerActors.some(row=>row.usage==='claim'&&row.entry==='Orders.ClaimCheckoutWorkEntry'&&row.caller_service==='orders'));
  assert.ok(workerActors.some(row=>row.usage==='snapshot'&&row.entry==='Orders.ReadCheckoutSnapshotEntry'&&row.caller_service==='orders'));
  assert.ok(workerActors.some(row=>row.usage==='observation'&&row.entry==='Orders.RecordCheckoutObservationEntry'&&row.caller_service==='orders'));
  assert.ok(workerActors.some(row=>row.usage==='remote'&&row.entry==='Inventory.ReserveStockEntry'&&row.target_service==='inventory'));
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  http=await owner.openSelectedHttpRuntime(native);
  console.error('C14 accepted: selected HTTP/Auth ready');
  const route=owner.selectHttpRoute('POST','/orders');
  assert.equal(route.kind,'matched');
  assert.equal(route.route.entry,'Orders.PlaceOrderEntry');
  const getRoute=owner.selectHttpRoute('GET','/orders/order-placeholder');
  assert.equal(getRoute.kind,'matched');
  assert.equal(getRoute.route.entry,'Orders.GetOrderEntry');
  const requirements=http.service_actor_requirements.filter(row=>row.caller_service==='orders');
  const requirement=requirements.find(row=>row.entry==='Catalog.ReadQuoteEntry'&&row.target_service==='catalog');
  assert.ok(requirement);
  assert.equal(requirement.target_service,'catalog');
  customerEntry=http.auth.bindEntry(route.route.entry);
  customerGetEntry=http.auth.bindEntry(getRoute.route.entry);
  serviceEntry=http.auth.bindEntry(requirement.entry);
  const customerPermission=http.auth.inspectEntry(customerEntry).access.auth_permission;
  const customerGetPermission=http.auth.inspectEntry(customerGetEntry).access.auth_permission;
  assert.equal(customerGetPermission.scope,customerPermission.scope);
  const servicePermission=http.auth.inspectEntry(serviceEntry).access.auth_permission;
  assert.deepEqual(requirement.permission,servicePermission);
  const customerFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'post-customer',evidence:'c14-post-customer-evidence',
   session:'c14-post-customer-session',routes:[{entry:route.route.entry,permission:customerPermission}]});
  customerActor=registerCommerceEntryFixtureActorV1(http.auth,customerFixture.handle,{subject:'post-customer',
   evidence:'c14-post-customer-evidence',principal_kind:'customer',service_id:null,scope:customerPermission.scope});
  const serviceFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'post-orders-service',evidence:'c14-post-service-evidence',
   session:'c14-post-service-session',routes:[{entry:requirement.entry,permission:requirement.permission}]});
  serviceActor=registerCommerceEntryFixtureActorV1(http.auth,serviceFixture.handle,{subject:'post-orders-service',
   evidence:'c14-post-service-evidence',principal_kind:'service',service_id:requirement.caller_service,scope:requirement.scope});
  assert.ok(http.bindServiceActor(serviceActor).includes(requirement.entry));
  console.error('C14 accepted: native customer and Catalog service actors ready');
  const repository=path.join(work,'generated','runtime','catalog','repository','service-repositories.js');
  const component=await import(pathToFileURL(repository).href);
  const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
  const table=physical.tables.find(row=>row.entity==='Catalog.Quote');
  assert.ok(table);
  const quote={id:'quote-one',customerId:'post-customer',currency:'USD',
   lines:[{sku:'sku-one',quantity:1n,unitPriceMinor:100n}],
   discountMinor:0n,taxMinor:0n,shippingMinor:0n,expiresAtEpochMs:4102444800000n,version:1n};
  const stored=physical.encode('Catalog.Quote',quote);
  const db=new DatabaseSync(path.join(work,'generated','runtime','catalog','store.sqlite'));
  try{db.prepare(table.insert_sql).run(...stored.bindings);}finally{db.close();}
  console.error('C14 accepted: generated Catalog Quote seeded');
  const accepted=await http.handle(new Request('http://localhost/orders',{method:'POST',headers:{'content-type':'application/json'},
   body:JSON.stringify({quoteId:'quote-one',checkoutKey:'checkout-accepted'})}),customerActor);
  console.error('C14 accepted: generated Orders POST returned',accepted.status);
  assert.equal(accepted.status,202);
  const acceptedBody=await accepted.json();
  assert.equal(acceptedBody.kind,'accepted');
  assert.equal(typeof acceptedBody.value.orderId,'string');
  assert.ok(acceptedBody.value.orderId.length>0);
  assert.equal(acceptedBody.value.status,'AwaitingStock');
  assert.equal(acceptedBody.value.payableMinor,'100');
  assert.equal(acceptedBody.value.currency,'USD');
  const relay=owner.openOutboxRelay('Orders.Checkout.Checkout');
  const relayed=await relay.relayPage(null,8);
  console.error('C14 accepted: original committed outbox relay returned',relayed.results.map(row=>row.outcome.kind));
  assert.equal(relayed.results.length,1);
  assert.equal(relayed.results[0].outcome.kind,'enqueued');
  assert.equal(relayed.next_cursor,null);
  const getFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'post-customer',evidence:'c14-get-customer-evidence',
   session:'c14-get-customer-session',routes:[{entry:getRoute.route.entry,permission:customerGetPermission}]});
  getActor=registerCommerceEntryFixtureActorV1(http.auth,getFixture.handle,{subject:'post-customer',
   evidence:'c14-get-customer-evidence',principal_kind:'customer',service_id:null,scope:customerGetPermission.scope});
  const fetched=await http.handle(new Request('http://localhost/orders/'+encodeURIComponent(acceptedBody.value.orderId)),getActor);
  console.error('C14 accepted: source-selected scoped GET returned',fetched.status);
  assert.equal(fetched.status,200);
  const fetchedBody=await fetched.json();
  assert.equal(fetchedBody.kind,'ok');
  assert.equal(fetchedBody.value.id,acceptedBody.value.orderId);
  assert.equal(fetchedBody.value.customerId,'post-customer');
  assert.equal(fetchedBody.value.quoteId,'quote-one');
  assert.equal(fetchedBody.value.payableMinor,'100');
  assert.equal(owner.inspect().complete_application,true);
 }finally{
  if(customerActor)try{http.auth.disposeActor(customerActor);}catch{}
  if(getActor)try{http.auth.disposeActor(getActor);}catch{}
  if(serviceActor)try{http.auth.disposeActor(serviceActor);}catch{}
  if(customerEntry)try{http.auth.disposeEntry(customerEntry);}catch{}
  if(customerGetEntry)try{http.auth.disposeEntry(customerGetEntry);}catch{}
  if(serviceEntry)try{http.auth.disposeEntry(serviceEntry);}catch{}
  http?.close();owner?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
