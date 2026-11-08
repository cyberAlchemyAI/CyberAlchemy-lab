import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericWorkflowSourceContract,inspectGenericWorkflowSource} from '../../src/generic/workflow-source.ts';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner,requireGenericWorkflowRuntime} from '../../src/generic/public-sdk.ts';

test('C13 original C11+C12 capture checks authored Workflow and profile binding',()=>{
 const root=workflowFixture();try{
  const owner=createCoreCommerceSourceOwner('event-handoff-entry'),capture=owner.prepare(root),inspection=owner.inspect(capture),result=createGenericWorkflowSourceContract(inspection),semantic=inspectGenericWorkflowSource(inspection);
  assert.equal(result.contract.workflow,'ReviewDesk.ApprovalFlow');assert.equal(result.contract.service,'ReviewDeskService');assert.equal(result.contract.start_entry,'ReviewDesk.BeginWorkflowEntry');assert.deepEqual(result.contract.steps.map(s=>s.entry),['ReviewDesk.ReserveWorkflowEntry','ReviewDesk.CommitRequestApprovalEntry','AuditService.RecordApprovedEntry']);assert.deepEqual(result.contract.compensation_order,['reserve']);assert.equal(semantic.workflows[0].profile_sha256,result.contract.profile_sha256);assert.equal(result.contract.source_capture_sha256,inspection.capture_sha256);owner.assertCurrent(capture);owner.dispose(capture);
 }finally{rmSync(path.dirname(root),{recursive:true,force:true});}
});
test('C13 SDK admits and generates source-checked Workflow plan with graph and bridge lineage',async()=>{
 const root=workflowFixture(),work=path.dirname(root),owner=createGenericCompositionOwner();let handle,generated,generatedHandle;
 try{
  handle=await owner.prepare({sourcePath:path.join(root,'business.alch'),additionalSourcePaths:[path.join(root,'audit-service.alch')],profilePath:path.join(root,'contracts/selected-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const inspection=owner.inspect(handle);assert.equal(inspection.workflow_contract.workflow,'ReviewDesk.ApprovalFlow');assert.equal(inspection.workflow_profile.path,'contracts/workflow-profile.json');
  assert.throws(()=>requireGenericWorkflowRuntime(owner,handle),error=>error.diagnostics?.[0]?.code==='MissingMapping');
  const review=owner.review(handle,'C13-source-review');owner.accept(handle,{decision_id:'C13-source-review',owner:'C13-source-review',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'C13-source-decision.json'));
  const binding=requireGenericWorkflowRuntime(owner,handle);assert.equal(binding.contract.workflow,'ReviewDesk.ApprovalFlow');assert.equal(binding.contract.start_parameters[0].name,'id');assert.equal(binding.contract.steps[0].parameters[0].name,'id');assert.equal(binding.contract.steps[0].compensation_parameters[0].name,'id');
  const output=path.join(work,'C13-generated'),manifest=owner.generate(handle,{entry:'ReviewDesk.BeginWorkflowEntry',outputDirectory:output});
  const plan=JSON.parse(readFileSync(path.join(output,'workflow-plan.json'),'utf8')),system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8')),bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.equal(plan.contract.workflow,binding.contract.workflow);assert.equal(plan.derivation.profile_sha256,binding.contract.profile_sha256);assert.equal(plan.qualification,'source-checked;worker-binding-required');
  assert.ok(system.nodes.some(n=>n.id==='workflow:ReviewDesk.ApprovalFlow'&&n.artifact==='workflow-plan.json'));
  assert.ok(system.edges.some(e=>e.from==='workflow:ReviewDesk.ApprovalFlow'&&e.to==='workflow-entry:ReviewDesk.BeginWorkflowEntry'));
  assert.ok(bridge.links.some(l=>l.business==='ReviewDesk.ApprovalFlow'&&l.profile_sha256===binding.contract.profile_sha256));
  assert.ok(manifest.files.some(f=>f.path==='workflow-plan.json'));
  const modulePath=path.join(output,'application.mjs'),bundle=JSON.parse(readFileSync(modulePath,'utf8').split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);generatedHandle=await generated.prepare();
  const generatedReview=generated.review(generatedHandle,'C13-generated-review');generated.accept(generatedHandle,{decision_id:'C13-generated-review',owner:'C13-generated-review',outcome:'accepted',reviewed_digest:generatedReview.review_sha256},path.join(work,'C13-generated-decision.json'));
  const bundled=requireGenericWorkflowRuntime(generated,generatedHandle);assert.equal(bundled.contract.workflow,binding.contract.workflow);assert.equal(bundled.contract.profile_sha256,binding.contract.profile_sha256);
  const profilePath=path.join(root,'contracts/workflow-profile.json'),originalProfile=readFileSync(profilePath,'utf8');
  writeFileSync(profilePath,originalProfile+' ');
  assert.throws(()=>binding.assertCurrent(),error=>error.diagnostics?.[0]?.code==='StaleOwner');
  writeFileSync(profilePath,originalProfile);
  assert.throws(()=>owner.assertCurrent(handle),error=>error.diagnostics?.[0]?.code==='StaleOwner');
 }finally{if(generatedHandle)try{generated.dispose(generatedHandle);}catch{}if(handle)try{owner.dispose(handle);}catch{}rmSync(work,{recursive:true,force:true});}
});
