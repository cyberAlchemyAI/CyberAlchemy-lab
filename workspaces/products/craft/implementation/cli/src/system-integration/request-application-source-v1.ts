import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson} from '../input/source-manifest.js';
import {captureJson} from '../profile-engine/contracts.js';

/** Adapter-derived request carrier. No provider/runtime/observation partition.
 * Open questions: business application BA06/09/18 qualification. */
export interface RequestApplicationEntryV1 {
 readonly id:string; readonly operation_ref:string; readonly mapping_ref:string;
 readonly mapping_arguments:readonly Readonly<{parameter:string;path:readonly string[]}>[];
 readonly request_parameter:string; readonly route:Readonly<{method:'POST';path:string}>;
 readonly access:Readonly<{kind:'public'}>;
}
export interface RequestApplicationSourceV1 {
 readonly schema_version:'domainspec.request-application-source/v1-candidate';
 readonly source_id:string;readonly entries:readonly RequestApplicationEntryV1[];
}
export class RequestApplicationError extends Error {
 readonly exitCode=22;
 constructor(readonly code:string,readonly pointer:string,message:string){super(`${code}:${pointer}:${message}`);this.name='RequestApplicationError';}
}
export const requestApplicationFail=(code:string,pointer:string,message:string):never=>{throw new RequestApplicationError(code,pointer,message);};
const keys=(v:unknown,names:readonly string[],at:string):Record<string,unknown>=>{
 if(!v||typeof v!=='object'||Array.isArray(v)||canonicalJson(Object.keys(v).sort())!==canonicalJson([...names].sort()))return requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA',at,'closed fields required');return v as Record<string,unknown>;
};
const text=(v:unknown,re:RegExp,at:string):string=>typeof v==='string'&&v.length<=256&&re.exec(v)?.[0]===v?v:requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA',at,'bounded exact identifier required');
const list=(v:unknown,max:number,min:number,at:string):readonly unknown[]=>Array.isArray(v)&&v.length<=max&&v.length>=min?v:requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA',at,'bounded list required');
export const freezeRequestApplication=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freezeRequestApplication);Object.freeze(v);}return v;};
const local=/^[A-Za-z][A-Za-z0-9_-]*$/,selector=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/,field=/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
export function decodeRequestApplicationSourceV1(input:unknown):RequestApplicationSourceV1 {
 assertInterfaceData(input);const value=keys(input,['schema_version','source_id','entries'],'/');
 if(value.schema_version!=='domainspec.request-application-source/v1-candidate')requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA','/schema_version','explicit request carrier required');
 const source_id=text(value.source_id,local,'/source_id');
 const entries=list(value.entries,32,1,'/entries').map((entry,index)=>{
  const at='/entries/'+index,row=keys(entry,['id','operation_ref','mapping_ref','mapping_arguments','request_parameter','route','access'],at),route=keys(row.route,['method','path'],at+'/route'),access=keys(row.access,['kind'],at+'/access');
  if(route.method!=='POST'||access.kind!=='public')requestApplicationFail('DS_REQUEST_APPLICATION_UNSUPPORTED',at,'only explicit public POST supported');
  const path=text(route.path,/^\/[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*$/,at+'/route/path');
  const mapping_arguments=list(row.mapping_arguments,32,0,at+'/mapping_arguments').map((raw,i)=>{
   const arg=keys(raw,['parameter','path'],at+'/mapping_arguments/'+i);return {parameter:text(arg.parameter,field,at),path:list(arg.path,32,0,at).map(part=>text(part,local,at))};
  });
  if(new Set(mapping_arguments.map(a=>a.parameter)).size!==mapping_arguments.length)requestApplicationFail('DS_REQUEST_APPLICATION_DUPLICATE',at,'duplicate Mapping argument');
  return {id:text(row.id,local,at+'/id'),operation_ref:text(row.operation_ref,selector,at+'/operation_ref'),mapping_ref:text(row.mapping_ref,selector,at+'/mapping_ref'),mapping_arguments,request_parameter:text(row.request_parameter,field,at+'/request_parameter'),route:{method:'POST' as const,path},access:{kind:'public' as const}};
 });
 for(const [key,values]of [['id',entries.map(e=>e.id)],['route',entries.map(e=>e.route.path)]] as const)if(new Set(values).size!==values.length)requestApplicationFail('DS_REQUEST_APPLICATION_DUPLICATE','/entries/'+key,'duplicate public identity');
 return freezeRequestApplication({schema_version:'domainspec.request-application-source/v1-candidate',source_id,entries});
}

/** Logical successor intent. No route, callable, binding, native digest or custody.
 * Open Questions: Q02 original selected handle and U08 actual native binding. */
export const REQUEST_APPLICATION_SOURCE_V2_MODULE_URL=import.meta.url;
export interface RequestApplicationIntentFieldV2 {
 readonly name:string;readonly scalar:'UInt64'|'Bool';readonly identity:boolean;
 readonly source_property:string;readonly target_property:string;
}
export interface RequestApplicationEntryIntentV2 {
 readonly logical_id:string;readonly public_name:string;readonly operation_ref:string;readonly rule_ref:string;readonly interface_ref:string;
 readonly permission:Readonly<{kind:'public'}>;
 readonly payload:Readonly<{kind:'whole-input';parameter:string;type_ref:string}>;
 readonly mappings:Readonly<{input:string;output:string;fields:readonly RequestApplicationIntentFieldV2[]}>;
 readonly origins:readonly Readonly<{kind:'entry'|'permission'|'operation-input'|'entity-field';source:string;selector:string;sha256:string}>[];
}
export interface RequestApplicationIntentSourceV2 {
 readonly schema_version:'domainspec.request-application-source/v2-candidate';readonly model_id:string;
 readonly source_sha256:string;readonly executable_sha256:string;readonly entries:readonly RequestApplicationEntryIntentV2[];readonly authority_effect:'none';
}
const directHash=(v:unknown,at:string)=>text(v,/^[a-f0-9]{64}$/,at);
export function decodeRequestApplicationSourceV2(input:unknown):RequestApplicationIntentSourceV2 {
 const value=keys(captureJson(input),['schema_version','model_id','source_sha256','executable_sha256','entries','authority_effect'],'/');
 if(value.schema_version!=='domainspec.request-application-source/v2-candidate'||value.authority_effect!=='none')requestApplicationFail('DS_REQUEST_APPLICATION_VERSION','/','explicit successor intent required');
 text(value.model_id,/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/,'/model_id');directHash(value.source_sha256,'/source_sha256');directHash(value.executable_sha256,'/executable_sha256');
 for(const raw of list(value.entries,1,1,'/entries')){
  const row=keys(raw,['logical_id','public_name','operation_ref','rule_ref','interface_ref','permission','payload','mappings','origins'],'/entries');
  text(row.logical_id,/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/,'/logical_id');text(row.public_name,/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/,'/public_name');
  for(const name of ['operation_ref','rule_ref','interface_ref'])text(row[name],selector,'/'+name);
  const permission=keys(row.permission,['kind'],'/permission');if(permission.kind!=='public')requestApplicationFail('DS_REQUEST_APPLICATION_UNSUPPORTED','/permission','U0 requires explicit public logical entry');
  const payload=keys(row.payload,['kind','parameter','type_ref'],'/payload');if(payload.kind!=='whole-input')requestApplicationFail('DS_REQUEST_APPLICATION_UNSUPPORTED','/payload','whole-input intent required');
  for(const name of ['parameter','type_ref'])text(payload[name],/^[A-Za-z_][A-Za-z0-9_-]{0,127}$/,'/payload/'+name);
  const mappings=keys(row.mappings,['input','output','fields'],'/mappings');text(mappings.input,selector,'/mappings/input');text(mappings.output,selector,'/mappings/output');
  if(mappings.input===mappings.output)requestApplicationFail('DS_REQUEST_APPLICATION_DUPLICATE','/mappings','input/result Mapping roles are distinct');
  const roleSelectors=[row.operation_ref,row.rule_ref,row.interface_ref,mappings.input,mappings.output] as string[];
  if(new Set(roleSelectors).size!==5||new Set(roleSelectors.map(ref=>ref.split(':')[0])).size!==1)requestApplicationFail('DS_REQUEST_APPLICATION_DUPLICATE','/entries','distinct selected roles in one source feature required');
  const fields=list(mappings.fields,2,2,'/mappings/fields').map(rawField=>{
   const f=keys(rawField,['name','scalar','identity','source_property','target_property'],'/fields');
   text(f.name,/^[A-Za-z_][A-Za-z0-9_]{0,127}$/,'/fields/name');
   if(!['UInt64','Bool'].includes(f.scalar as string)||typeof f.identity!=='boolean'||f.identity!==(f.scalar==='UInt64'))requestApplicationFail('DS_REQUEST_APPLICATION_UNSUPPORTED','/fields','one UInt64 identity and one Bool field required');
   for(const key of ['source_property','target_property'])text(f[key],/^[A-Z][A-Z0-9-]+#[A-Za-z_][A-Za-z0-9_]*$/,'/fields/'+key);
   if(!(f.source_property as string).endsWith('#'+f.name)||!(f.target_property as string).endsWith('#'+f.name))requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA','/fields','explicit identity field correspondence required');
   return f;
  });
  if(new Set(fields.map(f=>f.name)).size!==2||new Set(fields.map(f=>f.scalar)).size!==2||new Set(fields.map(f=>f.source_property)).size!==2||new Set(fields.map(f=>f.target_property)).size!==2)requestApplicationFail('DS_REQUEST_APPLICATION_DUPLICATE','/fields','complete unique finite field inventory required');
  const origins=list(row.origins,5,5,'/origins').map(rawOrigin=>{
   const origin=keys(rawOrigin,['kind','source','selector','sha256'],'/origins');if(!['entry','permission','operation-input','entity-field'].includes(origin.kind as string))requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA','/origins','known original clause required');
   if(typeof origin.source!=='string'||!origin.source||origin.source.length>4096||origin.source.startsWith('/')||/[\\:\u0000-\u001f\u007f]/.test(origin.source)||origin.source.split('/').length>16||origin.source.split('/').some(part=>!part||part==='.'||part==='..'))requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA','/origins/source','portable original source path required');
   text(origin.selector,/^line:[1-9][0-9]*$/,'/origins/selector');directHash(origin.sha256,'/origins/sha256');
   if(origin.sha256!==value.source_sha256)requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA','/origins','original source hash required');return origin;
  });
  if(new Set(origins.map(row=>row.source)).size!==1||new Set(origins.map(row=>row.selector)).size!==5||origins.filter(o=>o.kind==='entity-field').length!==2||['entry','permission','operation-input'].some(kind=>origins.filter(o=>o.kind===kind).length!==1))requestApplicationFail('DS_REQUEST_APPLICATION_SCHEMA','/origins','exact original clause inventory required');
 }
 return value as unknown as RequestApplicationIntentSourceV2;
}
export function decodeVersionedRequestApplicationSource(input:unknown):RequestApplicationSourceV1|RequestApplicationIntentSourceV2 {
 const value=captureJson(input) as unknown as {schema_version?:unknown};
 if(value?.schema_version==='domainspec.request-application-source/v2-candidate')return decodeRequestApplicationSourceV2(value);
 if(value?.schema_version==='domainspec.request-application-source/v1-candidate')return decodeRequestApplicationSourceV1(value);
 return requestApplicationFail('DS_REQUEST_APPLICATION_VERSION','/schema_version','explicit supported request source version required');
}
