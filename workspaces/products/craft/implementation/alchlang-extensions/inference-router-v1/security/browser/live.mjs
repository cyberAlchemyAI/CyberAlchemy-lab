import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {buildPublicPolicy} from '../../build-public-policy.mjs';
import {createBrowserInference} from './binding.mjs';
import {launchBrowser} from '../../../../../../../../../auth-foundation/implementation/authentication-https/scripts/browser.mjs';
// Browser-only application interception; actual Keycloak HTTPS/OIDC. Open Questions: PLAN.md.
const af=new URL('../../../../../../../../../auth-foundation/implementation/authentication-https/',import.meta.url),dir=await mkdtemp(join(tmpdir(),'browser-inference-'));let browser;let attempts=0;const checks=[];let stage="build",page;const trace=[];let acceptCallback;const callbackReady=new Promise(r=>acceptCallback=r);
try{
 const generated=await buildPublicPolicy(dir,{protectedService:true});
 const profile=JSON.parse(await readFile(new URL('.runtime/config.json',af),'utf8'));
 const existing=JSON.parse(await readFile(new URL('.runtime/policy.json',af),'utf8'));
 const human=existing.principals.find(p=>p.kind==='human'&&p.enabled);assert.ok(human);
 const policy={revision:1,principals:[{issuer:human.issuer,subject:human.subject,kind:'human',client:profile.browserClient,enabled:true,enrollment_roles:['inference'],memberships:[{tenant:'browser-tenant',enabled:true}],sessions:[]}],roles:[{id:'inference',permissions:[{resource:'inference-catalog',action:'discover',scope:'browser-tenant'},{resource:'balanced',action:'use',scope:'browser-tenant'},{resource:'browser-model',action:'invoke',scope:'browser-tenant'}]}]};
 const policyPath=join(dir,'policy.json');await writeFile(policyPath,JSON.stringify(policy),{mode:0o600});
 const {handler}=await createBrowserInference({...generated,profile,policyPath,binary:fileURLToPath(new URL('../tenant-bridge/target/debug/auth-tenant-bridge',af)),bindings:[{id:'browser-provider',version:'v1',model:'browser-model',remoteModel:'fixture',url:'https://fixture.invalid',secret:'fixture-secret'}],catalogs:{balanced:{tenant_id:'unused',policy_version:'v1',providers:[{binding_id:'browser-provider',binding_version:'v1',model:'browser-model',enabled:true,tenant_allowed:false,task:'text.generate',context_limit:4096,output_limit:1024,streaming:false,rank:1}]}},estimateContext:()=>512,fetchImpl:async()=>{attempts++;return Response.json({answer:'browser inference worked',stop_reason:'stop'});}});
 browser=await launchBrowser();const context=await browser.newContext();
 await context.route(profile.origin+'/**',async route=>{
  try{const original=route.request(),headers=await original.allHeaders();
  const request=new Request(original.url(),{method:original.method(),headers,...(['GET','HEAD'].includes(original.method())?{}:{body:original.postDataBuffer()})});
  const response=await handler(request);trace.push({path:new URL(original.url()).pathname,status:response.status});const output=Object.fromEntries(response.headers);if(response.headers.getSetCookie().length)output['set-cookie']=response.headers.getSetCookie().join('\n');
  if(new URL(original.url()).pathname==='/callback'&&response.status===303){delete output.location;await route.fulfill({status:200,headers:output,body:'Handoff complete'});}
  else await route.fulfill({status:response.status,headers:output,body:await response.text()});
  }catch{trace.push({stage:'application transport error'});await route.abort().catch(()=>{});}
 });
 // Playwright routes do not intercept every cross-origin redirect continuation.
 // Preserve the real issuer response/cookies, then navigate its exact callback as
 // a new browser request so only this context reaches the candidate handler.
 await context.route(profile.issuer+'/login-actions/**',async route=>{
  try{const response=await route.fetch({maxRedirects:0});const location=response.headers().location;
  if(location&&new URL(location).origin===profile.origin&&new URL(location).pathname==='/callback'){
   await route.fulfill({response,status:200,body:'Completing sign-in'});acceptCallback(location);
  }else await route.fulfill({response});}catch{trace.push({stage:"issuer transport error"});await route.abort().catch(()=>{});}
 });
 page=await context.newPage();stage="open app";await page.goto(profile.origin);stage='start login';await page.getByRole('link',{name:'Sign in',exact:true}).click();
 stage='issuer credentials';await page.locator('#username').fill('alice');await page.locator('#password').fill(profile.userPassword);stage='callback';await page.locator('#kc-login').click();let timer;let callback;try{callback=await Promise.race([callbackReady,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('CALLBACK_TIMEOUT')),30000);})]);}finally{clearTimeout(timer);}await page.goto(callback);await page.goto(profile.origin+'/');await page.locator('#app').waitFor({state:'visible'});checks.push('real Keycloak code+PKCE browser login reaches new consumer');
 const session=await page.evaluate(async()=>{const r=await fetch('/session');return {status:r.status,data:await r.json()};});assert.equal(session.status,200);assert.deepEqual(session.data.tenants,['browser-tenant']);assert.ok(!('token' in session.data));checks.push('automatic session enrollment and tenant picker without token exposure');
 const cookies=await context.cookies(profile.origin);const sessionCookie=cookies.find(c=>c.name==='__Host-inference_session');assert.ok(sessionCookie?.secure&&sessionCookie.httpOnly&&sessionCookie.sameSite==='Lax');checks.push('opaque Secure HttpOnly SameSite browser cookie');
 await page.locator('#message').fill('hello');await page.getByRole('button',{name:'Send',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#result').textContent.includes('browser inference worked'));assert.equal(attempts,1);checks.push('browser form invokes generated inference with current Rust permission check');
 const missingCsrf=await page.evaluate(async()=>{const r=await fetch('/v1/inference',{method:'POST',headers:{'content-type':'application/json','x-tenant-id':'browser-tenant'},body:'{}'});return r.status;});assert.equal(missingCsrf,403);assert.equal(attempts,1);checks.push('browser write without CSRF denied before provider');
 policy.roles[0].permissions=policy.roles[0].permissions.filter(p=>p.action!=='invoke');await writeFile(policyPath,JSON.stringify(policy),{mode:0o600});
 const models=await page.evaluate(async()=>{const r=await fetch('/v1/models',{headers:{'x-tenant-id':'browser-tenant'}});return r.json();});assert.deepEqual(models.models,[]);checks.push('current role revocation hides browser discovery without re-login');
 await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#app').hidden);const after=await page.evaluate(async()=>{const r=await fetch('/session');return r.status;});assert.equal(after,401);checks.push('local logout invalidates enrolled session and browser cookie');
 console.log(JSON.stringify({status:'passed-browser-local-candidate',checks,provider_attempts:attempts,transport:{issuer:'real HTTPS Keycloak',application:'Playwright route interception to real in-process gateway; harness drives exact issuer callback navigation',provider:'local response fixture'},authority_effect:'none',claim_ceiling:'No application TLS ingress or running AF app replacement; no issuer-wide logout or renewal claim',open_questions_ref:'PLAN.md#open-questions'},null,2));
}catch(error){console.error('Browser rehearsal failed:',error.code??error.name,'after',checks.length,'checks',JSON.stringify({stage,trace,page:page?new URL(page.url()).pathname:null}));process.exitCode=1;}
finally{await browser?.close();await rm(dir,{recursive:true,force:true});}
