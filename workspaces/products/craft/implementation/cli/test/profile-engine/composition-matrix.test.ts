import assert from 'node:assert/strict';
import test from 'node:test';
import {cpSync,readFileSync,writeFileSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {applicationFixture,useShippedProfile} from './profile-fixture.js';
import {prepareProfileProject,generateProfileProject,planProfileProject,verifyProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Open questions: adversarial/frozen/installed qualification PE17/19/23.
test('both domains and architectures preserve independent outcomes and real application composition',async t=>{
 let frozen:unknown;const receipts:any[]=[];
 for(const domain of ['quote','appointment'])for(const profile of ['node-http-entry-local-v1','node-http-shared-ports-v1']){
  const f=applicationFixture(t,profile);if(domain==='appointment'){const original=JSON.parse(readFileSync(f.projectPath,'utf8'));cpSync(path.resolve(import.meta.dirname,'../../examples/profile-engine/appointment-business'),f.root,{recursive:true});useShippedProfile(f,profile);const project=JSON.parse(readFileSync(f.projectPath,'utf8'));project.application_calls=original.application_calls;writeFileSync(f.projectPath,JSON.stringify(project));}
  const prepared=await prepareProfileProject(f.projectPath);t.after(()=>disposeProfileProject(prepared));const plan=planProfileProject(prepared),identity={engine:plan.lock.engine_sha256,tools:plan.lock.tool_sha256};if(frozen)assert.deepEqual(identity,frozen);else frozen=identity;
  assert.equal(plan.views.system.applications.length,1);assert.equal(plan.composition.components.filter((c:any)=>c.role==='shared-http-port').length,profile==='node-http-shared-ports-v1'?1:0);
  const output=path.join(f.root,'output');const built=generateProfileProject(prepared,output);verifyProfileProject(prepared,output);const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),oracle=JSON.parse(readFileSync(path.join(f.root,'oracle.json'),'utf8'));
  const env=domain==='quote'?{DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'}:{DEPENDENCY_CLINICIANAVAILABILITY_URL:'https://clinician.invalid/slots',DEPENDENCY_VENUEAVAILABILITY_URL:'https://venue.invalid/slots'};
  for(const c of oracle.cases){const response=await service.handler(new Request('https://test.invalid/'+c.intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c.input)}),env,{fetch:async(url:URL)=>new Response(JSON.stringify(domain==='quote'?c.external:url.hostname==='clinician.invalid'?c.clinician:c.venue))});const body=await response.json();if(c.expected_error)assert.equal(body.error,c.expected_error,domain+':'+profile+':'+c.id);else assert.deepEqual(body,c.expected,domain+':'+profile+':'+c.id);}
  let begins=0;const store={begin:async()=>{begins++;return {read:async()=>{throw Error('unexpected read');},commit:async()=>({status:'committed'}),rollback:async()=>{throw Error('unexpected rollback');}};}};
  const response=await service.handler(new Request('https://test.invalid/receiveNotice',{method:'POST',headers:{'content-type':'application/json'},body:'{"payload":{"id":"7"}}'}),{},{applications:{receiveNotice:{store}}});assert.equal(response.status,200);assert.deepEqual((await response.json()).value,{id:'7'});assert.equal(begins,1);
  const repeated=path.join(f.root,'repeat');generateProfileProject(prepared,repeated);const manifest=readFileSync(path.join(output,'.profile-manifest.json'),'utf8');assert.equal(manifest,readFileSync(path.join(repeated,'.profile-manifest.json'),'utf8'));
  receipts.push({domain,profile,lock:plan.lock,whole:prepared.composition.applications[0].whole.plan_sha256,native:built.qualification.receipt_sha256,oracle_cases:oracle.cases.length,real_operation_invocations:begins,repeat_manifest:JSON.parse(manifest)});
 }
 if(process.env.PROFILE_MATRIX_EVIDENCE)writeFileSync(process.env.PROFILE_MATRIX_EVIDENCE,JSON.stringify({task:'PE16',cases:receipts,core_tool_identity:frozen,authority_effect:'none',claim_ceiling:'finite checked native composition; no hosting/proof/admission',open_questions_ref:'../../DESIGN.md#open-questions'},null,2)+'\n');
});
