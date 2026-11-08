import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync,renameSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {once} from 'node:events';
import {request as httpRequest} from 'node:http';
import {createHash} from 'node:crypto';
import {buildLocalPattern} from './build.mjs';
import {createEngineFixture} from './fixture.mjs';
import {createHttpInvocation} from '../../../implementation/dist/http-invocation-adapter.js';
import {loadOutbound} from '../../../implementation/dist/outbound-composition.js';
import {compileOutboundComposition} from '../../../../../../../../craft/projects/domainspec-v2/impl/cli/dist/typed-backend/outbound-composition.js';
// Generated-host conformance; Open Questions: README.md.
const folder=mkdtempSync(join(tmpdir(),'local-pattern-test-'));let api,bundle;
const baseConfig=JSON.parse(readFileSync(new URL('./configuration.example.json',import.meta.url)));
const listen=async server=>{server.listen(0,'127.0.0.1');await once(server,'listening');return 'http://127.0.0.1:'+server.address().port;};
const close=async server=>{server.closeAllConnections();await new Promise(r=>server.close(r));};
before(async()=>{await buildLocalPattern(join(folder,'original'));bundle=join(folder,'moved');renameSync(join(folder,'original'),bundle);api=await import(pathToFileURL(join(bundle,'index.mjs')).href);});
after(()=>rmSync(folder,{recursive:true,force:true}));
async function scenario(fn,options={}){
 const a=createEngineFixture('A',options),b=createEngineFixture('B');const ua=await listen(a.server),ub=await listen(b.server);
 const config=structuredClone(baseConfig);config.engines[0].url=ua+'/infer';config.engines[1].url=ub+'/infer';
 let service;try{service=api.createServer(config);const root=await listen(service);await fn({root,a,b,config});}finally{if(service)await close(service);await close(a.server);await close(b.server);}
}
const payload=(extra={})=>({task:'text.generate',input:{messages:[{role:'user',content:'hello'}]},...extra});
const send=(root,value=payload(),headers={})=>fetch(root+'/v1/inference',{method:'POST',headers:{'content-type':'application/json',...headers},body:JSON.stringify(value)});
test('relocated standalone bundle has a complete hash manifest and authored provenance',()=>{
 const m=JSON.parse(readFileSync(join(bundle,'manifest.json')));
 for(const [p,h]of Object.entries(m.files))assert.equal(createHash('sha256').update(readFileSync(join(bundle,p))).digest('hex'),h,p);
 assert.equal(m.protocol,'alch-local-text/v1');assert.match(readFileSync(join(bundle,'provider-invocation/source.alch'),'utf8'),/profile outbound-invocation-v2/);
 assert.ok(Object.keys(m.files).some(p=>p.endsWith('source.alch')));
});
test('discovery, deterministic selection, explicit alias and wire mapping use the generated host',async()=>scenario(async({root,a,b})=>{
 const discovery=await(await fetch(root+'/v1/models')).json();assert.match(JSON.stringify(discovery),/local-chat-a/);assert.doesNotMatch(JSON.stringify(discovery),/127\.0\.0\.1|fixture-a/);
 assert.equal((await fetch(root+'/v1/capabilities')).status,200);
 const result=await(await send(root)).json();assert.equal(result.model,'local-chat-a');assert.equal(result.output.text,'A');
 assert.equal(a.calls.length,1);assert.equal(b.calls.length,0);assert.equal(a.calls[0].headers.authorization,undefined);
 assert.deepEqual(a.calls[0].body,{messages:[{role:'user',content:'hello'}],model:'fixture-a',max_tokens:256,stream:false});
 assert.equal((await(await send(root,payload({model:'local-chat-b'}))).json()).output.text,'B');
 assert.equal((await send(root,payload({model:'missing'}))).status,404);
}));
test('changing configuration ranks changes generated selection without native policy edits',async()=>scenario(async({config,b})=>{
 config.engines[1].rank=0;const s=api.createServer(config);const root=await listen(s);
 try{assert.equal((await(await send(root)).json()).output.text,'B');assert.equal(b.calls.length,1);}finally{await close(s);}
}));
test('JSON replay and conflicting keys never dispatch a second attempt',async()=>scenario(async({root,a})=>{
 const h={'idempotency-key':'same'};const first=await(await send(root,payload(),h)).json();
 assert.deepEqual(await(await send(root,payload(),h)).json(),first);
 assert.equal((await send(root,payload({parameters:{max_output_tokens:12}}),h)).status,409);assert.equal(a.calls.length,1);
}));
test('canonical streaming has started/delta/completed and cannot replay',async()=>scenario(async({root,a})=>{
 const h={'idempotency-key':'stream'};const response=await send(root,payload({stream:true}),h);assert.equal(response.status,200);
 const text=await response.text();assert.match(text,/event: started/);assert.match(text,/event: delta/);assert.match(text,/event: completed/);assert.doesNotMatch(text,/event: error/);
 assert.equal((await send(root,payload({stream:true}),h)).status,409);assert.equal(a.calls.length,1);
}));
test('early stream EOF terminates with error without fallback',async()=>scenario(async({root,b})=>{
 const text=await(await send(root,payload({stream:true}))).text();assert.match(text,/event: error/);assert.doesNotMatch(text,/event: completed/);assert.equal(b.calls.length,0);
},{mode:'incomplete'}));
test('invalid provider JSON and redirects fail without another engine attempt',async()=>{
 for(const mode of ['invalid','redirect'])await scenario(async({root,a,b})=>{assert.equal((await send(root)).status,502);assert.equal(a.calls.length,1);assert.equal(b.calls.length,0);},{mode});
});
test('a legitimate local response after five seconds succeeds within the authored v2 budget',async()=>scenario(async({root})=>{
 assert.equal((await send(root)).status,200);
},{waitMs:5100}));
test('tightened deadline cancels and does not fallback',async()=>scenario(async({config,a,b})=>{
 config.timeoutMs=30;const s=api.createServer(config);const root=await listen(s);
 try{assert.equal((await send(root)).status,504);assert.ok(a.calls.length<=1);assert.equal(b.calls.length,0);}finally{await close(s);}
},{waitMs:150}));
test('invalid config, unknown estimates and incompatible context fail before execution',async()=>scenario(async({config,a,b})=>{
 for(const change of [c=>c.protocol='other',c=>c.extra=true,c=>c.timeoutMs=30001,c=>c.contextBound.inputTokens=null,c=>c.engines[0].authentication='other',c=>c.engines[0].secretEnv='SECRET',c=>c.engines[0].url='http://192.0.2.1/infer',c=>c.engines[1].id=c.engines[0].id]){const c=structuredClone(config);change(c);assert.throws(()=>api.createServer(c));}
 config.engines.forEach(e=>e.contextLimit=256);const s=api.createServer(config);const root=await listen(s);
 try{assert.equal((await send(root)).status,503);assert.equal(a.calls.length+b.calls.length,0);}finally{await close(s);}
}));
test('untrusted origins and forwarding headers cannot use the local composition',async()=>scenario(async({root,a})=>{
 for(const headers of [{origin:'https://example.com'},{'x-forwarded-host':'example.com'}])assert.equal((await send(root,payload(),headers)).status,403,JSON.stringify(headers));
 // Fetch normalizes Host; use the actual HTTP wire for this negative witness.
 const status=await new Promise((resolve,reject)=>{const req=httpRequest(root+'/v1/inference',{method:'POST',headers:{host:'example.com','content-type':'application/json'}},res=>{res.resume();resolve(res.statusCode);});req.on('error',reject);req.end(JSON.stringify(payload()));});
 assert.equal(status,403);
 assert.equal(a.calls.length,0);
}));
test('explicit transport policy preserves legacy bearer and rejects malformed/no-auth remote bindings',async()=>{
 const binding={id:'a',version:'v1',model:'model',url:'http://127.0.0.1:1/infer',policy:{scope:'loopback',authentication:'none'}};
 for(const patch of [{url:'https://example.com'},{secret:'unexpected'},{policy:{scope:'https',authentication:'none'}},{policy:{scope:'loopback',authentication:'none',extra:true}}])assert.throws(()=>createHttpInvocation({bindings:[{...binding,...patch}]}));
 let headers;const port=createHttpInvocation({bindings:[{...binding,url:'https://example.com',policy:undefined,secret:'test-secret'}],fetchImpl:async(_url,o)=>{headers=o.headers;return Response.json({ok:true});}});
 const attempt=port.http.sendOnce({id:'a',version:'v1'},{},{deadline:performance.now()+1000,signal:new AbortController().signal});
 const response=await attempt.response;for await(const _ of response.body){}await attempt.settled;assert.equal(headers.authorization,'Bearer test-secret');
});
test('outbound v2 is opt-in, bounded, and leaves legacy v1 validation intact',async()=>{
 const {compiled}=await loadOutbound(new URL('../local-invocation.alch',import.meta.url).pathname);const c=structuredClone(compiled.contract);
 assert.equal(c.schema_version,'domainspec.outbound-composition/v2-candidate');assert.equal(c.limits.deadline_ms,30000);
 assert.throws(()=>compileOutboundComposition({...c,schema_version:'domainspec.outbound-composition/v1-candidate'}),/limit deadline_ms/);
 for(const deadline_ms of [0,300001,Infinity])assert.throws(()=>compileOutboundComposition({...c,limits:{...c.limits,deadline_ms}}));
 assert.doesNotThrow(()=>compileOutboundComposition({...c,schema_version:'domainspec.outbound-composition/v1-candidate',limits:{...c.limits,deadline_ms:5000}}));
});
