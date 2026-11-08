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

test('C14 selected scoped GET returns the owner Order and hides it from another authorized customer',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-core-get-existing-'));
 let owner,native,http,actor,otherActor,entry;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  console.error('C14 existing GET: five-service artifact ready');
  const modulePath=path.join(work,'generated','runtime','orders','repository','service-repositories.js');
  const component=await import(pathToFileURL(modulePath).href);
  const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
  const table=physical.tables.find(row=>row.entity==='Orders.Order');
  assert.ok(table);
  const order={id:'order-existing',customerId:'get-customer',quoteId:'quote-existing',currency:'USD',payableMinor:100n,
   lines:[{sku:'sku-one',quantity:1n}],status:'AwaitingStock',version:1n};
  const stored=physical.encode('Orders.Order',order);
  const db=new DatabaseSync(path.join(work,'generated','runtime','orders','store.sqlite'));
  try{db.prepare(table.insert_sql).run(...stored.bindings);}finally{db.close();}
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  http=await owner.openSelectedHttpRuntime(native);
  entry=http.auth.bindEntry('Orders.GetOrderEntry');
  const permission=http.auth.inspectEntry(entry).access.auth_permission;
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'get-customer',evidence:'get-existing-evidence',
   session:'get-existing-session',routes:[{entry:'Orders.GetOrderEntry',permission}]});
  actor=registerCommerceEntryFixtureActorV1(http.auth,fixture.handle,{subject:'get-customer',
   evidence:'get-existing-evidence',principal_kind:'customer',service_id:null,scope:permission.scope});
  console.error('C14 existing GET: generated Order and native customer actor ready');
  const response=await http.handle(new Request('http://localhost/orders/order-existing'),actor);
  console.error('C14 existing GET: selected scoped Query returned',response.status);
  assert.equal(response.status,200);
  const body=await response.json();
  assert.equal(body.kind,'ok');
  assert.equal(body.value.id,'order-existing');
  assert.equal(body.value.customerId,'get-customer');
  assert.equal(body.value.quoteId,'quote-existing');
  assert.equal(body.value.payableMinor,'100');
  const other=seedCommerceAuthFixtureDatabaseV1(native,{subject:'other-customer',evidence:'other-customer-evidence',
   session:'other-customer-session',routes:[{entry:'Orders.GetOrderEntry',permission}]});
  otherActor=registerCommerceEntryFixtureActorV1(http.auth,other.handle,{subject:'other-customer',
   evidence:'other-customer-evidence',principal_kind:'customer',service_id:null,scope:permission.scope});
  const hidden=await http.handle(new Request('http://localhost/orders/order-existing'),otherActor);
  assert.equal(hidden.status,404);
  assert.deepEqual(await hidden.json(),{kind:'error',code:'resource-not-found'});
  assert.equal(owner.inspect().complete_application,true);
 }finally{
  if(actor)try{http.auth.disposeActor(actor);}catch{}
  if(otherActor)try{http.auth.disposeActor(otherActor);}catch{}
  if(entry)try{http.auth.disposeEntry(entry);}catch{}
  http?.close();owner?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
