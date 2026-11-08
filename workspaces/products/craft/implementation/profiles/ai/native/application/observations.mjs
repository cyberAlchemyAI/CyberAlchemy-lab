/** Optional bounded diagnostics over actual original runtime owners. No event
 * payload supplies tenant/mode/resource, prompts, credentials or usage labels.
 * Durable business/effect/exposure owners remain authoritative.
 * Open Questions: README.md. */
import {createObservationSink} from '../observations/index.mjs';
import {assert,canonical,closed,freeze,sha256,text} from '../shared.mjs';

const identityFields=['runtime_id','tenant','application','resource_id','mode'];
// Only constructors in this module can register this checked owner join.
const workflowReaders=new WeakMap();
const finiteCodes=new Set(['InvalidContract','ResourceLimit','PermissionDenied','SourceRevoked','ProviderUnavailable','OperationFailed','StaleOwner','Timeout','Cancelled']);
function codeFor(error){try{if(finiteCodes.has(error?.code))return error.code;const value=typeof error?.message==='string'?error.message:'';if(/DENIED|PermissionDenied|RECIPIENT/.test(value))return 'PermissionDenied';if(/STALE|StaleOwner/.test(value))return 'StaleOwner';if(/TIMEOUT|DEADLINE|Timeout/.test(value))return 'Timeout';if(/CANCEL/.test(value))return 'Cancelled';if(/LIMIT|BOUND|ResourceLimit/.test(value))return 'ResourceLimit';}catch{}return 'OperationFailed';}
function usageFor(result){
 if(result?.usage_state==='observed'&&Number.isSafeInteger(result.usage?.input_tokens)&&result.usage.input_tokens>=0&&Number.isSafeInteger(result.usage?.output_tokens)&&result.usage.output_tokens>=0)return {kind:'observed',input_units:result.usage.input_tokens,output_units:result.usage.output_tokens};
 if(result?.usage_state==='estimated'&&Number.isSafeInteger(result.usage?.input_tokens)&&result.usage.input_tokens>=0&&Number.isSafeInteger(result.usage?.output_tokens)&&result.usage.output_tokens>=0)return {kind:'estimated',input_units:result.usage.input_tokens,output_units:result.usage.output_tokens};
 return {kind:'unknown'};
}
function workTransition(value){const result=value?.result??value;if(value instanceof Response)return value.status===401||value.status===403?'denied':value.ok?'returned':'unknown';
 if(['completed','committed'].includes(result?.kind))return 'committed';if(['needs-review','review'].includes(result?.kind))return 'review';if(['suspended-unknown','unknown'].includes(result?.kind))return 'unknown';if(['rejected','denied'].includes(result?.kind))return 'denied';if(result?.kind==='cancelled')return 'cancelled';return 'returned';}

/** Identity is derived from the original Workflow definition and an actual
 * selected execution resource. Inspecting the original definition checks its
 * live owner; no fixture/provider mode is inferred from an operation result. */
export function createWorkflowObservationRuntime({driver,access,executionRuntime}){
 assert(typeof driver?.inspectDefinition==='function'&&typeof access?.assertCurrent==='function'&&typeof executionRuntime?.inspect==='function'&&typeof executionRuntime?.assertCurrent==='function','ForeignOwner','original Workflow/access/execution owners');
 // Both original inspect APIs already validate their current owners. Keep one
 // fresh read of each, rather than asserting and then inspecting them again.
 const read=()=>{access.assertCurrent();const definition=driver.inspectDefinition(),selected=closed(executionRuntime.inspect(),identityFields);text(definition.workflow,'original workflow');return freeze({runtime_id:'workflow:'+sha256(canonical({workflow:definition.workflow,service:definition.service,source:definition.source_closure_sha256,profile:definition.profile_sha256,compatibility:definition.compatibility_sha256})),tenant:selected.tenant,application:selected.application,resource_id:definition.workflow,mode:selected.mode});};
 const runtime=Object.freeze({assertCurrent(){read();},inspect:read});workflowReaders.set(runtime,read);return runtime;
}

export function createApplicationObservations({sink:provided,bounds,now}={}){
 const sink=provided??createObservationSink({...(bounds?{bounds}:{}),...(now?{now}:{})});assert(typeof sink?.bindRuntime==='function'&&typeof sink?.drain==='function','ForeignOwner','original observation sink');
 const emitters=new WeakMap();let closedOwner=false,lost=0,unbound=0;
 function record(runtime){let owned=emitters.get(runtime);if(!owned){assert(typeof runtime?.inspect==='function'&&typeof runtime?.assertCurrent==='function','ForeignOwner','actual observation runtime');owned={active:false,frame:undefined,emitter:undefined};
   // The sink's original closed identity/drift validation stays in place. This
   // view is usable only inside the one synchronous bind/emit below; it cannot
   // retain an authority snapshot across an await or a subsequent event.
   owned.view=Object.freeze({assertCurrent(){assert(owned.active&&owned.frame,'StaleOwner','active synchronous observation required');},inspect(){assert(owned.active&&owned.frame,'StaleOwner','active synchronous observation required');return owned.frame;}});emitters.set(runtime,owned);}return owned;}
 function fresh(runtime,operation){const owned=record(runtime);assert(!owned.active,'StaleOwner','reentrant observation rejected');owned.active=true;try{const read=workflowReaders.get(runtime);if(!read)runtime.assertCurrent();owned.frame=closed(read?read():runtime.inspect(),identityFields);if(!owned.emitter)owned.emitter=sink.bindRuntime(owned.view);return operation(owned);}finally{owned.frame=undefined;owned.active=false;}}
 function safe(runtime,event,fallbackCorrelation=false){if(closedOwner){lost++;return {accepted:false,reason:'optional-observations-closed'};}try{const result=fresh(runtime,owned=>owned.emitter.emit(fallbackCorrelation?{...event,correlation_id:event.correlation_id??owned.frame.runtime_id}:event));if(result?.accepted===false)lost++;return result;}catch{lost++;return {accepted:false,reason:'optional-observation-unavailable'};}}
 function createBinding(){let actual,facade;const observer=Object.freeze({emit(event){if(!actual){unbound++;return {accepted:false,reason:'actual-runtime-not-bound'};}return safe(actual,event);}});
  return Object.freeze({observer,attach(runtime){assert(runtime&&typeof runtime.inspect==='function'&&typeof runtime.assertCurrent==='function','ForeignOwner','actual selected runtime');assert(!actual||actual===runtime,'ForeignOwner','one original runtime per lazy binding');if(facade)return facade;actual=runtime;
    // Binding errors are optional diagnostics. The actual owner still controls
    // execution; a broken sink cannot replace its durable operation result.
    try{fresh(actual,()=>{});}catch{lost++;}
    const invoke=async request=>{try{const result=await actual.invoke(request);const transition=result.kind==='candidate'?'returned':result.kind==='refusal'?'refused':result.kind==='invalid'?'incomplete':['incomplete','unavailable','unknown'].includes(result.kind)?result.kind:'returned';safe(actual,{category:'model',transition,correlation_id:result.attemptId??request.intentId,usage:usageFor(result),...(result.kind==='invalid'?{code:'InvalidContract'}:{})});return result;}catch(error){const code=codeFor(error),correlation=request?.intentId??'native-invocation';safe(actual,{category:code==='PermissionDenied'?'access':'model',transition:code==='PermissionDenied'?'denied':'unknown',correlation_id:correlation,code});throw error;}};
    facade=Object.freeze({...actual,...(typeof actual.invoke==='function'?{invoke}:{} )});return facade;
  }});
 }
 return Object.freeze({
  createBinding,
  construct(factory){assert(typeof factory==='function','InvalidContract','native constructor');const binding=createBinding(),created=factory({observer:binding.observer});return created&&typeof created.then==='function'?created.then(runtime=>binding.attach(runtime)):binding.attach(created);},
  observerFor(runtime){return Object.freeze({emit:event=>safe(runtime,event)});},
  async observeWorkflow(metadata,operation){assert(metadata&&Object.keys(metadata).every(k=>['runtime','operation','correlationId'].includes(k)),'InvalidContract','closed original Workflow observation metadata');const {runtime,operation:kind,correlationId}=metadata;assert(['submit','advance','close'].includes(kind)&&typeof operation==='function','InvalidContract','original Workflow operation');const correlation=correlationId;if(correlation!==undefined)text(correlation,'actual work correlation',128);safe(runtime,{category:'work',transition:'dispatched',correlation_id:correlation},true);
   try{const result=await operation(),transition=workTransition(result);safe(runtime,{category:'work',transition,correlation_id:correlation,...(transition==='denied'?{code:'OperationFailed'}:{})},true);if(transition==='denied')safe(runtime,{category:'access',transition:'denied',correlation_id:correlation,code:'PermissionDenied'},true);return result;}catch(error){const code=codeFor(error);safe(runtime,{category:code==='PermissionDenied'?'access':'work',transition:code==='PermissionDenied'?'denied':'unknown',correlation_id:correlation,code},true);throw error;}},
  drain(max){return max===undefined?sink.drain():sink.drain(max);},
  inspect(){let details;try{details=sink.inspect();}catch{details={status:'unavailable'};}return freeze({abi:'craft.application-observation-join/v1',optional:true,lost,unbound,sink:details});},
  close(){closedOwner=true;if(!provided)sink.close();},
 });
}
