import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {once} from 'node:events';
import {generateKeyPair,SignJWT} from '../../../../../../../../auth-foundation/implementation/authentication-https/node_modules/jose/dist/webapi/index.js';
import {verifier} from '../../../../../../../../auth-foundation/implementation/authentication-https/src/identity.mjs';
import {createTenantSecurityPort,createTenantAuthorizer} from './auth-foundation.mjs';
import {createProtectedHandler,createProtectedServer} from './host.mjs';
import {buildPublicPolicy} from '../build-public-policy.mjs';
import {loadServiceRoutes} from '../../../implementation/dist/service-routes.js';
const dir=mkdtempSync(join(tmpdir(),'isb09-security-'));
const issuer='https://localhost:18443/realms/auth-https';let keys,handlers;
const binary=fileURLToPath(new URL('../../../../../../../../auth-foundation/implementation/tenant-bridge/target/debug/auth-tenant-bridge',import.meta.url));
const now=()=>Math.floor(Date.now()/1000);
const claims=(name='alice',extra={})=>({iss:issuer,sub:name,aud:'prototype-api',azp:'prototype-browser',typ:'Bearer',iat:now(),exp:now()+300,jti:name+'-session',...extra});
const sign=(payload,key=keys.privateKey)=>new SignJWT(payload).setProtectedHeader({alg:'RS256'}).sign(key);
const perm=(resource,action,scope='t1')=>({resource,action,scope});
const principal=(name,kind='human')=>({issuer,subject:name,kind,client:kind==='human'?'prototype-browser':'prototype-service',enabled:true,memberships:[{tenant:'t1',enabled:true},{tenant:'t2',enabled:true}],sessions:[{jti:name+'-session',enabled:true,active_roles:['user']}]});
const policy=()=>({revision:1,principals:[principal('alice'),principal('bob'),principal('alice','service')],roles:[{id:'user',permissions:['t1','t2'].flatMap(t=>[perm('inference-catalog','discover',t),perm('balanced','use',t),perm('fixture-a','invoke',t),perm('fixture-a','stream',t),perm('fixture-b','invoke',t)])}]});
const row=(id,rank)=>({binding_id:id,binding_version:'v1',model:'fixture-'+id,enabled:true,tenant_allowed:false,task:'text.generate',context_limit:4096,output_limit:1024,streaming:true,rank});
before(async()=>{keys=await generateKeyPair('RS256');handlers=await buildPublicPolicy(dir,{protectedService:true});});
after(()=>rmSync(dir,{recursive:true,force:true}));
function fixture(extra={}){
 const path=join(dir,'policy-'+crypto.randomUUID()+'.json');let current=policy(),active=true,calls=0,checkCount=0;
 const save=()=>writeFileSync(path,JSON.stringify(current));save();
 const auth=createTenantAuthorizer({binary,policy:path});
 const security=createTenantSecurityPort({verifyToken:verifier({issuer},keys.publicKey),assertActive:async()=>{if(!active)throw Error('inactive fixture');},authorize:async(...args)=>{checkCount++;extra.beforeCheck?.(checkCount,current,save);return auth(...args);}});
 const config={...handlers,security,token:'internal-fixture',bindings:['a','b'].map(id=>({id,version:'v1',model:'fixture-'+id,remoteModel:'deployment-'+id,url:'https://provider.invalid/'+id,secret:'private-'+id})),catalogs:{balanced:{tenant_id:'ignored',policy_version:'v1',providers:[row('a',1),row('b',2)]}},estimateContext:()=>512,fetchImpl:async(_url,options)=>{calls++;const request=JSON.parse(options.body);if(request.stream)return new Response('event: delta\ndata: {"text":"hello"}\n\nevent: completed\ndata: {"stop_reason":"stop"}\n\n',{headers:{'content-type':'text/event-stream'}});return Response.json({answer:'private result',stop_reason:'stop'});},...extra.config};
 const handle=createProtectedHandler(config);
 return {handle,config,security,path,get policy(){return current;},save,get calls(){return calls;},revoke(){active=false;}};
}
async function request(path='/v1/inference',{name='alice',tenant='t1',token,body,headers={},...rest}={}){
 token??=await sign(claims(name));const h={authorization:'Bearer '+token,'x-tenant-id':tenant,...headers};
 if(path==='/v1/inference'){h['content-type']='application/json';return new Request('http://localhost'+path,{method:'POST',headers:h,body:JSON.stringify(body??{task:'text.generate',input:{messages:[{role:'user',content:'hello'}]}}),...rest});}
 return new Request('http://localhost'+path,{headers:h,...rest});
}
test('protected assembly requires explicit security binding, and anonymous health stays public',async()=>{
 const f=fixture();
 assert.throws(()=>handlers.serviceFactory({contexts:{models:{providers:[]},capabilities:{providers:[],strategies:[],retention_ms:60000}},operations:{ExecuteInference:async()=>{}}}),/SERVICE_SECURITY_BINDING/);
 assert.equal((await f.handle(new Request('http://localhost/healthz'))).status,200);
 for(const path of ['/v1/models','/v1/capabilities','/v1/inference'])assert.equal((await f.handle(new Request('http://localhost'+path,{method:path.endsWith('inference')?'POST':'GET'}))).status,401);
 assert.equal(f.calls,0);
});
test('real signed bearer identity rejects hostile signatures, issuer, audience, token kind and expiry',async()=>{
 const f=fixture(),other=await generateKeyPair('RS256');
 for(const token of [await sign(claims(),other.privateKey),await sign(claims('alice',{iss:'https://other.invalid'})),await sign(claims('alice',{aud:'other'})),await sign(claims('alice',{typ:'ID'})),await sign(claims('alice',{exp:now()-1})),await sign(claims('alice',{azp:'other'})),'malformed'])assert.equal((await f.handle(await request('/v1/models',{token}))).status,401);
 f.revoke();assert.equal((await f.handle(await request('/v1/models'))).status,401);assert.equal(f.calls,0);
});
test('tenant selector is not authority; missing, duplicate, disabled membership and unknown identity deny',async()=>{
 const f=fixture();
 for(const tenant of ['','t3','t1,t2'])assert.equal((await f.handle(await request('/v1/models',{tenant}))).status,403);
 assert.equal((await f.handle(await request('/v1/models',{name:'unknown'}))).status,403);
 f.policy.principals[0].memberships[0].enabled=false;f.save();assert.equal((await f.handle(await request('/v1/models'))).status,403);
 f.policy.principals[0].memberships[0].enabled=true;f.policy.principals[0].memberships.push({tenant:'t1',enabled:true});f.save();assert.equal((await f.handle(await request('/v1/models'))).status,403);
});
test('membership alone grants nothing; inactive sessions, inactive roles and wrong exact scope deny',async()=>{
 for(const mutate of [p=>p.roles[0].permissions=[],p=>p.principals[0].sessions[0].enabled=false,p=>p.principals[0].sessions[0].active_roles=[],p=>p.roles[0].permissions=p.roles[0].permissions.map(x=>({...x,scope:'other'})),p=>p.principals[0].enabled=false,p=>p.revision=0,p=>p.principals.push(structuredClone(p.principals[0]))]){
  const f=fixture();mutate(f.policy);f.save();assert.equal((await f.handle(await request('/v1/models'))).status,403);assert.equal(f.calls,0);
 }
});
test('discovery filters aliases, strategies and streaming by current grants without leaking private bindings',async()=>{
 const f=fixture();f.policy.roles[0].permissions=f.policy.roles[0].permissions.filter(x=>x.resource!=='fixture-b'&&x.action!=='stream');f.save();
 const models=await(await f.handle(await request('/v1/models'))).json();assert.deepEqual(models.models.map(m=>m.id),['fixture-a']);assert.ok(!JSON.stringify(models).includes('private-'));assert.equal(models.models[0].streaming,false);
 const caps=await(await f.handle(await request('/v1/capabilities'))).json();assert.equal(caps.authentication,'auth-foundation');assert.equal(caps.scope,'tenant-principal');assert.equal(caps.streaming,false);
 f.policy.roles[0].permissions=f.policy.roles[0].permissions.filter(x=>x.action!=='use');f.save();assert.deepEqual((await(await f.handle(await request('/v1/models'))).json()).models,[]);assert.deepEqual((await(await f.handle(await request('/v1/capabilities'))).json()).routing_strategies,[]);
});
test('automatic selection uses authorized aliases; forbidden explicit alias/stream never invokes a provider',async()=>{
 const f=fixture();f.policy.roles[0].permissions=f.policy.roles[0].permissions.filter(x=>x.resource!=='fixture-a');f.save();
 const response=await f.handle(await request());assert.equal(response.status,200);assert.equal((await response.json()).model,'fixture-b');assert.equal(f.calls,1);
 const body={task:'text.generate',input:{messages:[{role:'user',content:'hello'}]},model:'fixture-a'};
 assert.equal((await f.handle(await request('/v1/inference',{body}))).status,403);
 body.model='fixture-b';body.stream=true;assert.equal((await f.handle(await request('/v1/inference',{body}))).status,403);assert.equal(f.calls,1);
});
test('revocation after admission is checked again immediately before the provider attempt',async()=>{
 const f=fixture({beforeCheck:(n,p,save)=>{if(n===2){p.roles[0].permissions=p.roles[0].permissions.filter(x=>x.action!=='invoke');save();}}});
 assert.equal((await f.handle(await request())).status,403);assert.equal(f.calls,0);
});
test('same tenant/principal/key replays while other tenants, subjects and kinds execute separately',async()=>{
 const f=fixture();const headers={'idempotency-key':'same-key'};
 const first=await(await f.handle(await request('/v1/inference',{headers}))).json();
 const repeat=await(await f.handle(await request('/v1/inference',{headers}))).json();assert.deepEqual(repeat,first);assert.equal(f.calls,1);
 for(const change of [{tenant:'t2'},{name:'bob'},{token:await sign(claims('alice',{azp:'prototype-service'}))}]){const r=await f.handle(await request('/v1/inference',{headers,...change}));assert.equal(r.status,200);assert.notEqual((await r.json()).request_id,first.request_id);}
 assert.equal(f.calls,4);
});
test('replay checks saved model rather than rerouting to a newly allowed model',async()=>{
 const f=fixture(),headers={'idempotency-key':'replay-key'};
 assert.equal((await f.handle(await request('/v1/inference',{headers}))).status,200);
 f.policy.roles[0].permissions=f.policy.roles[0].permissions.filter(x=>x.resource!=='fixture-a');f.save();
 const r=await f.handle(await request('/v1/inference',{headers}));assert.equal(r.status,403);assert.deepEqual(await r.json(),{error:{code:'FORBIDDEN'}});assert.equal(f.calls,1);
});
test('authorized SSE works and streams remain non-replayable',async()=>{
 const f=fixture(),headers={'idempotency-key':'stream-key'},body={task:'text.generate',input:{messages:[{role:'user',content:'hello'}]},stream:true};
 const r=await f.handle(await request('/v1/inference',{headers,body}));assert.equal(r.status,200);assert.match(await r.text(),/event: completed/);
 assert.equal((await f.handle(await request('/v1/inference',{headers,body}))).status,409);assert.equal(f.calls,1);
});
test('malformed or missing policy denies and security errors never expose policy/token/secret',async()=>{
 const f=fixture();writeFileSync(f.path,'{private-policy');const r=await f.handle(await request());assert.equal(r.status,403);assert.deepEqual(await r.json(),{error:{code:'FORBIDDEN'}});assert.equal(f.calls,0);
 rmSync(f.path);assert.equal((await f.handle(await request('/v1/models'))).status,403);
});
test('real HTTP adapter carries bearer and tenant selectors to the generated protected service',async()=>{
 const f=fixture(),server=createProtectedServer(f.config);server.listen(0,'127.0.0.1');await once(server,'listening');
 try{const url='http://127.0.0.1:'+server.address().port;assert.equal((await fetch(url+'/v1/models')).status,401);const r=await fetch(url+'/v1/models',{headers:{authorization:'Bearer '+await sign(claims()),'x-tenant-id':'t1'}});assert.equal(r.status,200);assert.equal((await r.json()).models.length,2);}finally{server.closeAllConnections();await new Promise(r=>server.close(r));}
});

test('a session or grant revoked after saving a result cannot use replay',async()=>{
 for(const mutate of [p=>p.principals[0].sessions[0].enabled=false,p=>p.principals[0].memberships[0].enabled=false,p=>p.roles[0].permissions=p.roles[0].permissions.filter(x=>x.action!=='use')]){
  const f=fixture(),headers={'idempotency-key':'revoke-key'};assert.equal((await f.handle(await request('/v1/inference',{headers}))).status,200);
  mutate(f.policy);f.save();assert.equal((await f.handle(await request('/v1/inference',{headers}))).status,403);assert.equal(f.calls,1);
 }
});
test('custody identity is stable across sessions and distinct across issuer, tenant, subject and kind',()=>{
 const f=fixture(),c={tenant:'t1',identity:{issuer,subject:'alice',kind:'human',jti:'old'}};
 assert.equal(f.security.scope(c),f.security.scope({...c,identity:{...c.identity,jti:'new'}}));
 for(const changed of [{...c,tenant:'t2'},...Object.entries({issuer:'https://other.invalid',subject:'bob',kind:'service'}).map(([k,v])=>({...c,identity:{...c.identity,[k]:v}}))])assert.notEqual(f.security.scope(c),f.security.scope(changed));
});
test('cancelled requests cannot dispatch, and security contracts cannot omit route access',async()=>{
 const f=fixture(),c=new AbortController();c.abort();assert.equal((await f.handle(await request('/v1/inference',{signal:c.signal}))).status,499);assert.equal(f.calls,0);
 const source=fileURLToPath(new URL('../protected-service.alch',import.meta.url));assert.equal(loadServiceRoutes(source).plan.routes.filter(x=>x.access==='public').length,1);
});
