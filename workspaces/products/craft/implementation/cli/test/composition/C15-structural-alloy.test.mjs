import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.ts';
import {createGenericServiceArtifactOwner} from '../../src/generic/service-artifact-owner.ts';
import {
  exportGenericStructuralAlloyModel,
  assertGenericStructuralAlloyCurrent,
  GenericStructuralAlloyUnsupportedError,
} from '../../src/generic/formal-structural-alloy.ts';

test('C15 structural Alloy projects the exact original selected service inventory and detects stale files',async()=>{
 const root=workflowFixture(),work=path.dirname(root),sdk=createGenericCompositionOwner();
 let source;
 try{
  source=await sdk.prepare({sourcePath:path.join(root,'business.alch'),
   additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),
   externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=sdk.review(source,'C15-structural-alloy');
  sdk.accept(source,{decision_id:'C15-structural-alloy',owner:'C15-structural-alloy',
   outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'C15-decision.json'));
  const owner=createGenericServiceArtifactOwner(sdk,source),out=path.join(work,'services');
  const artifact=owner.emit({outputDirectory:out,
   entries:['ReviewDesk.BeginWorkflowEntry','AuditService.RecordApprovedEntry']});
  const original=owner.inspect(artifact),model=exportGenericStructuralAlloyModel(owner,artifact);
  const joined=sdk.exportStructuralAlloyFormal(source,{owner,artifact});
  assert.equal(joined.schema_version,'craft.generic-structural-alloy-sdk-join/v1-candidate');
  assert.equal(joined.model.alloy_sha256,model.alloy_sha256);
  assert.equal(joined.claim_ceiling,model.claim_ceiling);
  assert.equal(model.language,'alloy');
  assert.equal(model.source_manifest_complete_application,false);
  assert.equal(model.inventory_sha256,original.inventory_sha256);
  assert.equal(model.source_capture_sha256,original.source_capture_sha256);
  assert.equal(model.profile_sha256,original.profile_sha256);
  assert.equal(model.executable_semantics_sha256,original.executable_semantics_sha256);
  assert.deepEqual(model.services.map(row=>row.id),['AuditService','ReviewDeskService']);
  assert.deepEqual(model.entries.map(row=>row.id),['AuditService.RecordApprovedEntry','ReviewDesk.BeginWorkflowEntry']);
  assert.equal(model.events.length,1);
  assert.equal(model.events[0].descriptors.length,2);
  assert.equal(model.workflows.length,1);
  assert.equal(model.services.find(row=>row.id==='ReviewDeskService').workflow,model.workflows[0].atom);
  assert.ok(model.services.every(row=>row.entries.length===1&&row.events.length===1));
  assert.ok(model.artifacts.some(row=>row.path.endsWith('/worker.mjs')));
  assert.ok(model.artifacts.every(row=>original.files.some(file=>file.path===row.path&&file.sha256===row.sha256)));
  assert.match(model.alloy,/abstract sig Service \{ entries: set Entry/);
  assert.match(model.alloy,/fact ExactEmittedStructure \{/);
  assert.match(model.alloy,/check EachEntryHasOneService for [1-9][0-9]*/);
  assert.match(model.alloy,/check EachBindingHasService for [1-9][0-9]*/);
  assert.match(model.alloy,/check EachBindingHasDescriptor for [1-9][0-9]*/);
  assert.match(model.alloy,/check BindingDescriptorsMatchServices for [1-9][0-9]*/);
  assert.match(model.alloy,/check EachWorkflowHasOneService for [1-9][0-9]*/);
  assert.match(model.alloy,/run \{\} for [1-9][0-9]*/);
  assert.doesNotMatch(model.alloy,/ReviewDesk|AuditService/,'source labels remain metadata, not Alloy identifiers');
  assert.equal(exportGenericStructuralAlloyModel(owner,artifact).alloy,model.alloy);
  assert.doesNotThrow(()=>assertGenericStructuralAlloyCurrent(owner,artifact,model));
  assert.throws(()=>exportGenericStructuralAlloyModel({inspect:()=>original},artifact));
  assert.throws(()=>exportGenericStructuralAlloyModel(owner,{...artifact}));
  assert.throws(()=>sdk.exportStructuralAlloyFormal({...source},{owner,artifact}));
  assert.throws(()=>sdk.exportStructuralAlloyFormal(source,{owner,artifact:{...artifact}}));
  assert.throws(()=>sdk.exportStructuralAlloyFormal(source,{owner:{inspect:()=>original},artifact}));
  assert.throws(()=>sdk.exportStructuralAlloyFormal(source,{owner,artifact,extra:true}));
  assert.throws(()=>assertGenericStructuralAlloyCurrent(owner,artifact,{...model,alloy:model.alloy+'\n'}),
   error=>error instanceof GenericStructuralAlloyUnsupportedError&&error.code==='InvalidInventory');
  assert.throws(()=>assertGenericStructuralAlloyCurrent(owner,artifact,{...model,profile_sha256:'0'.repeat(64)}),
   error=>error instanceof GenericStructuralAlloyUnsupportedError&&error.code==='InvalidInventory');
  const module=path.join(out,original.services[0].directory,'service.mjs'),bytes=readFileSync(module);
  writeFileSync(module,Buffer.concat([bytes,Buffer.from('// tampered\n')]));
  assert.throws(()=>assertGenericStructuralAlloyCurrent(owner,artifact,model));
  assert.throws(()=>sdk.exportStructuralAlloyFormal(source,{owner,artifact}));
 }finally{if(source)try{sdk.dispose(source);}catch{}rmSync(work,{recursive:true,force:true});}
});
