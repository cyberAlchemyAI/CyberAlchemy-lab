import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createCommerceApplicationAssemblyV1} from '../../src/commerce/commerce-application-assembly-v1.ts';
import {createCoreCommerceWorkerActorRegistry} from '../../src/generic/core-commerce-worker-actor-registry.ts';
import {produceCommerceAuthNativeOwnerV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';
import {registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 worker actor registry derives every required Entry from source and keeps native Auth at invocation',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-worker-actors-'));
 let assembly,native,selected,serviceActor,customerActor;
 try{
  assembly=await createCommerceApplicationAssemblyV1(source,path.join(work,'generated'));
  console.error('C14 worker registry: original application assembly ready');
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  selected=await assembly.openSelectedEntryAuth(native);
  console.error('C14 worker registry: native Auth and selected Entry ready');
  const registry=createCoreCommerceWorkerActorRegistry(assembly,selected.auth,'Orders.Checkout.Checkout');
  console.error('C14 worker registry: checked Workflow requirements ready');
  const initial=registry.inspect();
  assert.ok(initial.requirements.length>4);
  assert.ok(initial.requirements.some(row=>row.usage==='claim'&&row.entry==='Orders.ClaimCheckoutWorkEntry'));
  assert.ok(initial.requirements.some(row=>row.usage==='snapshot'&&row.entry==='Orders.ReadCheckoutSnapshotEntry'));
  assert.ok(initial.requirements.some(row=>row.usage==='observation'&&row.entry==='Orders.RecordCheckoutObservationEntry'));
  assert.ok(initial.requirements.some(row=>row.usage==='remote'&&row.step==='reserve'&&row.entry==='Inventory.ReserveStockEntry'));
  assert.deepEqual(initial.assigned_entries,[]);
  assert.equal(initial.missing_entries.length,new Set(initial.requirements.map(row=>row.entry)).size);
  assert.throws(()=>registry.actorFor('claim'),/missing/);
  const claim=initial.requirements.find(row=>row.usage==='claim');
  const customer=seedCommerceAuthFixtureDatabaseV1(native,{subject:'worker-customer',evidence:'worker-customer-evidence',
   session:'worker-customer-session',routes:[{entry:claim.entry,permission:claim.auth_permission}]});
  customerActor=registerCommerceEntryFixtureActorV1(selected.auth,customer.handle,{subject:'worker-customer',
   evidence:'worker-customer-evidence',principal_kind:'customer',service_id:null,scope:claim.auth_permission.scope});
  assert.throws(()=>registry.bind(customerActor),/service actor required/);
  const service=seedCommerceAuthFixtureDatabaseV1(native,{subject:'worker-orders',evidence:'worker-orders-evidence',
   session:'worker-orders-session',routes:[{entry:claim.entry,permission:claim.auth_permission}]});
  serviceActor=registerCommerceEntryFixtureActorV1(selected.auth,service.handle,{subject:'worker-orders',
   evidence:'worker-orders-evidence',principal_kind:'service',service_id:claim.caller_service,scope:claim.auth_permission.scope});
  const assigned=registry.bind(serviceActor);
  assert.ok(assigned.includes('Orders.ClaimCheckoutWorkEntry'));
  assert.equal(registry.actorFor('claim'),serviceActor);
  assert.equal(registry.actorFor('snapshot'),serviceActor);
  assert.equal(registry.actorFor('remote','reserve'),serviceActor);
  assert.equal(registry.actorFor('observation'),serviceActor);
  assert.deepEqual(registry.inspect().missing_entries,[]);
  assert.equal(registry.inspect().qualification,'native-service-actor-selection-only;fresh-entry-auth-required');
  selected.auth.disposeActor(serviceActor);serviceActor=undefined;
  assert.throws(()=>registry.actorFor('claim'),/DisposedOwner/);
 }finally{
  if(serviceActor)try{selected?.auth.disposeActor(serviceActor);}catch{}
  if(customerActor)try{selected?.auth.disposeActor(customerActor);}catch{}
  assembly?.close();await native?.dispose();rmSync(work,{recursive:true,force:true});
 }
});
