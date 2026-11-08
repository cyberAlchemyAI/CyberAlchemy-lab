import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,readdirSync} from 'node:fs';
import {execFileSync,spawn} from 'node:child_process';
import {once} from 'node:events';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {parseFunctionSource,parseFunctionExpression} from '../src/function-profile.js';
import {buildFunction} from '../src/function-builder.js';
const implementation=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const extension=path.resolve(implementation,'../extensions/serverless-function-v1');
const sourcePath=path.join(extension,'quantity-price.alch'),source=readFileSync(sourcePath,'utf8');
const fixtures=JSON.parse(readFileSync(path.resolve(extension,'../medusa-quantity-price-v1/fixtures.json'),'utf8'));
const temp=(t:any)=>{const p=mkdtempSync(path.join(os.tmpdir(),'alch-function-test-'));t.after(()=>rmSync(p,{recursive:true,force:true}));return p;};
const plain=(v:any)=>JSON.parse(JSON.stringify(v));
const request=(body:any,token='test-secret')=>new Request('http://localhost/quote',{method:'POST',headers:{authorization:`Bearer ${token}`,'content-type':'application/json'},body:JSON.stringify(body)});

test('one .alch source generates a standalone authenticated function with fixture parity',async t=>{
 const p=temp(t),out=path.join(p,'bundle');
 execFileSync(process.execPath,[path.join(implementation,'dist/cli.js'),'build',sourcePath,'--target','node-http','--out',out],{encoding:'utf8'});
 const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 for(const f of fixtures){const body={snapshot:f.snapshot,request:f.request};const before=structuredClone(body);const result=plain(await api.invoke(body));for(const [key,value]of Object.entries(f.expected))assert.deepEqual(result[key],value,f.name);assert.deepEqual(body,before);
  const response=await api.handler(request(body),{QUOTE_API_TOKEN:'test-secret'});assert.equal(response.status,({quoted:200,no_price:404,ambiguous_price:409} as any)[result.status]);assert.deepEqual(await response.json(),result);
 }
 const input={snapshot:fixtures[0].snapshot,request:fixtures[0].request};
 assert.equal((await api.handler(request(input),{})).status,503);
 assert.equal((await api.handler(request(input,'wrong'),{QUOTE_API_TOKEN:'test-secret'})).status,401);
 assert.equal((await api.handler(new Request('http://localhost/wrong'),{})).status,404);
 assert.equal((await api.handler(new Request('http://localhost/quote'),{})).status,405);
 const malformed=new Request('http://localhost/quote',{method:'POST',headers:{authorization:'Bearer test-secret','content-type':'application/json'},body:'{'});
 assert.equal((await api.handler(malformed,{QUOTE_API_TOKEN:'test-secret'})).status,400);
 const bad=structuredClone(input);bad.request.quantity=0;assert.equal((await api.handler(request(bad),{QUOTE_API_TOKEN:'test-secret'})).status,422);
 const extra=structuredClone(input);extra.request.region_id='hidden';assert.equal((await api.handler(request(extra),{QUOTE_API_TOKEN:'test-secret'})).status,422);
 const max=fixtures.find((f:any)=>f.name==='uint64_max');const overflow={snapshot:max.snapshot,request:{...max.request,quantity:2}};
 assert.deepEqual(await (await api.handler(request(overflow),{QUOTE_API_TOKEN:'test-secret'})).json(),{error:'CALCULATION_OVERFLOW'});
 const manifest=JSON.parse(readFileSync(path.join(out,'deployment.json'),'utf8'));assert.equal(manifest.provisioned,false);assert.ok(manifest.environment_references.includes('QUOTE_API_TOKEN'));
 const files=(d:string):string[]=>readdirSync(d,{withFileTypes:true}).flatMap(x=>x.isDirectory()?files(path.join(d,x.name)):[path.join(d,x.name)]);
 for(const f of files(out))assert.ok(!readFileSync(f,'utf8').includes('test-secret'));
 await assert.rejects(buildFunction(sourcePath,out),/FUNCTION_OUTPUT_EXISTS/);
 const child=spawn(process.execPath,[path.join(out,manifest.launcher)],{env:{...process.env,PORT:'0',HOST:'127.0.0.1',QUOTE_API_TOKEN:'test-secret'},stdio:['ignore','pipe','pipe']});
 t.after(()=>child.kill());
 const line=await Promise.race([once(child.stdout!,'data').then(([v])=>String(v)),new Promise<string>((_,reject)=>setTimeout(()=>reject(Error('launcher timeout')),5000).unref())]);
 const port=JSON.parse(line).address.port;
 const live=await fetch(`http://127.0.0.1:${port}/quote`,{method:'POST',headers:{authorization:'Bearer test-secret','content-type':'application/json'},body:JSON.stringify(input)});
 assert.equal(live.status,200);assert.equal((await live.json() as any).subtotal,'120.00');const closed=once(child,'exit');child.kill();await closed;
});

test('declared integration supplies query/auth/limits and validates upstream failures',async t=>{
 const p=temp(t),out=path.join(p,'bundle');await buildFunction(sourcePath,out);const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 const body={request:fixtures[0].request};const env={QUOTE_API_TOKEN:'test-secret',PRICE_SNAPSHOT_URL:'https://snapshot.example/prices',PRICE_SNAPSHOT_TOKEN:'upstream-secret'};
 let called=0;const io={fetch:async(url:any,options:any)=>{called++;assert.equal(url.searchParams.get('variant_id'),body.request.variant_id);assert.equal(options.headers.authorization,'Bearer upstream-secret');assert.equal(options.redirect,'error');assert.equal(options.method,'GET');assert.ok(options.signal);return Response.json(fixtures[0].snapshot);}};
 assert.equal((await api.handler(request(body),env,io)).status,200);assert.equal(called,1);
 assert.equal((await api.handler(request({...body,snapshot:fixtures[0].snapshot}),env,io)).status,200);assert.equal(called,1);
 assert.equal((await api.handler(request(body),{QUOTE_API_TOKEN:'test-secret'},io)).status,503);
 assert.equal((await api.handler(request(body),env,{fetch:async()=>new Response('',{status:503})})).status,502);
 assert.equal((await api.handler(request(body),env,{fetch:async()=>Response.json({wrong:true})})).status,502);
 assert.equal((await api.handler(request(body),env,{fetch:async()=>new Response('not json')})).status,502);
 const big='x'.repeat(262145);assert.equal((await api.handler(request(body),env,{fetch:async()=>new Response(big)})).status,502);
 const invalid={...env,PRICE_SNAPSHOT_URL:'http://untrusted.example'};assert.equal((await api.handler(request(body),invalid,io)).status,503);assert.equal(called,1);
 const altered=structuredClone(fixtures[0].snapshot);altered.variant_id='other';assert.equal((await api.handler(request(body),env,{fetch:async()=>Response.json(altered)})).status,422);
});

test('function source rejects unresolved bindings, duplicates, unsafe syntax and unsupported constructs',()=>{
 assert.equal(parseFunctionSource(source).model.endpoint.path,'/quote');
 for(const [from,to]of [['from Prices','from Missing'],['provided input.snapshot','provided input.missing'],['query variant_id input.request.variant_id','query variant_id input.missing'],['target node-http','target lambda'],['query("EligiblePrices"','query("Missing"'],['let request = input.request','let request = absent.request'],['  flow QuotePrice','  flow Missing'],['  auth-env QUOTE_API_TOKEN','  auth-env literal-secret'],['  method POST','  method PATCH'],['  timeout-ms 5000','  timeout-ms 0'],['  max-bytes 262144','  max-bytes 0'],['  let request = input.request','  let request = input.request\n  let request = input.request'],['profile function-v1','profile function-v2'],['  output PriceSnapshot','  output Missing'],['  transport provided-or-http','  transport javascript']])assert.throws(()=>parseFunctionSource(source.replace(from,to)),/FUNCTION_SOURCE/,to);
 for(const expression of ['eval("anything")','input.constructor','eq(1)','1 + 2','{a: 1, a: 2}','uint64(18446744073709551615)','(() => 1)()'])assert.throws(()=>parseFunctionExpression(expression),/FUNCTION_SOURCE/,expression);
});

test('source changes alter behavior without a custom adapter and request limits are enforced',async t=>{
 const p=temp(t),s=path.join(p,'euro.alch'),out=path.join(p,'bundle');
 writeFileSync(s,source.replaceAll('"usd"','"eur"'));
 await buildFunction(s,out);const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 const f=structuredClone(fixtures[0]);f.request.currency_code='EUR';for(const row of f.snapshot.prices)row.currency_code='eur';
 assert.equal((await api.invoke({request:f.request,snapshot:f.snapshot})).currency_code,'eur');
 const oversized=new Request('http://localhost/quote',{method:'POST',headers:{authorization:'Bearer test-secret','content-type':'application/json'},body:' '.repeat(262145)});
 assert.equal((await api.handler(oversized,{QUOTE_API_TOKEN:'test-secret'})).status,413);
 const {createFunction}=await import('../src/function-runtime.js');
 const model=parseFunctionSource(source.replace('timeout-ms 5000','timeout-ms 10').replace('timeout-ms 3000','timeout-ms 10')).model;
 const bounded=createFunction(model,{});
 const slow=new Request('http://localhost/quote',{method:'POST',headers:{authorization:'Bearer test-secret','content-type':'application/json'},body:new ReadableStream({start(){}}),duplex:'half'} as any);
 assert.equal((await bounded.handler(slow,{QUOTE_API_TOKEN:'test-secret'})).status,408);
 let aborted=false;
 const result=await bounded.handler(request({request:fixtures[0].request}),{QUOTE_API_TOKEN:'test-secret',PRICE_SNAPSHOT_URL:'https://snapshot.example',PRICE_SNAPSHOT_TOKEN:'test-secret'},{fetch:((_url:any,options:any)=>new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>{aborted=true;reject(Error('timeout'));},{once:true}))) as typeof fetch});
 assert.equal(result.status,504);assert.equal(aborted,true);
});
