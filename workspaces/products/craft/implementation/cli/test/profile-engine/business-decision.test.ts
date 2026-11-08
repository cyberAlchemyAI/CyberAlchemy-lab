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
import {selectBusinessAuthoringRecipe} from '../../src/profile-engine/business-authoring-recipes.js';
import {prepareBusinessAuthoringReview} from '../../src/profile-engine/business-review.js';
import {recordBusinessDecision,captureBusinessDecision,assertBusinessDecisionCurrent,requireAcceptedBusinessDecision,assertAcceptedBusinessDecisionCurrent} from '../../src/profile-engine/business-decision.js';
import type {BusinessRecipeModelInput} from '../../src/profile-engine/business-authoring-normalization-protocol.js';
// Actual registered Core selections/reviews and explicit owned temporary decisions only.
// No accepted carrier, fake graph, producer authentication, or real project acceptance.
// Open questions: B06.2 accepted materialization and stronger owner authentication remain separate.
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
function patched(run:()=>void,change:(original:typeof fs)=>void):void {
 const original={...fs};try{change(original as typeof fs);syncBuiltinESMExports();run();}finally{for(const key of ['openSync','closeSync','writeSync','unlinkSync','lstatSync'] as const)(fs as any)[key]=original[key];syncBuiltinESMExports();}
}

test('explicit fixture recording binds exact real review scope, only a new0600 file and immutable current capture',t=>{
 const f=ready(t),before=new Map(['project.json','business.alch','profile/profile.json'].map(relative=>[relative,readFileSync(path.join(f.root,relative))])),file=path.join(f.root,'fixture-decision.json');
 const value=recordBusinessDecision(f.review,f.request('accepted'),file);assertBusinessDecisionCurrent(value);
 assert.equal(value.kind,'captured-business-decision');assert.equal(value.review,f.review);assert.equal(value.authority_effect,'none');assert.equal(lstatSync(file).mode&0o777,0o600);
 assert.deepEqual(clone(value.decision.subject),clone(f.review.subject));assert.deepEqual(clone(value.decision.legacy_meaning_subjects),clone(f.review.legacy_meaning_subjects));assert.deepEqual(clone(value.decision.definition_closure),clone(f.review.definition_closure));
 const bytes=readFileSync(file);assert.equal(value.file.sha256,hash(bytes));assert.equal(value.file.bytes,bytes.length);assert.equal(value.file.path,file);assert.deepEqual(JSON.parse(bytes.toString('utf8')),clone(value.decision));
 assert.ok(Object.isFrozen(value)&&Object.isFrozen(value.decision.subject)&&Object.isFrozen(value.decision.definition_closure.definition_ids));
 for(const [relative,original] of before)assert.deepEqual(readFileSync(path.join(f.root,relative)),original);
 assert.equal(Object.hasOwn(value,'accepted_carrier'),false);assert.equal(Object.hasOwn(value,'authenticated_owner'),false);
});
test('accepted guard exposes only exact accepted scope and retains original review and capture',t=>{
 const f=ready(t),capture=recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'accepted.json')),scope=requireAcceptedBusinessDecision(f.review,capture);assertAcceptedBusinessDecisionCurrent(scope);
 assert.equal(scope.kind,'accepted-business-decision');assert.equal(scope.review,f.review);assert.equal(scope.capture,capture);assert.deepEqual(scope.subject,f.review.subject);assert.deepEqual(scope.legacy_meaning_subjects,f.review.legacy_meaning_subjects);assert.deepEqual(scope.definition_closure,f.review.definition_closure);assert.equal(scope.authority_effect,'none');
 assert.equal(Object.hasOwn(scope,'definitions'),false);assert.equal(Object.hasOwn(scope,'status'),false);assert.equal(Object.hasOwn(scope,'graph'),false);
});
test('explicit decline is inspectable/current and cannot enter accepted guard',t=>{
 const f=ready(t),value=recordBusinessDecision(f.review,f.request('declined'),path.join(f.root,'declined.json'));assertBusinessDecisionCurrent(value);assert.equal(value.decision.outcome,'declined');rejected(()=>requireAcceptedBusinessDecision(f.review,value),'BUSINESS_DECISION_DECLINED');
});
test('occupied identical/conflicting records, symlinks, FIFO and directory reject without opening or altering destinations',t=>{
 const f=ready(t),file=path.join(f.root,'occupied.json');recordBusinessDecision(f.review,f.request('accepted'),file);const before=readFileSync(file),inode=lstatSync(file).ino;
 for(const outcome of ['accepted','declined'] as const)rejected(()=>recordBusinessDecision(f.review,f.request(outcome),file),'BUSINESS_DECISION_DESTINATION_OCCUPIED');assert.deepEqual(readFileSync(file),before);assert.equal(lstatSync(file).ino,inode);
 const sentinel=f.write('sentinel','PRIVATE SENTINEL'),link=path.join(f.root,'linked.json');symlinkSync(sentinel,link);rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),link),'BUSINESS_DECISION_DESTINATION_OCCUPIED');assert.equal(readFileSync(sentinel,'utf8'),'PRIVATE SENTINEL');assert.ok(lstatSync(link).isSymbolicLink());
 const fifo=path.join(f.root,'fifo.json');execFileSync('mkfifo',[fifo]);rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),fifo),'BUSINESS_DECISION_DESTINATION_OCCUPIED');assert.ok(lstatSync(fifo).isFIFO());
 const directory=path.join(f.root,'directory.json');mkdirSync(directory);rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),directory),'BUSINESS_DECISION_DESTINATION_OCCUPIED');assert.ok(lstatSync(directory).isDirectory());
});
test('record request has no default outcome, inferred owner/digest or open executable fields',t=>{
 const f=ready(t),request=f.request('accepted'),mutations=[(v:any)=>delete v.outcome,(v:any)=>delete v.owner,(v:any)=>delete v.reviewed_digest,(v:any)=>v.outcome='approve',(v:any)=>v.owner='foreign-owner',(v:any)=>v.reviewed_digest='a'.repeat(64),(v:any)=>v.decision_id=' ',(v:any)=>v.decision_id='x'.repeat(4097),(v:any)=>v.current=true,(v:any)=>v.schema_version='manual'];
 for(const [index,mutate] of mutations.entries()){const value:any=clone(request);mutate(value);const file=path.join(f.root,'invalid-'+index+'.json');rejected(()=>recordBusinessDecision(f.review,value,file));assert.equal(existsSync(file),false);}
 let called=0;const getter={...request,get owner(){called++;return 'receipt-team';}};rejected(()=>recordBusinessDecision(f.review,getter,path.join(f.root,'getter.json')));assert.equal(called,0);rejected(()=>recordBusinessDecision(f.review,new Proxy(request,{}),path.join(f.root,'proxy.json')));
});
test('absolute new path requires an existing nonsymlink parent and never creates parent trees',t=>{
 const f=ready(t),missing=path.join(f.root,'missing','new.json');rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),missing),'BUSINESS_DECISION_PATH');assert.equal(existsSync(path.dirname(missing)),false);
 for(const value of ['relative.json',path.join(f.root,'x')+'/../out.json',path.join(f.root,'nul\0.json')])rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),value),'BUSINESS_DECISION_PATH');
 mkdirSync(path.join(f.root,'actual-parent'));symlinkSync(path.join(f.root,'actual-parent'),path.join(f.root,'linked-parent'),'dir');rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'linked-parent','new.json')),'BUSINESS_DECISION_SYMLINK');assert.deepEqual(readdirSync(path.join(f.root,'actual-parent')),[]);
});
test('private mode0600 remains exact under a restrictive process umask',t=>{
 const f=ready(t),before=process.umask(0o777);try{const file=path.join(f.root,'private.json');recordBusinessDecision(f.review,f.request('declined'),file);assert.equal(lstatSync(file).mode&0o777,0o600);}finally{process.umask(before);}
});
test('capture reloads actual matching record and a fresh equivalent review requires explicit recapture',t=>{
 const f=ready(t),file=path.join(f.root,'record.json'),original=recordBusinessDecision(f.review,f.request('accepted'),file),reload=captureBusinessDecision(f.review,file);assertBusinessDecisionCurrent(reload);assert.equal(reload.review,f.review);assert.deepEqual(reload.decision,original.decision);
 const freshReview=prepareBusinessAuthoringReview(f.selection,'fixture',f.subject);rejected(()=>requireAcceptedBusinessDecision(freshReview,original),'BUSINESS_DECISION_FOREIGN_REVIEW');const fresh=captureBusinessDecision(freshReview,file);assertAcceptedBusinessDecisionCurrent(requireAcceptedBusinessDecision(freshReview,fresh));
 const another=recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'explicit-new-record.json'));assertBusinessDecisionCurrent(another);
});
for(const [name,mutate] of [
 ['model',(v:any)=>v.subject.model_id='other'],['version',(v:any)=>v.subject.version='2'],['aggregate digest',(v:any)=>v.subject.digest='0'.repeat(64)],['owner',(v:any)=>v.owner='another-owner'],['legacy missing',(v:any)=>v.legacy_meaning_subjects=[]],['legacy duplicate',(v:any)=>v.legacy_meaning_subjects.push(v.legacy_meaning_subjects[0])],['legacy digest',(v:any)=>v.legacy_meaning_subjects[0].digest='0'.repeat(64)],['legacy version',(v:any)=>v.legacy_meaning_subjects[0].version='2'],['closure missing',(v:any)=>v.definition_closure.definition_ids=[]],['closure partial/wrong',(v:any)=>v.definition_closure.definition_ids=['DEF-UNSELECTED']],['closure duplicate',(v:any)=>v.definition_closure.definition_ids.push(v.definition_closure.definition_ids[0])],['closure digest',(v:any)=>v.definition_closure.digest='0'.repeat(64)],['blank identity',(v:any)=>v.decision_id=' '],['unknown approval',(v:any)=>v.accepted=true],['wrong canonicalization',(v:any)=>v.subject.canonicalization='other'],
] as [string,(value:any)=>void][])test('capture rejects altered exact decision scope '+name,t=>{
 const f=ready(t),original=recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'original.json')),bad=clone(original.decision);mutate(bad);const file=f.write('altered.json',bad);rejected(()=>captureBusinessDecision(f.review,file));assertBusinessDecisionCurrent(original);
});
test('capture does not follow leaf symlinks, accept FIFO/directories or normalize malformed encoding/BOM/JSON',t=>{
 const f=ready(t),file=path.join(f.root,'record.json');recordBusinessDecision(f.review,f.request('declined'),file);const link=path.join(f.root,'link.json');symlinkSync(file,link);rejected(()=>captureBusinessDecision(f.review,link),'BUSINESS_DECISION_SYMLINK');
 const fifo=path.join(f.root,'capture-fifo.json');execFileSync('mkfifo',[fifo]);rejected(()=>captureBusinessDecision(f.review,fifo),'BUSINESS_DECISION_FILE_KIND');rejected(()=>captureBusinessDecision(f.review,f.root),'BUSINESS_DECISION_FILE_KIND');
 const invalid=path.join(f.root,'encoding.json');writeFileSync(invalid,Buffer.from([0xff,0xfe]));rejected(()=>captureBusinessDecision(f.review,invalid),'BUSINESS_DECISION_FILE_ENCODING');
 f.write('bom.json','\ufeff'+readFileSync(file,'utf8'));rejected(()=>captureBusinessDecision(f.review,path.join(f.root,'bom.json')),'BUSINESS_DECISION_FILE_JSON');f.write('invalid.json','{invalid');rejected(()=>captureBusinessDecision(f.review,path.join(f.root,'invalid.json')),'BUSINESS_DECISION_FILE_JSON');
});
test('captured and accepted guards reject JSON/spread/proxy handles and immutable scope mutation',t=>{
 const f=ready(t),capture=recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'record.json')),scope=requireAcceptedBusinessDecision(f.review,capture);
 for(const forged of [clone(capture),{...capture},Object.create(capture),new Proxy(capture,{})]){rejected(()=>assertBusinessDecisionCurrent(forged),'BUSINESS_DECISION_UNREGISTERED');rejected(()=>requireAcceptedBusinessDecision(f.review,forged),'BUSINESS_DECISION_UNREGISTERED');}
 for(const forged of [clone(scope),{...scope},Object.create(scope),new Proxy(scope,{})])rejected(()=>assertAcceptedBusinessDecisionCurrent(forged),'BUSINESS_DECISION_UNREGISTERED');rejected(()=>requireAcceptedBusinessDecision(f.review,undefined as any),'BUSINESS_DECISION_UNREGISTERED');
 assert.throws(()=>{(capture.decision.subject as any).digest='fake';},TypeError);assert.throws(()=>{(scope.definition_closure.definition_ids as any).push('extra');},TypeError);
});
for(const mutation of ['bytes','same-bytes-inode','parent-inode','mode','missing','symlink'])test('decision physical custody detects '+mutation,t=>{
 const f=ready(t),parent=path.join(f.root,'decisions');mkdirSync(parent);const file=path.join(parent,'record.json'),capture=recordBusinessDecision(f.review,f.request('accepted'),file),scope=requireAcceptedBusinessDecision(f.review,capture),bytes=readFileSync(file);
 if(mutation==='bytes')writeFileSync(file,Buffer.concat([bytes,Buffer.from('\n')]));
 if(mutation==='same-bytes-inode'){writeFileSync(file+'.replacement',bytes);renameSync(file+'.replacement',file);}
 if(mutation==='parent-inode'){renameSync(parent,parent+'.old');mkdirSync(parent);writeFileSync(file,bytes);}
 if(mutation==='mode')chmodSync(file,0o644);if(mutation==='missing')rmSync(file);if(mutation==='symlink'){renameSync(file,file+'.actual');symlinkSync(file+'.actual',file);}
 rejected(()=>assertBusinessDecisionCurrent(capture));rejected(()=>assertAcceptedBusinessDecisionCurrent(scope));
});
for(const relative of ['business.alch','project.json','profile/profile.json','identity/core.ts','identity/tool.ts'])test('decision guard traverses original review/source/selection custody '+relative,t=>{
 const f=ready(t),capture=recordBusinessDecision(f.review,f.request('accepted'),path.join(f.root,'record.json')),scope=requireAcceptedBusinessDecision(f.review,capture);f.write(relative,readFileSync(path.join(f.root,relative),'utf8')+'\n');rejected(()=>assertBusinessDecisionCurrent(capture));rejected(()=>assertAcceptedBusinessDecisionCurrent(scope));const destination=path.join(f.root,'must-not-exist.json');rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),destination));assert.equal(existsSync(destination),false);
});
test('partial-write failure conservatively leaves only bounded new residue and never deletes any path',t=>{
 const f=ready(t),file=path.join(f.root,'partial.json');let writes=0,deletes=0;
 patched(()=>rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),file)),original=>{
  fs.writeSync=((fd:number,buffer:Buffer,offset:number,length:number,position:null)=>{if(++writes===1)return original.writeSync(fd,buffer,offset,Math.min(length,17),position);throw Object.assign(new Error('injected write failure'),{code:'EIO'});}) as typeof fs.writeSync;
  fs.unlinkSync=(()=>{deletes++;throw Error('no pathname deletion is safe');}) as typeof fs.unlinkSync;
 });
 assert.equal(deletes,0);assert.equal(readFileSync(file).length,17);assert.equal(lstatSync(file).mode&0o777,0o600);rejected(()=>captureBusinessDecision(f.review,file),'BUSINESS_DECISION_FILE_JSON');rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),file),'BUSINESS_DECISION_DESTINATION_OCCUPIED');
});
test('replacement inserted during failure descriptor cleanup survives without an unlink race',t=>{
 const f=ready(t),file=path.join(f.root,'cleanup-boundary.json');let recordFd:number|undefined,replaced=false,deletes=0;
 patched(()=>rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),file)),original=>{
  fs.writeSync=((fd:number)=>{recordFd=fd;throw Object.assign(new Error('injected failure'),{code:'EIO'});}) as typeof fs.writeSync;
  fs.closeSync=((fd:number)=>{if(fd===recordFd&&!replaced){replaced=true;fs.writeSync=original.writeSync;syncBuiltinESMExports();rmSync(file);writeFileSync(file,'FOREIGN REPLACEMENT');}return original.closeSync(fd);}) as typeof fs.closeSync;
  fs.unlinkSync=(()=>{deletes++;throw Error('cleanup must not unlink by name');}) as typeof fs.unlinkSync;
 });
 assert.ok(replaced);assert.equal(deletes,0);assert.equal(readFileSync(file,'utf8'),'FOREIGN REPLACEMENT');
});
test('opened-parent anchoring never writes through a substituted parent and preserves both paths on failure',t=>{
 const f=ready(t),parent=path.join(f.root,'decisions');mkdirSync(parent);const file=path.join(parent,'record.json');let replaced=false;
 patched(()=>rejected(()=>recordBusinessDecision(f.review,f.request('accepted'),file)),original=>{
  fs.writeSync=((fd:number,buffer:Buffer,offset:number,length:number,position:null)=>{if(!replaced){replaced=true;fs.writeSync=original.writeSync;syncBuiltinESMExports();renameSync(parent,parent+'.old');mkdirSync(parent);writeFileSync(file,'FOREIGN PARENT SENTINEL');}return original.writeSync(fd,buffer,offset,length,position);}) as typeof fs.writeSync;
 });
 assert.equal(readFileSync(file,'utf8'),'FOREIGN PARENT SENTINEL');assert.ok(existsSync(path.join(parent+'.old','record.json')));assert.equal(JSON.parse(readFileSync(path.join(parent+'.old','record.json'),'utf8')).subject.digest,f.review.subject.digest);
});
test('actual decision implementation replacement invalidates captures/guards and cannot bless fresh recording',async t=>{
 const f=ready(t),copy=path.join(f.root,'isolated-owner');mkdirSync(copy);cpSync(path.join(cli,'src'),path.join(copy,'src'),{recursive:true});cpSync(path.join(cli,'contracts'),path.join(copy,'contracts'),{recursive:true});
 const loader=await import(pathToFileURL(path.join(copy,'src/profile-engine/loader-v3.ts')).href),recipes=await import(pathToFileURL(path.join(copy,'src/profile-engine/business-authoring-recipes.ts')).href),reviews=await import(pathToFileURL(path.join(copy,'src/profile-engine/business-review.ts')).href),decisions=await import(pathToFileURL(path.join(copy,'src/profile-engine/business-decision.ts')).href);
 const selection=recipes.selectBusinessAuthoringRecipe(loader.loadBusinessAuthoringProject(f.file,f.identity),[f.input]),review=reviews.prepareBusinessAuthoringReview(selection,'fixture',f.subject),capture=decisions.recordBusinessDecision(review,f.request('accepted'),path.join(f.root,'copied-owner-record.json')),scope=decisions.requireAcceptedBusinessDecision(review,capture);
 const filename=path.join(copy,'src/profile-engine/business-decision.ts'),replacement=filename+'.replacement';writeFileSync(replacement,readFileSync(filename));renameSync(replacement,filename);
 rejected(()=>decisions.assertBusinessDecisionCurrent(capture),'BUSINESS_DECISION_MODULE_STALE');rejected(()=>decisions.assertAcceptedBusinessDecisionCurrent(scope),'BUSINESS_DECISION_MODULE_STALE');const fresh=path.join(f.root,'fresh-module-must-not-exist.json');rejected(()=>decisions.recordBusinessDecision(review,f.request('accepted'),fresh),'BUSINESS_DECISION_MODULE_STALE');assert.equal(existsSync(fresh),false);
});
