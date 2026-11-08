import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';

const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixture=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C08/fixtures-candidate-002/approval');
const entry='ReviewDesk.CommitRequestApprovalEntry',subject='http-reviewer';
const wire=(value:unknown)=>new Uint8Array(Buffer.from(JSON.stringify(value)));
const sourceOwner=createGenericCompositionOwner();
const accept=(owner:any,handle:any,decision:string)=>{const review=owner.review(handle,'C09 HTTP integration');owner.accept(handle,{decision_id:'C09-http',owner:'C09 HTTP integration',outcome:'accepted',reviewed_digest:review.review_sha256},decision);};
const request=(route:string,key='approval-http-23')=>new Request('http://component.invalid'+route,{method:'POST',headers:{'content-type':'application/json','idempotency-key':key},body:JSON.stringify({id:'23'})});

test('C09 generated injected HTTP entry reaches the original C08 command only after current permission',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'craft-C09-http-'));let source:any,generated:any,generatedHandle:any,auth:any,runtime:any;
 try{
  const packageHome=fileURLToPath(new URL('../../',import.meta.url));
  mkdirSync(path.join(dir,'node_modules/@domainspec-v2'),{recursive:true});
  symlinkSync(packageHome,path.join(dir,'node_modules/@domainspec-v2/cli'),'dir');
  source=await sourceOwner.prepare({sourcePath:path.join(fixture,'business.alch'),profilePath:path.join(fixture,'profile.json')});
  accept(sourceOwner,source,path.join(dir,'source-decision.json'));
  const output=path.join(dir,'generated'),manifest:any=sourceOwner.generate(source,{entry,outputDirectory:output});
  assert.equal(manifest.runtime_contract.http.module,'entry-http.mjs');
  assert.equal(manifest.runtime_contract.http.route,'/entries/ReviewDesk/CommitRequestApprovalEntry');
  assert.ok(manifest.files.some((f:any)=>f.path==='entry-http.mjs'));
  const [{createGeneratedApplicationOwner},{createGeneratedHttpHandler}]=await Promise.all([
   import(pathToFileURL(path.join(output,'application.mjs')).href),
   import(pathToFileURL(path.join(output,'entry-http.mjs')).href),
  ]);
  generated=createGeneratedApplicationOwner();generatedHandle=await generated.prepare();
  accept(generated,generatedHandle,path.join(dir,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:subject,evidence:'http-evidence',session:'http-session'}],grants:[{subject,entry},{subject,entry:'ReviewDesk.ReadStoredRequestEntry'}]});
  const setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:'ReviewDeskService',ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});
  runtime=setup.runtime;loadGenericFixture(setup.fixture,wire(JSON.parse(readFileSync(path.join(fixture,'fixture-rows.json'),'utf8'))));
  const handler=createGeneratedHttpHandler(runtime),route=manifest.runtime_contract.http.route;
  const journalCount=()=>{const db=new DatabaseSync(setup.storePath,{readOnly:true});try{return (db.prepare('SELECT count(*) AS n FROM "_craft_generic_commands_v1"').get() as {n:number}).n;}finally{db.close();}};
  assert.equal(journalCount(),0);
  const anonymous=await handler(request(route));assert.equal(anonymous.status,401);assert.equal((await anonymous.json()).code,'AuthenticationRequired');
  assert.equal(journalCount(),0);
  const invalidKey=await handler(request(route,'x'.repeat(129)),auth.actor(runtime,subject,entry));
  assert.equal(invalidKey.status,400);assert.equal(journalCount(),0);
  const malformed=await handler(new Request('http://component.invalid'+route,{method:'POST',headers:{'content-type':'application/json','idempotency-key':'malformed-1'},body:'{' }),auth.actor(runtime,subject,entry));
  assert.equal(malformed.status,400);assert.equal(journalCount(),0);
  auth.setPermission(subject,entry,false);
  const actor=auth.actor(runtime,subject,entry),denied=await handler(request(route),actor);
  assert.equal(denied.status,403);assert.equal((await denied.json()).code,'PermissionDenied');assert.equal(journalCount(),0);
  auth.setPermission(subject,entry,true);
  const allowed=await handler(request(route),auth.actor(runtime,subject,entry));
  assert.equal(allowed.status,200);const committed=await allowed.json();
  assert.equal(committed.ok,true);assert.equal(committed.observation.kind,'committed');assert.equal(committed.outcome.kind,'Returned');assert.equal(committed.outcome.value.decisionId,'23');assert.equal(journalCount(),1);
  const other=await handler(request('/entries/ReviewDesk/Other'),auth.actor(runtime,subject,entry));assert.equal(other.status,404);assert.equal(journalCount(),1);
 }finally{
  if(runtime)await runtime.close();if(auth)await auth.close();if(generatedHandle)generated.dispose(generatedHandle);
  if(source)sourceOwner.dispose(source);rmSync(dir,{recursive:true,force:true});
 }
});
