import type {HttpInvocation,HttpAttempt,BindingIdentity,InvocationJson,InvocationControl} from './integration-runtime-types.js';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {defaultDomainSpecPackageRoot} from './domainspec-cli.js';
const httpRuntimePath=path.join(defaultDomainSpecPackageRoot(),'dist/runtime/http-invocation.js');
const {validateHttpBindingPolicy}=await import(pathToFileURL(httpRuntimePath).href) as {validateHttpBindingPolicy:(input:unknown)=>any};
// Fixed operator bindings and resource custody. Contract/Open Questions: ../OUTBOUND.md.
const fail=(code:string):never=>{throw Object.assign(new Error(code),{code});};
export function createHttpInvocation({bindings,fetchImpl=fetch,allowLoopbackFixtures=false,now=()=>performance.now()}:any){
 const configured=new Map<string,any>();
 for(const b of bindings){let url:URL;try{url=new URL(b.url);}catch{return fail('INVALID_PROVIDER_URL');}
  const loopback=['127.0.0.1','[::1]'].includes(url.hostname);
  const policy=b.policy===undefined?undefined:validateHttpBindingPolicy(b.policy);
  const permitted=policy?(policy.scope==='loopback'?loopback&&['http:','https:'].includes(url.protocol):url.protocol==='https:'):(url.protocol==='https:'||allowLoopbackFixtures&&loopback&&url.protocol==='http:');
  if(url.username||url.password||url.hash||url.search||!permitted)fail('INVALID_PROVIDER_URL');
  if(configured.has(b.id)||[b.id,b.version,b.model,b.remoteModel??b.model].some(v=>typeof v!=='string'||!v.trim()||v.length>128)||(policy?.authentication==='none'?b.secret!==undefined:typeof b.secret!=='string'||!b.secret))fail('INVALID_BINDING');
  configured.set(b.id,Object.freeze({...b,policy,url:url.href}));
 }
 const resolveBinding=(identity:any)=>{const b=configured.get(identity.id);if(!b||b.version!==identity.version||b.model!==identity.model)fail('BINDING_MISMATCH');return {id:b.id,version:b.version,model:b.model,remote_model:b.remoteModel??b.model};};
 const sendOnce:HttpInvocation['sendOnce']=(identity:BindingIdentity,body:InvocationJson,control:InvocationControl):HttpAttempt=>{
  const b=configured.get(identity.id);if(!b||b.version!==identity.version||b.model!==identity.model)fail('BINDING_MISMATCH');
  const controller=new AbortController();let reader:ReadableStreamDefaultReader<Uint8Array>|undefined,cancelPromise:Promise<void>|undefined,ended=false,started=false;
  let settle!:()=>void;const settled=new Promise<void>(r=>{settle=r;});
  const finish=()=>{if(ended)return;ended=true;control.signal.removeEventListener('abort',onAbort);settle();};
  const cancel=async(reason:any)=>{controller.abort(reason);if(reader&&!ended){cancelPromise??=reader.cancel().then(()=>{finish();},()=>{finish();});await cancelPromise;}};
  const onAbort=()=>{void cancel(control.signal.reason).catch(()=>{});};control.signal.addEventListener('abort',onAbort,{once:true});
  const response=(async()=>{
   try{
    if(control.signal.aborted||now()>=control.deadline){controller.abort(control.signal.reason);fail('CANCELLED');}
    const response=await fetchImpl(b.url,{method:'POST',redirect:'manual',headers:{'content-type':'application/json',...(b.policy?.authentication==='none'?{}:{authorization:'Bearer '+b.secret})},body:JSON.stringify(body),signal:controller.signal});
    reader=response.body?.getReader();if(!reader){finish();fail('INVALID_PROVIDER_RESPONSE');}
    if(controller.signal.aborted){await cancel(controller.signal.reason);fail('CANCELLED');}
    const bytes:AsyncIterable<Uint8Array>={async *[Symbol.asyncIterator](){if(started)fail('BODY_ALREADY_CONSUMED');started=true;try{for(;;){const result=await reader!.read();if(result.done){finish();return;}yield result.value;}}finally{await cancel('invalid-response');reader!.releaseLock();}}};
    return {status:response.status,mediaType:response.headers.get('content-type')??'',body:bytes};
   }catch(error){if(reader)await cancel('invalid-response');else finish();throw error;}
  })();
  return {response,settled,cancel};
 };
 return {http:{sendOnce},resolveBinding};
}
/** Bridge only: the existing native SSE lifecycle consumes Web Response bytes. */
export function exchangeResponse(exchange:any,cancel:()=>Promise<void>){const iterator=exchange.body[Symbol.asyncIterator]();return new Response(new ReadableStream({async pull(c){try{const {done,value}=await iterator.next();if(done)c.close();else c.enqueue(value);}catch(e){c.error(e);}},async cancel(){await cancel();await iterator.return?.();}}),{status:exchange.status,headers:{'content-type':exchange.mediaType}});}
