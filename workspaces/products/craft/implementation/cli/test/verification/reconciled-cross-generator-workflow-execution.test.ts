import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {execFileSync} from 'node:child_process';import test from 'node:test';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import type {OperationActionBindings} from '../../src/typed-operation/action-bindings.ts';
import {workflowValuesFixture} from '../helpers/workflow-values.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorWorkflowControls} from '../../src/verification/reconciled-cross-generator-workflow.ts';
import {createCrossGeneratorWorkflowSurface} from '../../src/verification/reconciled-cross-generator-workflow-surface.ts';
import {createCrossGeneratorWorkflowAudit} from '../../src/verification/reconciled-cross-generator-workflow-audit.ts';
import {executeCrossGeneratorWorkflow} from '../../src/verification/reconciled-cross-generator-workflow-execution.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),cli=path.join(project,'impl/cli'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions=Object.fromEntries(['workflow','operation','workflow-protocol','workflow-cases','workflow-execution','verification'].map(k=>[k,fs.readFileSync(path.join(base,'cross-generator-'+k+'-contract.json'),'utf8')]));
type Fixture=ReturnType<typeof workflowFixture>;
function context(f:Fixture,layout='domain'){
 const graph=f.graph,plan=planCompiledReconciledProject(graph,{...f.selection,module_root:layout}),b=createCrossGeneratorBoundary(graph,plan,definitions.verification!);
 const s=createCrossGeneratorWorkflowSurface(graph,plan,b,definitions.workflow!,definitions.operation!);
 return {plan,controls:createCrossGeneratorWorkflowControls(graph,plan,b,definitions.workflow!,definitions.operation!,definitions['workflow-protocol']!,definitions['workflow-cases']!),audit:createCrossGeneratorWorkflowAudit(graph,plan,s)};
}
function native(f:Fixture,layout='domain'){
 const require=createRequire(import.meta.url),types=fs.realpathSync(require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))})),nodeRoot=path.dirname(types),deps=path.dirname(path.dirname(nodeRoot));
 const undici=path.dirname(createRequire(types).resolve('undici-types/package.json')),dist=path.join(f.root,'dist');
 fs.mkdirSync(dist);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"module"}');
 const image=nativeToolchainImage();
 assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),
  '--mount','type=bind,source='+project+',target='+project+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly',
  '--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',stdio:'pipe',timeout:300000,maxBuffer:16777216});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 command(['tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',path.join(cli,'src'),'--outDir',dist,path.join(cli,'src/verification/reconciled-cross-generator-workflow-execution.ts')]);
 const prefix=String.raw`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';
import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {createCrossGeneratorBoundary} from './dist/verification/reconciled-cross-generator-boundary.js';
import {createCrossGeneratorWorkflowControls} from './dist/verification/reconciled-cross-generator-workflow.js';
import {createCrossGeneratorWorkflowSurface} from './dist/verification/reconciled-cross-generator-workflow-surface.js';
import {createCrossGeneratorWorkflowAudit} from './dist/verification/reconciled-cross-generator-workflow-audit.js';
import {executeCrossGeneratorWorkflow,assertCrossGeneratorWorkflowExecutionCurrent} from './dist/verification/reconciled-cross-generator-workflow-execution.js';
const source=__SOURCE__,selection=__SELECTION__,definitions=__DEFINITIONS__,definition=definitions['workflow-execution'];
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions.verification);
const surface=createCrossGeneratorWorkflowSurface(graph,plan,boundary,definitions.workflow,definitions.operation);
const controls=createCrossGeneratorWorkflowControls(graph,plan,boundary,definitions.workflow,definitions.operation,definitions['workflow-protocol'],definitions['workflow-cases']);
const audit=createCrossGeneratorWorkflowAudit(graph,plan,surface);
const options={workspace_parent:__ROOT__,typescript_root:'/opt/node-toolchain/node_modules/typescript',node_types_root:__TYPES__};
const execute=()=>executeCrossGeneratorWorkflow(plan,controls,audit,definition,definitions.workflow,options);
`;
 return {run:(body:string)=>{
  const client=path.join(f.root,'client.mjs');
  fs.writeFileSync(client,prefix.replace('__SOURCE__',JSON.stringify(path.join(f.root,'source'))).replace('__SELECTION__',JSON.stringify({...f.selection,module_root:layout})).replace('__DEFINITIONS__',JSON.stringify(definitions)).replace('__ROOT__',JSON.stringify(f.root)).replace('__TYPES__',JSON.stringify(nodeRoot))+body);
  return JSON.parse(command(['node',client]));
 }};
}
test('Workflow retained preflight rejects cloned controls/audits, foreign plans, drift and active options before writes',t=>{
 const f=workflowFixture(t),c=context(f),options={workspace_parent:f.root,typescript_root:'/tmp',node_types_root:'/tmp'},before=fs.readdirSync(f.root);
 const run=(controls=c.controls,audit=c.audit,opts=options,def=definitions['workflow-execution']!)=>executeCrossGeneratorWorkflow(c.plan,controls,audit,def,definitions.workflow!,opts);
 assert.throws(()=>run(structuredClone(c.controls)),/registered/);assert.throws(()=>run(c.controls,structuredClone(c.audit)),/registered/);
 assert.throws(()=>run(c.controls,c.audit,options,definitions['workflow-execution']!+' '),/definition drift/);
 const other=context(workflowFixture(t),'application/domain');assert.throws(()=>executeCrossGeneratorWorkflow(other.plan,c.controls,c.audit,definitions['workflow-execution']!,definitions.workflow!,options),/foreign/);
 let reads=0;const active:any={workspace_parent:f.root,typescript_root:'/tmp'};Object.defineProperty(active,'node_types_root',{enumerable:true,get(){reads++;return '/tmp';}});
 assert.throws(()=>run(c.controls,c.audit,active),/closed data tool options/);assert.equal(reads,0);
 assert.throws(()=>run(c.controls,c.audit,{...options,extra:'x'} as any),/closed data tool options/);
 assert.deepEqual(fs.readdirSync(f.root),before);
});
test('original scalar Workflow retained ESM execution includes complete declarations and six exact audits',t=>{
 const f=native(workflowFixture(t)),result=f.run(String.raw`
const r=execute();assertCrossGeneratorWorkflowExecutionCurrent(r);
assert.equal(r.outcome.tested_case_count,133);assert.equal(r.outcome.tested_call_count,998);assert.deepEqual(r.outcome.remaining,[]);
assert.equal(Object.keys(r.audits).length,6);assert.equal(r.families[0].inputs.length,1);
assert.equal(r.claim_scope,'finite-private-retained-original-workflow-esm-not-whole-project');assert.equal(r.outcome.public_cross_generator_behavior,'not_evaluable');
assert.ok(Object.keys(r.files).some(p=>p.endsWith('/declarations/node_modules/undici-types/index.d.ts')));
assert.equal(JSON.parse(fs.readFileSync(path.join(r.workspace,'compiler.json'))).compilerOptions.skipLibCheck,false);
assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(structuredClone(r)),/registered/);
console.log(JSON.stringify({...r.outcome,audits:Object.keys(r.audits).length,modules:r.native_modules.length}));
`);t.diagnostic(JSON.stringify(result));
});

test('multiple Workflow families retain separate complete manifests and lawful distinct forward Operations',t=>{
 const f=workflowFixture(t),source=path.join(f.root,'source'),manifestFile=path.join(source,'specs/commerce/feature.json');
 const manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8')),original=JSON.parse(fs.readFileSync(path.join(source,'specs/commerce/nodes/flow.json'),'utf8'));
 const second=structuredClone(original);second.node_id='flow-two';second.body.typed_contract.ontology_workflow='FIXTURE-FLOW-TWO';
 for(const step of second.body.typed_contract.steps)step.operation_ref+='-two';
 for(const compensation of second.body.typed_contract.compensations)compensation.operation_ref+='-two';
 fs.writeFileSync(path.join(source,'specs/commerce/nodes/flow-two.json'),JSON.stringify(second));manifest.nodes.push('flow-two');
 for(const target of ['perform','undo']){
  const node=JSON.parse(fs.readFileSync(path.join(source,'specs/commerce/nodes/'+target+'.json'),'utf8'));node.node_id=target+'-two';
  fs.writeFileSync(path.join(source,'specs/commerce/nodes/'+node.node_id+'.json'),JSON.stringify(node));manifest.nodes.push(node.node_id);
  for(const [from,relationship] of [['flow-two','orchestrates'],['allowed','enforces']]){
   const edge_id=from+'-'+relationship+'-'+node.node_id;
   fs.writeFileSync(path.join(source,'specs/commerce/edges/'+edge_id+'.json'),JSON.stringify({schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id,source_node_id:from,target_node_id:node.node_id,relationship,scope:'feature'}));manifest.edges.push(edge_id);
  }
  const action=structuredClone(f.selection.operations.find((o:Pick<OperationActionBindings,'selector'>)=>o.selector==='commerce:'+target)!);action.selector+='-two';f.selection.operations.push(action);
 }
 fs.writeFileSync(manifestFile,JSON.stringify(manifest));
 const binding=structuredClone(f.selection.workflows[0]!);binding.selector='commerce:flow-two';
 // Action bindings resolve from each new occurrence's declared Operation reference.
 f.selection.workflows.push(binding);
 const n=native(f),result=n.run(String.raw`
const r=execute();assertCrossGeneratorWorkflowExecutionCurrent(r);
assert.equal(r.outcome.tested_workflow_count,2);assert.equal(r.outcome.tested_case_count,266);assert.equal(r.outcome.tested_call_count,1996);
assert.equal(r.families.length,2);assert.deepEqual(r.families.map(f=>f.inputs.length),[1,1]);assert.equal(r.native_modules.length,11);
assert.equal(r.families[0].selector,controls.rows[0].selector);assert.equal(r.families[1].selector,controls.rows[1].selector);
console.log(JSON.stringify({...r.outcome,families:r.families.length,modules:r.native_modules.length}));
`);t.diagnostic(JSON.stringify(result));
});
test('unavailable whole Workflow families reject before materializing a workspace',t=>{
 const n=native(workflowFixture(t)),result=n.run(String.raw`
const ruleFile=path.join(source,'specs/commerce/nodes/allowed.json'),rule=JSON.parse(fs.readFileSync(ruleFile));
rule.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:false}};
fs.writeFileSync(ruleFile,JSON.stringify(rule));
const g=loadCompiledProjectGraph(source),p=planCompiledReconciledProject(g,selection),b=createCrossGeneratorBoundary(g,p,definitions.verification);
const s=createCrossGeneratorWorkflowSurface(g,p,b,definitions.workflow,definitions.operation),a=createCrossGeneratorWorkflowAudit(g,p,s);
const c=createCrossGeneratorWorkflowControls(g,p,b,definitions.workflow,definitions.operation,definitions['workflow-protocol'],definitions['workflow-cases']);
assert.ok(c.rows.length>0);assert.ok(c.rows.every(r=>r.state==='not_evaluable'));
const before=fs.readdirSync(options.workspace_parent);
assert.throws(()=>executeCrossGeneratorWorkflow(p,c,a,definition,definitions.workflow,options),/no ready Workflow families/);
assert.deepEqual(fs.readdirSync(options.workspace_parent),before);console.log(JSON.stringify({whole_family_unavailable:true,no_writes:true}));
`);t.diagnostic(JSON.stringify(result));
});

test('retained complete compound Workflow binds every original ESM batch in both layouts and detects stale artifacts',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const n=native(workflowValuesFixture(t,{events:true}),layout),result=n.run(String.raw`
const r=execute();assertCrossGeneratorWorkflowExecutionCurrent(r);
assert.equal(r.outcome.tested_case_count,12472);assert.equal(r.outcome.tested_call_count,20369);assert.deepEqual(r.outcome.remaining,[]);
assert.equal(r.families[0].inputs.length,4);assert.equal(r.families[0].outputs.length,4);assert.equal(r.native_modules.length,13);assert.equal(Object.keys(r.audits).length,6);
const files=['source-module-audit-input.json','native-effects-audit-input.json','native-orchestration-audit-observation.json','families/0/manifest.json','families/0/batch-3.json','families/0/observation-3.json','observation-index.json','observer.mjs','compiler.json','declarations/node_modules/@types/node/crypto.d.ts','declarations/node_modules/undici-types/index.d.ts','source/'+controls.rows[0].provider_path,'native/'+controls.rows[0].provider_path.replace(/\.ts$/,'.js')];
for(const name of files){const file=path.join(r.workspace,name),before=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(r),/artifact changed/);fs.writeFileSync(file,before);assertCrossGeneratorWorkflowExecutionCurrent(r);}
const observer=path.join(r.workspace,'observer.mjs'),saved=fs.readFileSync(observer);fs.unlinkSync(observer);assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(r),/artifact changed/);
fs.symlinkSync(path.join(r.workspace,'compiler.json'),observer);assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(r),/symbolic/);fs.unlinkSync(observer);fs.writeFileSync(observer,saved);assertCrossGeneratorWorkflowExecutionCurrent(r);
const manifest=JSON.parse(fs.readFileSync(path.join(r.workspace,'families/0/manifest.json')));
assert.equal(manifest.length,4);for(const input of manifest)assert.ok(!fs.readFileSync(input,'utf8').includes('"expected"'));
console.log(JSON.stringify({layout:selection.module_root,...r.outcome,batches:r.families[0].inputs.length,retained_mutations:files.length+2}));
`);t.diagnostic(JSON.stringify(result));
 });
});
test('retained Workflow rejects incomplete native output and missing independent audit observations',t=>{
 const n=native(workflowFixture(t)),result=n.run(String.raw`
const original=cp.spawnSync;let injected=0;
for(const mode of ['missing-output','duplicate-output','changed-envelope','missing-case','changed-descriptor','changed-material-descriptor','changed-semantic','module-omission','effects-omission','orchestration-omission']){
 let changed=false;
 cp.spawnSync=function(exe,args,...rest){
  const out=original.call(cp,exe,args,...rest);
  if(mode.endsWith('-omission')&&String(args[0]).endsWith('/'+mode.replace('-omission','')+'-audit.mjs')){
   const value=JSON.parse(out.stdout);value.modules.pop();out.stdout=JSON.stringify(value);changed=true;
  }else if(args.includes('--permission')){
   const lines=out.stdout.trim().split('\n'),value=JSON.parse(lines[0]);
   if(mode==='missing-output'){out.stdout='';changed=true;}
   if(mode==='duplicate-output'){out.stdout+=out.stdout;changed=true;}
   if(mode==='changed-envelope'){value.controls_sha256='0'.repeat(64);out.stdout=JSON.stringify(value)+'\n';changed=true;}
   if(mode==='missing-case'){value.cases.pop();out.stdout=JSON.stringify(value)+'\n';changed=true;}
   if(mode==='changed-descriptor'){value.descriptor=null;out.stdout=JSON.stringify(value)+'\n';changed=true;}
   if(mode==='changed-material-descriptor'){value.material_descriptor=null;out.stdout=JSON.stringify(value)+'\n';changed=true;}
   if(mode==='changed-semantic'){value.cases[0].semantic_sha256='0'.repeat(64);out.stdout=JSON.stringify(value)+'\n';changed=true;}
  }return out;
 };syncBuiltinESMExports();
 try{assert.throws(()=>execute(),/audit mismatch|batch observations|framing|batch observation identity|observation mismatch/);assert.ok(changed,mode);injected++;}
 finally{cp.spawnSync=original;syncBuiltinESMExports();}
}
console.log(JSON.stringify({injected_native_and_audit_rejections:injected}));
`);t.diagnostic(JSON.stringify(result));
});
test('retained Workflow detects in-flight artifact drift while captured source remains sufficient',t=>{
 const n=native(workflowFixture(t,{noCompensations:true})),result=n.run(String.raw`
const sourceFile=path.join(source,'specs/commerce/nodes/flow.json'),sourceBytes=fs.readFileSync(sourceFile);fs.unlinkSync(sourceFile);
const r=execute();assertCrossGeneratorWorkflowExecutionCurrent(r);fs.writeFileSync(sourceFile,sourceBytes);
let injected=0;
for(const trigger of ['source-module-audit-input.json','native-effects-audit-input.json','families/0/manifest.json','families/0/observation-0.json']){
 const original=fs.writeFileSync;let changed=false;
 fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/'+trigger)){original.call(fs,path.join(path.dirname(String(file)),'unexpected'),'x');changed=true;}return out;};
 try{assert.throws(()=>execute(),/artifact changed or unexpected/);assert.ok(changed,trigger);injected++;}
 finally{fs.writeFileSync=original;}
}
assertCrossGeneratorWorkflowExecutionCurrent(r);console.log(JSON.stringify({captured_source:true,in_flight_artifact_rejections:injected,no_compensation:true}));
`);t.diagnostic(JSON.stringify(result));
});
test('retained Workflow binds compiler platform and physical declaration dependency trees before and after execution',t=>{
 const n=native(workflowFixture(t)),result=n.run(String.raw`
const packageRoot=path.join(options.workspace_parent,'tool-copy','node_modules');fs.mkdirSync(packageRoot,{recursive:true});
fs.cpSync(options.typescript_root,path.join(packageRoot,'typescript'),{recursive:true});fs.cpSync('/opt/node-toolchain/node_modules/@typescript',path.join(packageRoot,'@typescript'),{recursive:true});
const nodeRoot=path.join(packageRoot,'@types/node');fs.mkdirSync(path.dirname(nodeRoot),{recursive:true});fs.cpSync(options.node_types_root,nodeRoot,{recursive:true});
const {createRequire}=await import('node:module'),undici=path.dirname(createRequire(path.join(options.node_types_root,'package.json')).resolve('undici-types/package.json'));
fs.cpSync(undici,path.join(packageRoot,'undici-types'),{recursive:true});options.typescript_root=path.join(packageRoot,'typescript');options.node_types_root=nodeRoot;
const r=execute();assertCrossGeneratorWorkflowExecutionCurrent(r);
const targets=[path.join(options.typescript_root,'lib/getExePath.js'),path.join(options.typescript_root,'dist/api/sync/api.js'),path.join(packageRoot,'@typescript/typescript-linux-x64/lib/tsc'),path.join(nodeRoot,'crypto.d.ts'),path.join(packageRoot,'undici-types/index.d.ts')];
for(const file of targets){const saved=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(r),/toolchain or declaration dependency changed/);fs.writeFileSync(file,saved);assertCrossGeneratorWorkflowExecutionCurrent(r);}
const dep=path.join(packageRoot,'undici-types/package.json'),saved=fs.readFileSync(dep);fs.unlinkSync(dep);assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(r));fs.writeFileSync(dep,saved);assertCrossGeneratorWorkflowExecutionCurrent(r);
const original=cp.spawnSync;let changed=false;const target=path.join(packageRoot,'undici-types/index.d.ts'),before=fs.readFileSync(target);
cp.spawnSync=function(exe,args,...rest){const out=original.call(cp,exe,args,...rest);if(args[0]===path.join(options.typescript_root,'bin/tsc')){fs.appendFileSync(target,'\n');changed=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>execute(),/toolchain or declaration dependency changed/);assert.ok(changed);}
finally{cp.spawnSync=original;syncBuiltinESMExports();fs.writeFileSync(target,before);}
assertCrossGeneratorWorkflowExecutionCurrent(r);
const shadow=path.join(packageRoot,'@types/node_modules/undici-types');fs.mkdirSync(path.dirname(shadow),{recursive:true});
fs.cpSync(path.join(packageRoot,'undici-types'),shadow,{recursive:true});
assert.throws(()=>assertCrossGeneratorWorkflowExecutionCurrent(r),/toolchain or declaration dependency changed/);
fs.rmSync(shadow,{recursive:true});fs.rmdirSync(path.dirname(shadow));assertCrossGeneratorWorkflowExecutionCurrent(r);
console.log(JSON.stringify({tool_and_declaration_mutations:targets.length+2,in_flight_declaration_rejection:true,shadow_dependency_rejected:true}));
`);t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
