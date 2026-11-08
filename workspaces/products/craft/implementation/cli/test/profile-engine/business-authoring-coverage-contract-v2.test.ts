import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {sha256} from '../../src/profile-engine/contracts.js';
import {inventoryBusinessSourceContractV2,planBusinessOutputsV2} from '../../src/profile-engine/business-authoring-coverage-contract-v2.js';
// Source/output contract checks only. Original owner/graph/native/installed joins are later tasks.
// Open Questions: docs/BUSINESS-COVERAGE-V2.md.
const sourceText=readFileSync(new URL('fixtures/u0-v2/business.alch',import.meta.url),'utf8');
const source={path:'business.alch',text:sourceText,sha256:sha256(sourceText),bytes:Buffer.byteLength(sourceText)};
const spec=JSON.parse(readFileSync(new URL('fixtures/u0-v2/spec.json',import.meta.url),'utf8'));
const clone=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
test('C04 zero-claim source retains every original fact plus explicit executable owner obligations',()=>{
 assert.equal(spec.claims.length,0);const inventory=inventoryBusinessSourceContractV2(spec,source);
 assert.equal(inventory.obligations.filter(row=>row.kind==='authored-fact').length,spec.obligations.length);
 for(const kind of ['entity-shape','condition','guard','result','rejection','effects','entry','permission']){
  const row=inventory.obligations.find(row=>row.kind===kind);assert.ok(row);assert.ok(row.origins.length);assert.equal(row.state,'producer-required');
  for(const origin of row.origins)assert.ok(spec.source_spans.some((span:any)=>span.selector===origin.selector&&span.source===origin.source&&span.source_sha256===origin.sha256));
 }
 assert.equal(Object.hasOwn(inventory,'accepted'),false);assert.equal(Object.hasOwn(inventory,'complete'),false);assert.ok(Object.isFrozen(inventory));
});
test('C04 missing, duplicated, substituted or drifted original facts cannot shrink the denominator',()=>{
 for(const mutate of [(v:any)=>v.obligations.pop(),(v:any)=>v.source_spans.pop(),(v:any)=>{v.source_spans[1]={...v.source_spans[0],selector:v.source_spans[1].selector};},(v:any)=>{v.obligations[1].span_selector=v.obligations[0].span_selector;},(v:any)=>{v.source_spans[0].text='invented';},(v:any)=>{v.source_spans[0].source_sha256='a'.repeat(64);}]){
  const value=clone(spec);mutate(value);assert.throws(()=>inventoryBusinessSourceContractV2(value,source),/COVERAGE/);
 }
 assert.throws(()=>inventoryBusinessSourceContractV2(spec,{...source,text:source.text+'\n# drift'}),/COVERAGE_SOURCE/);
});
test('C04 explicit required code and graph outputs start pending actual producers',()=>{
 const plan=planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind:'business-system-bridge',requiredness:'required'}]);
 assert.equal(plan.mode,'code-only');assert.deepEqual(plan.outputs.map(row=>row.state),['pending-producer','pending-producer']);
 assert.equal(Object.hasOwn(plan,'complete'),false);assert.ok(Object.isFrozen(plan));
 assert.throws(()=>planBusinessOutputsV2([]),/OUTPUT_REQUEST/);
 assert.throws(()=>planBusinessOutputsV2([{kind:'business-graph',requiredness:'required'}]),/CODE_REQUIRED/);
 assert.throws(()=>planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind:'code',requiredness:'optional'}]),/OUTPUT_REQUEST/);
});
test('C04 unsupported required formal exporters reject while optional diagnostics do not supply execution',()=>{
 for(const kind of ['base-model','conjecture-problems'] as const){
  assert.throws(()=>planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind,requiredness:'required'}]),/UNSUPPORTED_REQUIRED/);
  const plan=planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind,requiredness:'optional'}]);assert.equal(plan.outputs[0]!.state,'pending-producer');assert.equal(plan.outputs[1]!.state,'unsupported-optional');
 }
 assert.throws(()=>planBusinessOutputsV2([{kind:'code',requiredness:'required',ready:true}] as any),/OUTPUT_REQUEST/);
});
test('C04 no accessor/proxy/callback can manufacture source/output readiness',()=>{
 let calls=0;assert.throws(()=>planBusinessOutputsV2([{get kind(){calls++;return 'code';},requiredness:'required'}] as any));assert.equal(calls,0);
 assert.throws(()=>planBusinessOutputsV2(new Proxy([{kind:'code',requiredness:'required'}],{}) as any),/PROFILE_DATA_PROXY/);
 assert.throws(()=>inventoryBusinessSourceContractV2(spec,{...source,callback:()=>true} as any),/PROFILE_DATA_TYPE/);
});
test('C04 actual inventories/plans and strict support/result evidence agree with standard schemas',()=>{
 const h='a'.repeat(64),inventory=inventoryBusinessSourceContractV2(spec,source),plan=planBusinessOutputsV2([{kind:'code',requiredness:'required'}]);
 const support={schema_version:'craft.business-support-cell/v2-candidate',cell_id:'u0',source_contract:'alchlang.business-spec/v2-candidate',recipe:'direct-entity-bool-operation/v2-candidate',descriptor:'node-http-entry-u0-v4',abi:'craft.u0.pure-submission/v1-candidate',entry_access:'public',effects:'none',evidence:[{stage:'declared',contract_ref:'C01-C04'}],authority_effect:'none'};
 const rows=[{schema:'business-coverage-v2',value:inventory,valid:true},{schema:'business-output-v2',value:plan,valid:true},{schema:'business-support-cell-v2',value:support,valid:true},{schema:'business-support-cell-v2',value:{...support,ready:true},valid:false},{schema:'business-support-cell-v2',value:{...support,evidence:[{stage:'installed-tested',candidate_sha256:h}]},valid:false},{schema:'business-support-cell-v2',value:{...support,evidence:[{stage:'proved',receipt_sha256:h}]},valid:false},{schema:'business-output-result-v2',value:{schema_version:'craft.business-output-result/v2-candidate',rows:[{kind:'code',requiredness:'required',state:'failed-required',artifact:null}],authority_effect:'none'},valid:true},{schema:'business-output-result-v2',value:{schema_version:'craft.business-output-result/v2-candidate',rows:[{kind:'code',requiredness:'required',state:'produced',artifact:null}],authority_effect:'none'},valid:false}];
 rows.push({schema:'business-output-result-v2',value:{schema_version:'craft.business-output-result/v2-candidate',rows:[{kind:'code',requiredness:'required',state:'unsupported-optional',artifact:null}],authority_effect:'none'},valid:false});
 const check=spawnSync('python3',['-c',"import json,sys; from pathlib import Path; from jsonschema import Draft202012Validator; rows=json.load(sys.stdin); root=Path(sys.argv[1]);\nfor row in rows:\n schema=json.loads((root/(row['schema']+'.schema.json')).read_text()); Draft202012Validator.check_schema(schema); actual=not list(Draft202012Validator(schema).iter_errors(row['value'])); assert actual==row['valid'],row['schema']",new URL('../../contracts/',import.meta.url).pathname],{input:JSON.stringify(rows),encoding:'utf8'});
 assert.equal(check.status,0,check.stderr);
});
