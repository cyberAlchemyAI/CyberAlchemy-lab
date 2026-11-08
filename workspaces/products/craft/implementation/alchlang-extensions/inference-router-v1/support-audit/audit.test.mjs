import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {buildFunction} from '../../../implementation/dist/function-builder.js';
import {parseDeclarativeSource} from '../../../implementation/dist/declarative-profile.js';
import {DurableSqliteTransactionalOutbox} from '../../../implementation/dist/durable-outbox-runtime.js';
const base=fileURLToPath(new URL('./',import.meta.url));
const ds=process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
const dsImport=p=>import(pathToFileURL(join(ds,p)).href);
const {compileDeclarativeFunction}=await dsImport('dist/typed-backend/declarative-function.js');
const {runDurableOperation}=await dsImport('dist/runtime/durable.js');
const {createCompleteL1Project}=await dsImport('test/helpers/l1-project.ts');
const {compileSystemIntegrationManifest}=await dsImport('dist/system-integration/compiler.js');
const dir=mkdtempSync(join(tmpdir(),'isb01-support-'));const functions={};let fixture;
const source=name=>readFileSync(join(base,name+'.alch'),'utf8');
before(async()=>{
 for(const name of ['aliases','model-summary','mapped-call']){
  await buildFunction(join(base,name+'.alch'),join(dir,name));
  functions[name]=await import(pathToFileURL(join(dir,name,'app/function/index.mjs')).href);
 }
});
after(()=>{if(fixture)rmSync(fixture.parent,{recursive:true,force:true});rmSync(dir,{recursive:true,force:true});});
const providers=[
 {model:'z',enabled:true,context_limit:8000,output_limit:1000,streaming:false},
 {model:'a',enabled:true,context_limit:4000,output_limit:800,streaming:false},
 {model:'a',enabled:true,context_limit:6000,output_limit:200,streaming:true},
 {model:'hidden',enabled:false,context_limit:1,output_limit:1,streaming:true},
];
const env={WITNESS_TOKEN:'local',REMOTE_URL:'https://provider.invalid/generate',REMOTE_TOKEN:'provider-secret'};
const input={request:{text:'hello'}};
const request=(path,body,signal)=>new Request('http://localhost/'+path,{method:'POST',headers:{authorization:'Bearer local','content-type':'application/json'},body:JSON.stringify(body),signal});
test('W01 generated query filters, deduplicates and sorts enabled aliases',async()=>{
 assert.deepEqual(await functions.aliases.invoke({providers}),{status:'listed',aliases:['a','z']});
 assert.deepEqual(await functions.aliases.invoke({providers:[]}),{status:'listed',aliases:[]});
});
test('W02 generated per-alias aggregation takes independent minima and any streaming',async()=>{
 const summary=await functions['model-summary'].invoke({providers,model:'a'});
 assert.deepEqual(summary,{status:'found',model:'a',context_limit:4000,output_limit:200,streaming:true});
 const missing=await functions['model-summary'].handler(request('model-summary',{providers,model:'hidden'}),env);
 assert.equal(missing.status,404);assert.deepEqual(await missing.json(),{status:'missing',model:'hidden'});
});
test('W03 complete discovery semantics reuse generated functions; native loop is still required in this witness',async()=>{
 const {aliases}=await functions.aliases.invoke({providers});
 const summaries=[];for(const model of aliases)summaries.push(await functions['model-summary'].invoke({providers,model}));
 assert.equal(summaries.length,2);assert.equal(summaries[0].output_limit,200);assert.equal(summaries[1].context_limit,8000);
});
test('W04 single-function correlated query input is rejected at Alch parsing',()=>{
 assert.throws(()=>parseDeclarativeSource(source('model-summary').replace('query Bindings:\n','query Bindings:\n  input alias: identifier\n')),/unsupported|clause/i);
});
test('W05 GET, anonymous endpoints, multiple endpoints and SSE response clause are unsupported in this profile',()=>{
 const valid=source('aliases');
 const variants=[valid.replace('method POST','method GET'),valid.replace('  auth-env WITNESS_TOKEN\n',''),valid+'\n'+valid.slice(valid.indexOf('endpoint Witness:')).replace('endpoint Witness:','endpoint Other:'),valid.replace('  method POST','  response-mode sse\n  method POST')];
 for(const variant of variants)assert.throws(()=>parseDeclarativeSource(variant),/endpoint|unknown|config/i);
});
test('W06 generated local result maps into a typed remote POST with fixed operator URL/token',async()=>{
 const calls=[];const result=await functions['mapped-call'].invoke(input,env,{fetch:async(url,options)=>{calls.push({url:String(url),options});return Response.json({status:'done',text:'remote result'});}});
 assert.deepEqual(result,{status:'done',text:'remote result'});assert.equal(calls.length,1);
 assert.equal(calls[0].url,env.REMOTE_URL);assert.equal(calls[0].options.method,'POST');assert.equal(calls[0].options.headers.authorization,'Bearer provider-secret');assert.deepEqual(JSON.parse(calls[0].options.body),{text:'hello'});
});
test('W07 declared integration error mapping already produces HTTP 502 without retry',async()=>{
 let count=0;const response=await functions['mapped-call'].handler(request('mapped-call',input),env,{fetch:async()=>{count++;return new Response('private diagnostic',{status:500});}});
 assert.equal(response.status,502);assert.deepEqual(await response.json(),{error:'FUNCTION_INTEGRATION_STATUS'});assert.equal(count,1);
});
test('W08 module HTTP requires declared business status and cannot directly consume raw inference JSON',async()=>{
 await assert.rejects(functions['mapped-call'].invoke(input,env,{fetch:async()=>Response.json({answer:'hello',stop_reason:'stop'})}),/FUNCTION_INTEGRATION_STATUS/);
});
test('W09 generic http-post transport is rejected rather than silently treated as module HTTP',()=>{
 const raw=source('aliases').replace('schema Input:',`integration Raw:\n  transport http-post\n  output Output\n  url-env RAW_URL\n  timeout-ms 100\n  max-bytes 1024\n\nschema Input:`);
 assert.throws(()=>parseDeclarativeSource(raw),/integration contract/);
});
test('W10 existing module transport consumes JSON and rejects SSE frames',async()=>{
 await assert.rejects(functions['mapped-call'].invoke(input,env,{fetch:async()=>new Response('event: delta\ndata: {"text":"hi"}\n\n',{headers:{'content-type':'text/event-stream'}})}),/FUNCTION_INTEGRATION_FAILED/);
});
test('W11 invoke accepts caller cancellation but HTTP handler does not forward Request.signal',async()=>{
 const c=new AbortController();c.abort();let signal;
 const fetch=async(_,options)=>{signal=options.signal;return Response.json({status:'done',text:'remote result'});};
 await functions['mapped-call'].invoke(input,env,{fetch,signal:c.signal});assert.equal(signal.aborted,true);
 await functions['mapped-call'].handler(request('mapped-call',input,c.signal),env,{fetch});assert.equal(signal.aborted,false);
});
test('W12 DomainSpec integration manifest already expresses bindings but makes no runtime-observation claim',()=>{
 const binding=JSON.parse(readFileSync(join(ds,'fixtures/input-roots/canonical-project/integrations/settle-runtime.json'),'utf8'));
 const result=compileSystemIntegrationManifest(binding,'typescript');
 assert.equal(result.runtime_guarantees_observed,false);assert.equal(result.authority_effect,'none');assert.match(result.binding_digest,/^[a-f0-9]{64}$/);
});
const durableRequest=()=>({schema_version:'domainspec.durable-operation-invocation/v1',invocation_id:'durable-settlement',selector:'alpha:settle',operation_input:{state:{customer:'customer-1','customer.settlement-status':'pending'},changes:{'customer.settlement-status':'settled'},guard:true},transaction:{aggregate_type:'Settlement',aggregate_id:'settlement-1',expected_version:0,occurred_at:'2026-09-03T12:00:00.000Z',event_ids:{'alpha:settlement-requested':'event-1'},event_payloads:{'alpha:settlement-requested':{}},max_attempts:3}});
const digest=createHash('sha256').update(readFileSync(fileURLToPath(new URL('../../../implementation/dist/durable-outbox-runtime.js',import.meta.url)))).digest('hex');
function port(store){return{provider_id:'sqlite-transactional-outbox-v1',implementation_sha256:digest,commit:(value,failpoint)=>store.commit(value,failpoint)};}
test('W13 compiled DomainSpec operation reuses actual SQLite atomic commit and restart reconciliation',()=>{
 fixture=createCompleteL1Project();const db=join(dir,'custody.sqlite');let store=new DurableSqliteTransactionalOutbox(db);
 try{const result=runDurableOperation(fixture.root,durableRequest(),port(store));assert.equal(result.commit_status,'committed');assert.equal(store.records().length,1);}finally{store.close();}
 store=new DurableSqliteTransactionalOutbox(db);
 try{assert.equal(runDurableOperation(fixture.root,durableRequest(),port(store)).commit_status,'already-committed');assert.equal(store.records().length,1);const conflict=durableRequest();conflict.transaction.event_payloads['alpha:settlement-requested']={changed:true};assert.throws(()=>runDurableOperation(fixture.root,conflict,port(store)),/OUTBOX_VERSION_CONFLICT/);assert.equal(store.records().length,1);}finally{store.close();}
});
test('W14 actual transaction failpoint rolls back both state and event; outbox is not generic request custody',()=>{
 const store=new DurableSqliteTransactionalOutbox(join(dir,'rollback.sqlite'));
 try{
  assert.throws(()=>runDurableOperation(fixture.root,durableRequest(),port(store),'after-state-write'),/OUTBOX_FAILPOINT_AFTER_STATE_WRITE/);
  assert.equal(store.state('Settlement','settlement-1'),null);assert.deepEqual(store.records(),[]);
  assert.throws(()=>store.commit({aggregateType:'Request',aggregateId:'key',expectedVersion:0,state:{pending:true},messages:[]}),/OUTBOX/);
 }finally{store.close();}
});
test('W15 DomainSpec declarative Query has no parameterized-query contract slot',()=>{
 const contract=structuredClone(parseDeclarativeSource(source('model-summary')).contract);
 contract.nodes.find(n=>n.kind==='Query').input={name:'alias',type:'String'};
 assert.throws(()=>compileDeclarativeFunction(contract),/contract keys/);
});
test('W16 current system-integration transport contract rejects HTTP request-response mode',()=>{
 const binding=JSON.parse(readFileSync(join(ds,'fixtures/input-roots/canonical-project/integrations/settle-runtime.json'),'utf8'));
 binding.transport_bindings=[{binding_id:'raw-http',mode:'http',direction:'request-response',operation_ref:'alpha:settle',event_ref:'alpha:settlement-requested',channel_ref:'channel',delivery_policy_ref:'delivery',failure_policy_ref:'failure',envelope_profile_ref:'envelope',evidence_boundary:'local-witness'}];
 assert.throws(()=>compileSystemIntegrationManifest(binding,'typescript'),error=>error.code==='SIC_TRANSPORT_BINDING');
});
test('W17 result bindings have no foreach module invocation clause',()=>{
 const valid=source('aliases').replace('schema Input:\n','schema Input:\n  snapshot: Output\n').replace('result Aliases:', 'integration Snapshot:\n  transport provided\n  provided input.snapshot\n  output Output\n  timeout-ms 100\n  max-bytes 65536\n\nresult Aliases:\n  bind snapshot from Snapshot');
 parseDeclarativeSource(valid);
 assert.throws(()=>parseDeclarativeSource(valid.replace('bind snapshot from Snapshot','bind each snapshot from Snapshot')),/result/);
});
