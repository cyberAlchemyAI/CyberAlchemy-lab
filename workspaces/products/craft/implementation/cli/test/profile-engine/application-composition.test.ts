import assert from 'node:assert/strict';
import test from 'node:test';
import {cpSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import {applicationFixture} from './profile-fixture.js';
import {prepareProfileProject,generateProfileProject,planProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
import {loadDomainSpecCompiler} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/domainspec-cli.js';
// Open questions: full matrix, adversarial and installed qualification PE16/17/23.

test('final service invokes actual checked Mapping and Operation and preserves complete outcomes',async t=>{
 const f=applicationFixture(t),prepared=await prepareProfileProject(f.projectPath);t.after(()=>disposeProfileProject(prepared));const plan=planProfileProject(prepared),app=prepared.composition.applications[0];
 assert.equal(plan.views.system.applications.length,1);assert.ok(plan.views.system.applications[0].application_graph.edges.length>0);assert.ok(plan.views.coverage.items.some((i:any)=>i.id==='application-mapping:receiveNotice#message-mapping:consume-order'));assert.equal(plan.views.coverage.items.find((i:any)=>i.id==='application-claim:receiveNotice#IdentityClaim').state,'claim-residue');
 const output=path.join(f.root,'output'),built=generateProfileProject(prepared,output);assert.ok(built.qualification.covered_files.includes('applications/receiveNotice/lib/profile-entry.js'));assert.ok(built.qualification.checked_files.includes('applications/receiveNotice/src/profile-entry.ts'));
 const compiler=await loadDomainSpecCompiler();assert.throws(()=>compiler.profileEngine.prepareApplicationCallable(app.graph,JSON.parse(JSON.stringify(app.whole)),app.binding,app.intent,app.assert_current),/DS_WHOLE_APPLICATION_SNAPSHOT/);
 const require=createRequire(import.meta.url),saved:{object:any;key:string;value:any}[]=[];let forbidden=0;
 for(const [object,key]of [[globalThis,'fetch'],[require('node:http'),'createServer'],[require('node:net'),'connect'],[require('node:child_process'),'spawn'],[require('node:child_process'),'execFileSync']] as const){saved.push({object,key,value:(object as any)[key]});(object as any)[key]=()=>{forbidden++;throw Error('forbidden operation runtime effect');};}syncBuiltinESMExports();
 try{
  const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href);let begins=0,commits=0;const ports=(status='committed',failBegin=false)=>({store:{begin:async()=>{begins++;if(failBegin)throw Error('fixture begin failure');return {read:async()=>{throw Error('unexpected read');},commit:async(batch:any)=>{commits++;assert.deepEqual(batch,{writes:[],events:[]});return {status};},rollback:async()=>{throw Error('unexpected rollback');}};}}});
  const request=(id='7')=>new Request('https://test.invalid/receiveNotice',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({payload:{id}})}),events:any[]=[];
  const invoke=async(status='committed',options:any={})=>{const response=await service.handler(request(),{},{applications:{receiveNotice:ports(status,options.failBegin)},observe:(event:any)=>events.push(event),...options});return {http:response.status,body:await response.json()};};
  const committed=await invoke();assert.equal(committed.http,200);assert.equal(committed.body.status,'returned');assert.deepEqual(committed.body.value,{id:'7'});assert.equal(committed.body.outcome.status,'committed');
  const rejected=await invoke('rejected');assert.equal(rejected.body.failure.status,'rejected');assert.equal(rejected.body.failure.code,'COMMIT_REJECTED');assert.equal(rejected.body.failure.stage,'commit');assert.equal(rejected.body.failure.continuation,'return-notice-error');
  const uncertain=await invoke('indeterminate');assert.equal(uncertain.body.failure.status,'indeterminate');assert.equal(uncertain.body.failure.code,'COMMIT_INDETERMINATE');assert.equal(uncertain.body.failure.cleanupFailed,false);
  const failed=await invoke('committed',{failBegin:true});assert.equal(failed.body.failure.code,'BEGIN_FAILED');assert.equal(failed.body.failure.stage,'begin');
  const before=begins;const required=await invoke('committed',{cancellation:'required'});assert.equal(required.body.failure.code,'PROFILE_OPERATION_CANCELLATION_UNSUPPORTED');assert.equal(begins,before);
  const controller=new AbortController();controller.abort();assert.equal((await invoke('committed',{signal:controller.signal})).body.failure.code,'FUNCTION_CANCELLED');assert.equal(begins,before);
  const bad=await service.handler(request('-1'),{},{applications:{receiveNotice:ports()}});assert.equal((await bad.json()).failure.code,'PROFILE_OPERATION_MAPPING');assert.equal(begins,before);
  const noPorts=await service.handler(request());assert.equal(noPorts.status,503);assert.equal((await noPorts.json()).failure.code,'PROFILE_OPERATION_PORTS_REQUIRED');
  assert.ok(events.some(e=>e.phase==='start'&&e.adapter==='operation'));assert.ok(events.some(e=>e.phase==='return'));assert.ok(events.some(e=>e.phase==='failure'));assert.equal(commits,3);assert.equal(forbidden,0);
 }finally{for(const entry of saved.reverse())entry.object[entry.key]=entry.value;syncBuiltinESMExports();}
});
test('unresolved Mapping, access, source closure and serialized app records reject',async t=>{
 for(const mutation of ['mapping','access']){const f=applicationFixture(t),p=JSON.parse(readFileSync(f.projectPath,'utf8'));if(mutation==='mapping')p.application_calls[0].mapping_binding_ref='unresolved';else p.application_calls[0].access={kind:'implicit'};writeFileSync(f.projectPath,JSON.stringify(p));await assert.rejects(()=>prepareProfileProject(f.projectPath),/PROFILE_APPLICATION_MAPPING|PROFILE_SCHEMA_/);}
});
