/** Data-only producer for the original protected HTTP and durable identity ports.
 * No client business evaluator, credential store or network listener is created.
 * Open Questions: docs/TECHNICAL-PROFILE-SOURCE.md#open-questions.
 */
import {dataDigest,reject} from './contracts.js';
import type {GenericHttpApplicationV1} from '../generic/http-data-v1.js';
import type {GenericTransactionApplicationContractV1} from '../generic/transaction-data-v1.js';
export const TECHNICAL_COMMAND_IDENTITY_ABI='craft.command-identity-store/v1';
export function renderTechnicalProfileCommandClient(input:{application:Pick<GenericTransactionApplicationContractV1,'application_namespace'|'values'>&Partial<Pick<GenericTransactionApplicationContractV1,'transaction_bounds'>>;applicationSha256:string;http:GenericHttpApplicationV1}){
 const {application,http}=input;
 if(!application.application_namespace||!http.entries.length||! /^[a-f0-9]{64}$/.test(input.applicationSha256))return reject('TECHNICAL_PROFILE_CLIENT','client','original application and HTTP contracts required');
 const routes=http.entries.filter(entry=>entry.route.method==='POST').map(entry=>({entry:entry.route.entry,service:entry.route.service,path:http.profile.route_prefix+entry.route.path,method:entry.route.method,entry_contract_sha256:entry.entry_contract_sha256,input_schema_sha256:dataDigest({parameters:entry.parameters,values:application.values}),source:entry.entry_source}));
 if(routes.some(route=>route.path.includes('{'))||new Set(routes.map(route=>route.entry)).size!==routes.length)return reject('TECHNICAL_PROFILE_CLIENT','client','one original command endpoint per Entry required');
 const contract={schema_version:'craft.generated-command-client/v1',application:application.application_namespace,application_contract_sha256:input.applicationSha256,identity_store_abi:TECHNICAL_COMMAND_IDENTITY_ABI,routes,limits:{request_bytes:http.profile.limits.request_bytes,response_bytes:http.profile.limits.response_bytes,command_key_bytes:Math.min(128,application.transaction_bounds?.max_command_key_bytes??128),command_key_scalars:Math.min(128,application.transaction_bounds?.max_command_key_scalars??128)},qualification:'original-durable-identity-port;original-server-auth-and-business-authority;single-explicit-send'};
 const source="import {randomUUID,createHash} from 'node:crypto';\nimport {types as hostTypes} from 'node:util';\nexport const contract=freeze("+JSON.stringify(contract)+");\n"+String.raw`
function fail(code,message){const error=new Error(message);error.code=code;throw error;}
function capture(value,depth=0,state={nodes:0}){
 if(++state.nodes>100000||depth>64)fail('ClientInputBound','Bounded JSON input required');
 if(value===null||typeof value==='boolean')return value;
 if(typeof value==='string'){for(let i=0;i<value.length;i++){const c=value.charCodeAt(i);if(c>=0xd800&&c<=0xdbff){const next=value.charCodeAt(++i);if(!(next>=0xdc00&&next<=0xdfff))fail('ClientInput','Valid Unicode input required');}else if(c>=0xdc00&&c<=0xdfff)fail('ClientInput','Valid Unicode input required');}return value;}
 if(typeof value==='number'&&Number.isFinite(value)&&Number.isSafeInteger(value))return value;
 if(!value||typeof value!=='object'||hostTypes.isProxy(value)||(Array.isArray(value)?Object.getPrototypeOf(value)!==Array.prototype:![Object.prototype,null].includes(Object.getPrototypeOf(value))))fail('ClientInput','Plain JSON input required');
 const descriptors=Object.getOwnPropertyDescriptors(value),keys=Reflect.ownKeys(descriptors);if(keys.some(key=>typeof key!=='string'||!Object.hasOwn(descriptors[key],'value')))fail('ClientInput','JSON values without accessors required');
 if(Array.isArray(value)){if(value.length>100000||keys.some(key=>key!=='length'&&!/^(0|[1-9][0-9]*)$/.test(key))||keys.length!==value.length+1)fail('ClientInput','Dense JSON list required');return Object.freeze(Array.from({length:value.length},(_,i)=>capture(descriptors[String(i)].value,depth+1,state)));}
 const result=Object.create(null);for(const key of keys.sort()){if(!descriptors[key].enumerable)fail('ClientInput','Enumerable JSON fields required');Object.defineProperty(result,key,{value:capture(descriptors[key].value,depth+1,state),enumerable:true});}return Object.freeze(result);
}
function text(value,name){if(typeof value!=='string'||!value||Buffer.byteLength(value)>512)fail('ClientConfiguration','Bounded '+name+' required');return value;}
function freeze(value){if(value&&typeof value==='object'&&!Object.isFrozen(value)){for(const child of Object.values(value))freeze(child);Object.freeze(value);}return value;}
async function observation(response){
 if(!(response instanceof Response))fail('ClientResponse','Original Response required');
 const copy=response.clone(),reader=copy.body?.getReader();if(!reader)fail('ClientResponse','Original response envelope required');let size=0;const chunks=[];
 try{for(;;){const next=await reader.read();if(next.done)break;size+=next.value.byteLength;if(size>contract.limits.response_bytes)fail('ClientResponseBound','Response limit exceeded');chunks.push(next.value);}const wire=Buffer.concat(chunks.map(value=>Buffer.from(value)));return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(wire));}finally{await reader.cancel().catch(()=>{});reader.releaseLock();}
}
export function createClient(configuration){
 const {identityStore,baseUrl,subject,tenant=null,headers,fetch:transport=globalThis.fetch,retentionMs=86400000}=configuration;
 if(!identityStore||!['prepare','inspect','observe'].every(name=>typeof identityStore[name]==='function')||typeof transport!=='function')fail('ClientConfiguration','Compatible durable identity port and fetch resource required');
 text(subject,'subject');if(tenant!==null)text(tenant,'tenant');const base=new URL(baseUrl);if(!['http:','https:'].includes(base.protocol)||base.username||base.password||base.search||base.hash)fail('ClientConfiguration','Explicit HTTP destination without credentials/query/fragment required');
 const endpointPrefix=base.pathname.replace(/\/$/,''),fixedHeaders=typeof headers==='function'?null:new Headers(headers),rows=new WeakMap(),inFlight=new WeakSet();
 const routeFor=entry=>{const matches=contract.routes.filter(route=>route.entry===entry);if(matches.length!==1)fail('ClientEntry','One generated command Entry required');return matches[0];};
 const state=command=>{const row=rows.get(command);if(!row)fail('ClientCommand','Original prepared client command required');return row;};
 const checkedIdentity=value=>{if(!value||typeof value.client_key!=='string'||!value.client_key.isWellFormed()||!value.client_key.length||Buffer.byteLength(value.client_key)>contract.limits.command_key_bytes||[...value.client_key].length>contract.limits.command_key_scalars||value.header!==Buffer.from(value.client_key,'utf8').toString('base64url'))fail('ClientIdentityCompatibility','Durable key/header must satisfy the original server command bounds');return value;};
 const current=row=>{const identity=checkedIdentity(identityStore.prepare(row.request));if(identity.client_key!==row.identity.client_key||identity.header!==row.identity.header)fail('ClientIdentity','Original durable allocation changed');return identityStore.inspect({scope:row.request.scope,logicalCommand:row.logicalCommand});};
 const observeUnknown=row=>{const prior=identityStore.inspect({scope:row.request.scope,logicalCommand:row.logicalCommand});if(prior?.state!=='completed')identityStore.observe({scope:row.request.scope,logicalCommand:row.logicalCommand,state:'unknown'});};
 return Object.freeze({
  prepare(entry,input,{logicalCommand=randomUUID(),entities=[],children=[]}={}){
   const route=routeFor(entry),body=capture(input),wire=JSON.stringify(body);if(Buffer.byteLength(wire)>contract.limits.request_bytes)fail('ClientInputBound','Request limit exceeded');
   text(logicalCommand,'logical command');const endpoint=new URL(base.origin);endpoint.pathname=endpointPrefix+route.path;
   const scopedEntry=JSON.stringify({service:route.service,entry:route.entry}),scope=freeze({application:contract.application,subject,entry:Buffer.byteLength(scopedEntry)<=256?scopedEntry:'sha256:'+createHash('sha256').update(scopedEntry).digest('hex'),tenant}),request=freeze({scope,logicalCommand,payload:{application_contract_sha256:contract.application_contract_sha256,entry_contract_sha256:route.entry_contract_sha256,input_schema_sha256:route.input_schema_sha256,endpoint:{url:endpoint.href,method:route.method},input:body},entities:capture(entities),children:capture(children),retentionMs}),identity=checkedIdentity(identityStore.prepare(request)),command=Object.freeze({kind:'craft-prepared-client-command/v1'});
   rows.set(command,{request,logicalCommand,identity,wire,url:endpoint.href,route});return freeze({command,logicalCommand,allocations:{entities:identity.entities,children:identity.children}});
  },
  inspect(command){const row=state(command),stored=identityStore.inspect({scope:row.request.scope,logicalCommand:row.logicalCommand});return freeze({logicalCommand:row.logicalCommand,entry:row.route.entry,endpoint:row.url,...stored});},
  async send(command,{signal}={}){
   const row=state(command);if(inFlight.has(command))fail('ClientConcurrentSend','One explicit send at a time per handle');inFlight.add(command);let attempted=false;
   try{current(row);const supplied=typeof headers==='function'?await headers():fixedHeaders,actual=new Headers(supplied);if(actual.has('x-craft-command-key')||actual.has('content-type')||actual.has('content-length'))fail('ClientHeaders','Command identity and JSON framing are generated');actual.set('content-type','application/json');actual.set('x-craft-command-key',row.identity.header);current(row);
    const request=new Request(row.url,{method:'POST',headers:actual,body:row.wire,redirect:'manual',cache:'no-store',...(signal?{signal}:{})});attempted=true;const response=await transport(request);const result=await observation(response);
    if(result.schema_version==='craft.generic-http-result/v1-candidate'&&['committed','replayed','business-rejected','business-failed','commit-observed-result-withheld'].includes(result.observation?.kind))identityStore.observe({scope:row.request.scope,logicalCommand:row.logicalCommand,state:'completed'});else observeUnknown(row);
    return response;
   }catch(error){if(!attempted)throw error;try{observeUnknown(row);}catch(storeError){throw new AggregateError([error,storeError],'Send and durable observation failed');}throw error;}finally{inFlight.delete(command);}
  }
 });
}
`;
 return {contract,source};
}
