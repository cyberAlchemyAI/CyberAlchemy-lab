import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {recordWitnessFixture} from '../helpers/record-witness-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorFactoryControls} from '../../src/verification/reconciled-cross-generator-factory.ts';
import {createCrossGeneratorOwnedValueControls} from '../../src/verification/reconciled-cross-generator-owned-values.ts';
import {createCrossGeneratorFactorySurface,createCrossGeneratorOwnedValueSurface,assertCrossGeneratorFactorySurface,assertCrossGeneratorOwnedValueSurface} from '../../src/verification/reconciled-cross-generator-factory-surface.ts';
import {executeCrossGeneratorOwnedValues} from '../../src/verification/reconciled-cross-generator-execution.ts';
import {CROSS_GENERATOR_FACTORY_AUDIT_RUNNER,CROSS_GENERATOR_OWNED_VALUES_AUDIT_RUNNER} from '../../src/verification/reconciled-cross-generator-factory-audit.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),cli=path.join(project,'impl/cli'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions=Object.fromEntries(['cross-generator-factory','cross-generator-factory-execution','cross-generator-owned-values','cross-generator-owned-values-execution','cross-generator-verification'].map(k=>[k,fs.readFileSync(path.join(base,k+'-contract.json'),'utf8')]));
const definition=definitions['cross-generator-owned-values-execution']!;
type Fixture=ReturnType<typeof recordWitnessFixture>;
function control(f:Fixture){
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']!);
 const behavior=createCrossGeneratorOwnedValueControls(graph,plan,boundary,definitions['cross-generator-owned-values']!);
 return {graph,plan,boundary,behavior,surface:createCrossGeneratorOwnedValueSurface(graph,plan,boundary,behavior,definition)};
}

function mixed(f:Fixture){
 const featureFile=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(featureFile,'utf8'));
 const add=(id:string,kind:string,body:any)=>{feature.nodes.push(id);fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/'+id+'.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body}));};
 const named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any)=>({kind,element});
 add('status','Enum',{description:'Status',values:['Open','Closed'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:['Open','Closed'].map(name=>({name,payload:null,ontology_variant:'TEST-STATUS#'+name}))}});
 const variants=[{name:'None',payload:null,ontology_variant:'TEST-AMOUNT-CHOICE#None'},{name:'Amount',payload:named('money'),ontology_variant:'TEST-AMOUNT-CHOICE#Amount'}];
 add('amount-choice','Enum',{description:'Amount choice',values:variants.map(v=>v.name),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-AMOUNT-CHOICE',variants}});
 const fields:any[]=[['credit',named('money')],['credit_again',named('money')],['inline',{kind:'sum',variants}],['list',wrap('list',named('money'))],['named',named('amount-choice')],['optional',wrap('optional',named('money'))],['person',named('customer')],['set',wrap('set',named('money'))],['status',named('status')],['status_again',named('status')],['status_list',wrap('list',named('status'))]];
 add('money-box','Value Object',{description:'Owned values across collection and sum boundaries',invariant_refs:['alpha:nonempty'],fields:fields.map(([name])=>name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-MONEY-BOX',properties:fields.map(([name,type])=>({name,type,ontology_property:'TEST-MONEY-BOX#'+name,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name}))}});
 f.selection.factories.push({selector:'alpha:money-box',base_validators:[{rule:'alpha:nonempty',arguments:[{parameter:'value',path:['person','id']}]}],extensions:[]} as any);
 fs.writeFileSync(featureFile,JSON.stringify(feature));
}
function native(t:any,moduleRoot='domain',prepare:(f:Fixture)=>void=()=>{}){
 const f=recordWitnessFixture(t,false,moduleRoot);prepare(f);
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const dist=path.join(f.root,'dist');fs.mkdirSync(dist);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"module"}');
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+project+',target='+project+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:240000,maxBuffer:33554432});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 command(['tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',path.join(cli,'src'),'--outDir',dist,path.join(cli,'src/verification/reconciled-cross-generator-execution.ts')]);
 const prefix=`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
import {loadCompiledProjectGraph} from './dist/input/project-model.js';import {planCompiledReconciledProject} from './dist/generation/reconciled-project.js';
import {createCrossGeneratorBoundary} from './dist/verification/reconciled-cross-generator-boundary.js';
import {createCrossGeneratorOwnedValueControls,checkCrossGeneratorOwnedValueObservations} from './dist/verification/reconciled-cross-generator-owned-values.js';
import {createCrossGeneratorFactoryControls} from './dist/verification/reconciled-cross-generator-factory.js';
import {createCrossGeneratorOwnedValueSurface} from './dist/verification/reconciled-cross-generator-factory-surface.js';
import {executeCrossGeneratorOwnedValues,assertCrossGeneratorExecutionCurrent} from './dist/verification/reconciled-cross-generator-execution.js';
const source=__SOURCE__,selection=__SELECTION__,definitions=__DEFINITIONS__,definition=definitions['cross-generator-owned-values-execution'];
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']);
const behavior=createCrossGeneratorOwnedValueControls(graph,plan,boundary,definitions['cross-generator-owned-values']),surface=createCrossGeneratorOwnedValueSurface(graph,plan,boundary,behavior,definition);
const options={workspace_parent:__ROOT__,typescript_root:'/opt/node-toolchain/node_modules/typescript'};
`;
 return {...f,run:(body:string)=>{const client=path.join(f.root,'client.mjs');fs.writeFileSync(client,prefix.replace('__SOURCE__',JSON.stringify(f.source)).replace('__SELECTION__',JSON.stringify(f.selection)).replace('__DEFINITIONS__',JSON.stringify(definitions)).replace('__ROOT__',JSON.stringify(f.root))+body);return JSON.parse(command(['node',client]));}};
}


test('owned surfaces use independent registrations, preserve repeated imports and reject foreign identities',t=>{
 const f=recordWitnessFixture(t);mixed(f);const c=control(f);
 const row=c.surface.rows.find(r=>r.selector==='alpha:money-box')!;
 assert.equal(row.state,'ready');if(row.state!=='ready')throw Error('unavailable');
 assert.ok(Object.isFrozen(row.modules));assert.equal(row.protocol.length,11);
 assert.equal(row.modules.find(m=>m.relative_path===row.relative_path)!.imports.filter(i=>i.names.includes('StatusValueComponent')).length,3);
 const rules=createCrossGeneratorFactoryControls(c.graph,c.plan,c.boundary,definitions['cross-generator-factory']!);
 assert.equal(rules.rows.find(r=>r.selector==='alpha:money-box')!.state,'not_evaluable','owned readiness does not invent a Rule-rejected witness');
 const ruleSurface=createCrossGeneratorFactorySurface(c.graph,c.plan,c.boundary,rules,definitions['cross-generator-factory-execution']!);
 assert.throws(()=>assertCrossGeneratorFactorySurface(c.surface),/registered/);
 assert.throws(()=>assertCrossGeneratorOwnedValueSurface(ruleSurface),/registered/);
 assert.throws(()=>createCrossGeneratorOwnedValueSurface(c.graph,c.plan,c.boundary,structuredClone(c.behavior),definition),/registered/);
 assert.throws(()=>createCrossGeneratorOwnedValueSurface(c.graph,c.plan,c.boundary,c.behavior,definition+' '),/definition drift/);
 const other=control(recordWitnessFixture(t,false,'application/domain'));
 assert.throws(()=>createCrossGeneratorOwnedValueSurface(other.graph,other.plan,other.boundary,c.behavior,definition),/foreign/);
 const before=fs.readdirSync(f.root);
 assert.throws(()=>executeCrossGeneratorOwnedValues(c.plan,structuredClone(c.surface),definition,{workspace_parent:f.root,typescript_root:'/tmp'}),/registered/);
 let reads=0;const active:any={workspace_parent:f.root};Object.defineProperty(active,'typescript_root',{enumerable:true,get(){reads++;return '/tmp';}});
 assert.throws(()=>executeCrossGeneratorOwnedValues(c.plan,c.surface,definition,active),/closed data tool options/);assert.equal(reads,0);
 assert.deepEqual(fs.readdirSync(f.root),before);
 assert.equal(CROSS_GENERATOR_OWNED_VALUES_AUDIT_RUNNER.replace(c.surface.definition_sha256,ruleSurface.definition_sha256),CROSS_GENERATOR_FACTORY_AUDIT_RUNNER,'only the pinned execution definition differs');
});

test('retained owned execution audits original modules in both layouts and binds current evidence',t=>{
 for(const moduleRoot of ['domain','application/domain']){
  const f=native(t,moduleRoot),result=f.run(String.raw`
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.surface_sha256,surface.surface_sha256);assert.equal(r.controls_sha256,behavior.controls_sha256);
assert.equal(r.claim_scope,'finite-private-instrumented-factory-owned-values-not-whole-project');
assert.equal(r.outcome.tested_factory_count,1);assert.equal(r.outcome.tested_case_count,192);assert.deepEqual(r.outcome.remaining,[]);
assert.equal(r.outcome.public_cross_generator_behavior,'not_evaluable');assert.equal(Object.keys(r.audits).length,2);
const input=JSON.parse(fs.readFileSync(path.join(r.workspace,'cases.json')));assert.ok(!JSON.stringify(input).includes('"expected"'));
assert.throws(()=>assertCrossGeneratorExecutionCurrent(structuredClone(r)),/registered/);
for(const name of ['source-audit-observation.json','native-audit-observation.json','observations.json','cases.json','runner.mjs']){
 const file=path.join(r.workspace,name),before=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(file,before);assertCrossGeneratorExecutionCurrent(r);
}
const runner=path.join(r.workspace,'runner.mjs'),saved=fs.readFileSync(runner);fs.unlinkSync(runner);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
fs.symlinkSync(path.join(r.workspace,'cases.json'),runner);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/symbolic/);fs.unlinkSync(runner);fs.writeFileSync(runner,saved);assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({module_root:selection.module_root,...r.outcome,modules:r.native_modules.length,audits:2,retained_mutations:7}));
`);assert.equal(result.tested_factory_count,1);t.diagnostic(JSON.stringify(result));
 }
});

test('recursive owned fields retain independent native surfaces without Rule-readiness coupling',t=>{
 const f=native(t,'domain',mixed),result=f.run(String.raw`
const rules=createCrossGeneratorFactoryControls(graph,plan,boundary,definitions['cross-generator-factory']);
assert.equal(rules.rows.find(r=>r.selector==='alpha:money-box').state,'not_evaluable');
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_factory_count,2);assert.equal(r.outcome.tested_case_count,1286);assert.deepEqual(r.outcome.remaining,[]);
const roles=[...new Set(surface.rows.filter(r=>r.state==='ready').flatMap(r=>r.modules.map(m=>m.role)))].sort();
assert.deepEqual(roles,['enum-component','enum-definition','enum-runtime','factory','rule','sum']);
const row=surface.rows.find(r=>r.selector==='alpha:money-box');assert.equal(row.protocol.length,11);assert.ok(row.ownership_coverage.every(c=>c.modes.length===4));
console.log(JSON.stringify({...r.outcome,roles,modules:r.native_modules.length,owned_occurrences:row.protocol.length}));
`);assert.equal(result.owned_occurrences,11);t.diagnostic(JSON.stringify(result));
});

test('owned source and native audits reject import export and ambient escapes',t=>{
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options),root=r.workspace;let rejected=0;
const relative=selection.module_root+'/features/alpha/src/domain/entities/customer';
for(const stage of ['source','native']){
 const file=path.join(root,stage,relative+(stage==='source'?'.ts':'.js')),original=fs.readFileSync(file,'utf8');
 const audit=()=>JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,stage+'-audit-config.json'),path.join(root,stage+'-audit-input.json')],{encoding:'utf8',timeout:60000}));
 const mutations=stage==='source'?[
  s=>'import {readFileSync} from "node:fs";\n'+s,
  s=>s.replace('import type {MoneySnapshot','import {MoneySnapshot'),
  s=>s+'\nexport const extra=1;',
  s=>s+'\nconst dynamic=()=>import("node:fs");',
  s=>s+'\nconst ambient=()=>process.cwd();'
 ]:[
  s=>'const foreign=require("node:fs");\n'+s,
  s=>s+'\nexports.extra=Object.freeze({});',
  s=>s+'\nconst alias=require;alias("node:fs");',
  s=>s+'\nfunction nested(){return require("node:fs");}',
  s=>s+'\nexports.CustomerValueComponent=Object.freeze({});',
  s=>s+'\nmodule.exports={};',
  s=>s+'\nexports.CustomerFields=1;'
 ];
 for(const mutate of mutations){const changed=mutate(original);assert.notEqual(changed,original);fs.writeFileSync(file,changed);assert.ok(audit().modules.some(m=>m.violations.length>0));assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);rejected++;}
 fs.writeFileSync(file,original);assertCrossGeneratorExecutionCurrent(r);
}
console.log(JSON.stringify({surface_mutants:rejected}));
`);assert.equal(result.surface_mutants,12);t.diagnostic(JSON.stringify(result));
});

test('strict-compiling owned provider-call mutations fail behavior even when factory outcomes are unchanged',t=>{
 const f=native(t),result=f.run(String.raw`
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options),root=r.workspace;
const file=path.join(root,'source',selection.module_root+'/features/alpha/src/domain/entities/customer.ts'),original=fs.readFileSync(file,'utf8');
const compile=()=>cp.execFileSync(process.execPath,[path.join(options.typescript_root,'bin/tsc'),'--project',path.join(root,'compiler.json'),'--pretty','false'],{encoding:'utf8',timeout:60000});
const observe=()=>JSON.parse(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw',path.join(root,'runner.mjs'),path.join(root,'cases.json'),path.join(root,'native')],{encoding:'utf8',timeout:60000,maxBuffer:16777216}));
const baseline=observe();
const changed=original.replace('if(!provider.isOwned(input))','if(!(provider.isOwned(input),provider.isOwned(input)))');assert.notEqual(changed,original);fs.writeFileSync(file,changed);compile();
const audit=JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,'native-audit-config.json'),path.join(root,'native-audit-input.json')],{encoding:'utf8',timeout:60000}));assert.ok(audit.modules.every(m=>m.violations.length===0));
const mutated=observe();assert.deepEqual(mutated.rows.map(r=>r.cases.map(({calls,...rest})=>rest)),baseline.rows.map(r=>r.cases.map(({calls,...rest})=>rest)));
assert.throws(()=>checkCrossGeneratorOwnedValueObservations(behavior,mutated),/native observation mismatch/);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
fs.writeFileSync(file,original);compile();checkCrossGeneratorOwnedValueObservations(behavior,observe());assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({strict_compiling_mutants:1,unchanged_factory_outcomes:true}));
`);assert.equal(result.strict_compiling_mutants,1);t.diagnostic(JSON.stringify(result));
});

function references(f:Fixture){
 const featureFile=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(featureFile,'utf8'));feature.nodes.push('account','account-valid');fs.writeFileSync(featureFile,JSON.stringify(feature));
 fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/account.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'account',kind:'Entity',body:{description:'Account',fields:['id'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-ACCOUNT',properties:[{name:'id',type:{kind:'scalar',name:'String'},ontology_property:'TEST-ACCOUNT#id',identity:true,cardinality:'one',meaning:'identity'}]}}}));
 fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/account-valid.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'account-valid',kind:'Rule',body:{description:'Account admissibility',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-ACCOUNT-VALID',parameters:[{name:'value',type:{kind:'scalar',name:'String'}}],expression:{op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:true}}}}}));
 (f.selection.factories as any[]).push({selector:'alpha:account',base_validators:[{rule:'alpha:account-valid',arguments:[{parameter:'value',field:'id'}]}],extensions:[]});
 const file=path.join(f.source,'specs/alpha/nodes/customer.json'),customer=JSON.parse(fs.readFileSync(file,'utf8'));
 customer.body.fields.push('account_id');customer.body.typed_contract.properties.push({name:'account_id',type:{kind:'scalar',name:'String'},ontology_property:'TEST-CUSTOMER#account_id',identity:false,cardinality:'one',meaning:'account identity'});
 fs.writeFileSync(file,JSON.stringify(customer));
 (f.selection.field_bindings as any[]).push({owner:'alpha:customer',field:'account_id',kind:'identity-reference',target:'alpha:account',projection:['id']});
}
test('type-only field references join the checked closure without a runtime Account import',t=>{
 const f=native(t,'domain',references),r=f.run(String.raw`
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
const row=surface.rows.find(r=>r.selector==='alpha:customer');assert.equal(row.state,'ready');
const own=row.modules.find(m=>m.relative_path===row.relative_path),reference=own.imports.find(i=>i.names.includes('AccountFields'));
assert.equal(reference.type_only,true);assert.ok(row.modules.some(m=>m.relative_path===reference.target_path));
const sourceAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'source-audit-observation.json'))),nativeAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'native-audit-observation.json')));
assert.ok(sourceAudit.modules.find(m=>m.relative_path===row.relative_path).imports.some(i=>i.names.includes('AccountFields')&&i.type_only));
assert.ok(!nativeAudit.modules.find(m=>m.relative_path===row.relative_path.replace(/\.ts$/,'.js')).imports.some(i=>i.specifier.includes('account')));
assert.equal(r.outcome.tested_factory_count,1);assert.deepEqual(r.outcome.remaining,[]);
console.log(JSON.stringify({...r.outcome,type_only_reference_retained:true}));
`);assert.equal(r.type_only_reference_retained,true);t.diagnostic(JSON.stringify(r));
});

test('owned execution retains captured source, rejects missing observations and in-flight drift, and cannot pass empty families',t=>{
 const f=native(t),r=f.run(String.raw`
const sourceFile=path.join(source,'specs/alpha/nodes/customer.json'),sourceBytes=fs.readFileSync(sourceFile);fs.unlinkSync(sourceFile);
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);fs.writeFileSync(sourceFile,sourceBytes);
for(const trigger of ['source-audit-input.json','native-audit-input.json','observations.json']){
 const original=fs.writeFileSync;let changed=false;
 fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/'+trigger)){original.call(fs,path.join(path.dirname(String(file)),'unexpected'),'x');changed=true;}return out;};
 try{assert.throws(()=>executeCrossGeneratorOwnedValues(plan,surface,definition,options),/artifact changed or unexpected/);assert.ok(changed);}finally{fs.writeFileSync=original;}
}
const originalSpawn=cp.spawnSync;let changed=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args.includes('--permission')){const value=JSON.parse(out.stdout);value.rows.pop();out.stdout=JSON.stringify(value);changed=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorOwnedValues(plan,surface,definition,options),/native observation mismatch/);assert.ok(changed);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();}
const budgetFile=path.join(source,'specs/alpha/nodes/budget.json'),budget=JSON.parse(fs.readFileSync(budgetFile));budget.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:false}};fs.writeFileSync(budgetFile,JSON.stringify(budget));
const g=loadCompiledProjectGraph(source),p=planCompiledReconciledProject(g,selection),b=createCrossGeneratorBoundary(g,p,definitions['cross-generator-verification']),c=createCrossGeneratorOwnedValueControls(g,p,b,definitions['cross-generator-owned-values']),s=createCrossGeneratorOwnedValueSurface(g,p,b,c,definition);
assert.ok(s.rows.every(r=>r.state!=='ready'));assert.equal(s.rows.find(r=>r.selector==='alpha:customer').state,'not_evaluable');const before=fs.readdirSync(options.workspace_parent);assert.throws(()=>executeCrossGeneratorOwnedValues(p,s,definition,options),/no ready interoperability/);assert.deepEqual(fs.readdirSync(options.workspace_parent),before);
assertCrossGeneratorExecutionCurrent(r);console.log(JSON.stringify({captured_source:true,in_flight_rejections:3,missing_observation_rejected:true,empty_pass_rejected:true}));
`);assert.equal(r.empty_pass_rejected,true);t.diagnostic(JSON.stringify(r));
});
test('owned execution complete compiler package custody detects library, platform executable and extra tool-file drift', t => {
  const f = native(t), result = f.run(String.raw`
const packageRoot=path.join(options.workspace_parent,'tool-copy','node_modules');fs.mkdirSync(packageRoot,{recursive:true});
fs.cpSync(options.typescript_root,path.join(packageRoot,'typescript'),{recursive:true});
fs.cpSync('/opt/node-toolchain/node_modules/@typescript',path.join(packageRoot,'@typescript'),{recursive:true});
options.typescript_root=path.join(packageRoot,'typescript');
const r=executeCrossGeneratorOwnedValues(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
let mutations=0;
for(const p of [path.join(options.typescript_root,'lib/getExePath.js'),path.join(options.typescript_root,'dist/api/sync/api.js'),path.join(packageRoot,'@typescript/typescript-linux-x64/lib/tsc')]){
 const original=fs.readFileSync(p);fs.appendFileSync(p,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.writeFileSync(p,original);assertCrossGeneratorExecutionCurrent(r);mutations++;
}
const extra=path.join(options.typescript_root,'extra');fs.writeFileSync(extra,'x');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/toolchain changed/);fs.unlinkSync(extra);assertCrossGeneratorExecutionCurrent(r);
const originalSpawn=cp.spawnSync,tool=path.join(options.typescript_root,'lib/getExePath.js'),before=fs.readFileSync(tool);let injected=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args[0]===path.join(options.typescript_root,'bin/tsc')){fs.appendFileSync(tool,'\n');injected=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorOwnedValues(plan,surface,definition,options),/toolchain changed/);assert.ok(injected);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();fs.writeFileSync(tool,before);}
assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({tool_mutations:mutations+1,in_flight_tool_rejections:1,compiler_files:Object.keys(r.tool_files.typescript).length,platform_files:Object.keys(r.tool_files.platform).length}));
`);
  assert.equal(result.tool_mutations, 4); t.diagnostic(JSON.stringify(result));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
