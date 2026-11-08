/** Offline external contract selection and typed port projection.
 * No native adapter is executed or qualified by this module.
 * Open Questions: research/are-lab-agent-runtime-2026-10-27/craft-alchlang/LAB-PROFILES-RESEARCH-DESIGN.md.
 */
import {createHash} from 'node:crypto';
import {readFileSync, realpathSync} from 'node:fs';
import path from 'node:path';

const DIALECT='https://json-schema.org/draft/2020-12/schema';
const hash=(bytes:Buffer|string)=>createHash('sha256').update(bytes).digest('hex');
const refuse=(reason:string):never=>{throw new Error(`EXTERNAL_CONTRACT:${reason}`);};
const capturedSlices=new WeakSet<object>();
function parseExactJson(raw:Buffer):any {
 const source=raw.toString('utf8'),stack:Set<string>[]=[];
 try{
  for(let i=0;i<source.length;i++){
   if(source[i]==='{')stack.push(new Set());else if(source[i]==='}')stack.pop();
   else if(source[i]==='"'){
    const start=i;for(i++;i<source.length&&source[i]!=='"';i++)if(source[i]==='\\')i++;
    if(i>=source.length)refuse('invalid-json');
    let end=i+1;while(/[\t\n\r ]/.test(source[end]??'x'))end++;
    if(source[end]===':'&&stack.length){const key=JSON.parse(source.slice(start,i+1)) as string,keys=stack[stack.length-1]!;
     if(keys.has(key))refuse('duplicate-json-key');keys.add(key);}
   }
  }
  return JSON.parse(source);
 }catch(error){if(error instanceof Error&&error.message.startsWith('EXTERNAL_CONTRACT:'))throw error;return refuse('invalid-json');}
}
export interface ExternalResourceBinding {readonly ref:string;readonly sha256:string}
export interface CapturedExternalResource extends ExternalResourceBinding {readonly uri:string;readonly bytes:number}
export interface ExternalContractSlice {readonly catalog:ExternalResourceBinding;readonly supporting_sources:readonly ExternalResourceBinding[];readonly resources:readonly CapturedExternalResource[];readonly lock_sha256:string;assertCurrent():void}
export interface ExternalPortEntry {readonly source_sha256:string;readonly module:string;readonly id:string;readonly invokes:string;readonly interaction:'request-response'|'event';readonly permission:string;readonly auth_resource:string;readonly auth_action:string;readonly auth_scope:string}
export interface ExternalPortOperation {readonly id:string;readonly branch:string;readonly effect:string;readonly caller_requirement:string;readonly implementation_status:string;readonly schemas:Readonly<{request:Readonly<{uri:string;sha256:string}>;result:Readonly<{uri:string;sha256:string}>;error:Readonly<{uri:string;sha256:string}>}>}
export interface ExternalPortBinding {readonly schema_version:'craft.external-port-binding/v1-candidate';readonly entry:string;readonly invokes:string;readonly operation:string;readonly permission:string;readonly caller_requirement:string;readonly authority_effect:'none'}
export function validateExternalPortBinding(value:unknown):ExternalPortBinding {
 if(!value||typeof value!=='object'||Array.isArray(value))refuse('invalid-binding');
 const b=value as Record<string,unknown>;
 if(JSON.stringify(Object.keys(b).sort())!==JSON.stringify(['schema_version','entry','invokes','operation','permission','caller_requirement','authority_effect'].sort())||
  b.schema_version!=='craft.external-port-binding/v1-candidate'||b.authority_effect!=='none'||
  ['entry','invokes','operation','permission','caller_requirement'].some(k=>typeof b[k]!=='string'||!b[k]))refuse('invalid-binding');
 return Object.freeze({schema_version:'craft.external-port-binding/v1-candidate',entry:b.entry as string,invokes:b.invokes as string,
  operation:b.operation as string,permission:b.permission as string,caller_requirement:b.caller_requirement as string,authority_effect:'none'});
}
export const EXTERNAL_OFFLINE_ROLES=Object.freeze(['external-contract-source','typed-native-port'] as const);
export interface ExternalPortProfile {readonly schema_version:'craft.external-port-profile/v1-candidate';readonly id:string;readonly version:string;readonly capabilities:readonly typeof EXTERNAL_OFFLINE_ROLES[number][];readonly effect_scope:'offline-only';readonly authority_effect:'none'}
export function validateExternalPortProfile(value:unknown):ExternalPortProfile {
 if(!value||typeof value!=='object'||Array.isArray(value))refuse('invalid-profile');
 const p=value as Record<string,unknown>;
 if(JSON.stringify(Object.keys(p).sort())!==JSON.stringify(['schema_version','id','version','capabilities','effect_scope','authority_effect'].sort())||
  p.schema_version!=='craft.external-port-profile/v1-candidate'||typeof p.id!=='string'||!/^[a-z][a-z0-9.-]+$/.test(p.id)||
  typeof p.version!=='string'||!/^\d+\.\d+\.\d+$/.test(p.version)||p.effect_scope!=='offline-only'||p.authority_effect!=='none'||
  JSON.stringify(p.capabilities)!==JSON.stringify(EXTERNAL_OFFLINE_ROLES))refuse('unsupported-profile-role-contract');
 return Object.freeze({schema_version:'craft.external-port-profile/v1-candidate',id:p.id as string,version:p.version as string,
  capabilities:EXTERNAL_OFFLINE_ROLES,effect_scope:'offline-only',authority_effect:'none'}) satisfies ExternalPortProfile;
}

function readBound(root:string,ref:string,expected:string):Buffer {
 if(typeof ref!=='string'||!ref||path.isAbsolute(ref)||ref.split('/').some(p=>p==='..'||p==='.'||!p)||ref.includes('\\'))refuse('invalid-resource-path');
 if(!/^[a-f0-9]{64}$/.test(expected))refuse('invalid-resource-digest');
 const base=realpathSync(root),file=realpathSync(path.join(base,ref));
 if(!file.startsWith(base+path.sep))refuse('resource-escapes-root');
 const bytes=readFileSync(file);if(bytes.length>1024*1024)refuse('resource-too-large');
 if(hash(bytes)!==expected)refuse(`digest-mismatch:${ref}`);return bytes;
}
function pointer(document:unknown,fragment:string):void {
 if(!fragment)return;if(!fragment.startsWith('/'))refuse('unsupported-fragment');
 let value:any=document;for(const part of fragment.slice(1).split('/')){
  const key=decodeURIComponent(part).replace(/~1/g,'/').replace(/~0/g,'~');
  if(!value||typeof value!=='object'||!Object.hasOwn(value,key))refuse(`missing-fragment:${fragment}`);
  value=value[key];
 }
}
function references(value:unknown,out:string[]):void {
 if(Array.isArray(value)){for(const child of value)references(child,out);return;}
 if(!value||typeof value!=='object')return;
 for(const [key,child] of Object.entries(value)){
  if(key==='$ref'||key==='$dynamicRef'){if(typeof child!=='string')refuse('invalid-reference');out.push(child);}
  else references(child,out);
 }
}
/** Capture raw selected bytes and the transitive local JSON Schema resource closure. */
export function captureExternalContractSlice(input:Readonly<{root:string;catalog:ExternalResourceBinding;supporting_sources?:readonly ExternalResourceBinding[];bindings:readonly ExternalResourceBinding[];root_uris:readonly string[]}>):ExternalContractSlice {
 if(input.bindings.length>128||input.root_uris.length<1||input.root_uris.length>16)refuse('resource-limit');
 parseExactJson(readBound(input.root,input.catalog.ref,input.catalog.sha256));
 const supporting_sources=input.supporting_sources??[];
 if(supporting_sources.length>8)refuse('supporting-source-limit');
 for(const source of supporting_sources)readBound(input.root,source.ref,source.sha256);
 const index=new Map<string,{binding:ExternalResourceBinding;document:any;bytes:number}>();
 const refs=new Set<string>();
 for(const binding of input.bindings){if(refs.has(binding.ref))refuse('duplicate-resource-path');refs.add(binding.ref);
  const raw=readBound(input.root,binding.ref,binding.sha256);const document=parseExactJson(raw);
  if(typeof document?.$id!=='string'||!document.$id||index.has(document.$id))refuse('missing-or-duplicate-id');
  index.set(document.$id,{binding,document,bytes:raw.length});
 }
 const selected=new Map<string,CapturedExternalResource>();const queue=[...input.root_uris];
 while(queue.length){const uri=queue.shift()!;if(selected.has(uri))continue;
  const row=index.get(uri);if(!row)throw new Error(`EXTERNAL_CONTRACT:unresolved-uri:${uri}`);
  if(row.document.$schema!==DIALECT)refuse(`unsupported-dialect:${uri}`);
  const links:string[]=[];references(row.document,links);
  for(const link of links){const split=link.indexOf('#'),base=split<0?link:link.slice(0,split),fragment=split<0?'':link.slice(split+1),target=base||uri;
   const targetRow=index.get(target);if(!targetRow)throw new Error(`EXTERNAL_CONTRACT:unresolved-uri:${target}`);
   pointer(targetRow.document,fragment);if(!selected.has(target))queue.push(target);
  }
  selected.set(uri,{...row.binding,uri,bytes:row.bytes});
  if(selected.size>64)refuse('selected-resource-limit');
 }
 const resources=[...selected.values()].sort((a,b)=>a.uri.localeCompare(b.uri));
 const lock_sha256=hash(JSON.stringify({catalog:input.catalog,supporting_sources,resources}));
 const assertCurrent=()=>{readBound(input.root,input.catalog.ref,input.catalog.sha256);for(const source of supporting_sources)readBound(input.root,source.ref,source.sha256);
  for(const resource of resources)readBound(input.root,resource.ref,resource.sha256);};
 const value=Object.freeze({catalog:Object.freeze({...input.catalog}),supporting_sources:Object.freeze(supporting_sources.map(s=>Object.freeze({...s}))),resources:Object.freeze(resources.map(r=>Object.freeze(r))),lock_sha256,assertCurrent});
 capturedSlices.add(value);return value;
}

/** Project an exact authored entry binding to a declared external operation. */
export function composeExternalContractPort(input:Readonly<{profile:ExternalPortProfile;entry:ExternalPortEntry;binding:ExternalPortBinding;operation:ExternalPortOperation;slice:ExternalContractSlice}>){
 const {entry,operation,slice}=input;if(!slice||!capturedSlices.has(slice))refuse('unregistered-contract-slice');slice.assertCurrent();
 const profile=validateExternalPortProfile(input.profile),binding=validateExternalPortBinding(input.binding),profile_lock_sha256=hash(JSON.stringify(profile)),binding_lock_sha256=hash(JSON.stringify(binding));
 if(entry.id!==binding.entry||entry.invokes!==binding.invokes||entry.permission!==binding.permission||operation.id!==binding.operation||operation.caller_requirement!==binding.caller_requirement)refuse('entry-operation-binding-mismatch');
 if(entry.interaction!=='request-response'||operation.effect!=='read-only')refuse('unsupported-first-slice');
 if(!/^[a-f0-9]{64}$/.test(entry.source_sha256))refuse('invalid-source-digest');
 for(const schema of Object.values(operation.schemas))if(!slice.resources.some(r=>r.uri===schema.uri&&r.sha256===schema.sha256))refuse(`missing-selected-schema:${schema.uri}`);
 const descriptor=Object.freeze({schema_version:'craft.external-port-descriptor/v1-candidate',operation:operation.id,branch:operation.branch,effect:operation.effect,
  caller_requirement:operation.caller_requirement,entry_permission:entry.permission,auth_resource:entry.auth_resource,auth_action:entry.auth_action,auth_scope:entry.auth_scope,
  schemas:operation.schemas,contract_lock_sha256:slice.lock_sha256,profile_lock_sha256,binding_lock_sha256,implementation_status:operation.implementation_status,runtime_readiness:'unavailable',native_adapter:null,authority_effect:'none'});
 const business_graph=Object.freeze({nodes:[{id:entry.id,kind:'Entry',source_sha256:entry.source_sha256},{id:entry.invokes,kind:'OperationReference',resolution:'not-compiled'}],edges:[{from:entry.id,to:entry.invokes,kind:'invokes'}]});
 const system_graph=Object.freeze({nodes:[{id:operation.id,kind:'ExternalOperation',branch:operation.branch,effect:operation.effect},...slice.resources.map(r=>({id:r.uri,kind:'SchemaResource',sha256:r.sha256}))],edges:Object.entries(operation.schemas).map(([kind,schema])=>({from:operation.id,to:schema.uri,kind:`${kind}-schema`}))});
 const bridge=Object.freeze({edges:[{from:entry.invokes,to:operation.id,kind:'explicit-contract-binding',entry:entry.id},{from:entry.permission,to:operation.caller_requirement,kind:'declared-permission-mapping',authorization:'unverified'}],contract_lock_sha256:slice.lock_sha256,profile_lock_sha256,binding_lock_sha256,source_sha256:entry.source_sha256});
 return Object.freeze({descriptor,business_graph,system_graph,bridge});
}
