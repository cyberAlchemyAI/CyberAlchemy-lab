import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {validateProfileProjectV2,validateProfileProjectInput,validateProfilePackageV2,validateBusinessApplication,PROFILE_ROLE_CONTRACTS_V2} from '../../src/profile-engine/contracts-v2.js';
import {dataDigest} from '../../src/profile-engine/contracts.js';
// Open questions: business-only application work-pack. This verifies contracts, not generation.
const root=path.join(import.meta.dirname,'fixtures/business-notice');
const project=()=>JSON.parse(readFileSync(path.join(root,'project.json'),'utf8'));
const business=()=>JSON.parse(readFileSync(path.join(root,'business-semantics.json'),'utf8'));
const clone=<T>(v:T):T=>structuredClone(v);
const pack=()=>({schema_version:'craft.profile-package/v2-candidate',id:'node-http-entry-local-v2',version:'1.0.0',engine:'craft.profile-engine/v2-candidate',conflict_policy:'reject',dependencies:[],capabilities:[{role:'application-operation',descriptor_ref:PROFILE_ROLE_CONTRACTS_V2['application-operation'].descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS_V2['application-operation'].recipe_ref}],budgets:{operations:100,rows:100,join_pairs:100,depth:16,bytes:65536},rules:[{id:'bootstrap',op:'defaults',as:'bootstrap',values:{id:'bootstrap'}}],assets:[{id:'formal-profile',kind:'data',path:'formal/profile.json',sha256:'a'.repeat(64),includes:[],holes:{}},{id:'identity',kind:'data',path:'formal/identity.json',sha256:'b'.repeat(64),includes:[],holes:{}},{id:'settlement',kind:'native',path:'runtime/settlement.ts',sha256:'c'.repeat(64),includes:[],holes:{}},{id:'transport',kind:'native',path:'runtime/transport.mts',sha256:'d'.repeat(64),includes:[],holes:{}}],application_runtime:{settlement:'empty-effects/v1',settlement_asset:'settlement',formal_profile_asset:'formal-profile',identity_algorithm_asset:'identity',transport:'entry-local',transport_asset:'transport'}});

test('v2 supports application-only and multiple model input without filler functions',()=>{
 const p=project(),b=validateBusinessApplication(business());assert.equal(validateProfileProjectV2(p).public_intents.length,0);assert.ok(Object.isFrozen(b.claim_meanings.IdentityClaim));
 const multi=clone(p);multi.application_models.push({...multi.application_models[0],id:'second',source:'other.alch',semantics:'other.json'});multi.application_intents.push({...multi.application_intents[0],id:'secondNotice',application_id:'second'});assert.equal(validateProfileProjectInput(multi).schema_version,'craft.profile-project/v2-candidate');
 const input=clone(business());const checked=validateBusinessApplication(input);input.operation_behaviors.ReceiveNotice.result.root='changed';assert.equal(checked.operation_behaviors.ReceiveNotice!.result.root,'request');
});
test('v1 input dispatch retains the existing two-function contract',()=>{
 const p=JSON.parse(readFileSync(path.join(import.meta.dirname,'fixtures/quote-business/project.json'),'utf8'));assert.equal(validateProfileProjectInput(p).schema_version,'craft.profile-project/v1');p.public_intents.pop();assert.throws(()=>validateProfileProjectInput(p),/PROFILE_SCHEMA_LIMIT/);
});
for(const [name,mutate] of [
 ['empty project',p=>{p.application_intents=[];p.application_models=[];}],
 ['unresolved model',p=>p.application_intents[0].application_id='missing'],
 ['unexposed model',p=>p.application_models.push({...p.application_models[0],id:'extra'})],
 ['duplicate intent',p=>p.application_intents.push(clone(p.application_intents[0]))],
 ['escaping semantics',p=>p.application_models[0].semantics='../outside.json'],
 ['native project hook',p=>p.execute='node custom.js'],
 ['protected access not qualified',p=>p.application_intents[0].access={kind:'policy',policy_ref:'private'}],
 ['mapping from unrelated scope',p=>p.application_intents[0].mapping_arguments.payload.root='value'],
 ['unconfigured external read',p=>{p.domain_sources=['function.alch'];p.external_reads=[{id:'stock',source:'function.alch',output_ref:'Output',request_fields:{id:'input.id'}}];}],
] as [string,(p:any)=>void][])test('v2 project rejects '+name,()=>{const p=project();mutate(p);assert.throws(()=>validateProfileProjectV2(p));});
for(const [name,mutate] of [
 ['candidate meaning',b=>b.claim_meanings.IdentityClaim.business_meaning.status='candidate'],
 ['criteria-only acceptance',b=>b.claim_meanings.IdentityClaim.owner_acceptance='accepted by criteria'],
 ['changed accepted subject',b=>b.claim_meanings.IdentityClaim.business_meaning.rule='different rule'],
 ['wrong decision owner',b=>b.claim_meanings.IdentityClaim.owner_acceptance.owner='other-owner'],
 ['candidate definition',b=>b.claim_meanings.IdentityClaim.definitions[0].status='candidate'],
 ['unresolved definition',b=>b.claim_meanings.IdentityClaim.definition_refs=['MISSING-DEFINITION']],
 ['missing transitive definition',b=>b.claim_meanings.IdentityClaim.definitions[0].depends_on=['MISSING-DEFINITION']],
 ['technical execution carrier',b=>b.selection={operations:[]}],
 ['result business mutation unsupported',b=>b.operation_behaviors.ReceiveNotice.result.path=['id']],
 ['guard from body',b=>b.operation_behaviors.ReceiveNotice.guards[0].arguments.identity.root='body'],
 ['invariant from operation',b=>b.value_invariant_bindings.OrderNotice[0].arguments.identity.root='request'],
] as [string,(b:any)=>void][])test('business metadata rejects '+name,()=>{const b=business();mutate(b);assert.throws(()=>validateBusinessApplication(b));});
test('accepted meaning remains distinct from proof and must bind exact subject',()=>{
 const b=business();assert.equal(b.claim_meanings.IdentityClaim.owner_acceptance.subject.digest,dataDigest(b.claim_meanings.IdentityClaim.business_meaning));assert.equal(validateBusinessApplication(b).claim_meanings.IdentityClaim!.owner_acceptance.outcome,'accepted');
 b.claim_meanings.IdentityClaim.proof='proved';assert.throws(()=>validateBusinessApplication(b),/UNKNOWN_FIELD/);
});
test('v2 packages pin inert formal data and the registered no-effects runtime',()=>{
 const p=pack();assert.equal(validateProfilePackageV2(p).assets[0]!.kind,'data');
 for(const mutation of ['missing','wrong-kind','hook','wrong-role','effectful-runtime']){const value:any=clone(p);if(mutation==='missing')value.application_runtime.formal_profile_asset='absent';if(mutation==='wrong-kind')value.assets[0].kind='native';if(mutation==='hook')value.assets[0].holes={eval:'javascript'};if(mutation==='wrong-role')value.capabilities[0].descriptor_ref='typescript.bound-operation/v1';if(mutation==='effectful-runtime')value.application_runtime.settlement='durable-database';assert.throws(()=>validateProfilePackageV2(value));}
});
