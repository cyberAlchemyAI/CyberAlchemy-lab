import test from 'node:test';
import assert from 'node:assert/strict';
import {createMemoryRequestCustody} from '../../src/runtime/request-custody.js';
import {compileRequestCustody} from '../../src/typed-backend/request-custody.js';
const decisions={execute:'execute',replay:'replay',reject:{conflict:'IDEMPOTENCY_CONFLICT',in_progress:'REQUEST_IN_PROGRESS',stream_not_replayable:'STREAM_NOT_REPLAYABLE',previous_failure:'PREVIOUS_REQUEST_FAILED'}};
const policy=async(i:any)=>({status:!i.exists?'execute':!i.matches?'conflict':i.pending?'in_progress':i.stream?'stream_not_replayable':i.succeeded?'replay':'previous_failure'});
const control=()=>({signal:new AbortController().signal,deadline:Infinity});
const req=(id='r1',key:string|null='key')=>({scope:'tenant',key,requestId:id,fingerprintVersion:'v1',fingerprint:'digest',stream:false});
const binding={id:'a',version:'v1',model:'model',policyVersion:'balanced'};
const make=(options:any={})=>createMemoryRequestCustody({policy,decisions,...options});
const reserve=async(s:any,r=req())=>{const v=await s.reserve(r,control());assert.equal(v.kind,'execute');return v.token;};
test('atomic duplicates and conflicts; tenant scope and no-key independence',async()=>{
 const s=make();const [a,b]=await Promise.all([s.reserve(req(),control()),s.reserve(req('r2'),control())]);assert.equal(a.kind,'execute');assert.deepEqual(b,{kind:'reject',code:'REQUEST_IN_PROGRESS',requestId:'r1'});
 assert.equal((await s.reserve({...req('r3'),fingerprint:'other'},control()) as any).code,'IDEMPOTENCY_CONFLICT');
 await reserve(s,{...req('r4'),scope:'other'});await reserve(s,req('r5',null));await reserve(s,req('r6',null));assert.equal(s.inspectAll().length,4);
});
test('opaque tokens reject forgery, cross-store use, reuse and attempts after outcome',async()=>{
 const s=make(),token=await reserve(s);await assert.rejects(s.beginAttempt('r1' as any,binding),/INVALID_EXECUTION_TOKEN/);await assert.rejects(make().beginAttempt(token,binding),/INVALID_EXECUTION_TOKEN/);await assert.rejects(s.beginAttempt(token,{...binding,model:'x'.repeat(129)}),/INVALID_ATTEMPT/);
 await s.beginAttempt(token,binding);await assert.rejects(s.beginAttempt(token,binding),/ATTEMPT_NOT_ALLOWED/);await s.recordOutcome(token,{kind:'failed',code:'FAILED'});await assert.rejects(s.recordOutcome(token,{kind:'failed',code:'OTHER'}),/OUTCOME_ALREADY_RECORDED/);await assert.rejects(s.beginAttempt(token,binding),/ATTEMPT_NOT_ALLOWED/);
});
test('expiry starts only after outcome AND settlement, in either order',async()=>{
 for(const settlementFirst of [true,false]){let now=0;const s=make({clock:()=>now,retentionMs:10,maxEntries:1}),token=await reserve(s);await s.beginAttempt(token,binding);
 if(settlementFirst)await s.markTransportSettled(token);else await s.recordOutcome(token,{kind:'failed',code:'DEADLINE_EXCEEDED'});
 now=1000;assert.equal((await s.reserve(req('r2'),control()) as any).code,'REQUEST_IN_PROGRESS');assert.equal((await s.reserve(req('r3','other'),control()) as any).code,'REQUEST_STORE_FULL');
 if(settlementFirst)await s.recordOutcome(token,{kind:'failed',code:'DEADLINE_EXCEEDED'});else await s.markTransportSettled(token);
 assert.equal((await s.inspect('r1'))?.remoteCompletion,'unknown');now=1009;assert.equal(s.inspectAll().length,1);now=1010;assert.equal(s.inspectAll().length,0);await assert.rejects(s.beginAttempt(token,binding),/INVALID_EXECUTION_TOKEN/);await reserve(s,req('r2'));
 }
});
test('replay is a deep copy and metadata excludes result/fingerprint/extra binding data',async()=>{
 const s=make(),token=await reserve(s);await s.beginAttempt(token,{...binding,secret:'hidden'} as any);const result={text:'private result'};await s.recordOutcome(token,{kind:'json-completed',result,usage:null});result.text='mutated';await s.markTransportSettled(token);
 const a:any=await s.reserve(req('r2'),control());assert.equal(a.result.text,'private result');a.result.text='mutated';assert.equal((await s.reserve(req('r3'),control()) as any).result.text,'private result');assert.ok(!/private|hidden|digest/.test(JSON.stringify(await s.inspect('r1'))));
});
test('stream success cannot replay; settlement never proves remote completion',async()=>{
 const s=make(),token=await reserve(s,{...req(),stream:true});await s.beginAttempt(token,binding);await s.markTransportSettled(token);assert.equal((await s.inspect('r1'))?.remoteCompletion,'unknown');await s.recordOutcome(token,{kind:'stream-completed',usage:null});assert.equal((await s.reserve({...req('r2'),stream:true},control()) as any).code,'STREAM_NOT_REPLAYABLE');
});
test('cancelled policy work stays queue-bounded and cannot leave an orphan reservation',async()=>{
 let release!:()=>void,entered!:()=>void;const started=new Promise<void>(r=>entered=r);const s=make({maxEntries:1,policy:async(i:any)=>{entered();await new Promise<void>(r=>release=r);return policy(i);}});const c=new AbortController();const pending=s.reserve(req(),{signal:c.signal,deadline:Infinity});await started;c.abort();await assert.rejects(pending,/CANCELLED/);assert.equal((await s.reserve(req('r2'),control()) as any).code,'REQUEST_STORE_BUSY');release();await new Promise(r=>setImmediate(r));assert.equal(s.inspectAll().length,0);
});
test('deadline after delayed policy rejects before reservation; invalid policy cannot overwrite existing',async()=>{
 let now=0;const s=make({clock:()=>now,policy:async(i:any)=>{now=10;return policy(i);}});await assert.rejects(s.reserve(req(),{signal:new AbortController().signal,deadline:5}),/DEADLINE_EXCEEDED/);assert.equal(s.inspectAll().length,0);
 const broken=make({policy:async()=>({status:'execute'})});await reserve(broken);await assert.rejects(broken.reserve(req('r2'),control()),/INVALID_IDEMPOTENCY_DECISION/);assert.equal(broken.inspectAll().length,1);
});
const contract=()=>({schema_version:'domainspec.request-custody/v1-candidate',limits:{retention_ms:60000,max_entries:128,max_bytes:65536,reservation_ms:5000},identity:{version:'v1',request:'request',payload:'messages',scope:'tenant_id',request_id:'request_id',stream:'stream',defaults:{stream:false},exclude:['request_id']},decisions,lifecycle:{attempts:1,outcome:'write-once',expiry:'outcome-and-transport-settled',backend:'bounded-memory'},module:{input:{type:Object.fromEntries(['exists','matches','pending','stream','succeeded'].map(k=>[k,{type:'boolean'}]))},output:{type:{status:{type:'string'}}}}});
test('normalized contract rejects unsupported lifecycle, unsafe identity and incompatible policy',()=>{
 assert.equal(compileRequestCustody(contract()).contract.lifecycle.attempts,1);
 for(const mutate of [(c:any)=>c.lifecycle.attempts=2,(c:any)=>c.lifecycle.expiry='deadline',(c:any)=>c.identity.exclude.push('routing_strategy'),(c:any)=>c.identity.defaults.__proto__=true,(c:any)=>c.module.input.type.pending.type='string',(c:any)=>c.limits.max_bytes=65537,(c:any)=>c.extra=true]){const c:any=contract();mutate(c);if(mutate.toString().includes('__proto__'))Object.defineProperty(c.identity.defaults,'__proto__',{value:true,enumerable:true});assert.throws(()=>compileRequestCustody(c),/REQUEST_CUSTODY/);}
});
