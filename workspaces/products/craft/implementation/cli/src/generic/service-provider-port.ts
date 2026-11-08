/** Bounded DemoPay-v1 HTTP port for generated service runtimes. The endpoint is
 * deployment configuration; the protocol, request shape and outcome rules remain
 * owned by the original checked native adapter.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {DemoPayRawHttpPort,DemoPayWireRequest} from './external-write-runtime.js';

const maximumResponseBytes=8193;

export function createGenericDemoPayFetchPort(endpoint:string):DemoPayRawHttpPort{
 let origin:URL;
 try{origin=new URL(endpoint);}catch{throw Error('C14_PROVIDER_ENDPOINT');}
 if(origin.href!==origin.origin+'/'||origin.username||origin.password||origin.search||origin.hash||
   !(origin.protocol==='https:'||origin.protocol==='http:'&&['127.0.0.1','[::1]','localhost'].includes(origin.hostname)))
  throw Error('C14_PROVIDER_ENDPOINT');
 return Object.freeze({async exchange(request:DemoPayWireRequest){
  if(request.origin!=='https://demopay.invalid'||request.method!=='POST'||
    !['/v1/capture','/v1/capture/inspect'].includes(request.path)||
    request.headers['content-type']!=='application/json; charset=utf-8'||
    request.headers['demopay-protocol']!=='1'||!(request.body instanceof Uint8Array)||
    request.body.byteLength>4096||!(request.signal instanceof AbortSignal))
   throw Error('C14_PROVIDER_REQUEST');
  const response=await fetch(new URL(request.path,origin),{method:'POST',headers:request.headers,
   body:Buffer.from(request.body),signal:request.signal,redirect:'manual'});
  const bytes:Uint8Array[]=[];let total=0;
  if(response.body){
   const reader=response.body.getReader();
   try{for(;;){const row=await reader.read();if(row.done)break;
    if(!(row.value instanceof Uint8Array))throw Error('C14_PROVIDER_RESPONSE');
    const take=Math.min(row.value.byteLength,maximumResponseBytes-total);
    bytes.push(row.value.slice(0,take));total+=take;
    if(total===maximumResponseBytes){await reader.cancel();break;}
   }}finally{reader.releaseLock();}
  }
  return Object.freeze({status:response.status,headers:Object.freeze({
   'content-type':response.headers.get('content-type')??'',
   'demopay-protocol':response.headers.get('demopay-protocol')??''}),
   body:Buffer.concat(bytes,total)});
 }});
}
