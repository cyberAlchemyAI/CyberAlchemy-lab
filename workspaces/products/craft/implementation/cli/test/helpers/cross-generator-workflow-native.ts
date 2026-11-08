import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {execFileSync} from 'node:child_process';
import {workflowFixture} from './workflow-verification.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorWorkflowControls,crossGeneratorWorkflowBatchProbes,checkCrossGeneratorWorkflowObservations} from '../../src/verification/reconciled-cross-generator-workflow.ts';
import {createCrossGeneratorWorkflowSurface} from '../../src/verification/reconciled-cross-generator-workflow-surface.ts';
import {createCrossGeneratorWorkflowAudit,CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER,WORKFLOW_EFFECT_AUDIT_RUNNER,WORKFLOW_ORCHESTRATION_AUDIT_RUNNER} from '../../src/verification/reconciled-cross-generator-workflow-audit.ts';
import {CROSS_GENERATOR_WORKFLOW_RUNNER} from '../../src/verification/reconciled-cross-generator-workflow-runner.ts';
export const workflowNativeProject=path.resolve(import.meta.dirname,'../../../..');
const base=path.join(workflowNativeProject,'development/reconciliation-v1/profile-compiler-reconciliation'),read=(p:string)=>fs.readFileSync(path.join(base,p),'utf8');
export const workflowNativeDefinitions={surface:read('cross-generator-workflow-contract.json'),operation:read('cross-generator-operation-contract.json'),protocol:read('cross-generator-workflow-protocol-contract.json'),cases:read('cross-generator-workflow-cases-contract.json'),boundary:read('cross-generator-verification-contract.json')};
export function nativeWorkflowProtocol(f:ReturnType<typeof workflowFixture>,layout='domain'){
 const d=workflowNativeDefinitions,graph=f.graph,plan=planCompiledReconciledProject(graph,{...f.selection,module_root:layout}),boundary=createCrossGeneratorBoundary(graph,plan,d.boundary);
 const surface=createCrossGeneratorWorkflowSurface(graph,plan,boundary,d.surface,d.operation),audits=createCrossGeneratorWorkflowAudit(graph,plan,surface);
 const controls=createCrossGeneratorWorkflowControls(graph,plan,boundary,d.surface,d.operation,d.protocol,d.cases),row=controls.rows[0]!;
 assert.equal(row.state,'ready',row.state==='not_evaluable'?row.reason:'');if(row.state!=='ready')throw Error('whole family unavailable');
 const root=path.join(f.root,'native-protocol'),src=path.join(root,'source'),out=path.join(root,'compiled');fs.mkdirSync(root);fs.writeFileSync(path.join(root,'package.json'),'{"type":"module"}');
 for(const m of row.modules){const a=plan.resolved.artifacts.find(a=>a.relative_path===m.relative_path)!,file=path.join(src,m.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const options={strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',types:['node'],typeRoots:[path.join(deps,'@types')]};
 const config=path.join(root,'source.json'),nativeConfig=path.join(root,'native.json'),auditFile=path.join(root,'audit.mjs'),auditInput=path.join(root,'audit.json'),runner=path.join(root,'observer.mjs');
 fs.writeFileSync(config,JSON.stringify({compilerOptions:{...options,rootDir:src,outDir:out},files:row.modules.map(m=>path.join(src,m.relative_path))}));
 fs.writeFileSync(nativeConfig,JSON.stringify({compilerOptions:{...options,allowJs:true,checkJs:false,noEmit:true,rootDir:out},files:row.modules.map(m=>path.join(out,m.relative_path.replace(/\.ts$/,'.js')))}));
 fs.writeFileSync(runner,CROSS_GENERATOR_WORKFLOW_RUNNER);
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',root,image];
 const command=(args:string[])=>execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:60000,maxBuffer:16777216});
 const compile=()=>command(['tsc','--project',config]);compile();
 const auditAll=()=>{
  for(const phase of ['source','native'] as const)for(const facet of ['module','effects','orchestration'] as const){
   const profile:any=facet==='module'?{module_paths:row.modules.map(m=>m.relative_path),modules:row.modules,support_modules:row.modules.filter(m=>m.role==='enum-runtime').map(m=>({relative_path:m.relative_path,source_sha256:m.sha256}))}:audits[facet];
   fs.writeFileSync(auditFile,facet==='module'?CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER:facet==='effects'?WORKFLOW_EFFECT_AUDIT_RUNNER:WORKFLOW_ORCHESTRATION_AUDIT_RUNNER);
   fs.writeFileSync(auditInput,JSON.stringify({...profile,definition:facet==='module'?d.surface:audits.definitions[facet],phase,module_root:phase==='source'?src:out,module_paths:profile.module_paths.map((p:string)=>phase==='source'?p:p.replace(/\.ts$/,'.js'))}));
   const observed=JSON.parse(command(['node',auditFile,'/opt/node-toolchain/node_modules/typescript',phase==='source'?config:nativeConfig,auditInput]));
   assert.deepEqual(observed.modules.flatMap((m:any)=>m.violations),[],phase+':'+facet);
  }
 };
 const probes=crossGeneratorWorkflowBatchProbes(controls);
 const observe=(selected:any[]=probes)=>{
  const files=selected.map((p,i)=>{const file=path.join(root,'batch-'+i+'.json');fs.writeFileSync(file,JSON.stringify(p));return file;}),manifest=path.join(root,'manifest.json');fs.writeFileSync(manifest,JSON.stringify(files));
  const output=execFileSync(process.execPath,['--experimental-vm-modules','--permission','--allow-fs-read='+root,'--disable-proto=throw','--max-old-space-size=256',runner,manifest,out],{encoding:'utf8',stdio:'pipe',timeout:60000,maxBuffer:33554432,env:{LANG:'C',TZ:'UTC'}});
  const batches=output.trim().split('\n').map(l=>JSON.parse(l)),first=batches[0];
  return {controls_sha256:controls.controls_sha256,rows:[{selector:first.selector,identity:first.identity,descriptor:first.descriptor,material_descriptor:first.material_descriptor,batches:batches.map(b=>b.batch),cases:batches.flatMap(b=>b.cases)}]};
 };
 return {graph,plan,boundary,surface,controls,row,root,src,out,runner,probes,compile,auditAll,observe,check:(v:unknown)=>checkCrossGeneratorWorkflowObservations(controls,v)};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from './native-toolchain-image.ts';
