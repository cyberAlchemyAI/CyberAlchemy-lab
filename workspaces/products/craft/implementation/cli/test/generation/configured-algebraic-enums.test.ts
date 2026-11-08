import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredAlgebraicEnums,ALGEBRAIC_ENUM_VERSION} from '../../src/generation/configured-algebraic-enums.ts';
import {planConfiguredFactories,STRUCTURED_FACTORY_VERSION,STRUCTURED_FACTORY_CONTRACT_SHA256} from '../../src/generation/configured-factories.ts';
import {STRUCTURED_RULE_VERSION} from '../../src/generation/configured-rules.ts';
import {planConfiguredEnums,EXACT_CONFIGURED_ENUM_VERSION} from '../../src/generation/configured-enums.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),pkg='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const factorySources={configuration:bytes(pkg+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
 rule_contract:bytes(pkg+'string-order-rule-contract.json'),collection_contract:bytes(pkg+'rule-collection-value-contract.json'),predicate_contract:bytes(pkg+'rule-collection-predicate-contract.json'),numeric_contract:bytes(pkg+'rule-numeric-contract.json'),exact_contract:bytes(pkg+'rule-exact-contract.json'),literal_contract:bytes(pkg+'rule-exact-literal-contract.json'),structured_contract:bytes(pkg+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json'),factory_contract:bytes(pkg+'factory-structured-rule-contract.json'),enum_provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts')};
const sources={standalone_contract:bytes(pkg+'standalone-sum-contract.json'),factories:factorySources};
const scalar={kind:'scalar',name:'UInt64'},named=(id:string)=>({kind:'named',selector:'commerce:'+id}),wrap=(kind:string,element:any)=>({kind,element});
function fixture(t:any,mixed=false){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-algebraic-enums-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));const source=path.join(temp,'source'),nodes:string[]=[];
 const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
 const sum=(id:string,variants:[string,any][])=>node(id,'Enum',{values:variants.map(([name])=>name),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-'+id.toUpperCase(),variants:variants.map(([name,payload])=>({name,payload,ontology_variant:'FIXTURE-'+id.toUpperCase()+'#'+name}))}});
 sum('status',[['Ready',null],['Draft',null]]);
 sum('answer',[['Amount',scalar],['None',null],['Other',scalar],...(mixed?[['Customer',named('customer')],['Detail',named('detail')]] as [string,any][]:[])]);
 sum('choice',[['List',wrap('list',named('answer'))],['Maybe',wrap('optional',named('answer'))],['None',null],['Set',wrap('set',named('answer'))],['Status',named('status')]]);
 const factories:any[]=[];
 if(mixed){
  node('positive','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-POSITIVE',parameters:[{name:'value',type:scalar}],expression:{op:'lt',left:{op:'literal',type:'UInt64',value:'0'},right:{op:'path',root:'value',properties:[]}}}});
  for(const [id,kind,field]of [['customer','Entity','id'],['detail','Value Object','amount']]){
   node(id!,kind!,{fields:[field],...(kind==='Value Object'?{invariant_refs:['commerce:positive']}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+id!.toUpperCase(),properties:[{name:field,ontology_property:'FIXTURE-'+id!.toUpperCase()+'#'+field,type:scalar,identity:kind==='Entity',cardinality:'one',meaning:field}]}});
   factories.push({selector:'commerce:'+id,base_validators:[{rule:'commerce:positive',arguments:[{parameter:'value',field}]}],extensions:[]});
  }
 }
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'algebraic-values',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges:[]});
 const graph=loadCompiledProjectGraph(source),fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:['commerce:choice'],bindings:[]},factorySources.field_contract);
 const selection:any={schema_version:ALGEBRAIC_ENUM_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256,factories};
 return {temp,source,write,graph,fields,selection,plan:()=>planConfiguredAlgebraicEnums(graph,fields,selection,sources)};
}
const sumPath=(id:string)=>'application/features/commerce/src/domain/enums/'+id+'.sum.ts';
function native(root:string,artifacts:readonly {relative_path:string;content:string}[]){
 for(const a of artifacts){const f=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,a.content);}
 const chain=read(path.join(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(chain.container_image);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
 const compile=(extra:string[]=[])=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--declaration','--rootDir',root,'--outDir',path.join(root,'js'),...artifacts.map(a=>path.join(root,a.relative_path)),...extra],{encoding:'utf8',stdio:'pipe'});
 compile();const load=(p:string)=>createRequire(import.meta.url)(path.join(root,'js',p.replace(/\.ts$/,'.js')));
 return {compile,load,docker};
}
test('standalone algebraic Enum closure generates no dummy record or Rule and is deterministic',t=>{
 const f=fixture(t),p=f.plan();assert.equal(p.sum_modules.length,2);assert.equal(p.dependency_plan_sha256,null);assert.deepEqual(p.components.map(c=>c.selector),['commerce:status']);assert.ok(f.graph.nodes.every(n=>n.kind==='Enum'));
 assert.deepEqual(f.plan(),p);assert.equal(Object.isFrozen(f.selection.factories),false);assert.ok(Object.isFrozen(p.selection.factories));
 const moved=planConfiguredAlgebraicEnums(f.graph,f.fields,{...f.selection,module_root:'other'},sources);assert.deepEqual(moved.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));fs.renameSync(f.source,path.join(f.temp,'moved'));assert.deepEqual(f.plan(),p);
});
test('standalone sums preserve tags payloads full-width values occurrence lists and unique sets natively',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'native'),f.plan().artifacts),a=n.load(sumPath('answer')).AnswerValueComponent,c=n.load(sumPath('choice')).ChoiceValueComponent,status=n.load(sumPath('status').replace('.sum.ts','.component.ts')).StatusValueComponent;
 const x=a.create({variant:'Amount',payload:'18446744073709551615'}),same=a.create({variant:'Amount',payload:18446744073709551615n}),other=a.create({variant:'Other',payload:18446744073709551615n});
 assert.equal(x.payload,18446744073709551615n);assert.equal(a.equals(x,same),true);assert.equal(a.equals(x,other),false);assert.equal(a.isOwned({...x}),false);
 const list=c.create({variant:'List',payload:[x,same]});assert.equal(list.payload.length,2);assert.throws(()=>c.create({variant:'Set',payload:[x,same]}),/DUPLICATE/);assert.equal(c.create({variant:'Set',payload:[x,other]}).payload.length,2);
 assert.equal(c.create({variant:'Maybe',payload:null}).payload,null);assert.ok(c.isOwned(c.create({variant:'Status',payload:status.fromVariant('Ready')})));assert.throws(()=>c.create({variant:'List',payload:[{variant:'Amount',payload:1}]}),/UNOWNED/);
 for(const v of [{variant:'None',payload:null},{variant:'Amount'},{variant:'Amount',payload:'01'},{variant:'Missing'},null])assert.throws(()=>a.create(v));
 let reads=0;assert.throws(()=>a.create({variant:'Amount',get payload(){reads++;return 1;}}));assert.equal(reads,0);
});
test('real Entity and Value Object payloads reuse exact existing factory artifacts and validators',t=>{
 const f=fixture(t,true),p=f.plan(),old=planConfiguredFactories(f.graph,f.fields,{schema_version:STRUCTURED_FACTORY_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:f.fields.compilation_sha256,factories:f.selection.factories,rule_selection:{schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE}},factorySources);
 assert.deepEqual(p.artifacts,old.artifacts);assert.equal(p.dependency_plan_sha256,old.plan_sha256);
 const n=native(path.join(f.temp,'mixed'),p.artifacts),a=n.load(sumPath('answer')).AnswerValueComponent,customer=n.load('application/features/commerce/src/domain/entities/customer.ts').createCustomerFactory(),detail=n.load('application/features/commerce/src/domain/value-objects/detail.ts').createDetailFactory();
 assert.equal(customer.create({id:0}).ok,false);assert.equal(detail.create({amount:0}).ok,false);
 const x=customer.create({id:'18446744073709551615'}),d=detail.create({amount:3});assert.equal(x.ok,true);assert.equal(d.ok,true);
 assert.equal(a.create({variant:'Customer',payload:x.value}).payload,x.value);assert.equal(a.create({variant:'Detail',payload:d.value}).payload,d.value);assert.throws(()=>a.create({variant:'Detail',payload:{amount:3}}),/UNOWNED/);
 const missing={...f.selection,factories:[]};assert.throws(()=>planConfiguredAlgebraicEnums(f.graph,f.fields,missing,sources));
});
test('algebraic selection rejects forged snapshots stale sources unsafe paths and host hooks',t=>{
 const f=fixture(t);assert.throws(()=>planConfiguredAlgebraicEnums(structuredClone(f.graph),f.fields,f.selection,sources));assert.throws(()=>planConfiguredAlgebraicEnums(f.graph,structuredClone(f.fields),f.selection,sources));
 for(const patch of [{schema_version:'future'},{language:'python'},{module_root:'../bad'},{module_root:'con'},{field_compilation_sha256:'stale'},{factories:[{selector:'fake'}]},{ignore:true}])assert.throws(()=>planConfiguredAlgebraicEnums(f.graph,f.fields,{...f.selection,...patch},sources));
 for(const key of Object.keys(factorySources))assert.throws(()=>planConfiguredAlgebraicEnums(f.graph,f.fields,f.selection,{...sources,factories:{...factorySources,[key]:(factorySources as any)[key]+' '}}),/drift/);
 assert.throws(()=>planConfiguredAlgebraicEnums(f.graph,f.fields,f.selection,{...sources,standalone_contract:sources.standalone_contract+' '}),/drift/);
 let reads=0;assert.throws(()=>planConfiguredAlgebraicEnums(f.graph,f.fields,{...f.selection,get factories(){reads++;return [];}},sources));assert.equal(reads,0);
});

test('leaf sum needs neither plain Enum runtime nor factory and old selections keep rejecting it',t=>{
 const f=fixture(t),fields=compileSelectedProjectFields(f.graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:f.fields.certificate.graph_sha256,roots:['commerce:answer'],bindings:[]},factorySources.field_contract);
 const p=planConfiguredAlgebraicEnums(f.graph,fields,{...f.selection,field_compilation_sha256:fields.compilation_sha256},sources);
 assert.equal(p.artifacts.length,1);assert.equal(p.artifacts[0]!.relative_path,sumPath('answer'));assert.deepEqual(p.components,[]);assert.deepEqual(p.component_bindings,[]);
 const n=native(path.join(f.temp,'leaf'),p.artifacts),a=n.load(sumPath('answer')).AnswerValueComponent;assert.equal(a.create({variant:'Amount',payload:'9007199254740993'}).payload,9007199254740993n);
 assert.throws(()=>planConfiguredEnums(fields,{schema_version:EXACT_CONFIGURED_ENUM_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256},{configuration:factorySources.configuration,base:factorySources.base,typescript:factorySources.typescript,provider:factorySources.enum_provider}),/payload-bearing sum unsupported/);
 assert.throws(()=>planConfiguredFactories(f.graph,fields,{schema_version:STRUCTURED_FACTORY_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256,factories:[],rule_selection:{schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE}},factorySources));
});
test('independent sum observer and native types reject compiling tag and payload changes',t=>{
 const f=fixture(t),p=f.plan(),root=path.join(f.temp,'observed'),n=native(root,p.artifacts),contract_sha256=STRUCTURED_FACTORY_CONTRACT_SHA256,support_sha256='1b207847013953e8863b829e3db0d8a721a8b617ca449f23dd51c9ad1a6ea5bc';
 const dep=(file:string,name:string,local:string)=>[{path:file,symbol:name+'ValueComponent',local},{path:file,symbol:name+'Case',local:local+'Type',type_only:true}];
 const expected={files:p.artifacts.map(a=>a.relative_path),modules:[],sum_modules:[
  {path:sumPath('answer'),name:'Answer',selector:'commerce:answer',imports:[],protocol:'sumValue(Object.freeze({["Amount"]:uint64Value,["None"]:null,["Other"]:uint64Value}))',contract_sha256,support_sha256},
  {path:sumPath('choice'),name:'Choice',selector:'commerce:choice',imports:[...dep('./answer.sum.js','Answer','payloadCase0Element'),...dep('./answer.sum.js','Answer','payloadCase1Element'),...dep('./answer.sum.js','Answer','payloadCase3Element'),...dep('./status.component.js','Status','payloadCase4')],protocol:'sumValue(Object.freeze({["List"]:listValue(ownedSumValue(payloadCase0Element)),["Maybe"]:optionalValue(ownedSumValue(payloadCase1Element)),["None"]:null,["Set"]:setValue(ownedSumValue(payloadCase3Element)),["Status"]:enumValue(payloadCase4)}))',contract_sha256,support_sha256}
 ]};
 fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(expected));fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expected.files}));
 const observer=path.join(project,'impl/cli/tools/observe-configured-factories.mjs');const observe=()=>{const args=[...n.docker.slice(0,-1),'--tmpfs','/tmp','--mount','type=bind,source='+observer+',target=/observer.mjs,readonly',n.docker.at(-1)!,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')];try{return JSON.parse(execFileSync('docker',args,{encoding:'utf8',stdio:'pipe'}));}catch(e:any){if(e.status===1)return JSON.parse(e.stdout);throw e;}};
 assert.equal(observe().result,'pass');
 const answer=p.artifacts.find(a=>a.relative_path===sumPath('answer'))!;
 for(const mutated of [answer.content.replace('["Other"]:uint64Value','["Other"]:Object.freeze({...uint64Value,normalize:(_input:unknown)=>0n})'),answer.content.replace("part(variant)","part('Amount')")]){assert.notEqual(mutated,answer.content);fs.writeFileSync(path.join(root,answer.relative_path),mutated);n.compile();assert.equal(observe().result,'fail');}
 fs.writeFileSync(path.join(root,answer.relative_path),answer.content);
 const consumer=path.join(root,'consumer.ts');fs.writeFileSync(consumer,`import {AnswerValueComponent as A} from './${sumPath('answer').replace(/\.ts$/,'.js')}';\n// @ts-expect-error payload is required\nA.create({variant:'Amount'});\n// @ts-expect-error boolean is not UInt64\nA.create({variant:'Amount',payload:true});\n// @ts-expect-error no payload on None\nA.create({variant:'None',payload:null});\nconst result=A.create({variant:'Amount',payload:'18446744073709551615'});if(result.variant==='Amount'){const exact:bigint=result.payload;}\n`);n.compile([consumer]);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
