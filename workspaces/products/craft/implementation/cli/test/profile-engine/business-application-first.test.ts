import {createBusinessApplicationFixture} from '../helpers/business-profile.ts';
import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,writeFileSync,rmSync,existsSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import http from 'node:http';
import https from 'node:https';
import childProcess from 'node:child_process';
import net from 'node:net';
import {syncBuiltinESMExports} from 'node:module';
import {prepareProfileProject,planProfileProject,generateProfileProject,verifyProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Open questions: frozen independent domain/matrix and installed qualification BA13–18.
const cli=path.resolve(import.meta.dirname,'../..');
for(const profile of ['node-http-entry-local-v2','node-http-shared-ports-v2'])test('public application-only generation and composed entry isolation: '+profile,async t=>{
 const f=createBusinessApplicationFixture(t,profile,true),prepared=await prepareProfileProject(f.file);t.after(()=>disposeProfileProject(prepared));assert.equal(prepared.lowered,undefined);assert.equal(prepared.composition.functions.length,0);assert.equal(existsSync(path.join(prepared.workspace,'service.alch')),false);
 const plan=planProfileProject(prepared),components=plan.composition.components,apps=components.filter((c:any)=>c.role==='application-operation'),shared=components.filter((c:any)=>c.role==='shared-http-port');assert.equal(apps.length,2);assert.equal(shared.length,profile==='node-http-shared-ports-v2'?1:0);
 for(const app of apps)assert.equal(app.depends_on.length,shared.length);if(shared.length)assert.ok(apps.every((c:any)=>c.depends_on[0]===shared[0].id));
 assert.equal(plan.views.business.application_models.length,2);assert.ok(plan.views.coverage.items.some((i:any)=>i.id.startsWith('application-meaning:receiveNotice#')));assert.ok(plan.views.coverage.items.some((i:any)=>i.id.startsWith('application-source:auditNotice#')));assert.ok(plan.views.coverage.items.filter((i:any)=>i.kind==='formal-claim').every((i:any)=>i.state==='claim-residue'));
 const output=path.join(f.root,'generated'),generated=generateProfileProject(prepared,output);assert.equal(generated.qualification.module_mode,'NodeNext');assert.equal(verifyProfileProject(prepared,output).status,'verified');
 const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),request=(intent:string,id:string)=>new Request('https://example.invalid/'+intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({payload:{id}})});
 const savedFetch=globalThis.fetch,savedHttp=http.createServer,savedHttps=https.createServer,savedSpawn=childProcess.spawn,savedExec=childProcess.execFileSync,savedConnect=net.connect;let effects=0;
 const forbidden=()=>{effects++;throw Error('forbidden real business effect');};globalThis.fetch=forbidden as typeof fetch;http.createServer=forbidden as typeof http.createServer;https.createServer=forbidden as typeof https.createServer;childProcess.spawn=forbidden as typeof childProcess.spawn;childProcess.execFileSync=forbidden as typeof childProcess.execFileSync;net.connect=forbidden as typeof net.connect;syncBuiltinESMExports();
 try{
 for(const [intent,id]of [['receiveNotice','7'],['auditNotice','17']]){const response=await service.handler(request(intent,id));assert.equal(response.status,200);const body=await response.json();assert.equal(body.status,'returned');assert.deepEqual(body.value,{id});assert.equal(body.outcome.status,'committed');}
 const failed=await service.handler(request('receiveNotice','8'),{},{applications:{receiveNotice:null}});assert.equal(failed.status,503);assert.equal((await failed.json()).failure.code,'PROFILE_OPERATION_PORTS_REQUIRED');assert.equal((await service.handler(request('auditNotice','18'),{},{applications:{receiveNotice:null}})).status,200);
 const observed=await service.handler(request('receiveNotice','9'),{},{observe:()=>{throw Error('observer')}});assert.equal(observed.status,200);
 let begins=0;const invalid=await service.handler(request('receiveNotice','invalid'),{},{applications:{receiveNotice:{store:{begin:async()=>{begins++;throw Error('must not begin')}}}}});assert.equal(invalid.status,400);assert.equal(begins,0);
 if(shared.length){assert.ok(existsSync(path.join(output,'runtime/lib/application-http.mjs')));for(const name of ['receiveNotice','auditNotice'])assert.match(readFileSync(path.join(output,'applications/'+name+'/src/profile-entry.ts'),'utf8'),/runtime\/lib\/application-http\.mjs/);}
 else for(const name of ['receiveNotice','auditNotice'])assert.ok(existsSync(path.join(output,'applications/'+name+'/lib/application-http.mjs')));
 const make=(body:string,method='POST',type='application/json')=>new Request('https://example.invalid/receiveNotice',{method,headers:{'content-type':type},body});
 assert.equal((await service.handler(make('{}','PUT'))).status,405);assert.equal((await service.handler(make('{}','POST','text/plain'))).status,415);assert.equal((await service.handler(make('invalid'))).status,400);assert.equal((await service.handler(make('x'.repeat(17000)))).status,413);
 const slow=new Request('https://example.invalid/receiveNotice',{method:'POST',headers:{'content-type':'application/json'},body:new ReadableStream({pull:()=>new Promise(()=>{})}),duplex:'half'} as RequestInit);assert.equal((await service.handler(slow)).status,504);
 const aborted=new AbortController();aborted.abort();assert.equal((await service.handler(request('receiveNotice','7'),{},{signal:aborted.signal})).status,409);assert.equal((await service.handler(request('receiveNotice','7'),{},{cancellation:'required'})).status,409);
 for(const status of ['rejected','indeterminate']){const response=await service.handler(request('receiveNotice','7'),{},{applications:{receiveNotice:{store:{begin:async()=>({read:async()=>{throw Error('unexpected read')},commit:async()=>({status}),rollback:async()=>{if(status==='indeterminate')throw Error('must not roll back uncertainty');}})}}}});const body=await response.json();assert.equal(body.status,'not-returned');assert.deepEqual(body.failure,{status,stage:'commit',code:status==='rejected'?'COMMIT_REJECTED':'COMMIT_INDETERMINATE',continuation:'return-notice-error',cleanupFailed:false});}
 const beginFailure=await service.handler(request('receiveNotice','7'),{},{applications:{receiveNotice:{store:{begin:async()=>{throw Error('controlled begin failure')}}}}});const beginFailed=await beginFailure.json();assert.equal(beginFailed.failure.status,'failed');assert.equal(beginFailed.failure.code,'BEGIN_FAILED');assert.equal(beginFailed.failure.stage,'begin');assert.equal(beginFailed.failure.continuation,'return-notice-error');
 assert.equal(effects,0);
 }finally{globalThis.fetch=savedFetch;http.createServer=savedHttp;https.createServer=savedHttps;childProcess.spawn=savedSpawn;childProcess.execFileSync=savedExec;net.connect=savedConnect;syncBuiltinESMExports();}
});
