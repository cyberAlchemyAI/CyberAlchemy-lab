import {validateShape,validateProfileProject,validateProfilePackage,captureJson,dataDigest,reject,PROFILE_ROLE_CONTRACTS,type ProfileProject,type ProfilePackage,type ProfileAsset,type Role} from './contracts.js';

// Open questions: docs/BUSINESS-APPLICATIONS.md. Accepted meaning is not proof or admission.
export interface BusinessPath {readonly root:'body'|'request'|'value';readonly path:readonly string[]}
export interface BusinessApplicationModel {readonly id:string;readonly source:string;readonly semantics:string}
export interface BusinessApplicationIntent {readonly id:string;readonly application_id:string;readonly operation_ref:string;readonly mapping_ref:string;readonly mapping_arguments:Readonly<Record<string,BusinessPath>>;readonly access:Readonly<{kind:'public'}>}
export interface ProfileProjectV2 extends Omit<ProfileProject,'schema_version'|'integration_configuration'> {
 readonly schema_version:'craft.profile-project/v2-candidate';readonly integration_configuration?:string;
 readonly application_models:readonly BusinessApplicationModel[];readonly application_intents:readonly BusinessApplicationIntent[];
}
export interface ProfileAssetV2 extends Omit<ProfileAsset,'kind'>{readonly kind:'template'|'native'|'data'}
export interface ProfilePackageV2 extends Omit<ProfilePackage,'schema_version'|'engine'|'assets'> {
 readonly schema_version:'craft.profile-package/v2-candidate';readonly engine:'craft.profile-engine/v2-candidate';readonly assets:readonly ProfileAssetV2[];
 readonly application_runtime:Readonly<{settlement:'empty-effects/v1';settlement_asset:string;formal_profile_asset:string;identity_algorithm_asset:string;transport:'entry-local'|'shared';transport_asset:string}>;
}
export const PROFILE_ROLE_CONTRACTS_V2=Object.freeze({...PROFILE_ROLE_CONTRACTS,'application-operation':Object.freeze({descriptor_ref:'typescript.bound-operation/v2-candidate',recipe_ref:'craft.profile.application-operation/v2-candidate',descriptor_kind:'candidate-engine-role' as const,factory_admission:'not-claimed' as const}),'shared-http-port':Object.freeze({descriptor_ref:'typescript.operation-http-port/v2-candidate',recipe_ref:'craft.profile.operation-http-port/v2-candidate',descriptor_kind:'candidate-engine-role' as const,factory_admission:'not-claimed' as const})});
function unique(values:readonly string[],at:string){if(new Set(values).size!==values.length)reject('PROFILE_DUPLICATE_ID',at,'unique identity required');}
function sourcePath(value:string,at:string){if(!value||value.startsWith('/')||value.includes('\\')||value.includes('\0')||value.split('/').some(p=>!p||p==='.'||p==='..'))reject('PROFILE_SOURCE_PATH',at,'owned relative source required');}
export function validateProfileProjectV2(raw:unknown):ProfileProjectV2 {
 const data=validateShape<ProfileProjectV2>('project-v2',raw);
 data.domain_sources.forEach(p=>sourcePath(p,'/domain_sources'));
 if(data.integration_configuration!==undefined)sourcePath(data.integration_configuration,'/integration_configuration');
 if(data.external_reads.length&&data.integration_configuration===undefined)reject('PROFILE_WIRE_CONTRACT_REQUIRED','/integration_configuration','authored reads require exact configuration');
 if(data.public_intents.length===1)reject('PROFILE_FUNCTION_CARDINALITY_UNSUPPORTED','/public_intents','existing function builder requires two or more actual function intents');
 const intents=[...data.public_intents,...data.application_calls??[],...data.application_intents];
 if(!intents.length||intents.length>32)reject('PROFILE_ENTRY_BUDGET','/','one to32 actual public entries required');
 unique(intents.map(i=>i.id),'/public_entries');unique(data.application_models.map(m=>m.id),'/application_models');unique(data.profiles.map(p=>p.id),'/profiles');
 unique(data.external_reads.map(r=>r.id),'/external_reads');unique(data.formal_claims.map(c=>c.id),'/formal_claims');
 for(const row of [...data.public_intents,...data.external_reads,...data.formal_claims])if(!data.domain_sources.includes(row.source))reject('PROFILE_PUBLIC_INTENT_UNKNOWN_REF',row.source,'function business source must be declared');
 for(const intent of data.public_intents)unique(intent.outcomes.map(o=>o.code),intent.id+'/outcomes');
 for(const call of data.application_calls??[])sourcePath(call.source,'/application_calls/source');
 for(const model of data.application_models){sourcePath(model.source,model.id+'/source');sourcePath(model.semantics,model.id+'/semantics');if(!data.application_intents.some(i=>i.application_id===model.id))reject('PROFILE_APPLICATION_MODEL_UNEXPOSED',model.id,'selected model needs an authored intent');}
 for(const intent of data.application_intents){
  if(!data.application_models.some(m=>m.id===intent.application_id))reject('PROFILE_APPLICATION_MODEL_UNKNOWN',intent.id,'resolve exact model before normalization');
  for(const expression of Object.values(intent.mapping_arguments))if(expression.root!=='body')reject('PROFILE_REQUEST_PATH_ROOT',intent.id,'public Mapping arguments must refer to the request body');
 }
 return data;
}
export function validateProfileProjectInput(raw:unknown):ProfileProject|ProfileProjectV2 {
 const inert=captureJson(raw) as unknown as {schema_version?:string};
 return inert?.schema_version==='craft.profile-project/v2-candidate'?validateProfileProjectV2(inert):validateProfileProject(inert);
}
export function validateProfilePackageV2(raw:unknown):ProfilePackageV2 {
 const data=validateShape<ProfilePackageV2>('package-v2',raw),runtime=data.application_runtime;
 for(const capability of data.capabilities){const expected=PROFILE_ROLE_CONTRACTS_V2[capability.role];if(!expected||capability.descriptor_ref!==expected.descriptor_ref||capability.recipe_ref!==expected.recipe_ref)reject('PROFILE_ROLE_MAPPING_UNSUPPORTED',capability.role,'exact registered v2 role required');}
 // Preserve the entire v1 bounded rule/template/conflict/closure validator. Data assets are inert.
 const {application_runtime:_runtime,...common}=data;
 validateProfilePackage({...common,schema_version:'craft.profile-package/v1',engine:'craft.profile-engine/v1',capabilities:data.capabilities.map(c=>({role:c.role,...PROFILE_ROLE_CONTRACTS[c.role]})).map(({role,descriptor_ref,recipe_ref})=>({role,descriptor_ref,recipe_ref})),assets:data.assets.map(a=>({...a,kind:a.kind==='data'?'native':a.kind}))});
 for(const [ref,kind] of [[runtime.formal_profile_asset,'data'],[runtime.identity_algorithm_asset,'data'],[runtime.settlement_asset,'native'],[runtime.transport_asset,'native']] as const){
  const asset=data.assets.find(a=>a.id===ref);if(!asset||asset.kind!==kind||asset.includes.length||Object.keys(asset.holes).length)reject('PROFILE_RUNTIME_ASSET_REQUIRED',ref,'owned inert formal data and native settlement component required');
 }
 if(!data.capabilities.some(c=>c.role==='application-operation'))reject('PROFILE_APPLICATION_ROLE_REQUIRED','/capabilities','application runtime requires its registered role');
 return data;
}
export function validateProfilePackageInput(raw:unknown):ProfilePackage|ProfilePackageV2 {
 const inert=captureJson(raw) as unknown as {schema_version?:string};return inert?.schema_version==='craft.profile-package/v2-candidate'?validateProfilePackageV2(inert):validateProfilePackage(inert);
}
export interface AcceptedBusinessClaim {readonly claim_id:string;readonly version:string;readonly supersedes:string|null;readonly business_meaning:Readonly<Record<string,any>>;readonly owner_acceptance:Readonly<Record<string,any>>;readonly definitions:readonly Readonly<Record<string,any>>[];readonly definition_refs:readonly string[]}
export interface BusinessGuard {readonly rule:string;readonly arguments:Readonly<Record<string,BusinessPath>>}
export interface BusinessApplication {readonly schema_version:'craft.business-application/v1-candidate';readonly owner:string;readonly declarations:Readonly<Record<string,any>>;readonly claim_meanings:Readonly<Record<string,AcceptedBusinessClaim>>;readonly rule_meanings:Readonly<Record<string,{readonly sorts:Readonly<Record<string,string>>;readonly constants:Readonly<Record<string,string>>;readonly predicates:Readonly<Record<string,string>>}>>;readonly operation_behaviors:Readonly<Record<string,{readonly input_name:string;readonly guards:readonly BusinessGuard[];readonly result:BusinessPath}>>;readonly required_guarantees:readonly string[];readonly value_invariant_bindings:Readonly<Record<string,readonly BusinessGuard[]>>}
export function validateBusinessApplication(raw:unknown):BusinessApplication {
 const data=validateShape<BusinessApplication>('business-application',raw);
 for(const [name,claim] of Object.entries(data.claim_meanings)){
  const meaning=claim.business_meaning,decision=claim.owner_acceptance,subject=decision.subject;
  if(meaning.owner!==data.owner||decision.owner!==meaning.owner||subject.meaning_id!==meaning.meaning_id||subject.version!==meaning.version||subject.digest!==dataDigest(meaning))reject('PROFILE_BUSINESS_ACCEPTANCE',name,'explicit owner decision must accept the exact current business-meaning subject');
  unique(claim.definitions.map(d=>String(d.definition_id)),name+'/definitions');
  const ids=new Set(claim.definition_refs);for(const id of ids)if(!claim.definitions.some(d=>d.definition_id===id))reject('PROFILE_DEFINITION_UNKNOWN',id,'explicit accepted definition must resolve');
  for(const definition of claim.definitions.filter(d=>ids.has(d.definition_id)))for(const dependency of definition.depends_on)if(!ids.has(dependency))reject('PROFILE_DEFINITION_CLOSURE',name,'explicit transitive definitions required');
 }
 for(const [name,behavior] of Object.entries(data.operation_behaviors)){
  if(behavior.result.root!=='request'||behavior.result.path.length)reject('PROFILE_APPLICATION_RESULT_UNSUPPORTED',name,'first application slice returns the whole authored input');
  unique(behavior.guards.map(g=>g.rule),name+'/guards');for(const g of behavior.guards)for(const value of Object.values(g.arguments))if(value.root!=='request')reject('PROFILE_BUSINESS_GUARD_ROOT',name,'Operation guard arguments refer to the authored input');
 }
 for(const [name,guards] of Object.entries(data.value_invariant_bindings)){unique(guards.map(g=>g.rule),name+'/invariants');for(const g of guards)for(const value of Object.values(g.arguments))if(value.root!=='value')reject('PROFILE_BUSINESS_INVARIANT_ROOT',name,'invariants bind explicit value paths');}
 return data;
}
