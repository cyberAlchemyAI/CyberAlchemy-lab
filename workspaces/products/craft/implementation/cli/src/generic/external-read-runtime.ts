import type {ReadableStreamReadResult,ReadableStreamDefaultReader} from 'node:stream/web';
/** Original bounded safeGET owner. Profiles and mappings remain data; no app callbacks.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {performance} from 'node:perf_hooks';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import {assertGenericRepositoryPlanOwner,type GenericRepositoryPlanOwner,type GenericTransactionApplicationHandle} from './repository-plan.js';
import {assertGenericInternalExecutionToken,genericCommandScopeContains,type GenericInternalExecutionToken} from './execution-session.js';
import type * as X from './external-read-data-v1.js';
import type * as W from './external-write-data-v1.js';
import type * as E from './event-data-v1.js';
const at={path:'external-read',start:0,end:0},nativeFetch=globalThis.fetch.bind(globalThis),now=performance.now.bind(performance);
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['execution-session'+ext,'external-read-source'+ext,'external-read-data-v1'+ext,'repository-plan'+ext,'../commerce/commerce-core-source-owner'+ext]);
const nativeOwners=new WeakSet<object>();
export type ExternalNativeOutcome<T>={readonly kind:'value';readonly value:T}|{readonly kind:'unavailable'|'malformed'};
export interface GenericExternalObservation{readonly kind:'original-generic-external-observation/v1-candidate'}
export interface Diagnostic{readonly ordinal:number;readonly invocation:number;readonly binding:string;readonly callsite:string;readonly phase:string;readonly monotonic_ms:number;readonly await_index?:number;readonly await_outcome?:'fulfilled'|'rejected';readonly original_fault_code?:string|null}
type SafeField=string|number|boolean|null;
type ObservationSink=(domain:'external',event:string,monotonic_ms:number,correlation_sha256:string,fields:Readonly<Record<string,SafeField>>)=>void;
const observedFaultCode=(error:unknown):{code:string|null;captureError:boolean}=>{try{if((typeof error!=='object'||error===null)&&typeof error!=='function')return {code:null,captureError:false};const descriptor=Object.getOwnPropertyDescriptor(error,'code');if(!descriptor||!Object.hasOwn(descriptor,'value'))return {code:null,captureError:true};const code=descriptor.value;return typeof code==='string'&&/^[A-Za-z][A-Za-z0-9]{0,63}$/.test(code)?{code,captureError:false}:{code:null,captureError:true};}catch{return {code:null,captureError:true};}};
class ProviderChannel extends Error{constructor(readonly channel:'unavailable'|'malformed'){super(channel);}}
/** Used only inside the original execution session, whose token/account never escape. */
export function createGenericExternalReadOwner(plans:GenericRepositoryPlanOwner,application:GenericTransactionApplicationHandle,observe?:ObservationSink){
 assertGenericRepositoryPlanOwner(plans);const initial=plans.inspectSourceApplication(application) as {readonly contract:X.GenericExternalTransactionApplicationV1|W.GenericExternalWriteTransactionApplicationV1|E.GenericEventTransactionApplicationV1;readonly source_capture_sha256:string};if(initial.contract.admission_mode!=='external-read-entry'&&initial.contract.admission_mode!=='external-write-entry'&&!(initial.contract.admission_mode==='event-handoff-entry'&&initial.contract.external_bindings.length>0))fail('InvalidContract',at,'actual accepted external application required');
 if(process.versions.node!=='26.8.1')fail('UnsupportedCapability',at,'selected native Node26.8.1 realization required');
 const pending=new WeakMap<object,{token:GenericInternalExecutionToken;result:ExternalNativeOutcome<any>;deadline:()=>void;binding:X.GenericExternalCheckedBindingV1;step:X.GenericExternalStepV1;invocation:number;correlation:string;used:boolean}>();
 const app=initial.contract,controllers=new Map<GenericInternalExecutionToken,AbortController>(),events:Diagnostic[]=[];let closed=false,sequence=0,ordinal=0,omittedEvents=0,captureErrors=0,omittedCaptureErrors=0;
 const capture=()=>{if(captureErrors<64)captureErrors++;else omittedCaptureErrors++;};
 const faultCode=(error:unknown):string|null=>{const observed=observedFaultCode(error);if(observed.captureError)capture();return observed.code;};
 const current=(token?:GenericInternalExecutionToken)=>{if(!nativeOwners.has(owner))fail('ForeignOwner',at,'original registered external owner required');pin.assertCurrent();if(closed)fail('DisposedOwner',at,'external read owner disposed');if(!token||!genericCommandScopeContains(token)){assertGenericRepositoryPlanOwner(plans);plans.assertCurrent(application);}};
 const log=(invocation:number,b:X.GenericExternalCheckedBindingV1,step:X.GenericExternalStepV1,phase:string,correlation:string,detail:{await_index?:number;await_outcome?:'fulfilled'|'rejected';original_fault_code?:string|null}={})=>{
  try{const atTime=now(),row=Object.freeze({ordinal:ordinal++,invocation,binding:b.id,callsite:step.call.source_callsite,phase,monotonic_ms:atTime,...detail});if(events.length<4096)events.push(row);else omittedEvents++;
   observe?.('external',phase,atTime,correlation,{invocation,binding_id:b.id,source_callsite:step.call.source_callsite,await_index:detail.await_index??null,await_outcome:detail.await_outcome??null,original_fault_code:detail.original_fault_code??null,provider_channel:phase==='unavailable'||phase==='malformed'?phase:null});
  }catch{capture();}
 };
 const owner=Object.freeze({
  async read<T>(token:GenericInternalExecutionToken,operation:string,step:X.GenericExternalStepV1,wireRequest:Readonly<Record<string,unknown>>,checkedAccept:(raw:unknown,mark:(phase:'checked-decode'|'validation-rule'|'response-mapping')=>void,deadline:()=>void)=>ExternalNativeOutcome<T>,correlation:string):Promise<GenericExternalObservation>{
   current();const tokenData=assertGenericInternalExecutionToken(token);if(tokenData.inspection.source_capture_sha256!==initial.source_capture_sha256)fail('ForeignOwner',at,'original same-application execution token required');
   const control=app.stateful_operations.find(o=>o.operation===operation),find=(rows:readonly (X.GenericExternalPreflightStepV1|W.GenericExternalWritePreflightStepV1)[]):boolean=>rows.some(s=>s.kind==='conditional'?find(s.then)||find(s.otherwise):s.kind==='read-external'&&dataDigest(s)===dataDigest(step));
   const binding=app.external_bindings.find(b=>b.id===step.call.binding_ref);if(!control||!find(control.preflight)||!binding||dataDigest(binding)!==step.call.binding_sha256||binding.binding_semantics_sha256!==step.call.binding_semantics_sha256||binding.interface_ref!==step.call.interface_ref||binding.contract_operation_ref!==step.call.contract_operation_ref)fail('ForeignOwner',at,'actual source-bound external call and binding required');
   if(controllers.has(token))fail('ForeignOwner',at,'one native effect per original account at a time');
   const query=binding.protocol.query.map(c=>{const v=wireRequest[c.field];if(typeof v!=='string'||c.encoding==='uint64-decimal'&&(!/^(0|[1-9][0-9]*)$/.test(v)||BigInt(v)>18446744073709551615n))fail('InvalidContract',at,'checked wire request carrier required');const encode=(s:string)=>encodeURIComponent(s).replace(/[!'()*]/g,c=>'%'+c.charCodeAt(0).toString(16).toUpperCase());return encode(c.key)+'='+encode(v);}).join('&');
   const target=new URL(binding.protocol.path,binding.configuration_source.origin);if(target.origin!==binding.configuration_source.origin||target.pathname!==binding.protocol.path||target.username||target.password)fail('InvalidContract',at,'immutable captured origin/path required');target.search=query;
   current();assertGenericInternalExecutionToken(token);
   const controller=new AbortController(),invocation=sequence++;let reader:ReadableStreamDefaultReader<Uint8Array>|undefined,timer:ReturnType<typeof setTimeout>|undefined,result:ExternalNativeOutcome<T>|undefined,error:unknown,hasError=false,timed=false,cancelPending=false,readIndex=0;
   // Initial owner checks occur before dispatch. All later work, including final
   // physical reentry, is checked against this same real monotonic deadline.
   const started=now(),deadline=()=>{if(timed||now()-started>=binding.limits.deadline_ms){timed=true;controller.abort();throw new ProviderChannel('unavailable');}};
   const mark=(phase:'checked-decode'|'validation-rule'|'response-mapping')=>{deadline();log(invocation,binding,step,phase,correlation);};
   controllers.set(token,controller);
   try{
    timer=setTimeout(()=>{timed=true;controller.abort();},binding.limits.deadline_ms);
    log(invocation,binding,step,'dispatch',correlation);let response:Response;
    log(invocation,binding,step,'fetch-await-start',correlation);
    try{response=await nativeFetch(target,{method:'GET',redirect:'manual',signal:controller.signal,headers:{accept:'application/json'}});log(invocation,binding,step,'fetch-await-settled',correlation,{await_outcome:'fulfilled'});}catch{log(invocation,binding,step,'fetch-await-settled',correlation,{await_outcome:'rejected'});throw new ProviderChannel('unavailable');}
    current(token);assertGenericInternalExecutionToken(token);deadline();log(invocation,binding,step,'fetch-post-guard-end',correlation);log(invocation,binding,step,'headers',correlation);
    if(response.body)reader=response.body.getReader();
    if(response.status!==binding.protocol.success_status)throw new ProviderChannel('unavailable');
    const media=response.headers.get('content-type');if(!media||!/^application\/json(?:\s*;\s*charset\s*=\s*utf-8)?$/i.test(media.trim()))throw new ProviderChannel('malformed');
    if(!reader)throw new ProviderChannel('malformed');
    const lengthHeader=response.headers.get('content-length'),identityEncoding=!response.headers.get('content-encoding')||response.headers.get('content-encoding')?.toLowerCase()==='identity';let expectedLength:number|null=null;
    if(lengthHeader!==null&&identityEncoding){if(!/^(0|[1-9][0-9]*)$/.test(lengthHeader)||BigInt(lengthHeader)>BigInt(binding.limits.body_bytes))throw new ProviderChannel('malformed');expectedLength=Number(lengthHeader);}
    const chunks:Uint8Array[]=[];let bytes=0;
    for(;;){deadline();let item:ReadableStreamReadResult<Uint8Array>;const index=readIndex++;log(invocation,binding,step,'body-read-await-start',correlation,{await_index:index});try{item=await reader.read();log(invocation,binding,step,'body-read-await-settled',correlation,{await_index:index,await_outcome:'fulfilled'});}catch{log(invocation,binding,step,'body-read-await-settled',correlation,{await_index:index,await_outcome:'rejected'});throw new ProviderChannel('unavailable');}current(token);assertGenericInternalExecutionToken(token);deadline();log(invocation,binding,step,'body-read-post-guard-end',correlation,{await_index:index});if(item.done)break;bytes+=item.value.byteLength;if(bytes>binding.limits.body_bytes)throw new ProviderChannel('malformed');chunks.push(item.value);}
    log(invocation,binding,step,'body-complete',correlation);reader.releaseLock();reader=undefined;if(expectedLength!==null&&bytes!==expectedLength)throw new ProviderChannel('malformed');const buffer=Buffer.concat(chunks,bytes);if(buffer[0]===0xef&&buffer[1]===0xbb&&buffer[2]===0xbf)throw new ProviderChannel('malformed');
    let raw:unknown;try{const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer);raw=parseCoreCommerceJson(text,'external-response');}catch{throw new ProviderChannel('malformed');}
    deadline();result=checkedAccept(raw,mark,deadline);deadline();
   }catch(caught){if(caught instanceof ProviderChannel)result={kind:caught.channel};else{error=caught;hasError=true;}}
   finally{
    if(timer!==undefined)clearTimeout(timer);controller.abort();
    if(reader){
     const resource=reader;try{current(token);assertGenericInternalExecutionToken(token);}catch(caught){error=caught;hasError=true;}
     cancelPending=true;log(invocation,binding,step,'cancel-requested',correlation);
     // The cancel is owned and observed. Waiting is limited to the remainder of
     // the original dispatch deadline; no fresh cleanup timeout widens it.
     const cancellation=Promise.resolve().then(()=>resource.cancel()).then(()=>{},()=>{}).then(()=>{cancelPending=false;try{current(token);assertGenericInternalExecutionToken(token);}catch(caught){error=caught;hasError=true;log(invocation,binding,step,'cancel-reentry-fault',correlation,{original_fault_code:faultCode(caught)});}try{resource.releaseLock();}catch{}if(controllers.get(token)===controller)controllers.delete(token);log(invocation,binding,step,'cancel-settled',correlation);});
     const remaining=Math.max(0,binding.limits.deadline_ms-(now()-started));let cleanupTimer:ReturnType<typeof setTimeout>|undefined;
     try{if(remaining>0)await Promise.race([cancellation,new Promise<void>(resolve=>{cleanupTimer=setTimeout(resolve,remaining);})]);}finally{if(cleanupTimer!==undefined)clearTimeout(cleanupTimer);}
     if(cancelPending)log(invocation,binding,step,'cancel-pending-after-deadline',correlation);
    }
// A pending native cancellation remains registered after deadline retirement.
    // Its observed settlement releases the registration; diagnostics never claim
    // that an unresolved cleanup resource has already retired.
    if(!cancelPending)controllers.delete(token);
    try{current(token);assertGenericInternalExecutionToken(token);log(invocation,binding,step,'final-reentry',correlation);deadline();}catch(caught){if(caught instanceof ProviderChannel){if(!hasError)result={kind:caught.channel};}else{error=caught;hasError=true;}}
    log(invocation,binding,step,cancelPending?'cleanup-pending':timed?'deadline-retired':closed?'cancelled-retired':'retired',correlation);
   }
   if(hasError)throw error;if(!result)fail('InvalidContract',at,'native read did not produce a closed observation');const observation=Object.freeze({kind:'original-generic-external-observation/v1-candidate' as const});pending.set(observation,{token,result,deadline,binding,step,invocation,correlation,used:false});return observation;
  },
  consume<T>(token:GenericInternalExecutionToken,observation:GenericExternalObservation,finalReentry:()=>void):ExternalNativeOutcome<T>{
   const row=observation&&typeof observation==='object'?pending.get(observation):undefined;if(!row||row.token!==token||row.used)fail('ForeignOwner',at,'original one-use external observation required');row.used=true;
   current(token);assertGenericInternalExecutionToken(token);finalReentry();log(row.invocation,row.binding,row.step,'final-reentry',row.correlation);let result=row.result;try{row.deadline();}catch(error){if(error instanceof ProviderChannel)result={kind:error.channel};else throw error;}
   log(row.invocation,row.binding,row.step,result.kind==='value'?'accepted':result.kind,row.correlation);
   return result;
  },
  inspect(){return coreFreeze({schema_version:'craft.generic-external-read-diagnostics/v1-candidate',clock:'node-perf-hooks-real-monotonic',closed,active:controllers.size,events:[...events],omitted_event_count:omittedEvents,overflow:omittedEvents>0,capture_error_count:captureErrors,omitted_capture_error_count:omittedCaptureErrors,authority_effect:'none'});},
  close(){closed=true;for(const controller of controllers.values())controller.abort();},
 });nativeOwners.add(owner);return owner;
}
