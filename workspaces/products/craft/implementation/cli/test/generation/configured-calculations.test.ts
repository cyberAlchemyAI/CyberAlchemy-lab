import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {planConfiguredCalculations,CONFIGURED_CALCULATION_VERSION,type ConfiguredCalculationSelection} from '../../src/generation/configured-calculations.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {sha256,canonicalJson} from '../../src/input/source-manifest.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const bytes=(p:string)=>fs.readFileSync(p,'utf8');
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  typescript:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')),calculation_contract:bytes(path.join(pkg,'calculation-generation-contract.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json'));
const scalar={kind:'scalar',name:'UInt64'};
const input=(name:string)=>({op:'input',name});
const binary=(op:string,left:any=input('left'),right:any=input('right'))=>({op,left,right});
const kinds=['add','subtract','multiply','floor','ceil','reject','identity','constant','intermediate'];
const formula=(id:string)=>id==='identity'?input('left'):id==='constant'?{op:'literal',value:Number.MAX_SAFE_INTEGER}:id==='intermediate'?binary('subtract',binary('add'),input('right')):binary(['floor','ceil','reject'].includes(id)?'divide':id);
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-calculations-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  const feature=read(path.join(source,'specs/alpha/feature.json'));
  const contracts:any={};
  for(const id of kinds){
    const node_id='compute-'+id,edge_id=node_id+'-calculates-settle';feature.nodes.push(node_id);feature.edges.push(edge_id);
    const c={schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'FIXTURE-COMPUTE-'+id.toUpperCase(),inputs:['left','right','unused'].map(name=>({name,type:scalar})),result:scalar,division_rounding:['floor','ceil'].includes(id)?id:'reject',expression:formula(id)};
    contracts['alpha:'+node_id]=c;
    write('specs/alpha/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id,kind:'Calculation',body:{description:id,inputs:['left','right','unused'],typed_contract:c}});
    write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship:'calculates',source_node_id:node_id,target_node_id:'settle',scope:'feature'});
  }
  write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256},boundaryContract);
  const selection:ConfiguredCalculationSelection={schema_version:CONFIGURED_CALCULATION_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256,module_root:'commerce',roots:Object.keys(contracts)};
  return {temp,source,write,graph,boundary,selection,contracts,plan:()=>planConfiguredCalculations(boundary,selection,sources)};
}
function native(root:string,plan:ReturnType<typeof planConfiguredCalculations>){
  for(const a of plan.artifacts){const f=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,a.content);}
  const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'));
  const image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root}`,'--workdir',root,image,'tsc'];
  assert.equal(execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
  const compile=()=>execFileSync('docker',[...args,'--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--rootDir',path.join(root,'commerce/features'),'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});
  compile();
  const module=(id:string)=>plan.modules.find(m=>m.selector==='alpha:compute-'+id)!;
  const js=(id:string)=>path.join(root,'js',module(id).relative_path.replace('commerce/features/','').replace(/\.ts$/,'.js'));
  const load=(id:string)=>createRequire(import.meta.url)(js(id))[module(id).callable];
  return {compile,load,js,module};
}

test('Calculation planner binds checked sources, preserves defaults, scope and deterministic layout',t=>{
  const f=fixture(t),p=f.plan(),old=planCompiledProjectBuild(f.graph,'typescript');
  assert.equal(p.modules.length,9);assert.equal(p.artifacts.length,18);assert.deepEqual(f.plan(),p);
  assert.deepEqual(planConfiguredCalculations(f.boundary,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
  const other=planConfiguredCalculations(f.boundary,{...f.selection,module_root:'alternate'},sources);
  assert.deepEqual(other.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  const subset=planConfiguredCalculations(f.boundary,{...f.selection,roots:['alpha:compute-add']},sources);
  assert.deepEqual(subset.artifacts,p.artifacts.filter(a=>a.relative_path.includes('/compute-add.')),'adding unrelated roots preserves the selected module');
  assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript'),old);
  assert.equal(p.authority_effect,'none');assert.ok(Object.isFrozen(p.modules[0]!.descriptor.inputs));
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
  for(const m of p.modules){const a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;assert.equal(m.descriptor.provider.sha256,sha256(a.content));const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));}
  fs.renameSync(f.source,path.join(f.temp,'relocated'));assert.deepEqual(f.plan(),p);
  assert.throws(()=>planConfiguredCalculations(structuredClone(f.boundary),f.selection,sources),/unvalidated boundary/);
});

test('Calculation selection is closed and rejects stale, unsafe or mismatched inputs without getter calls',t=>{
  const f=fixture(t);
  for(const patch of [{schema_version:'future'},{language:'python'},{value_profile:'number'},{boundary_sha256:'stale'},{module_root:'../escape'},{module_root:'con'},{module_root:'a//b'},{roots:[]},{roots:['alpha:compute-add','alpha:compute-add']},{roots:['alpha:settle']},{roots:['alpha:missing']},{ignore_errors:true}])assert.throws(()=>planConfiguredCalculations(f.boundary,{...f.selection,...patch} as any,sources));
  for(const key of Object.keys(sources))assert.throws(()=>planConfiguredCalculations(f.boundary,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
  let reads=0;const bad={...f.selection,get module_root(){reads++;return 'commerce';}};
  assert.throws(()=>planConfiguredCalculations(f.boundary,bad,sources),/closed data/);
  const roots:any=[];Object.defineProperty(roots,0,{get(){reads++;return 'alpha:compute-add';},enumerable:true});
  assert.throws(()=>planConfiguredCalculations(f.boundary,{...f.selection,roots},sources));assert.equal(reads,0);
  const filename='specs/alpha/feature.json',feature=read(path.join(f.source,filename));feature.edges=feature.edges.filter((x:string)=>x!=='compute-add-calculates-settle');f.write(filename,feature);
  fs.unlinkSync(path.join(f.source,'specs/alpha/edges/compute-add-calculates-settle.json'));
  assert.throws(()=>loadCompiledProjectGraph(f.source),/calculates/,'old required relationship remains required');
});

test('Native exact Calculation arithmetic, rounding and intermediate bounds remain distinct',t=>{
  const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'native'),p),max=18446744073709551615n;
  const facts=(left:any,right:any=0n,unused:any=0n)=>Object.freeze({left,right,unused});
  assert.equal(n.load('identity')(facts(max)),max);assert.equal(n.load('identity')(facts(max.toString())),max);
  assert.equal(n.load('identity')(facts(-0)),0n);assert.equal(n.load('constant')(facts(0)),BigInt(Number.MAX_SAFE_INTEGER));
  for(let a=0n;a<12n;a++)for(let b=0n;b<12n;b++){
    assert.equal(n.load('add')(facts(a,b)),a+b);assert.equal(n.load('multiply')(facts(a,b)),a*b);
    if(a>=b)assert.equal(n.load('subtract')(facts(a,b)),a-b);else assert.throws(()=>n.load('subtract')(facts(a,b)),/UNDERFLOW/);
    if(b){assert.equal(n.load('floor')(facts(a,b)),a/b);assert.equal(n.load('ceil')(facts(a,b)),a/b+(a%b?1n:0n));if(a%b)assert.throws(()=>n.load('reject')(facts(a,b)),/INEXACT/);else assert.equal(n.load('reject')(facts(a,b)),a/b);}
  }
  assert.equal(n.load('ceil')(facts(max,2n)),9223372036854775808n);
  for(const id of ['floor','ceil','reject'])assert.throws(()=>n.load(id)(facts(0,0)),/DIVIDE_BY_ZERO/);
  assert.throws(()=>n.load('add')(facts(max,1)),/OVERFLOW/);assert.throws(()=>n.load('multiply')(facts(max,2)),/OVERFLOW/);
  assert.throws(()=>n.load('intermediate')(facts(max,1)),/OVERFLOW/,'intermediate overflow cannot be hidden by final subtraction');
  const fn=n.load('add'),descriptor=fn.descriptor;
  assert.ok(Object.isFrozen(fn));assert.ok(Object.isFrozen(descriptor));assert.ok(Object.isFrozen(descriptor.inputs[0].type));
  assert.deepEqual(descriptor,n.module('add').descriptor);assert.throws(()=>{(descriptor.inputs[0] as {name:string}).name='changed';});
  for(const v of [-1,max+1n,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1,'01','+1','1\n',' 1','1.0','18446744073709551616',{},null,true])assert.throws(()=>fn(facts(v)),/CALCULATION_INPUT/);
  assert.throws(()=>n.load('constant')(facts(0,0,'bad')),/CALCULATION_INPUT/,'unused declared inputs must still validate');
  let calls=0;const getter={get left(){calls++;return 1;},right:2,unused:0};assert.throws(()=>fn(getter),/CALCULATION_INPUT/);assert.equal(calls,0);
  for(const v of [null,[],{},Object.create({left:1,right:2,unused:0}),{left:1,right:2,unused:0,extra:1},{left:1,right:2,unused:0,[Symbol()]:1}])assert.throws(()=>fn(v),/CALCULATION_INPUT/);
  assert.equal(fn(Object.assign(Object.create(null),{left:'4',right:5n,unused:0})),9n);
  const hidden={left:1,right:2,unused:0};Object.defineProperty(hidden,'unused',{enumerable:false});assert.throws(()=>fn(hidden),/CALCULATION_INPUT/);
  const boxed={valueOf(){calls++;return 1;}};assert.throws(()=>fn(facts(boxed)),/CALCULATION_INPUT/);assert.equal(calls,0);
  const script=`const f=require(${JSON.stringify(n.js('add'))})[${JSON.stringify(n.module('add').callable)}];process.stdout.write(JSON.stringify({pid:process.pid,result:String(f({left:'18446744073709551614',right:1,unused:0}))}));`;
  const run=()=>JSON.parse(execFileSync(process.execPath,['-e',script],{encoding:'utf8'}));const a=run(),b=run();assert.notEqual(a.pid,b.pid);assert.equal(a.result,max.toString());assert.equal(a.result,b.result);
});

test('Independent closed-source observer rejects compiling arithmetic and effect mutations',async t=>{
  const f=fixture(t),p=f.plan(),root=path.join(f.temp,'observed'),n=native(root,p);
  const {observeCalculation}=await import('../../tools/observe-configured-calculations.mjs');
  for(const m of p.modules){const a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;assert.equal(observeCalculation(a.content,f.contracts[m.selector]).result,'pass');}
  const m=n.module('add'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
  const mutants=[a.content.replace('checked(p0+p1)','checked(p0-p1)'),a.content.replace('return v0;','return p0;'),a.content.replace('return v0;','Date.now(); return v0;'),a.content.replace('return v0;','Math.random(); return v0;'),a.content.replace('return v0;','(globalThis as any).changed=true; return v0;'),a.content.replace('return v0;','return true as unknown as bigint;')];
  for(const mutant of mutants){assert.notEqual(mutant,a.content);fs.writeFileSync(path.join(root,m.provider_path),mutant);n.compile();assert.throws(()=>observeCalculation(mutant,f.contracts[m.selector]),/CALCULATION_OBSERVER/);}
  const corruptSupport=a.content.replace('result=input;','result=0n;');assert.throws(()=>observeCalculation(corruptSupport,f.contracts[m.selector]),/support perimeter/);
});

test('Independent binding observation rejects detached callables and stale descriptor/provider bytes',async t=>{
  const f=fixture(t),p=f.plan();
  const {observeCalculationBinding}=await import('../../tools/observe-configured-calculations.mjs');
  for(const m of p.modules){
    const provider=p.artifacts.find(a=>a.relative_path===m.provider_path)!.content,wrapper=p.artifacts.find(a=>a.relative_path===m.relative_path)!.content,c=f.contracts[m.selector];
    assert.equal(observeCalculationBinding(provider,wrapper,m,c).result,'pass');
    assert.throws(()=>observeCalculationBinding(provider+'\n',wrapper,m,c),/stale descriptor or provider/);
    assert.throws(()=>observeCalculationBinding(provider,wrapper,{...m,descriptor:{...m.descriptor,descriptor_sha256:'stale'}},c),/stale descriptor/);
    assert.throws(()=>observeCalculationBinding(provider,wrapper.replace('Object.freeze(Object.assign(calculate,','Object.assign(calculate,').replace(/\)\);\n$/ ,');\n'),m,c),/unbound or changed/);
    assert.throws(()=>observeCalculationBinding(provider,wrapper,m,{...c,ontology_calculation:'FORGED-CALCULATION'}),/contract binding/);
    assert.throws(()=>observeCalculationBinding(provider,wrapper.replace('import {calculate}', 'import {calculate as detached}'),m,c),/unbound or changed/);
  }
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
