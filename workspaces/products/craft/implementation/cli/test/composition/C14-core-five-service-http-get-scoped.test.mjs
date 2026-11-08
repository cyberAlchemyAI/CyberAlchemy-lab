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

test('C14 original scoped GET evaluates native customer context and maps a missing row to declared 404',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-core-http-scoped-get-'));
 let owner,native,http,actor,entry;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  console.error('C14 scoped GET: five-service application ready');
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  http=await owner.openSelectedHttpRuntime(native);
  entry=http.auth.bindEntry('Orders.GetOrderEntry');
  const definition=http.auth.inspectEntry(entry),subject='scoped-customer',evidence='c14-scoped-get-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'c14-scoped-get-session',
   routes:[{entry:'Orders.GetOrderEntry',permission:definition.access.auth_permission}]});
  actor=registerCommerceEntryFixtureActorV1(http.auth,fixture.handle,{subject,evidence,
   principal_kind:'customer',service_id:null,scope:definition.access.auth_permission.scope});
  console.error('C14 scoped GET: native customer actor ready');
  const response=await http.handle(new Request('http://localhost/orders/missing-order'),actor);
  console.error('C14 scoped GET: original Query returned',response.status);
  assert.equal(response.status,404);
  assert.deepEqual(await response.json(),{kind:'error',code:'resource-not-found'});
  assert.equal(owner.inspect().complete_application,true);
 }finally{
  if(actor)try{http.auth.disposeActor(actor);}catch{}
  if(entry)try{http.auth.disposeEntry(entry);}catch{}
  http?.close();owner?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
