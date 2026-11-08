import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import test from 'node:test';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture} from '../helpers/workflow-values.ts';
import {nativeWorkflowProtocol,workflowNativeDefinitions} from '../helpers/cross-generator-workflow-native.ts';
import {createWorkflowProtocolReference} from '../../src/verification/reconciled-cross-generator-workflow-reference.ts';
import {expandWorkflowProtocolCase} from '../../src/verification/reconciled-cross-generator-workflow.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';

test('original scalar ESM Workflow preserves actual call identity and complete semantics',t=>{
 const n=nativeWorkflowProtocol(workflowFixture(t));n.auditAll();const actual=n.observe(),result=n.check(actual);
 assert.equal(result.tested_case_count,133);assert.equal(result.tested_call_count,998);assert.equal(actual.rows[0]!.identity.workflow,true);
 t.diagnostic(JSON.stringify(result));
});
test('original complete compound ESM family passes all four batches in both layouts',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const n=nativeWorkflowProtocol(workflowValuesFixture(t,{events:true}),layout);n.auditAll();
  const actual=n.observe(),result=n.check(actual);
  assert.equal(result.tested_case_count,12472);assert.equal(result.tested_call_count,20369);assert.equal(actual.rows[0]!.batches.length,4);
  assert.equal(actual.rows[0]!.identity.operations.every((o:any)=>o.original),true);
  t.diagnostic(JSON.stringify({layout,...result}));
  if(layout==='domain'){
   // A copied object-valued Operation result keeps semantic data but loses the original handoff.
   const file=path.join(n.src,n.row.provider_path),original=fs.readFileSync(file,'utf8');
   const changed=original.replace('Object.getOwnPropertyDescriptor(raw,"value")!.value','({...Object.getOwnPropertyDescriptor(raw,"value")!.value})');
   assert.notEqual(changed,original);fs.writeFileSync(file,changed);n.compile();
   const p=structuredClone(n.probes[0]!);p.batch={index:0,start:0,count:1};p.rows[0]!.batches=[p.batch];p.rows[0]!.cases=p.rows[0]!.cases.slice(0,1);
   const observed=n.observe([p]).rows[0]!.cases[0],expected=n.row.cases[0]!.expected;
   assert.equal(observed.semantic_sha256,expected.semantic_sha256);
   assert.notDeepEqual(observed.calls,expected.calls);
  }
 });
});
test('original no-compensation ESM Workflow retains all forward behavior without recovery execution',t=>{
 const n=nativeWorkflowProtocol(workflowFixture(t,{noCompensations:true}));n.auditAll();n.check(n.observe());
});
test('strict-compiling call, dependency and original wrapper mutants cannot pass identity comparison',t=>{
 const n=nativeWorkflowProtocol(workflowFixture(t)),file=path.join(n.src,n.row.provider_path),original=fs.readFileSync(file,'utf8'),wrapper=path.join(n.src,n.row.relative_path),oldWrapper=fs.readFileSync(wrapper,'utf8');
 // Independent hostile-behavior probes deliberately bypass audit approval after mutation.
 const mutants=[
  original.replace('const input=material.capture(parameters);','const input=(material.capture(parameters),material.capture(parameters));'),
  original.replace('raw=await call0(args,dep0);','raw=await call0({...args},dep0);'),
  original.replace('raw=await call0(args,dep0);','raw=await call0(args,{...dep0});'),
  original.replace('material.result(input,results)','(0n as ReturnType<typeof material.result>)')
 ];
 for(const changed of mutants){
  assert.notEqual(changed,original);fs.writeFileSync(file,changed);n.compile();
  let actual;try{actual=n.observe();}catch{continue;}
  assert.throws(()=>n.check(actual),/observation mismatch/);
 }
 fs.writeFileSync(file,original);
 const changed=oldWrapper.replace('Object.assign(execute,','Object.assign(((...args:Parameters<typeof execute>)=>execute(...args)),');
 assert.notEqual(changed,oldWrapper);fs.writeFileSync(wrapper,changed);n.compile();assert.throws(()=>n.check(n.observe()),/observation mismatch/);
});
test('missing or reordered batches never produce a complete family observation',t=>{
 const n=nativeWorkflowProtocol(workflowFixture(t)),p=structuredClone(n.probes[0]!);
 const wrong=structuredClone(p);wrong.batch.index=1;assert.throws(()=>n.observe([wrong]));
 const omitted=structuredClone(p);omitted.rows[0].cases.pop();assert.throws(()=>n.observe([omitted]));
 const reordered=structuredClone(p);reordered.rows[0].cases.reverse();assert.throws(()=>n.observe([reordered]));
 const drift=structuredClone(p);drift.protocol_sha256='0'.repeat(64);assert.throws(()=>n.observe([drift]));
 assert.notEqual(canonicalJson(p),canonicalJson(omitted));
});

test('original equal-valued captures reused across batches fail identity even when complete semantics are unchanged',t=>{
 const n=nativeWorkflowProtocol(workflowFixture(t)),seed=n.row.cases[0]!,reference=createWorkflowProtocolReference(n.graph,n.plan,n.surface,n.row.selector,workflowNativeDefinitions.protocol);
 const plan=[{index:0,start:0,count:1},{index:1,start:1,count:1}];
 // Two-case identity stress probe, not a replacement for the complete 133-case family.
 const probes=plan.map(batch=>{const p=structuredClone(n.probes[0]!);p.batch=batch;p.rows[0]!.batches=plan;p.rows[0]!.cases=[{id:'case-'+batch.index,data:seed.data}];return p;});
 const clean=n.observe(probes),expected=reference.expected('case-1',expandWorkflowProtocolCase(n.row.recipes,seed.data));
 assert.deepEqual(clean.rows[0]!.cases[1].calls,expected.calls);
 assert.throws(()=>n.check(clean),/observation mismatch/,'a self-consistent prefix is still not the full family');
 assert.throws(()=>n.observe(probes.slice(0,1)),/incomplete family/);
 assert.throws(()=>n.observe([...probes].reverse()),/batch identity\/order/);
 assert.throws(()=>n.observe([probes[0],probes[0]]),/batch identity\/order/);
 const drift=structuredClone(probes);drift[1]!.rows[0]!.modules[0]!.sha256='0'.repeat(64);
 assert.throws(()=>n.observe(drift),/batch identity\/order/);
 const file=path.join(n.src,n.row.material_path),original=fs.readFileSync(file,'utf8');
 const changed=original.replace('export const capture=(value:WorkflowInput):CapturedInput=>{','let cached:CapturedInput|undefined;\nexport const capture=(value:WorkflowInput):CapturedInput=>{if(cached)return cached;')
  .replace('inputs.add(input);return input;','inputs.add(input);cached=input;return input;');
 assert.notEqual(changed,original);fs.writeFileSync(file,changed);n.compile();
 const mutant=n.observe(probes);
 assert.deepEqual(mutant.rows[0]!.cases.map((c:any)=>c.semantic_sha256),clean.rows[0]!.cases.map((c:any)=>c.semantic_sha256));
 assert.notDeepEqual(mutant.rows[0]!.cases[1].calls,expected.calls);
 assert.deepEqual(mutant.rows[0]!.cases[1].calls[0].result.value,['identity','return:case-0:0']);
 assert.deepEqual(clean.rows[0]!.cases[1].calls[0].result.value,['identity','return:case-1:0']);
});
