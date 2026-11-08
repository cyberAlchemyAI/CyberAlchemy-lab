import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,cpSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {buildOutbound,loadOutbound} from '../../../implementation/dist/outbound-composition.js';
import {createHttpInvocation} from '../../../implementation/dist/http-invocation-adapter.js';
const base=fileURLToPath(new URL('../',import.meta.url)),dir=mkdtempSync(join(tmpdir(),'outbound-tests-'));
let bundle,built;
before(async()=>{built=await buildOutbound(join(base,'provider-invocation.alch'),join(dir,'bundle'));bundle=await import(pathToFileURL(join(dir,'bundle/app/invocation/index.mjs')).href);});
after(()=>rmSync(dir,{recursive:true,force:true}));
const row={binding_id:'a',binding_version:'v1',model:'alias',enabled:true,tenant_allowed:true,task:'text.generate',context_limit:4096,output_limit:1024,streaming:false,rank:1};
const input=()=>({request:{request_id:'r1',tenant_id:'t1',task:'text.generate',required_context_tokens:10,max_output_tokens:8,stream:false},catalog:{tenant_id:'t1',policy_version:'v1',providers:[{...row}]},messages:[{role:'user',content:'line one\nline two'}]});
const binding={id:'a',version:'v1',model:'alias',remoteModel:'deployment',url:'https://fixture.invalid/invoke',secret:'private-secret'};
const deps=fetchImpl=>createHttpInvocation({bindings:[binding],fetchImpl});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
test('generated local mappings compose one raw HTTP attempt without a provider business status',async()=>{
 const calls=[];const invoke=bundle.createInvocation(deps(async(url,options)=>{calls.push({url,...options});return Response.json({answer:'hello',stop_reason:'stop',prompt_tokens:0});}));
 const result=await invoke(input());assert.equal(result.output.text,'hello');assert.deepEqual(result.usage,{input_tokens:{value:0,provenance:'provider-reported'},output_tokens:{value:null,provenance:'unavailable'}});assert.equal(calls.length,1);assert.equal(calls[0].url,binding.url);assert.equal(calls[0].redirect,'manual');assert.equal(JSON.parse(calls[0].body).model,'deployment');assert.ok(!JSON.stringify(result).includes('private-secret'));
});
test('failed input, unavailable selection and mismatched binding never invoke transport',async()=>{
 let calls=0;const invoke=bundle.createInvocation(deps(async()=>{calls++;return Response.json({});}));
 const invalid=input();invalid.messages[0].content='';await assert.rejects(invoke(invalid),/INVALID_INPUT/);
 const empty=input();empty.catalog.providers=[];await assert.rejects(invoke(empty),/NO_ELIGIBLE_PROVIDER/);
 const mismatch=input();mismatch.catalog.providers[0].binding_version='v2';await assert.rejects(invoke(mismatch),/BINDING_MISMATCH/);assert.equal(calls,0);
});
test('response rejection and cancel acknowledgment do not release a pending transport slot',async()=>{
 let release;const events=[];const native=deps(()=>{throw Error('not used');});let attempts=0;
 const invoke=bundle.createInvocation({...native,http:{sendOnce(){attempts++;return {response:Promise.reject(Error('deadline from transport')),settled:new Promise(r=>{release=r;}),cancel:async()=>{}};}}},{maxConcurrent:1});
 await assert.rejects(invoke(input(),{observe:e=>events.push(e)}),/PROVIDER_TRANSPORT_FAILED/);await assert.rejects(invoke(input()),/OVERLOADED/);assert.equal(attempts,1);assert.ok(!events.some(e=>e.type==='transport_settled'));release();await sleep(0);assert.ok(events.some(e=>e.type==='transport_settled'));
});
test('deadline holds custody across ignored abort and late response, then permits another request',async()=>{
 let release,expire,started,settled,calls=0,now=0;const events=[];
 const begun=new Promise(r=>started=r),ended=new Promise(r=>settled=r);
 const native=createHttpInvocation({bindings:[binding],now:()=>now,fetchImpl:()=>{calls++;if(calls===1){started();return new Promise(r=>release=r);}return Response.json({answer:'next',stop_reason:'stop'});}});
 const invoke=bundle.createInvocation({...native,clock:{now:()=>now,schedule:callback=>{expire=callback;return ()=>{};}}},{timeoutMs:20,maxConcurrent:1});
 const first=invoke(input(),{observe:e=>{events.push(e);if(e.type==='transport_settled')settled();}});await begun;now=20;expire();
 await assert.rejects(first,/DEADLINE_EXCEEDED/);await assert.rejects(invoke(input()),/OVERLOADED/);release(Response.json({answer:'too late',stop_reason:'stop'}));await ended;assert.equal(calls,1);assert.equal(events.filter(e=>e.type==='transport_settled').length,1);assert.equal((await invoke(input())).output.text,'next');assert.equal(calls,2);
});
test('cancellation and invalid UTF-8 cannot yield successful JSON',async()=>{
 const bad=bundle.createInvocation(deps(async()=>new Response(Uint8Array.of(0xff))));await assert.rejects(bad(input()),/INVALID_PROVIDER_RESPONSE/);
 let started;const ready=new Promise(r=>{started=r;});const c=new AbortController();let release;const invoke=bundle.createInvocation(deps(async()=>{started();return new Promise(r=>{release=r;});}));const result=invoke(input(),{signal:c.signal});await ready;c.abort();await assert.rejects(result,/CANCELLED/);release(Response.json({answer:'late',stop_reason:'stop'}));await sleep(5);
});
test('bundle inventory binds normalized contract, module manifests, source and trace',()=>{
 const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');for(const [file,hash]of Object.entries(built.manifest.files))assert.equal(sha(join(dir,'bundle',file)),hash,file);
 const trace=JSON.parse(readFileSync(join(dir,'bundle/trace.json')));assert.deepEqual(trace.steps.map(s=>s.kind),['local','local','binding','local','http','local','local']);assert.equal(trace.authority_effect,'none');assert.deepEqual(bundle.contract.limits,{deadline_ms:5000,max_bytes:65536,max_concurrent:2,max_attempts:1});
});
test('authored changes lower to different rejection policy; unsupported syntax and targets reject',async()=>{
 const fixture=join(dir,'source');cpSync(base,fixture,{recursive:true,filter:p=>p===base||!['generated','support-audit'].includes(p.split('/').at(-1))});const file=join(fixture,'provider-invocation.alch'),source=readFileSync(file,'utf8');
 writeFileSync(file,source.replace('"NO_ELIGIBLE_PROVIDER"','"EMPTY_CATALOG"'));const changed=await loadOutbound(file);assert.equal(changed.compiled.contract.steps[1].reject,'EMPTY_CATALOG');
 for(const [from,to]of [['max-attempts 1','max-attempts 2'],['target node-http','target rust-http'],['output Complete.value','output Future.value'],['  body "Payload"','  body "Payload"\n  url "https://injected.invalid"'],['./invocation-input.alch','../outside.alch']]){writeFileSync(file,source.replace(from,to));await assert.rejects(loadOutbound(file));}
});
test('fixed binding adapter rejects unsafe URLs and enforces exact version before attempt',()=>{
 for(const url of ['http://provider.test/x','https://u:p@provider.test/x','https://provider.test/x?q=1','https://provider.test/x#fragment'])assert.throws(()=>createHttpInvocation({bindings:[{...binding,url}]}),/INVALID_PROVIDER_URL/);
 const d=deps(()=>{throw Error('must not call');});assert.throws(()=>d.http.sendOnce({id:'a',version:'v2'},{},{signal:new AbortController().signal,deadline:performance.now()+100}),/BINDING_MISMATCH/);
});
test('rejected settlement is not evidence for releasing a slot',async()=>{
 const events=[];const native=deps(()=>{});const invoke=bundle.createInvocation({...native,http:{sendOnce(){const settled=Promise.reject(Error('custody unknown'));settled.catch(()=>{});return {response:Promise.reject(Error('transport failed')),settled,cancel:async()=>{}};}}},{maxConcurrent:1});
 await assert.rejects(invoke(input(),{observe:e=>events.push(e)}),/PROVIDER_TRANSPORT_FAILED/);await sleep(0);await assert.rejects(invoke(input()),/OVERLOADED/);assert.ok(!events.some(e=>e.type==='transport_settled'));
});
test('resolved settlement releases a slot even if cancellation acknowledgment stays pending',async()=>{
 const native=deps(async()=>Response.json({answer:'done',stop_reason:'stop'}));const sendOnce=native.http.sendOnce;native.http={sendOnce(...args){return {...sendOnce(...args),cancel:()=>new Promise(()=>{})};}};
 const invoke=bundle.createInvocation(native,{maxConcurrent:1});assert.equal((await invoke(input())).output.text,'done');await sleep(0);assert.equal((await invoke(input())).output.text,'done');
});
