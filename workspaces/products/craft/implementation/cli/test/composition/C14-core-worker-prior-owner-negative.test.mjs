import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner} from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');

test('C14 original WorkSchedule claim cannot reuse prior worker progress after ownership changes',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-prior-owner-'));
 let owner;
 try{
  owner=await createCoreCommerceServiceArtifactOwner(source,path.join(work,'generated'));
  const ordersRoot=path.join(work,'generated','runtime','orders');
  const component=await import(pathToFileURL(path.join(ordersRoot,'repository','service-repositories.js')).href);
  const physical=deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
  const orderId='stale-claim-order-one',occurrenceId='evt_'+('d'.repeat(64));
  const order={id:orderId,customerId:'customer-one',quoteId:'quote-one',currency:'USD',payableMinor:100n,
   lines:[{sku:'sku-one',quantity:1n}],status:'AwaitingStock',version:1n};
  const metadata={eventId:occurrenceId,producer:'orders',aggregateId:orderId,aggregateVersion:1n,
   ordinal:0n,correlationId:orderId,commandId:'cmd_stale_claim_one'};
  const outbox={eventId:occurrenceId,event:{metadata,orderId},state:'Ready',version:1n};
  const db=new DatabaseSync(path.join(ordersRoot,'store.sqlite'));
  try{
   for(const [entity,value] of [['Orders.Order',order],['Orders.OrderPlacedOutbox',outbox]]){
    const table=physical.tables.find(row=>row.entity===entity);
    assert.ok(table);
    db.prepare(table.insert_sql).run(...physical.encode(entity,value).bindings);
   }
  }finally{db.close();}
  const ingress=owner.openWorkflowIngress('Orders.Checkout.Checkout');
  assert.equal((await ingress.enqueue(occurrenceId)).kind,'enqueued');
  const scheduled=ingress.claim(occurrenceId);
  assert.equal(scheduled.kind,'claimed');
  const progress={orderId,state:'AwaitingStock',reserveCommandId:'cmd_stale_reserve_one',
   captureAttemptKey:'cmd_stale_capture_one',allocateCommandId:'cmd_stale_allocate_one',
   releaseCommandId:'cmd_stale_release_one',confirmCommandId:'cmd_stale_confirm_one',
   cancelCommandId:'cmd_stale_cancel_one',reserveResult:{kind:'none'},reserveRejected:{kind:'none'},
   paymentResult:{kind:'none'},allocationResult:{kind:'none'},releaseResult:{kind:'none'},
   captureDispatched:false,workerOwner:{kind:'some',value:'another-worker'},workerEpoch:1n,version:2n};
  const progressTable=physical.tables.find(row=>row.entity==='Orders.CheckoutProgress');
  assert.ok(progressTable);
  const progressDb=new DatabaseSync(path.join(ordersRoot,'store.sqlite'));
  try{progressDb.prepare(progressTable.insert_sql).run(...physical.encode('Orders.CheckoutProgress',progress).bindings);}
  finally{progressDb.close();}
  assert.deepEqual(ingress.inspectClaimInput(scheduled.claim),
   {kind:'not-ready',reason:'prior-owner-changed',authority_effect:'none'});
  assert.throws(()=>ingress.inspectClaimInput({...scheduled.claim}),/ForeignOwner|original committed/i);
 }finally{owner?.close();rmSync(work,{recursive:true,force:true});}
});
