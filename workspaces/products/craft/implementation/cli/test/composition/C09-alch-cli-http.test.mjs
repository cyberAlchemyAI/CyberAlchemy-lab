/** Real compiled AlchLang CLI -> emitted protected HTTP application.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,copyFileSync,existsSync,rmSync,realpathSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '@domainspec-v2/cli/generic/testing';
const cli=fileURLToPath(new URL('../../',import.meta.url));
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const source=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C14/three-app-authoring-contract-001/casedesk');
const alch=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/generic-composition-cli.js');
test('AlchLang CLI selects explicit or referenced HTTP profiles and emits a protected API over the same application',async()=>{
 const work=mkdtempSync(path.join(cli,'.c09-cli-http-')),root=path.join(work,'authored');
 let owner,handle,auth,runtime,setupRuntime;
 try{
  mkdirSync(path.join(root,'contracts'),{recursive:true});
  for(const [from,to]of [['business.alch','business.alch'],['selected-profile.json','contracts/selected-profile.json'],['http-profile.json','contracts/http-profile.json']])
   copyFileSync(path.join(source,from),path.join(root,to));
  const base=JSON.parse(readFileSync(path.join(source,'selected-profile.json'),'utf8'));
  writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify({schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:base.limits}}));
  writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(base.transaction_bounds));
  const business=path.join(root,'business.alch'),profile=path.join(root,'contracts/selected-profile.json'),http=path.join(root,'contracts/http-profile.json');
  const invoke=(name,selection,additional=[])=>{
   const output=path.join(work,name),args=[alch,'generate','--source',business,'--profile',selection,...additional,'--entry','CaseDesk.ResolveCaseEntry','--out',output,'--accept-local-review','cli-http'];
   const result=spawnSync(process.execPath,args,{cwd:work,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:cli},encoding:'utf8',timeout:300000,maxBuffer:8*1024*1024});
   writeFileSync(path.join(work,name+'-command.json'),JSON.stringify({args,exit:result.status,stdout:result.stdout,stderr:result.stderr},null,2));
   return {result,output};
  };
  const explicit=invoke('explicit',profile,['--http-profile',http]);
  assert.equal(explicit.result.status,0,explicit.result.stderr);
  const selected=JSON.parse(explicit.result.stdout);
  assert.equal(selected.runtime_contract.profile_schema_version,'craft.generic-http-profile/v1-candidate');
  assert.ok(selected.runtime_contract.http.routes.some(route=>route.id==='CaseDeskHttp.Resolve'));
  const referenced=invoke('referenced',http);
  assert.equal(referenced.result.status,0,referenced.result.stderr);
  assert.equal(JSON.parse(referenced.result.stdout).runtime_contract.http.transport_semantics_sha256,selected.runtime_contract.http.transport_semantics_sha256);
  const double=invoke('double',http,['--http-profile',http]);
  assert.equal(double.result.status,1);assert.match(double.result.stderr,/select one HTTP profile/);assert.equal(existsSync(double.output),false);
  const bad=path.join(root,'contracts/not-http.json');writeFileSync(bad,JSON.stringify(base));
  const wrong=invoke('wrong-overlay',profile,['--http-profile',bad]);
  assert.equal(wrong.result.status,1);assert.match(wrong.result.stderr,/exact HTTP transport profile/);assert.equal(existsSync(wrong.output),false);
  const generated=await import(pathToFileURL(path.join(explicit.output,'application.mjs')).href);
  owner=generated.createGeneratedApplicationOwner();handle=await owner.prepare();
  const review=owner.review(handle,'cli-http-runtime');owner.accept(handle,{decision_id:'cli-http-runtime',owner:'cli-http-runtime',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'runtime-decision.json'));
  auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(work,'auth'),subjects:[{id:'case-owner',evidence:'case-owner-evidence',session:'case-owner-session'}],grants:[{subject:'case-owner',entry:'CaseDesk.ReadCaseEntry'},{subject:'case-owner',entry:'CaseDesk.ResolveCaseEntry'}]});
  const setup=await prepareGenericFixtureRuntime(owner,handle,{service:'CaseDeskService',ownedDirectory:path.join(work,'store'),nativeAuth:auth.nativeAuth});
  setupRuntime=setup.runtime;loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(source,'fixture-rows.json'))));await setupRuntime.close();setupRuntime=undefined;
  runtime=await owner.openRuntime(handle,{service:'CaseDeskService',storePath:setup.storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  const handler=owner.bindHttp(handle,runtime,'CaseDeskHttp.Resolve');
  const request=new Request('http://cases.invalid/api/cases/resolve',{method:'POST',headers:{'content-type':'application/json; charset=utf-8','x-craft-command-key':Buffer.from('cli-http-resolve').toString('base64url')},body:JSON.stringify({caseId:'7',proposed:{caseId:'7',resolutionCode:'42'}})});
  auth.associateRequest(handler,request,'case-owner');
  const response=await handler(request);assert.equal(response.status,200);assert.deepEqual((await response.json()).value,{caseId:'7',resolutionCode:'42'});
 }finally{
  await setupRuntime?.close();await runtime?.close();await auth?.close();if(handle)try{owner.dispose(handle);}catch{}
  assert.ok(realpathSync(work).startsWith(realpathSync(cli)+path.sep+'.c09-cli-http-'));rmSync(work,{recursive:true,force:true});
 }
});

test('AlchLang CLI exports an optional bounded Workflow model with the same checked HTTP profile',async()=>{
 const root=workflowFixture(),work=mkdtempSync(path.join(cli,'.c09-cli-http-'));
 try{
  const existing=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk/contracts/http-profile.json');
  copyFileSync(existing,path.join(root,'contracts/http-profile.json'));
  const sourcePath=path.join(root,'business.alch'),sourceBytes=readFileSync(sourcePath);
  const output=path.join(work,'formal'),args=[alch,'formal-export','--model','tla+','--source',sourcePath,
   '--additional-source',path.join(root,'audit-service.alch'),'--profile',path.join(root,'contracts/selected-profile.json'),
   '--http-profile',path.join(root,'contracts/http-profile.json'),'--external-profile',path.join(root,'contracts/external-profile.json'),
   '--external-write-selection',path.join(root,'contracts/external-write-bindings.json'),'--workflow','ReviewDesk.ApprovalFlow',
   '--out',output,'--accept-local-review','http-formal'];
  const result=spawnSync(process.execPath,args,{cwd:work,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:cli},encoding:'utf8',timeout:300000,maxBuffer:8*1024*1024});
  assert.equal(result.status,0,result.stderr);
  const manifest=JSON.parse(result.stdout);
  assert.equal(manifest.language,'tla+');assert.equal(manifest.authority_effect,'none');
  for(const file of manifest.files){
   const bytes=readFileSync(path.join(output,file.path));
   assert.equal(createHash('sha256').update(bytes).digest('hex'),file.sha256);assert.equal(bytes.length,file.bytes);
  }
  const joined=JSON.parse(readFileSync(path.join(output,'model.json'),'utf8'));
  assert.equal(joined.model.workflow,'ReviewDesk.ApprovalFlow');
  assert.equal(joined.model.qualification,'bounded-control-abstraction-only');
  assert.match(readFileSync(path.join(output,'model.tla'),'utf8'),/MODULE/);
  assert.deepEqual(readFileSync(sourcePath),sourceBytes,'formal export cannot rewrite business requirements or insert claims');
 }finally{
  assert.ok(realpathSync(work).startsWith(realpathSync(cli)+path.sep+'.c09-cli-http-'));
  assert.ok(path.basename(path.dirname(root)).startsWith('craft-c11-v3-plan-'));
  rmSync(work,{recursive:true,force:true});rmSync(path.dirname(root),{recursive:true,force:true});
 }
});
