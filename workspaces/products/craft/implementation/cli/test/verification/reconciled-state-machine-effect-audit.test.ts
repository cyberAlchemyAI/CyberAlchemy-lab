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
function fixture(t:any,moduleRoot='domain'){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-state-controls-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(p:string,value:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 const edge=(event:string,machine:string)=>{const id=event+'-advances-'+machine;edges.push(id);write('specs/alpha/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:id,relationship:'transitions',source_node_id:event,target_node_id:machine,scope:'feature'});};
 const parameters=[{name:'amount',type:scalar('UInt64')}];
 node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-ALLOWED',parameters,expression:{op:'lt',left:{op:'literal',type:'UInt64',value:'100'},right:at('amount')}}});
 node('forward','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-FORWARD',parameters,expression:{op:'rule_ref',selector:'alpha:allowed',arguments:[{parameter:'amount',value:at('amount')}]}}});
 for(const id of ['requested','completed','unrelated'])node(id,'Event',{event_type:id,version:'1',occurrence_id:{field_id:'id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[]});
 const c:any={schema_version:'domainspec.typed-state-machine/v1',ontology_state_machine:'TEST-LIFECYCLE',inputs:[...parameters,{name:'unused',type:scalar('Bool')}],states:['draft','submitted','closed'],initial:'draft',transitions:[
  {transition_id:'submit',source_state:'draft',target_state:'submitted',trigger_event_ref:'alpha:requested',guard:{selector:'alpha:forward',arguments:[{parameter:'amount',value:at('amount')}]},output_intents:[{slot:'primary',event_ref:'alpha:completed'},{slot:'audit',event_ref:'alpha:completed'}]},
  {transition_id:'close',source_state:'submitted',target_state:'closed',trigger_event_ref:'alpha:completed',guard:null,output_intents:[]},
  {transition_id:'repeat',source_state:'closed',target_state:'closed',trigger_event_ref:'alpha:requested',guard:null,output_intents:[]}
 ]};
 node('lifecycle','State Machine',{typed_contract:c});
 node('guardless','State Machine',{typed_contract:{...c,ontology_state_machine:'TEST-GUARDLESS',inputs:[],states:['idle'],initial:'idle',transitions:[{...c.transitions[2],source_state:'idle',target_state:'idle'}]}});
 edge('requested','lifecycle');edge('completed','lifecycle');edge('requested','guardless');
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'state-controls',features:['alpha'],cross_feature_edges:[]});write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges});};save();
 const selection={...publicSelection(moduleRoot),factories:[],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,root:temp,source,selection,graph,plan,c,node,edge,save};
}
test('public reducer effect audits reject ambient code without relying on changed outcomes',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['global','rule-global','source-global','class','class-expression','await','date','escaped-global','depth',...['process','Math','Promise','fetch','require','eval','Function','setTimeout','setInterval','queueMicrotask','WebSocket'].map(n=>'ambient:'+n)]){
  let nativeCalls=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated effect audit'};
   if(args.includes('--permission'))nativeCalls++;
   const config=args[args.indexOf('--project')+1],sourcePhase=mode==='source-global';
   const install=()=>{
    const folder=sourcePhase?path.join(path.dirname(config),'domain/features/alpha/src/domain'):path.join(path.dirname(config),'modules/domain/features/alpha/src/domain');
    const file=path.join(folder,mode==='rule-global'?'rules/allowed.js':'state-machines/lifecycle.provider.'+(sourcePhase?'ts':'js'));
    const suffix=mode==='class'?'class ForbiddenUnused {}':mode==='await'?'await 0;':mode==='date'?'void Date.now();':mode==='escaped-global'?'Object.defineProperty(glo\\\\u0062alThis,"auditLeak",{value:1,configurable:true});':'Object.defineProperty(globalThis,"auditLeak",{value:1,configurable:true});';
    const installed=mode.startsWith('ambient:')?'void '+mode.slice(8)+';':mode==='class-expression'?'void class {};':mode==='depth'?'void '+'['.repeat(520)+'0'+']'.repeat(520)+';':suffix;
    fs.appendFileSync(file,'\\n'+installed+'\\n');
    if(!sourcePhase){const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('effect mutation must compile:'+mode+':'+syntax.stderr);}
   };
   if(sourcePhase&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))install();
   const result=original(command,args,settings);
   if(!sourcePhase&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json'))install();
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
  if(mode!=='source-global')assert.equal(check('selected-generator-semantic-controls').result,'fail',mode+':'+check('selected-generator-semantic-controls').reason);
  const audit=check(mode==='source-global'?'state-machine-source-effect-audit':'state-machine-native-effect-audit');
  assert.equal(audit?.result,'fail',mode);assert.match(audit.reason,/STATE_MACHINE_EFFECT_AUDIT/);
  assert.equal(nativeCalls,0,mode);if(mode==='depth')assert.match(audit.reason,/bounded AST capacity exceeded/);
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});

test('audit observation substitution and artifact drift cannot authorize native execution',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['source-omit','native-phase','native-hash','source-script','native-script','late']){
  let nativeCalls=0,auditScript='';
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for audit custody'};
   if(args.includes('--permission'))nativeCalls++;
   const result=original(command,args,settings),script=args.find(a=>String(a).endsWith('/state-machine-effects.mjs'));
   if(script&&result.status===0){
    auditScript=script;const observed=JSON.parse(result.stdout);
    if(mode==='source-omit'&&observed.phase==='source'){observed.modules.pop();result.stdout=JSON.stringify(observed);}
    if(mode==='native-phase'&&observed.phase==='native'){observed.phase='source';result.stdout=JSON.stringify(observed);}
    if(mode==='native-hash'&&observed.phase==='native'){observed.modules[0].source_sha256='0'.repeat(64);result.stdout=JSON.stringify(observed);}
    if(mode===observed.phase+'-script')fs.appendFileSync(script,'\\n// changed after audit\\n');
   }
   if(mode==='late'&&args.includes('--permission')&&result.status===0)fs.appendFileSync(auditScript,'\\n// late change\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
  assert.equal(report.result,'fail',mode);
  if(mode==='late'){
   assert.ok(nativeCalls>0);assert.equal(check('state-machine-effect-audit-currentness').result,'fail');
   for(const id of ['state-machine-source-effect-audit','state-machine-native-effect-audit','selected-generator-semantic-controls'])assert.equal(check(id).result,'not_evaluable',id);
  }else{
   assert.equal(nativeCalls,0,mode+': changed or unbound audit must stop before native execution');
   assert.equal(check(mode.startsWith('source')?'state-machine-source-effect-audit':'state-machine-native-effect-audit').result,'fail',mode);
  }
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
});
test('literal words remain valid and unmet finite witnesses retain the full source effect audit',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 const file=path.join(source,'specs/alpha/nodes/lifecycle.json'),baseline=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const mode of ['literal','capacity','capacity-forbidden']){
  const node=JSON.parse(JSON.stringify(baseline));if(mode!=='literal')node.body.typed_contract.inputs=Array.from({length:128},(_,i)=>({name:i===0?'amount':'value_'+i,type:{kind:'scalar',name:'UInt64'}}));fs.writeFileSync(file,JSON.stringify(node));
  let nativeCalls=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated audit scope'};
   if(args.includes('--permission'))nativeCalls++;
   const config=args[args.indexOf('--project')+1];
   if(mode==='capacity-forbidden'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/domain/state-machines/lifecycle.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(mode==='literal'&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json'))fs.appendFileSync(path.join(path.dirname(config),'modules/domain/features/alpha/src/domain/state-machines/lifecycle.provider.js'),'\\n// class await globalThis process Date Math Promise fetch require eval Function setTimeout setInterval queueMicrotask WebSocket\\nvoid "class await globalThis process Date Math Promise fetch require eval Function setTimeout setInterval queueMicrotask WebSocket";\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}
  finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),source=check('state-machine-source-effect-audit'),native=check('state-machine-native-effect-audit'),semantic=check('selected-generator-semantic-controls');
  if(mode==='capacity-forbidden'){assert.equal(source.result,'fail',source.reason);assert.match(source.reason,/STATE_MACHINE_EFFECT_AUDIT/);assert.equal(nativeCalls,0);}
  else{
   assert.equal(source.result,'pass',source.reason);assert.deepEqual(source.evidence.selectors,['alpha:guardless','alpha:lifecycle']);assert.equal(source.evidence.module_count,6);
   assert.equal(native.result,'pass',native.reason);assert.equal(semantic.result,mode==='capacity'?'not_evaluable':'pass',semantic.reason);assert.ok(nativeCalls>0);
   if(mode==='capacity'){assert.deepEqual(native.evidence.selectors,['alpha:guardless']);assert.equal(native.evidence.module_count,2);assert.ok(semantic.evidence.remaining.some((r:any)=>r.selector==='alpha:lifecycle'));assert.ok(!native.evidence.modules.some((m:any)=>m.relative_path.includes('lifecycle')));}
   else{assert.equal(native.evidence.module_count,6);assert.deepEqual(semantic.evidence.remaining,[]);}
   assert.equal(check('state-machine-effect-audit-currentness').result,'pass');
  }
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 assert.deepEqual(fs.readdirSync(path.join(f.temp,'scratch')),[]);
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
