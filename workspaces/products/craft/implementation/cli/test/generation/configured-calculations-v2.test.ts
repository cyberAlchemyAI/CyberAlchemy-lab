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
import {planConfiguredCalculationsV2,CONFIGURED_CALCULATION_V2_VERSION,type ConfiguredCalculationV2Selection} from '../../src/generation/configured-calculations-v2.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {decodeExactCalculation} from '../../src/typed-backend/calculation-exact.ts';
import {decodeTypedCalculationContract} from '../../src/typed-backend/contracts.ts';
import {planConfiguredCalculations as legacyPlan,CONFIGURED_CALCULATION_VERSION as LEGACY_SELECTION} from '../../src/generation/configured-calculations.ts';
import {selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredMappings,CONFIGURED_MAPPING_VERSION} from '../../src/generation/configured-mappings.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {sha256,canonicalJson} from '../../src/input/source-manifest.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const bytes=(p:string)=>fs.readFileSync(p,'utf8');
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  typescript:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')),calculation_contract:bytes(path.join(pkg,'calculation-v2-contract.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json'));
const scalar={kind:'scalar',name:'UInt64'};
const input=(name:string)=>({op:'input',name});
const binary=(op:string,left:any=input('left'),right:any=input('right'))=>({op,left,right});
const kinds=['add','subtract','multiply','floor','ceil','reject','identity','constant','intermediate'];
const formula=(id:string)=>id==='identity'?input('left'):id==='constant'?{op:'literal',value:'18446744073709551615'}:id==='intermediate'?binary('subtract',binary('add'),input('right')):binary(['floor','ceil','reject'].includes(id)?'divide':id);
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-calculations-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  const feature=read(path.join(source,'specs/alpha/feature.json'));
  const contracts:any={};
  for(const id of kinds){
    const node_id='compute-'+id,edge_id=node_id+'-calculates-settle';feature.nodes.push(node_id);
    const c={schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'FIXTURE-COMPUTE-'+id.toUpperCase(),inputs:['left','right','unused'].map(name=>({name,type:scalar})),result:scalar,division_rounding:['floor','ceil'].includes(id)?id:'reject',expression:formula(id)};
    contracts['alpha:'+node_id]=c;
    write('specs/alpha/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id,kind:'Calculation',body:{description:id,inputs:['left','right','unused'],typed_contract:c}});
  }
  write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256},boundaryContract);
  const selection:ConfiguredCalculationV2Selection={schema_version:CONFIGURED_CALCULATION_V2_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256,module_root:'commerce',roots:Object.keys(contracts)};
  return {temp,source,write,graph,boundary,selection,contracts,plan:()=>planConfiguredCalculationsV2(boundary,selection,sources)};
}
function native(root:string,plan:ReturnType<typeof planConfiguredCalculationsV2>){
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
  const f=fixture(t),p=f.plan();
  assert.equal(p.modules.length,9);assert.equal(p.artifacts.length,18);assert.deepEqual(f.plan(),p);
  assert.deepEqual(planConfiguredCalculationsV2(f.boundary,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
  const other=planConfiguredCalculationsV2(f.boundary,{...f.selection,module_root:'alternate'},sources);
  assert.deepEqual(other.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  const subset=planConfiguredCalculationsV2(f.boundary,{...f.selection,roots:['alpha:compute-add']},sources);
  assert.deepEqual(subset.artifacts,p.artifacts.filter(a=>a.relative_path.includes('/compute-add.')),'adding unrelated roots preserves the selected module');
  assert.throws(()=>planCompiledProjectBuild(f.graph,'typescript'),/Calculation v2 requires/);
  assert.equal(p.authority_effect,'none');assert.ok(Object.isFrozen(p.modules[0]!.descriptor.inputs));
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
  for(const m of p.modules){const a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;assert.equal(m.descriptor.provider.sha256,sha256(a.content));const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));}
  fs.renameSync(f.source,path.join(f.temp,'relocated'));assert.deepEqual(f.plan(),p);
  assert.throws(()=>planConfiguredCalculationsV2(structuredClone(f.boundary),f.selection,sources),/unvalidated boundary/);
});

test('Calculation selection is closed and rejects stale, unsafe or mismatched inputs without getter calls',t=>{
  const f=fixture(t);
  for(const patch of [{schema_version:'future'},{language:'python'},{value_profile:'number'},{boundary_sha256:'stale'},{module_root:'../escape'},{module_root:'con'},{module_root:'a//b'},{roots:[]},{roots:['alpha:compute-add','alpha:compute-add']},{roots:['alpha:settle']},{roots:['alpha:missing']},{ignore_errors:true}])assert.throws(()=>planConfiguredCalculationsV2(f.boundary,{...f.selection,...patch} as any,sources));
  for(const key of Object.keys(sources))assert.throws(()=>planConfiguredCalculationsV2(f.boundary,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
  let reads=0;const bad={...f.selection,get module_root(){reads++;return 'commerce';}};
  assert.throws(()=>planConfiguredCalculationsV2(f.boundary,bad,sources),/closed data/);
  const roots:any=[];Object.defineProperty(roots,0,{get(){reads++;return 'alpha:compute-add';},enumerable:true});
  assert.throws(()=>planConfiguredCalculationsV2(f.boundary,{...f.selection,roots},sources));assert.equal(reads,0);
});

test('Native exact Calculation arithmetic, rounding and intermediate bounds remain distinct',t=>{
  const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'native'),p),max=18446744073709551615n;
  const facts=(left:any,right:any=0n,unused:any=0n)=>Object.freeze({left,right,unused});
  assert.equal(n.load('identity')(facts(max)),max);assert.equal(n.load('identity')(facts(max.toString())),max);
  assert.equal(n.load('identity')(facts(-0)),0n);assert.equal(n.load('constant')(facts(0)),max);
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
  const {observeCalculationV2}=await import('../../tools/observe-configured-calculations-v2.mjs');
  for(const m of p.modules){const a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;assert.equal(observeCalculationV2(a.content,f.contracts[m.selector]).result,'pass');}
  const m=n.module('add'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
  const mutants=[a.content.replace('checked(p0+p1)','checked(p0-p1)'),a.content.replace('return v0;','return p0;'),a.content.replace('return v0;','Date.now(); return v0;'),a.content.replace('return v0;','Math.random(); return v0;'),a.content.replace('return v0;','(globalThis as any).changed=true; return v0;'),a.content.replace('return v0;','return true as unknown as bigint;')];
  for(const mutant of mutants){assert.notEqual(mutant,a.content);fs.writeFileSync(path.join(root,m.provider_path),mutant);n.compile();assert.throws(()=>observeCalculationV2(mutant,f.contracts[m.selector]),/CALCULATION_OBSERVER/);}
  const corruptSupport=a.content.replace('result=input;','result=0n;');assert.throws(()=>observeCalculationV2(corruptSupport,f.contracts[m.selector]),/support perimeter/);
});

test('Independent binding observation rejects detached callables and stale descriptor/provider bytes',async t=>{
  const f=fixture(t),p=f.plan();
  const {observeCalculationV2Binding}=await import('../../tools/observe-configured-calculations-v2.mjs');
  for(const m of p.modules){
    const provider=p.artifacts.find(a=>a.relative_path===m.provider_path)!.content,wrapper=p.artifacts.find(a=>a.relative_path===m.relative_path)!.content,c=f.contracts[m.selector];
    assert.equal(observeCalculationV2Binding(provider,wrapper,m,c).result,'pass');
    assert.throws(()=>observeCalculationV2Binding(provider+'\n',wrapper,m,c),/stale descriptor or provider/);
    assert.throws(()=>observeCalculationV2Binding(provider,wrapper,{...m,descriptor:{...m.descriptor,descriptor_sha256:'stale'}},c),/stale descriptor/);
    assert.throws(()=>observeCalculationV2Binding(provider,wrapper.replace('Object.freeze(Object.assign(calculate,','Object.assign(calculate,').replace(/\)\);\n$/ ,');\n'),m,c),/unbound or changed/);
    assert.throws(()=>observeCalculationV2Binding(provider,wrapper,m,{...c,ontology_calculation:'FORGED-CALCULATION'}),/contract binding/);
    assert.throws(()=>observeCalculationV2Binding(provider,wrapper.replace('import {calculate}', 'import {calculate as detached}'),m,c),/unbound or changed/);
  }
});

test('v2 admits standalone constants, keeps lawful consumers, and preserves v1 rejection',t=>{
  const f=fixture(t),p=f.plan();
  assert.equal(f.graph.relationships.filter(e=>e.relationship==='calculates'&&e.source.node_id.startsWith('compute-')).length,0);
  const file='specs/alpha/nodes/compute-constant.json',node=read(path.join(f.source,file));
  node.body.inputs=[];node.body.typed_contract.inputs=[];f.write(file,node);
  const graph=loadCompiledProjectGraph(f.source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256},boundaryContract);
  const constant=planConfiguredCalculationsV2(boundary,{...f.selection,boundary_sha256:boundary.boundary_sha256,roots:['alpha:compute-constant']},sources);
  const n=native(path.join(f.temp,'constant'),constant);assert.equal(n.load('constant')({}),18446744073709551615n);
  assert.throws(()=>n.load('constant')({invented:1}),/CALCULATION_INPUT/);
  const feature=read(path.join(f.source,'specs/alpha/feature.json'));
  feature.edges.push('compute-add-calculates-settle');f.write('specs/alpha/feature.json',feature);
  const edge={schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:'compute-add-calculates-settle',relationship:'calculates',source_node_id:'compute-add',target_node_id:'settle',scope:'feature'};
  f.write('specs/alpha/edges/'+edge.edge_id+'.json',edge);assert.doesNotThrow(()=>loadCompiledProjectGraph(f.source));
  f.write('specs/alpha/edges/'+edge.edge_id+'.json',{...edge,target_node_id:'compute-subtract'});
  assert.throws(()=>loadCompiledProjectGraph(f.source),'canonical endpoint rules still apply');
  f.write('specs/alpha/edges/'+edge.edge_id+'.json',edge);
  const legacy=read(path.join(f.source,'specs/alpha/nodes/compute-identity.json'));
  legacy.body.typed_contract.schema_version='domainspec.typed-calculation/v1';
  f.write('specs/alpha/nodes/compute-identity.json',legacy);
  assert.throws(()=>loadCompiledProjectGraph(f.source),/calculates/);
  assert.throws(()=>decodeTypedCalculationContract(f.contracts['alpha:compute-add']),/unsupported typed Calculation schema/);
  assert.throws(()=>legacyPlan(f.boundary,{...f.selection,schema_version:LEGACY_SELECTION},{...sources,calculation_contract:bytes(path.join(pkg,'calculation-generation-contract.json'))}),/unsupported typed Calculation schema/);
  for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planInstantiation(selectCompiledProjectNode(f.graph,'alpha:compute-add'),language),/Calculation v2 requires/);
});

test('v2 source closes literal syntax, inputs, expression bounds and hostile data',t=>{
  const f=fixture(t),original=f.contracts['alpha:compute-constant'];
  assert.equal(decodeExactCalculation(original).expression.op,'literal');
  for(const value of [0,1,Number.MAX_SAFE_INTEGER,18446744073709551615n,'','01','-1','+1','1.0','1e2',' 1','1\n','18446744073709551616','9'.repeat(100),null,{}]){
    assert.throws(()=>decodeExactCalculation({...original,expression:{op:'literal',value}}));
  }
  for(const value of ['0','9007199254740993','18446744073709551615'])assert.doesNotThrow(()=>decodeExactCalculation({...original,expression:{op:'literal',value}}));
  for(const expression of [{op:'input',name:'undeclared'},{op:'query',name:'left'},{op:'literal',value:'1',coerce:true},binary('add',input('left'),{op:'literal',value:'-1'})])assert.throws(()=>decodeExactCalculation({...original,expression}));
  let deep:any={op:'literal',value:'0'};for(let i=0;i<33;i++)deep=binary('add',deep,{op:'literal',value:'0'});
  assert.throws(()=>decodeExactCalculation({...original,expression:deep}),/bounds/);
  let wide:any={op:'literal',value:'0'};for(let i=0;i<12;i++)wide=binary('add',wide,wide);
  assert.throws(()=>decodeExactCalculation({...original,expression:wide}),/bounds/);
  for(const patch of [{inputs:[original.inputs[0],original.inputs[0]]},{inputs:[{name:'left',type:{kind:'scalar',name:'Text'}}]},{result:{kind:'scalar',name:'Text'}},{division_rounding:'nearest'},{schema_version:'domainspec.typed-calculation/v3'}])assert.throws(()=>decodeExactCalculation({...original,...patch}));
  let reads=0;const accessor={...original,get expression(){reads++;return {op:'literal',value:'1'};}};
  assert.throws(()=>decodeExactCalculation(accessor));assert.equal(reads,0);
  const sparse:any=[];sparse.length=1;assert.throws(()=>decodeExactCalculation({...original,inputs:sparse}));
  const cyclic:any={op:'add',right:{op:'literal',value:'0'}};cyclic.left=cyclic;assert.throws(()=>decodeExactCalculation({...original,expression:cyclic}),/bounds/);
  const filename='specs/alpha/nodes/compute-constant.json',node=read(path.join(f.source,filename));
  f.write(filename,{...node,body:{...node.body,inputs:['not_declared']}});assert.throws(()=>loadCompiledProjectGraph(f.source),/exactly match/);
  f.write(filename,{...node,body:{...node.body,semantics:{}}});assert.throws(()=>loadCompiledProjectGraph(f.source));
});

test('v2 cannot leak into legacy execution or formalization',t=>{
  const f=fixture(t);
  assert.throws(()=>createMetaTypeFormalizationProjection(f.graph),(error:any)=>error.code==='MTCLI_CALCULATION_FORMALIZATION_UNSUPPORTED');
  assert.throws(()=>runInMemoryProject(f.source,{schema_version:'domainspec.runtime-invocation/v1',invocation_id:'exact-calculation',provider:'in-memory-v1',steps:[{step_id:'calculate',selector:'alpha:compute-add',input:{inputs:{left:1,right:2,unused:0}}}]}),(error:any)=>error.code==='MTCLI_CALCULATION_PROFILE_REQUIRED');
});

test('full-width authored expression operands retain exact identity and intermediate failure',async t=>{
  const f=fixture(t),cases:any={
    identity:{op:'literal',value:'9007199254740993'},
    add:binary('add',{op:'literal',value:'18446744073709551614'},{op:'literal',value:'1'}),
    subtract:binary('subtract',{op:'literal',value:'18446744073709551615'},{op:'literal',value:'9007199254740993'}),
    multiply:binary('multiply',{op:'literal',value:'18446744073709551615'},{op:'literal',value:'2'}),
    floor:binary('divide',{op:'literal',value:'18446744073709551615'},{op:'literal',value:'2'}),
    ceil:binary('divide',{op:'literal',value:'18446744073709551615'},{op:'literal',value:'2'}),
    reject:binary('divide',{op:'literal',value:'18446744073709551615'},{op:'literal',value:'2'}),
    intermediate:binary('subtract',binary('add',{op:'literal',value:'18446744073709551615'},{op:'literal',value:'1'}),{op:'literal',value:'1'})
  };
  for(const [id,expression]of Object.entries(cases)){
    const file='specs/alpha/nodes/compute-'+id+'.json',node=read(path.join(f.source,file));node.body.typed_contract.expression=expression;f.write(file,node);f.contracts['alpha:compute-'+id]=node.body.typed_contract;
  }
  const graph=loadCompiledProjectGraph(f.source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256},boundaryContract);
  const p=planConfiguredCalculationsV2(boundary,{...f.selection,boundary_sha256:boundary.boundary_sha256},sources),n=native(path.join(f.temp,'literal-operands'),p),facts={left:0,right:0,unused:0};
  assert.equal(n.load('identity')(facts),9007199254740993n);assert.equal(n.load('add')(facts),18446744073709551615n);
  assert.equal(n.load('subtract')(facts),18446744073709551615n-9007199254740993n);
  assert.equal(n.load('floor')(facts),9223372036854775807n);assert.equal(n.load('ceil')(facts),9223372036854775808n);
  assert.throws(()=>n.load('reject')(facts),/INEXACT/);for(const id of ['multiply','intermediate'])assert.throws(()=>n.load(id)(facts),/OVERFLOW/);
  const {observeCalculationV2}=await import('../../tools/observe-configured-calculations-v2.mjs');
  for(const m of p.modules)assert.equal(observeCalculationV2(p.artifacts.find(a=>a.relative_path===m.provider_path)!.content,f.contracts[m.selector]).result,'pass');
  const m=n.module('identity'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!,mutant=a.content.replace('9007199254740993n','9007199254740992n');
  fs.writeFileSync(path.join(f.temp,'literal-operands',m.provider_path),mutant);n.compile();assert.throws(()=>observeCalculationV2(mutant,f.contracts[m.selector]),/expression meaning/);
});

test('standalone Calculation feeds Mapping through explicit values without a fabricated consumer',t=>{
  const f=fixture(t),feature=read(path.join(f.source,'specs/alpha/feature.json'));
  const record={schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-CALCULATION-SUMMARY',properties:[{name:'amount',ontology_property:'FIXTURE-CALCULATION-SUMMARY#amount',type:scalar,identity:true,cardinality:'one',meaning:'Computed amount'}]};
  const mapping={schema_version:'domainspec.typed-mapping/v2',ontology_mapping:'FIXTURE-EXPLICIT-SUMMARY',inputs:[{name:'order_total',type:scalar}],target:'alpha:calculation-summary',fields:[{target:'amount',value:{op:'path',root:'order_total',properties:[]},default:null}],total:true};
  for(const [id,kind,body]of [['calculation-summary','Entity',{fields:['amount'],typed_contract:record}],['map-calculation-summary','Mapping',{target:mapping.target,typed_contract:mapping}]] as const){feature.nodes.push(id);f.write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});}
  feature.edges.push('summary-mapping');f.write('specs/alpha/edges/summary-mapping.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:'summary-mapping',relationship:'maps',source_node_id:'map-calculation-summary',target_node_id:'calculation-summary',scope:'feature'});f.write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(f.source),graph_sha256=createCompiledProjectCertificate(graph).graph_sha256;
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256},boundaryContract);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256,roots:['alpha:calculation-summary'],bindings:[]},bytes(path.join(project,'development/reconciliation-v1/contracts/exact-field-and-reference-model.json')));
  const calculations=planConfiguredCalculationsV2(boundary,{...f.selection,boundary_sha256:boundary.boundary_sha256,roots:['alpha:compute-add']},sources);
  const {calculation_contract,...shared}=sources;
  const mappings=planConfiguredMappings(boundary,fields,{schema_version:CONFIGURED_MAPPING_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,module_root:'commerce',roots:['alpha:map-calculation-summary']},{...shared,mapping_contract:bytes(path.join(pkg,'mapping-generation-contract.json'))});
  const combined={...calculations,artifacts:[...calculations.artifacts,...mappings.artifacts]},root=path.join(f.temp,'explicit-flow'),n=native(root,combined);
  const m=mappings.modules[0]!,map=createRequire(import.meta.url)(path.join(root,'js',m.relative_path.replace('commerce/features/','').replace(/\.ts$/,'.js')))[m.callable];
  let calls=0;const calculate=(left:bigint,right:bigint)=>{calls++;return n.load('add')({left,right,unused:0});};
  const total=calculate(9007199254740993n,1n);
  assert.deepEqual(map({order_total:total}),{amount:9007199254740994n});assert.deepEqual(map({order_total:4n}),{amount:4n});assert.equal(calls,1);
  assert.equal(graph.relationships.filter(e=>e.source.node_id==='compute-add').length,0);
  const provider=mappings.artifacts.find(a=>a.relative_path===m.provider_path)!.content;assert.doesNotMatch(provider,/compute-add|calculate\(/);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
