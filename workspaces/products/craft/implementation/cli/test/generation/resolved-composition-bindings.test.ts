import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {fixture,publicFixture,publicSelection} from '../helpers/composition-project.ts';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileProjectComposition} from '../../src/input/project-composition.ts';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.ts';
import {planResolvedArtifacts,RESOLVED_ARTIFACT_SELECTION_VERSION,RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {CONFIGURED_CALCULATION_VERSION} from '../../src/generation/configured-calculations.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {planCompiledReconciledProject,RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE} from '../../src/generation/reconciled-project.ts';
import {planReconciledProject,selectReconciledArtifacts} from '../../src/generation/reconciled-project.ts';
import {createReconciledVerificationProjection} from '../../src/verification/reconciled-projection.ts';
import {OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {planProjectBuild,planCompiledProjectBuild,publishProjectBuild,verifyProjectBuild} from '../../src/generation/project-build.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {planProjectInstantiation} from '../../src/generation/project-instantiation.ts';
import {APPLICATION_LAYOUT} from '../../src/generation/output-layout.ts';
import {runCli} from '../../src/cli/main.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {planResolvedCompositionBindings,validateResolvedCompositionBindings,renderResolvedCompositionBindings,RESOLVED_COMPOSITION_BINDINGS_DEFINITION_SHA256} from '../../src/generation/resolved-composition-bindings.ts';

const project=path.resolve(import.meta.dirname,'../../../..');
const definition=fs.readFileSync(path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation/resolved-composition-bindings-contract.json'),'utf8');
const sources={configuration:getReconciledSource('configuration'),base:getReconciledSource('base'),typescript:getReconciledSource('typescript'),calculation_contract:getReconciledSource('calculation_v1')};
const scalar=(name:string)=>({kind:'scalar',name});
test('public source and snapshot composition plans preserve exact artifacts and node-only closure',t=>{
 const f=publicFixture(t),selection=publicSelection();
 const p=planCompiledReconciledProject(f.graph,selection),fromSource=planReconciledProject(f.source,selection);
 assert.deepEqual(p,fromSource);
 assert.ok(p.composition);assert.equal(p.composition.compositions.length,1);
 const view=selectReconciledArtifacts(p);
 assert.deepEqual(view.artifacts.map(a=>a.relative_path).sort(),[...p.resolved.artifacts,...p.composition.artifacts].map(a=>a.relative_path).sort());
 for(const a of p.composition.artifacts)assert.equal(view.artifacts.find(v=>v.relative_path===a.relative_path),a);
 const node=selectReconciledArtifacts(p,['alpha:compute']);
 assert.ok(node.artifacts.length);assert.ok(node.artifacts.every(a=>!a.relative_path.startsWith('compositions/')));
 for(const a of node.artifacts)assert.equal(view.artifacts.find(v=>v.relative_path===a.relative_path),a);
 assert.deepEqual(createReconciledVerificationProjection(f.graph,p).composition_projection,p.composition);
 const build=planCompiledProjectBuild(f.graph,'typescript',undefined,undefined,selection);
 fs.rmSync(f.source,{recursive:true});assert.deepEqual(planCompiledReconciledProject(f.graph,selection),p);
 assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript',undefined,undefined,selection),build);
});

test('public composition builds publish exact files and compile unchanged behavior in both output layouts',async t=>{
 const f=publicFixture(t),selection=publicSelection('alternate/deeper');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const image=nativeToolchainImage();
 assert.equal(image, NATIVE_TEST_IMAGE_ID);
 for(const layout of [undefined,APPLICATION_LAYOUT.id]){
  const tag=layout?'application':'plain',target=path.join(f.root,tag),output=path.join(f.root,tag+'-js'),prefix=layout?'domain/typescript/src/':'';
  const p=planProjectBuild(f.source,'typescript',undefined,layout,selection);
  assert.deepEqual(p,planCompiledProjectBuild(f.graph,'typescript',undefined,layout,selection));
  const published=publishProjectBuild(p,target);assert.equal(verifyProjectBuild(f.source,'typescript',target,undefined,layout,selection).result,'pass');
  assert.deepEqual(published.receipt.artifacts,p.artifacts.map(({content,...a})=>a));
  fs.mkdirSync(output);
  execFileSync('docker',['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),
   '--mount','type=bind,source='+target+',target=/input,readonly','--mount','type=bind,source='+output+',target=/output','--mount','type=bind,source='+deps+',target='+deps+',readonly',image,
   'tsc','--ignoreConfig','--strict','--skipLibCheck','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','commonjs','--rootDir','/input','--outDir','/output',...p.artifacts.filter(a=>a.relative_path.endsWith('.ts')).map(a=>'/input/'+a.relative_path)],{encoding:'utf8'});
  for(const a of p.artifacts)assert.equal(sha256(fs.readFileSync(path.join(target,a.relative_path))),a.sha256);
  const api=require(path.join(output,prefix+'compositions/calculate/core-api.js'));
  const behavior=await import(pathToFileURL(path.join(target,prefix+'compositions/calculate/behavior.mjs')).href);
  assert.deepEqual(behavior.execute({input:{id:'request',qty:'10',rebate:'3'}},api),{net:'7',other:'13'});
  assert.deepEqual(behavior.execute({input:{id:'request',qty:'18446744073709551615',rebate:'0'}},api),{net:'18446744073709551615',other:'18446744073709551615'});
  assert.throws(()=>behavior.execute({input:{id:'request',qty:'2',rebate:'3'}},api),/CALCULATION_UNDERFLOW/);
  assert.throws(()=>behavior.execute({input:{id:'request',qty:'18446744073709551615',rebate:'1'}},api),/CALCULATION_OVERFLOW/);
  const file=path.join(target,prefix+'compositions/calculate/behavior.mjs'),original=fs.readFileSync(file);
  fs.appendFileSync(file,'\n// changed');assert.equal(verifyProjectBuild(f.source,'typescript',target,undefined,layout,selection).result,'fail');
  fs.writeFileSync(file,original);fs.unlinkSync(file);assert.equal(verifyProjectBuild(f.source,'typescript',target,undefined,layout,selection).result,'fail');
  fs.writeFileSync(file,original);const extra=path.join(target,prefix+'compositions/calculate/surplus.json');fs.writeFileSync(extra,'{}');
  assert.equal(verifyProjectBuild(f.source,'typescript',target,undefined,layout,selection).result,'fail');fs.unlinkSync(extra);
  assert.equal(verifyProjectBuild(f.source,'typescript',target,undefined,layout,selection).result,'pass');
 }
});
test('public composition CLI and instantiation share inventories and reject invalid selection before writes',t=>{
 const f=publicFixture(t),selection=publicSelection(),p=planReconciledProject(f.source,selection),selected=path.join(f.root,'selection.json');fs.writeFileSync(selected,JSON.stringify(selection));
 const invoke=(args:string[])=>{const out:string[]=[],errors:string[]=[];const code=runCli(args,{stdout:s=>out.push(s),stderr:s=>errors.push(s)});return {code,out,errors};};
 const whole=planProjectInstantiation(f.source,['typescript'],selection);assert.deepEqual(whole.artifacts,selectReconciledArtifacts(p).artifacts);
 const node=planInstantiation('alpha:compute','typescript',null,undefined,p);assert.deepEqual(node.artifacts,selectReconciledArtifacts(p,['alpha:compute']).artifacts);
 assert.throws(()=>publishProjectBuild(structuredClone(planProjectBuild(f.source,'typescript',undefined,undefined,selection)),path.join(f.root,'forged')),/registered/);
 for(const layout of [undefined,APPLICATION_LAYOUT.id]){
  const target=path.join(f.root,layout?'cli-application':'cli-plain'),flags=['--language','typescript','--target-root',target,'--compilation-selection',selected,...(layout?['--output-layout',layout]:[])];
  const result=invoke(['build',f.source,...flags]);assert.equal(result.code,0,result.errors.join(''));
  assert.deepEqual(JSON.parse(result.out.at(-1)!).receipt,planProjectBuild(f.source,'typescript',undefined,layout,selection).receipt);
  assert.equal(invoke(['verify',f.source,...flags]).code,0);
 }
 const incomplete={...selection,factories:[]};fs.writeFileSync(selected,JSON.stringify(incomplete));const target=path.join(f.root,'rejected');
 const rejected=invoke(['build',f.source,'--language','typescript','--target-root',target,'--compilation-selection',selected]);
 assert.equal(rejected.code,22);assert.match(rejected.errors.join(''),/exact qualified binding coverage/);assert.equal(fs.existsSync(target),false);
 const rust=structuredClone(f.composition);rust.model.endpoint.target='rust-http';rust.model.endpoint.runtime='rust>=1.94';const endpoint=rust.ontology.nodes.find((n:any)=>n.name==='Endpoint');endpoint!.binding=rust.model.endpoint;f.write('compositions/calculate.json',rust);
 assert.throws(()=>planProjectBuild(f.source,'typescript',undefined,undefined,selection),/unsupported composition target/);assert.equal(fs.existsSync(target),false);
});

test('public integration preserves the source profile single-composition restriction',t=>{
 const f=publicFixture(t),second=structuredClone(f.composition);second.id='second';
 f.write('compositions/second.json',second);f.write('project.json',{...f.manifest,compositions:['second','calculate']});
 assert.throws(()=>planReconciledProject(f.source,publicSelection()),/exactly one function composition/);
});

test('definition and scaffold bind the pure adapter; source behavior and typed record bindings stay unchanged',t=>{
 assert.equal(sha256(definition),RESOLVED_COMPOSITION_BINDINGS_DEFINITION_SHA256);
 const scaffold=JSON.parse(fs.readFileSync(path.join(project,'development/reconciliation-v1/ontology/resolved-composition-bindings-candidate.json'),'utf8'));
 assert.equal(scaffold.authority_effect,'none');assert.equal(scaffold.status,'candidate-navigation-only');
 const f=fixture(t),resolved=f.resolved(),p=planResolvedCompositionBindings(f.graph,resolved,definition);
 assert.deepEqual(p,planResolvedCompositionBindings(f.graph,resolved,definition));
 assert.equal(p.compositions.length,1);const c=p.compositions[0]!;
 assert.deepEqual(c.bindings.map(b=>[b.name,b.selector,b.role]),[['Net','alpha:compute','calculation-call'],['Other','beta:compute','calculation-call'],['Values','alpha:values','structural-record']]);
 assert.equal(c.bindings[2]!.native_target,null);
 for(const [name,content] of Object.entries(f.graph.compositions![0]!.artifacts))assert.equal(p.artifacts.find(a=>a.relative_path==='compositions/calculate/'+name)!.content,content);
 assert.deepEqual(p.modules[0]!.imports.map(i=>i.target_path),['domain/features/alpha/src/domain/calculations/compute.ts','domain/features/beta/src/domain/calculations/compute.ts']);
 assert.equal(p.artifacts.filter(a=>a.relative_path.endsWith('.ts')).length,1);
 assert.doesNotMatch(p.artifacts.find(a=>a.relative_path.endsWith('core-api.ts'))!.content,/createValues|factory|execute\(/);
 assert.ok(Object.isFrozen(c.bindings[0]!.arguments));assert.ok(Object.isFrozen(p.artifacts));
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
 assert.deepEqual(validateResolvedCompositionBindings(JSON.parse(renderResolvedCompositionBindings(p)),f.graph,resolved,definition),p);
 fs.renameSync(f.source,path.join(f.root,'moved-source'));
 assert.deepEqual(planResolvedCompositionBindings(f.graph,resolved,definition),p);
});
test('unregistered, foreign, stale, missing and unsafe selected bindings reject without writes',t=>{
 const f=fixture(t),resolved=f.resolved(),p=planResolvedCompositionBindings(f.graph,resolved,definition),before=fs.readdirSync(f.root);
 assert.throws(()=>planResolvedCompositionBindings(structuredClone(f.graph),resolved,definition),/unvalidated or changed/);
 assert.throws(()=>planResolvedCompositionBindings(f.graph,structuredClone(resolved),definition),/unregistered/);
 assert.throws(()=>planResolvedCompositionBindings(f.graph,resolved,definition+' '),/definition/);
 const foreign=fixture(t);foreign.write('project.json',{...foreign.manifest,project_id:'foreign',compositions:['calculate']});
 assert.throws(()=>planResolvedCompositionBindings(loadCompiledProjectGraph(foreign.source),resolved,definition),/graph/);
 assert.throws(()=>planResolvedCompositionBindings(f.graph,f.resolved(f.graph,'domain',['alpha:compute']),definition),/selected native Calculation/);
 assert.throws(()=>planResolvedCompositionBindings(f.graph,f.resolved(f.graph,'compositions/calculate/core-api.ts'),definition),/module root/);
 for(const mutate of [(v:any)=>v.compositions[0].bindings[0].selector='beta:compute',(v:any)=>v.artifacts[0].content+=' ',(v:any)=>v.modules[0].imports.pop(),(v:any)=>v.compositions.pop()]){
  const altered=structuredClone(p);mutate(altered);const {plan_sha256,...body}=altered;altered.plan_sha256=sha256(canonicalJson(body));
  assert.throws(()=>validateResolvedCompositionBindings(altered,f.graph,resolved,definition),/changed|incomplete/);
  assert.throws(()=>renderResolvedCompositionBindings(altered),/registered/);
 }
 assert.deepEqual(fs.readdirSync(f.root),before);
 let reads=0;
 assert.throws(()=>planResolvedCompositionBindings(f.graph,{get modules(){reads++;return resolved.modules;}} as any,definition),/unregistered/);
 assert.equal(reads,0);
 f.graph.compositions![0]!.source.core_bindings.Net.fields.qty='right';
 assert.throws(()=>planResolvedCompositionBindings(f.graph,resolved,definition),/unvalidated or changed/);
});
test('unsupported target rejects and incomplete public bindings never bypass whole-project checking',t=>{
 const f=fixture(t),selection={schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root:'domain',layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],factories:[],operations:[],workflows:[]};
 assert.throws(()=>planCompiledReconciledProject(f.graph,selection),/exact qualified binding coverage/);
 const rust=structuredClone(f.composition);
 rust.model.endpoint.target='rust-http';rust.model.endpoint.runtime='rust>=1.94';
 rust.ontology.nodes.find(n=>n.name==='Endpoint')!.binding=rust.model.endpoint;
 f.write('compositions/calculate.json',rust);
 const graph=loadCompiledProjectGraph(f.source),resolved=f.resolved(graph),before=fs.readdirSync(f.root);
 assert.throws(()=>planResolvedCompositionBindings(graph,resolved,definition),/unsupported composition target; no fallback/);
 assert.deepEqual(fs.readdirSync(f.root),before);
});
test('legacy provenance remains exact and a changed checked source cannot reuse the old native plan',t=>{
 const f=fixture(t),prior=f.resolved(),legacy:any=structuredClone(f.composition);
 delete legacy.ontology.source_format;legacy.ontology.schema_version='alchlang.derived-ontology/v1';
 f.write('compositions/calculate.json',legacy);
 const graph=loadCompiledProjectGraph(f.source),resolved=f.resolved(graph),p=planResolvedCompositionBindings(graph,resolved,definition);
 assert.throws(()=>planResolvedCompositionBindings(graph,prior,definition),/graph/);
 for(const [name,content] of Object.entries(graph.compositions![0]!.artifacts))assert.equal(p.artifacts.find(a=>a.relative_path==='compositions/calculate/'+name)!.content,content);
 assert.ok(p.artifacts.some(a=>a.relative_path.endsWith('source.alch')));
 assert.ok(!p.artifacts.some(a=>a.relative_path.endsWith('source.json')));
});
function native(root:string,resolved:ReturnType<typeof planResolvedArtifacts>,p:ReturnType<typeof planResolvedCompositionBindings>){
 const input=path.join(root,'input'),output=path.join(root,'js');fs.mkdirSync(input,{recursive:true});fs.mkdirSync(output);
 for(const a of [...resolved.artifacts,...p.artifacts]){const file=path.join(input,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content,{flag:'wx'});}
 const all=[...resolved.artifacts,...p.artifacts],nativeFiles=all.filter(a=>a.relative_path.endsWith('.ts'));
 const image=nativeToolchainImage();
 assert.equal(image, NATIVE_TEST_IMAGE_ID);
 execFileSync('docker',['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+input+',target=/input,readonly','--mount','type=bind,source='+output+',target=/output',image,'tsc','--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--rootDir','/input','--outDir','/output',...nativeFiles.map(a=>'/input/'+a.relative_path)],{encoding:'utf8'});
 for(const a of all)assert.equal(sha256(fs.readFileSync(path.join(input,a.relative_path))),a.sha256,'native compiler must not repair input');
 return {input,output,api:createRequire(import.meta.url)(path.join(output,'compositions/calculate/core-api.js'))};
}
test('native authored behavior uses qualified calculations, renamed ordered arguments and exact failures in two roots',async t=>{
 const f=fixture(t);
 for(const moduleRoot of ['domain','alternate/deeper']){
  const resolved=f.resolved(f.graph,moduleRoot),p=planResolvedCompositionBindings(f.graph,resolved,definition),n=native(path.join(f.root,moduleRoot==='domain'?'one':'two'),resolved,p);
  const behavior=await import(pathToFileURL(path.join(n.input,'compositions/calculate/behavior.mjs')).href);
  const calls:any[]=[];
  const api={evaluateCalculation(name:string,input:unknown){calls.push([name,input]);return n.api.evaluateCalculation(name,input);}};
  assert.deepEqual(behavior.execute({input:{id:'request',qty:'10',rebate:'3'}},api),{net:'7',other:'13'});
  assert.deepEqual(calls,[['Net',{qty:10n,rebate:3n}],['Other',{qty:10n,rebate:3n}]]);
  for(let qty=0n;qty<12n;qty++)for(let rebate=0n;rebate<12n;rebate++){
   const input={qty,rebate};
   assert.equal(n.api.evaluateCalculation('Other',input),qty+rebate);
   if(qty>=rebate)assert.equal(n.api.evaluateCalculation('Net',input),qty-rebate);
   else assert.throws(()=>n.api.evaluateCalculation('Net',input),/CALCULATION_UNDERFLOW/);
  }
  const max='18446744073709551615';
  assert.deepEqual(behavior.execute({input:{id:'request',qty:max,rebate:'0'}},n.api),{net:max,other:max});
  assert.throws(()=>behavior.execute({input:{id:'request',qty:'2',rebate:'3'}},n.api),/CALCULATION_UNDERFLOW/);
  assert.throws(()=>behavior.execute({input:{id:'request',qty:max,rebate:'1'}},n.api),/CALCULATION_OVERFLOW/);
  assert.throws(()=>n.api.evaluateCalculation('Other',{qty:1,rebate:'01'}),/CALCULATION_INPUT/);
  assert.throws(()=>n.api.evaluateCalculation('calculateCompute',{qty:10,rebate:3}),/COMPOSITION_CALCULATION/);
  let reads=0;const accessor={get qty(){reads++;return 10n;},rebate:3n};
  const hidden=Object.defineProperty({rebate:3n},'qty',{value:10n,enumerable:false});
  for(const bad of [null,[],{qty:10n},{qty:10n,rebate:3n,extra:0},Object.assign(Object.create({qty:10n}),{rebate:3n}),accessor,hidden,{qty:10n,rebate:3n,[Symbol('extra')]:0}])assert.throws(()=>n.api.evaluateCalculation('Net',bad),/COMPOSITION_CALCULATION_INPUT/);
  assert.equal(reads,0);
  assert.equal(n.api.evaluateCalculation('Net',Object.assign(Object.create(null),{qty:10n,rebate:3n})),7n);
 }
});
test('canonical Value Object composition and reused edge IDs reach the checked native binding without factories',async t=>{
 const plain=fixture(t,{valueObject:true});assert.equal(plain.graph.compositions!.length,1);
 const f=fixture(t,{valueObject:true,collidingEdges:true}),resolved=f.resolved(),p=planResolvedCompositionBindings(f.graph,resolved,definition);
 assert.equal(f.graph.nodes.find(n=>n.selector==='alpha:values')!.kind,'Value Object');
 assert.equal(p.compositions[0]!.bindings.find(b=>b.name==='Values')!.native_target,null);
 const n=native(path.join(f.root,'value-object'),resolved,p),behavior=await import(pathToFileURL(path.join(n.input,'compositions/calculate/behavior.mjs')).href);
 assert.deepEqual(behavior.execute({input:{id:'value',qty:'10',rebate:'3'}},n.api),{net:'7',other:'13'});
 const direct=compileProjectComposition(f.composition,f.graph.nodes.map(node=>({...node,kind:node.kind==='Value Object'?'ValueObject':node.kind})));
 assert.deepEqual(direct,f.graph.compositions![0]);
 const file='specs/alpha/nodes/values.json',invalid=JSON.parse(fs.readFileSync(path.join(f.source,file),'utf8'));
 invalid.body.typed_contract.properties[0].identity=true;f.write(file,invalid);
 assert.throws(()=>loadCompiledProjectGraph(f.source),/Value Object properties cannot designate Entity identity/);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
