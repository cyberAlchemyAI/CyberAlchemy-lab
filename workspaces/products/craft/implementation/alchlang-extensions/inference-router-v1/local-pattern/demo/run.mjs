import {readFileSync,realpathSync} from 'node:fs';
import {resolve,dirname,relative,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash,randomUUID} from 'node:crypto';
import {once} from 'node:events';
import assert from 'node:assert/strict';
// Demo orchestration only; accepted generated policies own behavior. Open Questions: README.md.
const here=dirname(fileURLToPath(import.meta.url));
const defaultBundle=resolve(here,'../../generated/local-pattern');
const acceptance=JSON.parse(readFileSync(resolve(here,'../ACCEPTANCE.json')));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function verifyBundle(bundle=defaultBundle){
 const root=realpathSync(bundle),bytes=readFileSync(resolve(root,'manifest.json'));
 if(sha(bytes)!==acceptance.accepted_candidate.manifest_sha256)throw Error('ACCEPTED_MANIFEST_MISMATCH');
 const manifest=JSON.parse(bytes);
 for(const [name,hash]of Object.entries(manifest.files)){
  const path=realpathSync(resolve(root,name)),rel=relative(root,path);
  if(isAbsolute(rel)||rel==='..'||rel.startsWith('../')||sha(readFileSync(path))!==hash)throw Error('ACCEPTED_FILE_MISMATCH: '+name);
 }
 return root;
}
const close=async server=>{if(!server.listening)return;server.closeAllConnections();await new Promise((yes,no)=>server.close(e=>e?no(e):yes()));};
export async function runDemo({serve=false,signal,onReady=()=>{},report=console.log,bundle=defaultBundle}={}){
 const root=verifyBundle(bundle),servers=[];
 const check=()=>signal?.throwIfAborted();
 const listen=async server=>{check();servers.push(server);server.listen(0,'127.0.0.1');await once(server,'listening');check();return 'http://127.0.0.1:'+server.address().port;};
 try{
  check();const {createEngineFixture}=await import(pathToFileURL(resolve(root,'fixture.mjs')).href);
  const {createServer}=await import(pathToFileURL(resolve(root,'index.mjs')).href);
  const a=createEngineFixture('Mock engine A'),b=createEngineFixture('Mock engine B');
  const engineA=await listen(a.server),engineB=await listen(b.server);
  const config=JSON.parse(readFileSync(resolve(root,'configuration.example.json')));
  config.engines[0].url=engineA+'/infer';config.engines[1].url=engineB+'/infer';
  const url=await listen(createServer(config));onReady({url,engines:[engineA,engineB]});
  report('Mock inference service: '+url);
  const examples=[];
  const request={task:'text.generate',input:{messages:[{role:'user',content:'Hello from the API walkthrough'}]}};
  const call=async(path,{body,headers={}}={})=>{
   check();const control=signal?AbortSignal.any([signal,AbortSignal.timeout(10000)]):AbortSignal.timeout(10000);
   const response=await fetch(url+path,{method:body?'POST':'GET',headers:{...(body?{'content-type':'application/json'}:{}),...headers},...(body?{body:JSON.stringify(body)}:{}),signal:control});
   const text=await response.text();return {status:response.status,body:response.headers.get('content-type')?.includes('application/json')?JSON.parse(text):text};
  };
  const record=(name,value)=>{examples.push({name,...value});report('PASS '+name+' ('+value.status+')');};
  let result=await call('/healthz');assert.equal(result.status,200);record('liveness',result);
  result=await call('/v1/models');assert.equal(result.status,200);assert.match(JSON.stringify(result.body),/local-chat-a/);assert.match(JSON.stringify(result.body),/local-chat-b/);record('model discovery',result);
  result=await call('/v1/capabilities');assert.equal(result.status,200);record('capability discovery',result);
  const key=randomUUID(),headers={'idempotency-key':key};
  result=await call('/v1/inference',{body:request,headers});assert.equal(result.status,200);assert.equal(result.body.model,'local-chat-a');assert.equal(result.body.output.text,'Mock engine A');record('automatic JSON inference',result);
  const original=result.body,count=a.calls.length;
  result=await call('/v1/inference',{body:request,headers});assert.deepEqual(result.body,original);assert.equal(a.calls.length,count);record('JSON replay without execution',result);
  result=await call('/v1/inference',{body:{...request,parameters:{max_output_tokens:12}},headers});assert.equal(result.status,409);assert.equal(a.calls.length,count);record('idempotency conflict',result);
  result=await call('/v1/inference',{body:{...request,model:'local-chat-b'}});assert.equal(result.status,200);assert.equal(result.body.output.text,'Mock engine B');record('explicit model inference',result);
  const streamHeaders={'idempotency-key':randomUUID()};
  result=await call('/v1/inference',{body:{...request,stream:true},headers:streamHeaders});assert.equal(result.status,200);for(const event of ['started','delta','completed'])assert.match(result.body,new RegExp('event: '+event));assert.doesNotMatch(result.body,/event: error/);record('SSE inference',result);
  const streamCount=a.calls.length;
  result=await call('/v1/inference',{body:{...request,stream:true},headers:streamHeaders});assert.equal(result.status,409);assert.equal(a.calls.length,streamCount);record('stream replay rejection',result);
  const calls=a.calls.length+b.calls.length;
  result=await call('/v1/inference',{body:{...request,model:'unknown-model'}});assert.equal(result.status,404);record('unknown model',result);
  result=await call('/v1/inference',{body:{...request,unexpected:true}});assert.equal(result.status,400);record('invalid request',result);
  assert.equal(a.calls.length+b.calls.length,calls);
  for(const call of [...a.calls,...b.calls])assert.equal(call.headers.authorization,undefined);
  report('Walkthrough complete: '+examples.length+' checks; deterministic mocks, no LLM required.');
  if(serve){report('Ready for API calls. Press Ctrl+C to stop the service and both engines.');if(!signal)throw Error('SERVE_SIGNAL_REQUIRED');if(!signal.aborted)await new Promise(r=>signal.addEventListener('abort',r,{once:true}));}
  return {status:'passed',checks:examples.length,url,examples,authority_effect:'none'};
 }finally{for(const server of servers.reverse())await close(server);report('Stopped service and mock engines.');}
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){
 const args=process.argv.slice(2);if(args.some(a=>a!=='--serve')||args.length>1)throw Error('Usage: node demo/run.mjs [--serve]');
 const controller=new AbortController(),stop=()=>controller.abort();process.once('SIGINT',stop);process.once('SIGTERM',stop);
 try{await runDemo({serve:args.includes('--serve'),signal:controller.signal});}catch(error){if(!controller.signal.aborted){console.error(error);process.exitCode=1;}}
 finally{process.off('SIGINT',stop);process.off('SIGTERM',stop);}
}
