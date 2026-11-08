import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericHttpCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {createGenericHttpHandler,associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixture=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C09/schedule-http-second-domain-source-001/fixture');
const oracle=JSON.parse(readFileSync(path.join(fixture,'http-oracle.json'),'utf8'));
const accept=(owner,handle,id,file)=>{const review=owner.review(handle,id);owner.accept(handle,
 {decision_id:id,owner:id,outcome:'accepted',reviewed_digest:review.review_sha256},file);};

test('C14 Schedule selects a second HTTP structure from unchanged business source',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-schedule-profile-'));
 const authored=path.join(work,'authored');cpSync(fixture,authored,{recursive:true});
 const originalBusiness=readFileSync(path.join(fixture,'business.alch'));
 const sourcePath=path.join(authored,'business.alch'),profilePath=path.join(authored,'contracts/selected-profile.json'),
  httpProfilePath=path.join(authored,'contracts/http-profile.json');
 const http=JSON.parse(readFileSync(httpProfilePath,'utf8'));
 writeFileSync(httpProfilePath,JSON.stringify({...http,route_prefix:'/schedule'},null,2)+'\n');
 assert.deepEqual(readFileSync(sourcePath),originalBusiness);
 const source=createGenericHttpCompositionOwner();let handle,generated,generatedHandle,auth,setup,runtime;
 try{
  handle=await source.prepare({sourcePath,profilePath,httpProfilePath});
  assert.equal(source.inspect(handle).http_contract.profile.route_prefix,'/schedule');
  accept(source,handle,'C14-Schedule-alternate-source',path.join(work,'source-decision.json'));
  const output=path.join(work,'generated');source.generate(handle,{entry:oracle.root_entry,outputDirectory:output});
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  assert.ok(system.nodes.some(node=>node.kind==='injected-http-handler'&&node.route.id===oracle.routes.read));
  const modulePath=path.join(output,'application.mjs');
  const bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);
  generatedHandle=await generated.prepare();
  accept(generated,generatedHandle,'C14-Schedule-alternate-generated',path.join(work,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),
   subjects:[{id:oracle.subject,evidence:'alternate-schedule-evidence',session:'alternate-schedule-session'}],
   grants:[{subject:oracle.subject,entry:oracle.child_entry}]});
  setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'ScheduleService',
   ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(fixture,'fixture-rows.json'))));
  await setup.runtime.close();
  runtime=await generated.openRuntime(generatedHandle,{service:'ScheduleService',storePath:setup.storePath,
   mode:'reopen',nativeAuth:auth.nativeAuth});
  const read=createGenericHttpHandler(generated,generatedHandle,runtime,oracle.routes.read);
  const newRequest=new Request('http://schedule.invalid/schedule/days/7');
  associateGenericHttpFixtureRequest(auth,read,newRequest,oracle.subject);
  const response=await read(newRequest),body=await response.json();
  assert.equal(response.status,200,JSON.stringify(body));
  assert.deepEqual(body.value,oracle.cases.find(row=>row.id==='schedule-read-empty').expected_value);
  const oldRequest=new Request('http://schedule.invalid/api/days/7');
  associateGenericHttpFixtureRequest(auth,read,oldRequest,oracle.subject);
  assert.equal((await read(oldRequest)).status,404);
 }finally{
  if(runtime)await runtime.close();
  if(setup?.runtime)try{await setup.runtime.close();}catch{}
  if(auth)await auth.close();
  if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}
  if(handle)try{source.dispose(handle);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});
