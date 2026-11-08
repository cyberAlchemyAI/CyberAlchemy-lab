import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {decodePublicMapping,checkPublicMapping,PUBLIC_MAPPING_VERSION,PUBLIC_MAPPING_CONTRACT_SHA256} from '../../src/typed-backend/mapping-public.ts';
import {decodeNamedInterface} from '../../src/typed-backend/interface.ts';
import {loadCompiledProjectGraph,selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {compilePublicMapping,assertCheckedPublicMapping} from '../../src/input/compiled-public-mapping.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {nativeProcessFailure,readNativeObserver} from '../helpers/native-process.ts';

const project=path.resolve(import.meta.dirname,'../../../..');
const read=(p:string)=>fs.readFileSync(path.join(project,'development/reconciliation-v1',p),'utf8');
const definition=read('profile-compiler-reconciliation/public-mapping-contract.json');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(selector='commerce:order'):any=>({kind:'named',selector});
const ref=(contract_id='response',interface_selector='commerce:api'):any=>({kind:'contract',interface_selector,contract_id});
const local=(contract_id='response'):any=>({kind:'contract',contract_id});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties});
const use=(operation_id='find',side='result'):any=>({interface_selector:'commerce:api',operation_id,side});
const field=(name:string,type:any=scalar()):any=>({name,ontology_field:'TEST-PUBLIC#'+name,meaning:name,type});
function api():any{return {schema_version:'domainspec.typed-interface/v1',ontology_interface:'TEST-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'backward',direction:'consumer-to-provider',provider_version:'1.0.0'},contracts:[{contract_id:'response',ontology_contract:'TEST-RESPONSE',fields:[field('id'),field('total',scalar('UInt64'))]},{contract_id:'shadow',ontology_contract:'TEST-SHADOW',fields:[field('id'),field('total',scalar('UInt64'))]},{contract_id:'empty',ontology_contract:'TEST-EMPTY',fields:[]}],operations:[{operation_id:'find',operation_ref:'commerce:find',request:scalar(),result:local()},{operation_id:'again',operation_ref:'commerce:again',request:scalar(),result:local()}]};}
function entity():any{return {selector:'commerce:order',kind:'Entity',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-ORDER',properties:[{name:'id',ontology_property:'TEST-ORDER#id',type:scalar(),cardinality:'one',identity:true,meaning:'identity'}]}};}
function mapping():any{return {schema_version:PUBLIC_MAPPING_VERSION,ontology_mapping:'TEST-SUMMARY',inputs:[{name:'order',type:named(),use:null},{name:'total',type:scalar('UInt64'),use:null}],target:ref(),target_use:use(),fields:[{target:'id',value:at('order','TEST-ORDER#id'),default:null},{target:'total',value:at('total'),default:null}],total:true};}
const check=(m:any=mapping(),a:any=api(),declarations:any[]=[entity()])=>checkPublicMapping(decodePublicMapping(m),declarations,[{selector:'commerce:api',contract:decodeNamedInterface(a)}]);
function fixture(t:any,m=mapping(),a=api()){
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'ds-public-mapping-'));t.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
 const nodes:string[]=[],edges:string[]=[];
 const write=(p:string,v:any)=>{const file=path.join(folder,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
 const edge=(id:string,relationship:string,from:string,to:string)=>{if(!edges.includes(id))edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id:id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 node('order','Entity',{fields:['id'],typed_contract:entity().contract});
 node('api','Interface',{typed_contract:a});
 for(const id of ['find','again']){node(id,'Query',{reads:['order']});edge('api-'+id,'exposes','api',id);}
 node('summary','Mapping',{target:m.target.kind==='named'?m.target.selector:m.target.interface_selector,typed_contract:m});edge('summary-target','maps','summary',m.target.kind==='named'?'order':'api');
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'public-mapping',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
 const compile=()=>{const graph=loadCompiledProjectGraph(folder),graph_sha256=createCompiledProjectCertificate(graph).graph_sha256;
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256},read('contracts/composition-boundary.json'));
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256,roots:['commerce:order'],bindings:[]},read('contracts/exact-field-and-reference-model.json'));
  return {graph,boundary,fields,check:(d=definition)=>compilePublicMapping(graph,boundary,fields,'commerce:summary',d)};};
 return {folder,nodes,edges,node,edge,write,save,compile};
}

import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {planConfiguredPublicBoundaries,CONFIGURED_PUBLIC_BOUNDARIES_VERSION,PUBLIC_BOUNDARY_GENERATION_SHA256} from '../../src/generation/configured-public-boundaries.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
const sources=()=>{
 const config=JSON.parse(read('profile-compiler-reconciliation/configuration.json'));
 return {configuration:read('profile-compiler-reconciliation/configuration.json'),base:fs.readFileSync(path.join(project,config.sources.base.path),'utf8'),typescript:fs.readFileSync(path.join(project,config.sources.typescript.path),'utf8'),generation_contract:read('profile-compiler-reconciliation/public-boundary-generation-contract.json'),public_mapping_contract:definition,interface_contract:read('profile-compiler-reconciliation/named-interface-contract.json')};
};
const selection=(roots=['commerce:summary']):any=>({schema_version:CONFIGURED_PUBLIC_BOUNDARIES_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,module_root:'generated',roots});
const plan=(c:ReturnType<ReturnType<typeof fixture>['compile']>,s=selection(),defs=sources())=>planConfiguredPublicBoundaries(c.graph,c.boundary,c.fields,s,defs);
function native(t:any,p:ReturnType<typeof plan>,extra:Record<string,string>={}){
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'ds-public-boundaries-native-'));t.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
 const artifacts=[...p.artifacts,...Object.entries(extra).map(([relative_path,content])=>({relative_path,content}))];
 for(const a of artifacts){const file=path.join(folder,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const image=nativeToolchainImage();
 try{execFileSync('docker',['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+folder+',target='+folder,'--workdir',folder,image,'tsc','--ignoreConfig','--strict','--declaration','--target','ES2022','--module','commonjs','--rootDir',folder,'--outDir',path.join(folder,'js'),...artifacts.map(a=>a.relative_path)],{stdio:'pipe'});}catch(error){throw nativeProcessFailure('public-boundary TypeScript compiler',error);}
 const require=createRequire(import.meta.url),load=(p:string):any=>require(path.join(folder,'js',p.replace(/\.ts$/,'.js')));
 return {folder,load};
}
test('configured boundaries bind definitions and qualified imports without changing the graph',t=>{
 const f=fixture(t),c=f.compile(),before=canonicalJson(c.graph),s=selection(),p=plan(c,s);
 assert.equal(sha256(sources().generation_contract),PUBLIC_BOUNDARY_GENERATION_SHA256);assert.deepEqual(plan(c),p);assert.equal(canonicalJson(c.graph),before);
 assert.equal(Object.isFrozen(s),false);assert.deepEqual(p.interfaces.map(i=>i.selector),['commerce:api']);assert.deepEqual(p.modules.map(m=>m.selector),['commerce:summary']);
 assert.equal(p.modules[0]!.descriptor.imports[0]!.path,'../interfaces/api.js');assert.equal(p.artifacts.length,3);assert.equal(p.authority_effect,'none');
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
 fs.renameSync(f.folder,f.folder+'-moved');t.after(()=>fs.rmSync(f.folder+'-moved',{recursive:true,force:true}));assert.deepEqual(plan(c),p);
 const relocated=plan(c,{...s,module_root:'other'});assert.deepEqual(relocated.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
});
test('native public Mapping receives computed values explicitly and preserves exact output',t=>{
 const p=plan(fixture(t).compile()),n=native(t,p),module=p.modules[0]!,mapping=n.load(module.relative_path)[module.callable],api=n.load(p.interfaces[0]!.relative_path);
 const input={order:{id:'order-1'},total:'18446744073709551615'},out=mapping(input);
 assert.deepEqual(out,{id:'order-1',total:18446744073709551615n});assert.ok(Object.isFrozen(out));input.order.id='changed';assert.equal(out.id,'order-1');
 assert.equal(api.publicContracts.response.key(out),api.publicContracts.response.key(api.publicContracts.response.normalize(out)));
 assert.equal(mapping.descriptor.effect_contract,'pure-explicit-field-projection');
 for(const bad of [{order:{id:'x'},total:-1},{order:{id:'x'},total:9007199254740992},{order:{id:'x'},total:'18446744073709551616'},{order:{id:'x'},total:'1',hidden:1}])assert.throws(()=>mapping(bad));
 let calls=0;assert.throws(()=>mapping({get order(){calls++;return {id:'x'};},total:'1'}));assert.equal(calls,0);
});
test('native request/result signatures and public projection types compile for a real consumer',t=>{
 const p=plan(fixture(t).compile());
 native(t,p,{'consumer.ts':`import {mappingSummary} from './generated/features/commerce/src/application/mappings/summary.js';
import type {Interface,PublicContracts} from './generated/features/commerce/src/application/interfaces/api.js';
const result:PublicContracts['response']=mappingSummary({order:{id:'x'},total:'18446744073709551615'});
const api:Interface={find:async request=>result,again:async request=>result};
const promise:Promise<PublicContracts['response']>=api.find('x');
// @ts-expect-error result amount is bigint, not number
const amount:number=result.total;
// @ts-expect-error mapping needs the explicit computed input
mappingSummary({order:{id:'x'}});
// @ts-expect-error request is String
api.find(1);
// @ts-expect-error result cannot be mutated
result.id='changed';
// @ts-expect-error no implicit transport member
api.listen();
`});
});
test('native partial and empty public targets stay projections rather than filled full contracts',t=>{
 const m=mapping();m.fields=[m.fields[0]];m.total=false;
 const p=plan(fixture(t,m).compile()),n=native(t,p),mod=p.modules[0]!;
 assert.deepEqual(n.load(mod.relative_path)[mod.callable]({order:{id:'x'},total:'1'}),{id:'x'});
 const empty=mapping();empty.target=ref('empty');empty.target_use=null;empty.fields=[];empty.inputs=[];
 const ep=plan(fixture(t,empty).compile()),en=native(t,ep);assert.deepEqual(en.load(ep.modules[0]!.relative_path)[ep.modules[0]!.callable]({}),{});
});
test('native inbound public values project an Entity without factory or invariant execution',t=>{
 const m=mapping();m.inputs=[{name:'request',type:ref(),use:use()}];m.target=named();m.target_use=null;m.fields=[{target:'id',value:at('request','TEST-PUBLIC#id'),default:null}];
 const p=plan(fixture(t,m).compile()),n=native(t,p),mod=p.modules[0]!,api=n.load(p.interfaces[0]!.relative_path);
 const request=api.publicContracts.response.normalize({id:'order-1',total:'9007199254740993'});
 assert.deepEqual(n.load(mod.relative_path)[mod.callable]({request}),{id:'order-1'});
});
test('closed selections, checked snapshots, profiles and stale graph evidence cannot be bypassed',t=>{
 const c=fixture(t).compile();
 for(const mutate of [(s:any)=>s.language='python',(s:any)=>s.extra=true,(s:any)=>s.roots=[],(s:any)=>s.roots.push(s.roots[0]),(s:any)=>s.roots=['commerce:order'],(s:any)=>s.module_root='../escape',(s:any)=>s.module_root='con']){const s=selection();mutate(s);assert.throws(()=>plan(c,s));}
 for(const key of Object.keys(sources())){const s:any=sources();s[key]+=' ';assert.throws(()=>plan(c,selection(),s),/source drift/);}
 assert.throws(()=>plan({...c,graph:structuredClone(c.graph)}));assert.throws(()=>plan({...c,fields:structuredClone(c.fields)}));assert.throws(()=>plan({...c,boundary:structuredClone(c.boundary)}));
 let reads=0;const s=selection();Object.defineProperty(s,'roots',{enumerable:true,get(){reads++;return [];}});assert.throws(()=>plan(c,s));assert.equal(reads,0);
 const interfaces=plan(c,selection(['commerce:api']));assert.equal(interfaces.modules.length,0);assert.equal(interfaces.artifacts.length,1);
});
function richFixture(t:any){
 const a=api(),m=mapping();a.contracts.push({contract_id:'detail',ontology_contract:'TEST-DETAIL',fields:[field('amount',scalar('UInt64'))]});
 const extras=[field('memo',{kind:'optional',element:scalar()}),field('tags',{kind:'set',element:scalar()}),field('lines',{kind:'list',element:scalar('UInt64')}),field('choice',{kind:'sum',variants:[{name:'None',ontology_variant:'TEST-CHOICE#None',payload:null},{name:'Some',ontology_variant:'TEST-CHOICE#Some',payload:local('detail')}]}),field('empty',local('empty')),field('money',named('commerce:money')),field('status',named('commerce:status'))];
 a.contracts[0].fields.push(...extras);m.inputs.push({name:'public_value',type:ref(),use:null});m.fields.push(...extras.map(f=>({target:f.name,value:at('public_value',f.ontology_field),default:null})));
 const f=fixture(t,m,a),order=entity().contract;order.properties.push({name:'money',ontology_property:'TEST-ORDER#money',type:named('commerce:money'),cardinality:'one',identity:false,meaning:'money value'},{name:'status',ontology_property:'TEST-ORDER#status',type:named('commerce:status'),cardinality:'one',identity:false,meaning:'status'});
 f.node('order','Entity',{fields:order.properties.map((p:any)=>p.name),typed_contract:order});
 f.node('valid-money','Rule',{predicate:'fixture invariant reference; Mapping does not execute it'});
 f.node('money','Value Object',{fields:['amount'],invariant_refs:['commerce:valid-money'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-MONEY',properties:[{name:'amount',ontology_property:'TEST-MONEY#amount',type:scalar('UInt64'),cardinality:'one',identity:false,meaning:'exact amount'}]}});
 f.node('status','Enum',{values:['Ready','Waiting'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'Ready',ontology_variant:'TEST-STATUS#Ready',payload:null},{name:'Waiting',ontology_variant:'TEST-STATUS#Waiting',payload:scalar('UInt64')}]}});f.save();return {f,a,m};
}
test('native public values compose shared domain values, nested contracts, sums and distinct collection semantics',t=>{
 const {f}=richFixture(t),p=plan(f.compile()),n=native(t,p),api=n.load(p.interfaces[0]!.relative_path),map=n.load(p.modules[0]!.relative_path)[p.modules[0]!.callable];
 const raw={id:'public',total:'2',tags:['z','a'],lines:['2','2','1'],choice:{variant:'Some',payload:{amount:'18446744073709551615'}},empty:{},money:{amount:'9007199254740993'},status:{variant:'Waiting',payload:'3'}};
 const public_value=api.publicContracts.response.normalize(raw),order={id:'domain',money:{amount:'4'},status:{variant:'Ready'}},out=map({order,total:'18446744073709551615',public_value});
 assert.equal(out.id,'domain');assert.equal(out.total,18446744073709551615n);assert.equal(out.memo,null);assert.deepEqual(out.tags,['a','z']);assert.deepEqual(out.lines,[2n,2n,1n]);assert.equal(out.choice.payload.amount,18446744073709551615n);assert.equal(out.money.amount,9007199254740993n);assert.equal(out.status.payload,3n);assert.deepEqual(out.empty,{});assert.ok(Object.isFrozen(out.choice.payload));assert.notEqual(out.money,public_value.money);
 for(const change of [(r:any)=>r.tags=['a','a'],(r:any)=>r.lines=[1,,2],(r:any)=>r.choice={variant:'None',payload:1},(r:any)=>r.money.amount='18446744073709551616',(r:any)=>r.empty.extra=true]){const r=structuredClone(raw);change(r);assert.throws(()=>map({order,total:'1',public_value:r}));}
 const again=map({order,total:'1',public_value:{...raw,lines:['1','2','2']}});assert.deepEqual(again.lines,[1n,2n,2n]);
});
test('native optional public inputs, collection projections, to_set and defaults retain their explicit meaning',t=>{
 const a=api(),m=mapping();a.contracts[0].fields=[field('id'),field('total',scalar('UInt64')),field('ids',{kind:'set',element:scalar()})];
 m.inputs.push({name:'rows',type:{kind:'list',element:ref('shadow')},use:null});m.inputs[1].type={kind:'optional',element:scalar('UInt64')};m.fields[1].default={op:'literal',type:'UInt64',value:'18446744073709551615'};m.fields.push({target:'ids',value:{op:'to_set',value:at('rows','TEST-PUBLIC#id')},default:null});
 m.inputs.push({name:'maybe',type:{kind:'optional',element:ref('empty')},use:null});
 const p=plan(fixture(t,m,a).compile()),n=native(t,p),map=n.load(p.modules[0]!.relative_path)[p.modules[0]!.callable];
 assert.deepEqual(map({order:{id:'x'},total:null,rows:[{id:'b',total:1n},{id:'a',total:2n},{id:'b',total:3n}],maybe:null}),{id:'x',total:18446744073709551615n,ids:['a','b']});
 assert.throws(()=>map({order:{id:'x'},total:null,rows:[],maybe:{unexpected:1}}));
});
function observe(t:any,p:ReturnType<typeof plan>,changes:Record<string,string>={}){
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'ds-public-observer-'));t.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
 for(const a of p.artifacts){const file=path.join(folder,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,changes[a.relative_path]??a.content);}
 fs.writeFileSync(path.join(folder,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'commonjs',strict:true},include:['generated/**/*.ts']}));
 const expected={provider_path:'generated/features/commerce/src/application/mappings/summary.provider.ts',facade_path:'generated/features/commerce/src/application/mappings/summary.ts',provider_import:'./summary.provider.js',callable:'mappingSummary',interfaces:[{path:'generated/features/commerce/src/application/interfaces/api.ts',members:['find','again'],contracts:['empty','response','shadow']}],imports:[{alias:'Public0',selector:'commerce:api',path:'../interfaces/api.js'}],inputs:[{name:'order',normalizer:'R1Value'},{name:'total',normalizer:'ruleUInt64'}],fields:[{name:'id',normalizer:'ruleString',expression:'p0["id"]'},{name:'total',normalizer:'ruleUInt64',expression:'p1'}]};
 fs.writeFileSync(path.join(folder,'expected.json'),JSON.stringify(expected));
 const observer=path.join(project,'impl/cli/tools/observe-configured-public-boundaries.mjs');
 return readNativeObserver(()=>execFileSync('docker',['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+folder+',target='+folder+',readonly','--mount','type=bind,source='+observer+',target=/observer.mjs,readonly',nativeToolchainImage(),'node','/observer.mjs',folder,path.join(folder,'expected.json')],{encoding:'utf8'}));
}
test('independent native observer rejects import, normalization, field and effect mutations',t=>{
 const p=plan(fixture(t).compile()),provider=p.modules[0]!.provider_path,source=p.artifacts.find(a=>a.relative_path===provider)!.content;
 assert.deepEqual(observe(t,p),{result:'pass',interfaces:1,fields:2});
 const mutations=[source.replace('ruleUInt64.normalize(p1)','ruleUInt64.normalize(0n)'),source.replace('ruleString.normalize(p0["id"])','ruleString.normalize("wrong")'),source.replace('const p1=ruleUInt64.normalize(d["total"]!.value);','const p1=0n;'),source.replace('return Object.freeze({["id"]:v0,["total"]:v1});','return {["id"]:v0,["total"]:v1};'),source.replace('../interfaces/api.js','../interfaces/other.js'),source.replace('if(Public0.descriptor.selector','if(false&&Public0.descriptor.selector'),source+'\nfetch("/hidden");\n'];
 const reasons=['exact field projection','exact field projection','input normalization','owned exact result','qualified import','qualified identity pin','hidden effect'];
 for(const [index,changed] of mutations.entries()){assert.notEqual(changed,source);assert.deepEqual(observe(t,p,{[provider]:changed}),{result:'fail',error:reasons[index]},'observer mutation '+index);}
 const apiPath=p.interfaces[0]!.relative_path,apiSource=p.artifacts.find(a=>a.relative_path===apiPath)!.content,wrongRequest=apiSource.replace('"find":(request:string)','"find":(request:number)');assert.notEqual(wrongRequest,apiSource);assert.deepEqual(observe(t,p,{[apiPath]:wrongRequest}),{result:'fail',error:'declared member signature'});
});
test('distinct Interfaces with repeated local contract names retain separate imports and runtime identities',t=>{
 const m=mapping();m.inputs.push({name:'first',type:ref(),use:null},{name:'second',type:ref('response','commerce:other-api'),use:null});m.fields[0].value=at('second','TEST-PUBLIC#id');
 const f=fixture(t,m),other=api();other.ontology_interface='TEST-OTHER-API';
 for(const operation of other.operations){const id='other-'+operation.operation_id;operation.operation_ref='commerce:'+id;f.node(id,'Query',{reads:['order']});f.edge(id,'exposes','other-api',id);}
 f.node('other-api','Interface',{typed_contract:other});f.save();
 const p=plan(f.compile()),n=native(t,p),left=p.interfaces.find(i=>i.selector==='commerce:api')!,right=p.interfaces.find(i=>i.selector==='commerce:other-api')!;
 const a=n.load(left.relative_path),b=n.load(right.relative_path),one={id:'same',total:1n};assert.notEqual(a.publicContracts.response.key(one),b.publicContracts.response.key(one));
 assert.equal(p.modules[0]!.descriptor.imports.length,2);const map=n.load(p.modules[0]!.relative_path)[p.modules[0]!.callable];assert.equal(map({order:{id:'order'},total:'9',first:one,second:{id:'selected',total:2n}}).id,'selected');
 const changed=native(t,p),wrong=changed.load(right.relative_path),original=changed.load(left.relative_path);original.descriptor=wrong.descriptor;assert.throws(()=>changed.load(p.modules[0]!.relative_path),/MAPPING_INTERFACE_BINDING/);
});
test('native compiling mutants are detected by semantic output and ownership controls',t=>{
 const p=plan(fixture(t).compile()),provider=p.modules[0]!.provider_path,source=p.artifacts.find(a=>a.relative_path===provider)!.content,input={order:{id:'source'},total:'18446744073709551615'};
 for(const [changed,detect] of [
  [source.replace('ruleString.normalize(p0["id"])','ruleString.normalize("wrong")'),(out:any)=>assert.notEqual(out.id,'source')],
  [source.replace('ruleUInt64.normalize(p1)','ruleUInt64.normalize(0n)'),(out:any)=>assert.notEqual(out.total,18446744073709551615n)],
  [source.replace('return Object.freeze({["id"]:v0,["total"]:v1});','return {["id"]:v0,["total"]:v1};'),(out:any)=>assert.equal(Object.isFrozen(out),false)],
 ] as const){assert.notEqual(changed,source);const mutant={...p,artifacts:p.artifacts.map(a=>a.relative_path===provider?{...a,content:changed}:a)},n=native(t,mutant);detect(n.load(p.modules[0]!.relative_path)[p.modules[0]!.callable](input));}
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
