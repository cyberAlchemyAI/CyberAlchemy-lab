import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {createGenericHttpHandler,associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixture=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C09/schedule-http-second-domain-source-001/fixture');
const oracle=JSON.parse(readFileSync(path.join(fixture,'http-oracle.json'),'utf8'));
const sourcePath=path.join(fixture,'business.alch');
const profilePath=path.join(fixture,'contracts/selected-profile.json');
const httpProfilePath=path.join(fixture,'contracts/http-profile.json');
const entry=oracle.root_entry,readEntry=oracle.child_entry,subject=oracle.subject,reader='c14-schedule-reader';
const readRoute=oracle.routes.read,writeRoute=oracle.routes.reserve;
const accepted=(owner,handle,label,file)=>{const review=owner.review(handle,label);owner.accept(handle,{decision_id:label,owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},file);};
const reserve=(item,key)=>new Request('http://schedule.invalid/api/reservations',{method:'POST',headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from(key).toString('base64url')},body:JSON.stringify(item.input)});
const quote=value=>'"'+value.replaceAll('"','""')+'"';
function snapshot(runtime,storePath){
 const db=new DatabaseSync(storePath,{readOnly:true});
 try{return {rows:runtime.inspect().storage.tables.map(table=>({entity:table.entity,
  rows:db.prepare('SELECT hex('+quote(table.row_column)+') AS row,hex('+quote(table.revision_column)+') AS revision FROM '+quote(table.physical_name)+' ORDER BY row').all()})),
  metadata:db.prepare('SELECT hex(revision_counter) AS revision,command_count,command_bytes FROM _craft_generic_metadata WHERE id=1').get(),
  journal_count:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n};}
 finally{db.close();}
}
function reservations(observed){
 const table=observed.rows.find(row=>row.entity==='Schedule.Reservation');
 assert.ok(table);
 return table.rows.map(row=>JSON.parse(Buffer.from(row.row,'hex').toString('utf8')));
}

test('C14 independent Schedule generated API runs original Auth and persistent booking transaction',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-schedule-runtime-'));
 const source=createGenericHttpCompositionOwner();let handle,generated,generatedHandle,auth,runtime,setup;
 try{
  handle=await source.prepare({sourcePath,profilePath,httpProfilePath});
  const inspection=source.inspect(handle);
  assert.deepEqual(inspection.http_contract.entries.map(row=>row.route.id),[readRoute,writeRoute]);
  accepted(source,handle,'C14-Schedule-source',path.join(work,'source-decision.json'));
  const output=path.join(work,'generated'),manifest=source.generate(handle,{entry,outputDirectory:output});
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.ok(system.nodes.some(node=>node.id==='storage:ScheduleService'&&node.kind==='sqlite-atomic-command-store'));
  assert.ok(system.nodes.some(node=>node.kind==='injected-http-handler'&&node.route.id===writeRoute));
  assert.ok(bridge.links.some(link=>link.business===entry&&link.system==='generated:'+entry));
  assert.ok(manifest.files.some(file=>file.path==='application.mjs'));
  const modulePath=path.join(output,'application.mjs');
  const bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);
  generatedHandle=await generated.prepare();
  assert.equal(generated.inspect(generatedHandle).transport_semantics_sha256,inspection.transport_semantics_sha256);
  accepted(generated,generatedHandle,'C14-Schedule-generated',path.join(work,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:subject,evidence:'c14-schedule-evidence',session:'c14-schedule-session'},{id:reader,evidence:'c14-reader-evidence',session:'c14-reader-session'}],grants:[{subject,entry},{subject,entry:readEntry},{subject:reader,entry:readEntry}]});
  setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'ScheduleService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(fixture,'fixture-rows.json'))));
  await setup.runtime.close();
  runtime=await generated.openRuntime(generatedHandle,{service:'ScheduleService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  let read=createGenericHttpHandler(generated,generatedHandle,runtime,readRoute);
  let write=createGenericHttpHandler(generated,generatedHandle,runtime,writeRoute);
  const anonymous=await read(new Request('http://schedule.invalid/api/days/7'));
  assert.equal(anonymous.status,401);
  assert.equal((await anonymous.json()).code,'AuthenticationRequired');
  const get=new Request('http://schedule.invalid/api/days/7');
  associateGenericHttpFixtureRequest(auth,read,get,subject);
  const readResult=await read(get),readBody=await readResult.json();
  assert.equal(readResult.status,200,JSON.stringify(readBody));
  assert.deepEqual(readBody.value,oracle.cases.find(row=>row.id==='schedule-read-empty').expected_value);
  const before=snapshot(runtime,setup.storePath);
  assert.deepEqual(reservations(before),[]);
  const commit=oracle.cases.find(row=>row.id==='schedule-reserve-commit');
  const deniedRequest=reserve(commit,'c14-denied-101');
  associateGenericHttpFixtureRequest(auth,write,deniedRequest,reader);
  const denied=await write(deniedRequest);assert.equal(denied.status,403);
  assert.equal((await denied.json()).code,'PermissionDenied');
  assert.deepEqual(snapshot(runtime,setup.storePath),before);
  const request=reserve(commit,commit.client_key);
  associateGenericHttpFixtureRequest(auth,write,request,subject);
  const committed=await write(request),committedBody=await committed.json();
  assert.equal(committed.status,200,JSON.stringify(committedBody));
  assert.equal(committedBody.observation.kind,'committed');
  assert.deepEqual(committedBody.value,commit.expected_value);
  const after=snapshot(runtime,setup.storePath);
  assert.deepEqual(reservations(after),[{...commit.expected_value,dayId:'7'}]);
  assert.equal(after.journal_count-before.journal_count,1);
  assert.equal(BigInt('0x'+after.metadata.revision)-BigInt('0x'+before.metadata.revision),2n);
  await runtime.close();runtime=null;
  runtime=await generated.openRuntime(generatedHandle,{service:'ScheduleService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  read=createGenericHttpHandler(generated,generatedHandle,runtime,readRoute);
  write=createGenericHttpHandler(generated,generatedHandle,runtime,writeRoute);
  const replayRequest=reserve(commit,commit.client_key);
  associateGenericHttpFixtureRequest(auth,write,replayRequest,subject);
  const replayed=await write(replayRequest),replayBody=await replayed.json();
  assert.equal(replayed.status,200,JSON.stringify(replayBody));
  assert.equal(replayBody.observation.kind,'replayed');
  assert.deepEqual(replayBody.value,commit.expected_value);
  assert.deepEqual(snapshot(runtime,setup.storePath),after);
  const overlap=oracle.cases.find(row=>row.id==='schedule-overlap-after-commit');
  const overlapRequest=reserve(overlap,overlap.client_key);
  associateGenericHttpFixtureRequest(auth,write,overlapRequest,subject);
  const rejected=await write(overlapRequest),rejectBody=await rejected.json();
  assert.equal(rejected.status,422,JSON.stringify(rejectBody));
  assert.equal(rejectBody.kind,'rejected');
  assert.equal(rejectBody.code,overlap.expected_outcome.code);
  const rejectedState=snapshot(runtime,setup.storePath);
  assert.deepEqual(rejectedState.rows,after.rows);
  assert.equal(rejectedState.metadata.revision,after.metadata.revision);
 }finally{
  if(runtime)await runtime.close();
  if(setup?.runtime)try{await setup.runtime.close();}catch{}
  if(auth)await auth.close();
  if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}
  if(handle)try{source.dispose(handle);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});
