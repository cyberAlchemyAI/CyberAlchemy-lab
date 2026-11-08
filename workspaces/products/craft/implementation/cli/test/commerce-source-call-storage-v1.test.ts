/** Selected application Entry to a source-derived local transaction handle. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCommerceApplicationAssemblyV1} from '../src/commerce/commerce-application-assembly-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSourceCallStorageOwnerV1,assertCommerceSourceCallStorageOwnerV1} from '../src/commerce/commerce-source-call-storage-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('selected Payment Entry derives exact local MarkDispatched source program without effect authority',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-source-call-storage-'));
 let app:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined,native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined,bridge:ReturnType<typeof createCommerceSourceCallStorageOwnerV1>|undefined;
 try{
  app=await createCommerceApplicationAssemblyV1(candidate,path.join(root,'application'));
  const storage=await app.openServiceStorage('payments');
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  const {auth,entries}=await app.openSelectedEntryAuth(native);
  bridge=createCommerceSourceCallStorageOwnerV1(entries,storage);assertCommerceSourceCallStorageOwnerV1(bridge);
  const entryId='Payments.CapturePaymentEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='service-'+definition.access.caller,evidence='source-call-storage-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'source-call-storage-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'},wire=Buffer.from(JSON.stringify(input,(_key,value)=>typeof value==='bigint'?String(value):value));
  const started=await entries.begin(actor,entryId,wire,input);assert.equal(started.ok,true,JSON.stringify(started));if(!started.ok)return;
  const argumentsForChild={orderId:'order-one',attemptKey:'attempt-one',requestFingerprint:'a'.repeat(64)};
  await assert.rejects(bridge.derive(started.invocation,'Payments.NoSuchLocalCall',argumentsForChild,'MarkDispatched'),code('MissingMapping'));
  await assert.rejects(bridge.derive(started.invocation,'Payments.DispatchOriginalCapture',argumentsForChild,'NoSuchTransaction'),code('UnknownReference'));
  const local=await bridge.derive(started.invocation,'Payments.DispatchOriginalCapture',argumentsForChild,'MarkDispatched'),inspection=bridge.inspect(local);
  assert.equal(inspection.root_entry,entryId);assert.equal(inspection.operation,'Payments.DispatchOriginalCapture');assert.equal(inspection.transaction,'MarkDispatched');assert.equal(inspection.service,'payments');
  assert.equal(inspection.qualification,'original-selected-local-source-transaction-only;command-and-quiescence-required');
  assert.throws(()=>bridge!.inspect({...local}),code('ForeignOwner'));
  assert.throws(()=>storage.apply(local as any,{logicalEntryId:entryId,principalId:subject,commandId:'not-issued',fingerprint:'a'.repeat(64),transactionNamespace:'1'.repeat(64)},{}),code('ForeignOwner'));
  bridge.retire(local);assert.throws(()=>bridge!.inspect(local),code('ForeignOwner'));
  entries.retire(started.invocation);auth.disposeActor(actor);auth.disposeEntry(entry);
 }finally{bridge?.dispose();app?.close();await native?.dispose();rmSync(root,{recursive:true,force:true});}
});
