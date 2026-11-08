import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {cpSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCommerceWorkflowCoordinationBindingV1,assertCommerceWorkflowCoordinationBindingV1} from '../src/commerce/commerce-workflow-coordination-binding-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');

test('original Workflow binds its declared application coordination records',async()=>{
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 try{
  const owner=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
  assertCommerceWorkflowCoordinationBindingV1(owner);
  const view=owner.inspect();
  assert.equal(view.owner_service,'orders');
  assert.equal(view.workflow.input_entry,'Orders.CheckoutStartEntry');
  assert.equal(view.inbox_entity,'Shop.Application.WorkflowInbox');
  assert.equal(view.schedule_entity,'Shop.Application.WorkSchedule');
  assert.equal(view.journal_entity,'Shop.Application.StepJournal');
  assert.equal(view.receipt_type,'Shop.Application.WorkScheduleReceipt');
  assert.throws(()=>createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.NotDeclared'));
 }finally{stage.dispose(source);semantics.dispose(semantic);sources.dispose(capture);}
});

test('a source-selected journal with incompatible native fields cannot bind',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-workflow-schema-')),sourceRoot=path.join(root,'source');
 cpSync(candidate,sourceRoot,{recursive:true});
 const file=path.join(sourceRoot,'application.alch'),original=readFileSync(file,'utf8');
 const changed=original.replace('  workerOwner Identifier\n  workerEpoch UInt64\n  observation optional<CheckoutObservation>',
  '  workerOwner Identifier\n  workerEpoch Bool\n  observation optional<CheckoutObservation>');
 assert.notEqual(changed,original);
 writeFileSync(file,changed);
 const identitiesFile=path.join(sourceRoot,'contracts/contract-identities.json'),identities=JSON.parse(readFileSync(identitiesFile,'utf8'));
 const identity=identities.modules.find((row:any)=>row.artifact.path==='application.alch');assert.ok(identity);
 identity.artifact.sha256=createHash('sha256').update(changed).digest('hex');identity.artifact.bytes=Buffer.byteLength(changed);
 writeFileSync(identitiesFile,JSON.stringify(identities,null,2)+'\n');
 const sources=createCoreCommerceSourceOwner();let capture:ReturnType<typeof sources.prepare>|undefined;
 let semantics:ReturnType<typeof createCoreCommerceSemanticOwner>|undefined,semantic:ReturnType<ReturnType<typeof createCoreCommerceSemanticOwner>['check']>|undefined;
 let stage:ReturnType<typeof createCoreCommerceStageSourceOwner>|undefined,source:Awaited<ReturnType<ReturnType<typeof createCoreCommerceStageSourceOwner>['prepare']>>|undefined;
 try{
  capture=sources.prepare(sourceRoot);semantics=createCoreCommerceSemanticOwner(sources);semantic=semantics.check(capture);
  stage=createCoreCommerceStageSourceOwner(sources,semantics);source=await stage.prepare(sourceRoot,'application.alch');
  assert.throws(()=>createCommerceWorkflowCoordinationBindingV1(sources,capture!,stage!,source!,'Orders.Checkout.Checkout'),
   (error:any)=>error?.diagnostics?.[0]?.code==='InvalidContract');
 }finally{if(stage&&source)stage.dispose(source);if(semantics&&semantic)semantics.dispose(semantic);if(capture)sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
