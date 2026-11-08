import test from 'node:test';
import assert from 'node:assert/strict';
import fs,{cpSync,mkdirSync,mkdtempSync,readFileSync,renameSync,rmSync,writeFileSync,lstatSync,readdirSync,symlinkSync,existsSync,chmodSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {loadBusinessAuthoringProject} from '../../src/profile-engine/loader-v3.js';
import {selectBusinessAuthoringRecipe,businessAuthoringRecipeSnapshot} from '../../src/profile-engine/business-authoring-recipes.js';
import {prepareBusinessAuthoringReview} from '../../src/profile-engine/business-review.js';
import {recordBusinessDecision,requireAcceptedBusinessDecision} from '../../src/profile-engine/business-decision.js';
import type {BusinessRecipeModelInput} from '../../src/profile-engine/business-authoring-normalization-protocol.js';
import {prepareBusinessAuthoringRequests} from '../../src/profile-engine/business-authoring-request.js';
import {prepareAuthoringBusinessInput,assertAuthoringBusinessInputCurrent} from '../../src/profile-engine/business-authoring-input.js';
import {assertBusinessInputV2Current} from '../../src/profile-engine/business-input-v2.js';
// Genuine Core owners, explicit temporary fixture decisions; no fake graph.
// Open questions: actual Alch checked preparation has its separate owner tests.
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
function independentReview(input:BusinessRecipeModelInput):any {
 const spec=input.spec,feature=spec.identity.namespace.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
 const key=(value:string)=>value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
 const byId=(values:readonly any[])=>[...values].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 const definitions=input.formal.definitions.map(value=>{
  const original=spec.definitions.find(row=>row.id===value.definition_ref)!,requirement=spec.requirements.find(row=>row.id===original.requirement_ref)!;
  return {definition_id:'DEF-'+feature.toUpperCase()+'-'+key(original.id).toUpperCase(),term:original.id,definition_kind:'predicate',formal:value.formal,plain_language:original.meaning,domain_context:requirement.context,depends_on:[],business_fact_refs:['#/inputs'],interpretation_refs:['#/rule'],source_concept_refs:['business:'+feature+':definition:'+key(original.id)],forbidden_collapses:requirement.boundaries};
 });
 const legacy=byId(spec.claims).map(claim=>{
  const requirement=spec.requirements.find(value=>value.id===claim.requirement_ref)!,rules=byId(spec.rules.filter(value=>value.claim_ref===claim.id)),operations=byId(spec.operations.filter(value=>value.guards.some(guard=>rules.some(rule=>rule.id===guard.rule_ref))));
  const inputText=(kind:string,value:any)=>{const entity=spec.entities.find(entity=>entity.id===value.input.type_ref)!;return `${kind} ${value.id} input ${value.input.name}: ${entity.id} {${[...entity.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(field=>field.name+': '+field.type).join(', ')}}.`;};
  const draft={schema_version:'domainspec-v2.business-meaning/v1-candidate',meaning_id:'Meaning:'+feature+':'+key(claim.id),version:claim.version,owner:spec.identity.owner,domain_context:requirement.context,rule:requirement.meaning,applies_when:requirement.applies_when,actors:requirement.actors,inputs:[...rules.map(value=>inputText('Rule',value)),...operations.map(value=>inputText('Operation',value))],outcomes:operations.map(value=>`Operation ${value.id} returns ${value.result.root}: ${value.output_ref}; on-rejection ${value.on_rejection}; effects none.`),examples:requirement.examples,counterexamples:requirement.counterexamples,boundaries:requirement.boundaries,claim_ceiling:claim.ceiling,authority_effect:'none'};
  return {meaning_id:draft.meaning_id,version:claim.version,canonicalization:'domainspec-json-keysort-excluding-acceptance-v1',digest_algorithm:'sha256',digest:digest({...draft,status:'accepted'})};
 });
 return {schema_version:'craft.business-review/v1-candidate',normalization_contract:'craft.business-authoring-contracts/1-candidate',model_identity:spec.identity,declarations:byId(spec.entities).map(value=>({...value,fields:[...value.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0)})),definitions,claims:byId(spec.claims),interpretations:byId(spec.rules).map(rule=>({rule_ref:rule.id,...input.formal.rule_meanings[rule.id]})),behaviors:byId(spec.operations),exposures:byId(spec.capabilities),requirements:byId(spec.requirements),legacy_meaning_subjects:legacy};
}
function ready(t:{after(fn:()=>void):void}) {const f=fixture(t),selection=f.select(),subject=independentReview(f.input),review=prepareBusinessAuthoringReview(selection,'fixture',subject);return {...f,selection,subject,review,request:(outcome:'accepted'|'declined')=>({decision_id:'owned-fixture-decision',owner:'receipt-team',outcome,reviewed_digest:review.subject.digest})};}
const rejected=(run:()=>unknown,code?:string)=>assert.throws(run,(error:any)=>typeof error?.code==='string'&&(code===undefined||error.code===code));
function acceptedReady(t:{after(fn:()=>void):void}) {
 const f=ready(t),capture=recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'explicit-fixture-decision.json')),accepted=requireAcceptedBusinessDecision(f.review,capture),requests=prepareBusinessAuthoringRequests(f.selection);
 // Independently authored source golden, not a production renderer.
 const source=`domain fixture "Submission receipt"
owner receipt-team
formal-claim EligibilityClaim:
  profile fol-core/1-candidate
  sort SubmissionValue
  predicate Eligible(SubmissionValue)
  constant submitted: SubmissionValue
  proposition Eligible(submitted)
  ceiling "One supplied submission, without external verification."
rule CheckEligibility:
  claim EligibilityClaim
entity Submission:
  identity id
  eligible Bool
  id UInt64
  label String
operation Submit:
  input Submission
  output Submission
  requires CheckEligibility

mapping CraftRequest_fixture_submission_endpoint:
  input body Submission
  target Submission
  total true
  field eligible <- body.eligible
  field id <- body.id
  field label <- body.label
`;
 const definition=f.review.review.definitions[0]!,subject=f.review.legacy_meaning_subjects[0]!,req=f.input.spec.requirements[0]!;
 const business_meaning={schema_version:'domainspec-v2.business-meaning/v1-candidate',meaning_id:'Meaning:fixture:eligibility-claim',version:'1',owner:'receipt-team',domain_context:req.context,rule:req.meaning,applies_when:req.applies_when,actors:req.actors,inputs:['Rule CheckEligibility input item: Submission {eligible: Bool, id: UInt64, label: String}.','Operation Submit input request: Submission {eligible: Bool, id: UInt64, label: String}.'],outcomes:['Operation Submit returns request: Submission; on-rejection return-submission-error; effects none.'],examples:req.examples,counterexamples:req.counterexamples,boundaries:req.boundaries,claim_ceiling:'One supplied submission, without external verification.',authority_effect:'none',status:'accepted'};
 const mapping=requests.models[0]!.mappings[0]!;
 const semantics:any={schema_version:'craft.business-application/v1-candidate',owner:'receipt-team',declarations:{Submission:{ontology:'BUSINESS-FIXTURE-SUBMISSION',meaning:'A received submission.',properties:{eligible:{ontology:'BUSINESS-FIXTURE-SUBMISSION#eligible',meaning:'Caller supplied eligibility.'},id:{ontology:'BUSINESS-FIXTURE-SUBMISSION#id',meaning:'Submission identity.'},label:{ontology:'BUSINESS-FIXTURE-SUBMISSION#label',meaning:'Unchanged label.'}}},CheckEligibility:{ontology:'BUSINESS-FIXTURE-CHECK-ELIGIBILITY',meaning:'Require the complete eligibility condition.'},Submit:{ontology:'BUSINESS-FIXTURE-SUBMIT',meaning:'Return the supplied eligible submission.',failure_continuation:'return-submission-error'},[mapping.mapping_id]:clone(mapping.declaration_binding)},claim_meanings:{EligibilityClaim:{claim_id:'FormalClaim:fixture:eligibility-claim',version:'1',supersedes:null,business_meaning,owner_acceptance:{schema_version:'domainspec-v2.business-acceptance-decision/v1-candidate',decision_id:'owned-fixture-decision',owner:'receipt-team',outcome:'accepted',subject,authority_effect:'none'},definitions:[{...definition,status:'accepted'}],definition_refs:[definition.definition_id]}},rule_meanings:{CheckEligibility:{sorts:{SubmissionValue:'Submission'},constants:{submitted:'item'},predicates:{Eligible:'eligible'}}},operation_behaviors:{Submit:{input_name:'request',guards:[{rule:'CheckEligibility',arguments:{item:{root:'request',path:[]}}}],result:{root:'request',path:[]}}},required_guarantees:[...f.selection.technical.required_guarantees],value_invariant_bindings:{}};
 const compatibility={model_id:'fixture',source,semantics};return {...f,capture,accepted,requests,compatibility,prepare:()=>prepareAuthoringBusinessInput(accepted,requests,compatibility)};
}
test('actual accepted owners produce explicit v3 input and exact generated artifacts',t=>{
 const f=acceptedReady(t),before=new Map(['project.json','business.alch','profile/profile.json','explicit-fixture-decision.json'].map(file=>[file,readFileSync(path.join(f.root,file))])),input=f.prepare();
 assertAuthoringBusinessInputCurrent(input);assertBusinessInputV2Current(input);assert.equal(input.kind,'business-authoring-input');assert.equal(input.accepted,f.accepted);assert.equal(input.requests,f.requests);assert.equal(input.authoring_snapshot,businessAuthoringRecipeSnapshot(f.selection));assert.equal(input.snapshot.kind,'business-authoring-input-context');assert.equal(input.snapshot.authoring_snapshot,input.authoring_snapshot);assert.equal(input.runtime,input.authoring_snapshot.packages.find(p=>p.data.schema_version==='craft.profile-package/v3-candidate'));assert.equal(input.runtime.data.schema_version,'craft.profile-package/v3-candidate');
 assert.equal(input.applications.length,1);assert.equal(input.applications[0]!.source,f.compatibility.source);assert.equal(canonical(input.applications[0]!.semantics),canonical(f.compatibility.semantics));assert.equal(input.applications[0]!.source_sha256,hash(f.compatibility.source));assert.equal(input.applications[0]!.semantics_sha256,hash(JSON.stringify(f.compatibility.semantics,null,2)+'\n'));assert.equal(input.applications[0]!.model.source,'derived/fixture/domain.alch');assert.equal(input.applications[0]!.model.semantics,'derived/fixture/semantics.json');assert.equal(input.provenance.kind,'generated-business-compatibility');assert.equal(canonical(input.provenance.original_source),canonical(f.input.source));assert.equal(canonical(input.provenance.decision_file),canonical(f.capture.file));assert.equal(input.provenance.source.bytes,Buffer.byteLength(f.compatibility.source));assert.equal(input.source_sha256,input.authoring_snapshot.lock.source_sha256);assert.equal(input.metadata_tables.applications.rows.length,1);assert.equal(input.metadata_tables.application_declarations.rows.length,5);assert.equal(input.snapshot.project.application_intents[0]!.id,'submit');
 assert.equal(canonical(input.formal_profile),canonical(JSON.parse(input.runtime.assets[input.runtime.data.application_runtime.formal_profile_asset]!.text!)));assert.equal(canonical(input.identity_algorithm),canonical(JSON.parse(input.runtime.assets[input.runtime.data.application_runtime.identity_algorithm_asset]!.text!)));for(const [relative,bytes] of before)assert.deepEqual(readFileSync(path.join(f.root,relative)),bytes);
});
test('captured compatibility is independent and deeply immutable',t=>{const f=acceptedReady(t),input=f.prepare();f.compatibility.semantics.declarations.Submit.meaning='caller mutation';f.compatibility.source='caller mutation';assertAuthoringBusinessInputCurrent(input);assert.equal(input.applications[0]!.semantics.declarations.Submit.meaning,'Return the supplied eligible submission.');for(const value of [input,input.snapshot,input.snapshot.project,input.applications,input.applications[0],input.compatibility,input.compatibility.semantics,input.metadata_tables,input.provenance])assert.equal(Object.isFrozen(value),true);});
const mutations:Record<string,(value:any)=>void>={
 'explicit profile carrier':v=>v.source=v.source.replace('owner receipt-team','profile application-v1\nowner receipt-team'),
 'extra declaration':v=>v.source+='entity Extra:\n  id UInt64\n',
 'missing Mapping':v=>v.source=v.source.slice(0,v.source.indexOf('\nmapping '))+'\n',
 'Mapping transform':v=>v.source=v.source.replace('body.id','body.eligible'),
 'changed source type':v=>v.source=v.source.replace('  eligible Bool','  eligible String'),
 'source whitespace':v=>v.source+='\n',
 'unknown argument field':v=>v.source_sha256=hash(v.source),
 'foreign model':v=>v.model_id='other',
 'semantic owner':v=>v.semantics.owner='another-team',
 'declaration meaning':v=>v.semantics.declarations.Submission.meaning='weakened',
 'property omission':v=>delete v.semantics.declarations.Submission.properties.label,
 'property ontology':v=>v.semantics.declarations.Submission.properties.eligible.ontology+='-other',
 'failure continuation':v=>v.semantics.declarations.Submit.failure_continuation='continue',
 'extra semantic declaration':v=>v.semantics.declarations.Unknown={ontology:'UNKNOWN',meaning:'Unknown.'},
 'Mapping ontology':v=>v.semantics.declarations.CraftRequest_fixture_submission_endpoint.ontology+='-other',
 'claim identity':v=>v.semantics.claim_meanings.EligibilityClaim.claim_id+='-other',
 'claim supersession':v=>v.semantics.claim_meanings.EligibilityClaim.supersedes='unknown',
 'self-rehashed meaning':v=>{const c=v.semantics.claim_meanings.EligibilityClaim;c.business_meaning.rule='weakened';c.owner_acceptance.subject.digest=digest(c.business_meaning);},
 'foreign decision':v=>v.semantics.claim_meanings.EligibilityClaim.owner_acceptance.decision_id='foreign',
 'declined derivative':v=>v.semantics.claim_meanings.EligibilityClaim.owner_acceptance.outcome='declined',
 'missing definition':v=>v.semantics.claim_meanings.EligibilityClaim.definitions=[],
 'changed definition body':v=>v.semantics.claim_meanings.EligibilityClaim.definitions[0].plain_language='changed',
 'extra accepted definition':v=>{const c=v.semantics.claim_meanings.EligibilityClaim;c.definitions.push({...c.definitions[0],definition_id:'DEF-EXTRA'});},
 'unaccepted definition':v=>delete v.semantics.claim_meanings.EligibilityClaim.definitions[0].status,
 'definition refs dropped':v=>v.semantics.claim_meanings.EligibilityClaim.definition_refs=[],
 'Rule interpretation':v=>v.semantics.rule_meanings.CheckEligibility.predicates.Eligible='label',
 'Operation guard':v=>v.semantics.operation_behaviors.Submit.guards=[],
 'Operation parameter':v=>v.semantics.operation_behaviors.Submit.input_name='body',
 'invented guarantee':v=>v.semantics.required_guarantees.push('invented'),
 'invented invariant':v=>v.semantics.value_invariant_bindings.Submission=[],
};
for(const [label,change] of Object.entries(mutations))test('independently rejects '+label,t=>{const f=acceptedReady(t),data=clone(f.compatibility);change(data);rejected(()=>prepareAuthoringBusinessInput(f.accepted,f.requests,data));});
test('inert compatibility rejects getters before executing them',t=>{const f=acceptedReady(t);let calls=0;const data={...f.compatibility};Object.defineProperty(data,'source',{enumerable:true,get(){calls++;return f.compatibility.source;}});rejected(()=>prepareAuthoringBusinessInput(f.accepted,f.requests,data));assert.equal(calls,0);});
test('copied accepted/request/selection/input handles are unregistered',t=>{const f=acceptedReady(t),input=f.prepare();rejected(()=>prepareAuthoringBusinessInput({...f.accepted},f.requests,f.compatibility));rejected(()=>prepareAuthoringBusinessInput(f.accepted,{...f.requests},f.compatibility));rejected(()=>businessAuthoringRecipeSnapshot({...f.selection}));for(const value of [{...input},clone(input),{}]){rejected(()=>assertAuthoringBusinessInputCurrent(value as any),'BUSINESS_AUTHORING_INPUT_UNREGISTERED');rejected(()=>assertBusinessInputV2Current(value as any),'PROFILE_BUSINESS_INPUT_UNREGISTERED');}});
test('same data through another original selection cannot substitute',t=>{const f=acceptedReady(t),another=prepareBusinessAuthoringRequests(f.select());rejected(()=>prepareAuthoringBusinessInput(f.accepted,another,f.compatibility),'BUSINESS_AUTHORING_INPUT_SELECTION');});
for(const [label,relative] of [['original source','business.alch'],['decision record','explicit-fixture-decision.json'],['profile manifest','profile/profile.json'],['tool','identity/tool.ts']] as const)test('currentness rejects changed '+label,t=>{const f=acceptedReady(t),input=f.prepare();writeFileSync(path.join(f.root,relative),readFileSync(path.join(f.root,relative),'utf8')+'\n');rejected(()=>assertAuthoringBusinessInputCurrent(input));rejected(()=>assertBusinessInputV2Current(input));rejected(f.prepare);});
for(const [label,relative] of [['source','business.alch'],['decision','explicit-fixture-decision.json'],['profile','profile/profile.json']] as const)test('currentness rejects same-byte '+label+' replacement',t=>{const f=acceptedReady(t),input=f.prepare(),file=path.join(f.root,relative),bytes=readFileSync(file);renameSync(file,file+'.old');writeFileSync(file,bytes,{mode:0o600});rejected(()=>assertAuthoringBusinessInputCurrent(input));rejected(()=>assertBusinessInputV2Current(input));});
test('original old-v2 registry and its source currentness still operate through the dispatcher',async t=>{
 const {createBusinessApplicationFixture}=await import('../helpers/business-profile.js'),{loadProfileProjectV2}=await import('../../src/profile-engine/loader.js'),{prepareBusinessInputV2}=await import('../../src/profile-engine/business-input-v2.js');
 const f=createBusinessApplicationFixture(t,'node-http-entry-local-v2'),input=prepareBusinessInputV2(loadProfileProjectV2(f.file,{engine:[{key:'loader',path:path.join(cli,'src/profile-engine/loader.ts')}],tools:[{key:'tool',path:path.join(cli,'src/profile-engine/contracts.ts')}]}));
 assertBusinessInputV2Current(input);assert.equal(input.runtime.data.schema_version,'craft.profile-package/v2-candidate');assert.equal('kind' in input,false);rejected(()=>assertBusinessInputV2Current({...input}),'PROFILE_BUSINESS_INPUT_UNREGISTERED');writeFileSync(path.join(f.root,'domain.alch'),readFileSync(path.join(f.root,'domain.alch'),'utf8')+'\n');rejected(()=>assertBusinessInputV2Current(input),'PROFILE_SNAPSHOT_STALE');
});
for(const replacement of ['same-byte-inode','changed-bytes'] as const)test('actual adapter module '+replacement+' invalidates owned input without altering the live implementation',async t=>{
 const f=acceptedReady(t),copy=path.join(f.root,'isolated-core');mkdirSync(copy);cpSync(path.join(cli,'src'),path.join(copy,'src'),{recursive:true});cpSync(path.join(cli,'contracts'),path.join(copy,'contracts'),{recursive:true});
 const load=(name:string)=>import(pathToFileURL(path.join(copy,'src/profile-engine/'+name+'.ts')).href);
 const [loader,recipes,reviews,decisions,requests,inputs,oldInputs]=await Promise.all(['loader-v3','business-authoring-recipes','business-review','business-decision','business-authoring-request','business-authoring-input','business-input-v2'].map(load));
 const selection=recipes.selectBusinessAuthoringRecipe(loader.loadBusinessAuthoringProject(f.file,f.identity),[f.input]),review=reviews.prepareBusinessAuthoringReview(selection,'fixture',f.subject),capture=decisions.recordBusinessDecision(review,f.request('accepted'),path.join(f.root,'isolated-decision.json')),accepted=decisions.requireAcceptedBusinessDecision(review,capture),request=requests.prepareBusinessAuthoringRequests(selection),input=inputs.prepareAuthoringBusinessInput(accepted,request,f.compatibility);
 oldInputs.assertBusinessInputV2Current(input);const filename=path.join(copy,'src/profile-engine/business-authoring-input.ts'),bytes=readFileSync(filename);if(replacement==='same-byte-inode'){renameSync(filename,filename+'.old');writeFileSync(filename,bytes);}else writeFileSync(filename,Buffer.concat([bytes,Buffer.from('\n// changed adapter bytes\n')]));
 rejected(()=>inputs.assertAuthoringBusinessInputCurrent(input),'BUSINESS_AUTHORING_INPUT_MODULE_STALE');rejected(()=>oldInputs.assertBusinessInputV2Current(input),'BUSINESS_AUTHORING_INPUT_MODULE_STALE');rejected(()=>inputs.prepareAuthoringBusinessInput(accepted,request,f.compatibility),'BUSINESS_AUTHORING_INPUT_MODULE_STALE');
});
