import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {once} from 'node:events';
import {buildServiceRoutes,loadServiceRoutes} from '../../../implementation/dist/service-routes.js';
import {buildFunction} from '../../../implementation/dist/function-builder.js';
const fixture=fileURLToPath(new URL('./quote-service/',import.meta.url));
const directory=mkdtempSync(join(tmpdir(),'quote-reuse-'));let generated,calculate,admission,built;
before(async()=>{
 built=await buildServiceRoutes(join(fixture,'service.alch'),join(directory,'service'));
 generated=await import(pathToFileURL(join(built.output,built.manifest.entry)).href);
 for(const [name,source] of [['calculate',join(fixture,'calculate.alch')],['admission',fileURLToPath(new URL('../admission.alch',import.meta.url))]]){
  await buildFunction(source,join(directory,name));const fn=(await import(pathToFileURL(join(directory,name,'app/function/index.mjs')).href)).invoke;
  if(name==='calculate')calculate=fn;else admission=fn;
 }
});
after(()=>rmSync(directory,{recursive:true,force:true}));
const operation=async(value,_env,io)=>(await calculate(value,{}, {...io,localOnly:true})).value;
const options=()=>({operations:{CalculateQuote:operation}});
const request=(value={quantity:4},extra={})=>new Request('http://local/v1/quotes',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(value),...extra});
test('independent generated quote service runs real loopback HTTP and authored pricing',async()=>{
 const server=generated.createServer(options());server.listen(0,'127.0.0.1');await once(server,'listening');const root='http://127.0.0.1:'+server.address().port;
 try{assert.deepEqual(await (await fetch(root+'/health')).json(),{service:'quote'});const response=await fetch(root+'/v1/quotes',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({quantity:4})});assert.equal(response.status,200);assert.equal(response.headers.get('cache-control'),'no-store');assert.deepEqual(await response.json(),{total:1000,currency:'USD'});}
 finally{server.closeAllConnections();await new Promise(r=>server.close(r));}
});
test('quote validation and generated HTTP error policy reject before the operation',async()=>{
 let calls=0;const handle=generated.createHandler({operations:{CalculateQuote:async(...args)=>{calls++;return operation(...args);}}});
 for(const body of [{quantity:0},{quantity:11},{quantity:1,discount:10}]){const response=await handle(request(body));assert.equal(response.status,400);assert.deepEqual(await response.json(),{code:'INVALID_INPUT'});}
 assert.equal((await handle(request(undefined,{headers:{'content-type':'text/plain'}}))).status,415);
 assert.equal((await handle(new Request('http://local/missing'))).status,404);
 const method=await handle(new Request('http://local/v1/quotes'));assert.equal(method.status,405);assert.equal(method.headers.get('allow'),'POST');assert.equal(calls,0);
});
test('independent operation binding validates its output and redacts native diagnostics',async()=>{
 assert.throws(()=>generated.createHandler(),/SERVICE_OPERATION_BINDINGS/);
 for(const CalculateQuote of [async()=>({total:10001,currency:'USD'}),async()=>{throw Error('private adapter diagnostic');},async()=>new Response('bypass')]){
 const response=await generated.createHandler({operations:{CalculateQuote}})(request());assert.equal(response.status,500);assert.deepEqual(await response.json(),{code:'QUOTE_FAILED'});
 }
});
test('quote cancellation reaches the typed operation and suppresses late success',async()=>{
 let entered,release,seen;const begun=new Promise(r=>entered=r),c=new AbortController();
 const handle=generated.createHandler({operations:{CalculateQuote:async(value,_env,io)=>{seen=io.signal;entered();await new Promise(r=>release=r);return operation(value,{},{});}}});
 const pending=handle(request(undefined,{signal:c.signal}));await begun;c.abort();assert.equal(seen.aborted,true);release();const response=await pending;assert.equal(response.status,499);assert.deepEqual(await response.json(),{code:'CANCELLED'});
});
test('quote bundle is fully inventoried with fixture-local sources and distinct routes',()=>{
 for(const [file,hash]of Object.entries(built.manifest.files))assert.equal(createHash('sha256').update(readFileSync(join(built.output,file))).digest('hex'),hash,file);
 assert.deepEqual(built.manifest.required_bindings,['CalculateQuote']);assert.deepEqual(generated.plan.routes.map(r=>r.path),['/health','/v1/quotes']);
 const source=readFileSync(join(fixture,'service.alch'),'utf8');assert.ok(!source.includes('inference'));for(const module of Object.values(loadServiceRoutes(join(fixture,'service.alch')).modules))assert.ok(module.file.startsWith(fixture));
});
test('changing authored pricing changes execution without changing a native adapter',async()=>{
 const path=join(directory,'changed.alch');writeFileSync(path,readFileSync(join(fixture,'calculate.alch'),'utf8').replace('field total = 1000','field total = 1200'));
 await buildFunction(path,join(directory,'changed'));const changed=(await import(pathToFileURL(join(directory,'changed/app/function/index.mjs')).href)).invoke;
 assert.equal((await changed({status:'normalized',quantity:4},{},{localOnly:true})).value.total,1200);
});
test('compiled inference admission preserves strategy precedence and automatic model selection',async()=>{
 const call=input=>admission(input,{}, {localOnly:true});
 assert.equal((await call({strategy:'balanced',strategies:['balanced'],models:[]})).code,'OK');
 assert.equal((await call({strategy:'balanced',model:'known',strategies:['balanced'],models:['known']})).code,'OK');
 assert.equal((await call({strategy:'balanced',model:'unknown',strategies:['balanced'],models:['known']})).code,'UNKNOWN_MODEL');
 assert.equal((await call({strategy:'cost',model:'unknown',strategies:['balanced'],models:['known']})).code,'UNSUPPORTED_STRATEGY');
});
test('native responsibility inventory covers every physical line of its exact source files',()=>{
 const root=fileURLToPath(new URL('../../../../../../../../',import.meta.url));const inventory=JSON.parse(readFileSync(new URL('../local-pattern/native-inventory.json',import.meta.url)));
 for(const file of inventory.files){const bytes=readFileSync(join(root,file.path));assert.equal(createHash('sha256').update(bytes).digest('hex'),file.sha256,file.path);assert.equal(bytes.toString().split('\n').length-1,file.lines);let next=1;for(const span of file.spans){assert.equal(span.start,next);assert.ok(span.responsibility&&span.owner);next=span.end+1;}assert.equal(next,file.lines+1);}
 assert.equal(inventory.files.reduce((n,f)=>n+f.lines,0),inventory.total_lines);
});
