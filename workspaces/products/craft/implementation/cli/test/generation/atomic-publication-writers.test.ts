import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {pathToFileURL} from 'node:url';
import {publishInstantiation} from '../../src/generation/publish-instantiation.ts';
import {planProjectBuild,publishProjectBuild} from '../../src/generation/project-build.ts';
import {planReconciledProject,RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE} from '../../src/generation/reconciled-project.ts';
import {publishReconciledProject} from '../../src/generation/reconciled-output.ts';
import {RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {testPlan} from '../helpers/plans.ts';

function fixture(t:any){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-atomic-writers-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 fs.writeFileSync(path.join(root,'sentinel'),'preserve');
 const source=path.join(root,'source');
 const write=(p:string,value:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value));};
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'r09-writers',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes:['total'],edges:[]});
 write('specs/alpha/nodes/total.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'total',kind:'Calculation',body:{description:'Writer fixture',inputs:[],typed_contract:{schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'R09-TOTAL',inputs:[],result:{kind:'scalar',name:'UInt64'},division_rounding:'reject',expression:{op:'literal',value:'7'}}}});
 const selection={schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'application',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:[],operations:[],workflows:[]};
 const reconciled=planReconciledProject(source,selection),legacy=testPlan('Entity');
 const build=planProjectBuild(path.resolve(import.meta.dirname,'../../fixtures/input-roots/canonical-project'),'typescript');
 const writers=[{name:'reconciled',run:(target:string)=>publishReconciledProject(reconciled,target),code:'DS_RECONCILED_OUTPUT_EXISTS'},
  {name:'legacy-node',run:(target:string)=>publishInstantiation(legacy,target),code:'MTCLI_PUBLISH_EXISTS'},
  {name:'legacy-build',run:(target:string)=>publishProjectBuild(build,target),code:'MTCLI_PROJECT_BUILD_EXISTS'}];
 return {root,writers};
}
test('all three public atomic writers preserve an empty target inserted at the final claim boundary',t=>{
 const {root,writers}=fixture(t);
 for(const writer of writers){
  const target=path.join(root,writer.name),realpath=fs.realpathSync,lstat=fs.lstatSync;
  let parentChecks=0,finalParentChecked=false,competing:fs.BigIntStats|undefined;
  fs.realpathSync=((file:any,...args:any[])=>{const result=(realpath as any)(file,...args);if(String(file)===root&&++parentChecks===4)finalParentChecked=true;return result;}) as any;
  fs.lstatSync=((file:any,...args:any[])=>{const result=(lstat as any)(file,...args);
   if(finalParentChecked&&!competing&&String(file).startsWith('/proc/self/fd/')&&path.basename(String(file)).startsWith('.domainspec-')){
    fs.mkdirSync(target);competing=lstat(target,{bigint:true});
   }return result;
  }) as any;
  try{assert.throws(()=>writer.run(target),{code:writer.code});}finally{fs.realpathSync=realpath;fs.lstatSync=lstat;}
  assert.ok(competing,writer.name+' reached the final claim boundary');
  assert.equal(fs.lstatSync(target,{bigint:true}).ino,competing.ino);assert.deepEqual(fs.readdirSync(target),[]);
  assert.deepEqual(fs.readdirSync(root).filter(n=>n.startsWith('.domainspec-')),[]);
 }
 assert.equal(fs.readFileSync(path.join(root,'sentinel'),'utf8'),'preserve');
});
test('all three public writers retain their error families and clean interrupted private staging',t=>{
 const {root,writers}=fixture(t);
 for(const writer of writers){
  const target=path.join(root,writer.name),write=fs.writeFileSync;let reached=false;
  fs.writeFileSync=((file:any,...args:any[])=>{
   if(typeof file==='number'&&fs.readlinkSync('/proc/self/fd/'+file).startsWith(root+path.sep)){reached=true;throw Error('R09 private write interrupted');}
   return (write as any)(file,...args);
  }) as any;
  try{assert.throws(()=>writer.run(target),/R09 private write interrupted/);}finally{fs.writeFileSync=write;}
  assert.ok(reached,writer.name);assert.equal(fs.existsSync(target),false);
  assert.deepEqual(fs.readdirSync(root).filter(n=>n.startsWith('.domainspec-')),[]);
 }
 assert.equal(fs.readFileSync(path.join(root,'sentinel'),'utf8'),'preserve');
});
test('simultaneous public publishers produce one complete project and preserve the competing owner', {timeout:30000},async t=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-public-writer-race-')),target=path.join(root,'target');
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));fs.writeFileSync(path.join(root,'sentinel'),'preserve');
 const publisher=pathToFileURL(path.resolve(import.meta.dirname,'../../src/generation/publish-instantiation.ts')).href;
 const plans=pathToFileURL(path.resolve(import.meta.dirname,'../helpers/plans.ts')).href;
 const program=`import {publishInstantiation} from ${JSON.stringify(publisher)};import {testPlan} from ${JSON.stringify(plans)};
 const plan=testPlan(process.argv[1]);process.send('ready');process.once('message',()=>{
  try{const result=publishInstantiation(plan,${JSON.stringify(target)});process.send({state:'published',node:result.receipt.input.node_id});}
  catch(error){process.send({state:'rejected',code:error.code});}finally{process.disconnect();}
 });`;
 const children=['Entity','State Machine'].map(kind=>spawn(process.execPath,[...process.execArgv,'--input-type=module','-e',program,kind],{stdio:['ignore','pipe','pipe','ipc']}));
 t.after(()=>{for(const child of children)if(child.exitCode===null)child.kill();});
 const exits=children.map(child=>once(child,'exit'));
 await Promise.all(children.map(async child=>assert.equal((await once(child,'message'))[0],'ready')));
 const replies=children.map(async child=>(await once(child,'message'))[0]);for(const child of children)child.send('go');
 const results=await Promise.all(replies);assert.deepEqual(results.map(r=>r.state).sort(),['published','rejected']);
 assert.equal(results.find(r=>r.state==='rejected').code,'MTCLI_PUBLISH_EXISTS');
 for(const [code]of await Promise.all(exits))assert.equal(code,0);
 const node=results.find(r=>r.state==='published').node;
 const expected=testPlan(node==='account'?'Entity':'State Machine');
 for(const artifact of expected.artifacts)assert.equal(fs.readFileSync(path.join(target,artifact.relative_path),'utf8'),artifact.content);
 assert.deepEqual(fs.readdirSync(root).sort(),['sentinel','target']);assert.equal(fs.readFileSync(path.join(root,'sentinel'),'utf8'),'preserve');
});
