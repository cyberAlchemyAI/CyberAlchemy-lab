import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import test from 'node:test';
import {createRequire} from 'node:module';import {execFileSync} from 'node:child_process';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {workflowValuesFixture} from '../helpers/workflow-values.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorWorkflowSurface,assertCrossGeneratorWorkflowSurface} from '../../src/verification/reconciled-cross-generator-workflow-surface.ts';
import {createCrossGeneratorWorkflowAudit,assertCrossGeneratorWorkflowAudit,CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER,WORKFLOW_EFFECT_AUDIT_RUNNER,WORKFLOW_ORCHESTRATION_AUDIT_RUNNER} from '../../src/verification/reconciled-cross-generator-workflow-audit.ts';
import {CROSS_GENERATOR_OPERATION_AUDIT_RUNNER} from '../../src/verification/reconciled-cross-generator-operation-audit.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definition=fs.readFileSync(path.join(base,'cross-generator-workflow-contract.json'),'utf8'),operationDefinition=fs.readFileSync(path.join(base,'cross-generator-operation-contract.json'),'utf8'),boundaryDefinition=fs.readFileSync(path.join(base,'cross-generator-verification-contract.json'),'utf8');
type Fixture=ReturnType<typeof workflowFixture>;
function surface(f:Fixture,layout='domain'){
 const graph=f.graph,plan=planCompiledReconciledProject(graph,{...f.selection,module_root:layout}),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 const surface=createCrossGeneratorWorkflowSurface(graph,plan,boundary,definition,operationDefinition),audit=createCrossGeneratorWorkflowAudit(graph,plan,surface);
 return {graph,plan,boundary,surface,audit};
}
function native(f:Fixture,layout='domain'){
 const c=surface(f,layout),row=c.surface.rows[0]!,root=path.join(f.root,'native-workflow-surface'),src=path.join(root,'source'),out=path.join(root,'compiled');
 fs.mkdirSync(root);fs.writeFileSync(path.join(root,'package.json'),'{"type":"module"}');
 for(const m of row.modules){const a=c.plan.resolved.artifacts.find(a=>a.relative_path===m.relative_path)!,file=path.join(src,m.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const config=path.join(root,'source.json'),nativeConfig=path.join(root,'native.json'),runner=path.join(root,'audit.mjs'),input=path.join(root,'input.json');
 const options={strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',types:['node'],typeRoots:[path.join(deps,'@types')]};
 fs.writeFileSync(config,JSON.stringify({compilerOptions:{...options,rootDir:src,outDir:out},files:row.modules.map(m=>path.join(src,m.relative_path))}));
 fs.writeFileSync(nativeConfig,JSON.stringify({compilerOptions:{...options,allowJs:true,checkJs:false,noEmit:true,rootDir:out},files:row.modules.map(m=>path.join(out,m.relative_path.replace(/\.ts$/,'.js')))}));
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:60000,maxBuffer:16777216});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 const compile=()=>command(['tsc','--project',config]);compile();
 const audit=(phase:'source'|'native',facet:'module'|'effects'|'orchestration',refreshProbeHashes=false,script?:string)=>{
  const profile=structuredClone(facet==='effects'?c.audit.effects:facet==='orchestration'?c.audit.orchestration:{module_paths:row.modules.map(m=>m.relative_path),modules:row.modules,support_modules:row.modules.filter(m=>m.role==='enum-runtime').map(m=>({relative_path:m.relative_path,source_sha256:m.sha256}))}) as any;
  // Hostile-probe-only refresh bypasses early byte rejection to exercise independent grammar.
  if(refreshProbeHashes)for(const m of profile.workflow_modules??[])m.source_sha256=sha256(fs.readFileSync(path.join(src,m.relative_path)));
  const selected={...profile,definition:facet==='module'?definition:c.audit.definitions[facet],phase,module_root:phase==='source'?src:out,module_paths:profile.module_paths.map((p:string)=>phase==='source'?p:p.replace(/\.ts$/,'.js'))};
  fs.writeFileSync(runner,script??(facet==='module'?CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER:facet==='effects'?WORKFLOW_EFFECT_AUDIT_RUNNER:WORKFLOW_ORCHESTRATION_AUDIT_RUNNER));
  fs.writeFileSync(input,JSON.stringify(selected));return JSON.parse(command(['node',runner,'/opt/node-toolchain/node_modules/typescript',phase==='source'?config:nativeConfig,input]));
 };
 return {...c,row,root,src,out,compile,audit};
}
const violations=(v:any)=>v.modules.flatMap((m:any)=>m.violations.map((v:any)=>({path:m.relative_path,...v})));
test('Workflow source surface preserves repeated occurrences and excludes compensation-only dependency code',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const f=workflowFixture(t),c=surface(f,layout),row=c.surface.rows[0]!;
  assert.equal(row.state,'surface-ready');assert.equal(row.behavior_status,'not_evaluable');assert.equal(row.native_status,'not_evaluable');
  assert.equal(row.steps.length,4);assert.equal(row.forward.length,1);assert.equal(row.compensations.length,3);assert.equal(row.modules.length,6);
  assert.ok(row.modules.every(m=>m.selector!=='commerce:undo'));
  assert.deepEqual(row.modules.find(m=>m.role==='workflow-material')!.imports,[]);
  const imports=row.modules.find(m=>m.role==='workflow-provider')!.imports;
  assert.equal(imports[0]!.specifier,'node:crypto');assert.equal(imports[1]!.namespace,true);assert.deepEqual(imports[1]!.native_names,['capture','captureResult','compensations','result','steps']);
  assert.equal(imports[2]!.reexport,true);assert.equal(imports[2]!.type_only,true);assert.equal(imports[3]!.reexport,false);assert.equal(imports[3]!.type_only,true);
  assert.equal(c.audit.required_facets.length,3);assert.ok(c.surface.coverage.some(e=>e.state==='uncovered'));
  assert.throws(()=>assertCrossGeneratorWorkflowSurface(structuredClone(c.surface)),/registered/);
  assert.throws(()=>assertCrossGeneratorWorkflowAudit(structuredClone(c.audit)),/registered/);
  assert.throws(()=>createCrossGeneratorWorkflowSurface(c.graph,c.plan,c.boundary,definition+' ',operationDefinition),/definition drift/);
  const other=surface(workflowFixture(t),layout==='domain'?'application/domain':'domain');
  assert.throws(()=>createCrossGeneratorWorkflowAudit(other.graph,other.plan,c.surface),/foreign surface/);
  assert.throws(()=>createCrossGeneratorWorkflowSurface(c.graph,c.plan,other.boundary,definition,operationDefinition),/foreign boundary/);
 });
});
test('compound source surface retains nested Entity Value Object named sum and Event providers',t=>{
 const c=surface(workflowValuesFixture(t,{events:true})),row=c.surface.rows[0]!;
 assert.ok(row.modules.some(m=>m.role==='factory'&&m.selector==='commerce:order'));
 assert.ok(row.modules.some(m=>m.role==='factory'&&m.selector==='commerce:money'));
 assert.ok(row.modules.some(m=>m.role==='sum'));
 assert.ok(row.modules.some(m=>m.role==='event-wrapper'&&m.selector==='commerce:posted'));
 assert.ok(row.modules.every(m=>m.selector!=='commerce:released'&&m.selector!=='commerce:undo'));
 assert.equal(row.material_descriptor.compensations.length,3);assert.equal(row.compensation_execution,false);
});
test('no-compensation Workflow retains forward steps without a fabricated recovery member read',t=>{
 const c=surface(workflowFixture(t,{noCompensations:true})),row=c.surface.rows[0]!;
 assert.equal(row.compensations.length,0);assert.deepEqual(row.modules.find(m=>m.role==='workflow-provider')!.imports.find(i=>i.namespace)!.native_names,['capture','captureResult','result','steps']);
});
test('original compound generated Workflow passes all three source/native audit facets in both layouts',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const n=native(workflowValuesFixture(t,{events:true}),layout);
  for(const phase of ['source','native'] as const)for(const facet of ['module','effects','orchestration'] as const){
   const result=n.audit(phase,facet);assert.deepEqual(violations(result),[],phase+':'+facet);
   if(facet==='module')assert.equal(result.modules.length,n.row.modules.length);
  }
  t.diagnostic(JSON.stringify({layout,modules:n.row.modules.length,audit_facets:6}));
 });
});
test('original scalar Workflow with no compensation passes every source/native facet',t=>{
 const n=native(workflowFixture(t,{noCompensations:true}));
 for(const phase of ['source','native'] as const)for(const facet of ['module','effects','orchestration'] as const)assert.deepEqual(violations(n.audit(phase,facet)),[]);
});
test('strict-compiling extra namespace members, value exports and runtime reexports fail module audit',t=>{
 const n=native(workflowFixture(t)),provider=path.join(n.src,n.row.provider_path),wrapper=path.join(n.src,n.row.relative_path);
 const original=fs.readFileSync(provider,'utf8'),oldWrapper=fs.readFileSync(wrapper,'utf8');let rejected=0;
 for(const changed of [original+'\nconst leaked=material.descriptor;',original+'\nexport const unwanted=1;']){
  fs.writeFileSync(provider,changed);n.compile();
  for(const phase of ['source','native'] as const){assert.ok(violations(n.audit(phase,'module')).length);rejected++;}
 }
 fs.writeFileSync(provider,original);
 const runtime=oldWrapper.replace('export type {','export {');assert.notEqual(runtime,oldWrapper);fs.writeFileSync(wrapper,runtime);n.compile();
 assert.ok(violations(n.audit('source','module')).length);rejected++;fs.writeFileSync(wrapper,oldWrapper);n.compile();
 const nativeFile=path.join(n.out,n.row.provider_path.replace(/\.ts$/,'.js')),old=fs.readFileSync(nativeFile,'utf8');
 for(const extra of ['\nexports.WorkflowInput=1;','\nconst alien=require("node:fs");','\nconst alias=require;alias("node:crypto");']){
  fs.writeFileSync(nativeFile,old+extra);assert.ok(violations(n.audit('native','module')).length);rejected++;
 }
 t.diagnostic(JSON.stringify({module_mutants:rejected}));
});
test('module matching cannot replace crypto effect or awaited orchestration checks',t=>{
 const n=native(workflowFixture(t)),file=path.join(n.src,n.row.provider_path),original=fs.readFileSync(file,'utf8');
 const escaped=original+'\nconst misuse=()=>createHash("sha256").update("not-metadata").digest("hex");';
 fs.writeFileSync(file,escaped);n.compile();
 for(const phase of ['source','native'] as const){assert.deepEqual(violations(n.audit(phase,'module')),[]);assert.ok(violations(n.audit(phase,'effects',true)).some((v:any)=>v.code==='crypto-escape'));}
 const changes=[original.replace('raw=await call0(args,dep0);','raw=call0(args,dep0);'),
  original.replace('const input=material.capture(parameters);','const input=(material.capture(parameters),material.capture(parameters));')];
 for(const changed of changes){
  assert.notEqual(changed,original);fs.writeFileSync(file,changed);n.compile();
  for(const phase of ['source','native'] as const){assert.deepEqual(violations(n.audit(phase,'module')),[]);assert.ok(violations(n.audit(phase,'orchestration',true)).some((v:any)=>v.code==='execute-protocol'));}
 }
 fs.writeFileSync(file,original);n.compile();
 assert.throws(()=>n.audit('source','module',false,CROSS_GENERATOR_OPERATION_AUDIT_RUNNER),/definition\/phase/);
 t.diagnostic(JSON.stringify({crypto_misuse:1,orchestration_mutants:2,earlier_profile_not_widened:true}));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
