import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createGenericHttpCompositionOwner,createGenericBundledApplicationOwner,requireGenericCompositionRuntime} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {createGenericHttpHandler,associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const evidence=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const cases=[
 {name:'CaseDesk',root:path.join(evidence,'C14/three-app-authoring-contract-001/casedesk'),read:'CaseDeskHttp.Read',write:'CaseDeskHttp.Resolve',entry:'CaseDesk.ResolveCaseEntry'},
 {name:'Schedule',root:path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture'),read:'ScheduleHttp.ReadDay',write:'ScheduleHttp.Reserve',entry:'Schedule.ReserveBookingEntry'},
];
function physical(row,work){
 if(row.name==='Schedule')return {sourcePath:path.join(row.root,'business.alch'),profilePath:path.join(row.root,'contracts/selected-profile.json'),httpProfilePath:path.join(row.root,'contracts/http-profile.json')};
 const root=path.join(work,'authored');mkdirSync(path.join(root,'contracts'),{recursive:true});
 writeFileSync(path.join(root,'business.alch'),readFileSync(path.join(row.root,'business.alch')));
 const profileText=readFileSync(path.join(row.root,'selected-profile.json'),'utf8'),profile=JSON.parse(profileText);
 writeFileSync(path.join(root,'contracts/selected-profile.json'),profileText);
 writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}}));
 writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds));
 writeFileSync(path.join(root,'contracts/http-profile.json'),readFileSync(path.join(row.root,'http-profile.json')));
 return {sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')};
}
for(const row of cases)test(`C14 ${row.name} accepted original HTTP owner binds its checked two-route plan`,async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-http-owner-')),input=physical(row,work),owner=createGenericHttpCompositionOwner();let handle,generated,generatedHandle;
 try{
  handle=await owner.prepare(input);const inspection=owner.inspect(handle);
  assert.deepEqual(inspection.http_contract.entries.map(entry=>entry.route.id),[row.read,row.write]);
  assert.equal(inspection.source.original_files.find(file=>file.role==='http-profile')?.model_path,'contracts/http-profile.json');
  const review=owner.review(handle,'C14-http-source');owner.accept(handle,{decision_id:'C14-http-source',owner:'C14-http-source',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'decision.json'));
  const binding=requireGenericCompositionRuntime(owner,handle),read=binding.plans.bindHttpEntry(binding.application,row.read),write=binding.plans.bindHttpEntry(binding.application,row.write);
  assert.equal(binding.plans.inspectHttpEntry(read).route.method,'GET');assert.equal(binding.plans.inspectHttpEntry(write).route.method,'POST');
  assert.equal(binding.plans.inspectHttpApplication(binding.application).transport_semantics_sha256,inspection.transport_semantics_sha256);
  assert.throws(()=>binding.plans.bindHttpEntry(binding.application,'Other.Unknown'),error=>error.diagnostics?.[0]?.code==='UnknownReference');
  const output=path.join(work,'generated'),manifest=owner.generate(handle,{entry:row.entry,outputDirectory:output});
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8')),bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.deepEqual(system.nodes.filter(node=>node.kind==='injected-http-handler').map(node=>node.route.id),[row.read,row.write]);
  assert.deepEqual(bridge.links.filter(link=>link.transport_semantics_sha256===inspection.transport_semantics_sha256).map(link=>link.mapping),inspection.http_contract.entries.map(entry=>entry.route.response_mapping));
  assert.ok(manifest.files.some(file=>file.path==='http-plan.json'));
  const modulePath=path.join(output,'application.mjs'),bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(new URL('file://'+modulePath).href,bundle);generatedHandle=await generated.prepare();
  const fresh=generated.inspect(generatedHandle);assert.equal(fresh.transport_semantics_sha256,inspection.transport_semantics_sha256);
  assert.deepEqual(fresh.http_contract.entries.map(entry=>entry.route.id),[row.read,row.write]);
 }finally{if(generatedHandle)generated.dispose(generatedHandle);if(handle)owner.dispose(handle);rmSync(work,{recursive:true,force:true});}
});

test('C14 generated CaseDesk GET and POST use original Auth, transaction, and response Mapping',async()=>{
 const row=cases[0],work=mkdtempSync(path.join(tmpdir(),'craft-c14-http-runtime-')),input=physical(row,work),owner=createGenericHttpCompositionOwner();
 let handle,generated,generatedHandle,auth,setup,runtime;
 try{
  handle=await owner.prepare(input);const review=owner.review(handle,'C14-http-runtime-source');owner.accept(handle,{decision_id:'C14-http-runtime-source',owner:'C14-http-runtime-source',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'source-decision.json'));
  const output=path.join(work,'generated');owner.generate(handle,{entry:row.entry,outputDirectory:output});
  const modulePath=path.join(output,'application.mjs'),bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(new URL('file://'+modulePath).href,bundle);generatedHandle=await generated.prepare();
  const freshReview=generated.review(generatedHandle,'C14-http-runtime-generated');generated.accept(generatedHandle,{decision_id:'C14-http-runtime-generated',owner:'C14-http-runtime-generated',outcome:'accepted',reviewed_digest:freshReview.review_sha256},path.join(work,'generated-decision.json'));
  const subject='c14-casedesk-user';auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:subject,evidence:'c14-casedesk-evidence',session:'c14-casedesk-session'}],grants:[{subject,entry:'CaseDesk.ReadCaseEntry'},{subject,entry:row.entry}]});
  setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'CaseDeskService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(row.root,'fixture-rows.json'))));await setup.runtime.close();
  runtime=await generated.openRuntime(generatedHandle,{service:'CaseDeskService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  const read=createGenericHttpHandler(generated,generatedHandle,runtime,row.read),write=createGenericHttpHandler(generated,generatedHandle,runtime,row.write);
  const anonymous=await read(new Request('http://casedesk.invalid/api/cases/7'));
  assert.equal(anonymous.status,401);assert.equal((await anonymous.json()).code,'AuthenticationRequired');
  const get=new Request('http://casedesk.invalid/api/cases/7');associateGenericHttpFixtureRequest(auth,read,get,subject);
  const readResponse=await read(get),readBody=await readResponse.json();assert.equal(readResponse.status,200,JSON.stringify(readBody));assert.equal(readBody.kind,'returned');assert.ok(readBody.fuel.response_fuel_used>0);assert.equal(readBody.value.caseId,'7');
  const post=new Request('http://casedesk.invalid/api/cases/resolve',{method:'POST',headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from('c14-casedesk-resolve-7').toString('base64url')},body:JSON.stringify({caseId:'7',proposed:{caseId:'7',resolutionCode:'42'}})});
  associateGenericHttpFixtureRequest(auth,write,post,subject);
  const writeResponse=await write(post),writeBody=await writeResponse.json();assert.equal(writeResponse.status,200,JSON.stringify(writeBody));assert.equal(writeBody.kind,'returned');assert.equal(writeBody.observation.kind,'committed');assert.ok(writeBody.fuel.response_fuel_used>0);assert.deepEqual(writeBody.value,{caseId:'7',resolutionCode:'42'});
 }finally{if(runtime)await runtime.close();if(auth)await auth.close();if(generatedHandle)generated.dispose(generatedHandle);if(handle)owner.dispose(handle);rmSync(work,{recursive:true,force:true});}
});
