/** Actual worker SIGKILL/restart over an emitted application and real SQLite.
 * Open questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 * The provider is a raw protocol peer, never a business implementation.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,realpathSync,copyFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import {workflowFixture} from './C13-workflow-fixture.mjs';

const cli=fileURLToPath(new URL('../../',import.meta.url));
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const base=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const read=name=>JSON.parse(readFileSync(path.join(base,name),'utf8'));
const headers={'content-type':'application/json; charset=utf-8','demopay-protocol':'1'};
const canonicalDriver=fileURLToPath(new URL('./C13-process-worker.mjs',import.meta.url));

test('C13 generated HTTP workflow survives SIGKILL at capture and post-ACK windows with fresh owners and no duplicate effects',async()=>{
 const installed=process.env.C13_INSTALLED_CONSUMER_ROOT;
 const outputRoot=installed?realpathSync(installed):cli;
 let sdk={createGenericHttpCompositionOwner},packageRoot=cli;
 if(installed){
  assert.ok(path.isAbsolute(installed));
  packageRoot=realpathSync(path.join(outputRoot,'node_modules/@domainspec-v2/cli'));
  const manifest=JSON.parse(readFileSync(path.join(packageRoot,'package.json'),'utf8'));
  assert.equal(manifest.name,'@domainspec-v2/cli');assert.equal(manifest.version,'1.3.0');
  assert.ok(packageRoot.startsWith(outputRoot+path.sep+'node_modules'+path.sep));
  sdk=await import(pathToFileURL(path.resolve(packageRoot,manifest.exports['./generic'].import)).href);
 }
 const root=workflowFixture(),work=mkdtempSync(path.join(outputRoot,'.c13-crash-test-')),oracle=read('independent-oracle.json');
 const driver=installed?path.join(work,'C13-process-worker.mjs'):canonicalDriver;
 if(installed)copyFileSync(canonicalDriver,driver);
 const owner=sdk.createGenericHttpCompositionOwner(),children=[],exchanges=[],effects=new Map(),stages=[];
 let sourceHandle,peer,passed=false;
 function run(mode,configPath){
  const child=spawn(process.execPath,['--import','tsx',driver,configPath,mode],{cwd:cli,
   detached:process.platform!=='win32',stdio:['ignore','pipe','pipe','ipc']});
  children.push(child);let stdout='',stderr='';
  child.stdout.on('data',bytes=>stdout+=bytes);child.stderr.on('data',bytes=>stderr+=bytes);
  const messages=[];const exit=new Promise((resolve,reject)=>{
   child.once('error',reject);child.once('exit',(code,signal)=>resolve({code,signal}));
  });
  child.on('message',message=>{
   messages.push(message);
   if(message.kind!=='wire-request'){
    stages.push({mode,...message});process.stderr.write('C13_PROCESS_STAGE '+mode+' '+message.kind+'\n');
    if(message.kind==='acked'){
     assert.equal(mode,'recovery');
     if(process.platform==='win32')child.kill('SIGKILL');else process.kill(-child.pid,'SIGKILL');
    }
    return;
   }
   try{
    assert.equal(message.method,'POST');assert.equal(message.origin,'https://demopay.invalid');
    assert.deepEqual(message.headers,headers);
    const body=JSON.parse(Buffer.from(message.body,'base64').toString('utf8'));
    assert.match(body.attemptKey,/^c11-[0-9a-f]{64}$/);
    exchanges.push({mode,path:message.path,body,bytes:message.body});
    if(message.path==='/v1/capture'){
     assert.equal(mode,'initial','replacement worker must inspect instead of recapturing');
     assert.equal(effects.size,0,'only one remote effect');
     effects.set(body.attemptKey,{body,bytes:message.body});
     // Kill the owned worker group only. Awaiting its kernel exit below proves
     // actual termination rather than normal SQLite/Auth close/reopen.
     if(process.platform==='win32')child.kill('SIGKILL');else process.kill(-child.pid,'SIGKILL');
    }else{
     assert.equal(mode,'recovery');assert.equal(message.path,'/v1/capture/inspect');
     const effect=effects.get(body.attemptKey);assert.ok(effect);
     assert.equal(message.body,effect.bytes,'inspection uses exact original body bytes');
     assert.deepEqual(body,effect.body);
     child.send({kind:'wire-response',id:message.id,status:200,headers,
      body:Buffer.from(JSON.stringify({...body,status:'Captured',providerReference:'process-receipt-'+body.orderId})).toString('base64')});
    }
   }catch(error){
    stderr+='\nPARENT_PROTOCOL_ASSERTION '+error.stack;
    if(child.exitCode===null&&child.signalCode===null)child.kill('SIGKILL');
   }
  });
  return {child,messages,exit,output:()=>({stdout,stderr})};
 }
 try{
  const peerScript="const {createServer}=require('node:http');const target=process.argv[1],body=process.argv[2];const server=createServer((req,res)=>{process.send({kind:'request',method:req.method,url:req.url});if(req.method!=='GET'||req.url!==target){res.writeHead(404);res.end('{}');return;}res.writeHead(200,{'content-type':'application/json'});res.end(body);});server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));process.on('message',m=>{if(m==='close'){server.close(()=>process.exit(0));server.closeAllConnections();}});";
  peer=spawn(process.execPath,['-e',peerScript,oracle.provider_target,JSON.stringify(oracle.provider_response)],{stdio:['ignore','ignore','inherit','ipc']});
  const ready=await Promise.race([new Promise((resolve,reject)=>{peer.on('message',m=>{if(m?.kind==='ready')resolve(m);});peer.once('error',reject);}),once(peer,'exit').then(()=>{throw Error('GET peer exited before readiness');})]);
  writeFileSync(path.join(root,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:'http://127.0.0.1:'+ready.port}]})+'\n');
  const businessPath=path.join(root,'business.alch'),business=readFileSync(businessPath,'utf8'),boundary='\n\nrule ApprovalSlotAvailable:';
  assert.ok(business.includes(boundary));
  writeFileSync(businessPath,business.replace(boundary,'\n  invariant startsAt < endsAt and endsAt <= 1440'+boundary)+
   '\nmapping HttpWorkflowStart:\n  input started WorkflowStart\n  target WorkflowStart\n  total true\n  expression started\n');
  const httpProfile=read('contracts/http-profile.json');
  httpProfile.routes.push({id:'ReviewDeskHttp.Begin',service:'ReviewDeskService',entry:'ReviewDesk.BeginWorkflowEntry',
   method:'POST',path:'/workflows',query:[],response_mapping:'ReviewDesk.HttpWorkflowStart'});
  writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(httpProfile,null,2)+'\n');
  sourceHandle=await owner.prepare({sourcePath:businessPath,additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=owner.review(sourceHandle,'process-crash-source');
  owner.accept(sourceHandle,{decision_id:'process-crash-source',owner:'process-crash-source',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'source-decision.json'));
  const output=path.join(work,'generated');owner.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:output});
  const rows=read('fixture-rows.json');
  for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';
  const configPath=path.join(work,'config.json'),config={work,output,oracle,rows,expectedGenericRoot:packageRoot};
  writeFileSync(configPath,JSON.stringify(config));
  const initial=run('initial',configPath),firstExit=await initial.exit;
  assert.deepEqual(firstExit,{code:null,signal:'SIGKILL'},JSON.stringify(initial.output()));
  assert.ok(!initial.output().stderr.includes('PARENT_PROTOCOL_ASSERTION'),initial.output().stderr);
  assert.equal(exchanges.length,1);assert.equal(effects.size,1);
  const recovery=initial.messages.find(message=>message.kind==='reserved');assert.ok(recovery,JSON.stringify(initial.output()));
  // Read crash-surviving journal bytes independently before any replacement opens.
  const journal=new DatabaseSync(path.join(work,'journal','workflow.sqlite'),{readOnly:true});
  let before;
  try{
   before=journal.prepare('SELECT * FROM _craft_workflow_instances_v1 WHERE instance_sha256=?').get(recovery.instance);
   assert.equal(before.state,'step-prepared');assert.equal(before.step_index,1);assert.equal(before.fence,1);
  }finally{journal.close();}
  config.recovery=recovery;writeFileSync(configPath,JSON.stringify(config));
  const replacement=run('recovery',configPath),secondExit=await replacement.exit;
  assert.deepEqual(secondExit,{code:null,signal:'SIGKILL'},JSON.stringify(replacement.output()));
  const acked=replacement.messages.find(message=>message.kind==='acked');assert.ok(acked,JSON.stringify(replacement.output()));
  assert.equal(acked.fence,2);assert.equal(acked.instance,recovery.instance);
  const finalWorker=run('after-ack',configPath),finalExit=await finalWorker.exit;
  assert.deepEqual(finalExit,{code:0,signal:null},JSON.stringify(finalWorker.output()));
  const complete=finalWorker.messages.find(message=>message.kind==='complete');assert.ok(complete,JSON.stringify(finalWorker.output()));
  assert.equal(complete.instance,recovery.instance);assert.equal(complete.compatibility,recovery.compatibility);
  assert.equal(complete.fence,3);assert.deepEqual(complete.identity,JSON.parse(before.identity_json));
  assert.deepEqual(exchanges.map(exchange=>exchange.path),['/v1/capture','/v1/capture/inspect']);
  assert.equal(effects.size,1);passed=true;
 }finally{
  if(!passed)process.stderr.write('C13_PROCESS_DIAGNOSTIC '+JSON.stringify({work,stages,exchanges})+'\n');
  for(const child of children)if(child.exitCode===null&&child.signalCode===null){
   const exited=once(child,'exit');
   if(process.platform==='win32')child.kill('SIGKILL');else process.kill(-child.pid,'SIGKILL');
   await exited;
  }
  if(sourceHandle)owner.dispose(sourceHandle);
  if(peer&&peer.exitCode===null&&peer.signalCode===null){const exited=once(peer,'exit');peer.send('close');await exited;}
  if(!passed&&process.env.C13_KEEP_FAILED==='1')process.stderr.write('C13_PROCESS_FILES '+JSON.stringify({root,work})+'\n');
  else{
   assert.ok(realpathSync(work).startsWith(realpathSync(outputRoot)+path.sep+'.c13-crash-test-'));
   assert.ok(path.basename(path.dirname(root)).startsWith('craft-c11-v3-plan-'));
   rmSync(work,{recursive:true,force:true});rmSync(path.dirname(root),{recursive:true,force:true});
  }
 }
});
