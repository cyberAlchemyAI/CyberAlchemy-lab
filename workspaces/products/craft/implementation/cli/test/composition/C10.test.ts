import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {cpSync,mkdtempSync,mkdirSync,readFileSync,rmSync,symlinkSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {validateExternalGenerationRecipe} from '../../src/generic/external-read-profile.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const wire=(value:unknown)=>new Uint8Array(Buffer.from(JSON.stringify(value)));

test('C10 generated external read maps provider response into the existing protected Operation',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'craft-C10-external-'));
 const authored=path.join(dir,'authored');cpSync(fixture,authored,{recursive:true});
 const oracle=JSON.parse(readFileSync(path.join(authored,'independent-oracle.json'),'utf8'));
 let requests=0,providerMode:'ok'|'unavailable'|'malformed'='ok';
 const peer=createServer((request,response)=>{
  requests++;assert.equal(request.method,'GET');assert.equal(request.url,oracle.provider_target);
  if(providerMode==='unavailable'){response.writeHead(503,{'content-type':'application/json'});response.end('{}');return;}
  response.writeHead(200,{'content-type':'application/json'});response.end(providerMode==='malformed'?'{"slots":true}':JSON.stringify(oracle.provider_response));
 });
 peer.listen(0,'127.0.0.1');await once(peer,'listening');
 const address=peer.address();assert.ok(address&&typeof address!=='string');
 writeFileSync(path.join(authored,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:`http://127.0.0.1:${address.port}`}]})+'\n');
 mkdirSync(path.join(dir,'node_modules/@domainspec-v2'),{recursive:true});symlinkSync(fileURLToPath(new URL('../../',import.meta.url)),path.join(dir,'node_modules/@domainspec-v2/cli'),'dir');
 const source=createGenericCompositionOwner();let sourceHandle:any,generated:any,generatedHandle:any,auth:any,runtime:any;
 try{
  sourceHandle=await source.prepare({sourcePath:path.join(authored,'business.alch'),profilePath:path.join(authored,'contracts/selected-profile.json'),externalProfilePath:path.join(authored,'contracts/external-profile.json')});
  const review=source.review(sourceHandle,'C10 focused integration');source.accept(sourceHandle,{decision_id:'C10-source',owner:'C10 focused integration',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'source-decision.json'));
  const output=path.join(dir,'generated'),manifest:any=source.generate(sourceHandle,{entry:oracle.root_entry,outputDirectory:output});
  assert.equal(manifest.logical.admission_mode,'external-read-entry');
  const graph=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  assert.ok(graph.nodes.some((node:any)=>node.kind==='profiled-safe-get-provider'));
  const [{createGeneratedApplicationOwner},{createGeneratedHttpHandler}]=await Promise.all([import(pathToFileURL(path.join(output,'application.mjs')).href),import(pathToFileURL(path.join(output,'entry-http.mjs')).href)]);
  generated=createGeneratedApplicationOwner();generatedHandle=await generated.prepare();
  const generatedReview=generated.review(generatedHandle,'C10 generated integration');generated.accept(generatedHandle,{decision_id:'C10-generated',owner:'C10 generated integration',outcome:'accepted',reviewed_digest:generatedReview.review_sha256},path.join(dir,'generated-decision.json'));
  auth=await createGenericAuthFixture(generated,generatedHandle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:oracle.subject,evidence:'C10-evidence',session:'C10-session'}],grants:[{subject:oracle.subject,entry:oracle.root_entry},{subject:oracle.subject,entry:oracle.child_entry}]});
  const setup=await prepareGenericFixtureRuntime(generated,generatedHandle,{service:oracle.service,ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});
  runtime=setup.runtime;loadGenericFixture(setup.fixture,wire(JSON.parse(readFileSync(path.join(authored,'fixture-rows.json'),'utf8'))));
  const handler=createGeneratedHttpHandler(runtime),route=manifest.runtime_contract.http.route;
  const invoke=(key:string)=>handler(new Request('http://component.invalid'+route,{method:'POST',headers:{'content-type':'application/json','idempotency-key':key},body:JSON.stringify(oracle.operation_input)}),auth.actor(runtime,oracle.subject,oracle.root_entry));
  const response=await invoke('c10-external-1');
  assert.equal(response.status,200);const result=await response.json();assert.equal(result.ok,true);assert.equal(result.outcome.kind,'Returned');
  assert.equal(result.outcome.value.approved,oracle.expected_http_value.approved);
  assert.equal(result.outcome.value.decisionId,oracle.expected_http_value.id);
  assert.equal(result.outcome.value.total,oracle.expected_http_value.total);
  assert.equal(result.outcome.value.proposal.state,oracle.expected_http_value.state);
  assert.equal(requests,1);
  providerMode='unavailable';const unavailable=await invoke('c10-external-2');assert.equal(unavailable.status,422);const unavailableResult=await unavailable.json();assert.equal(unavailableResult.outcome.kind,'Failed');assert.equal(unavailableResult.outcome.code,'availability-unavailable');
  providerMode='malformed';const malformed=await invoke('c10-external-3');assert.equal(malformed.status,422);const malformedResult=await malformed.json();assert.equal(malformedResult.outcome.kind,'Failed');assert.equal(malformedResult.outcome.code,'availability-malformed');
  assert.equal(requests,3);
  const db=new DatabaseSync(setup.storePath,{readOnly:true});try{assert.equal((db.prepare('SELECT count(*) AS n FROM "_craft_generic_commands_v1"').get() as {n:number}).n,3);}finally{db.close();}
 }finally{
  if(runtime)await runtime.close();if(auth)await auth.close();if(generatedHandle)generated.dispose(generatedHandle);if(sourceHandle)source.dispose(sourceHandle);
  peer.closeAllConnections();await new Promise<void>(resolve=>peer.close(()=>resolve()));rmSync(dir,{recursive:true,force:true});
 }
});

test('C10 rejects a selected external Interface that does not match the declared contract',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'craft-C10-contract-'));cpSync(fixture,dir,{recursive:true});
 try{
  const profilePath=path.join(dir,'contracts/external-profile.json'),profile=JSON.parse(readFileSync(profilePath,'utf8'));
  profile.bindings[0].interface='ReviewDesk.UnknownAvailability';writeFileSync(profilePath,JSON.stringify(profile)+'\n');
  writeFileSync(path.join(dir,'contracts/external-config.json'),JSON.stringify({schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:'availability',origin:'http://127.0.0.1:1'}]})+'\n');
  const source=createGenericCompositionOwner();
  await assert.rejects(()=>source.prepare({sourcePath:path.join(dir,'business.alch'),profilePath:path.join(dir,'contracts/selected-profile.json'),externalProfilePath:profilePath}),(error:any)=>['MissingMapping','InvalidContract'].includes(error?.diagnostics?.[0]?.code));
 }finally{rmSync(dir,{recursive:true,force:true});}
});

test('C10 rejects an external recipe that requests retries',()=>{
 const recipePath=fileURLToPath(new URL('../../profiles/generic-v1/external-read/recipes/http-safe-get-v1.json',import.meta.url));
 const recipe=JSON.parse(readFileSync(recipePath,'utf8'));recipe.limits.max_attempts=2;
 assert.throws(()=>validateExternalGenerationRecipe(recipe),(error:any)=>error?.diagnostics?.[0]?.code==='InvalidContract');
});
