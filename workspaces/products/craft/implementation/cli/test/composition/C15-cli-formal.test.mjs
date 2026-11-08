import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync,existsSync,readdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {workflowFixture} from './C13-workflow-fixture.mjs';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const cli=path.join(repository,'craft/projects/domainspec-v2/impl/cli');
const entry=path.join(repository,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts');
const c05=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05');
const run=(args,timeout=600000)=>spawnSync(process.execPath,['--import','tsx',entry,...args],{cwd:cli,encoding:'utf8',timeout,maxBuffer:8*1024*1024,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:cli}});

test('C15 CLI exports optional SMT-LIB from accepted Rule and generation still needs no claim or solver',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'craft-c15-cli-smt-'));
 try{
  mkdirSync(path.join(root,'contracts'));
  const source=path.join(root,'business.alch'),profile=path.join(root,'profile.json'),out=path.join(root,'formal'),generated=path.join(root,'generated');
  writeFileSync(source,'module Logic version 1\nvalue-object Request:\n  verified Bool\n  flagged Bool\nrule IsVerified:\n  input request Request\n  expression request.verified and not request.flagged\n');
  writeFileSync(profile,readFileSync(path.join(c05,'profile.json')));
  writeFileSync(path.join(root,'contracts/bounds.json'),readFileSync(path.join(c05,'bounds.json')));
  writeFileSync(out+'.decision.json','preexisting unrelated decision\n');
  const exported=run(['formal-export','--model','smtlib2','--source',source,'--profile',profile,'--rule','Logic.IsVerified','--out',out,'--accept-local-review','C15-cli-smt']);
  assert.equal(exported.status,0,exported.stderr+'\n'+exported.stdout);
  const manifest=JSON.parse(readFileSync(path.join(out,'manifest.json'),'utf8'));
  const joined=JSON.parse(readFileSync(path.join(out,'model.json'),'utf8'));
  assert.equal(manifest.language,'smtlib2');assert.equal(manifest.profile_sha256,joined.profile.sha256);
  assert.equal(joined.profile_binding,'original-selected-profile-bound');
  assert.equal(joined.model.source_node,'Logic.IsVerified');
  assert.match(readFileSync(path.join(out,'model.smt2'),'utf8'),/\(define-fun Evaluate/);
  assert.equal(joined.model.observations.length,4);
  assert.ok(existsSync(path.join(out,'decision.json')));
  assert.equal(readFileSync(out+'.decision.json','utf8'),'preexisting unrelated decision\n');
  const firstManifest=readFileSync(path.join(out,'manifest.json'),'utf8');
  const collision=run(['formal-export','--model','smtlib2','--source',source,'--profile',profile,'--rule','Logic.IsVerified','--out',out,'--accept-local-review','C15-cli-smt']);
  assert.notEqual(collision.status,0);assert.match(collision.stderr,/GENERIC_FORMAL_OUTPUT_EXISTS/);
  assert.equal(readFileSync(path.join(out,'manifest.json'),'utf8'),firstManifest);
  assert.equal(readdirSync(root).filter(name=>name.startsWith('.alch-formal-')).length,0);
  const ordinary=run(['generate','--source',source,'--profile',profile,'--rule','Logic.IsVerified','--out',generated,'--accept-local-review','C15-cli-generate']);
  assert.equal(ordinary.status,0,ordinary.stderr+'\n'+ordinary.stdout);
  assert.ok(existsSync(path.join(generated,'rule.mjs')));
  const wrong=run(['formal-export','--model','tla+','--source',source,'--profile',profile,'--workflow','Logic.Flow','--out',path.join(root,'wrong'),'--accept-local-review','C15-cli-wrong']);
  assert.notEqual(wrong.status,0);assert.match(wrong.stderr,/UnsupportedCapability/);
  const pureExternal=run(['generate','--source',source,'--profile',profile,'--external-profile',path.join(root,'external-profile.json'),'--rule','Logic.IsVerified','--out',path.join(root,'wrong-external'),'--accept-local-review','C15-cli-wrong']);
  assert.notEqual(pureExternal.status,0);assert.match(pureExternal.stderr,/UnsupportedCapability/);
 }finally{rmSync(root,{recursive:true,force:true});}
});

test('C15 ordinary generate admits Core-checked Event and external source syntax',()=>{
 const root=workflowFixture(),work=path.dirname(root);
 try{
  const output=path.join(work,'generated-event-entry');
  const generated=run(['generate','--source',path.join(root,'business.alch'),
   '--additional-source',path.join(root,'audit-service.alch'),
   '--profile',path.join(root,'contracts/selected-profile.json'),
   '--external-profile',path.join(root,'contracts/external-profile.json'),
   '--external-write-selection',path.join(root,'contracts/external-write-bindings.json'),
   '--entry','ReviewDesk.BeginWorkflowEntry','--out',output,'--accept-local-review','C15-cli-event'],900000);
  assert.equal(generated.status,0,generated.stderr+'\n'+generated.stdout);
  const manifest=JSON.parse(readFileSync(path.join(output,'manifest.json'),'utf8'));
  assert.equal(manifest.entry,'ReviewDesk.BeginWorkflowEntry');
  assert.ok(existsSync(path.join(output,'application.mjs')));
  assert.ok(existsSync(path.join(output,'business-system-bridge.json')));
 }finally{rmSync(work,{recursive:true,force:true});}
});

test('C15 CLI exports TLA+ and Alloy from original Event Workflow and emitted service artifacts',()=>{
 const root=workflowFixture(),work=path.dirname(root);
 try{
  const common=['--source',path.join(root,'business.alch'),'--additional-source',path.join(root,'audit-service.alch'),
   '--profile',path.join(root,'contracts/selected-profile.json'),'--external-profile',path.join(root,'contracts/external-profile.json'),
   '--external-write-selection',path.join(root,'contracts/external-write-bindings.json')];
  const tlaOut=path.join(work,'formal-tla');
  const tla=run(['formal-export','--model','tla+',...common,'--workflow','ReviewDesk.ApprovalFlow','--out',tlaOut,'--accept-local-review','C15-cli-tla']);
  assert.equal(tla.status,0,tla.stderr+'\n'+tla.stdout);
  const tlaJoined=JSON.parse(readFileSync(path.join(tlaOut,'model.json'),'utf8'));
  assert.equal(tlaJoined.model.workflow,'ReviewDesk.ApprovalFlow');
  assert.match(readFileSync(path.join(tlaOut,'model.tla'),'utf8'),/MODULE GenericWorkflowJournal/);
  assert.equal(JSON.parse(readFileSync(path.join(tlaOut,'manifest.json'),'utf8')).profile_sha256,tlaJoined.model.profile_sha256);
  const alloyOut=path.join(work,'formal-alloy');
  const alloy=run(['formal-export','--model','alloy',...common,
   '--artifact-entry','ReviewDesk.BeginWorkflowEntry','--artifact-entry','AuditService.RecordApprovedEntry',
   '--out',alloyOut,'--accept-local-review','C15-cli-alloy'],900000);
  assert.equal(alloy.status,0,alloy.stderr+'\n'+alloy.stdout);
  const alloyJoined=JSON.parse(readFileSync(path.join(alloyOut,'model.json'),'utf8'));
  const manifest=JSON.parse(readFileSync(path.join(alloyOut,'manifest.json'),'utf8'));
  assert.equal(alloyJoined.model.language,'alloy');
  assert.equal(manifest.artifact_inventory_sha256,alloyJoined.artifact_manifest.inventory_sha256);
  assert.equal(alloyJoined.model.inventory_sha256,alloyJoined.artifact_manifest.inventory_sha256);
  assert.ok(existsSync(path.join(alloyOut,'artifacts/service-inventory.json')));
  assert.match(readFileSync(path.join(alloyOut,'model.als'),'utf8'),/fact ExactEmittedStructure/);
 }finally{rmSync(work,{recursive:true,force:true});}
});
