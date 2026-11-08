import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {parseBusinessSource} from '../src/business-authoring-parser.js';
import {resolveBusinessSpec,prepareBusinessSpecFile,disposeResolvedBusinessSpec} from '../src/business-authoring-resolve.js';
import {lowerBusinessFormalSemantics} from '../src/business-authoring-semantics.js';
import {lowerBusinessBehavior,assertBusinessBehaviorCurrent,type BusinessBehavior} from '../src/business-authoring-behavior.js';
import {BusinessSourceRejected} from '../src/business-authoring-model.js';

// Normalized correspondence only; no acceptance/native/API execution. Open questions: B06-B10.
const source=readFileSync(new URL('./fixtures/business-authoring/delivery-acknowledgement/business.alch',import.meta.url),'utf8');
const lower=(text=source)=>lowerBusinessBehavior(lowerBusinessFormalSemantics(resolveBusinessSpec(parseBusinessSource(text))));

test('one explicit Rule guards complete whole-input/output structures and retains authored continuation',()=>{
 const value=lower();assertBusinessBehaviorCurrent(value);const operation=value.data.operations[0]!;
 assert.deepEqual(operation.input.type,{kind:'entity',entity_ref:'Submission',identity:'id',fields:[{name:'id',type:'UInt64'},{name:'label',type:'String'},{name:'recipient_confirmed',type:'Bool'},{name:'verified',type:'Bool'}]});
 assert.deepEqual(operation.output,operation.input.type);assert.deepEqual(operation.result,{root:'request',path:[],type:operation.input.type});
 assert.equal(operation.guards.length,1);assert.deepEqual(operation.guards[0],{rule_ref:'CanProcess',claim_ref:'Ready',parameter:{name:'item',type:operation.input.type},argument:{root:'request',path:[]}});
 assert.deepEqual(operation.effects,[]);assert.deepEqual(operation.failure,{kind:'continuation-metadata',continuation:'delivery-verification-required',executable:false});
 assert.equal(value.data.formal_sha256,value.formal.derivation_sha256);assert.equal(value.data.business_sha256,value.business.business_sha256);
});

test('compound Boolean meaning stays in its single Rule rather than becoming multiple guards',()=>{
 const text=source.replace('  proposition DeliveryPermitted(current)','  proposition DeliveryPermitted(current) and not DeliveryPermitted(current)');
 const value=lower(text),claim=value.formal.data.claims[0]!;
 assert.equal(claim.proposition.kind,'and');assert.equal(value.data.operations[0]!.guards.length,1);
 assert.equal(claim.proposition_source,'DeliveryPermitted(current) and not DeliveryPermitted(current)');
});

test('actors remain informational and failure tokens do not declare executable recovery',()=>{
 const text=source.replace('actor "Dispatch API caller"','actor "administrator; retry service owner"').replaceAll('delivery-verification-required','retry_forever');
 const value=lower(text);assert.equal(value.data.actor_semantics,'informational-only');
 assert.deepEqual(value.data.contexts,value.business.data.requirements);
 assert.equal(value.data.operations[0]!.failure.continuation,'retry_forever');assert.equal(value.data.operations[0]!.failure.executable,false);
 assert.deepEqual(Object.keys(value.data).sort(),['schema_version','normalization_contract','model_id','business_sha256','formal_sha256','operations','exposures','contexts','actor_semantics','authority_effect'].sort());
 assert.ok(!('authentication' in value.data)&&!('recovery_policy' in value.data));
});

test('exposure is copied exactly; unexposed declarations do not acquire public entries',()=>{
 const extra=source.slice(source.indexOf('operation Process:'),source.indexOf('capability Entry:')).replace('operation Process:','operation InternalProcess:');
 const value=lower(source+'\n'+extra);assert.equal(value.data.operations.length,2);assert.equal(value.data.exposures.length,1);
 assert.deepEqual(value.data.exposures,value.business.data.capabilities);
 assert.equal(value.data.exposures[0]!.operation_ref,'Process');
});

test('effects, subset/computed results, protected access and wrong guard/input structures reject',()=>{
 const cases:[string,string][]=[
  ['  effects none','  effects write Submission'],['  returns request','  returns request.label'],['  returns request','  returns compute_label(request)'],
  ['  audience public','  audience protected'],['  requires CanProcess(item: request)','  requires CanProcess(other: request)'],
  ['  requires CanProcess(item: request)','  requires CanProcess(item: request.label)'],
  ['  requires CanProcess(item: request)','  requires CanProcess(item: request)\n  requires CanProcess(item: request)'],
  ['  input request Submission','  input request Other'],
 ];
 for(const [before,after] of cases)assert.throws(()=>lower(source.replace(before,after)),e=>e instanceof BusinessSourceRejected&&e.code.startsWith('BUSINESS_'));
 const other='\nentity Other:\n  meaning "Another structure."\n  id UInt64 meaning "Identity."\n  identity id\n  verified Bool meaning "Flag."\n';
 assert.throws(()=>lower(source.replace('  output Submission','  output Other')+other),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_TYPE');
});

test('registered behavior rejects clones/proxies and is deeply immutable',()=>{
 const value=lower();
 for(const forged of [JSON.parse(JSON.stringify(value)),{...value},Object.create(value),new Proxy(value,{})])assert.throws(()=>assertBusinessBehaviorCurrent(forged as BusinessBehavior),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_HANDLE');
 assert.throws(()=>{(value.data.operations[0]!.effects as unknown as unknown[]).push('write');},TypeError);
 assert.throws(()=>lowerBusinessBehavior(JSON.parse(JSON.stringify(value.formal))),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_HANDLE');
 disposeResolvedBusinessSpec(value.business);assert.throws(()=>assertBusinessBehaviorCurrent(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_DISPOSED');
});

test('file-byte drift invalidates the entire formal/behavior chain',t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'business-behavior-'));t.after(()=>rmSync(root,{recursive:true,force:true}));writeFileSync(path.join(root,'business.alch'),source);
 const business=prepareBusinessSpecFile(root,'business.alch'),formal=lowerBusinessFormalSemantics(business),value=lowerBusinessBehavior(formal);
 writeFileSync(path.join(root,'business.alch'),source+'\n# changed original bytes\n');
 assert.throws(()=>assertBusinessBehaviorCurrent(value),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_DRIFT');
 assert.throws(()=>lowerBusinessBehavior(formal),e=>e instanceof BusinessSourceRejected&&e.code==='BUSINESS_SOURCE_DRIFT');
});
