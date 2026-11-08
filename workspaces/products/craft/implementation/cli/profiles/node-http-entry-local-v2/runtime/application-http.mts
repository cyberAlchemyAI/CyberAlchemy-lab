/** Typed request transport; business invocation and settlement stay with the generated entry.
 * Open questions: full profile assembly and installed matrix BA09/18. No listener/provider. */
export interface InvocationContext {
 readonly signal?:AbortSignal;readonly cancellation?:'preflight'|'required';
 readonly observe?:(event:Readonly<{phase:string;adapter:string;intent:string}>)=>void;
}
export type PublicInvocationResult=Readonly<{status:'returned';value:unknown;outcome:unknown}>|Readonly<{status:'not-returned';failure:unknown}>;
export interface HttpRequestLimits {readonly request_bytes:number;readonly timeout_ms:number}
export function createOperationHttpHandler<Io extends InvocationContext>(limits:HttpRequestLimits,run:(body:unknown,io:Io,context:InvocationContext)=>Promise<PublicInvocationResult>) {
 if(!Number.isSafeInteger(limits.request_bytes)||limits.request_bytes<1||limits.request_bytes>1048576||!Number.isSafeInteger(limits.timeout_ms)||limits.timeout_ms<1||limits.timeout_ms>30000)throw new TypeError('PROFILE_APPLICATION_LIMITS');
 const reply=(body:unknown,status:number)=>new Response(JSON.stringify(body,(_key,value:unknown)=>typeof value==='bigint'?value.toString():value),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
 const failureCode=(failure:unknown):string|undefined=>{if(!failure||typeof failure!=='object')return;const code=Object.getOwnPropertyDescriptor(failure,'code');return code&&'value' in code&&typeof code.value==='string'?code.value:undefined;};
 return async(request:Request,_env:Readonly<Record<string,string|undefined>>,io:Io):Promise<Response>=>{
  if(request.method!=='POST')return reply({error:'METHOD_NOT_ALLOWED'},405);
  if(request.headers.get('content-type')?.split(';')[0]?.trim()!=='application/json')return reply({error:'CONTENT_TYPE'},415);
  if(request.signal.aborted||io.signal?.aborted)return reply({status:'not-returned',failure:{code:'FUNCTION_CANCELLED',stage:'preflight'}},409);
  if(io.cancellation==='required')return reply({status:'not-returned',failure:{code:'PROFILE_OPERATION_CANCELLATION_UNSUPPORTED',stage:'preflight'}},409);
  let body:unknown;
  try{
   const reader=request.body?.getReader();if(!reader)return reply({error:'INVALID_JSON'},400);
   const parts:Uint8Array[]=[];let size=0,timedOut=false;
   const timer=setTimeout(()=>{timedOut=true;void reader.cancel().catch(()=>{});},limits.timeout_ms);
   try{for(;;){const chunk=await reader.read();if(timedOut)return reply({error:'FUNCTION_TIMEOUT'},504);if(chunk.done)break;size+=chunk.value.byteLength;if(size>limits.request_bytes){await reader.cancel();return reply({error:'FUNCTION_BODY_LIMIT'},413);}parts.push(chunk.value);}}
   finally{clearTimeout(timer);reader.releaseLock();}
   const bytes=new Uint8Array(size);let offset=0;for(const part of parts){bytes.set(part,offset);offset+=part.length;}
   body=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
  }catch{return reply({error:'INVALID_JSON'},400);}
  // The deadline above bounds body reading only; it never cancels unsettled business work.
  const context:InvocationContext={signal:io.signal?AbortSignal.any([request.signal,io.signal]):request.signal,...(io.cancellation?{cancellation:io.cancellation}:{}),...(io.observe?{observe:io.observe}:{})};
  const result=await run(body,io,context),code=result.status==='not-returned'?failureCode(result.failure):undefined;
  return reply(result,result.status==='returned'?200:code==='PROFILE_OPERATION_PORTS_REQUIRED'?503:code==='PROFILE_OPERATION_MAPPING'?400:409);
 };
}
