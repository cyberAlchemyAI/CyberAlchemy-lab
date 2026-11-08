import {captureJson,dataDigest,reject} from './contracts.js';
import {checkU0WireConfiguration,U0_NATIVE_ABI,U0_SUCCESSOR_DESCRIPTOR,type U0WireConfiguration} from './u0-realization-contract.js';
import {BUSINESS_AUTHORING_RECIPE_V2} from './business-authoring-protocol-v2.js';
/** Closed first v4 realization, not arbitrary native/profile extension support.
 * Open Questions: docs/U0-SHARED-CONTRACTS.md; EC profile-family work is separate. */
export const U0_PROFILE_V4='craft.profile-package/v4-candidate' as const;
export const U0_PROFILE_ENGINE_V4='craft.profile-engine/v4-candidate' as const;
export const U0_NATIVE_ROLE_EXPORTS_V4=Object.freeze({
 decoder:Object.freeze(['decodeU0Json']),values:Object.freeze(['formU0Submission','copyU0Submission']),
 encoder:Object.freeze(['checkU0EncoderConfiguration','encodeU0Outcome','encodeU0AdapterError','u0WireBounds']),
 handler:Object.freeze(['createU0HttpHandler','inspectU0HttpResponse']),
});
export type U0RuntimeRoleV4=keyof typeof U0_NATIVE_ROLE_EXPORTS_V4;
export interface U0RuntimeAssetV4 {readonly role:U0RuntimeRoleV4;readonly path:string;readonly sha256:string;readonly bytes:number;readonly exports:readonly string[]}
export interface ProfilePackageV4 {
 readonly schema_version:typeof U0_PROFILE_V4;readonly id:typeof U0_SUCCESSOR_DESCRIPTOR;readonly version:'1.0.0';readonly engine:typeof U0_PROFILE_ENGINE_V4;
 readonly source_contract:'alchlang.business-spec/v2-candidate';readonly recipe:typeof BUSINESS_AUTHORING_RECIPE_V2;
 readonly abi:typeof U0_NATIVE_ABI;readonly entry_access:'public';readonly effects:'none';
 readonly capabilities:readonly Readonly<{role:'application-operation'|'http-dispatch';descriptor_ref:string;recipe_ref:string}>[];
 readonly configuration:U0WireConfiguration;readonly assets:readonly U0RuntimeAssetV4[];
 readonly scalar_producer:Readonly<{path:'dist/generation/configured-exact-uint64-source.js';sha256:string;bytes:number;export_name:'renderExactUInt64Support'}>;
 readonly build:Readonly<{node:string;typescript:string}>;readonly authority_effect:'none';readonly open_questions_ref:string;
}
function fail(at:string,message:string):never{return reject('BUSINESS_PROFILE_V4',at,message);}
function closed(value:unknown,keys:readonly string[],at:string):asserts value is Record<string,unknown>{
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).sort().join(',')!==[...keys].sort().join(','))fail(at,'closed v4 contract fields required');
}
const hash=(value:unknown)=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
const bytes=(value:unknown)=>typeof value==='number'&&Number.isSafeInteger(value)&&value>0&&value<=16777216;
export const U0_PROFILE_CAPABILITIES_V4=Object.freeze([
 Object.freeze({role:'application-operation',descriptor_ref:U0_NATIVE_ABI,recipe_ref:BUSINESS_AUTHORING_RECIPE_V2}),
 Object.freeze({role:'http-dispatch',descriptor_ref:U0_SUCCESSOR_DESCRIPTOR,recipe_ref:'craft.u0.public-http/v1-candidate'}),
]);
export function validateProfilePackageV4(input:unknown):ProfilePackageV4 {
 const value=captureJson(input);closed(value,['schema_version','id','version','engine','source_contract','recipe','abi','entry_access','effects','capabilities','configuration','assets','scalar_producer','build','authority_effect','open_questions_ref'],'/');
 const constants={schema_version:U0_PROFILE_V4,id:U0_SUCCESSOR_DESCRIPTOR,version:'1.0.0',engine:U0_PROFILE_ENGINE_V4,source_contract:'alchlang.business-spec/v2-candidate',recipe:BUSINESS_AUTHORING_RECIPE_V2,abi:U0_NATIVE_ABI,entry_access:'public',effects:'none',authority_effect:'none'};
 for(const [key,expected]of Object.entries(constants))if(value[key]!==expected)fail('/'+key,'unsupported version/primitive/ABI/access/effects');
 if(dataDigest(value.capabilities)!==dataDigest(U0_PROFILE_CAPABILITIES_V4))fail('/capabilities','exact implemented v4 role contracts required');
 checkU0WireConfiguration(value.configuration);
 if(!Array.isArray(value.assets)||value.assets.length!==4)fail('/assets','four finite runtime assets required');
 const roles=new Set<string>(),paths=new Set<string>();
 for(const raw of value.assets as unknown[]){closed(raw,['role','path','sha256','bytes','exports'],'/assets');const role=raw.role as U0RuntimeRoleV4;
  if(!Object.hasOwn(U0_NATIVE_ROLE_EXPORTS_V4,role)||roles.has(role)||typeof raw.path!=='string'||!/^runtime\/[a-z][a-z0-9-]*\.m?js$/.test(raw.path)||paths.has(raw.path)||!hash(raw.sha256)||!bytes(raw.bytes)||dataDigest(raw.exports)!==dataDigest(U0_NATIVE_ROLE_EXPORTS_V4[role]))fail('/assets','unique actual role/path/hash/byte/export obligation required');
  roles.add(role);paths.add(raw.path);
 }
 closed(value.scalar_producer,['path','sha256','bytes','export_name'],'/scalar_producer');
 if(value.scalar_producer.path!=='dist/generation/configured-exact-uint64-source.js'||value.scalar_producer.export_name!=='renderExactUInt64Support'||!hash(value.scalar_producer.sha256)||!bytes(value.scalar_producer.bytes))fail('/scalar_producer','actual existing scalar producer required');
 closed(value.build,['node','typescript'],'/build');for(const [key,version]of Object.entries(value.build))if(typeof version!=='string'||!/^\d+\.\d+\.\d+$/.test(version))fail('/build/'+key,'actual exact tool version operand required');
 if(typeof value.open_questions_ref!=='string'||!value.open_questions_ref||value.open_questions_ref.length>256)fail('/open_questions_ref','explicit question owner required');
 return value as unknown as ProfilePackageV4;
}
