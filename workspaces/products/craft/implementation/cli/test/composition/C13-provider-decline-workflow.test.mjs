import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {spawn} from 'node:child_process';
import {mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner,
  requireGenericWorkflowRuntime} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {GenericWorkflowStore} from '../../src/generic/workflow-store.ts';
import {createGenericWorkflowWorker,workflowCompatibilitySha256} from '../../src/generic/workflow-worker.ts';
import {canonicalJson} from '../../src/profile-engine/contracts.ts';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const c10Fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const oracle=JSON.parse(readFileSync(path.join(c10Fixture,'independent-oracle.json'),'utf8'));
const wire=value=>Buffer.from(JSON.stringify(value));
const inboxCount=file=>{const db=new DatabaseSync(file);try{return db.prepare('SELECT count(*) AS n FROM _craft_event_inbox_v1').get().n;}finally{db.close();}};
const withAdvancedClock=(milliseconds,action)=>{const now=Date.now;Date.now=()=>now()+milliseconds;try{return action();}finally{Date.now=now;}};
const accept=(owner,handle,id,file)=>{const review=owner.review(handle,id);owner.accept(handle,
  {decision_id:id,owner:id,outcome:'accepted',reviewed_digest:review.review_sha256},file);};

test('C13 original worker compensates only after checked definitive provider decline',async()=>{
  const root=workflowFixture(),work=mkdtempSync(path.join(tmpdir(),'c13-worker-'));
  const peerScript=`const {createServer}=require('node:http');const target=process.argv[1],body=process.argv[2];const server=createServer((request,response)=>{process.send({kind:'request',method:request.method,url:request.url});if(request.method!=='GET'||request.url!==target){response.writeHead(404);response.end('{}');return;}response.writeHead(200,{'content-type':'application/json'});response.end(body);});server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));process.on('message',message=>{if(message==='close')server.close(()=>process.exit(0));});`;
  const peer=spawn(process.execPath,['-e',peerScript,oracle.provider_target,JSON.stringify(oracle.provider_response)],
    {stdio:['ignore','ignore','inherit','ipc']});
  const peerEvents=[];peer.on('message',event=>peerEvents.push(event));
  let sourceHandle,generated,generatedHandle,auth,producerSetup,consumerSetup,producerRuntime,
    consumerRuntime,relay,journalDb,passed=false;
  const source=createGenericCompositionOwner();
  const exchanges=[];
  const port={async exchange(request){
    exchanges.push(request.path);
    const body=JSON.parse(Buffer.from(request.body).toString('utf8'));
    return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},
      body:wire({...body,status:'DefinitivelyDeclined',providerReference:'declined-'+body.orderId})};
  }};
  try{
    const ready=await Promise.race([new Promise((resolve,reject)=>{const handler=event=>{if(event?.kind==='ready'){peer.off('message',handler);resolve(event);}};peer.on('message',handler);peer.once('error',reject);}),
      once(peer,'exit').then(()=>{throw Error('controlled GET peer exited before ready');})]);
    writeFileSync(path.join(root,'contracts/external-config.json'),JSON.stringify({
      schema_version:'craft.generic-external-read-config/v1-candidate',
      bindings:[{binding:oracle.configuration_binding,origin:`http://127.0.0.1:${ready.port}`}]
    })+'\n');
    sourceHandle=await source.prepare({sourcePath:path.join(root,'business.alch'),
      additionalSourcePaths:[path.join(root,'audit-service.alch')],
      profilePath:path.join(root,'contracts/selected-profile.json'),
      externalProfilePath:path.join(root,'contracts/external-profile.json'),
      externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
    accept(source,sourceHandle,'C13-worker-source',path.join(work,'source-decision.json'));
    const generatedDir=path.join(work,'generated');
    const manifest=source.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:generatedDir});
    assert.equal(manifest.runtime_contract.application_schema_version,
      'craft.generic-transaction-application/v4-candidate');
    const modulePath=path.join(generatedDir,'application.mjs');
    const bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
    generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);
    generatedHandle=await generated.prepare();
    accept(generated,generatedHandle,'C13-worker-generated',path.join(work,'generated-decision.json'));
    const checked=requireGenericWorkflowRuntime(generated,generatedHandle).contract;
    assert.equal(checked.workflow,'ReviewDesk.ApprovalFlow');
    const customer='c13-customer',operator='c13-operator';
    auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),
      sessionTtlSeconds:7200,
      subjects:[{id:customer,evidence:'c13-customer-evidence',session:'c13-customer-session'},
        {id:operator,evidence:'c13-operator-evidence',session:'c13-operator-session'}],
      grants:[{subject:customer,entry:checked.start_entry},
        ...[checked.steps[0].entry,checked.steps[0].compensation_entry,
          checked.steps[1].entry,'ReviewDesk.ReadStoredRequestEntry',
          'ReviewDesk.ReadWorkflowReservationEntry'].map(entry=>({subject:operator,entry}))]});
    producerSetup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:checked.service,
      ownedDirectory:path.join(work,'producer'),nativeAuth:auth.nativeAuth});
    const rows=JSON.parse(readFileSync(path.join(c10Fixture,'fixture-rows.json'),'utf8'));
    for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';
    const secondRow=structuredClone(rows.rows.find(row=>row.entity==='ReviewDesk.StoredRequest'&&row.value.id==='23'));
    secondRow.value.id='26';secondRow.value.reference='506';secondRow.value.value.requestId='26';
    rows.rows.push(secondRow);
    loadGenericFixture(producerSetup.fixture,wire(rows));await producerSetup.runtime.close();
    consumerSetup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'AuditService',
      ownedDirectory:path.join(work,'consumer'),nativeAuth:auth.nativeAuth});
    loadGenericFixture(consumerSetup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
    await consumerSetup.runtime.close();
    const journalPath=path.join(work,'workflow.sqlite'),storeId='ReviewDeskService.workflow';
    journalDb=new DatabaseSync(journalPath);
    let journal=new GenericWorkflowStore(journalDb,{store_id:storeId,owner_service:checked.service,
      compatibility_sha256:workflowCompatibilitySha256(checked)});
    const open=async()=>{
      producerRuntime=await generated.openRuntime(generatedHandle,{service:checked.service,
        storePath:producerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port});
      consumerRuntime=await generated.openRuntime(generatedHandle,{service:'AuditService',
        storePath:consumerSetup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
      auth.bindReceiver(consumerRuntime,checked.steps[2].entry);
      const actors=new Map();
      actors.set(checked.start_entry,auth.actor(producerRuntime,customer,checked.start_entry));
      for(const entry of [checked.steps[0].entry,checked.steps[0].compensation_entry,
        checked.steps[1].entry])actors.set(entry,auth.actor(producerRuntime,operator,entry));
    return createGenericWorkflowWorker({source:checked,runtime:producerRuntime,journal,
      journal_store_id:storeId,actors,receiver:consumerRuntime});
    };
    let worker=await open();
    const started=await worker.scheduleStart(canonicalJson(oracle.operation_input),'c13-start-23');
    assert.equal(started.result.ok,true,JSON.stringify(started.result));
    assert.equal(started.result.observation.kind,'committed');
    let claim=worker.claimNext(300000);
    assert.ok(claim);
    let progress=await worker.advance(claim);
    assert.equal(progress.state,'step-committed',JSON.stringify(progress));
    assert.equal(worker.inspect(started.instance_sha256).step_index,0);
    claim=progress.active_claim;assert.ok(claim);
    progress=await worker.advance(claim);
    assert.equal(progress.state,'compensating',JSON.stringify(progress));
    assert.equal(progress.kind,'advanced');
    const failed=worker.inspect(started.instance_sha256);
    assert.equal(failed.step_index,0,'the failed provider step is skipped');
    assert.equal(failed.history.some(row=>JSON.parse(row.commitment_json).kind==='definite-step-failure'),true);
    assert.equal(failed.history.some(row=>row.step_index===1&&
      JSON.parse(row.commitment_json).kind==='commit-step'),false);
    assert.deepEqual(exchanges,['/v1/capture']);
    claim=progress.active_claim;assert.ok(claim);
    progress=await worker.advance(claim);
    assert.equal(progress.state,'compensating',JSON.stringify(progress));
    assert.equal(worker.inspect(started.instance_sha256).step_index,-1);
    claim=progress.active_claim;assert.ok(claim);
    progress=await worker.advance(claim);
    assert.equal(progress.state,'compensated',JSON.stringify(progress));
    assert.equal(worker.inspect(started.instance_sha256).state,'compensated');
    passed=true;
  }finally{
    if(!passed)process.stderr.write('C13_TEST_DIAGNOSTIC '+JSON.stringify({exchanges,peerEvents})+'\n');
    relay?.close();
    if(consumerRuntime)await consumerRuntime.close();
    if(producerRuntime)await producerRuntime.close();
    journalDb?.close();
    if(auth)await auth.close();
    if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}
    if(sourceHandle)try{source.dispose(sourceHandle);}catch{}
    if(peer.exitCode===null){peer.send('close');await once(peer,'exit');}
    if(!passed&&process.env.C13_KEEP_FAILED==='1')
      process.stderr.write('C13_TEST_FILES '+JSON.stringify({root,work})+'\n');
    else{rmSync(path.dirname(root),{recursive:true,force:true});rmSync(work,{recursive:true,force:true});}
  }
});
