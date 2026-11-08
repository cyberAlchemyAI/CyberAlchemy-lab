import {randomUUID} from 'node:crypto';
import {createPublicHandler} from './native/host.mjs';
import {createNodeServiceServer} from './native/node-service-host.js';
// Operator configuration and dependency wiring only. Open Questions: README.md.
const fail=()=>{throw Error('INVALID_LOCAL_CONFIGURATION');};
const closed=(v,keys)=>{if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>!keys.includes(k)))fail();};
const integer=(n,min,max)=>{if(!Number.isSafeInteger(n)||n<min||n>max)fail();};
const id=v=>{if(typeof v!=='string'||!v.trim()||v.length>128)fail();};
export function localConfiguration(value,env={}){
 const c=structuredClone(value);
 closed(c,['protocol','contextBound','engines','timeoutMs']);
 if(c.protocol!=='alch-local-text/v1')fail();
 integer(c.timeoutMs,1,30000);
 closed(c.contextBound,['version','inputTokens']);id(c.contextBound.version);integer(c.contextBound.inputTokens,0,999999);
 if(!Array.isArray(c.engines)||c.engines.length<1||c.engines.length>100)fail();
 const ids=new Set();
 const bindings=[],providers=[];
 for(const e of c.engines){
  closed(e,['id','version','model','remoteModel','url','authentication','secretEnv','contextLimit','outputLimit','streaming','rank','enabled']);
  for(const k of ['id','version','model','remoteModel'])id(e[k]);
  if(ids.has(e.id))fail();ids.add(e.id);
  integer(e.contextLimit,1,1000000);integer(e.outputLimit,1,1000000);integer(e.rank,0,1000000);
  if(typeof e.enabled!=='boolean'||typeof e.streaming!=='boolean'||!['none','bearer'].includes(e.authentication))fail();
  let secret;
  if(e.authentication==='bearer'){if(typeof e.secretEnv!=='string'||!/^[_A-Z][_A-Z0-9]*$/.test(e.secretEnv))fail();secret=env[e.secretEnv];if(typeof secret!=='string'||!secret)fail();}
  else if(e.secretEnv!==undefined)fail();
  bindings.push({id:e.id,version:e.version,model:e.model,remoteModel:e.remoteModel,url:e.url,policy:{scope:'loopback',authentication:e.authentication},...(secret===undefined?{}:{secret})});
  providers.push({binding_id:e.id,binding_version:e.version,model:e.model,enabled:e.enabled,tenant_allowed:true,task:'text.generate',context_limit:e.contextLimit,output_limit:e.outputLimit,streaming:e.streaming,rank:e.rank});
 }
 return {bindings,catalogs:{balanced:{tenant_id:'public',policy_version:'local-v1-'+c.contextBound.version,providers}},timeoutMs:c.timeoutMs,
  estimateContext:({max_output_tokens})=>c.contextBound.inputTokens+max_output_tokens};
}
export function createLocalServer(policy,config,env={}){
 const handle=createPublicHandler({...policy,...localConfiguration(config,env),token:randomUUID()});
 // This minimal composition is loopback-only; protected hosting remains separate.
 let server;
 const guarded=async request=>{
  const port=server.address()?.port,host=request.headers.get('host');
  if(host!==`127.0.0.1:${port}`||request.headers.has('forwarded')||[...request.headers.keys()].some(k=>k.startsWith('x-forwarded-'))||
   request.headers.has('origin')&&request.headers.get('origin')!==`http://127.0.0.1:${port}`)return new Response(null,{status:403});
  return handle(request);
 };
 server=createNodeServiceServer(guarded,handle.errorResponse);
 return server;
}
