import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkCoreDirectBusinessRecipeV2,validateCoreDirectRecipeRequirementsV2,validateCoreDirectNativeContractV2,createBusinessCoreRecipeOwnerV2} from '../src/profile-engine/business-authoring-recipes.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2} from '../src/profile-engine/business-authoring-identity-v2.js';
import {BUSINESS_AUTHORING_CONTRACT} from '../src/profile-engine/business-authoring-protocol.js';
import {U0_CONFIG_EXAMPLE} from '../src/profile-engine/u0-realization-contract.js';
import {sha256,canonicalJson,captureJson} from '../src/profile-engine/contracts.js';
// Independent C01/C02 source/DTO/canonical vectors; no Alch runtime import.
// Tests of data/ABI contracts do not mint a native basis or selection.
// Open Questions: real production capture owner/selection at J01/J02; graph at L02/G01.
const fixture=new URL('profile-engine/fixtures/u0-v2/',import.meta.url);
const source=readFileSync(new URL('business.alch',fixture),'utf8'),base=JSON.parse(readFileSync(new URL('spec.json',fixture),'utf8'));
const vectors=JSON.parse(readFileSync(new URL('identity-vectors.json',fixture),'utf8')).vectors;
const clone=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
function transfer(text=source,spec:any=clone(base)){
 const hash=sha256(text),rows=text.split('\n').map((line,i,lines)=>({raw:i<lines.length-1?line.replace(/\r$/,''):line,line:i+1})).filter(row=>row.raw.trim()&&!row.raw.trimStart().startsWith('#'));
 spec.source_spans=rows.map(row=>({selector:'line:'+row.line,source:'business.alch',line:row.line,column:row.raw.length-row.raw.trimStart().length+1,text:row.raw,source_sha256:hash}));
 spec.obligations=rows.map(row=>({selector:'line:'+row.line,kind:'clause',span_selector:'line:'+row.line}));
 return {source:{path:'business.alch',text,sha256:hash,bytes:Buffer.byteLength(text)},spec,executable:projectDirectExecutableV2(spec),assurance:projectOptionalAssuranceV2(spec)};
}
const optional=`
definition Eligibility:
  requirement Processing
  input item Submission
  meaning "Supplied eligibility."
  boolean-field item.verified

formal-claim EligibilityClaim version 1:
  requirement Processing
  supersedes none
  profile fol-core/1-candidate
  sort SubmissionValue interpreted-as Submission
  predicate Eligible(SubmissionValue) defined-by Eligibility
  constant current: SubmissionValue
  proposition Eligible(current)
  ceiling "One supplied flag; no proof."
  subject CanProcess
  subject Process
`;
test('U03 independent source check matches fixed canonical subjects with no formal claims',()=>{
 const value=checkCoreDirectBusinessRecipeV2(transfer());
 assert.equal(value.executable_sha256,'a9d937495394cf07732d52cc417d1804518dce516438c75b29b88d604d1486be');
 assert.equal(canonicalJson(captureJson(value.transfer.executable)),vectors[0].expected.executable_canonical);
 assert.equal(canonicalJson(captureJson(value.transfer.assurance)),vectors[0].expected.assurance_canonical);
 assert.equal(value.transfer.spec.claims.length,0);assert.ok(Object.isFrozen(value));
 assert.equal(value.roles.selectors.rule,'dispatching:can-process');
 assert.deepEqual(clone(value.roles.typed_rule.expression),{op:'eq',left:{op:'path',root:'item',properties:['BUSINESS-DISPATCHING-SUBMISSION#verified']},right:{op:'literal',type:'Bool',value:true}});
 assert.equal(value.roles.guard_parameter,'item');assert.equal(value.roles.guard_root,'request');assert.equal(value.roles.result_root,'request');assert.equal(value.roles.rejection,'delivery-verification-required');
 assert.equal(Object.hasOwn(value,'selection_sha256'),false);assert.equal(Object.hasOwn(value,'accepted'),false);
});
test('U03 optional assurance retains fixed identities without contributing execution',()=>{
 const spec=clone(vectors[1].spec),value=checkCoreDirectBusinessRecipeV2(transfer(source+optional,spec));
 assert.equal(value.executable_sha256,vectors[0].expected.executable_sha256);assert.equal(value.assurance_sha256,vectors[1].expected.assurance_sha256);
 assert.deepEqual(clone(value.transfer.assurance.claims[0].subject_refs),['CanProcess','Process']);
 const changed=clone(spec);changed.claims[0].proposition='not Eligible(current)';
 const next=checkCoreDirectBusinessRecipeV2(transfer(source+optional.replace('proposition Eligible(current)','proposition not Eligible(current)'),changed));
 assert.equal(next.executable_sha256,value.executable_sha256);assert.notEqual(next.assurance_sha256,value.assurance_sha256);
});
test('U03 finite optional FOL independently checks equality, precedence, sorts and symbol use',()=>{
 const spec=clone(vectors[1].spec);spec.claims[0].proposition='(Eligible(current) and current = current) implies not not Eligible(current)';
 assert.doesNotThrow(()=>checkCoreDirectBusinessRecipeV2(transfer(source+optional.replace('proposition Eligible(current)','proposition '+spec.claims[0].proposition),spec)));
 for(const formula of ['Unknown(current)','Eligible(missing)','Eligible(current) and','Eligible(current) iff Eligible(current) iff Eligible(current)','forall x: SubmissionValue: Eligible(x)','current = current']){
  const changed=clone(vectors[1].spec);changed.claims[0].proposition=formula;
  assert.throws(()=>checkCoreDirectBusinessRecipeV2(transfer(source+optional.replace('proposition Eligible(current)','proposition '+formula),changed)),/BUSINESS_DIRECT_ASSURANCE/);
 }
});
test('U03 a forged well-shaped DTO cannot replace a condition, guard, result, rejection or public name',()=>{
 for(const mutate of [
  (s:any)=>{s.entities[0].fields[1].name='approved';s.rules[0].condition.value.path=['approved'];},
  (s:any)=>{s.rules[0].meaning='Different explanation.';},
  (s:any)=>{s.operations[0].guards[0].arguments[0].parameter='other';},
  (s:any)=>{s.operations[0].result.root='other';},
  (s:any)=>{s.operations[0].on_rejection='other-code';},
  (s:any)=>{s.entries[0].public_name='other-entry';},
 ]){const spec=clone(base);mutate(spec);assert.throws(()=>checkCoreDirectBusinessRecipeV2(transfer(source,spec)),/BUSINESS_DIRECT_SOURCE/);}
});
test('U03 matching source/DTO still requires the actual Bool and correct explicit reference types',()=>{
 const cases:[string,string,(s:any)=>void][]=[
  ['condition item.verified','condition item.id',s=>{s.rules[0].condition.value.path=['id'];}],
  ['requires CanProcess(item: request)','requires Missing(item: request)',s=>{s.operations[0].guards[0].rule_ref='Missing';}],
  ['returns request','returns missing',s=>{s.operations[0].result.root='missing';}],
  ['identity id','identity verified',s=>{s.entities[0].identity='verified';}],
  ['invokes Process','invokes Missing',s=>{s.entries[0].operation_ref='Missing';}],
 ];
 for(const [before,after,mutate] of cases){const spec=clone(base);mutate(spec);assert.throws(()=>checkCoreDirectBusinessRecipeV2(transfer(source.replace(before,after),spec)),/BUSINESS_DIRECT_(CONDITION|TYPE|OPERATION|ENTRY)/);}
});
test('U03 every containing declaration/scenario/fact is required; unsupported source cannot hide in spans',()=>{
 for(const text of [source.replace('  condition item.verified\n',''),source.replace('  effects none\n',''),source.replace('    why "The authored Boolean condition is true."\n',''),source+'\n  native "run javascript"\n',source+'\nentity Unknown:\n  meaning "Not in the DTO."\n',source.replace('source-contract alchlang.business-spec/v2-candidate','source-contract other')])assert.throws(()=>checkCoreDirectBusinessRecipeV2(transfer(text)),/BUSINESS_DIRECT_SOURCE/);
 const value=transfer();value.spec.source_spans.pop();assert.throws(()=>checkCoreDirectBusinessRecipeV2(value),/SOURCE_COVERAGE/);
 const duplicate=transfer();duplicate.spec.obligations[1]={...duplicate.spec.obligations[0]};assert.throws(()=>checkCoreDirectBusinessRecipeV2(duplicate),/CORRESPONDENCE/);
});
test('U03 ordered business lists cannot be swapped behind the same physical source',()=>{
 const text=source.replace('  actor "Delivery API caller"','  actor "First caller"\n  actor "Second caller"'),spec=clone(base);spec.requirements[0].actors=['First caller','Second caller'];
 assert.doesNotThrow(()=>checkCoreDirectBusinessRecipeV2(transfer(text,spec)));
 const swapped=clone(spec);swapped.requirements[0].actors.reverse();assert.throws(()=>checkCoreDirectBusinessRecipeV2(transfer(text,swapped)),/SOURCE_CORRESPONDENCE/);
});
test('U03 legal prose escapes, independent clause order, CRLF and comments retain exact capture',()=>{
 const escaped=source.replace('  meaning "Require the supplied verified flag."','  meaning "Require the supplied \\u0076erified flag."');
 assert.equal(checkCoreDirectBusinessRecipeV2(transfer(escaped)).executable_sha256,vectors[0].expected.executable_sha256);
 const reordered=source.replace('  returns request\n  on-rejection delivery-verification-required','  on-rejection delivery-verification-required\n  returns request');assert.doesNotThrow(()=>checkCoreDirectBusinessRecipeV2(transfer(reordered)));
 const crlf='# capture commentary\r\n'+source.replaceAll('\n','\r\n');const value=checkCoreDirectBusinessRecipeV2(transfer(crlf));assert.equal(value.transfer.source.text,crlf);assert.equal(value.executable_sha256,vectors[0].expected.executable_sha256);
});
test('U03 frontend projection or version substitution rejects even when the source itself is valid',()=>{
 for(const mutate of [(v:any)=>{v.executable.rules=[];},(v:any)=>{v.executable.operations[0].result.root='other';},(v:any)=>{v.executable.entries[0].permission={kind:'protected'};},(v:any)=>{v.assurance.definitions=[{id:'invented'}];}]){const value=clone(transfer());mutate(value);assert.throws(()=>checkCoreDirectBusinessRecipeV2(value),/BUSINESS_DIRECT_CORRESPONDENCE/);}
 assert.throws(()=>checkCoreDirectBusinessRecipeV2({...transfer(),accepted:true}),/SHAPE/);
 const wrong=transfer();wrong.spec.schema_version='alchlang.business-spec/v1-candidate';assert.throws(()=>checkCoreDirectBusinessRecipeV2(wrong),/SCHEMA/);
});
test('U03 finite recipe and native contracts reject unknown primitives/ABI without resolving assets',()=>{
 assert.equal(validateCoreDirectRecipeRequirementsV2().effects,'none');
 assert.throws(()=>validateCoreDirectRecipeRequirementsV2({source_contract:'alchlang.business-spec/v2-candidate',recipe_ref:'another-primitive',target:'node-typescript',effects:'none',entry_access:'public'}),/CORRESPONDENCE/);
 assert.throws(()=>validateCoreDirectRecipeRequirementsV2({...validateCoreDirectRecipeRequirementsV2(),logic_profile:'required'}),/SHAPE/);
 assert.doesNotThrow(()=>validateCoreDirectNativeContractV2({abi:'craft.u0.pure-submission/v1-candidate',descriptor:'node-http-entry-u0-v4',configuration:U0_CONFIG_EXAMPLE}));
 assert.throws(()=>validateCoreDirectNativeContractV2({abi:'unregistered' as any,descriptor:'node-http-entry-u0-v4',configuration:U0_CONFIG_EXAMPLE}),/NATIVE_CONTRACT/);
 assert.throws(()=>validateCoreDirectNativeContractV2({abi:'craft.u0.pure-submission/v1-candidate',descriptor:'node-http-entry-local-v3' as any,configuration:U0_CONFIG_EXAMPLE}),/NATIVE_CONTRACT/);
});
test('U03 inert transfer and actual source budgets cannot execute accessors or aliases',()=>{
 let calls=0;assert.throws(()=>checkCoreDirectBusinessRecipeV2({get source(){calls++;return transfer().source;}}));assert.equal(calls,0);
 assert.throws(()=>checkCoreDirectBusinessRecipeV2(new Proxy(transfer(),{})),/PROXY/);
 for(const path of ['../outside.alch','/outside.alch','a\\b.alch']){const value=transfer();value.source.path=path;assert.throws(()=>checkCoreDirectBusinessRecipeV2(value),/BUSINESS_DIRECT_SOURCE/);}
 const large=transfer();large.source.text='#'.repeat(1048577);large.source.bytes=1048577;large.source.sha256=sha256(large.source.text);assert.throws(()=>checkCoreDirectBusinessRecipeV2(large),/BUSINESS_DIRECT_SOURCE/);
 assert.equal(BUSINESS_AUTHORING_CONTRACT,'craft.business-authoring-contracts/1-candidate');
});
test('U03 instance-scoped selection cannot be forged by JSON or an unavailable native capture',()=>{
 let captures=0;const owner=createBusinessCoreRecipeOwnerV2({assertCurrent(){throw Error('ACTUAL_NATIVE_BASIS_REQUIRED');},capture(){captures++;throw Error('no fixture native producer');}});
 assert.throws(()=>owner.select([],{abi:'craft.u0.pure-submission/v1-candidate'} as any),/ACTUAL_NATIVE_BASIS_REQUIRED/);
 for(const fake of [{kind:'business-recipe-selection-v2'},JSON.parse(JSON.stringify(transfer()))]){assert.throws(()=>owner.assertCurrent(fake as any),/UNREGISTERED/);assert.throws(()=>owner.dispose(fake as any),/UNREGISTERED/);}
 assert.equal(captures,0,'a rejected native basis cannot mint a successful selection');
});
