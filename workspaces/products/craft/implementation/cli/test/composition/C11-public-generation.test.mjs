import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {createGenericCompositionOwner,createGenericBundledApplicationOwner} from '../../src/generic/public-sdk.ts';
import {build} from './C11-source-fixture.mjs';

test('C11 public owner generates and recaptures a selected write/inspect source closure',async()=>{
 const fixture=build('ReviewDesk'),out=mkdtempSync(path.join(os.tmpdir(),'craft-c11-public-'));
 const owner=createGenericCompositionOwner();let handle,generated,generatedHandle;
 try{
  handle=await owner.prepare({sourcePath:path.join(fixture.root,'business.alch'),profilePath:path.join(fixture.root,'contracts/selected-profile.json'),externalProfilePath:path.join(fixture.root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(fixture.root,'contracts/external-write-bindings.json')});
  assert.equal(owner.inspect(handle).transaction_contract.admission_mode,'external-write-entry');
  const review=owner.review(handle,'C11-public-generation');
  owner.accept(handle,{decision_id:'C11-public-generation',owner:'C11-public-generation',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(out,'decision.json'));
  const output=path.join(out,'generated');
  const manifest=owner.generate(handle,{entry:'ReviewDesk.CommitRequestApprovalEntry',outputDirectory:output});
  assert.equal(manifest.runtime_contract.application_schema_version,'craft.generic-transaction-application/v3-candidate');
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  const bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  assert.ok(system.nodes.some(n=>n.id==='external-write:capture'&&n.inspect_query==='ReviewDesk.Inspect'));
  assert.ok(system.nodes.some(n=>n.id==='external-intent:capture'));
  assert.ok(bridge.links.some(l=>l.business==='ReviewDesk.Provider'&&l.system==='external-write:capture'));
  assert.equal(readFileSync(path.join(output,'model/native/provider.json'),'utf8'),readFileSync(path.join(fixture.root,'native/provider.json'),'utf8'));
  const modulePath=path.join(output,'application.mjs'),moduleText=readFileSync(modulePath,'utf8');
  const bundle=JSON.parse(moduleText.split('const bundle=')[1].split(';\nexport function')[0]);
  generated=createGenericBundledApplicationOwner(pathToFileURL(modulePath).href,bundle);generatedHandle=await generated.prepare();
  assert.equal(generated.inspect(generatedHandle).transaction_contract.admission_mode,'external-write-entry');
 }finally{
  if(generatedHandle)generated.dispose(generatedHandle);
  if(handle)owner.dispose(handle);
  rmSync(fixture.root,{recursive:true,force:true});rmSync(out,{recursive:true,force:true});
 }
});
