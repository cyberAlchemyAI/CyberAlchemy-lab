/** Genuine local marker -> fresh acknowledged successor -> native Prepared journal.
 * Initial domain rows are schema-bound test fixtures; all claim, observation,
 * selection and mutation behavior comes from the original source/generated code.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createCoreCommerceServiceArtifactOwner} from '../../src/generic/core-commerce-service-artifact-owner.ts';
import {createCommerceTestAuthNativeV1} from '../support/commerce-auth-native-variant-v1.ts';
import {registerCommerceEntryFixtureActorV1} from '../../src/commerce/commerce-entry-context-v1.ts';
import {seedCommerceAuthFixtureDatabaseV1} from '../support/commerce-auth-fixture-provider-v1.ts';
import {deriveCommerceSqlitePhysicalLayoutV1} from '../../profiles/commerce-local-v1-candidate/runtime/sqlite-physical-layout.ts';
import {disposeCommerceWorkflowFreshLocalSuccessorV1} from '../../src/commerce/commerce-workflow-fresh-local-successor-v1.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'examples/ecommerce-target-candidate');
const workflowId='Orders.Checkout.Checkout';
const services=['catalog','orders','payments','inventory','fulfillment'];
function insert(root,layout,entity,value){
 const table=layout.tables.find(row=>row.entity===entity);assert.ok(table,entity);
 const db=new DatabaseSync(path.join(root,'runtime/orders/store.sqlite'));
 try{db.prepare(table.insert_sql).run(...layout.encode(entity,value).bindings);}finally{db.close();}
}
function mutateSameVersion(root,layout,entity,original,changes){
 const table=layout.tables.find(row=>row.entity===entity);assert.ok(table);
 const next={...original,...changes};assert.equal(next.version,original.version);
 const old=layout.encode(entity,original),replacement=layout.encode(entity,next);
 const names=[...table.columns.map(column=>column.sql_name),'_craft_row',...table.keys.map((_,index)=>'_craft_key_'+index)];
 const q=name=>'"'+name.replaceAll('"','""')+'"';
 const sql='UPDATE '+q(table.physical_name)+' SET '+names.map(name=>q(name)+'=?').join(',')+' WHERE '+q('_craft_key_0')+'=?';
 const db=new DatabaseSync(path.join(root,'runtime/orders/store.sqlite'));
 try{assert.equal(db.prepare(sql).run(...replacement.bindings,old.bindings[table.columns.length+1]).changes,1);}finally{db.close();}
}
async function layout(root){
 const module=await import(pathToFileURL(path.join(root,'runtime/orders/repository/service-repositories.js')).href);
 return deriveCommerceSqlitePhysicalLayoutV1(module.commerceRepositoryData);
}
function seed(root,physical,index){
 const orderId='fresh-local-order-'+index,occurrenceId='evt_'+String(index).repeat(64),reserveCommandId='cmd_local_reserve_'+index;
 const lines=[{sku:'fresh-local-sku-'+index,quantity:1n}];
 const reservation={reservationId:'fresh-local-reservation-'+index,orderId,lines,linesFingerprint:'a'.repeat(64),reserveCommandId,lastCommandId:reserveCommandId,status:'Reserved',version:1n};
 const order={id:orderId,customerId:'fresh-local-customer',quoteId:'fresh-local-quote-'+index,currency:'USD',payableMinor:100n,lines,status:'AwaitingPayment',version:2n};
 const progress={orderId,state:'AwaitingPayment',reserveCommandId,captureAttemptKey:'cmd_local_capture_'+index,allocateCommandId:'cmd_local_allocate_'+index,releaseCommandId:'cmd_local_release_'+index,confirmCommandId:'cmd_local_confirm_'+index,cancelCommandId:'cmd_local_cancel_'+index,reserveResult:{kind:'some',value:reservation},reserveRejected:{kind:'none'},paymentResult:{kind:'none'},allocationResult:{kind:'none'},releaseResult:{kind:'none'},captureDispatched:false,workerOwner:{kind:'none'},workerEpoch:0n,version:2n};
 const metadata={eventId:occurrenceId,producer:'orders',aggregateId:orderId,aggregateVersion:1n,ordinal:0n,correlationId:orderId,commandId:'cmd_local_place_'+index};
 for(const [entity,value]of [['Orders.Order',order],['Orders.CheckoutProgress',progress],['Orders.OrderPlacedOutbox',{eventId:occurrenceId,event:{metadata,orderId},state:'Ready',version:1n}]])insert(root,physical,entity,value);
 return {orderId,occurrenceId,captureAttemptKey:progress.captureAttemptKey};
}
function register(owner,auth,native,label,usages){
 const requirements=owner.inspectWorkerActorRequirements(workflowId).filter(row=>usages.includes(row.usage));
 const groups=new Map();for(const requirement of requirements){const key=requirement.caller_service+'|'+requirement.auth_permission.scope;const group=groups.get(key)??[];group.push(requirement);groups.set(key,group);}
 return [...groups.values()].map((group,index)=>{
  const subject=label+'-'+index,evidence=subject+'-evidence';
  const routes=[...new Map(group.map(row=>[row.entry,{entry:row.entry,permission:row.auth_permission}])).values()];
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:subject+'-session',valid_for_seconds:14400,routes});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:group[0].caller_service,scope:group[0].auth_permission.scope});
  return {auth,actor};
 });
}

// Each expensive marker scenario receives a fresh genuine native Auth fixture.
// The private fixture covers the long generated replay; product Auth expiry is unchanged.
async function harness(count,label){
 const h={work:mkdtempSync('/var/tmp/craft-c14-fresh-local-'),actors:[],sessions:[],witnesses:[],prepared:[],successors:[],providerCalls:0};
 h.firstRoot=path.join(h.work,'first');
 try{
  h.owner=await createCoreCommerceServiceArtifactOwner(source,h.firstRoot);
  h.physical=await layout(h.firstRoot);h.rows=Array.from({length:count},(_,index)=>seed(h.firstRoot,h.physical,index+1));
  console.error('C14 fresh local '+label+': original five-service assembly and AwaitingPayment fixtures ready');
  h.owner.openDemoPayDispatch({async exchange(){h.providerCalls++;throw new Error('local continuation test forbids provider dispatch');}});
  h.native=await createCommerceTestAuthNativeV1(path.join(h.work,'auth'));h.selected=await h.owner.openSelectedEntryAuth(h.native);
  const registered=register(h.owner,h.selected.auth,h.native,'fresh-local-'+label,['claim','snapshot','observation']);h.actors.push(...registered);
  h.executor=h.owner.openWorkflowClaimExecutor(workflowId);h.snapshots=h.owner.openWorkflowSnapshotQuery(workflowId);h.local=h.owner.openWorkflowLocalObservationRunner(workflowId);h.continuation=h.owner.openWorkflowContinuation(workflowId);
  for(const {actor}of registered){h.executor.bindActor(actor);h.snapshots.bindActor(actor);h.local.bindActor(actor);}
  const ingress=h.owner.openWorkflowIngress(workflowId);
  for(const row of h.rows){
   assert.equal((await ingress.enqueue(row.occurrenceId)).kind,'enqueued');
   const scheduled=ingress.claim(row.occurrenceId);assert.equal(scheduled.kind,'claimed');
   const claimed=await h.executor.run(scheduled.claim);assert.equal(claimed.kind,'claimed-progress');h.sessions.push(claimed.session);
   const snapshot=await h.snapshots.run(claimed.session);assert.equal(snapshot.kind,'snapshot');h.witnesses.push(snapshot);
   assert.equal(snapshot.inspection.value.progress.captureDispatched,false);
  }
  console.error('C14 fresh local '+label+': original generated worker claims and snapshots ready');return h;
 }catch(error){await cleanup(h,false);throw error;}
}
function releaseHandles(h){
 for(const value of h.prepared)value.dispose();h.prepared.length=0;
 for(const value of h.witnesses)value.dispose();h.witnesses.length=0;
 for(const value of h.sessions)value.dispose();h.sessions.length=0;
}
function closeOriginalOwner(h){
 h.local?.close();h.local=undefined;h.continuation?.close();h.continuation=undefined;
 h.snapshots?.close();h.snapshots=undefined;h.executor?.close();h.executor=undefined;
 for(const {auth,actor}of h.actors)try{auth.disposeActor(actor);}catch{}h.actors.length=0;
 h.owner?.close();h.owner=undefined;
}
async function cleanup(h,completed){
 for(const value of h.prepared)try{value.dispose();}catch{}
 for(const value of h.witnesses)try{value.dispose();}catch{}
 for(const value of h.sessions)try{value.dispose();}catch{}
 for(const value of h.successors)try{disposeCommerceWorkflowFreshLocalSuccessorV1(value);}catch{}
 closeOriginalOwner(h);await h.native?.dispose();
 if(completed)rmSync(h.work,{recursive:true,force:true});else console.error('C14 fresh-local diagnostic fixture retained at '+h.work);
}
function assertNoPaymentEffects(h){assert.equal(h.providerCalls,0);assert.equal(h.owner.serviceStorage('payments').countStoredRecords('Payments.PaymentAttempt'),0n);}

test('C14 fresh generated local acknowledgement selects capture once; forged, cloned, foreign and reused continuations cannot',async()=>{
 const h=await harness(2,'custody');let completed=false;
 try{
  console.error('C14 fresh local custody: starting original generated local marker');
  const observed=await h.local.run(h.sessions[0],h.witnesses[0]);assert.equal(observed.kind,'observed',JSON.stringify(observed));assert.equal(observed.next,'capture');assert.equal(observed.commits,1);assert.ok(observed.successor);h.successors.push(observed.successor);
  h.witnesses[0].dispose();const fresh=await h.snapshots.run(h.sessions[0]);assert.equal(fresh.kind,'snapshot');h.witnesses.push(fresh);
  assert.equal(fresh.inspection.value.progress.captureDispatched,true);assert.equal(fresh.inspection.value.progress.version,4n);assert.equal(fresh.inspection.value.order.version,3n);assert.equal(fresh.inspection.value.progress.state,'AwaitingPayment');
  assert.equal(h.sessions[0].context.provesNeverDispatched(h.rows[0].captureAttemptKey),false,'fresh acknowledgement must not change conservative native never-dispatched proof');
  await assert.rejects(h.continuation.prepareNext(h.sessions[0],fresh,{}));
  await assert.rejects(h.continuation.prepareNext(h.sessions[0],fresh,{...observed.successor}));
  await assert.rejects(h.continuation.prepareNext(h.sessions[1],h.witnesses[1],observed.successor));
  const next=await h.continuation.prepareNext(h.sessions[0],fresh,observed.successor);assert.equal(next.kind,'prepared-step');h.prepared.push(next);
  assert.deepEqual(next.decision.action,{kind:'step',target:'capture'});assert.equal(next.identity_inspection.target_entry_id,'Payments.CapturePaymentEntry');assert.equal(next.identity_inspection.command_id,h.rows[0].captureAttemptKey);
  assert.equal(h.owner.serviceStorage('orders').inspectWorkflowStepJournal(next.journal).phase,'Prepared');
  await assert.rejects(h.continuation.prepareNext(h.sessions[0],fresh,observed.successor));assertNoPaymentEffects(h);
  console.error('C14 fresh local custody: genuine successor prepared capture once; fake/clone/foreign/reused handles rejected');completed=true;
 }finally{await cleanup(h,completed);}
});

test('C14 a fresh local successor rejects same-version row changes; whole-owner reopen without its ticket selects reconciliation',async()=>{
 const h=await harness(1,'stale-reopen');let completed=false;
 try{
  console.error('C14 fresh local stale-reopen: starting independently authorized original generated local marker');
  const observed=await h.local.run(h.sessions[0],h.witnesses[0]);assert.equal(observed.kind,'observed',JSON.stringify(observed));assert.equal(observed.next,'capture');assert.equal(observed.commits,1);assert.ok(observed.successor);h.successors.push(observed.successor);h.witnesses[0].dispose();
  const current=h.owner.serviceStorage('orders').inspectStoredRecord('Orders.CheckoutProgress',0,{orderId:h.rows[0].orderId});assert.equal(current.captureDispatched,true);assert.equal(current.version,4n);
  mutateSameVersion(h.firstRoot,h.physical,'Orders.CheckoutProgress',current,{releaseCommandId:'changed-same-version-release'});
  const changed=await h.snapshots.run(h.sessions[0]);assert.equal(changed.kind,'snapshot');h.witnesses.push(changed);
  assert.equal(changed.inspection.value.progress.version,current.version);assert.equal(changed.inspection.value.progress.releaseCommandId,'changed-same-version-release');
  await assert.rejects(h.continuation.prepareNext(h.sessions[0],changed,observed.successor));
  disposeCommerceWorkflowFreshLocalSuccessorV1(observed.successor);disposeCommerceWorkflowFreshLocalSuccessorV1(observed.successor);assertNoPaymentEffects(h);
  console.error('C14 fresh local stale-reopen: actual same-version stored-row change rejects stale successor');
  releaseHandles(h);closeOriginalOwner(h);
  h.owner=await createCoreCommerceServiceArtifactOwner(source,path.join(h.work,'reopened'),{services:Object.fromEntries(services.map(service=>[service,{mode:'reopen',directory:path.join(h.firstRoot,'runtime',service)}]))});
  const selected=await h.owner.openSelectedEntryAuth(h.native),freshActors=register(h.owner,selected.auth,h.native,'fresh-local-reopened',['claim','snapshot']);h.actors.push(...freshActors);
  h.executor=h.owner.openWorkflowClaimExecutor(workflowId);h.snapshots=h.owner.openWorkflowSnapshotQuery(workflowId);h.continuation=h.owner.openWorkflowContinuation(workflowId);
  for(const {actor}of freshActors){h.executor.bindActor(actor);h.snapshots.bindActor(actor);}
  const reclaimed=h.owner.openWorkflowIngress(workflowId).reclaimQuiescent(h.rows[0].occurrenceId);assert.equal(reclaimed.kind,'claimed');
  const claimed=await h.executor.run(reclaimed.claim);assert.equal(claimed.kind,'claimed-progress');h.sessions.push(claimed.session);
  const afterReopen=await h.snapshots.run(claimed.session);assert.equal(afterReopen.kind,'snapshot');h.witnesses.push(afterReopen);assert.equal(afterReopen.inspection.value.progress.captureDispatched,true);assert.equal(afterReopen.inspection.value.progress.workerEpoch,2n);assert.equal(afterReopen.inspection.value.progress.version,5n);
  assert.equal(claimed.session.context.provesNeverDispatched(h.rows[0].captureAttemptKey),false);
  const recovered=await h.continuation.prepareNext(claimed.session,afterReopen);assert.equal(recovered.kind,'prepared-step');h.prepared.push(recovered);
  assert.deepEqual(recovered.decision.action,{kind:'step',target:'reconcile-payment'});assert.equal(recovered.identity_inspection.target_entry_id,'Payments.ReconcilePaymentEntry');assertNoPaymentEffects(h);
  console.error('C14 fresh local stale-reopen: whole-owner reopen without a fresh ticket selects original payment inspection');completed=true;
 }finally{await cleanup(h,completed);}
});
