import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import * as api from '../../src/index.ts';
import {runCli} from '../../src/cli/main.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {publicFixture,publicSelection} from '../helpers/composition-project.ts';
import {publishReconciledProject,createReconciledOutputReceipt} from '../../src/generation/reconciled-output.ts';
import {reconciledOutputView} from '../../src/generation/reconciled-output-layout.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
function nativeContext(f:any){
 const cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const undici=path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
 const leanRoot=path.dirname(path.dirname(process.env.DOMAINSPEC_LEAN!));assert.ok(path.isAbsolute(leanRoot),'explicit installed Lean required');
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+path.join(f.temp,'scratch'),image];
 fs.mkdirSync(path.join(f.temp,'scratch'));fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts'),path.join(src,'cli/main.ts')],{encoding:'utf8'});}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const client=path.join(f.temp,'consumer.ts');fs.writeFileSync(client,"import {verifyProject,verifyReconciledSourceProject,verifyCompiledReconciledProject,type ReconciledVerificationExecution,type ProjectVerificationReceiptV1,type ReconciledCompilationSelection,type ReconciledVerificationTools} from './dist/index.js';\ndeclare const selected:ReconciledCompilationSelection;\ndeclare const tools:ReconciledVerificationTools;\ndeclare const graph:Parameters<typeof verifyCompiledReconciledProject>[0];\nconst legacy:ProjectVerificationReceiptV1=verifyProject('/source','/target');\nconst source:ReconciledVerificationExecution=verifyReconciledSourceProject('/source',selected,tools);\nconst snapshot:ReconciledVerificationExecution=verifyCompiledReconciledProject(graph,selected,tools);\nconst explicit:ReconciledVerificationExecution=verifyProject('/source','/target',selected,tools);\n// @ts-expect-error explicit selection requires explicit tools\nverifyProject('/source','/target',selected);\n// @ts-expect-error incomplete execution is not a legacy pass-only receipt\nconst wrong:ProjectVerificationReceiptV1=explicit;\nvoid [legacy,source,snapshot,wrong];\n");
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--noEmit','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext',client],{encoding:'utf8'});}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}};
 return {run,options};
}
const layout='domainspec.application-layout/v1' as const;
const absentTools={typescript_root:'/missing/typescript',node_type_root:'/missing/types',lean_executable:'/missing/lean'};
const cli=(args:string[])=>{let out='',err='';const code=runCli(args,{stdout:s=>out+=s,stderr:s=>err+=s});return {code,out,err};};

test('source, snapshot, overload and CLI preserve the same complete failed report in both layouts',t=>{
 const f=publicFixture(t),selection=publicSelection(),plan=api.planCompiledReconciledProject(f.graph,selection),file=path.join(f.root,'selection.json');
 fs.writeFileSync(file,JSON.stringify(selection));
 for(const output_layout of [undefined,layout]){
  const target=path.join(f.root,output_layout?'application':'plain'),tools={...absentTools,target_root:target,...(output_layout?{output_layout}:{})};
  const publication=publishReconciledProject(plan,target,null,output_layout),view=reconciledOutputView(plan,null,output_layout);
  const snapshot=api.verifyCompiledReconciledProject(f.graph,selection,tools),source=api.verifyReconciledSourceProject(f.source,selection,tools),overload=api.verifyProject(f.source,target,selection,tools);
  const argv=['verify-project',f.source,'--compilation-selection',file,'--target-root',target,'--typescript-root',tools.typescript_root,'--node-type-root',tools.node_type_root,'--lean-executable',tools.lean_executable,...(output_layout?['--output-layout',output_layout]:[])];
  const command=cli(argv);assert.equal(command.code,1);assert.equal(command.err,'');
  assert.deepEqual(JSON.parse(command.out),snapshot);assert.deepEqual(source,snapshot);assert.deepEqual(overload,snapshot);
  assert.equal(snapshot.result,'fail');assert.equal(snapshot.output_layout,output_layout);
  const current=snapshot.checks.find(c=>c.id==='exact-output-currentness')!;
  assert.equal(current.result,'pass');assert.equal(current.evidence.view_sha256,view.view_sha256);
  assert.equal(current.evidence.receipt_sha256,createReconciledOutputReceipt(plan,null,output_layout).receipt_sha256);
  assert.equal(snapshot.denominators.artifact_count,view.artifacts.length);
  for(const a of view.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
  assert.equal(fs.readFileSync(path.join(target,publication.receipt_path),'utf8'),canonicalJson(publication.receipt)+'\n');
  const {output_layout:omitted,...plainTools}=tools;
  const wrong=api.verifyCompiledReconciledProject(f.graph,selection,output_layout?plainTools:{...plainTools,output_layout:layout});
  assert.equal(wrong.result,'fail');assert.equal(wrong.checks.find(c=>c.id==='exact-output-currentness')!.result,'fail');
  assert.equal(wrong.checks.find(c=>c.id==='strict-native-compilation')!.executed,false);
 }
 const node=path.join(f.source,'specs/alpha/nodes/allowed.json'),raw=JSON.parse(fs.readFileSync(node,'utf8'));raw.body.description+=' updated';fs.writeFileSync(node,JSON.stringify(raw));
 const stale=api.verifyCompiledReconciledProject(f.graph,selection,absentTools);
 assert.equal(stale.result,'fail');assert.equal(stale.checks.find(c=>c.id==='source-currentness')!.result,'fail');
 assert.equal(stale.checks.find(c=>c.id==='strict-native-compilation')!.executed,false);
 const fresh=api.verifyReconciledSourceProject(f.source,selection,absentTools);
 assert.notEqual(fresh.project_plan_sha256,stale.project_plan_sha256);
 assert.equal(fresh.checks.find(c=>c.id==='source-currentness')!.result,'pass');
});

test('compiled public verification and actual CLI run native and Lean checks for plain and application output',t=>{
 const original=publicFixture(t),f={...original,temp:original.root},selection=publicSelection(),plan=api.planCompiledReconciledProject(f.graph,selection);
 const n=nativeContext(f),file=path.join(f.root,'selection.json');fs.writeFileSync(file,JSON.stringify(selection));
 for(const output_layout of [undefined,layout]){
  const target=path.join(f.root,output_layout?'application':'plain'),view=reconciledOutputView(plan,null,output_layout);
  const publication=publishReconciledProject(plan,target,null,output_layout),tools={...n.options,target_root:target,...(output_layout?{output_layout}:{})};
  const argv=['verify-project',f.source,'--compilation-selection',file,'--target-root',target,'--typescript-root',tools.typescript_root,'--node-type-root',tools.node_type_root,'--lean-executable',tools.lean_executable,...(output_layout?['--output-layout',output_layout]:[])];
  const observed=n.run(output_layout?
   `import cp from 'node:child_process';const r=cp.spawnSync(process.execPath,['./dist/cli/main.js',...${JSON.stringify(argv)}],{encoding:'utf8',timeout:150000,maxBuffer:32*1024*1024});console.log(JSON.stringify({code:r.status,stderr:r.stderr,report:JSON.parse(r.stdout)}));`:
   `import {loadCompiledProjectGraph,verifyCompiledReconciledProject} from './dist/index.js';const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)});console.log(JSON.stringify({report:verifyCompiledReconciledProject(graph,${JSON.stringify(selection)},${JSON.stringify(tools)})}));`);
  if(output_layout){assert.equal(observed.code,1);assert.equal(observed.stderr,'');}
  const report=observed.report;
  assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
  assert.equal(report.output_layout,output_layout);
  for(const id of ['strict-native-compilation','generated-javascript-syntax','independent-module-surface-observation','lean-structural-kernel','source-and-selection-preservation','composition-source-preservation','selected-calculation-bindings','exact-output-currentness','verification-workspace-cleanup'])assert.equal(report.checks.find((c:any)=>c.id===id)?.result,'pass',id);
  assert.equal(report.checks.find((c:any)=>c.id==='exact-output-currentness').evidence.view_sha256,view.view_sha256);
  assert.equal(report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls').result,'pass');
  for(const id of ['composition-behavior-controls','composition-behavior-currentness'])assert.equal(report.checks.find((c:any)=>c.id===id)?.result,'pass',id);
  assert.equal(report.checks.find((c:any)=>c.id==='composition-behavior-controls').evidence.case_count,116);
  assert.deepEqual(report.checks.filter((c:any)=>c.result==='not_evaluable').map((c:any)=>c.id).sort(),['cross-generator-behavior','safe-output-separate-from-planning']);
  assert.equal(report.denominators.artifact_count,view.artifacts.length);
  for(const a of view.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
  assert.equal(fs.readFileSync(path.join(target,publication.receipt_path),'utf8'),canonicalJson(publication.receipt)+'\n');
  assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
 }
});

test('selected source and snapshot verification APIs exist and reject invalid options before source access',()=>{
 assert.equal(typeof api.verifyReconciledSourceProject,'function');
 assert.equal(typeof api.verifyCompiledReconciledProject,'function');
 const source='/missing/source',target='/missing/target',selection=publicSelection();
 for(const options of [{...absentTools,output_layout:'unknown'},{...absentTools,target_root:'relative'},{...absentTools,extra:true},{...absentTools,lean_executable:'lean'}]){
  assert.throws(()=>api.verifyReconciledSourceProject(source,selection,options as any),/DS_RECONCILED/);
  assert.throws(()=>api.verifyCompiledReconciledProject({} as any,selection,options as any),/DS_RECONCILED/);
 }
 let reads=0;const active={...absentTools};Object.defineProperty(active,'typescript_root',{enumerable:true,get(){reads++;return absentTools.typescript_root;}});
 assert.throws(()=>api.verifyReconciledSourceProject(source,selection,active),/inert/);assert.equal(reads,0);
 assert.throws(()=>api.verifyProject(source,target,selection,{...absentTools,target_root:'/another'}),/target/);
 assert.throws(()=>api.verifyProject(source,target,selection,undefined as any),/tools/);
 assert.throws(()=>(api.verifyProject as any)(source,target,undefined,absentTools),/selection/);
});

test('selected CLI rejects missing, duplicate, unsupported and relative arguments without creating output',t=>{
 const f=publicFixture(t),file=path.join(f.root,'selection.json'),target=path.join(f.root,'never-created');
 fs.writeFileSync(file,JSON.stringify(publicSelection()));
 const args=['verify-project',f.source,'--compilation-selection',file,'--target-root',target,'--typescript-root',absentTools.typescript_root,'--node-type-root',absentTools.node_type_root,'--lean-executable',absentTools.lean_executable];
 for(const values of [args.slice(0,-2),[...args,'--lean-executable','/another'],[...args,'--unknown','value'],[...args,'--output-layout','unknown'],args.map(a=>a===target?'relative':a),[...args,'--node','alpha:values']]){
  const r=cli(values);assert.notEqual(r.code,0);assert.equal(r.out,'');assert.equal(JSON.parse(r.err).result,'fail');assert.equal(fs.existsSync(target),false);
 }
 const result=cli(args);assert.equal(result.code,1);assert.equal(result.err,'');
 const report=JSON.parse(result.out);assert.equal(report.schema_version,'domainspec.reconciled-verification-execution/v1-candidate');assert.equal(report.result,'fail');assert.equal(fs.existsSync(target),false);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
