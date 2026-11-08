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

test('C14 five-service source selects HTTP routes and executes scoped GET through original Auth and Query',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-core-http-get-'));
 let owner,native,http,actor,deniedActor,entry;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  http=await owner.openSelectedHttpRuntime(native);
  assert.deepEqual([...owner.inspect().services.map(service=>service.id)].sort(),['catalog','fulfillment','inventory','orders','payments']);
  const unknown=await http.handle(new Request('http://localhost/unknown'),null);
  assert.equal(unknown.status,404);
  assert.deepEqual(await unknown.json(),{kind:'error',code:'route-not-found'});
  const wrongMethod=await http.handle(new Request('http://localhost/orders'),null);
  assert.equal(wrongMethod.status,405);
  assert.equal(wrongMethod.headers.get('allow'),'POST');
  const anonymous=await http.handle(new Request('http://localhost/orders/order-1'),null);
  assert.equal(anonymous.status,401);
  assert.deepEqual(await anonymous.json(),{kind:'error',code:'unauthorized'});
  entry=http.auth.bindEntry('Orders.GetOrderEntry');
  const definition=http.auth.inspectEntry(entry),subject='customer-1',evidence='c14-get-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'c14-get-session',
   routes:[{entry:'Orders.GetOrderEntry',permission:definition.access.auth_permission}]});
  actor=registerCommerceEntryFixtureActorV1(http.auth,fixture.handle,{subject,evidence,principal_kind:'customer',service_id:null,
   scope:definition.access.auth_permission.scope});
  const deniedSubject='customer-without-orders-permission',deniedEvidence='c14-denied-evidence';
  const deniedFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:deniedSubject,evidence:deniedEvidence,
   session:'c14-denied-session',routes:[]});
  deniedActor=registerCommerceEntryFixtureActorV1(http.auth,deniedFixture.handle,{subject:deniedSubject,
   evidence:deniedEvidence,principal_kind:'customer',service_id:null,scope:definition.access.auth_permission.scope});
  const forbidden=await http.handle(new Request('http://localhost/orders/missing-order'),deniedActor);
  assert.equal(forbidden.status,403);
  assert.deepEqual(await forbidden.json(),{kind:'error',code:'forbidden'});
  const missing=await http.handle(new Request('http://localhost/orders/missing-order'),actor);
  assert.equal(missing.status,404);
  assert.deepEqual(await missing.json(),{kind:'error',code:'resource-not-found'});
  const unsupported=await http.handle(new Request('http://localhost/orders',{method:'POST',body:'{}'}),actor);
  assert.equal(unsupported.status,415);
  assert.deepEqual(await unsupported.json(),{kind:'error',code:'unsupported-media-type'});
  assert.equal(owner.inspect().complete_application,true);
 }finally{
  if(actor)try{http.auth.disposeActor(actor);}catch{}
  if(deniedActor)try{http.auth.disposeActor(deniedActor);}catch{}
  if(entry)try{http.auth.disposeEntry(entry);}catch{}
  http?.close();owner?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
