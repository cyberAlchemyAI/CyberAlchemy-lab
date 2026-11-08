import type {BusinessBehaviorData,BusinessEntityStructure,BusinessNormalizedOperation} from './business-authoring-normalization-protocol.js';
import {BUSINESS_NORMALIZATION_CONTRACT} from './business-authoring-normalization-protocol.js';
import type {BusinessEntity,ResolvedBusinessSpec} from './business-authoring-protocol.js';
import {businessCanonical,businessHash,businessReject,freezeBusinessData} from './business-authoring-model.js';
import {assertBusinessFormalSemanticsCurrent,type BusinessFormalSemantics} from './business-authoring-semantics.js';
import {assertDirectBusinessNormalizationV2Current,type DirectBusinessNormalizationV2} from './business-authoring-semantics.js';
import type {BusinessParameter,BusinessValuePath} from './business-authoring-protocol.js';
import type {DirectBooleanConditionV2,BusinessLogicalEntryV2} from './business-authoring-protocol-v2.js';

// B03.2 normalizes authored behavior only. Open questions: B06-B08 materialization/API/lineage.
export interface BusinessBehavior {
 readonly kind:'business-behavior';readonly business:ResolvedBusinessSpec;readonly formal:BusinessFormalSemantics;
 readonly data:BusinessBehaviorData;readonly derivation_sha256:string;
}
const current=new WeakMap<object,{formal:BusinessFormalSemantics;fingerprint:string}>();
const structure=(entity:BusinessEntity):BusinessEntityStructure=>({kind:'entity',entity_ref:entity.id,identity:entity.identity,fields:[...entity.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(({name,type})=>({name,type}))});

export function lowerBusinessBehavior(formal:BusinessFormalSemantics):BusinessBehavior {
 assertBusinessFormalSemanticsCurrent(formal);
 const business=formal.business,spec=business.data,source=business.source.path;
 const fail=(code:string,id:string,clause:string,message:string):never=>{
  const span=spec.source_spans.find(s=>s.selector.startsWith('operation:'+id+'/'+clause+'/line:'))??spec.source_spans.find(s=>s.selector.startsWith('operation:'+id+'/line:'));
  return businessReject(code,source,span?.line??1,span?.column??1,message);
 };
 const entity=(ref:string,id:string,clause:string):BusinessEntityStructure=>{
  const declaration=spec.entities.find(e=>e.id===ref);if(!declaration)return fail('BUSINESS_REFERENCE',id,clause,'resolve the exact declared Entity');return structure(declaration);
 };
 const same=(a:unknown,b:unknown)=>businessCanonical(a)===businessCanonical(b);
 const byId=<T extends {id:string}>(values:readonly T[])=>[...values].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 const operations:BusinessNormalizedOperation[]=byId(spec.operations).map(operation=>{
  const id=operation.id,inputType=entity(operation.input.type_ref,id,'input'),outputType=entity(operation.output_ref,id,'output');
  if(!same(inputType,outputType))fail('BUSINESS_TYPE',id,'output','whole-input output must match complete Entity structure');
  if(operation.effects.length)fail('BUSINESS_UNSUPPORTED',id,'effects','nonempty effects require another qualified recipe');
  if(operation.result.root!==operation.input.name||operation.result.path.length)fail('BUSINESS_UNSUPPORTED',id,'returns','only the explicit whole input may be returned');
  if(operation.guards.length!==1)fail('BUSINESS_UNSUPPORTED',id,'requires','one backend-compatible Rule must own the complete condition');
  const guard=operation.guards[0]!,rule=spec.rules.find(r=>r.id===guard.rule_ref);
  if(!rule)fail('BUSINESS_REFERENCE',id,'requires','guard Rule must be explicitly declared');
  const selected=rule!,claim=spec.claims.find(c=>c.id===selected.claim_ref),meaning=formal.data.rule_meanings[selected.id];
  if(!claim||!meaning||!formal.data.claims.some(c=>c.claim_ref===selected.claim_ref))fail('BUSINESS_REFERENCE',id,'requires','guard must select its normalized claim interpretation');
  if(guard.arguments.length!==1||guard.arguments[0]!.parameter!==selected.input.name)fail('BUSINESS_TYPE',id,'requires','bind the exact Rule parameter once');
  const argument=guard.arguments[0]!.value;
  if(argument.root!==operation.input.name||argument.path.length)fail('BUSINESS_TYPE',id,'requires','guard argument must be the explicit whole Operation input');
  const parameterType=entity(selected.input.type_ref,id,'requires');
  if(!same(parameterType,inputType))fail('BUSINESS_TYPE',id,'requires','guard argument and parameter must match complete Entity structures');
  if(claim!.constants.length!==1||selected.bindings.length!==1)fail('BUSINESS_UNSUPPORTED',id,'requires','one explicit constant-to-parameter binding is backend compatible');
  const constant=claim!.constants[0]!,binding=selected.bindings[0]!;
  if(binding.constant_ref!==constant.name||binding.parameter_ref!==selected.input.name||meaning.constants[constant.name]!==selected.input.name)fail('BUSINESS_REFERENCE',id,'requires','constant binding must select the same Rule parameter');
  const interpreted=entity(meaning.sorts[constant.sort_ref]!,id,'requires');
  if(!same(interpreted,parameterType))fail('BUSINESS_TYPE',id,'requires','formal sort and guard parameter must match complete Entity structures');
  return {
   operation_ref:id,meaning:operation.meaning,input:{name:operation.input.name,type:inputType},output:outputType,
   guards:[{rule_ref:selected.id,claim_ref:selected.claim_ref,parameter:{name:selected.input.name,type:parameterType},argument:{root:argument.root,path:[]}}],
   result:{root:operation.result.root,path:[],type:outputType},effects:[],failure:{kind:'continuation-metadata',continuation:operation.on_rejection,executable:false},
  };
 });
 const exposures=byId(spec.capabilities).map(capability=>{
  if(capability.audience!=='public')businessReject('BUSINESS_UNSUPPORTED',source,1,1,'protected audience needs an explicit supported authorization mechanism');
  if(!operations.some(operation=>operation.operation_ref===capability.operation_ref))businessReject('BUSINESS_REFERENCE',source,1,1,'exposure must name a normalized Operation');
  return {...capability};
 });
 if(!exposures.length)businessReject('BUSINESS_REQUIRED',source,1,1,'at least one explicit exposure is required; no implicit public entry');
 const data=freezeBusinessData<BusinessBehaviorData>({schema_version:'craft.business-behavior-normalization/v1-candidate',normalization_contract:BUSINESS_NORMALIZATION_CONTRACT,
  model_id:spec.identity.namespace,business_sha256:business.business_sha256,formal_sha256:formal.derivation_sha256,operations,
  exposures,contexts:byId(spec.requirements),actor_semantics:'informational-only',authority_effect:'none'},source);
 const result=freezeBusinessData<BusinessBehavior>({kind:'business-behavior',business,formal,data,derivation_sha256:businessHash(businessCanonical(data))},source);
 current.set(result,{formal,fingerprint:businessHash(businessCanonical(result))});assertBusinessBehaviorCurrent(result);return result;
}

export function assertBusinessBehaviorCurrent(value:BusinessBehavior):void {
 const state=value&&typeof value==='object'?current.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered original business behavior required');
 assertBusinessFormalSemanticsCurrent(state.formal);
 if(value.formal!==state.formal||value.business!==state.formal.business||businessHash(businessCanonical(value))!==state.fingerprint)
  businessReject('BUSINESS_SOURCE_DRIFT',state.formal.business.source.path,1,1,'normalized business behavior changed');
}

/** Typed direct behavior data only; genuine Core/native ownership is a later join.
 * Open Questions: U02 CONTEXT.md; L01/L02/G01. */
export interface DirectBusinessBehaviorDataV2 {
 readonly schema_version:'craft.direct-business-behavior/v2-candidate';
 readonly executable_sha256:string;readonly entity:BusinessEntityStructure;
 readonly rule:Readonly<{id:string;requirement_ref:string;input:BusinessParameter;condition:DirectBooleanConditionV2}>;
 readonly operation:Readonly<{
  id:string;input:BusinessParameter;output_ref:string;
  guard:Readonly<{rule_ref:string;parameter:BusinessParameter;argument:BusinessValuePath}>;
  result:BusinessValuePath;rejection:Readonly<{kind:'authored-guard-rejection';code:string}>;effects:readonly [];
 }>;
 readonly entry:BusinessLogicalEntryV2;readonly authority_effect:'none';
}
export interface DirectBusinessBehaviorV2 {
 readonly kind:'direct-business-behavior-v2';readonly normalization:DirectBusinessNormalizationV2;
 readonly data:DirectBusinessBehaviorDataV2;readonly behavior_sha256:string;readonly authority_effect:'none';
}
const directBehaviorRegistry=new WeakMap<object,{normalization:DirectBusinessNormalizationV2;fingerprint:string}>();
export function lowerDirectBusinessBehaviorV2(normalization:DirectBusinessNormalizationV2):DirectBusinessBehaviorV2 {
 assertDirectBusinessNormalizationV2Current(normalization);
 const spec=normalization.executable,entity=spec.entities[0]!,rule=spec.rules[0]!,operation=spec.operations[0]!,entry=spec.entries[0]!;
 const guard=operation.guards[0]!,argument=guard.arguments[0]!;
 // The real source resolver has already checked these references. Preserve the
 // explicit correspondence here rather than inventing a claim or dropping guard data.
 if(rule.condition.kind!=='boolean-field'||rule.input.type_ref!==entity.id||rule.condition.value.root!==rule.input.name||entity.fields.find(field=>field.name===rule.condition.value.path[0])?.type!=='Bool'||guard.rule_ref!==rule.id||argument.parameter!==rule.input.name||argument.value.root!==operation.input.name||argument.value.path.length||operation.input.type_ref!==entity.id||operation.output_ref!==entity.id||operation.result.root!==operation.input.name||operation.result.path.length||operation.effects.length||entry.operation_ref!==operation.id||entry.permission.kind!=='public')businessReject('BUSINESS_DIRECT_CORRESPONDENCE',normalization.capture.path,1,1,'explicit direct source/guard/result/entry correspondence required');
 const data=freezeBusinessData<DirectBusinessBehaviorDataV2>({schema_version:'craft.direct-business-behavior/v2-candidate',executable_sha256:normalization.executable_sha256,entity:structure(entity),rule,
  operation:{id:operation.id,input:operation.input,output_ref:operation.output_ref,guard:{rule_ref:guard.rule_ref,parameter:rule.input,argument:argument.value},result:operation.result,rejection:{kind:'authored-guard-rejection',code:operation.on_rejection},effects:[]},entry,authority_effect:'none'},normalization.capture.path);
 const result=freezeBusinessData<DirectBusinessBehaviorV2>({kind:'direct-business-behavior-v2',normalization,data,behavior_sha256:businessHash(businessCanonical(data)),authority_effect:'none'},normalization.capture.path);
 directBehaviorRegistry.set(result,{normalization,fingerprint:businessHash(businessCanonical(result))});assertDirectBusinessBehaviorV2Current(result);return result;
}
export function assertDirectBusinessBehaviorV2Current(value:DirectBusinessBehaviorV2):void {
 const state=value&&typeof value==='object'?directBehaviorRegistry.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original direct business behavior required');
 assertDirectBusinessNormalizationV2Current(state.normalization);
 if(value.normalization!==state.normalization||businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.normalization.capture.path,1,1,'direct business behavior changed');
}
