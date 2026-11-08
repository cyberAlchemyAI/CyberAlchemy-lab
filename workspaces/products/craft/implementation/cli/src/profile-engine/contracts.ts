import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {types} from 'node:util';

/** Finite v1 shape contracts. Semantic/current-object checks belong to composition.
 * Open questions: docs/PROFILE-CALLABLES.md and the PE07/09 construction tasks. */
export type Json = null | boolean | number | string | readonly Json[] | {readonly [key:string]:Json};
export type FieldPath = readonly string[];
export type Expression = Readonly<{literal:Json}> | Readonly<{field:FieldPath}> | Readonly<{concat:readonly Expression[]}>;
export type Role = 'domain-function'|'http-entry'|'http-dispatch'|'shared-http-port'|'external-read'|'application-operation'|'environment'|'operational-expectation';
export type DerivationRule =
 | Readonly<{id:string;op:'select';from:string;as:string;where?:{readonly field:FieldPath;readonly equals:Json}}>
 | Readonly<{id:string;op:'project';from:string;as:string;fields:Readonly<Record<string,Expression>>}>
 | Readonly<{id:string;op:'join';left:string;right:string;as:string;on:Readonly<{left:FieldPath;right:FieldPath}>;cardinality:'one'|'many'}>
 | Readonly<{id:string;op:'traverse';from:string;edges:string;as:string;max_depth:number}>
 | Readonly<{id:string;op:'require-one';from:string;as:string}>
 | Readonly<{id:string;op:'defaults';as:string;values:Readonly<Record<string,Json>>}>
 | Readonly<{id:string;op:'emit';from:string;role:Role;fields:Readonly<Record<string,Expression>>}>;

/** Exact core-owned references. Candidate roles are generation contracts, not factory admission. */
export const PROFILE_ROLE_CONTRACTS:Readonly<Record<Role,Readonly<{descriptor_ref:string;recipe_ref:string;descriptor_kind:'existing-generator'|'candidate-engine-role';factory_admission:'not-claimed'}>>>=Object.freeze(Object.fromEntries([
 ['domain-function','declarative-function-v1','existing-generator'],
 ['http-entry','craft.profile.http-entry/v1','candidate-engine-role'],
 ['http-dispatch','service-v1','existing-generator'],
 ['shared-http-port','craft.profile.shared-http-port/v1','candidate-engine-role'],
 ['external-read','craft.profile.external-read/v1','candidate-engine-role'],
 ['application-operation','typescript.bound-operation/v1','existing-generator'],
 ['environment','craft.profile.environment/v1','candidate-engine-role'],
 ['operational-expectation','craft.profile.operational-expectation/v1','candidate-engine-role'],
].map(([role,descriptor,kind])=>[role,Object.freeze({descriptor_ref:descriptor!,recipe_ref:`craft.profile.${role}/v1`,descriptor_kind:kind!,factory_admission:'not-claimed' as const})])) as Record<Role,Readonly<{descriptor_ref:string;recipe_ref:string;descriptor_kind:'existing-generator'|'candidate-engine-role';factory_admission:'not-claimed'}>>);

export interface Budget {readonly operations:number;readonly rows:number;readonly join_pairs:number;readonly depth:number;readonly bytes:number}
export interface ProfileAsset {readonly id:string;readonly path:string;readonly kind:'template'|'native';readonly sha256:string;readonly includes:readonly string[];readonly holes:Readonly<Record<string,'identifier'|'string'|'json'|'import-path'>>}
export interface PackageReference {readonly id:string;readonly version:string;readonly path:string;readonly sha256:string}
export interface ProfilePackage {
 readonly schema_version:'craft.profile-package/v1';readonly id:string;readonly version:string;readonly engine:'craft.profile-engine/v1';readonly conflict_policy:'reject';
 readonly dependencies:readonly PackageReference[];readonly capabilities:readonly Readonly<{role:Role;descriptor_ref:string;recipe_ref:string}>[];
 readonly budgets:Budget;readonly rules:readonly DerivationRule[];readonly assets:readonly ProfileAsset[];
}
export interface PublicIntent {
 readonly id:string;readonly source:string;readonly result_ref:string;readonly input_ref:string;readonly output_ref:string;
 readonly access:Readonly<{kind:'public'}>|Readonly<{kind:'policy';policy_ref:string}>;
 readonly outcomes:readonly Readonly<{code:string;kind:'success'|'business-rejection'}>[];
}
export interface ExternalRead {readonly id:string;readonly source:string;readonly output_ref:string;readonly request_fields:Readonly<Record<string,string>>}
export interface FormalClaim {readonly id:string;readonly source:string;readonly selector:string;readonly statement:string}
export interface ProfileProject {
 readonly schema_version:'craft.profile-project/v1';readonly id:string;readonly domain_sources:readonly string[];
 readonly public_intents:readonly PublicIntent[];readonly external_reads:readonly ExternalRead[];readonly formal_claims:readonly FormalClaim[];
 readonly integration_configuration:string;readonly profiles:readonly Omit<PackageReference,'sha256'>[];
 readonly application_calls?:readonly Readonly<{id:string;source:string;operation_ref:string;mapping_binding_ref:string;access:Readonly<{kind:'public'}>}>[];
}
export interface ProfileLock {
 readonly schema_version:'craft.profile-lock/v1';readonly engine_sha256:string;readonly tool_sha256:string;readonly source_sha256:string;
 readonly packages:readonly Readonly<{id:string;version:string;sha256:string;asset_sha256:string}>[];readonly lock_sha256:string;
}
export interface Origin {readonly kind:'business'|'profile-rule'|'integration-configuration';readonly source:string;readonly selector:string;readonly sha256:string}
export interface Component {readonly id:string;readonly role:Role;readonly owner:string;readonly artifact_paths:readonly string[];readonly depends_on:readonly string[];readonly origins:readonly Origin[];readonly contract_ref:string}
export interface CompositionData {readonly schema_version:'craft.profile-composition/v1';readonly source_sha256:string;readonly lock_sha256:string;readonly components:readonly Component[];readonly composition_sha256:string;readonly authority_effect:'none'}
export type EvidenceState='linked'|'generated'|'statically-checked'|'finite-observed'|'proved'|'admitted';
export interface CoverageItem {readonly id:string;readonly origin:Origin;readonly kind:'business-obligation'|'public-intent'|'access-policy'|'integration-binding'|'generated-role'|'formal-claim';readonly state:'retained'|'unsupported-required'|'claim-residue';readonly reason:string;readonly artifact_refs:readonly string[];readonly evidence_states:readonly EvidenceState[]}
export interface CoverageData {readonly schema_version:'craft.profile-coverage/v1';readonly source_sha256:string;readonly lock_sha256:string;readonly items:readonly CoverageItem[];readonly authority_effect:'none'}
export interface CallableContext {readonly signal?:AbortSignal;readonly cancellation?:'preflight'|'required';readonly observe?:(event:Readonly<{phase:string;adapter:string}>)=>void}
export type InvocationResult<V,F>=Readonly<{status:'returned';value:V}>|Readonly<{status:'not-returned';failure:F}>;
export type ProfileCallable<I,V,P,F>=(input:I,ports:P,context?:CallableContext)=>Promise<InvocationResult<V,F>>;

export class ProfileRejected extends TypeError {
 constructor(readonly code:string,readonly pointer:string,detail:string){super(`${code}:${pointer}:${detail}`);this.name='ProfileRejected';}
}
export function reject(code:string,pointer:string,detail:string):never{throw new ProfileRejected(code,pointer,detail);}
const schemas=Object.fromEntries(['project','package','lock','composition','coverage'].map(name=>[name,JSON.parse(readFileSync(new URL(`../../contracts/profile-${name}-v1.schema.json`,import.meta.url),'utf8'))])) as Record<string,any>;
for(const [name,file] of [['project-v2','profile-project-v2'],['package-v2','profile-package-v2'],['business-application','business-application-v1']] as const){
 schemas[name]=JSON.parse(readFileSync(new URL(`../../contracts/${file}.schema.json`,import.meta.url),'utf8'));
}
const capabilitySchema=JSON.parse(readFileSync(new URL('../../contracts/generic-capability-v1.schema.json',import.meta.url),'utf8'));
for(const [name,definition] of Object.entries({'capability-selection':'GenericCapabilitySelection','context-manifest':'GenericSourceContextManifest','release-ticket':'GenericSourceReleaseTicketData','trusted-search-context':'GenericTrustedSearchContextData','continuation':'GenericContinuationDecision'})){
 schemas[name]={...capabilitySchema,$ref:'#/$defs/'+definition};
}

/** Capture plain inert data without executing accessors or accepting class instances. */
function captureJsonData(input:unknown,finiteSchemaNumbers:boolean):Json {
 let nodes=0,bytes=0;
 const walk=(v:unknown,depth:number,pointer:string):Json=>{
  if(++nodes>100000||depth>64)reject('PROFILE_DATA_BUDGET',pointer,'maximum nodes/depth exceeded');
  if(v===null||typeof v==='boolean')return v;
  if(typeof v==='number'){if(!Number.isFinite(v)||!finiteSchemaNumbers&&!Number.isSafeInteger(v)&&Math.abs(v)>=Number.MAX_SAFE_INTEGER)reject('PROFILE_DATA_NUMBER',pointer,'finite safely represented number required');return v;}
  if(typeof v==='string'){bytes+=Buffer.byteLength(v);if(bytes>16777216)reject('PROFILE_DATA_BUDGET',pointer,'maximum string bytes exceeded');return v;}
  if(!v||typeof v!=='object')return reject('PROFILE_DATA_TYPE',pointer,'JSON value required');
  if(types.isProxy(v))reject('PROFILE_DATA_PROXY',pointer,'plain captured data required');
  const array=Array.isArray(v),proto=Object.getPrototypeOf(v);
  if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)reject('PROFILE_DATA_TYPE',pointer,'plain inert data required');
  const descriptors=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(descriptors);
  if(array){
   const length=descriptors.length?.value as number;
   if(!Number.isInteger(length)||length>10000||keys.length!==length+1)reject('PROFILE_DATA_ARRAY',pointer,'bounded dense array required');
   const out:Json[]=[];for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable)reject('PROFILE_DATA_ACCESSOR',pointer,'inert array entries required');out.push(walk(d.value,depth+1,`${pointer}/${i}`));}return Object.freeze(out);
  }
  if(keys.length>2048)reject('PROFILE_DATA_BUDGET',pointer,'maximum object fields exceeded');
  const out:Record<string,Json>=Object.create(null);
  for(const key of keys){const d=descriptors[key as string];if(typeof key!=='string'||!d||!Object.hasOwn(d,'value')||!d.enumerable)reject('PROFILE_DATA_ACCESSOR',pointer,'inert enumerable string properties required');bytes+=Buffer.byteLength(key);if(bytes>16777216)reject('PROFILE_DATA_BUDGET',pointer,'maximum bytes exceeded');out[key]=walk(d.value,depth+1,`${pointer}/${key}`);}
  return Object.freeze(out);
 };return walk(input,0,'');
}
export function captureJson(input:unknown):Json{return captureJsonData(input,false);}
/** Schema keywords describe native finite-number ranges; metadata/counters keep
 * the exact-number policy above. Both paths share the inert-data/budget checks. */
export function captureSchemaJson(input:unknown):Json{return captureJsonData(input,true);}
export function canonicalJson(value:Json):string {
 if(Array.isArray(value))return '['+value.map(v=>canonicalJson(v)).join(',')+']';
 if(value!==null&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonicalJson((value as Record<string,Json>)[k]!)).join(',')+'}';
 return JSON.stringify(value);
}
export const sha256=(value:string|Buffer):string=>createHash('sha256').update(value).digest('hex');
export const dataDigest=(input:unknown):string=>sha256(canonicalJson(captureJson(input)));
const object=(v:Json):v is {[key:string]:Json}=>v!==null&&typeof v==='object'&&!Array.isArray(v);

// Implements only the vocabulary used by the fixed core schemas, never supplied schemas.
function validateSchema(s:any,v:Json,root:any,pointer=''):void {
 if(s.$ref){const key=String(s.$ref).replace('#/$defs/','');if(!s.$ref.startsWith('#/$defs/')||!root.$defs?.[key])reject('PROFILE_SCHEMA_REF',pointer,'unknown core schema ref');return validateSchema(root.$defs[key],v,root,pointer);}
 if(s.oneOf){let count=0;for(const variant of s.oneOf){try{validateSchema(variant,v,root,pointer);count++;}catch(error){if(!(error instanceof ProfileRejected))throw error;}}if(count!==1)reject('PROFILE_SCHEMA_VARIANT',pointer,'one exact variant required');return;}
 if(s.const!==undefined&&canonicalJson(v)!==canonicalJson(s.const))reject('PROFILE_SCHEMA_CONST',pointer,'wrong schema/version/constant');
 if(s.enum&&!s.enum.some((item:Json)=>canonicalJson(item)===canonicalJson(v)))reject('PROFILE_SCHEMA_ENUM',pointer,'unsupported vocabulary');
 const kinds=s.type===undefined?[]:Array.isArray(s.type)?s.type:[s.type];
 const matches=(kind:string)=>kind==='null'?v===null:kind==='array'?Array.isArray(v):kind==='object'?object(v):kind==='integer'?typeof v==='number'&&Number.isSafeInteger(v):typeof v===kind;
 if(kinds.length&&!kinds.some(matches))reject('PROFILE_SCHEMA_TYPE',pointer,'wrong value type');
 if(typeof v==='string'){
  if(s.minLength!==undefined&&v.length<s.minLength||s.maxLength!==undefined&&v.length>s.maxLength)reject('PROFILE_SCHEMA_LIMIT',pointer,'string bounds');
  if(s.pattern&&!new RegExp(s.pattern,'u').test(v))reject('PROFILE_SCHEMA_PATTERN',pointer,'invalid identifier/path/value');
 }
 if(typeof v==='number'&&(s.minimum!==undefined&&v<s.minimum||s.maximum!==undefined&&v>s.maximum))reject('PROFILE_SCHEMA_LIMIT',pointer,'number bounds');
 if(Array.isArray(v)){
  if(s.minItems!==undefined&&v.length<s.minItems||s.maxItems!==undefined&&v.length>s.maxItems)reject('PROFILE_SCHEMA_LIMIT',pointer,'array bounds');
  if(s.uniqueItems&&new Set(v.map(canonicalJson)).size!==v.length)reject('PROFILE_SCHEMA_DUPLICATE',pointer,'duplicate item');
  if(s.items)v.forEach((item,i)=>validateSchema(s.items,item,root,`${pointer}/${i}`));
 }
 if(object(v)){
  const keys=Object.keys(v);
  if(s.minProperties!==undefined&&keys.length<s.minProperties||s.maxProperties!==undefined&&keys.length>s.maxProperties)reject('PROFILE_SCHEMA_LIMIT',pointer,'object bounds');
  for(const key of s.required??[])if(!Object.hasOwn(v,key))reject('PROFILE_SCHEMA_REQUIRED',`${pointer}/${key}`,'missing required field');
  for(const key of keys){
   if(s.propertyNames)validateSchema(s.propertyNames,key,root,`${pointer}/${key}`);
   if(Object.hasOwn(s.properties??{},key))validateSchema(s.properties[key],v[key]!,root,`${pointer}/${key}`);
   else if(s.additionalProperties===false)reject('PROFILE_SCHEMA_UNKNOWN_FIELD',`${pointer}/${key}`,'unknown field or executable hook');
   else if(object(s.additionalProperties))validateSchema(s.additionalProperties,v[key]!,root,`${pointer}/${key}`);
  }
 }
}
export function validateShape<T>(name:'project'|'package'|'lock'|'composition'|'coverage'|'project-v2'|'package-v2'|'business-application'|'capability-selection'|'context-manifest'|'release-ticket'|'trusted-search-context'|'continuation',input:unknown):T {
 if(!Object.hasOwn(schemas,name))reject('PROFILE_SCHEMA_REF','', 'unknown fixed core schema');
 const data=captureJson(input);validateSchema(schemas[name],data,schemas[name]);return data as T;
}
function unique(values:readonly string[],pointer:string){if(new Set(values).size!==values.length)reject('PROFILE_DUPLICATE_ID',pointer,'unique identities required');}
function sourcePath(value:string,pointer:string){if(value.startsWith('/')||value.split('/').some(p=>!p||p==='.'||p==='..')||value.includes('\\'))reject('PROFILE_SOURCE_PATH',pointer,'owned relative path required');}
export function validateProfileProject(input:unknown):ProfileProject {
 const data=validateShape<ProfileProject>('project',input);
 data.domain_sources.forEach((p,i)=>sourcePath(p,`/domain_sources/${i}`));sourcePath(data.integration_configuration,'/integration_configuration');
 unique(data.public_intents.map(x=>x.id),'/public_intents');unique(data.external_reads.map(x=>x.id),'/external_reads');unique(data.formal_claims.map(x=>x.id),'/formal_claims');unique(data.profiles.map(x=>x.id),'/profiles');
 for(const row of [...data.public_intents,...data.external_reads,...data.formal_claims])if(!data.domain_sources.includes(row.source))reject('PROFILE_PUBLIC_INTENT_UNKNOWN_REF',row.source,'undeclared business source');
 for(const row of data.public_intents)unique(row.outcomes.map(x=>x.code),`/public_intents/${row.id}/outcomes`);
 for(const row of data.application_calls??[])sourcePath(row.source,'/application_calls/source');
 unique([...data.public_intents.map(i=>i.id),...(data.application_calls??[]).map(i=>i.id)],'/public_intents/application_calls');
 if(data.public_intents.length+(data.application_calls?.length??0)>32)reject('PROFILE_ENTRY_BUDGET','/','at most 32 authored public entries');
 return data;
}
export function validateProfilePackage(input:unknown):ProfilePackage {
 const data=validateShape<ProfilePackage>('package',input);
 unique(data.rules.map(x=>x.id),'/rules');unique(data.assets.map(x=>x.id),'/assets');unique(data.assets.map(x=>x.path),'/assets/paths');unique(data.dependencies.map(x=>x.id),'/dependencies');unique(data.capabilities.map(x=>x.role),'/capabilities');
 for(const asset of data.assets){sourcePath(asset.path,`/assets/${asset.id}`);unique(asset.includes,`/assets/${asset.id}/includes`);if(asset.kind==='native'&&(asset.includes.length||Object.keys(asset.holes).length))reject('PROFILE_NATIVE_ASSET_CONTRACT',asset.id,'native assets are runtime components, not evaluator templates');}
 for(const capability of data.capabilities){const expected=PROFILE_ROLE_CONTRACTS[capability.role];if(capability.descriptor_ref!==expected.descriptor_ref||capability.recipe_ref!==expected.recipe_ref)reject('PROFILE_ROLE_MAPPING_UNSUPPORTED',capability.role,'missing exact registered descriptor/recipe mapping; no admission implied');}
 const byId=new Map(data.assets.map(x=>[x.id,x]));const done=new Set<string>(),active=new Set<string>();
 const visit=(id:string,depth=0)=>{if(depth>data.budgets.depth)reject('PROFILE_INCLUDE_BUDGET',id,'include depth budget exceeded');if(active.has(id))reject('PROFILE_INCLUDE_CYCLE',id,'cyclic includes');if(done.has(id))return;const asset=byId.get(id);if(!asset)reject('PROFILE_INCLUDE_MISSING',id,'include outside package closure');active.add(id);for(const child of asset.includes){if(byId.get(child)?.kind!=='template')reject('PROFILE_INCLUDE_KIND',child,'includes must reference owned template assets');visit(child,depth+1);}active.delete(id);done.add(id);};
 for(const id of byId.keys())visit(id);
 for(const rule of data.rules)if(rule.op==='emit'&&!data.capabilities.some(x=>x.role===rule.role))reject('PROFILE_ROLE_REQUIRED',rule.id,'missing generation capability role');
 return data;
}
/** Shape validation is not registered graph/plan currentness or semantic admission. */
export function validateCompositionShape(input:unknown):CompositionData {
 const data=validateShape<CompositionData>('composition',input);unique(data.components.map(x=>x.id),'/components');
 const byId=new Map(data.components.map(x=>[x.id,x])),paths=new Map<string,string>();
 for(const component of data.components){
  unique(component.depends_on,`/components/${component.id}/depends_on`);
  for(const file of component.artifact_paths){sourcePath(file,`/components/${component.id}/artifact_paths`);if(paths.has(file))reject('PROFILE_ARTIFACT_OWNER_CONFLICT',file,'one explicit artifact owner required');paths.set(file,component.owner);}
 }
 const active=new Set<string>(),done=new Set<string>();
 const visit=(id:string,depth=0)=>{if(depth>64)reject('PROFILE_COMPONENT_DEPTH',id,'component depth budget exceeded');if(active.has(id))reject('PROFILE_COMPONENT_CYCLE',id,'component dependencies must be acyclic');if(done.has(id))return;const component=byId.get(id);if(!component)reject('PROFILE_COMPONENT_MISSING',id,'unknown component dependency');active.add(id);for(const child of component.depends_on)visit(child,depth+1);active.delete(id);done.add(id);};
 for(const id of byId.keys())visit(id);return data;
}
export function validateCoverageShape(input:unknown):CoverageData {
 const data=validateShape<CoverageData>('coverage',input);unique(data.items.map(x=>x.id),'/items');
 for(const item of data.items){
  if(item.evidence_states.some(s=>s==='proved'||s==='admitted'))reject('PROFILE_EVIDENCE_STATE_UNSUPPORTED',item.id,'generation shape input cannot manufacture proof or admission');
  if(item.state==='claim-residue'&&item.kind!=='formal-claim')reject('PROFILE_CLAIM_RESIDUE_KIND',item.id,'required behavior cannot be hidden as claim residue');
 }
 return data;
}
