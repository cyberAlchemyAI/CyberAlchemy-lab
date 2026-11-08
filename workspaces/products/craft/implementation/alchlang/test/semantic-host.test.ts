import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawnSync,spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {buildSemanticHost,compileSemanticHost} from '../src/semantic-host.js';
const sourcePath=fileURLToPath(new URL('../../extensions/semantic-corrections-v1/orders.alch',import.meta.url));
const historicalArtifactPath=new URL('../../extensions/semantic-corrections-v1/runtime-artifacts.json',import.meta.url);
const historicalArtifactBytes=readFileSync(historicalArtifactPath);
const source=readFileSync(sourcePath,'utf8'),work=mkdtempSync(path.join(tmpdir(),'semantic-tests-')),bundle=path.join(work,'bundle');
const context={actor:'OrderService',grants:['order-transaction-authority'],transport_grants:['orders-local']};
const base=Date.parse('2026-09-06T12:00:00.000Z'),time=(delta=0)=>({now:base+delta,at:new Date(base+delta).toISOString()});
const invoke={command:'invoke',operation:'place-order',facts:{orderId:'o1',payload:{quantity:2}},message_id:'m1',expected_version:0,...time()};
type Target='node'|'rust';
const ready=buildSemanticHost(sourcePath,bundle);
function command(target:Target,root=bundle){return target==='node'?{bin:process.execPath,args:[path.join(root,'handler.mjs')]}:{bin:path.join(root,'alch-event'),args:[]};}
function run(target:Target,database:string,request:any,ctx:any=context,failpoint?:string,root=bundle){const {bin,args}=command(target,root);const p=spawnSync(bin,args,{input:JSON.stringify({request,context:ctx}),encoding:'utf8',env:{...process.env,ALCH_EVENT_DATABASE:database,...(failpoint?{ALCH_EVENT_TEST_FAILPOINT:failpoint}:{})}});assert(p.status===0||p.status===1,`${target}: ${p.error??p.stderr}`);try{return JSON.parse(p.stdout)}catch{assert.fail(`${target} non-JSON: ${p.stdout} ${p.stderr}`)}}
const inspect=(t:Target,d:string)=>run(t,d,{command:'inspect'});
function scenario(name:string,body:(t:Target,d:string)=>unknown){test(name,async()=>{await ready;const node=await body('node',path.join(work,name+'-node.sqlite'));const rust=await body('rust',path.join(work,name+'-rust.sqlite'));assert.deepEqual(rust,node);});}

test('F2 F5 F6 F7 F8 typed input state payload projection and imported ontology closure',async()=>{
 const p=await compileSemanticHost(source);assert.equal(p.config.executions[0].input,'PlaceOrder');assert.equal(p.config.executions[0].storage,'entity:Order');assert.equal(p.config.executions[1].storage,'projection:RecordedOrder');
 assert.deepEqual(p.ontology.records.PlaceOrder.properties.map(p=>p.id),['orderId','payload','note']);
 for(const kind of ['actor','boundary','effect','permission','Mapping','transition','system','event','projection','command','binding'])assert(p.ontology.nodes.some(n=>n.kind===kind),kind);
 assert(p.generated.every(g=>g.source.includes('domainspec.declarative-function/v1')));
 await assert.rejects(()=>compileSemanticHost(source+'\nentity OutboxMessage:\n  fake: string required\n'),/collision/);
 await assert.rejects(()=>compileSemanticHost(source.replace('binding sqlite-event-store-v2','binding sqlite-transactional-outbox')),/binding/);
 await assert.rejects(()=>compileSemanticHost(source.replace('actor OrderService','')),/actor/);
 const explicit=source.replace('event OrderPlaced:\n  from Order','event OrderPlaced:\n  orderId: identifier required\n  status: string required\n  payload: record required\n  note: string required').replace('projection RecordedOrder:\n  from OrderPlaced','projection RecordedOrder:\n  orderId: identifier required\n  status: string required\n  payload: record required\n  note: string required');
 const q=await compileSemanticHost(explicit);assert.deepEqual({...q.config,binding_digest:''},{...p.config,binding_digest:''});
});

test('F3 unsupported declarations reject rather than disappear',async()=>{
 for(const change of ['  ordering fifo','  backoff none','  retention-seconds 0','  max-receives 0','  unexpected silently'])await assert.rejects(()=>compileSemanticHost(source+'\n'+change));
 await assert.rejects(()=>compileSemanticHost(source.replace('  input PlaceOrder','  input Order')),/command/);
 await assert.rejects(()=>compileSemanticHost(source.replace('  transition status pending -> committed','  transition payload pending -> committed')),/transition/);
});

scenario('F1 state transition durable replay and conflict',(t,d)=>{
 assert.deepEqual(run(t,d,invoke),{status:'committed',message_id:'m1'});
 assert.deepEqual(run(t,d,invoke),{status:'already-committed',message_id:'m1'});
 assert.deepEqual(run(t,d,{...invoke,message_id:'m2',expected_version:1}),{error:'TRANSITION_DENIED'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...invoke.facts,status:'pending'},message_id:'m2',expected_version:1}),{error:'FACTS'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...invoke.facts,payload:{quantity:3}}}),{error:'MESSAGE_ID_CONFLICT'});
 const snap=inspect(t,d);assert.equal(snap.states[0].state.status,'committed');assert.equal(snap.outbox[0].body.payload.status,'committed');return snap;
});
scenario('F2 F4 independent input and fallback default',(t,d)=>{
 for(const note of [null,2,false])assert.deepEqual(run(t,d,{...invoke,facts:{...invoke.facts,note}}),{error:'FACTS'});
 for(const [id,note] of [['m1','provided'],['m2','']])assert.equal(run(t,d,{...invoke,message_id:id,facts:{orderId:id,payload:{opaque:{untouched:true}},note}}).status,'committed');
 assert.equal(run(t,d,{...invoke,message_id:'m3',facts:{orderId:'m3',payload:{}}}).status,'committed');
 const snap=inspect(t,d);assert.deepEqual(snap.states.map((s:any)=>s.state.note),['provided','','']);return snap;
});
scenario('authority and invalid facts have no business effects',(t,d)=>{
 assert.deepEqual(run(t,d,invoke,{...context,actor:'Other'}),{error:'ACTOR_DENIED'});
 assert.deepEqual(run(t,d,invoke,{...context,grants:[]}),{error:'AUTHORITY_DENIED'});
 assert.deepEqual(run(t,d,{command:'inspect'},{...context,transport_grants:[]}),{error:'TRANSPORT_DENIED'});
 for(const facts of [{orderId:'o1'},{...invoke.facts,unknown:true},{...invoke.facts,orderId:3},{...invoke.facts,payload:null}])assert.deepEqual(run(t,d,{...invoke,facts}),{error:'FACTS'});
 assert.equal(inspect(t,d).states.length,0);return inspect(t,d);
});
scenario('producer rollback leaves no state outbox or delivery history',(t,d)=>{
 assert.deepEqual(run(t,d,invoke,context,'after-state'),{error:'FAILPOINT'});const snap=inspect(t,d);assert.equal(snap.states.length,0);assert.equal(snap.outbox.length,0);assert.equal(snap.delivery.length,0);return snap;
});
scenario('F3 receive limit differs from transport limit and reaches named dead letter',(t,d)=>{
 run(t,d,invoke);const claim=run(t,d,{command:'claim',worker:'w',...time()});
 const request={command:'invoke',operation:'record-order',message:claim.message,...time()};
 assert.deepEqual(run(t,d,request,context,'after-state'),{error:'FAILPOINT'});
 assert.equal(inspect(t,d).delivery[0].receives,1);assert.equal(inspect(t,d).inbox.length,0);
 assert.deepEqual(run(t,d,request),{error:'RECEIVE_LIMIT'});
 assert.equal(run(t,d,{command:'claim',worker:'w2',...time(30000)}).status,'dead');
 const snap=inspect(t,d);assert.equal(snap.outbox[0].attempts,1);assert.equal(snap.dead_letters[0].channel,'orders-dead-letter');assert.equal(snap.dead_letters[0].reason,'receives');return snap;
});
scenario('F3 retention ends delivery without deleting replay receipts',(t,d)=>{
 run(t,d,invoke);assert.equal(run(t,d,{command:'claim',worker:'w',...time(345600000)}).status,'dead');
 assert.deepEqual(run(t,d,invoke),{status:'already-committed',message_id:'m1'});
 const snap=inspect(t,d);assert.equal(snap.dead_letters[0].reason,'retention');assert.equal(snap.outbox.length,1);return snap;
});
scenario('F6 consumer projection atomic duplicate and restart',(t,d)=>{
 run(t,d,invoke);const m=inspect(t,d).outbox[0].body;const r={command:'invoke',operation:'record-order',message:m,...time()};
 assert.deepEqual(run(t,d,r),{status:'processed',message_id:'m1'});assert.deepEqual(run(t,d,r),{status:'duplicate',message_id:'m1'});
 assert.deepEqual(run(t,d,{...r,message:{...m,payload:{...m.payload,note:'changed'}}}),{error:'MESSAGE_ID_CONFLICT'});
 const snap=inspect(t,d);assert.deepEqual(snap.states.map((x:any)=>x.operation),['entity:Order','projection:RecordedOrder']);assert.equal(snap.delivery[0].receives,1);return snap;
});
scenario('lease fencing retry backoff and transport terminal copy',(t,d)=>{
 run(t,d,invoke);for(let attempt=1;attempt<=5;attempt++){
 const delta=(attempt-1)*60000;assert.equal(run(t,d,{command:'claim',worker:'w',...time(delta)}).attempt,attempt);
 assert.deepEqual(run(t,d,{command:'settle',worker:'stale',message_id:'m1',attempt,outcome:'provider-accepted',...time(delta+1)}),{error:'LEASE'});
 assert.equal(run(t,d,{command:'settle',worker:'w',message_id:'m1',attempt,outcome:'unknown',...time(delta+1)}).status,attempt===5?'dead':'pending');
 assert.equal(run(t,d,{command:'claim',worker:'w',...time(delta+2)}).status,'empty');
 }const snap=inspect(t,d);assert.equal(snap.dead_letters[0].reason,'attempts');assert.equal(snap.delivery[0].receives,0);return snap;
});

test('changing transition destination changes actual Node and Rust state',async()=>{
 await ready;const input=path.join(work,'cancelled.alch'),out=path.join(work,'cancelled');writeFileSync(input,source.replace('pending -> committed','pending -> cancelled'));await buildSemanticHost(input,out);
 for(const t of ['node','rust'] as const){const d=path.join(work,'cancelled-'+t+'.sqlite');assert.equal(run(t,d,invoke,context,undefined,out).status,'committed');assert.equal(run(t,d,{command:'inspect'},context,undefined,out).states[0].state.status,'cancelled');}
});
test('Node and Rust concurrent producers serialize one winner',async()=>{
 await ready;const d=path.join(work,'concurrent.sqlite');inspect('node',d);
 const asyncRun=(t:Target,r:any)=>new Promise<any>((resolve,reject)=>{const {bin,args}=command(t),p=spawn(bin,args,{env:{...process.env,ALCH_EVENT_DATABASE:d},stdio:['pipe','pipe','pipe']});let out='';p.stdout.on('data',x=>out+=x);p.on('error',reject);p.on('close',()=>{try{resolve(JSON.parse(out))}catch(e){reject(e)}});p.stdin.end(JSON.stringify({request:r,context}));});
 const result=await Promise.all([asyncRun('node',invoke),asyncRun('rust',{...invoke,message_id:'m2'})]);assert.equal(result.filter(r=>r.status==='committed').length,1);assert.equal(result.filter(r=>r.error==='VERSION_CONFLICT').length,1);
});
test('cross runtime local delivery survives lost acknowledgement',async()=>{
 await ready;const d=path.join(work,'cross.sqlite');assert.equal(run('node',d,invoke).status,'committed');const claim=run('rust',d,{command:'claim',worker:'w',...time()});
 const request={command:'invoke',operation:'record-order',message:claim.message,...time()};assert.equal(run('rust',d,request).status,'processed');
 const next=run('node',d,{command:'claim',worker:'w2',...time(30000)});assert.equal(next.status,'leased');assert.equal(run('node',d,{...request,...time(30001)}).status,'duplicate');
 assert.equal(run('rust',d,{command:'settle',worker:'w2',message_id:'m1',attempt:2,outcome:'provider-accepted',...time(30002)}).status,'published');assert.deepEqual(inspect('node',d),inspect('rust',d));
});
test('fallback distinguishes missing false zero null and explicit assignment',async()=>{
 await ready;const input=path.join(work,'values.alch'),out=path.join(work,'values');
 writeFileSync(input,source.replace('  note: string required default ""','  note: string required default ""\n  flag: boolean required default true\n  count: integer required default 9').replace('  note: string optional','  note: string optional\n  flag: boolean optional\n  count: integer optional').replace('  input PlaceOrder','  input PlaceOrder\n  assign note "assigned"'));await buildSemanticHost(input,out);
 for(const t of ['node','rust'] as const){const d=path.join(work,'values-'+t+'.sqlite');
  assert.equal(run(t,d,{...invoke,facts:{...invoke.facts,flag:false,count:0,note:'supplied'}},context,undefined,out).status,'committed');
  let state=run(t,d,{command:'inspect'},context,undefined,out).states[0].state;assert.equal(state.flag,false);assert.equal(state.count,0);assert.equal(state.note,'assigned');
  assert.deepEqual(run(t,d,{...invoke,message_id:'m2',facts:{orderId:'o2',payload:{},flag:null}},context,undefined,out),{error:'FACTS'});
  assert.equal(run(t,d,{...invoke,message_id:'m2',facts:{orderId:'o2',payload:{}}},context,undefined,out).status,'committed');
  state=run(t,d,{command:'inspect'},context,undefined,out).states[1].state;assert.equal(state.flag,true);assert.equal(state.count,9);
 }
});
scenario('process crash cannot reset the durable receive budget',(t,d)=>{
 run(t,d,invoke);const message=inspect(t,d).outbox[0].body;const {bin,args}=command(t);
 const p=spawnSync(bin,args,{input:JSON.stringify({request:{command:'invoke',operation:'record-order',message,...time()},context}),encoding:'utf8',env:{...process.env,ALCH_EVENT_DATABASE:d,ALCH_EVENT_TEST_FAILPOINT:'after-receive'}});
 assert.equal(p.status,75);const snap=inspect(t,d);assert.equal(snap.delivery[0].receives,1);assert.equal(snap.inbox.length,0);assert.equal(snap.states.length,1);
 assert.deepEqual(run(t,d,{command:'invoke',operation:'record-order',message,...time()}),{error:'RECEIVE_LIMIT'});return snap;
});
test('ordinary semantic runtime tests preserve historical artifact bytes',async()=>{
 await ready;assert.deepEqual(readFileSync(historicalArtifactPath),historicalArtifactBytes);
});
test.after(async()=>{
 try{
  await ready;
  const report={status:'built-test-fixtures',artifacts:['bundle','cancelled','values'].map(name=>({name,manifest:JSON.parse(readFileSync(path.join(work,name,'manifest.json'),'utf8'))})),authority_effect:'none'};
  const reportPath=path.join(work,'runtime-artifacts.json');
  writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
  assert.deepEqual(JSON.parse(readFileSync(reportPath,'utf8')),report);
  assert.deepEqual(readFileSync(historicalArtifactPath),historicalArtifactBytes,'semantic tests must not reissue historical artifact evidence');
 }finally{rmSync(work,{recursive:true,force:true});}
});
