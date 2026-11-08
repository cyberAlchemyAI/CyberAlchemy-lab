import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {createGenericHttpHandler,associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C14/three-app-authoring-contract-001/casedesk');
const oracle=JSON.parse(readFileSync(path.join(source,'ORACLE.json'),'utf8'));
const entry='CaseDesk.ResolveCaseEntry',readEntry='CaseDesk.ReadCaseEntry';
const readRoute='CaseDeskHttp.Read',writeRoute='CaseDeskHttp.Resolve';
const subject='c14-case-owner',reader='c14-case-reader';
const accepted=(owner,handle,label,file)=>{const review=owner.review(handle,label);owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},file);};
const quote=value=>'"'+value.replaceAll('"','""')+'"';

function physicalSource(work,routePrefix=null){
 const root=path.join(work,'authored');mkdirSync(path.join(root,'contracts'),{recursive:true});
 cpSync(path.join(source,'business.alch'),path.join(root,'business.alch'));
 cpSync(path.join(source,'selected-profile.json'),path.join(root,'contracts/selected-profile.json'));
 cpSync(path.join(source,'http-profile.json'),path.join(root,'contracts/http-profile.json'));
 if(routePrefix!==null){
  const profile=JSON.parse(readFileSync(path.join(root,'contracts/http-profile.json'),'utf8'));
  profile.id='CaseDeskAlternativeHttp';profile.route_prefix=routePrefix;
  writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(profile,null,2)+'\n');
 }
 const profile=JSON.parse(readFileSync(path.join(source,'selected-profile.json'),'utf8'));
 writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}},null,2)+'\n');
 writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds,null,2)+'\n');
 return root;
}
function snapshot(runtime,storePath){
 const db=new DatabaseSync(storePath,{readOnly:true});
 try{
  const table=runtime.inspect().storage.tables.find(row=>row.entity==='CaseDesk.CaseFile');
  assert.ok(table);
  return {
   cases:db.prepare('SELECT hex('+quote(table.row_column)+') AS row FROM '+quote(table.physical_name)+' ORDER BY row').all().map(row=>JSON.parse(Buffer.from(row.row,'hex').toString('utf8'))),
   journal:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n,
  };
 }finally{db.close();}
}
function request(input,key){
 return new Request('http://cases.invalid/api/cases/resolve',{method:'POST',headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from(key).toString('base64url')},body:JSON.stringify(input)});
}

test('C14 independent CaseDesk source generates a protected API with durable resolve and replay',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-casedesk-runtime-'));
 const root=physicalSource(work),original=createGenericHttpCompositionOwner();
 let originalHandle,generated,generatedHandle,auth,setup,runtime;
 try{
  originalHandle=await original.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')});
  accepted(original,originalHandle,'C14-CaseDesk-source',path.join(work,'source-decision.json'));
  const output=path.join(work,'generated');original.generate(originalHandle,{entry,outputDirectory:output});
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.ok(system.nodes.some(node=>node.id==='storage:CaseDeskService'&&node.kind==='sqlite-atomic-command-store'));
  assert.ok(system.nodes.some(node=>node.kind==='injected-http-handler'&&node.route.id===writeRoute));
  assert.ok(bridge.links.some(link=>link.business===entry&&link.system==='generated:'+entry));
  const modulePath=path.join(output,'application.mjs');
  const bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);
  generatedHandle=await generated.prepare();
  accepted(generated,generatedHandle,'C14-CaseDesk-generated',path.join(work,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:subject,evidence:'case-owner-evidence',session:'case-owner-session'},{id:reader,evidence:'case-reader-evidence',session:'case-reader-session'}],grants:[{subject,entry},{subject,entry:readEntry},{subject:reader,entry:readEntry}]});
  setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'CaseDeskService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(source,'fixture-rows.json'))));
  await setup.runtime.close();
  runtime=await generated.openRuntime(generatedHandle,{service:'CaseDeskService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  let read=createGenericHttpHandler(generated,generatedHandle,runtime,readRoute);
  let write=createGenericHttpHandler(generated,generatedHandle,runtime,writeRoute);
  const readRequest=new Request('http://cases.invalid/api/cases/7');
  associateGenericHttpFixtureRequest(auth,read,readRequest,subject);
  const readResult=await read(readRequest);
  assert.equal(readResult.status,200);
  assert.deepEqual((await readResult.json()).value,oracle.positive.find(row=>row.id==='read-open').expected_value);
  const before=snapshot(runtime,setup.storePath);
  const resolve=oracle.positive.find(row=>row.id==='resolve-once');
  const missingRequest=request({caseId:'8',proposed:{caseId:'8',resolutionCode:'42'}},'c14-missing-case');
  associateGenericHttpFixtureRequest(auth,write,missingRequest,subject);
  const missing=await write(missingRequest),missingBody=await missing.json();
  assert.equal(missing.status,422,JSON.stringify(missingBody));
  assert.equal(missingBody.code,'case-not-found');
  const afterMissing=snapshot(runtime,setup.storePath);
  assert.deepEqual(afterMissing.cases,before.cases);
  assert.equal(afterMissing.journal,before.journal+1);
  const deniedRequest=request(resolve.input,'c14-denied-case');
  associateGenericHttpFixtureRequest(auth,write,deniedRequest,reader);
  const denied=await write(deniedRequest);assert.equal(denied.status,403);
  assert.equal((await denied.json()).code,'PermissionDenied');
  assert.deepEqual(snapshot(runtime,setup.storePath),afterMissing);
  const resolveRequest=request(resolve.input,resolve.client_key);
  associateGenericHttpFixtureRequest(auth,write,resolveRequest,subject);
  const committed=await write(resolveRequest),committedBody=await committed.json();
  assert.equal(committed.status,200,JSON.stringify(committedBody));
  assert.equal(committedBody.observation.kind,'committed');
  assert.deepEqual(committedBody.value,resolve.expected_outcome.value);
  const after=snapshot(runtime,setup.storePath);
  assert.deepEqual(after.cases,[resolve.expected_case_row]);
  assert.equal(after.journal-afterMissing.journal,resolve.expected_journal_records);
  await runtime.close();runtime=null;
  runtime=await generated.openRuntime(generatedHandle,{service:'CaseDeskService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  write=createGenericHttpHandler(generated,generatedHandle,runtime,writeRoute);
  const replayRequest=request(resolve.input,resolve.client_key);
  associateGenericHttpFixtureRequest(auth,write,replayRequest,subject);
  const replayed=await write(replayRequest),replayedBody=await replayed.json();
  assert.equal(replayed.status,200,JSON.stringify(replayedBody));
  assert.equal(replayedBody.observation.kind,'replayed');
  assert.deepEqual(replayedBody.value,resolve.expected_outcome.value);
  assert.deepEqual(snapshot(runtime,setup.storePath),after);
  const againRequest=request(resolve.input,'c14-new-key-resolved');
  associateGenericHttpFixtureRequest(auth,write,againRequest,subject);
  const again=await write(againRequest),againBody=await again.json();
  assert.equal(again.status,422,JSON.stringify(againBody));
  assert.equal(againBody.code,'case-not-resolvable');
  const afterAgain=snapshot(runtime,setup.storePath);
  assert.deepEqual(afterAgain.cases,after.cases);
  assert.equal(afterAgain.journal,after.journal+1);
 }finally{
  if(runtime)await runtime.close();
  if(setup?.runtime)try{await setup.runtime.close();}catch{}
  if(auth)await auth.close();
  if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}
  if(originalHandle)try{original.dispose(originalHandle);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});

test('C14 authored CaseDesk HTTP profile changes the generated route without compiler edits',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-casedesk-profile-'));
 const root=physicalSource(work,'/review'),original=createGenericHttpCompositionOwner();
 let originalHandle,generated,generatedHandle,auth,setup,runtime;
 try{
  originalHandle=await original.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')});
  const inspected=original.inspect(originalHandle);
  assert.equal(inspected.http_contract.profile.route_prefix,'/review');
  accepted(original,originalHandle,'C14-CaseDesk-alternative-source',path.join(work,'source-decision.json'));
  const output=path.join(work,'generated');original.generate(originalHandle,{entry,outputDirectory:output});
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  assert.ok(system.nodes.some(node=>node.kind==='injected-http-handler'&&node.route.id===readRoute));
  const modulePath=path.join(output,'application.mjs');
  const bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);
  generatedHandle=await generated.prepare();
  accepted(generated,generatedHandle,'C14-CaseDesk-alternative-generated',path.join(work,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:subject,evidence:'case-profile-evidence',session:'case-profile-session'}],grants:[{subject,entry:readEntry}]});
  setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'CaseDeskService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(source,'fixture-rows.json'))));
  await setup.runtime.close();
  runtime=await generated.openRuntime(generatedHandle,{service:'CaseDeskService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  const read=createGenericHttpHandler(generated,generatedHandle,runtime,readRoute);
  const changedRequest=new Request('http://cases.invalid/review/cases/7');
  associateGenericHttpFixtureRequest(auth,read,changedRequest,subject);
  const changed=await read(changedRequest);
  assert.equal(changed.status,200);
  assert.deepEqual((await changed.json()).value,oracle.positive.find(row=>row.id==='read-open').expected_value);
  const oldRequest=new Request('http://cases.invalid/api/cases/7');
  associateGenericHttpFixtureRequest(auth,read,oldRequest,subject);
  const old=await read(oldRequest);
  assert.equal(old.status,404);
 }finally{
  if(runtime)await runtime.close();
  if(setup?.runtime)try{await setup.runtime.close();}catch{}
  if(auth)await auth.close();
  if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}
  if(originalHandle)try{original.dispose(originalHandle);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});
