import {types} from 'node:util';
import {businessCanonical,businessHash,businessReject,businessSourceKey} from './business-authoring-model.js';
import type {BusinessSpecDataV2,DirectExecutableProjectionV2,OptionalAssuranceProjectionV2} from './business-authoring-protocol-v2.js';
import type {BusinessCaptureManifestV2,BusinessCaptureIdentityV2,BusinessReviewSubjectV2} from './business-authoring-identity-protocol-v2.js';
/** Independently computed frontend projections. Data never supplies original Core custody.
 * Open Questions: Core docs/BUSINESS-IDENTITIES-V2.md. */
const fail=(detail:string):never=>businessReject('BUSINESS_IDENTITY_V2','business.alch',1,1,detail);
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const sorted=<T extends {readonly id:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>compare(a.id,b.id));
const named=<T extends {readonly name:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>compare(a.name,b.name));
function inert<T>(input:unknown):T {
 let nodes=0,bytes=0;
 const walk=(value:unknown,depth:number):unknown=>{
  if(++nodes>100000||depth>64)fail('bounded captured identity data required');
  if(value===null||typeof value==='boolean')return value;
  if(typeof value==='string'){bytes+=Buffer.byteLength(value);if(bytes>16777216||/[\uD800-\uDFFF]/u.test(value))fail('bounded Unicode scalar data required');return value;}
  if(typeof value==='number'){if(!Number.isSafeInteger(value))fail('safe integer data required');return value;}
  if(!value||typeof value!=='object'||types.isProxy(value))return fail('plain inert data required');
  const array=Array.isArray(value),proto=Object.getPrototypeOf(value);
  if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)fail('ordinary data containers required');
  const descriptors=Object.getOwnPropertyDescriptors(value),keys=Reflect.ownKeys(descriptors);
  if(array){const length=descriptors.length!.value as number;if(length>10000||keys.length!==length+1)fail('bounded dense array required');const rows:unknown[]=[];for(let i=0;i<length;i++){const field=descriptors[String(i)];if(!field||!('value' in field)||!field.enumerable)fail('inert array member required');rows.push(walk(field!.value,depth+1));}return Object.freeze(rows);}
  if(keys.length>2048)fail('bounded object required');const result:Record<string,unknown>=Object.create(null);
  for(const key of keys){const field=descriptors[key as string];if(typeof key!=='string'||!field||!('value' in field)||!field.enumerable)fail('inert enumerable members required');bytes+=Buffer.byteLength(key as string);if(bytes>16777216)fail('bounded keys required');result[key as string]=walk(field!.value,depth+1);}return Object.freeze(result);
 };return walk(input,0) as T;
}
function specData(input:BusinessSpecDataV2):BusinessSpecDataV2 {
 const value=inert<BusinessSpecDataV2>(input);
 const expected=['schema_version','identity','requirements','entities','definitions','claims','rules','operations','entries','source_spans','obligations','authority_effect'];
 if(value.schema_version!=='alchlang.business-spec/v2-candidate'||value.authority_effect!=='none'||Object.keys(value).length!==expected.length||Object.keys(value).some(key=>!expected.includes(key)))fail('exact v2 source contract required');
 for(const key of ['requirements','entities','definitions','claims','rules','operations','entries','source_spans','obligations'] as const)if(!Array.isArray(value[key]))fail('declared source list required');
 return value;
}
export function projectAlchDirectExecutableV2(input:BusinessSpecDataV2):DirectExecutableProjectionV2 {
 const spec=specData(input);
 return inert({schema_version:'craft.business-executable/v2-candidate',normalization_contract:'craft.business-authoring-contracts/2-candidate',
  identity:spec.identity,requirements:sorted(spec.requirements),entities:sorted(spec.entities).map(entity=>({...entity,fields:named(entity.fields)})),
  rules:sorted(spec.rules).map(({id,requirement_ref,input,condition})=>({id,requirement_ref,input,condition})),operations:sorted(spec.operations),entries:sorted(spec.entries),authority_effect:'none'});
}
export function projectAlchOptionalAssuranceV2(input:BusinessSpecDataV2):OptionalAssuranceProjectionV2 {
 const spec=specData(input);return inert({schema_version:'craft.business-assurance/v2-candidate',definitions:sorted(spec.definitions),
  claims:sorted(spec.claims).map(claim=>({...claim,sorts:named(claim.sorts),predicates:named(claim.predicates),constants:named(claim.constants),subject_refs:[...claim.subject_refs].sort(compare)})),authority_effect:'none'});
}
export const alchDirectExecutableDigestV2=(spec:BusinessSpecDataV2):string=>businessHash(businessCanonical(projectAlchDirectExecutableV2(spec)));
export const alchOptionalAssuranceDigestV2=(spec:BusinessSpecDataV2):string=>businessHash(businessCanonical(projectAlchOptionalAssuranceV2(spec)));
export function captureAlchBusinessIdentityV2(input:BusinessCaptureManifestV2):BusinessCaptureIdentityV2 {
 const manifest=inert<BusinessCaptureManifestV2>(input);
 const keys=(value:unknown,expected:readonly string[])=>{if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==expected.length||Object.keys(value).some(key=>!expected.includes(key)))fail('closed capture fields required');};
 keys(manifest,['schema_version','recipe_ref','source','profiles','tools','authority_effect']);
 if(manifest.schema_version!=='craft.business-capture/v2-candidate'||manifest.recipe_ref!=='direct-entity-bool-operation/v2-candidate'||manifest.authority_effect!=='none')fail('fixed capture contract required');
 keys(manifest.source,['path','sha256','bytes']);
 businessSourceKey(manifest.source.path);
 const sha=(value:unknown)=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
 const id=(value:unknown)=>typeof value==='string'&&/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/.test(value);
 if(!sha(manifest.source.sha256)||!Number.isSafeInteger(manifest.source.bytes)||manifest.source.bytes<1||manifest.source.bytes>1048576)fail('exact bounded source identity required');
 for(const [kind,rows] of [['profiles',manifest.profiles],['tools',manifest.tools]] as const){
  if(!Array.isArray(rows)||rows.length<1||rows.length>64)fail('bounded artifact list required');
  for(const row of rows){keys(row,kind==='profiles'?['id','version','sha256']:['id','sha256']);if(!id(row.id)||!sha(row.sha256))fail('exact artifact identity required');if(kind==='profiles'){const version=(row as {version:string}).version;if(typeof version!=='string'||version.length<1||[...version].length>256)fail('exact profile version field required');}}
  if(new Set(rows.map(row=>row.id)).size!==rows.length)fail('duplicate artifact identity');
 }
 const body={...manifest,profiles:sorted(manifest.profiles),tools:sorted(manifest.tools)};return inert({...body,capture_sha256:businessHash(businessCanonical(body))});
}
export function projectAlchBusinessReviewSubjectV2(input:BusinessSpecDataV2):BusinessReviewSubjectV2 {
 const spec=specData(input);return inert({schema_version:'craft.business-review/v2-candidate',normalization_contract:'craft.business-authoring-contracts/2-candidate',model_id:spec.identity.namespace,owner:spec.identity.owner,version:spec.identity.version,authored_rules:sorted(spec.rules),executable:projectAlchDirectExecutableV2(spec),executable_sha256:alchDirectExecutableDigestV2(spec),assurance:projectAlchOptionalAssuranceV2(spec),assurance_sha256:alchOptionalAssuranceDigestV2(spec),authority_effect:'none'});
}
