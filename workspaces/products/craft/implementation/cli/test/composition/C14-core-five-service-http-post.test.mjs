import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceServiceArtifactOwner} from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {produceCommerceAuthNativeOwnerV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';
import {registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 source-selected POST uses native customer and service Auth, then maps absent Catalog quote to the declared 404',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-core-http-post-'));
 let owner,native,http,customerActor,serviceActor,customerEntry,serviceEntry;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  http=await owner.openSelectedHttpRuntime(native);
  const route=owner.selectHttpRoute('POST','/orders');
  assert.equal(route.kind,'matched');
  assert.equal(route.route.entry,'Orders.PlaceOrderEntry');
  const requirements=http.service_actor_requirements.filter(row=>row.caller_service==='orders');
  const requirement=requirements.find(row=>row.entry==='Catalog.ReadQuoteEntry'&&row.target_service==='catalog');
  assert.ok(requirement);
  assert.equal(requirement.target_service,'catalog');
  customerEntry=http.auth.bindEntry(route.route.entry);
  serviceEntry=http.auth.bindEntry(requirement.entry);
  const customerPermission=http.auth.inspectEntry(customerEntry).access.auth_permission;
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
  const request=()=>new Request('http://localhost/orders',{method:'POST',headers:{'content-type':'application/json'},
   body:JSON.stringify({quoteId:'missing-quote',checkoutKey:'checkout-1'})});
  const anonymous=await http.handle(request(),null);
  assert.equal(anonymous.status,401);
  const missing=await http.handle(request(),customerActor);
  assert.equal(missing.status,404);
  assert.deepEqual(await missing.json(),{kind:'error',code:'resource-not-found'});
  assert.equal(owner.inspect().complete_application,true);
 }finally{
  if(customerActor)try{http.auth.disposeActor(customerActor);}catch{}
  if(serviceActor)try{http.auth.disposeActor(serviceActor);}catch{}
  if(customerEntry)try{http.auth.disposeEntry(customerEntry);}catch{}
  if(serviceEntry)try{http.auth.disposeEntry(serviceEntry);}catch{}
  http?.close();owner?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
