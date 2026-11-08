import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {planProfiledProject,PROFILED_SELECTION_VERSION,PROFILED_SOURCE_DIGESTS,type ProfiledSelection} from '../../src/generation/profiled-project.ts';
import {observeProfiledProject,type ProfileTargetExpectation} from '../../src/conformance/observe-profiled-project.ts';
import {sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const evidenceRoot=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const profiles={base:fs.readFileSync(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),'utf8'),typescript:fs.readFileSync(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),'utf8')};
const selection:ProfiledSelection={schema_version:PROFILED_SELECTION_VERSION,language:'typescript',source_root:'commerce-module',profile_digests:PROFILED_SOURCE_DIGESTS,entity_rules:[{entity:'commerce:order',rule:'commerce:order-is-valid',parameter:'order'}]};
function fixture(){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'domainspec-pcr-l0-'));
  const source=path.join(temp,'source');
  fs.cpSync(path.join(project,'development/reconciliation-v1/verticals/entity-query/source'),source,{recursive:true});
  const featurePath=path.join(source,'specs/commerce/feature.json');const feature=read(featurePath);
  feature.nodes.push('order-is-valid');fs.writeFileSync(featurePath,JSON.stringify(feature,null,2)+'\n');
  const rule={schema_version:'domainspec.node/v1',node_id:'order-is-valid',feature_id:'commerce',kind:'Rule',body:{description:'Orders require nonempty identity and a supported lifecycle status.',predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'COMMERCE-ORDER-IS-VALID',parameters:[{name:'order',type:{kind:'named',selector:'commerce:order'}}],expression:{op:'all',terms:[{op:'not',term:{op:'eq',left:{op:'path',root:'order',properties:['COMMERCE-ORDER#order_id']},right:{op:'literal',type:'String',value:''}}},{op:'any',terms:['draft','submitted'].map(value=>({op:'eq',left:{op:'path',root:'order',properties:['COMMERCE-ORDER#status']},right:{op:'literal',type:'String',value}}))}]}}}};
  fs.writeFileSync(path.join(source,'specs/commerce/nodes/order-is-valid.json'),JSON.stringify(rule,null,2)+'\n');
  try {return {temp,source,graph:loadCompiledProjectGraph(source)};}
  catch(error){fs.rmSync(temp,{recursive:true,force:true});throw error;}
}
function expected(root='commerce-module'):ProfileTargetExpectation[]{return [
  {path:root+'/src/domain/entities/order.ts',kind:'Entity',callable:'createOrderFactory',bound_rule:'ruleOrderIsValid',imports:[{path:'../rules/order-is-valid.js',symbol:'ruleOrderIsValid',type_only:false}]},
  {path:root+'/src/domain/rules/order-is-valid.ts',kind:'Rule',callable:'ruleOrderIsValid',imports:[{path:'../entities/order.js',symbol:'OrderFields',type_only:true}]},
  {path:root+'/src/application/queries/find-order.ts',kind:'Query',callable:'queryFindOrder',imports:[{path:'../../domain/entities/order.js',symbol:'OrderSnapshot',type_only:true}]},
];}
function writePlan(root:string,artifacts:readonly {relative_path:string;content:string}[]){for(const a of artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content,{flag:'wx'});}}
function nativeCompile(temp:string,target:string,files:readonly string[]){
  const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'));
  const image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${temp},target=${temp}`,'--workdir',temp,image,'tsc'];
  const version=execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim();assert.equal(version,'Version '+toolchain.typescript);
  execFileSync('docker',[...args,'--target','ES2022','--module','commonjs','--strict','--skipLibCheck','--outDir',target,...files],{encoding:'utf8'});
  return {image,typescript:version};
}
function nativeObserve(temp:string,target:string,expectations:ProfileTargetExpectation[],image:string){
  const config=path.join(target,'tsconfig.json'),expectedPath=path.join(target,'expected.json');
  fs.writeFileSync(config,JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expectations.map(e=>e.path)}));
  fs.writeFileSync(expectedPath,JSON.stringify(expectations));
  try{return JSON.parse(execFileSync('docker',['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--tmpfs','/tmp','--mount',`type=bind,source=${temp},target=${temp},readonly`,'--mount',`type=bind,source=${path.join(project,'impl/cli/tools/observe-profiled-target.mjs')},target=/observer.mjs,readonly`,image,'node','/observer.mjs',config,expectedPath],{encoding:'utf8'}));}
  catch(error){const result=error as {status?:number;stdout?:string};if(result.status===1 && result.stdout){const observation=JSON.parse(result.stdout);if(observation.schema_version==='domainspec.profile-native-observation/v1-candidate')return observation;}throw error;}
}
test('PCR-01: crosswalk keeps all 39 baseline cells and historical drift separate',()=>{
  const audit=JSON.parse(execFileSync(process.execPath,[path.join(evidenceRoot,'audit.mjs')],{encoding:'utf8',maxBuffer:4*1024*1024}));
  assert.equal(audit.cells.length,39);assert.equal(audit.counts.current_core_refs,117);
  assert.equal(audit.cells.filter((c:any)=>c.profile.document_status==='candidate').length,39);
  assert.equal(audit.cells.find((c:any)=>c.meta_type_label==='Rule'&&c.language==='typescript').observer.status,'stale');
});
test('PCR-02: selection is closed, digest-bound and isolated from legacy behavior',()=>{
  const f=fixture();try{
    const legacy=planCompiledProjectBuild(f.graph,'typescript');
    const p=planProfiledProject(f.graph,selection,profiles);
    assert.equal(p.artifacts.length,3);assert.equal(observeProfiledProject(p.artifacts,expected()).result,'pass');
    assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript'),legacy);
    for(const mutation of [{...selection,schema_version:'unknown'},{...selection,language:'rust'},{...selection,unknown:true},{...selection,source_root:'../escape'},{...selection,source_root:'/absolute'},{...selection,source_root:'Foo'},{...selection,source_root:'a\\b'},{...selection,entity_rules:[]},{...selection,entity_rules:[{entity:'commerce:order',rule:'commerce:missing',parameter:'order'}]},{...selection,profile_digests:{...PROFILED_SOURCE_DIGESTS,typescript:'0'.repeat(64)}}])assert.throws(()=>planProfiledProject(f.graph,mutation as any,profiles),/DS_PROFILE_L0/);
    assert.throws(()=>planProfiledProject(f.graph,selection,{...profiles,typescript:profiles.typescript+' '}),/tampered profile/);
    assert.throws(()=>planProfiledProject({...f.graph,nodes:f.graph.nodes.slice(1)},selection,profiles));
    assert.ok(Object.isFrozen(p.selection));
    const rulePath=path.join(f.source,'specs/commerce/nodes/order-is-valid.json');const rule=read(rulePath);
    rule.body.typed_contract.expression.terms[0].term.right.value='http://process/class Example/import/export';fs.writeFileSync(rulePath,JSON.stringify(rule));
    assert.equal(observeProfiledProject(planProfiledProject(loadCompiledProjectGraph(f.source),selection,profiles).artifacts,expected()).result,'pass','string data is not executable syntax');
  }finally{fs.rmSync(f.temp,{recursive:true,force:true});}
});
test('PCR-03: expected-red class, bypass, path, import and export mutants are rejected',()=>{
  const f=fixture();try{
    const p=planProfiledProject(f.graph,selection,profiles);
    const legacy=planCompiledProjectBuild(f.graph,'typescript');
    // Put the old class at the expected location: this tests form, not just its old path.
    const old=legacy.artifacts.find(a=>a.relative_path.endsWith('/order.ts'))!;
    const classMutant=p.artifacts.map(a=>a.relative_path.endsWith('/order.ts')?{...old,relative_path:a.relative_path}:a);
    assert.ok(observeProfiledProject(classMutant,expected()).failures.some(s=>s.startsWith('class-construction:')));
    const mutants=[
      ['bypass','if (!ruleOrderIsValid(fields))','if (false && !ruleOrderIsValid(fields))','validation-before-construction:'],
      ['wrong-import','../rules/order-is-valid.js','../rules/nonexistent.js','import-binding:'],
      ['extra-export','const makeFactory','export const makeFactory','export-form:'],
      ['bypass-reconstruct','reconstruct:(input:unknown):Result=>construct(input)','reconstruct:(input:unknown):Result=>({ok:true,value:input,failure_codes:[]})','construction-routes:'],
    ];
    for(const [name,from,to,reason] of mutants){
      const artifacts=p.artifacts.map(a=>{const content=a.content.replace(from!,to!);return {...a,content,sha256:sha256(content),size_bytes:Buffer.byteLength(content)};});
      assert.ok(observeProfiledProject(artifacts,expected()).failures.some(s=>s.startsWith(reason!)),name);
    }
    assert.ok(observeProfiledProject(p.artifacts.map(a=>({...a,relative_path:a.relative_path.replace('/domain/','/wrong/')})),expected()).failures.some(s=>s.startsWith('path:')));
  }finally{fs.rmSync(f.temp,{recursive:true,force:true});}
});
test('PCR-04 candidate: compile and execute factories, declared Rule and Query in two roots',()=>{
  const f=fixture();try{
    const sourceFiles=fs.readdirSync(f.source,{recursive:true,withFileTypes:true}).filter(e=>e.isFile()).map(e=>{const absolute=path.join(e.parentPath,e.name);return {path:path.relative(f.source,absolute),content:fs.readFileSync(absolute,'utf8')};}).sort((a,b)=>a.path.localeCompare(b.path));
    const p=planProfiledProject(f.graph,selection,profiles);
    const same=planProfiledProject(f.graph,selection,profiles);assert.deepEqual(p,same);
    const alt=planProfiledProject(f.graph,{...selection,source_root:'alternate-module'},profiles);
    assert.deepEqual(p.artifacts.map(a=>a.content),alt.artifacts.map(a=>a.content));
    assert.equal(observeProfiledProject(alt.artifacts,expected('alternate-module')).result,'pass');
    // Once checked, the graph remains the source: editing disk cannot change this plan.
    fs.appendFileSync(path.join(f.source,'project.json'),' ');
    assert.deepEqual(planProfiledProject(f.graph,selection,profiles),p);
    const observations=[];
    for(const [index,plan] of [p,alt].entries()){
      const target=path.join(f.temp,'target-'+index),js=path.join(f.temp,'js-'+index);writePlan(target,plan.artifacts);
      const toolchain=nativeCompile(f.temp,js,plan.artifacts.map(a=>path.join(target,a.relative_path)));
      const native=nativeObserve(f.temp,target,expected(plan.selection.source_root),toolchain.image);
      assert.equal(native.result,'pass');assert.equal(native.observations.length,3);
      const require=createRequire(import.meta.url);
      const {createOrderFactory}=require(path.join(js,'domain/entities/order.js'));
      const {ruleOrderIsValid}=require(path.join(js,'domain/rules/order-is-valid.js'));
      const {queryFindOrder}=require(path.join(js,'application/queries/find-order.js'));
      const factory=createOrderFactory();const data={order_id:'order-1',status:'draft',internal_note:'private'};
      assert.equal(ruleOrderIsValid(data),true);assert.equal(ruleOrderIsValid({...data,status:'illegal'}),false);
      assert.equal(factory.constructor,Object);assert.equal(factory.directConstructor,undefined);
      const first=factory.create(data);assert.equal(first.ok,true);
      data.internal_note='changed externally';assert.equal(first.value.fields.internal_note,'private');
      const second=factory.transition(first.value,{...data,status:'submitted'});assert.equal(second.ok,true);
      assert.equal(first.value.sameIdentity(second.value),true);assert.equal(first.value.hash(),second.value.hash());
      assert.notDeepEqual(first.value.fields,second.value.fields);
      const different=factory.create({...data,order_id:'order-2'});assert.equal(first.value.sameIdentity(different.value),false);
      assert.equal(factory.transition(first.value,{...data,order_id:'order-2'}).ok,false);
      assert.equal(factory.transition({fields:data,hash:()=>first.value.hash()},data).ok,false);
      for(const route of ['create','reconstruct'])for(const invalid of [{...data,order_id:''},{...data,status:'illegal'},{...data,order_id:7},{...data,unexpected:true},null]){const result=factory[route](invalid);assert.equal(result.ok,false);assert.equal(result.value,null);assert.ok(result.failure_codes.length);}
      assert.equal(factory.transition(first.value,{...data,status:'illegal'}).value,null);
      const extended=factory.extend(()=>true);assert.equal(extended.create({...data,status:'illegal'}).value,null);
      assert.equal(factory.extend(()=>false).create(data).value,null);
      assert.equal(factory.extend(()=>{throw Error('bad validator');}).create(data).value,null);
      assert.equal(extended.create(data).ok,true);assert.equal(factory.create(data).ok,true);
      assert.ok(Object.isFrozen(first.value));assert.ok(Object.isFrozen(first.value.fields));
      const rows=Object.freeze([second.value,different.value]);const before=JSON.stringify(rows);
      const output=queryFindOrder(rows,Object.freeze({order_id:'order-1'}));
      assert.deepEqual(output,[{order_id:'order-1',status:'submitted'}]);
      assert.deepEqual(queryFindOrder(rows,{order_id:'absent'}),[]);
      assert.throws(()=>queryFindOrder(rows,{}),/missing parameter/);
      assert.ok(Object.isFrozen(output));assert.ok(Object.isFrozen(output[0]));assert.equal(JSON.stringify(rows),before);
      observations.push({toolchain,native_ast:{result:native.result,typescript:native.typescript,module_count:native.observations.length},output,identity:first.value.hash(),source_hashes:plan.artifacts.map(a=>a.sha256)});
    }
    assert.deepEqual(observations[0],observations[1]);
    if(process.env.PCR_PRINT_PRODUCT==='1')console.log('PCR_PRODUCT:'+JSON.stringify({schema_version:'domainspec.pcr-l0-product-example/v1-candidate',source_files:sourceFiles,plan:p,native_outcomes:observations,authority_effect:'none',claim_ceiling:'L0 generated-code example; not a package qualification or 39-cell compiler result'}));
  }finally{fs.rmSync(f.temp,{recursive:true,force:true});}
});
test('PCR-03/04: native AST and behavior oracles independently kill generated-source mutants',()=>{
  const f=fixture();try{
    const p=planProfiledProject(f.graph,selection,profiles);
    const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'));
    const image=nativeToolchainImage(toolchain.container_image);
    const mutants=[
      {id:'class',suffix:'/order.ts',change:(s:string)=>s+'\nclass HiddenConstructor {}\n',reason:'class-construction:'},
      {id:'bypass',suffix:'/order.ts',change:(s:string)=>s.replace('if (!ruleOrderIsValid(fields))','if (false && !ruleOrderIsValid(fields))'),reason:'validation-before-construction:'},
      {id:'wrong-import',suffix:'/order.ts',change:(s:string)=>s.replace('../rules/order-is-valid.js','../rules/missing.js'),reason:'import-binding:'},
      {id:'unreachable-guard',suffix:'/order.ts',change:(s:string)=>s.replace('if (!ruleOrderIsValid(fields)) return failure("RULE_FAILED:commerce:order-is-valid");','if (false) {if (!ruleOrderIsValid(fields)) return failure("RULE_FAILED:commerce:order-is-valid");}'),reason:'validation-before-construction:'},
    ];
    for(const m of mutants){const target=path.join(f.temp,m.id);const artifacts=p.artifacts.map(a=>({...a,content:a.relative_path.endsWith(m.suffix)?m.change(a.content):a.content}));writePlan(target,artifacts);const observation=nativeObserve(f.temp,target,expected(),image);assert.equal(observation.result,'fail',m.id);assert.ok(observation.errors.some((s:string)=>s.startsWith(m.reason)),m.id);}
    const behaviors=[
      {id:'rule-always-true',suffix:'/order-is-valid.ts',change:(s:string)=>s.replace(/:boolean =>[\s\S]*;/,':boolean => true;')},
      {id:'guard-bypass',suffix:'/order.ts',change:(s:string)=>s.replace('if (!ruleOrderIsValid(fields))','if (false && !ruleOrderIsValid(fields))')},
      {id:'query-unfiltered',suffix:'/find-order.ts',change:(s:string)=>s.replace(/\.filter\(row=>[^\n]+;/,'.filter(row=>true);')},
    ];
    for(const m of behaviors){
      const target=path.join(f.temp,m.id),js=path.join(f.temp,m.id+'-js');
      const artifacts=p.artifacts.map(a=>({...a,content:a.relative_path.endsWith(m.suffix)?m.change(a.content):a.content}));
      assert.ok(artifacts.some((a,i)=>a.content!==p.artifacts[i]!.content));writePlan(target,artifacts);nativeCompile(f.temp,js,artifacts.map(a=>path.join(target,a.relative_path)));
      const require=createRequire(import.meta.url),factory=require(path.join(js,'domain/entities/order.js')).createOrderFactory();
      if(m.id==='query-unfiltered'){
        const row=factory.create({order_id:'order-1',status:'draft',internal_note:'secret'}).value;
        assert.notDeepEqual(require(path.join(js,'application/queries/find-order.js')).queryFindOrder([row],{order_id:'absent'}),[]);
      }else assert.equal(factory.create({order_id:'',status:'illegal',internal_note:'secret'}).ok,true,'positive suite would reject this semantic mutant');
    }
    const target=path.join(f.temp,'nominal'),js=path.join(f.temp,'nominal-js');writePlan(target,p.artifacts);
    const forged=path.join(target,'commerce-module/src/forged.ts');
    fs.writeFileSync(forged,'import type {OrderSnapshot} from "./domain/entities/order.js";\nconst forged:OrderSnapshot={fields:{order_id:"x",status:"draft",internal_note:""},hash:()=>"x",sameIdentity:()=>true};\n');
    assert.throws(()=>nativeCompile(f.temp,js,[...p.artifacts.map(a=>path.join(target,a.relative_path)),forged]),(error:unknown)=>/TS2741/.test((error as {stdout:string}).stdout) && /brand/.test((error as {stdout:string}).stdout));
  }finally{fs.rmSync(f.temp,{recursive:true,force:true});}
});
test('L0 scalar envelope: Boolean data survives native generation; unsupported fields fail closed',()=>{
  const f=fixture();try{
    const entityPath=path.join(f.source,'specs/commerce/nodes/order.json');const entity=read(entityPath);
    entity.body.typed_contract.properties[2].type.name='Bool';fs.writeFileSync(entityPath,JSON.stringify(entity));
    const p=planProfiledProject(loadCompiledProjectGraph(f.source),selection,profiles);
    const target=path.join(f.temp,'bool'),js=path.join(f.temp,'bool-js');writePlan(target,p.artifacts);
    nativeCompile(f.temp,js,p.artifacts.map(a=>path.join(target,a.relative_path)));
    const factory=createRequire(import.meta.url)(path.join(js,'domain/entities/order.js')).createOrderFactory();
    assert.equal(factory.create({order_id:'x',status:'draft',internal_note:false}).value.fields.internal_note,false);
    assert.equal(factory.create({order_id:'x',status:'draft',internal_note:'false'}).value,null);
    for(const type of [{kind:'scalar',name:'UInt64'},{kind:'optional',element:{kind:'scalar',name:'String'}},{kind:'list',element:{kind:'scalar',name:'String'}}]){
      const field=entity.body.typed_contract.properties[2];field.type=type;field.cardinality=type.kind==='optional'?'optional':type.kind==='list'?'many':'one';
      fs.writeFileSync(entityPath,JSON.stringify(entity));
      const graph=loadCompiledProjectGraph(f.source);assert.throws(()=>planProfiledProject(graph,selection,profiles),/unsupported L0 field envelope/);
    }
  }finally{fs.rmSync(f.temp,{recursive:true,force:true});}
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
