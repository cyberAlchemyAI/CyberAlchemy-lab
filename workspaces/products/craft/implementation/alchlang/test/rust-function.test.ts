import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {execFileSync,spawn} from 'node:child_process';
import {once} from 'node:events';
import {buildRustFunction} from '../src/rust-function-builder.js';
import {digest} from '../src/domainspec-profile.js';
const source=path.resolve(import.meta.dirname,'../../extensions/unified-project-v1/quantity-price.alch');
const fixtures=JSON.parse(fs.readFileSync(path.resolve(import.meta.dirname,'../../extensions/medusa-quantity-price-v1/fixtures.json'),'utf8'));
test('native Rust executable preserves all pricing fixtures, failures, traces and HTTP boundaries',async t=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'alch-rust-test-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));const initial=path.join(root,'bundle'),out=path.join(root,'moved');await buildRustFunction(source,initial);fs.renameSync(initial,out);const binary=path.join(out,'bin/alch-function');
 assert.ok(!fs.existsSync(path.join(out,'rust')));assert.ok(!fs.existsSync(path.join(out,'domain/generated')));
 const inventory=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8'));for(const [file,hash] of Object.entries(inventory.files))assert.equal(hash,digest(fs.readFileSync(path.join(out,file))),file);
 const run=(input:any,command='invoke')=>{try{return {status:0,value:JSON.parse(execFileSync(binary,[command],{input:JSON.stringify(input),encoding:'utf8'}))};}catch(e:any){return {status:e.status,value:JSON.parse(e.stdout)};}};
 for(const f of fixtures){const input={request:f.request,snapshot:f.snapshot};const result=run(input);assert.equal(result.status,0,f.name);for(const [key,value]of Object.entries(f.expected))assert.deepEqual(result.value[key],value,f.name);const trace=run(input,'trace');assert.equal(trace.status,0);assert.deepEqual(trace.value.outcome.result,result.value);assert.equal(trace.value.capture.complete,true);assert.ok(trace.value.events.some((e:any)=>e.kind==='selected-case'));const reversed=structuredClone(input);reversed.snapshot.prices.reverse();assert.deepEqual(run(reversed).value,result.value);}
 const base={request:fixtures[0].request,snapshot:fixtures[0].snapshot};
 const decimalInteger=JSON.parse(execFileSync(binary,['invoke'],{input:JSON.stringify(base).replace(/"quantity":15/, '"quantity":15e0'),encoding:'utf8'}));assert.deepEqual(decimalInteger,run(base).value);
 for(const [mutate,code] of [
  [(b:any)=>b.request.quantity=0,'FUNCTION_RANGE'],[(b:any)=>b.request.currency_code='eur','QUOTE_UNSUPPORTED_CURRENCY'],
  [(b:any)=>b.snapshot.prices.push(structuredClone(b.snapshot.prices[0])),'QUOTE_DUPLICATE_PRICE'],
  [(b:any)=>b.snapshot.prices[0].raw_amount.value='1.001','FUNCTION_DECIMAL'],
  [(b:any)=>{b.snapshot.prices=b.snapshot.prices.filter((p:any)=>p.id==='tier10');b.snapshot.prices[0].raw_amount.value='184467440737095516.15';},'CALCULATION_OVERFLOW'],
  [(b:any)=>b.snapshot.variant_id='wrong','QUOTE_VARIANT_MISMATCH'],
 ]as const){const b=structuredClone(base);mutate(b);const result=run(b);assert.equal(result.status,1,code);assert.equal(result.value.error,code);}
 const absent=run({request:base.request},'trace');assert.equal(absent.status,1);assert.equal(absent.value.outcome.code,'FUNCTION_INTEGRATION_REQUIRED');
 const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8'));for(const [name,sha]of Object.entries(manifest.files))assert.equal(digest(fs.readFileSync(path.join(out,name))),sha);
 assert.ok(!Object.keys(manifest.files).some(p=>p.endsWith('.js')||p.endsWith('.mjs')));assert.ok(Object.keys(manifest.files).some(p=>p.endsWith('Cargo.lock')));
 const child=spawn(binary,['serve'],{env:{...process.env,HOST:'127.0.0.1',PORT:'0',QUOTE_API_TOKEN:'test-secret'},stdio:['ignore','pipe','pipe']});t.after(()=>child.kill());
 const line=await Promise.race([once(child.stdout!,'data').then(([v])=>String(v)),new Promise<string>((_,reject)=>setTimeout(()=>reject(Error('Rust server timeout')),10000).unref())]);const address=JSON.parse(line).address;
 const request=(body:any,token='test-secret',url='/quote')=>fetch('http://'+address+url,{method:'POST',headers:{authorization:'Bearer '+token,'content-type':'application/json'},body:JSON.stringify(body)});
 for(const f of fixtures){const response=await request({request:f.request,snapshot:f.snapshot});assert.equal(response.status,({quoted:200,no_price:404,ambiguous_price:409}as any)[f.expected.status]);}
 assert.equal((await request(base,'wrong')).status,401);assert.equal((await request(base,'test-secret','/other')).status,404);assert.equal((await request({request:base.request})).status,503);assert.equal((await request({...base,unexpected:true})).status,422);
 assert.equal((await request({padding:'x'.repeat(262145)})).status,413);
 const closed=once(child,'exit');child.kill();await closed;
 await assert.rejects(()=>buildRustFunction(source,out),/FUNCTION_OUTPUT_EXISTS/);
});
