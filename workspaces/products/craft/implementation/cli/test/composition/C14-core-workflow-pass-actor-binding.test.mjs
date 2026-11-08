/** Composed Workflow actor binding retains native source, actor, and closed-owner checks.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCommerceApplicationAssemblyV1}
 from '../../src/commerce/commerce-application-assembly-v1.ts';
import {produceCommerceAuthNativeOwnerV1}
 from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';
import {registerCommerceEntryFixtureActorV1}
 from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1}
 from '../support/commerce-auth-fixture-provider-v1.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 composed Workflow pass binds one native actor per checked scope and rejects foreign or closed actors',
 {skip:process.env.CRAFT_C14_PASS_ACTORS_RUN!=='1'},async()=>{
 const work=mkdtempSync(path.join('/var/tmp','craft-c14-pass-actors-'));
 let assembly,native,selected,pass;
 const actors=[];
 try{
  assembly=await createCommerceApplicationAssemblyV1(source,path.join(work,'generated'));
  for(const service of assembly.inspect().services)await assembly.openServiceStorage(service);
  native=await produceCommerceAuthNativeOwnerV1(path.join(work,'native-auth'));
  selected=await assembly.openSelectedEntryAuth(native);
  pass=assembly.openWorkflowPass('Orders.Checkout.Checkout');
  assert.equal(pass.inspect().qualification,
   'source-bounded-workflow-pass;vacant-and-quiescent-recovery');
  await assert.rejects(pass.runQuiescent('evt_'+('c'.repeat(64))),
   /whole-process reopen required/);
  const requirements=assembly.inspectWorkerActorRequirements('Orders.Checkout.Checkout');
  const routes=[...new Map(requirements.filter(row=>row.caller_service==='orders')
   .map(row=>[row.entry,{entry:row.entry,permission:row.auth_permission}])).values()];
  assert.ok(routes.length>4);
  assert.equal(new Set(routes.map(row=>row.permission.scope)).size,1);
  const scope=routes[0].permission.scope;
  const register=(subject,principal_kind,service_id)=>{
   const evidence=subject+'-evidence';
   const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,
    session:subject+'-session',valid_for_seconds:7200,routes});
   const actor=registerCommerceEntryFixtureActorV1(selected.auth,fixture.handle,
    {subject,evidence,principal_kind,service_id,scope});
   actors.push(actor);return actor;
  };
  const customer=register('pass-customer','customer',null);
  assert.throws(()=>pass.bindActor(customer),/native Workflow service actor required/);
  const foreign=register('pass-foreign','service','catalog');
  assert.throws(()=>pass.bindActor(foreign),/matches no selected Workflow Entry/);
  const first=register('pass-orders-one','service','orders');
  const assigned=pass.bindActor(first);
  assert.ok(assigned.includes('Orders.ConfirmOrderEntry'));
  assert.ok(assigned.includes('Orders.ClaimCheckoutWorkEntry'));
  const second=register('pass-orders-two','service','orders');
  assert.throws(()=>pass.bindActor(second),/actor cannot be replaced/);
  pass.close();
  assert.throws(()=>pass.bindActor(first),/Workflow pass closed/);
  await assert.rejects(pass.runQuiescent('evt_'+('c'.repeat(64))),/Workflow pass closed/);
 }finally{
  for(const actor of actors)try{selected?.auth.disposeActor(actor);}catch{}
  pass?.close();assembly?.close();await native?.dispose();
  rmSync(work,{recursive:true,force:true});
 }
});
