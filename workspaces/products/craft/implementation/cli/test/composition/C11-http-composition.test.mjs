/** Cumulative C11 HTTP regression over genuine generated owners and native Auth.
 * Open questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 * The controlled peers supply protocol bytes, never business callbacks.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,realpathSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {DatabaseSync,StatementSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';
import {build} from './C11-source-fixture.mjs';

const cli=fileURLToPath(new URL('../../',import.meta.url));
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const base=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const read=name=>JSON.parse(readFileSync(path.join(base,name),'utf8'));
const wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const nativeHeaders={'content-type':'application/json; charset=utf-8','demopay-protocol':'1'};
function accept(owner,handle,label,directory){
 const review=owner.review(handle,label);
 owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,label+'.json'));
}

test('C11 profiled generated HTTP preserves capture identity, fresh-Auth replay, unknown inspection and decline',async()=>{
 const fixture=build('ReviewDesk'),directory=mkdtempSync(path.join(cli,'.c11-http-test-')),oracle=read('independent-oracle.json');
 let sourceHandle,epoch,storePath,peer;
 const source=createGenericHttpCompositionOwner(),exchanges=[];
 let sequence=0,unknownNext=false,declineNext=false;
 const port={async exchange(request){
  assert.equal(request.origin,'https://demopay.invalid');assert.equal(request.method,'POST');
  assert.deepEqual(request.headers,nativeHeaders);assert.equal(request.signal.aborted,false);
  const body=JSON.parse(Buffer.from(request.body).toString('utf8'));
  assert.match(body.attemptKey,/^c11-[0-9a-f]{64}$/);assert.equal(body.currency,'USD');
  exchanges.push({path:request.path,body});
  if(unknownNext&&request.path==='/v1/capture'){unknownNext=false;return {status:503,headers:nativeHeaders,body:wire({kind:'error',code:'unavailable'})};}
  const status=declineNext&&request.path==='/v1/capture'?'DefinitivelyDeclined':'Captured';declineNext=false;
  return {status:200,headers:nativeHeaders,body:wire({...body,status,providerReference:'receipt-'+body.orderId})};
 }};
 const closeEpoch=async()=>{
  if(!epoch)return;const current=epoch;epoch=undefined;const errors=[];
  for(const close of [()=>current.runtime.close(),()=>current.auth.close(),()=>current.owner.dispose(current.handle)])
   try{await close();}catch(error){errors.push(error);}
  if(errors.length)throw new AggregateError(errors,'HTTP epoch cleanup failed');
 };
 const observeProtectedReads=async action=>{
  const schema=JSON.parse(readFileSync(path.join(directory,'generated/storage/schema.json'),'utf8')),names=schema.tables.map(table=>table.physical_name);
  const originals=new Map();let reads=0;
  try{
   for(const method of ['all','get','iterate']){
    const descriptor=Object.getOwnPropertyDescriptor(StatementSync.prototype,method);assert.ok(descriptor?.value&&descriptor.configurable);originals.set(method,descriptor);
    Object.defineProperty(StatementSync.prototype,method,{...descriptor,value:function(...args){
     const sql=this.sourceSQL;
     if(typeof sql==='string'&&/^\s*SELECT\b/i.test(sql)&&names.some(name=>sql.includes('"'+name.replaceAll('"','""')+'"')||sql.includes(' '+name+' ')))reads++;
     return Reflect.apply(descriptor.value,this,args);
    }});
   }
   const value=await action();return {value,reads};
  }finally{for(const [method,descriptor]of originals)Object.defineProperty(StatementSync.prototype,method,descriptor);}
 };
 const snapshot=()=>{
  const schema=JSON.parse(readFileSync(path.join(directory,'generated/storage/schema.json'),'utf8'));
  const db=new DatabaseSync(storePath,{readOnly:true});
  try{return {journal:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n,
   rows:schema.tables.map(table=>({entity:table.entity,rows:db.prepare('SELECT * FROM "'+table.physical_name.replaceAll('"','""')+'" ORDER BY rowid').all()}))};}
  finally{db.close();}
 };
 try{
  const peerScript="const {createServer}=require('node:http');const body=process.argv[1];const server=createServer((req,res)=>{process.send({kind:'request',method:req.method,url:req.url});res.writeHead(200,{'content-type':'application/json'});res.end(body);});server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));process.on('message',m=>{if(m==='close'){server.close(()=>process.exit(0));server.closeAllConnections();}});";
  peer=spawn(process.execPath,['-e',peerScript,JSON.stringify(oracle.provider_response)],{stdio:['ignore','ignore','inherit','ipc']});
  const ready=await Promise.race([new Promise((resolve,reject)=>{peer.on('message',event=>{if(event?.kind==='ready')resolve(event);});peer.once('error',reject);}),once(peer,'exit').then(()=>{throw Error('controlled provider exited before readiness');})]);
  writeFileSync(path.join(fixture.root,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:'http://127.0.0.1:'+ready.port}]})+'\n');
  // Select the existing checked HTTP response mappings over the V3 application.
  writeFileSync(path.join(fixture.root,'contracts/http-profile.json'),JSON.stringify(read('contracts/http-profile.json'),null,2)+'\n');
  // Keep the original C10 input invariant in this cumulative path. Earlier
  // prototype fixtures removed it; this generated HTTP application must retain it.
  const businessPath=path.join(fixture.root,'business.alch'),business=readFileSync(businessPath,'utf8'),invariantBoundary='\n\nrule ApprovalSlotAvailable:';
  assert.ok(business.includes(invariantBoundary));
  writeFileSync(businessPath,business.replace(invariantBoundary,'\n  invariant startsAt < endsAt and endsAt <= 1440'+invariantBoundary));
  sourceHandle=await source.prepare({sourcePath:path.join(fixture.root,'business.alch'),profilePath:path.join(fixture.root,'contracts/selected-profile.json'),httpProfilePath:path.join(fixture.root,'contracts/http-profile.json'),externalProfilePath:path.join(fixture.root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(fixture.root,'contracts/external-write-bindings.json')});
  accept(source,sourceHandle,'source-http-write',directory);
  const output=path.join(directory,'generated'),manifest=source.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:output});
  assert.equal(manifest.runtime_contract.application_schema_version,'craft.generic-transaction-application/v3-candidate');
  assert.ok(manifest.runtime_contract.http.routes.some(route=>route.id===oracle.route_id));
  const generated=await import(pathToFileURL(path.join(output,'application.mjs')).href);
  const rows=read('fixture-rows.json');
  for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';
  const extra=structuredClone(rows.rows.find(row=>row.entity==='ReviewDesk.StoredRequest'&&row.value.id==='23'));
  extra.value.id='26';extra.value.reference='504';extra.value.value.requestId='26';rows.rows.push(extra);
  const open=async(grants=[oracle.root_entry,oracle.child_entry])=>{
   const owner=generated.createGeneratedApplicationOwner(),handle=await owner.prepare(),id=++sequence;
   let auth,runtime,setupRuntime;
   try{
    accept(owner,handle,'http-write-epoch-'+id,directory);
    auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(directory,'auth-'+id),subjects:[{id:oracle.subject,evidence:'write-evidence-'+id,session:'write-session-'+id}],grants:grants.map(entry=>({subject:oracle.subject,entry}))});
    if(!storePath){
     const setup=await prepareGenericFixtureRuntime(owner,handle,{service:oracle.service,ownedDirectory:path.join(directory,'store'),nativeAuth:auth.nativeAuth});
     setupRuntime=setup.runtime;loadGenericFixture(setup.fixture,wire(rows));storePath=setup.storePath;await setupRuntime.close();setupRuntime=undefined;
    }
    runtime=await owner.openRuntime(handle,{service:oracle.service,storePath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
    epoch={owner,handle,auth,runtime};return epoch;
   }catch(error){
    const errors=[error];for(const close of [()=>setupRuntime?.close(),()=>runtime?.close(),()=>auth?.close(),()=>owner.dispose(handle)])try{await close();}catch(cleanup){errors.push(cleanup);}
    throw errors.length===1?error:new AggregateError(errors,'HTTP setup and cleanup failed',{cause:error});
   }
  };
  const invoke=async(key,id,associated=true,inputOverride)=>{
   const handler=epoch.owner.bindHttp(epoch.handle,epoch.runtime,oracle.route_id);
   const request=new Request('https://application.invalid/api/approvals',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from(key).toString('base64url')},body:JSON.stringify(inputOverride??{...oracle.operation_input,id})});
   if(associated)epoch.auth.associateRequest(handler,request,oracle.subject);
   const response=await handler(request);return {status:response.status,body:await response.json()};
  };
  await open();
  const invalidInput=structuredClone(oracle.operation_input);invalidInput.slotRequest.startsAt='120';invalidInput.slotRequest.endsAt='60';
  const beforeInvalid=snapshot(),invalid=await invoke('invalid-slot','23',true,invalidInput);
  assert.equal(invalid.status,400,JSON.stringify(invalid));assert.equal(invalid.body.code,'InvalidInput');assert.equal(invalid.body.cause_code,'InputType');
  assert.equal(exchanges.length,0);assert.deepEqual(snapshot(),beforeInvalid);
  const beforeMissing=snapshot(),missing=await invoke('missing-auth','23',false);
  assert.equal(missing.status,401);assert.equal(missing.body.code,'AuthenticationRequired');
  assert.equal(exchanges.length,0);assert.deepEqual(snapshot(),beforeMissing);
  const observedFirst=await observeProtectedReads(()=>invoke('capture-23','23'));assert.ok(observedFirst.reads>0,'positive control must observe actual protected business SQL');
  const first=observedFirst.value;
  assert.equal(first.status,200,JSON.stringify(first));assert.equal(first.body.kind,'returned');assert.deepEqual(first.body.value,oracle.expected_http_value);assert.equal(first.body.observation.kind,'committed');
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture']);const committed=snapshot();assert.equal(committed.journal-beforeMissing.journal,1);
  const conflict=await invoke('capture-23','25');
  assert.equal(conflict.status,409,JSON.stringify(conflict));assert.equal(conflict.body.code,'CommandPayloadConflict');assert.deepEqual(snapshot(),committed);assert.equal(exchanges.length,1);
  await closeEpoch();await open();
  const replay=await invoke('capture-23','23');
  assert.equal(replay.status,200,JSON.stringify(replay));assert.equal(replay.body.observation.kind,'replayed');assert.deepEqual(replay.body.value,first.body.value);
  assert.equal(replay.body.observation.command_tuple_sha256,first.body.observation.command_tuple_sha256);assert.equal(replay.body.observation.result_sha256,first.body.observation.result_sha256);
  assert.deepEqual(snapshot(),committed);assert.equal(exchanges.length,1);
  unknownNext=true;const uncertain=await invoke('capture-25','25');
  assert.equal(uncertain.status,503,JSON.stringify(uncertain));assert.equal(uncertain.body.kind,'fault');assert.equal(uncertain.body.code,'ExternalOutcomeUnknown');
  assert.deepEqual(snapshot(),committed);assert.equal(exchanges.length,2);
  await closeEpoch();await open([oracle.child_entry]);
  const observedDenied=await observeProtectedReads(()=>invoke('capture-25','25')),denied=observedDenied.value;
  assert.equal(denied.status,403,JSON.stringify(denied));assert.equal(denied.body.code,'PermissionDenied');assert.equal(observedDenied.reads,0);
  assert.equal(exchanges.length,2);assert.deepEqual(snapshot(),committed);
  await closeEpoch();await open();
  const inspected=await invoke('capture-25','25');
  assert.equal(inspected.status,200,JSON.stringify(inspected));assert.equal(inspected.body.observation.kind,'committed');
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture','/v1/capture','/v1/capture/inspect']);
  assert.deepEqual(exchanges[1].body,exchanges[2].body,'recovery must inspect the exact original request and attempt key');
  const beforeDecline=snapshot();declineNext=true;const declined=await invoke('capture-26','26');
  assert.equal(declined.status,422,JSON.stringify(declined));assert.equal(declined.body.kind,'rejected');assert.equal(declined.body.code,'provider-declined');
  assert.deepEqual(snapshot().rows,beforeDecline.rows);assert.equal(exchanges.length,4);
  assert.equal(exchanges[3].path,'/v1/capture');
 }finally{
  const errors=[];
  for(const close of [closeEpoch,()=>sourceHandle?source.dispose(sourceHandle):undefined,async()=>{if(peer&&peer.exitCode===null){peer.send('close');await once(peer,'exit');}}])try{await close();}catch(error){errors.push(error);}
  assert.equal(realpathSync(directory),directory);assert.ok(directory.startsWith(path.join(cli,'.c11-http-test-')));
  rmSync(directory,{recursive:true,force:true});
  assert.equal(realpathSync(fixture.root),fixture.root);assert.ok(fixture.root.startsWith(path.join(tmpdir(),'craft-c11-v3-plan-')));
  rmSync(fixture.root,{recursive:true,force:true});
  if(errors.length)throw new AggregateError(errors,'C11 HTTP cleanup failed');
 }
});
