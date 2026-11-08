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
import {createRecordRuleReference} from '../../src/verification/reconciled-rule-reference.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
const scalar=(name:string)=>({kind:'scalar',name}),p=(root:string,properties:string[]=[])=>({op:'path',root,properties}),lit=(type:string,value:unknown)=>({op:'literal',type,value}),eq=(left:unknown,right:unknown)=>({op:'eq',left,right});
function fixture(t:any,moduleRoot='domain'){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-policy-controls-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(name:string,value:unknown)=>{const f=path.join(source,name);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(value)+'\n');};
 const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 node('perform','Operation',{reads:[],writes:[],effects:[],guard:'allowed',failure_continuation:'return-error'});
 for(const id of ['fast','review','fallback']){
  node(id,'Calculation',{inputs:['amount'],typed_contract:{schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'TEST-'+id.toUpperCase(),inputs:[{name:'amount',type:scalar('UInt64')}],result:scalar('UInt64'),division_rounding:'reject',expression:{op:'input',name:'amount'}}});
  const edgeId=id+'-calculates-perform';edges.push(edgeId);write('specs/alpha/edges/'+edgeId+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:edgeId,relationship:'calculates',source_node_id:id,target_node_id:'perform',scope:'feature'});
 }
 const rule=(id:string,parameters:any[],expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-'+id.toUpperCase(),parameters,expression}});
 rule('high',[{name:'amount',type:scalar('UInt64')}],{op:'lt',left:lit('UInt64','100'),right:p('amount')});
 rule('forward',[{name:'amount',type:scalar('UInt64')}],{op:'rule_ref',selector:'alpha:high',arguments:[{parameter:'amount',value:p('amount')}]});
 rule('enabled',[{name:'value',type:scalar('Bool')}],eq(p('value'),lit('Bool',true)));
 rule('equal',[{name:'left',type:scalar('UInt64')},{name:'right',type:scalar('UInt64')}],eq(p('left'),p('right')));
 rule('allowed',[{name:'value',type:scalar('UInt64')}],eq(p('value'),p('value')));
 edges.push('allowed-enforces-perform');write('specs/alpha/edges/allowed-enforces-perform.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:'allowed-enforces-perform',relationship:'enforces',source_node_id:'allowed',target_node_id:'perform',scope:'feature'});
 const ruleRef=(id:string,args:any[])=>({selector:'alpha:'+id,arguments:args}),arg=(parameter:string,value:any)=>({parameter,value});
 const inputs=[{name:'total',type:scalar('UInt64')},{name:'other',type:scalar('UInt64')},{name:'active',type:scalar('Bool')}];
 const cases=[{target:'alpha:fast',rule:ruleRef('forward',[arg('amount',p('total'))])},{target:'alpha:review',rule:ruleRef('enabled',[arg('value',p('active'))])}];
 const policies:any={choose:{inputs,cases},repeated:{inputs,cases:[cases[0],cases[0]]},constant:{inputs,cases:[{target:'alpha:fast',rule:ruleRef('high',[arg('amount',lit('UInt64','101'))])}]},literal:{inputs:[inputs[0]],cases:[{target:'alpha:fast',rule:ruleRef('equal',[arg('left',p('total')),arg('right',lit('UInt64','777'))])}]}};
 const orderType={kind:'named',selector:'alpha:order'};
 node('order','Entity',{fields:['id','active','note'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-ORDER',properties:[['id',scalar('String')],['active',scalar('Bool')],['note',{kind:'optional',element:scalar('String')}]].map(([name,type]:any)=>({name,type,ontology_property:'TEST-ORDER#'+name,meaning:name,identity:name==='id',cardinality:name==='note'?'optional':'one'}))}});
 policies.structured={inputs:[{name:'order',type:orderType},{name:'tags',type:{kind:'set',element:scalar('String')}},{name:'choice',type:{kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'TEST-CHOICE#None'},{name:'Amount',payload:scalar('UInt64'),ontology_variant:'TEST-CHOICE#Amount'}]}}],cases:[{target:'alpha:fast',rule:ruleRef('enabled',[arg('value',p('order',['TEST-ORDER#active']))])}]};
 rule('contains',[{name:'values',type:{kind:'set',element:scalar('String')}}],{op:'contains',left:p('values'),right:lit('String','approved')});
 policies.collection={inputs:[{name:'values',type:{kind:'list',element:scalar('String')}}],cases:[{target:'alpha:fast',rule:ruleRef('contains',[arg('values',{op:'to_set',value:p('values')})])}]};
 for(const [id,value]of Object.entries(policies) as [string,any][]){
  const contract={schema_version:'domainspec.typed-policy/v2',ontology_policy:'TEST-'+id.toUpperCase(),...value,default_target:'alpha:fallback'};node(id,'Policy',{typed_contract:contract});
  for(const target of new Set([...value.cases.map((c:any)=>c.target),'alpha:fallback']) as Set<string>){const edgeId=id+'-applies-'+target.split(':')[1];edges.push(edgeId);write('specs/alpha/edges/'+edgeId+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:edgeId,relationship:'applies',source_node_id:id,target_node_id:target.split(':')[1],scope:'feature'});}
 }
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'policy-controls',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges});
 const selection={...publicSelection(moduleRoot),factories:[{selector:'alpha:order',base_validators:[{rule:'alpha:enabled',arguments:[{parameter:'value',field:'active'}]}],extensions:[]}],operations:[publicSelection().operations[0]]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,root:temp,source,selection,graph,plan};
}
test('Policy cases retain source order, transitive and argument literals, structural facts and unmet sensitivity',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),rows=controls.rows.filter(r=>r.kind==='Policy');
 assert.equal(rows.length,6);assert.equal(controls.node_count,f.graph.nodes.length);
 for(const r of rows)if(r.selector==='alpha:constant'){assert.equal(r.state,'not_evaluable');assert.match((r as any).reason,/input-sensitivity witnesses/);assert.equal('cases' in r,false);}else{
  assert.equal(r.state,'ready',r.selector+':'+(r as any).reason);const row=r as any;
  assert.ok(row.source_predicted_targets.length>=2);assert.ok(row.module_paths.every((p:string)=>p.includes('/policies/')||p.includes('/rules/')));
  assert.deepEqual(row.native_imports.map((m:any)=>m.relative_path),row.module_paths);assert.ok(Object.isFrozen(row.native_imports));
  assert.ok(row.cases.some((c:any)=>c.expected.message==='POLICY_INPUT'));
 }
 const choose=rows.find(r=>r.selector==='alpha:choose') as any;assert.deepEqual(choose.source_predicted_targets,['alpha:fallback','alpha:fast','alpha:review']);assert.deepEqual(choose.source_predicted_branches,[-1,0,1]);
 const reference=createRecordRuleReference(f.graph),contract=f.graph.nodes.find(n=>n.selector==='alpha:choose')!.body.typed_contract as any;
 for(const [total,active,target,index]of [[101n,true,'alpha:fast',0],[1n,true,'alpha:review',1],[1n,false,'alpha:fallback',-1]] as const){
  const values={total,other:0n,active};assert.deepEqual(reference.select(contract,new Map(contract.inputs.map((p:any)=>[p.name,{type:p.type,value:values[p.name as keyof typeof values]}]))),{target,index});
 }
 const repeated=rows.find(r=>r.selector==='alpha:repeated') as any;assert.deepEqual(repeated.source_predicted_branches,[-1,0]);
 const literal=rows.find(r=>r.selector==='alpha:literal') as any;assert.ok(literal.recipes.some((r:any)=>r.tag==='scalar'&&r.value==='777'));
 const moved=fixture(t,'elsewhere/native'),relocated=createReconciledSemanticControls(moved.graph,moved.plan);
 for(const row of rows.filter(r=>r.state==='ready')){const other=relocated.rows.find(r=>r.selector===row.selector) as any;assert.deepEqual((row as any).cases,other.cases);assert.deepEqual((row as any).recipes,other.recipes);}
});
test('native Policies observe exact selectors independently without importing strategy targets',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),n=nativeContext(f);
 const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'not_evaluable',semantic.reason);assert.equal(semantic.evidence.tested_node_count,controls.ready_count);
 const operation=controls.rows.find(r=>r.selector==='alpha:perform');
 assert.ok(operation?.state==='ready'&&operation.kind==='Operation');assert.ok(operation.cases.length>0);
 assert.deepEqual(semantic.evidence.tested.find((r:any)=>r.selector===operation.selector),{
  selector:operation.selector,kind:operation.kind,contract_sha256:operation.contract_sha256,case_count:operation.cases.length,
 });
 assert.deepEqual(semantic.evidence.remaining.map((r:any)=>r.selector),['alpha:constant']);
 assert.equal(semantic.evidence.remaining[0].kind,'Policy');assert.match(semantic.evidence.remaining[0].reason,/input-sensitivity witnesses/);
 assert.equal(report.checks.find((c:any)=>c.id==='semantic-workspace-currentness').result,'pass');assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('syntax-valid Policy mutants, forbidden effects and late drift cannot pass semantic verification',t=>{
 const f=fixture(t),n=nativeContext(f),forbidden=path.join(f.temp,'forbidden-policy-effect');
 const reports:any[]=[];
 const modes=['order','argument','default','predicate','rule','collection','carrier','target','getter','mutation','error','write','target-import','caught-import','late'];
 for(let offset=0;offset<modes.length;offset+=2){
  const batch=modes.slice(offset,offset+2);
  const observed=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ${JSON.stringify(batch)}){
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated Policy controls'};
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain'),file=path.join(folder,mode==='rule'?'rules/high.js':mode==='collection'?'policies/collection.provider.js':'policies/choose.provider.js'),old=fs.readFileSync(file,'utf8');let changed=old;
    if(mode==='order'){const lines=old.split('\\n'),indices=lines.map((line,i)=>line.includes('if (condition')?i:-1).filter(i=>i>=0);if(indices.length!==2)throw Error('two Policy cases required');[lines[indices[0]],lines[indices[1]]]=[lines[indices[1]],lines[indices[0]]];changed=lines.join('\\n');}
    if(mode==='argument')changed=old.replace('["amount"]: p0','["amount"]: p1');
    if(mode==='default')changed=old.replace('return "alpha:fallback";','return "alpha:fast";');
    if(mode==='predicate')changed=old.replace(/if \\((condition[0-9]+)\\(/,'if (!$1(');
    if(mode==='rule')changed=old.replace('(100n < p0)','(101n < p0)');
    if(mode==='collection')changed=old.replace('ruleToSet(p0, ruleString)','p0');
    if(mode==='carrier')changed=old.replace('return "alpha:fast";','return true;');
    if(mode==='target')changed=old.replace('return "alpha:fast";','return "alpha:missing";');
    if(mode==='getter')changed=old.replace('const descriptors = Object.getOwnPropertyDescriptors(input);','for(const key of Object.keys(input)) void input[key]; const descriptors = Object.getOwnPropertyDescriptors(input);');
    if(mode==='mutation')changed=old.replace('const descriptors = Object.getOwnPropertyDescriptors(input);','Object.freeze(input); const descriptors = Object.getOwnPropertyDescriptors(input);');
    if(mode==='error')changed=old.replace("TypeError('POLICY_INPUT')","TypeError('RULE_INPUT')");
    if(mode==='target-import')changed=old+'\\nimport "../calculations/fast.js";\\n';
    if(mode==='caught-import')changed=old+'\\nimport("../calculations/fast.js").catch(()=>{});\\n';
    if(mode==='write')changed=old+'\\n(await import("node:fs")).writeFileSync('+JSON.stringify(${JSON.stringify(forbidden)})+',"forbidden");\\n';
    if(changed===old)throw Error('Policy mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{cwd:folder,encoding:'utf8',timeout:60000});if(syntax.error||syntax.status!==0)throw Error('Policy mutant must compile:'+mode);
   }
   if(result.status===0&&args.includes('--permission')&&mode==='late')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/policies/choose.provider.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
  assert.deepEqual(observed.map((r:any)=>r.mode),batch,'complete native mutation batch');
  reports.push(...observed);
  t.diagnostic('native mutation batch completed: '+batch.join(', '));
 }
 assert.deepEqual(reports.map(r=>r.mode),modes,'complete ordered mutation coverage');
 for(const {mode,report}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'fail',mode);
  if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');}
  else {assert.equal(semantic.result,'fail',mode+':'+semantic.reason);if(!['write','target-import','caught-import'].includes(mode))assert.match(semantic.reason,/observation mismatch/,mode);}
  if(['target-import','caught-import'].includes(mode))assert.match(semantic.reason,/POLICY_NATIVE_IMPORT_BOUNDARY/,mode);
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.equal(fs.existsSync(forbidden),false);assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('Policy capacity preserves the entire node instead of certifying a passing prefix',t=>{
 const f=fixture(t),file=path.join(f.source,'specs/alpha/nodes/constant.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 raw.body.typed_contract.inputs=Array.from({length:128},(_,i)=>({name:'value_'+i,type:scalar('UInt64')}));
 raw.body.typed_contract.cases[0].rule.arguments[0].value=p('value_0');
 fs.writeFileSync(file,JSON.stringify(raw)+'\n');
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),controls=createReconciledSemanticControls(graph,plan),row=controls.rows.find(r=>r.selector==='alpha:constant')!;
 assert.equal(controls.node_count,graph.nodes.length);assert.equal(row.state,'not_evaluable');assert.match((row as any).reason,/bounded Policy (vector expansion|case capacity)/);assert.equal('cases' in row,false);
});
test('native Policy imports and selects correctly while every strategy module is poisoned',t=>{
 const f=fixture(t),n=nativeContext(f),result=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {pathToFileURL} from 'node:url';
 import {loadCompiledProjectGraph,planCompiledReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),root=${JSON.stringify(f.temp)},source=path.join(root,'target-isolation'),output=path.join(root,'target-isolation-js');
 for(const a of plan.resolved.artifacts){const file=path.join(source,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 cp.execFileSync('tsc',['--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','NodeNext','--rootDir',source,'--outDir',output,...plan.resolved.artifacts.filter(a=>a.relative_path.endsWith('.ts')).map(a=>path.join(source,a.relative_path))],{encoding:'utf8',timeout:60000});
 const poisoned=plan.resolved.modules.filter(m=>m.relative_path.includes('/calculations/')||m.relative_path.includes('/operations/'));
 for(const m of poisoned)fs.writeFileSync(path.join(output,m.relative_path.replace(/\\.ts$/,'.js')),'throw new Error("STRATEGY_MODULE_LOADED");\\n');
 const file=path.join(output,'domain/features/alpha/src/domain/policies/choose.js'),client='import {policyChoose} from '+JSON.stringify(pathToFileURL(file).href)+';console.log(JSON.stringify([policyChoose({total:101,other:0,active:true}),policyChoose({total:1,other:0,active:true}),policyChoose({total:1,other:0,active:false})]));';
 const check=()=>cp.spawnSync(process.execPath,['--input-type=module','--eval',client],{cwd:root,encoding:'utf8',timeout:60000});
 const baseline=check();
 fs.appendFileSync(file.replace(/choose\\.js$/,'choose.provider.js'),'\\nimport "../calculations/fast.js";\\n');
 const imported=check();
 console.log(JSON.stringify({poisoned:poisoned.length,baseline:{status:baseline.status,stdout:baseline.stdout,stderr:baseline.stderr},imported:{status:imported.status,stderr:imported.stderr}}));`);
 assert.ok(result.poisoned>=4);assert.equal(result.baseline.status,0,result.baseline.stderr);assert.deepEqual(JSON.parse(result.baseline.stdout),['alpha:fast','alpha:review','alpha:fallback']);assert.notEqual(result.imported.status,0);assert.match(result.imported.stderr,/STRATEGY_MODULE_LOADED/);
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
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(JSON.stringify({message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(JSON.stringify({message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
