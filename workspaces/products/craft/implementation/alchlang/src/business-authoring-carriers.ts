import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {BUSINESS_AUTHORING_CONTRACT,BUSINESS_AUTHORING_RECIPE} from './business-authoring-protocol.js';
import type {BusinessDerivationOrigin,BusinessEntity,BusinessLoweringLedger,BusinessOperation,BusinessRequirement,BusinessReviewSubject,BusinessScenario,BusinessSemanticPreview,BusinessSourceSpan,LegacyMeaningSubject,ReviewDefinition} from './business-authoring-protocol.js';
import type {BusinessFormalData} from './business-authoring-normalization-protocol.js';
import type {BusinessBehavior} from './business-authoring-behavior.js';
import {assertBusinessBehaviorCurrent} from './business-authoring-behavior.js';
import type {BusinessRecipeSelectionSurface,PreparedBusinessRecipeSelection} from './business-authoring-profile-selection.js';
import {assertPreparedBusinessRecipeSelectionCurrent} from './business-authoring-profile-selection.js';
import {businessCanonical,businessHash,businessReject,businessSymbol,freezeBusinessData} from './business-authoring-model.js';
import type {AcceptedBusinessReviewDecision} from './business-authoring-review.js';
import {assertAcceptedBusinessReviewDecisionCurrent} from './business-authoring-review.js';
import type {BusinessRequestPreparationSurface,InsertedBusinessRequestMappings} from './business-authoring-request.js';
import {assertInsertedBusinessRequestMappingsCurrent,insertBusinessRequestMappings} from './business-authoring-request.js';
import {normalizeDirectBusinessV2,assertDirectBusinessNormalizationV2Current,type DirectBusinessNormalizationV2} from './business-authoring-semantics.js';
import {lowerDirectBusinessBehaviorV2,assertDirectBusinessBehaviorV2Current,type DirectBusinessBehaviorV2} from './business-authoring-behavior.js';
import type {ResolvedBusinessSpecV2} from './business-authoring-protocol-v2.js';
import type {LoweredDirectBusinessV2,BusinessDirectLoweringOwnerV2} from './business-authoring-stages-v2.js';

/** Direct source carrier; no legacy FormalClaim or accepted-input object is synthesized.
 * Open Questions: L01/Core join at G01, native/installed qualification afterward. */
const directCarriers=new WeakMap<object,{normalization:DirectBusinessNormalizationV2;behavior:DirectBusinessBehaviorV2;fingerprint:string}>();
export function lowerDirectBusinessV2(business:ResolvedBusinessSpecV2):LoweredDirectBusinessV2 {
 const normalization=normalizeDirectBusinessV2(business),behavior=lowerDirectBusinessBehaviorV2(normalization);
 const result=freezeBusinessData<LoweredDirectBusinessV2>({kind:'lowered-direct-business-v2',business,executable:normalization.executable,assurance:normalization.assurance,review:normalization.review,authority_effect:'none'},business.source.path);
 directCarriers.set(result,{normalization,behavior,fingerprint:businessHash(businessCanonical(result))});assertLoweredDirectBusinessV2Current(result);return result;
}
export function assertLoweredDirectBusinessV2Current(value:LoweredDirectBusinessV2):void {
 const state=value&&typeof value==='object'?directCarriers.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original direct business carrier required');
 assertDirectBusinessNormalizationV2Current(state.normalization);assertDirectBusinessBehaviorV2Current(state.behavior);
 if(value.business!==state.normalization.business||businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.normalization.capture.path,1,1,'direct carrier source/meaning changed');
}
export const BUSINESS_DIRECT_LOWERING_OWNER_V2:BusinessDirectLoweringOwnerV2=Object.freeze({lower:lowerDirectBusinessV2,assertCurrent:assertLoweredDirectBusinessV2Current});

// Pure B06.1 preview. Open questions: B04 decisions and B06.2 accepted materialization remain separate.
export interface BusinessPreviewSelection extends BusinessRecipeSelectionSurface {
 readonly recipe_ref:typeof BUSINESS_AUTHORING_RECIPE;
 readonly technical:Readonly<{profile_id:string;manifest_sha256:string;required_guarantees:readonly string[];lock_sha256:string}>;
}
export interface BusinessMeaningDraft {
 readonly schema_version:'domainspec-v2.business-meaning/v1-candidate';readonly meaning_id:string;readonly version:string;readonly owner:string;
 readonly domain_context:string;readonly rule:string;readonly applies_when:readonly string[];readonly actors:readonly string[];
 readonly inputs:readonly string[];readonly outcomes:readonly string[];readonly examples:readonly BusinessScenario[];readonly counterexamples:readonly BusinessScenario[];
 readonly boundaries:readonly string[];readonly claim_ceiling:string;readonly authority_effect:'none';
}
export interface BusinessDeclarationDraft {
 readonly ontology:string;readonly meaning:string;readonly properties?:Readonly<Record<string,Readonly<{ontology:string;meaning:string}>>>;
 readonly failure_continuation?:string;
}
export interface BusinessClaimDraft {readonly claim_id:string;readonly version:string;readonly supersedes:string|null;readonly meaning_ref:string;readonly definition_refs:readonly string[]}
export interface BusinessOperationBehaviorDraft {
 readonly input_name:string;readonly guards:readonly Readonly<{rule:string;arguments:Readonly<Record<string,Readonly<{root:'request';path:readonly []}>>>}>[];
 readonly result:Readonly<{root:'request';path:readonly []}>;
}
export interface BusinessSemanticProjections {
 readonly declarations:Readonly<Record<string,BusinessDeclarationDraft>>;readonly meaning_drafts:Readonly<Record<string,BusinessMeaningDraft>>;
 readonly definitions:readonly ReviewDefinition[];readonly claim_drafts:Readonly<Record<string,BusinessClaimDraft>>;
 readonly rule_meanings:BusinessFormalData['rule_meanings'];readonly operation_behaviors:Readonly<Record<string,BusinessOperationBehaviorDraft>>;
 readonly required_guarantees:readonly string[];readonly value_invariant_bindings:Readonly<Record<string,never>>;
}
export interface DetailedBusinessSemanticPreview<Selection extends BusinessPreviewSelection=BusinessPreviewSelection> extends BusinessSemanticPreview {
 readonly prepared:PreparedBusinessRecipeSelection<Selection>;readonly model_id:string;readonly projections:BusinessSemanticProjections;
 readonly ledger:BusinessLoweringLedger;readonly preview_sha256:string;
}
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const byId=<T extends {id:string}>(rows:readonly T[]):T[]=>[...rows].sort((a,b)=>compare(a.id,b.id));
const fields=(entity:BusinessEntity)=>[...entity.fields].sort((a,b)=>compare(a.name,b.name));
const pointer=(value:string)=>value.replaceAll('~','~0').replaceAll('/','~1');
const adapterContract=Object.freeze({contract:'craft.business-semantic-preview/2-candidate',identity:'business-projection-api/epoch-2',input:'KIND ID input PARAM: ENTITY {FIELD: SCALAR, ...}.',outcome:'Operation OP returns PARAM: ENTITY; on-rejection CONTINUATION; effects none.',legacy_root:'request',definition_pointers:['#/inputs','#/rule']});
const adapter:BusinessDerivationOrigin=Object.freeze({kind:'semantic-adapter',source:adapterContract.contract,selector:'identity-and-structural-rendering/epoch-2',sha256:businessHash(businessCanonical(adapterContract))});
const owners=new WeakMap<object,{prepared:PreparedBusinessRecipeSelection<BusinessPreviewSelection>;behavior:BusinessBehavior;fingerprint:string}>();

export function previewBusinessSemantics<Selection extends BusinessPreviewSelection>(prepared:PreparedBusinessRecipeSelection<Selection>,modelId:string):DetailedBusinessSemanticPreview<Selection> {
 assertPreparedBusinessRecipeSelectionCurrent(prepared);
 const behavior=prepared.behaviors.find(value=>value.data.model_id===modelId);
 if(!behavior)businessReject('BUSINESS_REFERENCE','business.alch',1,1,'preview model must select a genuine prepared business behavior');
 assertBusinessBehaviorCurrent(behavior);
 const business=behavior.business,spec=business.data,source=business.source.path;
 const reject=(code:string,message:string,selector?:string):never=>{
  const span=selector?spec.source_spans.find(span=>span.selector===selector||span.selector.startsWith(selector+'/line:')):undefined;
  return businessReject(code,source,span?.line??1,span?.column??1,message);
 };
 const symbol=(key:string):string=>{const result=businessSymbol(key);if(!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(result))reject('BUSINESS_UNSUPPORTED','unsupported backend identity '+key);return result;};
 const feature=symbol(spec.identity.namespace),header='model:'+spec.identity.namespace;
 // Check distinct namespaces independently of local declaration IDs before deriving any public identity.
 const modelSymbols=prepared.behaviors.map(value=>symbol(value.data.model_id));
 if(new Set(modelSymbols).size!==modelSymbols.length)reject('BUSINESS_AMBIGUOUS','model namespaces collide after backend normalization');
 // Flat legacy ontology/definition IDs must also be unique across composed namespaces.
 // Distinct feature/local pairs can collapse to the same hyphenated identifier.
 const identitySpaces={ontology:new Map<string,string>(),definition:new Map<string,string>(),property:new Map<string,string>()};
 for(const model of prepared.behaviors){
  const modelSpec=model.business.data,modelFeature=symbol(modelSpec.identity.namespace);
  const reserve=(space:keyof typeof identitySpaces,value:string,kind:string,id:string):void=>{
   const previous=identitySpaces[space].get(value),owner=model.data.model_id+':'+kind+':'+id;
   if(previous!==undefined){const span=modelSpec.source_spans.find(span=>span.selector.startsWith(kind+':'+id+'/line:'));businessReject('BUSINESS_AMBIGUOUS',model.business.source.path,span?.line??1,span?.column??1,`derived ${space} identity ${value} collides between ${previous} and ${owner}`);}
   identitySpaces[space].set(value,owner);
  };
  for(const [kind,values] of [['entity',modelSpec.entities],['rule',modelSpec.rules],['operation',modelSpec.operations]] as const)for(const declaration of values){
   const id=`BUSINESS-${modelFeature.toUpperCase()}-${symbol(declaration.id).toUpperCase()}`;reserve('ontology',id,kind,declaration.id);
   if(kind==='entity')for(const field of modelSpec.entities.find(entity=>entity.id===declaration.id)!.fields)reserve('property',id+'#'+symbol(field.name).replaceAll('-','_'),kind,declaration.id);
  }
  for(const definition of modelSpec.definitions)reserve('definition',`DEF-${modelFeature.toUpperCase()}-${symbol(definition.id).toUpperCase()}`,'definition',definition.id);
 }
 const all=[...spec.requirements,...spec.entities,...spec.definitions,...spec.claims,...spec.rules,...spec.operations,...spec.capabilities];
 if(new Set(all.map(value=>symbol(value.id))).size!==all.length)reject('BUSINESS_AMBIGUOUS','declaration identities collide after backend normalization');
 const ontology=(key:string)=>`BUSINESS-${feature.toUpperCase()}-${symbol(key).toUpperCase()}`;
 const definitionId=(key:string)=>`DEF-${feature.toUpperCase()}-${symbol(key).toUpperCase()}`;
 const entities=new Map(spec.entities.map(entity=>[entity.id,entity])),requirements=new Map(spec.requirements.map(requirement=>[requirement.id,requirement]));
 const declarations:Record<string,BusinessDeclarationDraft>=Object.create(null),meanings:Record<string,BusinessMeaningDraft>=Object.create(null),claimDrafts:Record<string,BusinessClaimDraft>=Object.create(null),operationBehaviors:Record<string,BusinessOperationBehaviorDraft>=Object.create(null);
 const assignments=new Map<string,readonly BusinessDerivationOrigin[]>();
 const origins=(...selectors:string[]):BusinessDerivationOrigin[]=>spec.source_spans.filter(span=>selectors.some(selector=>span.selector===selector||span.selector.startsWith(selector+'/line:'))).map(span=>({kind:'business',source:span.source,selector:span.selector,sha256:span.source_sha256}));
 const fullOrigins=(prefix:string):BusinessDerivationOrigin[]=>spec.source_spans.filter(span=>span.selector.startsWith(prefix+'/')).map(span=>({kind:'business',source:span.source,selector:span.selector,sha256:span.source_sha256}));
 const assign=(target:string,value:readonly BusinessDerivationOrigin[])=>assignments.set(target,value);
 const derived=(...selectors:string[])=>[...origins(...selectors),adapter];
 const bounded=(value:string):string=>{if(value.length>4096)reject('BUSINESS_SOURCE_BUDGET','derived legacy text exceeds 4096 characters');return value;};
 const inputText=(kind:'Rule'|'Operation',id:string,name:string,type:string):string=>bounded(`${kind} ${id} input ${name}: ${type} {${fields(entities.get(type)!).map(field=>`${field.name}: ${field.type}`).join(', ')}}.`);
 const outcomeText=(operation:BusinessOperation):string=>bounded(`Operation ${operation.id} returns ${operation.result.root}: ${operation.output_ref}; on-rejection ${operation.on_rejection}; effects none.`);
 for(const entity of byId(spec.entities)){
  const base='/projections/declarations/'+pointer(entity.id),selector='entity:'+entity.id;
  const properties:Record<string,{ontology:string;meaning:string}>=Object.create(null);
  for(const field of fields(entity)){
   const fieldKey=businessSymbol(field.name).replaceAll('-','_');symbol(field.name);
   properties[field.name]={ontology:ontology(entity.id)+'#'+fieldKey,meaning:field.meaning};
   assign(base+'/properties/'+pointer(field.name)+'/ontology',derived(header,selector,selector+'/field:'+field.name));
   assign(base+'/properties/'+pointer(field.name)+'/meaning',origins(selector+'/field:'+field.name));
  }
  declarations[entity.id]={ontology:ontology(entity.id),meaning:entity.meaning,properties};
  assign(base,derived(header,selector));assign(base+'/meaning',origins(selector+'/meaning'));
 }
 for(const rule of byId(spec.rules)){
  const base='/projections/declarations/'+pointer(rule.id),selector='rule:'+rule.id;
  declarations[rule.id]={ontology:ontology(rule.id),meaning:rule.meaning};assign(base,derived(header,selector));assign(base+'/meaning',origins(selector+'/meaning'));
 }
 for(const operation of byId(spec.operations)){
  const base='/projections/declarations/'+pointer(operation.id),selector='operation:'+operation.id;
  declarations[operation.id]={ontology:ontology(operation.id),meaning:operation.meaning,failure_continuation:operation.on_rejection};assign(base,derived(header,selector));assign(base+'/meaning',origins(selector+'/meaning'));assign(base+'/failure_continuation',origins(selector+'/on-rejection'));
  const guards=operation.guards.map(guard=>({rule:guard.rule_ref,arguments:{[guard.arguments[0]!.parameter]:{root:'request' as const,path:[] as []}}}));
  operationBehaviors[operation.id]={input_name:operation.input.name,guards,result:{root:'request',path:[]}};
  const behaviorBase='/projections/operation_behaviors/'+pointer(operation.id);assign(behaviorBase,derived(selector,selector+'/input',selector+'/requires',selector+'/returns'));
  assign(behaviorBase+'/input_name',origins(selector+'/input'));
  assign(behaviorBase+'/result',derived(selector+'/returns'));assign(behaviorBase+'/guards',derived(selector+'/input',selector+'/requires'));
 }
 const normalizedDefinitions=behavior.formal.data.definitions;
 const definitions:ReviewDefinition[]=normalizedDefinitions.map<ReviewDefinition>(definition=>{
  const authored=spec.definitions.find(value=>value.id===definition.definition_ref)!,requirement=requirements.get(authored.requirement_ref)!;
  if(new Set(requirement.boundaries).size!==requirement.boundaries.length)reject('BUSINESS_AMBIGUOUS','legacy definition boundaries must remain unique without rewriting authored prose','requirement:'+requirement.id+'/does-not-mean');
  return {definition_id:definitionId(authored.id),term:authored.id,definition_kind:'predicate',formal:definition.formal,plain_language:authored.meaning,domain_context:requirement.context,depends_on:[],business_fact_refs:['#/inputs'],interpretation_refs:['#/rule'],source_concept_refs:[`business:${feature}:definition:${symbol(authored.id)}`],forbidden_collapses:requirement.boundaries};
 }).sort((a,b)=>compare(a.definition_id,b.definition_id));
 for(const [index,definition] of definitions.entries()){
  const authored=spec.definitions.find(value=>definitionId(value.id)===definition.definition_id)!,selector='definition:'+authored.id,requirement='requirement:'+authored.requirement_ref;
  const base='/projections/definitions/'+index;
  assign(base,derived(header,selector));assign(base+'/term',origins(selector));assign(base+'/plain_language',origins(selector+'/meaning'));assign(base+'/domain_context',origins(requirement+'/context'));
  assign(base+'/formal',[...fullOrigins(selector),...fullOrigins('entity:'+authored.input.type_ref),...spec.claims.flatMap(claim=>claim.predicates.filter(predicate=>predicate.definition_ref===authored.id).flatMap(predicate=>origins('formal-claim:'+claim.id+'/predicate:'+predicate.name))),adapter]);
  assign(base+'/forbidden_collapses',origins(...spec.source_spans.filter(span=>span.selector.startsWith(requirement+'/does-not-mean/')).map(span=>span.selector)));
 }
 const legacySubjects:LegacyMeaningSubject[]=[];
 for(const claim of byId(spec.claims)){
  const key=symbol(claim.id),requirement=requirements.get(claim.requirement_ref)!,linkedRules=byId(spec.rules.filter(rule=>rule.claim_ref===claim.id)),ruleIds=new Set(linkedRules.map(rule=>rule.id));
  const linkedOperations=byId(spec.operations.filter(operation=>operation.guards.some(guard=>ruleIds.has(guard.rule_ref))));
  const inputs=[...linkedRules.map(rule=>inputText('Rule',rule.id,rule.input.name,rule.input.type_ref)),...linkedOperations.map(operation=>inputText('Operation',operation.id,operation.input.name,operation.input.type_ref))];
  const draft:BusinessMeaningDraft={schema_version:'domainspec-v2.business-meaning/v1-candidate',meaning_id:`Meaning:${feature}:${key}`,version:claim.version,owner:spec.identity.owner,domain_context:requirement.context,rule:requirement.meaning,applies_when:requirement.applies_when,actors:requirement.actors,inputs,outcomes:linkedOperations.map(outcomeText),examples:requirement.examples,counterexamples:requirement.counterexamples,boundaries:requirement.boundaries,claim_ceiling:claim.ceiling,authority_effect:'none'};
  // Preserve the existing formal-claim owner's exact set constraints before computing a subject.
  for(const property of ['applies_when','actors','inputs','outcomes','boundaries'] as const){
   const seen=new Set<string>();
   for(const [index,value] of draft[property].entries()){
    if(seen.has(value)){
     const clause=property==='applies_when'?'applies-when':property==='actors'?'actor':property==='boundaries'?'does-not-mean':undefined;
     const span=clause?spec.source_spans.filter(span=>span.selector.startsWith('requirement:'+requirement.id+'/'+clause+'/line:'))[index]:undefined;
     reject('BUSINESS_AMBIGUOUS',`legacy BusinessMeaning ${property} requires unique exact strings; duplicate authored facts cannot be deduplicated`,span?.selector??'formal-claim:'+claim.id);
    }
    seen.add(value);
   }
  }
  meanings[claim.id]=draft;
  const definition_refs=[...new Set(claim.predicates.map(predicate=>definitionId(predicate.definition_ref)))].sort(compare);
  claimDrafts[claim.id]={claim_id:`FormalClaim:${feature}:${key}`,version:claim.version,supersedes:claim.supersedes,meaning_ref:draft.meaning_id,definition_refs};
  // This prospective subject is the only use of accepted status. The payload never leaves this scope.
  legacySubjects.push({meaning_id:draft.meaning_id,version:draft.version,canonicalization:'domainspec-json-keysort-excluding-acceptance-v1',digest_algorithm:'sha256',digest:businessHash(businessCanonical({...draft,status:'accepted'}))});
  const base='/projections/meaning_drafts/'+pointer(claim.id),claimSelector='formal-claim:'+claim.id,req='requirement:'+requirement.id;
  assign(base,[adapter]);assign(base+'/meaning_id',derived(header,claimSelector));assign(base+'/version',origins(claimSelector));assign(base+'/owner',origins('model/owner'));assign(base+'/domain_context',origins(req+'/context'));assign(base+'/rule',origins(req+'/meaning'));assign(base+'/claim_ceiling',origins(claimSelector+'/ceiling'));
  for(const [property,clause] of [['applies_when','applies-when'],['actors','actor'],['boundaries','does-not-mean']] as const)assign(base+'/'+property,fullOrigins(req).filter(origin=>origin.selector.startsWith(req+'/'+clause+'/')||property==='actors'&&origin.selector.startsWith(req+'/actors/')));
  for(const [property,kind] of [['examples','example'],['counterexamples','counterexample']] as const)for(const [caseIndex,scenario] of requirement[property].entries())assign(base+'/'+property+'/'+caseIndex,fullOrigins(req+'/'+kind+':'+scenario.case_id));
  let inputIndex=0;
  for(const rule of linkedRules)assign(base+'/inputs/'+inputIndex++,[...origins('rule:'+rule.id+'/input',claimSelector+'/requirement'),...fullOrigins('entity:'+rule.input.type_ref),adapter]);
  for(const operation of linkedOperations)assign(base+'/inputs/'+inputIndex++,[...origins('operation:'+operation.id+'/input'),...fullOrigins('entity:'+operation.input.type_ref),adapter]);
  for(const [outcomeIndex,operation] of linkedOperations.entries())assign(base+'/outcomes/'+outcomeIndex,derived('operation:'+operation.id+'/returns','operation:'+operation.id+'/output','operation:'+operation.id+'/on-rejection','operation:'+operation.id+'/effects'));
  assign('/projections/claim_drafts/'+pointer(claim.id),[...fullOrigins(claimSelector),...origins(header),adapter]);
 }
 legacySubjects.sort((a,b)=>compare(a.meaning_id,b.meaning_id));
 for(const rule of spec.rules){
  const claim=spec.claims.find(value=>value.id===rule.claim_ref)!;
  for(const sort of claim.sorts)assign('/projections/rule_meanings/'+pointer(rule.id)+'/sorts/'+pointer(sort.name),origins('formal-claim:'+claim.id+'/sort:'+sort.name,'rule:'+rule.id+'/claim'));
  for(const constant of claim.constants)assign('/projections/rule_meanings/'+pointer(rule.id)+'/constants/'+pointer(constant.name),origins('formal-claim:'+claim.id+'/constant:'+constant.name,'rule:'+rule.id+'/bind:'+constant.name));
  for(const predicate of claim.predicates){const definition=spec.definitions.find(value=>value.id===predicate.definition_ref)!;assign('/projections/rule_meanings/'+pointer(rule.id)+'/predicates/'+pointer(predicate.name),origins('formal-claim:'+claim.id+'/predicate:'+predicate.name,'definition:'+definition.id+'/boolean-field'));}
 }
 const projections:BusinessSemanticProjections={declarations,meaning_drafts:meanings,definitions,claim_drafts:claimDrafts,rule_meanings:behavior.formal.data.rule_meanings,operation_behaviors:operationBehaviors,required_guarantees:[...prepared.selection.technical.required_guarantees],value_invariant_bindings:Object.create(null)};
 assign('/projections/required_guarantees',[{kind:'profile',source:'profile:'+prepared.selection.technical.profile_id,selector:'/authoring/recipe_ref',sha256:prepared.selection.technical.manifest_sha256},adapter]);
 assign('/projections/value_invariant_bindings',[adapter]);
 const review:BusinessReviewSubject={schema_version:'craft.business-review/v1-candidate',normalization_contract:BUSINESS_AUTHORING_CONTRACT,model_identity:spec.identity,
  declarations:byId(spec.entities).map(entity=>({...entity,fields:fields(entity)})),definitions,
  claims:byId(spec.claims).map(claim=>({...claim,sorts:[...claim.sorts].sort((a,b)=>compare(a.name,b.name)),predicates:[...claim.predicates].sort((a,b)=>compare(a.name,b.name)),constants:[...claim.constants].sort((a,b)=>compare(a.name,b.name))})),
  interpretations:byId(spec.rules).map(rule=>({rule_ref:rule.id,...behavior.formal.data.rule_meanings[rule.id]!})),behaviors:byId(spec.operations),exposures:byId(spec.capabilities),requirements:byId(spec.requirements),legacy_meaning_subjects:legacySubjects};
 assign('/review',[adapter]);assign('/review/model_identity',origins(header,'model/owner'));
 for(const [index,entity] of review.declarations.entries())assign('/review/declarations/'+index,fullOrigins('entity:'+entity.id));
 for(const [index,definition] of review.definitions.entries()){
  const projectionPrefix='/projections/definitions/'+index,reviewPrefix='/review/definitions/'+index;
  for(const [target,origin] of [...assignments.entries()])if(target===projectionPrefix||target.startsWith(projectionPrefix+'/'))assign(reviewPrefix+target.slice(projectionPrefix.length),origin);
 }
 for(const [index,claim] of review.claims.entries())assign('/review/claims/'+index,fullOrigins('formal-claim:'+claim.id));
 for(const [index,rule] of byId(spec.rules).entries()){
  const base='/review/interpretations/'+index,projectionPrefix='/projections/rule_meanings/'+pointer(rule.id);
  assign(base,[...fullOrigins('rule:'+rule.id),...fullOrigins('formal-claim:'+rule.claim_ref),adapter]);
  for(const [target,origin] of [...assignments.entries()])if(target.startsWith(projectionPrefix+'/'))assign(base+target.slice(projectionPrefix.length),origin);
 }
 for(const [index,operation] of review.behaviors.entries())assign('/review/behaviors/'+index,fullOrigins('operation:'+operation.id));
 for(const [index,exposure] of review.exposures.entries())assign('/review/exposures/'+index,fullOrigins('capability:'+exposure.id));
 for(const [index,requirement] of review.requirements.entries())assign('/review/requirements/'+index,fullOrigins('requirement:'+requirement.id));
 for(const [index,subject] of legacySubjects.entries()){
  const claim=spec.claims.find(value=>meanings[value.id]!.meaning_id===subject.meaning_id)!;
  const draftPrefix='/projections/meaning_drafts/'+pointer(claim.id);
  assign('/review/legacy_meaning_subjects/'+index,[...fullOrigins('formal-claim:'+claim.id),...[...assignments.entries()].filter(([target])=>target===draftPrefix||target.startsWith(draftPrefix+'/')).flatMap(([,origin])=>[...origin]),adapter]);
 }
 // Reference already projected subtrees when a rendered/hash field depends on many source facts.
 // These are real logical preview targets, whose own leaves carry original source provenance.
 const intermediate=(selector:string,value:unknown):BusinessDerivationOrigin=>({kind:'semantic-adapter',source:'preview.json',selector,sha256:businessHash(businessCanonical(value))});
 const rows=(prefix:string,clause:string)=>spec.source_spans.filter(span=>span.selector.startsWith(prefix+'/'+clause+'/line:')||clause==='actor'&&span.selector.startsWith(prefix+'/actors/line:'));
 const exactRows=(base:string,values:readonly unknown[],spans:readonly BusinessSourceSpan[])=>{
  assign(base,spans.length===1?origins(spans[0]!.selector):[adapter]);for(const [index] of values.entries())assign(base+'/'+index,origins(spans[index]!.selector));
 };
 for(const [index,entity] of review.declarations.entries()){
  const base='/review/declarations/'+index,selector='entity:'+entity.id;
  assign(base,origins(selector));assign(base+'/meaning',origins(selector+'/meaning'));assign(base+'/identity',origins(selector+'/identity'));
  for(const [fieldIndex,field] of entity.fields.entries())assign(base+'/fields/'+fieldIndex,origins(selector+'/field:'+field.name));
 }
 for(const [index,claim] of review.claims.entries()){
  const base='/review/claims/'+index,selector='formal-claim:'+claim.id;
  assign(base,origins(selector));
  for(const [property,clause] of [['requirement_ref','requirement'],['supersedes','supersedes'],['logic_profile','profile'],['proposition','proposition'],['ceiling','ceiling']] as const)assign(base+'/'+property,origins(selector+'/'+clause));
  for(const [property,clause] of [['sorts','sort'],['predicates','predicate'],['constants','constant']] as const)for(const [itemIndex,item] of claim[property].entries())assign(base+'/'+property+'/'+itemIndex,origins(selector+'/'+clause+':'+item.name));
 }
 for(const [index,rule] of byId(spec.rules).entries())assign('/review/interpretations/'+index,derived('rule:'+rule.id));
 for(const [index,operation] of review.behaviors.entries()){
  const base='/review/behaviors/'+index,selector='operation:'+operation.id;assign(base,origins(selector));
  for(const [property,clause] of [['meaning','meaning'],['input','input'],['output_ref','output'],['guards','requires'],['result','returns'],['on_rejection','on-rejection'],['effects','effects']] as const)assign(base+'/'+property,origins(selector+'/'+clause));
 }
 for(const [index,exposure] of review.exposures.entries()){
  const base='/review/exposures/'+index,selector='capability:'+exposure.id;assign(base,origins(selector));
  for(const [property,clause] of [['operation_ref','invokes'],['public_name','public-name'],['audience','audience']] as const)assign(base+'/'+property,origins(selector+'/'+clause));
 }
 const requirementOrigins=(base:string,requirement:BusinessRequirement)=>{
  const selector='requirement:'+requirement.id;assign(base,origins(selector));assign(base+'/context',origins(selector+'/context'));assign(base+'/meaning',origins(selector+'/meaning'));
  exactRows(base+'/applies_when',requirement.applies_when,rows(selector,'applies-when'));
  exactRows(base+'/actors',requirement.actors,rows(selector,'actor'));
  exactRows(base+'/boundaries',requirement.boundaries,rows(selector,'does-not-mean'));
  for(const [property,kind] of [['examples','example'],['counterexamples','counterexample']] as const)for(const [caseIndex,scenario] of requirement[property].entries()){
   const caseBase=base+'/'+property+'/'+caseIndex,caseSelector=selector+'/'+kind+':'+scenario.case_id;assign(caseBase,origins(caseSelector));
   for(const clause of ['given','when','then','why'])assign(caseBase+'/'+clause,origins(caseSelector+'/'+clause));
  }
 };
 for(const [index,requirement] of review.requirements.entries())requirementOrigins('/review/requirements/'+index,requirement);
 for(const [index,definition] of definitions.entries()){
  const authored=spec.definitions.find(value=>definitionId(value.id)===definition.definition_id)!,entity=entities.get(authored.input.type_ref)!,normalized=normalizedDefinitions.find(value=>value.definition_ref===authored.id)!,requirement=requirements.get(authored.requirement_ref)!;
  const selector='definition:'+authored.id,entitySelector='entity:'+entity.id,fieldSelector=entitySelector+'/field:'+normalized.primitive.field;
  for(const base of ['/projections/definitions/'+index,'/review/definitions/'+index]){
   assign(base,derived(header,selector));assign(base+'/formal',derived(selector,selector+'/input',selector+'/boolean-field',fieldSelector));
   assign(base+'/formal/expression',[...derived(selector+'/boolean-field',fieldSelector),intermediate('/review/claims',review.claims)]);
   assign(base+'/formal/notation/0/meaning',origins(entitySelector+'/meaning'));assign(base+'/formal/notation/1/meaning',origins(fieldSelector));
   exactRows(base+'/forbidden_collapses',definition.forbidden_collapses,rows('requirement:'+requirement.id,'does-not-mean'));
  }
 }
 for(const claim of spec.claims){
  const base='/projections/meaning_drafts/'+pointer(claim.id),claimBase='/projections/claim_drafts/'+pointer(claim.id),requirement=requirements.get(claim.requirement_ref)!,selector='formal-claim:'+claim.id;
  for(const [property,clause] of [['applies_when','applies-when'],['actors','actor'],['boundaries','does-not-mean']] as const)exactRows(base+'/'+property,requirement[property],rows('requirement:'+requirement.id,clause));
  const linkedRules=byId(spec.rules.filter(rule=>rule.claim_ref===claim.id)),linkedOperations=byId(spec.operations.filter(operation=>operation.guards.some(guard=>linkedRules.some(rule=>rule.id===guard.rule_ref))));let inputIndex=0;
  for(const [kind,values] of [['rule',linkedRules],['operation',linkedOperations]] as const)for(const value of values){
   const entityIndex=review.declarations.findIndex(entity=>entity.id===value.input.type_ref);
   assign(base+'/inputs/'+inputIndex++,[...origins(kind+':'+value.id+'/input'),intermediate('/review/declarations/'+entityIndex,review.declarations[entityIndex]),adapter]);
  }
  assign(claimBase,derived(header,selector));assign(claimBase+'/version',origins(selector));assign(claimBase+'/supersedes',origins(selector+'/supersedes'));
  const claimIndex=review.claims.findIndex(value=>value.id===claim.id);assign(claimBase+'/definition_refs',[...derived(header),intermediate('/review/claims/'+claimIndex,review.claims[claimIndex])]);
 }
 for(const [index,subject] of legacySubjects.entries()){
  const claim=spec.claims.find(value=>meanings[value.id]!.meaning_id===subject.meaning_id)!;
  assign('/review/legacy_meaning_subjects/'+index,[...derived(header,'formal-claim:'+claim.id),intermediate('/projections/meaning_drafts/'+pointer(claim.id),meanings[claim.id])]);
 }
 const entries:BusinessLoweringLedger['entries'][number][]=[];
 const inheritedOrigins=(target:string):readonly BusinessDerivationOrigin[]=>{
  let at=target;for(;;){const found=assignments.get(at);if(found)return found;const last=at.lastIndexOf('/');if(last<0)break;at=at.slice(0,last);}return [adapter];
 };
 const walk=(value:unknown,target:string):void=>{
  if(value&&typeof value==='object'&&Object.keys(value).length){for(const key of Object.keys(value))walk((value as Record<string,unknown>)[key],target+'/'+pointer(key));return;}
  if(typeof value==='string'&&value.length>4096)reject('BUSINESS_SOURCE_BUDGET','derived legacy/review field exceeds 4096 characters');
  const actualOrigins=inheritedOrigins(target),unique=new Map(actualOrigins.map(origin=>[businessCanonical(origin),origin]));
  if(unique.size>16)reject('BUSINESS_SOURCE_BUDGET','derived field exceeds the closed ledger origin budget: '+target);
  if(entries.length>=10000)reject('BUSINESS_SOURCE_BUDGET','preview exceeds the closed ledger entry budget');
  if(!unique.size)reject('BUSINESS_REFERENCE','derived field has no exact source or adapter origin: '+target);
  entries.push({id:'preview.json#'+target,origins:[...unique.values()].sort((a,b)=>compare(businessCanonical(a),businessCanonical(b))),target:{artifact:'preview.json',pointer:target}});
 };
 walk({review,projections},'');entries.sort((a,b)=>compare(a.id,b.id));
 const ledger:BusinessLoweringLedger={schema_version:'craft.business-lowering/v1-candidate',recipe_ref:prepared.selection.recipe_ref,business_sha256:business.business_sha256,lock_sha256:prepared.selection.technical.lock_sha256,entries,authority_effect:'none'};
 const stable={model_id:modelId,review,legacy_meaning_subjects:legacySubjects,projections,ledger};
 const result=freezeBusinessData<DetailedBusinessSemanticPreview<Selection>>({kind:'business-semantic-preview',business,prepared,...stable,preview_sha256:businessHash(businessCanonical(stable))},source);
 owners.set(result,{prepared,behavior,fingerprint:businessHash(businessCanonical(result))});assertBusinessSemanticPreviewCurrent(result);return result;
}
export function assertBusinessSemanticPreviewCurrent(value:DetailedBusinessSemanticPreview):void {
 const state=value&&typeof value==='object'?owners.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered original business semantic preview required');
 assertPreparedBusinessRecipeSelectionCurrent(state.prepared);assertBusinessBehaviorCurrent(state.behavior);
 if(value.prepared!==state.prepared||value.business!==state.behavior.business||value.model_id!==state.behavior.data.model_id||businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.behavior.business.source.path,1,1,'semantic preview or producer correspondence changed');
}

// B06.2 derives the existing accepted carrier only from the registered review owner.
// Open questions: business-materialization-api.md; callable realization remains B07.2.
export interface BusinessMaterializationRequestSurface<Selection extends BusinessPreviewSelection=BusinessPreviewSelection> extends BusinessRequestPreparationSurface<Selection> {
 readonly models:readonly Readonly<{model_id:string;source_fragment:string;mappings:readonly Readonly<{mapping_id:string;source_fragment:string;declaration_binding:Readonly<{ontology:string;meaning:string}>}>[];declaration_bindings:Readonly<Record<string,Readonly<{ontology:string;meaning:string}>>>}>[];
 readonly ledger:BusinessLoweringLedger;
}
export interface BusinessAcceptedClaim {
 readonly claim_id:string;readonly version:string;readonly supersedes:string|null;
 readonly business_meaning:BusinessMeaningDraft&Readonly<{status:'accepted'}>;
 readonly owner_acceptance:Readonly<{schema_version:'domainspec-v2.business-acceptance-decision/v1-candidate';decision_id:string;owner:string;outcome:'accepted';subject:LegacyMeaningSubject;authority_effect:'none'}>;
 readonly definitions:readonly (ReviewDefinition&Readonly<{status:'accepted'}>)[];readonly definition_refs:readonly string[];
}
export interface BusinessApplicationSemantics {
 readonly schema_version:'craft.business-application/v1-candidate';readonly owner:string;
 readonly declarations:Readonly<Record<string,BusinessDeclarationDraft>>;readonly claim_meanings:Readonly<Record<string,BusinessAcceptedClaim>>;
 readonly rule_meanings:BusinessFormalData['rule_meanings'];readonly operation_behaviors:Readonly<Record<string,BusinessOperationBehaviorDraft>>;
 readonly required_guarantees:readonly string[];readonly value_invariant_bindings:Readonly<Record<string,never>>;
}
/** Trusted public Core SDK. Neither a profile nor a serialized input supplies this owner. */
export interface BusinessMaterializationEngine<Requests=BusinessMaterializationRequestSurface> {
 assertBusinessAuthoringRequestsCurrent(requests:Requests):void;
 validateBusinessApplication(data:unknown):unknown;
}
export interface MaterializedBusinessApplication<Accepted extends AcceptedBusinessReviewDecision=AcceptedBusinessReviewDecision,Requests extends BusinessMaterializationRequestSurface=BusinessMaterializationRequestSurface> {
 readonly kind:'materialized-business-application';readonly accepted:Accepted;readonly requests:Requests;
 readonly inserted:InsertedBusinessRequestMappings<Requests['selection'],Requests>;readonly model_id:string;
 readonly compatibility:Readonly<{model_id:string;source:string;semantics:BusinessApplicationSemantics}>;
 readonly application_source:string;
 /** Exact UTF-8 SHA-256 of compatibility.source; inserted.source_sha256 hashes application_source. */
 readonly source_sha256:string;readonly semantics_text:string;readonly semantics_sha256:string;
 readonly ledger:BusinessLoweringLedger;readonly materialization_sha256:string;readonly authority_effect:'none';
}
const materializationPath=fileURLToPath(import.meta.url);
function materializationImplementation():string {
 const fail=():never=>materializationReject('bounded original regular materialization implementation and ancestor custody required');
 try{
  const ancestors=():string[]=>{
   let cursor=path.parse(materializationPath).root;const identities:string[]=[];
   const check=(directory:boolean):void=>{const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink()||(directory?!stat.isDirectory():!stat.isFile()))fail();identities.push(`${stat.dev}:${stat.ino}:${stat.mode}`);};
   check(true);const parts=materializationPath.slice(cursor.length).split(path.sep).filter(Boolean);
   for(const [index,part] of parts.entries()){cursor=path.join(cursor,part);check(index<parts.length-1);}
   return identities;
  };
  const originalAncestors=ancestors(),before=lstatSync(materializationPath,{bigint:true});
  if(!before.isFile()||before.isSymbolicLink()||before.size>16777216n)fail();
  const fd=openSync(materializationPath,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),chunks:Buffer[]=[];let bytes=0;
  const same=(value:BigIntStats):boolean=>value.isFile()&&value.dev===before.dev&&value.ino===before.ino&&value.mode===before.mode&&value.size===before.size&&value.mtimeNs===before.mtimeNs&&value.ctimeNs===before.ctimeNs;
  try{
   if(!same(fstatSync(fd,{bigint:true})))fail();
   for(;;){const chunk=Buffer.alloc(65536),count=readSync(fd,chunk,0,chunk.length,null);if(!count)break;bytes+=count;if(bytes>16777216)fail();chunks.push(chunk.subarray(0,count));}
   if(!same(fstatSync(fd,{bigint:true})))fail();
  }finally{closeSync(fd);}
  if(BigInt(bytes)!==before.size||!same(lstatSync(materializationPath,{bigint:true}))||businessCanonical(ancestors())!==businessCanonical(originalAncestors))fail();
  return businessHash(businessCanonical({ancestors:originalAncestors,sha256:businessHash(Buffer.concat(chunks)),size:String(before.size),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)}));
 }catch(error){if(error instanceof Error&&error.message.startsWith('BUSINESS_MATERIALIZATION'))throw error;return fail();}
}
const originalMaterializationImplementation=materializationImplementation();
type MaterializationOwner={accepted:AcceptedBusinessReviewDecision;requests:BusinessMaterializationRequestSurface;inserted:InsertedBusinessRequestMappings;assertRequests:(requests:BusinessMaterializationRequestSurface)=>void;fingerprint:string};
const materializations=new WeakMap<object,MaterializationOwner>();
function materializationReject(message:string):never {return businessReject('BUSINESS_MATERIALIZATION','business.alch',1,1,message);}
function assertMaterializationImplementation():void {if(materializationImplementation()!==originalMaterializationImplementation)materializationReject('accepted materialization implementation changed');}
const equivalent=(a:unknown,b:unknown)=>businessCanonical(a)===businessCanonical(b);

/** Deterministic generated syntax; every formal/signature item remains explicit. */
function materializationSource(preview:DetailedBusinessSemanticPreview):string {
 const review=preview.review,identity=review.model_identity;
 const lines=[`domain ${identity.namespace} ${JSON.stringify(identity.title)}`,'profile application-v1',`owner ${identity.owner}`];
 for(const claim of byId(review.claims))lines.push(`formal-claim ${claim.id}:`,'  profile fol-core/1-candidate',
  ...[...claim.sorts].sort((a,b)=>compare(a.name,b.name)).map(value=>`  sort ${value.name}`),
  ...[...claim.predicates].sort((a,b)=>compare(a.name,b.name)).map(value=>`  predicate ${value.name}(${value.sort_refs.join(',')})`),
  ...[...claim.constants].sort((a,b)=>compare(a.name,b.name)).map(value=>`  constant ${value.name}: ${value.sort_ref}`),
  `  proposition ${claim.proposition}`,`  ceiling ${JSON.stringify(claim.ceiling)}`);
 const spec=preview.business.data;
 for(const rule of byId(spec.rules))lines.push(`rule ${rule.id}:`,`  claim ${rule.claim_ref}`);
 for(const entity of byId(review.declarations))lines.push(`entity ${entity.id}:`,`  identity ${entity.identity}`,...fields(entity).map(field=>`  ${field.name} ${field.type}`));
 for(const operation of byId(review.behaviors))lines.push(`operation ${operation.id}:`,`  input ${operation.input.type_ref}`,`  output ${operation.output_ref}`,`  requires ${operation.guards.map(guard=>guard.rule_ref).join(', ')}`);
 return lines.join('\n')+'\n';
}

export function materializeAcceptedBusinessApplication<Accepted extends AcceptedBusinessReviewDecision,Requests extends BusinessMaterializationRequestSurface>(
 accepted:Accepted,requests:Requests,coreSdk:BusinessMaterializationEngine<Requests>,
):MaterializedBusinessApplication<Accepted,Requests> {
 assertAcceptedBusinessReviewDecisionCurrent(accepted);assertMaterializationImplementation();
 const assertRequests=coreSdk.assertBusinessAuthoringRequestsCurrent.bind(coreSdk);assertRequests(requests);
 const preview=accepted.prepared.preview,prepared=preview.prepared,modelId=preview.model_id,projection=preview.projections,decision=accepted.decision.capture.decision;
 if(requests.selection!==prepared.selection||decision.outcome!=='accepted'||decision.owner!==preview.review.model_identity.owner)materializationReject('materialization requires the same original selection and exact accepted owner scope');
 const requestIndex=requests.models.findIndex(model=>model.model_id===modelId),request=requests.models[requestIndex];
 if(!request)materializationReject('accepted model has no original request preparation');
 const approved=accepted.accepted.definition_closure,approvedIds=new Set(approved.definition_ids),definitions=new Map(projection.definitions.map(definition=>[definition.definition_id,definition]));
 const selectedBodies=[...approved.definition_ids].sort(compare).map(id=>{const definition=definitions.get(id);if(!definition||!preview.review.definitions.some(value=>value.definition_id===id&&equivalent(value,definition)))materializationReject('accepted definition closure differs from the genuine reviewed complete body');return definition!;});
 if(approvedIds.size!==approved.definition_ids.length||approved.digest_algorithm!=='sha256'||businessHash(businessCanonical(selectedBodies))!==approved.digest)materializationReject('accepted complete definition closure digest differs');
 const declarations:Record<string,BusinessDeclarationDraft>=Object.create(null),claims:Record<string,BusinessAcceptedClaim>=Object.create(null);
 for(const id of Object.keys(projection.declarations).sort(compare))declarations[id]=projection.declarations[id]!;
 if(!equivalent(Object.keys(request.declaration_bindings).sort(compare),request.mappings.map(mapping=>mapping.mapping_id).sort(compare)))materializationReject('request declaration bindings must correspond exactly to original Mapping identities');
 for(const mapping of request.mappings){
  if(Object.hasOwn(declarations,mapping.mapping_id)||!equivalent(mapping.declaration_binding,request.declaration_bindings[mapping.mapping_id]))materializationReject('Mapping declaration metadata collides or differs from the original request owner');
  declarations[mapping.mapping_id]=request.declaration_bindings[mapping.mapping_id]!;
 }
 const allSelected=new Set<string>();
 for(const id of Object.keys(projection.claim_drafts).sort(compare)){
  const draft=projection.meaning_drafts[id]!,claim=projection.claim_drafts[id]!,meaning={...draft,status:'accepted' as const};
  const subjects=accepted.accepted.legacy_meaning_subjects.filter(value=>value.meaning_id===draft.meaning_id&&value.version===draft.version),subject=subjects[0];
  if(subjects.length!==1||!subject||subject.canonicalization!=='domainspec-json-keysort-excluding-acceptance-v1'||subject.digest_algorithm!=='sha256'||subject.digest!==businessHash(businessCanonical(meaning)))materializationReject('accepted legacy subject differs from the exact prospective meaning');
  const closure=new Set<string>(),active=new Set<string>();
  const visit=(reference:string,depth=0):void=>{
   if(depth>64)materializationReject('definition dependency depth exceeds the accepted closure budget');
   const matches=projection.definitions.filter(value=>value.definition_id===reference||value.term===reference),definition=matches[0];
   if(matches.length!==1||!definition||!approvedIds.has(definition.definition_id))materializationReject('claim definition is absent or ambiguous in the accepted complete closure');
   if(active.has(definition.definition_id))materializationReject('cyclic definition dependency');if(closure.has(definition.definition_id))return;
   active.add(definition.definition_id);for(const dependency of definition.depends_on)visit(dependency,depth+1);active.delete(definition.definition_id);closure.add(definition.definition_id);allSelected.add(definition.definition_id);
  };
  for(const reference of claim.definition_refs)visit(reference);
  const refs=[...closure].sort(compare);
  claims[id]={claim_id:claim.claim_id,version:claim.version,supersedes:claim.supersedes,business_meaning:meaning,
   owner_acceptance:{schema_version:'domainspec-v2.business-acceptance-decision/v1-candidate',decision_id:decision.decision_id,owner:decision.owner,outcome:'accepted',subject,authority_effect:'none'},
   definitions:refs.map(reference=>({...definitions.get(reference)!,status:'accepted' as const})),definition_refs:refs};
 }
 if(!equivalent([...allSelected].sort(compare),[...approvedIds].sort(compare)))materializationReject('accepted global definition closure is not exactly the union of per-claim closures');
 const semantics:BusinessApplicationSemantics={schema_version:'craft.business-application/v1-candidate',owner:preview.review.model_identity.owner,declarations,claim_meanings:claims,rule_meanings:projection.rule_meanings,operation_behaviors:projection.operation_behaviors,required_guarantees:projection.required_guarantees,value_invariant_bindings:projection.value_invariant_bindings};
 const validated=coreSdk.validateBusinessApplication(semantics);
 if(!equivalent(validated,semantics))materializationReject('legacy semantic validator changed the generated carrier');
 const inserted=insertBusinessRequestMappings(prepared as PreparedBusinessRecipeSelection<Requests['selection']>,requests,modelId,materializationSource(preview),coreSdk);
 const applicationSource=inserted.source,sourceLines=applicationSource.split('\n');
 if(sourceLines.filter(line=>line==='profile application-v1').length!==1)materializationReject('generated source must contain exactly one explicit application profile');
 const source=sourceLines.filter(line=>line!=='profile application-v1').join('\n'),semanticsText=JSON.stringify(semantics,null,2)+'\n';
 const compatibility={model_id:modelId,source,semantics},stable={model_id:modelId,compatibility,application_source:applicationSource,source_sha256:businessHash(source),semantics_text:semanticsText,semantics_sha256:businessHash(semanticsText),authority_effect:'none' as const};
 const contract={contract:'craft.business-materialization/1-candidate',source:'business-materialization-api/epoch-2',status:'original-accepted-decision-only',profile:'remove-one-application-v1-line',encoding:'JSON.stringify(semantics,null,2)+LF'};
 const render:BusinessDerivationOrigin={kind:'semantic-adapter',source:contract.contract,selector:contract.source,sha256:businessHash(businessCanonical(contract))};
 const intermediate=(artifact:string,selector:string,value:unknown):BusinessDerivationOrigin=>({kind:'semantic-adapter',source:artifact,selector,sha256:businessHash(businessCanonical(value))});
 const fromPreview=(selector:string,value:unknown)=>intermediate('preview.json',selector,value),fromRequest=(selector:string,value:unknown)=>intermediate('business-authoring-request-preparation.json',selector,value);
 const ownerDecision=(selector:string):BusinessDerivationOrigin=>({kind:'owner-decision',source:accepted.decision.capture.file.path,selector,sha256:accepted.decision.capture.file.sha256});
 const assignments=new Map<string,readonly BusinessDerivationOrigin[]>(),assign=(target:string,origins:readonly BusinessDerivationOrigin[])=>assignments.set(target,origins);
 const reviewOrigin=fromPreview('/review',preview.review),requestOrigin=fromRequest('/models/'+requestIndex+'/source_fragment',request.source_fragment);
 const profileOrigin:BusinessDerivationOrigin={kind:'profile',source:'profile:'+prepared.selection.technical.profile_id,selector:'/authoring/recipe_ref',sha256:prepared.selection.technical.manifest_sha256};
 const identitySpan=preview.business.data.source_spans.find(span=>span.selector.startsWith('model:'+preview.review.model_identity.namespace+'/line:'));
 const identityOrigins:BusinessDerivationOrigin[]=identitySpan?[{kind:'business',source:identitySpan.source,selector:identitySpan.selector,sha256:identitySpan.source_sha256}]:[];
 assign('',[render]);assign('/model_id',[fromPreview('/model_id',modelId),render]);assign('/compatibility/model_id',[fromPreview('/model_id',modelId),render]);
 for(const key of ['source','application_source'])assign(key==='source'?'/compatibility/source':'/application_source',[...identityOrigins,reviewOrigin,requestOrigin,profileOrigin,render]);
 assign('/source_sha256',[intermediate('materialization.json','/compatibility/source',source),render]);
 assign('/semantics_text',[intermediate('materialization.json','/compatibility/semantics',semantics),render]);assign('/semantics_sha256',[intermediate('materialization.json','/semantics_text',semanticsText),render]);
 const semanticBase='/compatibility/semantics';assign(semanticBase+'/owner',[fromPreview('/review/model_identity/owner',semantics.owner)]);
 for(const id of Object.keys(projection.declarations))assign(semanticBase+'/declarations/'+pointer(id),[fromPreview('/projections/declarations/'+pointer(id),projection.declarations[id])]);
 for(const [index,mapping] of request.mappings.entries())assign(semanticBase+'/declarations/'+pointer(mapping.mapping_id),[fromRequest('/models/'+requestIndex+'/mappings/'+index+'/declaration_binding',mapping.declaration_binding),render]);
 for(const key of ['rule_meanings','operation_behaviors','required_guarantees','value_invariant_bindings'] as const)assign(semanticBase+'/'+key,[fromPreview('/projections/'+key,projection[key])]);
 assign(semanticBase+'/required_guarantees',[fromPreview('/projections/required_guarantees',projection.required_guarantees),profileOrigin,render]);
 for(const [id,claim] of Object.entries(claims)){
  const base=semanticBase+'/claim_meanings/'+pointer(id),draft=projection.claim_drafts[id]!;
  assign(base,[fromPreview('/projections/claim_drafts/'+pointer(id),draft),render]);
  assign(base+'/business_meaning',[fromPreview('/projections/meaning_drafts/'+pointer(id),projection.meaning_drafts[id])]);assign(base+'/business_meaning/status',[ownerDecision('/outcome'),render]);
 assign(base+'/owner_acceptance',[ownerDecision('/subject'),render]);
  for(const key of ['decision_id','owner','outcome'] as const)assign(base+'/owner_acceptance/'+key,[ownerDecision('/'+key)]);
  const subjectIndex=decision.legacy_meaning_subjects.findIndex(value=>value.meaning_id===claim.business_meaning.meaning_id);assign(base+'/owner_acceptance/subject',[ownerDecision('/legacy_meaning_subjects/'+subjectIndex)]);
  assign(base+'/definition_refs',[fromPreview('/projections/claim_drafts/'+pointer(id)+'/definition_refs',draft.definition_refs),ownerDecision('/definition_closure'),render]);
  for(const [index,definition] of claim.definitions.entries()){
   const definitionIndex=projection.definitions.findIndex(value=>value.definition_id===definition.definition_id);
   assign(base+'/definitions/'+index,[fromPreview('/projections/definitions/'+definitionIndex,projection.definitions[definitionIndex]),ownerDecision('/definition_closure'),render]);
   assign(base+'/definitions/'+index+'/status',[ownerDecision('/outcome'),ownerDecision('/definition_closure'),render]);
  }
 }
 const entries:BusinessLoweringLedger['entries'][number][]=[];
 const walk=(node:unknown,target:string):void=>{
  if(node&&typeof node==='object'&&Object.keys(node).length){for(const [key,value] of Object.entries(node))walk(value,target+'/'+pointer(key));return;}
  let at=target,origins:readonly BusinessDerivationOrigin[]|undefined;
  for(;;){origins=assignments.get(at);if(origins)break;at=at.slice(0,at.lastIndexOf('/'));}
  if(!origins.length||origins.length>16||entries.length>=10000)materializationReject('materialization exceeds the closed ledger budget');
  entries.push({id:'materialization.json#'+target,origins:[...origins].sort((a,b)=>compare(businessCanonical(a),businessCanonical(b))),target:{artifact:'materialization.json',pointer:target}});
 };
 walk(stable,'');entries.sort((a,b)=>compare(a.id,b.id));
 const ledger:BusinessLoweringLedger={schema_version:'craft.business-lowering/v1-candidate',recipe_ref:prepared.selection.recipe_ref,business_sha256:preview.business.business_sha256,lock_sha256:prepared.selection.technical.lock_sha256,entries,authority_effect:'none'};
 freezeBusinessData({stable,ledger},preview.business.source.path);
 const result=Object.freeze({kind:'materialized-business-application' as const,accepted,requests,inserted,...stable,ledger,materialization_sha256:businessHash(businessCanonical({ ...stable,ledger}))});
 materializations.set(result,{accepted,requests,inserted,assertRequests:assertRequests as MaterializationOwner['assertRequests'],fingerprint:businessHash(businessCanonical(result))});
 assertMaterializedBusinessApplicationCurrent(result);return result;
}
export function assertMaterializedBusinessApplicationCurrent<Accepted extends AcceptedBusinessReviewDecision,Requests extends BusinessMaterializationRequestSurface>(value:MaterializedBusinessApplication<Accepted,Requests>):void {
 const state=value&&typeof value==='object'?materializations.get(value):undefined;
 if(!state)materializationReject('registered original accepted materialization required');
 assertMaterializationImplementation();assertAcceptedBusinessReviewDecisionCurrent(state.accepted);state.assertRequests(state.requests);assertInsertedBusinessRequestMappingsCurrent(state.inserted);
 if(value.accepted!==state.accepted||value.requests!==state.requests||value.inserted!==state.inserted||businessHash(businessCanonical(value))!==state.fingerprint)materializationReject('accepted materialization custody or generated data changed');
}
