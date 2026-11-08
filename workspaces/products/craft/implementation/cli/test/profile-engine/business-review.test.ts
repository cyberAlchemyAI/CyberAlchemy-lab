import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,renameSync,rmSync,writeFileSync,readdirSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {loadBusinessAuthoringProject} from '../../src/profile-engine/loader-v3.js';
import {selectBusinessAuthoringRecipe} from '../../src/profile-engine/business-authoring-recipes.js';
import {prepareBusinessAuthoringReview,assertBusinessAuthoringReviewCurrent,renderBusinessAuthoringReview,type PreparedBusinessAuthoringReview} from '../../src/profile-engine/business-review.js';
import {ProfileRejected} from '../../src/profile-engine/contracts.js';
import type {BusinessRecipeModelInput} from '../../src/profile-engine/business-authoring-normalization-protocol.js';
import type {BusinessReviewSubject} from '../../src/profile-engine/business-authoring-protocol.js';
// Independent inert Core DTO fixtures. Core data validation is not Alch handle authentication.
// Open questions: B04.2 decision capture and B06.2 accepted materialization.
const cli=path.resolve(import.meta.dirname,'../..'),clone=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
const hash=(value:string|Buffer)=>createHash('sha256').update(value).digest('hex');
const canonical=(value:any):string=>Array.isArray(value)?'['+value.map(canonical).join(',')+']':value!==null&&typeof value==='object'?'{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+canonical(value[key])).join(',')+'}':JSON.stringify(value);
const digest=(value:unknown)=>hash(canonical(value));
const recipe='ground-entity-bool-operation/v1-candidate',normalization='craft.business-normalization/1-candidate';
const atom=()=>({kind:'predicate',name:'Eligible',arguments:[{kind:'constant',name:'submitted',sort:'SubmissionValue'}]});
function independentInput(modelId='fixture',relative='business.alch'):{text:string;input:BusinessRecipeModelInput} {
 const text=`business-model ${modelId} version 1 "Submission receipt"
owner receipt-team

requirement SubmissionAllowed:
  context "A submission is received."
  meaning "Return an eligible submission."
  applies-when "Submit is called."
  actor "Submission caller"
  does-not-mean "The flag does not authenticate the caller."
  example allowed:
    given "Eligible submission."
    when "Submit is called."
    then "Return it."
    why "The Boolean field is true."
  counterexample blocked:
    given "Ineligible submission."
    when "Submit is called."
    then "Reject it."
    why "The Boolean field is false."

entity Submission:
  meaning "A received submission."
  id UInt64 meaning "Submission identity."
  eligible Bool meaning "Caller supplied eligibility."
  label String meaning "Unchanged label."
  identity id

definition EligibilityDefinition:
  requirement SubmissionAllowed
  input item Submission
  meaning "Check the eligibility field."
  boolean-field item.eligible

formal-claim EligibilityClaim version 1:
  requirement SubmissionAllowed
  supersedes none
  profile fol-core/1-candidate
  sort SubmissionValue interpreted-as Submission
  predicate Eligible(SubmissionValue) defined-by EligibilityDefinition
  constant submitted: SubmissionValue
  proposition Eligible(submitted)
  ceiling "One supplied submission, without external verification."

rule CheckEligibility:
  meaning "Require the complete eligibility condition."
  input item Submission
  claim EligibilityClaim
  bind submitted <- item

operation Submit:
  meaning "Return the supplied eligible submission."
  input request Submission
  output Submission
  requires CheckEligibility(item: request)
  returns request
  on-rejection return-submission-error
  effects none

capability SubmissionEndpoint:
  invokes Submit
  public-name submit
  audience public
`;
 const source={path:relative,sha256:hash(text),bytes:Buffer.byteLength(text)};
 const requirement={id:'SubmissionAllowed',context:'A submission is received.',meaning:'Return an eligible submission.',applies_when:['Submit is called.'],actors:['Submission caller'],boundaries:['The flag does not authenticate the caller.'],examples:[{case_id:'allowed',given:'Eligible submission.',when:'Submit is called.',then:'Return it.',why:'The Boolean field is true.'}],counterexamples:[{case_id:'blocked',given:'Ineligible submission.',when:'Submit is called.',then:'Reject it.',why:'The Boolean field is false.'}]};
 const entity={id:'Submission',meaning:'A received submission.',fields:[{name:'id',type:'UInt64',meaning:'Submission identity.'},{name:'eligible',type:'Bool',meaning:'Caller supplied eligibility.'},{name:'label',type:'String',meaning:'Unchanged label.'}],identity:'id'};
 const definition={id:'EligibilityDefinition',requirement_ref:'SubmissionAllowed',input:{name:'item',type_ref:'Submission'},meaning:'Check the eligibility field.',boolean_field:{root:'item',path:['eligible']}};
 const claim={id:'EligibilityClaim',version:'1',supersedes:null,requirement_ref:'SubmissionAllowed',logic_profile:'fol-core/1-candidate',sorts:[{name:'SubmissionValue',type_ref:'Submission'}],predicates:[{name:'Eligible',sort_refs:['SubmissionValue'],definition_ref:'EligibilityDefinition'}],constants:[{name:'submitted',sort_ref:'SubmissionValue'}],proposition:'Eligible(submitted)',ceiling:'One supplied submission, without external verification.'};
 const rule={id:'CheckEligibility',meaning:'Require the complete eligibility condition.',input:{name:'item',type_ref:'Submission'},claim_ref:'EligibilityClaim',bindings:[{constant_ref:'submitted',parameter_ref:'item'}]};
 const operation={id:'Submit',meaning:'Return the supplied eligible submission.',input:{name:'request',type_ref:'Submission'},output_ref:'Submission',guards:[{rule_ref:'CheckEligibility',arguments:[{parameter:'item',value:{root:'request',path:[]}}]}],result:{root:'request',path:[]},on_rejection:'return-submission-error',effects:[]};
 const capability={id:'SubmissionEndpoint',operation_ref:'Submit',public_name:'submit',audience:'public'};
 const facts=text.split('\n').flatMap((raw,index)=>raw.trim()&&!raw.trimStart().startsWith('#')?[{selector:'original-fact/line:'+(index+1),source:relative,line:index+1,column:raw.length-raw.trimStart().length+1,text:raw,source_sha256:source.sha256}]:[]);
 const spec:any={schema_version:'alchlang.business-spec/v1-candidate',identity:{namespace:modelId,stable_id:modelId,version:'1',title:'Submission receipt',owner:'receipt-team'},requirements:[requirement],entities:[entity],definitions:[definition],claims:[claim],rules:[rule],operations:[operation],capabilities:[capability],source_spans:facts,obligations:facts.map(fact=>({selector:fact.selector,kind:'clause',span_selector:fact.selector})),authority_effect:'none'};
 const {source_spans:_s,obligations:_o,...semantic}=spec;
 const business=digest({...semantic,entities:[{...entity,fields:[entity.fields[1],entity.fields[0],entity.fields[2]]}]});
 const structure={kind:'entity',entity_ref:'Submission',identity:'id',fields:[{name:'eligible',type:'Bool'},{name:'id',type:'UInt64'},{name:'label',type:'String'}]};
 const formal:any={schema_version:'craft.business-formal-normalization/v1-candidate',normalization_contract:normalization,model_id:modelId,business_sha256:business,definitions:[{definition_ref:'EligibilityDefinition',requirement_ref:'SubmissionAllowed',input:{name:'item',type_ref:'Submission'},entity:structure,field:entity.fields[1],primitive:{kind:'entity-bool-field',entity_ref:'Submission',parameter:'item',field:'eligible',field_type:'Bool',comparison:'eq',value:true},formal:{definition:'EligibilityDefinition(item: Submission) := (item.eligible = true)',expression:'EligibilityClaim::Eligible(item: SubmissionValue) iff (item.eligible = true)',notation:[{symbol:'item',meaning:'A received submission.'},{symbol:'item.eligible',meaning:'Caller supplied eligibility.'}],operational_interpretation:'Read item.eligible: Bool and compare with true.'},predicate_uses:[{claim_ref:'EligibilityClaim',predicate_ref:'Eligible',sort_ref:'SubmissionValue'}]}],claims:[{claim_ref:'EligibilityClaim',version:'1',logic_profile:'fol-core/1-candidate',signature:{sorts:[{name:'SubmissionValue'}],functions:[],predicates:[{name:'Eligible',parameter_sorts:['SubmissionValue']}],constants:[{name:'submitted',sort:'SubmissionValue'}]},proposition_source:claim.proposition,proposition:atom(),ceiling:claim.ceiling}],rule_meanings:{CheckEligibility:{sorts:{SubmissionValue:'Submission'},constants:{submitted:'item'},predicates:{Eligible:'eligible'}}},authority_effect:'none'};
 const behavior:any={schema_version:'craft.business-behavior-normalization/v1-candidate',normalization_contract:normalization,model_id:modelId,business_sha256:business,formal_sha256:digest(formal),operations:[{operation_ref:'Submit',meaning:operation.meaning,input:{name:'request',type:structure},output:structure,guards:[{rule_ref:'CheckEligibility',claim_ref:'EligibilityClaim',parameter:{name:'item',type:structure},argument:{root:'request',path:[]}}],result:{root:'request',path:[],type:structure},effects:[],failure:{kind:'continuation-metadata',continuation:'return-submission-error',executable:false}}],exposures:[capability],contexts:[requirement],actor_semantics:'informational-only',authority_effect:'none'};
 return {text,input:{model_id:modelId,source,spec,formal,behavior}};
}
function recalculate(input:any):void {
 const {source_spans:_s,obligations:_o,...semantic}=input.spec;
 const sort=(rows:any[],key:string)=>[...rows].sort((a,b)=>a[key]<b[key]?-1:a[key]>b[key]?1:0);
 const business=digest({...semantic,requirements:sort(input.spec.requirements,'id'),entities:sort(input.spec.entities,'id').map(entity=>({...entity,fields:sort(entity.fields,'name')})),definitions:sort(input.spec.definitions,'id'),claims:sort(input.spec.claims,'id').map(claim=>({...claim,sorts:sort(claim.sorts,'name'),predicates:sort(claim.predicates,'name'),constants:sort(claim.constants,'name')})),rules:sort(input.spec.rules,'id'),operations:sort(input.spec.operations,'id'),capabilities:sort(input.spec.capabilities,'id')});
 input.formal.business_sha256=business;input.behavior.business_sha256=business;input.behavior.formal_sha256=digest(input.formal);
}
function fixture(t:{after(fn:()=>void):void},variant='node-http-entry-local-v2'){
 const root=mkdtempSync(path.join(os.tmpdir(),'business-recipe-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const write=(relative:string,value:unknown)=>{const file=path.join(root,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');return file;};
 cpSync(path.join(cli,'profiles',variant),path.join(root,'profile'),{recursive:true});
 const profile=JSON.parse(readFileSync(path.join(root,'profile/profile.json'),'utf8'));
 const technical=variant==='node-http-api-prefix-v2'?{route_prefix:'/api/',request_bytes:8192,timeout_ms:1500}:{route_prefix:'/',request_bytes:16384,timeout_ms:2000};
 Object.assign(profile,{schema_version:'craft.profile-package/v3-candidate',id:variant.replace(/v2$/,'v3'),engine:'craft.profile-engine/v3-candidate',authoring:{contract:'craft.business-authoring-contracts/1-candidate',input_schema:'alchlang.business-spec/v1-candidate',recipe_ref:recipe,logic_profile:'fol-core/1-candidate',target:'node-typescript',effects:'none',wire:{schema_version:'craft.operation-json-post/v1-candidate',method:'POST',body:'whole-input',...technical}}});
 write('profile/profile.json',profile);
 const authored=independentInput();write('business.alch',authored.text);
 const project={schema_version:'craft.business-authoring-project/v1-candidate',id:'fixture-project',models:[{id:'fixture',source:'business.alch'}],profiles:[{id:profile.id,version:'1.0.0',path:'profile'}],decisions:[]};
 const file=write('project.json',project);write('identity/core.ts',readFileSync(path.join(cli,'src/profile-engine/loader-v3.ts'),'utf8'));write('identity/tool.ts','// independently captured test tool bytes');
 const identity={engine:[{key:'core',path:path.join(root,'identity/core.ts')}],tools:[{key:'tool',path:path.join(root,'identity/tool.ts')}]};
 const snapshot=()=>loadBusinessAuthoringProject(file,identity);
 return {root,file,write,profile,project,identity,input:authored.input,snapshot,saveProfile:()=>write('profile/profile.json',profile),saveProject:()=>write('project.json',project),select:()=>selectBusinessAuthoringRecipe(snapshot(),[authored.input])};
}
const rejected=(run:()=>unknown,code?:string)=>assert.throws(run,(error:unknown)=>error instanceof ProfileRejected&&(code===undefined||error.code===code));
function independentSubject(input:BusinessRecipeModelInput):BusinessReviewSubject {
 const spec=input.spec,feature=spec.identity.namespace.replaceAll('_','-'),sort=<T extends {id:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 const normalized=(value:string)=>value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
 const definitions=input.formal.definitions.map(definition=>{
  const authored=spec.definitions.find(row=>row.id===definition.definition_ref)!,requirement=spec.requirements.find(row=>row.id===authored.requirement_ref)!;
  return {definition_id:'DEF-'+feature.toUpperCase()+'-'+normalized(authored.id).toUpperCase(),term:authored.id,definition_kind:'predicate' as const,formal:definition.formal,plain_language:authored.meaning,domain_context:requirement.context,depends_on:[],business_fact_refs:['#/inputs'],interpretation_refs:['#/rule'],source_concept_refs:['business:'+feature+':definition:'+normalized(authored.id)],forbidden_collapses:requirement.boundaries};
 });
 const meaning={schema_version:'domainspec-v2.business-meaning/v1-candidate',meaning_id:'Meaning:'+feature+':eligibility-claim',version:'1',owner:'receipt-team',domain_context:'A submission is received.',rule:'Return an eligible submission.',applies_when:spec.requirements[0]!.applies_when,actors:spec.requirements[0]!.actors,
  inputs:['Rule CheckEligibility input item: Submission {eligible: Bool, id: UInt64, label: String}.','Operation Submit input request: Submission {eligible: Bool, id: UInt64, label: String}.'],
  outcomes:['Operation Submit returns request: Submission; on-rejection return-submission-error; effects none.'],examples:spec.requirements[0]!.examples,counterexamples:spec.requirements[0]!.counterexamples,boundaries:spec.requirements[0]!.boundaries,claim_ceiling:'One supplied submission, without external verification.',authority_effect:'none'};
 return {schema_version:'craft.business-review/v1-candidate',normalization_contract:'craft.business-authoring-contracts/1-candidate',model_identity:spec.identity,declarations:sort(spec.entities).map(entity=>({...entity,fields:[...entity.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0)})),definitions,claims:sort(spec.claims),interpretations:sort(spec.rules).map(rule=>({rule_ref:rule.id,...input.formal.rule_meanings[rule.id]!})),behaviors:sort(spec.operations),exposures:sort(spec.capabilities),requirements:sort(spec.requirements),legacy_meaning_subjects:[{meaning_id:meaning.meaning_id,version:'1',canonicalization:'domainspec-json-keysort-excluding-acceptance-v1',digest_algorithm:'sha256',digest:digest({...meaning,status:'accepted'})}]};
}
function refresh(f:ReturnType<typeof fixture>,text:string):void {
 const input:any=f.input;input.source={...input.source,sha256:hash(text),bytes:Buffer.byteLength(text)};
 input.spec.source_spans=text.split('\n').flatMap((raw,index)=>raw.trim()&&!raw.trimStart().startsWith('#')?[{selector:'original-fact/line:'+(index+1),source:'business.alch',line:index+1,column:raw.length-raw.trimStart().length+1,text:raw,source_sha256:input.source.sha256}]:[]);
 input.spec.obligations=input.spec.source_spans.map((span:any)=>({selector:span.selector,kind:'clause',span_selector:span.selector}));recalculate(input);f.write('business.alch',text);
}
const prepare=(f:ReturnType<typeof fixture>)=>{const selection=f.select();return prepareBusinessAuthoringReview(selection,'fixture',independentSubject(f.input));};

test('closed registered review hashes exact business-only subject and complete selected definition bodies',t=>{
 const f=fixture(t),selection=f.select(),subject=independentSubject(f.input),review=prepareBusinessAuthoringReview(selection,'fixture',subject);
 assertBusinessAuthoringReviewCurrent(review);assert.equal(review.selection,selection);assert.deepEqual(clone(review.review),subject);
 assert.deepEqual(clone(review.subject),{model_id:'fixture',version:'1',canonicalization:'craft.business-review-keysort/v1',digest_algorithm:'sha256',digest:digest(subject)});
 assert.deepEqual(clone(review.definition_closure),{definition_ids:['DEF-FIXTURE-ELIGIBILITY-DEFINITION'],digest_algorithm:'sha256',digest:digest(subject.definitions)});
 assert.deepEqual(clone(review.legacy_meaning_subjects),subject.legacy_meaning_subjects);assert.deepEqual(clone(review.technical),clone(selection.technical));
 const {review_sha256,...body}=review;assert.equal(review_sha256,digest(body));assert.notEqual(review.subject.digest,review_sha256);
 const visit=(value:unknown)=>{if(value&&typeof value==='object')for(const [key,child] of Object.entries(value)){assert.ok(!['status','acceptance','owner_acceptance','decision','wire','technical','ledger','source_spans'].includes(key),key);visit(child);}};visit(review.review);
 assert.ok(Object.isFrozen(review)&&Object.isFrozen(review.review.definitions)&&Object.isFrozen(review.subject)&&Object.isFrozen(review.definition_closure.definition_ids));
});
test('unknown, missing, duplicate and changed review fields never acquire exact model correspondence',t=>{
 const f=fixture(t),selection=f.select(),valid=independentSubject(f.input);
 for(const mutate of [
  (value:any)=>value.extra=true,(value:any)=>delete value.requirements,(value:any)=>value.declarations.push(value.declarations[0]),
  (value:any)=>value.definitions[0].formal.expression='item.id = item.id',(value:any)=>value.interpretations[0].predicates.Eligible='id',
  (value:any)=>value.behaviors[0].guards[0].arguments[0].value.root='another',(value:any)=>value.behaviors[0].result.path=['label'],
  (value:any)=>value.exposures[0].public_name='other',(value:any)=>value.claims[0].proposition='not Eligible(submitted)',
  (value:any)=>value.requirements[0].examples[0].then='An invented result.',(value:any)=>value.model_identity.owner='other-owner',
 ]){const changed:any=clone(valid);mutate(changed);rejected(()=>prepareBusinessAuthoringReview(selection,'fixture',changed));}
 rejected(()=>prepareBusinessAuthoringReview(selection,'absent',valid),'BUSINESS_REVIEW_CORRESPONDENCE');
});
test('prospective legacy subjects are unique, complete, exact and preserve the accepted-status v1 representation',t=>{
 const f=fixture(t),selection=f.select(),subject=independentSubject(f.input);
 for(const change of [(x:any)=>x.legacy_meaning_subjects=[],(x:any)=>x.legacy_meaning_subjects.push(x.legacy_meaning_subjects[0]),(x:any)=>x.legacy_meaning_subjects[0].digest='f'.repeat(64),(x:any)=>x.legacy_meaning_subjects[0].version='2']){const changed:any=clone(subject);change(changed);rejected(()=>prepareBusinessAuthoringReview(selection,'fixture',changed));}
 const review=prepareBusinessAuthoringReview(selection,'fixture',subject);assert.equal(review.legacy_meaning_subjects[0]!.digest,subject.legacy_meaning_subjects[0]!.digest);
 assert.ok(!Object.hasOwn(review,'business_meaning'));assert.ok(!Object.hasOwn(review,'owner_acceptance'));
});
test('technical local/shared/prefix changes preserve review and closure digests',t=>{
 const reviews=['node-http-entry-local-v2','node-http-shared-ports-v2','node-http-api-prefix-v2'].map(variant=>prepare(fixture(t,variant)));
 for(const review of reviews){assert.equal(review.subject.digest,reviews[0]!.subject.digest);assert.deepEqual(clone(review.review),clone(reviews[0]!.review));assert.deepEqual(clone(review.definition_closure),clone(reviews[0]!.definition_closure));}
 assert.notEqual(reviews[0]!.technical.transport,reviews[1]!.technical.transport);assert.notEqual(reviews[0]!.technical.wire.route_prefix,reviews[2]!.technical.wire.route_prefix);assert.notEqual(reviews[0]!.review_sha256,reviews[2]!.review_sha256);
});
test('unused definitions stay inspectable but are outside the selected complete-body closure',t=>{
 const f=fixture(t),base=prepare(f),input:any=f.input;
 const declaration=clone(input.spec.definitions[0]);declaration.id='UnusedDefinition';declaration.meaning='An explicitly declared unused definition.';input.spec.definitions.push(declaration);
 const normalized=clone(input.formal.definitions[0]);normalized.definition_ref='UnusedDefinition';normalized.predicate_uses=[];normalized.formal.definition='UnusedDefinition(item: Submission) := (item.eligible = true)';normalized.formal.expression=normalized.formal.definition;input.formal.definitions.push(normalized);
 const text=readFileSync(path.join(f.root,'business.alch'),'utf8')+'\ndefinition UnusedDefinition:\n  requirement SubmissionAllowed\n  input item Submission\n  meaning "An explicitly declared unused definition."\n  boolean-field item.eligible\n';refresh(f,text);
 const review=prepare(f);assert.equal(review.review.definitions.length,2);assert.notEqual(review.subject.digest,base.subject.digest);assert.deepEqual(clone(review.definition_closure),clone(base.definition_closure));
 assert.match(renderBusinessAuthoringReview(review),/UnusedDefinition/);
});
test('unresolved, cyclic and duplicate definition dependency injections reject without inference',t=>{
 const f=fixture(t),selection=f.select(),original=independentSubject(f.input);
 for(const depends_on of [['Missing'],['DEF-FIXTURE-ELIGIBILITY-DEFINITION'],['Missing','Missing']]){const changed:any=clone(original);changed.definitions[0].depends_on=depends_on;rejected(()=>prepareBusinessAuthoringReview(selection,'fixture',changed));}
 const changed:any=clone(original);changed.definitions[0].term='SimilarEligibilityDefinition';rejected(()=>prepareBusinessAuthoringReview(selection,'fixture',changed));
});
test('exact source meaning changes alter aggregate while retaining unchanged legacy v1 subject',t=>{
 const f=fixture(t),base=prepare(f),input:any=f.input;
 input.spec.entities[0].fields[1].meaning='Changed exact field meaning.';input.formal.definitions[0].field.meaning='Changed exact field meaning.';input.formal.definitions[0].formal.notation[1].meaning='Changed exact field meaning.';
 const text=readFileSync(path.join(f.root,'business.alch'),'utf8').replace('Caller supplied eligibility.','Changed exact field meaning.');refresh(f,text);
 const changed=prepare(f);assert.notEqual(base.subject.digest,changed.subject.digest);assert.notEqual(base.definition_closure.digest,changed.definition_closure.digest);assert.deepEqual(clone(base.legacy_meaning_subjects),clone(changed.legacy_meaning_subjects));
});
test('legacy duplicate string constraints are independently enforced rather than silently normalized',t=>{
 const f=fixture(t),input:any=f.input;input.spec.requirements[0].actors.push('Submission caller');
 const text=readFileSync(path.join(f.root,'business.alch'),'utf8').replace('  actor "Submission caller"','  actor "Submission caller"\n  actor "Submission caller"');refresh(f,text);
 const selection=f.select();rejected(()=>prepareBusinessAuthoringReview(selection,'fixture',independentSubject(f.input)),'BUSINESS_REVIEW_LEGACY');
});
test('readable review contains every authored scope and visibly separates proposed technical conventions',t=>{
 const f=fixture(t),review=prepare(f),before=readdirSync(f.root).sort(),rendered=renderBusinessAuthoringReview(review);
 for(const required of ['A submission is received.','Return an eligible submission.','Eligible submission.','Ineligible submission.','The flag does not authenticate the caller.','Submission identity.','Check the eligibility field.','Eligible(submitted)','item.eligible = true','submitted','return-submission-error','Effects: none','audience public',review.subject.digest,review.definition_closure.digest,review.legacy_meaning_subjects[0]!.digest])assert.ok(rendered.includes(required),required);
 assert.ok(rendered.indexOf('Proposed technical conventions')>rendered.indexOf('Prospective exact legacy subjects'));assert.match(rendered,/informational, not authentication/);assert.match(rendered,/no generated layout is inspected/);assert.deepEqual(readdirSync(f.root).sort(),before);assert.equal(renderBusinessAuthoringReview(review),rendered);
});
test('cloned/foreign handles, mutation and selected source/profile drift cannot remain current',t=>{
 const f=fixture(t),review=prepare(f);
 for(const forged of [clone(review),{...review},Object.create(review),new Proxy(review,{})]){rejected(()=>assertBusinessAuthoringReviewCurrent(forged as PreparedBusinessAuthoringReview),'BUSINESS_REVIEW_HANDLE');rejected(()=>renderBusinessAuthoringReview(forged as PreparedBusinessAuthoringReview),'BUSINESS_REVIEW_HANDLE');}
 rejected(()=>prepareBusinessAuthoringReview(clone(review.selection),'fixture',review.review),'BUSINESS_RECIPE_UNREGISTERED');
 assert.throws(()=>{(review.definition_closure.definition_ids as unknown as string[]).push('FORGED');},TypeError);
 f.write('business.alch',readFileSync(path.join(f.root,'business.alch'),'utf8')+'\n# source changed\n');rejected(()=>assertBusinessAuthoringReviewCurrent(review),'BUSINESS_PROFILE_SNAPSHOT_STALE');rejected(()=>renderBusinessAuthoringReview(review),'BUSINESS_PROFILE_SNAPSHOT_STALE');
 const other=fixture(t),otherReview=prepare(other);other.write('profile/profile.json',readFileSync(path.join(other.root,'profile/profile.json'),'utf8')+'\n');rejected(()=>assertBusinessAuthoringReviewCurrent(otherReview),'BUSINESS_PROFILE_SNAPSHOT_STALE');
});
test('own executing implementation bytes cannot change or bless later reviews in the same module instance',t=>{
 const f=fixture(t),copy=path.join(f.root,'copied');mkdirSync(path.join(copy,'src'),{recursive:true});cpSync(path.join(cli,'src/profile-engine'),path.join(copy,'src/profile-engine'),{recursive:true});cpSync(path.join(cli,'contracts'),path.join(copy,'contracts'),{recursive:true});writeFileSync(path.join(copy,'package.json'),'{"type":"module"}');
 const inputPath=f.write('input.json',f.input),subjectPath=f.write('review.json',independentSubject(f.input));
 const script=f.write('check.mjs',`import {readFileSync,writeFileSync} from 'node:fs';import assert from 'node:assert/strict';\nconst loader=await import(${JSON.stringify(pathToFileURL(path.join(copy,'src/profile-engine/loader-v3.ts')).href)});const recipes=await import(${JSON.stringify(pathToFileURL(path.join(copy,'src/profile-engine/business-authoring-recipes.ts')).href)});const owner=await import(${JSON.stringify(pathToFileURL(path.join(copy,'src/profile-engine/business-review.ts')).href)});const snapshot=loader.loadBusinessAuthoringProject(${JSON.stringify(f.file)},${JSON.stringify(f.identity)});const selected=recipes.selectBusinessAuthoringRecipe(snapshot,[JSON.parse(readFileSync(${JSON.stringify(inputPath)},'utf8'))]);const subject=JSON.parse(readFileSync(${JSON.stringify(subjectPath)},'utf8')),review=owner.prepareBusinessAuthoringReview(selected,'fixture',subject);const file=${JSON.stringify(path.join(copy,'src/profile-engine/business-review.ts'))};writeFileSync(file,readFileSync(file,'utf8')+'\\n// changed copied implementation\\n');recipes.assertBusinessRecipeSelectionCurrent(selected);assert.throws(()=>owner.assertBusinessAuthoringReviewCurrent(review),e=>e.code==='BUSINESS_REVIEW_MODULE_STALE');assert.throws(()=>owner.prepareBusinessAuthoringReview(selected,'fixture',subject),e=>e.code==='BUSINESS_REVIEW_MODULE_STALE');process.stdout.write('module-currentness-rejected\\n');`);
 const output=execFileSync(process.execPath,['--import',path.join(cli,'node_modules/tsx/dist/loader.mjs'),script],{encoding:'utf8',timeout:30000});assert.match(output,/module-currentness-rejected/);
});
