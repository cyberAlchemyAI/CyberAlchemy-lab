import assert from 'node:assert/strict';
import test from 'node:test';
import {cpSync,readFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createProfileFixture,useShippedProfile} from './profile-fixture.js';
import {prepareProfileProject,planProfileProject,generateProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Independent two-provider/boolean/timestamp/pricing domain. Open questions: PE16/19/23.
test('independent appointment domain needs only source/configuration/profile changes',async t=>{
 let frozen:{engine:string;tools:string}|undefined;
 for(const name of ['node-http-entry-local-v1','node-http-shared-ports-v1']){
  const f=createProfileFixture(t);cpSync(path.resolve(import.meta.dirname,'../../examples/profile-engine/appointment-business'),f.root,{recursive:true});useShippedProfile(f,name);
  const prepared=await prepareProfileProject(path.join(f.root,'project.json'));t.after(()=>disposeProfileProject(prepared));const plan=planProfileProject(prepared),identity={engine:plan.lock.engine_sha256,tools:plan.lock.tool_sha256};if(frozen)assert.deepEqual(identity,frozen);else frozen=identity;
  assert.equal(prepared.selection.input.project.external_reads.length,2);
  for(const source of ['appointment.alch','policy.alch'])assert.doesNotMatch(readFileSync(path.join(f.root,source),'utf8'),/^(profile|integration|endpoint|service|import|execution|interpretation)\b/m);
  for(const selector of ['calculation:AppointmentFee','rule:EligibleSlot','schema:AppointmentRequest'])assert.ok(plan.views.coverage.items.some((i:any)=>i.id==='business:appointment.alch#'+selector));assert.equal(plan.views.coverage.items.find((i:any)=>i.id==='claim:ExactAppointmentFee').state,'claim-residue');
  const output=path.join(f.root,'output');generateProfileProject(prepared,output);const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),oracle=JSON.parse(readFileSync(path.join(f.root,'oracle.json'),'utf8'));
  for(const c of oracle.cases){let calls=0;const response=await service.handler(new Request('https://test.invalid/'+c.intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c.input)}),{DEPENDENCY_CLINICIANAVAILABILITY_URL:'https://clinician.invalid/slots',DEPENDENCY_VENUEAVAILABILITY_URL:'https://venue.invalid/slots'},{fetch:async(url:URL,options:RequestInit)=>{calls++;assert.equal(options.method,'GET');assert.equal(url.searchParams.get('slot_id'),c.input.slot_id);return new Response(JSON.stringify(url.hostname==='clinician.invalid'?c.clinician:c.venue));}});const actual=await response.json();if(c.expected_error){assert.equal(actual.error,c.expected_error,name+':'+c.id);if(c.expected_error==='FUNCTION_INPUT_SCHEMA')assert.equal(calls,0);}else{assert.deepEqual(actual,c.expected,name+':'+c.id);assert.equal(calls,c.intent==='checkAppointment'?2:0);}}
 }
});
