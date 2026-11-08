import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {publicFixture,publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject,selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {createReconciledVerificationProjection,validateReconciledVerificationProjection} from '../../src/verification/reconciled-projection.ts';
import {publishReconciledProject} from '../../src/generation/reconciled-output.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.ts';
import {createPublicCompositionControls,compositionVerificationDefinitions} from '../../src/verification/reconciled-composition-public.ts';
const project=path.resolve(import.meta.dirname,'../../../..');

function nativeContext(f:any){
 const cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const undici = path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
 const leanRoot=path.dirname(path.dirname(process.env.DOMAINSPEC_LEAN!));assert.ok(path.isAbsolute(leanRoot),'explicit installed Lean required');
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+path.join(f.temp,'scratch'),image];
 fs.mkdirSync(path.join(f.temp,'scratch'));fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts'),path.join(src,'cli/main.ts')],{encoding:'utf8'});}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:900000,maxBuffer:32*1024*1024}));}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}};
 return {run,options};
}

test('real composition verification executes bounded computation and checks all files without changing target',t=>{
 const original=publicFixture(t),f={...original,temp:original.root},selection=publicSelection(),plan=planCompiledReconciledProject(f.graph,selection),view=selectReconciledArtifacts(plan),target=path.join(f.root,'target');
 publishReconciledProject(plan,target);
 const n=nativeContext(f),report=n.run(`import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(selection)}),original=cp.spawnSync;
 cp.spawnSync=(command,args,options)=>{if(args.some(a=>String(a).endsWith('/server.mjs')))throw Error('endpoint must not execute');return original(command,args,options);};syncBuiltinESMExports();
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})})));
 `);
 assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
 assert.equal(report.denominators.artifact_count,view.artifacts.length);assert.equal(report.denominators.composition_count,1);
 const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
 for(const id of ['isolated-exact-source-replay','strict-native-compilation','generated-javascript-syntax','independent-module-surface-observation','lean-structural-kernel','source-and-selection-preservation','composition-source-preservation','selected-calculation-bindings','verification-workspace-currentness','exact-output-currentness','verification-workspace-cleanup'])assert.equal(check(id)?.result,'pass',id);
 assert.equal(check('strict-native-compilation').evidence.artifact_count,report.denominators.typescript_artifact_count);
 assert.equal(check('generated-javascript-syntax').evidence.scope,'syntax-only-no-behavior-execution');
 assert.equal(check('independent-module-surface-observation').evidence.module_count,report.denominators.typescript_artifact_count+report.denominators.javascript_artifact_count);
 assert.equal(check('selected-generator-semantic-controls').result,'pass');
 assert.equal(check('composition-behavior-controls').result,'pass');assert.equal(check('composition-behavior-currentness').result,'pass');
 assert.equal(check('composition-behavior-controls').evidence.case_count,116);
 assert.deepEqual(report.checks.filter((c:any)=>c.result==='not_evaluable').map((c:any)=>c.id).sort(),['cross-generator-behavior','safe-output-separate-from-planning']);
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
 for(const a of view.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
});
test('JavaScript syntax, changed exports and late supporting-file or inventory drift reject with complete accounting',t=>{
 const original=publicFixture(t),f={...original,temp:original.root},selection=publicSelection(),n=nativeContext(f);
 const reports=n.run(String.raw`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(selection)},options=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['javascript-syntax','javascript-export','data-drift','extra-file']){
  const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
  cp.spawnSync=(command,args,settings)=>{
   if(command===options.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated native mutation controls'};
   if(args.includes('--check')&&mode==='javascript-syntax')fs.appendFileSync(args.at(-1),'\nexport function (');
   const result=original(command,args,settings);
   if(result.status===0&&args.includes('--project')&&mode==='javascript-export')fs.appendFileSync(path.join(settings.cwd,'compositions/calculate/behavior.mjs'),'\nexport const Unexpected = 1;\n');
   if(result.status===0&&String(args[0]).endsWith('observe.mjs')){
    if(mode==='data-drift')fs.appendFileSync(path.join(settings.cwd,'compositions/calculate/ontology.json'),'\n');
    if(mode==='extra-file')fs.writeFileSync(path.join(settings.cwd,'unexpected.json'),'{}');
   }
   return result;
  };syncBuiltinESMExports();
  try{reports.push({mode,report:executeReconciledVerification(graph,plan,options)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report} of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
  assert.equal(report.result,'fail',mode);assert.equal(check('verification-workspace-currentness').result,'fail',mode);
  assert.equal(check('strict-native-compilation').result,'not_evaluable',mode);
  assert.equal(check('composition-source-preservation').result,'not_evaluable');assert.ok(check('composition-source-preservation').blocked_by.includes('verification-workspace-currentness'));
  assert.equal(check('selected-calculation-bindings').result,'not_evaluable');
  if(mode==='javascript-syntax')assert.equal(check('generated-javascript-syntax').result,'fail');
  else if(mode==='javascript-export')assert.equal(check('independent-module-surface-observation').result,'fail');
  else {assert.equal(check('generated-javascript-syntax').result,'not_evaluable');assert.equal(check('independent-module-surface-observation').result,'not_evaluable');}
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});

test('verification preserves the complete composition source, bindings, artifacts and evidence denominator',t=>{
 const f=publicFixture(t),plan=planCompiledReconciledProject(f.graph,publicSelection()),view=selectReconciledArtifacts(plan),p:any=createReconciledVerificationProjection(f.graph,plan);
 assert.deepEqual(p.composition_projection,plan.composition);
 assert.deepEqual(p.native_projection.artifacts,view.artifacts.map(({content,...a})=>a));
 assert.equal(p.denominators.artifact_count,view.artifacts.length);assert.equal(p.denominators.composition_count,1);
 const coverage=p.native_projection.artifact_coverage;
 assert.equal(new Set([...coverage.typescript_paths,...coverage.javascript_paths,...coverage.preserved_paths]).size,view.artifacts.length);
 assert.equal(coverage.typescript_paths.length+coverage.javascript_paths.length+coverage.preserved_paths.length,view.artifacts.length);
 assert.deepEqual(coverage.javascript_paths,['compositions/calculate/behavior.mjs']);
 assert.ok(coverage.preserved_paths.includes('compositions/calculate/ontology.json'));
 assert.equal(p.native_projection.modules.length,coverage.typescript_paths.length+coverage.javascript_paths.length);
 const ids=p.evidence_requirements.map((r:any)=>r.id);assert.equal(new Set(ids).size,ids.length);
 for(const id of ['generated-javascript-syntax','composition-source-preservation','selected-calculation-bindings','composition-behavior-controls'])assert.ok(ids.includes(id),id);
 for(const mutate of [(v:any)=>delete v.composition_projection,(v:any)=>v.native_projection.artifacts.pop(),(v:any)=>v.native_projection.artifact_coverage.preserved_paths.pop(),(v:any)=>v.composition_projection.compositions[0].bindings[0].selector='beta:compute',(v:any)=>v.evidence_requirements.pop()]){
  const changed=structuredClone(p);mutate(changed);const {projection_sha256,...body}=changed;changed.projection_sha256=sha256(canonicalJson(body));assert.throws(()=>validateReconciledVerificationProjection(changed,f.graph,plan),/incomplete|changed/);
 }
 fs.rmSync(f.source,{recursive:true});assert.deepEqual(createReconciledVerificationProjection(f.graph,plan),p);
});

test('source, snapshot and actual CLI composition verification agree in both output layouts',t=>{
 const original=publicFixture(t),f={...original,temp:original.root},n=nativeContext(f);
 const reports=n.run(String.raw`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,verifyReconciledSourceProject,verifyCompiledReconciledProject,publishReconciledProject} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(publicSelection())},tools=${JSON.stringify(n.options)},reports=[];
 const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),file=path.join(source,'selection.json');fs.writeFileSync(file,JSON.stringify(selection));
 for(const layout of [undefined,'domainspec.application-layout/v1']){
  const target=path.join(path.dirname(source),layout?'application':'plain'),options={...tools,target_root:target,...(layout?{output_layout:layout}:{})};publishReconciledProject(plan,target,null,layout);
  for(const entry of ['source','snapshot','cli']){
   let report;
   if(entry==='source')report=verifyReconciledSourceProject(source,selection,options);
   else if(entry==='snapshot')report=verifyCompiledReconciledProject(graph,selection,options);
   else {
    const args=['./dist/cli/main.js','verify-project',source,'--compilation-selection',file,'--target-root',target,'--typescript-root',tools.typescript_root,'--node-type-root',tools.node_type_root,'--lean-executable',tools.lean_executable,...(layout?['--output-layout',layout]:[])];
    const result=cp.spawnSync(process.execPath,args,{encoding:'utf8',timeout:180000,maxBuffer:33554432});
    assert.equal(result.status,1,result.stderr);assert.equal(result.stderr,'');report=JSON.parse(result.stdout);
   }
   reports.push({entry,layout:layout??'plain',report});
  }
 }
 console.log(JSON.stringify(reports));`);
 let identity:string|undefined;
 for(const {entry,layout,report} of reports){
  const check=(id:string)=>report.checks.find((r:any)=>r.id===id),label=entry+':'+layout;
  assert.equal(report.result,'incomplete',label+':'+JSON.stringify(report.checks.filter((r:any)=>r.result==='fail')));
  for(const id of ['composition-behavior-controls','composition-behavior-currentness','composition-source-preservation','selected-calculation-bindings','isolated-exact-source-replay','lean-structural-kernel','exact-output-currentness','verification-workspace-cleanup'])assert.equal(check(id).result,'pass',label+':'+id);
  const evidence=check('composition-behavior-controls').evidence,row=evidence.rows[0];
  assert.equal(evidence.composition_count,1);assert.equal(evidence.case_count,116);assert.equal(row.id,'calculate');assert.equal(row.state,'pass');
  assert.equal(row.coverage.required.length,row.coverage.witnessed.length);assert.equal(Object.keys(row.audits).length,2);
  assert.ok(row.modules.every((m:any)=>!m.relative_path.endsWith('server.mjs')));
  identity??=row.case_family_sha256;assert.equal(row.case_family_sha256,identity);
  assert.deepEqual(report.checks.filter((r:any)=>r.result==='not_evaluable').map((r:any)=>r.id).sort(),['cross-generator-behavior','safe-output-separate-from-planning']);
 }
 assert.equal(reports.length,6);assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
 t.diagnostic('6 public reports, 696 composition case executions; no endpoint or target mutation');
});

test('public behavior fails executed native semantic and effect mutations, and invalidates late evidence or cleanup failures',t=>{
 const original=publicFixture(t),f={...original,temp:original.root},n=nativeContext(f);
 const reports=n.run(String.raw`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(publicSelection())},tools=${JSON.stringify(n.options)},reports=[],spawn=cp.spawnSync,remove=fs.rmSync;
 const sourceFile=path.join(source,'project.json'),sourceBytes=fs.readFileSync(sourceFile);
 for(const mode of ['native-semantic','native-effect','late-observation','late-extra-file','late-source','cleanup']){
  let injected=false,nativeCalls=0,workspace;
  cp.spawnSync=(command,args,options)=>{
   const result=spawn(command,args,options),child=options?.cwd?.includes('/ds-composition-run-');
   if(child&&args.includes('--project')&&result.status===0){
    workspace=options.cwd;
    if(mode==='native-semantic'||mode==='native-effect'){
     const file=path.join(workspace,'native/domain/features/alpha/src/domain/calculations/compute.provider.js'),text=fs.readFileSync(file,'utf8');
     const changed=mode==='native-semantic'?text.replace(/checked\(([^()]+)-([^()]+)\)/,'checked($1+$2)'):text+'\nprocess.cwd();\n';
     assert.notEqual(changed,text);fs.writeFileSync(file,changed);injected=true;
    }
   }
   if(child&&args.includes('--permission'))nativeCalls++;
   if(command===tools.lean_executable&&args.some(a=>String(a).endsWith('/Audit.lean'))&&result.status===0){
    assert.ok(workspace);
    if(mode==='late-observation'){fs.appendFileSync(path.join(workspace,'observations.json'),'\n');injected=true;}
    if(mode==='late-extra-file'){fs.writeFileSync(path.join(workspace,'extra.txt'),'changed');injected=true;}
    if(mode==='late-source'){fs.appendFileSync(sourceFile,'\n');injected=true;}
   }
   return result;
  };
  fs.rmSync=(file,options)=>{if(mode==='cleanup'&&path.basename(String(file)).startsWith('domainspec-reconciled-verify-')){injected=true;throw Error('injected owned cleanup failure');}return remove(file,options);};syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),injected,nativeCalls});}
  finally{cp.spawnSync=spawn;fs.rmSync=remove;syncBuiltinESMExports();fs.writeFileSync(sourceFile,sourceBytes);}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,injected,nativeCalls} of reports){
  const check=(id:string)=>report.checks.find((r:any)=>r.id===id),behavior=check('composition-behavior-controls');
  assert.equal(injected,true,mode);assert.equal(report.result,'fail',mode);
  if(mode==='native-semantic'||mode==='native-effect'){
   assert.equal(behavior.result,'fail',mode);assert.equal(behavior.evidence.rows[0].phase,mode==='native-semantic'?'native-behavior':'native-effect-audit');
   assert.equal(nativeCalls,mode==='native-semantic'?1:0);assert.equal(behavior.evidence.case_count,0,'no passing prefix');
  }else {
   assert.equal(nativeCalls,1);assert.equal(behavior.result,'not_evaluable',mode);assert.equal(behavior.executed,true);
   const prerequisite=mode==='cleanup'?'verification-workspace-cleanup':mode==='late-source'?'source-currentness':'composition-behavior-currentness';
   assert.equal(check(prerequisite).result,'fail',mode);assert.ok(behavior.blocked_by.includes(prerequisite),mode);
  }
  if(mode!=='cleanup')assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 // The deliberately failed cleanup remains within this test's exact fixture root;
 // publicFixture's teardown owns its recovery, not the verifier's failed claim.
 assert.equal(fs.readdirSync(path.join(f.temp,'scratch')).length,1);
});

test('public adapter keeps unavailable whole families distinct from graph and binding defects',t=>{
 const f=publicFixture(t),selection=publicSelection(),plan=planCompiledReconciledProject(f.graph,selection);
 assert.ok(Object.isFrozen(compositionVerificationDefinitions()));
 assert.throws(()=>createPublicCompositionControls(structuredClone(f.graph),plan,'calculate'),/unvalidated|changed/);
 assert.throws(()=>createPublicCompositionControls(f.graph,plan,'unknown'),/source composition ID/);
 const source=structuredClone(f.composition),c=source.contract;c.results.forEach((r:any)=>{r.condition={op:'literal',value:false};});
 source.source_text=JSON.stringify(c,null,2)+'\n';const hash=sha256(source.source_text);source.ontology.source.sha256=hash;source.ontology.composition_trace=compileDeclarativeFunction(c).trace as any;
 source.ontology.nodes.forEach((r:any)=>{r.source.sha256=hash;if(r.name==='Result')r.cases=c.results;});source.ontology.references.forEach((r:any)=>{r.evidence.sha256=hash;});f.write('compositions/calculate.json',source);
 const graph=loadCompiledProjectGraph(f.source),unavailable=createPublicCompositionControls(graph,planCompiledReconciledProject(graph,selection),'calculate');
 assert.equal(unavailable.state,'not_evaluable');if(unavailable.state==='not_evaluable'){assert.ok(unavailable.missing.includes('phase:{"mode":"execute"}'));assert.match(unavailable.reason,/not an unsatisfiability proof/);}
 const n=nativeContext({...f,temp:f.root}),report=n.run(`import {verifyReconciledSourceProject} from './dist/index.js';console.log(JSON.stringify(verifyReconciledSourceProject(${JSON.stringify(f.source)},${JSON.stringify(selection)},${JSON.stringify(n.options)})));`);
 const check=(id:string)=>report.checks.find((r:any)=>r.id===id);
 assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((r:any)=>r.result==='fail')));
 assert.equal(check('composition-behavior-controls').result,'not_evaluable');assert.equal(check('composition-behavior-controls').evidence.rows.length,1);
 assert.equal(check('composition-behavior-controls').evidence.case_count,0);assert.equal(check('composition-behavior-currentness').result,'not_evaluable');assert.equal(check('verification-workspace-cleanup').result,'pass');
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});

test('public composition without Calculation calls executes structural mappings without factory substitution',t=>{
 const f=publicFixture(t),source=structuredClone(f.composition),c=source.contract;
 c.calculations={};delete source.core_bindings.Net;delete source.core_bindings.Other;
 c.nodes.find((n:any)=>n.id==='Emit').fields={net:{op:'call',name:'text',args:[{op:'path',path:['Parsed','qty']}]},other:{op:'call',name:'text',args:[{op:'path',path:['Parsed','rebate']}]}};
 source.source_text=JSON.stringify(c,null,2)+'\n';const hash=sha256(source.source_text);source.ontology.source.sha256=hash;source.ontology.composition_trace=compileDeclarativeFunction(c).trace as any;
 source.ontology.nodes=source.ontology.nodes.filter((n:any)=>!['Net','Other'].includes(n.name));
 source.ontology.nodes.forEach((r:any)=>{r.source.sha256=hash;if(r.name==='Emit')r.typed_contract=c.nodes.find((n:any)=>n.id==='Emit');});
 source.ontology.references=source.ontology.references.filter((r:any)=>!['TEST-ALPHA','TEST-BETA'].includes(r.source)&&!['TEST-ALPHA','TEST-BETA'].includes(r.target));
 source.ontology.references.forEach((r:any)=>{r.evidence.sha256=hash;});f.write('compositions/calculate.json',source);
 const n=nativeContext({...f,temp:f.root}),report=n.run(`import {verifyReconciledSourceProject} from './dist/index.js';console.log(JSON.stringify(verifyReconciledSourceProject(${JSON.stringify(f.source)},${JSON.stringify(publicSelection())},${JSON.stringify(n.options)})));`);
 const check=(id:string)=>report.checks.find((r:any)=>r.id===id),behavior=check('composition-behavior-controls');
 assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((r:any)=>r.result==='fail')));assert.equal(behavior.result,'pass');
 assert.equal(behavior.evidence.case_count,116);assert.equal(behavior.evidence.rows[0].modules.length,2);
 assert.equal(check('selected-calculation-bindings').result,'pass');assert.deepEqual(check('selected-calculation-bindings').evidence.bindings,[]);
 assert.equal(check('verification-workspace-cleanup').result,'pass');assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
