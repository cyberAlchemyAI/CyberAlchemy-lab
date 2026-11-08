import {createServer} from 'node:http';
import {once} from 'node:events';
import {randomBytes,timingSafeEqual} from 'node:crypto';
import {authHeaders,endpoint,fail} from './config.mjs';
// Wire translation only. Generated Alch/DomainSpec retains public policy and lifecycle.
// Open Questions: README.md.
const MAX_UPSTREAM=1048576;
async function bytes(body,max){let size=0;const chunks=[];for await(const c of body){size+=c.length;if(size>max)fail('VLLM_RESPONSE_TOO_LARGE');chunks.push(c);}return Buffer.concat(chunks);}
export async function api(base,path,{body,headers={},signal}={}){
 const response=await fetch(endpoint(base)+path,{method:body?'POST':'GET',headers:{...headers,...(body?{'content-type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{}),redirect:'error',signal});
 if(!response.ok){await response.body?.cancel();fail('VLLM_HTTP_'+response.status);}
 return response;
}
export async function jsonApi(base,path,options){
 const response=await api(base,path,options);if(!response.headers.get('content-type')?.includes('application/json')){await response.body?.cancel();fail('VLLM_INVALID_CONTENT_TYPE');}
 return JSON.parse((await bytes(response.body,MAX_UPSTREAM)).toString('utf8'));
}
export async function models(base,options){
 const body=await jsonApi(base,'/v1/models',options);
 if(!Array.isArray(body.data)||!body.data.length||body.data.length>100)fail('VLLM_INVALID_MODELS');
 return body.data.map(m=>{if(typeof m?.id!=='string'||!m.id||m.id.length>128)fail('VLLM_INVALID_MODEL');return {id:m.id,max_model_len:m.max_model_len};});
}
function usage(value){
 const count=v=>{if(v==null)return null;if(!Number.isSafeInteger(v)||v<0||v>1000000000)fail('VLLM_INVALID_USAGE');return v;};
 return {prompt_tokens:count(value?.prompt_tokens),completion_tokens:count(value?.completion_tokens)};
}
const reason=value=>{if(typeof value!=='string'||!value)fail('VLLM_MISSING_FINISH_REASON');if(['tool_calls','function_call'].includes(value))fail('VLLM_UNSUPPORTED_TOOL_CALL');return ['stop','length','content_filter'].includes(value)?value:'unknown';};
export function mapCompletion(body){
 if(!Array.isArray(body?.choices)||body.choices.length!==1)fail('VLLM_INVALID_CHOICES');const c=body.choices[0];
 if(c.index!==0||typeof c.message?.content!=='string'||c.message.content.length>32768||c.message.tool_calls?.length||c.message.function_call)fail('VLLM_INVALID_COMPLETION');
 return {answer:c.message.content,stop_reason:reason(c.finish_reason),...usage(body.usage)};
}
export async function* streamEvents(body){
 const reader=body.getReader(),decoder=new TextDecoder('utf-8',{fatal:true});let buffer='',total=0;
 try{
  while(true){const {value,done}=await reader.read();if(done){buffer+=decoder.decode();if(buffer.trim())fail('VLLM_INCOMPLETE_EVENT');return;}
   total+=value.length;if(total>MAX_UPSTREAM)fail('VLLM_STREAM_TOO_LARGE');buffer+=decoder.decode(value,{stream:true});
   let match;while((match=/\r?\n\r?\n/.exec(buffer))){const frame=buffer.slice(0,match.index);buffer=buffer.slice(match.index+match[0].length);if(Buffer.byteLength(frame)>65536)fail('VLLM_EVENT_TOO_LARGE');
    const data=frame.split(/\r?\n/).filter(l=>l.startsWith('data:')).map(l=>l.slice(5).replace(/^ /,'')).join('\n');if(data)yield data;
   }
   if(Buffer.byteLength(buffer)>65536)fail('VLLM_EVENT_TOO_LARGE');
  }
 }finally{await reader.cancel().catch(()=>{});reader.releaseLock();}
}
export async function* mapStream(body){
 let finish=null,observations=usage(),length=0;
 for await(const data of streamEvents(body)){
  if(data==='[DONE]'){if(!finish)fail('VLLM_MISSING_FINISH_REASON');yield {event:'completed',data:{stop_reason:finish,...observations}};return;}
  const chunk=JSON.parse(data);if(chunk.error)fail('VLLM_STREAM_ERROR');
  if(chunk.usage!=null)observations=usage(chunk.usage);
  if(!Array.isArray(chunk.choices)||chunk.choices.length>1)fail('VLLM_INVALID_CHOICES');
  if(!chunk.choices.length)continue;
  if(finish)fail('VLLM_EVENT_AFTER_FINISH');const c=chunk.choices[0];
  if(c.index!==0||!c.delta||typeof c.delta!=='object'||c.delta.tool_calls?.length||c.delta.function_call)fail('VLLM_INVALID_DELTA');
  const content=c.delta.content;if(content!=null){if(typeof content!=='string')fail('VLLM_INVALID_DELTA');length+=content.length;if(length>32768)fail('VLLM_TEXT_TOO_LARGE');
   for(let i=0;i<content.length;i+=2000)yield {event:'delta',data:{text:content.slice(i,i+2000)}};
  }
  if(c.finish_reason!=null)finish=reason(c.finish_reason);
 }
 fail('VLLM_INCOMPLETE_STREAM');
}
export async function tokenize(base,c,messages,maxTokens,{headers,signal}={}){
 const t=await jsonApi(base,'/tokenize',{body:{model:c.model,messages,add_generation_prompt:true},headers,signal});
 if(!Number.isSafeInteger(t.count)||t.count<0||t.count>c.contextLimit-c.outputLimit||t.count+maxTokens>c.contextLimit)fail('VLLM_CONTEXT_LIMIT');
 return t.count;
}
export async function createBridge(c,base,{signal,env=process.env}={}){
 const headers=authHeaders(c,env),secret=randomBytes(32).toString('hex'),controllers=new Set();let active=0;
 const server=createServer(async(req,res)=>{
  const expected=Buffer.from('Bearer '+secret),provided=Buffer.from(req.headers.authorization??'');
  if(req.method!=='POST'||req.url!=='/infer'||req.headers.host!==`127.0.0.1:${server.address().port}`||req.headers.origin||Object.keys(req.headers).some(k=>k==='forwarded'||k.startsWith('x-forwarded-'))||provided.length!==expected.length||!timingSafeEqual(expected,provided)){res.writeHead(403).end();return;}
  if(active>=2){res.writeHead(503).end();return;}active++;
  const controller=new AbortController();controllers.add(controller);const abort=()=>controller.abort();req.once('aborted',abort);res.once('close',()=>{if(!res.writableEnded)abort();});
  const control=AbortSignal.any([controller.signal,AbortSignal.timeout(c.timeoutMs),...(signal?[signal]:[])]);
  const terminate=()=>{if(!res.writableEnded)res.destroy();};control.addEventListener('abort',terminate,{once:true});
  try{
   const payload=JSON.parse((await bytes(req,65536)).toString('utf8'));
   if(payload.model!==c.model||!Array.isArray(payload.messages)||!Number.isSafeInteger(payload.max_tokens)||payload.max_tokens<1||payload.max_tokens>c.outputLimit||typeof payload.stream!=='boolean')fail('INVALID_ENGINE_REQUEST');
   await tokenize(base,c,payload.messages,payload.max_tokens,{headers,signal:control});
   const body={model:c.model,messages:payload.messages,max_tokens:payload.max_tokens,stream:payload.stream,n:1,...(payload.stream?{stream_options:{include_usage:true}}:{})};
   if(!payload.stream){const result=mapCompletion(await jsonApi(base,'/v1/chat/completions',{body,headers,signal:control}));res.writeHead(200,{'content-type':'application/json'}).end(JSON.stringify(result));}
   else{
    const response=await api(base,'/v1/chat/completions',{body,headers,signal:control});
    if(!response.headers.get('content-type')?.includes('text/event-stream')){await response.body?.cancel();fail('VLLM_INVALID_CONTENT_TYPE');}
    res.writeHead(200,{'content-type':'text/event-stream','cache-control':'no-cache'});let sent=0;
    for await(const frame of mapStream(response.body)){const text=`event: ${frame.event}\ndata: ${JSON.stringify(frame.data)}\n\n`;sent+=Buffer.byteLength(text);if(sent>65536)fail('VLLM_NORMALIZED_STREAM_TOO_LARGE');if(!res.write(text))await once(res,'drain',{signal:control});}
    res.end();
   }
  }catch{
   control.removeEventListener('abort',terminate);controller.abort();if(!res.destroyed){if(!res.headersSent)res.writeHead(502,{'content-type':'application/json'}).end('{"error":"VLLM_BINDING_FAILED"}');else res.end('event: error\ndata: {"code":"VLLM_BINDING_FAILED"}\n\n');}
  }finally{control.removeEventListener('abort',terminate);controllers.delete(controller);active--;}
 });
 signal?.throwIfAborted();server.listen(0,'127.0.0.1');await once(server,'listening');
 const close=async()=>{for(const c of controllers)c.abort();server.closeAllConnections();if(server.listening)await new Promise(r=>server.close(r));};
 return {url:`http://127.0.0.1:${server.address().port}/infer`,secret,close,server};
}
