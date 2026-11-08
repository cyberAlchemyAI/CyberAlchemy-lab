import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,readdirSync} from 'node:fs';
import {execFileSync,spawn} from 'node:child_process';
import {once} from 'node:events';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {parseDeclarativeSource,parseDeclarativeExpression} from '../src/declarative-profile.js';
import {loadDomainSpecCompiler} from '../src/domainspec-cli.js';
import {buildFunction} from '../src/function-builder.js';
const implementation=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const extension=path.resolve(implementation,'../extensions/declarative-function-v1');
const sourcePath=path.join(extension,'quantity-price.alch'),source=readFileSync(sourcePath,'utf8');
const fixtures=JSON.parse(readFileSync(path.resolve(extension,'../medusa-quantity-price-v1/fixtures.json'),'utf8'));
const temp=(t:any)=>{const p=mkdtempSync(path.join(os.tmpdir(),'alch-function-test-'));t.after(()=>rmSync(p,{recursive:true,force:true}));return p;};
const plain=(v:any)=>JSON.parse(JSON.stringify(v));
const request=(body:any,token='test-secret')=>new Request('http://localhost/quote',{method:'POST',headers:{authorization:`Bearer ${token}`,'content-type':'application/json'},body:JSON.stringify(body)});

test('declarative .alch source generates a standalone authenticated function with fixture parity',async t=>{
 const p=temp(t),out=path.join(p,'bundle');
 execFileSync(process.execPath,[path.join(implementation,'dist/cli.js'),'build',sourcePath,'--target','node-http','--out',out],{encoding:'utf8'});
 const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 for(const f of fixtures){const body={snapshot:f.snapshot,request:f.request};const before=structuredClone(body);const result=plain(await api.invoke(body));for(const [key,value]of Object.entries(f.expected))assert.deepEqual(result[key],value,f.name);assert.deepEqual(body,before);
  const response=await api.handler(request(body),{QUOTE_API_TOKEN:'test-secret'});assert.equal(response.status,({quoted:200,no_price:404,ambiguous_price:409} as any)[result.status]);assert.deepEqual(await response.json(),result);
 }
 const runtime=readFileSync(path.join(out,'runtime/boundary.mjs'),'utf8');assert.ok(!runtime.includes('function evaluate('));assert.ok(!runtime.includes("step.kind==='let'"));
 assert.ok(readFileSync(path.join(out,'app/function/behavior.mjs'),'utf8').includes('domainspec.declarative-function/v1'));
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
 const unsupported={request:{...body.request,currency_code:'eur'}};assert.equal((await api.handler(request(unsupported),env,io)).status,422);assert.equal(called,0);
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


test('declarative type checking rejects procedural syntax, unresolved fields, cycles and wrong types',async()=>{
 const compiler=await loadDomainSpecCompiler();
 const check=(s:string)=>compiler.compileDeclarativeFunction(parseDeclarativeSource(s).contract);
 check(source);
 for(const [from,to] of [
  ['row.raw_amount.value','row.raw_amount.missing'],
  ['decimal(row.raw_amount.value, 2)','row.raw_amount.value'],
  ['select PriceRow(row)','select PriceRow(input.request)'],
  ['from p in Tiers','from p in Eligible'],
  ['condition exactly_one p in Cheapest: true','condition count(Cheapest)'],
  ['field price_id = p.priceId','field price_id = p.missing'],
  ['when NoPrice yield EmptyQuote','when NoPrice yield Cheapest'],
  ['from Prices','from Missing'],
  ['  result QuotePrice','  result Missing'],
  ['query Tiers:','query Tiers:\n  let x = input'],
  ['decimal(row.raw_amount.value, 2)','decimal(row.raw_amount.value, 19)'],
  ['p.minQuantity <= uint64(input.request.quantity)','p.minQuantity <= input.request.quantity'],
  ['where not present(row.deleted_at)','where row.deleted_at == "x"'],
  ['field request_id = input.request.request_id','field request_id = input.constructor'],
 ])assert.throws(()=>check(source.replace(from,to)),/ALCH_DECLARATIVE|DS_DECLARATIVE|FUNCTION_SOURCE/,to);
 for(const e of ['x => x','{a: 1}','1 + 2','eval("evil")']){
  if(e.startsWith('eval'))assert.throws(()=>check(source.replace('condition exactly_one p in Cheapest: true','condition '+e)),/unknown operator/);
  else assert.throws(()=>parseDeclarativeExpression(e),/ALCH_DECLARATIVE/);
 }
});

test('quantified pricing is independent of row order and rejects invalid boundary data',async t=>{
 const p=temp(t),out=path.join(p,'bundle');await buildFunction(sourcePath,out);const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 for(const f of fixtures){const snapshot=structuredClone(f.snapshot);snapshot.prices.reverse();const result=plain(await api.invoke({request:f.request,snapshot}));for(const [k,v]of Object.entries(f.expected))assert.deepEqual(result[k],v,f.name);}
 const base={request:fixtures[0].request,snapshot:fixtures[0].snapshot};
 const failures:[string,(b:any)=>void,string][]=[
  ['duplicate',b=>b.snapshot.prices.push(structuredClone(b.snapshot.prices[0])),'QUOTE_DUPLICATE_PRICE'],
  ['range',b=>{b.snapshot.prices[0].min_quantity=20;b.snapshot.prices[0].max_quantity=10;},'QUOTE_TIER_RANGE'],
  ['set',b=>b.snapshot.prices[0].price_set_id='wrong','QUOTE_PRICE_SET_MISMATCH'],
  ['decimal',b=>b.snapshot.prices[0].raw_amount.value='1.001','FUNCTION_DECIMAL'],
  ['negative',b=>b.snapshot.prices[0].raw_amount.value='-1','FUNCTION_DECIMAL'],
  ['unsupported',b=>b.request.currency_code='eur','QUOTE_UNSUPPORTED_CURRENCY'],
 ];
 for(const [name,mutate,code]of failures){const b=structuredClone(base);mutate(b);const response=await api.handler(request(b),{QUOTE_API_TOKEN:'test-secret'});assert.equal(response.status,422,name);assert.deepEqual(await response.json(),{error:code},name);}
});

test('changed Alch declarations change generated behavior; ambiguous result cases fail closed',async t=>{
 const compiler=await loadDomainSpecCompiler(),parsed=parseDeclarativeSource(source);
 const first=compiler.compileDeclarativeFunction(parsed.contract);assert.deepEqual(first,compiler.compileDeclarativeFunction(parsed.contract));
 const contract=structuredClone(parsed.contract);contract.results.push(contract.results[0]);const generated=compiler.compileDeclarativeFunction(contract);
 const module=await import('data:text/javascript;base64,'+Buffer.from(generated.source).toString('base64'));
 const f=fixtures.find((f:any)=>f.expected.status==='no_price');assert.throws(()=>module.execute({input:{request:f.request},snapshot:f.snapshot},{}),/DS_RESULT_CARDINALITY/);
 const p=temp(t),s=path.join(p,'euro.alch'),out=path.join(p,'bundle');writeFileSync(s,source.replaceAll('"usd"','"eur"'));await buildFunction(s,out);
 const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);const euro=structuredClone(fixtures[0]);euro.request.currency_code='EUR';for(const row of euro.snapshot.prices)row.currency_code='eur';
 assert.equal((await api.invoke({request:euro.request,snapshot:euro.snapshot})).currency_code,'eur');
});

test('transport-only runtime enforces request and integration time bounds',async()=>{
 const {createBoundary}=await import('../src/boundary-runtime.js');
 const parsed=parseDeclarativeSource(source.replace('timeout-ms 5000','timeout-ms 10').replace('timeout-ms 3000','timeout-ms 10'));
 const bounded=createBoundary(parsed.model,parsed.boundaryBindings,()=>{throw Error('must not execute');});
 const slow=new Request('http://localhost/quote',{method:'POST',headers:{authorization:'Bearer test-secret','content-type':'application/json'},body:new ReadableStream({start(){}}),duplex:'half'} as any);
 assert.equal((await bounded.handler(slow,{QUOTE_API_TOKEN:'test-secret'})).status,408);
 let aborted=false;
 const result=await bounded.handler(request({request:fixtures[0].request}),{QUOTE_API_TOKEN:'test-secret',PRICE_SNAPSHOT_URL:'https://snapshot.example',PRICE_SNAPSHOT_TOKEN:'test-secret'},{fetch:((_url:any,options:any)=>new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>{aborted=true;reject(Error('timeout'));},{once:true}))) as typeof fetch});
 assert.equal(result.status,504);assert.equal(aborted,true);
});
