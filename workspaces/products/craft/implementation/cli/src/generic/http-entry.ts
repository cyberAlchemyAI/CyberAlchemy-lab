/** Injected HTTP boundary for an original protected generic Entry. No listener or identity minting. */
import {assertGenericErrorPresentationRuntime,renderGenericErrorPresentation,renderGenericPlatformError,type GenericErrorPresentationBinding} from './error-presentation.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import type {GenericApplicationRuntime,GenericTransactionApplicationRuntime} from './invocation-owner.js';
import {captureGenericCommandMetadata,GenericCommandPreparationError,GenericInputPreparationError} from './invocation-owner.js';

export interface GenericHttpEntryConfig {
 readonly entry:string;
 readonly route:string;
 readonly kind:'read'|'command';
 readonly max_request_bytes:number;
 readonly errorPresentation?:GenericErrorPresentationBinding;
}

const json=(status:number,value:unknown,extra:Record<string,string>={}):Response=>new Response(JSON.stringify(value),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store',...extra}});
const error=(status:number,code:string,extra:Record<string,string>={})=>json(status,{kind:'adapter-error',code},extra);
const safeCode=(value:unknown):string=>typeof value==='string'&&/^[A-Za-z][A-Za-z0-9_-]{0,127}$/.test(value)?value:'OperationFailure';

async function bodyBytes(request:Request,max:number):Promise<Uint8Array|null>{
 const body=request.body;if(!body)return new Uint8Array();
 const reader=body.getReader();const parts:Uint8Array[]=[];let length=0;
 try{
  for(;;){if(request.signal.aborted)return null;const next=await reader.read();if(next.done)break;
   if(!(next.value instanceof Uint8Array))return null;
   length+=next.value.byteLength;if(length>max)return null;
   parts.push(new Uint8Array(next.value));
  }
  const bytes=new Uint8Array(length);let offset=0;for(const part of parts){bytes.set(part,offset);offset+=part.byteLength;}return bytes;
 }finally{if(length>max||request.signal.aborted)void reader.cancel().catch(()=>{});reader.releaseLock();}
}

/** The caller injects a runtime-bound actor; headers never become Auth identity. */
export function createGenericEntryHttpHandler(runtime:GenericApplicationRuntime|GenericTransactionApplicationRuntime,config:GenericHttpEntryConfig){
 if(!config||typeof config.entry!=='string'||!config.entry||typeof config.route!=='string'||!/^\/[A-Za-z0-9/_-]+$/.test(config.route)||!['read','command'].includes(config.kind)||!Number.isSafeInteger(config.max_request_bytes)||config.max_request_bytes<1||config.max_request_bytes>1048576)throw Error('INVALID_HTTP_ENTRY_CONFIG');
 runtime.assertCurrent();const entry=runtime.entry(config.entry);
 const presentation=config.errorPresentation;if(presentation)assertGenericErrorPresentationRuntime(presentation,runtime);
 const fail=(status:number,code:string,extra:Record<string,string>={})=>{if(!presentation)return error(status,code,extra);const result=renderGenericPlatformError(code,status);for(const [key,value]of Object.entries(extra))result.headers.set(key,value);return result;};
 const denied=(code:string)=>fail(code==='AuthenticationRequired'?401:code==='PermissionDenied'?403:503,code);
 const present=(result:any,status:number)=>{if(!presentation)return json(status,result);if(result.ok&&result.outcome.kind==='Returned')return json(status,result);if(result.ok)return renderGenericErrorPresentation(presentation,{entry:config.entry,outcomeKind:result.outcome.kind,code:result.outcome.code});return renderGenericPlatformError(result.error.code,status);};
 if(config.kind==='command'&&typeof (runtime as GenericTransactionApplicationRuntime).prepareCommand!=='function')throw Error('COMMAND_RUNTIME_REQUIRED');
 return async (request:Request,actor:GenericFixtureActor|null=null):Promise<Response>=>{
  if(!(request instanceof Request))return fail(400,'invalid-request');
  let pathname:string;try{pathname=new URL(request.url).pathname;}catch{return fail(400,'invalid-request');}
  if(pathname!==config.route)return fail(404,'route-not-found');
  if(request.method!=='POST')return fail(405,'method-not-allowed',{allow:'POST'});
  if(request.signal.aborted)return fail(400,'request-aborted');
  if(!/^application\/json(?:\s*;\s*charset\s*=\s*utf-8)?$/i.test(request.headers.get('content-type')??''))return fail(415,'unsupported-media-type');
  const declared=request.headers.get('content-length');if(declared!==null&&/^\d+$/.test(declared)&&BigInt(declared)>BigInt(config.max_request_bytes))return fail(413,'request-too-large');
  const commandKey=config.kind==='command'?request.headers.get('idempotency-key'):null;
  if(config.kind==='command'&&!commandKey)return fail(400,'command-key-required');
  let bytes:Uint8Array|null;try{bytes=await bodyBytes(request,config.max_request_bytes);}catch{return fail(400,'body-read-failed');}
  if(request.signal.aborted)return fail(400,'request-aborted');
  if(bytes===null)return fail(413,'request-too-large');
  let prepared:ReturnType<GenericApplicationRuntime['prepareInput']>|ReturnType<GenericTransactionApplicationRuntime['prepareCommand']>|undefined;
  try{
   runtime.assertCurrent();
   if(config.kind==='command'){
    const command=runtime as GenericTransactionApplicationRuntime;
    let metadata;try{metadata=captureGenericCommandMetadata({client_key:commandKey!});}catch{return fail(400,'invalid-command-key');}
    prepared=command.prepareCommand(entry,bytes,metadata);
    const authorization=await command.authorize(actor,prepared);
    if(!authorization.ok)return denied(authorization.error.code);
    const transfer=await command.consume(authorization.value,prepared);
    if(!transfer.ok)return denied(transfer.error.code);
    const result=await command.executeCommand(transfer.value);
    return present(result,result.ok?(result.outcome.kind==='Returned'?200:422):(result.error.code==='CommitIndeterminate'||result.error.code==='ExternalOutcomeUnknown'?503:500));
   }
   prepared=runtime.prepareInput(entry,bytes);
   const authorization=await runtime.authorize(actor,prepared);
   if(!authorization.ok)return denied(authorization.error.code);
   const transfer=await runtime.consume(authorization.value,prepared);
   if(!transfer.ok)return denied(transfer.error.code);
   const result=await runtime.execute(transfer.value);
   return present(result,result.ok?(result.outcome.kind==='Returned'?200:422):500);
  }catch(cause){
   if(cause instanceof GenericCommandPreparationError)return fail(400,presentation?'InvalidInput':safeCode(cause.code));
   if(cause instanceof GenericInputPreparationError)return fail(400,presentation?'InvalidInput':safeCode(cause.error.code));
   return fail(500,'entry-unavailable');
  }
  finally{if(prepared)try{(runtime as GenericTransactionApplicationRuntime).disposePrepared(prepared);}catch{}}
 };
}

function authError(code:string):Response {
 return error(code==='AuthenticationRequired'?401:code==='PermissionDenied'?403:503,safeCode(code));
}
