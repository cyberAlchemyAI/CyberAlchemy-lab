/** C12 HTTP -> C11 effect -> committed Event -> original receiver.
 * Open questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,realpathSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';
import {composedFixture} from './C13-composed-source-fixture.mjs';

const cli=fileURLToPath(new URL('../../',import.meta.url)),repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const base=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const read=name=>JSON.parse(readFileSync(path.join(base,name),'utf8')),wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const accept=(owner,handle,label,directory)=>{const review=owner.review(handle,label);owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,label+'.json'));};

test('C12 generated HTTP commits one effect and outbox occurrence, then authorizes receiver and replays without duplicates',async()=>{
 const root=composedFixture(),directory=mkdtempSync(path.join(cli,'.c12-http-test-')),oracle=read('independent-oracle.json');
 const source=createGenericHttpCompositionOwner(),operator='c12-http-operator',receiverEntry='AuditService.RecordApprovedEntry';
 let sourceHandle,owner,handle,auth,producer,consumer,producerSetup,consumerSetup,relay,peer,primary;
 const captures=[];
 const port={async exchange(request){
  assert.equal(request.origin,'https://demopay.invalid');assert.equal(request.path,'/v1/capture');
  const body=JSON.parse(Buffer.from(request.body).toString('utf8'));captures.push(body);
  return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},body:wire({...body,status:'Captured',providerReference:'event-receipt-'+body.orderId})};
 }};
 const observe=file=>{
  const db=new DatabaseSync(file,{readOnly:true});
  try{return {commands:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n,
   outbox:db.prepare('SELECT * FROM _craft_event_outbox_v1 ORDER BY rowid').all(),
   inbox:db.prepare('SELECT * FROM _craft_event_inbox_v1 ORDER BY rowid').all()};}
  finally{db.close();}
 };
 try{
  const peerScript="const {createServer}=require('node:http');const body=process.argv[1];const server=createServer((req,res)=>{process.send({kind:'request',method:req.method,url:req.url});res.writeHead(200,{'content-type':'application/json'});res.end(body);});server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));process.on('message',m=>{if(m==='close'){server.close(()=>process.exit(0));server.closeAllConnections();}});";
  peer=spawn(process.execPath,['-e',peerScript,JSON.stringify(oracle.provider_response)],{stdio:['ignore','ignore','inherit','ipc']});
  const requests=[];peer.on('message',event=>{if(event?.kind==='request')requests.push(event);});
  const ready=await Promise.race([new Promise((resolve,reject)=>{peer.on('message',event=>{if(event?.kind==='ready')resolve(event);});peer.once('error',reject);}),once(peer,'exit').then(()=>{throw Error('controlled provider exited before ready');})]);
  writeFileSync(path.join(root,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:'http://127.0.0.1:'+ready.port}]})+'\n');
  writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(read('contracts/http-profile.json'),null,2)+'\n');
  const businessPath=path.join(root,'business.alch'),business=readFileSync(businessPath,'utf8'),boundary='\n\nrule ApprovalSlotAvailable:';
  assert.ok(business.includes(boundary));writeFileSync(businessPath,business.replace(boundary,'\n  invariant startsAt < endsAt and endsAt <= 1440'+boundary));
  sourceHandle=await source.prepare({sourcePath:businessPath,additionalSourcePaths:[path.join(root,'audit-service.alch')],profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  accept(source,sourceHandle,'c12-http-source',directory);const output=path.join(directory,'generated');
  const manifest=source.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:output});
  assert.equal(manifest.runtime_contract.application_schema_version,'craft.generic-transaction-application/v4-candidate');
  const generated=await import(pathToFileURL(path.join(output,'application.mjs')).href);
  owner=generated.createGeneratedApplicationOwner();handle=await owner.prepare();accept(owner,handle,'c12-http-generated',directory);
  auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth'),subjects:[{id:operator,evidence:'c12-http-evidence',session:'c12-http-session'}],grants:[oracle.root_entry,oracle.child_entry].map(entry=>({subject:operator,entry}))});
  producerSetup=await prepareGenericFixtureRuntime(owner,handle,{service:oracle.service,ownedDirectory:path.join(directory,'producer'),nativeAuth:auth.nativeAuth});
  const rows=read('fixture-rows.json');for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';
  loadGenericFixture(producerSetup.fixture,wire(rows));await producerSetup.runtime.close();
  consumerSetup=await prepareGenericFixtureRuntime(owner,handle,{service:'AuditService',ownedDirectory:path.join(directory,'consumer'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(consumerSetup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));await consumerSetup.runtime.close();
  producer=await owner.openRuntime(handle,{service:oracle.service,storePath:producerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
  consumer=await owner.openRuntime(handle,{service:'AuditService',storePath:consumerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  auth.bindReceiver(consumer,receiverEntry);
  const invoke=async()=>{
   const handler=owner.bindHttp(handle,producer,oracle.route_id),request=new Request('https://application.invalid/api/approvals',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from('http-event-23').toString('base64url')},body:JSON.stringify(oracle.operation_input)});
   auth.associateRequest(handler,request,operator);const response=await handler(request);return {status:response.status,body:await response.json()};
  };
  assert.equal(observe(producerSetup.storePath).outbox.length,0);assert.equal(observe(consumerSetup.storePath).inbox.length,0);
  const first=await invoke();assert.equal(first.status,200,JSON.stringify(first));assert.deepEqual(first.body.value,oracle.expected_http_value);assert.equal(first.body.observation.kind,'committed');
  const produced=observe(producerSetup.storePath);assert.equal(produced.commands,1);assert.equal(produced.outbox.length,1);assert.equal(captures.length,1);
  assert.equal(produced.outbox[0].causal_command_tuple_sha256,first.body.observation.command_tuple_sha256);
  assert.equal(produced.outbox[0].event_selector,'ReviewDesk.ApprovalCommitted');assert.equal(produced.outbox[0].target_entry,receiverEntry);
  relay=producer.openEventRelay();const claim=relay.claimNext(240000);assert.ok(claim);
  const servicePrincipal=auth.inspect().servicePrincipals.find(row=>row.entry===receiverEntry)?.subject;assert.equal(typeof servicePrincipal,'string');
  auth.setPermission(servicePrincipal,receiverEntry,false);
  const denied=await relay.deliver(claim,consumer);assert.equal(denied.kind,'denied',JSON.stringify(denied));assert.equal(Object.hasOwn(denied,'receipt'),false);assert.equal(Object.hasOwn(denied,'outcome'),false);
  assert.equal(observe(consumerSetup.storePath).inbox.length,0);assert.equal(observe(producerSetup.storePath).outbox[0].state,'claimed');
  auth.setPermission(servicePrincipal,receiverEntry,true);
  const delivered=await relay.deliver(claim,consumer);assert.equal(delivered.kind,'committed',JSON.stringify(delivered));
  await assert.rejects(Promise.resolve().then(()=>relay.ack(claim,{kind:'forged-receipt'})),/ForeignOwner|receipt/i);
  await relay.ack(claim,delivered.receipt);
  assert.equal(observe(producerSetup.storePath).outbox[0].state,'acked');assert.equal(observe(consumerSetup.storePath).inbox.length,1);
  const table=consumer.inspect().storage.tables.find(row=>row.entity==='AuditService.AuditRecord');assert.ok(table);
  const db=new DatabaseSync(consumerSetup.storePath,{readOnly:true});
  try{const actual=db.prepare('SELECT "'+table.row_column.replaceAll('"','""')+'" AS value FROM "'+table.physical_name.replaceAll('"','""')+'"').all();assert.equal(actual.length,1);assert.deepEqual(JSON.parse(Buffer.from(actual[0].value).toString('utf8')),{id:'23',approved:true});}finally{db.close();}
  const replay=await invoke();assert.equal(replay.status,200,JSON.stringify(replay));assert.equal(replay.body.observation.kind,'replayed');assert.deepEqual(replay.body.value,first.body.value);
  assert.equal(replay.body.observation.command_tuple_sha256,first.body.observation.command_tuple_sha256);assert.equal(captures.length,1);assert.equal(requests.length,1);
  assert.equal(observe(producerSetup.storePath).outbox.length,1);assert.equal(observe(consumerSetup.storePath).inbox.length,1);assert.equal(relay.claimNext(240000),null);
 }catch(error){primary=error;throw error;}
 finally{
  const errors=[];for(const close of [()=>relay?.close(),()=>consumer?.close(),()=>producer?.close(),()=>consumerSetup?.runtime.close(),()=>producerSetup?.runtime.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined,()=>sourceHandle?source.dispose(sourceHandle):undefined,async()=>{if(peer&&peer.exitCode===null){peer.send('close');await once(peer,'exit');}}])try{await close();}catch(error){errors.push(error);}
  assert.equal(realpathSync(directory),directory);assert.ok(directory.startsWith(path.join(cli,'.c12-http-test-')));rmSync(directory,{recursive:true,force:true});
  assert.equal(realpathSync(root),root);assert.ok(root.startsWith(path.join(tmpdir(),'craft-c11-v3-plan-')));rmSync(root,{recursive:true,force:true});
  if(errors.length)throw new AggregateError(primary?[primary,...errors]:errors,'C12 HTTP cleanup failed',{cause:primary});
 }
});

test('C12 checked HTTP profile cannot turn a service Event receiver into a request-response route',async()=>{
 const root=composedFixture(),owner=createGenericHttpCompositionOwner();let handle;
 try{
  const profile=read('contracts/http-profile.json');
  profile.id='AuditHttp';
  profile.routes=[{id:'AuditHttp.Receive',service:'AuditService',entry:'AuditService.RecordApprovedEntry',method:'POST',path:'/events',query:[],response_mapping:'AuditService.ToAuditRecord'}];
  writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(profile,null,2)+'\n');
  await assert.rejects(async()=>{handle=await owner.prepare({
   sourcePath:path.join(root,'business.alch'),additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json'),
   externalProfilePath:path.join(root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')
  });},error=>error.diagnostics?.[0]?.code==='UnsupportedCapability'&&/original relay credential/.test(error.message));
 }finally{
  if(handle)owner.dispose(handle);
  assert.equal(realpathSync(root),root);assert.ok(root.startsWith(path.join(tmpdir(),'craft-c11-v3-plan-')));rmSync(root,{recursive:true,force:true});
 }
});
