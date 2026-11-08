import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {captureJson,canonicalJson,dataDigest,validateProfileProject,validateProfilePackage,validateCoverageShape,validateCompositionShape,PROFILE_ROLE_CONTRACTS,ProfileRejected} from '../../src/profile-engine/contracts.ts';

// Open questions: docs/PROFILE-AUTHORING.md. Contract validation is not graph admission.
const fixture=path.join(import.meta.dirname,'fixtures/quote-business/project.json');
const hash='a'.repeat(64);
function profile():any{return {schema_version:'craft.profile-package/v1',id:'testPackage',version:'1.0.0',engine:'craft.profile-engine/v1',conflict_policy:'reject',dependencies:[],capabilities:[{role:'http-entry',descriptor_ref:PROFILE_ROLE_CONTRACTS['http-entry'].descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS['http-entry'].recipe_ref}],budgets:{operations:100,rows:100,join_pairs:100,depth:16,bytes:4096},rules:[{id:'chooseIntents',op:'select',from:'intents',as:'chosen'},{id:'createEntries',op:'emit',from:'chosen',role:'http-entry',fields:{id:{field:['id']},route:{concat:[{literal:'/'},{field:['id']}]}}}],assets:[{id:'entry',path:'templates/entry.mjs.template',kind:'template',sha256:hash,includes:[],holes:{id:'identifier',route:'string'}}]};}

test('closed project and package contracts capture immutable inert snapshots',()=>{
 const raw=JSON.parse(readFileSync(fixture,'utf8'));const checked=validateProfileProject(raw);
 assert.equal(checked.public_intents.length,2);assert.ok(Object.isFrozen(checked.public_intents[0]));
 raw.public_intents[0].id='changed';assert.equal(checked.public_intents[0]!.id,'requestQuote');
 const packageInput=profile();const pack=validateProfilePackage(packageInput);packageInput.rules[0].as='mutated';assert.equal((pack.rules[0] as any).as,'chosen');
 assert.equal(dataDigest({b:2,a:1}),dataDigest({a:1,b:2}));assert.equal(canonicalJson(captureJson({__proto__:null,constructor:'inert',a:[1,true]})),'{"a":[1,true],"constructor":"inert"}');
});
for(const [name,change] of [
 ['opaque evaluator',p=>p.rules[0].op='eval'],
 ['build hook',p=>p.build_script='node feature.js'],
 ['executable hole',p=>p.assets[0].holes.id='javascript'],
 ['outside include',p=>p.assets[0].includes=['outside']],
 ['cyclic include',p=>p.assets[0].includes=['entry']],
 ['asset escape',p=>p.assets[0].path='../source.js'],
 ['missing role',p=>p.capabilities=[]],
 ['unavailable descriptor mapping',p=>p.capabilities[0].descriptor_ref='fabricated-admitted-profile'],
 ['duplicate owner/rule identity',p=>p.rules[1].id=p.rules[0].id],
 ['unsupported engine',p=>p.engine='engine/v99'],
 ['budget overflow',p=>p.budgets.join_pairs=100001],
 ['native template execution',p=>p.assets[0].kind='native'],
] as Array<[string,(p:any)=>void]>)test('rejects '+name,()=>{const value=profile();change(value);assert.throws(()=>validateProfilePackage(value),ProfileRejected);});
test('business source and public intent references cannot escape or collide',()=>{
 const value=JSON.parse(readFileSync(fixture,'utf8'));value.domain_sources[0]='nested/../private.alch';assert.throws(()=>validateProfileProject(value),/PROFILE_SOURCE_PATH/);
 const duplicate=JSON.parse(readFileSync(fixture,'utf8'));duplicate.public_intents[1].id=duplicate.public_intents[0].id;assert.throws(()=>validateProfileProject(duplicate),/PROFILE_DUPLICATE_ID/);
 const missing=JSON.parse(readFileSync(fixture,'utf8'));missing.public_intents[0].source='missing.alch';assert.throws(()=>validateProfileProject(missing),/PROFILE_PUBLIC_INTENT_UNKNOWN_REF/);
});
test('accessors and proxies never run during data capture',()=>{
 let runs=0;const accessor=Object.defineProperty({},'value',{get(){runs++;return 'execute';},enumerable:true});assert.throws(()=>captureJson(accessor),/PROFILE_DATA_ACCESSOR/);
 const proxy=new Proxy({},{getPrototypeOf(){runs++;return Object.prototype;}});assert.throws(()=>captureJson(proxy),/PROFILE_DATA_PROXY/);assert.equal(runs,0);
 assert.throws(()=>captureJson([,]),/PROFILE_DATA_ARRAY/);assert.throws(()=>captureJson(Number.POSITIVE_INFINITY),/PROFILE_DATA_NUMBER/);
});
test('generation coverage cannot manufacture proof/admission or hide required behavior',()=>{
 const value:any={schema_version:'craft.profile-coverage/v1',source_sha256:hash,lock_sha256:hash,authority_effect:'none',items:[{id:'guard:stock',origin:{kind:'business',source:'quote.alch',selector:'rule:EnoughStock',sha256:hash},kind:'business-obligation',state:'retained',reason:'checked behavior',artifact_refs:['behavior.mjs'],evidence_states:['generated','statically-checked']}]};
 assert.equal(validateCoverageShape(value).items.length,1);value.items[0].evidence_states.push('admitted');assert.throws(()=>validateCoverageShape(value),/PROFILE_EVIDENCE_STATE_UNSUPPORTED/);value.items[0].evidence_states=['linked'];value.items[0].state='claim-residue';assert.throws(()=>validateCoverageShape(value),/PROFILE_CLAIM_RESIDUE_KIND/);
});

test('composition rejects competing ownership, unresolved references and dependency cycles',()=>{
 const origin={kind:'profile-rule',source:'package.json',selector:'rule:entry',sha256:hash};
 const input:any={schema_version:'craft.profile-composition/v1',source_sha256:hash,lock_sha256:hash,composition_sha256:hash,authority_effect:'none',components:[{id:'entry',role:'http-entry',owner:'entryOwner',artifact_paths:['src/entry.mjs'],depends_on:[],origins:[origin],contract_ref:'craft.profile.http-entry/v1'}]};
 assert.equal(validateCompositionShape(input).components.length,1);
 input.components.push({...input.components[0],id:'other',owner:'otherOwner'});assert.throws(()=>validateCompositionShape(input),/PROFILE_ARTIFACT_OWNER_CONFLICT/);
 input.components.pop();input.components[0].depends_on=['missing'];assert.throws(()=>validateCompositionShape(input),/PROFILE_COMPONENT_MISSING/);
 input.components[0].depends_on=['entry'];assert.throws(()=>validateCompositionShape(input),/PROFILE_COMPONENT_CYCLE/);
});
