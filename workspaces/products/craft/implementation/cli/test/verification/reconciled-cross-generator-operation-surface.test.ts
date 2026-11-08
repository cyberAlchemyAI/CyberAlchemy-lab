import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {operationFixture,valueOperationFixture} from '../helpers/cross-generator-operation.ts';
import {publicFixture,publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorOperationSurface,assertCrossGeneratorOperationSurface} from '../../src/verification/reconciled-cross-generator-operation-surface.ts';
import {CROSS_GENERATOR_OPERATION_AUDIT_RUNNER} from '../../src/verification/reconciled-cross-generator-operation-audit.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';


test('Enum-only Operation needs no factory and passes both AST phases with a set of named sums',t=>{
 const f=valueOperationFixture(t,'application/domain'),n=native(t,'application/domain',f);
 assert.ok(n.graph.nodes.every(node=>!['Entity','Value Object'].includes(node.kind)));
 assert.deepEqual(n.row.initialization,[]);
 assert.deepEqual(n.row.modules.find(m=>m.role==='operation-provider')!.imports.map(i=>i.names),[['ruleAllowed'],['ChoiceValueComponent'],['StateValueComponent']]);
 for(const phase of ['source','native'] as const)assert.deepEqual(n.audit(phase).modules.flatMap((m:any)=>m.violations),[]);
});
test('guard order is source-bound and scalar result is not an owned value dependency',t=>{
 const f=operationFixture(t),first=controls(f).surface.rows[0]!;f.bindings.guards.reverse();
 const second=controls(f).surface.rows[0]!;
 assert.deepEqual(second.guards.map(g=>g.selector),first.guards.map(g=>g.selector).reverse());
 assert.notEqual(second.action_sha256,first.action_sha256);
 assert.deepEqual(second.initialization,first.initialization);
});

const project=path.resolve(import.meta.dirname,'../../../..'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definition=fs.readFileSync(path.join(base,'cross-generator-operation-contract.json'),'utf8'),boundaryDefinition=fs.readFileSync(path.join(base,'cross-generator-verification-contract.json'),'utf8');
function controls(f:Pick<ReturnType<typeof operationFixture>,'compile'>){
 const {graph,plan}=f.compile(),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 return {graph,plan,boundary,surface:createCrossGeneratorOperationSurface(graph,plan,boundary,definition)};
}
test('Operation source surface retains compound providers, duplicate Event slots and original dependency order',async t=>{
 for(const root of ['domain','application/domain'])await t.test(root,t=>{
  const f=operationFixture(t,root),c=controls(f),row=c.surface.rows[0]!;
  assert.deepEqual(c.surface.rows.map(r=>r.selector),['commerce:post']);
  assert.equal(row.events.length,2);assert.equal(new Set(row.events.map(e=>e.target)).size,1);
  assert.deepEqual(row.events.map(e=>e.clock),['posted-fact','audit-fact']);
  assert.deepEqual(row.guards.map(g=>g.selector),['commerce:can-post','commerce:receipt-matches']);
  assert.deepEqual(row.initialization.map(i=>i.selector),['commerce:detail','commerce:account','commerce:receipt']);
  const provider=row.modules.find(m=>m.role==='operation-provider')!;
  assert.deepEqual(provider.imports.map(i=>[i.names,i.type_only]),[
   [['ruleCanPost'],false],[['ruleReceiptMatches'],false],[['eventPosted'],false],[['EventInput','EventValue'],true],
   [['createAccountFactory'],false],[['createDetailFactory'],false],[['StatusValueComponent'],false],[['createReceiptFactory'],false]
  ]);
  assert.deepEqual([...new Set(row.modules.map(m=>m.role))].sort(),['enum-component','enum-definition','enum-runtime','event-provider','event-wrapper','factory','operation-provider','operation-wrapper','rule']);
  assert.equal(row.modules.length,13);
  assert.equal(row.behavior_status,'not_evaluable');assert.equal(row.native_status,'not_evaluable');
  assert.ok(c.surface.coverage.every(e=>e.behavior_status==='not_evaluable'));
  assert.ok(Object.isFrozen(row.initialization));
  assertCrossGeneratorOperationSurface(c.surface);
  assert.throws(()=>assertCrossGeneratorOperationSurface(structuredClone(c.surface)),/registered/);
  assert.throws(()=>createCrossGeneratorOperationSurface(c.graph,c.plan,c.boundary,definition+' '),/definition drift/);
  const other=controls(operationFixture(t,'relocated/root'));
  assert.throws(()=>createCrossGeneratorOperationSurface(c.graph,c.plan,other.boundary,definition),/foreign/);
  assert.doesNotThrow(()=>createCrossGeneratorOperationSurface(other.graph,c.plan,c.boundary,definition),'equal checked source bytes remain the same graph');
  assert.throws(()=>createCrossGeneratorOperationSurface(structuredClone(c.graph),c.plan,c.boundary,definition),/unvalidated/);
  const foreign=operationFixture(t),file='specs/commerce/nodes/positive.json',node=JSON.parse(fs.readFileSync(path.join(foreign.source,file),'utf8'));
  node.body.description='Distinct checked source bytes';foreign.write(file,node);
  assert.throws(()=>createCrossGeneratorOperationSurface(foreign.compile().graph,c.plan,c.boundary,definition),/foreign/);
 });
});
test('result-first adapter initialization caches shared named providers and supports named sum wrappers',t=>{
 const f=operationFixture(t);
 f.node('choice','Enum',{values:['Some','None'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-NAMED-CHOICE',variants:[
  {name:'Some',ontology_variant:'FIXTURE-NAMED-CHOICE#Some',payload:{kind:'named',selector:'commerce:account'}},
  {name:'None',ontology_variant:'FIXTURE-NAMED-CHOICE#None',payload:null}
 ]}});
 const type={kind:'optional',element:{kind:'list',element:{kind:'named',selector:'commerce:choice'}}};
 f.bindings.inputs.find((p:any)=>p.name==='response').type=type;f.bindings.result.type=type;f.save();
 const row=controls(f).surface.rows[0]!,provider=row.modules.find(m=>m.role==='operation-provider')!;
 assert.deepEqual(row.initialization.map(i=>i.selector),['commerce:detail','commerce:account','commerce:receipt']);
 assert.equal(provider.imports.filter(i=>i.names.includes('createAccountFactory')).length,1);
 assert.equal(provider.imports.filter(i=>i.names.includes('ChoiceValueComponent')).length,1);
 assert.ok(row.modules.some(m=>m.role==='sum'&&m.selector==='commerce:choice'));
 assert.equal(provider.imports.findIndex(i=>i.names.includes('ChoiceValueComponent')),4);
});
test('scalar Operations bind only actual Rules and leave unrelated graph relationships uncovered',t=>{
 const f=publicFixture(t),plan=planCompiledReconciledProject(f.graph,publicSelection()),boundary=createCrossGeneratorBoundary(f.graph,plan,boundaryDefinition),surface=createCrossGeneratorOperationSurface(f.graph,plan,boundary,definition);
 assert.equal(surface.rows.length,2);
 for(const row of surface.rows){assert.equal(row.modules.length,3);assert.deepEqual(row.initialization,[]);assert.deepEqual(row.events,[]);assert.ok(row.modules.every(m=>['rule','operation-wrapper','operation-provider'].includes(m.role)));}
 assert.ok(surface.coverage.some(e=>e.state==='uncovered'));assert.equal(surface.behavior_status,'not_evaluable');
});

function native(t:any,moduleRoot='domain',f:Pick<ReturnType<typeof operationFixture>,'root'|'compile'>=operationFixture(t,moduleRoot)){
 const c=controls(f),row=c.surface.rows[0]!,root=path.join(f.root,'native'),src=path.join(root,'source'),out=path.join(root,'compiled');
 fs.mkdirSync(root);
 for(const m of row.modules){const artifact=c.plan.resolved.artifacts.find(a=>a.relative_path===m.relative_path)!,file=path.join(src,m.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,artifact.content);}
 const sourceConfig=path.join(root,'source.json'),nativeConfig=path.join(root,'native.json');
 fs.writeFileSync(sourceConfig,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',rootDir:src,outDir:out,types:[]},files:row.modules.map(m=>path.join(src,m.relative_path))}));
 fs.writeFileSync(nativeConfig,JSON.stringify({compilerOptions:{allowJs:true,checkJs:false,target:'ES2022',module:'CommonJS',types:[]},files:row.modules.map(m=>path.join(out,m.relative_path.replace(/\.ts$/,'.js')))}));
 const runner=path.join(root,'audit.mjs'),input=path.join(root,'input.json');fs.writeFileSync(runner,CROSS_GENERATOR_OPERATION_AUDIT_RUNNER);
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:60000,maxBuffer:16777216});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 const compile=()=>command(['tsc','--project',sourceConfig]);compile();
 const audit=(phase:'source'|'native',runnerText=CROSS_GENERATOR_OPERATION_AUDIT_RUNNER)=>{
  fs.writeFileSync(runner,runnerText);
  fs.writeFileSync(input,JSON.stringify({definition,phase,module_root:phase==='source'?src:out,module_paths:row.modules.map(m=>phase==='source'?m.relative_path:m.relative_path.replace(/\.ts$/,'.js')),modules:row.modules,support_modules:row.modules.filter(m=>m.role==='enum-runtime').map(m=>({relative_path:m.relative_path,source_sha256:m.sha256}))}));
  return JSON.parse(command(['node',runner,'/opt/node-toolchain/node_modules/typescript',phase==='source'?sourceConfig:nativeConfig,input]));
 };
 return {...f,...c,row,root,src,out,compile,audit};
}
test('strict-compiled compound Operation passes independent source and native AST surfaces in both layouts',async t=>{
 for(const root of ['domain','application/domain'])await t.test(root,t=>{
  const n=native(t,root);
  for(const phase of ['source','native'] as const){
   const result=n.audit(phase);assert.equal(result.definition_sha256,sha256(definition));
   assert.equal(result.modules.length,n.row.modules.length);
   assert.deepEqual(result.modules.flatMap((m:any)=>m.violations.map((v:any)=>({path:m.relative_path,...v}))),[]);
  }
 });
});
test('dedicated Operation audit rejects compiling source escapes and native binding escapes',t=>{
 const n=native(t),sourceFile=path.join(n.src,n.row.provider_path),source=fs.readFileSync(sourceFile,'utf8');
 const sourceMutants=[
  source+'\nObject.seal({});\n',
  source+'\nObject.freeze(Object.prototype);\n',
  source+'\nPromise.resolve();\n',
  source+'\nconst hidden=Object["defineProperty"]({},"x",{value:1});\n',
 ];
 for(const mutant of sourceMutants){fs.writeFileSync(sourceFile,mutant);n.compile();assert.ok(n.audit('source').modules.some((m:any)=>m.violations.length));}
 fs.writeFileSync(sourceFile,source);n.compile();
 const file=path.join(n.out,n.row.relative_path.replace(/\.ts$/,'.js')),original=fs.readFileSync(file,'utf8');
 for(const mutant of [
  original+'\nexports.extra=1;\n',
  original+'\nconst alias=exports;\n',
  original+'\nconst load=require;load("./post.provider.js");\n',
  original.replace('Object.assign(post_provider_js_1.execute,','Object.assign(()=>{},'),
  original+'\nObject.defineProperty(exports,"surplus",{value:1});\n'
 ]){
  assert.notEqual(mutant,original);fs.writeFileSync(file,mutant);assert.ok(n.audit('native').modules.some((m:any)=>m.violations.length));
 }
 fs.writeFileSync(file,original);
 const wrapper=path.join(n.src,n.row.relative_path),wrapperSource=fs.readFileSync(wrapper,'utf8');
 for(const mutant of [wrapperSource.replace('export type {','export {'),wrapperSource+'\nexport type {OperationFailure} from "./post.provider.js";\n']){
  fs.writeFileSync(wrapper,mutant);assert.ok(n.audit('source').modules.some((m:any)=>m.violations.length));
 }
 fs.writeFileSync(wrapper,wrapperSource);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
