import type {StreamFrameSink} from './integration-runtime-types.js';
// Byte parsing and bounded downstream capacity only. Open Questions: ../STREAMS.md.
export const streamFault=(code:string)=>Object.assign(new Error(code),{code});
export async function streamBounded<T>(promise:Promise<T>,signal:AbortSignal):Promise<T>{
 let listener!:()=>void;const aborted=new Promise<never>((_,reject)=>{listener=()=>reject(streamFault(signal.reason==='deadline'?'DEADLINE_EXCEEDED':'CANCELLED'));signal.addEventListener('abort',listener,{once:true});if(signal.aborted)listener();});
 try{return await Promise.race([promise,aborted]);}finally{signal.removeEventListener('abort',listener);}
}
export async function* readSse(source:AsyncIterable<Uint8Array>,signal:AbortSignal,maxBytes:number,maxEventBytes:number){
 const decoder=new TextDecoder('utf-8',{fatal:true}),iterator=source[Symbol.asyncIterator]();let buffer='',data:string[]=[],event='',total=0,eventBytes=0;
 for(;;){
  const {done,value}=await streamBounded(iterator.next(),signal);
  if(done){buffer+=decoder.decode();if(buffer==='\r'){if(data.length)yield {event:event||'message',data:data.join('\n')};return;}if(buffer||data.length)throw streamFault('INCOMPLETE_PROVIDER_STREAM');return;}
  if(!(value instanceof Uint8Array))throw streamFault('INVALID_PROVIDER_STREAM');total+=value.byteLength;if(total>maxBytes)throw streamFault('RESPONSE_TOO_LARGE');buffer+=decoder.decode(value,{stream:true});
  for(;;){
   const match=/\r\n|\r|\n/.exec(buffer);if(!match)break;if(match[0]==='\r'&&match.index===buffer.length-1)break;
   const line=buffer.slice(0,match.index);buffer=buffer.slice(match.index+match[0].length);eventBytes+=Buffer.byteLength(line)+match[0].length;if(eventBytes>maxEventBytes)throw streamFault('EVENT_TOO_LARGE');
   if(!line){if(data.length)yield {event:event||'message',data:data.join('\n')};data=[];event='';eventBytes=0;continue;}
   if(line.startsWith(':'))continue;const colon=line.indexOf(':');const field=colon<0?line:line.slice(0,colon);let val=colon<0?'':line.slice(colon+1);if(val.startsWith(' '))val=val.slice(1);if(field==='event')event=val;else if(field==='data')data.push(val);
  }
  if(eventBytes+Buffer.byteLength(buffer)>maxEventBytes)throw streamFault('EVENT_TOO_LARGE');
 }
}
export function createSseSink(maxFrameBytes:number,onCancel:()=>Promise<void>){
 let controller!:ReadableStreamDefaultController<Uint8Array>,closed=false;const waiters=new Set<()=>void>(),cancelled=new AbortController();const wake=()=>{for(const f of waiters)f();waiters.clear();};
 const body=new ReadableStream<Uint8Array>({start(c){controller=c;},pull(){wake();},cancel(){closed=true;cancelled.abort('cancelled');wake();return onCancel();}},{highWaterMark:1});
 const sink:StreamFrameSink={async write(event,value,signal,accepted){
  if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(event))throw streamFault('INVALID_STREAM_EVENT');const bytes=new TextEncoder().encode(`event: ${event}\ndata: ${JSON.stringify(value)}\n\n`);if(bytes.byteLength>maxFrameBytes)throw streamFault('EVENT_TOO_LARGE');
  const combined=signal?AbortSignal.any([signal,cancelled.signal]):cancelled.signal;
  while(!closed&&(controller.desiredSize??0)<=0){let wakeOne!:()=>void;const capacity=new Promise<void>(r=>{wakeOne=r;waiters.add(r);});try{await streamBounded(capacity,combined);}finally{waiters.delete(wakeOne);}}
  if(closed||combined.aborted)throw streamFault(combined.reason==='deadline'?'DEADLINE_EXCEEDED':'CANCELLED');controller.enqueue(bytes);accepted?.();
 },close(){if(!closed){closed=true;controller.close();wake();}},error(reason){if(!closed){closed=true;controller.error(reason);wake();}}};
 return {sink,response:new Response(body,{headers:{'content-type':'text/event-stream; charset=utf-8','cache-control':'no-cache'}})};
}
