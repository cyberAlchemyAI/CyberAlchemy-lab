import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.ts';
import {
 exportGenericWorkflowTlaModel,
 assertGenericWorkflowTlaCurrent,
 GenericWorkflowTlaUnsupportedError,
} from '../../src/generic/formal-workflow-tla.ts';

test('C15 TLA+ journal projection binds original checked C13 source and rejects stale data',async()=>{
 const root=workflowFixture(),work=path.dirname(root),owner=createGenericCompositionOwner();
 let handle;
 try{
  handle=await owner.prepare({sourcePath:path.join(root,'business.alch'),
   additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),
   externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  assert.throws(()=>exportGenericWorkflowTlaModel(owner,handle),
   error=>error.diagnostics?.[0]?.code==='MissingMapping');
  const review=owner.review(handle,'C15-workflow-tla');
  owner.accept(handle,{decision_id:'C15-workflow-tla',owner:'C15-workflow-tla',
   outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'C15-tla-decision.json'));
  const model=exportGenericWorkflowTlaModel(owner,handle);
  const joined=owner.exportWorkflowTlaFormal(handle);
  assert.equal(joined.schema_version,'craft.generic-workflow-tla-sdk-join/v1-candidate');
  assert.equal(joined.model.tla_sha256,model.tla_sha256);
  assert.equal(joined.claim_ceiling,model.claim_ceiling);
  assert.equal(model.language,'tla+');
  assert.equal(model.workflow,'ReviewDesk.ApprovalFlow');
  assert.deepEqual(model.steps.map(s=>s.kind),['local-command','provider-command','event-await']);
  assert.match(model.tla,/---- MODULE GenericWorkflowJournal ----/);
  assert.match(model.tla,/Spec == Init \/\\ \[\]\[Next\]_vars/);
  assert.match(model.tla,/Claim == .*fence < MaxFence/);
  const claimAction=model.tla.split('Claim == ')[1]?.split('Expire == ')[0];
  const expireAction=model.tla.split('Expire == ')[1]?.split('Renew == ')[0];
  assert.ok(claimAction?.includes("providerNoEffect' = FALSE")&&expireAction?.includes("providerNoEffect' = FALSE"),
   'a recovered worker must reacquire provider no-effect evidence');
  assert.match(model.tla,/DefiniteFailure ==/);
  const observedCommand=model.tla.split('ObserveCommandSuccess == ')[1]?.split('CommitStep == ')[0];
  const committedCommand=model.tla.split('CommitStep == ')[1]?.split('SuspendUnknown == ')[0];
  assert.ok(observedCommand?.includes("commandSuccessObserved' = TRUE"));
  assert.ok(committedCommand?.includes('/\\ commandSuccessObserved'),
   'prepared or unknown commands need an observed success before journal commit');
  const observedEvent=model.tla.split('ObserveEventReceipt == ')[1]?.split('CommitEvent == ')[0];
  const committedEvent=model.tla.split('CommitEvent == ')[1]?.split('Complete == ')[0];
  assert.ok(observedEvent?.includes("eventReceiptObserved' = TRUE"));
  assert.ok(committedEvent?.includes('/\\ eventReceiptObserved'),
   'waiting events need an observed receipt before journal commit');
  assert.match(model.tla,/Next ==[\s\S]*?ObserveCommandSuccess[\s\S]*?ObserveEventReceipt/);
  const failureAction=model.tla.split('DefiniteFailure == ')[1]?.split('ProviderFailureUnproven == ')[0];
  assert.ok(failureAction,'the provider failure transition must be present');
  assert.ok(failureAction.includes('(step = 0 \\/ (step = 1 /\\ providerNoEffect))'),
   'provider failure cannot enter compensation without no-effect evidence');
  assert.match(model.tla,/ProviderFailureUnproven ==[\s\S]*?phase' = "needs-review"/,
   'unproven provider failure must retain a review state');
  assert.ok(model.tla.includes('BeginCompensation == /\\ held /\\ phase = "step-committed" /\\ step = 0'),
   'manual compensation cannot skip over a committed provider step');
  assert.match(model.tla,/CommitEvent ==/);
  assert.match(model.tla,/CommittedHasObservation == \(phase = "step-committed"\) =>/);
  assert.match(model.tla,/PrepareCompensation ==/);
  assert.match(model.tla,/FenceMonotonic ==/);
  assert.ok(model.tla.includes(`source_capture_sha256=${model.source_capture_sha256}`));
  assert.ok(model.tla.includes(`compatibility_sha256=${model.compatibility_sha256}`));
  assert.doesNotMatch(model.tla,/ReviewDesk|AuditService/);
  assert.equal(exportGenericWorkflowTlaModel(owner,handle).tla,model.tla);
  assert.doesNotThrow(()=>assertGenericWorkflowTlaCurrent(owner,handle,model));
  assert.throws(()=>exportGenericWorkflowTlaModel({},handle));
  assert.throws(()=>exportGenericWorkflowTlaModel(owner,{...handle}));
  assert.throws(()=>owner.exportWorkflowTlaFormal({...handle}));
  assert.throws(()=>assertGenericWorkflowTlaCurrent(owner,handle,{...model,tla:model.tla+'\n'}),
   error=>error instanceof GenericWorkflowTlaUnsupportedError&&error.code==='InvalidModel');
  const profile=path.join(root,'contracts/workflow-profile.json');
  writeFileSync(profile,readFileSync(profile,'utf8')+' ');
  assert.throws(()=>assertGenericWorkflowTlaCurrent(owner,handle,model),
   error=>error.diagnostics?.[0]?.code==='StaleOwner');
  assert.throws(()=>owner.exportWorkflowTlaFormal(handle),
   error=>error.diagnostics?.[0]?.code==='StaleOwner');
 }finally{if(handle)try{owner.dispose(handle);}catch{}rmSync(work,{recursive:true,force:true});}
});
