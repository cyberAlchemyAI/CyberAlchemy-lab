import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {fork} from 'node:child_process';
import {once} from 'node:events';
import {randomBytes} from 'node:crypto';
import {setTimeout as delay} from 'node:timers/promises';
import {generateKeyPair,exportJWK,SignJWT} from '../../../../../../../../../auth-foundation/implementation/authentication-https/node_modules/jose/dist/webapi/index.js';
import {buildPublicPolicy} from '../../build-public-policy.mjs';
import {createEngineFixture} from '../../generated/local-pattern/fixture.mjs';
import {verifyBundle} from '../demo/run.mjs';
// Actual HTTP/process/SQLite/Rust authorization; isolated signed identity fixture.
// Open Questions: README.md.
test('protected HTTP, current authorization and durable replay across clean and abrupt process restart', {timeout:180000},async()=>{
 verifyBundle();const directory=mkdtempSync(join(tmpdir(),'protected-durable-')),children=[];
 const engine=createEngineFixture('protected mock result',{waitMs:300});let checks=0;
 const passed=name=>{checks++;console.log('CHECK '+name);};
 async function stop(worker,signal='SIGTERM'){if(worker.child.exitCode!==null||worker.child.signalCode!==null)return;worker.child.kill(signal);const [code,killed]=await worker.exit;if(signal==='SIGTERM')assert.equal(code,0);else assert.equal(killed,signal);}
 try{
  const bundle=join(directory,'compiled');mkdirSync(bundle);await buildPublicPolicy(bundle,{protectedService:true,durableCustody:true,localPattern:true});
  engine.server.listen(0,'127.0.0.1');await once(engine.server,'listening');
  const issuer='https://localhost:18443/realms/auth-https',keys=await generateKeyPair('RS256'),now=Math.floor(Date.now()/1000);
  const token=async(subject,key=keys.privateKey)=>new SignJWT({iss:issuer,sub:subject,aud:'prototype-api',azp:'prototype-browser',typ:'Bearer',iat:now,exp:now+300,jti:subject+'-session'}).setProtectedHeader({alg:'RS256'}).sign(key);
  const alice=await token('alice'),bob=await token('bob');
  const permission=(resource,action,scope)=>({resource,action,scope});
  const policy={revision:1,principals:['alice','bob'].map(subject=>({issuer,subject,kind:'human',client:'prototype-browser',enabled:true,memberships:['t1','t2'].map(tenant=>({tenant,enabled:true})),sessions:[{jti:subject+'-session',enabled:true,active_roles:['user']}]})),roles:[{id:'user',permissions:['t1','t2'].flatMap(t=>[permission('inference-catalog','discover',t),permission('balanced','use',t),permission('local-chat-a','invoke',t),permission('local-chat-a','stream',t)])}]};
  const policyFile=join(directory,'policy.json'),save=()=>writeFileSync(policyFile,JSON.stringify(policy));save();
  const config={bundle,issuer,publicKey:await exportJWK(keys.publicKey),binary:fileURLToPath(new URL('../../../../../../../../../auth-foundation/implementation/tenant-bridge/target/debug/auth-tenant-bridge',import.meta.url)),policy:policyFile,database:join(directory,'requests.db'),key:randomBytes(32).toString('hex'),host:{timeoutMs:10000,bindings:[{id:'local-a',version:'v1',model:'local-chat-a',remoteModel:'mock',url:'http://127.0.0.1:'+engine.server.address().port+'/infer',policy:{scope:'loopback',authentication:'none'}}],catalogs:{balanced:{tenant_id:'ignored',policy_version:'v1',providers:[{binding_id:'local-a',binding_version:'v1',model:'local-chat-a',enabled:true,tenant_allowed:false,task:'text.generate',context_limit:131072,output_limit:1024,streaming:true,rank:1}]}}}};
  const start=async()=>{
   const child=fork(new URL('./worker.mjs',import.meta.url),[],{stdio:['ignore','ignore','pipe','ipc']});children.push(child);child.stderr.resume();const exit=once(child,'exit');
   let timer;try{const message=await new Promise((yes,no)=>{timer=setTimeout(()=>no(Error('WORKER_START_TIMEOUT')),10000);child.once('error',no);child.once('exit',()=>no(Error('WORKER_START_FAILED')));child.once('message',yes);child.send(config);});assert.equal(message.ready,true);return {child,exit,url:message.url};}finally{clearTimeout(timer);}
  };
  const request={task:'text.generate',input:{messages:[{role:'user',content:'private rehearsal prompt'}]}};
  const call=async(worker,{path='/v1/inference',bearer=alice,tenant='t1',key='same-key',body=request}={})=>{
   const response=await fetch(worker.url+path,{method:path==='/v1/inference'?'POST':'GET',headers:{...(bearer?{authorization:'Bearer '+bearer}:{}),'x-tenant-id':tenant,'idempotency-key':key,'content-type':'application/json'},...(path==='/v1/inference'?{body:JSON.stringify(body)}:{}),signal:AbortSignal.timeout(15000)});
   const text=await response.text();return {status:response.status,value:response.headers.get('content-type')?.includes('application/json')?JSON.parse(text):text};
  };
  let worker=await start();
  assert.equal((await call(worker,{path:'/healthz',bearer:null})).status,200);assert.equal((await call(worker,{path:'/v1/models',bearer:null})).status,401);assert.equal(engine.calls.length,0);passed('anonymous health and protected discovery');
  assert.equal((await call(worker,{path:'/v1/models',bearer:await token('alice',(await generateKeyPair('RS256')).privateKey)})).status,401);passed('invalid signature denied');
  assert.equal((await call(worker,{tenant:'outside'})).status,403);assert.equal(engine.calls.length,0);passed('tenant selector does not grant access');
  const models=await call(worker,{path:'/v1/models'});assert.equal(models.status,200);assert.deepEqual(models.value.models.map(m=>m.id),['local-chat-a']);passed('Rust-authorized discovery');
  const first=await call(worker);assert.equal(first.status,200);assert.equal(first.value.output.text,'protected mock result');assert.equal(engine.calls.length,1);passed('authorized JSON through generated service and real mock HTTP');
  await stop(worker);worker=await start();assert.deepEqual((await call(worker)).value,first.value);assert.equal(engine.calls.length,1);passed('same principal replays original result after process restart');
  assert.equal((await call(worker,{body:{...request,parameters:{max_output_tokens:12}}})).status,409);assert.equal(engine.calls.length,1);passed('changed request conflicts after restart');
  const saved=structuredClone(policy.roles[0].permissions);policy.roles[0].permissions=policy.roles[0].permissions.filter(p=>p.action!=='invoke');save();assert.equal((await call(worker)).status,403);assert.equal(engine.calls.length,1);passed('current grant removal blocks durable replay');
  policy.roles[0].permissions=saved;save();assert.deepEqual((await call(worker)).value,first.value);assert.equal(engine.calls.length,1);passed('restored permission replays without executing');
  const other=await call(worker,{bearer:bob});assert.equal(other.status,200);assert.notEqual(other.value.request_id,first.value.request_id);assert.equal(engine.calls.length,2);passed('same key in another principal creates isolated execution');
  const otherTenant=await call(worker,{tenant:'t2'});assert.equal(otherTenant.status,200);assert.notEqual(otherTenant.value.request_id,first.value.request_id);assert.equal(engine.calls.length,3);passed('same key in another tenant creates isolated execution');
  const stream=await call(worker,{key:'stream-key',body:{...request,stream:true}});assert.equal(stream.status,200);assert.match(stream.value,/event: completed/);await stop(worker);worker=await start();assert.equal((await call(worker,{key:'stream-key',body:{...request,stream:true}})).status,409);assert.equal(engine.calls.length,4);passed('completed stream does not reexecute after restart');
  const pending=call(worker,{key:'interrupted'}).catch(()=>null);const deadline=Date.now()+5000;while(engine.calls.length<5&&Date.now()<deadline)await delay(5);assert.equal(engine.calls.length,5);await stop(worker,'SIGKILL');await pending;await delay(350);worker=await start();assert.equal((await call(worker,{key:'interrupted'})).status,409);assert.equal(engine.calls.length,5);passed('abrupt exit leaves uncertain request non-executable');
  policy.principals[0].sessions[0].enabled=false;save();assert.equal((await call(worker)).status,403);assert.equal(engine.calls.length,5);passed('revoked authorization session cannot replay');
  for(const c of engine.calls)assert.equal(c.headers.authorization,undefined);
  const bytes=readFileSync(config.database);for(const secret of ['private rehearsal prompt','protected mock result',alice])assert.ok(!bytes.includes(Buffer.from(secret)));passed('encrypted SQLite and separate upstream no-auth boundary');
  await stop(worker);verifyBundle();assert.equal(checks,15);
 }finally{
  for(const child of children)if(child.exitCode===null&&child.signalCode===null){const exited=once(child,'exit');child.kill('SIGKILL');await exited;}
  engine.server.closeAllConnections();if(engine.server.listening)await new Promise(r=>engine.server.close(r));rmSync(directory,{recursive:true,force:true});
 }
});
