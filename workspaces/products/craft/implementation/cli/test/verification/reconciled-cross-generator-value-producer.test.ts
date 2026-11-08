import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {recordWitnessFixture} from '../helpers/record-witness-project.ts';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorValueProducerControls,checkCrossGeneratorValueProducerObservations,crossGeneratorValueProducerProbe} from '../../src/verification/reconciled-cross-generator-value-producer.ts';
import {createCrossGeneratorValueProducerSurface,assertCrossGeneratorValueProducerSurface,assertCrossGeneratorOwnedValueSurface} from '../../src/verification/reconciled-cross-generator-factory-surface.ts';
import {executeCrossGeneratorValueProducer} from '../../src/verification/reconciled-cross-generator-execution.ts';
import {CROSS_GENERATOR_FACTORY_AUDIT_RUNNER,CROSS_GENERATOR_VALUE_PRODUCER_AUDIT_RUNNER} from '../../src/verification/reconciled-cross-generator-factory-audit.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),cli=path.join(project,'impl/cli'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions=Object.fromEntries(['cross-generator-factory','cross-generator-factory-execution','cross-generator-value-producer','cross-generator-verification'].map(k=>[k,fs.readFileSync(path.join(base,k+'-contract.json'),'utf8')]));
const definition=definitions['cross-generator-value-producer']!;
function control(f:{source:string;selection:any}){
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']!);
 const behavior=createCrossGeneratorValueProducerControls(graph,plan,boundary,definition);
 return {graph,plan,boundary,behavior,surface:createCrossGeneratorValueProducerSurface(graph,plan,boundary,behavior,definition)};
}
function fixture(t:any,record=false,moduleRoot='domain',capacity=false){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-sum-controls-')),source=path.join(root,'source'),nodes:string[]=[];
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const write=(p:string,v:unknown)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:unknown)=>{nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body});};
 const scalar=(name:string)=>({kind:'scalar',name}),named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:unknown)=>({kind,element});
 const variants=(values:[string,any][])=>values.map(([name,payload])=>({name,payload,ontology_variant:'TEST-VARIANT#'+name}));
 const sum=(id:string,values:[string,any][])=>node(id,'Enum',{description:id,values:values.map(v=>v[0]),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-'+id.toUpperCase(),variants:variants(values)}});
 sum('state',[['Open',null],['Closed',null]]);
 sum('status',[['Open',null],['Closed',null]]);
 sum('amount',[['First',scalar('UInt64')],['Other',scalar('UInt64')],['None',null]]);
 sum('detail',[['Text',scalar('String')],['Flag',scalar('Bool')],['Maybe',wrap('optional',scalar('String'))],['List',wrap('list',scalar('UInt64'))],['Set',wrap('set',scalar('UInt64'))],['Inline',{kind:'sum',variants:variants([['Absent',null],['Present',wrap('optional',scalar('Bool'))]])}],['None',null]]);
 sum('choice',[['Amount',named('amount')],['List',wrap('list',named('amount'))],['Set',wrap('set',named('amount'))],['Maybe',wrap('optional',named('amount'))],['State',named('state')],['States',wrap('list',named('state'))],['StateSet',wrap('set',named('state'))],['Status',named('status')],['Inline',{kind:'sum',variants:variants([['None',null],['Many',wrap('list',named('state'))]])}],['None',null]]);
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
function native(t:any,moduleRoot='domain',records=false,prepare:(f:any)=>void=()=>{}){
 const f=records?recordWitnessFixture(t,false,moduleRoot):fixture(t,false,moduleRoot);prepare(f);
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const dist=path.join(f.root,'dist');fs.mkdirSync(dist);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"module"}');
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+project+',target='+project+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:240000,maxBuffer:33554432});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 command(['tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',path.join(cli,'src'),'--outDir',dist,path.join(cli,'src/verification/reconciled-cross-generator-execution.ts')]);
 const prefix=`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {createCrossGeneratorBoundary} from './dist/verification/reconciled-cross-generator-boundary.js';
import {createCrossGeneratorValueProducerControls,checkCrossGeneratorValueProducerObservations} from './dist/verification/reconciled-cross-generator-value-producer.js';
import {createCrossGeneratorFactoryControls} from './dist/verification/reconciled-cross-generator-factory.js';
import {createCrossGeneratorValueProducerSurface} from './dist/verification/reconciled-cross-generator-factory-surface.js';
import {executeCrossGeneratorValueProducer,assertCrossGeneratorExecutionCurrent} from './dist/verification/reconciled-cross-generator-execution.js';
const source=__SOURCE__,selection=__SELECTION__,definitions=__DEFINITIONS__,definition=definitions['cross-generator-value-producer'];
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']);
const behavior=createCrossGeneratorValueProducerControls(graph,plan,boundary,definitions['cross-generator-value-producer']),surface=createCrossGeneratorValueProducerSurface(graph,plan,boundary,behavior,definition);
const options={workspace_parent:__ROOT__,typescript_root:'/opt/node-toolchain/node_modules/typescript'};
`;
 return {...f,run:(body:string)=>{const client=path.join(f.root,'client.mjs');fs.writeFileSync(client,prefix.replace('__SOURCE__',JSON.stringify(f.source)).replace('__SELECTION__',JSON.stringify(f.selection)).replace('__DEFINITIONS__',JSON.stringify(definitions)).replace('__ROOT__',JSON.stringify(f.root))+body);return JSON.parse(command(['node',client]));}};
}

test('source producer controls preserve actual Enum roots, import occurrences and all ownership modes',t=>{
 const f=fixture(t),c=control(f);
 assert.deepEqual(c.behavior.rows.map(r=>r.selector),c.graph.nodes.map(n=>n.selector));
 assert.ok(c.graph.nodes.every(n=>n.kind==='Enum'));assert.deepEqual(f.selection.factories,[]);
 assert.equal(c.behavior.rows.filter(r=>r.state==='ready').length,3);
 assert.equal(c.behavior.rows.filter(r=>r.state==='inapplicable').length,2);
 const choice=c.behavior.rows.find(r=>r.selector==='alpha:choice')!;
 assert.equal(choice.state,'ready');if(choice.state!=='ready'||choice.adapter!=='sum')throw Error('unavailable');
 assert.equal(choice.protocol.length,9);assert.equal(choice.ownership_coverage.length,9);
 for(const coverage of choice.ownership_coverage)assert.deepEqual(coverage.modes,['clone-named','foreign-named','owned','raw-named']);
 assert.deepEqual([...new Set(choice.cases.map(c=>c.recipe.variant))].sort(),choice.shape.kind==='sum'?choice.shape.variants.map(v=>v.name).sort():[]);
 assert.ok(choice.cases.some(c=>JSON.stringify(c.expected).includes('"input_paths":[["payload",0],["payload",1]]')),'same Enum singleton has both actual input locations');
 const probe=crossGeneratorValueProducerProbe(c.behavior);assert.ok(!JSON.stringify(probe).includes('"expected"'));
 const observed={controls_sha256:c.behavior.controls_sha256,rows:c.behavior.rows.flatMap(r=>r.state!=='ready'?[]:[{selector:r.selector,cases:r.cases.map(c=>c.expected)}])};
 const result=checkCrossGeneratorValueProducerObservations(c.behavior,observed);assert.equal(result.tested_producer_count,3);assert.deepEqual(result.remaining,[]);
 for(const mutate of [(v:any)=>v.rows.pop(),(v:any)=>v.rows.push(v.rows[0]),(v:any)=>v.rows[0].cases.pop(),(v:any)=>v.rows[0].cases[0].calls.push(v.rows[0].cases[0].calls[0]),(v:any)=>v.rows[0].cases[0].getter_reads=1]){
  const bad=structuredClone(observed);mutate(bad);assert.throws(()=>checkCrossGeneratorValueProducerObservations(c.behavior,bad),/observation mismatch/);
 }
 assert.throws(()=>crossGeneratorValueProducerProbe(structuredClone(c.behavior)),/registered/);
 assert.throws(()=>createCrossGeneratorValueProducerControls(c.graph,c.plan,c.boundary,definition+' '),/definition drift/);
 assert.throws(()=>createCrossGeneratorValueProducerSurface(c.graph,c.plan,c.boundary,structuredClone(c.behavior),definition),/registered/);
 assert.throws(()=>assertCrossGeneratorValueProducerSurface(structuredClone(c.surface)),/registered/);
 assert.throws(()=>assertCrossGeneratorOwnedValueSurface(c.surface),/registered/);
 const other=control(fixture(t,false,'application/domain'));assert.throws(()=>createCrossGeneratorValueProducerSurface(other.graph,other.plan,other.boundary,c.behavior,definition),/foreign/);
 const before=fs.readdirSync(f.root);let reads=0;const active:any={workspace_parent:f.root};Object.defineProperty(active,'typescript_root',{enumerable:true,get(){reads++;return '/tmp';}});
 assert.throws(()=>executeCrossGeneratorValueProducer(c.plan,c.surface,definition,active),/closed data tool options/);assert.equal(reads,0);assert.deepEqual(fs.readdirSync(f.root),before);
 assert.equal(CROSS_GENERATOR_VALUE_PRODUCER_AUDIT_RUNNER.replace(c.surface.definition_sha256,'caaa51768bc0c922a987396f6c36de5f66eb056401d8e81c1399bd3b6811eeb2'),CROSS_GENERATOR_FACTORY_AUDIT_RUNNER);
 const wide=control(fixture(t,false,'domain',true));assert.equal(wide.behavior.rows.length,wide.graph.nodes.length);assert.ok(wide.behavior.rows.some(r=>r.state==='not_evaluable'&&/bounded sum|capacity/.test(r.reason)));
 t.diagnostic(JSON.stringify({cases:result.tested_case_count,producers:result.tested_producer_count,rows:c.behavior.rows.length,protocol:choice.protocol.length,hash:c.behavior.controls_sha256}));
});
test('original sum and Enum producer protocols execute with audited retained custody in both layouts',t=>{
 for(const moduleRoot of ['domain','application/domain']){
  const f=native(t,moduleRoot),result=f.run(String.raw`
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.claim_scope,'finite-private-instrumented-value-producer-not-whole-project');assert.equal(r.outcome.tested_producer_count,3);assert.deepEqual(r.outcome.remaining,[]);
assert.equal(r.surface_sha256,surface.surface_sha256);assert.equal(r.controls_sha256,behavior.controls_sha256);assert.equal(Object.keys(r.audits).length,2);
assert.ok(!JSON.stringify(JSON.parse(fs.readFileSync(path.join(r.workspace,'cases.json')))).includes('"expected"'));
assert.throws(()=>assertCrossGeneratorExecutionCurrent(structuredClone(r)),/registered/);
for(const name of ['source-audit-observation.json','native-audit-observation.json','observations.json','cases.json','runner.mjs']){
 const file=path.join(r.workspace,name),old=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(file,old);assertCrossGeneratorExecutionCurrent(r);
}
const file=path.join(r.workspace,'runner.mjs'),old=fs.readFileSync(file);fs.unlinkSync(file);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
fs.symlinkSync(path.join(r.workspace,'cases.json'),file);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/symbolic/);fs.unlinkSync(file);fs.writeFileSync(file,old);assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({layout:selection.module_root,...r.outcome,modules:r.native_modules.length,hash:r.controls_sha256}));
`);
  assert.equal(result.tested_producer_count,3);t.diagnostic(JSON.stringify(result));
 }
});
test('named sum roots compose actual Entity and Value Object factories without fabricated consumers',t=>{
 const f=native(t,'domain',true),result=f.run(String.raw`
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_producer_count,1);assert.deepEqual(r.outcome.remaining,[]);
const roles=[...new Set(surface.rows.flatMap(r=>r.state==='ready'?r.modules.map(m=>m.role):[]))].sort();assert.deepEqual(roles,['factory','rule','sum']);
console.log(JSON.stringify({...r.outcome,modules:r.native_modules.length,roles}));
`);
 assert.equal(result.tested_producer_count,1);t.diagnostic(JSON.stringify(result));
});

test('producer source and native audits reject import export and ambient escapes',t=>{
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options),root=r.workspace;let rejected=0;
const relative=selection.module_root+'/features/alpha/src/domain/enums/choice.sum';
for(const stage of ['source','native']){
 const file=path.join(root,stage,relative+(stage==='source'?'.ts':'.js')),original=fs.readFileSync(file,'utf8');
 const audit=()=>JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,stage+'-audit-config.json'),path.join(root,stage+'-audit-input.json')],{encoding:'utf8',timeout:60000}));
 const mutations=stage==='source'?[
  s=>'import {readFileSync} from "node:fs";\n'+s,
  s=>s.replace('import type {AmountCase','import {AmountCase'),
  s=>s+'\nexport const extra=1;',
  s=>s+'\nconst dynamic=()=>import("node:fs");',
  s=>s+'\nconst ambient=()=>process.cwd();'
 ]:[
  s=>'const foreign=require("node:fs");\n'+s,
  s=>s+'\nexports.extra=Object.freeze({});',
  s=>s+'\nconst alias=require;alias("node:fs");',
  s=>s+'\nfunction nested(){return require("node:fs");}',
  s=>s+'\nexports.ChoiceValueComponent=Object.freeze({});',
  s=>s+'\nmodule.exports={};',
  s=>s+'\nexports.ChoiceInput=1;'
 ];
 for(const mutate of mutations){const changed=mutate(original);assert.notEqual(changed,original);fs.writeFileSync(file,changed);assert.ok(audit().modules.some(m=>m.violations.length>0));assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);rejected++;}
 fs.writeFileSync(file,original);assertCrossGeneratorExecutionCurrent(r);
}
console.log(JSON.stringify({surface_mutants:rejected}));
`);assert.equal(result.surface_mutants,12);t.diagnostic(JSON.stringify(result));
});


test('strict-compiling duplicate producer calls and member reads cannot hide behind unchanged outcomes',t=>{
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options),root=r.workspace,folder=path.join(root,'source',selection.module_root+'/features/alpha/src/domain/enums');
const compile=()=>cp.execFileSync(process.execPath,[path.join(options.typescript_root,'bin/tsc'),'--project',path.join(root,'compiler.json'),'--pretty','false'],{encoding:'utf8',timeout:60000});
const observe=()=>JSON.parse(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw',path.join(root,'runner.mjs'),path.join(root,'cases.json'),path.join(root,'native')],{encoding:'utf8',timeout:60000,maxBuffer:16777216}));
const baseline=observe(),outcomes=v=>v.rows.map(r=>({selector:r.selector,cases:r.cases.map(({calls,reads,...rest})=>rest)}));let mutations=0;
for(const [name,mutate]of [
 ['choice.sum.ts',s=>s.replaceAll('if(!provider.isOwned(input))','if(!(provider.isOwned(input),provider.isOwned(input)))')],
 ['choice.sum.ts',s=>s.replaceAll("part(provider.key(value))","part((provider.key(value),provider.key(value)))")],
 ['state.ts',s=>s+'\nconst duplicate = defineEnum({"Closed":"Closed","Open":"Open"} as const);\n'],
 ['state.component.ts',s=>s.replace('variant:EnumDefinition["Closed"]','variant:(EnumDefinition["Closed"],EnumDefinition["Closed"])')]
]){
 const file=path.join(folder,name),original=fs.readFileSync(file,'utf8'),changed=mutate(original);assert.notEqual(changed,original);
 fs.writeFileSync(file,changed);compile();
 const audit=JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,'native-audit-config.json'),path.join(root,'native-audit-input.json')],{encoding:'utf8',timeout:60000}));
 assert.ok(audit.modules.every(m=>m.violations.length===0),JSON.stringify(audit.modules.filter(m=>m.violations.length)));
 const mutated=observe();assert.deepEqual(outcomes(mutated),outcomes(baseline));assert.throws(()=>checkCrossGeneratorValueProducerObservations(behavior,mutated),/native observation mismatch/);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
 fs.writeFileSync(file,original);compile();checkCrossGeneratorValueProducerObservations(behavior,observe());assertCrossGeneratorExecutionCurrent(r);mutations++;
}
console.log(JSON.stringify({strict_compiling_mutants:mutations,unchanged_outcomes:true}));
`);assert.equal(result.strict_compiling_mutants,4);t.diagnostic(JSON.stringify(result));
});

test('producer execution retains captured source, rejects missing observations and in-flight drift, and cannot pass empty families',t=>{
 const f=native(t,'domain',true),r=f.run(String.raw`
const sourceFile=path.join(source,'specs/alpha/nodes/customer.json'),sourceBytes=fs.readFileSync(sourceFile);fs.unlinkSync(sourceFile);
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);fs.writeFileSync(sourceFile,sourceBytes);
for(const trigger of ['source-audit-input.json','native-audit-input.json','observations.json']){
 const original=fs.writeFileSync;let changed=false;
 fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/'+trigger)){original.call(fs,path.join(path.dirname(String(file)),'unexpected'),'x');changed=true;}return out;};
 try{assert.throws(()=>executeCrossGeneratorValueProducer(plan,surface,definition,options),/artifact changed or unexpected/);assert.ok(changed);}finally{fs.writeFileSync=original;}
}
const originalSpawn=cp.spawnSync;let changed=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args.includes('--permission')){const value=JSON.parse(out.stdout);value.rows.pop();out.stdout=JSON.stringify(value);changed=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorValueProducer(plan,surface,definition,options),/native observation mismatch/);assert.ok(changed);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();}
const budgetFile=path.join(source,'specs/alpha/nodes/budget.json'),budget=JSON.parse(fs.readFileSync(budgetFile));budget.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:false}};fs.writeFileSync(budgetFile,JSON.stringify(budget));
const g=loadCompiledProjectGraph(source),p=planCompiledReconciledProject(g,selection),b=createCrossGeneratorBoundary(g,p,definitions['cross-generator-verification']),c=createCrossGeneratorValueProducerControls(g,p,b,definitions['cross-generator-value-producer']),s=createCrossGeneratorValueProducerSurface(g,p,b,c,definition);
assert.ok(s.rows.every(r=>r.state!=='ready'));assert.equal(s.rows.find(r=>r.selector==='alpha:choice').state,'not_evaluable');const before=fs.readdirSync(options.workspace_parent);assert.throws(()=>executeCrossGeneratorValueProducer(p,s,definition,options),/no ready interoperability/);assert.deepEqual(fs.readdirSync(options.workspace_parent),before);
assertCrossGeneratorExecutionCurrent(r);console.log(JSON.stringify({captured_source:true,in_flight_rejections:3,missing_observation_rejected:true,empty_pass_rejected:true}));
`);assert.equal(r.empty_pass_rejected,true);t.diagnostic(JSON.stringify(r));
});
test('producer execution complete compiler package custody detects library, platform executable and extra tool-file drift', t => {
  const f = native(t), result = f.run(String.raw`
const packageRoot=path.join(options.workspace_parent,'tool-copy','node_modules');fs.mkdirSync(packageRoot,{recursive:true});
fs.cpSync(options.typescript_root,path.join(packageRoot,'typescript'),{recursive:true});
fs.cpSync('/opt/node-toolchain/node_modules/@typescript',path.join(packageRoot,'@typescript'),{recursive:true});
options.typescript_root=path.join(packageRoot,'typescript');
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
let mutations=0;
for(const p of [path.join(options.typescript_root,'lib/getExePath.js'),path.join(options.typescript_root,'dist/api/sync/api.js'),path.join(packageRoot,'@typescript/typescript-linux-x64/lib/tsc')]){
 const original=fs.readFileSync(p);fs.appendFileSync(p,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.writeFileSync(p,original);assertCrossGeneratorExecutionCurrent(r);mutations++;
}
const extra=path.join(options.typescript_root,'extra');fs.writeFileSync(extra,'x');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.unlinkSync(extra);assertCrossGeneratorExecutionCurrent(r);
const originalSpawn=cp.spawnSync,tool=path.join(options.typescript_root,'lib/getExePath.js'),before=fs.readFileSync(tool);let injected=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args[0]===path.join(options.typescript_root,'bin/tsc')){fs.appendFileSync(tool,'\n');injected=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorValueProducer(plan,surface,definition,options),/toolchain changed/);assert.ok(injected);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();fs.writeFileSync(tool,before);}
assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({tool_mutations:mutations+1,in_flight_tool_rejections:1,compiler_files:Object.keys(r.tool_files.typescript).length,platform_files:Object.keys(r.tool_files.platform).length}));
`);
  assert.equal(result.tool_mutations, 4); t.diagnostic(JSON.stringify(result));
});
function mixed(f:ReturnType<typeof recordWitnessFixture>){
 const featureFile=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(featureFile,'utf8'));
 const add=(id:string,kind:string,body:any)=>{feature.nodes.push(id);fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/'+id+'.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body}));};
 const named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any)=>({kind,element});
 add('status','Enum',{description:'Status',values:['Open','Closed'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:['Open','Closed'].map(name=>({name,payload:null,ontology_variant:'TEST-STATUS#'+name}))}});
 const variants=[{name:'None',payload:null,ontology_variant:'TEST-AMOUNT-CHOICE#None'},{name:'Amount',payload:named('money'),ontology_variant:'TEST-AMOUNT-CHOICE#Amount'}];
 add('amount-choice','Enum',{description:'Amount choice',values:variants.map(v=>v.name),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-AMOUNT-CHOICE',variants}});
 const fields:any[]=[['credit',named('money')],['credit_again',named('money')],['inline',{kind:'sum',variants}],['list',wrap('list',named('money'))],['named',named('amount-choice')],['optional',wrap('optional',named('money'))],['person',named('customer')],['set',wrap('set',named('money'))],['status',named('status')],['status_again',named('status')],['status_list',wrap('list',named('status'))]];
 add('money-box','Value Object',{description:'Owned values across collection and sum boundaries',invariant_refs:['alpha:nonempty'],fields:fields.map(([name])=>name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-MONEY-BOX',properties:fields.map(([name,type])=>({name,type,ontology_property:'TEST-MONEY-BOX#'+name,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name}))}});
 f.selection.factories.push({selector:'alpha:money-box',base_validators:[{rule:'alpha:nonempty',arguments:[{parameter:'value',path:['person','id']}]}],extensions:[]} as any);
 const variants2=[['Box',named('money-box')],['Amount',named('amount-choice')],['Status',named('status')],['Inline',{kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'TEST-INLINE#None'},{name:'Statuses',payload:wrap('list',named('status')),ontology_variant:'TEST-INLINE#Statuses'}]}],['None',null]].map(([name,payload])=>({name,payload,ontology_variant:'TEST-ALL#'+name}));
 add('all-values','Enum',{description:'Recursive producer boundaries',values:variants2.map(v=>v.name),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-ALL',variants:variants2}});
 fs.writeFileSync(featureFile,JSON.stringify(feature));
}

test('one compound sum project composes records, plain Enums and named sums across wrapper boundaries',t=>{
 const f=native(t,'application/domain',true,mixed),result=f.run(String.raw`
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_producer_count,4);assert.deepEqual(r.outcome.remaining,[]);
const roles=[...new Set(surface.rows.flatMap(r=>r.state==='ready'?r.modules.map(m=>m.role):[]))].sort();
assert.deepEqual(roles,['enum-component','enum-definition','enum-runtime','factory','rule','sum']);
console.log(JSON.stringify({...r.outcome,modules:r.native_modules.length,roles}));
`);assert.equal(result.tested_producer_count,4);t.diagnostic(JSON.stringify(result));
});
test('redirecting a plain Enum to another same-valued definition fails both surface and interaction evidence',t=>{
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorValueProducer(plan,surface,definition,options),root=r.workspace,file=path.join(root,'source',selection.module_root+'/features/alpha/src/domain/enums/state.component.ts'),old=fs.readFileSync(file,'utf8');
const changed=old.replace('import {State as EnumDefinition} from "./state.js";','import {Status as EnumDefinition} from "./status.js";');assert.notEqual(changed,old);fs.writeFileSync(file,changed);
cp.execFileSync(process.execPath,[path.join(options.typescript_root,'bin/tsc'),'--project',path.join(root,'compiler.json'),'--pretty','false'],{encoding:'utf8',timeout:60000});
for(const stage of ['source','native']){
 const audit=JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,stage+'-audit-config.json'),path.join(root,stage+'-audit-input.json')],{encoding:'utf8',timeout:60000}));
 assert.ok(audit.modules.some(m=>m.violations.length>0));
}
const observed=JSON.parse(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw',path.join(root,'runner.mjs'),path.join(root,'cases.json'),path.join(root,'native')],{encoding:'utf8',timeout:60000,maxBuffer:16777216}));
const original=JSON.parse(fs.readFileSync(path.join(root,'observations.json'))),outcomes=v=>v.rows.map(r=>r.cases.map(({calls,reads,...rest})=>rest));
assert.deepEqual(outcomes(observed),outcomes(original));assert.throws(()=>checkCrossGeneratorValueProducerObservations(behavior,observed),/native observation mismatch/);
assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
console.log(JSON.stringify({same_wire_redirect_rejected:true,unchanged_outcomes:true}));
`);assert.equal(result.same_wire_redirect_rejected,true);t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
