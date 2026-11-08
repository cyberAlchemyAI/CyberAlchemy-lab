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
import {createCrossGeneratorFactorySurface} from '../../src/verification/reconciled-cross-generator-factory-surface.ts';
import {executeCrossGeneratorFactory} from '../../src/verification/reconciled-cross-generator-execution.ts';
import type {FactoryBinding} from '../../src/generation/configured-factories.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),cli=path.join(project,'impl/cli'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definitions=Object.fromEntries(['cross-generator-factory','cross-generator-factory-execution','cross-generator-verification'].map(k=>[k,fs.readFileSync(path.join(base,k+'-contract.json'),'utf8')]));
const definition=definitions['cross-generator-factory-execution']!;

function extended(f:Fixture){
 const original=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/nodes/budget.json'),'utf8'));
 const featureFile=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(featureFile,'utf8'));
 for(const id of ['first','second']){
  const n=structuredClone(original);n.node_id=id;n.body.description=id;n.body.typed_contract.ontology_rule='TEST-'+id.toUpperCase();
  n.body.typed_contract.expression={op:'rule_ref',selector:'alpha:budget',arguments:n.body.typed_contract.parameters.map((p:any)=>({parameter:p.name,value:{op:'path',root:p.name,properties:[]}}))};
  fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/'+id+'.json'),JSON.stringify(n));feature.nodes.push(id);
 }
 fs.writeFileSync(featureFile,JSON.stringify(feature));
 const money=f.selection.factories.find((f:FactoryBinding)=>f.selector==='alpha:money')! as any;
 money.extensions=['first','second'].map(id=>({id,validators:[{rule:'alpha:'+id,arguments:structuredClone(money.base_validators[0].arguments)}]}));
 const file=path.join(f.source,'specs/alpha/nodes/money.json'),node=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const [name,type,cardinality]of [
  ['note',{kind:'optional',element:{kind:'scalar',name:'String'}},'optional'],
  ['tags',{kind:'set',element:{kind:'scalar',name:'String'}},'many-unique'],
  ['choice',{kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'TEST-MONEY-CHOICE#None'},{name:'Amount',payload:{kind:'scalar',name:'UInt64'},ontology_variant:'TEST-MONEY-CHOICE#Amount'}]},'one']
 ]){
  node.body.fields.push(name);node.body.typed_contract.properties.push({name,type,ontology_property:'TEST-MONEY#'+name,identity:false,cardinality,meaning:name});
 }
 fs.writeFileSync(file,JSON.stringify(node));
}
test('retained native factory execution preserves ordered extensions and structured optional set sum fields',t=>{
 const f=native(t,'domain',extended),r=f.run(String.raw`
const r=executeCrossGeneratorFactory(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_factory_count,2);assert.deepEqual(r.outcome.remaining,[]);
const row=surface.rows.find(r=>r.selector==='alpha:money'),chains=new Set(row.cases.map(c=>JSON.parse(c.values[0]).chain.join(',')));
assert.ok(chains.has('first,second'));assert.ok(chains.has('second,first'));assert.equal(row.validator_outcomes.length,3);
const observed=JSON.parse(fs.readFileSync(path.join(r.workspace,'observations.json'))),money=observed.rows.find(r=>r.selector==='alpha:money');
assert.ok(money.cases.some(c=>c.calls.length===5&&c.calls[2].parent===1&&c.calls[4].parent===3));
console.log(JSON.stringify({...r.outcome,modules:r.native_modules.length,ordered_extensions:true,structured_fields:true}));
`);assert.equal(r.ordered_extensions,true);t.diagnostic(JSON.stringify(r));
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
const r=executeCrossGeneratorFactory(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
const row=surface.rows.find(r=>r.selector==='alpha:customer');assert.equal(row.state,'ready');
const own=row.modules.find(m=>m.relative_path===row.relative_path),reference=own.imports.find(i=>i.names.includes('AccountFields'));
assert.equal(reference.type_only,true);assert.ok(row.modules.some(m=>m.relative_path===reference.target_path));
const sourceAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'source-audit-observation.json'))),nativeAudit=JSON.parse(fs.readFileSync(path.join(r.workspace,'native-audit-observation.json')));
assert.ok(sourceAudit.modules.find(m=>m.relative_path===row.relative_path).imports.some(i=>i.names.includes('AccountFields')&&i.type_only));
assert.ok(!nativeAudit.modules.find(m=>m.relative_path===row.relative_path.replace(/\.ts$/,'.js')).imports.some(i=>i.specifier.includes('account')));
assert.equal(r.outcome.tested_factory_count,2);assert.deepEqual(r.outcome.remaining.map(r=>r.selector),['alpha:account']);
console.log(JSON.stringify({...r.outcome,type_only_reference_retained:true}));
`);assert.equal(r.type_only_reference_retained,true);t.diagnostic(JSON.stringify(r));
});

test('factory AST audits reject extra imports, type-runtime conflation and CommonJS export escapes',t=>{
 const f=native(t),r=f.run(String.raw`
const r=executeCrossGeneratorFactory(plan,surface,definition,options),root=r.workspace;let rejected=0;
const relative=selection.module_root+'/features/alpha/src/domain/entities/customer';
for(const stage of ['source','native']){
 const file=path.join(root,stage,relative+(stage==='source'?'.ts':'.js')),original=fs.readFileSync(file,'utf8');
 const audit=()=>JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,stage+'-audit-config.json'),path.join(root,stage+'-audit-input.json')],{encoding:'utf8',timeout:60000}));
 assert.ok(audit().modules.every(m=>m.violations.length===0));
 const mutations=stage==='source'?[
  s=>'import {readFileSync} from "node:fs";\n'+s,
  s=>s.replace('import type {MoneySnapshot','import {MoneySnapshot'),
  s=>s+'\nexport const extra=1;',
  s=>s+'\nconst dynamic=()=>import("node:fs");',
  s=>s+'\nconst ambient=()=>process.cwd();',
  s=>s.replace(/^export const createCustomerFactory = .*;$/m,'export type createCustomerFactory = () => unknown;')
 ]:[
  s=>'const foreign=require("node:fs");\n'+s,
  s=>s+'\nexports.extra=Object.freeze({});',
  s=>s+'\nconst alias=require;alias("node:fs");',
  s=>s+'\nfunction nested(){return require("node:fs");}',
  s=>s+'\nexports.CustomerValueComponent=Object.freeze({});',
  s=>s+'\nmodule.exports={};',
  s=>s+'\nexports.CustomerFields=1;'
 ];
 for(const mutate of mutations){const next=mutate(original);assert.notEqual(next,original);fs.writeFileSync(file,next);assert.ok(audit().modules.some(m=>m.violations.length>0));assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);rejected++;}
 fs.writeFileSync(file,original);assertCrossGeneratorExecutionCurrent(r);
}
console.log(JSON.stringify({surface_mutants:rejected}));
`);assert.equal(r.surface_mutants,13);t.diagnostic(JSON.stringify(r));
});

test('strict-compiling factory call mutations pass surface checks but fail original behavior observation',t=>{
 const f=native(t),r=f.run(String.raw`
const r=executeCrossGeneratorFactory(plan,surface,definition,options),root=r.workspace;
const money=selection.module_root+'/features/alpha/src/domain/value-objects/money.ts',customer=selection.module_root+'/features/alpha/src/domain/entities/customer.ts';
const originals=new Map([money,customer].map(p=>[p,fs.readFileSync(path.join(root,'source',p),'utf8')]));
const compile=()=>cp.execFileSync(process.execPath,[path.join(options.typescript_root,'bin/tsc'),'--project',path.join(root,'compiler.json'),'--pretty','false'],{encoding:'utf8',timeout:60000});
const observe=()=>JSON.parse(cp.execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--disable-proto=throw',path.join(root,'runner.mjs'),path.join(root,'cases.json'),path.join(root,'native')],{encoding:'utf8',timeout:60000,maxBuffer:16777216}));
const mutations=[
 [money,s=>s.replace('["approved"]:fields["approved"]','["approved"]:true')],
 [customer,s=>s.replace('validator.validate(fields) === true','(validator.validate(fields),validator.validate(fields)) === true')],
 [customer,s=>s.replace('["amount"]:fields["credit"].fields["amount"]','["amount"]:2n')]
];
for(const [p,mutate]of mutations){
 for(const [file,text]of originals)fs.writeFileSync(path.join(root,'source',file),text);
 const next=mutate(originals.get(p));assert.notEqual(next,originals.get(p));fs.writeFileSync(path.join(root,'source',p),next);compile();
 const audit=JSON.parse(cp.execFileSync(process.execPath,[path.join(root,'audit.mjs'),options.typescript_root,path.join(root,'native-audit-config.json'),path.join(root,'native-audit-input.json')],{encoding:'utf8',timeout:60000}));
 assert.ok(audit.modules.every(m=>m.violations.length===0));assert.throws(()=>checkCrossGeneratorFactoryObservations(behavior,observe()),/native observation mismatch/);assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);
}
for(const [p,text]of originals)fs.writeFileSync(path.join(root,'source',p),text);compile();checkCrossGeneratorFactoryObservations(behavior,observe());assertCrossGeneratorExecutionCurrent(r);
console.log(JSON.stringify({strict_compiling_semantic_mutants:mutations.length}));
`);assert.equal(r.strict_compiling_semantic_mutants,3);t.diagnostic(JSON.stringify(r));
});

test('factory execution retains captured source, rejects missing observations and in-flight drift, and cannot pass empty families',t=>{
 const f=native(t),r=f.run(String.raw`
const sourceFile=path.join(source,'specs/alpha/nodes/customer.json'),sourceBytes=fs.readFileSync(sourceFile);fs.unlinkSync(sourceFile);
const r=executeCrossGeneratorFactory(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);fs.writeFileSync(sourceFile,sourceBytes);
for(const trigger of ['source-audit-input.json','native-audit-input.json','observations.json']){
 const original=fs.writeFileSync;let changed=false;
 fs.writeFileSync=function(file,...args){const out=original.call(fs,file,...args);if(String(file).endsWith('/'+trigger)){original.call(fs,path.join(path.dirname(String(file)),'unexpected'),'x');changed=true;}return out;};
 try{assert.throws(()=>executeCrossGeneratorFactory(plan,surface,definition,options),/artifact changed or unexpected/);assert.ok(changed);}finally{fs.writeFileSync=original;}
}
const originalSpawn=cp.spawnSync;let changed=false;
cp.spawnSync=function(exe,args,...rest){const out=originalSpawn.call(cp,exe,args,...rest);if(args.includes('--permission')){const value=JSON.parse(out.stdout);value.rows.pop();out.stdout=JSON.stringify(value);changed=true;}return out;};syncBuiltinESMExports();
try{assert.throws(()=>executeCrossGeneratorFactory(plan,surface,definition,options),/native observation mismatch/);assert.ok(changed);}finally{cp.spawnSync=originalSpawn;syncBuiltinESMExports();}
const budgetFile=path.join(source,'specs/alpha/nodes/budget.json'),budget=JSON.parse(fs.readFileSync(budgetFile));budget.body.typed_contract.expression={op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:false}};fs.writeFileSync(budgetFile,JSON.stringify(budget));
const g=loadCompiledProjectGraph(source),p=planCompiledReconciledProject(g,selection),b=createCrossGeneratorBoundary(g,p,definitions['cross-generator-verification']),c=createCrossGeneratorFactoryControls(g,p,b,definitions['cross-generator-factory']),s=createCrossGeneratorFactorySurface(g,p,b,c,definition);
assert.ok(s.rows.every(r=>r.state==='not_evaluable'));const before=fs.readdirSync(options.workspace_parent);assert.throws(()=>executeCrossGeneratorFactory(p,s,definition,options),/no ready interoperability/);assert.deepEqual(fs.readdirSync(options.workspace_parent),before);
assertCrossGeneratorExecutionCurrent(r);console.log(JSON.stringify({captured_source:true,in_flight_rejections:3,missing_observation_rejected:true,empty_pass_rejected:true}));
`);assert.equal(r.empty_pass_rejected,true);t.diagnostic(JSON.stringify(r));
});
type Fixture=ReturnType<typeof recordWitnessFixture>;
function control(f:Fixture){
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']!);
 const behavior=createCrossGeneratorFactoryControls(graph,plan,boundary,definitions['cross-generator-factory']!);
 return {graph,plan,boundary,behavior,surface:createCrossGeneratorFactorySurface(graph,plan,boundary,behavior,definition)};
}
function mixed(f:Fixture){
 const add=(id:string,variants:any[])=>{
  const file=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(file,'utf8'));feature.nodes.push(id);fs.writeFileSync(file,JSON.stringify(feature));
  fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/'+id+'.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind:'Enum',body:{description:id,values:variants.map(v=>v.name),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-'+id.toUpperCase(),variants:variants.map(v=>({...v,ontology_variant:'TEST-'+id.toUpperCase()+'#'+v.name}))}}}));
 };
 add('status',[{name:'Open',payload:null},{name:'Closed',payload:null}]);
 add('amount-choice',[{name:'None',payload:null},{name:'Money',payload:{kind:'named',selector:'alpha:money'}}]);
 const file=path.join(f.source,'specs/alpha/nodes/customer.json'),customer=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const [name,selector]of [['status','status'],['status_again','status'],['amount_choice','amount-choice']]){
  customer.body.fields.push(name);customer.body.typed_contract.properties.push({name,type:{kind:'named',selector:'alpha:'+selector},ontology_property:'TEST-CUSTOMER#'+name,identity:false,cardinality:'one',meaning:name});
 }
 fs.writeFileSync(file,JSON.stringify(customer));
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
import {createCrossGeneratorFactoryControls,checkCrossGeneratorFactoryObservations} from './dist/verification/reconciled-cross-generator-factory.js';
import {createCrossGeneratorFactorySurface} from './dist/verification/reconciled-cross-generator-factory-surface.js';
import {executeCrossGeneratorFactory,assertCrossGeneratorExecutionCurrent} from './dist/verification/reconciled-cross-generator-execution.js';
const source=__SOURCE__,selection=__SELECTION__,definitions=__DEFINITIONS__,definition=definitions['cross-generator-factory-execution'];
const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),boundary=createCrossGeneratorBoundary(graph,plan,definitions['cross-generator-verification']);
const behavior=createCrossGeneratorFactoryControls(graph,plan,boundary,definitions['cross-generator-factory']),surface=createCrossGeneratorFactorySurface(graph,plan,boundary,behavior,definition);
const options={workspace_parent:__ROOT__,typescript_root:'/opt/node-toolchain/node_modules/typescript'};
`;
 return {...f,run:(body:string)=>{const client=path.join(f.root,'client.mjs');fs.writeFileSync(client,prefix.replace('__SOURCE__',JSON.stringify(f.source)).replace('__SELECTION__',JSON.stringify(f.selection)).replace('__DEFINITIONS__',JSON.stringify(definitions)).replace('__ROOT__',JSON.stringify(f.root))+body);return JSON.parse(command(['node',client]));}};
}

test('factory surfaces are source-derived, registered, exact across roots and retain import occurrences',t=>{
 for(const root of ['domain','application/domain']){
  const f=recordWitnessFixture(t,false,root);mixed(f);const c=control(f);
  const row=c.surface.rows.find(r=>r.selector==='alpha:customer')!;if(row.state!=='ready')throw Error(row.reason);assert.equal(row.state,'ready');
  assert.ok(Object.isFrozen(c.surface));assert.ok(Object.isFrozen(row.modules));
  assert.equal(c.surface.controls_sha256,c.behavior.controls_sha256);assert.notEqual(c.surface.surface_sha256,c.behavior.controls_sha256);
  const own=row.modules.find(m=>m.relative_path===row.relative_path)!;
  assert.deepEqual(own.value_exports,['CustomerFieldBindings','CustomerValueComponent','createCustomerFactory']);
  assert.equal(own.imports.filter(i=>i.target_path.endsWith('/status.component.ts')).length,4,'repeated runtime/type occurrences preserved');
  assert.ok(row.modules.some(m=>m.role==='enum-runtime'));assert.ok(row.modules.some(m=>m.role==='sum'));assert.ok(row.modules.some(m=>m.role==='rule'));
  assert.throws(()=>createCrossGeneratorFactorySurface(c.graph,c.plan,c.boundary,structuredClone(c.behavior),definition),/registered/);
  assert.throws(()=>createCrossGeneratorFactorySurface(c.graph,c.plan,c.boundary,c.behavior,definition+' '),/definition drift/);
  const before=fs.readdirSync(f.root);assert.throws(()=>executeCrossGeneratorFactory(c.plan,structuredClone(c.surface),definition,{workspace_parent:f.root,typescript_root:'/tmp'}),/registered/);assert.deepEqual(fs.readdirSync(f.root),before);
 }
});

test('retained native factory execution passes both layouts with original Rule calls and source/native audits',t=>{
 for(const moduleRoot of ['domain','application/domain']){
  const f=native(t,moduleRoot),result=f.run(String.raw`
const r=executeCrossGeneratorFactory(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.surface_sha256,surface.surface_sha256);assert.equal(r.controls_sha256,behavior.controls_sha256);
assert.equal(r.outcome.tested_factory_count,2);assert.equal(r.outcome.tested_case_count,290);assert.equal(r.outcome.tested_call_count,311);assert.equal(r.native_modules.length,6);assert.deepEqual(r.outcome.remaining,[]);
const input=JSON.parse(fs.readFileSync(path.join(r.workspace,'cases.json')));assert.ok(input.rows.every(row=>row.cases.every(c=>!Object.hasOwn(c,'expected'))));assert.ok(!Object.hasOwn(input,'surface_sha256'));
assert.equal(Object.keys(r.audits).length,2);assert.throws(()=>assertCrossGeneratorExecutionCurrent(structuredClone(r)),/registered/);
for(const name of ['source-audit-observation.json','native-audit-observation.json','observations.json','cases.json','runner.mjs']){
 const file=path.join(r.workspace,name),before=fs.readFileSync(file);fs.appendFileSync(file,'\n');assert.throws(()=>assertCrossGeneratorExecutionCurrent(r),/artifact changed/);fs.writeFileSync(file,before);assertCrossGeneratorExecutionCurrent(r);
}
console.log(JSON.stringify({module_root:selection.module_root,...r.outcome,modules:r.native_modules.length,audits:2,retained_mutations:5}));
`);assert.equal(result.tested_factory_count,2);t.diagnostic(JSON.stringify(result));
 }
});

test('plain Enum, payload sum and repeated owned field dependencies retain independent native surfaces',t=>{
 const f=native(t,'domain',mixed),r=f.run(String.raw`
const r=executeCrossGeneratorFactory(plan,surface,definition,options);assertCrossGeneratorExecutionCurrent(r);
assert.equal(r.outcome.tested_factory_count,2);assert.deepEqual(r.outcome.remaining,[]);
const roles=[...new Set(surface.rows.filter(r=>r.state==='ready').flatMap(r=>r.modules.map(m=>m.role)))].sort();
assert.deepEqual(roles,['enum-component','enum-definition','enum-runtime','factory','rule','sum']);
console.log(JSON.stringify({...r.outcome,roles,modules:r.native_modules.length}));
`);assert.equal(r.tested_factory_count,2);t.diagnostic(JSON.stringify(r));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
