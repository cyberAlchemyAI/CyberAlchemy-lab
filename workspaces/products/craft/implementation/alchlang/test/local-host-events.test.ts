import { after, before, test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, execFileSync, type ChildProcess } from 'node:child_process';
import { once } from 'node:events';
import { mkdtempSync, readFileSync, rmSync, existsSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { buildLocalHost, compileLocalHost } from '../src/local-host.js';

const dir = fileURLToPath(new URL('../../extensions/local-host-events-v1/',import.meta.url));
const source = path.join(dir,'orders.alch');
const policy = JSON.parse(readFileSync(path.join(dir,'operator-policy.json'),'utf8'));
const fixture = JSON.parse(readFileSync(new URL('../../extensions/event-execution-v1/place-order.request.json',import.meta.url),'utf8'));
const temp = mkdtempSync(path.join(tmpdir(), 'alch-events-build-')); const bundle = path.join(temp,'bundle');
const roots: string[] = []; const processes = new Set<ChildProcess>();
const token = 'event_fixture_token_'.repeat(3);
const root = () => {const r=mkdtempSync(path.join(tmpdir(), 'alch-provision-'));roots.push(r);return r;};
const delay = (ms:number) => new Promise(r=>setTimeout(r,ms));
before(async()=>{await buildLocalHost(source,bundle);});
async function stop(p:ChildProcess){if(p.exitCode===null&&p.signalCode===null){const exit=once(p,'exit');p.kill('SIGTERM');await exit;}processes.delete(p);}
after(async()=>{for(const p of processes)await stop(p);for(const r of roots)rmSync(r,{recursive:true,force:true});rmSync(temp,{recursive:true,force:true});});

async function start(r:string, crash=false, grants=policy, credential=token, selectedBundle=bundle){
 const p=spawn('/usr/bin/python3',[path.join(selectedBundle,'serve.py'),'--run-root',r,...(crash?['--test-crash-after-consume']:[])],{env:{...process.env,PYTHONDONTWRITEBYTECODE:'1',ALCH_HOST_TOKEN:credential,ALCH_HOST_POLICY:JSON.stringify(grants)},stdio:['ignore','pipe','pipe']});processes.add(p);
 return await new Promise<{proc:ChildProcess;url:string;endpoint:string;status:string;error?:string}>((resolve,reject)=>{
  let out='',err='';const timer=setTimeout(()=>{p.kill('SIGTERM');reject(Error('START_TIMEOUT:'+err));},30000);
  p.stderr!.on('data',d=>err+=d);p.stdout!.on('data',d=>{out+=d;if(out.includes('\n')){clearTimeout(timer);resolve({proc:p,...JSON.parse(out.split('\n')[0])});}});
  p.once('exit',()=>{clearTimeout(timer);if(!out.includes('\n'))reject(Error('START_FAILED:'+err));});p.once('error',reject);
 });
}
async function post(s:{url:string;endpoint:string}, credential=token){
 for(let i=0;i<50;i++){
  const r=await fetch(s.url+s.endpoint,{method:'POST',headers:{Authorization:`Bearer ${credential}`,'Content-Type':'application/json'},body:JSON.stringify({facts:fixture.request.facts,expected_version:0})});
  if(r.status!==503)return r;await r.arrayBuffer();await delay(40);
 }throw Error('BUSY');
}
function snapshot(r:string){
 return JSON.parse(execFileSync('/usr/bin/python3',['-c',`import sqlite3,json,sys
with sqlite3.connect(sys.argv[1]) as db:
 print(json.dumps({'outbox':list(db.execute('SELECT status,attempts FROM outbox')), 'inbox':list(db.execute('SELECT operation,id FROM inbox')), 'states':list(db.execute('SELECT operation,version FROM state'))}))`,path.join(r,'target/state/runtime/function.sqlite')],{encoding:'utf8'}));
}
async function published(r:string){for(let i=0;i<100;i++){const s=snapshot(r);if(s.outbox[0]?.[0]==='published')return s;await delay(100);}throw Error('DELIVERY_TIMEOUT');}

test('compiler binds local delivery and bubblewrap while refusing public and unknown modes',async()=>{
 const text=readFileSync(source,'utf8');const c=await compileLocalHost(text);
 assert.equal(c.deployment.consumer.operation,'record-order');assert.equal(c.deployment.isolation,'bubblewrap');
 const plan=JSON.parse(readFileSync(path.join(bundle,'host-plan.json'),'utf8'));
 assert.equal(plan.local_delivery.enabled,true);assert.equal(plan.local_delivery.consumer,'record-order');assert.equal(plan.isolation,'bubblewrap');
 for(const bad of [text.replace('events local','events kafka'),text.replace('isolation bubblewrap','isolation automatic'),text.replace('listen loopback','listen public')])await assert.rejects(compileLocalHost(bad),/LOCAL_HOST/);
});

test('isolated producer delivers through outbox to consumer with one durable inbox receipt',async()=>{
 const r=root();const s=await start(r);assert.equal(s.status,'listening',s.error ?? 'HOST_NOT_LISTENING');
 const response=await post(s);assert.equal(response.status,200);assert.equal((await response.json()).status,'committed');
 const state=await published(r);assert.deepEqual(state.inbox,[['record-order','m1']]);
 assert.deepEqual(state.states.sort(),[['place-order',1],['record-order',1]]);
 assert.equal((await post(s)).status,200);assert.equal((await published(r)).inbox.length,1);await stop(s.proc);
});

test('consumer commit followed by host loss recovers without applying consumer twice',async()=>{
 const r=root();const s=await start(r,true);
 assert.equal((await post(s)).status,200);
 if(s.proc.exitCode===null)await once(s.proc,'exit');assert.equal(s.proc.exitCode,75);processes.delete(s.proc);
 assert.equal(snapshot(r).outbox[0][0],'leased');
 const resumed=await start(r);const state=await published(r);
 assert.equal(state.outbox[0][1],2);assert.deepEqual(state.inbox,[['record-order','m1']]);
 assert.deepEqual(state.states.sort(),[['place-order',1],['record-order',1]]);await stop(resumed.proc);
});

test('consumer and isolation permissions must be supplied by the operator before provisioning',async()=>{
 for(const grant of [{...policy,consumer:{}},{...policy,transport_grants:[]},{...policy,isolation:'trusted-process'},
   {...policy,transport_grants:'order-transport'},{...policy,consumer:{...policy.consumer,grants:'order-transaction-authority'}}]){
  const r=root();const s=await start(r,false,grant);assert.equal(s.status,'blocked');assert.ok(!existsSync(path.join(r,'history.sqlite')));await stop(s.proc);
 }
});

test('two host instances keep credentials and state separate',async()=>{
 const a=root(),b=root();const first=await start(a);const secondToken='second_fixture_token_'.repeat(3);const second=await start(b,false,policy,secondToken);
 assert.equal((await post(second)).status,401);assert.equal((await post(first)).status,200);
 await published(a);await stop(second.proc);
 const bState=snapshot(b);assert.equal(bState.inbox.length,0);assert.equal(bState.outbox.length,0);await stop(first.proc);
});

test('sandbox hides sibling data and host secrets and has no external network',()=>{
 const data=mkdtempSync(path.join(tmpdir(), 'alch-sandbox-data-'));const sibling=mkdtempSync(path.join(tmpdir(), 'alch-sandbox-other-'));
 try{
  writeFileSync(path.join(sibling,'secret'),'private');
  const code=`import importlib.util,subprocess,json,sys
spec=importlib.util.spec_from_file_location('worker',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
probe="import os,socket,json; s=socket.socket(); s.settimeout(.2); print(json.dumps({'sibling':os.path.exists("+repr(sys.argv[3])+"),'secret':os.getenv('HOST_SECRET'),'network':s.connect_ex(('198.51.100.1',80)),'writable':os.access('/data',os.W_OK)}))"
p=subprocess.run(m.sandbox_command('/usr/bin/python3',sys.argv[2]),input=probe,text=True,capture_output=True,check=True);print(p.stdout)`;
  const value=JSON.parse(execFileSync('/usr/bin/python3',['-c',code,path.join(bundle,'local_worker.py'),data,path.join(sibling,'secret')],{encoding:'utf8',env:{...process.env,HOST_SECRET:'must-not-enter-sandbox',PYTHONDONTWRITEBYTECODE:'1'}}));
  assert.equal(value.sibling,false);assert.equal(value.secret,null);assert.notEqual(value.network,0);assert.equal(value.writable,true);
 }finally{rmSync(data,{recursive:true,force:true});rmSync(sibling,{recursive:true,force:true});}
});

test('unavailable isolation rejects startup without falling back or provisioning',()=>{
 const r=root();
 const code=`import sys
sys.path.insert(0,sys.argv[1]);import serve
serve.local_worker.sandbox_command=lambda *_: ['/nonexistent-alch-sandbox']
try: serve.run(sys.argv[2],0)
except ValueError as e: print(str(e))`;
 const out=execFileSync('/usr/bin/python3',['-c',code,bundle,r],{encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1',ALCH_HOST_TOKEN:token,ALCH_HOST_POLICY:JSON.stringify(policy)}});
 assert.equal(out.trim(),'ISOLATION_UNAVAILABLE');assert.ok(!existsSync(path.join(r,'history.sqlite')));
});

test('consumer rejection exhausts the declared retries into a dead outbox row',async()=>{
 const badSource=path.join(temp,'rejected-consumer.alch');const badBundle=path.join(temp,'rejected-bundle');
 writeFileSync(badSource,readFileSync(source,'utf8').replace('field status default string "pending"','field status default string "committed"').replace('max-attempts 5','max-attempts 2'));
 await buildLocalHost(badSource,badBundle);
 const r=root();const s=await start(r,false,policy,token,badBundle);assert.equal((await post(s)).status,200);
 let state;for(let i=0;i<100;i++){state=snapshot(r);if(state.outbox[0]?.[0]==='dead')break;await delay(100);}
 assert.deepEqual(state.outbox,[['dead',2]]);assert.deepEqual(state.inbox,[]);assert.deepEqual(state.states,[['place-order',1]]);
 await stop(s.proc);
});
