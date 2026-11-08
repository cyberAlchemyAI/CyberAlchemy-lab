import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {operationFixture,valueOperationFixture} from '../helpers/cross-generator-operation.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorOperationControls} from '../../src/verification/reconciled-cross-generator-operation.ts';
import {executeCrossGeneratorOperation} from '../../src/verification/reconciled-cross-generator-execution.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),cli=path.join(project,'impl/cli'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions=Object.fromEntries(['cross-generator-operation','cross-generator-operation-protocol','cross-generator-verification'].map(k=>[k,fs.readFileSync(path.join(base,k+'-contract.json'),'utf8')]));
type Fixture=Pick<ReturnType<typeof operationFixture>,'root'|'source'|'selection'|'compile'>;
function control(f:Fixture){
 const {graph,plan}=f.compile(),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']!);
 return {graph,plan,boundary,controls:createCrossGeneratorOperationControls(graph,plan,boundary,definitions['cross-generator-operation']!,definitions['cross-generator-operation-protocol']!)};
}
function native(f:Fixture){
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const dist=path.join(f.root,'dist');fs.mkdirSync(dist);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"module"}');
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+project+',target='+project+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:240000,maxBuffer:16777216});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 command(['tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',path.join(cli,'src'),'--outDir',dist,path.join(cli,'src/verification/reconciled-cross-generator-execution.ts')]);
 const prefix=`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';
import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {createCrossGeneratorBoundary} from './dist/verification/reconciled-cross-generator-boundary.js';
import {createCrossGeneratorOperationControls,checkCrossGeneratorOperationObservations} from './dist/verification/reconciled-cross-generator-operation.js';
import {executeCrossGeneratorOperation,assertCrossGeneratorExecutionCurrent} from './dist/verification/reconciled-cross-generator-execution.js';
const source=__SOURCE__,selection=__SELECTION__,definitions=__DEFINITIONS__,definition=definitions['cross-generator-operation'];
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']);
const controls=createCrossGeneratorOperationControls(graph,plan,boundary,definition,definitions['cross-generator-operation-protocol']);
const options={workspace_parent:__ROOT__,typescript_root:'/opt/node-toolchain/node_modules/typescript'};
`;
 return {...f,run:(body:string)=>{const client=path.join(f.root,'client.mjs');fs.writeFileSync(client,prefix.replace('__SOURCE__',JSON.stringify(f.source)).replace('__SELECTION__',JSON.stringify(f.selection)).replace('__DEFINITIONS__',JSON.stringify(definitions)).replace('__ROOT__',JSON.stringify(f.root))+body);return JSON.parse(command(['node',client]));}};
}
test('Operation retained preflight rejects clone, foreign plan, definition drift and active options before writes',t=>{
 const f=operationFixture(t),c=control(f),options={workspace_parent:f.root,typescript_root:'/tmp'},before=fs.readdirSync(f.root);
 assert.throws(()=>executeCrossGeneratorOperation(c.plan,structuredClone(c.controls),definitions['cross-generator-operation']!,options),/registered/);
 assert.throws(()=>executeCrossGeneratorOperation(c.plan,c.controls,definitions['cross-generator-operation']!+' ',options),/definition drift/);
 assert.throws(()=>executeCrossGeneratorOperation(control(operationFixture(t,'application/domain')).plan,c.controls,definitions['cross-generator-operation']!,options),/foreign plan/);
 let reads=0;const active:any={workspace_parent:f.root};Object.defineProperty(active,'typescript_root',{enumerable:true,get(){reads++;return '/tmp';}});
 assert.throws(()=>executeCrossGeneratorOperation(c.plan,c.controls,definitions['cross-generator-operation']!,active),/closed data tool options/);
 assert.equal(reads,0);assert.deepEqual(fs.readdirSync(f.root),before);
});
test('retained original Operation execution binds both layouts and rejects altered artifacts',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const f=native(operationFixture(t,layout)),result=f.run(String.raw`
const r=executeCrossGeneratorOperation(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.surface_sha256,controls.surface_sha256);assert.equal(r.protocol_sha256,controls.protocol_sha256);
assert.equal(r.claim_scope,'finite-private-instrumented-operation-providers-not-whole-project');
assert.equal(r.outcome.tested_operation_count,1);assert.equal(r.outcome.tested_case_count,1903);assert.deepEqual(r.outcome.remaining,[]);
assert.equal(r.outcome.public_cross_generator_behavior,'not_evaluable');assert.equal(Object.keys(r.audits).length,2);
const sourceAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'source-audit-observation.json'))),nativeAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'native-audit-observation.json')));
assert.ok(sourceAudit.modules.some(m=>m.imports.some(i=>i.reexport&&i.type_only)));
assert.ok(nativeAudit.modules.every(m=>m.imports.every(i=>!i.reexport&&!i.type_only)));
assert.ok(!JSON.stringify(JSON.parse(fs.readFileSync(path.join(r.workspace,'cases.json')))).includes('"expected"'));
assert.throws(()=>assertCrossGeneratorExecutionCurrent(structuredClone(r)),/registered/);
for(const name of ['source-audit-input.json','native-audit-input.json','source-audit-observation.json','native-audit-observation.json','observations.json','cases.json','runner.mjs','compiler.json']){
 const file=path.join(r.workspace,name),before=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(file,before);assertCrossGeneratorExecutionCurrent(r);
}
for(const file of [path.join(r.workspace,'source',controls.rows[0].provider_path),path.join(r.workspace,'native',controls.rows[0].provider_path.replace(/\.ts$/,'.js'))]){
 const before=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(file,before);assertCrossGeneratorExecutionCurrent(r);
}
const runner=path.join(r.workspace,'runner.mjs'),saved=fs.readFileSync(runner);fs.unlinkSync(runner);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
fs.symlinkSync(path.join(r.workspace,'cases.json'),runner);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/symbolic/);fs.unlinkSync(runner);fs.writeFileSync(runner,saved);assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({...r.outcome,layout:selection.module_root,modules:r.native_modules.length,audits:2,retained_mutations:12}));
`);t.diagnostic(JSON.stringify(result));
 });
});
test('retained Enum-only Operation uses no synthetic factory or Event',t=>{
 const f=native(valueOperationFixture(t,'application/domain')),result=f.run(String.raw`
const r=executeCrossGeneratorOperation(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.ok(controls.rows.every(r=>r.state==='ready'));assert.ok(!controls.rows.flatMap(r=>r.modules).some(m=>['factory','event-wrapper','event-provider'].includes(m.role)));
assert.equal(r.outcome.tested_operation_count,1);assert.deepEqual(r.outcome.remaining,[]);
console.log(JSON.stringify({...r.outcome,modules:r.native_modules.length}));
`);t.diagnostic(JSON.stringify(result));
});
test('Operation retained execution uses captured sources and rejects in-flight drift, missing observations and unavailable witnesses',t=>{
 const f=native(operationFixture(t)),result=f.run(String.raw`
const sourceFile=path.join(source,'specs/commerce/nodes/post.json'),sourceBytes=fs.readFileSync(sourceFile);fs.unlinkSync(sourceFile);
const r=executeCrossGeneratorOperation(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);fs.writeFileSync(sourceFile,sourceBytes);
for(const trigger of ['source-audit-input.json','native-audit-input.json','observations.json']){
 const original=fs.writeFileSync;let changed=false;
 fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/'+trigger)){original.call(fs,path.join(path.dirname(String(file)),'unexpected'),'x');changed=true;}return out;};
 try{assert.throws(()=>executeCrossGeneratorOperation(plan,controls,definition,options),/artifact changed or unexpected/);assert.ok(changed);}finally{fs.writeFileSync=original;}
}
const originalSpawn=cp.spawnSync;let changed=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args.includes('--permission')){const value=JSON.parse(out.stdout);value.rows.pop();out.stdout=JSON.stringify(value);changed=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorOperation(plan,controls,definition,options),/observation mismatch/);assert.ok(changed);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();}
const ruleFile=path.join(source,'specs/commerce/nodes/can-post.json'),rule=JSON.parse(fs.readFileSync(ruleFile));rule.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:false}};fs.writeFileSync(ruleFile,JSON.stringify(rule));
const g=loadCompiledProjectGraph(source),p=planCompiledReconciledProject(g,selection),b=createCrossGeneratorBoundary(g,p,definitions['cross-generator-verification']),c=createCrossGeneratorOperationControls(g,p,b,definition,definitions['cross-generator-operation-protocol']);
assert.ok(c.rows.every(r=>r.state==='not_evaluable'));const before=fs.readdirSync(options.workspace_parent);
assert.throws(()=>executeCrossGeneratorOperation(p,c,definition,options),/no ready interoperability/);assert.deepEqual(fs.readdirSync(options.workspace_parent),before);
assertCrossGeneratorExecutionCurrent(r);console.log(JSON.stringify({captured_source:true,in_flight_rejections:3,missing_observation_rejected:true,unavailable_family_rejected:true}));
`);t.diagnostic(JSON.stringify(result));
});
test('Operation retained custody detects complete compiler/platform and in-flight tool drift',t=>{
 const f=native(valueOperationFixture(t)),result=f.run(String.raw`
const packageRoot=path.join(options.workspace_parent,'tool-copy','node_modules');fs.mkdirSync(packageRoot,{recursive:true});
fs.cpSync(options.typescript_root,path.join(packageRoot,'typescript'),{recursive:true});fs.cpSync('/opt/node-toolchain/node_modules/@typescript',path.join(packageRoot,'@typescript'),{recursive:true});
options.typescript_root=path.join(packageRoot,'typescript');const r=executeCrossGeneratorOperation(plan,controls,definition,options);assertCrossGeneratorExecutionCurrent(r);
for(const file of [path.join(options.typescript_root,'lib/getExePath.js'),path.join(options.typescript_root,'dist/api/sync/api.js'),path.join(packageRoot,'@typescript/typescript-linux-x64/lib/tsc')]){
 const before=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.writeFileSync(file,before);assertCrossGeneratorExecutionCurrent(r);
}
const extra=path.join(options.typescript_root,'extra');fs.writeFileSync(extra,'x');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.unlinkSync(extra);assertCrossGeneratorExecutionCurrent(r);
const spawn=cp.spawnSync,tool=path.join(options.typescript_root,'lib/getExePath.js'),before=fs.readFileSync(tool);let injected=false;
cp.spawnSync=function(exe,args,...rest){const out=spawn.call(cp,exe,args,...rest);if(args[0]===path.join(options.typescript_root,'bin/tsc')){fs.appendFileSync(tool,'\n');injected=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorOperation(plan,controls,definition,options),/toolchain changed/);assert.ok(injected);}finally{cp.spawnSync=spawn;syncBuiltinESMExports();fs.writeFileSync(tool,before);}
assertCrossGeneratorExecutionCurrent(r);console.log(JSON.stringify({tool_mutations:4,in_flight_tool_rejections:1}));
`);t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
