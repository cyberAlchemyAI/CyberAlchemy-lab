import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {parseBusinessSourceV2} from '../src/business-authoring-parser.js';
import {resolveBusinessSpecV2,prepareBusinessSpecFileV2,disposeResolvedBusinessSpecV2} from '../src/business-authoring-resolve.js';
import {normalizeDirectBusinessV2,assertDirectBusinessNormalizationV2Current} from '../src/business-authoring-semantics.js';
import {lowerDirectBusinessBehaviorV2,assertDirectBusinessBehaviorV2Current} from '../src/business-authoring-behavior.js';
import {businessCanonical} from '../src/business-authoring-model.js';
// Open Questions: L01/Core graph/accepted/native owners and formal model output remain later.
const core=new URL('../../../../../../../craft/projects/domainspec-v2/impl/cli/',import.meta.url);
const source=readFileSync(new URL('test/profile-engine/fixtures/u0-v2/business.alch',core),'utf8');
const fixed=JSON.parse(readFileSync(new URL('test/profile-engine/fixtures/u0-v2/identity-vectors.json',core),'utf8')).vectors[0];
const normalize=(text=source)=>normalizeDirectBusinessV2(resolveBusinessSpecV2(parseBusinessSourceV2(text)));
const assurance=`
definition SuppliedVerified:
  requirement Processing
  input item Submission
  meaning "Supplied verification flag."
  boolean-field item.verified
formal-claim SuppliedFlag version 1:
  requirement Processing
  supersedes none
  profile fol-core/1-candidate
  sort SubmissionValue interpreted-as Submission
  predicate suppliedVerified(SubmissionValue) defined-by SuppliedVerified
  constant sample: SubmissionValue
  proposition suppliedVerified(sample)
  ceiling "A supplied value only; no verified delivery."
  subject CanProcess
  subject Process
`;
test('U02 genuine normalization matches the independent C02 canonical executable/assurance vectors',()=>{
 const normalized=normalize();assertDirectBusinessNormalizationV2Current(normalized);
 assert.equal(businessCanonical(normalized.executable),fixed.expected.executable_canonical);
 assert.equal(businessCanonical(normalized.assurance),fixed.expected.assurance_canonical);
 assert.equal(normalized.executable_sha256,fixed.expected.executable_sha256);
 assert.equal(normalized.assurance_sha256,fixed.expected.assurance_sha256);
 assert.equal(normalized.capture,normalized.business.source);assert.equal(normalized.source_sha256,normalized.capture.sha256);
 assert.deepEqual(JSON.parse(JSON.stringify(normalized.assurance)),{schema_version:'craft.business-assurance/v2-candidate',definitions:[],claims:[],authority_effect:'none'});
 assert.equal(Object.getPrototypeOf(normalized.assurance),null,'inert data projection retains its closed container');
 assert.equal(Object.hasOwn(normalized.executable,'claims'),false);assert.ok(Object.isFrozen(normalized.executable.rules));
});
test('U02 direct behavior retains all explicit typed guard/result/rejection/entry data without claims',()=>{
 const behavior=lowerDirectBusinessBehaviorV2(normalize());assertDirectBusinessBehaviorV2Current(behavior);
 assert.deepEqual(JSON.parse(JSON.stringify(behavior.data)),{
  schema_version:'craft.direct-business-behavior/v2-candidate',executable_sha256:fixed.expected.executable_sha256,
  entity:{kind:'entity',entity_ref:'Submission',identity:'id',fields:[{name:'id',type:'UInt64'},{name:'verified',type:'Bool'}]},
  rule:{id:'CanProcess',requirement_ref:'Processing',input:{name:'item',type_ref:'Submission'},condition:{kind:'boolean-field',value:{root:'item',path:['verified']}}},
  operation:{id:'Process',input:{name:'request',type_ref:'Submission'},output_ref:'Submission',guard:{rule_ref:'CanProcess',parameter:{name:'item',type_ref:'Submission'},argument:{root:'request',path:[]}},result:{root:'request',path:[]},rejection:{kind:'authored-guard-rejection',code:'delivery-verification-required'},effects:[]},
  entry:{id:'ProcessHttp',operation_ref:'Process',public_name:'confirm-delivery',permission:{kind:'public'}},authority_effect:'none',
 });
 assert.equal(Object.hasOwn(behavior.data,'formal'),false);assert.equal(Object.hasOwn(behavior.data.rule,'claim_ref'),false);
 assert.ok(Object.isFrozen(behavior.data.operation.guard.argument));
});
test('U02 optional claim edits affect assurance/capture while direct executable and behavior stay equal',()=>{
 const base=normalize(),claimed=normalize(source+assurance),edited=normalize(source+assurance.replace('proposition suppliedVerified(sample)','proposition not suppliedVerified(sample)'));
 for(const value of [claimed,edited]){
  assert.equal(value.executable_sha256,base.executable_sha256);
  assert.equal(lowerDirectBusinessBehaviorV2(value).behavior_sha256,lowerDirectBusinessBehaviorV2(base).behavior_sha256);
 }
 assert.notEqual(base.assurance_sha256,claimed.assurance_sha256);assert.notEqual(claimed.assurance_sha256,edited.assurance_sha256);
 assert.notEqual(base.source_sha256,claimed.source_sha256);assert.notEqual(claimed.source_sha256,edited.source_sha256);
 assert.equal(edited.review.assurance.claims[0]!.proposition,'not suppliedVerified(sample)');
 assert.throws(()=>normalize((source+assurance).replace('  condition item.verified\n','')),/BUSINESS_REQUIRED/);
});
test('U02 guard identity, parameter wiring, field, rejection and entry edits change executable behavior',()=>{
 const baseline=normalize(),baselineBehavior=lowerDirectBusinessBehaviorV2(baseline).behavior_sha256;
 const variants=[
  source.replaceAll('CanProcess','MayProcess'),
  source.replace('input item Submission','input acknowledgement Submission').replace('condition item.verified','condition acknowledgement.verified').replace('CanProcess(item: request)','CanProcess(acknowledgement: request)'),
  source.replaceAll('verified','approved'),
  source.replace('on-rejection delivery-verification-required','on-rejection another-rejection'),
  source.replace('public-name confirm-delivery','public-name accept-delivery'),
 ];
 for(const text of variants){const changed=normalize(text);assert.notEqual(changed.executable_sha256,baseline.executable_sha256);assert.notEqual(lowerDirectBusinessBehaviorV2(changed).behavior_sha256,baselineBehavior);}
 for(const [before,after] of [['requires CanProcess(item: request)','requires CanProcess(item: unknown)'],['returns request','returns unknown'],['condition item.verified','condition item.id']])assert.throws(()=>normalize(source.replace(before!,after!)),/BUSINESS_REFERENCE|BUSINESS_TYPE/);
});
test('U02 explanation-only and source-only edits stay in review/capture without invented execution meaning',()=>{
 const base=normalize(),prose=normalize(source.replace('Require the supplied verified flag.','The supplied verification flag must be true.')),comment=normalize('# commentary\n'+source);
 assert.equal(prose.executable_sha256,base.executable_sha256);assert.equal(comment.executable_sha256,base.executable_sha256);
 assert.notDeepEqual(prose.review.authored_rules,base.review.authored_rules);assert.notEqual(prose.source_sha256,base.source_sha256);
 assert.deepEqual(comment.review,base.review);assert.notEqual(comment.source_sha256,base.source_sha256);
});
test('U02 neither matching data nor a serialized normalized/behavior record has original custody',()=>{
 const value=normalize(),behavior=lowerDirectBusinessBehaviorV2(value);
 for(const foreign of [JSON.parse(JSON.stringify(value)),{...value},Object.create(value),new Proxy(value,{})])assert.throws(()=>assertDirectBusinessNormalizationV2Current(foreign),/BUSINESS_HANDLE/);
 for(const foreign of [JSON.parse(JSON.stringify(behavior)),{...behavior},Object.create(behavior),new Proxy(behavior,{})])assert.throws(()=>assertDirectBusinessBehaviorV2Current(foreign),/BUSINESS_HANDLE/);
 disposeResolvedBusinessSpecV2(value.business);
 assert.throws(()=>assertDirectBusinessNormalizationV2Current(value),/BUSINESS_DISPOSED/);
 assert.throws(()=>assertDirectBusinessBehaviorV2Current(behavior),/BUSINESS_DISPOSED/);
});
test('U02 claim-only physical source recapture invalidates old owners while preserving executable projection',()=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-u02-'));
 try{
  const file=path.join(root,'business.alch');writeFileSync(file,source);
  const original=normalizeDirectBusinessV2(prepareBusinessSpecFileV2(root,'business.alch')),behavior=lowerDirectBusinessBehaviorV2(original);
  writeFileSync(file,source+assurance);
  assert.throws(()=>assertDirectBusinessNormalizationV2Current(original),/BUSINESS_SOURCE_DRIFT/);
  assert.throws(()=>assertDirectBusinessBehaviorV2Current(behavior),/BUSINESS_SOURCE_DRIFT/);
  const recaptured=normalizeDirectBusinessV2(prepareBusinessSpecFileV2(root,'business.alch'));
  assert.equal(recaptured.executable_sha256,original.executable_sha256);assert.notEqual(recaptured.source_sha256,original.source_sha256);
 }finally{rmSync(root,{recursive:true,force:true});}
});
