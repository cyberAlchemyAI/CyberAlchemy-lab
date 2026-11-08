/** C12 generated Event handoff witness. This stays red until the selected
 * V4 public generation and original relay/receiver owners implement the
 * frozen event-handoff-contract-003 behavior. No test callback maps payloads,
 * creates an Event envelope, supplies a receiver actor, or writes SQL.
 * Open Questions: implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C12/event-handoff-contract-003/CONTRACT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {buildEventSourceFixture} from './C12-source-fixture.mjs';

const wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const trace=(name,stage)=>{if(process.env.C12_TRACE==='1')process.stderr.write(`[C12 ${name}] ${stage}\n`);};
const privateInboxSelect=/^SELECT\s+\*\s+FROM\s+_craft_event_inbox_v1\s+WHERE\s+occurrence_sha256\s*=\s*\?$/i;
function withAdvancedClock(offsetMs,work){
 const actual=Date.now;
 Date.now=()=>actual()+offsetMs;
 try{return work();}finally{Date.now=actual;}
}
async function watchPrivateInboxSelect(work,{reject}={reject:false}){
 const descriptor=Object.getOwnPropertyDescriptor(DatabaseSync.prototype,'prepare');
 assert.ok(descriptor?.value&&descriptor.configurable);
 let reads=0;
 Object.defineProperty(DatabaseSync.prototype,'prepare',{...descriptor,value:function(sql,...args){
  if(typeof sql==='string'&&privateInboxSelect.test(sql.trim())){
   reads++;
   if(reject)throw Error('C12_PRIVATE_INBOX_SELECTED_BEFORE_AUTH');
  }
  return Reflect.apply(descriptor.value,this,[sql,...args]);
 }});
 try{return {result:await work(),reads:()=>reads};}
 finally{Object.defineProperty(DatabaseSync.prototype,'prepare',descriptor);}
}
const cases=[
 {name:'Request to Audit',producer:'RequestService',consumer:'AuditService',producerFile:'request-service.alch',consumerFile:'audit-service.alch',
  producerEntry:'RequestService.ApproveRequestEntry',readEntry:'RequestService.ReadRequestEntry',receiverEntry:'AuditService.RecordApprovedEntry',
  producerEntity:'RequestService.Request',consumerEntity:'AuditService.AuditRecord',selector:'RequestService.RequestApproved',
  id:'R-001',initialState:'Draft',finalState:'Approved',auditId:'audit-R-001',decision:'Approved'},
 {name:'Permit to Ledger',producer:'PermitService',consumer:'LedgerService',producerFile:'permit-service.alch',consumerFile:'ledger-service.alch',
  producerEntry:'PermitService.GrantPermitEntry',readEntry:'PermitService.ReadPermitEntry',receiverEntry:'LedgerService.RecordGrantedEntry',
  producerEntity:'PermitService.Permit',consumerEntity:'LedgerService.LedgerRecord',selector:'PermitService.PermitGranted',
  id:'P-007',initialState:'Pending',finalState:'Granted',auditId:'ledger-P-007',decision:'Granted'},
];

function observe(storePath){
 const db=new DatabaseSync(storePath,{readOnly:true});
 try{
  const tableRows=db.prepare("SELECT name FROM sqlite_schema WHERE type='table' AND name LIKE 'craft_%' ORDER BY name").all();
  const business=tableRows.map(({name})=>{
   assert.match(name,/^craft_[0-9a-f_]+$/);
   return db.prepare(`SELECT _craft_row FROM "${name}" ORDER BY rowid`).all().map(row=>JSON.parse(Buffer.from(row._craft_row).toString('utf8')));
  });
  const journal=db.prepare('SELECT tuple_sha256,result_sha256 FROM _craft_generic_commands_v1 ORDER BY rowid').all();
  const outbox=db.prepare('SELECT occurrence_sha256,causal_command_tuple_sha256,producer_namespace,event_selector,event_version,emission_ordinal,target_service,target_entry,route,payload_sha256,payload_bytes,state,fence,lease_until_ms FROM _craft_event_outbox_v1 ORDER BY rowid').all();
  const inbox=db.prepare('SELECT occurrence_sha256,envelope_sha256,consumer_command_tuple_sha256 FROM _craft_event_inbox_v1 ORDER BY rowid').all();
  return {business,journal,outbox,inbox};
 }finally{db.close();}
}

/** Independent implementation of PROFILE-SELECTION.json's byte oracle. */
function occurrence(producer,causal,selector,version,ordinal){
 const members=[producer,causal,selector,String(version),String(ordinal)];
 const parts=[Buffer.from('craft.event-occurrence/v1-candidate\0','ascii')];
 for(const member of members){const bytes=Buffer.from(member,'utf8'),length=Buffer.alloc(4);assert.ok(bytes.length<=4096);length.writeUInt32BE(bytes.length);parts.push(length,bytes);}
 return createHash('sha256').update(Buffer.concat(parts)).digest('hex');
}

const accept=(owner,handle,label,file)=>{const review=owner.review(handle,label);owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},file);};

for(const choice of cases)test(`C12 generated ${choice.name} Event receiver commits once and reauthenticates before replay`,{concurrency:false},async()=>{
 const root=buildEventSourceFixture(choice.producer==='RequestService'?'request':'permit'),work=mkdtempSync(path.join(os.tmpdir(),'craft-c12-receiver-run-'));
 const leaseMs=240000;
 const source=createGenericCompositionOwner();let sourceHandle,generated,generatedHandle,auth,producerSetup,consumerSetup,producerRuntime,consumerRuntime,relay;
 try{
  trace(choice.name,'prepare source');
  sourceHandle=await source.prepare({sourcePath:path.join(root,choice.producerFile),additionalSourcePaths:[path.join(root,choice.consumerFile)],profilePath:path.join(root,'contracts/selected-profile.json')});
  trace(choice.name,'review and accept source');
  accept(source,sourceHandle,'C12-receiver-source-'+choice.producer,path.join(work,'source-decision.json'));
  trace(choice.name,'generate');
  const output=path.join(work,'generated'),manifest=source.generate(sourceHandle,{entry:choice.producerEntry,outputDirectory:output});
  trace(choice.name,'prepare generated bundle');
  assert.equal(manifest.runtime_contract.application_schema_version,'craft.generic-transaction-application/v4-candidate');
  const modulePath=path.join(output,'application.mjs'),moduleText=readFileSync(modulePath,'utf8');
  const bundle=JSON.parse(moduleText.split('const bundle=')[1].split(';\nexport function')[0]);
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.match(JSON.stringify(system),new RegExp(choice.selector.replaceAll('.','\\.')),'system graph must trace the Event selector');
  assert.match(JSON.stringify(bridge),new RegExp(choice.receiverEntry.replaceAll('.','\\.')),'bridge must trace the receiver Entry');
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);generatedHandle=await generated.prepare();
  trace(choice.name,'review and accept generated bundle');
  accept(generated,generatedHandle,'C12-receiver-generated-'+choice.producer,path.join(work,'generated-decision.json'));
  const operator='c12-operator-'+choice.producer;
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:operator,evidence:'c12-operator-evidence-'+choice.producer,session:'c12-operator-session-'+choice.producer}],grants:[{subject:operator,entry:choice.producerEntry},{subject:operator,entry:choice.readEntry}]});
  trace(choice.name,'prepare and seed stores');
  producerSetup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:choice.producer,ownedDirectory:path.join(work,'producer-store'),nativeAuth:auth.nativeAuth});
  trace(choice.name,'seed producer');
  loadGenericFixture(producerSetup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[{entity:choice.producerEntity,value:{id:choice.id,verified:true,state:choice.initialState}}]}));
  await producerSetup.runtime.close();
  trace(choice.name,'prepare consumer store');
  consumerSetup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:choice.consumer,ownedDirectory:path.join(work,'consumer-store'),nativeAuth:auth.nativeAuth});
  trace(choice.name,'seed consumer');
  loadGenericFixture(consumerSetup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
  await consumerSetup.runtime.close();
  trace(choice.name,'reopen producer');
  producerRuntime=await generated.openRuntime(generatedHandle,{service:choice.producer,storePath:producerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  trace(choice.name,'reopen consumer');
  consumerRuntime=await generated.openRuntime(generatedHandle,{service:choice.consumer,storePath:consumerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  trace(choice.name,'execute producer command');
  auth.bindReceiver(consumerRuntime,choice.receiverEntry);
  const servicePrincipal=auth.inspect().servicePrincipals.find(row=>row.entry===choice.receiverEntry)?.subject;
  assert.ok(servicePrincipal,'fixture must expose only the profile-owned service subject for policy changes');
  const beforeProducer=observe(producerSetup.storePath),beforeConsumer=observe(consumerSetup.storePath);
  assert.equal(beforeProducer.business.flat().length,1);assert.equal(beforeProducer.outbox.length,0);assert.equal(beforeConsumer.business.flat().length,0);assert.equal(beforeConsumer.inbox.length,0);
  const entry=producerRuntime.entry(choice.producerEntry),prepared=producerRuntime.prepareCommand(entry,wire({id:choice.id}),{client_key:'c12-'+choice.producer+'-first'});
  try{
   const granted=await producerRuntime.authorize(auth.actor(producerRuntime,operator,choice.producerEntry),prepared);
   assert.equal(granted.ok,true,JSON.stringify(granted));
   const transferred=await producerRuntime.consume(granted.value,prepared);
   assert.equal(transferred.ok,true,JSON.stringify(transferred));
   const result=await producerRuntime.executeCommand(transferred.value);
   assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.observation.kind,'committed');assert.equal(result.outcome.kind,'Returned');
  }finally{producerRuntime.disposePrepared(prepared);}
  const produced=observe(producerSetup.storePath);
  assert.equal(produced.business.flat().length,1);assert.equal(produced.business.flat()[0].state,choice.finalState);
  assert.equal(produced.journal.length,1);assert.equal(produced.outbox.length,1);
  const event=produced.outbox[0];assert.equal(event.producer_namespace,choice.producer);assert.equal(event.event_selector,choice.selector);assert.equal(event.event_version,1);assert.equal(event.emission_ordinal,0);
  assert.equal(event.causal_command_tuple_sha256,produced.journal[0].tuple_sha256);
  assert.equal(event.occurrence_sha256,occurrence(choice.producer,produced.journal[0].tuple_sha256,choice.selector,1,0));
  assert.deepEqual(JSON.parse(Buffer.from(event.payload_bytes).toString('utf8')),{[choice.consumer==='AuditService'?'requestId':'permitId']:choice.id,decision:choice.decision});
  assert.equal(event.state,'pending');assert.equal(observe(consumerSetup.storePath).business.flat().length,0);
  relay=producerRuntime.openEventRelay();
  trace(choice.name,'claim and deliver');
  const claim=relay.claimNext(leaseMs);assert.ok(claim);
  trace(choice.name,'reject caller ACK');
  await assert.rejects(Promise.resolve().then(()=>relay.ack(claim,{kind:'caller-receipt'})),/ForeignOwner|receipt/i,'caller-minted ACK must fail');
  trace(choice.name,'deliver first claim');
  const delivered=await relay.deliver(claim,consumerRuntime);
  assert.equal(delivered.kind,'committed',JSON.stringify(delivered));assert.ok(delivered.receipt);assert.equal(Object.hasOwn(delivered,'outcome'),false);
  const received=observe(consumerSetup.storePath),claimed=observe(producerSetup.storePath);
  assert.equal(received.business.flat().length,1);assert.equal(received.business.flat()[0].id,choice.auditId);
  assert.equal(received.inbox.length,1);assert.equal(received.inbox[0].occurrence_sha256,event.occurrence_sha256);assert.equal(received.journal.length,1);
  assert.equal(claimed.outbox[0].state,'claimed','ACK must wait until receiver commit');
  const freshClaim=withAdvancedClock(leaseMs+1000,()=>relay.claimNext(leaseMs));assert.ok(freshClaim);
  const refenced=observe(producerSetup.storePath);
  assert.equal(refenced.outbox[0].fence,claimed.outbox[0].fence+1,'redelivery must use a fresh monotone fence');
  await assert.rejects(()=>relay.deliver(claim,consumerRuntime),/C12_EVENT_STALE_CLAIM/,'old fence cannot deliver again');
  auth.setPermission(servicePrincipal,choice.receiverEntry,false);
  trace(choice.name,'deliver denied replay');
  const deniedObserved=await watchPrivateInboxSelect(()=>relay.deliver(freshClaim,consumerRuntime),{reject:true}),denied=deniedObserved.result;
  assert.equal(deniedObserved.reads(),0,'denied Auth must precede the private inbox lookup');
  assert.equal(denied.kind,'denied',JSON.stringify(denied));assert.equal(Object.hasOwn(denied,'receipt'),false);assert.equal(Object.hasOwn(denied,'outcome'),false);
  const afterDenial=observe(consumerSetup.storePath);assert.deepEqual(afterDenial,received,'denied replay cannot read out a private result or create a second effect');
  assert.notEqual(observe(producerSetup.storePath).outbox[0].state,'acked');
  auth.setPermission(servicePrincipal,choice.receiverEntry,true);
  trace(choice.name,'deliver permitted replay');
  const replayObserved=await watchPrivateInboxSelect(()=>relay.deliver(freshClaim,consumerRuntime)),replayed=replayObserved.result;
  assert.ok(replayObserved.reads()>0,'permitted replay must inspect the exact private inbox key');
  assert.equal(replayed.kind,'replayed',JSON.stringify(replayed));assert.ok(replayed.receipt);assert.equal(Object.hasOwn(replayed,'outcome'),false);
  assert.deepEqual(observe(consumerSetup.storePath),received,'exact redelivery is idempotent');
  await relay.ack(freshClaim,replayed.receipt);
  assert.equal(observe(producerSetup.storePath).outbox[0].state,'acked');
  await assert.rejects(Promise.resolve().then(()=>relay.deliver({kind:'original-generic-event-relay-claim/v1-candidate'},consumerRuntime)),/ForeignOwner|claim/i);
 }finally{
  relay?.close();if(consumerRuntime)await consumerRuntime.close();if(producerRuntime)await producerRuntime.close();
  if(auth)await auth.close();if(generatedHandle)generated.dispose(generatedHandle);if(sourceHandle)source.dispose(sourceHandle);
  rmSync(path.dirname(root),{recursive:true,force:true});rmSync(work,{recursive:true,force:true});
 }
});
