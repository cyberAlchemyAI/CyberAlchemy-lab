import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {buildFunction} from '../../implementation/dist/function-builder.js';
const temp=mkdtempSync(join(tmpdir(),'inference-execution-'));
let handler;
before(async()=>{await buildFunction(fileURLToPath(new URL('provider-selection.alch',import.meta.url)),join(temp,'bundle'));({handler}=await import(pathToFileURL(join(temp,'bundle/app/function/index.mjs')).href));});
after(()=>rmSync(temp,{recursive:true,force:true}));
const provider=(id,rank=10)=>({binding_id:id,binding_version:'v1',model:id==='a'?'fixture-chat-a':'fixture-chat-b',enabled:true,tenant_allowed:true,task:'text.generate',context_limit:4096,output_limit:1024,streaming:true,rank});
const request={request_id:'r1',tenant_id:'t1',task:'text.generate',required_context_tokens:512,max_output_tokens:256,stream:false};
async function run(rows,patch={},tenant='t1',token='fixture-secret'){
 const response=await handler(new Request('http://localhost/internal/select-provider',{method:'POST',headers:{authorization:'Bearer '+token,'content-type':'application/json'},body:JSON.stringify({request:{...request,...patch},catalog:{tenant_id:tenant,policy_version:'balanced-v1',providers:rows}})}),{INFERENCE_INTERNAL_TOKEN:'fixture-secret'},{fetch:()=>{throw Error('Unexpected external call');}});
 return {status:response.status,body:await response.json()};
}
test('compiled selection chooses minimum rank and pins versions',async()=>{
 const r=await run([provider('b',20),provider('a',10)]);assert.equal(r.status,200);assert.equal(r.body.binding_id,'a');assert.equal(r.body.binding_version,'v1');assert.equal(r.body.policy_version,'balanced-v1');
});
test('stable binding-ID tie breaking is independent of catalog order',async()=>{
 for(const rows of [[provider('b'),provider('a')],[provider('a'),provider('b')]])assert.equal((await run(rows)).body.binding_id,'a');
});
test('hard constraints exclude disabled, forbidden, over-limit and nonstreaming providers',async()=>{
 for(const patch of [{enabled:false},{tenant_allowed:false},{context_limit:511},{output_limit:255},{streaming:false}])assert.equal((await run([{...provider('a'),...patch},provider('b',20)],{stream:true})).body.binding_id,'b');
});
test('explicit model never silently substitutes another offering',async()=>{
 assert.equal((await run([provider('a'),provider('b',20)],{model:'fixture-chat-b'})).body.binding_id,'b');
 const r=await run([provider('a')],{model:'fixture-chat-b'});assert.equal(r.status,503);assert.equal(r.body.status,'unavailable');
});
test('empty and wholly ineligible catalogs return unavailable without evaluating a head',async()=>{
 for(const rows of [[],[{...provider('a'),enabled:false}]]){const r=await run(rows);assert.equal(r.status,503);assert.equal(r.body.status,'unavailable');}
});
test('tenant mismatch and duplicate binding identity fail closed',async()=>{
 for(const r of [await run([provider('a')],{},'other'),await run([provider('a'),provider('a')])])assert.equal(r.status,422);
});
test('HTTP boundary rejects unauthorized callers and forged request fields',async()=>{
 assert.equal((await run([provider('a')],{},'t1','wrong')).status,401);
 assert.equal((await run([provider('a')],{upstream_url:'https://example.com'})).status,422);
});
