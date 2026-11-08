import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {build} from './C11-source-fixture.mjs';

test('C11 original source admits one checked write/inspect pair without execution authority',()=>{
 const owned=build('ReviewDesk');
 try{
  const checked=owned.plans.inspectSourceApplication(owned.application);
  assert.equal(checked.contract.admission_mode,'external-write-entry');
  assert.equal(checked.contract.execution_policy,'refused-until-original-durable-external-owner');
  assert.equal(checked.contract.write_bindings.length,1);
  const binding=checked.contract.write_bindings[0];
  assert.equal(binding.write_operation_ref,'ReviewDesk.Capture');
  assert.equal(binding.inspect_query_ref,'ReviewDesk.Inspect');
  assert.deepEqual(binding.request_type,{kind:'record',name:'ReviewDesk.ProviderRequest'});
  assert.deepEqual(binding.wire_request_type,{kind:'record',name:'ReviewDesk.ProviderRequest'});
  assert.deepEqual(binding.wire_result_type,{kind:'record',name:'ReviewDesk.ProviderResult'});
  assert.throws(()=>owned.plans.inspect(owned.application),/V3 requires inert source inspection/);
 }finally{rmSync(owned.root,{recursive:true,force:true});}
});

test('C11 captured write selection loses currentness when its physical source changes',()=>{
 const owned=build('ReviewDesk');
 try{
  const selected=path.join(owned.root,'contracts/external-write-bindings.json');
  const original=readFileSync(selected,'utf8');
  const altered=original.replace('ReviewDesk','ReviewDesK');
  assert.notEqual(altered,original);
  assert.equal(Buffer.byteLength(altered),Buffer.byteLength(original));
  writeFileSync(selected,altered);
  assert.throws(()=>owned.plans.inspectSourceApplication(owned.application),error=>error?.diagnostics?.[0]?.code==='StaleOwner');
  writeFileSync(selected,original);
  assert.throws(()=>owned.plans.inspectSourceApplication(owned.application),error=>error?.diagnostics?.[0]?.code==='StaleOwner');
 }finally{rmSync(owned.root,{recursive:true,force:true});}
});

test('C11 accepted decision remains stale after same-size tamper and restore',()=>{
 const owned=build('ReviewDesk');
 try{
  const decision=path.join(owned.root,'decision.json'),original=readFileSync(decision,'utf8');
  const altered=original.replace('"accepted"','"declined"');
  assert.notEqual(altered,original);
  assert.equal(Buffer.byteLength(altered),Buffer.byteLength(original));
  writeFileSync(decision,altered);
  assert.throws(()=>owned.plans.inspectSourceApplication(owned.application),error=>error?.diagnostics?.[0]?.code==='StaleOwner');
  writeFileSync(decision,original);
  assert.throws(()=>owned.plans.inspectSourceApplication(owned.application),error=>error?.diagnostics?.[0]?.code==='StaleOwner');
 }finally{rmSync(owned.root,{recursive:true,force:true});}
});
