import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {once} from 'node:events';
import https from 'node:https';
import {createHttpsIngress} from './server.mjs';
import {operatorRequest,operatorHeaders} from '../../../../../../../../../auth-foundation/implementation/authentication-https/scripts/operator.mjs';
import {buildPublicPolicy} from '../../build-public-policy.mjs';
import {createBrowserInference} from '../browser/binding.mjs';
import {launchBrowser} from '../../../../../../../../../auth-foundation/implementation/authentication-https/scripts/browser.mjs';
// Direct TLS application and actual Keycloak HTTPS/OIDC. Open Questions: PLAN.md.
const af=new URL('../../../../../../../../../auth-foundation/implementation/authentication-https/',import.meta.url),dir=await mkdtemp(join(tmpdir(),'browser-inference-'));let browser,server,profile,clientPath,originalUris,changed=false,report;let attempts=0;const checks=[];let stage='build',page;const trace=[];const origin='https://localhost:14443',callback=origin+'/callback';
try{
 const generated=await buildPublicPolicy(dir,{protectedService:true});
 profile=JSON.parse(await readFile(new URL('.runtime/config.json',af),'utf8'));
 const existing=JSON.parse(await readFile(new URL('.runtime/policy.json',af),'utf8'));
 const human=existing.principals.find(p=>p.kind==='human'&&p.enabled);assert.ok(human);
 const policy={revision:1,principals:[{issuer:human.issuer,subject:human.subject,kind:'human',client:profile.browserClient,enabled:true,enrollment_roles:['inference'],memberships:[{tenant:'browser-tenant',enabled:true}],sessions:[]}],roles:[{id:'inference',permissions:[{resource:'inference-catalog',action:'discover',scope:'browser-tenant'},{resource:'balanced',action:'use',scope:'browser-tenant'},{resource:'browser-model',action:'invoke',scope:'browser-tenant'}]}]};
 const policyPath=join(dir,'policy.json');await writeFile(policyPath,JSON.stringify(policy),{mode:0o600});
 const {handler}=await createBrowserInference({...generated,profile,origin,policyPath,binary:fileURLToPath(new URL('../tenant-bridge/target/debug/auth-tenant-bridge',af)),bindings:[{id:'browser-provider',version:'v1',model:'browser-model',remoteModel:'fixture',url:'https://fixture.invalid',secret:'fixture-secret'}],catalogs:{balanced:{tenant_id:'unused',policy_version:'v1',providers:[{binding_id:'browser-provider',binding_version:'v1',model:'browser-model',enabled:true,tenant_allowed:false,task:'text.generate',context_limit:4096,output_limit:1024,streaming:false,rank:1}]}},estimateContext:()=>512,fetchImpl:async()=>{attempts++;return Response.json({answer:'browser inference worked',stop_reason:'stop'});}});
 const [key,cert,ca]=await Promise.all(['frontend.key','frontend.crt','ca.crt'].map(name=>readFile(new URL('.runtime/tls/'+name,af))));
 server=createHttpsIngress({origin,key,cert,handler});server.listen(14443,'127.0.0.1');await once(server,'listening');
 const probe=headers=>new Promise((resolve,reject)=>{const request=https.request(origin+'/healthz',{ca,servername:'localhost',headers},response=>{response.resume();response.on('end',()=>resolve(response.statusCode));});request.on('error',reject);request.end();});
 assert.equal(await probe({}),200);assert.equal(await probe({Host:'attacker.invalid'}),400);assert.equal(await probe({'x-forwarded-host':'localhost:14443'}),400);checks.push('real TLS health and rejection of wrong Host/forwarding hints');
 const headers=await operatorHeaders(profile);const clients=await operatorRequest('/admin/realms/auth-https/clients?clientId=prototype-browser',{headers});assert.equal(clients.status,200);const list=await clients.json();assert.equal(list.length,1);clientPath='/admin/realms/auth-https/clients/'+encodeURIComponent(list[0].id);
 const current=await operatorRequest(clientPath,{headers});assert.equal(current.status,200);originalUris=(await current.json()).redirectUris;assert.ok(Array.isArray(originalUris)&&!originalUris.includes(callback));
 changed=true;const update=await operatorRequest(clientPath,{method:'PUT',headers,body:JSON.stringify({redirectUris:[...originalUris,callback]})});assert.equal(update.status,204);
 browser=await launchBrowser();const context=await browser.newContext();
 page=await context.newPage();stage="open app";await page.goto(origin);stage='start login';await page.getByRole('link',{name:'Sign in',exact:true}).click();
 stage='issuer credentials';await page.locator('#username').fill('alice');await page.locator('#password').fill(profile.userPassword);stage='callback';await page.locator('#kc-login').click();await page.waitForURL(origin+'/');await page.locator('#app').waitFor({state:'visible'});checks.push('real Keycloak code+PKCE browser login reaches new consumer');
 const session=await page.evaluate(async()=>{const r=await fetch('/session');return {status:r.status,data:await r.json()};});assert.equal(session.status,200);assert.deepEqual(session.data.tenants,['browser-tenant']);assert.ok(!('token' in session.data));checks.push('automatic session enrollment and tenant picker without token exposure');
 const cookies=await context.cookies(origin);const sessionCookie=cookies.find(c=>c.name==='__Host-inference_session');assert.ok(sessionCookie?.secure&&sessionCookie.httpOnly&&sessionCookie.sameSite==='Lax');checks.push('opaque Secure HttpOnly SameSite browser cookie');
 await page.locator('#message').fill('hello');await page.getByRole('button',{name:'Send',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#result').textContent.includes('browser inference worked'));assert.equal(attempts,1);checks.push('browser form invokes generated inference with current Rust permission check');
 const missingCsrf=await page.evaluate(async()=>{const r=await fetch('/v1/inference',{method:'POST',headers:{'content-type':'application/json','x-tenant-id':'browser-tenant'},body:'{}'});return r.status;});assert.equal(missingCsrf,403);assert.equal(attempts,1);checks.push('browser write without CSRF denied before provider');
 policy.roles[0].permissions=policy.roles[0].permissions.filter(p=>p.action!=='invoke');await writeFile(policyPath,JSON.stringify(policy),{mode:0o600});
 const models=await page.evaluate(async()=>{const r=await fetch('/v1/models',{headers:{'x-tenant-id':'browser-tenant'}});return r.json();});assert.deepEqual(models.models,[]);checks.push('current role revocation hides browser discovery without re-login');
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#app').hidden);const after=await page.evaluate(async()=>{const r=await fetch('/session');return r.status;});assert.equal(after,401);checks.push('local logout invalidates enrolled session and browser cookie');
 report={status:'passed-https-ingress-local-candidate',checks,provider_attempts:attempts,transport:{issuer:'real HTTPS Keycloak',application:'real HTTPS listener; no request interception or callback navigation shim',provider:'local response fixture'},authority_effect:'none',claim_ceiling:'Local TLS/browser candidate; no production deployment, issuer-wide logout or renewal claim',open_questions_ref:'PLAN.md#open-questions'};
}catch(error){console.error('Browser rehearsal failed:',error.code??error.name,'after',checks.length,'checks',JSON.stringify({stage,trace,page:page?new URL(page.url()).pathname:null}));process.exitCode=1;}
finally{
 await browser?.close();if(server){server.closeAllConnections();await new Promise(r=>server.close(r));}
 if(changed){try{const headers=await operatorHeaders(profile);const read=await operatorRequest(clientPath,{headers});assert.equal(read.status,200);const current=(await read.json()).redirectUris;const restored=current.filter(uri=>uri!==callback);const write=await operatorRequest(clientPath,{method:'PUT',headers,body:JSON.stringify({redirectUris:restored})});assert.equal(write.status,204);const check=await operatorRequest(clientPath,{headers});assert.equal(check.status,200);assert.deepEqual((await check.json()).redirectUris,originalUris);if(report)report.callback_registration='temporary URI removed; original list verified';}catch{console.error('CALLBACK_RESTORATION_FAILED');process.exitCode=1;}}
 await rm(dir,{recursive:true,force:true});
}
if(report&&process.exitCode!==1)console.log(JSON.stringify(report,null,2));
