import test from 'node:test';import assert from 'node:assert/strict';
import {createObservationSink,evaluateQuality,observeTransition} from './index.mjs';
const runtime=(tenant='tenantA')=>({inspect:()=>({runtime_id:'runtime:'+tenant,tenant,application:'Example',resource_id:'selected-1',mode:'fixture'}),assertCurrent(){}});
test('closed actual-runtime observations redact tenant/correlation and never accept payload or mode labels',()=>{
 const sink=createObservationSink(),emitter=sink.bindRuntime(runtime());
 assert.throws(()=>emitter.emit({category:'model',transition:'returned',correlation_id:'secret',prompt:'raw'}));assert.throws(()=>emitter.emit({category:'model',transition:'returned',correlation_id:'secret',mode:'provider'}));
 emitter.emit({category:'model',transition:'returned',correlation_id:'secret',usage:{kind:'observed',input_units:12,output_units:3}});const result=sink.drain();assert.equal(result.length,1);assert.equal(result[0].runtime.mode,'fixture');assert.doesNotMatch(JSON.stringify(result),/tenantA|secret|prompt|token/);
 assert.throws(()=>emitter.emit({category:'provider',transition:'unknown',correlation_id:'a',code:'secretPassword'}));assert.throws(()=>emitter.emit({category:'model',transition:'returned',correlation_id:'a',usage:{kind:'unknown',input_units:0}}));
});
test('runtime identity drift refuses events and separate tenant emitters cannot label another tenant',()=>{
 const sink=createObservationSink(),a=runtime(),b=runtime('tenantB'),ea=sink.bindRuntime(a),eb=sink.bindRuntime(b);ea.emit({category:'access',transition:'authorized',correlation_id:'a'});eb.emit({category:'access',transition:'denied',correlation_id:'b'});const rows=sink.drain();assert.notEqual(rows[0].runtime.tenant_sha256,rows[1].runtime.tenant_sha256);
 a.inspect=()=>({...runtime().inspect(),mode:'provider'});assert.throws(()=>ea.emit({category:'work',transition:'returned',correlation_id:'a'}),{code:'StaleOwner'});
});
test('bounded overflow/retention and optional sink outage preserve actual operation outcome',async()=>{
 let now=100;const sink=createObservationSink({now:()=>now,bounds:{capacity:1,retentionMs:10}}),e=sink.bindRuntime(runtime());const record={category:'provider',transition:'dispatched',correlation_id:'x'};assert.equal(e.emit(record).accepted,true);assert.equal(e.emit(record).accepted,false);assert.equal(sink.inspect().dropped,1);now=111;assert.equal(sink.drain().length,0);assert.equal(sink.inspect().dropped,2);
 const original=new Error('private prompt error');sink.close();assert.equal(await observeTransition(e,{category:'provider',correlation_id:'x'},async()=>23),23);await assert.rejects(observeTransition(e,{category:'provider',correlation_id:'x'},async()=>{throw original;}),error=>error===original);
});
test('execution helper actually emits success/failure and error messages stay out of events',async()=>{
 const sink=createObservationSink(),e=sink.bindRuntime(runtime());await observeTransition(e,{category:'work',correlation_id:'1'},async()=>true);await assert.rejects(observeTransition(e,{category:'model',correlation_id:'2'},async()=>{throw Error('private raw prompt and password');}));const rows=sink.drain();assert.deepEqual(rows.map(x=>x.transition),['dispatched','returned','dispatched','unknown']);assert.doesNotMatch(JSON.stringify(rows),/private|password|prompt/);
});
test('quality counts refusals/invalids in denominator and never promotes fixtures to model/provider quality',()=>{
 const result=evaluateQuality({kind:'retrieval',threshold:{numerator:2,denominator:3},cases:[{id:'good',expected:['a'],actual:['a'],status:'returned'},{id:'refused',expected:['b'],actual:null,status:'refused'},{id:'invalid',expected:['c'],actual:null,status:'invalid'}]});assert.equal(result.total,3);assert.equal(result.passed,1);assert.equal(result.status,'failed');assert.match(result.scope,/no-real-model/);
 assert.throws(()=>evaluateQuality({kind:'real-model',threshold:{numerator:1,denominator:1},cases:[]}));
});
