import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,cpSync,rmSync,readdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {buildServiceRoutes,loadServiceRoutes} from '../../../implementation/dist/service-routes.js';
import {createBoundary} from '../../../implementation/dist/boundary-runtime.js';
const base=fileURLToPath(new URL('../',import.meta.url));
const dir=mkdtempSync(join(tmpdir(),'alch-service-routes-'));let api;
before(async()=>{await buildServiceRoutes(join(base,'public-service.alch'),join(dir,'bundle'));api=await import(pathToFileURL(join(dir,'bundle/app/service/index.mjs')).href);});
after(()=>rmSync(dir,{recursive:true,force:true}));
const contexts=()=>({models:{providers:[]},capabilities:{providers:[],strategies:['balanced'],retention_ms:60000}});
const output=()=>({request_id:'r1',model:'demo',output:{text:'ok'},finish_reason:'stop',usage:{input_tokens:{value:null,provenance:'unavailable'},output_tokens:{value:null,provenance:'unavailable'}}});
const body=()=>({task:'text.generate',input:{messages:[{role:'user',content:'hello'}]}});
const request=(value=body(),signal)=>new Request('http://localhost/v1/inference',{method:'POST',headers:{'content-type':'application/json','idempotency-key':'key'},body:JSON.stringify(value),signal});
const create=(operation=async()=>output(),extra={})=>api.createHandler({contexts:contexts(),operations:{ExecuteInference:operation},...extra});
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
test('generated service normalizes input, preserves headers/signal and validates native JSON output',async()=>{
 let seen;const handle=create(async(input,_env,io)=>{seen={input,io};return output();});
 const req=request();const response=await handle(req);assert.equal(response.status,200);assert.deepEqual(await response.json(),output());
 assert.equal(Object.getPrototypeOf(seen.input.messages[0]),Object.prototype);assert.equal(seen.input.strategy,'balanced');assert.equal(seen.input.max_output_tokens,256);assert.equal(seen.io.signal,req.signal);assert.equal(seen.io.headers.get('idempotency-key'),'key');
 assert.deepEqual(await(await handle(new Request('http://localhost/healthz'))).json(),{status:'ok'});
 const broken=create(async()=>({...output(),private_secret:'must-not-escape'}));const out=await broken(request());assert.equal(out.status,500);assert.ok(!(await out.text()).includes('must-not-escape'));
});
test('missing, extra and non-callable native bindings or missing contexts reject at construction',()=>{
 for(const operations of [{},{ExecuteInference:1},{ExecuteInference:async()=>output(),Extra:async()=>{}}])assert.throws(()=>api.createHandler({contexts:contexts(),operations}),/SERVICE_OPERATION_BINDINGS/);
 assert.throws(()=>api.createHandler({contexts:{},operations:{ExecuteInference:async()=>output()}}),/SERVICE_CONTEXT_BINDINGS/);
 assert.throws(()=>create(undefined,{maxRequestBytes:65537}),/SERVICE_LIMITS/);
});
test('invalid JSON/media/fields and cancellation cause no native operation',async()=>{
 let calls=0;const handle=create(async()=>{calls++;return output();});
 for(const r of [request({...body(),private:'invalid'}),new Request('http://localhost/v1/inference',{method:'POST',headers:{'content-type':'application/json'},body:'{'}),new Request('http://localhost/v1/inference',{method:'POST',body:'{}'})])assert.ok((await handle(r)).status>=400);
 const controller=new AbortController();controller.abort();assert.equal((await handle(request(body(),controller.signal))).status,499);assert.equal(calls,0);
});
test('body read deadline and mid-read cancellation are bounded and sanitized',async()=>{
 const handle=create(async()=>{throw Error('must not execute');},{readTimeoutMs:15});
 const stalled=signal=>new Request('http://localhost/v1/inference',{method:'POST',headers:{'content-type':'application/json'},body:new ReadableStream(),duplex:'half',signal});
 assert.equal((await handle(stalled())).status,504);
 const controller=new AbortController();const pending=handle(stalled(controller.signal));controller.abort();assert.equal((await pending).status,499);
});
test('cancellation during a native operation reaches the binding and suppresses late success',async()=>{
 const controller=new AbortController();let entered;const started=new Promise(r=>{entered=r;});
 const handle=create(async(_value,_env,io)=>{entered();await new Promise(r=>io.signal.addEventListener('abort',r,{once:true}));return output();});
 const pending=handle(request(body(),controller.signal));await started;controller.abort();const response=await pending;assert.equal(response.status,499);
});
test('stream mode accepts SSE and rejects JSON Response bypasses and wrong status/media',async()=>{
 const stream=create(async()=>new Response('event: completed\ndata: {}\n\n',{headers:{'content-type':'text/event-stream'}}));assert.match((await stream(request())).headers.get('content-type'),/text\/event-stream/);
 for(const response of [Response.json(output()),new Response('private',{status:201,headers:{'content-type':'text/event-stream'}}),new Response('private',{headers:{'content-type':'text/plain'}})]){const handle=create(async()=>response);const result=await handle(request());assert.equal(result.status,500);assert.ok(!(await result.text()).includes('private'));}
});
function fixture(fn){const folder=mkdtempSync(join(dir,'source-'));for(const file of ['public-service.alch','public-request.alch'])cpSync(join(base,file),join(folder,file));for(const sub of ['discovery','service'])cpSync(join(base,sub),join(folder,sub),{recursive:true});return fn(folder);}
const replace=(folder,file,from,to)=>writeFileSync(join(folder,file),readFileSync(join(folder,file),'utf8').replace(from,to));
test('route compiler rejects duplicate routes, missing references, mismatched types and unsupported modes',()=>{
 const cases=[['status 200','status 205',/JSON success status/],['path "/v1/models"','path "/healthz"',/duplicate route/],['function Health','function Missing',/missing function/],['operation ExecuteInference','operation Missing',/missing operation/],['input PublicRequest.output','input Health.output',/incompatible operation types/],['output InferenceResult.input','output Health.output',/incompatible operation types/],['target node-http','target rust-http',/unsupported service/],['response json-or-sse','response sse',/unsupported operation/],['output value','output missing',/required output/],['authentication deferred','authentication bearer',/unsupported service/],['method GET','method DELETE',/unsupported route/],['max-request-bytes 65536','max-request-bytes 0',/invalid bound/],['path "/healthz"','path "//evil"',/unsupported route/],['import Health from "./service/health.alch"','import Health from "../health.alch"',/relative module/]];
 for(const [from,to,error]of cases)fixture(folder=>{replace(folder,'public-service.alch',from,to);assert.throws(()=>loadServiceRoutes(join(folder,'public-service.alch')),error);});
});
test('route manifest is deterministic, carries type/source bindings and inventories the generated bundle',()=>{
 const source=join(base,'public-service.alch');assert.deepEqual(loadServiceRoutes(source).plan,loadServiceRoutes(source).plan);
 assert.equal(api.plan.routes.length,4);assert.equal(api.plan.operations.ExecuteInference.inputType.type.strategy.type,'string');
 const manifest=JSON.parse(readFileSync(join(dir,'bundle/manifest.json')));assert.deepEqual(manifest.required_bindings,['ExecuteInference']);assert.equal(manifest.routes_sha256,sha(readFileSync(join(dir,'bundle/routes.json'))));
 for(const [file,hash]of Object.entries(manifest.files))assert.equal(sha(readFileSync(join(dir,'bundle',file))),hash);
 assert.equal(api.plan.functions.Models.source_sha256,sha(readFileSync(join(base,'discovery/models.alch'))));
});
test('changing an authored route changes generated dispatch and enforces response byte limits',async()=>{
 await fixture(async folder=>{
  replace(folder,'public-service.alch','path "/healthz"','path "/alive"');replace(folder,'public-service.alch','max-response-bytes 65536','max-response-bytes 128');
  await buildServiceRoutes(join(folder,'public-service.alch'),join(folder,'bundle'));const changed=await import(pathToFileURL(join(folder,'bundle/app/service/index.mjs')).href);
  const handle=changed.createHandler({contexts:contexts(),operations:{ExecuteInference:async()=>output()}});
  assert.equal((await handle(new Request('http://localhost/healthz'))).status,404);assert.deepEqual(await(await handle(new Request('http://localhost/alive'))).json(),{status:'ok'});
  const response=await handle(request());assert.equal(response.status,502);assert.equal((await response.json()).error.code,'RESPONSE_TOO_LARGE');
 });
});
test('existing generated function handler forwards request cancellation to integration I/O',async()=>{
 const model={schemas:{Input:{value:{type:'string'}},Output:{status:{type:'string',const:'ok'}}},integrations:{Remote:{transport:'http-get',output:'Input',urlEnv:'REMOTE_URL',timeout:1000,maxBytes:1024}},flows:{},endpoint:{path:'/test',method:'POST',input:'Input',output:'Output',authEnv:'TOKEN',maxBytes:1024,timeout:1000,statuses:{ok:200},errorStatus:500,errors:{}}};
 const boundary=createBoundary(model,[{name:'remote',integration:'Remote'}],()=>({status:'ok'}));const controller=new AbortController();let entered;const started=new Promise(r=>{entered=r;});let upstream;
 const pending=boundary.handler(new Request('http://localhost/test',{method:'POST',headers:{authorization:'Bearer token','content-type':'application/json'},body:'{"value":"x"}',signal:controller.signal}),{TOKEN:'token',REMOTE_URL:'https://example.invalid'}, {fetch:async(_url,options)=>{upstream=options.signal;entered();return new Promise((_,reject)=>upstream.addEventListener('abort',()=>reject(Error('aborted')),{once:true}));}});
 await started;controller.abort();await pending;assert.equal(upstream.aborted,true);
});
