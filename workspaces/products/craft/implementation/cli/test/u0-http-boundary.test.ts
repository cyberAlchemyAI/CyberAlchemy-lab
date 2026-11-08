import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {getEventListeners} from 'node:events';
import {createU0HttpHandler,acceptsU0JsonMedia,inspectU0HttpResponse,U0_HTTP_STATUS} from '../profiles/node-http-entry-u0-v4/runtime/application-http.mjs';
import {U0_CONFIG_EXAMPLE,U0_ADAPTER_FAILURES,type U0PureInvoke,type U0WireConfiguration} from '../src/profile-engine/u0-realization-contract.js';
import type {U0HandlerAssetOwnerV2} from '../src/profile-engine/business-authoring-stages-v2.js';
// Component seam fixtures, not generated business code or application qualification.
// Open Questions: J01/G01/U08/V01 and fixed installed replay.
const owner:U0HandlerAssetOwnerV2=Object.freeze({create:createU0HttpHandler});
const domain={rejection_code:'delivery-verification-required'};
const value='{"id":"9007199254740993","verified":true}';
const bytes=(s:string)=>new TextEncoder().encode(s);
const contract:U0PureInvoke<string>=input=>input.verified?{kind:'completed',value:input}:{kind:'rejected',code:domain.rejection_code};
function request(body:BodyInit|null=value,options:RequestInit&{url?:string}={}):Request {
 const {url,...init}=options;
 return new Request(url??'http://component.invalid/confirm-delivery',{method:'POST',headers:{'content-type':'application/json'},body,...init,duplex:'half'} as RequestInit);
}
const stream=(source:UnderlyingDefaultSource<Uint8Array>)=>new ReadableStream<Uint8Array>(source,{highWaterMark:0});
function fixture(invoke:U0PureInvoke<string>=contract,timeout=2000,cap=4096){
 let calls=0;const handler=owner.create(input=>{calls++;return invoke(input);},{...U0_CONFIG_EXAMPLE,body_timeout_ms:timeout,request_bytes:cap},domain);
 return {handler,calls:()=>calls};
}
async function error(response:Response,status:number,code:string){
 assert.equal(response.status,status);assert.equal(response.headers.get('content-type'),'application/json; charset=utf-8');
 assert.equal(await response.text(),'{"kind":"adapter-error","code":"'+code+'"}');
 const observed=inspectU0HttpResponse(response)!;assert.equal(observed.outcome,'adapter-error');assert.equal(observed.code,code);assert.equal(observed.peer_delivery,'not-observed');assert.ok(Object.isFrozen(observed));
}
function cleaned(response:Response,req:Request){
 const observed=inspectU0HttpResponse(response)!;assert.equal(observed.timer_clear_count,1);assert.equal(observed.abort_listener_removed,true);
 assert.equal(req.body?.locked??false,false);assert.equal(getEventListeners(req.signal,'abort').length,0);
}
test('U07 independent fixed adapter status and all media contracts',()=>{
 assert.deepEqual(U0_HTTP_STATUS,Object.fromEntries(U0_ADAPTER_FAILURES.map(row=>[row.code,row.status])));
 const fixed=JSON.parse(readFileSync(new URL('profile-engine/fixtures/u0-v2/wire-vectors.json',import.meta.url),'utf8'));
 for(const row of fixed.media)assert.equal(acceptsU0JsonMedia(row.value),row.accepted,row.value);
 for(const value of [null,'','application/json;','application/json ; other=x','application/json; charset=utf-8;','application/json\n','application/json; charset="UTF-8"x'])assert.equal(acceptsU0JsonMedia(value),false);
 assert.equal(acceptsU0JsonMedia('\tApplication/JSON ; charset = "UTF-8"\t'),true);
});
test('U07 real Request/Response completion, rejection and exact headers',async()=>{
 const f=fixture();const req=request();const response=await f.handler(req);
 assert.equal(response.status,200);assert.equal(await response.text(),'{"kind":"completed","value":{"id":"9007199254740993","verified":true}}');
 assert.equal(response.headers.get('content-length'),'70');assert.equal(response.headers.get('cache-control'),'no-store');assert.equal(f.calls(),1);cleaned(response,req);
 const rejected=await f.handler(request('{"id":"31","verified":false}'));assert.equal(rejected.status,422);assert.equal(await rejected.text(),'{"kind":"rejected","code":"delivery-verification-required"}');assert.equal(inspectU0HttpResponse(rejected)!.outcome,'rejected');
});
test('U07 route, method, media and abort preflight never read a body',async()=>{
 const f=fixture();let reads=0;
 for(const [options,status,code]of [[{url:'http://component.invalid/other',method:'PUT'},404,'route-not-found'],[{method:'PUT'},405,'method-not-allowed'],[{headers:{'content-type':'text/plain'}},415,'unsupported-media-type']] as const){
  const body=stream({pull(){reads++;}}),req=request(body,options),response=await f.handler(req);await error(response,status,code);
  if(status===405)assert.equal(response.headers.get('allow'),'POST');assert.equal(inspectU0HttpResponse(response)!.timer_started,false);assert.equal(req.body!.locked,false);
 }
 const controller=new AbortController();controller.abort();const response=await f.handler(request(stream({pull(){reads++;}}),{signal:controller.signal}));await error(response,400,'request-aborted');assert.equal(reads,0);assert.equal(f.calls(),0);
});
test('U07 query strings are not business input; media variants invoke only after validation',async()=>{
 const f=fixture();const fixed=JSON.parse(readFileSync(new URL('profile-engine/fixtures/u0-v2/wire-vectors.json',import.meta.url),'utf8'));
 for(const row of fixed.media){const response=await f.handler(request(value,{url:'http://component.invalid/confirm-delivery?id=0&verified=false',headers:{'content-type':row.value}}));assert.equal(response.status,row.accepted?200:415);}
 assert.equal(f.calls(),4);
});
test('U07 fixed 34 C03 wire cases run through real body acquisition and codecs',async()=>{
 const fixed=JSON.parse(readFileSync(new URL('profile-engine/fixtures/u0-v2/wire-vectors.json',import.meta.url),'utf8'));
 for(const row of fixed.decoder){
  const f=fixture(),req=request(Buffer.from(row.bytes_hex,'hex')),response=await f.handler(req);
  if(row.expected.kind==='decoded'){assert.equal(response.status,row.expected.value.verified?200:422);assert.equal(f.calls(),1);}
  else {await error(response,400,'invalid-request');assert.equal(f.calls(),0);}
  cleaned(response,req);
 }
});
test('U07 arbitrary UTF-8/token chunk boundaries and exact counted cap',async()=>{
 const f=fixture(contract,2000,46);let offset=0;const raw=bytes('{"verified":true,"id":"18446744073709551615"}');
 const req=request(stream({pull(controller){if(offset===raw.length){controller.close();return;}controller.enqueue(raw.slice(offset,++offset));}}));
 const response=await f.handler(req);assert.equal(response.status,200);assert.equal(inspectU0HttpResponse(response)!.acquired_bytes,45);cleaned(response,req);
 const exact=await f.handler(request('{"id":"18446744073709551615","verified":false}'));assert.equal(exact.status,422);
 const over=await f.handler(request('{"id":"18446744073709551615","verified":false} '));await error(over,413,'request-too-large');
});
test('U07 absent, malformed and false Content-Length cannot bypass counted bytes',async()=>{
 for(const length of [undefined,'1','nonsense','-1','46x']){
  const f=fixture(contract,2000,46);let cancelled=0;const req=request(stream({pull(controller){controller.enqueue(new Uint8Array(47));},cancel(){cancelled++;}}),{headers:{'content-type':'application/json',...(length===undefined?{}:{'content-length':length})}});
  const response=await f.handler(req);await error(response,413,'request-too-large');assert.equal(f.calls(),0);assert.equal(cancelled,1);assert.equal(inspectU0HttpResponse(response)!.cancellation_requested,true);cleaned(response,req);
 }
});
test('U07 syntactically valid excessive advertised length rejects before reading',async()=>{
 const f=fixture(contract,2000,46);let reads=0;
 const req=request(stream({pull(){reads++;}}),{headers:{'content-type':'application/json','content-length':'00000000000000000000000047'}});
 const response=await f.handler(req);await error(response,413,'request-too-large');assert.equal(reads,0);assert.equal(f.calls(),0);cleaned(response,req);
});
test('U07 byte chunks are owned without length getters or coercion; invalid chunks reject',async()=>{
 let getters=0;const raw=bytes(value);Object.defineProperty(raw,'byteLength',{get(){getters++;throw Error('getter');}});
 const f=fixture(),req=request(stream({start(controller){controller.enqueue(raw);controller.close();}}));assert.equal((await f.handler(req)).status,200);assert.equal(getters,0);
 for(const chunk of [{get byteLength(){getters++;return 1;}},'text',new Proxy(bytes(value),{}),new Uint8Array(new SharedArrayBuffer(8))]){
  const bad=request(stream({start(controller){controller.enqueue(chunk as any);controller.close();}}));await error(await fixture().handler(bad),400,'body-read-failed');
 }
 assert.equal(getters,0);
});
test('U07 pre-invocation abort beats coincident overflow and read failure',async()=>{
 for(const failing of [false,true]){
  const controller=new AbortController(),f=fixture(contract,2000,46);
  const req=request(stream({pull(source){if(failing)source.error(Error('private'));else source.enqueue(new Uint8Array(47));controller.abort();}}),{signal:controller.signal});
  const response=await f.handler(req);await error(response,400,'request-aborted');assert.equal(f.calls(),0);cleaned(response,req);
 }
});
test('U07 abort wakes a genuinely pending read, cancels and releases without waiting for cancel completion',async()=>{
 const controller=new AbortController(),f=fixture();let cancelled=0,started!:()=>void;const reading=new Promise<void>(resolve=>{started=resolve;});
 const req=request(stream({pull(){started();return new Promise(()=>{});},cancel(){cancelled++;return new Promise(()=>{});}}),{signal:controller.signal});
 const pending=f.handler(req);await reading;controller.abort();const response=await pending;
 await error(response,400,'request-aborted');assert.equal(cancelled,1);assert.equal(f.calls(),0);cleaned(response,req);
});
test('U07 actual body timeout wakes a pending read and cleans the timer/listener/reader',async()=>{
 const f=fixture(contract,20);let cancelled=0;
 const req=request(stream({pull(){return new Promise(()=>{});},cancel(){cancelled++;}}));const response=await f.handler(req);
 await error(response,408,'body-timeout');assert.equal(cancelled,1);assert.equal(f.calls(),0);cleaned(response,req);
});
test('U07 monotonic deadline handles blocked event loop and gives overflow priority over timeout',async()=>{
 for(const overflowing of [false,true]){
  const f=fixture(contract,10,46);const req=request(stream({pull(controller){Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,30);controller.enqueue(overflowing?new Uint8Array(47):bytes(value));controller.close();}}));
  const response=await f.handler(req);await error(response,overflowing?413:408,overflowing?'request-too-large':'body-timeout');assert.equal(f.calls(),0);cleaned(response,req);
 }
});
test('U07 timeout has priority over a coincident read rejection',async()=>{
 const f=fixture(contract,10),req=request(stream({pull(controller){Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,30);controller.error(Error('private'));}}));
 const response=await f.handler(req);await error(response,408,'body-timeout');assert.equal(f.calls(),0);cleaned(response,req);
});
test('U07 read failure and already locked body are fixed adapter failures with cleanup',async()=>{
 const f=fixture(),req=request(stream({pull(controller){controller.error(Error('private input/stack'));}}));const response=await f.handler(req);await error(response,400,'body-read-failed');cleaned(response,req);
 const locked=request();const reader=locked.body!.getReader();try{const failed=await f.handler(locked);await error(failed,400,'body-read-failed');assert.equal(inspectU0HttpResponse(failed)!.timer_clear_count,1);}finally{reader.releaseLock();}
 assert.equal(f.calls(),0);
});
test('U07 late acquisition abort is checked before any synchronous invocation',async()=>{
 const controller=new AbortController(),f=fixture();let chunked=false;
 const req=request(stream({pull(source){if(!chunked){chunked=true;source.enqueue(bytes(value));}else{source.close();queueMicrotask(()=>controller.abort());}}}),{signal:controller.signal});
 const response=await f.handler(req);await error(response,400,'request-aborted');assert.equal(f.calls(),0);cleaned(response,req);
});
test('U07 cancellation after synchronous invocation never reclassifies its result',async()=>{
 const controller=new AbortController(),f=fixture(input=>{controller.abort();return contract(input);});
 const response=await f.handler(request(value,{signal:controller.signal}));assert.equal(response.status,200);assert.equal(f.calls(),1);assert.equal(inspectU0HttpResponse(response)!.outcome,'completed');
});
test('U07 body timer is cleared before pure invocation and cannot impose a business deadline',async()=>{
 const f=fixture(input=>{Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,40);return contract(input);},20);
 const req=request(),response=await f.handler(req);assert.equal(response.status,200);cleaned(response,req);
});
test('U07 callable/encoder contract defects are contained without private details or fake business branches',async()=>{
 let hooks=0;
 const defects=[()=>{throw Error('private secret');},()=>({kind:'completed',value:{id:1n,verified:false}}),()=>({kind:'completed',get value(){hooks++;throw Error('getter');}}),()=>({kind:'rejected',code:'other-secret'}),()=>Promise.reject(Error('private rejection')),()=>({get then(){hooks++;throw Error('then');}})];
 for(const invoke of defects){const response=await fixture(invoke as any).handler(request());await error(response,500,'adapter-contract-defect');assert.equal(inspectU0HttpResponse(response)!.invoked,true);}
 assert.equal(hooks,0);
});
test('U07 captures actual configuration/domain and concurrent observations remain separate',async()=>{
 const config:U0WireConfiguration={...U0_CONFIG_EXAMPLE},selected={...domain};const handler=owner.create(contract,config,selected);(config as {request_bytes:number}).request_bytes=1;selected.rejection_code='changed';
 const [a,b]=await Promise.all([handler(request()),handler(request('{"id":"0","verified":false}'))]);assert.equal(a.status,200);assert.equal(b.status,422);assert.equal(inspectU0HttpResponse(b)!.code,domain.rejection_code);
 assert.notEqual(inspectU0HttpResponse(a),inspectU0HttpResponse(b));assert.equal(inspectU0HttpResponse(new Response()),null);
 assert.throws(()=>owner.create(contract,{...U0_CONFIG_EXAMPLE,response_bytes:1},domain));
});
test('U07 missing and empty bodies reject without business invocation and clear acquisition resources',async()=>{
 const f=fixture();
 for(const req of [request(null),request('')]){
  const response=await f.handler(req);await error(response,400,'invalid-request');cleaned(response,req);assert.equal(inspectU0HttpResponse(response)!.acquired_bytes,0);
 }
 assert.equal(f.calls(),0);
});
