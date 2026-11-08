import {readSse,createSseSink,streamBounded,streamFault} from './sse-adapter.js';
// Generated contract owns transitions, provider events and frame mappings. Open Questions: ../STREAMS.md.
export function createStreamSession(contract:any,functions:Record<string,any>,session:any){
 const c=JSON.parse(JSON.stringify(contract)),modules={...functions};const {exchange,cancelTransport,identity:original,signal,abort,observe,maxBytes=c.limits.max_bytes}=session;
 if(!/^text\/event-stream(?:\s*;|$)/i.test(exchange.mediaType??''))throw streamFault('INVALID_STREAM_CONTENT_TYPE');
 if(!exchange.body?.[Symbol.asyncIterator])throw streamFault('INVALID_PROVIDER_STREAM');
 if(!Number.isSafeInteger(maxBytes)||maxBytes<1||maxBytes>c.limits.max_bytes)throw streamFault('INVALID_LIMITS');
 if(Object.values(c.frames).some((f:any)=>typeof modules[f.module]!=='function'))throw streamFault('STREAM_BINDING_REQUIRED');
 const identity=JSON.parse(JSON.stringify(original)),local=new AbortController(),control=AbortSignal.any([signal,local.signal]);let state=c.initial,terminal=false,notified=false;
 const notify=(outcome:string,value?:any)=>{if(notified)return;notified=true;try{observe?.({type:'stream_terminal',outcome,...(value===undefined?{}:{value})});}catch{}};
 const transition=(event:string)=>{const t=c.transitions.find((t:any)=>t.from===state&&t.event===event);if(!t)throw streamFault('INVALID_STREAM_TRANSITION');state=t.to;terminal=Object.values(c.terminal).includes(state);};
 const check=()=>{if(control.aborted)throw streamFault(control.reason==='deadline'?'DEADLINE_EXCEEDED':'CANCELLED');};
 const {sink,response}=createSseSink(c.limits.max_frame_bytes,async()=>{if(!terminal){transition('cancel');notify('cancelled');}local.abort('cancelled');abort('cancelled');await cancelTransport();});
 const map=async(kind:string,arg:any,cancellable=true)=>{
  const value=modules[c.frames[kind].module]({identity,...arg},{},{localOnly:true,...(cancellable?{signal:control}:{})});
  const mapped=await (cancellable?streamBounded(Promise.resolve(value),control):streamBounded(Promise.resolve(value),local.signal));
  const payload=mapped.value;if(!payload||typeof payload!=='object'||Array.isArray(payload)||Object.keys(identity).some(k=>payload[k]!==identity[k]))throw streamFault('INVALID_STREAM_IDENTITY');return payload;
 };
 const finished=(async()=>{
  try{
   check();const start=await map('start',{});check();await sink.write(c.frames.start.event,start,control,()=>transition('start'));
   for await(const event of readSse(exchange.body,control,maxBytes,c.limits.max_event_bytes)){
    check();const kind=Object.keys(c.provider_events).find(k=>c.provider_events[k]===event.event);if(!kind)throw streamFault(c.errors.unknown);if(kind==='fail')throw streamFault(c.errors.provider);
    let value;try{value=JSON.parse(event.data);}catch{throw streamFault(c.errors.invalid);}if(!value||typeof value!=='object'||Array.isArray(value))throw streamFault(c.errors.invalid);
    const payload=await map(kind,{event:value});check();if(terminal)return;
    await sink.write(c.frames[kind].event,payload,control,()=>{transition(kind);if(terminal)notify('completed',payload);});if(terminal)break;
   }
   if(!terminal)throw streamFault(c.errors.eof);
  }catch(error){
   if(!terminal){
    if(local.signal.aborted||control.aborted&&control.reason!=='deadline'){transition('cancel');notify('cancelled');}
    else {
     // Terminal state is claimed before asynchronous error mapping; cancel cannot claim it again.
     transition('fail');notify('error');
     try{const raw=(error as any)?.code;const payload=await map('fail',{code:typeof raw==='string'&&raw.length<=256?raw:''},false);await sink.write(c.frames.fail.event,payload);}
     catch{sink.error(streamFault('STREAM_ERROR_MAPPING_FAILED'));}
    }
   }
  }finally{sink.close();void Promise.resolve().then(cancelTransport).catch(()=>{});}
 })();
 // A stream consumer observes errors in the response. Invocation still awaits actual cleanup.
 finished.catch(()=>{});return {response,finished};
}
