import {types} from 'node:util';
import {performance} from 'node:perf_hooks';
import {setTimeout,clearTimeout} from 'node:timers';
import type {U0PureInvoke,U0WireConfiguration,U0AdapterFailureCode,U0InjectedHandler} from '../../../src/profile-engine/u0-realization-contract.js';
import type {U0ResponseDomainV2} from '../../../src/profile-engine/business-authoring-stages-v2.js';
import {decodeU0Json} from './u0-json-decode.js';
import {formU0Submission} from './u0-values.js';
import {encodeU0Outcome,encodeU0AdapterError,checkU0EncoderConfiguration,u0WireBounds} from './u0-json-encode.js';

/** Pure U0 injected transport. No listener, environment ports or effect settlement.
 * Open Questions: J01 materialization and G01/U08/V01 real generated join. */
export interface U0LocalHttpObservation {
 readonly invoked:boolean;readonly acquired_bytes:number;
 readonly timer_started:boolean;readonly timer_clear_count:number;
 readonly abort_listener_added:boolean;readonly abort_listener_removed:boolean;
 readonly cancellation_requested:boolean;readonly reader_released:boolean;
 readonly locally_settled:true;readonly peer_delivery:'not-observed';
 readonly outcome:'completed'|'rejected'|'adapter-error';readonly code:string|null;
}
type Work={-readonly [K in keyof Omit<U0LocalHttpObservation,'locally_settled'|'peer_delivery'|'outcome'|'code'>]:U0LocalHttpObservation[K]};
const observations=new WeakMap<Response,U0LocalHttpObservation>();
export function inspectU0HttpResponse(response:Response):U0LocalHttpObservation|null{return observations.get(response)??null;}
export const U0_HTTP_STATUS=Object.freeze({
 'route-not-found':404,'method-not-allowed':405,'unsupported-media-type':415,
 'request-aborted':400,'request-too-large':413,'body-timeout':408,
 'body-read-failed':400,'invalid-request':400,'adapter-contract-defect':500,
} as const);
export function acceptsU0JsonMedia(value:string|null):boolean {
 return typeof value==='string'&&/^[\t ]*application\/json[\t ]*(?:;[\t ]*charset[\t ]*=[\t ]*(?:utf-8|"utf-8")[\t ]*)?$/i.exec(value)?.[0]===value;
}
const arrayPrototype=Object.getPrototypeOf(Uint8Array.prototype) as object;
const byteLength=Object.getOwnPropertyDescriptor(arrayPrototype,'byteLength')!.get!;
const arrayBuffer=Object.getOwnPropertyDescriptor(arrayPrototype,'buffer')!.get!;
function advertisedOverflow(header:string|null,cap:number):boolean {
 if(header===null||/^[0-9]+$/.exec(header)?.[0]!==header)return false;
 const digits=header.replace(/^0+/,'')||'0',limit=String(cap);
 return digits.length>limit.length||digits.length===limit.length&&digits>limit;
}
type BodyResult=Readonly<{ok:true;bytes:Uint8Array;deadline:number}>|Readonly<{ok:false;code:U0AdapterFailureCode}>;
async function acquire(request:Request,configuration:U0WireConfiguration,work:Work):Promise<BodyResult> {
 const deadline=performance.now()+configuration.body_timeout_ms;
 let timeout=false,overflow=false,readFailure=false,settled=false,done=false;
 let wake!:()=>void;const interrupted=new Promise<void>(resolve=>{wake=resolve;});
 const abort=()=>wake();request.signal.addEventListener('abort',abort,{once:true});work.abort_listener_added=true;
 const timer=setTimeout(()=>{timeout=true;wake();},configuration.body_timeout_ms);work.timer_started=true;
 let reader:ReadableStreamDefaultReader<Uint8Array>|undefined;
 const parts:Uint8Array[]=[];
 const failure=():U0AdapterFailureCode|undefined=>request.signal.aborted?'request-aborted':overflow?'request-too-large':timeout||performance.now()>=deadline?'body-timeout':readFailure?'body-read-failed':undefined;
 try{
  overflow=advertisedOverflow(request.headers.get('content-length'),configuration.request_bytes);
  let code=failure();if(code)return {ok:false,code};
  if(request.body){
   reader=request.body.getReader();
   while(!done){
    const pending=reader.read().then(result=>{
     if(settled)return;
     done=result.done;
     if(!result.done){
      const chunk=result.value;
      if(!types.isUint8Array(chunk)||types.isSharedArrayBuffer(Reflect.apply(arrayBuffer,chunk,[]))){readFailure=true;return;}
      const size=Reflect.apply(byteLength,chunk,[]) as number;
      work.acquired_bytes+=size;
      if(work.acquired_bytes>configuration.request_bytes){overflow=true;return;}
      try{const copy=new Uint8Array(size);Uint8Array.prototype.set.call(copy,chunk);parts.push(copy);}catch{readFailure=true;}
     }
    },()=>{if(!settled)readFailure=true;});
    await Promise.race([pending,interrupted]);
    code=failure();if(code)return {ok:false,code};
   }
  }
  code=failure();if(code)return {ok:false,code};
  const bytes=new Uint8Array(work.acquired_bytes);let offset=0;
  for(const part of parts){bytes.set(part,offset);offset+=part.length;}
  return {ok:true,bytes,deadline};
 }catch{
  readFailure=true;return {ok:false,code:failure()??'body-read-failed'};
 }finally{
  settled=true;clearTimeout(timer);work.timer_clear_count++;
  request.signal.removeEventListener('abort',abort);work.abort_listener_removed=true;
  if(reader){
   if(!done){work.cancellation_requested=true;void reader.cancel().catch(()=>{});}
   try{reader.releaseLock();work.reader_released=true;}catch{/* Contained; no peer delivery or rollback inference. */}
  }
 }
}
/** Component seam only: production assembly must supply its genuine generated import. */
export function createU0HttpHandler(invoke:U0PureInvoke<string>,configuration:U0WireConfiguration,domain:U0ResponseDomainV2):U0InjectedHandler {
 if(typeof invoke!=='function'||types.isProxy(invoke))throw new TypeError('U0_HTTP_CALLABLE');
 // Validate before descriptor access, then capture the actual authored domain.
 u0WireBounds(domain);
 const responseDomain=Object.freeze({rejection_code:Object.getOwnPropertyDescriptor(domain,'rejection_code')!.value as string});
 const config=checkU0EncoderConfiguration(configuration,responseDomain);
 return async(request:Request):Promise<Response>=>{
  const work:Work={invoked:false,acquired_bytes:0,timer_started:false,timer_clear_count:0,abort_listener_added:false,abort_listener_removed:false,cancellation_requested:false,reader_released:false};
  const reply=(body:Uint8Array,status:number,outcome:U0LocalHttpObservation['outcome'],code:string|null,allow=false):Response=>{
   const headers:Record<string,string>={'content-type':'application/json; charset=utf-8','cache-control':'no-store','content-length':String(body.length)};
   if(allow)headers.allow='POST';
   const response=new Response(new Uint8Array(body),{status,headers});
   observations.set(response,Object.freeze({...work,locally_settled:true,peer_delivery:'not-observed',outcome,code}));return response;
  };
  const error=(code:U0AdapterFailureCode)=>reply(encodeU0AdapterError(code),U0_HTTP_STATUS[code],'adapter-error',code,code==='method-not-allowed');
  try{
   if(new URL(request.url).pathname!==config.pathname)return error('route-not-found');
   if(request.method!==config.method)return error('method-not-allowed');
   if(!acceptsU0JsonMedia(request.headers.get('content-type')))return error('unsupported-media-type');
   if(request.signal.aborted)return error('request-aborted');
   const body=await acquire(request,config,work);
   if(!body.ok)return error(body.code);
   if(request.signal.aborted)return error('request-aborted');
   let value;
   try{value=formU0Submission(decodeU0Json(body.bytes,config.request_bytes));}catch{return error('invalid-request');}
   // No await between final current abort/deadline check and synchronous invoke.
   if(request.signal.aborted)return error('request-aborted');
   if(performance.now()>=body.deadline)return error('body-timeout');
   work.invoked=true;
   const result=invoke(value);
   if(types.isPromise(result)){
    // Consume only native Promise rejection; never await or touch caller thenables.
    void Promise.prototype.then.call(result,undefined,()=>{});return error('adapter-contract-defect');
   }
   const encoded=encodeU0Outcome(result,responseDomain);
   if(encoded.length>config.response_bytes)return error('adapter-contract-defect');
   const kind=Object.getOwnPropertyDescriptor(result,'kind')!.value as 'completed'|'rejected';
   return reply(encoded,kind==='completed'?200:422,kind,kind==='rejected'?responseDomain.rejection_code:null);
  }catch{return error('adapter-contract-defect');}
 };
}
