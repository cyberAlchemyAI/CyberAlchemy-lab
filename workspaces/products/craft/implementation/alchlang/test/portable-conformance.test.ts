import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {checkFunction} from '../src/function-builder.js';
import {parseDeclarativeSource} from '../src/declarative-profile.js';
import {portableTimestamp,prepareIntegrationRequest,validateSchema} from '../src/boundary-runtime.js';
import {compareExecutions} from '../src/conformance.js';
const source=path.resolve(import.meta.dirname,'../../extensions/portable-conformance-v1/shipping-options.alch');
test('portable schema agrees on strict calendar dates, full pattern matches and error order',()=>{
 for(const date of ['2024-02-29T23:59:59Z','0001-01-01T00:00:00.123456789+23:59'])assert.ok(portableTimestamp(date));
 for(const date of ['2025-02-29T00:00:00Z','0000-01-01T00:00:00Z','2024-04-31T00:00:00Z','2024-01-01T00:00:60Z','2024-01-01t00:00:00z','2024-01-01T00:00:00+24:00'])assert.equal(portableTimestamp(date),false,date);
 const {model}=parseDeclarativeSource(readFileSync(source,'utf8'));
 assert.throws(()=>validateSchema(model,'Request',{request_id:'x',country:'GB\n',weight_grams:-1,requires_tracking:false}),/FUNCTION_PATTERN/);
 const value=validateSchema(model,'Request',{request_id:'\u00a0',country:'GB',weight_grams:0,requires_tracking:false});assert.ok(!Object.hasOwn(value,'note'));
});
test('request preparation replaces declared duplicates and requires nonempty credentials',()=>{
 const b={urlEnv:'URL',secretEnv:'TOKEN',query:{country:'input.country'},timeout:100,maxBytes:500};
 const request=prepareIntegrationRequest(b,{input:{country:'GB'}},{URL:'https://fixture.invalid/path?country=US&country=FR&keep=x',TOKEN:'fixture'});
 const u=new URL(request.url);assert.deepEqual(u.searchParams.getAll('country'),['GB']);assert.equal(u.searchParams.get('keep'),'x');assert.equal(request.headers.authorization,'Bearer fixture');
 assert.throws(()=>prepareIntegrationRequest(b,{input:{country:'GB'}},{URL:u.href,TOKEN:''}),/FUNCTION_ENV_REQUIRED/);
});
test('both target checks reject unsupported patterns with the source field location',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'portable-reject-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 const bad=readFileSync(source,'utf8').replace('pattern "^[A-Z]{2}$"','pattern "^(?=GB)[A-Z]{2}$"'),file=path.join(root,'unsupported.alch');writeFileSync(file,bad);
 const line=bad.slice(0,bad.indexOf('  country:')).split('\n').length;
 for(const target of ['node-http','rust-http'])await assert.rejects(()=>checkFunction(file,target),error=>{assert.match(String(error),/DS_TARGET_UNSUPPORTED/);assert.ok(String(error).includes(`:${line}: Option.country:`),String(error));return true;});
 assert.throws(()=>parseDeclarativeSource(bad.replace('node-rust-v1','future-v9')),/portability/);
});
test('comparison cannot pass wrong oracle, changed requests, decisions or truncated captures',()=>{
 const execution={outcome:{status:'succeeded',result:{status:'ok'}},requests:[{url:'https://fixture.invalid/?b=2&a=1',method:'GET'}],events:[{kind:'node-result',node_kind:'Rule',declaration:'Eligible',value:true}],capture:{complete:true},unused_responses:0};
 const other=structuredClone(execution);other.requests[0].url='https://fixture.invalid/?a=1&b=2';assert.ok(Object.values(compareExecutions(execution,other,execution.outcome)).every(Boolean));
 other.events[0].value=false;assert.equal(compareExecutions(execution,other,execution.outcome).decisions,false);
 other.capture.complete=false;assert.equal(compareExecutions(execution,other,execution.outcome).complete,false);
 assert.equal(compareExecutions(execution,execution,{status:'failed',code:'WRONG'}).oracle,false);
 other.requests[0].url='https://fixture.invalid/?a=3';assert.equal(compareExecutions(execution,other,execution.outcome).requests,false);
 other.unused_responses=1;assert.equal(compareExecutions(execution,other,execution.outcome).consumed,false);
});

test('target checking rejects legacy procedural functions before native generation',async()=>{
 const legacy=path.resolve(import.meta.dirname,'../../extensions/serverless-function-v1/quantity-price.alch');
 await assert.rejects(()=>checkFunction(legacy,'rust-http'),/DS_TARGET_UNSUPPORTED:.*requires declarative-function-v1/);
});
