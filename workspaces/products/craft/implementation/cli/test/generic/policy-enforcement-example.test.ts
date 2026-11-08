/** The documentation sample must become an actual generated Operation.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';

test('EN09 documented publication example generates and executes both admission outcomes',async()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'craft-enforce-example-'));
 try{
  const sourcePath=path.join(directory,'publication.alch'),profilePath=path.join(directory,'profile.json');
  const example=new URL('../../examples/policy-enforcement/',import.meta.url);mkdirSync(path.join(directory,'contracts'));
  writeFileSync(sourcePath,readFileSync(new URL('publication.alch',example)));writeFileSync(profilePath,readFileSync(new URL('profile.json',example)));writeFileSync(path.join(directory,'contracts/bounds.json'),readFileSync(new URL('contracts/bounds.json',example)));
  const owner=createGenericCompositionOwner(),handle=await owner.prepare({sourcePath,profilePath});
  const review=owner.review(handle,'policy-enforcement-example');owner.accept(handle,{decision_id:'policy-enforcement-example',owner:'policy-enforcement-example',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,'acceptance.json'));
  const generated=path.join(directory,'generated');await owner.generate(handle,{operation:'Publications.Publish',outputDirectory:generated});
  const {evaluate}=await import(pathToFileURL(path.join(generated,'operation.mjs')).href);
  for(const approved of [true,false]){
   const wire=new Uint8Array(Buffer.from(JSON.stringify({approved}))),reference=await owner.evaluateReference(handle,{operation:'Publications.Publish'},wire),actual=evaluate(wire);
   assert.equal(reference.ok,true);assert.equal(actual.ok,true);assert.equal(actual.fuel_used,reference.fuel_used);if(!actual.ok||!reference.ok)throw Error('unexpected computation fault');
   const result=JSON.parse(Buffer.from(actual.wire).toString('utf8'));assert.deepEqual(Buffer.from(actual.wire),Buffer.from(reference.wire));
   assert.deepEqual(result,approved?{tag:'Returned',fields:{value:true}}:{tag:'Rejected',fields:{code:'approval-needed'}});
  }
 }finally{rmSync(directory,{recursive:true,force:true});}
});
