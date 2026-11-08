import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,mkdirSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {stripTypeScriptTypes} from 'node:module';
import {prepareTechnicalProfileDecisionSource,validateTechnicalProfileDecision} from '../../src/profile-engine/technical-profile-decisions.js';
const source=readFileSync(new URL('./fixtures/technical-profile-decisions/decision.alch',import.meta.url),'utf8');
const limits={max_input_bytes:65536,max_output_bytes:65536,max_value_bytes:32768,max_items:100,max_iterations:100,max_ast_nodes:8192,max_ast_depth:128,max_call_depth:32,fuel:200000};
function fixture(t:any,text=source){const root=mkdtempSync(path.join(tmpdir(),'craft-profile-decisions-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(path.join(root,'source'));mkdirSync(path.join(root,'contracts'));writeFileSync(path.join(root,'source/decisions.alch'),text);writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits}}));writeFileSync(path.join(root,'application.alch'),'module ProfileDecisionRoot version 1\ninterface Application:\n  kind application-composition\n  source source/decisions.alch\n  computation-bounds contracts/bounds.json\n');return root;}
const input=()=>({attempt:{outcome:'NotSent',effect:'Mutating',sends:'0',remainingMs:'300000',retryAfterMs:'0',retryState:'RetryUnscheduled'},credential:{state:'Active',remainingMs:'300000',refreshGrantAvailable:true,refreshAttempts:'0'},evidence:{sourceCurrent:true,releaseAllowed:true,approvalCurrent:true},options:{mode:'ProvenNoEffectOnly',maxSends:'3',maxRefreshAttempts:'2',refreshMarginMs:'60000',defaultDelayMs:'1000'}});
const wire=(v:unknown)=>new Uint8Array(Buffer.from(JSON.stringify(v)));
const decision=(observed:any)=>{assert.equal(observed.result.ok,true,JSON.stringify(observed.result));const value=JSON.parse(Buffer.from(observed.result.wire).toString());return value.tag==='Returned'?value.fields.value:value;};
test('original Core and emitted consumer execute typed Policy->Calculation decisions and Operation composition',async t=>{
 const root=fixture(t),model=prepareTechnicalProfileDecisionSource({sourceRoot:root,selector:'Profiles.Execution.PlanRequest'});
 const compiled=model.compile(),native=await import('data:text/javascript;base64,'+Buffer.from(stripTypeScriptTypes(compiled.source)).toString('base64'));
 const cases:{mutate:(v:ReturnType<typeof input>)=>void;action:string;delay?:string}[]=[
  {mutate:()=>{},action:'Dispatch'},
  {mutate:v=>{v.attempt.outcome='Completed';v.evidence.sourceCurrent=false;v.credential.state='Revoked';},action:'Finish'},
  {mutate:v=>{v.attempt.outcome='OutcomeUnknown';v.evidence.approvalCurrent=false;},action:'InspectOriginal'},
  {mutate:v=>{v.evidence.sourceCurrent=false;},action:'Halt'},
  {mutate:v=>{v.evidence.releaseAllowed=false;},action:'Halt'},
  {mutate:v=>{v.attempt.outcome='Rejected';},action:'Halt'},
  {mutate:v=>{v.credential.state='Expiring';},action:'Renew'},
  {mutate:v=>{v.credential.state='Refreshing';},action:'WaitForRefresh'},
  {mutate:v=>{v.credential.state='RotationUnknown';},action:'RecoverRefresh'},
  {mutate:v=>{v.credential.state='ReauthorizationRequired';},action:'Reauthorize'},
  {mutate:v=>{v.attempt.outcome='ProvenNoEffect';v.attempt.sends='1';v.attempt.retryAfterMs='120000';},action:'Backoff',delay:'120000'},
  {mutate:v=>{v.attempt.outcome='ProvenNoEffect';v.attempt.retryAfterMs='300000';},action:'Halt'},
  {mutate:v=>{v.attempt.outcome='ProvenNoEffect';v.attempt.retryState='RetryDue';},action:'Dispatch'},
  {mutate:v=>{v.attempt.outcome='ProvenNoEffect';v.attempt.retryState='RetryBlocked';},action:'Halt'},
  {mutate:v=>{v.attempt.outcome='OutcomeUnknown';v.attempt.effect='ReadOnly';v.options.mode='SafeReads';},action:'Backoff',delay:'1000'},
 ];
 for(const c of cases){const value=input();c.mutate(value);const bytes=wire(value),observed=model.evaluate(bytes);assert.deepEqual(native.evaluateObserved(bytes),observed);assert.deepEqual(decision(observed),{action:c.action,delayMs:c.delay??'0'});assert.ok(observed.policy_decisions.length>0);assert.ok(observed.policy_decisions.every(p=>p.calculation.startsWith('Profiles.Execution.')));}
 assert.equal(model.inspect().authority_effect,'none');model.dispose();
});
test('source mutation prevents stale decision reuse',t=>{const root=fixture(t),model=prepareTechnicalProfileDecisionSource({sourceRoot:root,selector:'Profiles.Execution.PlanRequest'});writeFileSync(path.join(root,'source/decisions.alch'),source+'\n');assert.throws(()=>model.evaluate(wire(input())),/changed|current|drift/i);});
test('Policy must select a declared Calculation rather than dispatch or reject',t=>{const root=fixture(t,source.replace('-> FinishDecision()','-> PlanRequest()'));assert.throws(()=>prepareTechnicalProfileDecisionSource({sourceRoot:root,selector:'Profiles.Execution.PlanRequest'}),/Calculation|argument|invocation/i);});
test('decision validation rejects action/context data smuggling and invalid delay representation',()=>{for(const v of [{action:'Dispatch',delayMs:'1'},{action:'Backoff',delayMs:'0'},{action:'Dispatch',delayMs:0},{action:'Dispatch',delayMs:'0',attemptId:'other'},{action:'Other',delayMs:'0'},{action:'Backoff',delayMs:'18446744073709551616'}])assert.throws(()=>validateTechnicalProfileDecision(v));assert.deepEqual(validateTechnicalProfileDecision({action:'Backoff',delayMs:'120000'}),{action:'Backoff',delayMs:'120000'});});
