/** Source/profile selection and a real service store share one application owner. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCommerceApplicationAssemblyV1,assertCommerceApplicationAssemblyV1} from '../src/commerce/commerce-application-assembly-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('one source-selected assembly owns storage and rejects a direct protected Payment entry',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-application-assembly-'));
 let owner:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined;
 let native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined;
 try{
  await assert.rejects(createCommerceApplicationAssemblyV1(candidate,path.join(candidate,'generated')),code('InvalidContract'));
  owner=await createCommerceApplicationAssemblyV1(candidate,path.join(root,'generated'));
  assertCommerceApplicationAssemblyV1(owner);
  const view=owner.inspect();
  assert.equal(view.application,'Shop.Application.Ecommerce');
  assert.equal(view.services.length,5);
  assert.ok(view.services.includes('payments'));
  assert.equal(view.native_basis_qualified,false);
  assert.equal(view.bound_application_qualified,false);
  assert.throws(()=>assertCommerceApplicationAssemblyV1({...owner}),code('ForeignOwner'));
  await assert.rejects(owner.openServiceStorage('unknown'),code('ForeignOwner'));
  const providerPort={async exchange(){throw new Error('provider port must not be used by the assembly test');}};
  assert.throws(()=>owner.openDemoPayDispatch(providerPort),code('InvalidContract'));
  const storage=await owner.openServiceStorage('payments');
  assert.equal(storage.inspect().service,'payments');
  assert.equal(storage.inspect().source_capture_sha256,view.source_capture_sha256);
  assert.equal(storage.inspect().family_sha256,view.family_sha256);
  await assert.rejects(owner.openServiceStorage('payments'),code('InvalidContract'));
  const dispatch=owner.openDemoPayDispatch(providerPort);
  dispatch.assertCurrent();
  assert.throws(()=>owner.openDemoPayDispatch(providerPort),code('InvalidContract'));
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  const selected=await owner.openSelectedEntryAuth(native);
  assert.equal(selected.entries.inspect().source_capture_sha256,view.source_capture_sha256);
  assert.equal(selected.entries.inspect().family_sha256,view.family_sha256);
  assert.equal(selected.auth.inspect().source_sha256,view.source_capture_sha256);
  await assert.rejects(owner.openSelectedEntryAuth(native),code('InvalidContract'));
  await assert.rejects(owner.openGeneratedOperation({kind:'forged'} as any),code('ForeignOwner'));
  const entryId='Payments.CapturePaymentEntry',entry=selected.auth.bindEntry(entryId),definition=selected.auth.inspectEntry(entry);
  const subject='service-'+definition.access.caller,evidence='assembly-payment-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'assembly-payment-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(selected.auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  try{
   const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'};
   const wire=Buffer.from(JSON.stringify(input,(_key,value)=>typeof value==='bigint'?String(value):value));
   const started=await selected.entries.begin(actor,entryId,wire,input);
   assert.deepEqual(started,{ok:false,code:'forbidden',status:403});
  }finally{selected.auth.disposeActor(actor);selected.auth.disposeEntry(entry);}
  owner.assertCurrent();
  owner.close();
  assert.throws(()=>owner!.inspect(),code('DisposedOwner'));
 }finally{owner?.close();await native?.dispose();rmSync(root,{recursive:true,force:true});}
});
