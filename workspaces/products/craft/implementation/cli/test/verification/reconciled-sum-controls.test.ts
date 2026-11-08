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
function fixture(t:any,record=false,moduleRoot='domain',capacity=false){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-sum-controls-')),source=path.join(root,'source'),nodes:string[]=[];
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,v:unknown)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:unknown)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body});};
 const scalar=(name:string)=>({kind:'scalar',name}),named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:unknown)=>({kind,element});
 const variants=(values:[string,any][])=>values.map(([name,payload])=>({name,payload,ontology_variant:'TEST-VARIANT#'+name}));
 const sum=(id:string,values:[string,any][])=>node(id,'Enum',{description:id,values:values.map(v=>v[0]),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-'+id.toUpperCase(),variants:variants(values)}});
 sum('state',[['Open',null],['Closed',null]]);
 sum('amount',[['First',scalar('UInt64')],['Other',scalar('UInt64')],['None',null]]);
 sum('detail',[['Text',scalar('String')],['Flag',scalar('Bool')],['Maybe',wrap('optional',scalar('String'))],['List',wrap('list',scalar('UInt64'))],['Set',wrap('set',scalar('UInt64'))],['Inline',{kind:'sum',variants:variants([['Absent',null],['Present',wrap('optional',scalar('Bool'))]])}],['None',null]]);
 sum('choice',[['Amount',named('amount')],['List',wrap('list',named('amount'))],['Set',wrap('set',named('amount'))],['Maybe',wrap('optional',named('amount'))],['State',named('state')],['None',null]]);
 if(capacity){
  sum('wide-zero',[['A',scalar('String')],['B',scalar('String')],['C',scalar('String')]]);
  let previous='wide-zero';for(let i=1;i<=5;i++){const id='wide-'+i;sum(id,[['A',named(previous)],['B',named(previous)],['C',named(previous)]]);previous=id;}
 }
 if(record){
  node('valid','Rule',{description:'Explicit factory validator.',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-VALID',parameters:[{name:'value',type:scalar('String')}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}}});
  node('customer','Entity',{description:'Independent factory witness required.',fields:['id'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-CUSTOMER',properties:[{name:'id',ontology_property:'TEST-CUSTOMER#id',type:scalar('String'),cardinality:'one',identity:true,meaning:'identity'}]}});
  sum('record-choice',[['None',null],['Customer',named('customer')]]);
 }
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'sum-controls',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges:[]});
 const selection={...publicSelection(),module_root:moduleRoot,factories:record?[{selector:'alpha:customer',base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:'id'}]}],extensions:[]}]:[],operations:[]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {root,temp:root,source,selection,graph,plan};
}
test('recursive sum controls preserve variant coverage, exact carriers, collections and record dependency accounting',t=>{
 const f=fixture(t),p=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(p.node_count,4);assert.equal(p.ready_count,4);assert.equal(p.not_evaluable_count,0);
 const row=(id:string)=>p.rows.find(r=>r.selector==='alpha:'+id&&r.state==='ready') as any;
 for(const id of ['amount','detail','choice']){
  const r=row(id),positive=r.cases.filter((c:any)=>c.expected.kind==='value');
  assert.deepEqual([...new Set(positive.map((c:any)=>JSON.parse(c.values[0]).variant))].sort(),[...r.names].sort());
  assert.ok(r.cases.some((c:any)=>c.expected.kind==='error'));assert.equal(r.adapter,'sum');
 }
 const amount=row('amount'),max=amount.cases.filter((c:any)=>c.expected.kind==='value'&&JSON.parse(c.values[0]).payload?.value==='18446744073709551615');
 assert.equal(max.length,4);for(const c of max)assert.equal(JSON.parse(c.expected.value).view.payload.value,'18446744073709551615');
 const positive=row('detail').cases.filter((c:any)=>c.expected.kind==='value'),sets=positive.filter((c:any)=>{const r=JSON.parse(c.values[0]);return r.variant==='Set'&&r.payload.items.length===2;}),lists=positive.filter((c:any)=>{const r=JSON.parse(c.values[0]);return r.variant==='List'&&r.payload.items.length===2;});
 assert.equal(sets.length,2);assert.equal(JSON.parse(sets[0].expected.value).key,JSON.parse(sets[1].expected.value).key);
 assert.notEqual(JSON.parse(lists[0].expected.value).key,JSON.parse(lists[1].expected.value).key);
 assert.ok(row('detail').cases.some((c:any)=>c.expected.message==='DUPLICATE_SET_VALUE'));
 const f2=fixture(t,true),full=createReconciledSemanticControls(f2.graph,f2.plan);
 assert.equal(full.node_count,7);assert.equal(full.ready_count,7);assert.equal(full.not_evaluable_count,0);
 assert.equal(full.rows.find(r=>r.selector==='alpha:record-choice')!.state,'ready');
 assert.equal(full.rows.find(r=>r.selector==='alpha:customer')!.state,'ready','separate factory adapter supplies lifecycle controls');
 const moved=fixture(t,false,'alternate/nested'),other=createReconciledSemanticControls(moved.graph,moved.plan);
 for(const id of ['amount','detail','choice'])assert.deepEqual((other.rows.find(r=>r.selector==='alpha:'+id) as any).cases,row(id).cases);
 const actual=p.rows.filter(r=>r.state==='ready').map(r=>({selector:r.selector,cases:r.cases.map(c=>({id:c.id,outcome:c.expected,getter_reads:0,input_changed:false}))}));
 assert.equal(checkSemanticObservations(p,canonicalJson(actual)).tested_node_count,4);
 actual[0]!.cases[0]!.getter_reads=1;assert.throws(()=>checkSemanticObservations(p,canonicalJson(actual)),/observation mismatch/);
 assert.throws(()=>renderSemanticCases(structuredClone(p)),/registered/);
 const large=fixture(t,false,'domain',true),bounded=createReconciledSemanticControls(large.graph,large.plan);
 assert.equal(bounded.node_count,large.graph.nodes.length);assert.deepEqual(bounded.rows.map(r=>r.selector),large.graph.nodes.map(n=>n.selector));
 assert.ok(bounded.rows.some(r=>r.state==='not_evaluable'&&/bounded sum/.test(r.reason)),'capacity remains unmet instead of dropping source variants');
});

test('real native recursive sums retain exact values, ownership, collections and deep input immutability',t=>{
 const f=fixture(t),n=nativeContext(f),target=path.join(f.root,'target');
 const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,publishReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 publishReconciledProject(plan,${JSON.stringify(target)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})})));`);
 const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
 assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
 assert.equal(semantic.result,'pass',semantic.reason);assert.equal(semantic.evidence.tested_node_count,4);assert.equal(semantic.evidence.remaining.length,0);
 assert.equal(check('semantic-workspace-currentness').result,'pass');
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
 assert.deepEqual(coverage.execution.rows.map((r:any)=>[r.family,r.selector,r.result,r.case_count,r.executed]),[['value-producer','alpha:amount','inapplicable',0,false],['value-producer','alpha:choice','pass',383,true],['value-producer','alpha:detail','inapplicable',0,false],['value-producer','alpha:state','pass',1,true]]);
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
 for(const a of f.plan.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
});

test('syntax-valid sum and collection mutants, input effects and late module drift cannot pass',t=>{
 const f=fixture(t),n=nativeContext(f);
 const reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['tag','payload','precision','equality','ownership','list','duplicates','freeze','getter','mutation','late']){
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated sum controls'};
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain/enums'),file=path.join(folder,['list','duplicates','freeze','mutation'].includes(mode)?'detail.sum.js':'amount.sum.js'),old=fs.readFileSync(file,'utf8');
    let changed=old;
    if(mode==='tag')changed=old.replace('{ variant, payload }','{ variant: "Other", payload }');
    if(mode==='payload')changed=old.replace('protocol.normalize(descriptors.payload.value)','protocol.normalize("0")');
    if(mode==='precision')changed=old.replaceAll('value = BigInt(input);','value = BigInt(Number(input));');
    if(mode==='equality')changed=old.replace('cases.get(left) === cases.get(right)','true');
    if(mode==='ownership')changed=old.replace('cases.has(value)','true');
    if(mode==='list')changed=old.replace('sequenceValue(element, false)','sequenceValue(element, true)');
    if(mode==='duplicates')changed=old.replace(/throw new TypeError\\(['"]DUPLICATE_SET_VALUE['"]\\);/,'void 0;');
    if(mode==='freeze')changed=old.replace('Object.freeze(entries.map(entry => entry.value))','entries.map(entry => entry.value)');
    if(mode==='getter')changed=old.replaceAll('const descriptors = Object.getOwnPropertyDescriptors(input);','const descriptors = Object.getOwnPropertyDescriptors(input); if (descriptors.variant?.get) void input.variant;');
    if(mode==='mutation')changed=old.replace('const result = Object.freeze(entries.map(entry => entry.value));','input.reverse(); const result = Object.freeze(entries.map(entry => entry.value));');
    if(changed===old)throw Error('sum mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{cwd:folder,encoding:'utf8',timeout:60000});
    if(syntax.error||syntax.status!==0)throw Error('sum mutant must remain syntactically valid:'+mode);
   }
   if(result.status===0&&args.includes('--permission')&&mode==='late')fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/domain/enums/amount.sum.js'),' ');
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
