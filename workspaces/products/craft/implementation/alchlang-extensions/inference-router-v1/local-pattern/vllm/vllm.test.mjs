import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtempSync,statSync,readFileSync,rmSync,chmodSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
import {configuration,endpoint,saveConfiguration,readConfiguration} from './config.mjs';
import {configure,parseOptions} from './cli.mjs';
import {startEngine,smoke} from './engine.mjs';
import {mapCompletion,mapStream,models} from './transport.mjs';
import {sshArguments,discoverRemote,startTunnel} from './ssh.mjs';
// Real sockets and accepted generated service; no remote instance/model required.
// Open Questions: README.md.
const textStream=s=>new ReadableStream({start(c){for(const b of Buffer.from(s))c.enqueue(Uint8Array.of(b));c.close();}});
const event=o=>'data: '+JSON.stringify(o)+'\r\n\r\n';
const chunks=()=>event({choices:[{index:0,delta:{role:'assistant',reasoning:'private reasoning'},finish_reason:null}]})+event({choices:[{index:0,delta:{content:'Héllo'},finish_reason:null}]})+event({choices:[{index:0,delta:{},finish_reason:'stop'}]})+event({choices:[],usage:{prompt_tokens:5,completion_tokens:3}})+'data: [DONE]\r\n\r\n';
async function fixture({token,behavior='normal',tokens=5}={}){
 const calls=[];let cancelled=false;
 const server=createServer(async(req,res)=>{
  const parts=[];for await(const part of req)parts.push(part);const body=parts.length?JSON.parse(Buffer.concat(parts)):null;calls.push({path:req.url,body,authorization:req.headers.authorization});
  if(token&&req.headers.authorization!=='Bearer '+token){res.writeHead(401).end('private failure detail');return;}
  const json=data=>res.writeHead(200,{'content-type':'application/json'}).end(JSON.stringify(data));
  if(req.url==='/v1/models')return json({data:[{id:'Qwen/test-27B',max_model_len:4096}]});
  if(req.url==='/tokenize')return json({count:tokens,tokens:[1,2,3]});
  if(req.url!=='/v1/chat/completions'){res.writeHead(404).end();return;}
  if(behavior==='http-error'){res.writeHead(500).end('private failure detail');return;}
  if(behavior==='redirect'){res.writeHead(307,{location:'/secret'}).end();return;}
  if(behavior==='wait'){res.once('close',()=>{cancelled=true;});return;}
  if(body.stream){res.writeHead(200,{'content-type':'text/event-stream'});const stream=behavior==='incomplete'?chunks().replace('data: [DONE]\r\n\r\n',''):chunks();res.end(stream);}
  else json({choices:[{index:0,message:{role:'assistant',content:'Héllo',reasoning:'private reasoning'},finish_reason:'stop'}],usage:{prompt_tokens:5,completion_tokens:3}});
 });
 server.listen(0,'127.0.0.1');await once(server,'listening');
 return {url:'http://127.0.0.1:'+server.address().port,server,calls,get cancelled(){return cancelled;},close:async()=>{server.closeAllConnections();await new Promise(r=>server.close(r));}};
}
const config=(url,extra={})=>configuration({schema_version:'alch.vllm-engine/v1',connection:{type:'direct',baseUrl:url},model:'Qwen/test-27B',alias:'vllm-chat',contextLimit:4096,outputLimit:256,timeoutMs:3000,...extra});
const request={task:'text.generate',input:{messages:[{role:'user',content:'Hello'}]},parameters:{max_output_tokens:32}};
async function call(url,body=request,headers={}){const r=await fetch(url+'/v1/inference',{method:'POST',headers:{'content-type':'application/json',...headers},body:JSON.stringify(body)});return {status:r.status,text:await r.text()};}

test('configure discovers exact model, verifies tokenizer and writes private reusable config',async()=>{
 const f=await fixture(),dir=mkdtempSync(join(tmpdir(),'vllm-config-')),file=join(dir,'engine.json');
 try{
  const c=await configure({yes:true,'base-url':f.url,config:file},{report:()=>{}});assert.equal(c.model,'Qwen/test-27B');assert.equal(statSync(file).mode&0o777,0o600);assert.deepEqual(readConfiguration(file),c);
  assert.equal(f.calls.some(c=>c.path==='/v1/chat/completions'),false);
  await assert.rejects(configure({yes:true,'base-url':f.url,config:file},{report:()=>{}}),/ENGINE_CONFIG_EXISTS/);
  chmodSync(file,0o644);assert.throws(()=>readConfiguration(file),/PRIVATE_REGULAR/);
 }finally{await f.close();rmSync(dir,{recursive:true,force:true});}
});
test('real service maps JSON/SSE/usage, keeps reasoning private and replays without another model execution',async()=>{
 const f=await fixture({token:'secret-fixture'});let engine;
 try{
  engine=await startEngine(config(f.url,{tokenEnv:'TEST_VLLM_TOKEN'}),{env:{TEST_VLLM_TOKEN:'secret-fixture'}});
  assert.equal((await smoke(engine.url)).status,'passed');
  const a=await call(engine.url,request,{'idempotency-key':'real-vllm-key'}),n=f.calls.length,b=await call(engine.url,request,{'idempotency-key':'real-vllm-key'});
  assert.equal(a.status,200);assert.deepEqual(a,b);assert.equal(f.calls.length,n);assert.equal(JSON.parse(a.text).output.text,'Héllo');assert.doesNotMatch(a.text,/private reasoning|secret-fixture/);
  assert.ok(f.calls.every(c=>c.authorization==='Bearer secret-fixture'));
  for(const c of f.calls.filter(c=>c.path==='/v1/chat/completions'))assert.equal(c.body.n,1);
 }finally{await engine?.close();await f.close();}
});
test('stream parser handles fragmented UTF-8, usage trailers and exactly one completion',async()=>{
 const frames=[];for await(const frame of mapStream(textStream(chunks())))frames.push(frame);
 assert.deepEqual(frames,[{event:'delta',data:{text:'Héllo'}},{event:'completed',data:{stop_reason:'stop',prompt_tokens:5,completion_tokens:3}}]);
 const mapped=mapCompletion({choices:[{index:0,message:{content:'ok'},finish_reason:'stop'}]});assert.equal(mapped.prompt_tokens,null);
});
test('stream truncation, tool calls, malformed events and byte limits fail closed',async()=>{
 for(const content of [chunks().replace('data: [DONE]\r\n\r\n',''),'data: [DONE]\n\n','data: not-json\n\n',event({choices:[{index:0,delta:{tool_calls:[{}]},finish_reason:'tool_calls'}]}),'data: '+ 'x'.repeat(65537)]){
  await assert.rejects(async()=>{for await(const frame of mapStream(textStream(content)))void frame;});
 }
 assert.throws(()=>mapCompletion({choices:[{index:0,message:{content:null,reasoning:'secret'},finish_reason:'stop'}]}),/INVALID_COMPLETION/);
});
test('upstream failures, redirects and incomplete streams never become successful completions',async()=>{
 for(const behavior of ['http-error','redirect','incomplete']){
  const f=await fixture({behavior});let engine;
  try{engine=await startEngine(config(f.url));const r=await call(engine.url,{...request,stream:behavior==='incomplete'});assert.doesNotMatch(r.text,/private failure detail/);if(behavior==='incomplete'){assert.match(r.text,/event: error/);assert.doesNotMatch(r.text,/event: completed/);}else assert.notEqual(r.status,200);assert.equal(f.calls.filter(c=>c.path==='/v1/chat/completions').length,1);assert.equal(f.calls.some(c=>c.path==='/secret'),false);}
  finally{await engine?.close();await f.close();}
 }
});
test('tokenizer limit blocks generation before the model executes',async()=>{
 const f=await fixture({tokens:4000});
 try{await assert.rejects(startEngine(config(f.url)),/VLLM_CONTEXT_LIMIT/);assert.equal(f.calls.some(c=>c.path==='/v1/chat/completions'),false);}finally{await f.close();}
});
test('deadline cancels upstream HTTP without retry',async()=>{
 const f=await fixture({behavior:'wait'});let engine;
 try{engine=await startEngine(config(f.url,{timeoutMs:150}));const r=await call(engine.url);assert.notEqual(r.status,200);for(let i=0;i<50&&!f.cancelled;i++)await delay(10);assert.equal(f.cancelled,true);assert.equal(f.calls.filter(c=>c.path==='/v1/chat/completions').length,1);}finally{await engine?.close();await f.close();}
});
test('unsafe configuration and SSH option injection are rejected',()=>{
 for(const url of ['http://example.com','https://user:secret@example.com','https://example.com/?token=secret'])assert.throws(()=>endpoint(url));
 for(const host of ['-oProxyCommand=bad','host; touch bad','host\nother'])assert.throws(()=>sshArguments({host,user:'root',port:22}));
 assert.throws(()=>parseOptions(['--token','secret']));assert.throws(()=>parseOptions(['--base-url','https://example.com','--host','host']));assert.throws(()=>configuration({...config('http://127.0.0.1:8000'),secret:'bad'}));
 const a=sshArguments({host:'example.com',user:'root',port:25453});assert.ok(a.includes('StrictHostKeyChecking=yes'));assert.ok(a.includes('BatchMode=yes'));
});
test('remote discovery script reports only model IDs and ports using read-only HTTP',async()=>{
 const f=await fixture();try{
  const found=await discoverRemote({host:'fixture',user:'root',port:22},{spawnProcess:(_cmd,_args,opts)=>spawn('python3',['-'],opts)});
  const selected=found.find(r=>r.port===f.server.address().port);assert.equal(selected.models[0].id,'Qwen/test-27B');assert.equal(JSON.stringify(found).includes('authorization'),false);
 }finally{await f.close();}
});
test('SSH tunnel lifecycle forwards traffic and service stops when tunnel exits',async()=>{
 const f=await fixture();let child,engine;
 const spawnProcess=(_cmd,args,opts)=>{
  const forward=args[args.indexOf('-L')+1].split(':');assert.equal(forward[0],'127.0.0.1');
  const code=`const net=require('node:net');const sockets=new Set();const server=net.createServer(a=>{const b=net.connect(${Number(forward[3])},'127.0.0.1');for(const s of [a,b]){sockets.add(s);s.on('error',()=>{});s.on('close',()=>sockets.delete(s));}a.pipe(b);b.pipe(a);});server.listen(${Number(forward[1])},'127.0.0.1');process.on('SIGTERM',()=>{for(const s of sockets)s.destroy();server.close(()=>process.exit(0));});`;
  child=spawn(process.execPath,['-e',code],opts);return child;
 };
 try{
  const c=config(f.url,{connection:{type:'ssh',ssh:{host:'fixture',port:22,user:'root',remotePort:f.server.address().port}}});
  engine=await startEngine(c,{tunnelFactory:(settings,options)=>startTunnel(settings,{...options,spawnProcess})});assert.equal((await call(engine.url)).status,200);
  child.kill('SIGTERM');await once(child,'close');for(let i=0;i<50&&!engine.signal.aborted;i++)await delay(10);assert.equal(engine.signal.aborted,true);await engine.close();await assert.rejects(fetch(engine.url+'/healthz'));
 }finally{await engine?.close();child?.kill();await f.close();}
});
test('CLI configure/check/test/serve round trip and SIGTERM cleanup',{timeout:20000},async()=>{
 const f=await fixture(),dir=mkdtempSync(join(tmpdir(),'vllm-cli-')),file=join(dir,'engine.json');let serving;
 const cli=new URL('./cli.mjs',import.meta.url).pathname;
 const command=async args=>{
  const child=spawn(process.execPath,[cli,...args],{stdio:['ignore','pipe','pipe']});let output='';child.stdout.on('data',c=>output+=c);child.stderr.on('data',c=>output+=c);const [code]=await once(child,'close');assert.equal(code,0,output);return output;
 };
 try{
  assert.match(await command(['configure-engine','--yes','--base-url',f.url,'--config',file]),/Configured vllm-chat/);
  assert.match(await command(['check-engine','--config',file]),/PASS/);
  assert.match(await command(['test-engine','--config',file]),/"status":"passed"/);
  serving=spawn(process.execPath,[cli,'engine','--config',file],{stdio:['ignore','pipe','pipe']});let output='';serving.stdout.on('data',c=>output+=c);serving.stderr.on('data',c=>output+=c);
  for(let i=0;i<200&&!output.includes('Inference service:');i++)await delay(25);
  const url=/Inference service: (http:\/\/127\.0\.0\.1:\d+)/.exec(output)?.[1];assert.ok(url,output);assert.equal((await fetch(url+'/healthz')).status,200);
  const done=once(serving,'close');serving.kill('SIGTERM');assert.equal((await done)[0],0);await assert.rejects(fetch(url+'/healthz'));
 }finally{serving?.kill('SIGKILL');await f.close();rmSync(dir,{recursive:true,force:true});}
});
