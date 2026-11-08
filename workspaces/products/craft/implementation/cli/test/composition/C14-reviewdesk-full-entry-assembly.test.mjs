import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner,requireGenericWorkflowRuntime} from '../../src/generic/public-sdk.ts';
import {createGenericServiceArtifactOwner} from '../../src/generic/service-artifact-owner.ts';
import {createGenericAuthFixture} from '../../src/generic/testing.ts';
import {GenericWorkflowStore} from '../../src/generic/workflow-store.ts';
import {workflowCompatibilitySha256} from '../../src/generic/workflow-worker.ts';

test('C14 emits every original ReviewDesk Entry and opens the source-bound two-service application',async()=>{
 const root=workflowFixture(),work=path.dirname(root),sdk=createGenericCompositionOwner();
 let source,auth,application,journalDb;
 try{
  source=await sdk.prepare({sourcePath:path.join(root,'business.alch'),additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=sdk.review(source,'C14-all-entry-reviewdesk');
  sdk.accept(source,{decision_id:'C14-all-entry-reviewdesk',owner:'C14-all-entry-reviewdesk',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'decision.json'));
  const sourceEntries=sdk.inspect(source).transaction_contract.entries.map(row=>row.entry);
  assert.ok(sourceEntries.length>6);
  const owner=createGenericServiceArtifactOwner(sdk,source),output=path.join(work,'all-entry-application');
  const artifact=owner.emit({outputDirectory:output,entries:sourceEntries});
  const manifest=owner.inspect(artifact),emittedEntries=manifest.services.flatMap(service=>service.entries.map(row=>row.entry));
  assert.deepEqual([...emittedEntries].sort(),[...sourceEntries].sort());
  assert.ok(manifest.services.every(service=>service.all_entries_covered));
  assert.equal(manifest.complete_application,false);
  assert.ok(manifest.missing_complete_application_classes.includes('provider-write-adapter'));
  assert.ok(manifest.missing_complete_application_classes.includes('event-relay-adapter'));
  assert.ok(manifest.missing_complete_application_classes.includes('workflow-worker-runtime-verification'));
  const graph=JSON.parse(readFileSync(path.join(output,'application-system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'application-business-system-bridge.json'),'utf8'));
  for(const service of manifest.services)for(const entry of service.entries){
   assert.ok(graph.nodes.some(node=>node.id===service.service+'::entry:'+entry.entry));
   assert.ok(bridge.links.some(link=>link.business===entry.entry&&link.system===service.service+'::entry:'+entry.entry));
  }
  assert.ok(graph.edges.every(edge=>graph.nodes.some(node=>node.id===edge.from)&&graph.nodes.some(node=>node.id===edge.to)));
  assert.ok(bridge.links.every(link=>graph.nodes.some(node=>node.id===link.system)));
  const workflow=requireGenericWorkflowRuntime(sdk,source).contract;
  const event=sdk.inspect(source).transaction_contract.event_bindings.find(row=>row.producer_service===workflow.service);
  assert.ok(event);
  auth=await createGenericAuthFixture(sdk,source,{ownedDirectory:path.join(work,'auth'),
   subjects:[{id:'c14-reviewdesk-operator',evidence:'c14-operator-evidence',session:'c14-operator-session'}],
   grants:[{subject:'c14-reviewdesk-operator',entry:workflow.start_entry}]});
  const generated=await import(pathToFileURL(path.join(output,'application.mjs')).href);
  assert.equal(generated.completeApplication,false);
  application=await generated.openGeneratedApplication(owner,artifact,{
   ReviewDeskService:{storePath:path.join(work,'review.sqlite'),mode:'create',nativeAuth:auth.nativeAuth,
    externalWriteEndpoint:'http://127.0.0.1:1/'},
   AuditService:{storePath:path.join(work,'audit.sqlite'),mode:'create',nativeAuth:auth.nativeAuth},
  });
  assert.equal(application.serviceIds.length,2);
  assert.equal(typeof application.runtime('ReviewDeskService').prepareCommand,'function');
  const relay=application.relay('ReviewDeskService');
  assert.equal(typeof relay.claimWorkflowEvent,'function');relay.close();
  journalDb=new DatabaseSync(':memory:');
  const journalStoreId='C14.full-entry.assembly';
  const journal=new GenericWorkflowStore(journalDb,{store_id:journalStoreId,owner_service:workflow.service,
   compatibility_sha256:workflowCompatibilitySha256(workflow)});
  const worker=application.worker(workflow.service,{journal,journal_store_id:journalStoreId,actors:new Map()});
  assert.equal(typeof worker.scheduleStart,'function');
  assert.equal(await application.deliverWorkflowEvent(event.id,'0'.repeat(64),1000),null);
 }finally{
  if(application)await application.close();
  if(journalDb)journalDb.close();
  if(auth)await auth.close();
  if(source)try{sdk.dispose(source);}catch{}
  rmSync(work,{recursive:true,force:true});
 }
});
