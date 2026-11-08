import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdtempSync,readFileSync,rmSync,unlinkSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {build} from './C11-source-fixture.mjs';
import {GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES} from '../../src/generic/composition-capabilities.ts';
import {captureExternalProfile,generateExternalBusinessSources} from '../../src/generic/external-read-profile.ts';
import {createExternalApiComposition} from '../../src/generic/external-read-source.ts';
import {reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.ts';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';

const wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const sha=value=>createHash('sha256').update(value).digest('hex');
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const c10Fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const accept=(owner,handle,id,file)=>{const review=owner.review(handle,id);owner.accept(handle,{decision_id:id,owner:id,outcome:'accepted',reviewed_digest:review.review_sha256},file);};

const receiver=`module AuditService version 1

value-object ApprovalNotice:
  approvalId UInt64
  approved Bool

mapping FromApprovalCommittedPayload:
  input payload ReviewDesk.ApprovalCommittedPayload
  target ApprovalNotice
  total true
  field approvalId <- payload.approvalId
  field approved <- payload.approved

entity AuditRecord:
  id UInt64
  approved Bool
  identity id

mapping ToAuditRecord:
  input notice ApprovalNotice
  target AuditRecord
  total true
  field id <- notice.approvalId
  field approved <- notice.approved

operation RecordApproval:
  input notice ApprovalNotice
  output AuditRecord
  transaction Record:
    atomic-participants AuditRecord
    create record AuditRecord from ToAuditRecord(notice)
    on-unique-conflict reject audit-conflict
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return record

entry AuditService.RecordApprovedEntry:
  invokes AuditService.RecordApproval
  interaction event ReviewDesk.ApprovalCommitted
  bind notice <- FromApprovalCommittedPayload(payload)
  access:
    authenticated relay
    permission audit-request.record
    auth-resource audit-request
    auth-action record
    auth-scope audit-service
`;

function replace(root,file,from,to){const p=path.join(root,file),text=readFileSync(p,'utf8');assert.ok(text.includes(from),`${file}: expected fixture marker`);writeFileSync(p,text.replace(from,to));}

function composedFixture(){
 const {root}=build('ReviewDesk');
 writeFileSync(path.join(root,'audit-service.alch'),receiver);
 replace(root,'business.alch','    atomic-participants StoredRequest\n','    atomic-participants StoredRequest, ApprovalCommitted\n');
 replace(root,'business.alch','      value <- ApplyDecision(request=stored.value,decision=decision)\n','      value <- ApplyDecision(request=stored.value,decision=decision)\n    emit ApprovalCommitted payload ToApprovalCommittedPayload(decision)\n');
 replace(root,'business.alch','entry ReviewDesk.ReadStoredRequestEntry:\n  invokes ReviewDesk.ReadStoredRequest\n  interaction request-response\n  access:\n    authenticated customer','entry ReviewDesk.ReadStoredRequestEntry:\n  invokes ReviewDesk.ReadStoredRequest\n  interaction request-response\n  access:\n    authenticated operator');
 replace(root,'business.alch','entry ReviewDesk.CommitRequestApprovalEntry:\n  invokes ReviewDesk.CommitRequestApproval\n  interaction request-response\n  access:\n    authenticated customer','entry ReviewDesk.CommitRequestApprovalEntry:\n  invokes ReviewDesk.CommitRequestApproval\n  interaction request-response\n  access:\n    authenticated operator');
 writeFileSync(path.join(root,'business.alch'),readFileSync(path.join(root,'business.alch'),'utf8')+`
value-object ApprovalCommittedPayload:
  approvalId UInt64
  approved Bool

mapping ToApprovalCommittedPayload:
  input decision Decision
  target ApprovalCommittedPayload
  total true
  field approvalId <- decision.decisionId
  field approved <- decision.approved

event ApprovalCommitted version 1:
  payload ApprovalCommittedPayload
  from ReviewDesk.CommitRequestApproval
  delivered-to AuditService.RecordApprovedEntry
`);
 replace(root,'application.alch','  source business.alch\n','  source business.alch\n  source audit-service.alch\n');
 replace(root,'application.alch','  service ReviewDeskService module ReviewDesk\n','  service ReviewDeskService module ReviewDesk\n  service AuditService module AuditService\n');
 const profilePath=path.join(root,'contracts/selected-profile.json'),profile=JSON.parse(readFileSync(profilePath,'utf8'));
 profile.schema_version='craft.generic-event-profile/v1-candidate';profile.capabilities=[...GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES];profile.storage='sqlite-fenced-event-handoff/v1-candidate';profile.services.push({id:'AuditService',module:'AuditService'});profile.string_policy={max_utf8_bytes:256,max_scalars:256};profile.event_handoff={transport:'process-local-checked-envelope/v1-candidate',delivery:'durable-at-least-once/v1-candidate'};
 writeFileSync(profilePath,JSON.stringify(profile,null,2)+'\n');
 const generationPath=path.join(root,'contracts/external-generation.json'),generation=JSON.parse(readFileSync(generationPath,'utf8'));
 generation.authored_paths.push('audit-service.alch');
 const application=readFileSync(path.join(root,'application.alch'),'utf8'),oldGenerated=application.match(/generated\/external-[a-f0-9]{64}\.alch/)?.[0];assert.ok(oldGenerated);
 const baseApp=application.split('\n').filter(line=>!line.includes('source generated/external-')&&!line.includes('external-bindings contracts/external-profile.json')&&!line.includes('external-config contracts/external-config.json')).join('\n');
 const business=readFileSync(path.join(root,'business.alch'),'utf8'),sources=[{path:'business.alch',text:business},{path:'audit-service.alch',text:receiver},{path:'application.alch',text:baseApp},{path:'generated/auth-context.alch',text:readFileSync(path.join(root,'generated/auth-context.alch'),'utf8')}];
 const external=captureExternalProfile(path.join(root,'contracts/external-profile.json'),root),regenerated=generateExternalBusinessSources(external,reconstructCoreCommerceSources(sources,'event-handoff-entry'),sources.filter(s=>s.path==='business.alch'||s.path==='audit-service.alch'),sources,'event-handoff-entry');
 unlinkSync(path.join(root,oldGenerated));for(const f of regenerated.files)writeFileSync(path.join(root,f.path),f.text);
 writeFileSync(path.join(root,'application.alch'),application.replace(oldGenerated,regenerated.files[0].path));
 const compositionText=JSON.stringify(createExternalApiComposition(regenerated.bindings),null,2)+'\n';writeFileSync(path.join(root,'contracts/external-composition.json'),compositionText);
 generation.bindings=regenerated.bindings;generation.calls=regenerated.calls;generation.files=generation.files.filter(f=>f.path!==oldGenerated&&f.path!=='contracts/external-composition.json');for(const f of [...regenerated.files,{path:'contracts/external-composition.json',text:compositionText}])generation.files.push({path:f.path,sha256:sha(f.text),bytes:Buffer.byteLength(f.text)});
 writeFileSync(generationPath,JSON.stringify(generation,null,2)+'\n');
 return root;
}

function observed(storePath){
 const db=new DatabaseSync(storePath,{readOnly:true});
 try{return {
  command:db.prepare('SELECT tuple,tuple_sha256 FROM _craft_generic_commands_v1 ORDER BY rowid').all(),
  intents:db.prepare('SELECT effect_json,effect_sha256,state FROM _craft_external_write_intents_v1 ORDER BY rowid').all(),
  outbox:db.prepare('SELECT occurrence_sha256,causal_command_tuple_sha256,event_selector,event_version,target_entry,state FROM _craft_event_outbox_v1 ORDER BY rowid').all(),
  inbox:db.prepare('SELECT occurrence_sha256 FROM _craft_event_inbox_v1 ORDER BY rowid').all(),
 };}finally{db.close();}
}

test('C12 V4 operator command composes safe GET, one durable DemoPay effect, and receiver Event handoff',async()=>{
 const root=composedFixture(),work=mkdtempSync(path.join(os.tmpdir(),'craft-c12-composed-runtime-'));
 const oracle=JSON.parse(readFileSync(path.join(c10Fixture,'independent-oracle.json'),'utf8'));
 const peerScript=`const {createServer}=require('node:http');const target=process.argv[1],body=process.argv[2];const server=createServer((request,response)=>{process.send({kind:'request',method:request.method,url:request.url});if(request.method!=='GET'||request.url!==target){response.writeHead(404);response.end('{}');return;}response.writeHead(200,{'content-type':'application/json'});response.end(body);});server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));process.on('message',message=>{if(message==='close')server.close(()=>process.exit(0));});`;
 const peer=spawn(process.execPath,['-e',peerScript,oracle.provider_target,JSON.stringify(oracle.provider_response)],{stdio:['ignore','ignore','inherit','ipc']});
 const peerEvents=[];peer.on('message',event=>peerEvents.push(event));
 let sourceHandle,generated,generatedHandle,auth,producerSetup,consumerSetup,producerRuntime,consumerRuntime,relay,completed=false;
 const source=createGenericCompositionOwner(),exchanges=[];
 const port={async exchange(request){exchanges.push({path:request.path,body:Buffer.from(request.body).toString('utf8')});assert.equal(request.origin,'https://demopay.invalid');assert.equal(request.method,'POST');const body=JSON.parse(Buffer.from(request.body).toString('utf8'));assert.match(body.attemptKey,/^c11-[0-9a-f]{64}$/);return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},body:wire({...body,status:'Captured',providerReference:'receipt-'+body.orderId})};}};
 try{
  const ready=await Promise.race([new Promise((resolve,reject)=>{const f=event=>{if(event?.kind==='ready'){peer.off('message',f);resolve(event);}};peer.on('message',f);peer.once('error',reject);}),once(peer,'exit').then(()=>{throw Error('controlled GET peer exited before ready');})]);
  writeFileSync(path.join(root,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:`http://127.0.0.1:${ready.port}`}]})+'\n');
  sourceHandle=await source.prepare({sourcePath:path.join(root,'business.alch'),additionalSourcePaths:[path.join(root,'audit-service.alch')],profilePath:path.join(root,'contracts/selected-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  accept(source,sourceHandle,'C12-composed-source',path.join(work,'source-decision.json'));
  const output=path.join(work,'generated'),manifest=source.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:output});assert.equal(manifest.runtime_contract.application_schema_version,'craft.generic-transaction-application/v4-candidate');
  const modulePath=path.join(output,'application.mjs'),moduleText=readFileSync(modulePath,'utf8'),bundle=JSON.parse(moduleText.split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);generatedHandle=await generated.prepare();accept(generated,generatedHandle,'C12-composed-generated',path.join(work,'generated-decision.json'));
  const operator='c12-composed-operator';auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:operator,evidence:'c12-composed-evidence',session:'c12-composed-session'}],grants:[{subject:operator,entry:oracle.root_entry},{subject:operator,entry:oracle.child_entry}]});
  producerSetup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:oracle.service,ownedDirectory:path.join(work,'producer-store'),nativeAuth:auth.nativeAuth});
  const rows=JSON.parse(readFileSync(path.join(c10Fixture,'fixture-rows.json'),'utf8'));for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';loadGenericFixture(producerSetup.fixture,wire(rows));await producerSetup.runtime.close();
  consumerSetup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'AuditService',ownedDirectory:path.join(work,'consumer-store'),nativeAuth:auth.nativeAuth});loadGenericFixture(consumerSetup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));await consumerSetup.runtime.close();
  producerRuntime=await generated.openRuntime(generatedHandle,{service:oracle.service,storePath:producerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
  consumerRuntime=await generated.openRuntime(generatedHandle,{service:'AuditService',storePath:consumerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});auth.bindReceiver(consumerRuntime,'AuditService.RecordApprovedEntry');
  const invoke=async()=>{const entry=producerRuntime.entry(oracle.root_entry),prepared=producerRuntime.prepareCommand(entry,wire(oracle.operation_input),{client_key:'c12-composed-23'});try{const granted=await producerRuntime.authorize(auth.actor(producerRuntime,operator,oracle.root_entry),prepared);assert.equal(granted.ok,true,JSON.stringify(granted));const transferred=await producerRuntime.consume(granted.value,prepared);assert.equal(transferred.ok,true,JSON.stringify(transferred));const identity=producerRuntime.inspectTransferredCommandIdentity(transferred.value);const result=await producerRuntime.executeCommand(transferred.value);assert.equal(result.observation.command_tuple_sha256,identity.command_tuple_sha256);return result;}finally{producerRuntime.disposePrepared(prepared);}};
  const first=await invoke();assert.equal(first.ok,true,JSON.stringify(first));
  const firstDiagnostic=first.observation.kind==='committed'?null:(()=>{
   const rows=observed(producerSetup.storePath);
   return {first,peerEvents,exchanges,store:{commands:rows.command.length,intents:rows.intents.length,outbox:rows.outbox.length},fixture:work};
  })();
  assert.equal(first.observation.kind,'committed',JSON.stringify(firstDiagnostic));
  assert.deepEqual(peerEvents.filter(x=>x.kind==='request').map(x=>[x.method,x.url]),[['GET',oracle.provider_target]]);assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture']);
  const produced=observed(producerSetup.storePath);assert.equal(produced.command.length,1);assert.equal(produced.intents.length,1);assert.equal(produced.outbox.length,1);
  const rootTuple=JSON.parse(Buffer.from(produced.command[0].tuple).toString('utf8'));assert.equal(rootTuple.schema_version,'craft.generic-root-command/v2-candidate');assert.deepEqual(rootTuple.principal,{kind:'operator',subject:operator,tenant:null});assert.equal(rootTuple.root_entry,oracle.root_entry);assert.equal(sha(Buffer.from(produced.command[0].tuple)),produced.command[0].tuple_sha256);
  const effect=JSON.parse(produced.intents[0].effect_json);assert.equal(effect.schema_version,'craft.generic-external-effect/v2-candidate');assert.deepEqual(effect.parent,rootTuple);assert.equal(effect.interface_ref,'ReviewDesk.Provider');assert.equal(effect.contract_operation_ref,'ReviewDesk.Capture');assert.equal(sha(produced.intents[0].effect_json),produced.intents[0].effect_sha256);
  assert.equal(produced.outbox[0].causal_command_tuple_sha256,produced.command[0].tuple_sha256);assert.equal(produced.outbox[0].event_selector,'ReviewDesk.ApprovalCommitted');assert.equal(produced.outbox[0].event_version,1);assert.equal(produced.outbox[0].target_entry,'AuditService.RecordApprovedEntry');
  relay=producerRuntime.openEventRelay();const claim=relay.claimNext(240000);assert.ok(claim);const delivered=await relay.deliver(claim,consumerRuntime);assert.equal(delivered.kind,'committed',JSON.stringify(delivered));await relay.ack(claim,delivered.receipt);assert.equal(observed(consumerSetup.storePath).inbox.length,1);assert.equal(observed(producerSetup.storePath).outbox[0].state,'acked');
  const replay=await invoke();assert.equal(replay.ok,true,JSON.stringify(replay));assert.equal(replay.observation.kind,'replayed');assert.equal(replay.observation.command_tuple_sha256,first.observation.command_tuple_sha256);assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture']);assert.equal(peerEvents.filter(x=>x.kind==='request').length,1);assert.equal(observed(producerSetup.storePath).outbox.length,1);assert.equal(observed(consumerSetup.storePath).inbox.length,1);completed=true;
 }finally{
  relay?.close();if(consumerRuntime)await consumerRuntime.close();if(producerRuntime)await producerRuntime.close();if(auth)await auth.close();if(generatedHandle)generated.dispose(generatedHandle);if(sourceHandle)source.dispose(sourceHandle);if(peer.exitCode===null){peer.send('close');await once(peer,'exit');}if(completed||process.env.C12_PRESERVE_FAILED_DIAGNOSTIC!=='1'){rmSync(path.dirname(root),{recursive:true,force:true});rmSync(work,{recursive:true,force:true});}else console.error('C12 preserved diagnostic fixture:',work,'source:',root);
 }
});
