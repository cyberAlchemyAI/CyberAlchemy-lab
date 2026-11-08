/** A committed generated claim survives owner termination and is resumed by
 * the emitted application, with a fresh native service actor and fenced epoch.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner}
 from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {createCommerceTestAuthNativeV1}
 from '../support/commerce-auth-native-variant-v1.ts';
import {registerCommerceEntryFixtureActorV1}
 from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1}
 from '../support/commerce-auth-fixture-provider-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1}
 from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
const workflowId='Orders.Checkout.Checkout';
function insert(root,service,physical,entity,value){
 const table=physical.tables.find(row=>row.entity===entity);assert.ok(table,entity);
 const db=new DatabaseSync(path.join(root,'runtime',service,'store.sqlite'));
 try{db.prepare(table.insert_sql).run(...physical.encode(entity,value).bindings);}finally{db.close();}
}
async function physical(root,service){
 const component=await import(pathToFileURL(path.join(root,'runtime',service,
  'repository','service-repositories.js')).href);
 return deriveCommerceSqlitePhysicalLayoutV1(component.commerceRepositoryData);
}
test('C14 cached step identity rechecks exact source handles and actual same-version snapshot contents',async()=>{
 const work=mkdtempSync('/var/tmp/craft-c14-identity-currentness-');
 const firstRoot=path.join(work,'first');
 const orderId='identity-order-one',occurrenceId='evt_'+('c'.repeat(64));
 let first,native,selected,executor,session,snapshotter,witness,otherWitness,continuation,prepared;
 const actors=[];let successful=false;const started=Date.now(),phase=name=>console.error('C14 cached identity phase='+name+' elapsed_s='+Math.round((Date.now()-started)/1000));
 try{
  first=await createCoreCommerceServiceArtifactOwner(source,firstRoot);
  phase('generated');
  const orders=await physical(firstRoot,'orders'),inventory=await physical(firstRoot,'inventory');
  const order={id:orderId,customerId:'recovery-customer',quoteId:'recovery-quote',
   currency:'USD',payableMinor:100n,lines:[{sku:'recovery-sku',quantity:1n}],
   status:'AwaitingStock',version:1n};
  const progress={orderId,state:'AwaitingStock',reserveCommandId:'cmd_recovery_reserve',
   captureAttemptKey:'cmd_recovery_capture',allocateCommandId:'cmd_recovery_allocate',
   releaseCommandId:'cmd_recovery_release',confirmCommandId:'cmd_recovery_confirm',
   cancelCommandId:'cmd_recovery_cancel',reserveResult:{kind:'none'},
   reserveRejected:{kind:'none'},paymentResult:{kind:'none'},allocationResult:{kind:'none'},
   releaseResult:{kind:'none'},captureDispatched:false,workerOwner:{kind:'none'},
   workerEpoch:0n,version:1n};
  const metadata={eventId:occurrenceId,producer:'orders',aggregateId:orderId,
   aggregateVersion:1n,ordinal:0n,correlationId:orderId,commandId:'cmd_recovery_place'};
  const outbox={eventId:occurrenceId,event:{metadata,orderId},state:'Ready',version:1n};
  insert(firstRoot,'orders',orders,'Orders.Order',order);
  insert(firstRoot,'orders',orders,'Orders.CheckoutProgress',progress);
  insert(firstRoot,'orders',orders,'Orders.OrderPlacedOutbox',outbox);
  insert(firstRoot,'inventory',inventory,'Inventory.Stock',{
   sku:'recovery-sku',onHand:20n,reserved:0n,allocated:0n,version:1n});
  const ingress=first.openWorkflowIngress(workflowId);
  assert.equal((await ingress.enqueue(occurrenceId)).kind,'enqueued');
  const scheduled=ingress.claim(occurrenceId);assert.equal(scheduled.kind,'claimed');
  native=await createCommerceTestAuthNativeV1(path.join(work,'auth'));
  selected=await first.openSelectedEntryAuth(native);
  const claimRequirement=first.inspectWorkerActorRequirements(workflowId)
   .find(row=>row.usage==='claim');assert.ok(claimRequirement);
  const claimFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'recovery-claim',
   evidence:'recovery-claim-evidence',session:'recovery-claim-session',valid_for_seconds:7200,
   routes:[{entry:claimRequirement.entry,permission:claimRequirement.auth_permission}]});
  const claimActor=registerCommerceEntryFixtureActorV1(selected.auth,claimFixture.handle,
   {subject:'recovery-claim',evidence:'recovery-claim-evidence',principal_kind:'service',
    service_id:claimRequirement.caller_service,scope:claimRequirement.auth_permission.scope});
  executor=first.openWorkflowClaimExecutor(workflowId);
  assert.ok(executor.bindActor(claimActor).includes(claimRequirement.entry));
  const claimed=await executor.run(scheduled.claim);
  assert.equal(claimed.kind,'claimed-progress');
  session=claimed.session;phase('claimed');
  const before=first.serviceStorage('orders').inspectStoredRecord('Orders.CheckoutProgress',0,{orderId});
  assert.equal(before.workerEpoch,1n);assert.equal(before.workerOwner.kind,'some');

  actors.push(claimActor);
  const snapshotRequirement=first.inspectWorkerActorRequirements(workflowId).find(row=>row.usage==='snapshot');assert.ok(snapshotRequirement);
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'identity-snapshot',evidence:'identity-snapshot-evidence',session:'identity-snapshot-session',valid_for_seconds:7200,routes:[{entry:snapshotRequirement.entry,permission:snapshotRequirement.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(selected.auth,fixture.handle,{subject:'identity-snapshot',evidence:'identity-snapshot-evidence',principal_kind:'service',service_id:snapshotRequirement.caller_service,scope:snapshotRequirement.auth_permission.scope});actors.push(actor);
  snapshotter=first.openWorkflowSnapshotQuery(workflowId);snapshotter.bindActor(actor);
  witness=await snapshotter.run(session);assert.equal(witness.kind,'snapshot');phase('snapshot');
  continuation=first.openWorkflowContinuation(workflowId);prepared=await continuation.prepareNext(session,witness);assert.equal(prepared.kind,'prepared-step');phase('prepared');
  const identity=prepared.identities.recheck(prepared.identity);
  assert.equal(identity,prepared.identity_inspection);
  assert.equal(prepared.identities.hasExactSourceHandles(prepared.identity,prepared.resumes,prepared.selection,witness.snapshots,witness.handle),true);
  assert.equal(prepared.identities.hasExactSourceHandles(prepared.identity,prepared.resumes,prepared.selection,witness.snapshots,{...witness.handle}),false);
  assert.throws(()=>prepared.identities.hasExactSourceHandles({...prepared.identity},prepared.resumes,prepared.selection,witness.snapshots,witness.handle),error=>error?.code==='ForeignOwner');
  otherWitness=await snapshotter.run(session);assert.equal(otherWitness.kind,'snapshot');
  assert.deepEqual(otherWitness.inspection.value,witness.inspection.value);
  assert.equal(prepared.identities.hasExactSourceHandles(prepared.identity,prepared.resumes,prepared.selection,otherWitness.snapshots,otherWitness.handle),false,'matching genuine snapshots do not share custody');
  await Promise.resolve();
  assert.equal(prepared.identities.recheck(prepared.identity),identity,'immutable data can be reused only after actual freshness checks');
  const table=orders.tables.find(row=>row.entity==='Orders.Order');assert.ok(table);
  const db=new DatabaseSync(path.join(firstRoot,'runtime/orders/store.sqlite'));
  try{db.prepare(table.insert_sql.replace(/^INSERT INTO /,'INSERT OR REPLACE INTO ')).run(...orders.encode(table.entity,{...order,payableMinor:101n}).bindings);}finally{db.close();}
  const actual=first.serviceStorage('orders').inspectStoredRecord('Orders.Order',0,{id:orderId});assert.equal(actual.version,order.version);assert.equal(actual.payableMinor,101n);
  assert.throws(()=>prepared.identities.recheck(prepared.identity),error=>error?.code==='StaleSnapshot','same domain version cannot conceal changed original snapshot data');
  phase('same-version-mutation-rejected');successful=true;
 }finally{
  prepared?.dispose?.();continuation?.close();otherWitness?.dispose?.();witness?.dispose?.();snapshotter?.close();session?.dispose();executor?.close();
  for(const actor of actors)try{selected?.auth.disposeActor(actor);}catch{}
  first?.close();await native?.dispose();
  if(successful)rmSync(work,{recursive:true,force:true});else console.error('identity currentness fixture retained at '+work);
 }
});
