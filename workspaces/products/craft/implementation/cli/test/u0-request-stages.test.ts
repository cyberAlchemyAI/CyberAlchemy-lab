import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {deriveDirectBusinessRequestSourceV2,createBusinessRequestStagesOwnerV2,type U0RequestNativeAssetsOwnerV2} from '../src/profile-engine/business-authoring-request.js';
import {createBusinessCoreRecipeOwnerV2} from '../src/profile-engine/business-authoring-recipes.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2} from '../src/profile-engine/business-authoring-identity-v2.js';
import {decodeRequestApplicationSourceV1,decodeRequestApplicationSourceV2,decodeVersionedRequestApplicationSource} from '../src/system-integration/request-application-source-v1.js';
import {composeDirectRequestApplicationPlanDataV2} from '../src/generation/request-application-plan-v1.js';
import {sha256} from '../src/profile-engine/contracts.js';
import type {BusinessRequestStagesOwnerV2,BusinessPureGenerationOwnerV2} from '../src/profile-engine/business-authoring-stages-v2.js';
// Data/protocol/component evidence only. No fake successful selected/early/native
// handle is used. Q02/U08 own actual cycle-free loaded and generated witnesses.
// Open Questions: J01 genuine native resolver, Q02 original early and U08 late join.
const fixtures=new URL('profile-engine/fixtures/u0-v2/',import.meta.url),text=readFileSync(new URL('business.alch',fixtures),'utf8');
const base=JSON.parse(readFileSync(new URL('spec.json',fixtures),'utf8'));
const clone=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
function transfer(){const spec=clone(base);return {source:{path:'business.alch',text,sha256:sha256(text),bytes:Buffer.byteLength(text)},spec,executable:projectDirectExecutableV2(spec),assurance:projectOptionalAssuranceV2(spec)};}
test('Q01 pure early source preserves literal logical entry, Interface and both Mapping intents',()=>{
 const source=deriveDirectBusinessRequestSourceV2(transfer()),entry=source.entries[0]!;
 assert.equal(source.schema_version,'domainspec.request-application-source/v2-candidate');assert.equal(source.model_id,'dispatching');assert.equal(source.executable_sha256,'a9d937495394cf07732d52cc417d1804518dce516438c75b29b88d604d1486be');
 assert.equal(entry.logical_id,'ProcessHttp');assert.equal(entry.public_name,'confirm-delivery');assert.equal(entry.operation_ref,'dispatching:process');assert.equal(entry.rule_ref,'dispatching:can-process');assert.equal(entry.interface_ref,'dispatching:process-http');
 assert.deepEqual(clone(entry.permission),{kind:'public'});assert.deepEqual(clone(entry.payload),{kind:'whole-input',parameter:'request',type_ref:'Submission'});
 assert.equal(entry.mappings.input,'dispatching:craftrequest-process-http-input');assert.equal(entry.mappings.output,'dispatching:craftrequest-process-http-output');
 assert.deepEqual(clone(entry.mappings.fields),[
  {name:'id',scalar:'UInt64',identity:true,source_property:'BUSINESS-DISPATCHING-PROCESS-HTTP-PAYLOAD#id',target_property:'BUSINESS-DISPATCHING-SUBMISSION#id'},
  {name:'verified',scalar:'Bool',identity:false,source_property:'BUSINESS-DISPATCHING-PROCESS-HTTP-PAYLOAD#verified',target_property:'BUSINESS-DISPATCHING-SUBMISSION#verified'},
 ]);
 assert.deepEqual(entry.origins.map(row=>[row.kind,row.selector]),[['entry','line:43'],['permission','line:46'],['operation-input','line:36'],['entity-field','line:24'],['entity-field','line:26']]);
 assert.ok(entry.origins.every(row=>row.source==='business.alch'&&row.sha256===sha256(text)));assert.ok(Object.isFrozen(source));assert.ok(Object.isFrozen(entry.mappings.fields));
});
test('Q01 early data contains no callable, final native subject, physical route or business acceptance',()=>{
 const source=deriveDirectBusinessRequestSourceV2(transfer());
 const walk=(value:unknown)=>{if(value&&typeof value==='object')for(const [key,child]of Object.entries(value)){assert.equal(['callable','invoke','handler','realized_sha256','basis_sha256','native_basis','accepted','route'].includes(key),false,key);walk(child);}};walk(source);
 assert.equal(base.claims.length,0);assert.equal(Object.hasOwn(source,'kind'),false,'pure intent data is not a registered early handle');
});
test('Q01 source/DTO substitution cannot change direct logical permission, Mapping fields or operation',()=>{
 for(const mutate of [(v:any)=>{v.spec.entries[0].operation_ref='Other';},(v:any)=>{v.spec.entities[0].fields[1].name='approved';},(v:any)=>{v.executable.rules=[];},(v:any)=>{v.spec.entries[0].permission={kind:'protected'};}]){const value=clone(transfer());mutate(value);assert.throws(()=>deriveDirectBusinessRequestSourceV2(value));}
});
test('Q01 closed intent decoder rejects missing, duplicate, wrong-role/shape and injected final bindings',()=>{
 const original=deriveDirectBusinessRequestSourceV2(transfer());
 const mutations=[(v:any)=>{v.entries=[];},(v:any)=>{v.callable={};},(v:any)=>{v.entries[0].route={method:'POST',path:'/confirm-delivery'};},(v:any)=>{v.entries[0].permission={kind:'protected'};},(v:any)=>{v.entries[0].mappings.output=v.entries[0].mappings.input;},(v:any)=>{v.entries[0].mappings.fields.pop();},(v:any)=>{v.entries[0].mappings.fields[1].scalar='UInt64';},(v:any)=>{v.entries[0].mappings.fields[0].source_property='BUSINESS-OTHER#wrong';},(v:any)=>{v.entries[0].origins[0].sha256='0'.repeat(64);},(v:any)=>{v.entries[0].origins[0]=v.entries[0].origins[1];},(v:any)=>{v.entries[0].origins[0].source='../outside';}];
 for(const mutate of mutations){const value=clone(original);mutate(value);assert.throws(()=>decodeRequestApplicationSourceV2(value));}
 const collision=clone(original) as any;collision.entries[0].operation_ref=collision.entries[0].mappings.input;assert.throws(()=>decodeRequestApplicationSourceV2(collision),/DUPLICATE/);
});
test('Q01 version dispatch preserves v1 source without reinterpreting it as logical v2 intent',()=>{
 const legacy={schema_version:'domainspec.request-application-source/v1-candidate',source_id:'legacy',entries:[{id:'confirm',operation_ref:'dispatching:process',mapping_ref:'dispatching:request',mapping_arguments:[{parameter:'body',path:[]}],request_parameter:'request',route:{method:'POST',path:'/confirm'},access:{kind:'public'}}]};
 assert.deepEqual(decodeVersionedRequestApplicationSource(legacy),decodeRequestApplicationSourceV1(legacy));const successor=deriveDirectBusinessRequestSourceV2(transfer());assert.deepEqual(decodeVersionedRequestApplicationSource(successor),successor);
 assert.throws(()=>decodeRequestApplicationSourceV1(successor));assert.throws(()=>decodeRequestApplicationSourceV2(legacy));assert.throws(()=>decodeVersionedRequestApplicationSource({...successor,schema_version:'unknown'}));
});
test('Q01 inert input capture does not invoke getters, proxy traps or injected callbacks',()=>{
 let calls=0;const value=deriveDirectBusinessRequestSourceV2(transfer());
 assert.throws(()=>decodeRequestApplicationSourceV2({...value,get entries(){calls++;return value.entries;}}));
 assert.throws(()=>decodeRequestApplicationSourceV2(new Proxy(value,{ownKeys(){calls++;return [];}})));
 assert.throws(()=>deriveDirectBusinessRequestSourceV2({...transfer(),get source(){calls++;return transfer().source;}}));assert.equal(calls,0);
});
function missingStages(){
 const counts={native:0,generation:0};
 const recipes=createBusinessCoreRecipeOwnerV2({assertCurrent(){throw Error('ACTUAL_NATIVE_BASIS_REQUIRED');},capture(){throw Error('actual producer required');}});
 const generation:BusinessPureGenerationOwnerV2={generate(){counts.generation++;throw Error('ACTUAL_GENERATED_SOURCE_REQUIRED');},async importGenerated(){counts.generation++;throw Error('ACTUAL_GENERATED_IMPORT_REQUIRED');},assertCurrent(){counts.generation++;throw Error('ACTUAL_GENERATED_IMPORT_REQUIRED');}};
 const native:U0RequestNativeAssetsOwnerV2={assertCurrent(){counts.native++;throw Error('ACTUAL_NATIVE_BASIS_REQUIRED');},assertSelectionBasis(){counts.native++;throw Error('ACTUAL_SELECTED_BASIS_REQUIRED');},assets(){counts.native++;throw Error('ACTUAL_NATIVE_ASSETS_REQUIRED');}};
 const owner=createBusinessRequestStagesOwnerV2(recipes,generation,native);const fixed:BusinessRequestStagesOwnerV2=owner;
 return {owner,fixed,native,counts};
}
test('Q01 original recipe selection is mandatory before any early preparation',()=>{
 const {owner,counts}=missingStages();let reads=0;
 const fake={kind:'business-recipe-selection-v2',get models(){reads++;throw Error('must not inspect');}};
 for(const value of [fake,deriveDirectBusinessRequestSourceV2(transfer()),{kind:'bound-u0-entry-v2'},{}])assert.throws(()=>owner.prepareEarly(value as any),/UNREGISTERED/);
 assert.equal(reads,0);assert.deepEqual(counts,{native:0,generation:0});
});
test('Q01 late stage rejects foreign, cloned or late objects before touching native/callable producers',async()=>{
 const {owner,fixed,counts}=missingStages();
 for(const value of [{kind:'business-early-requests-v2'},{kind:'bound-u0-entry-v2'},{...deriveDirectBusinessRequestSourceV2(transfer())},new Proxy({}, {})]){
  assert.throws(()=>fixed.assertEarlyCurrent(value as any),/UNREGISTERED/);assert.throws(()=>owner.source(value as any),/UNREGISTERED/);
  await assert.rejects(()=>fixed.bindLate(value as any,{} as any,{} as any),/UNREGISTERED/);assert.throws(()=>fixed.assertBoundCurrent(value as any),/UNREGISTERED/);
 }
 assert.deepEqual(counts,{native:0,generation:0});
});
test('Q01 replacement of an original stage producer invalidates the factory',()=>{
 const {owner,native}=missingStages();native.assets=()=>{throw Error('replacement must not execute');};
 assert.throws(()=>owner.prepareEarly({} as any),/OWNER_STALE/);
});
test('Q01 pure plan data rejects absent actual callable/native/graph references and grants no custody',()=>{
 const source=deriveDirectBusinessRequestSourceV2(transfer());
 for(const binding of [{},{kind:'bound-u0-entry-v2'},{callable:()=>{}},{handler:()=>{}}])assert.throws(()=>composeDirectRequestApplicationPlanDataV2(source,binding as any));
 const {owner}=missingStages();assert.throws(()=>owner.assertBoundCurrent({kind:'direct-request-application-plan-data-v2'} as any),/UNREGISTERED/);
});
