import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {mkdtemp,readFile,writeFile,rm,chmod} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {buildPublicPolicy} from '../../build-public-policy.mjs';
import {createProtectedServer} from '../host.mjs';
import {createAuthFoundation} from '../auth-foundation.mjs';
import {serviceToken,verifier,configuration,active} from '../../../../../../../../../auth-foundation/implementation/authentication-https/src/identity.mjs';
// Explicit live runner; never included in the offline suite. Open Questions: PLAN.md.
const af=new URL('../../../../../../../../../auth-foundation/implementation/authentication-https/',import.meta.url);
const directory=await mkdtemp(join(tmpdir(),'inference-live-'));await chmod(directory,0o700);
const passed=[];let provider,server;let attempts=0;
const sha=x=>createHash('sha256').update(x).digest('hex');
try{
 const generated=await buildPublicPolicy(directory,{protectedService:true});
 const profile=JSON.parse(await readFile(new URL('.runtime/config.json',af),'utf8'));
 const {access_token:token}=await serviceToken(profile);
 const verified=await verifier(profile)(token);await active(await configuration(profile,true),token,verified);
 assert.equal(verified.azp,'prototype-service');passed.push('live HTTPS token acquisition, JWKS verification and introspection');
 const permission=(resource,action,scope)=>({resource,action,scope});
 const policy={revision:1,principals:[{issuer:verified.iss,subject:verified.sub,kind:'service',client:verified.azp,enabled:true,memberships:['live-a','live-b'].map(tenant=>({tenant,enabled:true})),sessions:[{jti:verified.jti,enabled:true,active_roles:['inference']}]}],roles:[{id:'inference',permissions:['live-a','live-b'].flatMap(t=>[permission('inference-catalog','discover',t),permission('balanced','use',t),permission('live-model','invoke',t),permission('live-model','stream',t)])}]};
 const policyPath=join(directory,'tenant-policy.json');const save=()=>writeFile(policyPath,JSON.stringify(policy),{mode:0o600});await save();
 provider=createServer(async(req,res)=>{let text='';for await(const chunk of req){text+=chunk;if(text.length>65536){res.writeHead(413).end();return;}}attempts++;const value=JSON.parse(text);assert.equal(req.headers.authorization,'Bearer disposable-provider-secret');
  if(value.stream){res.writeHead(200,{'content-type':'text/event-stream'});res.end('event: delta\ndata: {"text":"live fixture"}\n\nevent: completed\ndata: {"stop_reason":"stop"}\n\n');}
  else{res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify({answer:'live fixture',stop_reason:'stop'}));}
 });provider.listen(0,'127.0.0.1');await once(provider,'listening');
 const binding={id:'live-provider',version:'v1',model:'live-model',remoteModel:'fixture',url:'http://127.0.0.1:'+provider.address().port,secret:'disposable-provider-secret'};
 server=createProtectedServer({...generated,security:createAuthFoundation({profile,binary:fileURLToPath(new URL('../tenant-bridge/target/debug/auth-tenant-bridge',af)),policy:policyPath}),bindings:[binding],allowLoopbackFixtures:true,catalogs:{balanced:{tenant_id:'operator',policy_version:'live-v1',providers:[{binding_id:binding.id,binding_version:binding.version,model:binding.model,enabled:true,tenant_allowed:false,task:'text.generate',context_limit:4096,output_limit:1024,streaming:true,rank:1}]}},estimateContext:()=>512});
 server.listen(0,'127.0.0.1');await once(server,'listening');const origin='http://127.0.0.1:'+server.address().port;
 const call=(path,{tenant='live-a',key,stream=false,authenticated=true}={})=>fetch(origin+path,{method:path==='/v1/inference'?'POST':'GET',headers:{...(authenticated?{authorization:'Bearer '+token}:{}),'x-tenant-id':tenant,'content-type':'application/json',...(key?{'idempotency-key':key}:{})},...(path==='/v1/inference'?{body:JSON.stringify({task:'text.generate',input:{messages:[{role:'user',content:'rehearsal'}]},stream})}:{}),signal:AbortSignal.timeout(15000)});
 assert.equal((await call('/healthz',{authenticated:false})).status,200);assert.equal((await call('/v1/models',{authenticated:false})).status,401);passed.push('public health and anonymous discovery denial');
 const models=await call('/v1/models');assert.equal(models.status,200);assert.deepEqual((await models.json()).models.map(x=>x.id),['live-model']);passed.push('authenticated tenant-filtered discovery');
 const caps=await call('/v1/capabilities');assert.equal(caps.status,200);assert.equal((await caps.json()).authentication,'auth-foundation');passed.push('authenticated capabilities');
 assert.equal((await call('/v1/models',{tenant:'not-a-member'})).status,403);passed.push('untrusted tenant selector denied');
 const first=await call('/v1/inference',{key:'same'});assert.equal(first.status,200);const result=await first.json();assert.equal(result.output.text,'live fixture');assert.equal(attempts,1);passed.push('live authenticated JSON through real loopback provider');
 assert.deepEqual(await(await call('/v1/inference',{key:'same'})).json(),result);assert.equal(attempts,1);passed.push('same-principal replay with no second provider attempt');
 const other=await call('/v1/inference',{tenant:'live-b',key:'same'});assert.equal(other.status,200);assert.notEqual((await other.json()).request_id,result.request_id);assert.equal(attempts,2);passed.push('same key isolated across tenants');
 const stream=await call('/v1/inference',{key:'stream',stream:true});assert.equal(stream.status,200);assert.match(await stream.text(),/event: completed/);assert.equal(attempts,3);passed.push('authenticated SSE completion');
 const original=structuredClone(policy.roles[0].permissions);policy.roles[0].permissions=original.filter(x=>x.action!=='invoke');await save();
 const revoked=await call('/v1/inference',{key:'same'});assert.equal(revoked.status,403);assert.equal(attempts,3);assert.deepEqual((await(await call('/v1/models')).json()).models,[]);passed.push('current model grant revocation blocks replay and hides discovery');
 policy.roles[0].permissions=original;policy.principals[0].sessions[0].enabled=false;await save();assert.equal((await call('/v1/inference',{key:'same'})).status,403);assert.equal(attempts,3);passed.push('current operator session revocation blocks replay');
 policy.principals[0].sessions[0].enabled=true;await save();assert.deepEqual(await(await call('/v1/inference',{key:'same'})).json(),result);assert.equal(attempts,3);passed.push('restored disposable session reuses original result');
 const sourcePaths=[new URL('./run.mjs',import.meta.url),new URL('../auth-foundation.mjs',import.meta.url),new URL('../host.mjs',import.meta.url),new URL('src/identity.mjs',af),new URL('../tenant-bridge/src/main.rs',af),new URL('../tenant-bridge/target/debug/auth-tenant-bridge',af)];
 const sources=await Promise.all(sourcePaths.map(async p=>({path:fileURLToPath(p),sha256:sha(await readFile(p))})));
 console.log(JSON.stringify({status:'passed-live-local-candidate',checks:passed,provider_attempts:attempts,sources,issuer:verified.iss,audience:'prototype-api',principal_kind:'service',tls_verification:true,issuer_status:'real per-request introspection',provider:'disposable loopback fixture',claim_ceiling:'Service bearer API path only; no browser handoff, issuer revocation, production deployment or durable session lifecycle claim',authority_effect:'none',open_questions_ref:'PLAN.md#open-questions'},null,2));
}catch(error){console.error('Live rehearsal failed:',error.code??error.name,'after',passed.length,'checks');process.exitCode=1;}
finally{for(const listener of [server,provider])if(listener){listener.closeAllConnections();await new Promise(r=>listener.close(r));}await rm(directory,{recursive:true,force:true});}
