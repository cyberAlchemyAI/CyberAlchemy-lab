import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawnSync,spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {buildEventExecution,compileEventExecution} from '../src/event-execution.js';
const sourcePath=fileURLToPath(new URL('../../extensions/event-execution-v1/order-events.alch',import.meta.url));
const source=readFileSync(sourcePath,'utf8');
const work=mkdtempSync(path.join(tmpdir(),'event-execution-test-'));const bundle=path.join(work,'bundle');
const ready=buildEventExecution(sourcePath,bundle);
const context={actor:'OrderService',grants:['order-transaction-authority'],transport_grants:['order-transport']};
const base=Date.parse('2026-09-06T12:00:00.000Z');
const time=(delta=0)=>({now:base+delta,at:new Date(base+delta).toISOString()});
const facts={operationId:'op1',orderId:'o1',status:'pending',outboxMessageId:'m1',occurredAt:time().at,payload:{quantity:2}};
const invoke={command:'invoke',operation:'place-order',facts,expected_version:0,...time()};
type Target='node'|'rust';
function command(target:Target){return target==='node'?{bin:process.execPath,args:[path.join(bundle,'handler.mjs')]}:{bin:path.join(bundle,'alch-event'),args:[]}}
function run(target:Target,db:string,request:any,ctx:any=context,failpoint?:string){const {bin,args}=command(target);const p=spawnSync(bin,args,{input:JSON.stringify({request,context:ctx}),encoding:'utf8',env:{...process.env,ALCH_EVENT_DATABASE:db,...(failpoint?{ALCH_EVENT_TEST_FAILPOINT:failpoint}:{})}});assert(p.status===0||p.status===1,`${target}: ${p.error??p.stderr}`);try{return JSON.parse(p.stdout)}catch{assert.fail(`${target} non-JSON: ${p.stdout} ${p.stderr}`)}}
function db(name:string){return path.join(work,`${name}.sqlite`)}
function inspect(target:Target,database:string){return run(target,database,{command:'inspect'})}
function scenario(name:string,body:(target:Target,database:string)=>unknown){test(name,async()=>{await ready;const node=await body('node',db(name+'-node'));const rust=await body('rust',db(name+'-rust'));assert.deepEqual(rust,node)})}

test('execution compiler rejects unbound roles, partial mappings, payload mismatch and unsupported SFOL',async()=>{
 for(const [a,b] of [
 ['  timestamp occurredAt','  timestamp orderId'],
 ['  key orderId','  key undeclared'],['  state OrderState','  state Unknown'],['  kind producer','  kind consumer'],['  total true','  total false'],['  field status default string "pending"','  field status default string "pending"\n  field status default string "pending"'],['  status == "pending"','  status contains "pending"'],['  payload OrderPayload','  payload OrderState\n  payload OrderPayload'],
 ])await assert.rejects(()=>compileEventExecution(source.replace(a,b)));
});

scenario('generated handlers enforce actor grants rules and input types before effects',(t,d)=>{
 assert.deepEqual(run(t,d,{command:'inspect'},{actor:context.actor,grants:context.grants}),{error:'TRANSPORT_DENIED'});
 assert.deepEqual(run(t,d,invoke,{actor:'Other',grants:context.grants}),{error:'ACTOR_DENIED'});
 assert.deepEqual(run(t,d,invoke,{actor:context.actor,grants:[]}),{error:'AUTHORITY_DENIED'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...facts,status:'cancelled'}}),{error:'RULE_DENIED'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...facts,orderId:99}}),{error:'FACTS'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...facts,unexpected:'x'}}),{error:'FACTS'});
 const snapshot=inspect(t,d);assert.equal(snapshot.states.length,0);assert.equal(snapshot.outbox.length,0);return snapshot;
});

scenario('producer restart replay and message identity conflict are durable',(t,d)=>{
 assert.deepEqual(run(t,d,invoke),{status:'committed',message_id:'m1'});
 assert.deepEqual(run(t,d,invoke),{status:'already-committed',message_id:'m1'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...facts,payload:{quantity:3}}}),{error:'MESSAGE_ID_CONFLICT'});
 const snap=inspect(t,d);assert.equal(snap.states[0].state.status,'committed');assert.equal(snap.outbox[0].body.payload.status,'pending');assert.equal(snap.outbox.length,1);assert.equal(snap.observations.length,1);return snap;
});

scenario('producer transaction failpoint rolls back state outbox and observations',(t,d)=>{
 assert.deepEqual(run(t,d,invoke,context,'after-state'),{error:'FAILPOINT'});const snap=inspect(t,d);assert.equal(snap.states.length,0);assert.equal(snap.outbox.length,0);assert.equal(snap.observations.length,0);return snap;
});

scenario('consumer restart duplicates and failed transaction preserve atomic inbox state',(t,d)=>{
 run(t,d,invoke);const m=inspect(t,d).outbox[0].body;const req={command:'invoke',operation:'record-order',message:m,...time()};
 assert.deepEqual(run(t,d,req,context,'after-state'),{error:'FAILPOINT'});assert.equal(inspect(t,d).inbox.length,0);assert.equal(inspect(t,d).states.length,1);
 assert.equal(inspect(t,d).observations.filter((o:any)=>o.attributes.stage==='consumer-failed').length,1);
 assert(!inspect(t,d).observations.some((o:any)=>o.attributes.stage==='consumer-committed'));
 assert.deepEqual(run(t,d,req),{status:'processed',message_id:'m1'});assert.deepEqual(run(t,d,req),{status:'duplicate',message_id:'m1'});
 assert.deepEqual(run(t,d,{...req,message:{...m,payload:{...m.payload,payload:{quantity:9}}}}),{error:'MESSAGE_ID_CONFLICT'});
 const snap=inspect(t,d);assert.equal(snap.inbox.length,1);assert.equal(snap.states.find((s:any)=>s.operation==='record-order').version,1);return snap;
});

scenario('lease expiry rejects stale acceptance and provider acceptance does not commit consumer',(t,d)=>{
 run(t,d,invoke);assert.equal(run(t,d,{command:'claim',worker:'w1',...time()}).attempt,1);
 assert.deepEqual(run(t,d,{command:'claim',worker:'w2',...time(1)}),{status:'empty'});
 assert.equal(run(t,d,{command:'claim',worker:'w2',...time(60001)}).attempt,2);
 assert.deepEqual(run(t,d,{command:'settle',worker:'w1',message_id:'m1',attempt:1,outcome:'provider-accepted',...time(60002)}),{error:'LEASE'});
 assert.deepEqual(run(t,d,{command:'settle',worker:'w2',message_id:'m1',attempt:2,outcome:'provider-accepted',...time(60002)}),{status:'published',message_id:'m1'});
 const snap=inspect(t,d);assert.equal(snap.inbox.length,0);assert(!snap.observations.some((o:any)=>o.attributes.stage==='consumer-committed'));return snap;
});

scenario('unknown outcomes obey retry schedule and terminate at declared maximum',(t,d)=>{
 run(t,d,invoke);for(let i=0;i<5;i++){
 const offset=i*60000;const claim=run(t,d,{command:'claim',worker:'w',...time(offset)});assert.equal(claim.attempt,i+1);
 const result=run(t,d,{command:'settle',worker:'w',message_id:'m1',attempt:i+1,outcome:'unknown',...time(offset+1)});assert.equal(result.status,i===4?'dead':'pending');
 assert.deepEqual(run(t,d,{command:'claim',worker:'w',...time(offset+2)}),{status:'empty'});
 }const snap=inspect(t,d);assert.equal(snap.outbox[0].attempts,5);assert.equal(snap.outbox[0].status,'dead');return snap;
});

test('Node producer and Rust consumer share durable storage across restarts',async()=>{
 await ready;const d=db('cross');run('node',d,invoke);const claim=run('rust',d,{command:'claim',worker:'w',...time()});
 const consume={command:'invoke',operation:'record-order',message:claim.message,...time()};
 assert.equal(run('rust',d,consume).status,'processed');assert.equal(run('node',d,consume).status,'duplicate');
 assert.deepEqual(inspect('node',d),inspect('rust',d));
});

test('concurrent Node and Rust producers serialize one optimistic-version winner',async()=>{
 await ready;const d=db('concurrent');inspect('node',d);
 const asyncRun=(target:Target,request:any)=>new Promise<any>((resolve,reject)=>{const cmd=command(target);const p=spawn(cmd.bin,cmd.args,{env:{...process.env,ALCH_EVENT_DATABASE:d},stdio:['pipe','pipe','pipe']});let out='';let err='';p.stdout.on('data',x=>out+=x);p.stderr.on('data',x=>err+=x);p.on('error',reject);p.on('close',()=>{try{resolve(JSON.parse(out))}catch{reject(Error(err))}});p.stdin.end(JSON.stringify({request,context}))});
 const outcomes=await Promise.all([asyncRun('node',invoke),asyncRun('rust',{...invoke,facts:{...facts,outboxMessageId:'m2'}})]);
 assert.equal(outcomes.filter(x=>x.status==='committed').length,1);assert.equal(outcomes.filter(x=>x.error==='VERSION_CONFLICT').length,1);assert.equal(inspect('node',d).outbox.length,1);
});

scenario('portable numeric boundary rejects lossy nested record values',(t,d)=>{
 assert.deepEqual(run(t,d,{...invoke,facts:{...facts,payload:{fraction:0.5}}}),{error:'NUMBER_RANGE'});
 assert.deepEqual(run(t,d,{...invoke,facts:{...facts,payload:{unsafe:9007199254740992}}}),{error:'NUMBER_RANGE'});
 return inspect(t,d);
});

test.after(async()=>{await ready;rmSync(work,{recursive:true,force:true})});
