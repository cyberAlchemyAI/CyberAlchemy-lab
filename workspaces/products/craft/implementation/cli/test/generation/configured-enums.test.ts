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
import {compileSelectedProjectFields, compiledFieldValueKey, FIELD_CONTRACT_SHA256, PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {planConfiguredEnums, CONFIGURED_ENUM_VERSION, type ConfiguredEnumSelection} from '../../src/generation/configured-enums.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const packageRoot = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const read = (p:string) => fs.readFileSync(path.join(project, p), 'utf8');
const descriptor = read('development/reconciliation-v1/contracts/field-and-reference-model.json');
const sources = {configuration: read('development/reconciliation-v1/profile-compiler-reconciliation/configuration.json'),
  base: read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  typescript: read('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
  provider: read('impl/architecture-conformance/typescript/runtime/enum/index.ts')};
function fixture(t:any, node='status', payload=false, withEntity=false) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'pcr06-enums-'));
  t.after(() => fs.rmSync(temp, {recursive:true, force:true}));
  const source = path.join(temp, 'source');
  const write = (relative:string, value:unknown) => {const file=path.join(source,relative);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
  write('project.json', {schema_version:'domainspec.project/v1',project_id:'configured-enums',features:['commerce','audit'],cross_feature_edges:[]});
  for (const feature_id of ['commerce','audit']) {
    write(`specs/${feature_id}/feature.json`,{schema_version:'domainspec.feature/v1',feature_id,nodes:[node,...(withEntity&&feature_id==='commerce'?['order']:[])],edges:[]});
    const names = feature_id==='commerce'?['Submitted','Draft']:['Recorded','Pending'];
    write(`specs/${feature_id}/nodes/${node}.json`,{schema_version:'domainspec.node/v1',feature_id,node_id:node,kind:'Enum',body:{description:'Owned Enum fixture',values:names,
      typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:names.map(name=>({ontology_variant:'FIXTURE-STATUS#'+name,name,payload:payload?{kind:'scalar',name:'String'}:null}))}}});
  }
  if(withEntity) write('specs/commerce/nodes/order.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:'order',kind:'Entity',body:{description:'Do not silently skip Entity',fields:['id'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties:[{ontology_property:'FIXTURE-ORDER#id',name:'id',type:{kind:'scalar',name:'String'},cardinality:'one',identity:true,meaning:'identity'}]}}});
  const graph=loadCompiledProjectGraph(source);
  const fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:[`commerce:${node}`,`audit:${node}`,...(withEntity?['commerce:order']:[])],bindings:[]},descriptor);
  const selection:ConfiguredEnumSelection={schema_version:CONFIGURED_ENUM_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256};
  return {temp,source,fields,selection,graph};
}
const expected = () => ({provider:{path:'application/runtime/enum.ts',sha256:'378e09358713b431e4a24e664e484feae0122462e47aabfa653ae21a17315fcc'},modules:[
  {path:'application/features/audit/src/domain/enums/status.ts',symbol:'Status',members:['Pending','Recorded'],provider_import:'../../../../../runtime/enum.js'},
  {path:'application/features/commerce/src/domain/enums/status.ts',symbol:'Status',members:['Draft','Submitted'],provider_import:'../../../../../runtime/enum.js'}]});
function native(root:string, artifacts:readonly {relative_path:string;content:string}[]) {
  for(const a of artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content,{flag:'wx'});}
  const toolchain=JSON.parse(read('../../toolchains/node-typescript/toolchain.json'));
  const image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root}`,'--workdir',root,image,'tsc'];
  assert.equal(execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
  const compile=(extra:string[]=[])=>execFileSync('docker',[...args,'--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...artifacts.map(a=>path.join(root,a.relative_path)),...extra],{encoding:'utf8',stdio:'pipe'});
  compile();
  const e=expected();
  fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:[...e.modules.map(m=>m.path),e.provider.path]}));
  fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(e));
  return {compile,observe:()=>{
    const observer=path.join(project,'impl/cli/tools/observe-configured-enums.mjs');
    const command=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root},readonly`,'--mount',`type=bind,source=${observer},target=/observer.mjs,readonly`,image,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')];
    try{return JSON.parse(execFileSync('docker',command,{encoding:'utf8',stdio:'pipe'}));}
    catch(error){const e=error as any;if(e.status===1&&e.stdout)return JSON.parse(e.stdout);throw error;}
  }};
}
const loadJs=(root:string,relative:string)=>createRequire(import.meta.url)(path.join(root,'js',relative.replace(/\.ts$/,'.js')));

test('PCR-06 Enum planner binds checked fields and exact sources; relocation preserves deterministic content',async t=>{
  const f=fixture(t),p=planConfiguredEnums(f.fields,f.selection,sources),e=expected();
  assert.equal(p.artifacts.length,3);assert.equal(p.modules.length,2);assert.equal(p.authority_effect,'none');
  assert.deepEqual(p.modules.map(m=>({path:m.relative_path,symbol:m.symbol,members:m.members.map(v=>v.name),provider_import:m.provider_import})),e.modules);
  assert.equal(p.runtime_support.relative_path,e.provider.path);assert.equal(p.artifacts.at(-1)!.content,sources.provider);
  assert.deepEqual(p.certificate,createCompiledProjectCertificate(f.graph));assert.equal(p.model_sha256,f.fields.model.model_sha256);
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  for(const a of p.artifacts){assert.equal(a.sha256,sha256(a.content));assert.equal(a.size_bytes,Buffer.byteLength(a.content));}
  assert.deepEqual(planConfiguredEnums(f.fields,f.selection,sources),p);
  const moved=planConfiguredEnums(f.fields,{...f.selection,module_root:'alternate/nested'},sources);
  assert.deepEqual(moved.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  const config=await import(path.join(packageRoot,'configuration.mjs'));
  const loaded=config.loadConfiguration(undefined,undefined,JSON.parse(fs.readFileSync(path.join(packageRoot,'configuration-input-boundary-sources.json'),'utf8')));
  const locations=config.previewLocations(config.resolveConfiguration({schema_version:'domainspec.compilation-selection/v1-candidate',language:'typescript',module_root:'application'},loaded),f.graph.nodes.map(n=>({kind:n.kind,feature_id:n.feature_id,node_id:n.node_id})));
  assert.deepEqual(locations.map((l:any)=>l.source_path).sort(),p.modules.map(m=>m.relative_path).sort());
  fs.renameSync(f.source,path.join(f.temp,'moved-source'));assert.deepEqual(planConfiguredEnums(f.fields,f.selection,sources),p);
  assert.throws(()=>planConfiguredEnums(structuredClone(f.fields),f.selection,sources),/PROJECT_FIELD_UNCHECKED/);
  assert.ok(Object.isFrozen(p.modules[0]!.members));assert.ok(Object.isFrozen(p.artifacts));
});

test('PCR-06 Enum planner rejects drift, unsafe paths, unknown options and provider name collisions',t=>{
  const f=fixture(t);
  for(const key of ['configuration','base','typescript','provider']) assert.throws(()=>planConfiguredEnums(f.fields,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
  for(const change of [{schema_version:'future'},{language:'rust'},{field_compilation_sha256:'0'.repeat(64)},{module_root:'../escape'},{module_root:'/absolute'},{module_root:'con'},{module_root:'a/class'},{module_root:'lpt9'},{ignore_blockers:true}]) assert.throws(()=>planConfiguredEnums(f.fields,{...f.selection,...change} as any,sources));
  let reads=0;const accessor={...f.selection,get language(){reads++;return 'typescript';}};
  assert.throws(()=>planConfiguredEnums(f.fields,accessor as any,sources));assert.equal(reads,0);
  assert.throws(()=>planConfiguredEnums(f.fields,{...f.selection,[Symbol('hidden')]:true},sources));
  for(const node of ['con','enum-value']){const g=fixture(t,node);assert.throws(()=>planConfiguredEnums(g.fields,g.selection,sources),/portable identifier|symbol collision/);}
});

test('PCR-06 Enum planner never erases sum payloads or silently filters Entity declarations',t=>{
  const sum=fixture(t,'status',true);assert.throws(()=>planConfiguredEnums(sum.fields,sum.selection,sources),/payload-bearing sum unsupported/);
  const mixed=fixture(t,'status',false,true);assert.throws(()=>planConfiguredEnums(mixed.fields,mixed.selection,sources),/unsupported declaration kind/);
});

test('PCR-06 Enum native compilation preserves owned runtime composition and exact values',t=>{
  const f=fixture(t),p=planConfiguredEnums(f.fields,f.selection,sources),root=path.join(f.temp,'target'),n=native(root,p.artifacts),e=expected();
  assert.equal(n.observe().result,'pass');
  const {Status}=loadJs(root,e.modules[1]!.path),{Status:AuditStatus}=loadJs(root,e.modules[0]!.path);
  const {defineEnum,composeEnum}=loadJs(root,e.provider.path);
  assert.deepEqual(Object.keys(Status),['Draft','Submitted']);assert.deepEqual(Object.values(Status),['Draft','Submitted']);assert.ok(Object.isFrozen(Status));
  for(const name of ['Draft','Submitted']) assert.equal(compiledFieldValueKey(f.fields,'commerce:status',{variant:Status[name]}),compiledFieldValueKey(f.fields,'commerce:status',{variant:name}));
  assert.throws(()=>compiledFieldValueKey(f.fields,'commerce:status',Status.Draft),'wire strings are not the field model tagged-value representation');
  const combined=composeEnum({Status,AuditStatus});assert.ok(Object.isFrozen(combined));assert.deepEqual(Object.keys(combined).sort(),['Draft','Pending','Recorded','Submitted']);
  assert.throws(()=>composeEnum({Fake:{Draft:'Draft'}}));assert.throws(()=>composeEnum({Status,Again:Status}));
  assert.throws(()=>defineEnum({One:'same',Two:'same'}));
  assert.throws(()=>{Status.Draft='Changed';},TypeError);
  const positive=path.join(root,'consumer.ts');
  fs.writeFileSync(positive,'import {Status} from "./application/features/commerce/src/domain/enums/status.js";\nexport const valid:Status = Status.Draft;\n');n.compile([positive]);
  fs.writeFileSync(positive,'import type {Status} from "./application/features/commerce/src/domain/enums/status.js";\nexport const invalid:Status = "Unknown";\n');
  assert.throws(()=>n.compile([positive]),(error:any)=>/not assignable/.test(String(error.stdout)));
});

test('PCR-06 independent native AST observation rejects missing members, bypasses and provider drift',t=>{
  const f=fixture(t),p=planConfiguredEnums(f.fields,f.selection,sources),root=path.join(f.temp,'mutants'),n=native(root,p.artifacts),e=expected();
  const file=path.join(root,e.modules[1]!.path),original=fs.readFileSync(file,'utf8');
  const mutants=[
    ['wrong wire',original.replace('"Draft":"Draft"','"Draft":"Wrong"'),'member-set:'],
    ['missing member',original.replace(',"Submitted":"Submitted"',''),'member-set:'],
    ['bare object',original.replace('defineEnum({','({'),'owned-call:'],
    ['wrong import',original.replaceAll('runtime/enum.js','runtime/forged.js'),'import-binding:'],
    ['extra export',original+'export const bypass = true;\n','export-set:'],
    ['mutable declaration',original.replace('export const Status','export let Status'),'const-form:'],
    ['erased type',original.replace('EnumValue<typeof Status>','string'),'value-type:'],
    ['computed member',original.replace('"Draft":','["Draft"]:'),'static-member:']];
  for(const [name,mutant,reason] of mutants){assert.notEqual(mutant,original,name);fs.writeFileSync(file,mutant!);assert.ok(n.observe().errors.some((s:string)=>s.startsWith(reason!)),name);}
  fs.writeFileSync(file,original);
  const provider=path.join(root,e.provider.path);fs.appendFileSync(provider,'\n// drift\n');assert.ok(n.observe().errors.includes('provider-digest'));
  fs.writeFileSync(provider,sources.provider);assert.equal(n.observe().result,'pass');
});

test('PCR-06 compiled semantic mutant is detected independently; overlapping string values are not nominally distinct',t=>{
  const f=fixture(t),p=planConfiguredEnums(f.fields,f.selection,sources),e=expected();
  const artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===e.modules[1]!.path?a.content.replace('"Draft":"Draft"','"Draft":"Recorded"'):a.content}));
  const root=path.join(f.temp,'semantic'),n=native(root,artifacts);
  const {Status}=loadJs(root,e.modules[1]!.path),{Status:AuditStatus}=loadJs(root,e.modules[0]!.path);
  assert.notEqual(Status.Draft,'Draft');assert.equal(Status.Draft,AuditStatus.Recorded,'the provider brands Enum objects, not each raw string value');
  assert.throws(()=>compiledFieldValueKey(f.fields,'commerce:status',{variant:Status.Draft}));
  assert.ok(n.observe().errors.some((s:string)=>s.startsWith('member-set:')));
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
