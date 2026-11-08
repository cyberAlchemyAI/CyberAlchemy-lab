import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {prepareProfileProject,generateProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Open questions: frozen matrix and fresh installed qualification BA15/18.
const cli=path.resolve(import.meta.dirname,'../..');
for(const profile of ['node-http-entry-local-v2','node-http-shared-ports-v2'])test('independent dispatch domain preserves Boolean guard and extra projected field: '+profile,async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'dispatch-public-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(import.meta.dirname,'fixtures/business-acknowledgement'),root,{recursive:true});const file=path.join(root,'project.json'),p=JSON.parse(readFileSync(file,'utf8'));p.profiles[0]={id:profile,version:'1.0.0',path:path.join(cli,'profiles',profile)};writeFileSync(file,JSON.stringify(p));const oracle=JSON.parse(readFileSync(path.join(root,'oracle.json'),'utf8'));
 const prepared=await prepareProfileProject(file);t.after(()=>disposeProfileProject(prepared));assert.equal(prepared.composition.functions.length,0);const output=path.join(root,'generated');generateProfileProject(prepared,output);
 const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),request=(body:unknown)=>new Request('https://example.invalid/confirmDelivery',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
 const success=await service.handler(request(oracle.happy.body));assert.equal(success.status,200);assert.deepEqual((await success.json()).value,oracle.happy.value);
 let begins=0,commits=0,rollbacks=0;const store={begin:async()=>{begins++;return {read:async()=>{throw Error('unexpected read')},commit:async()=>{commits++;return {status:'committed'}},rollback:async()=>{rollbacks++;}}}};
 const rejected=await service.handler(request(oracle.guard_false.body),{},{applications:{confirmDelivery:{store}}});const failure=await rejected.json();assert.equal(rejected.status,409);assert.equal(failure.status,'not-returned');assert.equal(failure.failure.status,'rejected');assert.equal(commits,oracle.guard_false.success_commits);
 // Existing Operation contract begins before evaluating the guard and rolls back rejection.
 assert.equal(begins,1);assert.equal(rollbacks,1);
 const wrong=await service.handler(request(oracle.wrong_type),{},{applications:{confirmDelivery:{store}}});assert.equal(wrong.status,400);assert.equal(begins,1);
 assert.ok(prepared.composition.applications.every((a:any)=>a.intent.operation_ref==='dispatching:confirm-delivery'));assert.ok(prepared.composition.applications.every((a:any)=>!a.operation_module.includes('commerce')));
});
