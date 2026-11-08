import {closeSync,constants,fstatSync,lstatSync,openSync,readSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest,reject,sha256} from './contracts.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {assertBusinessAuthoringSnapshotCurrent,type BusinessAuthoringSnapshot} from './loader-v3.js';
import {BUSINESS_AUTHORING_CONTRACT,BUSINESS_AUTHORING_LIMITS,BUSINESS_AUTHORING_LOGIC,BUSINESS_AUTHORING_RECIPE,type BusinessClaim,type BusinessEntity,type BusinessSpecData,type BusinessWireConvention} from './business-authoring-protocol.js';
import {BUSINESS_NORMALIZATION_CONTRACT,BUSINESS_RECIPE_GUARANTEES,type BusinessBehaviorData,type BusinessEntityStructure,type BusinessFormalData,type BusinessGroundProposition,type BusinessNormalizedDefinition,type BusinessRecipeModelInput,type BusinessRecipeRequirements,type BusinessRuleInterpretation} from './business-authoring-normalization-protocol.js';
import {validateBusinessAuthoringContractV2} from './business-authoring-schema-v2.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2,projectBusinessReviewSubjectV2,captureBusinessIdentityV2} from './business-authoring-identity-v2.js';
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import {BUSINESS_SPEC_V2,BUSINESS_SOURCE_V2_MARKER,BUSINESS_AUTHORING_RECIPE_V2,type BusinessSpecDataV2,type BusinessClaimV2} from './business-authoring-protocol-v2.js';
import type {BusinessCaptureIdentityV2,BusinessSelectedModelV2,BusinessRecipeSelectionV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessDirectSourceTransferV2,BusinessCoreRecipeOwnerV2} from './business-authoring-stages-v2.js';
import {U0_NATIVE_ABI,U0_SUCCESSOR_DESCRIPTOR,checkU0WireConfiguration,type U0ResolvedNativeBasis} from './u0-realization-contract.js';

/** Core-owned finite selection over inert validated data, not an Alch handle or source provenance proof.
 * The public Alch join and future B06 must retain the genuine producer owners.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md; acceptance/generation are later stages. */
export interface BusinessRecipeSelection {
 readonly kind:'business-recipe-selection';readonly recipe_ref:typeof BUSINESS_AUTHORING_RECIPE;
 readonly normalization_contract:typeof BUSINESS_NORMALIZATION_CONTRACT;
 readonly models:readonly BusinessRecipeModelInput[];readonly requirements:BusinessRecipeRequirements;
 readonly business_sha256:string;
 readonly technical:Readonly<{profile_id:string;profile_version:string;manifest_sha256:string;asset_sha256:string;wire:BusinessWireConvention;transport:'entry-local'|'shared';required_guarantees:readonly string[];lock_sha256:string}>;
 readonly authority_effect:'none';
}
const registry=new WeakMap<object,{snapshot:BusinessAuthoringSnapshot;module:string;fingerprint:string}>();
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const byId=<T extends {id:string}>(rows:readonly T[]):T[]=>[...rows].sort((a,b)=>compare(a.id,b.id));
const byName=<T extends {name:string}>(rows:readonly T[]):T[]=>[...rows].sort((a,b)=>compare(a.name,b.name));
const normalized=(value:string)=>value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
function fail(at:string,message:string):never{return reject('BUSINESS_RECIPE_CORRESPONDENCE',at,message);}
function same(actual:unknown,expected:unknown,at:string):void {if(actual===undefined||expected===undefined||dataDigest(actual)!==dataDigest(expected))fail(at,'exact finite normalization correspondence required');}
function closed(value:unknown,keys:readonly string[],at:string):asserts value is Record<string,unknown> {
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==keys.length||keys.some(key=>!Object.hasOwn(value,key)))fail(at,'closed required DTO fields only');
}
function unique(values:readonly string[],at:string):void {if(new Set(values.map(normalized)).size!==values.length)fail(at,'duplicate or normalization-colliding identities');}
function validName(value:string,at:string):void {
 const key=normalized(value).replace(/^craft-request-/,'craftrequest-');
 if(key.startsWith('craftrequest-')||['constructor','prototype','__proto__'].includes(value.toLowerCase()))fail(at,'reserved backend identity');
}
function nonempty(value:string,at:string):void {if(!value.trim())fail(at,'authored nonempty meaning required');}
function expectedBusinessDigest(spec:BusinessSpecData):string {
 const {source_spans:_spans,obligations:_obligations,...semantic}=spec;
 return dataDigest({...semantic,requirements:byId(spec.requirements),entities:byId(spec.entities).map(entity=>({...entity,fields:byName(entity.fields)})),definitions:byId(spec.definitions),claims:byId(spec.claims).map(claim=>({...claim,sorts:byName(claim.sorts),predicates:byName(claim.predicates),constants:byName(claim.constants)})),rules:byId(spec.rules),operations:byId(spec.operations),capabilities:byId(spec.capabilities)});
}
function checkSource(snapshot:BusinessAuthoringSnapshot,input:BusinessRecipeModelInput,at:string):void {
 const selected=snapshot.project.models.find(model=>model.id===input.model_id);
 if(!selected)fail(at+'/model_id','model is not selected');
 const file=snapshot.sources[selected!.source];if(!file||file.text===undefined)fail(at+'/source','exact captured source required');
 same(input.source,{path:selected!.source,sha256:file!.sha256,bytes:file!.bytes},at+'/source');
 const spec=input.spec;
 if(spec.identity.stable_id!==input.model_id||spec.identity.namespace!==input.model_id)fail(at+'/spec/identity','selection and explicit model identities differ');
 if(file!.bytes>BUSINESS_AUTHORING_LIMITS.source_bytes||Buffer.byteLength(file!.text!)!==file!.bytes||sha256(file!.text!)!==file!.sha256)fail(at+'/source','original finite UTF-8 bytes required');
 const lines=file!.text!.split('\n');if(lines.length>BUSINESS_AUTHORING_LIMITS.lines)fail(at+'/source','source line budget exceeded');
 const facts:{raw:string;line:number;column:number}[]=[];
 for(const [index,line] of lines.entries()){
  const raw=index<lines.length-1?line.replace(/\r$/,''):line;
  if(/[\t\r\0]/.test(raw))fail(at+'/source','invalid original source line');
  if(!raw.trim()||raw.trimStart().startsWith('#'))continue;
  const indent=raw.length-raw.trimStart().length;
  if(raw.length>4096||raw.slice(0,indent)!==' '.repeat(indent)||indent%2||indent/2>BUSINESS_AUTHORING_LIMITS.depth)fail(at+'/source','invalid source indentation or span budget');
  facts.push({raw,line:index+1,column:indent+1});
 }
 if(spec.source_spans.length!==facts.length||spec.obligations.length!==facts.length)fail(at+'/spec/source_spans','complete original source inventory required');
 const selectors=new Set<string>();
 facts.forEach((fact,index)=>{
  const span=spec.source_spans[index]!,obligation=spec.obligations[index]!;
  if(span.source!==file!.relative||span.source_sha256!==file!.sha256||span.text!==fact.raw||span.line!==fact.line||span.column!==fact.column||!span.selector.endsWith('/line:'+fact.line)||selectors.has(span.selector))fail(at+'/spec/source_spans/'+index,'span must identify its exact original fact once');
  selectors.add(span.selector);
  if(obligation.selector!==span.selector||obligation.span_selector!==span.selector)fail(at+'/spec/obligations/'+index,'complete one-to-one original obligation inventory required');
 });
}
function structure(entity:BusinessEntity):BusinessEntityStructure {return {kind:'entity',entity_ref:entity.id,identity:entity.identity,fields:byName(entity.fields).map(({name,type})=>({name,type}))};}

/** Bounded independent parser for the registered ground subgrammar. Grouping and associativity are retained. */
function groundProposition(claim:BusinessClaim,at:string):BusinessGroundProposition {
 const tokens:string[]=[];let offset=0;
 while(offset<claim.proposition.length){if(/\s/.test(claim.proposition[offset]!)){offset++;continue;}const match=/^(?:[A-Za-z_][A-Za-z0-9_.-]*|[(),])/.exec(claim.proposition.slice(offset));if(!match)fail(at,'unsupported ground proposition token');tokens.push(match![0]);offset+=match![0].length;}
 if(tokens.length>10000)fail(at,'ground proposition token budget exceeded');
 let groups=0;
 for(const token of tokens){if(token==='('&&++groups>64)fail(at,'source formula grouping budget exceeded');if(token===')')groups--;}
 if(tokens.filter(token=>token==='not'||token==='implies'||token==='forall'||token==='exists').length>64)fail(at,'source formula recursion budget exceeded');
 const predicates=new Map(claim.predicates.map(predicate=>[predicate.name,predicate])),constants=new Map(claim.constants.map(constant=>[constant.name,constant])),used=new Set<string>();let cursor=0,visits=0;
 const take=(expected?:string):string=>{const token=tokens[cursor++];if(!token||expected!==undefined&&token!==expected)fail(at,'malformed ground proposition');return token!;};
 const peek=()=>tokens[cursor];
 const unary=(depth:number):BusinessGroundProposition=>{
  // Source grouping and semantic AST depth are separate budgets. Redundant grouping
  // does not increase the normalized AST depth; the source guard above bounds parsing.
  if(++visits>10000||depth>128)fail(at,'ground proposition parsing budget exceeded');
  if(peek()==='not'){take();return {kind:'not',operand:unary(depth+1)};}
  if(peek()==='('){take();const value=iff(depth+1);take(')');return value;}
  const name=take(),predicate=predicates.get(name);if(!predicate)fail(at,'unknown or unsupported predicate '+name);used.add(name);take('(');const constantName=take(),constant=constants.get(constantName);if(!constant)fail(at,'unknown ground constant '+constantName);used.add(constantName);take(')');
  if(predicate!.sort_refs.length!==1||constant!.sort_ref!==predicate!.sort_refs[0])fail(at,'predicate argument sort differs');
  return {kind:'predicate',name,arguments:[{kind:'constant',name:constantName,sort:constant!.sort_ref}]};
 };
 const and=(depth:number):BusinessGroundProposition=>{let left=unary(depth);while(peek()==='and'){take();left={kind:'and',left,right:unary(depth)};}return left;};
 const or=(depth:number):BusinessGroundProposition=>{let left=and(depth);while(peek()==='or'){take();left={kind:'or',left,right:and(depth)};}return left;};
 const implies=(depth:number):BusinessGroundProposition=>{if(depth>128)fail(at,'ground parsing depth exceeded');const left=or(depth);if(peek()!=='implies')return left;take();return {kind:'implies',left,right:implies(depth+1)};};
 const iff=(depth:number):BusinessGroundProposition=>{const left=implies(depth);if(peek()!=='iff')return left;take();const value:BusinessGroundProposition={kind:'iff',left,right:implies(depth)};if(peek()==='iff')fail(at,'chained iff requires explicit grouping');return value;};
 const value=iff(0);if(cursor!==tokens.length)fail(at,'unexpected trailing ground proposition data');
 for(const name of [...predicates.keys(),...constants.keys()])if(!used.has(name))fail(at,'unused declared proposition symbol '+name);
 const expansion=(node:BusinessGroundProposition,depth=0):number=>{if(depth>64)fail(at,'ground AST depth exceeded');const count=node.kind==='predicate'?1:node.kind==='not'?1+expansion(node.operand,depth+1):1+(node.kind==='iff'?2:1)*(expansion(node.left,depth+1)+expansion(node.right,depth+1));if(count>1024)fail(at,'expanded formal projection exceeds 1024 nodes');return count;};expansion(value);return value;
}

function expectedNormalization(spec:BusinessSpecData,at:string):{formal:BusinessFormalData;behavior:BusinessBehaviorData;business:string} {
 const all=[...spec.requirements,...spec.entities,...spec.definitions,...spec.claims,...spec.rules,...spec.operations,...spec.capabilities];
 if(all.length>BUSINESS_AUTHORING_LIMITS.declarations||spec.entities.reduce((count,entity)=>count+entity.fields.length,0)>BUSINESS_AUTHORING_LIMITS.fields)fail(at,'declaration or field budget exceeded');
 unique(all.map(row=>row.id),at+'/ids');for(const row of all)validName(row.id,at+'/'+row.id);validName(spec.identity.stable_id,at+'/identity');
 nonempty(spec.identity.title,at+'/identity/title');for(const token of [spec.identity.owner,spec.identity.version])if(!token||/\s/.test(token))fail(at+'/identity','explicit whitespace-free owner/version required');
 const entities=new Map(spec.entities.map(entity=>[entity.id,entity])),requirements=new Map(spec.requirements.map(requirement=>[requirement.id,requirement])),definitions=new Map(spec.definitions.map(definition=>[definition.id,definition])),claims=new Map(spec.claims.map(claim=>[claim.id,claim])),rules=new Map(spec.rules.map(rule=>[rule.id,rule])),operations=new Map(spec.operations.map(operation=>[operation.id,operation]));
 const get=<T>(map:Map<string,T>,key:string,pointer:string):T=>{const value=map.get(key);if(!value)fail(pointer,'unknown explicit reference '+key);return value!;};
 for(const entity of spec.entities){unique(entity.fields.map(field=>field.name),at+'/entities/'+entity.id);nonempty(entity.meaning,at+'/entities/'+entity.id);if(!entity.fields.some(field=>field.name===entity.identity))fail(at,'Entity identity must select its declared field');for(const field of entity.fields){validName(field.name,at+'/fields');nonempty(field.meaning,at+'/fields');}}
 for(const requirement of spec.requirements){for(const text of [requirement.context,requirement.meaning,...requirement.applies_when,...requirement.actors,...requirement.boundaries])nonempty(text,at+'/requirements');unique([...requirement.examples,...requirement.counterexamples].map(row=>row.case_id),at+'/requirements/cases');for(const example of [...requirement.examples,...requirement.counterexamples])for(const text of [example.given,example.when,example.then,example.why])nonempty(text,at+'/requirements/cases');}
 for(const definition of spec.definitions){get(requirements,definition.requirement_ref,at+'/definitions/requirement');const entity=get(entities,definition.input.type_ref,at+'/definitions/input'),field=entity.fields.find(field=>field.name===definition.boolean_field.path[0]);validName(definition.input.name,at+'/definitions/input');nonempty(definition.meaning,at+'/definitions/meaning');if(definition.boolean_field.root!==definition.input.name||definition.boolean_field.path.length!==1||field?.type!=='Bool')fail(at+'/definitions','exact Entity Bool-field primitive required');}
 for(const claim of spec.claims){
  get(requirements,claim.requirement_ref,at+'/claims/requirement');if(claim.supersedes!==null||/\s/.test(claim.version))fail(at+'/claims','supersession/version is outside the supported recipe');nonempty(claim.ceiling,at+'/claims/ceiling');
  unique([...claim.sorts,...claim.predicates,...claim.constants].map(row=>row.name),at+'/claims/signature');
  for(const row of [...claim.sorts,...claim.predicates,...claim.constants]){validName(row.name,at+'/claims/signature');if(['forall','exists','not','and','or','implies','iff'].includes(row.name))fail(at+'/claims/signature','reserved formal symbol');}
  const sorts=new Map(claim.sorts.map(sort=>[sort.name,sort]));
  for(const sort of claim.sorts){get(entities,sort.type_ref,at+'/claims/sorts');if(!claim.predicates.some(predicate=>predicate.sort_refs.includes(sort.name))&&!claim.constants.some(constant=>constant.sort_ref===sort.name))fail(at+'/claims/sorts','unused formal sort');}
  for(const constant of claim.constants)get(sorts,constant.sort_ref,at+'/claims/constants');
  for(const predicate of claim.predicates){const sort=get(sorts,predicate.sort_refs[0]!,at+'/claims/predicates'),definition=get(definitions,predicate.definition_ref,at+'/claims/predicates');if(predicate.sort_refs.length!==1||definition.input.type_ref!==sort.type_ref)fail(at+'/claims/predicates','unary typed predicate/definition correspondence required');}
 }
 const business=expectedBusinessDigest(spec);
 const normalizedDefinitions:BusinessNormalizedDefinition[]=byId(spec.definitions).map(definition=>{
  const entity=entities.get(definition.input.type_ref)!,field=entity.fields.find(field=>field.name===definition.boolean_field.path[0])!,parameter=definition.input.name,selected=parameter+'.'+field.name;
  const uses=spec.claims.flatMap(claim=>claim.predicates.filter(predicate=>predicate.definition_ref===definition.id).map(predicate=>({claim_ref:claim.id,predicate_ref:predicate.name,sort_ref:predicate.sort_refs[0]!}))).sort((a,b)=>compare(a.claim_ref,b.claim_ref)||compare(a.predicate_ref,b.predicate_ref)||compare(a.sort_ref,b.sort_ref));
  const direct=`${definition.id}(${parameter}: ${entity.id}) := (${selected} = true)`;
  return {definition_ref:definition.id,requirement_ref:definition.requirement_ref,input:definition.input,entity:structure(entity),field,primitive:{kind:'entity-bool-field',entity_ref:entity.id,parameter,field:field.name,field_type:'Bool',comparison:'eq',value:true},formal:{definition:direct,expression:uses.length?uses.map(use=>`${use.claim_ref}::${use.predicate_ref}(${parameter}: ${use.sort_ref}) iff (${selected} = true)`).join('; '):direct,notation:[{symbol:parameter,meaning:entity.meaning},{symbol:selected,meaning:field.meaning}],operational_interpretation:`Read ${selected}: Bool and compare with true.`},predicate_uses:uses};
 });
 const ruleMeanings:Record<string,BusinessRuleInterpretation>=Object.create(null);
 for(const rule of byId(spec.rules)){
  const entity=get(entities,rule.input.type_ref,at+'/rules/input'),claim=get(claims,rule.claim_ref,at+'/rules/claim');validName(rule.input.name,at+'/rules/input');nonempty(rule.meaning,at+'/rules/meaning');
  if(rule.bindings.length!==1||claim.constants.length!==1)fail(at+'/rules/bindings','one explicit backend-compatible constant binding required');
  const binding=rule.bindings[0]!,constant=claim.constants[0]!,sort=claim.sorts.find(sort=>sort.name===constant.sort_ref)!;
  if(binding.constant_ref!==constant.name||binding.parameter_ref!==rule.input.name||sort.type_ref!==entity.id)fail(at+'/rules/bindings','exact constant/Rule input/Entity correspondence required');
  ruleMeanings[rule.id]={sorts:Object.fromEntries(byName(claim.sorts).map(sort=>[sort.name,sort.type_ref])),constants:Object.fromEntries(byName(claim.constants).map(constant=>[constant.name,rule.bindings.find(binding=>binding.constant_ref===constant.name)!.parameter_ref])),predicates:Object.fromEntries(byName(claim.predicates).map(predicate=>[predicate.name,definitions.get(predicate.definition_ref)!.boolean_field.path[0]!]))};
 }
 const formal:BusinessFormalData={schema_version:'craft.business-formal-normalization/v1-candidate',normalization_contract:BUSINESS_NORMALIZATION_CONTRACT,model_id:spec.identity.stable_id,business_sha256:business,definitions:normalizedDefinitions,claims:byId(spec.claims).map(claim=>({claim_ref:claim.id,version:claim.version,logic_profile:claim.logic_profile,signature:{sorts:byName(claim.sorts).map(sort=>({name:sort.name})),functions:[],predicates:byName(claim.predicates).map(predicate=>({name:predicate.name,parameter_sorts:[...predicate.sort_refs]})),constants:byName(claim.constants).map(constant=>({name:constant.name,sort:constant.sort_ref}))},proposition_source:claim.proposition,proposition:groundProposition(claim,at+'/claims/'+claim.id+'/proposition'),ceiling:claim.ceiling})),rule_meanings:ruleMeanings,authority_effect:'none'};
 const normalizedOperations:BusinessBehaviorData['operations'][number][]=byId(spec.operations).map(operation=>{
  const input=get(entities,operation.input.type_ref,at+'/operations/input'),output=get(entities,operation.output_ref,at+'/operations/output');validName(operation.input.name,at+'/operations/input');nonempty(operation.meaning,at+'/operations/meaning');
  if(input.id!==output.id||operation.result.root!==operation.input.name||operation.result.path.length||operation.effects.length||operation.guards.length!==1)fail(at+'/operations','one guard, whole identical input result and empty effects required');
  const guard=operation.guards[0]!,rule=get(rules,guard.rule_ref,at+'/operations/guard'),argument=guard.arguments[0];
  if(rule.input.type_ref!==input.id||guard.arguments.length!==1||argument?.parameter!==rule.input.name||argument.value.root!==operation.input.name||argument.value.path.length)fail(at+'/operations/guard','whole structurally matching typed guard argument required');
  validName(operation.on_rejection,at+'/operations/on_rejection');
  return {operation_ref:operation.id,meaning:operation.meaning,input:{name:operation.input.name,type:structure(input)},output:structure(output),guards:[{rule_ref:rule.id,claim_ref:rule.claim_ref,parameter:{name:rule.input.name,type:structure(input)},argument:{root:operation.input.name,path:[]}}],result:{root:operation.input.name,path:[],type:structure(output)},effects:[],failure:{kind:'continuation-metadata',continuation:operation.on_rejection,executable:false}};
 });
 unique(spec.capabilities.map(capability=>capability.public_name),at+'/exposures');for(const capability of spec.capabilities){get(operations,capability.operation_ref,at+'/exposures');validName(capability.public_name,at+'/exposures');}
 const behavior:BusinessBehaviorData={schema_version:'craft.business-behavior-normalization/v1-candidate',normalization_contract:BUSINESS_NORMALIZATION_CONTRACT,model_id:spec.identity.namespace,business_sha256:business,formal_sha256:dataDigest(formal),operations:normalizedOperations,exposures:byId(spec.capabilities),contexts:byId(spec.requirements),actor_semantics:'informational-only',authority_effect:'none'};
 return {formal,behavior,business};
}

const forbiddenProfileKeys=new Set(['predicate','predicates','guard','guards','result','results','failure','failures','audience','effect','effects','meaning','meanings','semantics','semantic','business','formal','definition','definitions','operationbehaviors','rulemeanings','acceptance','owneracceptance','decision','decisions','evaluate','evaluator','native','javascript','logicprofile','requiredguarantees']);
function checkTechnicalRules(snapshot:BusinessAuthoringSnapshot,wire:BusinessWireConvention):void {
 const scan=(value:unknown,at:string):void=>{if(Array.isArray(value)){value.forEach((child,index)=>scan(child,at+'/'+index));return;}if(value&&typeof value==='object')for(const [key,child] of Object.entries(value)){if(forbiddenProfileKeys.has(key.replace(/[^A-Za-z]/g,'').toLowerCase()))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/'+key,'profiles cannot supply business semantics or semantic execution hooks');scan(child,at+'/'+key);}};
 let operations=0,dispatchers=0,shared=0;
 const fields:Record<string,readonly string[]>={'application-operation':['id','project_ref','selector','route','technical','artifact_path'],'http-dispatch':['id','artifact_path','template_ref','technical'],'shared-http-port':['id','artifact_path','template_ref','technical']};
 const reserved=new Set(['applications','application_models','application_declarations','business','business_models','business_declarations','definitions','claims','rules','operations','capabilities','semantics','formal','behavior']);
 const technicalKeys=['id','artifact_path','technical'];
 const technicalValue=(value:unknown,at:string):void=>{
  if(!value||typeof value!=='object'||Array.isArray(value))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at,'closed technical convention dictionary required');
  for(const [key,child] of Object.entries(value)){
   if(!['kind','request_bytes','timeout_ms'].includes(key)||key==='kind'&&child!=='application-operation'||key==='request_bytes'&&child!==wire.request_bytes||key==='timeout_ms'&&child!==wire.timeout_ms)reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/'+key,'unknown or incompatible technical convention');
  }
 };
 for(const pkg of snapshot.packages){const tables=new Map<string,ReadonlySet<string>>();for(const [index,rule] of pkg.data.rules.entries()){
  const at='/packages/'+pkg.id+'/rules/'+index;scan(rule,at);
  if('as' in rule&&reserved.has(rule.as))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/as','authored input tables cannot be replaced or shadowed');
  const expression=(value:any,columns:ReadonlySet<string>,pointer:string,technical=false):void=>{
   if('field' in value){if(value.field.length!==1||!columns.has(value.field[0])||technical!==(value.field[0]==='technical'))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',pointer,'only correctly typed owned technical metadata columns may be referenced');return;}
   if('literal' in value){if(technical)technicalValue(value.literal,pointer+'/literal');else if(typeof value.literal!=='string')reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',pointer,'technical scalar literals must be strings');return;}
   if(technical)reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',pointer,'technical dictionaries cannot be computed');
   for(const child of value.concat)expression(child,columns,pointer+'/concat');
  };
  if(rule.op==='defaults'){
   if(tables.has(rule.as)||Object.keys(rule.values).some(key=>!technicalKeys.includes(key)))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/values','only distinct owned technical tables and closed value fields are supported');
   for(const [key,value] of Object.entries(rule.values)){if(key==='technical')technicalValue(value,at+'/values/technical');else if(typeof value!=='string')reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/values/'+key,'technical scalar strings required');}
   tables.set(rule.as,new Set(Object.keys(rule.values)));continue;
  }
  if(rule.op==='project'){
   const columns=tables.get(rule.from);
   if(!columns||tables.has(rule.as)||Object.keys(rule.fields).some(key=>!technicalKeys.includes(key)))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at,'only closed projections of owned technical tables are supported');
   for(const [key,value] of Object.entries(rule.fields))expression(value,columns!,at+'/fields/'+key,key==='technical');
   tables.set(rule.as,new Set(Object.keys(rule.fields)));continue;
  }
  if(rule.op!=='emit')reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at,'transformation is not qualified for this finite technical recipe');
  if(rule.op==='emit'){
   const allowed=fields[rule.role];if(!allowed||Object.keys(rule.fields).some(key=>!allowed.includes(key)))reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/fields','unsupported technical role/field for this recipe');
   if(rule.role==='application-operation'){
    operations++;
    if(rule.from!=='applications')reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/from','profile cannot substitute/filter authored exposures');
    same(rule.fields.id,{field:['id']},at+'/id');same(rule.fields.project_ref,{field:['source']},at+'/project_ref');same(rule.fields.selector,{field:['selector']},at+'/selector');
    same(rule.fields.route,{concat:[{literal:wire.route_prefix},{field:['id']}]},at+'/route');
    same(rule.fields.technical,{literal:{request_bytes:wire.request_bytes,timeout_ms:wire.timeout_ms}},at+'/technical');
    if(rule.fields.artifact_path)expression(rule.fields.artifact_path,new Set(['id','source','selector']),at+'/artifact_path');
   }else{
    if(!rule.fields.id||!rule.fields.artifact_path)reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/fields','required technical identity/artifact path fields missing');
    if(rule.role==='http-dispatch')dispatchers++;if(rule.role==='shared-http-port')shared++;
    const columns=tables.get(rule.from);if(!columns)reject('BUSINESS_RECIPE_PROFILE_AUTHORITY',at+'/from','technical emission must use its owned technical table');
    for(const [key,value] of Object.entries(rule.fields))expression(value,columns!,at+'/fields/'+key,key==='technical');
   }
  }
 }}
 const runtime=snapshot.packages.find(pkg=>pkg.data.schema_version==='craft.profile-package/v3-candidate')!;
 const sharedExpected=runtime.data.schema_version==='craft.profile-package/v3-candidate'&&runtime.data.application_runtime.transport==='shared'?1:0;
 if(operations!==1||dispatchers!==1||shared!==sharedExpected)reject('BUSINESS_RECIPE_PROFILE_AUTHORITY','/profiles','exactly the selected application/dispatcher/transport technical projections are required');
}

function moduleIdentity():string {
 const filename=fileURLToPath(import.meta.url);let cursor=path.parse(filename).root;const owners:string[]=[];
 for(const part of filename.slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,part);const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink())reject('BUSINESS_RECIPE_MODULE_STALE',filename,'owning module cannot be substituted through symlinks');owners.push(`${stat.dev}:${stat.ino}`);}
 const before=lstatSync(filename,{bigint:true});if(!before.isFile()||before.size>16777216n)reject('BUSINESS_RECIPE_MODULE_STALE',filename,'bounded regular owning module required');
 const fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);const parts:Buffer[]=[];let bytes=0;
 try{
  const opened=fstatSync(fd,{bigint:true});if(opened.dev!==before.dev||opened.ino!==before.ino||!opened.isFile())reject('BUSINESS_RECIPE_MODULE_STALE',filename,'owning module changed during capture');
  for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>16777216)reject('BUSINESS_RECIPE_MODULE_STALE',filename,'module exceeds capture budget');parts.push(buffer.subarray(0,count));}
  const after=fstatSync(fd,{bigint:true});if(after.size!==before.size||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)reject('BUSINESS_RECIPE_MODULE_STALE',filename,'module changed while reading');
 }finally{closeSync(fd);}
 const after=lstatSync(filename,{bigint:true});if(after.dev!==before.dev||after.ino!==before.ino||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)reject('BUSINESS_RECIPE_MODULE_STALE',filename,'module path changed while reading');
 return dataDigest({owners,sha256:sha256(Buffer.concat(parts)),bytes,mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)});
}
// Bind the bytes actually loaded by this module instance; a later edit cannot bless new selections.
const executingModuleIdentity=moduleIdentity();
export function selectBusinessAuthoringRecipe(snapshot:BusinessAuthoringSnapshot,models:readonly BusinessRecipeModelInput[],requirements?:BusinessRecipeRequirements):BusinessRecipeSelection {
 assertBusinessAuthoringSnapshotCurrent(snapshot);
 const module=moduleIdentity(),captured=captureJson(models) as unknown as readonly BusinessRecipeModelInput[];
 if(module!==executingModuleIdentity)reject('BUSINESS_RECIPE_MODULE_STALE','/','reload the owning module after its bytes or physical identity change');
 if(!Array.isArray(captured)||captured.length!==snapshot.project.models.length||!captured.length||captured.length>BUSINESS_AUTHORING_LIMITS.models)fail('/models','complete bounded selected model set required');
 unique(captured.map(model=>{closed(model,['model_id','source','spec','formal','behavior'],'/models');if(typeof model.model_id!=='string')fail('/models/model_id','model identity required');return model.model_id;}),'/models');
 const expectedRequirements:BusinessRecipeRequirements={recipe_ref:BUSINESS_AUTHORING_RECIPE,logic_profile:BUSINESS_AUTHORING_LOGIC,target:'node-typescript',effects:'none',required_guarantees:[...BUSINESS_RECIPE_GUARANTEES]};
 const required=captureJson(requirements===undefined?expectedRequirements:requirements) as unknown as BusinessRecipeRequirements;
 closed(required,['recipe_ref','logic_profile','target','effects','required_guarantees'],'/requirements');
 if(required.recipe_ref!==BUSINESS_AUTHORING_RECIPE||required.logic_profile!==BUSINESS_AUTHORING_LOGIC||required.target!=='node-typescript'||required.effects!=='none'||!Array.isArray(required.required_guarantees)||required.required_guarantees.some(value=>typeof value!=='string'||!(BUSINESS_RECIPE_GUARANTEES as readonly string[]).includes(value))||new Set(required.required_guarantees).size!==required.required_guarantees.length)reject('BUSINESS_RECIPE_UNSUPPORTED','/requirements','only the finite registered recipe/logic/target/effects/guarantees are supported');
 const owner=snapshot.packages.find(pkg=>pkg.data.schema_version==='craft.profile-package/v3-candidate');if(!owner||owner.data.schema_version!=='craft.profile-package/v3-candidate')reject('BUSINESS_RECIPE_UNSUPPORTED','/profiles','compatible authoring owner required');
 const declaration=owner.data.authoring;
 if(declaration.contract!==BUSINESS_AUTHORING_CONTRACT||declaration.recipe_ref!==required.recipe_ref||declaration.logic_profile!==required.logic_profile||declaration.target!==required.target||declaration.effects!==required.effects)reject('BUSINESS_RECIPE_UNSUPPORTED','/profiles','selected owner does not implement the required contract');
 checkTechnicalRules(snapshot,declaration.wire);
 const businessRows:{model_id:string;business_sha256:string}[]=[];let entries=0;
 for(const [index,input] of captured.entries()){
  const at='/models/'+index;closed(input.source,['path','sha256','bytes'],at+'/source');
  validateBusinessAuthoringContract<BusinessSpecData>('spec',input.spec);checkSource(snapshot,input,at);
  const expected=expectedNormalization(input.spec,at+'/spec');same(input.formal,expected.formal,at+'/formal');same(input.behavior,expected.behavior,at+'/behavior');
  entries+=input.behavior.exposures.length;businessRows.push({model_id:input.model_id,business_sha256:expected.business});
 }
 if(entries>BUSINESS_AUTHORING_LIMITS.intents||entries>BUSINESS_AUTHORING_LIMITS.total_entries)reject('BUSINESS_RECIPE_UNSUPPORTED','/models','selected exposure entry budget exceeded');
 const sorted=[...captured].sort((a,b)=>compare(a.model_id,b.model_id));
 const result=captureJson({kind:'business-recipe-selection',recipe_ref:BUSINESS_AUTHORING_RECIPE,normalization_contract:BUSINESS_NORMALIZATION_CONTRACT,models:sorted,requirements:required,business_sha256:dataDigest(businessRows.sort((a,b)=>compare(a.model_id,b.model_id))),technical:{profile_id:owner.id,profile_version:owner.data.version,manifest_sha256:owner.manifest_sha256,asset_sha256:owner.asset_sha256,wire:declaration.wire,transport:owner.data.application_runtime.transport,required_guarantees:[...BUSINESS_RECIPE_GUARANTEES],lock_sha256:snapshot.lock.lock_sha256},authority_effect:'none'}) as unknown as BusinessRecipeSelection;
 registry.set(result,{snapshot,module,fingerprint:dataDigest(result)});assertBusinessRecipeSelectionCurrent(result);return result;
}
export function assertBusinessRecipeSelectionCurrent(selection:BusinessRecipeSelection):void {
 const state=registry.get(selection);if(!state)reject('BUSINESS_RECIPE_UNREGISTERED','/','only a Core-registered recipe selection is current; JSON DTOs are not handles');
 assertBusinessAuthoringSnapshotCurrent(state.snapshot);
 let current:string;try{current=moduleIdentity();}catch{return reject('BUSINESS_RECIPE_MODULE_STALE','/','owning recipe module is unavailable or changed');}
 if(current!==state.module||dataDigest(selection)!==state.fingerprint)reject('BUSINESS_RECIPE_MODULE_STALE','/','recipe module or normalized selection changed');
}

/** Original current v3 snapshot, available only through the genuine recipe registry. */
export function businessAuthoringRecipeSnapshot(selection:BusinessRecipeSelection):BusinessAuthoringSnapshot {
 assertBusinessRecipeSelectionCurrent(selection);return registry.get(selection)!.snapshot;
}

/** U03 independent direct recipe checking. These data checks do not mint runtime
 * selection, graph custody, native support or business acceptance.
 * Open Questions: actual source/native capture owner at J01/J02; graph join L02/G01. */
export const CORE_DIRECT_RECIPE_REQUIREMENTS_V2=Object.freeze({source_contract:BUSINESS_SPEC_V2,recipe_ref:BUSINESS_AUTHORING_RECIPE_V2,target:'node-typescript',effects:'none',entry_access:'public'} as const);
export interface CoreDirectRecipeDataV2 {
 readonly schema_version:'craft.core-direct-recipe-data/v2-candidate';readonly transfer:BusinessDirectSourceTransferV2;
 readonly executable_sha256:string;readonly assurance_sha256:string;
 readonly review:ReturnType<typeof projectBusinessReviewSubjectV2>;
 readonly roles:Readonly<{
  feature:string;selectors:Readonly<{entity:string;rule:string;operation:string;entry:string;input_mapping:string;output_mapping:string}>;
  typed_rule:Readonly<{schema_version:'domainspec.typed-rule/v1';ontology_rule:string;parameters:readonly Readonly<{name:string;type:Readonly<{kind:'named';selector:string}>}>[];expression:Readonly<{op:'eq';left:Readonly<{op:'path';root:string;properties:readonly [string]}>;right:Readonly<{op:'literal';type:'Bool';value:true}>}>}>;
  guard_parameter:string;guard_root:string;result_root:string;rejection:string;effects:readonly [];permission:Readonly<{kind:'public'}>;
 }>;
 readonly authority_effect:'none';
}
const directFailure=(code:string,at:string,message:string):never=>reject('BUSINESS_DIRECT_'+code,at,message);
const directSame=(a:unknown,b:unknown,at:string):void=>{if(dataDigest(a)!==dataDigest(b))directFailure('CORRESPONDENCE',at,'captured source and independently reconstructed data differ');};
function directClosed(value:unknown,keys:readonly string[],at:string):asserts value is Record<string,unknown> {
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==keys.length||keys.some(key=>!Object.hasOwn(value,key)))directFailure('SHAPE',at,'closed direct data fields required');
}
export function validateCoreDirectRecipeRequirementsV2(input:unknown=CORE_DIRECT_RECIPE_REQUIREMENTS_V2):typeof CORE_DIRECT_RECIPE_REQUIREMENTS_V2 {
 const value=captureJson(input);directClosed(value,Object.keys(CORE_DIRECT_RECIPE_REQUIREMENTS_V2),'/requirements');
 directSame(value,CORE_DIRECT_RECIPE_REQUIREMENTS_V2,'/requirements');return value as unknown as typeof CORE_DIRECT_RECIPE_REQUIREMENTS_V2;
}
/** Eligibility only. It does not resolve or authenticate a native asset/basis. */
export function validateCoreDirectNativeContractV2(input:Pick<U0ResolvedNativeBasis,'abi'|'descriptor'|'configuration'>):void {
 const data=captureJson(input) as unknown as Pick<U0ResolvedNativeBasis,'abi'|'descriptor'|'configuration'>;
 directClosed(data,['abi','descriptor','configuration'],'/native-contract');
 if(data.abi!==U0_NATIVE_ABI||data.descriptor!==U0_SUCCESSOR_DESCRIPTOR)directFailure('NATIVE_CONTRACT','/native-contract','unsupported finite descriptor/ABI');
 checkU0WireConfiguration(data.configuration);
}

type DirectFactQueue={lines:readonly string[];used:number};
type DirectExpectedBlock={kind:string;id:string;header:string;groups:Map<string,DirectFactQueue>;scenarios:Map<string,Map<string,DirectFactQueue>>};
/** Independently prove every physical source fact against its claimed AST. Queues
 * preserve ordered fields/lists/scenarios; interleaved independent clauses may reorder.
 * JSON.parse below decodes only one quoted prose string, never a source program. */
function checkDirectSourceFacts(spec:BusinessSpecDataV2,source:BusinessSourceCapture):void {
 directClosed(source,['path','text','sha256','bytes'],'/source');
 if(typeof source.path!=='string'||!source.path||source.path.length>4096||source.path.split('/').length>16||source.path.startsWith('/')||/[\\:\x00-\x1f\x7f]/.test(source.path)||source.path.split('/').some(part=>!part||part==='.'||part==='..'))directFailure('SOURCE','/source/path','portable original source path required');
 if(typeof source.text!=='string'||source.bytes!==Buffer.byteLength(source.text)||source.bytes>1048576||sha256(source.text)!==source.sha256)directFailure('SOURCE','/source','exact finite source bytes required');
 const lines=source.text.split('\n');if(lines.length>10000)directFailure('SOURCE_BUDGET','/source','line budget exceeded');
 const facts:{text:string;raw:string;line:number;column:number;depth:number}[]=[];
 for(const [i,line] of lines.entries()){
  const raw=i<lines.length-1?line.replace(/\r$/,''):line;
  if(/[\t\r\0]/.test(raw))directFailure('SOURCE','/source/line:'+String(i+1),'tabs, bare CR and NUL forbidden');
  if(!raw.trim()||raw.trimStart().startsWith('#'))continue;
  const spaces=raw.length-raw.trimStart().length;
  if(raw.length>4096||raw.slice(0,spaces)!==' '.repeat(spaces)||spaces%2||spaces>4)directFailure('SOURCE','/source/line:'+String(i+1),'bounded exact source indentation required');
  facts.push({text:raw.slice(spaces),raw,line:i+1,column:spaces+1,depth:spaces/2});
 }
 if(facts[0]?.text!==BUSINESS_SOURCE_V2_MARKER||facts[0]?.depth!==0)directFailure('SOURCE_VERSION','/source','original successor header required');
 if(spec.source_spans.length!==facts.length||spec.obligations.length!==facts.length)directFailure('SOURCE_COVERAGE','/source_spans','one original span/obligation per source fact');
 for(const [i,row] of facts.entries()){
  directSame(spec.source_spans[i],{selector:'line:'+row.line,source:source.path,line:row.line,column:row.column,text:row.raw,source_sha256:source.sha256},'/source_spans/'+i);
  directSame(spec.obligations[i],{selector:'line:'+row.line,kind:'clause',span_selector:'line:'+row.line},'/obligations/'+i);
 }
 const quoted=(text:string):string=>JSON.stringify(text);
 const queue=(groups:Map<string,DirectFactQueue>,key:string,values:readonly string[])=>groups.set(key,{lines:values,used:0});
 const blocks:DirectExpectedBlock[]=[];
 const block=(kind:string,id:string,rows:readonly string[],version?:string)=>{
  const value:DirectExpectedBlock={kind,id,header:kind+' '+id+(version===undefined?'':' version '+version)+':',groups:new Map(),scenarios:new Map()};
  for(const row of rows){const key=row.split(' ')[0]!,old=value.groups.get(key);if(old)value.groups.set(key,{lines:[...old.lines,row],used:0});else queue(value.groups,key,[row]);}
  blocks.push(value);return value;
 };
 for(const requirement of spec.requirements){
  const out=block('requirement',requirement.id,[`context ${quoted(requirement.context)}`,`meaning ${quoted(requirement.meaning)}`,
   ...(requirement.applies_when.length?requirement.applies_when.map(value=>'applies-when '+quoted(value)):['applies-when none']),
   ...(requirement.actors.length?requirement.actors.map(value=>'actor '+quoted(value)):['actors none']),...requirement.boundaries.map(value=>'does-not-mean '+quoted(value))]);
  for(const [kind,scenarios] of [['example',requirement.examples],['counterexample',requirement.counterexamples]] as const){
   queue(out.groups,kind,scenarios.map(value=>kind+' '+value.case_id+':'));
   for(const scenario of scenarios){const groups=new Map<string,DirectFactQueue>();for(const key of ['given','when','then','why'] as const)queue(groups,key,[key+' '+quoted(scenario[key])]);out.scenarios.set(kind+' '+scenario.case_id+':',groups);}
  }
 }
 for(const entity of spec.entities){const out=block('entity',entity.id,[`meaning ${quoted(entity.meaning)}`,'identity '+entity.identity]);queue(out.groups,'$field',entity.fields.map(field=>field.name+' '+field.type+' meaning '+quoted(field.meaning)));}
 for(const definition of spec.definitions)block('definition',definition.id,['requirement '+definition.requirement_ref,'input '+definition.input.name+' '+definition.input.type_ref,'meaning '+quoted(definition.meaning),'boolean-field '+definition.boolean_field.root+'.'+definition.boolean_field.path[0]]);
 for(const claim of spec.claims)block('formal-claim',claim.id,['requirement '+claim.requirement_ref,'supersedes none','profile '+claim.logic_profile,...claim.sorts.map(value=>'sort '+value.name+' interpreted-as '+value.type_ref),...claim.predicates.map(value=>'predicate '+value.name+'('+value.sort_refs[0]+') defined-by '+value.definition_ref),...claim.constants.map(value=>'constant '+value.name+': '+value.sort_ref),'proposition '+claim.proposition,'ceiling '+quoted(claim.ceiling),...claim.subject_refs.map(value=>'subject '+value)],claim.version);
 for(const rule of spec.rules)block('rule',rule.id,['requirement '+rule.requirement_ref,'meaning '+quoted(rule.meaning),'input '+rule.input.name+' '+rule.input.type_ref,'condition '+rule.condition.value.root+'.'+rule.condition.value.path[0]]);
 for(const operation of spec.operations){const guard=operation.guards[0]!,argument=guard.arguments[0]!;block('operation',operation.id,['meaning '+quoted(operation.meaning),'input '+operation.input.name+' '+operation.input.type_ref,'output '+operation.output_ref,'requires '+guard.rule_ref+'('+argument.parameter+': '+argument.value.root+')','returns '+operation.result.root,'on-rejection '+operation.on_rejection,'effects none']);}
 for(const entry of spec.entries)block('entry',entry.id,['invokes '+entry.operation_ref,'public-name '+entry.public_name,'permission public']);
 const byHeader=new Map(blocks.map(value=>[value.header,value])),seen=new Set<string>(),byKind=new Map<string,string[]>(),usedKind=new Map<string,number>();
 for(const value of blocks)byKind.set(value.kind,[...(byKind.get(value.kind)??[]),value.id]);
 let active:DirectExpectedBlock|undefined,scenario:Map<string,DirectFactQueue>|undefined,modelSeen=false,ownerSeen=false;
 const finish=(groups:Map<string,DirectFactQueue>|undefined,at:string)=>{for(const [key,value] of groups??[])if(value.used!==value.lines.length)directFailure('SOURCE_COVERAGE',at+'/'+key,'declared source facts were omitted or reordered');};
 const finishBlock=()=>{finish(scenario,'/scenario');scenario=undefined;if(active){finish(active.groups,'/'+active.header);for(const groups of active.scenarios.values())finish(groups,'/'+active.header+'/scenario');}active=undefined;};
 const consume=(groups:Map<string,DirectFactQueue>,key:string,text:string,line:number)=>{const value=groups.get(key);if(!value||value.lines[value.used]!==text)directFailure('SOURCE_CORRESPONDENCE','/source/line:'+line,'unexpected, duplicate or substituted source fact');value!.used++;};
 const prose=(text:string,line:number):string=>{try{const value:unknown=JSON.parse(text);if(typeof value==='string'&&value.trim())return JSON.stringify(value);}catch{}return directFailure('SOURCE','/source/line:'+line,'one nonempty quoted prose string required');};
 for(const [i,row] of facts.entries()){
  if(i===0)continue;
  if(row.depth===0){
   finishBlock();
   const model=/^business-model ([A-Za-z_][A-Za-z0-9_-]{0,127}) version (\S+) (.+)$/.exec(row.text);
   if(model){if(modelSeen||model[1]!==spec.identity.namespace||model[1]!==spec.identity.stable_id||model[2]!==spec.identity.version||prose(model[3]!,row.line)!==quoted(spec.identity.title))directFailure('SOURCE_CORRESPONDENCE','/identity','original model identity differs');modelSeen=true;continue;}
   const owner=/^owner (\S+)$/.exec(row.text);if(owner){if(ownerSeen||owner[1]!==spec.identity.owner)directFailure('SOURCE_CORRESPONDENCE','/identity/owner','original owner differs');ownerSeen=true;continue;}
   const value=byHeader.get(row.text);if(!value||seen.has(row.text))directFailure('SOURCE_CORRESPONDENCE','/source/line:'+row.line,'unknown or duplicate declaration');
   const n=usedKind.get(value!.kind)??0;if(byKind.get(value!.kind)?.[n]!==value!.id)directFailure('SOURCE_CORRESPONDENCE','/source/line:'+row.line,'authored declaration order differs');usedKind.set(value!.kind,n+1);seen.add(row.text);active=value;continue;
  }
  if(!active)directFailure('SOURCE','/source/line:'+row.line,'clause requires its containing declaration');
  if(row.depth===1){finish(scenario,'/scenario');scenario=undefined;const selected=active!.scenarios.get(row.text);if(selected){consume(active!.groups,row.text.split(' ')[0]!,row.text,row.line);scenario=selected;continue;}}
  if(row.depth===2){if(!scenario)directFailure('SOURCE','/source/line:'+row.line,'nested clause requires an explicit scenario');const match=/^(given|when|then|why) (.+)$/.exec(row.text);if(!match)directFailure('SOURCE','/source/line:'+row.line,'unsupported scenario clause');consume(scenario!,match![1]!,match![1]+' '+prose(match![2]!,row.line),row.line);continue;}
  let key=row.text.split(' ')[0]!,canonical=row.text;
  const field=active!.kind==='entity'?/^([a-z][a-z0-9]*(?:_[a-z0-9]+)*) (UInt64|Bool) meaning (.+)$/.exec(row.text):null;
  if(field){key='$field';canonical=field[1]+' '+field[2]+' meaning '+prose(field[3]!,row.line);}
  else if(['context','meaning','applies-when','actor','does-not-mean','ceiling'].includes(key)&&row.text!=='applies-when none')canonical=key+' '+prose(row.text.slice(key.length+1),row.line);
  consume(active!.groups,key,canonical,row.line);
 }
 finishBlock();if(!modelSeen||!ownerSeen||seen.size!==blocks.length)directFailure('SOURCE_COVERAGE','/source','complete explicit model/owner/declaration inventory required');
}

/** Independent finite optional FOL capture validation. No proof, native model or
 * executable predicate is obtained from this payload. Equality retains its sorts. */
function checkDirectAssuranceProposition(claim:BusinessClaimV2):void {
 const at='/claims/'+claim.id+'/proposition',tokens:string[]=[];
 for(let offset=0;offset<claim.proposition.length;){if(/\s/.test(claim.proposition[offset]!)){offset++;continue;}const match=/^(?:[A-Za-z_][A-Za-z0-9_.-]*|[():,=])/.exec(claim.proposition.slice(offset));if(!match)directFailure('ASSURANCE_SYNTAX',at,'unknown FOL token');tokens.push(match![0]);offset+=match![0].length;}
 let groups=0;for(const token of tokens){if(token==='('&&++groups>64)directFailure('ASSURANCE_BUDGET',at,'bounded grouping required');if(token===')')groups--;}
 if(tokens.length>10000||tokens.filter(token=>['not','implies','forall','exists'].includes(token)).length>64)directFailure('ASSURANCE_BUDGET',at,'bounded finite FOL required');
 if(tokens.some(token=>token==='forall'||token==='exists'))directFailure('ASSURANCE_UNSUPPORTED',at,'quantifier capture requires a later source capability');
 const predicates=new Map(claim.predicates.map(value=>[value.name,value])),constants=new Map(claim.constants.map(value=>[value.name,value])),used=new Set<string>();let position=0,visits=0;
 const peek=()=>tokens[position],take=(expected?:string)=>{const token=tokens[position++];if(!token||expected!==undefined&&token!==expected)directFailure('ASSURANCE_SYNTAX',at,'malformed finite FOL');return token!;};
 const term=():string=>{const name=take(),constant=constants.get(name);if(!constant)directFailure('ASSURANCE_REFERENCE',at,'undeclared finite term '+name);used.add(name);return constant!.sort_ref;};
 const unary=(depth:number):void=>{if(++visits>10000||depth>256)directFailure('ASSURANCE_BUDGET',at,'bounded FOL recursion required');if(peek()==='not'){take();unary(depth+1);return;}if(peek()==='('){take();iff(depth+1);take(')');return;}
  const predicate=predicates.get(peek()??'');if(predicate){take();used.add(predicate.name);take('(');const sort=term();take(')');if(predicate.sort_refs.length!==1||predicate.sort_refs[0]!==sort)directFailure('ASSURANCE_TYPE',at,'predicate argument sort differs');return;}
  const left=term();take('=');if(term()!==left)directFailure('ASSURANCE_TYPE',at,'equality sorts differ');
 };
 const and=(depth:number)=>{unary(depth);while(peek()==='and'){take();unary(depth);}};
 const or=(depth:number)=>{and(depth);while(peek()==='or'){take();and(depth);}};
 const implies=(depth:number):void=>{or(depth);if(peek()==='implies'){take();implies(depth+1);}};
 const iff=(depth:number):void=>{implies(depth);if(peek()==='iff'){take();implies(depth+1);if(peek()==='iff')directFailure('ASSURANCE_SYNTAX',at,'chained iff requires grouping');}};
 iff(0);if(position!==tokens.length)directFailure('ASSURANCE_SYNTAX',at,'trailing FOL tokens');for(const name of [...predicates.keys(),...constants.keys()])if(!used.has(name))directFailure('ASSURANCE_REFERENCE',at,'unused declared FOL symbol');
}
function checkDirectSemanticReferences(spec:BusinessSpecDataV2):void {
 const declarations=[...spec.requirements,...spec.entities,...spec.definitions,...spec.claims,...spec.rules,...spec.operations,...spec.entries];unique(declarations.map(value=>value.id),'/direct/ids');
 for(const value of declarations)validName(value.id,'/direct/ids');
 for(const value of [spec.identity.namespace,spec.identity.stable_id])validName(value,'/direct/identity');
 const requirements=new Map(spec.requirements.map(value=>[value.id,value])),entity=spec.entities[0]!,rule=spec.rules[0]!,operation=spec.operations[0]!,entry=spec.entries[0]!;
 unique(entity.fields.map(value=>value.name),'/direct/fields');for(const field of entity.fields){validName(field.name,'/direct/fields');nonempty(field.meaning,'/direct/fields');}
 if(entity.fields.filter(field=>field.type==='UInt64').length!==1||entity.fields.filter(field=>field.type==='Bool').length!==1||entity.fields.find(field=>field.name===entity.identity)?.type!=='UInt64')directFailure('TYPE','/entity','one exact UInt64 identity and one Bool required');
 if(rule.input.type_ref!==entity.id||rule.condition.value.root!==rule.input.name||entity.fields.find(field=>field.name===rule.condition.value.path[0])?.type!=='Bool'||!requirements.has(rule.requirement_ref))directFailure('CONDITION','/rule','explicit well-typed Bool field and requirement required');
 const guard=operation.guards[0]!,argument=guard.arguments[0]!;
 if(operation.input.type_ref!==entity.id||operation.output_ref!==entity.id||guard.rule_ref!==rule.id||argument.parameter!==rule.input.name||argument.value.root!==operation.input.name||argument.value.path.length||operation.result.root!==operation.input.name||operation.result.path.length||operation.effects.length)directFailure('OPERATION','/operation','one explicit typed guard, identity result, authored rejection and no effects required');
 if(!/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/.test(operation.on_rejection))directFailure('SOURCE','/operation/on-rejection','an authored rejection identifier is required');
 if(entry.operation_ref!==operation.id||entry.permission.kind!=='public')directFailure('ENTRY','/entry','explicit public logical entry must select the authored Operation');
 for(const value of [rule.input.name,operation.input.name,operation.on_rejection])validName(value,'/direct/parameters');
 for(const value of [entity.meaning,rule.meaning,operation.meaning])nonempty(value,'/direct/meaning');
 validName(entry.public_name,'/entry/public-name');
 for(const requirement of spec.requirements){const cases=[...requirement.examples,...requirement.counterexamples];unique(cases.map(value=>value.case_id),'/requirements/cases');for(const scenario of cases)validName(scenario.case_id,'/requirements/cases');for(const text of [requirement.context,requirement.meaning,...requirement.applies_when,...requirement.actors,...requirement.boundaries,...cases.flatMap(value=>[value.given,value.when,value.then,value.why])])nonempty(text,'/requirements');}
 const definitions=new Map(spec.definitions.map(value=>[value.id,value]));
 for(const definition of spec.definitions){if(!requirements.has(definition.requirement_ref)||definition.input.type_ref!==entity.id||definition.boolean_field.root!==definition.input.name||entity.fields.find(field=>field.name===definition.boolean_field.path[0])?.type!=='Bool')directFailure('ASSURANCE_REFERENCE','/definitions','typed optional definition must retain its declared Entity/requirement/Bool field');validName(definition.input.name,'/definitions');nonempty(definition.meaning,'/definitions');}
 for(const claim of spec.claims){
  if(!requirements.has(claim.requirement_ref)||claim.supersedes!==null||/\s/.test(claim.version))directFailure('ASSURANCE_REFERENCE','/claims','supported explicit optional requirement/version required');
  unique([...claim.sorts,...claim.predicates,...claim.constants].map(value=>value.name),'/claims/signature');
  for(const item of [...claim.sorts,...claim.predicates,...claim.constants]){validName(item.name,'/claims/signature');if(['forall','exists','not','and','or','implies','iff'].includes(item.name))directFailure('ASSURANCE_REFERENCE','/claims/signature','reserved FOL signature name');}
  const sorts=new Map(claim.sorts.map(value=>[value.name,value]));
  for(const sort of claim.sorts)if(sort.type_ref!==entity.id)directFailure('ASSURANCE_TYPE','/claims/sorts','Entity interpretation differs');
  for(const constant of claim.constants)if(!sorts.has(constant.sort_ref))directFailure('ASSURANCE_REFERENCE','/claims/constants','sort is undeclared');
  for(const predicate of claim.predicates)if(sorts.get(predicate.sort_refs[0]!)?.type_ref!==definitions.get(predicate.definition_ref)?.input.type_ref||!sorts.has(predicate.sort_refs[0]!)||!definitions.has(predicate.definition_ref))directFailure('ASSURANCE_TYPE','/claims/predicates','explicit unary predicate/sort/definition correspondence required');
  for(const ref of claim.subject_refs)if(ref!==rule.id&&ref!==operation.id)directFailure('ASSURANCE_REFERENCE','/claims/subjects','optional subject must name the authored Rule or Operation');
  nonempty(claim.ceiling,'/claims/ceiling');checkDirectAssuranceProposition(claim);
 }
}
function directRoleProjection(spec:BusinessSpecDataV2):CoreDirectRecipeDataV2['roles'] {
 const feature=normalized(spec.identity.namespace),entity=spec.entities[0]!,rule=spec.rules[0]!,operation=spec.operations[0]!,entry=spec.entries[0]!;
 const local=(value:string):string=>{const result=normalized(value);if(!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(result))directFailure('SYMBOL_DOMAIN','/roles','source identity is outside the selected role domain');return result;};
 local(spec.identity.namespace);const entityId=local(entity.id),ruleId=local(rule.id),operationId=local(operation.id),entryId=local(entry.id);
 const selectors={entity:feature+':'+entityId,rule:feature+':'+ruleId,operation:feature+':'+operationId,entry:feature+':'+entryId,input_mapping:feature+':craftrequest-'+entryId+'-input',output_mapping:feature+':craftrequest-'+entryId+'-output'};
 const ontology='BUSINESS-'+feature.toUpperCase()+'-'+entityId.toUpperCase(),property=ontology+'#'+rule.condition.value.path[0];
 const roleIds=[entityId,ruleId,operationId,entryId,'craftrequest-'+entryId+'-input','craftrequest-'+entryId+'-output'];
 const publicOntology='BUSINESS-'+feature.toUpperCase()+'-'+entryId.toUpperCase()+'-PAYLOAD';
 if([...Object.values(selectors),...roleIds.map(value=>'BUSINESS-'+feature.toUpperCase()+'-'+value.toUpperCase()),publicOntology,...entity.fields.flatMap(field=>[ontology+'#'+field.name,publicOntology+'#'+field.name])].some(value=>value.length>256))directFailure('SYMBOL_DOMAIN','/roles','derived identity is outside the selected Core role bounds');
 return {feature,selectors,typed_rule:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'BUSINESS-'+feature.toUpperCase()+'-'+ruleId.toUpperCase(),parameters:[{name:rule.input.name,type:{kind:'named',selector:selectors.entity}}],expression:{op:'eq',left:{op:'path',root:rule.input.name,properties:[property]},right:{op:'literal',type:'Bool',value:true}}},guard_parameter:operation.guards[0]!.arguments[0]!.parameter,guard_root:operation.guards[0]!.arguments[0]!.value.root,result_root:operation.result.root,rejection:operation.on_rejection,effects:[],permission:entry.permission};
}
export function checkCoreDirectBusinessRecipeV2(input:unknown,requirements:unknown=CORE_DIRECT_RECIPE_REQUIREMENTS_V2):CoreDirectRecipeDataV2 {
 validateCoreDirectRecipeRequirementsV2(requirements);const raw=captureJson(input);directClosed(raw,['source','spec','executable','assurance'],'/transfer');
 const spec=validateBusinessAuthoringContractV2('spec',raw.spec),source=raw.source as unknown as BusinessSourceCapture;
 checkDirectSourceFacts(spec,source);checkDirectSemanticReferences(spec);
 const executable=projectDirectExecutableV2(spec),assurance=projectOptionalAssuranceV2(spec);
 directSame(raw.executable,executable,'/executable');directSame(raw.assurance,assurance,'/assurance');
 return captureJson({schema_version:'craft.core-direct-recipe-data/v2-candidate',transfer:{source,spec,executable,assurance},executable_sha256:dataDigest(executable),assurance_sha256:dataDigest(assurance),review:projectBusinessReviewSubjectV2(spec),roles:directRoleProjection(spec),authority_effect:'none'}) as unknown as CoreDirectRecipeDataV2;
}

/** Trusted construction capability, supplied by the actual J01/J02 SDK capture
 * owner. It is never read from business/profile JSON. Each factory's registry is
 * private: a selection from another component/owner instance cannot transfer. */
export interface BusinessCoreRecipeCaptureOwnerV2 {
 assertCurrent(basis:U0ResolvedNativeBasis):void;
 capture(modelId:string,basis:U0ResolvedNativeBasis):Readonly<{source:BusinessSourceCapture;capture:BusinessCaptureIdentityV2}>;
}
export function createBusinessCoreRecipeOwnerV2(captureOwner:BusinessCoreRecipeCaptureOwnerV2):BusinessCoreRecipeOwnerV2 {
 const originalAssert=captureOwner.assertCurrent,originalCapture=captureOwner.capture;
 const owned=new WeakMap<object,{basis:U0ResolvedNativeBasis;fingerprint:string;disposed:boolean}>();
 const currentOwner=()=>{if(captureOwner.assertCurrent!==originalAssert||captureOwner.capture!==originalCapture||moduleIdentity()!==executingModuleIdentity)directFailure('OWNER_STALE','/selection','owning implementation/capture capability changed');};
 const captured=(model:BusinessSelectedModelV2,basis:U0ResolvedNativeBasis):void=>{
  const original=captureOwner.capture(model.model_id,basis);directSame(model.source,original.source,'/selection/source');directSame(model.capture,original.capture,'/selection/capture');
  const checked=checkCoreDirectBusinessRecipeV2({source:original.source,spec:model.spec,executable:projectDirectExecutableV2(model.spec),assurance:projectOptionalAssuranceV2(model.spec)});
  if(model.model_id!==model.spec.identity.namespace||model.executable_sha256!==checked.executable_sha256||model.assurance_sha256!==checked.assurance_sha256)directFailure('CORRESPONDENCE','/selection/model','exact model/meaning identities required');
  const {capture_sha256,...manifest}=model.capture;const identity=captureBusinessIdentityV2(manifest);
  if(identity.capture_sha256!==capture_sha256)directFailure('CORRESPONDENCE','/selection/capture','capture identity differs');
  directSame(identity.source,{path:original.source.path,sha256:original.source.sha256,bytes:original.source.bytes},'/selection/capture/source');
 };
 const assertCurrent=(selection:BusinessRecipeSelectionV2):void=>{
  const state=selection&&typeof selection==='object'?owned.get(selection):undefined;if(!state)directFailure('UNREGISTERED','/selection','original selection from this exact owner instance required');
  if(state!.disposed)directFailure('DISPOSED','/selection','selection disposed');currentOwner();captureOwner.assertCurrent(state!.basis);
  if(dataDigest(selection)!==state!.fingerprint)directFailure('OWNER_STALE','/selection','selection data changed');for(const model of selection.models)captured(model,state!.basis);
 };
 return Object.freeze({
  select(models:readonly BusinessSelectedModelV2[],basis:U0ResolvedNativeBasis):BusinessRecipeSelectionV2 {
   currentOwner();captureOwner.assertCurrent(basis);validateCoreDirectNativeContractV2({abi:basis.abi,descriptor:basis.descriptor,configuration:basis.configuration});
   const values=captureJson(models) as unknown as readonly BusinessSelectedModelV2[];
   // One public pure route is the selected U0 cell. Whole applications/services are EC work.
   if(!Array.isArray(values)||values.length!==1)directFailure('UNSUPPORTED','/models','one selected U0 business model required');
   for(const raw of values){directClosed(raw,['model_id','source','spec','executable_sha256','assurance_sha256','capture'],'/models');const model=raw as unknown as BusinessSelectedModelV2;const spec=validateBusinessAuthoringContractV2('spec',model.spec);if(typeof model.model_id!=='string'||model.model_id!==spec.identity.namespace||typeof model.executable_sha256!=='string'||!/^[a-f0-9]{64}$/.test(model.executable_sha256)||typeof model.assurance_sha256!=='string'||!/^[a-f0-9]{64}$/.test(model.assurance_sha256))directFailure('SHAPE','/models','exact typed model/meaning identities required');captured(model,basis);}
   const reference={kind:'native-basis-reference-v2',descriptor:U0_SUCCESSOR_DESCRIPTOR,abi:U0_NATIVE_ABI,sdk_sha256:basis.sdk_sha256,basis_sha256:basis.basis_sha256,configuration_sha256:dataDigest(basis.configuration)};
   const body={kind:'business-recipe-selection-v2',models:values,native_basis:reference,authority_effect:'none'};
   const result=captureJson({...body,selection_sha256:dataDigest(body)}) as unknown as BusinessRecipeSelectionV2;
   captureOwner.assertCurrent(basis);owned.set(result,{basis,fingerprint:dataDigest(result),disposed:false});assertCurrent(result);return result;
  },assertCurrent,
  dispose(selection:BusinessRecipeSelectionV2):void {const state=selection&&typeof selection==='object'?owned.get(selection):undefined;if(!state)directFailure('UNREGISTERED','/selection','original selection required');if(state!.disposed)directFailure('DISPOSED','/selection','selection already disposed');state!.disposed=true;},
 });
}
