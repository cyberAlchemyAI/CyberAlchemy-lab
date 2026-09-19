// Generic generated-service boundary. Open questions: ../SERVICE.md.
type Invoke=(input:any,env?:any,io?:any)=>Promise<any>;
const fail=(code:string):never=>{throw Object.assign(new Error(code),{code});};
const checkSignal=(signal:AbortSignal)=>{if(signal.aborted)fail('CANCELLED');};
async function body(request:Request,maxBytes:number,timeout:number){
 checkSignal(request.signal);const length=request.headers.get('content-length');if(length!==null&&(!/^\d+$/.test(length)||Number(length)>maxBytes))fail('REQUEST_TOO_LARGE');
 const reader=request.body?.getReader()??fail('INVALID_INPUT');let bytes=0;const chunks:Uint8Array[]=[];let reject!: (e:Error)=>void;
 const stopped=new Promise<never>((_,r)=>{reject=r;});const abort=()=>reject(Object.assign(new Error('CANCELLED'),{code:'CANCELLED'}));request.signal.addEventListener('abort',abort,{once:true});
 const timer=setTimeout(()=>reject(Object.assign(new Error('DEADLINE_EXCEEDED'),{code:'DEADLINE_EXCEEDED'})),timeout);
 try{checkSignal(request.signal);for(;;){const {done,value}=await Promise.race([reader.read(),stopped]);if(done)break;bytes+=value.byteLength;if(bytes>maxBytes)fail('REQUEST_TOO_LARGE');chunks.push(value);}}
 finally{clearTimeout(timer);request.signal.removeEventListener('abort',abort);void reader.cancel().catch(()=>{});reader.releaseLock();}
 const all=new Uint8Array(bytes);let offset=0;for(const chunk of chunks){all.set(chunk,offset);offset+=chunk.length;}
 try{return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(all));}catch{return fail('INVALID_INPUT');}
}
export function createService(plan:any,functions:Record<string,Invoke>,options:{contexts?:Record<string,any>;operations?:Record<string,Invoke>;maxRequestBytes?:number;readTimeoutMs?:number}={}){
 plan=structuredClone(plan);functions={...functions};
 const {contexts={},operations={},maxRequestBytes=plan.limits.requestBytes,readTimeoutMs=plan.limits.readTimeoutMs}=options;
 for(const [supplied,required,label]of [[operations,plan.operations,'OPERATION'],[contexts,plan.contexts,'CONTEXT']] as const){if(Object.keys(required).some(k=>!Object.hasOwn(supplied,k))||Object.keys(supplied).some(k=>!Object.hasOwn(required,k)))fail('SERVICE_'+label+'_BINDINGS');}
 if(Object.values(operations).some(f=>typeof f!=='function'))fail('SERVICE_OPERATION_BINDINGS');
 if(!Number.isSafeInteger(maxRequestBytes)||maxRequestBytes<1||maxRequestBytes>plan.limits.requestBytes||!Number.isSafeInteger(readTimeoutMs)||readTimeoutMs<1||readTimeoutMs>plan.limits.readTimeoutMs)fail('SERVICE_LIMITS');
 const snapshot=structuredClone(contexts),bound={...operations};
 const json=(value:any,status:number,headers:Record<string,string>={})=>{const text=JSON.stringify(value);if(text===undefined)fail('SERVICE_OUTPUT');if(new TextEncoder().encode(text).length>plan.limits.responseBytes)fail('RESPONSE_TOO_LARGE');return new Response(text,{status,headers:{'content-type':'application/json','cache-control':'no-store',...headers}});};
 async function errorResponse(error:any,headers:Record<string,string>={}){
  try{const code=typeof error?.code==='string'&&error.code.length<=256?error.code:'';const id=error?.request_id;
   const mapped=await functions[plan.errors]({code,...(typeof id==='string'&&id.trim()&&id.length<=128?{request_id:id}:{})},{},{localOnly:true});
   return json(mapped.body,mapped.http_status,headers);
  }catch{return new Response(null,{status:500,headers:{'cache-control':'no-store'}});}
 }
 const handle=async(request:Request):Promise<Response>=>{
  try{
   checkSignal(request.signal);const pathname=new URL(request.url).pathname;const matching=plan.routes.filter((r:any)=>r.path===pathname);
   if(!matching.length)return errorResponse({code:'NOT_FOUND'});
   const route=matching.find((r:any)=>r.method===request.method);if(!route)return errorResponse({code:'METHOD_NOT_ALLOWED'},{allow:matching.map((r:any)=>r.method).sort().join(', ')});
   let input:any;
   if(route.input==='json'){
    if(request.headers.get('content-type')?.split(';')[0].trim().toLowerCase()!=='application/json')fail('UNSUPPORTED_MEDIA_TYPE');input=await body(request,maxRequestBytes,readTimeoutMs);
   }else input=route.input==='unit'?{unit:true}:structuredClone(snapshot[route.input.slice(8)]);
   const io={signal:request.signal,localOnly:true};let value:any;
   try{checkSignal(request.signal);value=await functions[route.function](input,{},io);}catch(error){checkSignal(request.signal);if(route.input==='json')fail('INVALID_INPUT');throw error;}
   checkSignal(request.signal);
   if(route.operation){
    // The native dependency receives JSON data, as it did across the old HTTP boundary.
    value=await bound[route.operation](JSON.parse(JSON.stringify(value)),{},{signal:request.signal,headers:request.headers});
    if(value instanceof Response){
     if(request.signal.aborted||route.response!=='json-or-sse'||value.status!==route.status||!value.body||!/^text\/event-stream(?:\s*;|$)/i.test(value.headers.get('content-type')??'')){
      void value.body?.cancel().catch(()=>{});checkSignal(request.signal);fail('SERVICE_RESPONSE_MODE');
     }
     return value;
    }
    checkSignal(request.signal);value=await functions[route.result](value,{},io);
   }
   checkSignal(request.signal);return json(route.output==='all'?value:value[route.output],route.status);
  }catch(error){return errorResponse(error);}
 };
 return Object.assign(handle,{errorResponse});
}
