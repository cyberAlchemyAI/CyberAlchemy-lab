/** Optional formal output and claim-free code generation from one selected
 * C05 source/profile owner. Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.ts';

const repository=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const contracts=path.join(repository,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C05');
const oracle=JSON.parse(readFileSync(path.join(contracts,'oracle-v1.json'),'utf8'));

test('C15 selected C05 Mapping has optional wire model and claim-free native generation',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'craft-c15-selected-wire-'));
 const sdk=createGenericCompositionOwner();let handle;
 try{
  mkdirSync(path.join(root,'contracts'));
  const sourcePath=path.join(root,'business.alch'),profilePath=path.join(root,'profile.json');
  writeFileSync(sourcePath,readFileSync(path.join(contracts,'request.alch')));
  writeFileSync(profilePath,readFileSync(path.join(contracts,'profile.json')));
  writeFileSync(path.join(root,'contracts/bounds.json'),readFileSync(path.join(contracts,'bounds.json')));
  handle=await sdk.prepare({sourcePath,profilePath});
  const review=sdk.review(handle,'C15-selected-pure-wire');
  sdk.accept(handle,{decision_id:'C15-selected-pure-wire',owner:'C15-selected-pure-wire',
   outcome:'accepted',reviewed_digest:review.review_sha256},path.join(root,'decision.json'));
  const outputDirectory=path.join(root,'generated');
  const generated=sdk.generate(handle,{mapping:'ReviewDesk.ToDecision',outputDirectory});
  const native=await import(pathToFileURL(path.join(outputDirectory,'mapping.mjs')).href);
  let firstFormal;
  for(const flagged of [false,true]){
   const request={...structuredClone(oracle.positive_input),flagged};
   const wire=new Uint8Array(Buffer.from(JSON.stringify({request})));
   const joined=sdk.exportPureWireFormal(handle,{mapping:'ReviewDesk.ToDecision'},wire);
   assert.equal(joined.profile_binding,'original-selected-profile-bound');
   assert.equal(joined.profile.sha256,sdk.inspect(handle).profile.sha256);
   assert.equal(joined.model.source_binding,'original-owner-checked');
   assert.equal(joined.model.input_mode,'same-account-wire-input');
   assert.equal(joined.reference_parity,'checked-reference-matched-for-this-wire');
   if(!firstFormal)firstFormal=joined;
   const actual=native.evaluate(wire),expected=joined.model.result;
   assert.equal(actual.ok,expected.ok);
   assert.equal(actual.fuel_used,expected.fuel_used);
   if(actual.ok&&expected.ok)
    assert.equal(Buffer.from(actual.wire).toString('hex'),expected.wire_hex);
   assert.equal(generated.native.contract_sha256,joined.model.contract_sha256);
  }
  const formalDirectory=path.join(root,'formal');
  sdk.publishFormalExportDirectory(handle,firstFormal,formalDirectory,[
   {relative_path:'pure.smt2',content:firstFormal.model.smtlib2},
  ]);
  assert.equal(readFileSync(path.join(formalDirectory,'pure.smt2'),'utf8'),firstFormal.model.smtlib2);
  writeFileSync(profilePath,Buffer.concat([readFileSync(profilePath),Buffer.from('\n')]));
  assert.throws(()=>sdk.publishFormalExportDirectory(handle,firstFormal,path.join(root,'stale-formal'),[
   {relative_path:'pure.smt2',content:firstFormal.model.smtlib2},
  ]),error=>(error?.diagnostics?.[0]?.code??error?.code)==='StaleOwner');
 }finally{if(handle)try{sdk.dispose(handle);}catch{}rmSync(root,{recursive:true,force:true});}
});
