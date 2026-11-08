import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,renameSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {loadBusinessAuthoringProject} from '../../src/profile-engine/loader-v3.js';
import {selectBusinessAuthoringRecipe} from '../../src/profile-engine/business-authoring-recipes.js';
import {prepareBusinessAuthoringRequests,assertBusinessAuthoringRequestsCurrent} from '../../src/profile-engine/business-authoring-request.js';
import {decodeRequestApplicationSourceV1} from '../../src/system-integration/request-application-source-v1.js';
import {validateBusinessAuthoringContract} from '../../src/profile-engine/business-authoring-contracts.js';
import type {BusinessRecipeModelInput} from '../../src/profile-engine/business-authoring-normalization-protocol.js';
// Independent source/DTO expectations; no Alch private import, accepted fixture, or fake graph.
// Open questions: B06.2 insertion before compilation and B07.2 real graph/API owners.
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
const rejected=(run:()=>unknown,code?:string)=>assert.throws(run,(error:any)=>typeof error?.code==='string'&&(code===undefined||error.code===code));
function refreshed(input:any,text:string):void {
 input.source={...input.source,sha256:hash(text),bytes:Buffer.byteLength(text)};
 input.spec.source_spans=text.split('\n').flatMap((raw,index)=>raw.trim()&&!raw.trimStart().startsWith('#')?[{selector:'original-fact/line:'+(index+1),source:input.source.path,line:index+1,column:raw.length-raw.trimStart().length+1,text:raw,source_sha256:input.source.sha256}]:[]);
 input.spec.obligations=input.spec.source_spans.map((span:any)=>({selector:span.selector,kind:'clause',span_selector:span.selector}));recalculate(input);
}
function renamed(input:BusinessRecipeModelInput,text:string,modelId:string,exposureId='SubmissionEndpoint',publicName='submit'):{input:BusinessRecipeModelInput;text:string} {
 const value:any=clone(input),oldModel=input.model_id,oldExposure=input.spec.capabilities[0]!.id,oldPublic=input.spec.capabilities[0]!.public_name;
 value.model_id=modelId;value.spec.identity.namespace=modelId;value.spec.identity.stable_id=modelId;value.formal.model_id=modelId;value.behavior.model_id=modelId;
 value.spec.capabilities[0].id=exposureId;value.behavior.exposures[0].id=exposureId;value.spec.capabilities[0].public_name=publicName;value.behavior.exposures[0].public_name=publicName;
 const source=text.replace('business-model '+oldModel+' version','business-model '+modelId+' version').replace('capability '+oldExposure+':','capability '+exposureId+':').replace('public-name '+oldPublic+'\n','public-name '+publicName+'\n');
 refreshed(value,source);return {input:value,text:source};
}
function pointer(value:any,at:string):unknown {return at.split('/').slice(1).reduce((current,key)=>current?.[key.replace(/~1/g,'/').replace(/~0/g,'~')],value);}

test('actual identity Mapping grammar covers every unchanged typed field and fixed technical metadata',t=>{
 const f=fixture(t),selection=f.select(),before=digest(selection),value=prepareBusinessAuthoringRequests(selection);assertBusinessAuthoringRequestsCurrent(value);
 assert.equal(value.kind,'business-authoring-request-preparation');assert.equal(value.selection,selection);assert.equal(digest(selection),before);assert.equal(value.authority_effect,'none');
 const model=value.models[0]!,mapping=model.mappings[0]!;
 assert.equal(mapping.mapping_id,'CraftRequest_fixture_submission_endpoint');assert.equal(mapping.mapping_selector,'fixture:craft-request-fixture-submission-endpoint');assert.equal(mapping.operation_selector,'fixture:submit');
 assert.equal(mapping.exposure_key,'fixture-submission-endpoint');assert.equal(mapping.input_entity,'Submission');
 assert.deepEqual(clone(mapping.fields),[{target:'eligible',path:['body','eligible'],type:'Bool'},{target:'id',path:['body','id'],type:'UInt64'},{target:'label',path:['body','label'],type:'String'}]);
 assert.equal(mapping.source_fragment,'mapping CraftRequest_fixture_submission_endpoint:\n  input body Submission\n  target Submission\n  total true\n  field eligible <- body.eligible\n  field id <- body.id\n  field label <- body.label\n');
 assert.equal(model.source_fragment,mapping.source_fragment);assert.equal(mapping.declaration_binding.ontology,'PROTOCOL-FIXTURE-SUBMISSION-ENDPOINT-REQUEST');
 assert.equal(mapping.declaration_binding.meaning,'Protocol identity Mapping from the whole request body to Submission without changing declared fields.');
 assert.deepEqual(model.declaration_bindings[mapping.mapping_id],mapping.declaration_binding);assert.equal(Object.hasOwn(mapping,'accepted'),false);
 assert.ok(Object.isFrozen(mapping.fields[0]!.path));assert.ok(Object.isFrozen(value.project_intents[0]!.mapping_arguments));
 const {derivation_sha256,...content}=value;assert.equal(derivation_sha256,digest(content));
});
test('exact public project intent and existing request decoder bind body root and whole typed parameter',t=>{
 const f=fixture(t),value=prepareBusinessAuthoringRequests(f.select()),model=value.models[0]!;
 const intent={id:'submit',application_id:'fixture',operation_ref:'Submit',mapping_ref:'CraftRequest_fixture_submission_endpoint',mapping_arguments:{body:{root:'body',path:[]}},access:{kind:'public'}};
 assert.deepEqual(clone(value.project_intents),[intent]);assert.deepEqual(clone(model.project_intents),[intent]);
 const entry={id:'submit',operation_ref:'fixture:submit',mapping_ref:'fixture:craft-request-fixture-submission-endpoint',mapping_arguments:[{parameter:'body',path:[]}],request_parameter:'request',route:{method:'POST',path:'/submit'},access:{kind:'public'}};
 assert.deepEqual(clone(model.request_source),{schema_version:'domainspec.request-application-source/v1-candidate',source_id:'fixture',entries:[entry]});
 assert.deepEqual(clone(value.request_source),{schema_version:'domainspec.request-application-source/v1-candidate',source_id:'business-authoring-requests',entries:[entry]});
 assert.deepEqual(clone(decodeRequestApplicationSourceV1(value.request_source)),clone(value.request_source));
});
test('selected local/shared/prefix wire changes technical routes while preserving field copies and business',t=>{
 const values=['node-http-entry-local-v2','node-http-shared-ports-v2','node-http-api-prefix-v2'].map(variant=>prepareBusinessAuthoringRequests(fixture(t,variant).select()));
 assert.equal(new Set(values.map(value=>value.selection.business_sha256)).size,1);assert.deepEqual(values.map(value=>value.request_source.entries[0]!.route.path),['/submit','/submit','/api/submit']);
 for(const value of values)assert.deepEqual(value.models[0]!.mappings[0]!.fields,values[0]!.models[0]!.mappings[0]!.fields);
});
test('multiple explicit exposures produce combined actual Mapping fragments without implicit entries',t=>{
 const f=fixture(t),input:any=clone(f.input),text=readFileSync(path.join(f.root,'business.alch'),'utf8')+'\ncapability SecondaryEndpoint:\n  invokes Submit\n  public-name submitAgain\n  audience public\n';
 input.spec.capabilities.push({id:'SecondaryEndpoint',operation_ref:'Submit',public_name:'submitAgain',audience:'public'});input.behavior.exposures.push({id:'SecondaryEndpoint',operation_ref:'Submit',public_name:'submitAgain',audience:'public'});input.behavior.exposures.sort((a:any,b:any)=>a.id<b.id?-1:a.id>b.id?1:0);refreshed(input,text);f.write('business.alch',text);
 const value=prepareBusinessAuthoringRequests(selectBusinessAuthoringRecipe(f.snapshot(),[input]));assert.equal(value.models[0]!.mappings.length,2);assert.equal(value.request_source.entries.length,2);
 assert.equal(value.models[0]!.source_fragment,value.models[0]!.mappings.map(mapping=>mapping.source_fragment).join('\n'));assert.deepEqual(value.project_intents.map(intent=>intent.id),['submitAgain','submit']);
});
test('mixed-origin ledger resolves every exact target and links real original fields plus honest profile identity',t=>{
 const f=fixture(t),value=prepareBusinessAuthoringRequests(f.select());validateBusinessAuthoringContract('ledger',value.ledger);
 assert.equal(value.ledger.business_sha256,value.selection.business_sha256);assert.equal(value.ledger.lock_sha256,value.selection.technical.lock_sha256);
 for(const row of value.ledger.entries){
  assert.equal(row.target.artifact,'business-authoring-request-preparation.json');assert.notEqual(pointer(value,row.target.pointer),undefined,row.id);
  assert.ok(row.origins.some(origin=>origin.kind==='business'));assert.ok(row.origins.some(origin=>origin.kind==='profile'));assert.ok(row.origins.some(origin=>origin.kind==='semantic-adapter'));
  for(const origin of row.origins)if(origin.kind==='business'){assert.equal(origin.source,'business.alch');assert.equal(origin.sha256,f.input.source.sha256);assert.ok(f.input.spec.source_spans.some(span=>span.selector===origin.selector));}
  const profile=row.origins.find(origin=>origin.kind==='profile')!;assert.equal(profile.source,'profile:'+f.profile.id);assert.equal(profile.selector,'/authoring/wire');assert.equal(profile.sha256,value.selection.technical.manifest_sha256);
 }
 const field=value.ledger.entries.find(row=>row.id.endsWith('/field/id'))!;const source=field.origins.find(origin=>origin.kind==='business')!;assert.match(f.input.spec.source_spans.find(span=>span.selector===source.selector)!.text,/id UInt64 meaning/);
});
test('composed independent model namespaces retain distinct mappings and exact caller public IDs',t=>{
 const f=fixture(t),other=independentInput('other','other.alch'),adapted=renamed(other.input,other.text,'other','OtherEndpoint','receive');f.write('other.alch',adapted.text);f.project.models.push({id:'other',source:'other.alch'});f.saveProject();
 const value=prepareBusinessAuthoringRequests(selectBusinessAuthoringRecipe(f.snapshot(),[adapted.input,f.input]));assert.deepEqual(value.models.map(model=>model.model_id),['fixture','other']);assert.deepEqual(value.project_intents.map(intent=>intent.id),['submit','receive']);
 assert.equal(new Set(value.models.flatMap(model=>model.mappings.map(mapping=>mapping.mapping_id))).size,2);assert.equal(new Set(value.request_source.entries.map(entry=>entry.operation_ref)).size,2);
});
for(const names of [['submit','submit'],['submitNow','submit_now']])test('composed exact or normalized public-name collisions reject '+names.join('/'),t=>{
 const f=fixture(t),first=renamed(f.input,readFileSync(path.join(f.root,'business.alch'),'utf8'),'fixture','SubmissionEndpoint',names[0]!),other=independentInput('other','other.alch'),second=renamed(other.input,other.text,'other','OtherEndpoint',names[1]!);
 f.write('business.alch',first.text);f.write('other.alch',second.text);f.project.models.push({id:'other',source:'other.alch'});f.saveProject();
 rejected(()=>prepareBusinessAuthoringRequests(selectBusinessAuthoringRecipe(f.snapshot(),[first.input,second.input])),'BUSINESS_REQUEST_COLLISION');
});
test('composition of model/exposure separators cannot collide or receive invented suffixes',t=>{
 const f=fixture(t),a=renamed(f.input,readFileSync(path.join(f.root,'business.alch'),'utf8'),'a','b_c','one'),other=independentInput('a_b','other.alch'),b=renamed(other.input,other.text,'a_b','c','two');
 f.write('business.alch',a.text);f.write('other.alch',b.text);f.project.models=[{id:'a',source:'business.alch'},{id:'a_b',source:'other.alch'}];f.saveProject();
 rejected(()=>prepareBusinessAuthoringRequests(selectBusinessAuthoringRecipe(f.snapshot(),[a.input,b.input])),'BUSINESS_REQUEST_COLLISION');
});
test('generated Mapping ID length boundary is exact and never truncates',t=>{
 const max=128-'CraftRequest_'.length-1-'submission_endpoint'.length;
 for(const delta of [0,1]){
  const f=fixture(t),model='a'.repeat(max+delta),adapted=renamed(f.input,readFileSync(path.join(f.root,'business.alch'),'utf8'),model);f.write('business.alch',adapted.text);f.project.models[0]!.id=model;f.saveProject();
  const selection=selectBusinessAuthoringRecipe(f.snapshot(),[adapted.input]);
  if(delta)rejected(()=>prepareBusinessAuthoringRequests(selection),'BUSINESS_REQUEST_IDENTITY_BUDGET');else assert.equal(prepareBusinessAuthoringRequests(selection).models[0]!.mappings[0]!.mapping_id.length,128);
 }
});
test('qualified Operation selector overflow rejects without shortening authored IDs',t=>{
 const f=fixture(t),renamedModel=renamed(f.input,readFileSync(path.join(f.root,'business.alch'),'utf8'),'a'.repeat(65)),input:any=renamedModel.input,operation='aA'.repeat(64);
 input.spec.operations[0].id=operation;input.behavior.operations[0].operation_ref=operation;input.spec.capabilities[0].operation_ref=operation;input.behavior.exposures[0].operation_ref=operation;
 const text=renamedModel.text.replace('operation Submit:','operation '+operation+':').replace('invokes Submit','invokes '+operation);refreshed(input,text);f.write('business.alch',text);f.project.models[0]!.id=input.model_id;f.saveProject();
 rejected(()=>prepareBusinessAuthoringRequests(selectBusinessAuthoringRecipe(f.snapshot(),[input])),'BUSINESS_REQUEST_IDENTITY_BUDGET');
});
test('registered preparation rejects clones, casts, proxy handles and field mutation',t=>{
 const f=fixture(t),selection=f.select(),value=prepareBusinessAuthoringRequests(selection);
 for(const forged of [clone(value),{...value},Object.create(value),new Proxy(value,{})])rejected(()=>assertBusinessAuthoringRequestsCurrent(forged),'BUSINESS_REQUEST_UNREGISTERED');
 rejected(()=>prepareBusinessAuthoringRequests(clone(selection)),'BUSINESS_RECIPE_UNREGISTERED');
 assert.throws(()=>{(value.models[0]!.mappings[0]!.fields as any).pop();},TypeError);assert.throws(()=>{(value.models[0]!.mappings[0]!.declaration_binding as any).meaning='override';},TypeError);
});
for(const relative of ['business.alch','project.json','profile/profile.json','profile/formal/profile.json','profile/runtime/application-http.mts','identity/core.ts','identity/tool.ts'])test('preparation currentness traverses real selection custody '+relative,t=>{
 const f=fixture(t),selection=f.select(),value=prepareBusinessAuthoringRequests(selection);f.write(relative,readFileSync(path.join(f.root,relative),'utf8')+'\n');rejected(()=>assertBusinessAuthoringRequestsCurrent(value));rejected(()=>prepareBusinessAuthoringRequests(selection));
});
test('owning request module drift invalidates preparation and cannot bless fresh results',async t=>{
 const f=fixture(t),copy=path.join(f.root,'isolated-owner');mkdirSync(path.join(copy,'src'),{recursive:true});cpSync(path.join(cli,'src'),path.join(copy,'src'),{recursive:true});cpSync(path.join(cli,'contracts'),path.join(copy,'contracts'),{recursive:true});
 const loader=await import(pathToFileURL(path.join(copy,'src/profile-engine/loader-v3.ts')).href),recipes=await import(pathToFileURL(path.join(copy,'src/profile-engine/business-authoring-recipes.ts')).href),requests=await import(pathToFileURL(path.join(copy,'src/profile-engine/business-authoring-request.ts')).href);
 const selection=recipes.selectBusinessAuthoringRecipe(loader.loadBusinessAuthoringProject(f.file,f.identity),[f.input]),value=requests.prepareBusinessAuthoringRequests(selection);requests.assertBusinessAuthoringRequestsCurrent(value);
 const filename=path.join(copy,'src/profile-engine/business-authoring-request.ts'),replacement=filename+'.replacement';writeFileSync(replacement,readFileSync(filename));renameSync(replacement,filename);rejected(()=>requests.assertBusinessAuthoringRequestsCurrent(value),'BUSINESS_REQUEST_STALE');rejected(()=>requests.prepareBusinessAuthoringRequests(selection),'BUSINESS_REQUEST_IMPLEMENTATION_STALE');
});
test('preparation stays pure with selected inert native assets and copied source model DTOs',t=>{
 const f=fixture(t);f.write('profile/never-execute.mjs','throw Error("NATIVE_REQUEST_EXECUTION_FORBIDDEN");');f.profile.assets.push({id:'never-execute',path:'never-execute.mjs',kind:'native',sha256:hash('throw Error("NATIVE_REQUEST_EXECUTION_FORBIDDEN");'),includes:[],holes:{}});f.saveProfile();
 const selection=selectBusinessAuthoringRecipe(f.snapshot(),[clone(f.input)]),value=prepareBusinessAuthoringRequests(selection);assertBusinessAuthoringRequestsCurrent(value);assert.equal(value.models[0]!.mappings[0]!.fields.find(field=>field.target==='id')!.type,'UInt64');assert.equal(Object.hasOwn(value,'graph'),false);assert.equal(Object.hasOwn(value,'accepted'),false);
});
