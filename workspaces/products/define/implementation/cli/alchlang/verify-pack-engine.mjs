import {openJsonPort} from '../../../../../../implementation/artifact-runtime/json-pipe.mjs';
import {verifyNativeCoverage} from '../../../../../../implementation/artifact-runtime/column-coverage.mjs';
import {observedPolicyFacts} from './test-value-observations.mjs';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
import {evaluateArtifact} from '../../../../../../implementation/artifact-runtime/pure-operation.mjs';
import {generate,root,node,fingerprint,selected} from './pack-engine-build.mjs';
import {spawnSync} from 'node:child_process';
if(process.execPath!==node){const child=spawnSync(node,[import.meta.filename,...process.argv.slice(2)],{stdio:'inherit'});process.exit(child.status??1);}
const R=path.resolve(root,'../../../../../..');
const O=path.join(root,'.local/pack-engine');mkdirSync(O,{recursive:true});const artifacts=Object.fromEntries(selected.components.map(row=>[row.name,generate(row.name)]));
const checks=[];
async function run(name,value){
 value=observedPolicyFacts(name,value);
 const result=await evaluateArtifact(artifacts[name].output,artifacts[name].member,{value});
 assert.equal(result.ok,true,JSON.stringify(result));return JSON.parse(new TextDecoder().decode(result.wire));
}
async function pass(name,value){const x=await run(name,value);assert.equal(x.tag,'Returned',JSON.stringify(x));assert.equal(x.fields.value,true);}
async function refuse(name,value,reason){const x=await run(name,value);assert.equal(x.tag,'Rejected',JSON.stringify(x));if(reason)assert.equal(x.fields.code??x.fields.reason,reason,JSON.stringify(x));}
const base={application_count:'0',fully_bound_application_count:'0',assessment_count:'0',materialization_count:'0',blocking_uses:[]};
for(const [requested_use,expected] of [['inspect-preparation','ready'],['apply-parameters','not-evaluable'],['consume-assessment','not-evaluable'],['materialize-definition','not-evaluable'],['prepare-owner-review','blocked'],['governing-application','blocked']]){
 const x=await run('UseReadiness',{...base,requested_use});assert.equal(x,expected);checks.push('readiness:'+requested_use);
}
for(const [patch,expected] of [[{application_count:'1',fully_bound_application_count:'1'},'ready'],[{application_count:'1'},'blocked'],[{application_count:'1',fully_bound_application_count:'1',blocking_uses:['apply-parameters']},'blocked']]){
 assert.equal(await run('UseReadiness',{...base,...patch,requested_use:'apply-parameters'}),expected);checks.push('application-readiness:'+expected);
}
for(const use of ['consume-assessment','materialize-definition']){
 assert.equal(await run('UseReadiness',{...base,assessment_count:'1',materialization_count:'1',requested_use:use}),'blocked');checks.push('candidate-presence-does-not-grant:'+use);
}
const digest='a'.repeat(64),other='b'.repeat(64),binding={path:'subject.json',sha256:digest,bytes:'10',digest_kind:'original-file-sha256'};
await pass('VerifyBinding',{selected:binding,observed:binding});checks.push('exact-binding');
for(const key of ['path','sha256','bytes']){await refuse('VerifyBinding',{selected:binding,observed:{...binding,[key]:key==='path'?'other.json':key==='sha256'?other:'11'}});checks.push('negative:binding-'+key);}
const material={owner_route:'role:definition-owner',selected_scope:'scope:test',actual_scope:'scope:test',selected_statement:'Meaning',actual_statement:'Meaning',selected_boundaries:['Bound'],actual_boundaries:['Bound'],selected_notation:[{symbol:'x',meaning:'subject'}],actual_notation:[{symbol:'x',meaning:'subject'}],selected_schema:digest,actual_schema:digest,selected_generator:digest,actual_generator:digest,successor:false,parent_identity:null,parent_revision:null,actual_identity:'meaning:test',actual_revision:'candidate.1'};
await pass('VerifyMaterialization',material);checks.push('materialization:new-identity');
for(const [key,value] of [['owner_route',null],['actual_scope','scope:wrong'],['actual_statement','Changed'],['actual_boundaries',['Changed']],['actual_notation',[{symbol:'y',meaning:'subject'}]],['actual_schema',other],['actual_generator',other],['successor',true]]){
 await refuse('VerifyMaterialization',{...material,[key]:value});checks.push('negative:materialization-'+key);
}
await pass('VerifyMaterialization',{...material,successor:true,parent_identity:material.actual_identity,parent_revision:'candidate.0'});checks.push('materialization:successor');
for(const patch of [{parent_identity:'other'}, {parent_revision:'candidate.1'}]){await refuse('VerifyMaterialization',{...material,successor:true,parent_identity:material.actual_identity,parent_revision:'candidate.0',...patch});checks.push('negative:successor-'+Object.keys(patch)[0]);}
const lineage={expected_targets:['/x','/y'],observations:[{target:'/x',target_value_digest:digest,source_value_digest:digest},{target:'/y',target_value_digest:other,source_value_digest:other}]};
await pass('VerifyLineageBatch',lineage);checks.push('lineage:complete');
for(const bad of [{...lineage,observations:lineage.observations.slice(1)},{...lineage,expected_targets:['/x','/x']},{...lineage,observations:lineage.observations.map(x=>({...x,source_value_digest:other}))},{...lineage,observations:[lineage.observations[0],lineage.observations[0]]}]){await refuse('VerifyLineageBatch',bad);checks.push('negative:lineage-'+checks.length);}
const assessment={execution_posture:'reported',validation_posture:'unverified-reported',reported_result:'FAIL',unevaluable_reason:null};await pass('VerifyAssessment',assessment);checks.push('assessment:reported-fail');
for(const patch of [{execution_posture:'verified-external'},{validation_posture:'binding-verified-within-scope'},{reported_result:'NOT_EVALUABLE'},{unevaluable_reason:'unjustified'}]){await refuse('VerifyAssessment',{...assessment,...patch});checks.push('negative:assessment-'+Object.keys(patch)[0]);}
await pass('VerifyAssessment',{...assessment,reported_result:'NOT_EVALUABLE',unevaluable_reason:'No qualified method'});checks.push('assessment:not-evaluable');
const coveragePort=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
async function coverageNative(selector,args){const row=selected.components.find(row=>row.selector===selector),artifact=artifacts[row.name],result=await evaluateArtifact(artifact.output,artifact.member,args);assert.equal(result.ok,true,JSON.stringify(result));const value=JSON.parse(new TextDecoder().decode(result.wire));if(row.kind==='operation'){if(value.tag!=='Returned')throw Error(value.fields.code);return value.fields.value;}return value;}
async function coverageFixture(required,handled){const protocol=await coverageNative('Define.PackEngine.ConceptCoverageProtocol',{marker:true}),{ref}=await coveragePort.request({operation:'put-value',value:{required_concepts:required.map(concept_id=>({concept_id})),handling:handled.map(concept_id=>({concept_id}))}});return verifyNativeCoverage({port:coveragePort,call:coverageNative,protocol,ref});}
try{
 assert.equal(await coverageFixture(['one','two'],['two','one']),true);checks.push('concepts:exact');
 for(const [required,handled]of [[[],[]],[['one','two'],['one']],[['one','two'],['one','one']],[['one','one'],['one','two']]]){await assert.rejects(()=>coverageFixture(required,handled));checks.push('negative:concepts-'+checks.length);}
}finally{await coveragePort.close();}
const external={selected_identity:'meaning:a',observed_identity:'meaning:a',selected_revision:'1',observed_revision:'1',selected_entry_digest:digest,observed_entry_digest:digest,source_standing:'local-reference',source_population:'caller-supplied'};
await pass('VerifyExternalReference',external);checks.push('external:exact');
for(const patch of [{observed_identity:'other'},{observed_revision:'2'},{observed_entry_digest:other},{source_standing:'admitted'},{source_population:'host-member'}]){await refuse('VerifyExternalReference',{...external,...patch});checks.push('negative:external-'+Object.keys(patch)[0]);}
const embedded={selected_pack:'pack:a',actual_pack:'pack:a',selected_pack_revision:'1',actual_pack_revision:'1',selected_identity:'meaning:a',observed_identity:'meaning:a',selected_revision:'1',observed_revision:'1',selected_entry_digest:digest,observed_entry_digest:digest,entry_kind:'working-meaning',selector_collection:'working_meanings',selector_depth:'2'};
await pass('VerifyEmbeddedReference',embedded);checks.push('embedded:exact');
for(const patch of [{actual_pack:'other'},{actual_pack_revision:'2'},{observed_identity:'other'},{observed_revision:'2'},{observed_entry_digest:other},{entry_kind:'unknown'},{selector_collection:'applications'},{selector_depth:'3'}]){await refuse('VerifyEmbeddedReference',{...embedded,...patch});checks.push('negative:embedded-'+Object.keys(patch)[0]);}
const capture={capture_mode:'local-snapshot',intended_use:'inspect-preparation',source_permitted_uses:['inspect-preparation'],retention_posture:'permitted',permission_observation_present:false,live_observation_present:false};
await pass('VerifyCapture',capture);checks.push('capture:bounded-snapshot');
await pass('VerifyCapture',{...capture,retention_posture:'unresolved'});checks.push('capture:unresolved-retention-does-not-grant-export');
for(const patch of [{capture_mode:'live'},{retention_posture:'forbidden'},{retention_posture:'implicit'},{permission_observation_present:true},{live_observation_present:true},{source_permitted_uses:['governing-application']}]){await refuse('VerifyCapture',{...capture,...patch});checks.push('negative:capture-'+Object.keys(patch)[0]);}
const successor={current_identity:'pack:a',current_revision:'1',predecessor_identity:null,predecessor_revision:null};await pass('VerifySuccessor',successor);checks.push('successor:initial');
await pass('VerifySuccessor',{...successor,current_revision:'2',predecessor_identity:'pack:a',predecessor_revision:'1'});checks.push('successor:exact');
for(const patch of [{current_revision:'2'},{predecessor_identity:'pack:a'},{current_revision:'2',predecessor_identity:'other',predecessor_revision:'1'},{current_revision:'2',predecessor_identity:'pack:a',predecessor_revision:'2'}]){await refuse('VerifySuccessor',{...successor,...patch});checks.push('negative:successor-'+checks.length);}
writeFileSync(path.join(O,'POLICY-VERIFICATION.json'),JSON.stringify({schema_version:'define-alchlang-policy-migration-verification/v1',status:'PASS',checks,check_count:checks.length,negative_controls:checks.filter(x=>x.startsWith('negative:')).length,source:fingerprint(),artifacts,engine_imports:[],actual_native_admission:false,end_to_end_python_engine_removed:false},null,2)+'\n');
console.log('GENERATED_ALCHLANG_POLICY_CHECKS_PASS',checks.length);