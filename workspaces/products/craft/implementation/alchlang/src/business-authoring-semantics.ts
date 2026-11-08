import type {BusinessSourceSpan,ResolvedBusinessSpec,ReviewDefinition} from './business-authoring-protocol.js';
import {BUSINESS_NORMALIZATION_CONTRACT} from './business-authoring-normalization-protocol.js';
import type {BusinessBoolPrimitive,BusinessEntityStructure,BusinessFormalData,BusinessGroundProposition,BusinessNormalizedClaim,BusinessNormalizedDefinition,BusinessRuleInterpretation} from './business-authoring-normalization-protocol.js';
import {assertResolvedBusinessSpecCurrent} from './business-authoring-resolve.js';
import {businessCanonical,businessHash,businessReject,freezeBusinessData} from './business-authoring-model.js';
import {parseFormalProposition,type FormalProposition} from './formal-claim.js';
import {CompilationRejected} from './model.js';
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {ResolvedBusinessSpecV2,DirectExecutableProjectionV2,OptionalAssuranceProjectionV2} from './business-authoring-protocol-v2.js';
import type {BusinessReviewSubjectV2} from './business-authoring-identity-protocol-v2.js';
import {assertResolvedBusinessSpecV2Current} from './business-authoring-resolve.js';
import {projectAlchDirectExecutableV2,projectAlchOptionalAssuranceV2,projectAlchBusinessReviewSubjectV2} from './business-authoring-identity-v2.js';

// Open questions: B06 owns semantic carriers and B04 owner decisions; neither is synthesized here.
export interface BusinessFormalSemantics {
 readonly kind:'business-formal-semantics';readonly business:ResolvedBusinessSpec;
 readonly data:BusinessFormalData;readonly derivation_sha256:string;
}
type PredicateUse=BusinessNormalizedDefinition['predicate_uses'][number];
const byName=<T extends {name:string}>(values:readonly T[]):T[]=>[...values].sort((a,b)=>compare(a.name,b.name));
const compare=(a:string,b:string):number=>a<b?-1:a>b?1:0;
const orderedUses=(uses:readonly PredicateUse[]):PredicateUse[]=>[...uses].sort((a,b)=>compare(a.claim_ref,b.claim_ref)||compare(a.predicate_ref,b.predicate_ref)||compare(a.sort_ref,b.sort_ref));
const registry=new WeakMap<object,{business:ResolvedBusinessSpec;fingerprint:string}>();

/** Mechanical text contract for the single primitive. It is definition metadata, never a proof. */
export function renderBusinessBoolFormal(definition_ref:string,primitive:BusinessBoolPrimitive,entity_meaning:string,field_meaning:string,predicate_uses:readonly PredicateUse[]):ReviewDefinition['formal'] {
 const selected=`${primitive.parameter}.${primitive.field}`;
 const expression=`(${selected} = true)`;
 const definition=`${definition_ref}(${primitive.parameter}: ${primitive.entity_ref}) := ${expression}`;
 const associations=orderedUses(predicate_uses).map(use=>`${use.claim_ref}::${use.predicate_ref}(${primitive.parameter}: ${use.sort_ref}) iff ${expression}`);
 return freezeBusinessData({definition,expression:associations.length?associations.join('; '):definition,
  notation:[{symbol:primitive.parameter,meaning:entity_meaning},{symbol:selected,meaning:field_meaning}],
  operational_interpretation:`Read ${selected}: Bool and compare with true.`},'business-formal-rendering');
}
export function assertBusinessFormalSemanticsCurrent(value:BusinessFormalSemantics):void {
 const state=value&&typeof value==='object'?registry.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered business formal semantics required');
 assertResolvedBusinessSpecCurrent(state.business);
 if(value.business!==state.business||businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.business.source.path,1,1,'formal normalization changed');
}
export function lowerBusinessFormalSemantics(business:ResolvedBusinessSpec):BusinessFormalSemantics {
 assertResolvedBusinessSpecCurrent(business);
 const spec=business.data,source=business.source.path;
 const fail=(code:string,selector:string,message:string):never=>{
  const span:BusinessSourceSpan|undefined=spec.source_spans.find(s=>s.selector.startsWith(selector+'/line:'));
  return businessReject(code,source,span?.line??1,span?.column??1,message);
 };
 const structures=new Map<string,BusinessEntityStructure>(spec.entities.map(entity=>[entity.id,{kind:'entity',entity_ref:entity.id,identity:entity.identity,fields:byName(entity.fields).map(field=>({name:field.name,type:field.type}))}]));
 const definitions:BusinessNormalizedDefinition[]=[...spec.definitions].sort((a,b)=>compare(a.id,b.id)).map(definition=>{
  const entity=spec.entities.find(entity=>entity.id===definition.input.type_ref);
  const field=entity?.fields.find(field=>field.name===definition.boolean_field.path[0]);
  if(!entity||!field||field.type!=='Bool'||definition.boolean_field.root!==definition.input.name||definition.boolean_field.path.length!==1)fail('BUSINESS_UNSUPPORTED','definition:'+definition.id+'/boolean-field','only an explicit unary Entity Bool-field definition is supported');
  const primitive:BusinessBoolPrimitive={kind:'entity-bool-field',entity_ref:entity!.id,parameter:definition.input.name,field:field!.name,field_type:'Bool',comparison:'eq',value:true};
  const predicate_uses=orderedUses(spec.claims.flatMap(claim=>claim.predicates.filter(predicate=>predicate.definition_ref===definition.id).map(predicate=>({claim_ref:claim.id,predicate_ref:predicate.name,sort_ref:predicate.sort_refs[0]!}))));
  return {definition_ref:definition.id,requirement_ref:definition.requirement_ref,input:definition.input,entity:structures.get(entity!.id)!,field:field!,primitive,
   formal:renderBusinessBoolFormal(definition.id,primitive,entity!.meaning,field!.meaning,predicate_uses),predicate_uses};
 });
 const definitionsById=new Map(definitions.map(definition=>[definition.definition_ref,definition]));
 const claims:BusinessNormalizedClaim[]=[...spec.claims].sort((a,b)=>compare(a.id,b.id)).map(claim=>{
  const at='formal-claim:'+claim.id+'/proposition';
  const signature={sorts:byName(claim.sorts).map(sort=>({name:sort.name})),functions:[] as [],predicates:byName(claim.predicates).map(predicate=>({name:predicate.name,parameter_sorts:[...predicate.sort_refs]})),constants:byName(claim.constants).map(constant=>({name:constant.name,sort:constant.sort_ref}))};
  for(const sort of claim.sorts){
   const sortAt='formal-claim:'+claim.id+'/sort:'+sort.name;
   if(!structures.has(sort.type_ref))fail('BUSINESS_UNSUPPORTED',sortAt,'formal sorts must retain their explicit resolved Entity type');
   if(!claim.predicates.some(predicate=>predicate.sort_refs.includes(sort.name))&&!claim.constants.some(constant=>constant.sort_ref===sort.name))fail('BUSINESS_UNSUPPORTED',sortAt,'unused formal sort has no supported ground interpretation');
  }
  for(const predicate of claim.predicates){
   const definition=definitionsById.get(predicate.definition_ref),sort=claim.sorts.find(sort=>sort.name===predicate.sort_refs[0]);
   if(predicate.sort_refs.length!==1||!definition||!sort||sort.type_ref!==definition.primitive.entity_ref||!structures.has(sort.type_ref))fail('BUSINESS_UNSUPPORTED',at,'predicates require one explicitly interpreted Entity sort and its typed Bool-field definition');
  }
  let parsed:FormalProposition;
  try{parsed=parseFormalProposition(claim.proposition,signature);}
  catch(error){if(error instanceof CompilationRejected)return fail('BUSINESS_UNSUPPORTED',at,error.message);throw error;}
  let visits=0;
  const ground=(node:FormalProposition,depth=0):BusinessGroundProposition=>{
   if(++visits>10000||depth>64)fail('BUSINESS_SOURCE_BUDGET',at,'formal AST exceeds finite node/depth budget');
   switch(node.kind){
    case 'predicate':{
     if(node.arguments.length!==1||node.arguments[0]!.kind!=='constant')return fail('BUSINESS_UNSUPPORTED',at,'ground unary predicate requires one explicitly bound constant');
     const argument=node.arguments[0]!;
     return {kind:'predicate',name:node.name,arguments:[{kind:'constant',name:argument.name,sort:argument.sort}]};
    }
    case 'not':return {kind:'not',operand:ground(node.operand,depth+1)};
    case 'and':case 'or':case 'implies':case 'iff':return {kind:node.kind,left:ground(node.left,depth+1),right:ground(node.right,depth+1)};
    default:return fail('BUSINESS_UNSUPPORTED',at,node.kind==='equal'?'Entity equality is not a scalar ground predicate interpretation':`${node.kind} has no supported ground Entity Bool interpretation`);
   }
  };
  const proposition=ground(parsed!);
  // Match the existing projector's recursive expansion accounting for iff's duplicated operands.
  const expansion=(node:BusinessGroundProposition):number=>{
   let count:number;
   if(node.kind==='predicate')count=1;
   else if(node.kind==='not')count=1+expansion(node.operand);
   else {const left=expansion(node.left),right=expansion(node.right);count=1+(node.kind==='iff'?2:1)*(left+right);}
   if(count>1024)fail('BUSINESS_SOURCE_BUDGET',at,'expanded formal projection exceeds 1024 nodes');return count;
  };expansion(proposition);
  return {claim_ref:claim.id,version:claim.version,logic_profile:claim.logic_profile,signature,proposition_source:claim.proposition,proposition,ceiling:claim.ceiling};
 });
 const rule_meanings:Record<string,BusinessRuleInterpretation>=Object.create(null);
 for(const rule of [...spec.rules].sort((a,b)=>compare(a.id,b.id))){
  const claim=spec.claims.find(claim=>claim.id===rule.claim_ref)!;
  const sorts:Record<string,string>=Object.create(null),constants:Record<string,string>=Object.create(null),predicates:Record<string,string>=Object.create(null);
  for(const sort of byName(claim.sorts))sorts[sort.name]=sort.type_ref;
  for(const constant of byName(claim.constants))constants[constant.name]=rule.bindings.find(binding=>binding.constant_ref===constant.name)!.parameter_ref;
  for(const predicate of byName(claim.predicates))predicates[predicate.name]=definitionsById.get(predicate.definition_ref)!.primitive.field;
  rule_meanings[rule.id]={sorts,constants,predicates};
 }
 const data:BusinessFormalData={schema_version:'craft.business-formal-normalization/v1-candidate',normalization_contract:BUSINESS_NORMALIZATION_CONTRACT,model_id:spec.identity.stable_id,business_sha256:business.business_sha256,definitions,claims,rule_meanings,authority_effect:'none'};
 const result=freezeBusinessData<BusinessFormalSemantics>({kind:'business-formal-semantics',business,data,derivation_sha256:businessHash(businessCanonical(data))},source);
 registry.set(result,{business,fingerprint:businessHash(businessCanonical(result))});assertBusinessFormalSemanticsCurrent(result);return result;
}

/** Direct normalization has its own source owner. It never visits the legacy
 * claim-to-execution lowering above. Open Questions: U02 CONTEXT.md; L01/Core join. */
export interface DirectBusinessNormalizationV2 {
 readonly kind:'direct-business-normalization-v2';readonly business:ResolvedBusinessSpecV2;
 readonly executable:DirectExecutableProjectionV2;readonly assurance:OptionalAssuranceProjectionV2;
 readonly review:BusinessReviewSubjectV2;readonly capture:BusinessSourceCapture;
 readonly executable_sha256:string;readonly assurance_sha256:string;readonly source_sha256:string;
 readonly authority_effect:'none';
}
const directNormalizationRegistry=new WeakMap<object,{business:ResolvedBusinessSpecV2;fingerprint:string}>();
export function normalizeDirectBusinessV2(business:ResolvedBusinessSpecV2):DirectBusinessNormalizationV2 {
 assertResolvedBusinessSpecV2Current(business);
 const executable=projectAlchDirectExecutableV2(business.data),assurance=projectAlchOptionalAssuranceV2(business.data);
 const executable_sha256=businessHash(businessCanonical(executable)),assurance_sha256=businessHash(businessCanonical(assurance));
 if(executable_sha256!==business.executable_sha256||assurance_sha256!==business.assurance_sha256)businessReject('BUSINESS_SOURCE_DRIFT',business.source.path,1,1,'direct normalization differs from the original resolved subject');
 const result=freezeBusinessData<DirectBusinessNormalizationV2>({kind:'direct-business-normalization-v2',business,executable,assurance,review:projectAlchBusinessReviewSubjectV2(business.data),capture:business.source,executable_sha256,assurance_sha256,source_sha256:business.source.sha256,authority_effect:'none'},business.source.path);
 directNormalizationRegistry.set(result,{business,fingerprint:businessHash(businessCanonical(result))});
 assertDirectBusinessNormalizationV2Current(result);return result;
}
export function assertDirectBusinessNormalizationV2Current(value:DirectBusinessNormalizationV2):void {
 const state=value&&typeof value==='object'?directNormalizationRegistry.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original direct normalization required');
 assertResolvedBusinessSpecV2Current(state.business);
 if(value.business!==state.business||value.capture!==state.business.source||businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.business.source.path,1,1,'direct normalization or capture changed');
}
