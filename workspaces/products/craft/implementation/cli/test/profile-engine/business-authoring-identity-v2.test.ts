import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dataDigest,canonicalJson,captureJson} from '../../src/profile-engine/contracts.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2,directExecutableIdentityV2,optionalAssuranceIdentityV2,projectBusinessReviewSubjectV2,businessReviewIdentityV2,captureBusinessIdentityV2} from '../../src/profile-engine/business-authoring-identity-v2.js';
import {validateBusinessAuthoringContractV2} from '../../src/profile-engine/business-authoring-schema-v2.js';
// Independent fixed data identities only. Genuine original custody is K01/L02.
// Open Questions: docs/BUSINESS-IDENTITIES-V2.md.
const fixture=JSON.parse(readFileSync(new URL('fixtures/u0-v2/identity-vectors.json',import.meta.url),'utf8'));
const [base,optional,claimEdit]=fixture.vectors;
const plain=(v:unknown)=>JSON.parse(JSON.stringify(v));
test('C02 Core matches independent fixed canonical projections and SHA256 vectors',()=>{
 for(const {spec,expected} of fixture.vectors){
  assert.equal(canonicalJson(captureJson(projectDirectExecutableV2(spec))),expected.executable_canonical);
  assert.equal(directExecutableIdentityV2(spec).sha256,expected.executable_sha256);
  assert.equal(canonicalJson(captureJson(projectOptionalAssuranceV2(spec))),expected.assurance_canonical);
  assert.equal(optionalAssuranceIdentityV2(spec).sha256,expected.assurance_sha256);
  assert.equal(canonicalJson(captureJson(projectBusinessReviewSubjectV2(spec))),expected.review_canonical);
  assert.equal(businessReviewIdentityV2(spec).sha256,expected.review_sha256);
 }
 assert.equal(directExecutableIdentityV2(base.spec).sha256,'a9d937495394cf07732d52cc417d1804518dce516438c75b29b88d604d1486be');
});
test('C02 claims do not supply execution while assurance and review identities change',()=>{
 assert.equal(directExecutableIdentityV2(base.spec).sha256,directExecutableIdentityV2(optional.spec).sha256);
 assert.equal(directExecutableIdentityV2(optional.spec).sha256,directExecutableIdentityV2(claimEdit.spec).sha256);
 assert.notEqual(optionalAssuranceIdentityV2(optional.spec).sha256,optionalAssuranceIdentityV2(claimEdit.spec).sha256);
 assert.notEqual(businessReviewIdentityV2(optional.spec).sha256,businessReviewIdentityV2(claimEdit.spec).sha256);
 const prose=plain(base.spec);prose.rules[0].meaning='Another explanation of the same Boolean projection.';
 assert.equal(directExecutableIdentityV2(prose).sha256,directExecutableIdentityV2(base.spec).sha256);
 assert.notEqual(businessReviewIdentityV2(prose).sha256,businessReviewIdentityV2(base.spec).sha256);
 assert.equal(projectBusinessReviewSubjectV2(prose).authored_rules[0]!.meaning,prose.rules[0].meaning);
});
test('C02 behavior edits change executable subject; unsupported access/effects/legacy shapes reject',()=>{
 for(const mutate of [(s:any)=>{s.operations[0].on_rejection='other-rejection';},(s:any)=>{s.entries[0].public_name='other-entry';},(s:any)=>{s.entities[0].fields[1].name='approved';s.rules[0].condition.value.path=['approved'];}]){
  const value=plain(base.spec);mutate(value);assert.notEqual(directExecutableIdentityV2(value).sha256,directExecutableIdentityV2(base.spec).sha256);
 }
 for(const mutate of [(s:any)=>{s.entries[0].permission.kind='protected';},(s:any)=>{s.operations[0].effects=['write'];},(s:any)=>{s.schema_version='alchlang.business-spec/v1-candidate';},(s:any)=>{delete s.rules[0].condition;}]){
  const value=plain(base.spec);mutate(value);assert.throws(()=>directExecutableIdentityV2(value));
 }
});
const capture=(sha='a'.repeat(64))=>({schema_version:'craft.business-capture/v2-candidate',recipe_ref:'direct-entity-bool-operation/v2-candidate',source:{path:'business.alch',sha256:sha,bytes:123},profiles:[{id:'profile',version:'1.0.0',sha256:'b'.repeat(64)}],tools:[{id:'compiler',sha256:'c'.repeat(64)}],authority_effect:'none'});
test('C02 exact source/profile/tool capture changes independently of executable meaning',()=>{
 const original=captureBusinessIdentityV2(capture());
 for(const mutate of [(v:any)=>{v.source.sha256='d'.repeat(64);},(v:any)=>{v.profiles[0].sha256='e'.repeat(64);},(v:any)=>{v.tools[0].sha256='f'.repeat(64);}]){
  const value=capture();mutate(value);assert.notEqual(captureBusinessIdentityV2(value).capture_sha256,original.capture_sha256);
 }
 const duplicated=capture();duplicated.tools.push({...duplicated.tools[0]!});assert.throws(()=>captureBusinessIdentityV2(duplicated),/DUPLICATE/);
 assert.throws(()=>captureBusinessIdentityV2({...capture(),source:{...capture().source,path:'../outside.alch'}}));
 assert.equal(Object.hasOwn(original,'accepted'),false);assert.equal(Object.hasOwn(original,'callable_sha256'),false);
});
test('C02 declaration order is canonical while ordered business sequences retain their order',()=>{
 const value=plain(optional.spec);value.entities[0].fields.reverse();value.claims[0].subject_refs.reverse();
 assert.equal(directExecutableIdentityV2(value).sha256,directExecutableIdentityV2(optional.spec).sha256);
 assert.equal(optionalAssuranceIdentityV2(value).sha256,optionalAssuranceIdentityV2(optional.spec).sha256);
 const bounded=plain(base.spec);bounded.requirements[0].boundaries.push('A second explicit boundary.');
 const swapped=plain(bounded);swapped.requirements[0].boundaries.reverse();assert.notEqual(directExecutableIdentityV2(swapped).sha256,directExecutableIdentityV2(bounded).sha256);
});
test('C02 fixed data schemas reject self-approval and premature native application identity',()=>{
 const subject=projectBusinessReviewSubjectV2(base.spec);
 assert.throws(()=>validateBusinessAuthoringContractV2('review',{...subject,accepted:true}));
 assert.throws(()=>validateBusinessAuthoringContractV2('review',{...subject,graph:{ready:true}}));
 const lock={schema_version:'craft.business-authoring-lock/v2-candidate',model_id:'dispatching',capture_sha256:'a'.repeat(64),executable_sha256:'b'.repeat(64),assurance_sha256:'c'.repeat(64),basis_sha256:'d'.repeat(64),selection_sha256:'e'.repeat(64),review_sha256:'f'.repeat(64),decision_file_sha256:'a'.repeat(64),entry_intent_sha256:'b'.repeat(64),lock_sha256:'c'.repeat(64),authority_effect:'none'};
 validateBusinessAuthoringContractV2('lock',lock);
 for(const key of ['callable_sha256','handler_sha256','realized_sha256','accepted'])assert.throws(()=>validateBusinessAuthoringContractV2('lock',{...lock,[key]:'d'.repeat(64)}));
 assert.equal(Object.isFrozen(subject),true);assert.equal(Object.hasOwn(subject,'selection'),false);
});
test('C02 projections cannot execute accessors or proxies and do not accept unsupported schema names',()=>{
 let calls=0;assert.throws(()=>projectDirectExecutableV2({get schema_version(){calls++;return base.spec.schema_version;}} as any));assert.equal(calls,0);
 assert.throws(()=>projectDirectExecutableV2(new Proxy(base.spec,{})),/PROFILE_DATA_PROXY/);
 assert.throws(()=>validateBusinessAuthoringContractV2('foreign' as any,base.spec),/SCHEMA_REF/);
});
test('C02 actual v1 source schema and protocol retain their own claim-dependent contract',()=>{
 const schema=JSON.parse(readFileSync(new URL('../../contracts/business-spec-v1.schema.json',import.meta.url),'utf8'));
 assert.equal(schema.properties.claims.minItems,1);assert.ok(schema.$defs.rule.required.includes('claim_ref'));
 assert.equal(Object.hasOwn(schema.$defs.rule.properties,'condition'),false);
});
test('C02 fixed owner checker agrees with independent standard JSON Schema cases',()=>{
 for(const row of fixture.schema_cases){
  const run=()=>validateBusinessAuthoringContractV2(row.schema,row.value);
  if(row.valid)assert.doesNotThrow(run,row.id);else assert.throws(run,undefined,row.id);
 }
});
