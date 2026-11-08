import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync,mkdirSync,symlinkSync,renameSync,unlinkSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {parseBusinessSource,BusinessSourceRejected} from '../src/business-authoring-parser.js';
import {resolveBusinessSpec,assertResolvedBusinessSpecCurrent,prepareBusinessSpecFile,disposeResolvedBusinessSpec} from '../src/business-authoring-resolve.js';
import type {ParsedBusinessSource,ResolvedBusinessSpec} from '../src/business-authoring-protocol.js';
const contracts=new URL('../../../../../../../research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan/contracts/',import.meta.url);
const reference=readFileSync(new URL('reference-business.alch',contracts),'utf8');
const resolve=(text:string)=>resolveBusinessSpec(parseBusinessSource(text));
const rejected=(text:string,family:string)=>assert.throws(()=>resolve(text),e=>{assert.ok(e instanceof BusinessSourceRejected);assert.ok(e.code.startsWith(family),e.message);assert.ok(e.line>=1);assert.ok(e.column>=1);return true;});
function sandbox(run:(root:string)=>void){const root=mkdtempSync(path.join(os.tmpdir(),'business-authoring-test-'));try{run(root);}finally{rmSync(root,{recursive:true,force:true});}}
test('differently named sorts/predicates resolve exclusively through explicit typed links',()=>{
  const resolved=resolve(reference);assertResolvedBusinessSpecCurrent(resolved);
  assert.equal(resolved.data.claims[0]!.sorts[0]!.type_ref,'Delivery');assert.equal(resolved.data.claims[0]!.predicates[0]!.definition_ref,'DeliveryEligibility');
  assert.equal(resolved.data.authority_effect,'none');assert.equal(resolved.business_sha256.length,64);
  rejected(reference.replace('sort DeliveryValue interpreted-as Delivery','sort DeliveryValue'),'BUSINESS_SYNTAX');
  rejected(reference.replace('defined-by DeliveryEligibility','defined-by Delivery'),'BUSINESS_REFERENCE');
  rejected(reference.replace('defined-by DeliveryEligibility','defined-by Permitted'),'BUSINESS_REFERENCE');
});
test('frozen reject vectors actually reject in B02 with their required diagnostic families',()=>{
  const vectors=JSON.parse(readFileSync(new URL('reject-vectors.json',contracts),'utf8')) as {cases:{id:string;replace:[string,string];family:string}[]};
  for(const vector of vectors.cases){assert.ok(reference.includes(vector.replace[0]),vector.id);rejected(reference.replace(...vector.replace),vector.family);}
});
test('typed references, Bool guards, bindings, returns and public exposure are all checked',()=>{
  for(const [before,after,family] of [
    ['identity id','identity absent','BUSINESS_REFERENCE'],['input delivery Delivery','input delivery Unknown','BUSINESS_REFERENCE'],
    ['boolean-field delivery.verified','boolean-field other.verified','BUSINESS_REFERENCE'],['boolean-field delivery.verified','boolean-field delivery.absent','BUSINESS_REFERENCE'],['boolean-field delivery.verified','boolean-field delivery.label','BUSINESS_TYPE'],
    ['interpreted-as Delivery','interpreted-as Unknown','BUSINESS_REFERENCE'],['constant current: DeliveryValue','constant current: Missing','BUSINESS_REFERENCE'],['predicate Permitted(DeliveryValue)','predicate Permitted(Missing)','BUSINESS_REFERENCE'],
    ['requirement DeliveryConfirmation','requirement Unknown','BUSINESS_REFERENCE'],['claim DeliveryReady','claim Unknown','BUSINESS_REFERENCE'],['bind current <- delivery','bind absent <- delivery','BUSINESS_REFERENCE'],['bind current <- delivery','bind current <- request','BUSINESS_REFERENCE'],
    ['requires CanConfirm(delivery: request)','requires Missing(delivery: request)','BUSINESS_REFERENCE'],['requires CanConfirm(delivery: request)','requires CanConfirm(other: request)','BUSINESS_REFERENCE'],['requires CanConfirm(delivery: request)','requires CanConfirm(delivery: other)','BUSINESS_REFERENCE'],
    ['returns request','returns delivery','BUSINESS_REFERENCE'],['invokes ConfirmDelivery','invokes Missing','BUSINESS_REFERENCE'],['proposition Permitted(current)','proposition Missing(current)','BUSINESS_REFERENCE'],
    ['supersedes none','supersedes DeliveryReady','BUSINESS_UNSUPPORTED'],['proposition Permitted(current)','proposition forall x: DeliveryValue: Permitted(x)','BUSINESS_UNSUPPORTED']
  ])rejected(reference.replace(before!,after!),family!);
  const extra='\nentity Other:\n  meaning "Other record."\n  id UInt64 meaning "Identity."\n  flag Bool meaning "Flag."\n  identity id\n';
  rejected(reference.replace('  output Delivery','  output Other')+extra,'BUSINESS_TYPE');
  rejected(reference.replace('sort DeliveryValue interpreted-as Delivery','sort DeliveryValue interpreted-as Other')+extra,'BUSINESS_TYPE');
  rejected(reference.replace('  input request Delivery','  input request Other').replace('  output Delivery','  output Other')+extra,'BUSINESS_TYPE');
});
test('normalization collisions and backend-ineligible many-to-one constant bindings reject',()=>{
  const extra='\ncapability OtherEntry:\n  invokes ConfirmDelivery\n  public-name confirm_delivery\n  audience public\n';rejected(reference+extra,'BUSINESS_AMBIGUOUS');
  rejected(reference.replace('  constant current: DeliveryValue','  constant current: DeliveryValue\n  constant other: DeliveryValue').replace('  proposition Permitted(current)','  proposition Permitted(current) and Permitted(other)').replace('  bind current <- delivery','  bind current <- delivery\n  bind other <- delivery'),'BUSINESS_AMBIGUOUS');
  rejected(reference.replace('  constant current: DeliveryValue','  constant current: DeliveryValue\n  constant other: DeliveryValue').replace('  proposition Permitted(current)','  proposition Permitted(current) and Permitted(other)'),'BUSINESS_REQUIRED');
});
test('ground Boolean composition/equality retains exact authored formula and sequence',()=>{
  const proposition='(Permitted(current) and not Permitted(current)) implies (current = current or Permitted(current))';
  const result=resolve(reference.replace('proposition Permitted(current)','proposition '+proposition));assert.equal(result.data.claims[0]!.proposition,proposition);
  rejected(reference.replace('proposition Permitted(current)','proposition '+ 'not '.repeat(65)+'Permitted(current)'),'BUSINESS_SOURCE_BUDGET');
});
test('business digest ignores physical formatting and identity declaration/field order, retaining prose and scenario order',()=>{
  const original=resolve(reference);
  const [header,...declarations]=reference.trimEnd().split('\n\n');
  const reordered=[header,...declarations.reverse()].join('\n\n')+'\n';
  assert.equal(resolve(reordered).business_sha256,original.business_sha256);
  const fields=reference.replace('  id UInt64 meaning "Delivery identity."\n  identity id\n  verified Bool meaning "Caller supplied eligibility flag."\n  label String meaning "Label retained in the acknowledgement."','  label String meaning "Label retained in the acknowledgement."\n  verified Bool meaning "Caller supplied eligibility flag."\n  identity id\n  id UInt64 meaning "Delivery identity."');
  assert.equal(resolve(fields).business_sha256,original.business_sha256);
  const comment='# external commentary\r\n'+reference.replaceAll('\n','\r\n');assert.equal(resolve(comment).business_sha256,original.business_sha256);assert.notEqual(resolve(comment).source.sha256,original.source.sha256);
  assert.notEqual(resolve(reference.replace('Delivery acknowledgements','Delivery receipts')).business_sha256,original.business_sha256);
  const another='  example another:\n    given "Another delivery."\n    when "ConfirmDelivery is requested."\n    then "Return supplied delivery."\n    why "Eligibility holds."\n';
  const added=reference.replace('  counterexample ineligible:',another+'  counterexample ineligible:');
  const swapped=added.replace(/(  example eligible:[\s\S]*?)(  example another:[\s\S]*?)(  counterexample)/,'$2$1$3');assert.notEqual(resolve(added).business_sha256,resolve(swapped).business_sha256);
  // Independent recursively sorted JSON computation, no helper from the producer.
  const {source_spans,obligations,...semantic}=original.data;
  const canonical=(v:unknown):string=>Array.isArray(v)?'['+v.map(canonical).join(',')+']':v!==null&&typeof v==='object'?'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical((v as Record<string,unknown>)[k])).join(',')+'}':JSON.stringify(v);
  const expected={...semantic,entities:semantic.entities.map(e=>({...e,fields:[...e.fields].sort((a,b)=>a.name.localeCompare(b.name))}))};
  assert.equal(original.business_sha256,createHash('sha256').update(canonical(expected)).digest('hex'));
});
test('registered resolved handles reject cloning, proxies, mutation and disposal reuse',()=>{
  const value=resolve(reference);
  for(const forged of [JSON.parse(JSON.stringify(value)),{...value},Object.create(value),new Proxy(value,{})]){
    assert.throws(()=>assertResolvedBusinessSpecCurrent(forged as ResolvedBusinessSpec),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_HANDLE');
    assert.throws(()=>disposeResolvedBusinessSpec(forged as ResolvedBusinessSpec),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_HANDLE');
  }
  assert.throws(()=>resolveBusinessSpec(JSON.parse(JSON.stringify(parseBusinessSource(reference))) as ParsedBusinessSource),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_HANDLE');
  assert.throws(()=>{(value as {business_sha256:string}).business_sha256='fake';},TypeError);
  disposeResolvedBusinessSpec(value);assert.throws(()=>assertResolvedBusinessSpecCurrent(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_DISPOSED');assert.throws(()=>disposeResolvedBusinessSpec(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_DISPOSED');
});
test('bounded file capture rechecks original bytes, ownership, currentness and disposal',()=>sandbox(root=>{
  mkdirSync(path.join(root,'models'));const file=path.join(root,'models/business.alch');writeFileSync(file,reference);
  const value=prepareBusinessSpecFile(root,'models/business.alch');assertResolvedBusinessSpecCurrent(value);assert.equal(value.source.path,'models/business.alch');assert.equal(value.source.text,reference);
  writeFileSync(file,reference.replace('Delivery acknowledgements','Changed delivery title'));assert.throws(()=>assertResolvedBusinessSpecCurrent(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_DRIFT');
  writeFileSync(file,reference);assert.throws(()=>assertResolvedBusinessSpecCurrent(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_DRIFT');
  const replacement=prepareBusinessSpecFile(root,'models/business.alch');renameSync(file,file+'.old');writeFileSync(file,reference);assert.throws(()=>assertResolvedBusinessSpecCurrent(replacement),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_DRIFT');
  disposeResolvedBusinessSpec(replacement);assert.throws(()=>assertResolvedBusinessSpecCurrent(replacement),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_DISPOSED');
}));
test('file preparation rejects traversal, leaf/parent/root symlinks, non-files, invalid UTF-8 and oversized files',()=>sandbox(root=>{
  const file=path.join(root,'business.alch');writeFileSync(file,reference);mkdirSync(path.join(root,'real'));writeFileSync(path.join(root,'real/business.alch'),reference);
  symlinkSync(file,path.join(root,'leaf.alch'));symlinkSync(path.join(root,'real'),path.join(root,'parent'));symlinkSync(root,path.join(root,'root-link'));
  for(const [base,key,code] of [[root,'../business.alch','BUSINESS_SOURCE_PATH'],[root,'leaf.alch','BUSINESS_SOURCE_SYMLINK'],[root,'parent/business.alch','BUSINESS_SOURCE_SYMLINK'],[path.join(root,'root-link'),'business.alch','BUSINESS_SOURCE_SYMLINK'],[root,'real','BUSINESS_SOURCE_PATH']] as const)assert.throws(()=>prepareBusinessSpecFile(base,key),e=>e instanceof BusinessSourceRejected&&e.code===code);
  writeFileSync(path.join(root,'bad.alch'),Buffer.from([0xc3,0x28]));assert.throws(()=>prepareBusinessSpecFile(root,'bad.alch'),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SYNTAX');
  writeFileSync(path.join(root,'large.alch'),Buffer.alloc(1048577));assert.throws(()=>prepareBusinessSpecFile(root,'large.alch'),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_BUDGET');
  const value=prepareBusinessSpecFile(root,'business.alch');unlinkSync(file);symlinkSync(path.join(root,'real/business.alch'),file);assert.throws(()=>assertResolvedBusinessSpecCurrent(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_SYMLINK');
}));
test('independent B10 domains parse and resolve with their original complete obligations',()=>{
  for(const domain of ['delivery-acknowledgement','publication-consent']){
    const source=readFileSync(new URL('./fixtures/business-authoring/'+domain+'/business.alch',import.meta.url),'utf8');const result=resolve(source);assertResolvedBusinessSpecCurrent(result);
    assert.equal(result.data.obligations.length,source.split('\n').filter(s=>s.trim()&&!s.trimStart().startsWith('#')).length);
    assert.equal(result.data.entities[0]!.id,'Submission');assert.equal(result.data.definitions[0]!.id,'Eligibility');
  }
});
