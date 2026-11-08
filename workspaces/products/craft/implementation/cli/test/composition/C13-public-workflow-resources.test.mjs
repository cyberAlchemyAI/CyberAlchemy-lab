/** Public journal lifecycle and no-authority boundaries, with genuine SDK
 * owners/runtimes. No business/provider callback or listener is supplied.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,renameSync,unlinkSync,linkSync,symlinkSync,existsSync,rmSync,realpathSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {DatabaseSync} from 'node:sqlite';
import {createGenericCompositionOwner} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture} from '@domainspec-v2/cli/generic/testing';
import {workflowFixture} from './C13-workflow-fixture.mjs';
const wire=value=>Buffer.from(JSON.stringify(value));
const code=error=>error?.diagnostics?.[0]?.code;
test('C13 public Workflow derives its journal binding and rejects foreign, replaced or malformed resources before progress',async()=>{
 const root=workflowFixture(),work=mkdtempSync(path.join(tmpdir(),'craft-public-workflow-')),owner=createGenericCompositionOwner();
 let handle,auth,producer,receiver,driver;
 try{
  handle=await owner.prepare({sourcePath:path.join(root,'business.alch'),additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=owner.review(handle,'public-workflow');
  owner.accept(handle,{decision_id:'public-workflow',owner:'public-workflow',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'decision.json'));
  auth=await createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(work,'auth'),
   subjects:[{id:'unprivileged',evidence:'unprivileged-evidence',session:'unprivileged-session'}],grants:[]});
  producer=await owner.openRuntime(handle,{service:'ReviewDeskService',storePath:path.join(work,'producer.sqlite'),mode:'create',nativeAuth:auth.nativeAuth});
  receiver=await owner.openRuntime(handle,{service:'AuditService',storePath:path.join(work,'receiver.sqlite'),mode:'create',nativeAuth:auth.nativeAuth});
  const directory=path.join(work,'journal'),options={runtime:producer,receiver,actors:new Map(),journal:{directory,mode:'create'}};
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,receiver:producer}),error=>code(error)==='ForeignOwner');
  assert.equal(existsSync(directory),false);
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,journal:{...options.journal,store_id:'caller-selected'}}),error=>code(error)==='InvalidContract');
  assert.equal(existsSync(directory),false);
  const foreign=path.join(work,'foreign');mkdirSync(foreign,{mode:0o700});
  const file=path.join(foreign,'workflow.sqlite'),foreignDb=new DatabaseSync(file);
  foreignDb.exec("CREATE TABLE retained_data (id TEXT PRIMARY KEY); INSERT INTO retained_data VALUES ('keep')");foreignDb.close();
  const digest=file=>createHash('sha256').update(readFileSync(file)).digest('hex'),before=digest(file);
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,journal:{directory:foreign,mode:'reopen'}}));
  assert.equal(digest(file),before);
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,journal:{directory:foreign,mode:'create'}}),/EEXIST/);
  assert.equal(digest(file),before);
  driver=await owner.openWorkflow(handle,options);
  const definition=driver.inspectDefinition();
  assert.equal(definition.workflow,'ReviewDesk.ApprovalFlow');assert.equal(definition.service,'ReviewDeskService');
  assert.equal(definition.source_closure_sha256,owner.inspect(handle).workflow_contract.source_closure_sha256);
  for(const input of [new Uint8Array([255]),Buffer.from('{"id":"1","id":"2"}'),Buffer.from('{} trailing')])
   await assert.rejects(()=>driver.scheduleStart(input,'invalid-input'));
  const missingAuthority=await driver.scheduleStart(wire({id:'23',slotRequest:{resourceId:'room-a',day:'7',startsAt:'60',endsAt:'90'}}),'without-actor');
  assert.equal(missingAuthority,null,'an empty actor map never grants command execution');
  const db=new DatabaseSync(definition.journal_path,{readOnly:true});
  try{assert.equal(db.prepare('SELECT count(*) AS n FROM _craft_workflow_instances_v1').get().n,0);}
  finally{db.close();}
  const saved=definition.journal_path+'.saved';
  renameSync(definition.journal_path,saved);
  assert.throws(()=>driver.claimNext(1000),error=>code(error)==='StaleOwner');
  writeFileSync(definition.journal_path,'replacement',{mode:0o600,flag:'wx'});
  assert.throws(()=>driver.claimNext(1000),error=>code(error)==='StaleOwner');
  unlinkSync(definition.journal_path);renameSync(saved,definition.journal_path);
  const extra=path.join(directory,'linked.sqlite');linkSync(definition.journal_path,extra);
  assert.throws(()=>driver.inspectDefinition(),error=>code(error)==='StaleOwner');
  unlinkSync(extra);
  await driver.close();await driver.close();
  assert.throws(()=>driver.inspectDefinition(),error=>code(error)==='DisposedOwner');
  const alias=path.join(work,'journal-alias');symlinkSync(directory,alias,'dir');
  await assert.rejects(()=>owner.openWorkflow(handle,{...options,journal:{directory:alias,mode:'reopen'}}),error=>code(error)==='InvalidContract');
  driver=await owner.openWorkflow(handle,{...options,journal:{directory,mode:'reopen'}});
  assert.equal(driver.claimNext(1000),null);
  await driver.close();driver=undefined;
 }finally{
  await driver?.close();await receiver?.close();await producer?.close();await auth?.close();
  if(handle)try{owner.dispose(handle);}catch{}
  assert.ok(realpathSync(work).startsWith(realpathSync(tmpdir())+path.sep+'craft-public-workflow-'));
  assert.ok(path.basename(path.dirname(root)).startsWith('craft-c11-v3-plan-'));
  rmSync(work,{recursive:true,force:true});rmSync(path.dirname(root),{recursive:true,force:true});
 }
});
