/** Same-source Workflow/Event definition and emitted service identity.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner,requireGenericWorkflowRuntime} from '../../src/generic/public-sdk.ts';
import {createGenericServiceArtifactOwner} from '../../src/generic/service-artifact-owner.ts';
import {exportGenericWorkflowEventJoinV1,assertGenericWorkflowEventJoinCurrentV1,
 GenericWorkflowEventJoinErrorV1} from '../../src/generic/formal-workflow-event-join-v1.ts';

test('C15 joins checked Workflow and Event transition identity to selected emitted artifacts',async()=>{
 const root=workflowFixture(),work=path.dirname(root),sdk=createGenericCompositionOwner();
 let handle;
 try{
  handle=await sdk.prepare({sourcePath:path.join(root,'business.alch'),
   additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),
   externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=sdk.review(handle,'C15-workflow-event-join');
  sdk.accept(handle,{decision_id:'C15-workflow-event-join',owner:'C15-workflow-event-join',
   outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'C15-join-decision.json'));
  const original=requireGenericWorkflowRuntime(sdk,handle);
  const entries=[...new Set([original.contract.start_entry,...original.contract.steps.flatMap(
   step=>[step.entry,...(step.compensation_entry?[step.compensation_entry]:[])])])].sort();
  const artifacts=createGenericServiceArtifactOwner(sdk,handle),out=path.join(work,'services');
  const emitted=artifacts.emit({outputDirectory:out,entries});
  const model=exportGenericWorkflowEventJoinV1(sdk,handle,artifacts,emitted);
  const temporal=sdk.exportWorkflowTlaFormal(handle);
  assert.equal(model.source_capture_sha256,original.contract.source_capture_sha256);
  assert.equal(model.workflow.id,original.contract.workflow);
  assert.equal(model.workflow_tla_sha256,temporal.model.tla_sha256);
  assert.equal(model.tla,temporal.model.tla);
  assert.equal(model.scope,'checked-workflow-event-definition-and-emitted-subgraph');
  assert.equal(model.event.binding,original.contract.steps[2].event_binding);
  assert.deepEqual(model.steps.map(row=>[row.index,row.kind,row.successor]),[
   [0,'local-command',1],[1,'provider-command',2],[2,'event-await',null]]);
  assert.equal(model.provider_policy.on_unknown,'resume-original-command');
  assert.equal(model.provider_policy.failure_compensation_precondition,'proven-no-provider-effect');
  assert.equal(model.emitted_complete_application,false);
  assert.ok(model.missing_complete_application_classes.includes('workflow-worker-runtime-verification'));
  assert.ok(model.steps.every(row=>readFileSync(path.join(out,row.emitted_artifact)).length>0));
  assert.ok(readFileSync(path.join(out,model.workflow.worker_artifact)).length>0);
  assert.match(model.alloy,/LocalStep\.next = ProviderStep/);
  assert.match(model.alloy,/ProviderStep\.next = EventStep/);
  assert.match(model.alloy,/EventStep\.awaits = Handoff/);
  assert.doesNotMatch(model.alloy,/ReviewDesk|AuditService/);
  assert.doesNotThrow(()=>assertGenericWorkflowEventJoinCurrentV1(sdk,handle,artifacts,emitted,model));
  assert.throws(()=>assertGenericWorkflowEventJoinCurrentV1(sdk,handle,artifacts,emitted,
   {...model,alloy:model.alloy+'\n'}),error=>error instanceof GenericWorkflowEventJoinErrorV1&&
   error.code==='InvalidModel');
  const workerPath=path.join(out,model.workflow.worker_artifact);
  writeFileSync(workerPath,Buffer.concat([readFileSync(workerPath),Buffer.from('// stale\n')]));
  assert.throws(()=>assertGenericWorkflowEventJoinCurrentV1(sdk,handle,artifacts,emitted,model));
 }finally{if(handle)try{sdk.dispose(handle);}catch{}rmSync(work,{recursive:true,force:true});}
});
