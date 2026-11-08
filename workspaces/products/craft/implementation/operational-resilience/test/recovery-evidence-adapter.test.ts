import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { normalizeRecoveryEvidence, recoveryDocument, type AdapterInputs, type AdapterPins, type RecoveryDocument } from '../src/recovery-evidence-adapter.js';
import { RECOVERY_IDS, RECOVERY_ROLES, RECOVERY_SCHEMA_VERSION, type RecoveryBundle } from '../contracts/recovery-product-test.js';
import { evaluateRecoveryProductTest, recoverySha256, recoveryBindingDigest, recoveryInvalidationDigest } from '../src/evaluate-recovery-product-test.js';

const here = dirname(fileURLToPath(import.meta.url));
const evidence = resolve(here, '../../../development/completion-dag/v1/evidence');
const r07 = resolve(evidence, 'r07-recovery-v1');
const read = (path: string): RecoveryDocument => { const content=readFileSync(path,'utf8');return {reference:{ref:path,version:'1.0.0-candidate.1',sha256:recoverySha256(content)},content}; };
function fixture() {
  const producer=recoveryDocument('recorded-producer',{artifact_sha256:read(resolve(r07,'case.py')).reference.sha256,mode:'historical'});
  const observer=recoveryDocument('historical-observer',{artifact_sha256:null,mode:'not-established'});
  const input:AdapterInputs={mode:'historical',manifest:read(resolve(r07,'PRODUCT-TEST-MANIFEST.json')),sourceManifest:read(resolve(r07,'source-manifest.json')),scenarioMap:read(resolve(r07,'scenario-map.json')),matrix:read(resolve(evidence,'r01-recovery-v1/failure-matrix.json')),results:read(resolve(r07,'RESULTS.json')),producer,observer};
  const pins:AdapterPins={manifest:input.manifest.reference.sha256,sourceManifest:input.sourceManifest.reference.sha256,scenarioMap:input.scenarioMap.reference.sha256,matrix:input.matrix.reference.sha256,results:input.results.reference.sha256,observer:null,driver:null,python:null};
  return {input,pins,producer,observer};
}
function changeResults(f:ReturnType<typeof fixture>,change:(r:Record<string,any>)=>void){
 const results=JSON.parse(f.input.results.content);change(results);
 f.input.results=recoveryDocument(f.input.results.reference.ref,results);f.pins.results=f.input.results.reference.sha256;
 const manifest=JSON.parse(f.input.manifest.content);manifest.results_sha256=f.pins.results;
 f.input.manifest=recoveryDocument(f.input.manifest.reference.ref,manifest);f.pins.manifest=f.input.manifest.reference.sha256;
}
function bundle(f:ReturnType<typeof fixture>){
 const adapted=normalizeRecoveryEvidence(f.input,f.pins);assert.equal(adapted.status,'normalized',adapted.findings.join(';'));
 if(adapted.status!=='normalized')throw new Error('invalid adapter');
 const docs=[...adapted.documents];
 const references=Object.fromEntries(RECOVERY_ROLES.map(role=>{let d:RecoveryDocument;
   if(role==='scenario_contract')d=adapted.scenarioDocument;
   else if(role==='candidate_artifact'||role==='subject')d=f.input.manifest;
   else if(role==='source_manifest')d=f.input.sourceManifest;
   else if(role==='producer')d=f.producer;
   else if(role==='observer')d=f.observer;
   else if(role==='evaluation_policy')d=recoveryDocument(role,{policy_id:'domainspec.orodi.recovery-evaluation-policy-candidate',fresh_max_age_seconds:86400,receipt_lifetime_seconds:86400});
   else d=recoveryDocument('test-binding/'+role,{role,test_fixture_only:true,source_manifest:f.input.sourceManifest.reference});
   if(!docs.some(x=>x.reference.ref===d.reference.ref))docs.push(d);return [role,d.reference];
 }));
 const binding={schema_version:'domainspec.orodi.recovery-test-binding/v1-candidate',binding_id:'B04-adapter-test',created_at:'2026-09-06T00:00:00Z',expires_at:'2026-09-07T12:00:00Z',invalidation_key_digest:recoveryInvalidationDigest(references),references,owners:Object.fromEntries(['recovery-runtime','operation','ORODI-profile','evidence-producer','observer','evaluator'].map(r=>[r,r])),authority_effect:'none' as const};
 const value:RecoveryBundle={schema_version:RECOVERY_SCHEMA_VERSION,binding,claim_mode:adapted.claim_mode,documents:docs,records:adapted.records,authority_effect:'none'};
 return {adapted,value};
}
function evaluate(f:ReturnType<typeof fixture>){const {value}=bundle(f);return evaluateRecoveryProductTest(JSON.stringify(value),{binding_digest:recoveryBindingDigest(value.binding),evaluated_at:'2026-09-06T12:00:00Z'});}

test('real R07 bytes normalize all 60 historical records and evaluate integrity',()=>{const f=fixture();const {adapted}=bundle(f);assert.equal(adapted.records.length,60);assert.ok(adapted.records.every(r=>r.origin==='historical'&&r.observer===null&&r.capture_started_at_utc===null));const r=evaluate(f);assert.equal(r.state,'passed');assert.equal(r.claim_mode,'historical-record-integrity');assert.equal(r.authority_effect,'none');});
test('all 30 missing-repetition mutations remain visible',()=>{for(const id of RECOVERY_IDS){const f=fixture();changeResults(f,r=>{r.runs=r.runs.filter((x:any)=>!(x.scenario_id===id&&x.repetition===2));});const r=evaluate(f);assert.equal(r.denominator,60);assert.equal(r.state,'missing');assert.equal(r.assertion_receipts.filter(x=>x.state==='missing').length,1);}});
test('original unknown outcome and raw source pointer survive',()=>{const {adapted}=bundle(fixture());const raw=JSON.parse(adapted.normalizedDocument.content);const r=raw.assertions.find((x:any)=>x.scenario_id==='R01-F17');assert.equal(r.runtime_outcome,'unknown');assert.match(r.raw_pointer,/^\/runs\/\d+$/);assert.equal(r.original_result,'PASS');});
test('duplicate run rejected without partial outputs',()=>{const f=fixture();changeResults(f,r=>{r.runs[1]=r.runs[0];});const a=normalizeRecoveryEvidence(f.input,f.pins);assert.equal(a.status,'invalid');assert.equal(a.records.length,0);});
test('wrong exact test name fails despite passing result',()=>{const f=fixture();changeResults(f,r=>{r.runs[0].observation.tests[0].test='unrelated.Test.pass';});assert.equal(evaluate(f).state,'failed');});
test('recorded failure stays failed and incomplete evidence stays unsupported',()=>{const f=fixture();changeResults(f,r=>{r.runs[0].observation.tests[0].result='FAIL';});assert.equal(evaluate(f).state,'failed');const g=fixture();changeResults(g,r=>{r.runs[0]={scenario_id:'R01-F01',repetition:1,result:'not_evaluable',cause:'unreadable result'};});assert.notEqual(evaluate(g).state,'passed');});
test('source drift and unknown fields reject',()=>{const f=fixture();f.input.results.content+=' ';assert.equal(normalizeRecoveryEvidence(f.input,f.pins).status,'invalid');const g=fixture();changeResults(g,r=>{r.runs[0].invoke='forbidden';});assert.equal(normalizeRecoveryEvidence(g.input,g.pins).status,'invalid');});
test('historical records cannot become fresh by changing claim',()=>{const f=fixture();const {value}=bundle(f);value.claim_mode='fresh-local-recovery-product-test';const r=evaluateRecoveryProductTest(JSON.stringify(value),{binding_digest:recoveryBindingDigest(value.binding),evaluated_at:'2026-09-06T12:00:00Z'});assert.equal(r.state,'inconclusive');});
test('formation probe cannot claim runtime observation',()=>{const f=fixture();changeResults(f,r=>{const run=r.runs.find((x:any)=>x.scenario_id==='R01-F26');const payload=JSON.parse(run.observation.contract_probe.stdout);payload.runtime_guarantees_observed=true;run.observation.contract_probe.stdout=JSON.stringify(payload);});assert.equal(evaluate(f).state,'failed');});
test('normalization deterministic and preserves inputs',()=>{const f=fixture();const before=JSON.stringify(f);assert.deepEqual(normalizeRecoveryEvidence(f.input,f.pins),normalizeRecoveryEvidence(f.input,f.pins));assert.equal(JSON.stringify(f),before);});
test('actual fresh driver output normalizes and observer spoof rejects',()=>{const f=fixture();const driver=resolve(here,'../src/recovery_observed_case.py');const observer=resolve(here,'../src/recovery_test_observer.py');const observerDigest=recoverySha256(readFileSync(observer,'utf8'));const child=spawnSync('python3',['-B',driver,'--scenario','R01-F01','--repetition','1','--manifest-sha256',f.pins.manifest,'--observer-sha256',observerDigest],{encoding:'utf8',timeout:40000});assert.equal(child.status,0,child.stdout+child.stderr);const run=JSON.parse(child.stdout);f.input.mode='fresh';f.input.results=recoveryDocument('fresh-smoke',{runs:[run]});f.pins.results=f.input.results.reference.sha256;f.pins.observer=observerDigest;f.pins.driver=recoverySha256(readFileSync(driver,'utf8'));f.pins.python=run.provenance.executable_sha256;f.producer=recoveryDocument('fresh-driver',{mode:'fresh',artifact_sha256:f.pins.driver});f.observer=recoveryDocument('fresh-observer',{mode:'fresh',artifact_sha256:f.pins.observer});f.input.producer=f.producer;f.input.observer=f.observer;const a=normalizeRecoveryEvidence(f.input,f.pins);assert.equal(a.status,'normalized',a.findings.join(';'));assert.equal(a.records[0].execution,'completed');assert.equal(a.records[0].origin,'fresh');for(const mutate of [(c:any)=>{c.observer_pid=run.observation.pid;},(c:any)=>{c.barrier_id='wrong';},(c:any)=>{c.capture_started_at_utc='2026-02-30T00:00:00.000Z';},(c:any)=>{c.telemetry={exported:99};},(c:any)=>{c.stores[0].tables.attempts.columns.push('attempt_id');}]){const changed=structuredClone(run);mutate(changed.observation.tests[0].before);f.input.results=recoveryDocument('fresh-smoke',{runs:[changed]});f.pins.results=f.input.results.reference.sha256;assert.equal(normalizeRecoveryEvidence(f.input,f.pins).status,'invalid');}});
