/** Inventory's selected Entry requires an original Orders workflow call.
 * Decoded request arguments and a valid service actor cannot replace it. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCommerceApplicationAssemblyV1} from '../src/commerce/commerce-application-assembly-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const json=(value:unknown)=>JSON.stringify(value,(_key,member)=>typeof member==='bigint'?member.toString():member);

test('Inventory ReserveStock rejects a missing original Orders causal call before effects',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-inventory-reserve-'));
 let application:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined;
 let native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined;
 try{
  application=await createCommerceApplicationAssemblyV1(candidate,path.join(root,'generated'));
  const storage=await application.openServiceStorage('inventory');
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  const {auth,entries}=await application.openSelectedEntryAuth(native);
  const entryId='Inventory.ReserveStockEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry);
  const subject='service-'+definition.access.caller,evidence='inventory-reserve-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'inventory-reserve-session',
   routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',
   service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  try{
   const input={orderId:'order-unavailable',commandId:'reserve-unavailable',lines:[{sku:'sku-unavailable',quantity:2n}]};
   const started=await entries.begin(actor,entryId,Buffer.from(json(input)),input);
   assert.deepEqual(started,{ok:false,code:'forbidden',status:403},
    'decoded Inventory arguments cannot substitute for the Orders workflow step journal');
   assert.equal(storage.inspectStoredRecord('Inventory.StockCommandRecord',0,{commandId:input.commandId}),null);
   assert.equal(storage.inspectStoredRecord('Inventory.Reservation',1,{orderId:input.orderId}),null);
  }finally{auth.disposeActor(actor);auth.disposeEntry(entry);}
 }finally{application?.close();await native?.dispose();rmSync(root,{recursive:true,force:true});}
});
