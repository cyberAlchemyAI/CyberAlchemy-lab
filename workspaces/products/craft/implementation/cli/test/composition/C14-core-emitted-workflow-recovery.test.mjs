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
const wireHeaders={'content-type':'application/json; charset=utf-8','demopay-protocol':'1'};
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
function provider(){
 const captured=new Map();
 return {async exchange(request){
  assert.equal(request.origin,'https://demopay.invalid');
  const input=JSON.parse(Buffer.from(request.body).toString('utf8'));
  const prior=captured.get(input.attemptKey);
  if(request.path==='/v1/capture/inspect'&&!prior)
   return {status:404,headers:wireHeaders,body:Buffer.from(JSON.stringify({...input,
    status:'UnknownKey',providerReference:null}))};
  assert.ok(request.path==='/v1/capture'||request.path==='/v1/capture/inspect');
  const result=prior??{...input,status:'Captured',providerReference:'receipt-'+input.attemptKey};
  captured.set(input.attemptKey,result);
  return {status:200,headers:wireHeaders,body:Buffer.from(JSON.stringify(result))};
 }};
}

test('C14 emitted application recovers a committed Workflow claim after whole-owner reopen',
 {skip:process.env.CRAFT_C14_EMITTED_RECOVERY_RUN!=='1'},async()=>{
 const work=mkdtempSync('/var/tmp/craft-c14-emitted-recovery-');
 const firstRoot=path.join(work,'first'),secondRoot=path.join(work,'reopened');
 const orderId='recovery-order-one',occurrenceId='evt_'+('d'.repeat(64));
 let first,reopened,native,selected,executor,session,app,successful=false;
 const actors=[];
 try{
  first=await createCoreCommerceServiceArtifactOwner(source,firstRoot);
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
   evidence:'recovery-claim-evidence',session:'recovery-claim-session',valid_for_seconds:43200,
   routes:[{entry:claimRequirement.entry,permission:claimRequirement.auth_permission}]});
  const claimActor=registerCommerceEntryFixtureActorV1(selected.auth,claimFixture.handle,
   {subject:'recovery-claim',evidence:'recovery-claim-evidence',principal_kind:'service',
    service_id:claimRequirement.caller_service,scope:claimRequirement.auth_permission.scope});
  executor=first.openWorkflowClaimExecutor(workflowId);
  assert.ok(executor.bindActor(claimActor).includes(claimRequirement.entry));
  const claimed=await executor.run(scheduled.claim);
  assert.equal(claimed.kind,'claimed-progress');
  session=claimed.session;
  const before=first.serviceStorage('orders').inspectStoredRecord('Orders.CheckoutProgress',0,{orderId});
  assert.equal(before.workerEpoch,1n);assert.equal(before.workerOwner.kind,'some');
  selected.auth.disposeActor(claimActor);session.dispose();session=undefined;
  executor.close();executor=undefined;first.close();first=undefined;
  const services=Object.fromEntries(['catalog','orders','payments','inventory','fulfillment']
   .map(id=>[id,{mode:'reopen',directory:path.join(firstRoot,'runtime',id)}]));
  reopened=await createCoreCommerceServiceArtifactOwner(source,secondRoot,{services});
  reopened.openDemoPayDispatch(provider());
  const generated=await import(pathToFileURL(path.join(secondRoot,'artifacts','application.mjs')).href);
  app=await generated.createGeneratedCommerceApplication(reopened,native);
  const requirements=app.inspectWorkerActorRequirements(workflowId);
  const groups=new Map();
  for(const requirement of requirements){
   const key=requirement.caller_service+'|'+requirement.auth_permission.scope;
   const group=groups.get(key)??[];group.push(requirement);groups.set(key,group);
  }
  for(const [index,group] of [...groups.values()].entries()){
   const subject='recovery-worker-'+index,evidence=subject+'-evidence';
   const routes=[...new Map(group.map(row=>[row.entry,
    {entry:row.entry,permission:row.auth_permission}])).values()];
   const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,
    session:subject+'-session',valid_for_seconds:43200,routes});
   const actor=registerCommerceEntryFixtureActorV1(app.auth,fixture.handle,{subject,evidence,
    principal_kind:'service',service_id:group[0].caller_service,
    scope:group[0].auth_permission.scope});
   actors.push(actor);app.bindWorkerActor(workflowId,actor);
  }
  const queryGroups=new Map();
  for(const requirement of app.serviceActorRequirements){
   const key=requirement.caller_service+'|'+requirement.scope;
   const group=queryGroups.get(key)??[];group.push(requirement);queryGroups.set(key,group);
  }
  for(const [index,group] of [...queryGroups.values()].entries()){
   const subject='recovery-query-'+index,evidence=subject+'-evidence';
   const routes=[...new Map(group.map(row=>[row.entry,
    {entry:row.entry,permission:row.permission}])).values()];
   const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,
    session:subject+'-session',valid_for_seconds:43200,routes});
   const actor=registerCommerceEntryFixtureActorV1(app.auth,fixture.handle,{subject,evidence,
    principal_kind:'service',service_id:group[0].caller_service,scope:group[0].scope});
   actors.push(actor);app.bindServiceActor(actor);
  }
  const recovered=await app.recoverWorkflow(workflowId,occurrenceId);
  assert.equal(recovered.kind,'cycle-result');
  assert.equal(recovered.result.kind,'finished',JSON.stringify(recovered.result));
  assert.equal(recovered.result.terminal,'confirmed');
  const after=reopened.serviceStorage('orders').inspectStoredRecord('Orders.CheckoutProgress',0,{orderId});
  assert.equal(after.workerEpoch,2n);
  assert.equal(reopened.serviceStorage('orders').inspectStoredRecord('Orders.Order',0,{id:orderId}).status,'Confirmed');
  assert.equal(reopened.serviceStorage('orders').countStoredRecords('Orders.OrderConfirmedOutbox'),1n);
  successful=true;
 }finally{
  for(const actor of actors)try{app?.auth.disposeActor(actor);}catch{}
  app?.close();session?.dispose();executor?.close();first?.close();reopened?.close();await native?.dispose();
  if(successful)rmSync(work,{recursive:true,force:true});
  else console.error('C14 emitted recovery diagnostic fixture retained at '+work);
 }
});
