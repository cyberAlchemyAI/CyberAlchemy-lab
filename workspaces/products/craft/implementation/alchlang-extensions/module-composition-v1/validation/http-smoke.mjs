import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync} from 'node:fs';
import {once} from 'node:events';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const directory=path.resolve(process.argv[2]??''),output=process.argv[3];if(process.argv.length!==4)throw Error('usage: node validation/http-smoke.mjs <checkout target directory> <new receipt.json>');
const fixtures=JSON.parse(readFileSync(path.resolve(import.meta.dirname,'../checkout-quote.fixtures.json'),'utf8')).filter(f=>!f.env);
const node=await import(pathToFileURL(path.join(directory,'node/index.mjs')).href);
const native=spawn(path.join(directory,'rust/alch-function'),['serve'],{env:{HOST:'127.0.0.1',PORT:'0',CHECKOUT_API_TOKEN:'fixture'},stdio:['ignore','pipe','pipe']});
let count=0;
try{
 const line=await Promise.race([once(native.stdout,'data').then(([b])=>String(b)),once(native,'exit').then(()=>{throw Error('native server exited');}),new Promise((_,reject)=>setTimeout(()=>reject(Error('native server startup timeout')),10000).unref())]);
 const origin='http://'+JSON.parse(line).address;
 const request=(input,token='fixture')=>new Request(origin+'/checkout-quote',{method:'POST',headers:{authorization:'Bearer '+token,'content-type':'application/json'},body:JSON.stringify(input)});
 for(const f of fixtures){const responses=[await node.handler(request(f.input),{CHECKOUT_API_TOKEN:'fixture'},{fetch:async()=>{throw Error('PROVIDER_FORBIDDEN');}}),await fetch(request(f.input))];
  const expected=f.expected.status==='succeeded'?f.expected.result:{error:f.expected.code};const status=f.expected.status==='succeeded'?({quoted:200,no_price:404,ambiguous_price:409,shipping_unavailable:404})[expected.status]:f.expected.code==='FUNCTION_ENV_REQUIRED'?503:422;
  for(const response of responses){assert.equal(response.status,status,f.name);assert.deepEqual(await response.json(),expected,f.name);}count++;
 }
 for(const response of [await node.handler(request(fixtures[0].input,'wrong'),{CHECKOUT_API_TOKEN:'fixture'}),await fetch(request(fixtures[0].input,'wrong'))])assert.equal(response.status,401);count++;
 const trace=await node.invokeWithTrace(fixtures[0].input);assert.equal(trace.selected_case,3);assert.equal(trace.capture.complete,true);
 const {execFileSync}=await import('node:child_process');const rustTrace=JSON.parse(execFileSync(path.join(directory,'rust/alch-function'),['trace'],{input:JSON.stringify(fixtures[0].input),encoding:'utf8',maxBuffer:8*1024*1024}));assert.equal(rustTrace.selected_case,3);assert.equal(rustTrace.capture.complete,true);assert.deepEqual(rustTrace.outcome,JSON.parse(JSON.stringify(trace.outcome)));count++;
 const receipt={schema_version:'alchlang.module-http-smoke/v1',status:'pass',cases:count,targets:['node-handler','native-loopback-http'],provider_connections:0,root_trace_selection:'pass',authority_effect:'none'};writeFileSync(output,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(receipt));
}finally{const exited=once(native,'exit');native.kill();await exited;}
