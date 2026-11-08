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
const scalar=(name:string)=>({kind:'scalar',name}),at=(root:string)=>({op:'path',root,properties:[]});
import {stateMachineFixture as fixture} from '../helpers/state-machine-project.ts';
test('State Machine controls preserve state, trigger, guard, initial state and ordered repeated output intents',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(controls.node_count,f.graph.nodes.length);
 const row=controls.rows.find(r=>r.selector==='alpha:lifecycle') as any;
 assert.equal(row.state,'ready',row.reason);assert.equal(row.declared_pair_count,6);
 assert.deepEqual(row.source_predicted_transitions,['close','repeat','submit']);assert.ok(Object.isFrozen(row.cases));
 assert.ok(row.module_paths.every((p:string)=>p.includes('/rules/')||p.includes('/state-machines/')));
 assert.deepEqual(row.native_imports.map((m:any)=>m.relative_path),row.module_paths);assert.ok(Object.isFrozen(row.native_imports));
 assert.deepEqual(row.cases[0].expected,{kind:'value',value:'draft'});
 const outcomes=row.cases.filter((c:any)=>c.mode!=='initial-state'&&c.expected.kind==='value').map((c:any)=>JSON.parse(c.expected.value));
 assert.ok(outcomes.some((v:any)=>v.status==='rejected'&&v.reason==='guard'&&v.state==='draft'));
 assert.ok(outcomes.some((v:any)=>v.status==='rejected'&&v.reason==='no-transition'&&v.state==='closed'));
 assert.ok(outcomes.some((v:any)=>v.status==='transitioned'&&v.state==='submitted'&&v.transition_id==='submit'&&JSON.stringify(v.output_intents)===JSON.stringify([{event_ref:'alpha:completed',slot:'primary'},{event_ref:'alpha:completed',slot:'audit'}])));
 assert.ok(row.cases.some((c:any)=>c.expected.message==='STATE_MACHINE_INPUT'&&JSON.parse(c.values[1]).value==='closed'&&JSON.parse(c.values[2]).value==='alpha:completed'));
 const guardless=controls.rows.find(r=>r.selector==='alpha:guardless') as any;assert.equal(guardless.state,'ready',guardless.reason);assert.equal(guardless.module_paths.length,2);
 assert.ok(guardless.cases.some((c:any)=>c.expected.kind==='value'&&c.expected.value.includes('"transition_id":"repeat"')));
 const moved=fixture(t,'other/native'),other=createReconciledSemanticControls(moved.graph,moved.plan);
 for(const row of controls.rows.filter(r=>r.state==='ready')){const b=other.rows.find(r=>r.selector===row.selector) as any;assert.deepEqual((row as any).cases,b.cases);assert.deepEqual((row as any).recipes,b.recipes);}
});
test('native State Machine and Event controls retain independent outcomes and module closures',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),n=nativeContext(f);
 const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(semantic.result,'pass',semantic.reason);assert.equal(semantic.evidence.tested_node_count,controls.ready_count);
 assert.deepEqual(semantic.evidence.remaining,[]);
 for(const phase of ['source','native']){
  const audit=check('state-machine-'+phase+'-effect-audit');assert.equal(audit.result,'pass',audit.reason);
  assert.equal(audit.evidence.phase,phase);assert.deepEqual(audit.evidence.selectors,['alpha:guardless','alpha:lifecycle']);
  assert.equal(audit.evidence.definition_sha256,'76dc0df7b5a296b350809a381cb7528a6ccf81722190afc43a716c16b5c4fdac');
  assert.equal(audit.evidence.module_count,6);assert.ok(audit.evidence.modules.every((m:any)=>!m.relative_path.includes('/events/')&&m.violations.length===0));
 }
 assert.equal(check('state-machine-effect-audit-currentness').result,'pass');
 assert.equal(check('semantic-workspace-currentness').result,'pass');assert.equal(check('verification-workspace-cleanup').result,'pass');assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('State Machine capacity retains the whole source node without a passing prefix',t=>{
 const f=fixture(t);f.c.inputs=Array.from({length:128},(_,i)=>({name:i===0?'amount':'value_'+i,type:scalar('UInt64')}));f.node('lifecycle','State Machine',{typed_contract:f.c});f.save();
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),controls=createReconciledSemanticControls(graph,plan),row=controls.rows.find(r=>r.selector==='alpha:lifecycle') as any;
 assert.equal(controls.node_count,graph.nodes.length);assert.equal(row.state,'not_evaluable');assert.match(row.reason,/bounded State Machine/);assert.equal('cases' in row,false);
});

test('compiling reducer mutations, forbidden imports and late drift cannot pass semantic verification',t=>{
 const f=fixture(t),n=nativeContext(f),forbidden=path.join(f.temp,'forbidden-state-effect');
 const reports:any[]=[];
 const modes=['initial','target','identity','source-state','trigger','event-ref','guard','argument','rule','reason','order','collapse','unfreeze','slot-unfreeze','extra','carrier','validation','mutation','invalid-number','error','event-import','caught-import','write','late'];
 for(let offset=0;offset<modes.length;offset+=2){
  const batch=modes.slice(offset,offset+2);
  const observed=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ${JSON.stringify(batch)}){
  process.stderr.write('State Machine mutation start: '+mode+'\\n');
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated State Machine controls'};
   const started=performance.now();process.stderr.write('State Machine subprocess start: '+mode+' '+path.basename(command)+'\\n');
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   process.stderr.write('State Machine subprocess end: '+mode+' '+path.basename(command)+' '+JSON.stringify({elapsed_ms:performance.now()-started,status:result.status,error:result.error?.code})+'\\n');
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain'),file=path.join(folder,mode==='rule'?'rules/allowed.js':'state-machines/lifecycle.provider.js'),old=fs.readFileSync(file,'utf8');let changed=old;
    if(mode==='initial')changed=old.replace('initialState = "draft"','initialState = "closed"');
    if(mode==='target')changed=old.replace('state: "submitted", transition_id: "submit"','state: "closed", transition_id: "submit"');
    if(mode==='identity')changed=old.replace('transition_id: "submit"','transition_id: "close"');
    if(mode==='source-state')changed=old.replace('state === "draft"','state === "closed"');
    if(mode==='trigger')changed=old.replace('trigger === "alpha:requested"','trigger === "alpha:completed"');
    if(mode==='event-ref')changed=old.replace('event_ref: "alpha:completed"','event_ref: "alpha:requested"');
    if(mode==='guard')changed=old.replace('if (!condition0(', 'if (condition0(');
    if(mode==='argument')changed=old.replace('["amount"]: p0','["amount"]: 101n');
    if(mode==='rule')changed=old.replace('(100n < p0)','(101n < p0)');
    if(mode==='reason')changed=old.replace('reason: "guard"','reason: "no-transition"');
    if(mode==='order')changed=old.replace('slot: "primary"','slot: "__swap__"').replace('slot: "audit"','slot: "primary"').replace('slot: "__swap__"','slot: "audit"');
    if(mode==='collapse')changed=old.replace(', Object.freeze({ slot: "audit", event_ref: "alpha:completed" })','');
    if(mode==='unfreeze')changed=old.replaceAll('Object.freeze(', 'Object(');
    if(mode==='slot-unfreeze')changed=old.replace('Object.freeze({ slot: "primary"','Object({ slot: "primary"');
    if(mode==='extra')changed=old.replace('status: "transitioned",','status: "transitioned", unexpected: true,');
    if(mode==='carrier')changed=old.replace('status: "transitioned", state: "submitted"','status: "transitioned", state: true');
    if(mode==='validation')changed=old.replace('const reduce = (state, trigger, parameters) => {','const reduce = (state, trigger, parameters) => { if(state==="closed" && trigger==="alpha:completed") return Object.freeze({status:"rejected",state,reason:"no-transition",output_intents:Object.freeze([])});');
    if(mode==='mutation')changed=old.replace('checkData(parameters);','checkData(parameters); Object.preventExtensions(parameters);');
    if(mode==='invalid-number')changed=old.replace('const reduce = (state, trigger, parameters) => {','const reduce = (state, trigger, parameters) => { const before = parameters && typeof parameters === "object" ? Object.getOwnPropertyDescriptor(parameters,"amount") : undefined; if(before && Object.hasOwn(before,"value") && Number.isNaN(before.value)) parameters.amount=Infinity;');
    if(mode==='error')changed=old.replaceAll('STATE_MACHINE_INPUT','RULE_INPUT');
    if(mode==='event-import')changed=old+'\\nimport "../events/completed.js";\\n';
    if(mode==='caught-import')changed=old+'\\nimport("../events/completed.js").catch(()=>{});\\n';
    if(mode==='write')changed=old+'\\n(await import("node:fs")).writeFileSync('+JSON.stringify(${JSON.stringify(forbidden)})+',"forbidden");\\n';
    if(changed===old)throw Error('State Machine mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{cwd:folder,encoding:'utf8',timeout:60000});if(syntax.error||syntax.status!==0)throw Error('State Machine mutant must compile:'+mode);
   }
   if(result.status===0&&args.includes('--permission')&&mode==='late')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/state-machines/lifecycle.provider.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools)});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`,'mutation batch: '+batch.join(', '));
  assert.deepEqual(observed.map((r:any)=>r.mode),batch,'complete native mutation batch');
  reports.push(...observed);
  t.diagnostic('native mutation batch completed: '+batch.join(', '));
 }
 assert.deepEqual(reports.map(r=>r.mode),modes,'complete ordered mutation coverage');
 for(const {mode,report}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.equal(report.result,'fail',mode);
  if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(check('state-machine-native-effect-audit').result,'not_evaluable');assert.equal(semantic.result,'not_evaluable');}
  else{assert.equal(semantic.result,'fail',mode+':'+semantic.reason);if(!['write','event-import','caught-import'].includes(mode))assert.match(semantic.reason,/observation mismatch/,mode);}
  if(mode==='event-import')assert.match(semantic.reason,/STATE_MACHINE_NATIVE_IMPORT_BOUNDARY/,mode);
  if(['caught-import','write'].includes(mode)){assert.match(semantic.reason,/STATE_MACHINE_EFFECT_AUDIT/,mode);assert.equal(check('state-machine-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.equal(fs.existsSync(forbidden),false);assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('structured reducer facts bind list-to-set guards and preserve optional and sum inputs',t=>{
 const f=fixture(t),choice={kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'TEST-CHOICE#None'},{name:'Amount',payload:scalar('UInt64'),ontology_variant:'TEST-CHOICE#Amount'}]};
 f.node('contains','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-CONTAINS',parameters:[{name:'values',type:{kind:'set',element:scalar('String')}}],expression:{op:'contains',left:at('values'),right:{op:'literal',type:'String',value:'approved'}}}});
 const file=path.join(f.source,'specs/alpha/nodes/guardless.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 raw.body.typed_contract.inputs=[{name:'values',type:{kind:'list',element:scalar('String')}},{name:'note',type:{kind:'optional',element:scalar('String')}},{name:'choice',type:choice}];
 raw.body.typed_contract.transitions[0].guard={selector:'alpha:contains',arguments:[{parameter:'values',value:{op:'to_set',value:at('values')}}]};
 fs.writeFileSync(file,JSON.stringify(raw));f.save();
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),controls=createReconciledSemanticControls(graph,plan),row=controls.rows.find(r=>r.selector==='alpha:guardless') as any;
 assert.equal(row.state,'ready',row.reason);assert.ok(row.recipes.some((r:any)=>r.tag==='scalar'&&r.value==='approved'));
 const values=row.cases.filter((c:any)=>c.mode!=='initial-state'&&c.expected.kind==='value').map((c:any)=>JSON.parse(c.expected.value));
 assert.ok(values.some((r:any)=>r.status==='rejected'&&r.reason==='guard'));assert.ok(values.some((r:any)=>r.status==='transitioned'));
 const n=nativeContext(f),report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass',semantic.reason);assert.equal(semantic.evidence.tested_node_count,controls.ready_count);
 assert.deepEqual(semantic.evidence.remaining,[]);
});
test('native reducer runs while every Event module is poisoned and rejects an introduced Event import',t=>{
 const f=fixture(t),n=nativeContext(f),result=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {pathToFileURL} from 'node:url';
 import {loadCompiledProjectGraph,planCompiledReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),root=${JSON.stringify(f.temp)},source=path.join(root,'event-isolation'),output=path.join(root,'event-isolation-js');
 for(const a of plan.resolved.artifacts){const file=path.join(source,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 cp.execFileSync('tsc',['--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','NodeNext','--rootDir',source,'--outDir',output,...plan.resolved.artifacts.filter(a=>a.relative_path.endsWith('.ts')).map(a=>path.join(source,a.relative_path))],{encoding:'utf8',timeout:60000});
 const poisoned=plan.resolved.modules.filter(m=>m.relative_path.includes('/events/'));
 for(const m of poisoned)fs.writeFileSync(path.join(output,m.relative_path.replace(/\\.ts$/,'.js')),'throw new Error("EVENT_MODULE_LOADED");\\n');
 const file=path.join(output,'domain/features/alpha/src/domain/state-machines/lifecycle.js'),client='import {transitionLifecycle,initialState} from '+JSON.stringify(pathToFileURL(file).href)+';console.log(JSON.stringify([initialState,transitionLifecycle("draft","alpha:requested",{amount:101,unused:false}),transitionLifecycle("draft","alpha:requested",{amount:1,unused:true}),transitionLifecycle("closed","alpha:completed",{amount:101,unused:false})]));';
 const check=()=>cp.spawnSync(process.execPath,['--input-type=module','--eval',client],{cwd:root,encoding:'utf8',timeout:60000});
 const baseline=check();
 fs.appendFileSync(file.replace(/lifecycle\\.js$/,'lifecycle.provider.js'),'\\nimport "../events/completed.js";\\n');
 const imported=check();
 console.log(JSON.stringify({poisoned:poisoned.length,baseline:{status:baseline.status,stdout:baseline.stdout,stderr:baseline.stderr},imported:{status:imported.status,stderr:imported.stderr}}));`);
 assert.ok(result.poisoned>=3);assert.equal(result.baseline.status,0,result.baseline.stderr);
 assert.deepEqual(JSON.parse(result.baseline.stdout),['draft',{status:'transitioned',state:'submitted',transition_id:'submit',output_intents:[{slot:'primary',event_ref:'alpha:completed'},{slot:'audit',event_ref:'alpha:completed'}]},{status:'rejected',state:'draft',reason:'guard',output_intents:[]},{status:'rejected',state:'closed',reason:'no-transition',output_intents:[]}]);
 assert.notEqual(result.imported.status,0);assert.match(result.imported.stderr,/EVENT_MODULE_LOADED/);
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
 const run=(body:string,label='native client')=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(JSON.stringify({label,message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
