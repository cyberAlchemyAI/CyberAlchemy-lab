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
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
function fixture(t:any,impossible=false,moduleRoot='domain',extensions=2,mixed=false){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-factory-controls-')),source=path.join(root,'source'),nodes:string[]=[];
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,v:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:unknown)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body});};
 const scalar=(name:string)=>({kind:'scalar',name}),p=(root:string)=>({op:'path',root,properties:[]}),lit=(type:string,value:unknown)=>({op:'literal',type,value}),eq=(left:unknown,right:unknown)=>({op:'eq',left,right});
 const rule=(id:string,type:string,expression:unknown)=>node(id,'Rule',{description:id,predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-'+id.toUpperCase(),parameters:[{name:'value',type:scalar(type)}],expression}});
 rule('nonempty','String',{op:'not',term:eq(p('value'),lit('String',''))});
 for(let i=0;i<extensions;i++)rule('extension-'+String.fromCharCode(97+i),i===0?'String':'Bool',impossible&&i===0?eq(lit('Bool',true),lit('Bool',false)):eq(p('value'),lit(i===0?'String':'Bool',i===0?'approved':true)));
 const fields:[string,any][]=[['id',scalar('String')],['label',scalar('String')],['enabled',scalar('Bool')],['note',{kind:'optional',element:scalar('String')}]];
 if(mixed){
  const variants=[{name:'Off',payload:null,ontology_variant:'TEST-CHOICE#off'},{name:'On',payload:scalar('UInt64'),ontology_variant:'TEST-CHOICE#on'}];
  node('choice','Enum',{description:'Exact payload',values:['Off','On'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-CHOICE',variants}});
  fields.push(['extra',scalar('String')],['payload',{kind:'named',selector:'alpha:choice'}],['branches',{kind:'list',element:{kind:'sum',variants:[{name:'Empty',payload:null,ontology_variant:'TEST-BRANCH#empty'},{name:'Label',payload:scalar('String'),ontology_variant:'TEST-BRANCH#label'}]}}]);
 }
 for(const [id,kind] of [['customer','Entity'],['label','Value Object']])node(id!,kind!,{description:id,...(kind==='Value Object'?{invariant_refs:['alpha:nonempty']}:{}),fields:fields.map(([n])=>n),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-'+id!.toUpperCase(),properties:fields.map(([name,type])=>({name,type,ontology_property:'TEST-'+id!.toUpperCase()+'#'+name,identity:kind==='Entity'&&name==='id',cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':'one',meaning:name}))}});
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'factory-controls',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges:[]});
 const selection={...publicSelection(),module_root:moduleRoot,factories:['customer','label'].map(id=>({selector:'alpha:'+id,base_validators:[{rule:'alpha:nonempty',arguments:[{parameter:'value',field:'id'}]}],extensions:Array.from({length:extensions},(_,i)=>({id:'extension-'+String.fromCharCode(97+i),validators:[{rule:'alpha:extension-'+String.fromCharCode(97+i),arguments:[{parameter:'value',field:i===0?'label':'enabled'}]}]}))})),operations:[]};
 const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {root,temp:root,source,selection,graph,plan};
}
test('factory source controls cover every lifecycle route, validator order and complete node denominator',t=>{
 const f=fixture(t),c=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(c.node_count,5);assert.equal(c.ready_count,5);assert.equal(c.not_evaluable_count,0);
 for(const row of c.rows.filter(r=>r.state==='ready'&&'adapter' in r&&r.adapter==='factory') as any[]){
  const requests=row.cases.map((c:any)=>JSON.parse(c.values[0]));
  assert.deepEqual([...new Set(requests.map((r:any)=>r.chain.join(',')))].sort(),['','extension-a','extension-a,extension-b','extension-b','extension-b,extension-a']);
  assert.deepEqual([...new Set(requests.map((r:any)=>r.route))].sort(),row.kind==='Entity'?['create','extend','reconstruct','transition']:['create','extend','reconstruct']);
  const expected=row.cases.filter((c:any)=>c.expected.kind==='value').map((c:any)=>JSON.parse(c.expected.value));
  assert.ok(expected.some((v:any)=>v.ok));assert.ok(expected.some((v:any)=>v.failure_codes[0]==='INVALID_FIELDS'));
  for(const id of ['nonempty','extension-a','extension-b'])assert.ok(expected.some((v:any)=>v.failure_codes[0]==='RULE_FAIL:alpha:'+id));
  if(row.kind==='Entity'){assert.ok(expected.some((v:any)=>v.failure_codes[0]==='IDENTITY_CHANGED'));assert.ok(expected.some((v:any)=>v.failure_codes[0]==='INVALID_PREVIOUS'));}
  for(const v of expected)for(const trace of v.trace.validators){assert.match(trace.closure_sha256,/^[a-f0-9]{64}$/);assert.match(trace.artifact_sha256,/^[a-f0-9]{64}$/);}
 }
 const moved=fixture(t,false,'alternate/path'),other=createReconciledSemanticControls(moved.graph,moved.plan);
 for(const row of c.rows.filter(r=>r.state==='ready'))assert.deepEqual((other.rows.find(r=>r.selector===row.selector) as any).cases,row.cases,'layout does not alter lifecycle semantics');
});
test('unsatisfied extension or exhaustive chain capacity retains whole factory as not_evaluable',t=>{
 for(const f of [fixture(t,true),fixture(t,false,'domain',7)]){
  const c=createReconciledSemanticControls(f.graph,f.plan);assert.equal(c.node_count,f.graph.nodes.length);assert.equal(c.ready_count,f.graph.nodes.filter(n=>n.kind==='Rule').length);
  for(const row of c.rows.filter(r=>r.kind==='Entity'||r.kind==='Value Object')){assert.equal(row.state,'not_evaluable');assert.match((row as any).reason,/no satisfying base factory witness|bounded factory extension chain capacity/);}
 }
});
test('native factory lifecycle controls pass in private verification and preserve target output',t=>{
 const f=fixture(t),n=nativeContext(f),target=path.join(f.root,'target');
 const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,publishReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 publishReconciledProject(plan,${JSON.stringify(target)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})})));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));assert.equal(semantic.evidence.tested_node_count,5);assert.equal(semantic.evidence.remaining.length,0);
 assert.equal(report.checks.find((c:any)=>c.id==='semantic-workspace-currentness').result,'pass');
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
 for(const a of f.plan.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
});
test('syntax-valid lifecycle mutants and late drift cannot certify factories',t=>{
 const f=fixture(t),n=nativeContext(f);
 const reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['reconstruct-route','transition-identity','transition-owner','transition-alias','extension-order','extension-drop','extension-repeat','trace-freeze','component','late']){
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated factory controls'};
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain'),file=path.join(folder,'entities/customer.js'),old=fs.readFileSync(file,'utf8');
    let changed=old;
    if(mode==='reconstruct-route')changed=old.replace("construct('reconstruct', input)","construct('create', input)");
    if(mode==='transition-identity')changed=old.replace("construct('transition', input, previous)","construct('transition', input)");
    if(mode==='transition-owner')changed=old.replace("owned(previous) ? construct","true ? construct");
    if(mode==='transition-alias')changed=old.replace("construct('transition', input, previous)","(r => r.ok ? Object.freeze({...r,value:previous}) : r)(construct('transition', input, previous))");
    if(mode==='extension-order')changed=old.replace('[...validators, ...extensionValidators[id]]','[...extensionValidators[id], ...validators]');
    if(mode==='extension-drop')changed=old.replace('[...validators, ...extensionValidators[id]]','[...validators]');
    if(mode==='extension-repeat')changed=old.replace('extensions.includes(id)','false');
    if(mode==='trace-freeze')changed=old.replace('phases: Object.freeze([...phases])','phases: [...phases]');
    if(mode==='component')changed=old.replace('component: components[1]','component: components[0]');
    if(changed===old)throw Error('factory mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{cwd:folder,encoding:'utf8',timeout:60000});
    if(syntax.error||syntax.status!==0)throw Error('factory mutant must remain syntactically valid:'+mode);
   }
   if(result.status===0&&args.includes('--permission')&&mode==='late')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/entities/customer.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report} of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'fail',mode);
  if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');assert.ok(semantic.blocked_by.includes('semantic-workspace-currentness'));}
  else {assert.equal(semantic.result,'fail',mode+':'+semantic.reason);assert.match(semantic.reason,/observation mismatch/);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
});
test('factory fields preserve inline and named sums without conflating nested construction and normalization',t=>{
 const f=fixture(t,false,'domain',0,true),controls=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(controls.node_count,4);assert.equal(controls.ready_count,4);
 const n=nativeContext(f),report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));assert.equal(semantic.evidence.tested_node_count,4);assert.equal(semantic.evidence.remaining.length,0);
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
