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
import {recordWitnesses,resolveRecordWitness,RecordWitnessUnavailable} from '../../src/verification/reconciled-record-witness.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
import {recordWitnessFixture as fixture, named, wrap} from '../helpers/record-witness-project.ts';
test('source-derived owned record witnesses retain Rules, identity/value equality and complete coverage',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),row=controls.rows.find(r=>r.selector==='alpha:choice') as any;
 assert.equal(row.state,'ready',row.reason);assert.equal(controls.node_count,7);assert.equal(controls.ready_count,7);assert.equal(controls.not_evaluable_count,0);
 for(const id of ['money','customer']){
  const d=row.dependencies['alpha:'+id];assert.ok(d.probes.some((p:any)=>p.expected.ok));assert.ok(d.probes.some((p:any)=>!p.expected.ok),'source-derived validator rejection probe');
  assert.ok(d.probes.every((p:any)=>p.expected.trace.validators.length>0));assert.equal(controls.rows.find(r=>r.selector==='alpha:'+id)!.state,'ready');
 }
 const positive=row.cases.filter((c:any)=>c.expected.kind==='value');
 assert.deepEqual([...new Set(positive.map((c:any)=>JSON.parse(c.values[0]).variant))].sort(),[...row.names].sort());
 const customer=positive.filter((c:any)=>JSON.parse(c.values[0]).variant==='Customer');
 for(const c of customer){const v=JSON.parse(c.expected.value).view.payload;assert.equal(v.record_kind,'Entity');assert.equal(v.fields.label.value,'approved');assert.equal(v.fields.credit.record_kind,'Value Object');}
 const reference=createRecordRuleReference(f.graph),money=named('money') as any,entity=named('customer') as any;
 assert.equal(reference.key(entity,{id:'same',label:'a'}),reference.key(entity,{id:'same',label:'b'}));
 assert.notEqual(reference.key(money,{amount:1n,approved:true}),reference.key(money,{amount:2n,approved:true}));
 const other=fixture(t,false,'alternate/path'),moved=createReconciledSemanticControls(other.graph,other.plan).rows.find(r=>r.selector==='alpha:choice') as any;
 assert.deepEqual(moved.cases,row.cases);for(const id of ['money','customer'])assert.deepEqual(moved.dependencies['alpha:'+id].probes,row.dependencies['alpha:'+id].probes);
 const impossible=fixture(t,true),unmet=createReconciledSemanticControls(impossible.graph,impossible.plan);
 assert.equal(unmet.node_count,7);assert.equal(unmet.ready_count,4);assert.match((unmet.rows.find(r=>r.selector==='alpha:choice') as any).reason,/no satisfying base factory witness.*not an unsatisfiability proof/);
});
test('native factories validate record payload witnesses alongside independent factory lifecycle controls',t=>{
 const f=fixture(t),n=nativeContext(f),target=path.join(f.root,'target');
 const report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,publishReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 publishReconciledProject(plan,${JSON.stringify(target)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify({...n.options,target_root:target})})));`);
 assert.equal(report.result,'incomplete',JSON.stringify(report.checks.filter((c:any)=>c.result==='fail')));
 const semantic=report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass',semantic.reason);assert.equal(semantic.evidence.tested_node_count,7);assert.equal(semantic.evidence.remaining.length,0);
 assert.ok(semantic.evidence.tested.some((n:any)=>n.selector==='alpha:choice'));
 assert.equal(report.checks.find((c:any)=>c.id==='semantic-workspace-currentness').result,'pass');
 assert.deepEqual(fs.readdirSync(path.join(f.root,'scratch')),[]);
 for(const a of f.plan.resolved.artifacts)assert.equal(fs.readFileSync(path.join(target,a.relative_path),'utf8'),a.content);
});

test('Rule list-to-set reference keeps the first identity representative',t=>{
 const f=fixture(t,false,'domain',true),reference=createRecordRuleReference(f.graph);
 const entity=(label:string)=>({id:'same',label,credit:{amount:1n,approved:true},tags:['approved'],note:null});
 const a=entity('approved'),b=entity('other'),type=wrap('list',named('customer')) as any;
 assert.equal(reference.evaluate('alpha:first-customer',new Map([['customers',{type,value:[a,b]}]])),true);
 assert.equal(reference.evaluate('alpha:first-customer',new Map([['customers',{type,value:[b,a]}]])),false);
 const n=nativeContext(f),target=path.join(f.root,'generated');
 const actual=n.run(`import cp from 'node:child_process';import {pathToFileURL} from 'node:url';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,publishReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 publishReconciledProject(plan,${JSON.stringify(target)});
 cp.execFileSync('tsc',['--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','NodeNext','--outDir',${JSON.stringify(path.join(f.root,'rule-output'))},${JSON.stringify(path.join(target,'domain/features/alpha/src/domain/rules/first-customer.ts'))}],{encoding:'utf8',timeout:60000});
 const native=await import(pathToFileURL(${JSON.stringify(path.join(f.root,'rule-output/first-customer.js'))}).href);
 const entity=label=>({id:'same',label,credit:{amount:1n,approved:true},tags:['approved'],note:null}),a=entity('approved'),b=entity('other');
 console.log(JSON.stringify([native.ruleFirstCustomer({customers:[a,b]}),native.ruleFirstCustomer({customers:[b,a]})]));`);
 assert.deepEqual(actual,[true,false],'native Rule and source reference preserve first identity representative');
});
test('duplicate recipes cannot cause unbounded Cartesian witness enumeration',t=>{
 const f=fixture(t,true),reference=createRecordRuleReference(f.graph),d=resolveRecordWitness(f.graph,f.plan,'alpha:money',reference);
 let reads=0;
 assert.throws(()=>recordWitnesses(d,reference,type=>{
  const value={tag:'scalar',value:type.kind==='scalar'&&type.name==='Bool'?false:'1'},values=Array.from({length:128},()=>value);
  Object.defineProperty(values,Symbol.iterator,{value:function*(){for(let i=0;i<values.length;i++){if(++reads>6000)throw Error('unbounded duplicate enumeration');yield values[i]!;}}});
  return values;
 }),RecordWitnessUnavailable);
 assert.ok(reads<6000);
});
test('compiling factory mutants and late drift cannot certify record payload witnesses',t=>{
 const f=fixture(t),n=nativeContext(f);
 const reports:any[]=[];
 const modes=['validator-bypass','failure-code','identity','value-equality','freeze','mutation','late'];
 for(let offset=0;offset<modes.length;offset+=2){
  const batch=modes.slice(offset,offset+2);
  const observed=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ${JSON.stringify(batch)}){
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for isolated factory controls'};
   const result=original(command,args,settings),project=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(project).endsWith('/semantic/compiler.json')&&mode!=='late'){
    const folder=path.join(path.dirname(project),'modules/domain/features/alpha/src/domain'),file=path.join(folder,['validator-bypass','failure-code','value-equality'].includes(mode)?'value-objects/money.js':'entities/customer.js'),old=fs.readFileSync(file,'utf8');
    let changed=old;
    if(mode==='validator-bypass')changed=old.replace('validator.validate(fields) === true','true');
    if(mode==='failure-code')changed=old.replace(/'RULE_' \\+ outcome.toUpperCase\\(\\) \\+ ':' \\+ validator.rule/,"'INVALID_FIELDS'");
    if(mode==='identity')changed=old.replace(/(const valueKey = \\(fields\\) => )([^;]+);/,'$1($2) + part(String(fields["label"]));');
    if(mode==='value-equality')changed=old.replace(/(const valueKey = \\(fields\\) => )([^;]+);/,'$1"collapsed";');
    if(mode==='freeze')changed=old.replace('fields = Object.freeze({','fields = ({');
    if(mode==='mutation')changed=old.replace("phases.push('form');","input.label = 'mutated'; phases.push('form');");
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
  assert.deepEqual(observed.map((r:any)=>r.mode),batch,'complete native mutation batch');
  reports.push(...observed);
  t.diagnostic('native mutation batch completed: '+batch.join(', '));
 }
 assert.deepEqual(reports.map(r=>r.mode),modes,'complete ordered mutation coverage');
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
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(JSON.stringify({message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(JSON.stringify({message:String(e.message).slice(0,2000),code:e.code,signal:e.signal,status:e.status,stdout:String(e.stdout??'').slice(-8192),stderr:String(e.stderr??'').slice(-8192)}),{cause:e});}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
