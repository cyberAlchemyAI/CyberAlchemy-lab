import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.ts';
import {canonicalJson} from '../../src/profile-engine/contracts.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const contractDirectory=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05');
const business='module Logic version 1\nvalue-object Request:\n  verified Bool\n  flagged Bool\nrule IsVerified:\n  input request Request\n  expression request.verified and not request.flagged\n';

test('C15 original SDK binds optional finite model to selected profile and generated Rule',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'craft-c15-sdk-'));
 const sdk=createGenericCompositionOwner();let handle;
 try{
  mkdirSync(path.join(root,'contracts'));
  const sourcePath=path.join(root,'business.alch'),profilePath=path.join(root,'profile.json');
  writeFileSync(sourcePath,business);
  writeFileSync(profilePath,readFileSync(path.join(contractDirectory,'profile.json')));
  writeFileSync(path.join(root,'contracts/bounds.json'),readFileSync(path.join(contractDirectory,'bounds.json')));
  handle=await sdk.prepare({sourcePath,profilePath});
  const review=sdk.review(handle,'C15-sdk-formal');
  sdk.accept(handle,{decision_id:'C15-sdk-formal',owner:'C15-sdk-formal',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(root,'decision.json'));
  const joined=sdk.exportFiniteBoolFormal(handle,{rule:'Logic.IsVerified'});
  assert.throws(()=>sdk.exportWorkflowTlaFormal(handle),
   error=>error.diagnostics?.[0]?.code==='UnsupportedCapability');
  assert.throws(()=>sdk.exportStructuralAlloyFormal(handle,{owner:{},artifact:{}}),
   error=>error.diagnostics?.[0]?.code==='UnsupportedCapability');
  const inspection=sdk.inspect(handle);
  assert.equal(joined.schema_version,'craft.generic-finite-bool-sdk-join/v1-candidate');
  assert.equal(joined.profile.sha256,inspection.profile.sha256);
  assert.equal(joined.model.profile_metadata.sha256,inspection.profile.sha256);
  assert.equal(joined.model.source_node,'Logic.IsVerified');
  assert.equal(joined.model.observations.length,4);
  const outputDirectory=path.join(root,'generated');
  const generated=sdk.generate(handle,{rule:'Logic.IsVerified',outputDirectory});
  const executable=await import(pathToFileURL(path.join(outputDirectory,'rule.mjs')).href);
  for(const row of joined.model.observations){
   const actual=executable.evaluate(Buffer.from(canonicalJson(row.input)));
   assert.equal(actual.ok,row.result.ok);
   assert.equal(actual.fuel_used,row.result.fuel_used);
   if(actual.ok)assert.equal(Buffer.from(actual.wire).toString('utf8'),row.result.wire);
   else assert.equal(canonicalJson(actual.error),row.result.error_json);
  }
  assert.equal(generated.native.contract_sha256,joined.model.contract_sha256);
  writeFileSync(profilePath,readFileSync(profilePath,'utf8')+'\n');
  assert.throws(()=>sdk.exportFiniteBoolFormal(handle,{rule:'Logic.IsVerified'}));
 }finally{if(handle)try{sdk.dispose(handle);}catch{}rmSync(root,{recursive:true,force:true});}
});
