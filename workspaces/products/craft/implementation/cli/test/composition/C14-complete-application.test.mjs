import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,rmSync,symlinkSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericHttpCompositionOwner} from '../../src/generic/public-sdk.ts';
import {createGenericServiceArtifactOwner} from '../../src/generic/service-artifact-owner.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {associateGenericHttpFixtureRequest} from '../../src/generic/http-adapter.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C14/three-app-authoring-contract-001/casedesk');
const readEntry='CaseDesk.ReadCaseEntry',writeEntry='CaseDesk.ResolveCaseEntry';
const readRoute='CaseDeskHttp.Read',writeRoute='CaseDeskHttp.Resolve';
const schedule=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C09/schedule-http-second-domain-source-001/fixture');

test('C14 emits and runs a complete source-bound CaseDesk service with profile GET/POST routes',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-complete-'));
 const root=path.join(work,'authored'),sdk=createGenericHttpCompositionOwner();
 let sourceHandle,auth,setup,application;
 try{
  mkdirSync(path.join(root,'contracts'),{recursive:true});
  cpSync(path.join(source,'business.alch'),path.join(root,'business.alch'));
  cpSync(path.join(source,'selected-profile.json'),path.join(root,'contracts/selected-profile.json'));
  cpSync(path.join(source,'http-profile.json'),path.join(root,'contracts/http-profile.json'));
  const profile=JSON.parse(readFileSync(path.join(source,'selected-profile.json'),'utf8'));
  writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:profile.limits}})+'\n');
  writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(profile.transaction_bounds)+'\n');
  sourceHandle=await sdk.prepare({sourcePath:path.join(root,'business.alch'),profilePath:path.join(root,'contracts/selected-profile.json'),httpProfilePath:path.join(root,'contracts/http-profile.json')});
  const review=sdk.review(sourceHandle,'C14-complete-source');
  sdk.accept(sourceHandle,{decision_id:'C14-complete-source',owner:'C14-complete-source',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'source-decision.json'));
  const owner=createGenericServiceArtifactOwner(sdk,sourceHandle),output=path.join(work,'application');
  assert.throws(()=>owner.emit({outputDirectory:path.join(work,'missing-entry'),entries:[readEntry],requireCompleteApplication:true}),
   error=>error.diagnostics?.[0]?.code==='MissingMapping');
  const artifact=owner.emit({outputDirectory:output,entries:[writeEntry,readEntry],requireCompleteApplication:true});
  const manifest=owner.inspect(artifact);
  assert.equal(manifest.complete_application,true);
  assert.deepEqual(manifest.missing_complete_application_classes,[]);
  assert.doesNotThrow(()=>owner.assertComplete(artifact));
  assert.equal(manifest.services.length,1);
  assert.deepEqual(manifest.services[0].entries.map(entry=>entry.entry),[readEntry,writeEntry]);
  assert.deepEqual(manifest.services[0].entries.flatMap(entry=>entry.http_routes.map(route=>route.id)).sort(),[readRoute,writeRoute].sort());
  const graph=JSON.parse(readFileSync(path.join(output,'application-system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'application-business-system-bridge.json'),'utf8'));
  assert.ok(graph.nodes.some(node=>node.id==='application'&&node.sha256===manifest.application_module_sha256));
  assert.ok(graph.nodes.some(node=>node.id==='CaseDeskService::api:'+readRoute));
  assert.ok(graph.nodes.some(node=>node.id==='CaseDeskService::api:'+writeRoute));
  assert.ok(graph.edges.every(edge=>graph.nodes.some(node=>node.id===edge.from)&&graph.nodes.some(node=>node.id===edge.to)));
  assert.ok(bridge.links.every(link=>graph.nodes.some(node=>node.id===link.system)));
  const packageScope=path.join(work,'node_modules/@domainspec-v2');mkdirSync(packageScope,{recursive:true});
  symlinkSync(fileURLToPath(new URL('../../',import.meta.url)),path.join(packageScope,'cli'),'dir');
  auth=await createGenericAuthFixture(sdk,sourceHandle,{ownedDirectory:path.join(work,'auth'),
   subjects:[{id:'case-owner',evidence:'case-owner-evidence',session:'case-owner-session'},
    {id:'case-reader',evidence:'case-reader-evidence',session:'case-reader-session'}],
   grants:[{subject:'case-owner',entry:readEntry},{subject:'case-owner',entry:writeEntry},{subject:'case-reader',entry:readEntry}]});
  setup=await prepareGenericFixtureRuntime(sdk,sourceHandle,{service:'CaseDeskService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(source,'fixture-rows.json'))));
  const storePath=setup.storePath;
  await setup.runtime.close();setup=null;
  const generated=await import(pathToFileURL(path.join(output,'application.mjs')).href);
  assert.equal(generated.completeApplication,true);
  await assert.rejects(generated.openGeneratedApplication(owner,Object.freeze({kind:artifact.kind}),{CaseDeskService:{}}),
   error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  await assert.rejects(generated.openGeneratedApplication(owner,artifact,{}),/GENERATED_APPLICATION_SERVICE_OPTIONS/);
  application=await generated.openGeneratedApplication(owner,artifact,{CaseDeskService:{storePath,mode:'reopen',nativeAuth:auth.nativeAuth}});
  const serviceModule=await import(pathToFileURL(path.join(output,manifest.services[0].directory,'service.mjs')).href);
  assert.deepEqual(serviceModule.entryIds,[readEntry,writeEntry]);
  assert.equal(typeof serviceModule.createGeneratedServiceOwners()[readEntry],'function');
  const serviceDispatch=await serviceModule.createGeneratedServiceHttpHandlers(application.runtime('CaseDeskService'),owner,artifact);
  assert.equal(typeof serviceDispatch.handlerForRoute(readRoute),'function');
  const dispatch=await application.http('CaseDeskService');
  const request=new Request('http://cases.invalid/api/cases/7');
  associateGenericHttpFixtureRequest(auth,dispatch.handlerForRoute(readRoute),request,'case-owner');
  const read=await dispatch(request);
  assert.equal(read.status,200);
  assert.deepEqual((await read.json()).value,{caseId:'7',resolved:false,resolutionCode:'0'});
  const deniedRequest=new Request('http://cases.invalid/api/cases/resolve',{method:'POST',headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from('c14-denied').toString('base64url')},body:JSON.stringify({caseId:'7',proposed:{caseId:'7',resolutionCode:'42'}})});
  associateGenericHttpFixtureRequest(auth,dispatch.handlerForRoute(writeRoute),deniedRequest,'case-reader');
  const denied=await dispatch(deniedRequest);
  assert.equal(denied.status,403);
  assert.equal((await denied.json()).code,'PermissionDenied');
  const resolveRequest=new Request('http://cases.invalid/api/cases/resolve',{method:'POST',headers:{
   'content-type':'application/json; charset=utf-8',
   'x-craft-command-key':Buffer.from('c14-accepted').toString('base64url')},
   body:JSON.stringify({caseId:'7',proposed:{caseId:'7',resolutionCode:'42'}})});
  associateGenericHttpFixtureRequest(auth,dispatch.handlerForRoute(writeRoute),resolveRequest,'case-owner');
  const resolved=await dispatch(resolveRequest);
  console.error('C14 CaseDesk: generated ResolveCase returned',resolved.status);
  assert.equal(resolved.status,200);
  assert.deepEqual((await resolved.json()).value,{caseId:'7',resolutionCode:'42'});
  const persistedRequest=new Request('http://cases.invalid/api/cases/7');
  associateGenericHttpFixtureRequest(auth,dispatch.handlerForRoute(readRoute),persistedRequest,'case-owner');
  const persisted=await dispatch(persistedRequest);
  assert.equal(persisted.status,200);
  assert.deepEqual((await persisted.json()).value,{caseId:'7',resolved:true,resolutionCode:'42'});
  const method=await dispatch(new Request('http://cases.invalid/api/cases/7',{method:'POST'}));
  assert.equal(method.status,405);
  const missing=await dispatch(new Request('http://cases.invalid/api/absent'));
  assert.equal(missing.status,404);
  await application.close();application=null;
  application=await generated.openGeneratedApplication(owner,artifact,{CaseDeskService:{storePath,mode:'reopen',nativeAuth:auth.nativeAuth}});
  const reopenedDispatch=await application.http('CaseDeskService');
  const reopenedRequest=new Request('http://cases.invalid/api/cases/7');
  associateGenericHttpFixtureRequest(auth,reopenedDispatch.handlerForRoute(readRoute),reopenedRequest,'case-owner');
  const reopened=await reopenedDispatch(reopenedRequest);
  console.error('C14 CaseDesk: reopened generated store returned',reopened.status);
  assert.equal(reopened.status,200);
  assert.deepEqual((await reopened.json()).value,{caseId:'7',resolved:true,resolutionCode:'42'});
  await application.close();application=null;
 }finally{
  if(application)await application.close();
  if(setup?.runtime)await setup.runtime.close();
  if(auth)await auth.close();
  if(sourceHandle)try{sdk.dispose(sourceHandle);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});

test('C14 complete Schedule profile opens the same generated facade without domain-specific compiler wiring',async()=>{
 const work=mkdtempSync(path.join(tmpdir(),'craft-c14-complete-schedule-'));
 const sdk=createGenericHttpCompositionOwner(),oracle=JSON.parse(readFileSync(path.join(schedule,'http-oracle.json'),'utf8'));
 let handle,auth,setup,application;
 try{
  handle=await sdk.prepare({sourcePath:path.join(schedule,'business.alch'),profilePath:path.join(schedule,'contracts/selected-profile.json'),httpProfilePath:path.join(schedule,'contracts/http-profile.json')});
  const review=sdk.review(handle,'C14-complete-schedule');
  sdk.accept(handle,{decision_id:'C14-complete-schedule',owner:'C14-complete-schedule',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'source-decision.json'));
  const owner=createGenericServiceArtifactOwner(sdk,handle),output=path.join(work,'application');
  const selected=[...new Set(sdk.inspect(handle).http_contract.entries.map(row=>row.route.entry))];
  const artifact=owner.emit({outputDirectory:output,entries:selected,requireCompleteApplication:true});
  assert.equal(owner.inspect(artifact).complete_application,true);
  const graph=JSON.parse(readFileSync(path.join(output,'application-system-graph.json'),'utf8'));
  assert.ok(graph.nodes.some(node=>node.id==='ScheduleService::api:'+oracle.routes.read));
  assert.ok(graph.nodes.some(node=>node.id==='ScheduleService::api:'+oracle.routes.reserve));
  auth=await createGenericAuthFixture(sdk,handle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:oracle.subject,evidence:'schedule-owner-evidence',session:'schedule-owner-session'}],grants:[{subject:oracle.subject,entry:oracle.root_entry},{subject:oracle.subject,entry:oracle.child_entry}]});
  setup=await prepareGenericFixtureRuntime(sdk,handle,{service:'ScheduleService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(schedule,'fixture-rows.json'))));
  const storePath=setup.storePath;await setup.runtime.close();setup=null;
  const generated=await import(pathToFileURL(path.join(output,'application.mjs')).href);
  application=await generated.openGeneratedApplication(owner,artifact,{ScheduleService:{storePath,mode:'reopen',nativeAuth:auth.nativeAuth}});
  const dispatch=await application.http('ScheduleService');
  const read=new Request('http://schedule.invalid/api/days/7');
  associateGenericHttpFixtureRequest(auth,dispatch.handlerForRoute(oracle.routes.read),read,oracle.subject);
  const response=await dispatch(read);assert.equal(response.status,200);
  assert.deepEqual((await response.json()).value,oracle.cases.find(row=>row.id==='schedule-read-empty').expected_value);
  const commit=oracle.cases.find(row=>row.id==='schedule-reserve-commit');
  const request=new Request('http://schedule.invalid/api/reservations',{method:'POST',headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from(commit.client_key).toString('base64url')},body:JSON.stringify(commit.input)});
  associateGenericHttpFixtureRequest(auth,dispatch.handlerForRoute(oracle.routes.reserve),request,oracle.subject);
  const committed=await dispatch(request);assert.equal(committed.status,200);
  assert.deepEqual((await committed.json()).value,commit.expected_value);
 }finally{
  if(application)await application.close();
  if(setup?.runtime)await setup.runtime.close();
  if(auth)await auth.close();
  if(handle)try{sdk.dispose(handle);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});
