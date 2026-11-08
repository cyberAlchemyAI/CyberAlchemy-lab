import assert from 'node:assert/strict';
import {readFile,mkdtemp,rm} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {randomBytes} from 'node:crypto';
import {openSqliteState} from '../../../../../../../../../auth-foundation/implementation/inference-browser/state.mjs';
import {createBrowserOAuth} from '../../../../../../../../../auth-foundation/implementation/inference-browser/oauth.mjs';
import {createBrowserGateway} from '../../../../../../../../../auth-foundation/implementation/inference-browser/gateway.mjs';
import {createEnrollment} from '../../../../../../../../../auth-foundation/implementation/inference-browser/enrollment.mjs';
import {launchBrowser} from '../../../../../../../../../auth-foundation/implementation/authentication-https/scripts/browser.mjs';
// Real issuer, browser and SQLite; browser-local application interception. Open Questions: PLAN.md.
const af=new URL('../../../../../../../../../auth-foundation/implementation/authentication-https/',import.meta.url),dir=await mkdtemp(join(tmpdir(),'renewal-live-'));let browser,state,stage='setup',report;const checks=[],trace=[];
try{
 const profile=JSON.parse(await readFile(new URL('.runtime/config.json',af),'utf8')),existing=JSON.parse(await readFile(new URL('.runtime/policy.json',af),'utf8'));
 const human=existing.principals.find(p=>p.kind==='human'&&p.enabled);assert.ok(human);
 const policy={revision:1,principals:[{...human,enrollment_roles:['reader'],memberships:[{tenant:'test-tenant',enabled:true}]}],roles:[{id:'reader',permissions:[]}]};
 const path=join(dir,'state.db'),key=randomBytes(32),oauth=await createBrowserOAuth(profile);let handler,enrollment;
 const start=()=>{state=openSqliteState({path,key});enrollment=createEnrollment({state,readPolicy:async()=>policy,decide:async()=>[true]});handler=createBrowserGateway({origin:profile.origin,state,oauth,enrollment,inference:async()=>Response.json({ok:true})});};start();
 browser=await launchBrowser();const context=await browser.newContext();let callbackResolve;let callbackReady=new Promise(r=>callbackResolve=r);
 await context.route(profile.origin+'/**',async route=>{try{const original=route.request(),response=await handler(new Request(original.url(),{method:original.method(),headers:await original.allHeaders(),...(['GET','HEAD'].includes(original.method())?{}:{body:original.postDataBuffer()})}));trace.push({path:new URL(original.url()).pathname,status:response.status});const headers=Object.fromEntries(response.headers);if(response.headers.getSetCookie().length)headers['set-cookie']=response.headers.getSetCookie().join('\n');if(new URL(original.url()).pathname==='/callback'&&response.status===303){delete headers.location;await route.fulfill({status:200,headers,body:'Complete'});}else await route.fulfill({status:response.status,headers,body:await response.text()});}catch{await route.abort().catch(()=>{});}});
 await context.route(profile.issuer+'/**',async route=>{try{const response=await route.fetch({maxRedirects:0}),location=response.headers().location;trace.push({issuer_path:new URL(route.request().url()).pathname,status:response.status(),callback:Boolean(location&&new URL(location).origin===profile.origin)});if(location&&new URL(location).origin===profile.origin&&new URL(location).pathname==='/callback'){await route.fulfill({response,status:200,body:'Completing authentication'});callbackResolve({url:location,landing:route.request().url()});}else await route.fulfill({response});}catch{await route.abort().catch(()=>{});}});
 const page=await context.newPage();
 const complete=async()=>{let timer;try{const handoff=await Promise.race([callbackReady,new Promise((_,reject)=>timer=setTimeout(()=>reject(Error('CALLBACK_TIMEOUT')),30000))]);await page.waitForURL(handoff.landing);await page.goto(handoff.url);await page.goto(profile.origin);await page.locator('#app').waitFor({state:'visible'});}finally{clearTimeout(timer);}};
 stage='login';await page.goto(profile.origin);await page.getByRole('link',{name:'Sign in',exact:true}).click();await page.locator('#username').fill('alice');await page.locator('#password').fill(profile.userPassword);await page.locator('#kc-login').click();await complete();checks.push('real OIDC login creates a renewable encrypted session');
 const before=[...state.sessions][0][1];assert.ok(before.authentication.issuerSession);assert.equal(before.expires,before.absolute);
 const oldCookie=(await context.cookies(profile.origin)).find(c=>c.name==='__Host-inference_session').value;
 stage='restart';state.close();start();assert.equal(await page.evaluate(async()=> (await fetch('/session')).status),200);checks.push('established renewable session survives reopening SQLite');
 callbackReady=new Promise(r=>callbackResolve=r);stage='silent renewal';await page.getByRole('button',{name:'Continue session',exact:true}).click();await complete();
 const after=[...state.sessions][0][1];assert.notEqual(after.identity.jti,before.identity.jti);assert.deepEqual(after.authentication,before.authentication);assert.equal(after.absolute,before.absolute);assert.equal(after.last,before.last);checks.push('real silent SSO code/PKCE renewal preserves identity and lifetime without credentials');
 const newCookie=(await context.cookies(profile.origin)).find(c=>c.name==='__Host-inference_session').value;assert.notEqual(newCookie,oldCookie);await assert.rejects(enrollment.enroll(before.identity));checks.push('cookie rotation and old token revocation');
 stage='restart renewed';state.close();start();assert.equal(await page.evaluate(async()=> (await fetch('/session')).status),200);await assert.rejects(enrollment.enroll(before.identity));checks.push('renewed session and revocation survive another restart');
 const metadata=await page.evaluate(async()=> (await fetch('/session')).json());assert.ok(!JSON.stringify(metadata).includes(after.token));assert.ok(!('authentication' in metadata));checks.push('session responses expose no token or issuer session binding');
 stage='logout';await page.getByRole('button',{name:'Sign out',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#app').hidden);assert.equal(await page.evaluate(async()=> (await fetch('/session')).status),401);checks.push('logout removes the renewed application session');
 report={status:'passed-local-renewal-rehearsal',checks,transport:{issuer:'real HTTPS Keycloak',application:'browser-local interception with exact callback navigation; no running host replacement',authorization:'fixture permission port; Rust integration covered separately',storage:'encrypted SQLite reopened twice'},authority_effect:'none',open_questions_ref:'PLAN.md#open-questions'};
}catch(error){console.error('Renewal rehearsal failed',error.code??error.name,'at',stage,'after',checks.length,'checks',JSON.stringify(trace));process.exitCode=1;}
finally{await browser?.close();state?.close();await rm(dir,{recursive:true,force:true});}
if(report&&process.exitCode!==1)console.log(JSON.stringify(report,null,2));
