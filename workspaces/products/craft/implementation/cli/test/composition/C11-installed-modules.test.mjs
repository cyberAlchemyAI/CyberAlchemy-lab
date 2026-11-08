import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';

const wire=value=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const headers={'content-type':'application/json; charset=utf-8','demopay-protocol':'1'};
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const c10Fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');

// Supply a tarball made from a stable, freshly built CLI: npm run build && npm pack --ignore-scripts.
// The generated modules live below a separate consumer whose only CLI copy comes from that tarball.
const tarball=process.env.CRAFT_C11_CLI_TARBALL;
test('C11 generated modules run through the installed public generic export',{skip:!tarball},async()=>{
 assert.equal(path.isAbsolute(tarball),true,'CRAFT_C11_CLI_TARBALL must be absolute');
 assert.equal(existsSync(tarball),true,'CRAFT_C11_CLI_TARBALL must name an existing tarball');
 const dir=mkdtempSync(path.join(tmpdir(),'craft-c11-installed-'));
 const consumer=path.join(dir,'consumer');mkdirSync(consumer);
 writeFileSync(path.join(consumer,'package.json'),JSON.stringify({name:'c11-clean-consumer',private:true,type:'module'})+'\n');
 const installed=spawnSync('npm',['install','--offline','--ignore-scripts','--no-audit','--no-fund','--no-save',tarball],{cwd:consumer,encoding:'utf8',timeout:120000,env:{...process.env,npm_config_update_notifier:'false'}});
 assert.equal(installed.status,0,`clean package install failed:\n${installed.stdout}\n${installed.stderr}`);
 // Keep both source and generated owners in the same installed registries.
 const installedRoot=path.join(consumer,'node_modules/@domainspec-v2/cli'),installedExports=JSON.parse(readFileSync(path.join(installedRoot,'package.json'),'utf8')).exports;
 const installedImport=key=>{const selected=installedExports[key]?.import;assert.ok(typeof selected==='string'&&selected.startsWith('./dist/'));return import(pathToFileURL(path.join(installedRoot,selected)).href);};
 const [{createGenericCompositionOwner},{createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture},{build}]=await Promise.all([
  installedImport('./generic'),installedImport('./generic/testing'),import('./C11-source-fixture.mjs')
 ]);
 const fixture=build('ReviewDesk');
 const oracle=JSON.parse(readFileSync(path.join(c10Fixture,'independent-oracle.json'),'utf8'));
 const peerScript=`const {createServer}=require('node:http');
const target=process.argv[1],body=process.argv[2];
const server=createServer((request,response)=>{
 process.send({kind:'request',method:request.method,url:request.url});
 if(request.method!=='GET'||request.url!==target){response.writeHead(404,{'content-type':'application/json'});response.end('{}');process.send({kind:'response',status:404});return;}
 response.writeHead(200,{'content-type':'application/json'});response.end(body);process.send({kind:'response',status:200});
});
server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));
process.on('message',message=>{if(message==='close')server.close(()=>process.exit(0));});`;
 const peer=spawn(process.execPath,['-e',peerScript,oracle.provider_target,JSON.stringify(oracle.provider_response)],{stdio:['ignore','ignore','inherit','ipc']});
 const peerEvents=[];peer.on('message',event=>peerEvents.push(event));
 const ready=await Promise.race([new Promise((resolve,reject)=>{const onMessage=event=>{if(event?.kind==='ready'){peer.off('message',onMessage);resolve(event);}};peer.on('message',onMessage);peer.once('error',reject);}),once(peer,'exit').then(()=>{throw Error('controlled GET peer exited before ready');})]);
 writeFileSync(path.join(fixture.root,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:`http://127.0.0.1:${ready.port}`}]})+'\n');
 const source=createGenericCompositionOwner();let sourceHandle,generated,generatedHandle,auth,setupRuntime,runtime;
 const exchanges=[];let unknownNext=false,declineNext=false;
 const port={async exchange(request){
  exchanges.push({path:request.path,body:Buffer.from(request.body).toString('utf8')});
  assert.equal(request.origin,'https://demopay.invalid');assert.equal(request.method,'POST');
  const body=JSON.parse(Buffer.from(request.body).toString('utf8'));
  assert.match(body.attemptKey,/^c11-[0-9a-f]{64}$/);assert.equal(body.currency,'USD');
  if(unknownNext&&request.path==='/v1/capture'){unknownNext=false;return {status:503,headers,body:wire({kind:'error',code:'provider-unavailable'})};}
  if(declineNext&&request.path==='/v1/capture'){declineNext=false;return {status:200,headers,body:wire({...body,status:'DefinitivelyDeclined',providerReference:'declined-'+body.orderId})};}
  return {status:200,headers,body:wire({...body,status:'Captured',providerReference:'receipt-'+body.orderId})};
 }};
 const accept=(owner,handle,id,file)=>{const review=owner.review(handle,id);owner.accept(handle,{decision_id:id,owner:id,outcome:'accepted',reviewed_digest:review.review_sha256},file);};
 try{
  sourceHandle=await source.prepare({sourcePath:path.join(fixture.root,'business.alch'),profilePath:path.join(fixture.root,'contracts/selected-profile.json'),externalProfilePath:path.join(fixture.root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(fixture.root,'contracts/external-write-bindings.json')});
  accept(source,sourceHandle,'C11-runtime-source',path.join(dir,'source-decision.json'));
  const output=path.join(consumer,'generated'),manifest=source.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:output});
  assert.equal(manifest.runtime_contract.application_schema_version,'craft.generic-transaction-application/v3-candidate');
  const [{createGeneratedApplicationOwner},{createGeneratedHttpHandler}]=await Promise.all([
   import(pathToFileURL(path.join(output,'application.mjs')).href),
   import(pathToFileURL(path.join(output,'entry-http.mjs')).href)
  ]);
  generated=createGeneratedApplicationOwner();generatedHandle=await generated.prepare();
  accept(generated,generatedHandle,'C11-runtime-generated',path.join(dir,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:oracle.subject,evidence:'C11-evidence',session:'C11-session'}],grants:[{subject:oracle.subject,entry:oracle.root_entry},{subject:oracle.subject,entry:oracle.child_entry}]});
  const setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:oracle.service,ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});
  setupRuntime=setup.runtime;
  const rows=JSON.parse(readFileSync(path.join(c10Fixture,'fixture-rows.json'),'utf8'));
  for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';
  const stored26=structuredClone(rows.rows.find(row=>row.entity==='ReviewDesk.StoredRequest'&&row.value.id==='23'));
  stored26.value.id='26';stored26.value.reference='504';stored26.value.value.requestId='26';rows.rows.push(stored26);
  const owned26=structuredClone(rows.rows.find(row=>row.entity==='ReviewDesk.HttpOwnedRequest'&&row.value.owner===oracle.subject));
  owned26.value.id='26';owned26.value.value.requestId='26';rows.rows.push(owned26);
  loadGenericFixture(setup.fixture,wire(rows));await setupRuntime.close();setupRuntime=undefined;
  runtime=await generated.openRuntime(generatedHandle,{service:oracle.service,storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
  let handler=createGeneratedHttpHandler(runtime);const route=manifest.runtime_contract.http.route;
  const invoke=async(key,id)=>{
   const response=await handler(new Request('http://component.invalid'+route,{method:'POST',headers:{'content-type':'application/json','idempotency-key':key},body:JSON.stringify({...oracle.operation_input,id})}),auth.actor(runtime,oracle.subject,oracle.root_entry));
   return {status:response.status,body:await response.json()};
  };
  const first=await invoke('c11-capture-23','23');
  if(first.status===500){
   let prepared;let diagnostic='no direct exception';
   try{
    const entry=runtime.entry(oracle.root_entry);
    prepared=runtime.prepareCommand(entry,wire({...oracle.operation_input,id:'23'}),{client_key:'c11-diagnostic-23'});
    const actor=auth.actor(runtime,oracle.subject,oracle.root_entry);
    const authorization=await runtime.authorize(actor,prepared);
    if(!authorization.ok)diagnostic='authorize: '+JSON.stringify(authorization);
    else{
     const transfer=await runtime.consume(authorization.value,prepared);
     if(!transfer.ok)diagnostic='consume: '+JSON.stringify(transfer);
     else diagnostic='execute: '+JSON.stringify(await runtime.executeCommand(transfer.value));
    }
   }catch(error){diagnostic=String(error?.stack??error);}
   finally{if(prepared)runtime.disposePrepared(prepared);}
   assert.fail(JSON.stringify({first,peerEvents,exchanges,diagnostic}));
  }
  assert.equal(first.status,200,JSON.stringify({first,peerEvents,exchanges,runtime:runtime.inspect()}));assert.equal(first.body.ok,true);assert.equal(first.body.observation.kind,'committed');
  assert.deepEqual(peerEvents.filter(event=>event.kind==='request').map(event=>[event.method,event.url]),[['GET',oracle.provider_target]]);
  assert.deepEqual(peerEvents.filter(event=>event.kind==='response').map(event=>event.status),[200]);
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture']);
  const replay=await invoke('c11-capture-23','23');
  assert.equal(replay.status,200,JSON.stringify(replay));assert.equal(replay.body.observation.kind,'replayed');
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture']);
  unknownNext=true;
  const unknown=await invoke('c11-capture-25','25');
  assert.equal(unknown.status,503,JSON.stringify(unknown));assert.equal(unknown.body.error.code,'ExternalOutcomeUnknown');
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture','/v1/capture']);
  await runtime.close();
  runtime=await generated.openRuntime(generatedHandle,{service:oracle.service,storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
  handler=createGeneratedHttpHandler(runtime);
  const recovered=await invoke('c11-capture-25','25');
  assert.equal(recovered.status,200,JSON.stringify(recovered));assert.equal(recovered.body.observation.kind,'committed');
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture','/v1/capture','/v1/capture/inspect']);
  assert.equal(JSON.parse(exchanges[1].body).attemptKey,JSON.parse(exchanges[2].body).attemptKey);
  const schema=JSON.parse(readFileSync(path.join(output,'storage/schema.json'),'utf8'));
  const businessRows=()=>{const db=new DatabaseSync(setup.storePath,{readOnly:true});try{return schema.tables.map(table=>({entity:table.entity,rows:db.prepare(`SELECT * FROM "${table.physical_name.replaceAll('"','""')}" ORDER BY rowid`).all()}));}finally{db.close();}};
  const beforeDecline=businessRows();declineNext=true;
  const declined=await invoke('c11-decline-26','26');
  assert.equal(declined.status,422,JSON.stringify(declined));assert.equal(declined.body.ok,true);
  assert.equal(declined.body.outcome.kind,'Rejected');assert.equal(declined.body.outcome.code,'provider-declined');
  assert.deepEqual(businessRows(),beforeDecline,'definite provider decline must leave business rows unchanged');
  assert.deepEqual(exchanges.map(x=>x.path),['/v1/capture','/v1/capture','/v1/capture/inspect','/v1/capture']);
 }finally{
  if(runtime)await runtime.close();if(setupRuntime)await setupRuntime.close();if(auth)await auth.close();
  if(generatedHandle)generated.dispose(generatedHandle);if(sourceHandle)source.dispose(sourceHandle);
  if(peer.exitCode===null){peer.send('close');await once(peer,'exit');}
  rmSync(fixture.root,{recursive:true,force:true});rmSync(dir,{recursive:true,force:true});
 }
});
