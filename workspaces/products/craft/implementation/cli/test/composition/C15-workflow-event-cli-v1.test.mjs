/** Optional same-source Workflow/Event formal publication through the selected CLI.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync,rmSync} from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {workflowFixture} from './C13-workflow-fixture.mjs';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const cli=path.join(repository,'craft/projects/domainspec-v2/impl/cli');
const entry=path.join(repository,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts');
const run=args=>spawnSync(process.execPath,['--import','tsx',entry,...args],{
 cwd:cli,encoding:'utf8',timeout:900000,maxBuffer:8*1024*1024,
 env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:cli}});

test('C15 selected CLI atomically publishes the same checked Workflow/Event Alloy and TLA join',()=>{
 const root=workflowFixture(),work=path.dirname(root),out=path.join(work,'formal-workflow-event');
 try{
  const args=['formal-export','--model','workflow-event',
   '--source',path.join(root,'business.alch'),'--additional-source',path.join(root,'audit-service.alch'),
   '--profile',path.join(root,'contracts/selected-profile.json'),
   '--external-profile',path.join(root,'contracts/external-profile.json'),
   '--external-write-selection',path.join(root,'contracts/external-write-bindings.json'),
   '--workflow','ReviewDesk.ApprovalFlow',
   ...['ReviewDesk.BeginWorkflowEntry','ReviewDesk.ReserveWorkflowEntry',
    'ReviewDesk.UndoWorkflowEntry','ReviewDesk.CommitRequestApprovalEntry',
    'AuditService.RecordApprovedEntry'].flatMap(value=>['--artifact-entry',value]),
   '--out',out,'--accept-local-review','C15-workflow-event-cli'];
  const result=run(args);
  assert.equal(result.status,0,result.stderr+'\n'+result.stdout);
  const manifest=JSON.parse(readFileSync(path.join(out,'manifest.json'),'utf8'));
  const joined=JSON.parse(readFileSync(path.join(out,'model.json'),'utf8'));
  assert.equal(manifest.language,'alloy+tla+');
  assert.equal(joined.model.workflow.id,'ReviewDesk.ApprovalFlow');
  assert.equal(joined.model.event.target_entry,'AuditService.RecordApprovedEntry');
  assert.equal(manifest.artifact_inventory_sha256,joined.artifact_manifest.inventory_sha256);
  assert.equal(readFileSync(path.join(out,'model.als'),'utf8'),joined.model.alloy);
  assert.equal(readFileSync(path.join(out,'model.tla'),'utf8'),joined.model.tla);
  assert.ok(existsSync(path.join(out,'artifacts/service-inventory.json')));
  assert.deepEqual(manifest.files.filter(file=>/^model\.(als|tla)$/.test(file.path)).map(file=>file.path).sort(),
   ['model.als','model.tla']);
  assert.equal(joined.model.emitted_complete_application,false);
 }finally{rmSync(work,{recursive:true,force:true});}
});
