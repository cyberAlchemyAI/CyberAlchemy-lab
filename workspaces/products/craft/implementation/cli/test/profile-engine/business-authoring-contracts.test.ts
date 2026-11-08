import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {dataDigest,canonicalJson,captureJson} from '../../src/profile-engine/contracts.js';
import {validateBusinessAuthoringContract,BUSINESS_AUTHORING_SCHEMAS} from '../../src/profile-engine/business-authoring-contracts.js';
const repository=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../../../../..');
const contracts=path.join(repository,'research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan/contracts');
const json=(name:string)=>JSON.parse(readFileSync(path.join(contracts,name),'utf8'));
const spec=json('reference-spec.json');
test('B01: fixed authoring schemas validate captured shape without acceptance or graph registration',()=>{
 const result=validateBusinessAuthoringContract<any>('spec',spec);
 assert.equal(result.schema_version,'alchlang.business-spec/v1-candidate');assert.equal(result.authority_effect,'none');assert.ok(Object.isFrozen(result.entities[0]));
 assert.equal(Object.hasOwn(result,'accepted'),false);assert.equal(Object.hasOwn(result,'graph'),false);
});
test('B01: unsupported capability/logic/effects/shape and injected acceptance reject',()=>{
 for(const mutation of [(x:any)=>x.accepted=true,(x:any)=>x.operations[0].effects.push('write'),(x:any)=>x.claims[0].logic_profile='any-logic',(x:any)=>x.capabilities[0].audience='authenticated',(x:any)=>x.entities[0].fields[0].type='Float64',(x:any)=>x.operations[0].result.path.push('label'),(x:any)=>x.definitions[0].native='code']){
  const input=structuredClone(spec);mutation(input);assert.throws(()=>validateBusinessAuthoringContract('spec',input),/BUSINESS_SCHEMA/);
 }
 assert.throws(()=>validateBusinessAuthoringContract('unknown' as any,{}),/BUSINESS_SCHEMA_REF/);
});
test('B01: authored examples and boundaries cannot be omitted or replaced by boilerplate',()=>{
 for(const name of ['examples','counterexamples','boundaries']){const input=structuredClone(spec);input.requirements[0][name]=[];assert.throws(()=>validateBusinessAuthoringContract('spec',input),/BUSINESS_SCHEMA_LIMIT/);}
 const input=structuredClone(spec);delete input.requirements[0].examples[0].why;assert.throws(()=>validateBusinessAuthoringContract('spec',input),/BUSINESS_SCHEMA_REQUIRED/);
});
test('B01: schema capture never invokes getters/proxies or accepts unsafe numeric data',()=>{
 let calls=0;const input={get schema_version(){calls++;return spec.schema_version;}};
 assert.throws(()=>validateBusinessAuthoringContract('spec',input));assert.equal(calls,0);
 assert.throws(()=>validateBusinessAuthoringContract('spec',new Proxy(spec,{})),/PROFILE_DATA_PROXY/);
 assert.throws(()=>validateBusinessAuthoringContract('spec',{...spec,extra:2**64}),/PROFILE_DATA_NUMBER/);
});
test('B01: independent canonical JSON, Unicode, exact integer and legacy meaning vectors agree',()=>{
 const vectors=json('golden-vectors.json').vectors;for(const v of vectors){assert.equal(canonicalJson(captureJson(v.value)),v.canonical_json,v.id);assert.equal(dataDigest(v.value),v.sha256,v.id);}
 assert.notEqual(vectors.find((v:any)=>v.id==='unicode-composed').sha256,vectors.find((v:any)=>v.id==='unicode-decomposed').sha256);
 assert.notEqual(vectors.find((v:any)=>v.id==='ordered-sequence').sha256,vectors.find((v:any)=>v.id==='reversed-sequence').sha256);
 assert.equal(vectors.at(-1).sha256,'401a3008332a9eaed7e667546f2937179304be88622aef83c2fb651981c62b9a');
});
test('B01: project has no handwritten semantic/request map and wire is a finite technical convention',()=>{
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'dispatching',models:[{id:'dispatching',source:'business.alch'}],profiles:[{id:'node-http-entry-local-v3',version:'1.0.0',path:'profiles/local'}],decisions:[]};
 validateBusinessAuthoringContract('project',project);assert.throws(()=>validateBusinessAuthoringContract('project',{...project,semantics:'semantic.json'}),/BUSINESS_SCHEMA_UNKNOWN/);
 for(const source of ['../foreign.alch','/absolute.alch','folder/../foreign.alch','folder\\foreign.alch'])assert.throws(()=>validateBusinessAuthoringContract('project',{...project,models:[{id:'dispatching',source}]}),/BUSINESS_SCHEMA_VALUE/);
 const wire={schema_version:'craft.operation-json-post/v1-candidate',method:'POST',body:'whole-input',route_prefix:'/api/',request_bytes:8192,timeout_ms:1500};validateBusinessAuthoringContract('wire',wire);
 assert.throws(()=>validateBusinessAuthoringContract('wire',{...wire,body:'infer'}),/BUSINESS_SCHEMA_CONST/);
});
test('B01: data-only Alch mirror and exported schema inventory have a single owner',()=>{
 const core=readFileSync(path.join(repository,'craft/projects/domainspec-v2/impl/cli/src/profile-engine/business-authoring-protocol.ts'),'utf8');
 const mirror=readFileSync(path.join(repository,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-authoring-protocol.ts'),'utf8');
 assert.equal(mirror,'// GENERATED from Core business-authoring-protocol.ts; canonical owner is Core.\n'+core);
 const freeze=json('contract-freeze.json');assert.deepEqual([...freeze.schemas].sort(),Object.values(BUSINESS_AUTHORING_SCHEMAS).sort());
 assert.equal(freeze.successor_versions.craft,'1.3.0');assert.equal(freeze.successor_versions.alchlang,'0.7.0-candidate.0');
});
test('B01: review separates business subjects from decisions, source positions and wire selection',()=>{
 const legacy=JSON.parse(readFileSync(path.join(repository,'craft/projects/domainspec-v2/impl/cli/examples/profile-engine/business-acknowledgement/business-semantics.json'),'utf8')).claim_meanings.DeliveryReady;
 const definition=structuredClone(legacy.definitions[0]);delete definition.status;
 const subject={meaning_id:legacy.business_meaning.meaning_id,version:'1',canonicalization:'domainspec-json-keysort-excluding-acceptance-v1',digest_algorithm:'sha256',digest:legacy.owner_acceptance.subject.digest};
 const review={schema_version:'craft.business-review/v1-candidate',normalization_contract:'craft.business-authoring-contracts/1-candidate',model_identity:spec.identity,declarations:spec.entities,definitions:[definition],claims:spec.claims,interpretations:[{rule_ref:'CanConfirm',sorts:{DeliveryValue:'Delivery'},constants:{current:'delivery'},predicates:{Permitted:'verified'}}],behaviors:spec.operations,exposures:spec.capabilities,requirements:spec.requirements,legacy_meaning_subjects:[subject]};
 validateBusinessAuthoringContract('review',review);
 for(const key of ['decision','acceptance','status','source_spans','profiles','wire'])assert.throws(()=>validateBusinessAuthoringContract('review',{...review,[key]:{}}),/BUSINESS_SCHEMA_UNKNOWN/);
 const decision={schema_version:'craft.business-decision/v1-candidate',decision_id:'synthetic-shape-only',owner:'dispatch-team',outcome:'accepted',subject:{model_id:'dispatching',version:'1',canonicalization:'craft.business-review-keysort/v1',digest_algorithm:'sha256',digest:dataDigest(review)},legacy_meaning_subjects:[subject],definition_closure:{definition_ids:[definition.definition_id],digest_algorithm:'sha256',digest:dataDigest([definition])},authority_effect:'none'};
 validateBusinessAuthoringContract('decision',decision);assert.equal(Object.hasOwn(review,'decision'),false);
});
test('B01: v3 explicitly declares one supported authoring convention; v2 remains distinct',()=>{
 const old=JSON.parse(readFileSync(path.join(repository,'craft/projects/domainspec-v2/impl/cli/profiles/node-http-entry-local-v2/profile.json'),'utf8'));
 assert.throws(()=>validateBusinessAuthoringContract('package',old),/BUSINESS_SCHEMA/);
 const next={...old,schema_version:'craft.profile-package/v3-candidate',id:'node-http-entry-local-v3',engine:'craft.profile-engine/v3-candidate',authoring:{contract:'craft.business-authoring-contracts/1-candidate',input_schema:'alchlang.business-spec/v1-candidate',recipe_ref:'ground-entity-bool-operation/v1-candidate',logic_profile:'fol-core/1-candidate',target:'node-typescript',effects:'none',wire:{schema_version:'craft.operation-json-post/v1-candidate',method:'POST',body:'whole-input',route_prefix:'/',request_bytes:16384,timeout_ms:2000}}};
 validateBusinessAuthoringContract('package',next);
 for(const key of ['recipe_ref','logic_profile','target','effects'])assert.throws(()=>validateBusinessAuthoringContract('package',{...next,authoring:{...next.authoring,[key]:'invented'}}),/BUSINESS_SCHEMA_CONST/);
 assert.equal(old.schema_version,'craft.profile-package/v2-candidate');
});
