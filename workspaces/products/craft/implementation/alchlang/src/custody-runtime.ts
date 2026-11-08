import {createHash,randomUUID} from 'node:crypto';
import type {RequestCustody,LocalOutcome} from './integration-runtime-types.js';
// Generated contract drives identity/defaults/decisions. Open Questions: ../CUSTODY.md.
const fault=(code:string,id?:string)=>Object.assign(new Error(code),{code,request_id:id});
function canonical(value:any):string{
 if(value===null||typeof value==='boolean'||typeof value==='string')return JSON.stringify(value);
 if(typeof value==='number'&&Number.isFinite(value))return JSON.stringify(value);
 if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
 if(value&&typeof value==='object'&&Object.getPrototypeOf(value)===Object.prototype){
  if(Reflect.ownKeys(value).some(k=>typeof k!=='string'||!('value' in Object.getOwnPropertyDescriptor(value,k)!)))throw fault('INVALID_INPUT');
  return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
 }
 throw fault('INVALID_INPUT');
}
export function createCustodyDispatcher(contract:any,{dispatch,policy,createStore,retentionMs,maxEntries,maxBytes,reservationMs,clock}:any){
 const c=structuredClone(contract),identity=c.identity;clock??=c.lifecycle.backend==='bounded-sqlite'?Date.now:()=>performance.now();
 const limits={retention_ms:retentionMs??c.limits.retention_ms,max_entries:maxEntries??c.limits.max_entries,max_bytes:maxBytes??c.limits.max_bytes,reservation_ms:reservationMs??c.limits.reservation_ms};
 for(const [k,n]of Object.entries(limits) as [string,number][])if(!Number.isSafeInteger(n)||n<1||n>c.limits[k])throw fault('INVALID_LIMITS');
 if(typeof dispatch!=='function'||typeof createStore!=='function'||typeof policy!=='function')throw fault('CUSTODY_BINDING_REQUIRED');
 if(c.lifecycle.backend==='bounded-sqlite'&&createStore.backend!=='bounded-sqlite'||c.lifecycle.backend==='bounded-memory'&&createStore.backend==='bounded-sqlite')throw fault('CUSTODY_BACKEND_MISMATCH');
 const store:RequestCustody&{inspectAll():any[];close?():void}=createStore({policy,decisions:c.decisions,retentionMs:limits.retention_ms,maxEntries:limits.max_entries,maxBytes:limits.max_bytes,clock});
 async function run(input:any){
  const request={...input[identity.request]};for(const [k,v]of Object.entries(identity.defaults))request[k]??=v;for(const k of identity.exclude)delete request[k];
  if(typeof request[identity.scope]!=='string'||!request[identity.scope]||typeof request[identity.stream]!=='boolean')throw fault('INVALID_INPUT');
  const bytes=canonical({[identity.request]:request,[identity.payload]:input[identity.payload]});if(Buffer.byteLength(bytes)>limits.max_bytes)throw fault('REQUEST_TOO_LARGE');
  const key=input.idempotencyKey??null;if(input.idempotencyKey!==undefined&&(typeof key!=='string'||!key||Buffer.byteLength(key)>128))throw fault('INVALID_IDEMPOTENCY_KEY');
  const snapshot:any=structuredClone(Object.fromEntries(Object.entries(input).filter(([k])=>!['signal','observe','beforeAttempt','beforeReplay'].includes(k))));snapshot[identity.request]=structuredClone(request);
  const controller=new AbortController(),parent=input.signal;const cancel=()=>controller.abort('cancelled');if(parent?.aborted)cancel();else parent?.addEventListener('abort',cancel,{once:true});
  const timer=setTimeout(()=>controller.abort('deadline'),limits.reservation_ms);
  let reservation;try{reservation=await store.reserve({scope:input.custodyScope??request[identity.scope],key,requestId:randomUUID(),fingerprintVersion:identity.version,fingerprint:createHash('sha256').update(bytes).digest('hex'),stream:request[identity.stream]},{signal:controller.signal,deadline:clock()+limits.reservation_ms});}finally{clearTimeout(timer);parent?.removeEventListener('abort',cancel);}
  if(reservation.kind==='replay'){if(input.beforeReplay)await input.beforeReplay(structuredClone(reservation.result));if(parent?.aborted)throw fault('CANCELLED');return reservation.result;}if(reservation.kind==='reject')throw fault(reservation.code,reservation.requestId);
  const {token,requestId}=reservation;snapshot[identity.request][identity.request_id]=requestId;
  let attempted=false,terminal=false;let writes=Promise.resolve();let writeError:any;
  const enqueue=(fn:()=>Promise<void>)=>{writes=writes.then(fn).catch(e=>{writeError??=e;});};
  const outcome=(value:LocalOutcome)=>{if(terminal)return;terminal=true;enqueue(()=>store.recordOutcome(token,value));};
  const observe=(event:any)=>{
   if(event.type==='transport_settled')enqueue(()=>store.markTransportSettled(token));
   if(event.type==='stream_terminal')outcome(event.outcome==='completed'?{kind:'stream-completed',usage:event.usage??null}:{kind:event.outcome==='cancelled'?'cancelled':'failed',code:event.code??'STREAM_FAILED'});
  };
  const beforeAttempt=async(binding:any)=>{if(input.beforeAttempt)await input.beforeAttempt(structuredClone(binding));if(parent?.aborted)throw fault('CANCELLED');await store.beginAttempt(token,binding);attempted=true;};
  try{
   const result=await dispatch({...snapshot,signal:parent,observe,beforeAttempt});
   if(result instanceof Response)return result;
   if(Buffer.byteLength(canonical(result))>limits.max_bytes)throw fault('RESULT_TOO_LARGE');
   // Do not mark the outcome terminal until the storage write succeeds.
   await writes;if(writeError)throw writeError;await store.recordOutcome(token,{kind:'json-completed',result,usage:result.usage??null});terminal=true;
   return structuredClone(result);
  }catch(error:any){outcome({kind:error.code==='CANCELLED'?'cancelled':'failed',code:typeof error.code==='string'?error.code:'REQUEST_FAILED'});if(!attempted)enqueue(()=>store.markTransportSettled(token));await writes;throw fault(writeError?.code??error.code??'REQUEST_FAILED',requestId);}
 }
 return {run,custody:store,close(){store.close?.();},inspect(){return store.inspectAll().map(r=>({id:r.requestId,state:r.outcome==='json-completed'?'completed':r.outcome==='stream-completed'?'stream_completed':r.outcome?'failed':r.attempt?'streaming':'pending',settled:r.transportSettled&&r.outcome!==null,attempt:r.attempt?{binding_id:r.attempt.id,binding_version:r.attempt.version,policy_version:r.attempt.policyVersion,state:r.transportSettled?'locally_settled':'started',remote_completion:r.remoteCompletion,...(r.usage?{usage:r.usage}:{})}:null}));}};
}
