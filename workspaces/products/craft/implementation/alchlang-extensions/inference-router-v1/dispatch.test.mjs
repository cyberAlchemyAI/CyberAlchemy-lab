import {createStreamSession} from '../../implementation/dist/stream-runtime.js';
import {buildPublicPolicy} from './build-public-policy.mjs';
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {mkdtempSync,rmSync,writeFileSync} from 'node:fs';
import {spawn} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {buildFunction} from '../../implementation/dist/function-builder.js';
import {createPublicServer,createPublicHandler} from './host.mjs';
import {createDispatcher} from './dispatch.mjs';
import {createIdempotentDispatcher} from './idempotency.mjs';
const dir=mkdtempSync(join(tmpdir(),'inference-dispatch-'));
const handlers={};let server,url;const calls=[];
before(async()=>{
 for(const [key,name] of [['policy','idempotency-policy']]){
  await buildFunction(fileURLToPath(new URL(name+'.alch',import.meta.url)),join(dir,name));
  handlers[key]=(await import(pathToFileURL(join(dir,name,'app/function/index.mjs')).href)).handler;
 }
 Object.assign(handlers,await buildPublicPolicy(dir));
 server=createServer(async(req,res)=>{let body='';for await(const chunk of req)body+=chunk;calls.push({url:req.url,authorization:req.headers.authorization,body:JSON.parse(body)});if(JSON.parse(body).stream){res.writeHead(200,{'content-type':'text/event-stream'});res.write('event: delta\ndata: {"text":"hello"}\n\n');setTimeout(()=>res.end('event: completed\ndata: {"stop_reason":"stop"}\n\n'),20);return;}res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify({answer:'fixture:'+req.url,stop_reason:'stop',prompt_tokens:4,completion_tokens:2}));});
 server.listen(0,'127.0.0.1');await once(server,'listening');url='http://127.0.0.1:'+server.address().port;
});
after(async()=>{server?.closeAllConnections();if(server)await new Promise(r=>server.close(r));rmSync(dir,{recursive:true,force:true});});
const row=(id,rank)=>({binding_id:id,binding_version:'v1',model:'fixture-'+id,enabled:true,tenant_allowed:true,task:'text.generate',context_limit:4096,output_limit:1024,streaming:false,rank});
const input=()=>({request:{request_id:'r1',tenant_id:'t1',task:'text.generate',required_context_tokens:512,max_output_tokens:256,stream:false},catalog:{tenant_id:'t1',policy_version:'balanced-v1',providers:[row('a',10),row('b',20)]},messages:[{role:'user',content:'hello'}]});
const config=()=>({...handlers,token:'internal-fixture',allowLoopbackFixtures:true,bindings:['a','b'].map(id=>({id,version:'v1',model:'fixture-'+id,remoteModel:'deployment-'+id,url:url+'/'+id,secret:'secret-'+id}))});
test('real loopback POST composes compiled selection, request and response mappings',async()=>{
 const run=createDispatcher(config());const first=await run(input());assert.equal(first.output.text,'fixture:/a');assert.equal(first.model,'fixture-a');assert.equal(first.usage.input_tokens.value,4);
 const second=input();second.request.model='fixture-b';assert.equal((await run(second)).output.text,'fixture:/b');
 assert.deepEqual(calls.map(c=>c.body),['a','b'].map(id=>({messages:[{role:'user',content:'hello'}],model:'deployment-'+id,max_tokens:256,stream:false})));
 assert.deepEqual(calls.map(c=>c.authorization),['Bearer secret-a','Bearer secret-b']);assert.ok(!JSON.stringify(first).includes('secret'));
});
test('missing usage remains null with unavailable provenance',async()=>{
 const run=createDispatcher({...config(),fetchImpl:async()=>Response.json({answer:'x',stop_reason:'stop'})});
 assert.deepEqual((await run(input())).usage,{input_tokens:{value:null,provenance:'unavailable'},output_tokens:{value:null,provenance:'unavailable'}});
});
test('malformed messages and no eligible provider cause no transport call',async()=>{
 let calls=0;const run=createDispatcher({...config(),fetchImpl:async()=>{calls++;return Response.json({});}});
 for(const messages of [[],[{role:'tool',content:'x'}],[{role:'user',content:''}]])await assert.rejects(run({...input(),messages}),/INVALID_INPUT/);
 const i=input();i.catalog.providers=[];await assert.rejects(run(i),/NO_ELIGIBLE_PROVIDER/);assert.equal(calls,0);
});
test('binding version mismatch fails before sending secrets',async()=>{
 let calls=0;const i=input();i.catalog.providers[0].binding_version='v2';const run=createDispatcher({...config(),fetchImpl:async()=>{calls++;return Response.json({});}});
 await assert.rejects(run(i),/BINDING_MISMATCH/);assert.equal(calls,0);
});
test('provider errors, redirects and ambiguous transport failure never retry',async()=>{
 for(const status of [302,429,500]){let n=0;const run=createDispatcher({...config(),fetchImpl:async(_,opts)=>{n++;assert.equal(opts.redirect,'manual');return new Response('secret diagnostic',{status});}});await assert.rejects(run(input()),/PROVIDER_STATUS/);assert.equal(n,1);}
 let n=0;const run=createDispatcher({...config(),fetchImpl:async()=>{n++;throw Error('secret diagnostic');}});await assert.rejects(run(input()),/PROVIDER_TRANSPORT_FAILED/);assert.equal(n,1);
});
test('invalid JSON, malformed usage and response size overflow fail closed',async()=>{
 for(const make of [()=>new Response('{'),()=>Response.json({answer:'x',stop_reason:'stop',prompt_tokens:-1}),()=>new Response('x'.repeat(65537))]){
 const run=createDispatcher({...config(),fetchImpl:async()=>make()});await assert.rejects(run(input()),/INVALID_PROVIDER_RESPONSE|RESPONSE_TOO_LARGE/);}
});
test('deadlines retain occupied slots until the transport settles',async()=>{
 let release;const run=createDispatcher({...config(),maxConcurrent:1,timeoutMs:20,fetchImpl:()=>new Promise(r=>{release=r;})});
 await assert.rejects(run(input()),/DEADLINE_EXCEEDED/);await assert.rejects(run(input()),/OVERLOADED/);
 release(Response.json({answer:'x',stop_reason:'stop'}));await new Promise(r=>setTimeout(r,10));
});
test('cancellation, streaming and unsafe provider configuration reject explicitly',async()=>{
 const controller=new AbortController();controller.abort();await assert.rejects(createDispatcher(config())({...input(),signal:controller.signal}),/CANCELLED/);
 const i=input();i.request.stream=true;await assert.rejects(createDispatcher({...config(),streamFactory:undefined})(i),/STREAMING_NOT_SUPPORTED/);
 assert.throws(()=>createDispatcher({...config(),allowLoopbackFixtures:false}),/INVALID_PROVIDER_URL/);
});

const streamInput=()=>{const i=input();i.request.stream=true;i.catalog.providers.forEach(p=>p.streaming=true);return i;};
const frames=text=>text.trim().split('\n\n').map(frame=>({event:frame.split('\n')[0].slice(7),data:JSON.parse(frame.split('\n')[1].slice(6))}));
const sse=text=>new Response(text,{headers:{'content-type':'text/event-stream'}});
test('loopback SSE sends incremental deltas and one completion with fixed identity',async()=>{
 const response=await createDispatcher(config())(streamInput());assert.equal(response.headers.get('content-type'),'text/event-stream; charset=utf-8');
 const f=frames(await response.text());assert.deepEqual(f.map(x=>x.event),['started','delta','completed']);assert.equal(f[1].data.text,'hello');
 assert.ok(f.every(x=>x.data.model==='fixture-a'&&x.data.request_id==='r1'));assert.equal(f[2].data.usage.input_tokens.value,null);
});
test('UTF-8 and CRLF split across chunks remain incremental before completion',async()=>{
 let feed;const body=new ReadableStream({start(c){feed=c;}});const run=createDispatcher({...config(),fetchImpl:async()=>new Response(body,{headers:{'content-type':'text/event-stream'}})});
 const response=await run(streamInput());const reader=response.body.getReader();assert.match(new TextDecoder().decode((await reader.read()).value),/event: started/);
 const bytes=new TextEncoder().encode('event: delta\r\ndata: {"text":"€"}\r\n\r\n');for(const byte of bytes)feed.enqueue(Uint8Array.of(byte));
 const delta=new TextDecoder().decode((await reader.read()).value);assert.match(delta,/€/);assert.match(delta,/event: delta/);
 feed.enqueue(new TextEncoder().encode('event: completed\ndata: {"stop_reason":"stop"}\n\n'));
 assert.match(new TextDecoder().decode((await reader.read()).value),/event: completed/);assert.equal((await reader.read()).done,true);
});
test('partial failure and premature EOF produce one sanitized error without fallback',async()=>{
 for(const suffix of ['', 'event: error\ndata: {"message":"secret provider diagnostic"}\n\n','event: delta\ndata: {broken}\n\n']){
 let n=0;const response=await createDispatcher({...config(),fetchImpl:async()=>{n++;return sse('event: delta\ndata: {"text":"partial"}\n\n'+suffix);}})(streamInput());
 const text=await response.text();const f=frames(text);assert.deepEqual(f.map(x=>x.event),['started','delta','error']);assert.ok(!text.includes('secret provider diagnostic'));assert.equal(n,1);
 }
});
test('stream deadline emits terminal error while consumer cancellation aborts upstream',async()=>{
 let upstreamSignal;const response=await createDispatcher({...config(),timeoutMs:30,fetchImpl:async(_,opts)=>{upstreamSignal=opts.signal;return new Response(new ReadableStream(),{headers:{'content-type':'text/event-stream'}});}})(streamInput());
 const f=frames(await response.text());assert.equal(f.at(-1).data.error.code,'DEADLINE_EXCEEDED');assert.equal(upstreamSignal.aborted,true);
 let cancelled=false;const second=await createDispatcher({...config(),fetchImpl:async()=>new Response(new ReadableStream({cancel(){cancelled=true;}}),{headers:{'content-type':'text/event-stream'}})})(streamInput());
 await second.body.cancel();assert.equal(cancelled,true);
});
test('invalid media type and oversized SSE frames reject without exposing payload',async()=>{
 await assert.rejects(createDispatcher({...config(),fetchImpl:async()=>Response.json({})})(streamInput()),/INVALID_STREAM_CONTENT_TYPE/);
 const response=await createDispatcher({...config(),fetchImpl:async()=>sse('data: '+ 'x'.repeat(17000))})(streamInput());assert.equal(frames(await response.text()).at(-1).data.error.code,'EVENT_TOO_LARGE');
});

test('deadline during completion mapping cannot turn an expired stream into success',async()=>{
 const slow=async(...args)=>{await new Promise(r=>setTimeout(r,60));return handlers.streamModules.Completed(...args);};
 const response=await createDispatcher({...config(),timeoutMs:20,streamFactory:session=>createStreamSession(handlers.streamContract,{...handlers.streamModules,Completed:slow},session),fetchImpl:async()=>sse('event: completed\ndata: {"stop_reason":"stop"}\n\n')})(streamInput());
 const f=frames(await response.text());assert.deepEqual(f.map(x=>x.event),['started','error']);assert.equal(f.at(-1).data.error.code,'DEADLINE_EXCEEDED');
});

const store=(options={},dispatchOptions={})=>createIdempotentDispatcher({custodyFactory:handlers.custodyFactory,dispatch:createDispatcher({...config(),...dispatchOptions}),token:'internal-fixture',...options});
const keyed=()=>({...input(),idempotencyKey:'key-1'});
test('completed JSON duplicates replay a copy without provider calls or rerouting',async()=>{
 let n=0;const s=store({}, {fetchImpl:async()=>{n++;return Response.json({answer:'original',stop_reason:'stop'});}});
 const first=await s.run(keyed());first.output.text='mutated';const again=keyed();again.request.request_id='new-client-id';again.catalog.providers.reverse();
 const replay=await s.run(again);assert.equal(replay.output.text,'original');assert.equal(replay.request_id,first.request_id);assert.equal(n,1);
 const record=s.inspect()[0];assert.equal(record.state,'completed');assert.equal(record.attempt.binding_id,'a');assert.equal(record.attempt.remote_completion,'reported-complete');assert.equal(record.attempt.usage.input_tokens.value,null);assert.ok(!JSON.stringify(record).includes('hello'));
});
test('concurrent duplicates report original identity and never start a second attempt',async()=>{
 let release,started;const begun=new Promise(r=>{started=r;});let n=0;
 const s=store({}, {fetchImpl:()=>{n++;started();return new Promise(r=>{release=r;});}});
 const first=s.run(keyed());await begun;
 await assert.rejects(s.run(keyed()),e=>e.code==='REQUEST_IN_PROGRESS'&&e.request_id===s.inspect()[0].id);
 release(Response.json({answer:'x',stop_reason:'stop'}));await first;assert.equal(n,1);
});
test('different input conflicts while the same key in another tenant is independent',async()=>{
 let n=0;const s=store({}, {fetchImpl:async()=>{n++;return Response.json({answer:'x',stop_reason:'stop'});}});await s.run(keyed());
 const changed=keyed();changed.messages[0].content='different';await assert.rejects(s.run(changed),/IDEMPOTENCY_CONFLICT/);
 const other=keyed();other.request.tenant_id=other.catalog.tenant_id='t2';await s.run(other);assert.equal(n,2);
});
test('retained failures cannot automatically execute again',async()=>{
 let n=0;const s=store({}, {fetchImpl:async()=>{n++;throw Error('provider diagnostic');}});
 await assert.rejects(s.run(keyed()),/PROVIDER_TRANSPORT_FAILED/);await assert.rejects(s.run(keyed()),/PREVIOUS_REQUEST_FAILED/);assert.equal(n,1);assert.equal(s.inspect()[0].attempt.remote_completion,'unknown');
});
test('expired settled records can execute anew; pending records cannot expire',async()=>{
 let now=0,n=0;const s=store({clock:()=>now,retentionMs:10,maxEntries:1},{fetchImpl:async()=>{n++;return Response.json({answer:'x',stop_reason:'stop'});}});
 await s.run(keyed());now=11;await s.run(keyed());assert.equal(n,2);
 let release,started;const begun=new Promise(r=>{started=r;});const pending=store({clock:()=>now,retentionMs:1,maxEntries:1},{fetchImpl:()=>{started();return new Promise(r=>{release=r;});}});
 const first=pending.run(keyed());await begun;now=1000;await assert.rejects(pending.run(keyed()),/REQUEST_IN_PROGRESS/);
 await assert.rejects(pending.run({...keyed(),idempotencyKey:'other'}),/REQUEST_STORE_FULL/);release(Response.json({answer:'x',stop_reason:'stop'}));await first;
});
test('deadline ambiguity stays pending until the actual transport settles',async()=>{
 let release;const s=store({retentionMs:1},{timeoutMs:15,fetchImpl:()=>new Promise(r=>{release=r;})});
 await assert.rejects(s.run(keyed()),/DEADLINE_EXCEEDED/);await assert.rejects(s.run(keyed()),/REQUEST_IN_PROGRESS/);assert.equal(s.inspect()[0].settled,false);
 release(Response.json({answer:'late',stop_reason:'stop'}));await new Promise(r=>setTimeout(r,5));
});
test('stream duplicates never re-execute and stream outcomes are tracked',async()=>{
 let n=0;const s=store({}, {fetchImpl:async()=>{n++;return sse('event: delta\ndata: {"text":"x"}\n\nevent: completed\ndata: {"stop_reason":"stop"}\n\n');}});
 const i={...streamInput(),idempotencyKey:'stream-key'};const response=await s.run(i);await response.text();await new Promise(r=>setTimeout(r,0));
 await assert.rejects(s.run(i),/STREAM_NOT_REPLAYABLE/);assert.equal(n,1);assert.equal(s.inspect()[0].state,'stream_completed');
});
test('key and request byte limits reject before transport',async()=>{
 let n=0;const s=store({}, {fetchImpl:async()=>{n++;return Response.json({});}});
 await assert.rejects(s.run({...keyed(),idempotencyKey:'x'.repeat(129)}),/INVALID_IDEMPOTENCY_KEY/);
 const i=keyed();i.messages[0].content='x'.repeat(65537);await assert.rejects(s.run(i),/REQUEST_TOO_LARGE/);assert.equal(n,0);
});

test('bounded reservation queue rejects overload before scheduling more policy work',async()=>{
 let release;let entered;const begun=new Promise(r=>{entered=r;});
 const policy=async(...args)=>{entered();await new Promise(r=>{release=r;});return handlers.policy(...args);};
 const s=store({maxEntries:1,policy},{fetchImpl:async()=>Response.json({answer:'x',stop_reason:'stop'})});
 const first=s.run(keyed());await begun;await assert.rejects(s.run(keyed()),/REQUEST_STORE_BUSY/);release();await first;
});
test('materialized defaults share a retained key and unkeyed calls stay independent',async()=>{
 let n=0;const s=store({}, {fetchImpl:async()=>{n++;return Response.json({answer:'x',stop_reason:'stop'});}});
 await s.run(keyed());const defaults=keyed();delete defaults.request.stream;delete defaults.request.max_output_tokens;await s.run(defaults);assert.equal(n,1);
 await s.run(input());await s.run(input());assert.equal(n,3);
});

const hostConfig=()=>({...config(),catalogs:{balanced:streamInput().catalog},estimateContext:()=>512});
const publicBody=()=>({task:'text.generate',input:{messages:[{role:'user',content:'hello'}]}});
const publicRequest=(body=publicBody(),headers={})=>new Request('http://localhost/v1/inference',{method:'POST',headers:{'content-type':'application/json',...headers},body:JSON.stringify(body)});
async function withHost(fn,options={}){
 const host=createPublicServer({...hostConfig(),...options});host.listen(0,'127.0.0.1');await once(host,'listening');
 try{await fn('http://127.0.0.1:'+host.address().port);}finally{host.closeAllConnections();await new Promise(r=>host.close(r));}
}
test('public HTTP discovery exposes only operator model aliases and configured capabilities',async()=>{
 await withHost(async base=>{
  assert.deepEqual(await(await fetch(base+'/healthz')).json(),{status:'ok'});
  const models=await(await fetch(base+'/v1/models')).json();assert.deepEqual(models.models.map(m=>m.id),['fixture-a','fixture-b']);
  assert.ok(!/secret|binding_id|deployment-|tenant_allowed|127\.0\.0\.1/.test(JSON.stringify(models)));
  const cap=await(await fetch(base+'/v1/capabilities')).json();assert.deepEqual(cap.routing_strategies,['balanced']);assert.equal(cap.scope,'shared-public');assert.equal(cap.authentication,'deferred');
  const method=await fetch(base+'/v1/models',{method:'POST'});assert.equal(method.status,405);assert.equal(method.headers.get('allow'),'GET');
  assert.equal((await fetch(base+'/internal/select-provider')).status,404);
 });
});
test('public HTTP JSON defaults and idempotency replay use the compiled pipeline',async()=>{
 await withHost(async base=>{
  const n=calls.length;const send=body=>fetch(base+'/v1/inference',{method:'POST',headers:{'content-type':'application/json','idempotency-key':'public-replay'},body:JSON.stringify(body)});
  const response=await send(publicBody());assert.equal(response.status,200,await response.clone().text());const first=await response.json();assert.equal(first.output.text,'fixture:/a');assert.match(first.request_id,/^[0-9a-f-]{36}$/);
  const second=await send({...publicBody(),stream:false,parameters:{max_output_tokens:256},routing:{strategy:'balanced'}});assert.equal(second.status,200);assert.deepEqual(await second.json(),first);assert.equal(calls.length,n+1);
  const conflict=await send({...publicBody(),model:'fixture-b'});assert.equal(conflict.status,409);assert.equal((await conflict.json()).error.code,'IDEMPOTENCY_CONFLICT');
 });
});
test('public request contract rejects injected configuration and invalid nested inputs before transport',async()=>{
 const handle=createPublicHandler(hostConfig());const n=calls.length;
 for(const body of [null,[],{...publicBody(),tenant_id:'other'},{...publicBody(),catalog:{}},{...publicBody(),url:'http://evil'}, {...publicBody(),input:{messages:[],extra:1}}, {...publicBody(),routing:{strategy:'balanced',rank:0}}, {...publicBody(),parameters:{max_output_tokens:0}}, {...publicBody(),stream:'true'}, {...publicBody(),input:{messages:[{role:'user',content:'hello',secret:'x'}]}}]){
  const response=await handle(publicRequest(body));assert.equal(response.status,400,JSON.stringify(body));
 }
 assert.equal((await handle(publicRequest({...publicBody(),model:'unknown'}))).status,404);
 assert.equal((await handle(publicRequest({...publicBody(),routing:{strategy:'cost'}}))).status,400);
 assert.equal(calls.length,n);
});
test('public HTTP SSE preserves terminal events and prevents stream reexecution',async()=>{
 await withHost(async base=>{
  const n=calls.length;const send=()=>fetch(base+'/v1/inference',{method:'POST',headers:{'content-type':'application/json','idempotency-key':'public-stream'},body:JSON.stringify({...publicBody(),stream:true})});
  const response=await send();assert.equal(response.status,200);assert.match(response.headers.get('content-type'),/text\/event-stream/);
  const events=frames(await response.text());assert.deepEqual(events.map(e=>e.event),['started','delta','completed']);assert.equal(events[1].data.text,'hello');
  assert.equal((await send()).status,409);assert.equal(calls.length,n+1);
 });
});
test('public body limits, JSON and media type errors are bounded and sanitized',async()=>{
 const handle=createPublicHandler({...hostConfig(),maxRequestBytes:512});
 for(const [body,headers,status] of [['x'.repeat(513),{'content-type':'application/json'},413],['{',{'content-type':'application/json'},400],['{}',{'content-type':'text/plain'},415]]){
  assert.equal((await handle(new Request('http://localhost/v1/inference',{method:'POST',headers,body}))).status,status);
 }
 const upstream=createPublicHandler({...hostConfig(),fetchImpl:async()=>{throw Error('secret diagnostic');}});
 const response=await upstream(publicRequest());assert.equal(response.status,502);assert.ok(!(await response.text()).includes('secret'));
});
test('HTTP client disconnect propagates cancellation to provider stream',async()=>{
 let signal;let stopped;const cancelled=new Promise(r=>{stopped=r;});
 await withHost(async base=>{
  const controller=new AbortController();const response=await fetch(base+'/v1/inference',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({...publicBody(),stream:true}),signal:controller.signal});
  const reader=response.body.getReader();await reader.read();controller.abort();await reader.cancel().catch(()=>{});
  await Promise.race([cancelled,new Promise((_,reject)=>{const timer=setTimeout(()=>reject(Error('cancellation missing')),1000);timer.unref();})]);assert.equal(signal.aborted,true);
 },{fetchImpl:async(_,opts)=>{signal=opts.signal;return new Response(new ReadableStream({cancel(){stopped();}}),{headers:{'content-type':'text/event-stream'}});}});
});
test('changing public routing strategy conflicts instead of replaying another policy',async()=>{
 const cfg=hostConfig();cfg.catalogs.cost={...structuredClone(cfg.catalogs.balanced),policy_version:'cost-v1'};
 const handle=createPublicHandler(cfg);const headers={'idempotency-key':'strategy'};
 assert.equal((await handle(publicRequest(publicBody(),headers))).status,200);
 const response=await handle(publicRequest({...publicBody(),routing:{strategy:'cost'}},headers));
 assert.equal(response.status,409);assert.equal((await response.json()).error.code,'IDEMPOTENCY_CONFLICT');
});
test('public host snapshots operator catalogs and hides disabled offerings',async()=>{
 const cfg=hostConfig();cfg.catalogs.balanced.providers[1].enabled=false;
 const handle=createPublicHandler(cfg);cfg.catalogs.balanced.providers[0].enabled=false;
 const discovery=await(await handle(new Request('http://localhost/v1/models'))).json();assert.deepEqual(discovery.models.map(m=>m.id),['fixture-a']);
 assert.equal((await handle(publicRequest())).status,200);
 const invalid=createPublicHandler({...hostConfig(),estimateContext:()=>NaN});assert.equal((await invalid(publicRequest())).status,500);
});
test('local launcher builds protected Alch handlers and shuts down cleanly',async()=>{
 const configPath=join(dir,'operator-config.mjs');
 writeFileSync(configPath,'export default {authFoundation:{binary:"/absolute/uninvoked-test-bridge",policy:"/absolute/uninvoked-test-policy",profile:{issuer:"https://localhost:18443/realms/auth-https",origin:"https://localhost:13443",browserClient:"prototype-browser",serviceClient:"prototype-service",apiSecret:"disposable-test-secret"}},token:"fixture",bindings:[],catalogs:{balanced:{policy_version:"balanced-v1",providers:[]}},estimateContext:()=>256};');
 const child=spawn(process.execPath,[fileURLToPath(new URL('serve.mjs',import.meta.url)),configPath,'0'],{env:process.env,stdio:['ignore','pipe','pipe']});
 let output='',errors='';child.stderr.on('data',chunk=>{errors+=chunk;});
 const exited=once(child,'exit');
 try{
  const base=await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(Error('host launch timeout: '+errors)),180000);
   child.stdout.on('data',chunk=>{output+=chunk;const match=output.match(/Inference host: (http:\/\/127\.0\.0\.1:\d+)/);if(match){clearTimeout(timer);resolve(match[1]);}});
   child.once('exit',code=>{clearTimeout(timer);reject(Error('host exited '+code+': '+errors));});
   child.once('error',error=>{clearTimeout(timer);reject(error);});
  });
  assert.equal((await fetch(base+'/healthz')).status,200);
  assert.equal((await fetch(base+'/v1/models')).status,401);
 }finally{child.kill('SIGTERM');const [code]=await exited;assert.equal(code,0,errors);}
});
test('HTTP chunked request overflow returns a structured 413',async()=>{
 await withHost(async base=>{
  const body=new ReadableStream({start(c){c.enqueue(new TextEncoder().encode('x'.repeat(600)));c.close();}});
  const response=await fetch(base+'/v1/inference',{method:'POST',headers:{'content-type':'application/json'},body,duplex:'half'});
  assert.equal(response.status,413);assert.equal((await response.json()).error.code,'REQUEST_TOO_LARGE');
 },{maxRequestBytes:512});
});

// ISB-03 regressions use the generated discovery and error definitions.
test('compiled discovery groups aliases across strategies with independent minima and redaction',async()=>{
 const cfg=hostConfig();const a=cfg.catalogs.balanced.providers[0];a.context_limit=8192;a.output_limit=128;a.streaming=false;
 cfg.catalogs.balanced.providers[1].enabled=false;
 cfg.catalogs.cost={policy_version:'cost-v1',providers:[{...a,context_limit:2048,output_limit:512,streaming:true}]};
 const handle=createPublicHandler(cfg);
 assert.deepEqual(await(await handle(new Request('http://localhost/v1/models'))).json(),{models:[{id:'fixture-a',task:'text.generate',context_limit:2048,output_limit:128,streaming:true}]});
 const cap=await(await handle(new Request('http://localhost/v1/capabilities'))).json();assert.deepEqual(cap.routing_strategies,['balanced','cost']);assert.equal(cap.streaming,true);assert.equal(cap.authorization,'deferred');
 assert.ok(!/binding|secret|deployment|tenant_allowed|rank|policy_version/.test(JSON.stringify(cap)));
});
test('compiled capabilities retain configured strategies for an empty or disabled catalog',async()=>{
 for(const providers of [[],[{...row('a',1),enabled:false,streaming:true}]]){
  const cfg=hostConfig();cfg.catalogs.balanced.providers=providers;cfg.catalogs.latency={policy_version:'latency-v1',providers:[]};cfg.store={retentionMs:1234};
  const handle=createPublicHandler(cfg);assert.deepEqual(await(await handle(new Request('http://localhost/v1/models'))).json(),{models:[]});
  assert.deepEqual(await(await handle(new Request('http://localhost/v1/capabilities'))).json(),{tasks:['text.generate'],routing_strategies:['balanced','latency'],streaming:false,authentication:'deferred',authorization:'deferred',scope:'shared-public',idempotency:{storage:'memory',retention_ms:1234,stream_replay:false}});
 }
});
test('compiled public error policy covers every existing status and sanitizes unknown faults',async()=>{
 const groups={400:['INVALID_INPUT','INVALID_IDEMPOTENCY_KEY','UNSUPPORTED_STRATEGY'],404:['UNKNOWN_MODEL','NOT_FOUND'],405:['METHOD_NOT_ALLOWED'],409:['IDEMPOTENCY_CONFLICT','REQUEST_IN_PROGRESS','STREAM_NOT_REPLAYABLE','PREVIOUS_REQUEST_FAILED'],413:['REQUEST_TOO_LARGE'],415:['UNSUPPORTED_MEDIA_TYPE'],429:['OVERLOADED','REQUEST_STORE_BUSY','REQUEST_STORE_FULL'],499:['CANCELLED'],502:['PROVIDER_STATUS','PROVIDER_TRANSPORT_FAILED','INVALID_PROVIDER_RESPONSE','RESPONSE_TOO_LARGE','INVALID_STREAM_CONTENT_TYPE'],503:['NO_ELIGIBLE_PROVIDER'],504:['DEADLINE_EXCEEDED']};
 for(const [status,codes]of Object.entries(groups))for(const code of codes){const out=await handlers.errorMapper({code,request_id:'r1'});assert.equal(out.http_status,Number(status));assert.deepEqual(out.body,{request_id:'r1',error:{code}});}
 for(const code of ['secret provider diagnostic','constructor','toString','']){const out=await handlers.errorMapper({code});assert.equal(out.http_status,500);assert.deepEqual(JSON.parse(JSON.stringify(out.body)),{error:{code:'INTERNAL_ERROR'}});}
});
test('compiled model iteration rejects oversized alias sets without leaking a partial list',async()=>{
 const providers=Array.from({length:101},(_,n)=>({...row('a',1),model:'alias-'+n}));await assert.rejects(handlers.modelsMapper({providers}),/QUERY_ITERATION_ITEM_LIMIT/);
});

test('compiled stream errors preserve known codes and redact unknown diagnostics',async()=>{
 for(const code of ['CANCELLED','DEADLINE_EXCEEDED','RESPONSE_TOO_LARGE','EVENT_TOO_LARGE','INCOMPLETE_PROVIDER_STREAM','INVALID_PROVIDER_EVENT','PROVIDER_STREAM_ERROR','INVALID_PROVIDER_RESPONSE'])assert.deepEqual((await handlers.streamErrorMapper({code})).error,{code});
 assert.deepEqual((await handlers.streamErrorMapper({code:'secret provider diagnostic'})).error,{code:'PROVIDER_STREAM_FAILED'});
});

test('awaited custody rejection prevents every outbound send',async()=>{
 let calls=0;const run=createDispatcher({...config(),fetchImpl:async()=>{calls++;return Response.json({});}});
 await assert.rejects(run({...input(),beforeAttempt:async()=>{throw Object.assign(Error('ATTEMPT_NOT_ALLOWED'),{code:'ATTEMPT_NOT_ALLOWED'});}}),/ATTEMPT_NOT_ALLOWED/);assert.equal(calls,0);
});
test('deadline during attempt gate prevents a late HTTP send',async()=>{
 let calls=0,release;const run=createDispatcher({...config(),timeoutMs:15,fetchImpl:async()=>{calls++;return Response.json({});}});
 await assert.rejects(run({...input(),beforeAttempt:()=>new Promise(r=>release=r)}),/DEADLINE_EXCEEDED/);release();await new Promise(r=>setTimeout(r,5));assert.equal(calls,0);
});
test('custody cancellation during policy evaluation leaves no retained request',async()=>{
 let release,entered;const started=new Promise(r=>entered=r),controller=new AbortController();
 const s=store({policy:async(...args)=>{entered();await new Promise(r=>release=r);return handlers.policy(...args);}});
 const pending=s.run({...keyed(),signal:controller.signal});await started;controller.abort();await assert.rejects(pending,/CANCELLED/);release();await new Promise(r=>setTimeout(r,5));assert.equal(s.inspect().length,0);
});
test('stream transport settlement without a terminal outcome cannot expire custody',async()=>{
 let now=0,observe;const s=createIdempotentDispatcher({custodyFactory:handlers.custodyFactory,clock:()=>now,retentionMs:1,dispatch:async input=>{observe=input.observe;await input.beforeAttempt({id:'a',version:'v1',model:'fixture-a',policyVersion:'balanced-v1'});observe({type:'transport_settled'});return new Response('pending');}});
 const request={...streamInput(),idempotencyKey:'stream-key'};await s.run(request);now=1000;await assert.rejects(s.run(request),/REQUEST_IN_PROGRESS/);assert.equal(s.inspect()[0].settled,false);observe({type:'stream_terminal',outcome:'cancelled'});await new Promise(r=>setImmediate(r));assert.equal(s.inspect()[0].settled,true);
});
