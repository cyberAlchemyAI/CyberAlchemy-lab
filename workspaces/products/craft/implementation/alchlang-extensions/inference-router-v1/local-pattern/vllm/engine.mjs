import {once} from 'node:events';
import {pathToFileURL} from 'node:url';
import {join} from 'node:path';
import {configuration,authHeaders,fail} from './config.mjs';
import {startTunnel} from './ssh.mjs';
import {createBridge,models,tokenize} from './transport.mjs';
import {verifyBundle} from '../demo/run.mjs';
// Composition only; accepted generated service owns selection, API and custody.
// Open Questions: README.md.
export async function connect(c,{signal,tunnelFactory=startTunnel}={}){
 const tunnel=c.connection.type==='ssh'?await tunnelFactory(c.connection.ssh,{signal}):null;
 return {baseUrl:tunnel?.baseUrl??c.connection.baseUrl,close:tunnel?.close??(async()=>{}),closed:tunnel?.closed};
}
export async function checkConnection(c,base,{signal,env=process.env}={}){
 const headers=authHeaders(c,env),control=AbortSignal.any([AbortSignal.timeout(c.timeoutMs),...(signal?[signal]:[])]);
 const list=await models(base,{headers,signal:control});const selected=list.find(m=>m.id===c.model);if(!selected)fail('CONFIGURED_MODEL_NOT_SERVED');
 if(selected.max_model_len!=null&&(!Number.isSafeInteger(selected.max_model_len)||selected.max_model_len<c.contextLimit))fail('CONFIGURED_CONTEXT_EXCEEDS_SERVER');
 await tokenize(base,c,[{role:'user',content:'Hello'}],1,{headers,signal:control});return selected;
}
export async function startEngine(c,{signal,env=process.env,tunnelFactory=startTunnel}={}){
 configuration(c);const bundle=verifyBundle(),controller=new AbortController();
 const control=signal?AbortSignal.any([signal,controller.signal]):controller.signal;
 let connection,bridge,service,closing;
 const close=()=>closing??=(async()=>{controller.abort();if(service?.listening){service.closeAllConnections();await new Promise(r=>service.close(r));}await bridge?.close();await connection?.close();})();
 try{
  connection=await connect(c,{signal:control,tunnelFactory});connection.closed?.then(()=>controller.abort());
  await checkConnection(c,connection.baseUrl,{signal:control,env});
  bridge=await createBridge(c,connection.baseUrl,{signal:control,env});
  const {createServer}=await import(pathToFileURL(join(bundle,'index.mjs')).href);
  const config={protocol:'alch-local-text/v1',timeoutMs:c.timeoutMs,contextBound:{version:'vllm-tokenize-bounded-v1',inputTokens:c.contextLimit-c.outputLimit},engines:[{id:'vllm',version:'v1',model:c.alias,remoteModel:c.model,url:bridge.url,authentication:'bearer',secretEnv:'ALCH_VLLM_BRIDGE_TOKEN',contextLimit:c.contextLimit,outputLimit:c.outputLimit,streaming:true,rank:0,enabled:true}]};
  control.throwIfAborted();service=createServer(config,{ALCH_VLLM_BRIDGE_TOKEN:bridge.secret});service.listen(0,'127.0.0.1');await once(service,'listening');control.throwIfAborted();
  control.addEventListener('abort',()=>{void close();},{once:true});
  return {url:`http://127.0.0.1:${service.address().port}`,close,signal:control};
 }catch(error){await close();throw error;}
}
export async function smoke(url,{signal}={}){
 const body={task:'text.generate',input:{messages:[{role:'user',content:'Reply with a short greeting.'}]},parameters:{max_output_tokens:32}};
 for(const stream of [false,true]){
  const response=await fetch(url+'/v1/inference',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({...body,stream}),signal});
  if(!response.ok)fail('ENGINE_SMOKE_HTTP_'+response.status);const text=await response.text();
  if(stream){if(!text.includes('event: completed')||text.includes('event: error'))fail('ENGINE_SMOKE_STREAM_FAILED');}
  else if(typeof JSON.parse(text).output?.text!=='string')fail('ENGINE_SMOKE_JSON_FAILED');
 }
 return {status:'passed',checks:['JSON inference','SSE inference']};
}
