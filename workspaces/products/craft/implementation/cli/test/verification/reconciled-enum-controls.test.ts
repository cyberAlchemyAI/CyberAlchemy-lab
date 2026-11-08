import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {createReconciledSemanticControls,renderSemanticCases,checkSemanticObservations} from '../../src/verification/reconciled-semantic-controls.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
function fixture(t:any,payload=false,moduleRoot='domain'){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-enum-controls-')),source=path.join(root,'source');
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,value:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value)+'\n');};
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'enum-controls',features:['alpha','beta'],cross_feature_edges:[]});
 for(const feature_id of ['alpha','beta']){
  const names=feature_id==='alpha'?['Shared','Draft','Submitted']:['Recorded','Shared'];
  write('specs/'+feature_id+'/feature.json',{schema_version:'domainspec.feature/v1',feature_id,nodes:['status'],edges:[]});
  write('specs/'+feature_id+'/nodes/status.json',{schema_version:'domainspec.node/v1',feature_id,node_id:'status',kind:'Enum',body:{description:'Owned cases retain qualified identity.',values:names,typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-'+feature_id.toUpperCase(),variants:names.map(name=>({name,ontology_variant:'TEST-'+feature_id.toUpperCase()+'#'+name,payload:payload&&feature_id==='beta'&&name==='Recorded'?{kind:'scalar',name:'String'}:null}))}}});
 }
 const selection={...publicSelection(),module_root:moduleRoot,factories:[],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {root,temp:root,source,selection,graph,plan};
}
test('source-derived Enum cases preserve membership, ownership and payload-sum adapter accounting',t=>{
 const f=fixture(t),p=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(p.node_count,2);assert.equal(p.ready_count,2);assert.equal(p.not_evaluable_count,0);
 const rows=p.rows.filter(r=>r.state==='ready');assert.deepEqual(rows.map(r=>r.selector),['alpha:status','beta:status']);
 assert.notEqual(rows[0]!.contract_sha256,rows[1]!.contract_sha256);
 const member=rows.map(r=>{const expected=r.cases.find(c=>c.mode==='member'&&c.values[0]==='Shared')!.expected;assert.equal(expected.kind,'value');return JSON.parse((expected as {value:string}).value);});
 assert.equal(member[0].variant,member[1].variant);assert.notEqual(member[0].key,member[1].key);
 assert.deepEqual(JSON.parse((rows[0]!.cases.find(c=>c.mode==='definition')!.expected as any).value).members,[['Draft','Draft'],['Shared','Shared'],['Submitted','Submitted']]);
 const moved=fixture(t,false,'alternate/nested'),m=createReconciledSemanticControls(moved.graph,moved.plan);
 assert.deepEqual(m.rows.filter(r=>r.state==='ready').map(r=>r.cases.filter(c=>c.mode!=='metadata')),rows.map(r=>r.cases.filter(c=>c.mode!=='metadata')));
 const mixed=fixture(t,true),coverage=createReconciledSemanticControls(mixed.graph,mixed.plan);
 assert.equal(coverage.node_count,2);assert.equal(coverage.ready_count,2);assert.equal(coverage.not_evaluable_count,0);
 assert.equal((coverage.rows.find(r=>r.selector==='beta:status') as any).adapter,'sum');
 const observed=rows.map(r=>({selector:r.selector,cases:r.cases.map(c=>({id:c.id,outcome:c.expected,getter_reads:0,input_changed:false}))}));
 assert.equal(checkSemanticObservations(p,canonicalJson(observed)).tested_node_count,2);
 observed[0]!.cases[0]!.outcome={kind:'value',value:'{}'};
 assert.throws(()=>checkSemanticObservations(p,canonicalJson(observed)),/observation mismatch/);
 assert.throws(()=>renderSemanticCases(structuredClone(p)),/registered/);
});

test('native Enum and payload-sum controls verify owned definitions and cases together',t=>{
 for(const payload of [false,true]){
  const f=fixture(t,payload),n=nativeContext(f),target=path.join(f.root,'target');
  const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,publishReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 publishReconciledProject(plan,${JSON.stringify(target)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})})));`);
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
  assert.equal(semantic.result,'pass');assert.equal(semantic.executed,true);
  assert.equal(semantic.evidence.tested_node_count,2);assert.equal(semantic.evidence.remaining.length,0);
  assert.equal(report.semantic_coverage.node_count,2);assert.equal(check('semantic-workspace-currentness').result,'pass');
  assert.deepEqual(report.checks.filter((c:any)=>c.result==='not_evaluable').map((c:any)=>c.id).sort(),['safe-output-separate-from-planning']);
 const coverage=report.cross_generator_coverage;
 assert.equal(check('cross-generator-behavior').result,'pass');
 assert.equal(check('cross-generator-currentness').result,'pass');
 assert.equal(check('verification-workspace-cleanup').result,'pass');
 assert.equal(coverage.public_result,'pass');
 assert.deepEqual(coverage.blocked_by,[]);
 assert.deepEqual(coverage.execution.currentness_issues,[]);
 assert.equal(coverage.evidence_scope,'sealed-historical-report-not-a-live-retained-receipt');
 assert.equal(coverage.execution.result,'pass');
 assert.equal(coverage.execution.retained_family_count,1);
 assert.equal(coverage.execution.executed_family_count,1);
 assert.equal(coverage.execution.retained[0].family,'value-producer');
 assert.equal(coverage.retained_workspace_state,'removed');
 assert.equal(fs.existsSync(coverage.execution.workspace),false);
 assert.deepEqual(coverage.execution.rows.map((r:any)=>[r.family,r.selector,r.result,r.case_count,r.executed]),[['value-producer','alpha:status','pass',1,true],['value-producer','beta:status',payload?'inapplicable':'pass',payload?0:1,!payload]]);
  assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
  for(const a of f.plan.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
 }
});
test('compiling Enum membership, ownership, equality, key and freeze mutants cannot pass',t=>{
 const f=fixture(t),n=nativeContext(f);
 const reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['wire','bare-definition','ownership','equality','key','freeze','late-component']){
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated Enum controls'};
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late-component'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain/enums');
    const file=path.join(folder,['wire','bare-definition'].includes(mode)?'status.js':'status.component.js'),old=fs.readFileSync(file,'utf8');
    const changed=mode==='wire'?old.replace(/("Draft"\\s*:\\s*)"Draft"/,'$1"Renamed"'):
     mode==='bare-definition'?old.replace('defineEnum(','('):
     mode==='ownership'?old.replace('ownership.has(value)','true'):
     mode==='equality'?old.replace('left.variant === right.variant','true'):
     mode==='key'?old.replace('part(value.variant)','part("wrong")'):
     old.replace('Object.freeze({','({');
    if(changed===old)throw Error('Enum mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{cwd:folder,encoding:'utf8',timeout:60000});
    if(syntax.error||syntax.status!==0)throw Error('Enum mutant must remain syntactically valid:'+mode);
   }
   if(result.status===0&&args.includes('--permission')&&mode==='late-component')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/enums/status.component.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report} of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'fail',mode);
  if(mode==='late-component'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');assert.ok(semantic.blocked_by.includes('semantic-workspace-currentness'));}
  else {assert.equal(semantic.result,'fail',mode+':'+semantic.reason);assert.match(semantic.reason,mode==='bare-definition'?/ENUM_COMPONENT_NOT_OWNED/:/observation mismatch/);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
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

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
