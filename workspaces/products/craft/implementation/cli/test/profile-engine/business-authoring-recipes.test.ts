import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,mkdtempSync,readFileSync,renameSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {loadBusinessAuthoringProject} from '../../src/profile-engine/loader-v3.js';
import {selectBusinessAuthoringRecipe,assertBusinessRecipeSelectionCurrent} from '../../src/profile-engine/business-authoring-recipes.js';
import {BUSINESS_RECIPE_GUARANTEES} from '../../src/profile-engine/business-authoring-normalization-protocol.js';
import type {BusinessRecipeModelInput} from '../../src/profile-engine/business-authoring-normalization-protocol.js';

// Independent DTO expectations, without private Alch imports or accepted carrier fixtures.
// Open questions: B06 must join the genuine Alch producer again before materialization.
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
const rejected=(run:()=>unknown,code?:string)=>assert.throws(run,(error:unknown)=>error instanceof TypeError&&'code' in error&&typeof error.code==='string'&&(code===undefined||error.code===code));

test('registered finite selection preserves independent business data separately from captured technical conventions',t=>{
 const f=fixture(t),selection=f.select();assertBusinessRecipeSelectionCurrent(selection);assert.equal(selection.recipe_ref,recipe);assert.equal(selection.authority_effect,'none');
 assert.equal(selection.business_sha256,digest([{model_id:'fixture',business_sha256:f.input.formal.business_sha256}]));
 assert.deepEqual(clone(selection.models[0]),f.input);assert.ok(Object.isFrozen(selection.models[0]!.formal.definitions[0]!.primitive));
 assert.deepEqual([...selection.technical.required_guarantees],[...BUSINESS_RECIPE_GUARANTEES]);
 assert.equal(selection.technical.wire.method,'POST');assert.equal(selection.technical.profile_id,f.profile.id);
 assert.equal(Object.hasOwn(selection,'accepted'),false);assert.equal(Object.hasOwn(selection,'business_handle'),false);
});
test('all supported architecture profiles and a novel profile ID select the same recipe and business',t=>{
 const rows=['node-http-entry-local-v2','node-http-shared-ports-v2','node-http-api-prefix-v2'].map(variant=>fixture(t,variant));
 const selections=rows.map(f=>f.select());assert.equal(new Set(selections.map(s=>s.business_sha256)).size,1);assert.equal(new Set(selections.map(s=>s.recipe_ref)).size,1);assert.equal(new Set(selections.map(s=>s.technical.lock_sha256)).size,3);
 const f=fixture(t);f.profile.id='independently-named-technical-variant';f.project.profiles[0]!.id=f.profile.id;f.saveProfile();f.saveProject();assert.equal(f.select().technical.profile_id,f.profile.id);
});
test('complete independently namespaced model sets are selected in deterministic order',t=>{
 const f=fixture(t),other=independentInput('another','other.alch');f.write('other.alch',other.text);f.project.models.push({id:'another',source:'other.alch'});f.saveProject();
 const snapshot=f.snapshot(),selection=selectBusinessAuthoringRecipe(snapshot,[f.input,other.input]);assert.deepEqual(selection.models.map(model=>model.model_id),['another','fixture']);assertBusinessRecipeSelectionCurrent(selection);
 rejected(()=>selectBusinessAuthoringRecipe(snapshot,[f.input]));rejected(()=>selectBusinessAuthoringRecipe(snapshot,[f.input,f.input]));
});
test('only registered Core selection objects and registered snapshot owners are current',t=>{
 const f=fixture(t),selection=f.select();for(const value of [clone(selection),{...selection},Object.create(selection),new Proxy(selection,{})])rejected(()=>assertBusinessRecipeSelectionCurrent(value),'BUSINESS_RECIPE_UNREGISTERED');
 rejected(()=>selectBusinessAuthoringRecipe(clone(f.snapshot()),[f.input]),'BUSINESS_PROFILE_SNAPSHOT_UNREGISTERED');
 const inert=clone(f.input);assertBusinessRecipeSelectionCurrent(selectBusinessAuthoringRecipe(f.snapshot(),[inert]));
 // Inert DTOs are explicitly supported input data; they are never labeled as Alch custody.
 assert.equal(Object.hasOwn(selection.models[0]!,'current'),false);
});
for(const [name,mutate] of [
 ['DTO unknown current flag',(i:any)=>i.current=true],['DTO callback',(i:any)=>i.assertCurrent=()=>{}],['source hash',(i:any)=>i.source.sha256='0'.repeat(64)],['source bytes',(i:any)=>i.source.bytes++],['source path',(i:any)=>i.source.path='other.alch'],['model identity',(i:any)=>i.spec.identity.namespace='other'],
 ['missing original span',(i:any)=>i.spec.source_spans.pop()],['duplicate span',(i:any)=>i.spec.source_spans[1]=i.spec.source_spans[0]],['changed span text',(i:any)=>i.spec.source_spans[0].text='fabricated'],['changed span hash',(i:any)=>i.spec.source_spans[0].source_sha256='0'.repeat(64)],['changed span column',(i:any)=>i.spec.source_spans[0].column=9],['missing obligation',(i:any)=>i.spec.obligations.pop()],['changed obligation ref',(i:any)=>i.spec.obligations[0].span_selector='other'],
 ['formal boolean value',(i:any)=>i.formal.definitions[0].primitive.value=false],['formal field',(i:any)=>i.formal.definitions[0].primitive.field='id'],['formal metadata',(i:any)=>i.formal.definitions[0].formal.expression='invented'],['formal notation',(i:any)=>i.formal.definitions[0].formal.notation.reverse()],['formal predicate use',(i:any)=>i.formal.definitions[0].predicate_uses[0].predicate_ref='Other'],['rule predicate map',(i:any)=>i.formal.rule_meanings.CheckEligibility.predicates.Eligible='id'],['rule constant map',(i:any)=>i.formal.rule_meanings.CheckEligibility.constants.submitted='request'],['rule sort map',(i:any)=>i.formal.rule_meanings.CheckEligibility.sorts.SubmissionValue='Other'],['extra normalized formal field',(i:any)=>i.formal.accepted=true],
 ['AST predicate',(i:any)=>i.formal.claims[0].proposition.name='Other'],['AST constant',(i:any)=>i.formal.claims[0].proposition.arguments[0].name='invented'],['AST sort',(i:any)=>i.formal.claims[0].proposition.arguments[0].sort='Other'],['AST wrapper',(i:any)=>i.formal.claims[0].proposition={kind:'not',operand:i.formal.claims[0].proposition}],['formal source text',(i:any)=>i.formal.claims[0].proposition_source='not Eligible(submitted)'],
 ['behavior field type',(i:any)=>i.behavior.operations[0].input.type.fields[0].type='String'],['behavior field loss',(i:any)=>i.behavior.operations[0].output.fields.pop()],['behavior field order',(i:any)=>i.behavior.operations[0].result.type.fields.reverse()],['behavior guard argument',(i:any)=>i.behavior.operations[0].guards[0].argument.root='item'],['behavior guard claim',(i:any)=>i.behavior.operations[0].guards[0].claim_ref='Other'],['behavior result subset',(i:any)=>i.behavior.operations[0].result.path=['id']],['behavior effects',(i:any)=>i.behavior.operations[0].effects=['write']],['failure continuation',(i:any)=>i.behavior.operations[0].failure.continuation='silently-retry'],['executable continuation',(i:any)=>i.behavior.operations[0].failure.executable=true],['exposure omission',(i:any)=>i.behavior.exposures=[]],['protected audience',(i:any)=>i.behavior.exposures[0].audience='authenticated'],['actor authentication',(i:any)=>i.behavior.actor_semantics='authenticated'],['context mutation',(i:any)=>i.behavior.contexts[0].actors=['Authenticated owner']],['business digest',(i:any)=>i.formal.business_sha256='0'.repeat(64)],['formal digest',(i:any)=>i.behavior.formal_sha256='0'.repeat(64)],
] as [string,(i:any)=>void][])test('finite normalized transport rejects '+name,t=>{const f=fixture(t),input=clone(f.input);mutate(input);rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[input]));});
for(const [name,mutate] of [
 ['unknown definition reference',(i:any)=>i.spec.claims[0].predicates[0].definition_ref='Missing'],['mismatched Bool field',(i:any)=>i.spec.definitions[0].boolean_field.path=['id']],['unknown formal sort',(i:any)=>i.spec.claims[0].constants[0].sort_ref='Missing'],['unused predicate',(i:any)=>i.spec.claims[0].predicates.push({name:'Unused',sort_refs:['SubmissionValue'],definition_ref:'EligibilityDefinition'})],['unsupported equality',(i:any)=>i.spec.claims[0].proposition='submitted = submitted'],['unsupported quantifier',(i:any)=>i.spec.claims[0].proposition='forall x: SubmissionValue: Eligible(x)'],['unknown formula constant',(i:any)=>i.spec.claims[0].proposition='Eligible(other)'],['duplicate declaration',(i:any)=>i.spec.entities.push(clone(i.spec.entities[0]))],['wrong rule parameter',(i:any)=>i.spec.rules[0].bindings[0].parameter_ref='request'],['wrong typed guard',(i:any)=>i.spec.operations[0].guards[0].arguments[0].parameter='wrong'],['subset source result',(i:any)=>i.spec.operations[0].result.path=['id']],['nonempty source effect',(i:any)=>i.spec.operations[0].effects.push('write')],['unsupported supersession',(i:any)=>i.spec.claims[0].supersedes='previous'],
] as [string,(i:any)=>void][])test('malformed inert BusinessSpec rejects '+name+' even after caller recomputes digests',t=>{const f=fixture(t),input=clone(f.input);mutate(input);recalculate(input);rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[input]));});
test('ground AST preserves grouping, precedence, repeated operands and implication associativity',t=>{
 const f=fixture(t),input:any=clone(f.input),predicate=atom();
 input.spec.claims[0].proposition='Eligible(submitted) and (not Eligible(submitted) or Eligible(submitted))';
 input.formal.claims[0].proposition_source=input.spec.claims[0].proposition;
 input.formal.claims[0].proposition={kind:'and',left:predicate,right:{kind:'or',left:{kind:'not',operand:clone(predicate)},right:clone(predicate)}};recalculate(input);
 assertBusinessRecipeSelectionCurrent(selectBusinessAuthoringRecipe(f.snapshot(),[input]));
 const dropped=clone(input);dropped.formal.claims[0].proposition=atom();recalculate(dropped);rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[dropped]));
 const regrouped=clone(input);regrouped.formal.claims[0].proposition={kind:'or',left:{kind:'and',left:atom(),right:{kind:'not',operand:atom()}},right:atom()};recalculate(regrouped);rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[regrouped]));
 input.spec.claims[0].proposition='Eligible(submitted) implies Eligible(submitted) implies Eligible(submitted)';input.formal.claims[0].proposition_source=input.spec.claims[0].proposition;input.formal.claims[0].proposition={kind:'implies',left:atom(),right:{kind:'implies',left:atom(),right:atom()}};recalculate(input);assertBusinessRecipeSelectionCurrent(selectBusinessAuthoringRecipe(f.snapshot(),[input]));
 const left=clone(input);left.formal.claims[0].proposition={kind:'implies',left:{kind:'implies',left:atom(),right:atom()},right:atom()};recalculate(left);rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[left]));
});
test('source grouping depth and normalized AST depth retain independent finite budgets',t=>{
 const f=fixture(t),input:any=clone(f.input);
 input.spec.claims[0].proposition='('.repeat(63)+'Eligible(submitted) implies Eligible(submitted) implies Eligible(submitted)'+')'.repeat(63);
 input.formal.claims[0].proposition_source=input.spec.claims[0].proposition;
 input.formal.claims[0].proposition={kind:'implies',left:atom(),right:{kind:'implies',left:atom(),right:atom()}};recalculate(input);
 assertBusinessRecipeSelectionCurrent(selectBusinessAuthoringRecipe(f.snapshot(),[input]));
 const deeper=clone(input);deeper.spec.claims[0].proposition='('+input.spec.claims[0].proposition+')';deeper.formal.claims[0].proposition_source=deeper.spec.claims[0].proposition;recalculate(deeper);rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[deeper]));
});
test('explicit predicate definition reuse preserves independently resolved requirement refs',t=>{
 const f=fixture(t),input:any=clone(f.input),other={...clone(input.spec.requirements[0]),id:'OtherRequirement'};
 input.spec.requirements.push(other);input.spec.claims[0].requirement_ref=other.id;input.behavior.contexts=[other,input.spec.requirements[0]];recalculate(input);
 assertBusinessRecipeSelectionCurrent(selectBusinessAuthoringRecipe(f.snapshot(),[input]));
});
for(const [name,mutate] of [
 ['direct predicate',(p:any)=>p.rules[0].fields.predicate={literal:'id = id'}],['nested technical guard',(p:any)=>p.rules[0].fields.technical.literal.guards=[]],['default business',(p:any)=>p.rules.push({id:'injected',op:'defaults',as:'extra',values:{business:{result:'id'}}})],['project failure',(p:any)=>p.rules.push({id:'injected',op:'project',from:'applications',as:'extra',fields:{failure:{literal:'retry'}}})],['hidden literal audience',(p:any)=>p.rules.push({id:'injected',op:'defaults',as:'extra',values:{misc:{audience:'private'}}})],['arbitrary evaluator',(p:any)=>p.rules.push({id:'injected',op:'defaults',as:'extra',values:{evaluate:'doEvil()'}})],['replaced operation selector',(p:any)=>p.rules[0].fields.selector={literal:'Other'}],['filtered exposure',(p:any)=>{p.rules.unshift({id:'filtered',op:'select',from:'applications',as:'onlyone',where:{field:['id'],equals:'hidden'}});p.rules[1].from='onlyone';}],['wrong wire limit',(p:any)=>p.rules[0].fields.technical.literal.request_bytes=9],
] as [string,(p:any)=>void][])test('profile authority cannot inject '+name,t=>{const f=fixture(t);mutate(f.profile);f.saveProfile();rejected(()=>f.select());});
test('unsupported required recipes, logic, target, effects, guarantees and open requirement fields reject',t=>{
 const f=fixture(t),snapshot=f.snapshot(),base={recipe_ref:recipe,logic_profile:'fol-core/1-candidate',target:'node-typescript',effects:'none',required_guarantees:[...BUSINESS_RECIPE_GUARANTEES]};
 for(const [key,value] of [['recipe_ref','arbitrary-js'],['logic_profile','other'],['target','python'],['effects','write'],['required_guarantees',['durable-exactly-once']]])rejected(()=>selectBusinessAuthoringRecipe(snapshot,[f.input],{...base,[key as string]:value} as any),'BUSINESS_RECIPE_UNSUPPORTED');
 rejected(()=>selectBusinessAuthoringRecipe(snapshot,[f.input],{...base,current:true} as any));
 assertBusinessRecipeSelectionCurrent(selectBusinessAuthoringRecipe(snapshot,[f.input],{...base,required_guarantees:[]} as any));
});
for(const table of ['applications','application_models','application_declarations','business','definitions','claims','operations'])test('profile cannot shadow authored table '+table,t=>{
 for(const operation of ['defaults','project']){
  const f=fixture(t);
  if(operation==='defaults')f.profile.rules.unshift({id:'shadow',op:'defaults',as:table,values:{id:'invented'}});
  else f.profile.rules.push({id:'shadow',op:'project',from:'dispatcher',as:table,fields:{id:{field:['id']}}});
  f.saveProfile();rejected(()=>f.select(),'BUSINESS_RECIPE_PROFILE_AUTHORITY');
 }
});
for(const key of ['failure_continuation','on_rejection','boolean_field','operation_behaviors','unknown_required_business_map'])test('closed technical profile vocabulary rejects semantic alias '+key,t=>{
 for(const container of ['defaults','project','technical']){
  const f=fixture(t);
  if(container==='defaults')f.profile.rules.push({id:'hidden',op:'defaults',as:'extra',values:{[key]:'replacement'}});
  if(container==='project')f.profile.rules.push({id:'hidden',op:'project',from:'dispatcher',as:'extra',fields:{[key]:{literal:'replacement'}}});
  if(container==='technical')f.profile.rules[0].fields.technical.literal[key]='replacement';
  f.saveProfile();rejected(()=>f.select());
 }
});
test('qualified technical projection and literal strings remain inert data',t=>{
 const f=fixture(t);f.profile.rules.splice(2,0,{id:'technical-copy',op:'project',from:'dispatcher',as:'copied-dispatcher',fields:{id:{field:['id']},artifact_path:{field:['artifact_path']}}});f.profile.rules[3].from='copied-dispatcher';
 f.profile.rules[1].values.id='semantic_failure_continuation_comment_only';f.saveProfile();assertBusinessRecipeSelectionCurrent(f.select());
});
for(const relative of ['business.alch','project.json','profile/profile.json','profile/formal/profile.json','profile/formal/identity.json','profile/runtime/empty-settlement.ts','profile/runtime/application-http.mts','identity/core.ts','identity/tool.ts'])test('recipe currentness rechecks captured closure '+relative,t=>{
 const f=fixture(t),selection=f.select();f.write(relative,readFileSync(path.join(f.root,relative),'utf8')+'\n');rejected(()=>assertBusinessRecipeSelectionCurrent(selection));
});
test('owning recipe module bytes are checked independently of caller engine manifest',async t=>{
 for(const mutation of ['bytes','replacement']){
  const f=fixture(t),copy=path.join(f.root,'isolated-owner');mkdirSync(path.join(copy,'src'),{recursive:true});
  cpSync(path.join(cli,'src/profile-engine'),path.join(copy,'src/profile-engine'),{recursive:true});cpSync(path.join(cli,'contracts'),path.join(copy,'contracts'),{recursive:true});
  const loader=await import(pathToFileURL(path.join(copy,'src/profile-engine/loader-v3.ts')).href),recipes=await import(pathToFileURL(path.join(copy,'src/profile-engine/business-authoring-recipes.ts')).href);
  const snapshot=loader.loadBusinessAuthoringProject(f.file,f.identity),selection=recipes.selectBusinessAuthoringRecipe(snapshot,[f.input]);recipes.assertBusinessRecipeSelectionCurrent(selection);
  const filename=path.join(copy,'src/profile-engine/business-authoring-recipes.ts');
  if(mutation==='bytes')writeFileSync(filename,readFileSync(filename,'utf8')+'\n');
  else {const replacement=filename+'.replacement';writeFileSync(replacement,readFileSync(filename));renameSync(replacement,filename);}
  rejected(()=>recipes.assertBusinessRecipeSelectionCurrent(selection),'BUSINESS_RECIPE_MODULE_STALE');
  rejected(()=>recipes.selectBusinessAuthoringRecipe(snapshot,[f.input]),'BUSINESS_RECIPE_MODULE_STALE');
 }
});
test('capture rejects supplied accessors/proxies and does not run a profile native asset',t=>{
 const f=fixture(t);let calls=0;const supplied={...f.input,get formal(){calls++;return f.input.formal;}};rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[supplied]));assert.equal(calls,0);
 rejected(()=>selectBusinessAuthoringRecipe(f.snapshot(),[new Proxy(f.input,{})]));
 f.write('profile/must-not-run.mjs','throw Error("PROFILE_NATIVE_EXECUTED");');f.profile.assets.push({id:'inert-extra',path:'must-not-run.mjs',kind:'native',sha256:hash('throw Error("PROFILE_NATIVE_EXECUTED");'),includes:[],holes:{}});f.saveProfile();assertBusinessRecipeSelectionCurrent(f.select());
});
