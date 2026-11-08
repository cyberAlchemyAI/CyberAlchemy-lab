import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {publicFixture,publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {publishReconciledProject} from '../../src/generation/reconciled-output.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {createReconciledSemanticControls,renderSemanticCases,checkSemanticObservations,semanticModulePaths} from '../../src/verification/reconciled-semantic-controls.ts';
import {executeReconciledVerification} from '../../src/verification/reconciled-execution.ts';
const project=path.resolve(import.meta.dirname,'../../../..');

test('compiling semantic mutants, forbidden effects and late semantic workspace drift cannot pass',t=>{
 const f=fixture(t),n=nativeContext(f),forbidden=path.join(f.root,'forbidden-effect'),secret=path.join(f.root,'private-input');
 fs.writeFileSync(secret,'not-an-input-to-generated-code');
 const reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[],forbidden=${JSON.stringify(forbidden)},secret=${JSON.stringify(secret)};
 const additions={
  write:"(await import('node:fs')).writeFileSync("+JSON.stringify(forbidden)+",'forbidden');",
  read:"(await import('node:fs')).readFileSync("+JSON.stringify(secret)+",'utf8');",
  network:"(await import('node:net')).connect({host:'127.0.0.1',port:9});",
  child:"(await import('node:child_process')).execFileSync(process.execPath,['-e','throw Error(1)']);"
 };
 for(const mode of ['math','write','read','network','child','runner-drift','cases-drift','module-drift','extra-file','pre-emit-source']){
  const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);let runs=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated semantic controls'};
   const result=original(command,args,settings);
   if(result.status===0&&String(args[0]).endsWith('observe.mjs')&&mode==='pre-emit-source')fs.appendFileSync(path.join(settings.cwd,'domain/features/alpha/src/domain/calculations/add.provider.ts'),' ');
   const project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')){
    const root=path.dirname(project),provider=path.join(root,'modules/domain/features/alpha/src/domain/calculations/add.provider.js');
    if(mode==='math'){const old=fs.readFileSync(provider,'utf8'),changed=old.replace(/return v0;/,'return 0n;');if(old===changed)throw Error('semantic mutant was not installed');fs.writeFileSync(provider,changed);}
    if(additions[mode])fs.appendFileSync(provider,'\\n'+additions[mode]+'\\n');
   }
   if(args.includes('--permission')){
    runs++;
    if(result.status===0){
     if(mode==='runner-drift')fs.appendFileSync(path.join(settings.cwd,'runner.mjs'),' ');
     if(mode==='cases-drift')fs.appendFileSync(path.join(settings.cwd,'cases.json'),' ');
     if(mode==='module-drift')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/calculations/add.provider.js'),' ');
     if(mode==='extra-file')fs.writeFileSync(path.join(settings.cwd,'extra.json'),'{}');
    }
   }
   return result;
  };syncBuiltinESMExports();
  try{const report=executeReconciledVerification(graph,plan,tools);reports.push({mode,runs,report});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,runs} of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);assert.equal(report.result,'fail',mode);
  if(['math','write','read','network','child','pre-emit-source'].includes(mode)){
   assert.equal(check('selected-generator-semantic-controls').result,'fail',mode);
   if(['write','read','network','child'].includes(mode))assert.match(check('selected-generator-semantic-controls').reason,/ERR_ACCESS_DENIED/);
   if(mode==='math')assert.match(check('selected-generator-semantic-controls').reason,/observation mismatch/);
   if(mode==='pre-emit-source')assert.equal(runs,0);
  }else{
   assert.equal(check('semantic-workspace-currentness').result,'fail',mode);
   assert.equal(check('selected-generator-semantic-controls').result,'not_evaluable',mode);
   assert.ok(check('selected-generator-semantic-controls').blocked_by.includes('semantic-workspace-currentness'),mode);
  }
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.equal(fs.existsSync(forbidden),false);assert.equal(fs.readFileSync(secret,'utf8'),'not-an-input-to-generated-code');
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});
test('late drift invalidates partial semantic evidence as well as fully covered evidence',t=>{
 const original=publicFixture(t),f={...original,temp:original.root},n=nativeContext(f);
 // Keep a genuine unmet whole-node Operation witness now that ordinary
 // Operations have an adapter; do not silently turn this into a full-coverage test.
 const guardPath='specs/beta/nodes/allowed.json',guard=JSON.parse(fs.readFileSync(path.join(f.source,guardPath),'utf8'));
 guard.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'UInt64',value:'0'},right:{op:'literal',type:'UInt64',value:'1'}};f.write(guardPath,guard);
 const report=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(publicSelection())},tools=${JSON.stringify(n.options)},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),original=cp.spawnSync;
 cp.spawnSync=(command,args,settings)=>{if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated partial control'};const result=original(command,args,settings);if(args.includes('--permission')&&result.status===0)fs.appendFileSync(path.join(settings.cwd,'cases.json'),' ');return result;};syncBuiltinESMExports();
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,tools)));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'not_evaluable');assert.equal(semantic.executed,true);assert.equal(semantic.evidence.tested_node_count,7);
 assert.deepEqual(semantic.evidence.remaining.map((r:any)=>r.selector),['beta:perform']);assert.ok(semantic.blocked_by.includes('semantic-workspace-currentness'));
 assert.equal(report.result,'fail');assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});
function nativeContext(f:any){
 const cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const undici = path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
 const leanRoot=path.dirname(path.dirname(process.env.DOMAINSPEC_LEAN!));assert.ok(path.isAbsolute(leanRoot),'explicit installed Lean required');
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+path.join(f.temp,'scratch'),image];
 fs.mkdirSync(path.join(f.temp,'scratch'));fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 return {run,options};
}
function fixture(t:any){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-semantic-controls-')),source=path.join(root,'source');
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,value:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value)+'\n');};
 const input=(name:string)=>({op:'input',name}),literal=(value:string)=>({op:'literal',value}),binary=(op:string,left:any,right:any)=>({op,left,right});
 const definitions=[
  {id:'add',op:'add'},{id:'subtract',op:'subtract'},{id:'multiply',op:'multiply'},
  {id:'floor',op:'divide',rounding:'floor'},{id:'ceil',op:'divide',rounding:'ceil'},{id:'reject',op:'divide'},
  {id:'constant',inputs:[],expression:literal('18446744073709551615')},
  {id:'precedence',inputs:[],expression:binary('add',binary('multiply',literal('18446744073709551615'),literal('2')),binary('divide',literal('1'),literal('0')))},
  {id:'unused',expression:input('left')},
 ] as any[];
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'semantic-controls',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes:definitions.map(d=>d.id),edges:[]});
 for(const d of definitions){
  const names=d.inputs??['left','right'];
  write('specs/alpha/nodes/'+d.id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:d.id,kind:'Calculation',body:{description:d.id,inputs:names,typed_contract:{schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'TEST-'+d.id.toUpperCase(),inputs:names.map((name:string)=>({name,type:{kind:'scalar',name:'UInt64'}})),result:{kind:'scalar',name:'UInt64'},division_rounding:d.rounding??'reject',expression:d.expression??binary(d.op,input('left'),input('right'))}}});
 }
 const selection={...publicSelection(),factories:[],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {root,temp:root,source,selection,graph,plan};
}
test('early output failure retains complete per-node semantic coverage without executing controls',t=>{
 const f=publicFixture(t),plan=planCompiledReconciledProject(f.graph,publicSelection());
 const report=executeReconciledVerification(f.graph,plan,{
  target_root:path.join(f.root,'absent-output'),typescript_root:'/unavailable/typescript',node_type_root:'/unavailable/types',lean_executable:'/unavailable/lean',
 });
 assert.equal(report.result,'fail');
 const check=report.checks.find(c=>c.id==='selected-generator-semantic-controls')!;
 assert.equal(check.result,'not_evaluable');assert.equal(check.executed,false);
 assert.deepEqual(check.blocked_by,['exact-output-currentness']);
 assert.equal(report.semantic_coverage.node_count,f.graph.nodes.length);
 assert.deepEqual(report.semantic_coverage.rows.map(r=>r.selector),f.graph.nodes.map(n=>n.selector));
 assert.equal(report.semantic_coverage.ready_count,8);
 assert.equal(report.semantic_coverage.not_evaluable_count,f.graph.nodes.length-8);
 assert.ok(report.semantic_coverage.rows.every(r=>r.adapter_status==='ready'?r.case_count>0:r.reason.length>0));
 assert.equal(fs.existsSync(path.join(f.root,'absent-output')),false);
});
test('independent cases preserve exact arithmetic, rounding, failure order and all source nodes',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(controls.node_count,9);assert.equal(controls.ready_count,9);assert.equal(controls.not_evaluable_count,0);
 const row=(id:string)=>controls.rows.find(r=>r.selector==='alpha:'+id)!;
 const outcome=(id:string,values:string[])=>{const r=row(id);assert.equal(r.state,'ready');return r.state==='ready'?r.cases.find(c=>c.mode==='record'&&c.format==='string'&&!c.bad&&canonicalJson(c.values)===canonicalJson(values))!.expected:null;};
 assert.deepEqual(outcome('add',['1','2']),{kind:'value',value:'3'});
 assert.deepEqual(outcome('subtract',['1','2']),{kind:'error',name:'RangeError',message:'CALCULATION_UNDERFLOW'});
 assert.deepEqual(outcome('multiply',['2','2']),{kind:'value',value:'4'});
 assert.deepEqual(outcome('floor',['5','4']),{kind:'value',value:'1'});
 assert.deepEqual(outcome('ceil',['5','4']),{kind:'value',value:'2'});
 assert.deepEqual(outcome('reject',['5','4']),{kind:'error',name:'RangeError',message:'CALCULATION_INEXACT'});
 assert.deepEqual(outcome('constant',[]),{kind:'value',value:'18446744073709551615'});
 assert.deepEqual(outcome('precedence',[]),{kind:'error',name:'RangeError',message:'CALCULATION_OVERFLOW'});
 const unused=row('unused');assert.ok(unused.state==='ready'&&unused.cases.some(c=>c.bad?.index===1&&c.expected.kind==='error'&&c.expected.message==='CALCULATION_INPUT'));
 assert.equal(semanticModulePaths(controls).length,18);
 assert.deepEqual(createReconciledSemanticControls(f.graph,f.plan),controls);assert.ok(Object.isFrozen(controls.rows));
 const mixed=publicFixture(t),p=planCompiledReconciledProject(mixed.graph,publicSelection()),all=createReconciledSemanticControls(mixed.graph,p);
 assert.equal(all.node_count,mixed.graph.nodes.length);assert.equal(all.ready_count,8);assert.equal(all.not_evaluable_count,all.node_count-8);
 assert.deepEqual(all.rows.map(r=>r.selector),mixed.graph.nodes.map(n=>n.selector));
 const ready=all.rows.filter(r=>r.state==='ready');assert.notEqual(ready[0]!.contract_sha256,ready[1]!.contract_sha256);
 assert.notEqual(canonicalJson(ready[0]!.cases.map(c=>c.expected)),canonicalJson(ready[1]!.cases.map(c=>c.expected)));
});
test('semantic observations reject omission, substitution, reordering and forged plans',t=>{
 const f=fixture(t),p=createReconciledSemanticControls(f.graph,f.plan),rows=JSON.parse(renderSemanticCases(p)).rows;
 const actual=rows.map((r:any)=>({selector:r.selector,cases:r.cases.map((c:any)=>({id:c.id,outcome:c.expected,getter_reads:0,input_changed:false}))}));
 const evidence=checkSemanticObservations(p,JSON.stringify(actual));assert.equal(evidence.case_count,p.case_count);
 for(const mutate of [(v:any)=>v.pop(),(v:any)=>v.reverse(),(v:any)=>v[0].cases.pop(),(v:any)=>v[0].cases.reverse(),(v:any)=>v[0].cases[0].getter_reads++,(v:any)=>v[0].cases[0].input_changed=true,(v:any)=>v[0].cases[0].outcome={kind:'value',value:'bogus'},(v:any)=>v.push(v[0])]){
  const value=structuredClone(actual);mutate(value);assert.throws(()=>checkSemanticObservations(p,JSON.stringify(value)),/observation mismatch/);
 }
 assert.throws(()=>renderSemanticCases(structuredClone(p)),/registered/);assert.throws(()=>checkSemanticObservations(structuredClone(p),'[]'),/registered/);
});
test('real pure native semantic controls pass exact v2 calculations with no inherited credentials',t=>{
 const f=fixture(t),n=nativeContext(f),target=path.join(f.root,'target');publishReconciledProject(f.plan,target);
 const observed=n.run(`import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),original=cp.spawnSync;let runs=0;
 process.env.DS_SEMANTIC_TEST_SECRET='must-not-be-forwarded';
 cp.spawnSync=(command,args,options)=>{if(args.includes('--permission')){runs++;if(Object.keys(options.env).sort().join(',')!=='LANG,TZ')throw Error('ambient environment leaked');for(const denied of ['--allow-fs-write','--allow-net','--allow-child-process','--allow-worker','--allow-addons','--allow-ffi','--allow-wasi'])if(args.some(a=>a.startsWith(denied)))throw Error('unexpected semantic permission');}return original(command,args,options);};syncBuiltinESMExports();
 const report=executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})});console.log(JSON.stringify({report,runs}));
 `);
 const {report}=observed,check=(id:string)=>report.checks.find((c:any)=>c.id===id);
 assert.equal(observed.runs,1);assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
 assert.equal(check('selected-generator-semantic-controls').result,'pass');assert.equal(check('semantic-workspace-currentness').result,'pass');
 assert.equal(check('selected-generator-semantic-controls').evidence.tested_node_count,9);
 assert.equal(check('selected-generator-semantic-controls').evidence.remaining.length,0);
 assert.deepEqual(report.checks.filter((c:any)=>c.result==='not_evaluable').map((c:any)=>c.id).sort(),['safe-output-separate-from-planning']);
 const coverage=report.cross_generator_coverage;
 assert.equal(check('cross-generator-behavior').result,'pass');
 assert.equal(check('cross-generator-currentness').result,'pass');
 assert.equal(check('verification-workspace-cleanup').result,'pass');
 assert.equal(coverage.public_result,'pass');
 assert.deepEqual(coverage.blocked_by,[]);
 assert.deepEqual(coverage.execution.currentness_issues,[]);
 assert.equal(coverage.evidence_scope,'sealed-historical-report-not-a-live-retained-receipt');
 assert.equal(check('cross-generator-behavior').evidence.native_result,'inapplicable');
 assert.match(check('cross-generator-behavior').reason,/zero native families/);
 assert.equal(coverage.execution.result,'inapplicable');
 assert.equal(coverage.execution.executed_family_count,0);
 assert.equal(coverage.execution.retained_family_count,0);
 assert.deepEqual(coverage.execution.retained,[]);
 assert.deepEqual(coverage.execution.rows,[]);
 assert.equal(coverage.execution.edges.length,9,'retain all same-generator provider edges');
 assert.ok(coverage.execution.edges.every((e:any)=>!e.behavior_required&&!e.cross_generator_kind));
 assert.ok(coverage.execution.edges.every((e:any)=>e.observations.length===0&&e.execution_status==='not_evaluable'));
 assert.deepEqual(coverage.execution.edges.flatMap((e:any)=>e.importer_selectors).sort(),f.graph.nodes.map((n:any)=>n.selector).sort());
 assert.equal(coverage.preparation.roots.length,9);
 assert.equal(coverage.execution.workspace,null);
 assert.equal(coverage.retained_workspace_state,'not_created');
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
 for(const a of f.plan.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
