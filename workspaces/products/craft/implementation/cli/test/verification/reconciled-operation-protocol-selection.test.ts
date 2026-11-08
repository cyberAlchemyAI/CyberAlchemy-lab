import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {mixedWorkflowPublicFixture} from '../helpers/workflow-public-mixed.ts';
import {operationFixture,valueOperationFixture} from '../helpers/cross-generator-operation.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorOperationControls,checkCrossGeneratorOperationObservations,crossGeneratorOperationProbe} from '../../src/verification/reconciled-cross-generator-operation.ts';
import {createOperationCases,operationVectorCaseIds} from '../../src/verification/reconciled-operation-cases.ts';
import {createOperationBinding} from '../../src/verification/reconciled-operation-binding.ts';
import {getCrossGeneratorSource} from '../../src/verification/cross-generator-sources.ts';
import {CROSS_GENERATOR_OPERATION_RUNNER} from '../../src/verification/reconciled-cross-generator-operation-runner.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const prepare=(graph:any,plan:any)=>{
 const boundary=createCrossGeneratorBoundary(graph,plan,getCrossGeneratorSource('verification'));
 return createCrossGeneratorOperationControls(graph,plan,boundary,getCrossGeneratorSource('operation'),getCrossGeneratorSource('operation_protocol'));
};
test('generic selection preserves complete semantic cases and matches the tested mixed witness policy',t=>{
 const f=mixedWorkflowPublicFixture(t),plan=planCompiledReconciledProject(f.graph,f.selection),first=prepare(f.graph,plan),second=prepare(f.graph,plan);
 assert.equal(first.controls_sha256,second.controls_sha256);
 const sourceRows=f.graph.nodes.filter(n=>n.kind==='Operation').map(n=>createOperationCases(f.graph,plan,createOperationBinding(n,f.graph,plan)));
 assert.equal(sha256(canonicalJson(sourceRows)),'fcf43890242d5fe1a87b73536aca7c224a31282b0767a2fd2ce6ae006bd0cb50');
 // Current complete source census; deliberately separate from historical diagnostics.
 const current=[
  {
    "selector": "commerce:oversized-perform",
    "selection": {
      "obligation_count": 2104,
      "policy": "obligation-boundary-v1",
      "reason": "selected",
      "selected_case_count": 1257,
      "selected_ids_sha256": "69642044831e023106d4eb7ec862f18b85fecc7a17a69228ca3e29f01739389e",
      "source_case_count": 1810,
      "source_cases_sha256": "1a9cf1c503a983785ad687ad44c860220a6c3533c64822a64b3458accec644b8"
    }
  },
  {
    "selector": "commerce:oversized-undo",
    "selection": {
      "obligation_count": 2098,
      "policy": "obligation-boundary-v1",
      "reason": "selected",
      "selected_case_count": 1260,
      "selected_ids_sha256": "14ffd12e31d05f5599221ba42acbf01b3376cc408b2bfeed614da6c5c5e41011",
      "source_case_count": 1813,
      "source_cases_sha256": "bc419208839e852e0ffd543a07efb9a798fd6285c8a93ad4217074dedbe76ca2"
    }
  },
  {
    "selector": "commerce:perform",
    "selection": {
      "obligation_count": 2104,
      "policy": "obligation-boundary-v1",
      "reason": "selected",
      "selected_case_count": 1257,
      "selected_ids_sha256": "69642044831e023106d4eb7ec862f18b85fecc7a17a69228ca3e29f01739389e",
      "source_case_count": 1810,
      "source_cases_sha256": "ede50163fec43d9fdc74cd09ce431365f2563bdd064c157428d25c74ad0d5be2"
    }
  },
  {
    "selector": "commerce:undo",
    "selection": {
      "obligation_count": 2098,
      "policy": "obligation-boundary-v1",
      "reason": "selected",
      "selected_case_count": 1260,
      "selected_ids_sha256": "14ffd12e31d05f5599221ba42acbf01b3376cc408b2bfeed614da6c5c5e41011",
      "source_case_count": 1813,
      "source_cases_sha256": "43b6da42fc5f641e115041adf82c75bea3dbc99e6180efaccc054cd41bc8b722"
    }
  }
];
 assert.deepEqual(first.rows.map(r=>r.selector),current.map(r=>r.selector));
 for(const row of first.rows){
  if(row.state!=='ready')assert.fail(row.reason);assert.equal(row.state,'ready');
  assert.deepEqual(row.selection,current[first.rows.indexOf(row)]!.selection);
  const source=sourceRows[first.rows.indexOf(row)]!,byId=new Map(source.cases.map(c=>[c.id,c]));
  assert.ok(Object.isFrozen(operationVectorCaseIds(source)));
  assert.throws(()=>operationVectorCaseIds(structuredClone(source)),/registered source/);
  const vectors=new Set(operationVectorCaseIds(source)),selected=new Set(row.cases.map(c=>c.id));
  for(const c of source.cases)if(!vectors.has(c.id))assert.ok(selected.has(c.id),'non-vector retained '+c.id);
  for(const c of row.cases){
   const expected=byId.get(c.id)!.expected;
   if(expected.kind!=='value')assert.fail('complete semantic value required');
   assert.equal(canonicalJson(c.expected.semantic),expected.value);
  }
 }
 t.diagnostic(JSON.stringify(first.rows.map(r=>r.state==='ready'?{selector:r.selector,...r.selection}:{selector:r.selector,reason:r.reason})));
});
test('historical mixed selection diagnostic remains unchanged and is not current qualification',()=>{
 const bytes=fs.readFileSync(path.resolve(import.meta.dirname,'../../../../development/reconciliation-v1/profile-compiler-reconciliation/evidence/verification-efficiency/SELECTION-RESULT.json'));
 assert.equal(sha256(bytes),'1e455cef39f750a61ea699e4123ef66160654830e0c3b11c7e1c9839ccc9bab2');
 const evidence=JSON.parse(bytes.toString('utf8'));
 assert.equal(evidence.schema_version,'diagnostic.operation-boundary-selection/v1');
 assert.equal(evidence.authority_effect,'none');assert.equal(evidence.production_changes,false);
 assert.deepEqual(evidence.rows.map((r:any)=>[r.selector,r.cases,r.selected_cases,r.selected_ids_sha256]),[
  ['commerce:oversized-perform',1804,1251,'5c578de6b4ae320e7e25a684ac3480c7fbb0087c8d30eb71746bc93dfe897061'],
  ['commerce:oversized-undo',1807,1254,'9112af3ae8ea8b9a41490d149cc17d9a208298d172a519490e41aff68d0895c4'],
  ['commerce:perform',1804,1251,'5c578de6b4ae320e7e25a684ac3480c7fbb0087c8d30eb71746bc93dfe897061'],
  ['commerce:undo',1807,1254,'9112af3ae8ea8b9a41490d149cc17d9a208298d172a519490e41aff68d0895c4']
 ]);
});
test('selection derives the result input from source bindings rather than fixture parameter names',t=>{
 const f=mixedWorkflowPublicFixture(t),selection=structuredClone(f.selection);
 for(const operation of selection.operations){
  operation.inputs=[{...operation.inputs[0]!,name:'subject'}];
  operation.result={...operation.result,value:{op:'path',root:'subject',properties:[]}};
 }
 for(const workflow of selection.workflows)for(const call of [...workflow.steps,...workflow.compensations])for(const argument of call.arguments)if(argument.parameter==='amount')argument.parameter='subject';
 const plan=planCompiledReconciledProject(f.graph,selection),controls=prepare(f.graph,plan);
 for(const row of controls.rows){if(row.state!=='ready')assert.fail(row.reason);assert.equal(row.state,'ready');assert.equal(row.selection.reason,'selected');assert.ok(row.cases.length<row.selection.source_case_count);}
});
test('effectful and multiple-input record-free Operations retain every direct source case',t=>{
 for(const make of [operationFixture,valueOperationFixture]){
  const f=make(t),{graph,plan}=f.compile(),controls=prepare(graph,plan);
  for(const row of controls.rows){
   if(row.state!=='ready')assert.fail(row.reason);assert.equal(row.state,'ready');
   const source=createOperationCases(graph,plan,createOperationBinding(graph.nodes.find(n=>n.selector===row.selector)!,graph,plan));
   assert.equal(row.selection.reason,'inapplicable-full-family');
   assert.deepEqual(row.cases.map(c=>c.id),source.cases.map(c=>c.id));
  }
 }
});
test('selected mixed families execute together under unchanged native limits and reject hidden protocol defects',t=>{
 const f=mixedWorkflowPublicFixture(t),plan=planCompiledReconciledProject(f.graph,f.selection),controls=prepare(f.graph,plan);
 assert.ok(controls.rows.every(r=>r.state==='ready'));
 const root=path.join(f.root,'selection-native'),src=path.join(root,'source'),out=path.join(root,'compiled');
 fs.mkdirSync(root);
 const paths=[...new Set(controls.rows.flatMap(r=>r.modules.map(m=>m.relative_path)))];
 for(const p of paths){const artifact=plan.resolved.artifacts.find(a=>a.relative_path===p)!;const target=path.join(src,p);fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,artifact.content);}
 const config=path.join(root,'tsconfig.json'),input=path.join(root,'input.json'),runner=path.join(root,'observe.mjs');
 fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',rootDir:src,outDir:out,types:[]},files:paths.map(p=>path.join(src,p))}));
 const payload=JSON.stringify(crossGeneratorOperationProbe(controls));assert.ok(Buffer.byteLength(payload)<16777216);
 fs.writeFileSync(input,payload);fs.writeFileSync(runner,CROSS_GENERATOR_OPERATION_RUNNER);
 const image=nativeToolchainImage();
 assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',root,image];
 const run=(args:string[])=>execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:60000,maxBuffer:16777216});
 const compile=()=>run(['tsc','--project',config]);compile();
 const output=run(['node',runner,input,out]),baseline=JSON.parse(output),verified=checkCrossGeneratorOperationObservations(controls,baseline);
 assert.equal(verified.tested_operation_count,4);assert.equal(verified.tested_case_count,5034);assert.ok(Buffer.byteLength(output)<16777216);
 const row=controls.rows.find(r=>r.selector==='commerce:perform')!,file=path.join(src,row.provider_path),original=fs.readFileSync(file,'utf8');
 for(const [name,mutant]of [
  ['empty-list-owned-validation',original.replace('    own0(result);','    if(result.lines.length!==0)own0(result);')],
  ['duplicate-guard',original.replace(/if\(!((guard\d+)\(\{[^\n]+\}\))\)/,'if(!($1,$1))')]
 ]){
  assert.notEqual(mutant,original);fs.writeFileSync(file,mutant!);compile();const observed=JSON.parse(run(['node',runner,input,out]));
  if(name==='duplicate-guard')assert.deepEqual(observed.rows.map((r:any)=>r.cases.map((c:any)=>c.semantic)),baseline.rows.map((r:any)=>r.cases.map((c:any)=>c.semantic)));
  assert.throws(()=>checkCrossGeneratorOperationObservations(controls,observed),/observation mismatch/);
 }
 fs.writeFileSync(file,original);
 const wrapper=path.join(src,row.relative_path),old=fs.readFileSync(wrapper,'utf8');
 const replaced=old.replace('Object.assign(execute,','Object.assign((...args:Parameters<typeof execute>)=>execute(...args),');
 assert.notEqual(replaced,old);fs.writeFileSync(wrapper,replaced);compile();
 const observed=JSON.parse(run(['node',runner,input,out]));assert.throws(()=>checkCrossGeneratorOperationObservations(controls,observed),/observation mismatch/);
 t.diagnostic(JSON.stringify({input_bytes:Buffer.byteLength(payload),output_bytes:Buffer.byteLength(output),cases:verified.tested_case_count,mutants:3}));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
