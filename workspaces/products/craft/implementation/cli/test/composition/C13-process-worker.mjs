/** Fresh-process crash fixture. Protocol bytes cross IPC; authority handles never do.
 * Open questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import assert from 'node:assert/strict';
import {readFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';

const config=JSON.parse(readFileSync(process.argv[2],'utf8')),mode=process.argv[3];
assert.ok(import.meta.resolve('@domainspec-v2/cli/generic').startsWith(pathToFileURL(config.expectedGenericRoot+path.sep).href),'worker must use the exact source/installed public SDK selected by the parent');
const send=value=>new Promise((resolve,reject)=>process.send(value,error=>error?reject(error):resolve()));
const pending=new Map();let sequence=0;
process.on('message',message=>{
 if(message?.kind!=='wire-response')return;
 const wait=pending.get(message.id);if(!wait)return;
 pending.delete(message.id);
 wait.resolve({status:message.status,headers:message.headers,body:Buffer.from(message.body,'base64')});
});
const port={async exchange(request){
 const id=++sequence;
 const answer=new Promise((resolve,reject)=>pending.set(id,{resolve,reject}));
 await send({kind:'wire-request',id,method:request.method,origin:request.origin,path:request.path,
  headers:request.headers,body:Buffer.from(request.body).toString('base64')});
 return answer;
}};
const wire=value=>Buffer.from(JSON.stringify(value));
const generated=await import(pathToFileURL(path.join(config.output,'application.mjs')).href);
let owner,handle,auth,producer,consumer,worker,setupRuntime;
try{
 owner=generated.createGeneratedApplicationOwner();handle=await owner.prepare();
 const label='process-'+mode,review=owner.review(handle,label);
 owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(config.work,label+'-decision.json'));
 const checked=owner.inspect(handle).workflow_contract;
 assert.equal(checked.workflow,'ReviewDesk.ApprovalFlow');

 const customer='c13-customer',operator='c13-operator';
 auth=await createGenericAuthFixture(owner,handle,{
  ownedDirectory:path.join(config.work,'auth-'+mode),sessionTtlSeconds:7200,
  subjects:[{id:customer,evidence:mode+'-customer-evidence',session:mode+'-customer-session'},
   {id:operator,evidence:mode+'-operator-evidence',session:mode+'-operator-session'}],
  grants:[{subject:customer,entry:checked.start_entry},
   ...[checked.steps[0].entry,checked.steps[0].compensation_entry,checked.steps[1].entry,
    'ReviewDesk.ReadStoredRequestEntry','ReviewDesk.ReadWorkflowReservationEntry'].map(entry=>({subject:operator,entry}))]
 });
 let producerPath,consumerPath;
 if(mode==='initial'){
  const setup=await prepareGenericFixtureRuntime(owner,handle,{service:checked.service,
   ownedDirectory:path.join(config.work,'producer'),nativeAuth:auth.nativeAuth});
  setupRuntime=setup.runtime;loadGenericFixture(setup.fixture,wire(config.rows));
  producerPath=setup.storePath;await setupRuntime.close();setupRuntime=undefined;
  const receiver=await prepareGenericFixtureRuntime(owner,handle,{service:'AuditService',
   ownedDirectory:path.join(config.work,'consumer'),nativeAuth:auth.nativeAuth});
  setupRuntime=receiver.runtime;
  loadGenericFixture(receiver.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
  consumerPath=receiver.storePath;await setupRuntime.close();setupRuntime=undefined;
 }else{
  ({producerPath,consumerPath}=config.recovery);
 }
 producer=await owner.openRuntime(handle,{service:checked.service,storePath:producerPath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
 consumer=await owner.openRuntime(handle,{service:'AuditService',storePath:consumerPath,mode:'reopen',nativeAuth:auth.nativeAuth});
 auth.bindReceiver(consumer,checked.steps[2].entry);
 const actors=new Map([[checked.start_entry,auth.actor(producer,customer,checked.start_entry)]]);
 for(const entry of [checked.steps[0].entry,checked.steps[0].compensation_entry,checked.steps[1].entry])
  actors.set(entry,auth.actor(producer,operator,entry));
 const directory=path.join(config.work,'journal');
 const options={runtime:producer,receiver:consumer,actors,journal:{directory,mode:mode==='initial'?'create':'reopen'}};
 if(mode==='initial'){
  const rejected=path.join(config.work,'rejected-journal');
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,receiver:producer,journal:{directory:rejected,mode:'create'}}),
   error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  assert.equal(existsSync(rejected),false,'foreign receiver must reject before journal effects');
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,compatibility_sha256:'forged'}),
   error=>error.diagnostics?.[0]?.code==='InvalidContract');
  assert.equal(existsSync(directory),false,'caller cannot supply semantic journal bindings');
  const foreign=path.join(config.work,'foreign-journal');mkdirSync(foreign,{mode:0o700});
  const file=path.join(foreign,'workflow.sqlite'),unrelated=new DatabaseSync(file);
  unrelated.exec('CREATE TABLE retained_data (id TEXT PRIMARY KEY); INSERT INTO retained_data VALUES (\'keep\')');unrelated.close();
  const sha=()=>createHash('sha256').update(readFileSync(file)).digest('hex'),before=sha();
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,journal:{directory:foreign,mode:'reopen'}}));
  assert.equal(sha(),before,'reopen must not initialize or repair an unrelated database');
 }
 worker=await owner.openWorkflow(handle,options);
 const compatibility=worker.inspectDefinition().compatibility_sha256;
 assert.equal(worker.inspectDefinition().source_closure_sha256,checked.source_closure_sha256);
 if(mode!=='initial')assert.equal(compatibility,config.recovery.compatibility,'fresh public owner must reconstruct the identical workflow contract');
 if(mode==='initial'){
  await assert.rejects(()=>worker.scheduleStart(new Uint8Array([255]),'bad-utf8'),/UTF-8/);
  await assert.rejects(()=>worker.scheduleStart(Buffer.from('{"id":"23","id":"24"}'),'duplicate-input'),/duplicate/i);
  const empty=new DatabaseSync(path.join(directory,'workflow.sqlite'),{readOnly:true});
  try{assert.equal(empty.prepare('SELECT count(*) AS n FROM _craft_workflow_instances_v1').get().n,0);}
  finally{empty.close();}
  await worker.close();await worker.close();
  assert.throws(()=>worker.inspectDefinition(),error=>error.diagnostics?.[0]?.code==='DisposedOwner');
  worker=await owner.openWorkflow(handle,{...options,journal:{directory,mode:'reopen'}});
 }
 let instance,claim;
 if(mode==='initial'){
  const handler=owner.bindHttp(handle,producer,'ReviewDeskHttp.Begin');
  const request=new Request('http://workflow.invalid/api/workflows',{method:'POST',
   headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from('c13-process-start-23').toString('base64url')},
   body:JSON.stringify(config.oracle.operation_input)});
  auth.associateRequest(handler,request,customer);
  const response=await handler(request);
  assert.equal(response.status,200);assert.deepEqual((await response.json()).value,{id:'23',initiated:true});
  await send({kind:'http-started',status:200});
  const start=await worker.scheduleStart(wire(config.oracle.operation_input),'c13-process-start-23');
  assert.equal(start.result.ok,true,JSON.stringify(start.result));
  assert.equal(start.result.observation.kind,'replayed','workflow scheduling reuses the original HTTP start command');
  instance=start.instance_sha256;
  claim=worker.claimNext(300000);assert.ok(claim);
  const local=await worker.advance(claim);
  assert.equal(local.state,'step-committed',JSON.stringify(local));claim=local.active_claim;assert.ok(claim);
  await send({kind:'reserved',instance,compatibility,producerPath,consumerPath,fence:claim.fence});
  // Parent kills this actual process after recording the remote capture. No
  // reply is sent, no close/dispose occurs, and the original intent is durable.
  await worker.advance(claim);
  throw Error('initial worker unexpectedly returned from held capture');
 }else{
  instance=config.recovery.instance;
  const before=worker.inspect(instance);
  assert.equal(before.state,mode==='recovery'?'step-prepared':'waiting-event');
  assert.equal(before.step_index,mode==='recovery'?1:2);
  const original=before.history.findLast(row=>row.step_index===1&&JSON.parse(row.commitment_json).kind==='prepare-step');
  assert.ok(original);
  // Only lease acquisition uses a controlled clock to avoid a five-minute
  // test sleep. All provider deadlines and subsequent execution use real time.
  const now=Date.now;
  Date.now=()=>Math.max(now(),before.lease_until_ms+1);
  try{claim=worker.claimNext(300000);}finally{Date.now=now;}
  assert.ok(claim);assert.equal(claim.fence,before.fence+1);
  await assert.rejects(()=>worker.advance({instance_sha256:instance,fence:before.fence,lease_until_ms:before.lease_until_ms}),/C13_WORKFLOW_STALE_CLAIM/);
  let progress;
  if(mode==='recovery'){
   progress=await worker.advance(claim);
   assert.equal(progress.state,'step-committed',JSON.stringify(progress));
   claim=progress.active_claim;assert.ok(claim);
   progress=await worker.advance(claim);assert.equal(progress.state,'waiting-event');
   const providerTuple=JSON.parse(original.commitment_json).command_tuple_sha256;
   const relay=producer.openEventRelay();
   const eventClaim=relay.claimWorkflowEvent(checked.steps[2].event_binding,providerTuple,300000);assert.ok(eventClaim);
   const delivered=await relay.deliver(eventClaim,consumer);
   assert.equal(delivered.kind,'committed',JSON.stringify(delivered));
   await relay.ack(eventClaim,delivered.receipt);
   assert.equal(worker.inspect(instance).state,'waiting-event','second crash window leaves journal before Event observation');
   await send({kind:'acked',instance,compatibility,producerPath,consumerPath,fence:claim.fence});
   // Parent SIGKILLs here; no owner or database is gracefully closed.
   await new Promise(()=>{});
  }
  assert.equal(mode,'after-ack');
  progress=await worker.advance(claim);assert.equal(progress.state,'step-committed',JSON.stringify(progress));
  claim=progress.active_claim;assert.ok(claim);
  progress=await worker.advance(claim);assert.equal(progress.state,'completed',JSON.stringify(progress));
  const after=worker.inspect(instance);
  assert.equal(after.state,'completed');assert.deepEqual(after.identity,before.identity);
  const prepare=after.history.filter(row=>row.step_index===1&&JSON.parse(row.commitment_json).kind==='prepare-step');
  assert.equal(prepare.length,1,'recovery retains the original provider command commitment');
  assert.deepEqual(prepare[0],original);
  const inbox=new DatabaseSync(consumerPath,{readOnly:true});
  try{assert.equal(inbox.prepare('SELECT count(*) AS n FROM _craft_event_inbox_v1').get().n,1);}
  finally{inbox.close();}
  const schema=JSON.parse(readFileSync(path.join(config.output,'storage/schema.json'),'utf8'));
  const db=new DatabaseSync(producerPath,{readOnly:true});
  try{
   for(const entity of ['ReviewDesk.WorkflowStart','ReviewDesk.WorkflowReservation']){
    const table=schema.tables.find(table=>table.entity===entity);assert.ok(table,entity);
    assert.equal(db.prepare('SELECT count(*) AS n FROM "'+table.physical_name.replaceAll('"','""')+'"').get().n,1,entity+' must not be created twice');
   }
   assert.equal(db.prepare('SELECT count(*) AS n FROM _craft_event_outbox_v1').get().n,1);
  }finally{db.close();}
  await send({kind:'complete',instance,compatibility,fence:after.fence,identity:after.identity,
   providerTuple:JSON.parse(original.commitment_json).command_tuple_sha256});
 }
}finally{
 for(const close of [()=>setupRuntime?.close(),()=>worker?.close(),()=>consumer?.close(),()=>producer?.close(),()=>auth?.close(),()=>handle&&owner.dispose(handle)])
  await close();
}
process.disconnect();
