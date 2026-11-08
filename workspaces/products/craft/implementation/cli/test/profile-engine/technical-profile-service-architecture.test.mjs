import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.ts';
import {createTechnicalProfileServiceArchitectureOwner} from '../../src/profile-engine/technical-profile-service-architecture.ts';
import {createGenericHttpCompositionOwner} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.ts';

const repository=path.resolve(import.meta.dirname,'../../../../../../..'),evidence=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const profileFixture=path.join(import.meta.dirname,'fixtures/technical-service-architecture');
const sha=value=>createHash('sha256').update(value).digest('hex');
const cases=[
 {name:'CaseDesk',root:path.join(evidence,'C14/three-app-authoring-contract-001/casedesk'),read:'CaseDesk.ReadCaseEntry',write:'CaseDesk.ResolveCaseEntry',service:'CaseDeskService'},
 {name:'Schedule',root:path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture'),read:'Schedule.ReadDayScheduleEntry',write:'Schedule.ReserveBookingEntry',service:'ScheduleService'},
];
function copyApplication(row,root){
 mkdirSync(path.join(root,'contracts'),{recursive:true});cpSync(path.join(row.root,'business.alch'),path.join(root,'business.alch'));
 const profile=JSON.parse(readFileSync(path.join(row.root,row.name==='CaseDesk'?'selected-profile.json':'contracts/selected-profile.json'),'utf8'));
 writeFileSync(path.join(root,'contracts/selected-profile.json'),JSON.stringify(profile));
 cpSync(path.join(row.root,row.name==='CaseDesk'?'http-profile.json':'contracts/http-profile.json'),path.join(root,'contracts/http-profile.json'));
 writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}}));
 writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds));
 return {sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')};
}
function accept(sdk,application,file){const review=sdk.review(application,'profile-service-architecture');sdk.accept(application,{decision_id:'profile-service-architecture',owner:'profile-service-architecture',outcome:'accepted',reviewed_digest:review.review_sha256},file);}

function businessSnapshot(storePath,storage){const db=new DatabaseSync(storePath,{readOnly:true});try{return storage.tables.map(table=>({entity:table.entity,table:table.physical_name,rows:db.prepare('SELECT * FROM "'+table.physical_name.replaceAll('"','""')+'"').all().sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)))}));}finally{db.close();}}

test('service architecture requires a genuine checked technical source owner',()=>{
 assert.throws(()=>createTechnicalProfileServiceArchitectureOwner({sourceOwner:{inspect:()=>({topology:{layout:'ServiceAssembly'}})},sourceHandle:{},sdk:{},application:{}}),/original technical-profile source owner/);
});

for(const row of cases)test(`source-selected ${row.name} entry and service layouts preserve actual protected API behavior`,async t=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-profile-service-')),appRoot=path.join(work,'app'),input=copyApplication(row,appRoot),originalBytes=readFileSync(input.sourcePath),sdk=createGenericHttpCompositionOwner(),sourceOwner=createTechnicalProfileSourceOwner();
 const handles=[];let application,runtime,auth;
 try{
  application=await sdk.prepare(input);accept(sdk,application,path.join(work,'accept.json'));
  const inspection=sdk.inspect(application),readRoute=inspection.http_contract.entries.find(e=>e.route.entry===row.read),writeRoute=inspection.http_contract.entries.find(e=>e.route.entry===row.write);
  assert.ok(readRoute);assert.ok(writeRoute);
  const oracle=JSON.parse(readFileSync(path.join(row.root,row.name==='CaseDesk'?'ORACLE.json':'http-oracle.json'),'utf8'));
  const readValue=row.name==='CaseDesk'?oracle.positive.find(c=>c.id==='read-open').expected_value:oracle.cases.find(c=>c.id==='schedule-read-empty').expected_value;
  const writeCase=row.name==='CaseDesk'?oracle.positive.find(c=>c.id==='resolve-once'):oracle.cases.find(c=>c.id==='schedule-reserve-commit');
  const expectedValue=writeCase.expected_outcome?.value??writeCase.expected_value,graphKinds=[];
  for(const layout of ['EntryModules','ServiceAssembly']){
   const technicalRoot=path.join(work,'technical-'+layout);cpSync(profileFixture,technicalRoot,{recursive:true});
   const sourceHandle=sourceOwner.prepare({sourceRoot:technicalRoot,manifestPath:path.join(technicalRoot,layout+'.profile.json')});handles.push(sourceHandle);
   assert.equal(sourceOwner.inspect(sourceHandle).topology.layout,layout);
   const owner=createTechnicalProfileServiceArchitectureOwner({sourceOwner,sourceHandle,sdk,application}),output=path.join(work,'output-'+layout),artifact=owner.emit({outputDirectory:output}),manifest=owner.inspect(artifact);
   assert.equal(manifest.layout,layout);assert.equal(manifest.entries.length,2);assert.equal(manifest.technical_source.mapping,'Profiles.ProtectedServiceArchitecture.Select');
   const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8')),bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
   const kinds=system.nodes.map(node=>node.kind);graphKinds.push(kinds);
   assert.equal(kinds.includes('generated-service-export'),layout==='ServiceAssembly');
   assert.ok(bridge.links.some(link=>link.business===row.write&&link.technical_mapping==='Profiles.ProtectedServiceArchitecture.Select'));
   const nativeRoot=path.join(work,'runtime-'+layout);mkdirSync(nativeRoot);
   auth=await createGenericAuthFixture(sdk,application,{ownedDirectory:path.join(nativeRoot,'auth'),subjects:[{id:'owner',evidence:'owner-evidence',session:'owner-session'},{id:'reader',evidence:'reader-evidence',session:'reader-session'}],grants:[{subject:'owner',entry:row.read},{subject:'owner',entry:row.write},{subject:'reader',entry:row.read}]});
   const setup=await prepareGenericFixtureRuntime(sdk,application,{service:row.service,ownedDirectory:path.join(nativeRoot,'store'),nativeAuth:auth.nativeAuth});loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(row.root,'fixture-rows.json'))));await setup.runtime.close();
   runtime=await owner.openRuntime(artifact,{service:row.service,storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
   const read=await owner.bindHttp(artifact,runtime,readRoute.route.id),write=await owner.bindHttp(artifact,runtime,writeRoute.route.id);
   const getUrl='https://test.invalid'+inspection.http_contract.profile.route_prefix+readRoute.route.path.replace(/\{[^}]+\}/g,'7');
   assert.equal((await read(new Request(getUrl))).status,401);
   const get=new Request(getUrl);associateGenericHttpFixtureRequest(auth,read,get,'owner');const readResult=await read(get);assert.equal(readResult.status,200);assert.deepEqual((await readResult.json()).value,readValue);
   const post=(key,input=writeCase.input)=>new Request('https://test.invalid'+inspection.http_contract.profile.route_prefix+writeRoute.route.path,{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':Buffer.from(key).toString('base64url')},body:JSON.stringify(input)});
   const denied=post('denied');associateGenericHttpFixtureRequest(auth,write,denied,'reader');assert.equal((await write(denied)).status,403);
   const command=post(writeCase.client_key);associateGenericHttpFixtureRequest(auth,write,command,'owner');const commit=await write(command),committed=await commit.json();assert.equal(commit.status,200,JSON.stringify(committed));assert.equal(committed.observation.kind,'committed');assert.deepEqual(committed.value,expectedValue);
   await runtime.close();runtime=await owner.openRuntime(artifact,{service:row.service,storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});const replayHandler=await owner.bindHttp(artifact,runtime,writeRoute.route.id),retry=post(writeCase.client_key);associateGenericHttpFixtureRequest(auth,replayHandler,retry,'owner');const replay=await replayHandler(retry),replayed=await replay.json();assert.equal(replay.status,200,JSON.stringify(replayed));assert.equal(replayed.observation.kind,'replayed');assert.deepEqual(replayed.value,expectedValue);
   const negative=row.name==='CaseDesk'?oracle.negative.find(c=>c.id==='already-resolved-new-key'):oracle.cases.find(c=>c.id==='schedule-overlap-after-commit');assert.ok(negative);assert.equal(negative.expected_business_updates??negative.expected_business_revision_delta,0);const selectedEntry=manifest.entries.find(entry=>entry.entry===row.write),storage=JSON.parse(readFileSync(path.join(output,selectedEntry.directory,'storage/schema.json'),'utf8')),beforeBusiness=businessSnapshot(setup.storePath,storage),inputNegative=negative.input??writeCase.input,newKey=negative.client_key??negative.id;assert.notEqual(newKey,writeCase.client_key,'authored rejection uses a fresh command, not replay');const rejectedRequest=post(newKey,inputNegative);associateGenericHttpFixtureRequest(auth,replayHandler,rejectedRequest,'owner');const rejectedResponse=await replayHandler(rejectedRequest),rejected=await rejectedResponse.json();if(negative.expected_status!==undefined)assert.equal(rejectedResponse.status,negative.expected_status);assert.equal(rejected.kind,negative.expected_outcome?.kind??'rejected');assert.equal(rejected.code,negative.expected_rejection??negative.expected_outcome.code);assert.equal(rejected.observation.kind,'business-rejected');const afterBusiness=businessSnapshot(setup.storePath,storage);assert.deepEqual(afterBusiness,beforeBusiness,'authored rejection changes neither business values nor hidden business revisions');const afterRead=await owner.bindHttp(artifact,runtime,readRoute.route.id),readAfterRequest=new Request(getUrl);associateGenericHttpFixtureRequest(auth,afterRead,readAfterRequest,'owner');const afterValue=(await(await afterRead(readAfterRequest)).json()).value;if(row.name==='CaseDesk')assert.deepEqual(afterValue,writeCase.expected_case_row);else{assert.equal(afterValue.bookings.length,negative.expected_reservation_count);assert.deepEqual(afterValue.bookings[0],expectedValue);}t.diagnostic(JSON.stringify({schema_version:'craft.technical-service-business-rejection/v1',domain:row.name,layout,oracle:{path:path.relative(repository,path.join(row.root,row.name==='CaseDesk'?'ORACLE.json':'http-oracle.json')),sha256:sha(readFileSync(path.join(row.root,row.name==='CaseDesk'?'ORACLE.json':'http-oracle.json'))),case:negative.id},actual:{kind:rejected.kind,code:rejected.code,observation:rejected.observation.kind},business_before_sha256:sha(JSON.stringify(beforeBusiness)),business_after_sha256:sha(JSON.stringify(afterBusiness)),business_state_unchanged:true}));
   await runtime.close();runtime=null;await auth.close();auth=null;
   assert.equal(sha(readFileSync(input.sourcePath)),sha(originalBytes),'business model bytes unchanged');
   owner.inspect(artifact);
   writeFileSync(path.join(technicalRoot,'profile.alch'),readFileSync(path.join(technicalRoot,'profile.alch'),'utf8')+'\n');assert.throws(()=>owner.inspect(artifact),/changed|STALE/);
  }
  assert.notDeepEqual(graphKinds[0],graphKinds[1],'source-selected grouping changes actual generated system structure');
 }finally{if(runtime)try{await runtime.close();}catch{}if(auth)try{await auth.close();}catch{}for(const handle of handles)try{sourceOwner.dispose(handle);}catch{}if(application)try{sdk.dispose(application);}catch{}rmSync(work,{recursive:true,force:true});}
});
