import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileSelectedProjectFields, compiledFieldValueKey, PROJECT_FIELD_SELECTION_VERSION, FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredFactories, CONFIGURED_FACTORY_VERSION, COMPOSED_FACTORY_VERSION, COLLECTION_FACTORY_VERSION, type ConfiguredFactorySelection, type FactoryValidatorBinding, type ConfiguredFactoryModule, type FactoryBinding} from '../../src/generation/configured-factories.ts';
import {renderConfiguredFactory} from '../../src/generation/configured-factory-source.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {ENUM_FIELD_FACTORY_VERSION} from '../../src/generation/configured-factories.ts';
import {SUM_FIELD_FACTORY_VERSION} from '../../src/generation/configured-factories.ts';
import {UINT64_FIELD_FACTORY_VERSION} from '../../src/generation/configured-factories.ts';
import {REFERENCE_FIELD_FACTORY_VERSION} from '../../src/generation/configured-factories.ts';
import {EMBEDDED_ENTITY_FACTORY_VERSION} from '../../src/generation/configured-factories.ts';
import {ENTITY_RULE_PATH_FACTORY_VERSION} from '../../src/generation/configured-factories.ts';
import {RULE_COMPOSITION_FACTORY_VERSION, RULE_COMPOSITION_FACTORY_CONTRACT_SHA256} from '../../src/generation/configured-factories.ts';
import {planConfiguredRules, NUMERIC_RULE_VERSION} from '../../src/generation/configured-rules.ts';
import {NUMERIC_RULE_VALUE_PROFILE} from '../../src/generation/configured-rule-numeric.ts';
import {renderConfiguredSum, type ValueShape} from '../../src/generation/configured-sum-source.ts';
import {planConfiguredEnums, CONFIGURED_ENUM_VERSION, type ConfiguredEnumSelection} from '../../src/generation/configured-enums.ts';
import {EXACT_CONFIGURED_ENUM_VERSION} from '../../src/generation/configured-enums.ts';
import {EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {EXACT_FACTORY_VERSION, EXACT_FACTORY_CONTRACT_SHA256} from '../../src/generation/configured-factories.ts';
import {EXACT_RULE_VERSION, EXACT_LITERAL_RULE_VERSION} from '../../src/generation/configured-rules.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {STRUCTURED_FACTORY_VERSION,STRUCTURED_FACTORY_CONTRACT_SHA256} from '../../src/generation/configured-factories.ts';
import {STRUCTURED_RULE_VERSION} from '../../src/generation/configured-rules.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const read=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
const packagePath='development/reconciliation-v1/profile-compiler-reconciliation';
const descriptor=read('development/reconciliation-v1/contracts/field-and-reference-model.json');
const sources={configuration:read(packagePath+'/configuration.json'),
  base:read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  typescript:read('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
  factory_contract:read(packagePath+'/scalar-factory-contract.json')};
const bind=(rule:string,parameter:string,field:string):FactoryValidatorBinding=>({rule,arguments:[{parameter,field}]});
const assertDeterministicDistinctKinds=(module:ConfiguredFactoryModule):void=>{
  const valueObject=renderConfiguredFactory(module),entity=renderConfiguredFactory({...module,kind:'Entity'});
  assert.equal(valueObject,renderConfiguredFactory(module));
  assert.equal(entity,renderConfiguredFactory({...module,kind:'Entity'}));
  assert.notEqual(sha256(valueObject),sha256(entity));
};
function fixture(t:any) {
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'pcr06-factories-'));
  t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');
  const write=(relative:string,value:unknown)=>{const file=path.join(source,relative);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
  write('project.json',{schema_version:'domainspec.project/v1',project_id:'factory-fixture',features:['commerce','audit'],cross_feature_edges:[]});
  write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes:['customer','contact','valid-id','is-visible'],edges:[]});
  write('specs/audit/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'audit',nodes:['has-label','is-enabled'],edges:[]});
  for(const [selector,parameter,scalar] of [['commerce:valid-id','value','String'],['audit:has-label','label','String'],['audit:is-enabled','enabled','Bool'],['commerce:is-visible','flag','Bool']]) {
    const [feature_id,node_id]=selector!.split(':');
    const eq={op:'eq',left:{op:'path',root:parameter,properties:[]},right:{op:'literal',type:scalar,value:scalar==='Bool'?true:''}};
    write(`specs/${feature_id}/nodes/${node_id}.json`,{schema_version:'domainspec.node/v1',feature_id,node_id,kind:'Rule',body:{description:selector,predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FIXTURE-RULE',parameters:[{name:parameter,type:{kind:'scalar',name:scalar}}],expression:scalar==='Bool'?eq:{op:'not',term:eq}}}});
  }
  for(const [node_id,kind,names] of [['customer','Entity',['id','label','enabled']],['contact','Value Object',['locale','label','enabled']]] as const) {
    write(`specs/commerce/nodes/${node_id}.json`,{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id,kind,body:{description:node_id,fields:names,...(kind==='Value Object'?{invariant_refs:['audit:has-label']}:{ }),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+node_id.toUpperCase(),properties:names.map(name=>({ontology_property:'FIXTURE-'+node_id.toUpperCase()+'#'+name,name,type:{kind:'scalar',name:name==='enabled'?'Bool':'String'},identity:name==='id',cardinality:'one',meaning:name}))}}});
  }
  const recompile=()=>{
    const graph=loadCompiledProjectGraph(source);
    const fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:['commerce:customer','commerce:contact'],bindings:[]},descriptor);
    const extensions=[{id:'enabled',validators:[bind('audit:is-enabled','enabled','enabled')]},{id:'visible',validators:[bind('commerce:is-visible','flag','enabled')]}];
    const selection:ConfiguredFactorySelection={schema_version:CONFIGURED_FACTORY_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:fields.compilation_sha256,factories:[
      {selector:'commerce:customer',base_validators:[bind('commerce:valid-id','value','id'),bind('audit:has-label','label','label')],extensions},
      {selector:'commerce:contact',base_validators:[bind('audit:has-label','label','label')],extensions}]};
    return {graph,fields,selection};
  };
  return {temp,source,write,recompile,...recompile()};
}
const paths={customer:'application/features/commerce/src/domain/entities/customer.ts',contact:'application/features/commerce/src/domain/value-objects/contact.ts'};
const rulePaths=['application/features/audit/src/domain/rules/has-label.ts','application/features/audit/src/domain/rules/is-enabled.ts','application/features/commerce/src/domain/rules/is-visible.ts','application/features/commerce/src/domain/rules/valid-id.ts'];
const call=(rule:string,local:string,param:string,field:string)=>({rule,call:`${local}({["${param}"]:fields["${field}"]})`});
const expected=()=>({files:[...rulePaths,paths.customer,paths.contact],modules:[
  {path:paths.contact,name:'Contact',imports:[{path:'../../../../audit/src/domain/rules/has-label.js',symbol:'ruleHasLabel',local:'validator0'},{path:'../../../../audit/src/domain/rules/is-enabled.js',symbol:'ruleIsEnabled',local:'validator1'},{path:'../rules/is-visible.js',symbol:'ruleIsVisible',local:'validator2'}],base:[call('audit:has-label','validator0','label','label')],extensions:[{id:'enabled',validators:[call('audit:is-enabled','validator1','enabled','enabled')]},{id:'visible',validators:[call('commerce:is-visible','validator2','flag','enabled')]}]},
  {path:paths.customer,name:'Customer',imports:[{path:'../../../../audit/src/domain/rules/has-label.js',symbol:'ruleHasLabel',local:'validator0'},{path:'../../../../audit/src/domain/rules/is-enabled.js',symbol:'ruleIsEnabled',local:'validator1'},{path:'../rules/is-visible.js',symbol:'ruleIsVisible',local:'validator2'},{path:'../rules/valid-id.js',symbol:'ruleValidId',local:'validator3'}],base:[call('commerce:valid-id','validator3','value','id'),call('audit:has-label','validator0','label','label')],extensions:[{id:'enabled',validators:[call('audit:is-enabled','validator1','enabled','enabled')]},{id:'visible',validators:[call('commerce:is-visible','validator2','flag','enabled')]}]}
]});
function native(root:string,artifacts:readonly {relative_path:string;content:string}[], expectation:unknown=expected()) {
  for(const a of artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content,{flag:'wx'});}
  const toolchain=JSON.parse(read('../../toolchains/node-typescript/toolchain.json'));
  const image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root}`,'--workdir',root,image,'tsc'];
  assert.equal(execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
  const compile=(extra:string[]=[])=>execFileSync('docker',[...args,'--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--declaration','--rootDir',root,'--outDir',path.join(root,'js'),...artifacts.map(a=>path.join(root,a.relative_path)),...extra],{encoding:'utf8',stdio:'pipe'});
  compile();
  fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:(expectation as any).files}));
  fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(expectation));
  return {compile,observe:()=>{
    const observer=path.join(project,'impl/cli/tools/observe-configured-factories.mjs');
    const command=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root},readonly`,'--mount',`type=bind,source=${observer},target=/observer.mjs,readonly`,image,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')];
    try{return JSON.parse(execFileSync('docker',command,{encoding:'utf8',stdio:'pipe'}));}catch(error){const e=error as any;if(e.status===1&&e.stdout)return JSON.parse(e.stdout);throw error;}
  }};
}
const loadJs=(root:string,p:string)=>createRequire(import.meta.url)(path.join(root,'js',p.replace(/\.ts$/,'.js')));
type CustomerFixtureFields={id:string;label:string;enabled:boolean};
type ContactFixtureFields={locale:string;label:string;enabled:boolean};
type FixtureSpread<Base,Patch>=Omit<Base,keyof Patch>&Patch;
function customer():CustomerFixtureFields;
function customer<P extends object>(patch:P):FixtureSpread<CustomerFixtureFields,P>;
function customer(patch:object={}){return {id:'customer-a',label:'Alex',enabled:true,...patch};}
function contact():ContactFixtureFields;
function contact<P extends object>(patch:P):FixtureSpread<ContactFixtureFields,P>;
function contact(patch:object={}){return {locale:'en',label:'Alex',enabled:true,...patch};}
const traceRules=(r:any)=>r.trace.validators.map((v:any)=>v.rule);

const collectionSources={...sources,factory_contract:read(packagePath+'/collection-factory-contract.json')};
const collectionSupportHash='1ea6b79deeab706c017a45f31cbeb96b743a5bcce09215cbfe73160c5cb1c30a';
const enumSources={...sources,factory_contract:read(packagePath+'/enum-field-factory-contract.json'),
  field_contract:descriptor,enum_provider:read('impl/architecture-conformance/typescript/runtime/enum/index.ts')};
const enumSupportHash='2510c2e218268adf0d5e3b0ba6344ff8510d8f32323c47680cf757882ae54c04';
const enumContractHash='a7eedabc1db6145afc50060d5fba762110bee91bd7f3bb7d8f23bf99b7f8d5ab';
const sumSources={...enumSources,factory_contract:read(packagePath+'/sum-field-factory-contract.json')};
const sumContractHash='f64f0b8bfb57a56cc676737e32e7a727e9c50caf9822f720d0585df7fdc10da2';
const sumSupportHash='c38fecb931c6c9cf81846555734925735e3ad04c492f697438fb8a097a898e6e';
const uintSources={...enumSources,factory_contract:read(packagePath+'/uint64-field-factory-contract.json')};
const uintContractHash='9b77a5827bef588b8f28cdac0efd65b4f1f39b837d8791b4b5d1cb4c7b990665';
const uintSupportHash='04125d6abc0e3bb18a624aa0b7390ac4958b0957ea634fdc800ab7135c91c3f9';
const uintMax=9007199254740991;
const referenceSources={...enumSources,factory_contract:read(packagePath+'/reference-field-factory-contract.json')};
const referenceContractHash='063b6d3228abfdedff01b0f743393ac8138d41af0b592071985a4686e083036f';
const entitySources={...enumSources,factory_contract:read(packagePath+'/embedded-entity-factory-contract.json')};
const entityContractHash='3725392ffac4dc7644779cfb3580905c86428394b7cf27f13f489fd8193649d7';
const entitySupportHash='f93c0ab11dae3236777ac2f05b12db8b4f64579842d3f9cf7b14aad448ba735f';
const deliveryPath='application/features/audit/src/domain/enums/delivery-choice.sum.ts';
const entityRuleSources={...entitySources,factory_contract:read(packagePath+'/entity-rule-path-factory-contract.json')};
const entityRuleContractHash='504bc456b793e87091c5133b4dda408f7233f266eb33994d19d04f298500644d';
function entityRuleFixture(t:any){
  const f=embeddedFixture(t),selection=structuredClone(f.selection) as any;
  selection.factories=selection.factories.map((factory:any)=>structuredClone(factory));
  selection.schema_version=ENTITY_RULE_PATH_FACTORY_VERSION;
  const contact=selection.factories.find((x:any)=>x.selector==='commerce:contact');
  contact.base_validators=[bindPath('audit:has-label','label','z_parent','z_child','label')];
  contact.extensions[0].validators=[bindPath('audit:is-enabled','enabled','z_entity','enabled')];
  contact.extensions[1].validators=[bindPath('commerce:is-visible','flag','z_parent','z_child','enabled')];
  const account=selection.factories.find((x:any)=>x.selector==='audit:account');
  account.base_validators[0]=bindPath('commerce:valid-id','value','z_child','label');
  account.extensions[0].validators=[bindPath('audit:is-enabled','enabled','z_child','enabled')];
  return {...f,selection:selection as ConfiguredFactorySelection};
}
function entityRuleExpected():any{
  const e=embeddedExpected(),contact=e.modules.find((m:any)=>m.name==='Contact'),account=e.modules.find((m:any)=>m.name==='Account');
  contact.base=[{rule:'audit:has-label',call:'validator0({["label"]:fields["z_parent"].fields["z_child"].fields["label"]})'}];
  contact.extensions[0].validators=[{rule:'audit:is-enabled',call:'validator1({["enabled"]:fields["z_entity"].fields["enabled"]})'}];
  contact.extensions[1].validators=[{rule:'commerce:is-visible',call:'validator2({["flag"]:fields["z_parent"].fields["z_child"].fields["enabled"]})'}];
  account.base[0]={rule:'commerce:valid-id',call:'validator3({["value"]:fields["z_child"].fields["label"]})'};
  account.extensions[0].validators=[{rule:'audit:is-enabled',call:'validator1({["enabled"]:fields["z_child"].fields["enabled"]})'}];
  e.sum_modules[0].contract_sha256=entityRuleContractHash;
  return e;
}
test('PCR-06 Entity Rule paths bind explicit checked paths deterministically without changing v8',t=>{
  const f=entityRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entityRuleSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v9-candidate');
  assert.equal(p.input_envelope,'explicit-owned-entity-rule-paths/v9-candidate');assert.equal(p.factory_contract_sha256,entityRuleContractHash);
  assert.equal(p.collection_support!.sha256,entitySupportHash);
  const c=p.modules.find(m=>m.name==='Contact')!,b=c.base_validators[0]!;
  assert.deepEqual(b.arguments,[{parameter:'label',path:['z_parent','z_child','label']}]);
  assert.match(b.closure_sha256,/^[a-f0-9]{64}$/);assert.match(b.artifact_sha256,/^[a-f0-9]{64}$/);
  for(const r of p.component_bindings!)assert.equal(r.artifact_sha256,p.artifacts.find(a=>a.relative_path===r.relative_path)!.sha256);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},entityRuleSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'relocated'},entityRuleSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const key of Object.keys(entityRuleSources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...entityRuleSources,[key]:(entityRuleSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:EMBEDDED_ENTITY_FACTORY_VERSION},entitySources),/validator path must traverse owned Value Objects/);
  const legacy=f.recompile(),v8=planConfiguredFactories(legacy.graph,legacy.fields,legacy.selection,entitySources);
  const v9=planConfiguredFactories(legacy.graph,legacy.fields,{...legacy.selection,schema_version:ENTITY_RULE_PATH_FACTORY_VERSION},entityRuleSources);
  assert.deepEqual(v9.artifacts.map(a=>a.content),v8.artifacts.map(a=>a.content.replaceAll(entityContractHash,entityRuleContractHash)));
  const before=canonicalJson(p);(f.selection.factories.find(x=>x.selector==='commerce:contact')!.base_validators[0]!.arguments[0]!.path as string[])[0]='changed';
  assert.equal(canonicalJson(p),before);fs.renameSync(f.source,path.join(f.temp,'moved'));
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,p.selection,entityRuleSources),p);
});
test('PCR-06 native Entity Rule paths separate snapshot state from identity and extension scope',t=>{
  const f=entityRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entityRuleSources),root=path.join(f.temp,'entity-rule-state');
  assert.deepEqual(native(root,p.artifacts,entityRuleExpected()).observe().errors,[]);const r=embeddedRuntime(root);
  const on=r.child({id:1,enabled:true}),off=r.child({id:1,enabled:false});assert.ok(r.c.CustomerValueComponent.equals(on,off));
  const positive=r.input({enabled:false,z_entity:on}),negative=r.input({enabled:true,z_entity:off});
  assert.ok(r.vf.create(negative).ok);assert.ok(r.vf.extend('enabled').create(positive).ok);
  const failed=r.vf.extend('enabled').create(negative);assert.deepEqual(failed.failure_codes,['RULE_FAIL:audit:is-enabled']);
  assert.deepEqual(traceRules(failed),['audit:has-label','audit:is-enabled']);
  const nested=r.input({z_entity:on,z_parent:r.af.create(r.account({z_child:off})).value});
  assert.ok(r.vf.extend('enabled').create(nested).ok);
  assert.deepEqual(r.vf.extend('visible').create(nested).failure_codes,['RULE_FAIL:commerce:is-visible']);
  assert.deepEqual(r.vf.extend('enabled').extend('visible').create(nested).failure_codes,['RULE_FAIL:commerce:is-visible']);
  assert.ok(r.vf.create(nested).ok);assert.ok(r.af.create(r.account({z_child:off})).ok);
  const parent=r.vf.create(r.input({z_entity:on})).value;
  assert.ok(r.cf.transition(on,refCustomer({enabled:false})).ok);assert.equal(parent.fields.z_entity.fields.enabled,true);
});
test('PCR-06 native Entity Rule paths guard every Entity construction route after ownership checks',t=>{
  const f=entityRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entityRuleSources),root=path.join(f.temp,'entity-rule-routes');
  native(root,p.artifacts,entityRuleExpected());const r=embeddedRuntime(root),factory=r.af.extend('enabled'),previous=factory.create(r.account()).value;
  for(const route of ['create','reconstruct','transition']){
    const run=(input:object)=>route==='transition'?factory.transition(previous,input):factory[route](input);
    assert.ok(run(r.account({enabled:false,z_child:r.child({enabled:true})})).ok);
    const failed=run(r.account({z_child:r.child({enabled:false})}));assert.deepEqual(failed.failure_codes,['RULE_FAIL:audit:is-enabled']);
    assert.deepEqual(traceRules(failed),['commerce:valid-id','audit:has-label','audit:is-enabled']);
    let reads=0;const forged={get fields(){reads++;return {label:'valid',enabled:true};}};
    const invalid=run(r.account({z_child:forged}));assert.deepEqual(invalid.failure_codes,['INVALID_FIELDS']);assert.deepEqual(traceRules(invalid),[]);assert.equal(reads,0);
  }
  assert.deepEqual(factory.transition(previous,r.account({id:99})).failure_codes,['IDENTITY_CHANGED']);
});
test('PCR-06 Entity Rule paths reject lookup wrappers non-scalar leaves and invalid bindings',t=>{
  const f=entityRuleFixture(t);
  for(const segments of [[],['missing'],['z_entity'],['z_entity','id'],['z_entity','missing'],['z_entity','label','length'],
    ['z_maybe','enabled'],['z_list','0','enabled'],['z_set','enabled'],['z_named','payload','enabled'],['z_sum','Entity','enabled'],
    ['a_customer','enabled'],['z_entity','a_account','enabled'],['z_entity','enabled'],['z_entity',1],Array(33).fill('z_entity')]){
    const selection=structuredClone(f.selection) as any;
    selection.factories.find((x:any)=>x.selector==='commerce:contact').base_validators=[{rule:'audit:has-label',arguments:[{parameter:'label',path:segments}]}];
    assert.throws(()=>planConfiguredFactories(f.graph,f.fields,selection,entityRuleSources),/DS_CONFIGURED_FACTORY:/);
  }
  const selection=structuredClone(f.selection) as any;selection.factories.find((x:any)=>x.selector==='commerce:contact').base_validators=[];
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,selection,entityRuleSources),/invalid binding list/);
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,entityRuleSources));
});
test('PCR-06 native Entity Rule path mutants detect same-type argument substitution',t=>{
  const f=entityRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entityRuleSources),original=p.artifacts.find(a=>a.relative_path===paths.contact)!.content;
  for(const [id,before,after] of [
    ['owner','validator1({["enabled"]:fields["z_entity"].fields["enabled"]})','validator1({["enabled"]:fields["enabled"]})'],
    ['sibling','validator2({["flag"]:fields["z_parent"].fields["z_child"].fields["enabled"]})','validator2({["flag"]:fields["z_entity"].fields["enabled"]})']]){
    assert.ok(original.includes(before!));const root=path.join(f.temp,'entity-rule-mutant-'+id);
    const n=native(root,p.artifacts.map(a=>({...a,content:a.relative_path===paths.contact?original.replace(before!,after!):a.content})),entityRuleExpected());
    assert.ok(n.observe().errors.includes('extension-binding:'+paths.contact));const r=embeddedRuntime(root);
    const input=id==='owner'?r.input({enabled:true,z_entity:r.child({enabled:false})}):r.input({z_entity:r.child({enabled:true}),z_parent:r.af.create(r.account({z_child:r.child({enabled:false})})).value});
    assert.ok(r.vf.extend(id==='owner'?'enabled':'visible').create(input).ok,'mutant incorrectly passes the independent false child-state oracle');
  }
});
test('PCR-06 native Entity Rule paths compose Value Object Entity Value Object String access',t=>{
  const f=uintFixture(t),feature=JSON.parse(fs.readFileSync(path.join(f.source,'specs/audit/feature.json'),'utf8'));feature.nodes.push('bundle');f.write('specs/audit/feature.json',feature);
  f.write('specs/audit/nodes/bundle.json',{schema_version:'domainspec.node/v1',feature_id:'audit',node_id:'bundle',kind:'Value Object',body:{description:'Entity holder',
    fields:['child'],invariant_refs:['audit:has-label'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-BUNDLE',properties:[
      {name:'child',type:{kind:'named',selector:'commerce:customer'},identity:false,cardinality:'one',ontology_property:'FIXTURE-BUNDLE#child',meaning:'Embedded child'}]}}});
  const g=f.recompile(),fields=compileSelectedProjectFields(g.graph,{...g.fields.selection,roots:[...g.fields.selection.roots,'audit:bundle']},descriptor);
  const selection:ConfiguredFactorySelection={...g.selection,schema_version:ENTITY_RULE_PATH_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256,
    factories:[...g.selection.factories,{selector:'audit:bundle',base_validators:[bindPath('audit:has-label','label','child','contact','locale')],extensions:[]}]};
  const p=planConfiguredFactories(g.graph,fields,selection,entityRuleSources),e=uintExpected(),bundle='application/features/audit/src/domain/value-objects/bundle.ts';
  for(const m of e.modules){m.collection_support_sha256=entitySupportHash;m.reference_bindings=[];if(m.name==='Customer'){m.provider='commerce:customer';m.entity_provider=true;}}
  for(const m of e.enum_components)m.contract_sha256=entityRuleContractHash;
  for(const m of e.sum_modules){m.contract_sha256=entityRuleContractHash;m.support_sha256=entitySupportHash;}
  e.files.push(bundle);e.modules.push({path:bundle,name:'Bundle',composed:true,provider:'audit:bundle',reference_bindings:[],
    imports:[{path:'../rules/has-label.js',symbol:'ruleHasLabel',local:'validator0'},...sumDep('../../../../commerce/src/domain/entities/customer.js','Customer','component0','Snapshot')],
    base:[{rule:'audit:has-label',call:'validator0({["label"]:fields["child"].fields["contact"].fields["locale"]})'}],extensions:[],collection_support_sha256:entitySupportHash,collection_protocols:['ownedEntityValue(component0)']});
  const root=path.join(f.temp,'entity-rule-mixed');assert.deepEqual(native(root,p.artifacts,e).observe().errors,[]);
  const r=uintRuntime(root),bf=loadJs(root,bundle).createBundleFactory();
  const good=r.ef.create(r.input()),bad=r.ef.create(r.input({contact:r.vf.create(r.base({locale:''})).value}));
  assert.ok(good.ok);assert.ok(bad.ok);assert.ok(bf.create({child:good.value}).ok);
  const rejected=bf.create({child:bad.value});assert.deepEqual(rejected.failure_codes,['RULE_FAIL:audit:has-label']);
  assert.deepEqual(traceRules(rejected),['audit:has-label']);
});
function embeddedReferences(){const bindings=simpleReferences();const b=bindings.find(r=>r.owner==='commerce:contact'&&r.field==='label')!;
  b.target='audit:account';b.projection=['z_child','label'];bindings.push(ref('commerce:contact','z_projection','field-projection','audit:account','z_child'));return bindings;}
function embeddedFixture(t:any){
  const f=referenceFixture(t),child={kind:'named',selector:'commerce:customer'},wrap=(kind:string)=>({kind,element:child});
  addReferenceFields(f,'audit:account',{z_child:child});
  addReferenceFields(f,'commerce:contact',{z_entity:child,z_list:wrap('list'),z_matrix:{kind:'list',element:wrap('list')},z_maybe:wrap('optional'),
    z_named:{kind:'named',selector:'audit:delivery-choice'},z_parent:{kind:'named',selector:'audit:account'},z_projection:child,z_set:wrap('set'),
    z_sum:{kind:'sum',variants:[{name:'Entity',payload:child,ontology_variant:'FIXTURE-EMBEDDED#Entity'},
      {name:'None',payload:null,ontology_variant:'FIXTURE-EMBEDDED#None'},
      {name:'Reference',payload:{kind:'scalar',name:'UInt64'},ontology_variant:'FIXTURE-EMBEDDED#Reference'}]}});
  const feature=JSON.parse(fs.readFileSync(path.join(f.source,'specs/audit/feature.json'),'utf8'));feature.nodes.push('delivery-choice');f.write('specs/audit/feature.json',feature);
  f.write('specs/audit/nodes/delivery-choice.json',{schema_version:'domainspec.node/v1',feature_id:'audit',node_id:'delivery-choice',kind:'Enum',
    body:{description:'Entity payload choice',values:['Customer','Empty'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-DELIVERY',variants:[
      {name:'Customer',payload:child,ontology_variant:'FIXTURE-DELIVERY#Customer'},{name:'Empty',payload:null,ontology_variant:'FIXTURE-DELIVERY#Empty'}]}}});
  const recompile=()=>{const g=f.recompile(embeddedReferences());return {...g,selection:{...g.selection,schema_version:EMBEDDED_ENTITY_FACTORY_VERSION} as ConfiguredFactorySelection};};
  return {...f,...recompile(),recompile};
}
function embeddedExpected():any{
  const e=referenceExpected(),customer=e.modules.find((m:any)=>m.name==='Customer'),account=e.modules.find((m:any)=>m.name==='Account'),contact=e.modules.find((m:any)=>m.name==='Contact');
  for(const m of e.modules){m.collection_support_sha256=entitySupportHash;m.reference_bindings=embeddedReferences().filter(r=>r.owner===(m.name==='Account'?'audit:account':m.name==='Customer'?'commerce:customer':'commerce:contact'));}
  customer.provider='commerce:customer';customer.entity_provider=true;account.provider='audit:account';account.entity_provider=true;
  account.collection_protocols.push('ownedEntityValue(component4)');
  const ai=account.imports.pop();account.imports.push(...sumDep('../../../../commerce/src/domain/entities/customer.js','Customer','component4','Snapshot'),ai);
  contact.collection_protocols.push('ownedEntityValue(component9)','listValue(ownedEntityValue(component10Element))','listValue(listValue(ownedEntityValue(component11ElementElement)))',
    'optionalValue(ownedEntityValue(component12Element))','ownedSumValue(component13)','ownedEntityValue(component14)','ownedEntityValue(component15)','setValue(ownedEntityValue(component16Element))',
    'sumValue(Object.freeze({["Entity"]:ownedEntityValue(component17Case0),["None"]:null,["Reference"]:uint64Value}))');
  const ci=contact.imports.splice(-7);ci[6].symbol='AccountFields';ci[6].path='../../../../audit/src/domain/entities/account.js';
  for(const local of ['component9','component10Element','component11ElementElement','component12Element'])contact.imports.push(...sumDep('../entities/customer.js','Customer',local,'Snapshot'));
  contact.imports.push(...sumDep('../../../../audit/src/domain/enums/delivery-choice.sum.js','DeliveryChoice','component13'),
    ...sumDep('../../../../audit/src/domain/entities/account.js','Account','component14','Snapshot'));
  for(const local of ['component15','component16Element','component17Case0'])contact.imports.push(...sumDep('../entities/customer.js','Customer',local,'Snapshot'));
  contact.imports.push(...ci,{path:'../../../../audit/src/domain/entities/account.js',symbol:'AccountFields',local:'referenceTarget7Fields',type_only:true});
  contact.reference_types.label='referenceTarget6Fields["z_child"]["fields"]["label"]';contact.reference_types.z_projection='referenceTarget7Fields["z_child"]';
  e.files.push(deliveryPath);e.sum_modules=[{path:deliveryPath,name:'DeliveryChoice',selector:'audit:delivery-choice',
    imports:sumDep('../../../../commerce/src/domain/entities/customer.js','Customer','payloadCase0','Snapshot'),
    protocol:'sumValue(Object.freeze({["Customer"]:ownedEntityValue(payloadCase0),["Empty"]:null}))',contract_sha256:entityContractHash,support_sha256:entitySupportHash}];
  return e;
}
function embeddedRuntime(root:string){
  const c=loadJs(root,paths.customer),a=loadJs(root,accountPath),v=loadJs(root,paths.contact),d=loadJs(root,deliveryPath).DeliveryChoiceValueComponent;
  const cf=c.createCustomerFactory(),af=a.createAccountFactory(),vf=v.createContactFactory();
  const child=(patch:object={})=>cf.create(refCustomer(patch)).value;
  const account=(patch:object={})=>customer({id:5,z_child:child(),...patch});
  const input=(patch:object={})=>refContact({z_entity:child(),z_list:[],z_matrix:[],z_named:d.create({variant:'Empty'}),z_parent:af.create(account()).value,
    z_projection:child(),z_set:[],z_sum:{variant:'None'},...patch});
  return {c,a,v,d,cf,af,vf,child,account,input};
}
const embeddedWire=(input:object)=>Object.fromEntries(Object.entries(input).map(([k,v])=>[k,sumWire(v)]));
test('PCR-06 embedded Entities emit selective deterministic support and closed checked dependency selection',t=>{
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',protocol_id:'typescript.owned-value-object-factory/v1',
    fields:[{name:'id',tag:'UInt64',identity:true,wrappers:[],value_shape:{kind:'UInt64'}},{name:'ref',tag:'UInt64',identity:false,wrappers:[],value_shape:{kind:'UInt64'}}],
    imports:[],base_validators:[],extensions:[],component_protocol_sha256:'reference',composed:true,collections:true,enum_fields:true,sum_fields:true,uint64_fields:true,
    reference_bindings:[{owner:'test:sample',field:'ref',kind:'identity-reference',target:'test:sample',projection:['id'],target_path:'sample.ts',target_type:'SampleFields',type_import:null,wrappers:[]}]};
  assertDeterministicDistinctKinds(m);
  const f=embeddedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entitySources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v8-candidate');assert.equal(p.collection_support!.sha256,entitySupportHash);
  assert.equal(p.modules.find(m=>m.name==='Contact')!.fields.find(f=>f.name==='z_entity')!.tag,'Entity');
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:REFERENCE_FIELD_FACTORY_VERSION},referenceSources),/unsupported sum payload|fields only/);
  for(const key of Object.keys(entitySources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...entitySources,[key]:(entitySources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,entitySources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:f.selection.factories.filter(x=>x.selector!=='commerce:customer')},entitySources),/factory coverage/);
  for(const b of p.component_bindings!)assert.equal(b.artifact_sha256,p.artifacts.find(a=>a.relative_path===b.relative_path)!.sha256);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},entitySources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'relocated/root'},entitySources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  fs.renameSync(f.source,path.join(f.temp,'moved'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,entitySources),p);
});
test('PCR-06 native embedded Entities compare by identity through parents collections and sums',t=>{
  const f=embeddedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entitySources),root=path.join(f.temp,'embedded-equality');
  assert.deepEqual(native(root,p.artifacts,embeddedExpected()).observe().errors,[]);const r=embeddedRuntime(root);
  const a=r.child({id:1,label:'first'}),same=r.child({id:1,label:'second'}),other=r.child({id:2,label:'first'});
  assert.ok(r.c.CustomerValueComponent.equals(a,same));assert.equal(r.c.CustomerValueComponent.equals(a,other),false);
  const patches=[{z_entity:a},{z_entity:same},{z_entity:other},{z_list:[a,same]},{z_list:[same,a]},{z_list:[a,other]},{z_list:[other,a]},
    {z_set:[a,other]},{z_set:[other,a]},{z_matrix:[[a],[other]]},{z_maybe:a},{z_maybe:same},{z_maybe:null},
    {z_sum:{variant:'Entity',payload:a}},{z_sum:{variant:'Entity',payload:same}},{z_sum:{variant:'Reference',payload:1}},
    {z_named:r.d.create({variant:'Customer',payload:a})},{z_named:r.d.create({variant:'Customer',payload:same})},
    {z_parent:r.af.create(r.account({id:5,label:'changed',z_child:other})).value},{z_projection:other}];
  const rows=patches.map(patch=>{const input=r.input(patch),result=r.vf.create(input);assert.ok(result.ok);return {value:result.value,key:compiledFieldValueKey(f.fields,'commerce:contact',embeddedWire(input))};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  assert.equal(r.vf.create(r.input({z_set:[a,same]})).ok,false);assert.ok(r.vf.create(r.input({z_list:[a,same]})).ok);
  const parent=r.vf.create(r.input({z_entity:a})).value;assert.equal(parent.fields.z_entity.fields.label,'first');
  const updated=r.cf.transition(a,refCustomer({id:1,label:'later'}));assert.ok(updated.ok);assert.equal(parent.fields.z_entity.fields.label,'first');
  assert.ok(parent.components.some((c:any)=>c.field==='z_entity'&&c.tag==='Entity'));
  assert.equal(typeof parent.fields.a_customer,'number');assert.ok(Object.isFrozen(parent.fields.z_entity));
});
test('PCR-06 native embedded Entity ownership rejects raw forged wrong and duplicate providers',t=>{
  const f=embeddedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entitySources),root=path.join(f.temp,'embedded-ownership');
  native(root,p.artifacts,embeddedExpected());const r=embeddedRuntime(root),a=r.child();let reads=0;
  const hostile={get fields(){reads++;return a.fields;}};
  const wrong=[1,refCustomer(),{...a},r.af.create(r.account({id:1})).value,hostile,new Proxy(a,{})];
  const duplicate=path.join(f.temp,'other-module');native(duplicate,p.artifacts,embeddedExpected());wrong.push(embeddedRuntime(duplicate).child());
  for(const value of wrong){
    assert.equal(r.c.CustomerValueComponent.isOwned(value),false);assert.throws(()=>r.c.CustomerValueComponent.key(value));
    for(const patch of [{z_entity:value},{z_list:[value]},{z_maybe:value},{z_set:[value]},{z_projection:value},{z_sum:{variant:'Entity',payload:value}}]){
      const result=r.vf.create(r.input(patch));assert.deepEqual(result.failure_codes,['INVALID_FIELDS']);assert.deepEqual(result.trace.validators,[]);
    }
    assert.throws(()=>r.d.create({variant:'Customer',payload:value}));
  }
  assert.equal(reads,0);assert.equal(r.c.CustomerValueComponent.isOwned(r.c.CustomerValueComponent),false);
});
test('PCR-06 native embedded Entity validation and transitions remain local and additive',t=>{
  const f=embeddedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entitySources),root=path.join(f.temp,'embedded-validation');native(root,p.artifacts,embeddedExpected());const r=embeddedRuntime(root);
  assert.equal(r.cf.create(refCustomer({label:''})).ok,false);assert.equal(r.cf.extend('enabled').create(refCustomer({enabled:false})).ok,false);
  const baseChild=r.cf.create(refCustomer({enabled:false}));assert.ok(baseChild.ok);assert.ok(r.vf.create(r.input({z_entity:baseChild.value})).ok);
  assert.equal(r.vf.extend('enabled').create(r.input({enabled:false})).ok,false);
  const previous=r.af.create(r.account()).value;
  for(const route of ['create','reconstruct','transition']){
    const input=r.account({z_child:refCustomer()}),result=route==='transition'?r.af.transition(previous,input):r.af[route](input);
    assert.deepEqual(result.failure_codes,['INVALID_FIELDS']);assert.deepEqual(result.trace.validators,[]);
  }
  assert.ok(r.af.transition(previous,r.account({z_child:r.child({id:99})})).ok);
  assert.deepEqual(r.af.transition(previous,r.account({id:99})).failure_codes,['IDENTITY_CHANGED']);
  const list=[r.child()],parent=r.vf.create(r.input({z_list:list})).value;list.push(r.child({id:2}));assert.equal(parent.fields.z_list.length,1);assert.ok(Object.isFrozen(parent.fields.z_list));
});
test('PCR-06 embedded Entities reject cyclic values Entity identity and implicit Entity Rule paths',t=>{
  const f=embeddedFixture(t),selection=structuredClone(f.selection);
  (selection.factories.find(x=>x.selector==='commerce:contact') as any).base_validators=[bindPath('audit:has-label','label','z_entity','label')];
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,selection,entitySources),/validator path must traverse owned Value Objects/);
  addReferenceFields(f,'commerce:customer',{z_back:{kind:'optional',element:{kind:'named',selector:'commerce:contact'}}});
  assert.throws(()=>f.recompile(),/FIELD_EMBEDDING_CYCLE/);
  const g=referenceFixture(t),node=JSON.parse(fs.readFileSync(path.join(g.source,'specs/commerce/nodes/customer.json'),'utf8'));
  node.body.typed_contract.properties.find((p:any)=>p.name==='id').type={kind:'named',selector:'audit:account'};g.write('specs/commerce/nodes/customer.json',node);
  assert.throws(()=>g.recompile(),/FIELD_IDENTITY_TYPE/);
});
test('PCR-06 native embedded Entity types retain snapshot identity and recursive readonly fields',t=>{
  const f=embeddedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entitySources),root=path.join(f.temp,'embedded-types'),n=native(root,p.artifacts,embeddedExpected());
  const file=path.join(root,'consumer.ts'),prefix='import type {ContactFields} from "./'+paths.contact.replace('.ts','.js')+'";\nimport type {AccountSnapshot} from "./'+accountPath.replace('.ts','.js')+'";\n';
  fs.writeFileSync(file,prefix+'declare const x:ContactFields;const id:number=x.z_entity.fields.id;const name:string=x.z_parent.fields.z_child.fields.label;\n');n.compile([file]);
  for(const code of ['const x:ContactFields["z_entity"]=1;','declare const a:AccountSnapshot;const x:ContactFields["z_entity"]=a;',
    'declare const x:ContactFields;x.z_entity.fields.label="changed";','declare const x:ContactFields;x.z_set.push(x.z_entity);']){
    fs.writeFileSync(file,prefix+code);assert.throws(()=>n.compile([file]),(e:any)=>{assert.match(String(e.stdout),/consumer\.ts.*TS(?:2322|2741|2540|2339)/);return true;});
  }
});
test('PCR-06 native embedded Entity mutants expose identity collapse and accidental record equality',t=>{
  const f=embeddedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,entitySources),original=p.artifacts.find(a=>a.relative_path===paths.customer)!.content;
  const before="return snapshots.get(value)!.key;";
  for(const [id,after] of [['collapse',"return 'one-key';"],['record-equality',"return snapshots.get(value)!.key + snapshots.get(value)!.fields.label;"]]){
    assert.ok(original.includes(before));const root=path.join(f.temp,id),n=native(root,p.artifacts.map(a=>({...a,content:a.relative_path===paths.customer?original.replace(before,after):a.content})),embeddedExpected());
    assert.ok(n.observe().errors.includes('entity-provider:'+paths.customer));const r=embeddedRuntime(root);
    const a=r.input({z_entity:r.child({id:1,label:'first'})}),b=r.input({z_entity:r.child({id:id==='collapse'?2:1,label:'second'})});
    const va=r.vf.create(a).value,vb=r.vf.create(b).value;
    assert.notEqual(va.equals(vb),compiledFieldValueKey(f.fields,'commerce:contact',embeddedWire(a))===compiledFieldValueKey(f.fields,'commerce:contact',embeddedWire(b)));
  }
});
test('PCR-06 native embedded Entity composite identities preserve checked equality in a Value Object',t=>{
  const f=uintFixture(t),feature=JSON.parse(fs.readFileSync(path.join(f.source,'specs/audit/feature.json'),'utf8'));feature.nodes.push('bundle');f.write('specs/audit/feature.json',feature);
  f.write('specs/audit/nodes/bundle.json',{schema_version:'domainspec.node/v1',feature_id:'audit',node_id:'bundle',kind:'Value Object',body:{description:'Entity holder',
    fields:['child','label'],invariant_refs:['audit:has-label'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-BUNDLE',properties:[
      {name:'child',type:{kind:'named',selector:'commerce:customer'},identity:false,cardinality:'one',ontology_property:'FIXTURE-BUNDLE#child',meaning:'Embedded child'},
      {name:'label',type:{kind:'scalar',name:'String'},identity:false,cardinality:'one',ontology_property:'FIXTURE-BUNDLE#label',meaning:'Bundle label'}]}}});
  const g=f.recompile(),fields=compileSelectedProjectFields(g.graph,{...g.fields.selection,roots:[...g.fields.selection.roots,'audit:bundle']},descriptor);
  const selection:ConfiguredFactorySelection={...g.selection,schema_version:EMBEDDED_ENTITY_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256,
    factories:[...g.selection.factories,{selector:'audit:bundle',base_validators:[bind('audit:has-label','label','label')],extensions:[]}]};
  const p=planConfiguredFactories(g.graph,fields,selection,entitySources),e=uintExpected(),bundle='application/features/audit/src/domain/value-objects/bundle.ts';
  for(const m of e.modules){m.collection_support_sha256=entitySupportHash;m.reference_bindings=[];if(m.name==='Customer'){m.provider='commerce:customer';m.entity_provider=true;}}
  for(const m of e.enum_components)m.contract_sha256=entityContractHash;
  for(const m of e.sum_modules){m.contract_sha256=entityContractHash;m.support_sha256=entitySupportHash;}
  e.files.push(bundle);e.modules.push({path:bundle,name:'Bundle',composed:true,provider:'audit:bundle',reference_bindings:[],
    imports:[{path:'../rules/has-label.js',symbol:'ruleHasLabel',local:'validator0'},...sumDep('../../../../commerce/src/domain/entities/customer.js','Customer','component0','Snapshot')],
    base:[call('audit:has-label','validator0','label','label')],extensions:[],collection_support_sha256:entitySupportHash,collection_protocols:['ownedEntityValue(component0)','stringValue']});
  const root=path.join(f.temp,'embedded-composite');assert.deepEqual(native(root,p.artifacts,e).observe().errors,[]);
  const r=uintRuntime(root),bf=loadJs(root,bundle).createBundleFactory();
  const rows=[{serial:0,label:'first'},{serial:0,label:'second'},{serial:uintMax,label:'first'}].map(({serial,label})=>{
    const c=r.ef.create(r.input({id:r.makeId(serial),label}));assert.ok(c.ok);const input={child:c.value,label:'bundle'},v=bf.create(input);assert.ok(v.ok);
    return {value:v.value,key:compiledFieldValueKey(fields,'audit:bundle',embeddedWire(input))};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  assert.ok(rows[0].value.equals(rows[1].value));assert.equal(rows[0].value.equals(rows[2].value),false);
});
const ref=(owner:string,field:string,kind:'identity-reference'|'field-projection',target:string,...projection:string[])=>({owner,field,kind,target,projection});
const accountPath='application/features/audit/src/domain/entities/account.ts';
const simpleReferences=()=>[
  ref('audit:account','a_customer','identity-reference','commerce:customer','id'),
  ref('commerce:contact','a_customer','identity-reference','commerce:customer','id'),
  ref('commerce:contact','b_account','identity-reference','audit:account','id'),
  ref('commerce:contact','c_same','field-projection','commerce:customer','id'),
  ref('commerce:contact','d_list','identity-reference','commerce:customer','id'),
  ref('commerce:contact','e_set','identity-reference','audit:account','id'),
  ref('commerce:contact','f_optional','identity-reference','commerce:customer','id'),
  ref('commerce:contact','label','field-projection','commerce:customer','label'),
  ref('commerce:customer','a_account','identity-reference','audit:account','id'),
  ref('commerce:customer','b_self','identity-reference','commerce:customer','id'),
];
function addReferenceFields(f:any,selector:string,additions:Record<string,any>) {
  const [feature,node]=selector.split(':'),p='specs/'+feature+'/nodes/'+node+'.json',value=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  for(const [name,type] of Object.entries(additions)){value.body.fields.push(name);value.body.typed_contract.properties.push({name,type,identity:false,meaning:name,
    ontology_property:'FIXTURE-'+node.toUpperCase()+'#'+name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});}
  f.write(p,value);
}
function referenceFields(g:any,bindings:ReturnType<typeof simpleReferences>) {
  const fields=compileSelectedProjectFields(g.graph,{...g.fields.selection,bindings},descriptor);
  return {...g,fields,selection:{...g.selection,schema_version:REFERENCE_FIELD_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256} as ConfiguredFactorySelection};
}
function referenceFixture(t:any) {
  const f=uintIdentityFixture(t),scalar={kind:'scalar',name:'UInt64'},wrap=(kind:string)=>({kind,element:scalar});
  const account=JSON.parse(fs.readFileSync(path.join(f.source,'specs/commerce/nodes/customer.json'),'utf8'));
  account.feature_id='audit';account.node_id='account';account.body.typed_contract.ontology_node='FIXTURE-ACCOUNT';
  for(const p of account.body.typed_contract.properties)p.ontology_property='FIXTURE-ACCOUNT#'+p.name;
  f.write('specs/audit/nodes/account.json',account);
  const feature=JSON.parse(fs.readFileSync(path.join(f.source,'specs/audit/feature.json'),'utf8'));feature.nodes.push('account');f.write('specs/audit/feature.json',feature);
  addReferenceFields(f,'audit:account',{a_customer:wrap('optional')});
  addReferenceFields(f,'commerce:customer',{a_account:wrap('optional'),b_self:wrap('list')});
  addReferenceFields(f,'commerce:contact',{a_customer:scalar,b_account:scalar,c_same:scalar,d_list:wrap('list'),e_set:wrap('set'),f_optional:wrap('optional')});
  const recompile=(bindings=simpleReferences())=>{
    const graph=loadCompiledProjectGraph(f.source),fields=compileSelectedProjectFields(graph,{...f.fields.selection,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,bindings},descriptor);
    const selection={...f.selection,schema_version:REFERENCE_FIELD_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256,
      factories:[...f.selection.factories,{...f.selection.factories.find(x=>x.selector==='commerce:customer')!,selector:'audit:account'}]} as ConfiguredFactorySelection;
    return {graph,fields,selection};
  };
  return {...f,...recompile(),recompile};
}
function referenceExpected():any {
  const e:any=expected(),customer=e.modules.find((m:any)=>m.name==='Customer'),contact=e.modules.find((m:any)=>m.name==='Contact');
  customer.base[0]=call('commerce:valid-id','validator3','value','label');
  const account=structuredClone(customer);account.name='Account';account.path=accountPath;
  for(const i of account.imports)i.path=i.path.includes('audit')?'../rules/'+path.basename(i.path):'../../../../commerce/src/domain/rules/'+path.basename(i.path);
  e.modules.unshift(account);e.files.push(accountPath);
  for(const m of e.modules){m.composed=true;m.collection_support_sha256=uintSupportHash;}
  account.collection_protocols=['optionalValue(uint64Value)','boolValue','uint64Value','stringValue'];
  customer.collection_protocols=['optionalValue(uint64Value)','listValue(uint64Value)','boolValue','uint64Value','stringValue'];
  contact.collection_protocols=['uint64Value','uint64Value','uint64Value','listValue(uint64Value)','setValue(uint64Value)','boolValue','optionalValue(uint64Value)','stringValue','stringValue'];
  contact.provider='commerce:contact';
  const r=simpleReferences();
  for(const [m,selector] of [[account,'audit:account'],[customer,'commerce:customer'],[contact,'commerce:contact']] as const)m.reference_bindings=r.filter(x=>x.owner===selector);
  const imp=(p:string,symbol:string,index:number)=>({path:p,symbol:symbol+'Fields',local:'referenceTarget'+index+'Fields',type_only:true});
  account.imports.push(imp('../../../../commerce/src/domain/entities/customer.js','Customer',0));
  customer.imports.push(imp('../../../../audit/src/domain/entities/account.js','Account',0));
  contact.imports.push(...[0,1,2,3,4,5,6].map(i=>imp([1,4].includes(i)?'../../../../audit/src/domain/entities/account.js':'../entities/customer.js',[1,4].includes(i)?'Account':'Customer',i)));
  account.reference_types={a_customer:'(referenceTarget0Fields["id"])|null'};
  customer.reference_types={a_account:'(referenceTarget0Fields["id"])|null',b_self:'ReadonlyArray<CustomerFields["id"]>'};
  contact.reference_types={a_customer:'referenceTarget0Fields["id"]',b_account:'referenceTarget1Fields["id"]',c_same:'referenceTarget2Fields["id"]',
    d_list:'ReadonlyArray<referenceTarget3Fields["id"]>',e_set:'ReadonlyArray<referenceTarget4Fields["id"]>',f_optional:'(referenceTarget5Fields["id"])|null',label:'referenceTarget6Fields["label"]'};
  return e;
}
type ReferenceCustomerFixtureFields=FixtureSpread<CustomerFixtureFields,{id:number;b_self:unknown[]}>;
type ReferenceContactFixtureFields=ContactFixtureFields&{a_customer:number;b_account:number;c_same:number;d_list:unknown[];e_set:unknown[]};
function refCustomer():ReferenceCustomerFixtureFields;
function refCustomer<P extends object>(patch:P):FixtureSpread<ReferenceCustomerFixtureFields,P>;
function refCustomer(patch:object={}){return customer({id:1,b_self:[],...patch});}
function refContact():ReferenceContactFixtureFields;
function refContact<P extends object>(patch:P):FixtureSpread<ReferenceContactFixtureFields,P>;
function refContact(patch:object={}){return contact({a_customer:1,b_account:1,c_same:1,d_list:[],e_set:[],...patch});}
test('PCR-06 references emit selective deterministic support and prior versions reject bindings',t=>{
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',
    protocol_id:'typescript.owned-value-object-factory/v1',fields:[{name:'id',tag:'UInt64',identity:true,wrappers:[],value_shape:{kind:'UInt64'}}],
    imports:[],base_validators:[],extensions:[],component_protocol_sha256:'numeric',composed:true,collections:true,enum_fields:true,sum_fields:true,uint64_fields:true};
  assertDeterministicDistinctKinds(m);
  const f=referenceFixture(t);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:UINT64_FIELD_FACTORY_VERSION},uintSources),/reference bindings unsupported/);
});
test('PCR-06 references bind exact checked targets and artifacts with deterministic cycles',t=>{
  const f=referenceFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,referenceSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v7-candidate');assert.equal(p.factory_contract_sha256,referenceContractHash);
  assert.deepEqual(p.reference_bindings!.map(({owner,field,kind,target,projection})=>({owner,field,kind,target,projection})),simpleReferences());
  for(const r of p.reference_bindings!)assert.equal(r.target_artifact_sha256,p.artifacts.find(a=>a.relative_path===r.target_path)!.sha256);
  const g=f.recompile([...simpleReferences()].reverse());assert.deepEqual(planConfiguredFactories(g.graph,g.fields,g.selection,referenceSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},referenceSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'other/root'},referenceSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const key of Object.keys(referenceSources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...referenceSources,[key]:(referenceSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,referenceSources));
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,referenceSources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:f.selection.factories.filter(x=>x.selector!=='audit:account')},referenceSources),/factory coverage/);
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  for(const change of [(r:any)=>{r.target='audit:account';},(r:any)=>{r.kind='field-projection';}]){
    const rs=simpleReferences();change(rs[1]);const g=f.recompile(rs),changed=planConfiguredFactories(g.graph,g.fields,g.selection,referenceSources);
    assert.notEqual(changed.plan_sha256,p.plan_sha256);
    assert.notEqual(changed.artifacts.find(a=>a.relative_path===paths.contact)!.sha256,p.artifacts.find(a=>a.relative_path===paths.contact)!.sha256);
    assert.deepEqual(changed.modules.find(m=>m.name==='Contact')!.fields,p.modules.find(m=>m.name==='Contact')!.fields);
  }
  assert.equal(Object.isFrozen(f.selection.factories),false);fs.renameSync(f.source,path.join(f.temp,'moved'));
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,referenceSources),p);
});
test('PCR-06 native references preserve descriptor distinctions without lookup or runtime cycles',t=>{
  const f=referenceFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,referenceSources),root=path.join(f.temp,'references');
  assert.deepEqual(native(root,p.artifacts,referenceExpected()).observe().errors,[]);
  const c=loadJs(root,paths.customer),v=loadJs(root,paths.contact),a=loadJs(root,accountPath);
  const all=[...a.AccountFieldBindings,...v.ContactFieldBindings,...c.CustomerFieldBindings];assert.deepEqual(all,simpleReferences());
  for(const entries of [a.AccountFieldBindings,v.ContactFieldBindings,c.CustomerFieldBindings]){
    assert.ok(Object.isFrozen(entries));for(const r of entries){assert.ok(Object.isFrozen(r));assert.ok(Object.isFrozen(r.projection));}
  }
  const vf=v.createContactFactory(),cf=c.createCustomerFactory(),af=a.createAccountFactory();
  // Nonexistent targets and independently supplied projected values remain accepted.
  assert.ok(vf.create(refContact({a_customer:uintMax,c_same:2,label:'independent projection'})).ok);
  assert.ok(cf.create(refCustomer({a_account:uintMax,b_self:[999]})).ok);assert.ok(af.create(customer({id:7,a_customer:123})).ok);
  const prior=cf.create(refCustomer()).value;
  assert.ok(cf.transition(prior,refCustomer({a_account:77,b_self:[1,2]})).ok);
  assert.deepEqual(cf.transition(prior,refCustomer({id:2})).failure_codes,['IDENTITY_CHANGED']);
  const rows=[{}, {a_customer:2},{b_account:2},{c_same:2},{f_optional:null},{f_optional:0},{d_list:[1,2]},{d_list:[2,1]},{d_list:[1,1]},
    {e_set:[1,2]},{e_set:[2,1]}].map(patch=>{const input=refContact(patch),r=vf.create(input);assert.ok(r.ok);return {value:r.value,key:compiledFieldValueKey(f.fields,'commerce:contact',input)};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  for(const file of [paths.customer,accountPath])assert.doesNotMatch(fs.readFileSync(path.join(root,'js',file.replace('.ts','.js')),'utf8'),/require\([^)]*(?:customer|account)\.js/);
  assert.equal(vf.extend('enabled').create(refContact({enabled:false})).ok,false);
});
test('PCR-06 native reference fields validate all routes and expose readonly target-indexed types',t=>{
  const f=referenceFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,referenceSources),root=path.join(f.temp,'reference-types'),n=native(root,p.artifacts,referenceExpected());
  const cf=loadJs(root,paths.customer).createCustomerFactory(),vf=loadJs(root,paths.contact).createContactFactory(),prior=cf.create(refCustomer()).value;
  for(const patch of [{a_account:'1'},{a_account:-1},{a_account:uintMax+1},{b_self:[null]},{b_self:[undefined]}])for(const route of ['create','reconstruct','transition']){
    const r=route==='transition'?cf.transition(prior,refCustomer(patch)):cf[route](refCustomer(patch));assert.deepEqual(r.failure_codes,['INVALID_FIELDS']);assert.deepEqual(r.trace.validators,[]);
  }
  for(const patch of [{e_set:[1,1]},{f_optional:undefined},{a_customer:prior},{label:null}])assert.equal(vf.create(refContact(patch)).ok,false);
  const input=refContact({d_list:[1,2],e_set:[2,1]}),v=vf.create(input).value;input.d_list.reverse();assert.deepEqual(v.fields.d_list,[1,2]);assert.ok(Object.isFrozen(v.fields.e_set));
  const file=path.join(root,'consumer.ts'),prefix='import {ContactFieldBindings,type ContactFields} from "./'+paths.contact.replace('.ts','.js')+'";\n';
  fs.writeFileSync(file,prefix+'const x:ContactFields["a_customer"]=1; const t:"commerce:customer"=ContactFieldBindings[0].target;\n');n.compile([file]);
  for(const code of ['const x:ContactFields["a_customer"]="1";','ContactFieldBindings[0].projection[0]="label";','declare const x:ContactFields;x.d_list.push(1);']){
    fs.writeFileSync(file,prefix+code);assert.throws(()=>n.compile([file]),(e:any)=>{assert.match(String(e.stdout),/consumer\.ts.*TS(?:2322|2540|2339)/);return true;});
  }
});
test('PCR-06 references preserve wrapper projections and reject invalid target or path meanings',t=>{
  const f=referenceFixture(t),bindings=simpleReferences();
  bindings.find(r=>r.field==='d_list')!.kind='field-projection';bindings.find(r=>r.field==='d_list')!.projection=['b_self'];
  bindings.find(r=>r.field==='f_optional')!.kind='field-projection';bindings.find(r=>r.field==='f_optional')!.projection=['a_account'];
  const g=f.recompile(bindings),p=planConfiguredFactories(g.graph,g.fields,g.selection,referenceSources),e=referenceExpected(),m=e.modules.find((m:any)=>m.name==='Contact');
  m.reference_bindings=bindings.filter(r=>r.owner==='commerce:contact');m.reference_types.d_list='referenceTarget3Fields["b_self"]';m.reference_types.f_optional='referenceTarget5Fields["a_account"]';
  assert.deepEqual(native(path.join(f.temp,'projection-wrappers'),p.artifacts,e).observe().errors,[]);
  for(const change of [
    (r:any)=>{r.target='audit:missing';},(r:any)=>{r.projection=['label'];},(r:any)=>{r.projection=['id','missing'];},
  ]){const bad=simpleReferences();change(bad.find(r=>r.owner==='commerce:contact'&&r.field==='a_customer'));assert.throws(()=>f.recompile(bad));}
  assert.throws(()=>f.recompile([...simpleReferences(),ref('commerce:customer','id','field-projection','audit:account','id')]),/FIELD_IDENTITY_BINDING/);
  assert.throws(()=>f.recompile([...simpleReferences(),ref('commerce:customer','label','field-projection','commerce:contact','label')]),/FIELD_REFERENCE_CYCLE/);
  const bad=simpleReferences();bad.find(r=>r.field==='c_same')!.projection=['a_account','id'];assert.throws(()=>f.recompile(bad),/FIELD_PROJECTION/);
});
test('PCR-06 native reference observers detect compiling target kind path and type mutants',t=>{
  const f=referenceFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,referenceSources),original=p.artifacts.find(a=>a.relative_path===paths.contact)!.content;
  for(const mutant of [
    {id:'target',before:'target:"commerce:customer"',after:'target:"audit:account"'},
    {id:'kind',before:'kind:"identity-reference"',after:'kind:"field-projection"'},
    {id:'path',before:'projection:Object.freeze(["id"] as const)',after:'projection:Object.freeze(["label"] as const)'},
    {id:'type',before:'readonly "a_customer":referenceTarget0Fields["id"]',after:'readonly "a_customer":number'},
  ]){
    assert.ok(original.includes(mutant.before));const root=path.join(f.temp,'reference-mutant-'+mutant.id),content=original.replace(mutant.before,mutant.after);
    const n=native(root,p.artifacts.map(a=>({...a,content:a.relative_path===paths.contact?content:a.content})),referenceExpected());
    assert.ok(n.observe().errors.some((e:string)=>e.startsWith(mutant.id==='type'?'reference-type:':'reference-binding:')));
    if(mutant.id!=='type')assert.notDeepEqual(loadJs(root,paths.contact).ContactFieldBindings,simpleReferences().filter(r=>r.owner==='commerce:contact'));
  }
});
test('PCR-06 native references compose with owned composite identities and nested sum projections',t=>{
  const f=uintFixture(t),named={kind:'named',selector:'commerce:order-id'};
  addReferenceFields(f,'commerce:contact',{zzz_copy:named,zzz_owner:{kind:'optional',element:named},zzz_owners:{kind:'set',element:named}});
  const bindings=[ref('commerce:contact','label','field-projection','commerce:customer','label'),
    ref('commerce:contact','locale','field-projection','audit:tenant','key'),
    ref('commerce:contact','z_named','field-projection','commerce:customer','z_result'),
    ref('commerce:contact','zz_count','field-projection','commerce:customer','id','serial'),
    ref('commerce:contact','zzz_copy','field-projection','commerce:customer','id'),
    ref('commerce:contact','zzz_owner','identity-reference','commerce:customer','id'),
    ref('commerce:contact','zzz_owners','identity-reference','commerce:customer','id')];
  const g=referenceFields(f.recompile(),bindings),p=planConfiguredFactories(g.graph,g.fields,g.selection,referenceSources),e=uintExpected();
  for(const m of e.modules)m.reference_bindings=m.name==='Contact'?bindings:[];
  for(const m of [...e.enum_components,...e.sum_modules])m.contract_sha256=referenceContractHash;
  const c=e.modules.find((m:any)=>m.name==='Contact');
  c.collection_protocols.push('ownedValue(component13)','optionalValue(ownedValue(component14Element))','setValue(ownedValue(component15Element))');
  for(const local of ['component13','component14Element','component15Element'])c.imports.push(...sumDep('./order-id.js','OrderId',local,'Snapshot'));
  c.imports.push(...bindings.map((b,i)=>({path:b.target==='audit:tenant'?'../../../../audit/src/domain/value-objects/tenant.js':'../entities/customer.js',
    symbol:b.target==='audit:tenant'?'TenantFields':'CustomerFields',local:'referenceTarget'+i+'Fields',type_only:true})));
  c.reference_types={label:'referenceTarget0Fields["label"]',locale:'referenceTarget1Fields["key"]',z_named:'referenceTarget2Fields["z_result"]',
    zz_count:'referenceTarget3Fields["id"]["fields"]["serial"]',zzz_copy:'referenceTarget4Fields["id"]',
    zzz_owner:'(referenceTarget5Fields["id"])|null',zzz_owners:'ReadonlyArray<referenceTarget6Fields["id"]>'};
  const root=path.join(f.temp,'reference-composition'),n=native(root,p.artifacts,e);assert.deepEqual(n.observe().errors,[]);
  const r=uintRuntime(root),base=(patch:object={})=>r.base({zzz_copy:r.makeId(),zzz_owners:[],...patch});
  const rows=[{}, {zzz_owner:null},{zzz_owner:r.makeId(1)},{zzz_owner:r.makeId(2)},
    {zzz_owners:[r.makeId(1),r.makeId(2)]},{zzz_owners:[r.makeId(2),r.makeId(1)]},
    {z_named:r.sum.create({variant:'Text',payload:1})},{z_named:r.sum.create({variant:'Text',payload:2})},
    {zz_count:10},{zzz_copy:r.makeId(5)}].map(patch=>{const input=base(patch),v=r.vf.create(input);assert.ok(v.ok);
      return {value:v.value,key:compiledFieldValueKey(g.fields,'commerce:contact',Object.fromEntries(Object.entries(input).map(([k,v])=>[k,sumWire(v)])))};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  assert.equal(r.vf.create(base({zzz_owners:[r.makeId(1),r.makeId(1)]})).ok,false);
  assert.equal(r.vf.create(base({zzz_owner:sumWire(r.makeId())})).ok,false);
  assert.equal(r.vf.create(base({zzz_owner:r.tf.create({key:'not-an-order-id'}).value})).ok,false);
  assert.equal(r.vf.create(base({z_named:r.other.create({variant:'Text',payload:1})})).ok,false);
  const prior=r.ef.create(r.input({contact:r.vf.create(base()).value}));assert.ok(prior.ok);
  assert.ok(r.ef.transition(prior.value,r.input({contact:r.vf.create(base({zzz_owner:r.makeId(99)})).value})).ok);
  const consumer=path.join(root,'consumer.ts');
  fs.writeFileSync(consumer,'import type {ContactFields} from "./'+paths.contact.replace('.ts','.js')+'";\ndeclare const x:ContactFields;const n:number=x.zz_count;const s:number=x.zzz_copy.fields.serial;\n');n.compile([consumer]);
});
test('PCR-06 native references keep String identity values exact without nominal or existence claims',t=>{
  const f=fixture(t),bindings=[ref('commerce:contact','label','field-projection','commerce:customer','label'),
    ref('commerce:contact','locale','identity-reference','commerce:customer','id')];
  const g=referenceFields(f,bindings),p=planConfiguredFactories(g.graph,g.fields,g.selection,referenceSources),e:any=expected();
  for(const m of e.modules){m.composed=true;m.collection_support_sha256=uintSupportHash;m.collection_protocols=['boolValue','stringValue','stringValue'];m.reference_bindings=[];}
  const c=e.modules[0];c.provider='commerce:contact';c.reference_bindings=bindings;
  c.reference_types={label:'referenceTarget0Fields["label"]',locale:'referenceTarget1Fields["id"]'};
  for(const i of [0,1])c.imports.push({path:'../entities/customer.js',symbol:'CustomerFields',local:'referenceTarget'+i+'Fields',type_only:true});
  const root=path.join(f.temp,'string-references');assert.deepEqual(native(root,p.artifacts,e).observe().errors,[]);
  const vf=loadJs(root,paths.contact).createContactFactory();
  const rows=['','missing target','é','e\u0301','1','01'].map(locale=>{const input=contact({locale}),r=vf.create(input);assert.ok(r.ok);
    return {value:r.value,key:compiledFieldValueKey(g.fields,'commerce:contact',input)};});
  for(const a of rows)for(const b of rows)assert.equal(a.value.equals(b.value),a.key===b.key);
  // The target's valid-id Rule is not silently applied to a mere reference field.
  assert.ok(vf.reconstruct(contact({locale:''})).ok);assert.equal(vf.create(contact({locale:1})).ok,false);
});
function uintFixture(t:any) {
  const f=sumFixture(t),scalar={kind:'scalar',name:'UInt64'},wrap=(kind:string,element:any)=>({kind,element});
  const additions={zz_count:scalar,zz_list:wrap('list',scalar),zz_matrix:wrap('list',wrap('list',scalar)),zz_maybe:wrap('optional',scalar),zz_set:wrap('set',scalar)};
  for(const [node_id,fields] of [['contact',additions],['order-id',{serial:scalar}]] as const) {
    const p='specs/commerce/nodes/'+node_id+'.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
    for(const [name,type] of Object.entries(fields)) {
      node.body.fields.push(name);node.body.typed_contract.properties.push({name,type,identity:false,meaning:name,
        ontology_property:'FIXTURE-'+node_id.toUpperCase()+'#'+name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});
    }
    f.write(p,node);
  }
  for(const [feature,node_id] of [['commerce','authorization'],['audit','other-authorization']]) {
    const p='specs/'+feature+'/nodes/'+node_id+'.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
    for(const v of node.body.typed_contract.variants) {
      if(v.name==='Text')v.payload=scalar;
      if(v.name==='Maybe')v.payload=wrap('optional',scalar);
      if(v.name==='Nested')v.payload.variants.find((v:any)=>v.name==='Text').payload=scalar;
    }
    f.write(p,node);
  }
  const recompile=()=>{const g=f.recompile();return {...g,selection:{...g.selection,schema_version:UINT64_FIELD_FACTORY_VERSION} as ConfiguredFactorySelection};};
  return {...f,...recompile(),recompile};
}
function uintExpected():any {
  const e=sumExpected();
  for(const m of e.modules)m.collection_support_sha256=uintSupportHash;
  for(const m of e.enum_components)m.contract_sha256=uintContractHash;
  for(const m of e.sum_modules) {
    m.contract_sha256=uintContractHash;m.support_sha256=uintSupportHash;
    if(m.name!=='Answer')m.protocol=m.protocol.replaceAll('["Text"]:stringValue','["Text"]:uint64Value').replace('["Maybe"]:optionalValue(stringValue)','["Maybe"]:optionalValue(uint64Value)');
  }
  e.modules.find((m:any)=>m.name==='Contact').collection_protocols.push('uint64Value','listValue(uint64Value)','listValue(listValue(uint64Value))','optionalValue(uint64Value)','setValue(uint64Value)');
  const id=e.modules.find((m:any)=>m.name==='OrderId');id.collection_protocols=['stringValue','uint64Value','ownedValue(component2)'];
  for(const i of id.imports) {if(i.local==='component1')i.local='component2';if(i.local==='component1Type')i.local='component2Type';}
  return e;
}
function uintRuntime(root:string) {
  const r=sumRuntime(root),base=(patch:object={})=>r.base({zz_count:0,zz_list:[],zz_matrix:[],zz_set:[],...patch});
  const makeId=(serial=0)=>r.of.create({key:'order-a',serial,tenant:r.tf.create({key:'tenant-a'}).value}).value;
  const input=(patch:object={})=>r.input({id:makeId(),contact:r.vf.create(base()).value,z_result:r.sum.create({variant:'Cancelled'}),...patch});
  return {...r,base,makeId,input};
}
function uintIdentityFixture(t:any) {
  const f=fixture(t),p='specs/commerce/nodes/customer.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  node.body.typed_contract.properties.find((p:any)=>p.name==='id').type={kind:'scalar',name:'UInt64'};f.write(p,node);
  const g=f.recompile(),selection={...g.selection,schema_version:UINT64_FIELD_FACTORY_VERSION} as ConfiguredFactorySelection;
  (selection.factories[0] as any).base_validators[0]=bind('commerce:valid-id','value','label');
  const e:any=expected();
  for(const m of e.modules){m.composed=true;m.collection_support_sha256=uintSupportHash;m.collection_protocols=['boolValue','stringValue','stringValue'];}
  e.modules[0].provider='commerce:contact';
  e.modules[1].collection_protocols=['boolValue','uint64Value','stringValue'];e.modules[1].base[0]=call('commerce:valid-id','validator3','value','label');
  return {...f,...g,selection,expectation:e};
}
test('PCR-06 UInt64 emits selective deterministic factory and sum support',()=>{
  const shape:ValueShape={kind:'sum',variants:[{name:'Empty',ontology_variant:'TEST#Empty',payload:null},{name:'Text',ontology_variant:'TEST#Text',payload:{kind:'String'}}]};
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',
    protocol_id:'typescript.owned-value-object-factory/v1',fields:[{name:'id',tag:'String',identity:true,wrappers:[],value_shape:{kind:'String'}},
      {name:'choice',tag:'Sum',identity:false,wrappers:[],value_shape:shape}],imports:[],base_validators:[],extensions:[],
    component_protocol_sha256:'sum',composed:true,collections:true,enum_fields:true,sum_fields:true};
  assertDeterministicDistinctKinds(m);
  const sumInput={selector:'test:choice',relative_path:'choice.sum.ts',name:'Choice',shape,contract_sha256:'sum'} as const;
  const renderedSum=renderConfiguredSum(sumInput);
  assert.equal(renderConfiguredSum(sumInput),renderedSum);
  assert.match(renderedSum,/const stringValue:ValueProtocol<string>/);
  assert.doesNotMatch(renderedSum,/const uint64Value:/);
});
test('PCR-06 UInt64 binds checked contract and deterministic closure without numeric Rule coercion',t=>{
  const f=uintFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,uintSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v6-candidate');assert.equal(p.factory_contract_sha256,uintContractHash);
  assert.equal(p.collection_support!.sha256,uintSupportHash);assert.equal(p.modules.find(m=>m.name==='Contact')!.fields.find(f=>f.name==='zz_count')!.tag,'UInt64');
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},uintSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'other/root'},uintSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const b of p.component_bindings!)assert.equal(b.artifact_sha256,p.artifacts.find(a=>a.relative_path===b.relative_path)!.sha256);
  for(const key of Object.keys(uintSources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...uintSources,[key]:(uintSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:SUM_FIELD_FACTORY_VERSION},sumSources),/unsupported sum payload|fields only/);
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,uintSources));
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,uintSources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,field_compilation_sha256:'0'.repeat(64)},uintSources));
  for(const binding of [bind('audit:has-label','label','zz_count'),bindPath('audit:has-label','label','id','serial')]) {
    const selection=structuredClone(f.selection),target=selection.factories.find(f=>f.selector===(binding.arguments[0]!.path?'commerce:customer':'commerce:contact'))! as any;
    target.base_validators=[binding];assert.throws(()=>planConfiguredFactories(f.graph,f.fields,selection,uintSources),/validator path/);
  }
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);assert.equal(Object.isFrozen(f.selection.factories),false);
  fs.renameSync(f.source,path.join(f.temp,'moved'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,uintSources),p);
});
test('PCR-06 native UInt64 composition agrees with checked equality and composite identity',t=>{
  const f=uintFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,uintSources),root=path.join(f.temp,'uint-composition'),n=native(root,p.artifacts,uintExpected());
  assert.deepEqual(n.observe().errors,[]);const r=uintRuntime(root);
  const patches=[{}, {zz_count:-0},{zz_count:0},{zz_count:1},{zz_count:uintMax-1},{zz_count:uintMax},
    {zz_maybe:null},{zz_maybe:0},{zz_maybe:uintMax},{zz_list:[0,1]},{zz_list:[1,0]},{zz_list:[1,1]},
    {zz_set:[0,uintMax]},{zz_set:[uintMax,0]},{zz_matrix:[[0],[uintMax]]},{zz_matrix:[[uintMax],[0]]},
    {z_named:r.sum.create({variant:'Text',payload:0})},{z_named:r.sum.create({variant:'Text',payload:uintMax})},
    {z_named:r.sum.create({variant:'Maybe',payload:null})},{z_named:r.sum.create({variant:'Maybe',payload:0})},
    {z_named:r.sum.create({variant:'Nested',payload:{variant:'Text',payload:uintMax}})}];
  const rows=patches.map(patch=>{const input=r.base(patch),result=r.vf.create(input);assert.equal(result.ok,true);
    return {value:result.value,key:compiledFieldValueKey(f.fields,'commerce:contact',Object.fromEntries(Object.entries(input).map(([k,v])=>[k,sumWire(v)])))};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  assert.equal(Object.is(r.vf.create(r.base({zz_count:-0})).value.fields.zz_count,-0),false);
  assert.equal(r.vf.create(r.base({zz_set:[0,-0]})).ok,false);
  assert.equal(r.vf.create(r.base({zz_list:[0,-0]})).ok,true);
  const left=r.makeId(uintMax),same=r.makeId(uintMax),other=r.makeId(uintMax-1);assert.ok(left.equals(same));assert.equal(left.equals(other),false);
  const prior=r.ef.create(r.input({id:left}));assert.ok(prior.ok);
  assert.ok(r.ef.transition(prior.value,r.input({id:same,label:'changed'})).ok);
  assert.deepEqual(r.ef.transition(prior.value,r.input({id:other})).failure_codes,['IDENTITY_CHANGED']);
  for(const bad of [-1,0.5,uintMax+1,NaN,Infinity,'1',1n]) {
    for(const patch of [{zz_count:bad},{zz_maybe:bad},{zz_list:[bad]},{zz_set:[bad]},{zz_matrix:[[bad]]}]) {
      const result=r.vf.create(r.base(patch));assert.deepEqual(result.failure_codes,['INVALID_FIELDS']);assert.deepEqual(result.trace.validators,[]);
    }
    for(const input of [{variant:'Text',payload:bad},{variant:'Maybe',payload:bad},{variant:'Nested',payload:{variant:'Text',payload:bad}}])assert.throws(()=>r.sum.create(input));
    assert.equal(r.makeId(bad as any),null);
  }
  const values=[0,uintMax],input=r.base({zz_list:values,zz_matrix:[values]});
  const created=r.vf.create(input);values.reverse();assert.deepEqual(created.value.fields.zz_list,[0,uintMax]);
  assert.ok(Object.isFrozen(created.value.fields.zz_matrix[0]));assert.equal(Object.isFrozen(values),false);
  assert.equal(r.vf.extend('enabled').create(r.base({enabled:false,zz_count:1})).ok,false);
});
test('PCR-06 native UInt64 identity rejects unsafe input on every route without coercion',t=>{
  const f=uintIdentityFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,uintSources),root=path.join(f.temp,'uint-identity');
  assert.equal(native(root,p.artifacts,f.expectation).observe().result,'pass');
  const ef=loadJs(root,paths.customer).createCustomerFactory(),prior=ef.create(customer({id:0}));assert.ok(prior.ok);
  const valid=[-0,0,1,2**32,2**48,uintMax-1,uintMax];
  const values=valid.map(id=>{const r=ef.create(customer({id}));assert.ok(r.ok);return r.value;});
  for(let i=0;i<valid.length;i++)for(let j=0;j<valid.length;j++) {
    const equal=compiledFieldValueKey(f.fields,'commerce:customer',customer({id:valid[i]}))===compiledFieldValueKey(f.fields,'commerce:customer',customer({id:valid[j]}));
    assert.equal(values[i].sameIdentity(values[j]),equal);assert.equal(values[i].hash()===values[j].hash(),equal);
  }
  assert.ok(ef.transition(prior.value,customer({id:-0})).ok);
  assert.deepEqual(ef.transition(prior.value,customer({id:1})).failure_codes,['IDENTITY_CHANGED']);
  let reads=0;const bad=[-1,-Number.MIN_VALUE,0.5,Number.EPSILON,uintMax+1,2**64,NaN,Infinity,-Infinity,null,undefined,'0','18446744073709551615',0n,(2n**64n)-1n,new Number(1),true,[],{valueOf(){reads++;return 1;}},Symbol('number')];
  for(const id of bad)for(const route of ['create','reconstruct','transition']) {
    const input=customer({id}),r=route==='transition'?ef.transition(prior.value,input):ef[route](input);
    assert.deepEqual(r.failure_codes,['INVALID_FIELDS']);assert.deepEqual(r.trace.validators,[]);
  }
  assert.equal(reads,0);
  assert.ok(ef.reconstruct(customer({id:uintMax})).ok);
  assert.equal(ef.extend('enabled').create(customer({id:1,enabled:false})).ok,false);
});
test('PCR-06 native UInt64 types are numeric and readonly while range validation remains runtime',t=>{
  const f=uintIdentityFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,uintSources),root=path.join(f.temp,'uint-types'),n=native(root,p.artifacts,f.expectation);
  const file=path.join(root,'consumer.ts'),prefix='import type {CustomerFields} from "./'+paths.customer.replace('.ts','.js')+'";\n';
  fs.writeFileSync(file,prefix+'export const number:CustomerFields["id"]=-1;\n');n.compile([file]);
  for(const input of ['"1"','1n','true']) {
    fs.writeFileSync(file,prefix+'const bad:CustomerFields["id"]='+input+';\n');
    assert.throws(()=>n.compile([file]),(error:any)=>{assert.match(String(error.stdout),/consumer\.ts.*TS2322/);return true;});
  }
  fs.writeFileSync(file,prefix+'const data:CustomerFields={id:1,label:"x",enabled:true};data.id=2;\n');
  assert.throws(()=>n.compile([file]),(error:any)=>{assert.match(String(error.stdout),/TS2540/);return true;});
});
test('PCR-06 native UInt64 AST and runtime checks expose compiling range and key mutants',t=>{
  const f=uintIdentityFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,uintSources),original=p.artifacts.find(a=>a.relative_path===paths.customer)!.content;
  for(const mutant of [
    {id:'unsafe-integer',before:'!Number.isSafeInteger(input)',after:'!Number.isInteger(input)',input:uintMax+1},
    {id:'negative-number',before:' || input < 0',after:'',input:-1},
    {id:'number-key-collapse',before:"part('UInt64') + part(String(value))",after:"part('UInt64')",input:null},
  ]) {
    assert.ok(original.includes(mutant.before));const root=path.join(f.temp,mutant.id),changed=original.replace(mutant.before,mutant.after);
    const artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===paths.customer?changed:a.content})),n=native(root,artifacts,f.expectation);
    assert.ok(n.observe().errors.includes('collection-support:'+paths.customer));
    const ef=loadJs(root,paths.customer).createCustomerFactory();
    if(mutant.input!==null) {assert.ok(ef.create(customer({id:mutant.input})).ok);assert.throws(()=>compiledFieldValueKey(f.fields,'commerce:customer',customer({id:mutant.input})));}
    else {const a=ef.create(customer({id:1})),b=ef.create(customer({id:2}));assert.ok(a.value.sameIdentity(b.value));assert.notEqual(compiledFieldValueKey(f.fields,'commerce:customer',customer({id:1})),compiledFieldValueKey(f.fields,'commerce:customer',customer({id:2})));}
  }
});
const sumPath=(selector='commerce:authorization')=>{const [feature,node]=selector.split(':');return 'application/features/'+feature+'/src/domain/enums/'+node+'.sum.ts';};
function sumFixture(t:any) {
  const f=composedFixture(t),scalar=(name='String')=>({kind:'scalar',name}),named=(selector:string)=>({kind:'named',selector}),
    wrap=(kind:string,element:any)=>({kind,element}),variants=(id:string,values:Record<string,any>)=>Object.entries(values).map(([name,payload])=>({name,payload,ontology_variant:id+'#'+name}));
  const raw=(p:string)=>JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  const forms:any={
    'commerce:status':{Draft:null,Submitted:null},
    'audit:answer':{Empty:null,Receipt:scalar()},
    'commerce:authorization':{Cancelled:null,Delegated:named('audit:answer'),Details:named('audit:tenant'),Flag:scalar('Bool'),
      Maybe:wrap('optional',scalar()),Nested:{kind:'sum',variants:variants('FIXTURE-NESTED-SUM',{Empty:null,Text:scalar()})},
      OtherText:scalar(),States:wrap('set',named('commerce:status')),Text:scalar()},
  };
  forms['audit:other-authorization']=structuredClone(forms['commerce:authorization']);
  for(const [selector,values] of Object.entries(forms)) {
    const [feature_id,node_id]=selector.split(':'),p='specs/'+feature_id+'/feature.json',feature=raw(p);
    feature.nodes.push(node_id);f.write(p,feature);
    const ontology='FIXTURE-'+feature_id!.toUpperCase()+'-'+node_id!.toUpperCase();
    f.write('specs/'+feature_id+'/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id,node_id,kind:'Enum',
      body:{description:selector,values:Object.keys(values as object),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:ontology,variants:variants(ontology,values as any)}}});
  }
  const inline={kind:'sum',variants:variants('FIXTURE-INLINE',{Nothing:null,State:named('commerce:status'),Text:scalar()})};
  const additions={z_choice:inline,z_list:wrap('list',named('commerce:authorization')),z_many:wrap('set',named('commerce:authorization')),
    z_maybe:wrap('optional',named('commerce:authorization')),z_named:named('commerce:authorization')};
  for(const node_id of ['contact','customer']) {
    const p='specs/commerce/nodes/'+node_id+'.json',node=raw(p);
    for(const [name,type] of Object.entries(node_id==='contact'?additions:{z_result:named('commerce:authorization')})) {
      node.body.fields.push(name);node.body.typed_contract.properties.push({name,type,identity:false,meaning:name,ontology_property:'FIXTURE-'+node_id.toUpperCase()+'#'+name,
        cardinality:type.kind==='optional'?'optional':type.kind==='set'?'many-unique':type.kind==='list'?'many':'one'});
    }
    f.write(p,node);
  }
  const recompile=()=>{
    const graph=loadCompiledProjectGraph(f.source),fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,
      contract_sha256:FIELD_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,
      roots:['commerce:customer','audit:alternate-tenant','audit:other-authorization'],bindings:[]},descriptor);
    return {graph,fields,selection:{...f.selection,schema_version:SUM_FIELD_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256} as ConfiguredFactorySelection};
  };
  return {...f,...recompile(),recompile};
}
const sumDep=(p:string,name:string,local:string,suffix='Case')=>[{path:p,symbol:name+'ValueComponent',local},
  {path:p,symbol:name+suffix,local:local+'Type',type_only:true}];
function sumExpected():any {
  const e=composedExpected();
  for(const m of e.modules) {
    m.collection_support_sha256=sumSupportHash;
    for(const i of m.imports)if(i.type_only)i.local=i.local[0].toLowerCase()+i.local.slice(1).replace(/Snapshot$/,'Type');
    m.collection_protocols=m.name==='Customer'?['ownedValue(component0)','boolValue','ownedValue(component2)','stringValue','ownedSumValue(component4)']:
      m.name==='OrderId'?['stringValue','ownedValue(component1)']:m.name==='Contact'?['boolValue','stringValue','stringValue',
        'sumValue(Object.freeze({["Nothing"]:null,["State"]:enumValue(component3Case1),["Text"]:stringValue}))',
        'listValue(ownedSumValue(component4Element))','setValue(ownedSumValue(component5Element))','optionalValue(ownedSumValue(component6Element))','ownedSumValue(component7)']:['stringValue'];
  }
  e.modules.find((m:any)=>m.name==='Customer').imports.push(...sumDep('../enums/authorization.sum.js','Authorization','component4'));
  const contact=e.modules.find((m:any)=>m.name==='Contact');
  contact.imports.push(...sumDep('../enums/status.component.js','Status','component3Case1'));
  for(const local of ['component4Element','component5Element','component6Element','component7'])contact.imports.push(...sumDep('../enums/authorization.sum.js','Authorization',local));
  const baseProtocol='sumValue(Object.freeze({["Cancelled"]:null,["Delegated"]:ownedSumValue(payloadCase1),["Details"]:ownedValue(payloadCase2),["Flag"]:boolValue,["Maybe"]:optionalValue(stringValue),["Nested"]:sumValue(Object.freeze({["Empty"]:null,["Text"]:stringValue})),["OtherText"]:stringValue,["States"]:setValue(enumValue(payloadCase7Element)),["Text"]:stringValue}))';
  e.sum_modules=[
    {path:sumPath('audit:answer'),name:'Answer',selector:'audit:answer',imports:[],protocol:'sumValue(Object.freeze({["Empty"]:null,["Receipt"]:stringValue}))'},
    {path:sumPath('audit:other-authorization'),name:'OtherAuthorization',selector:'audit:other-authorization',protocol:baseProtocol,imports:[
      ...sumDep('./answer.sum.js','Answer','payloadCase1'),...sumDep('../value-objects/tenant.js','Tenant','payloadCase2','Snapshot'),
      ...sumDep('../../../../commerce/src/domain/enums/status.component.js','Status','payloadCase7Element')]},
    {path:sumPath(),name:'Authorization',selector:'commerce:authorization',protocol:baseProtocol,imports:[
      ...sumDep('../../../../audit/src/domain/enums/answer.sum.js','Answer','payloadCase1'),...sumDep('../../../../audit/src/domain/value-objects/tenant.js','Tenant','payloadCase2','Snapshot'),
      ...sumDep('./status.component.js','Status','payloadCase7Element')]},
  ].map(m=>({...m,contract_sha256:sumContractHash,support_sha256:sumSupportHash}));
  const ee=enumExpected();e.enum_provider=ee.enum_provider;e.enum_components=ee.enum_components.filter((m:any)=>m.selector==='commerce:status').map((m:any)=>({...m,contract_sha256:sumContractHash}));
  e.files.push(...e.sum_modules.map((m:any)=>m.path),enumPath(),enumPath().replace('.component.ts','.ts'),e.enum_provider.path);
  return e;
}
function sumRuntime(root:string) {
  const r=composedRuntime(root),sum=loadJs(root,sumPath()).AuthorizationValueComponent,other=loadJs(root,sumPath('audit:other-authorization')).OtherAuthorizationValueComponent,
    answer=loadJs(root,sumPath('audit:answer')).AnswerValueComponent,status=loadJs(root,enumPath()).StatusValueComponent;
  const base=(patch:object={})=>contact({z_choice:{variant:'Nothing'},z_list:[],z_many:[],z_named:sum.create({variant:'Cancelled'}),...patch});
  return {...r,sum,other,answer,status,base};
}
const sumWire=(value:any):any=>Array.isArray(value)?value.map(sumWire):value&&typeof value==='object'?
  Object.hasOwn(value,'fields')?Object.fromEntries(Object.entries(value.fields).map(([k,v])=>[k,sumWire(v)])):
    Object.hasOwn(value,'variant')?{variant:value.variant,...(Object.hasOwn(value,'payload')?{payload:sumWire(value.payload)}:{})}:value:value;
test('PCR-06 sums emit selective deterministic support',()=>{
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',
    protocol_id:'typescript.owned-value-object-factory/v1',fields:[{name:'id',tag:'String',identity:true,wrappers:[]},{name:'status',tag:'Enum',identity:false,wrappers:['list'],
      component:{selector:'test:status',path:'./status.component.js',symbol:'StatusValueComponent',local:'component1',type_symbol:'StatusCase',type_local:'Component1Case'}}],
    imports:[],base_validators:[],extensions:[],component_protocol_sha256:'enum',composed:true,collections:true,enum_fields:true};
  assertDeterministicDistinctKinds(m);
});
test('PCR-06 sums bind checked variants, full dependencies and deterministic artifacts',t=>{
  const f=sumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sumSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v5-candidate');assert.equal(p.sum_modules!.length,3);
  assert.equal(p.modules.length,5);assert.equal(p.enum_components!.length,1);assert.equal(p.artifacts.length,15);
  assert.equal(p.collection_support!.sha256,sumSupportHash);
  for(const b of p.component_bindings!)assert.equal(b.artifact_sha256,p.artifacts.find(a=>a.relative_path===b.relative_path)!.sha256);
  assert.ok(p.component_bindings!.some((b:any)=>b.owner==='commerce:authorization'&&b.provider==='audit:tenant'&&b.value_path.join('/')==='variant/Details/payload'));
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},sumSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'alternate/root'},sumSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const key of Object.keys(sumSources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...sumSources,[key]:(sumSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:ENUM_FIELD_FACTORY_VERSION},enumSources));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,sumSources));
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,sumSources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,field_compilation_sha256:'0'.repeat(64)},sumSources));
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  assert.ok(Object.isFrozen(p.sum_modules![0]!.shape));assert.equal(Object.isFrozen(f.selection.factories),false);
  fs.renameSync(f.source,path.join(f.temp,'moved'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,sumSources),p);
});
test('PCR-06 native sums preserve tags and payload equality against the checked model',t=>{
  const f=sumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sumSources),root=path.join(f.temp,'sum-native'),n=native(root,p.artifacts,sumExpected());
  assert.deepEqual(n.observe().errors,[]);
  const r=sumRuntime(root),D=r.status.values.Draft,S=r.status.values.Submitted;
  const inputs=[{variant:'Cancelled'},{variant:'Text',payload:''},{variant:'Text',payload:'a'},{variant:'OtherText',payload:'a'},
    {variant:'Flag',payload:false},{variant:'Flag',payload:true},{variant:'Maybe',payload:null},{variant:'Maybe',payload:''},
    {variant:'Nested',payload:{variant:'Empty'}},{variant:'Nested',payload:{variant:'Text',payload:'a'}},
    {variant:'Delegated',payload:r.answer.create({variant:'Receipt',payload:'a'})},
    {variant:'Details',payload:r.tf.create({key:'a'}).value},{variant:'Details',payload:r.tf.create({key:'a'}).value},
    {variant:'Details',payload:r.tf.create({key:'b'}).value},
    {variant:'States',payload:[D,S]},{variant:'States',payload:[S,D]},{variant:'States',payload:[]}];
  const rows=inputs.map(input=>({value:r.sum.create(input),key:compiledFieldValueKey(f.fields,'commerce:authorization',sumWire(input))}));
  for(const a of rows)for(const b of rows){assert.equal(r.sum.equals(a.value,b.value),a.key===b.key);assert.equal(r.sum.key(a.value)===r.sum.key(b.value),a.key===b.key);}
  const a=r.sum.create({variant:'Text',payload:'a'}),b=r.sum.create({variant:'Text',payload:'b'});
  const patches=[{}, {z_named:a},{z_named:b},{z_maybe:null},{z_maybe:a},{z_many:[a,b]},{z_many:[b,a]},
    {z_list:[a,b]},{z_list:[b,a]},{z_list:[a,a]},{z_choice:{variant:'Text',payload:''}},{z_choice:{variant:'State',payload:D}}];
  const records=patches.map(patch=>{const input=r.base(patch),result=r.vf.create(input);assert.equal(result.ok,true);
    return {value:result.value,key:compiledFieldValueKey(f.fields,'commerce:contact',Object.fromEntries(Object.entries(input).map(([k,v])=>[k,sumWire(v)])))};});
  for(const a of records)for(const b of records){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  const input={variant:'States',payload:[D,S]},owned=r.sum.create(input);input.payload.reverse();
  assert.ok(Object.isFrozen(owned)&&Object.isFrozen(owned.payload));assert.equal(Object.isFrozen(input.payload),false);
  const inline={variant:'Text',payload:'one'},record=r.vf.create(r.base({z_choice:inline}));inline.payload='two';
  assert.equal(record.value.fields.z_choice.payload,'one');assert.ok(Object.isFrozen(record.value.fields.z_choice));
  const cv=r.vf.create(r.base()).value,prior=r.ef.create(r.input({contact:cv,z_result:a}));
  assert.ok(prior.ok&&r.ef.transition(prior.value,r.input({contact:cv,z_result:b})).ok);
  for(const route of ['create','reconstruct']) {
    assert.ok(r.vf[route](r.base()).ok);assert.equal(r.vf.extend('enabled')[route](r.base({enabled:false})).ok,false);
    assert.equal(r.ef[route](r.input({contact:cv,z_result:{variant:'Text',payload:'raw'}})).ok,false);
  }
  assert.equal(r.ef.transition(prior.value,r.input({contact:cv,z_result:a,label:''})).ok,false);
  assert.equal(r.ef.transition(prior.value,r.input({contact:cv,z_result:{variant:'Cancelled'}})).ok,false);
});
test('PCR-06 sums reject unsupported leaves, implicit Rule paths and embedding cycles',t=>{
  for(const scenario of ['UInt64','entity','cycle','missing-factory','implicit-rule','inline-UInt64']) {
    const f=sumFixture(t),nodePath='specs/commerce/nodes/authorization.json',node=JSON.parse(fs.readFileSync(path.join(f.source,nodePath),'utf8'));
    if(['UInt64','entity','cycle'].includes(scenario)) {
      node.body.typed_contract.variants.find((v:any)=>v.name==='Text').payload=scenario==='UInt64'?{kind:'scalar',name:'UInt64'}:
        {kind:'named',selector:scenario==='entity'?'commerce:customer':'commerce:authorization'};f.write(nodePath,node);
    }
    if(scenario==='inline-UInt64') {
      const file='specs/commerce/nodes/contact.json',c=JSON.parse(fs.readFileSync(path.join(f.source,file),'utf8'));
      c.body.typed_contract.properties.find((p:any)=>p.name==='z_choice').type.variants.find((v:any)=>v.name==='Text').payload={kind:'scalar',name:'UInt64'};f.write(file,c);
    }
    assert.throws(()=>{
      const g=f.recompile(),selection=structuredClone(g.selection);
      if(scenario==='missing-factory')(selection as any).factories=selection.factories.filter(f=>f.selector!=='audit:tenant');
      if(scenario==='implicit-rule')(selection.factories.find(f=>f.selector==='commerce:contact') as any).base_validators[0].arguments=[{parameter:'label',path:['z_named','payload']}];
      planConfiguredFactories(g.graph,g.fields,selection,sumSources);
    },scenario==='missing-factory'?/coverage/:scenario==='implicit-rule'?/validator path/:scenario==='UInt64'?/unsupported sum payload/:scenario==='inline-UInt64'?/fields only/:/FIELD_EMBEDDING_CYCLE|unsupported sum payload/,scenario);
  }
});
test('PCR-06 native sum ownership and exact payload shapes fail closed without invoking getters',t=>{
  const f=sumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sumSources),root=path.join(f.temp,'sum-invalid');
  native(root,p.artifacts,sumExpected());const r=sumRuntime(root),good=r.sum.create({variant:'Text',payload:'same'});
  let reads=0;
  const malformed=[null,[],{},'Text',{variant:'Unknown'},{variant:'Cancelled',payload:null},{variant:'Maybe'},
    {variant:'Maybe',payload:undefined},{variant:'Text'},{variant:'Text',payload:false},{variant:'Flag',payload:'true'},
    {variant:'Text',payload:'a',extra:true},{variant:'States',payload:[r.status.values.Draft,r.status.values.Draft]},
    {variant:'Nested',payload:{variant:'Empty',payload:null}},{variant:'Delegated',payload:{variant:'Empty'}},
    {variant:'Details',payload:{key:'a'}},{variant:'Details',payload:r.other.create({variant:'Cancelled'})},
    {get variant(){reads++;return 'Cancelled';}},{variant:'Text',get payload(){reads++;return 'a';}},
    {[Symbol('hidden')]:true,variant:'Cancelled'},Object.create({variant:'Cancelled'}),
    Object.defineProperty({variant:'Text'},'payload',{value:'a',enumerable:false})];
  for(const value of malformed)assert.throws(()=>r.sum.create(value));
  assert.equal(reads,0);assert.throws(()=>r.sum.key({variant:'Text',payload:'same'}));
  assert.equal(r.sum.equals(good,r.other.create({variant:'Text',payload:'same'})),false);
  assert.notEqual(r.sum.key(good),r.other.key(r.other.create({variant:'Text',payload:'same'})));
  for(const bad of [{variant:'Text',payload:'same'},{...good},Object.create(good),new Proxy(good,{}),
    r.other.create({variant:'Text',payload:'same'}),r.answer.create({variant:'Receipt',payload:'same'})]) {
    assert.equal(r.sum.isOwned(bad),false);
    for(const route of ['create','reconstruct'])for(const patch of [{z_named:bad},{z_maybe:bad},{z_many:[bad]},{z_list:[bad]}]) {
      const result=r.vf[route](r.base(patch));assert.deepEqual(result.failure_codes,['INVALID_FIELDS']);assert.deepEqual(result.trace.validators,[]);
    }
  }
  for(const patch of [{z_many:[good,r.sum.create({variant:'Text',payload:'same'})]},
    {z_choice:{variant:'Nothing',payload:null}},{z_choice:{variant:'Text'}},{z_choice:{variant:'State',payload:'Draft'}},
    {z_choice:{variant:'State',payload:{variant:'Draft'}}},{z_choice:{variant:'Text',get payload(){reads++;return 'bad';}}}]) {
    const result=r.vf.create(r.base(patch));assert.equal(result.ok,false);assert.deepEqual(result.trace.validators,[]);
  }
  assert.equal(reads,0);
  const req=createRequire(import.meta.url),file=path.join(root,'js',sumPath().replace('.ts','.js'));
  delete req.cache[req.resolve(file)];const otherInstance=req(file).AuthorizationValueComponent;
  assert.equal(r.vf.create(r.base({z_named:otherInstance.create({variant:'Cancelled'})})).ok,false);
});
test('PCR-06 native sum unions narrow by tag and reject wrong payload and nominal types',t=>{
  const f=sumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sumSources),root=path.join(f.temp,'sum-types'),n=native(root,p.artifacts,sumExpected());
  const prefix='import {AuthorizationValueComponent as A} from "./'+sumPath().replace('.ts','.js')+'";\n'+
    'import type {AuthorizationCase} from "./'+sumPath().replace('.ts','.js')+'";\n'+
    'import {OtherAuthorizationValueComponent as Other} from "./'+sumPath('audit:other-authorization').replace('.ts','.js')+'";\n';
  const file=path.join(root,'consumer.ts');
  const valid=prefix+'export const inspect=(value:AuthorizationCase):string=>{switch(value.variant){'+
    'case "Cancelled":return "cancelled";case "Delegated":return value.payload.variant;case "Details":return value.payload.fields.key;'+
    'case "Flag":return value.payload?"true":"false";case "Maybe":return value.payload??"none";'+
    'case "Nested":return value.payload.variant==="Text"?value.payload.payload:"empty";'+
    'case "OtherText":case "Text":return value.payload;case "States":return value.payload.map(v=>v.variant).join(",");'+
    'default:const exhaustive:never=value;return exhaustive;}};\n';
  fs.writeFileSync(file,valid);n.compile([file]);
  for(const line of ['const bad:AuthorizationCase=Other.create({variant:"Text",payload:"same"});',
    'A.create({variant:"Flag",payload:"false"});','A.create({variant:"Cancelled",payload:null});','A.create({variant:"Maybe"});',
    'const readonly=A.create({variant:"Text",payload:"x"});if(readonly.variant==="Text")readonly.payload="changed";']) {
    fs.writeFileSync(file,valid+line+'\n');
    assert.throws(()=>n.compile([file]),(error:any)=>{assert.match(String(error.stdout),/consumer\.ts.*error TS/);
      if(line.startsWith('const readonly'))assert.match(String(error.stdout),/TS2540/);return true;});
  }
});
test('PCR-06 native sum observers and behavior detect compiling tag and payload mutants',t=>{
  const f=sumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sumSources),root=path.join(f.temp,'sum-mutants'),n=native(root,p.artifacts,sumExpected());
  assert.equal(n.observe().result,'pass');
  const file=path.join(root,sumPath()),original=fs.readFileSync(file,'utf8');
  for(const [before,after,error] of [['["Text"]:stringValue','["Text"]:boolValue','sum-composition:'],
    ['isOwned:owned','isOwned:()=>true','sum-ownership:']]) {
    assert.ok(original.includes(before!));fs.writeFileSync(file,original.replace(before!,after!));
    assert.ok(n.observe().errors.some((e:string)=>e.startsWith(error!)));fs.writeFileSync(file,original);
  }
  const mutations=[
    {id:'tag-collapse',from:"part('Sum') + part(variant)",to:"part('Sum')",left:{variant:'Text',payload:'same'},right:{variant:'OtherText',payload:'same'}},
    {id:'payload-collapse',from:'part(protocol.key(payload as never))',to:"part('ignored')",left:{variant:'Text',payload:'left'},right:{variant:'Text',payload:'right'}},
  ];
  for(const mutation of mutations) {
    const changed=original.replace(mutation.from,mutation.to);assert.notEqual(changed,original);
    const target=path.join(f.temp,mutation.id),artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===sumPath()?changed:a.content}));
    const mutant=native(target,artifacts,sumExpected());assert.ok(mutant.observe().errors.includes('sum-support:'+sumPath()));
    const r=sumRuntime(target),left=r.sum.create(mutation.left),right=r.sum.create(mutation.right);
    assert.equal(r.sum.equals(left,right),true,'mutant collapses meanings that the independent model distinguishes');
    assert.notEqual(compiledFieldValueKey(f.fields,'commerce:authorization',mutation.left),compiledFieldValueKey(f.fields,'commerce:authorization',mutation.right));
  }
});
test('PCR-06 native inline-sum collections work without named sums or Enum providers',t=>{
  const f=fixture(t),file='specs/commerce/nodes/contact.json',node=JSON.parse(fs.readFileSync(path.join(f.source,file),'utf8'));
  const shape={kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'FIXTURE-STRUCTURAL#None'},
    {name:'Ready',payload:{kind:'scalar',name:'String'},ontology_variant:'FIXTURE-STRUCTURAL#Ready'}]};
  for(const kind of ['list','set']) {
    const name='z_inline_'+kind;node.body.fields.push(name);node.body.typed_contract.properties.push({name,meaning:name,identity:false,
      cardinality:kind==='set'?'many-unique':'many',ontology_property:'FIXTURE-CONTACT#'+name,type:{kind,element:shape}});
  }
  f.write(file,node);const g=f.recompile(),selection={...g.selection,schema_version:SUM_FIELD_FACTORY_VERSION} as ConfiguredFactorySelection;
  const p=planConfiguredFactories(g.graph,g.fields,selection,sumSources),e:any=expected(),root=path.join(f.temp,'inline-only');
  assert.deepEqual(p.sum_modules,[]);assert.deepEqual(p.enum_components,[]);assert.equal(p.artifacts.length,6);
  for(const m of e.modules){m.composed=true;m.collection_support_sha256=sumSupportHash;m.collection_protocols=['boolValue','stringValue','stringValue'];}
  const c=e.modules[0];c.provider='commerce:contact';
  c.collection_protocols.push('listValue(sumValue(Object.freeze({["None"]:null,["Ready"]:stringValue})))','setValue(sumValue(Object.freeze({["None"]:null,["Ready"]:stringValue})))');
  assert.equal(native(root,p.artifacts,e).observe().result,'pass');
  const vf=loadJs(root,paths.contact).createContactFactory(),ready=(payload='a')=>({variant:'Ready',payload}),none={variant:'None'};
  const base=(list:any[],set:any[])=>contact({z_inline_list:list,z_inline_set:set});
  const a=vf.create(base([ready(),none],[ready(),none])),b=vf.create(base([ready(),none],[none,ready()])),c2=vf.create(base([none,ready()],[none,ready()]));
  assert.ok(a.ok&&b.ok&&c2.ok);assert.ok(a.value.equals(b.value));assert.equal(a.value.equals(c2.value),false);
  assert.equal(vf.create(base([],[ready(),ready()])).ok,false);assert.ok(vf.create(base([ready(),ready()],[])).ok);
  const keys=[a,b,c2].map(r=>compiledFieldValueKey(g.fields,'commerce:contact',sumWire(r.value)));
  assert.equal(keys[0],keys[1]);assert.notEqual(keys[0],keys[2]);
});
const enumPath=(feature='commerce')=>'application/features/'+feature+'/src/domain/enums/status.component.ts';
function enumFixture(t:any) {
  const f=fixture(t);
  for(const feature of ['audit','commerce']) {
    const p='specs/'+feature+'/feature.json',featureNode=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
    featureNode.nodes.push('status');f.write(p,featureNode);
    f.write('specs/'+feature+'/nodes/status.json',{schema_version:'domainspec.node/v1',feature_id:feature,node_id:'status',kind:'Enum',
      body:{description:feature+' status',values:['Submitted','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',
        ontology_node:'FIXTURE-'+feature.toUpperCase()+'-STATUS',variants:['Submitted','Draft'].map(name=>({name,payload:null,ontology_variant:'FIXTURE-'+feature.toUpperCase()+'-STATUS#'+name}))}}});
  }
  for(const node_id of ['contact','customer']) {
    const p='specs/commerce/nodes/'+node_id+'.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
    const named={kind:'named',selector:'commerce:status'}, additions:any={status:named};
    if(node_id==='contact') Object.assign(additions,{status_history:{kind:'list',element:named},status_maybe:{kind:'optional',element:named},status_set:{kind:'set',element:named}});
    for(const [name,type] of Object.entries(additions) as any) {
      node.body.fields.push(name);node.body.typed_contract.properties.push({name,type,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'FIXTURE-'+node_id.toUpperCase()+'#'+name});
    }
    f.write(p,node);
  }
  const recompile=()=>{
    const graph=loadCompiledProjectGraph(f.source),fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,
      contract_sha256:FIELD_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,
      roots:['commerce:customer','commerce:contact','audit:status'],bindings:[]},descriptor);
    return {graph,fields,selection:{...f.selection,schema_version:ENUM_FIELD_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256} as ConfiguredFactorySelection};
  };
  return {...f,...recompile(),recompile};
}
function enumExpected():any {
  const e:any=expected();
  for(const m of e.modules) {
    m.composed=true;m.collection_support_sha256=enumSupportHash;
    if(m.name==='Contact')m.provider='commerce:contact';
    const indices=m.name==='Contact'?[3,4,5,6]:[3];
    for(const i of indices)m.imports.push({path:'../enums/status.component.js',symbol:'StatusValueComponent',local:'component'+i},
      {path:'../enums/status.component.js',symbol:'StatusCase',local:'Component'+i+'Case',type_only:true});
    m.collection_protocols=m.name==='Contact'?['boolValue','stringValue','stringValue','enumValue(component3)','listValue(enumValue(component4))','optionalValue(enumValue(component5))','setValue(enumValue(component6))']:['boolValue','stringValue','stringValue','enumValue(component3)'];
  }
  e.enum_components=['audit','commerce'].map(feature=>({path:enumPath(feature),definition:enumPath(feature).replace('.component.ts','.ts'),
    definition_import:'./status.js',name:'Status',selector:feature+':status',members:['Draft','Submitted'],contract_sha256:enumContractHash}));
  e.enum_provider={path:'application/runtime/enum.ts',sha256:'378e09358713b431e4a24e664e484feae0122462e47aabfa653ae21a17315fcc'};
  e.files.push(...e.enum_components.flatMap((e:any)=>[e.path,e.definition]),e.enum_provider.path);return e;
}
test('PCR-06 Enum fields emit selective deterministic support',()=>{
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',
    protocol_id:'typescript.owned-value-object-factory/v1',fields:[{name:'id',tag:'String',identity:true,wrappers:[]},{name:'enabled',tag:'Bool',identity:false,wrappers:['optional']},
      {name:'child',tag:'ValueObject',identity:false,wrappers:['list'],component:{selector:'test:child',path:'./child.js',symbol:'ChildValueComponent',local:'component2',type_symbol:'ChildSnapshot',type_local:'Component2Snapshot'}}],
    imports:[],base_validators:[],extensions:[],component_protocol_sha256:'collection',composed:true,collections:true};
  assertDeterministicDistinctKinds(m);
});
test('PCR-06 Enum fields bind original checked projection and unchanged provider deterministically',t=>{
  const f=enumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,enumSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v4-candidate');assert.equal(p.modules.length,2);assert.equal(p.artifacts.length,11);
  assert.equal(p.enum_components!.length,2);assert.equal(p.collection_support!.sha256,enumSupportHash);
  const projection=compileSelectedProjectFields(f.graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,
    graph_sha256:createCompiledProjectCertificate(f.graph).graph_sha256,roots:['audit:status','commerce:status'],bindings:[]},descriptor);
  const ep=planConfiguredEnums(projection,{schema_version:CONFIGURED_ENUM_VERSION,language:'typescript',module_root:'application',field_compilation_sha256:projection.compilation_sha256},
    {configuration:sources.configuration,base:sources.base,typescript:sources.typescript,provider:enumSources.enum_provider});
  assert.equal(p.enum_field_compilation_sha256,projection.compilation_sha256);assert.equal(p.enum_plan_sha256,ep.plan_sha256);
  for(const a of ep.artifacts) {
    const component=p.enum_components!.find(c=>c.definition_path===a.relative_path),emitted=p.artifacts.find(v=>v.relative_path===a.relative_path)!;
    if(component) {assert.equal(component.unannotated_definition_sha256,a.sha256);assert.equal(component.definition_sha256,emitted.sha256);assert.notEqual(a.sha256,emitted.sha256);}
    else assert.deepEqual(emitted,a);
  }
  for(const b of p.component_bindings!)assert.equal(b.artifact_sha256,p.artifacts.find(a=>a.relative_path===b.relative_path)!.sha256);
  assert.equal(p.modules[0]!.fields.find(v=>v.name==='status')!.tag,'Enum');
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},enumSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'another/root'},enumSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const key of Object.keys(enumSources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...enumSources,[key]:(enumSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,sources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:COLLECTION_FACTORY_VERSION},collectionSources));
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,enumSources));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,enumSources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,field_compilation_sha256:'0'.repeat(64)},enumSources));
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  assert.ok(Object.isFrozen(p.enum_components![0]!.members));assert.equal(Object.isFrozen(f.selection.factories),false);
  fs.renameSync(f.source,path.join(f.temp,'moved'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,enumSources),p);
});
test('PCR-06 Enum fields reject payload sums, Enum identity and implicit Rule projections',t=>{
  const f=enumFixture(t),p='specs/commerce/nodes/status.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  node.body.typed_contract.variants[0].payload={kind:'scalar',name:'String'};f.write(p,node);
  const g=f.recompile();assert.throws(()=>planConfiguredFactories(g.graph,g.fields,g.selection,enumSources),/payload-bearing sum unsupported/);
  node.body.typed_contract.variants[0].payload=null;f.write(p,node);
  const good=f.recompile();
  for(const argument of [{parameter:'label',field:'status'},{parameter:'label',path:['status','variant']}]) {
    const selection=structuredClone(good.selection),b=selection.factories.find(b=>b.selector==='commerce:contact')! as any;
    b.base_validators[0].arguments=[argument];
    assert.throws(()=>planConfiguredFactories(good.graph,good.fields,selection,enumSources),/validator path/);
  }
  const entityPath='specs/commerce/nodes/customer.json',entity=JSON.parse(fs.readFileSync(path.join(f.source,entityPath),'utf8'));
  entity.body.typed_contract.properties.find((p:any)=>p.name==='id').type={kind:'named',selector:'commerce:status'};f.write(entityPath,entity);
  assert.throws(()=>f.recompile(),/identity/i);
});
test('PCR-06 native Enum cases retain semantic equality, wrappers and runtime ownership',t=>{
  const f=enumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,enumSources),root=path.join(f.temp,'enum-native'),n=native(root,p.artifacts,enumExpected());
  assert.deepEqual(n.observe().errors,[]);
  const c=loadJs(root,enumPath()).StatusValueComponent,other=loadJs(root,enumPath('audit')).StatusValueComponent;
  const vf=loadJs(root,paths.contact).createContactFactory(),ef=loadJs(root,paths.customer).createCustomerFactory();
  const D=c.values.Draft,S=c.values.Submitted,base=(patch:object={})=>contact({status:D,status_history:[D,S],status_set:[D,S],...patch});
  assert.equal(c.fromVariant('Draft'),D);assert.equal(c.fromVariant(loadJs(root,enumPath('audit').replace('.component.ts','.ts')).Status.Draft),D,'decoding intentionally selects the target Enum; strings do not carry provenance');
  assert.ok(Object.isFrozen(c)&&Object.isFrozen(c.values)&&Object.isFrozen(D));assert.equal(c.equals(D,other.values.Draft),false);
  for(const value of ['missing','__proto__',null,{},new String('Draft')])assert.throws(()=>c.fromVariant(value));
  const patches=[{},{status:D},{status:S},{status_maybe:null},{status_maybe:D},{status_maybe:S},{status_history:[S,D]},{status_history:[D,D]},{status_history:[]},{status_set:[S,D]},{status_set:[]},{status_set:[D]}];
  const wire=(v:any):any=>Array.isArray(v)?v.map(wire):v&&typeof v==='object'&&Object.hasOwn(v,'variant')?{variant:v.variant}:v;
  const rows=patches.map(patch=>{const input=base(patch),r=vf.create(input);assert.equal(r.ok,true);
    const key=compiledFieldValueKey(f.fields,'commerce:contact',Object.fromEntries(Object.entries(input).map(([k,v])=>[k,wire(v)])));
    return {value:r.value,key};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  const input=base(),created=vf.create(input);assert.equal(created.value.fields.status_maybe,null);assert.equal(created.value.components.find((c:any)=>c.field==='status').tag,'Enum');
  assert.equal(Object.isFrozen(input),false);assert.equal(Object.isFrozen(input.status_history),false);
  input.status_history.reverse();assert.deepEqual(created.value.fields.status_history,[D,S]);
  const a=ef.create(customer({status:D})),b=ef.transition(a.value,customer({status:S}));assert.ok(a.ok&&b.ok&&a.value.sameIdentity(b.value));
  assert.ok(vf.reconstruct(base()).ok);assert.equal(vf.extend('enabled').create(base({enabled:false})).ok,false);
  for(const bad of ['Draft',{variant:'Draft'},other.values.Draft,{...D},Object.create(D),new Proxy(D,{})]) {
    assert.equal(c.isOwned(bad),false);assert.throws(()=>c.key(bad));
    for(const patch of [{status:bad},{status_maybe:bad},{status_history:[bad]},{status_set:[bad]}]) {
      const r=vf.create(base(patch));assert.equal(r.ok,false);assert.deepEqual(r.failure_codes,['INVALID_FIELDS']);assert.deepEqual(r.trace.validators,[]);
    }
  }
  for(const patch of [{status_maybe:undefined},{status_set:[D,D]},{status_history:[D,undefined]},{status_history:new Array(1)}])assert.equal(vf.create(base(patch)).ok,false);
  // A second evaluation of identical adapter bytes must not impersonate its original instance.
  const req=createRequire(import.meta.url),js=path.join(root,'js',enumPath().replace('.ts','.js'));
  delete req.cache[req.resolve(js)];const duplicate=req(js).StatusValueComponent;
  assert.equal(vf.create(base({status:duplicate.values.Draft})).ok,false);
  const badType=path.join(root,'bad-type.ts');
  fs.writeFileSync(badType,'import {StatusValueComponent as Wrong} from "./'+enumPath('audit').replace('.ts','.js')+'";\nimport type {ContactFields} from "./'+paths.contact.replace('.ts','.js')+'";\nconst bad:ContactFields["status"]=Wrong.values.Draft;\n');
  assert.throws(()=>n.compile([badType]),(error:any)=>{
    assert.match(String(error.stdout),/bad-type\.ts.*error TS(?:2322|2741)/);
    assert.match(String(error.stdout),/brand/);return true;
  });
});
test('PCR-06 native Enum fields compose with nested collections and owned Value Objects',t=>{
  const f=collectionFixture(t),sourceEnum=enumFixture(t),featurePath='specs/commerce/feature.json',feature=JSON.parse(fs.readFileSync(path.join(f.source,featurePath),'utf8'));
  feature.nodes.push('status');f.write(featurePath,feature);
  const nodePath='specs/commerce/nodes/status.json';f.write(nodePath,JSON.parse(fs.readFileSync(path.join(sourceEnum.source,nodePath),'utf8')));
  const contactPath='specs/commerce/nodes/contact.json',node=JSON.parse(fs.readFileSync(path.join(f.source,contactPath),'utf8'));
  node.body.fields.push('z_status');node.body.typed_contract.properties.push({name:'z_status',identity:false,cardinality:'optional',meaning:'optional set of ordered status histories',
    ontology_property:'FIXTURE-CONTACT#z_status',type:{kind:'optional',element:{kind:'set',element:{kind:'list',element:{kind:'named',selector:'commerce:status'}}}}});
  f.write(contactPath,node);
  const g=f.recompile(),selection={...g.selection,schema_version:ENUM_FIELD_FACTORY_VERSION} as ConfiguredFactorySelection;
  const p=planConfiguredFactories(g.graph,g.fields,selection,enumSources),root=path.join(f.temp,'enum-nested'),e:any=collectionExpected(),ee=enumExpected();
  e.enum_components=ee.enum_components.filter((m:any)=>m.selector==='commerce:status');e.enum_provider=ee.enum_provider;
  e.files.push(enumPath(),enumPath().replace('.component.ts','.ts'),e.enum_provider.path);
  for(const m of e.modules)m.collection_support_sha256=enumSupportHash;
  const c=e.modules.find((m:any)=>m.name==='Contact');
  c.imports.push({path:'../enums/status.component.js',symbol:'StatusValueComponent',local:'component17'},
    {path:'../enums/status.component.js',symbol:'StatusCase',local:'Component17Case',type_only:true});
  c.collection_protocols.push('optionalValue(setValue(listValue(enumValue(component17))))');
  assert.equal(native(root,p.artifacts,e).observe().result,'pass');
  const r=composedRuntime(root),status=loadJs(root,enumPath()).StatusValueComponent,D=status.values.Draft,S=status.values.Submitted;
  const make=(z_status:any)=>r.vf.create(collectionInput({history:[r.tf.create({key:'tenant'}).value],z_status}));
  const a=make([[D,S],[S,D]]),b=make([[S,D],[D,S]]),different=make([[D,S]]);
  assert.ok(a.ok&&b.ok&&different.ok);assert.ok(a.value.equals(b.value));assert.equal(a.value.hash(),b.value.hash());assert.equal(a.value.equals(different.value),false);
  assert.equal(make([[D,S],[D,S]]).ok,false);assert.equal(make([[{variant:'Draft'}]]).ok,false);
  assert.ok(r.ef.create(r.input({contact:a.value})).ok);
});
test('PCR-06 Enum observer catches case substitution and ownership removal',t=>{
  const f=enumFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,enumSources),root=path.join(f.temp,'enum-observer'),n=native(root,p.artifacts,enumExpected());
  assert.equal(n.observe().result,'pass');
  const file=path.join(root,enumPath()),original=fs.readFileSync(file,'utf8');
  for(const [from,to,error] of [['variant:EnumDefinition["Draft"]','variant:EnumDefinition["Submitted"]','enum-cases:'],['ownership.has(value)','true','enum-ownership:']]) {
    assert.ok(original.includes(from!));fs.writeFileSync(file,original.replace(from!,to!));
    assert.ok(n.observe().errors.some((e:string)=>e.startsWith(error!)));fs.writeFileSync(file,original);
  }
});
function collectionFixture(t:any) {
  const f=composedFixture(t),p='specs/commerce/nodes/contact.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  const scalar=(name='String')=>({kind:'scalar',name}),named={kind:'named',selector:'audit:tenant'},wrap=(kind:string,element:any)=>({kind,element});
  const additions={memo:wrap('optional',scalar()),consent:wrap('optional',scalar('Bool')),alternate:wrap('optional',named),
    messages:wrap('list',scalar()),flags:wrap('set',scalar('Bool')),history:wrap('list',named),members:wrap('set',named),
    matrix:wrap('list',wrap('list',scalar('Bool'))),buckets:wrap('set',wrap('list',scalar())),ranked:wrap('list',wrap('set',scalar())),groups:wrap('set',wrap('set',scalar())),
    optional_list:wrap('optional',wrap('list',scalar())),optional_set:wrap('optional',wrap('set',named)),optional_matrix:wrap('optional',wrap('list',wrap('list',scalar())))};
  for(const [name,type] of Object.entries(additions)) {
    node.body.fields.push(name);node.body.typed_contract.properties.push({name,type,cardinality:type.kind==='optional'?'optional':type.kind==='set'?'many-unique':'many',identity:false,meaning:name,ontology_property:'FIXTURE-CONTACT#'+name});
  }
  f.write(p,node);
  const recompile=()=>{
    const graph=loadCompiledProjectGraph(f.source),fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,
      graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:['commerce:customer','audit:alternate-tenant'],bindings:[]},descriptor);
    const selection:ConfiguredFactorySelection={...f.selection,schema_version:COLLECTION_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256};
    return {graph,fields,selection};
  };
  return {...f,...recompile(),recompile};
}
function collectionExpected() {
  const e=composedExpected();
  const contact=e.modules.find((m:any)=>m.name==='Contact');
  for(const i of [0,6,10,15]) contact.imports.push(
    {path:'../../../../audit/src/domain/value-objects/tenant.js',symbol:'TenantValueComponent',local:'component'+i},
    {path:'../../../../audit/src/domain/value-objects/tenant.js',symbol:'TenantSnapshot',local:'Component'+i+'Snapshot',type_only:true});
  for(const m of e.modules)m.collection_support_sha256=collectionSupportHash;
  contact.collection_protocols=['optionalValue(ownedValue(component0))','setValue(listValue(stringValue))','optionalValue(boolValue)','boolValue','setValue(boolValue)','setValue(setValue(stringValue))','listValue(ownedValue(component6))','stringValue','stringValue','listValue(listValue(boolValue))','setValue(ownedValue(component10))','optionalValue(stringValue)','listValue(stringValue)','optionalValue(listValue(stringValue))','optionalValue(listValue(listValue(stringValue)))','optionalValue(setValue(ownedValue(component15)))','listValue(setValue(stringValue))'];
  e.modules.find((m:any)=>m.name==='Customer').collection_protocols=['ownedValue(component0)','boolValue','ownedValue(component2)','stringValue'];
  e.modules.find((m:any)=>m.name==='OrderId').collection_protocols=['stringValue','ownedValue(component1)'];
  for(const name of ['Tenant','AlternateTenant'])e.modules.find((m:any)=>m.name===name).collection_protocols=['stringValue'];
  return e;
}
type CollectionFixtureFields=ContactFixtureFields&{messages:string[];flags:boolean[];history:unknown[];members:unknown[];matrix:boolean[][];buckets:string[][];ranked:string[][];groups:string[][]};
function collectionInput():CollectionFixtureFields;
function collectionInput<P extends object>(patch:P):FixtureSpread<CollectionFixtureFields,P>;
function collectionInput(patch:object={}){return contact({messages:['one','two'],flags:[true,false],history:[],members:[],matrix:[[true,false],[]],buckets:[['one'],['two']],ranked:[['one','two'],[]],groups:[['one'],['two']],...patch});}
const rawValue=(value:any):any=>Array.isArray(value)?value.map(rawValue):value&&typeof value==='object'&&Object.hasOwn(value,'fields')?Object.fromEntries(Object.entries(value.fields).map(([key,v])=>[key,rawValue(v)])):value;

test('PCR-06 collections emit selective deterministic support',()=>{
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',protocol_id:'typescript.owned-value-object-factory/v1',fields:[{name:'id',tag:'String',identity:true},{name:'enabled',tag:'Bool',identity:false},{name:'child',tag:'ValueObject',identity:false,component:{selector:'test:child',path:'./child.js',symbol:'ChildValueComponent',local:'component2',type_symbol:'ChildSnapshot',type_local:'Component2Snapshot'}}],imports:[],base_validators:[],extensions:[],component_protocol_sha256:'composed',composed:true};
  assertDeterministicDistinctKinds(m);
});

test('PCR-06 collections bind exact protocol bytes, checked shapes and deterministic provider closure',t=>{
  const f=collectionFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v3-candidate');assert.equal(p.artifacts.length,9);assert.equal(p.authority_effect,'none');
  assert.deepEqual(p.collection_support,{protocol_id:'typescript.owned-collection-components/v1-candidate',sha256:collectionSupportHash,placement:'inline-private'});
  assert.equal(p.component_bindings!.length,7);
  for(const binding of p.component_bindings!)assert.equal(binding.artifact_sha256,p.artifacts.find(a=>a.relative_path===binding.relative_path)!.sha256);
  const shape=p.modules.find(m=>m.selector==='commerce:contact')!.fields;
  assert.deepEqual(shape.find(f=>f.name==='optional_set')!.wrappers,['optional','set']);assert.equal(shape.find(f=>f.name==='optional_set')!.component!.selector,'audit:tenant');
  assert.deepEqual(shape.find(f=>f.name==='matrix')!.wrappers,['list','list']);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},collectionSources),p);
  const relocated=planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'different/root'},collectionSources);assert.deepEqual(relocated.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const key of ['configuration','base','typescript','factory_contract'])assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...collectionSources,[key]:(collectionSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:COMPOSED_FACTORY_VERSION},composedSources),/required String\/Bool/);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,composedSources),/contract drift/);
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,collectionSources));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,collectionSources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,field_compilation_sha256:'0'.repeat(64)},collectionSources));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:f.selection.factories.filter(b=>b.selector!=='audit:tenant')},collectionSources),/coverage/);
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);assert.ok(Object.isFrozen(shape[0]!.wrappers));
  assert.equal(Object.isFrozen(f.selection.factories[0]!.base_validators[0]!.arguments[0]!.path),false);
  fs.renameSync(f.source,path.join(f.temp,'moved'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources),p);
});

test('PCR-06 native collections agree with checked-field equality without collapsing absence, order or uniqueness',t=>{
  const f=collectionFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources),root=path.join(f.temp,'collections');const n=native(root,p.artifacts,collectionExpected());
  assert.equal(n.observe().result,'pass');
  const r=composedRuntime(root),tenant=(key='a')=>r.tf.create({key}).value;
  const patches=[{}, {memo:null},{memo:''},{memo:'text'},{memo:'é'},{memo:'e\u0301'}, {consent:null},{consent:false},{consent:true},
    {alternate:tenant()},{alternate:tenant()},{alternate:tenant('b')},{messages:['two','one']},{messages:['one','one']},{messages:[]},
    {flags:[false,true]},{flags:[]},{flags:[false]},{flags:[true]}, {history:[tenant(),tenant('b')]},{history:[tenant('b'),tenant()]},{history:[tenant(),tenant()]},
    {members:[tenant(),tenant('b')]},{members:[tenant('b'),tenant()]},{members:[tenant()]}, {matrix:[[],[true,false]]},{matrix:[[false,true],[]]},
    {buckets:[['two'],['one']]},{buckets:[['a','b']]},{buckets:[['b','a']]}, {ranked:[['two','one'],[]]},{ranked:[[],['one','two']]},
    {groups:[['two'],['one']]},{groups:[['b','a'],[]]},{groups:[[],['a','b']]},
    {optional_list:null},{optional_list:[]},{optional_list:['a']},{optional_set:[]},{optional_set:[tenant(),tenant('b')]},{optional_set:[tenant('b'),tenant()]},
    {optional_matrix:[]},{optional_matrix:[[]]},{optional_matrix:[['a'],['b']]},{optional_matrix:[['b'],['a']]}];
  const rows=patches.map(patch=>{const input=collectionInput(patch),result=r.vf.create(input);assert.equal(result.ok,true,JSON.stringify(patch));
    const key=compiledFieldValueKey(f.fields,'commerce:contact',Object.fromEntries(Object.entries(input).map(([k,v])=>[k,rawValue(v)])));
    assert.equal(key,compiledFieldValueKey(f.fields,'commerce:contact',rawValue(result.value)),'normalization preserves model meaning');return {value:result.value,key};});
  for(const left of rows)for(const right of rows){const equal=left.key===right.key;assert.equal(left.value.equals(right.value),equal);assert.equal(left.value.hash()===right.value.hash(),equal);}
  assert.equal(rows[0]!.value.fields.memo,null);assert.equal(rows[0]!.value.fields.optional_list,null);
  const base=rows[0]!.value,reverse=r.vf.create(collectionInput({flags:[false,true]})).value;
  assert.deepEqual(base.fields.flags,reverse.fields.flags,'set output has canonical order');
  assert.equal(base.components.find((c:any)=>c.field==='memo').tag,'Optional');assert.equal(base.components.find((c:any)=>c.field==='messages').tag,'List');assert.equal(base.components.find((c:any)=>c.field==='flags').tag,'Set');
});

test('PCR-06 collections copy caller arrays, recursively freeze and expose readonly nullable types',t=>{
  const f=collectionFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources),root=path.join(f.temp,'collection-immutability'),n=native(root,p.artifacts,collectionExpected());
  const r=composedRuntime(root),input=collectionInput({optional_list:['a'],optional_set:[r.tf.create({key:'a'}).value],optional_matrix:[['a']]});
  const before=rawValue({fields:input}),result=r.vf.create(input);assert.equal(result.ok,true);assert.deepEqual(rawValue({fields:input}),before);
  const value=result.value,normalizedBefore=rawValue(value),visit=(v:any):void=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));if(Array.isArray(v))v.forEach(visit);else if(Object.hasOwn(v,'fields'))visit(v.fields);else Object.values(v).forEach(visit);}};visit(value.fields);
  assert.notEqual(value.fields.messages,input.messages);assert.notEqual(value.fields.matrix[0],input.matrix[0]);assert.equal(Object.isFrozen(input.messages),false);
  input.messages.push('changed');input.matrix[0].reverse();input.groups[0].push('changed');input.flags.reverse();assert.deepEqual(rawValue(value),normalizedBefore);
  const nullPrototype=Object.assign(Object.create(null),collectionInput());assert.equal(r.vf.create(nullPrototype).ok,true);
  const consumer=path.join(root,'consumer.ts');fs.writeFileSync(consumer,'import type {ContactSnapshot} from "./'+paths.contact.replace(/\.ts$/,'.js')+'";\ndeclare const value:ContactSnapshot;\nvalue.fields.messages.push("bad");\nvalue.fields.matrix[0].push(true);\nconst memo:string=value.fields.memo;\n');
  assert.throws(()=>n.compile([consumer]),(e:any)=>/does not exist/.test(String(e.stdout))&&/null/.test(String(e.stdout)));
});

test('PCR-06 malformed and duplicate collections fail before Rules on every factory route',t=>{
  const f=collectionFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources),root=path.join(f.temp,'collection-hostile');native(root,p.artifacts,collectionExpected());
  const r=composedRuntime(root),tenant=()=>r.tf.create({key:'a'}).value;let reads=0;
  const getter=['a'];Object.defineProperty(getter,'0',{get(){reads++;return 'a';},enumerable:true});
  const hidden=['a'];Object.defineProperty(hidden,'0',{value:'a',enumerable:false});
  const inherited=['a'];Object.setPrototypeOf(inherited,Object.create(Array.prototype));
  const symbol=['a'];Object.defineProperty(symbol,Symbol.iterator,{value:function*(){reads++;yield 'a';}});
  const patches=[{memo:undefined},{consent:0},{optional_list:undefined},{optional_list:[null]},{optional_set:new Set()},
    {messages:null},{messages:new Set(['a'])},{messages:[undefined]},{messages:['a',true]},{messages:new Array(2)},
    {messages:getter},{messages:hidden},{messages:inherited},{messages:symbol},{messages:Object.assign(['a'],{extra:true})},
    {flags:[true,true]},{flags:[false,false]},{members:[tenant(),tenant()]},{members:[{...tenant()}]},
    {history:[{key:'a'}]},{alternate:{...tenant()}},{matrix:[[true],null]},{matrix:[[true],['false']]},
    {buckets:[['a'],['a']]},{groups:[['a','b'],['b','a']]},{ranked:[['a','a']]},{optional_set:[tenant(),tenant()]}];
  for(const patch of patches)for(const method of ['create','reconstruct']){const failure=r.vf[method](collectionInput(patch));assert.equal(failure.ok,false);assert.equal(failure.value,null);assert.deepEqual(failure.trace.validators,[]);assert.deepEqual(failure.trace.phases,['normalize']);}
  for(const key of ['messages','flags','matrix']){const input:any=collectionInput();delete input[key];assert.equal(r.vf.create(input).ok,false);}
  const badField=collectionInput();Object.defineProperty(badField,'memo',{get(){reads++;return 'a';},enumerable:true});assert.equal(r.vf.create(badField).ok,false);assert.equal(reads,0);
  const prior=r.ef.create(r.input({contact:r.vf.create(collectionInput()).value})).value;
  for(const method of ['create','reconstruct'])assert.equal(r.ef[method](r.input({contact:collectionInput()})).value,null);
  assert.equal(r.ef.transition(prior,r.input({contact:collectionInput()})).value,null);
});

test('PCR-06 collection changes preserve Entity identity and additive validation on all routes',t=>{
  const f=collectionFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources),root=path.join(f.temp,'collection-routes');native(root,p.artifacts,collectionExpected());
  const r=composedRuntime(root),first=r.vf.create(collectionInput()).value,second=r.vf.create(collectionInput({messages:[],memo:'changed'})).value;
  assert.equal(first.equals(second),false);
  const input=r.input({contact:first}),prior=r.ef.create(input).value,next=r.ef.transition(prior,r.input({contact:second}));
  assert.equal(next.ok,true);assert.equal(next.value.sameIdentity(prior),true);assert.equal(next.value.hash(),prior.hash());assert.equal(prior.fields.contact,first);
  const ext=r.vf.extend('enabled').extend('visible');
  for(const method of ['create','reconstruct']) {
    assert.equal(ext[method](collectionInput({label:''})).value,null);
    const failed=ext[method](collectionInput({enabled:false}));assert.equal(failed.value,null);assert.deepEqual(traceRules(failed),['audit:has-label','audit:is-enabled']);
    const good=ext[method](collectionInput());assert.equal(good.value.equals(first),true);assert.equal(good.value.hash(),first.hash());assert.deepEqual(traceRules(good),['audit:has-label','audit:is-enabled','commerce:is-visible']);
  }
  const disabled=r.vf.create(collectionInput({enabled:false})).value;
  assert.equal(r.ef.create(r.input({contact:disabled})).ok,true,'parent does not infer child extensions');
  assert.equal(r.ef.extend('visible').transition(prior,r.input({contact:disabled})).value,null,'explicit nested parent Rule still executes');
  assert.equal(r.ef.transition(prior,r.input({id:r.makeId('changed'),contact:first})).value,null);
});

test('PCR-06 collection generation rejects unsafe Rule projections and unsupported leaves without silent skipping',t=>{
  const f=collectionFixture(t);
  for(const segments of [['contact','memo'],['contact','optional_list'],['contact','alternate','key'],['contact','members','key'],['contact','history','0','key']]) {
    const selection=structuredClone(f.selection);(selection.factories[0] as any).base_validators[0]=bindPath('commerce:valid-id','value',...segments);
    assert.throws(()=>planConfiguredFactories(f.graph,f.fields,selection,collectionSources),/validator path/);
  }
  const propPath='specs/commerce/nodes/contact.json',node=JSON.parse(fs.readFileSync(path.join(f.source,propPath),'utf8'));
  node.body.typed_contract.properties.find((p:any)=>p.name==='messages').type.element={kind:'scalar',name:'UInt64'};f.write(propPath,node);
  const u=f.recompile();assert.throws(()=>planConfiguredFactories(u.graph,u.fields,u.selection,collectionSources),/fields only/);
  const identityPath='specs/commerce/nodes/customer.json',entity=JSON.parse(fs.readFileSync(path.join(f.source,identityPath),'utf8'));
  const id=entity.body.typed_contract.properties.find((p:any)=>p.name==='id');id.type={kind:'list',element:id.type};id.cardinality='many';f.write(identityPath,entity);
  assert.throws(()=>f.recompile(),/identity property must have one cardinality/);
});

test('PCR-06 independent collection observation and native behavior distinguish compiling semantic mutants',t=>{
  const f=collectionFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,collectionSources),root=path.join(f.temp,'collection-observer'),n=native(root,p.artifacts,collectionExpected());
  const original=p.artifacts.find(a=>a.relative_path===paths.contact)!.content,file=path.join(root,paths.contact);
  fs.writeFileSync(file,original.replace('const field12Value = listValue(stringValue)','const field12Value = setValue(stringValue)'));
  assert.ok(n.observe().errors.some((e:string)=>e.startsWith('collection-composition:')));fs.writeFileSync(file,original);assert.equal(n.observe().result,'pass');
  const mutants=[
    {name:'list-collapse',rewrite:(s:string)=>s.replace('sequenceValue(element,false)','sequenceValue(element,true)'),check:(r:ReturnType<typeof composedRuntime>)=>assert.equal(r.vf.create(collectionInput({messages:['a','a']})).ok,false)},
    {name:'set-order',rewrite:(s:string)=>s.replace("entries.sort((a,b)=>a.key < b.key ? -1 : a.key > b.key ? 1 : 0);",''),check:(r:ReturnType<typeof composedRuntime>)=>assert.equal(r.vf.create(collectionInput()).value.equals(r.vf.create(collectionInput({flags:[false,true]})).value),false)},
    {name:'mutable-copy',rewrite:(s:string)=>s.replace('const result = Object.freeze(entries.map(entry=>entry.value));','const result = entries.map(entry=>entry.value);'),check:(r:ReturnType<typeof composedRuntime>)=>assert.equal(Object.isFrozen(r.vf.create(collectionInput()).value.fields.messages),false)}
  ];
  for(const mutant of mutants){const content=mutant.rewrite(original);assert.notEqual(content,original);const folder=path.join(f.temp,mutant.name),artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===paths.contact?content:a.content}));
    const observer=native(folder,artifacts,collectionExpected());assert.ok(observer.observe().errors.some((e:string)=>e.startsWith('collection-support:')));mutant.check(composedRuntime(folder));}
});

const composedSources={...sources,factory_contract:read(packagePath+'/composed-factory-contract.json')};
const bindPath=(rule:string,parameter:string,...segments:string[]):FactoryValidatorBinding=>({rule,arguments:[{parameter,path:segments}]});
const composedPaths={...paths,tenant:'application/features/audit/src/domain/value-objects/tenant.ts',
  alternate:'application/features/audit/src/domain/value-objects/alternate-tenant.ts',
  id:'application/features/commerce/src/domain/value-objects/order-id.ts'};
function composedFixture(t:any) {
  const f=fixture(t);
  const json=(p:string)=>JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  for(const [feature,extra] of [['commerce',['order-id']],['audit',['tenant','alternate-tenant']]] as const) {
    const p=`specs/${feature}/feature.json`,node=json(p);node.nodes.push(...extra);f.write(p,node);
  }
  const property=(name:string,type:any,identity=false)=>({name,type,identity,cardinality:'one',meaning:name,ontology_property:'FIXTURE-NESTED#'+name});
  const string=(name:string)=>property(name,{kind:'scalar',name:'String'});
  const named=(name:string,selector:string,identity=false)=>property(name,{kind:'named',selector},identity);
  for(const selector of ['audit:tenant','audit:alternate-tenant','commerce:order-id']) {
    const [feature_id,node_id]=selector.split(':');
    const properties=node_id==='order-id'?[named('tenant','audit:tenant'),string('key')]:[string('key')];
    for(const p of properties)p.ontology_property='FIXTURE-'+node_id!.toUpperCase()+'#'+p.name;
    f.write(`specs/${feature_id}/nodes/${node_id}.json`,{schema_version:'domainspec.node/v1',feature_id,node_id,kind:'Value Object',body:{description:node_id,fields:properties.map(p=>p.name),
      invariant_refs:node_id==='order-id'?['commerce:valid-id','audit:has-label']:['commerce:valid-id'],
      typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+node_id!.toUpperCase(),properties}}});
  }
  const customer=json('specs/commerce/nodes/customer.json');
  customer.body.typed_contract.properties[0]=named('id','commerce:order-id',true);
  customer.body.typed_contract.properties.push(named('contact','commerce:contact'));customer.body.fields.push('contact');
  for(const p of customer.body.typed_contract.properties)p.ontology_property='FIXTURE-CUSTOMER#'+p.name;
  f.write('specs/commerce/nodes/customer.json',customer);
  const graph=loadCompiledProjectGraph(f.source);
  const fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,
    graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:['commerce:customer','audit:alternate-tenant'],bindings:[]},descriptor);
  const factories=structuredClone(f.selection.factories) as any[];
  factories[0].base_validators[0]=bindPath('commerce:valid-id','value','id','tenant','key');
  factories[0].extensions=structuredClone(factories[0].extensions);
  factories[0].extensions[1].validators=[bindPath('commerce:is-visible','flag','contact','enabled')];
  for(const selector of ['audit:tenant','audit:alternate-tenant'])factories.push({selector,base_validators:[bind('commerce:valid-id','value','key')],extensions:[]});
  factories.push({selector:'commerce:order-id',base_validators:[bindPath('commerce:valid-id','value','tenant','key'),bind('audit:has-label','label','key')],extensions:[]});
  const selection:ConfiguredFactorySelection={...f.selection,schema_version:COMPOSED_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256,factories};
  return {...f,graph,fields,selection};
}
// Hand-authored expectations: independent of planner module/import metadata.
function composedExpected() {
  const e:any=expected();
  e.files.push(composedPaths.tenant,composedPaths.alternate,composedPaths.id);
  e.modules[0].composed=true;e.modules[0].provider='commerce:contact';
  e.modules[1].composed=true;
  e.modules[1].base[0]={rule:'commerce:valid-id',call:'validator3({["value"]:fields["id"].fields["tenant"].fields["key"]})'};
  e.modules[1].extensions[1].validators=[{rule:'commerce:is-visible',call:'validator2({["flag"]:fields["contact"].fields["enabled"]})'}];
  const dep=(p:string,s:string,l:string)=>[{path:p,symbol:s+'ValueComponent',local:l},{path:p,symbol:s+'Snapshot',local:l[0]!.toUpperCase()+l.slice(1)+'Snapshot',type_only:true}];
  e.modules[1].imports.push(...dep('../value-objects/contact.js','Contact','component0'),...dep('../value-objects/order-id.js','OrderId','component2'));
  for(const [p,n,s] of [[composedPaths.alternate,'AlternateTenant','audit:alternate-tenant'],[composedPaths.tenant,'Tenant','audit:tenant']])e.modules.push({path:p,name:n,composed:true,provider:s,
    imports:[{path:'../../../../commerce/src/domain/rules/valid-id.js',symbol:'ruleValidId',local:'validator0'}],base:[call('commerce:valid-id','validator0','value','key')],extensions:[]});
  e.modules.push({path:composedPaths.id,name:'OrderId',composed:true,provider:'commerce:order-id',imports:[
    {path:'../../../../audit/src/domain/rules/has-label.js',symbol:'ruleHasLabel',local:'validator0'},
    {path:'../rules/valid-id.js',symbol:'ruleValidId',local:'validator1'},...dep('../../../../audit/src/domain/value-objects/tenant.js','Tenant','component1')],
    base:[{rule:'commerce:valid-id',call:'validator1({["value"]:fields["tenant"].fields["key"]})'},call('audit:has-label','validator0','label','key')],extensions:[]});
  return e;
}
function composedRuntime(root:string) {
  const tenant=loadJs(root,composedPaths.tenant),other=loadJs(root,composedPaths.alternate),id=loadJs(root,composedPaths.id),vo=loadJs(root,paths.contact),entity=loadJs(root,paths.customer);
  const tf=tenant.createTenantFactory(),of=id.createOrderIdFactory(),vf=vo.createContactFactory(),ef=entity.createCustomerFactory();
  const makeId=(tenantKey='tenant-a',key='order-a')=>of.create({tenant:tf.create({key:tenantKey}).value,key}).value;
  const input=(patch:object={})=>customer({id:makeId(),contact:vf.create(contact()).value,...patch});
  return {tenant,other,id,tf,of,vf,ef,makeId,input};
}

test('PCR-06 scalar emitter retains deterministic kind-distinct outputs',()=>{
  const m:ConfiguredFactoryModule={selector:'test:sample',kind:'Value Object',relative_path:'sample.ts',name:'Sample',callable:'createSampleFactory',protocol_id:'typescript.owned-value-object-factory/v1',
    fields:[{name:'id',tag:'String',identity:true},{name:'enabled',tag:'Bool',identity:false}],imports:[],base_validators:[],extensions:[],component_protocol_sha256:'scalar'};
  assertDeterministicDistinctKinds(m);
});

test('PCR-06 composed plans bind checked closure, owned provider artifacts and scalar paths deterministically',t=>{
  const f=composedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,composedSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v2-candidate');assert.equal(p.authority_effect,'none');
  assert.equal(p.artifacts.length,9);assert.equal(p.component_bindings!.length,3);
  for(const b of p.component_bindings!)assert.equal(b.artifact_sha256,p.artifacts.find(a=>a.relative_path===b.relative_path)!.sha256);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},composedSources),p);
  assert.equal(Object.isFrozen(f.selection.factories[0]!.base_validators[0]!.arguments[0]!.path),false);
  const before=canonicalJson(p);(f.selection.factories[0]!.base_validators[0]!.arguments[0]!.path as string[])[0]='changed';assert.equal(canonicalJson(p),before);
  const relocated=planConfiguredFactories(f.graph,f.fields,{...p.selection,module_root:'elsewhere/deep'},composedSources);
  assert.deepEqual(relocated.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  fs.renameSync(f.source,path.join(f.temp,'source-moved'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,p.selection,composedSources),p);
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
});

test('PCR-06 composed selection rejects uncovered dependencies, scalar-lane mixing and invalid paths',t=>{
  const f=composedFixture(t),run=(s:any)=>planConfiguredFactories(f.graph,f.fields,s,composedSources);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:CONFIGURED_FACTORY_VERSION},sources),/required String\/Bool/);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,sources),/contract drift/);
  for(const key of ['configuration','base','typescript','factory_contract'])assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...composedSources,[key]:(composedSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,composedSources));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,composedSources));
  assert.throws(()=>run({...f.selection,field_compilation_sha256:'0'.repeat(64)}));
  assert.throws(()=>run({...f.selection,factories:f.selection.factories.filter(b=>b.selector!=='audit:tenant')}),/coverage/);
  const mutate=(change:(s:any)=>void)=>{const s=structuredClone(f.selection);change(s);assert.throws(()=>run(s));};
  for(const segments of [[],['id'],['id','missing'],['label','key'],['id','tenant','key','extra'],['contact','enabled']])mutate(s=>s.factories[0].base_validators[0].arguments[0].path=segments);
  mutate(s=>s.factories[0].base_validators[0].arguments[0].field='label');
  mutate(s=>s.factories.find((b:any)=>b.selector==='audit:tenant').base_validators=[bind('audit:has-label','label','key')]);
  let reads=0;const s=structuredClone(f.selection);Object.defineProperty(s.factories[0]!.base_validators[0]!.arguments[0]!,'path',{enumerable:true,get(){reads++;return ['id','tenant','key'];}});
  assert.throws(()=>run(s));assert.equal(reads,0);
});

test('PCR-06 native owned composition preserves recursive equality, composite identity and immutable transitions',t=>{
  const f=composedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,composedSources),root=path.join(f.temp,'nested'),n=native(root,p.artifacts,composedExpected());
  assert.equal(n.observe().result,'pass');
  const r=composedRuntime(root),left=r.makeId(),right=r.makeId();assert.notEqual(left,right);assert.equal(left.equals(right),true);assert.equal(left.hash(),right.hash());
  assert.equal(r.id.OrderIdValueComponent.equals(left,right),true);
  for(const changed of [r.makeId('tenant-b'),r.makeId('tenant-a','order-b')]){assert.equal(left.equals(changed),false);assert.notEqual(left.hash(),changed.hash());}
  const a=r.ef.create(r.input({id:left})),b=r.ef.reconstruct(r.input({id:right,label:'Blair',enabled:false,contact:r.vf.create(contact({locale:'pt'})).value}));
  assert.equal(a.ok,true);assert.equal(b.ok,true);assert.equal(a.value.sameIdentity(b.value),true);assert.equal(a.value.hash(),b.value.hash());
  assert.equal(a.value.identity.component.tag,'ValueObject');assert.equal(a.value.identity.component.value,left);
  const raw=(s:any):any=>Object.fromEntries(Object.entries(s.fields).map(([key,value]:any)=>[key,value&&typeof value==='object'&&'fields' in value?raw(value):value]));
  assert.equal(compiledFieldValueKey(f.fields,'commerce:customer',raw(a.value)),compiledFieldValueKey(f.fields,'commerce:customer',raw(b.value)));
  assert.equal(compiledFieldValueKey(f.fields,'commerce:order-id',raw(left)),compiledFieldValueKey(f.fields,'commerce:order-id',raw(right)));
  const next=r.ef.transition(a.value,r.input({id:right,label:'Next'}));assert.equal(next.ok,true);assert.equal(a.value.fields.label,'Alex');
  for(const id of [r.makeId('other'),r.makeId('tenant-a','other')]){const failed=r.ef.transition(a.value,r.input({id}));assert.equal(failed.ok,false);assert.equal(failed.value,null);assert.deepEqual(failed.failure_codes,['IDENTITY_CHANGED']);}
  assert.deepEqual(traceRules(a),['commerce:valid-id','audit:has-label']);
  for(const obj of [left,left.fields,left.fields.tenant,left.fields.tenant.fields,a.value,a.value.fields,a.value.identity,a.value.components,...a.value.components])assert.ok(Object.isFrozen(obj));
  const source={key:'tenant-a'},snapshot=r.tf.create(source).value;source.key='mutated';assert.equal(snapshot.fields.key,'tenant-a');
  for(const [tenantKey,key,tenant2,key2] of [['ab','c','a','bc'],['é','a','e\u0301','a'],['a:1\u0000b','c','a',':1\u0000bc']]) {
    const x=r.makeId(tenantKey,key),y=r.makeId(tenant2,key2);assert.equal(x.equals(y),false);assert.notEqual(x.hash(),y.hash());
  }
});

test('PCR-06 composed fields reject collections, embedded Entities, recursive ownership and Bool identity',t=>{
  for(const scenario of ['optional','list','set','UInt64','entity','cycle','bool-identity']) {
    const f=composedFixture(t),readNode=(p:string)=>JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
    const target=scenario==='cycle'?'specs/commerce/nodes/order-id.json':scenario==='bool-identity'?'specs/audit/nodes/tenant.json':'specs/commerce/nodes/contact.json';
    const node=readNode(target),property=node.body.typed_contract.properties.find((p:any)=>p.name===(scenario==='cycle'?'tenant':scenario==='bool-identity'?'key':'locale'));
    if(scenario==='cycle')property.type={kind:'named',selector:'commerce:order-id'};
    else if(scenario==='bool-identity')property.type={kind:'scalar',name:'Bool'};
    else if(scenario==='entity') {
      property.type={kind:'named',selector:'audit:alternate-tenant'};
      const p='specs/audit/nodes/alternate-tenant.json',entity=readNode(p);entity.kind='Entity';delete entity.body.invariant_refs;entity.body.typed_contract.properties[0].identity=true;f.write(p,entity);
    } else if(scenario==='UInt64')property.type={kind:'scalar',name:'UInt64'};
    else {property.type={kind:scenario,element:{kind:'scalar',name:'String'}};property.cardinality=scenario==='optional'?'optional':scenario==='set'?'many-unique':'many';}
    f.write(target,node);
    assert.throws(()=>{
      const graph=loadCompiledProjectGraph(f.source);
      const fields=compileSelectedProjectFields(graph,{schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,
        graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:['commerce:customer','audit:alternate-tenant'],bindings:[]},descriptor);
      planConfiguredFactories(graph,fields,{...f.selection,field_compilation_sha256:fields.compilation_sha256},composedSources);
    },scenario==='cycle'?/FIELD_EMBEDDING_CYCLE/:scenario==='bool-identity'?/FIELD_IDENTITY_TYPE/:/required String\/Bool\/owned Value Object/,scenario);
  }
});

test('PCR-06 owned inputs reject forged, raw, wrong-concept and duplicate-module child values',t=>{
  const f=composedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,composedSources),root=path.join(f.temp,'ownership'),n=native(root,p.artifacts,composedExpected()),r=composedRuntime(root);
  const id=r.makeId(),tenant=r.tf.create({key:'tenant-a'}).value;let reads=0;
  const fake={get fields(){reads++;return tenant.fields;},hash(){throw Error('ambient');},equals(){throw Error('ambient');}};
  for(const bad of [null,tenant.fields,{...tenant},Object.create(tenant),new Proxy(tenant,{}),fake,r.other.createAlternateTenantFactory().create({key:'tenant-a'}).value]) {
    assert.equal(r.tenant.TenantValueComponent.isOwned(bad),false);assert.throws(()=>r.tenant.TenantValueComponent.key(bad),/UNOWNED_COMPONENT/);
    assert.equal(r.tenant.TenantValueComponent.equals(tenant,bad),false);
    for(const method of ['create','reconstruct']){const failure=r.of[method]({tenant:bad,key:'order-a'});assert.equal(failure.ok,false);assert.equal(failure.value,null);assert.deepEqual(failure.trace.validators,[]);}
  }
  assert.equal(reads,0);
  for(const method of ['create','reconstruct'])assert.equal(r.ef[method](r.input({id:{...id}})).ok,false);
  const previous=r.ef.create(r.input()).value;assert.equal(r.ef.transition(previous,r.input({id:{...id}})).ok,false);
  const duplicateRoot=path.join(f.temp,'duplicate');native(duplicateRoot,p.artifacts,composedExpected());
  assert.equal(r.of.create({tenant:composedRuntime(duplicateRoot).tf.create({key:'tenant-a'}).value,key:'order-a'}).ok,false);
  const consumer=path.join(root,'consumer.ts');fs.writeFileSync(consumer,'import type {OrderIdFields} from "./'+composedPaths.id.replace(/\.ts$/,'.js')+'";\nconst raw:OrderIdFields={tenant:{key:"tenant-a"},key:"order-a"};\n');
  assert.throws(()=>n.compile([consumer]),(e:any)=>/not assignable|does not exist|missing/.test(String(e.stdout)));
});

test('PCR-06 nested construction keeps child invariants and parent additive extensions on every route',t=>{
  const f=composedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,composedSources),root=path.join(f.temp,'nested-validation');native(root,p.artifacts,composedExpected());
  const r=composedRuntime(root),prior=r.ef.create(r.input()).value,extended=r.ef.extend('enabled').extend('visible');
  for(const method of ['create','reconstruct']) {
    assert.equal(r.tf[method]({key:''}).value,null);assert.equal(r.of[method]({tenant:r.tf.create({key:'ok'}).value,key:''}).value,null);
    const failure=extended[method](r.input({enabled:false}));assert.equal(failure.ok,false);assert.equal(failure.value,null);
    assert.deepEqual(traceRules(failure),['commerce:valid-id','audit:has-label','audit:is-enabled']);assert.deepEqual(failure.trace.phases,['normalize']);
    assert.equal(extended[method](r.input({label:''})).ok,false);
  }
  assert.equal(extended.transition(prior,r.input({enabled:false})).ok,false);
  assert.equal(extended.transition(prior,r.input({id:r.makeId('different')})).ok,false);
  const extendedValue=extended.create(r.input()).value;assert.equal(extendedValue.sameIdentity(prior),true);assert.equal(extendedValue.hash(),prior.hash());
  assert.deepEqual(traceRules(extended.create(r.input())),['commerce:valid-id','audit:has-label','audit:is-enabled','commerce:is-visible']);
  // A parent requires the base child concept, not an inferred child extension.
  const baseContact=r.vf.create(contact({enabled:false}));assert.equal(baseContact.ok,true);assert.equal(r.vf.extend('enabled').create(contact({enabled:false})).value,null);
  assert.equal(r.ef.create(r.input({contact:baseContact.value})).ok,true);
  assert.deepEqual(extended.create(r.input({contact:baseContact.value})).failure_codes,['RULE_FAIL:commerce:is-visible']);
});

test('PCR-06 composed structural and behavior controls catch path, provider and recursive-equality mutants',t=>{
  const f=composedFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,composedSources),root=path.join(f.temp,'nested-mutants'),n=native(root,p.artifacts,composedExpected());
  const file=path.join(root,composedPaths.id),original=fs.readFileSync(file,'utf8');
  for(const [before,after,reason] of [
    ['fields["tenant"].fields["key"]','fields["key"]','base-binding:'],
    ['isOwned:owned','isOwned:()=>true','provider-form:'],
    ['TenantValueComponent as component1','AlternateTenantValueComponent as component1','import-binding:']]){
    const changed=original.replace(before!,after!);assert.notEqual(changed,original);fs.writeFileSync(file,changed);assert.ok(n.observe().errors.some((e:string)=>e.startsWith(reason!)));
  }
  fs.writeFileSync(file,original);
  const mutants=[
    {name:'reference-equality',before:'component1.equals(snapshots.get(other)!.fields["tenant"],fields["tenant"])',after:'snapshots.get(other)!.fields["tenant"] === fields["tenant"]',check:(r:ReturnType<typeof composedRuntime>)=>assert.equal(r.makeId().equals(r.makeId()),false)},
    {name:'dropped-key',before:' + part("key") + part("String") + part(fields["key"])',after:'',check:(r:ReturnType<typeof composedRuntime>)=>assert.equal(r.makeId('a','one').hash(),r.makeId('a','two').hash())},
    {name:'child-validation-bypass',before:'validator.validate(fields) === true',after:'true',check:(r:ReturnType<typeof composedRuntime>)=>assert.equal(r.of.create({tenant:r.tf.create({key:'a'}).value,key:''}).ok,true)}
  ];
  for(const mutant of mutants) {
    const content=original.replace(mutant.before,mutant.after);assert.notEqual(content,original);
    const folder=path.join(f.temp,mutant.name),artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===composedPaths.id?content:a.content}));
    const observer=native(folder,artifacts,composedExpected());assert.equal(observer.observe().result,'pass','structural pass alone does not prove behavior');mutant.check(composedRuntime(folder));
  }
});

test('PCR-06 factories bind checked fields, exact Rule artifacts and deterministic configured paths',async t=>{
  const f=fixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sources),before=canonicalJson(f.graph);
  assert.equal(p.artifacts.length,6);assert.deepEqual(p.artifacts.map(a=>a.relative_path).sort(),expected().files.sort());
  assert.equal(p.authority_effect,'none');assert.equal(f.fields.invariant_execution,'not-performed');
  assert.equal(Object.isFrozen(f.selection.factories[0]!.base_validators[0]!.arguments[0]),false,'planning does not freeze caller-owned binding objects');
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,sources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},sources),p);
  const relocated=planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'elsewhere/nested'},sources);
  assert.deepEqual(relocated.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  for(const m of p.modules)for(const v of [...m.base_validators,...m.extensions.flatMap(e=>e.validators)])assert.ok(p.artifacts.some(a=>a.sha256===v.artifact_sha256));
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));assert.ok(Object.isFrozen(p.modules[0]!.base_validators));
  const config=await import(path.join(project,packagePath,'configuration.mjs'));
  const loaded=config.loadConfiguration(undefined,undefined,JSON.parse(fs.readFileSync(path.join(project,packagePath,'configuration-input-boundary-sources.json'),'utf8')));
  const locations=config.previewLocations(config.resolveConfiguration({schema_version:'domainspec.compilation-selection/v1-candidate',language:'typescript',module_root:'application'},loaded),f.graph.nodes.map(n=>({kind:n.kind,feature_id:n.feature_id,node_id:n.node_id})));
  assert.deepEqual(locations.map((l:any)=>l.source_path).sort(),p.artifacts.map(a=>a.relative_path).sort());
  fs.renameSync(f.source,path.join(f.temp,'moved-source'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,sources),p);assert.equal(canonicalJson(f.graph),before);
});

test('PCR-06 factories reject unchecked/stale input, missing invariants and validator binding bypasses',t=>{
  const f=fixture(t),run=(s:any)=>planConfiguredFactories(f.graph,f.fields,s,sources);
  assert.throws(()=>planConfiguredFactories(structuredClone(f.graph),f.fields,f.selection,sources));
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,sources));
  for(const key of ['configuration','base','typescript','factory_contract'])assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...sources,[key]:(sources as any)[key]+' '}));
  for(const patch of [{schema_version:'future'},{language:'rust'},{module_root:'../escape'},{module_root:'class'},{field_compilation_sha256:'0'.repeat(64)},{factories:[]},{ignore_blockers:true}])assert.throws(()=>run({...f.selection,...patch}));
  const mutate=(change:(s:any)=>void)=>{const s=structuredClone(f.selection);change(s);assert.throws(()=>run(s));};
  mutate(s=>s.factories[0].base_validators=[]);
  mutate(s=>s.factories[1].base_validators=[bind('commerce:valid-id','value','locale')]);
  mutate(s=>s.factories[0].base_validators[0].arguments=[]);
  mutate(s=>s.factories[0].base_validators[0].arguments[0].field='enabled');
  mutate(s=>s.factories[0].base_validators[0].arguments[0].field='missing');
  mutate(s=>s.factories[0].base_validators[0].rule='commerce:contact');
  mutate(s=>s.factories[0].extensions.push(s.factories[0].extensions[0]));
  mutate(s=>s.factories[0].extensions[0].validators=[s.factories[0].base_validators[0]]);
  mutate(s=>s.factories[0].base_validators[0].arguments[0].coerce=true);
  let reads=0;assert.throws(()=>run({...f.selection,get factories(){reads++;return f.selection.factories;}}));assert.equal(reads,0);
  const node=JSON.parse(fs.readFileSync(path.join(f.source,'specs/commerce/nodes/customer.json'),'utf8'));node.body.description='changed';f.write('specs/commerce/nodes/customer.json',node);
  assert.throws(()=>planConfiguredFactories(f.recompile().graph,f.fields,f.selection,sources),/stale graph/);
});

test('PCR-06 factories reject unsupported field forms before any source artifact is returned',t=>{
  for(const type of [{kind:'scalar',name:'UInt64'},{kind:'optional',element:{kind:'scalar',name:'String'}},{kind:'list',element:{kind:'scalar',name:'String'}}]) {
    const f=fixture(t),p='specs/commerce/nodes/contact.json',node=JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
    const property=node.body.typed_contract.properties.find((p:any)=>p.name==='locale');property.type=type;property.cardinality=type.kind==='optional'?'optional':type.kind==='list'?'many':'one';f.write(p,node);
    const g=f.recompile();assert.throws(()=>planConfiguredFactories(g.graph,g.fields,g.selection,sources),/required String\/Bool/);
  }
});

test('PCR-06 native factories validate all routes and preserve Entity versus Value Object semantics',t=>{
  const f=fixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sources),root=path.join(f.temp,'native'),n=native(root,p.artifacts);
  assert.equal(n.observe().result,'pass');
  const {createCustomerFactory}=loadJs(root,paths.customer),{createContactFactory}=loadJs(root,paths.contact);
  const ef=createCustomerFactory(),vf=createContactFactory(),a=ef.create(customer()),b=ef.reconstruct(customer({label:'Blair',enabled:false}));
  assert.equal(a.ok,true);assert.equal(b.ok,true);assert.equal(a.value.sameIdentity(b.value),true);assert.equal(a.value.hash(),b.value.hash());
  assert.deepEqual(a.trace.phases,['normalize','resolve-identity','form','freeze']);
  assert.deepEqual(traceRules(a),['commerce:valid-id','audit:has-label']);
  assert.equal(compiledFieldValueKey(f.fields,'commerce:customer',a.value.fields),compiledFieldValueKey(f.fields,'commerce:customer',b.value.fields));
  for(const method of ['create','reconstruct']){const failed=ef[method](customer({label:''}));assert.equal(failed.ok,false);assert.equal(failed.value,null);assert.deepEqual(failed.trace.phases,['normalize']);}
  const moved=ef.transition(a.value,customer({label:'Next'}));assert.equal(moved.ok,true);assert.equal(a.value.fields.label,'Alex');assert.equal(moved.value.sameIdentity(a.value),true);
  const bad=ef.transition(a.value,customer({id:'other'}));assert.equal(bad.ok,false);assert.deepEqual(bad.trace.phases,['normalize','resolve-identity']);assert.equal(bad.value,null);
  assert.equal(ef.transition({...a.value},customer()).ok,false);
  const x=vf.create(contact()),y=vf.reconstruct(contact());assert.equal(x.ok,true);assert.equal(x.value.equals(y.value),true);assert.equal(x.value.hash(),y.value.hash());
  assert.deepEqual(x.trace.phases,['normalize','form','freeze']);assert.equal('transition' in vf,false);assert.equal('identity' in x.value,false);assert.equal('sameIdentity' in x.value,false);assert.equal('equals' in a.value,false);
  for(const patch of [{label:'Blair'},{locale:'pt'},{enabled:false}]) {const z=vf.create(contact(patch));assert.equal(z.ok,true);assert.equal(x.value.equals(z.value),false);assert.notEqual(x.value.hash(),z.value.hash());assert.notEqual(compiledFieldValueKey(f.fields,'commerce:contact',x.value.fields),compiledFieldValueKey(f.fields,'commerce:contact',z.value.fields));}
  assert.equal(x.value.equals({...x.value}),false);assert.equal(a.value.sameIdentity({...a.value}),false);assert.equal(x.value.equals(a.value),false);
  for(const item of [a.value,a.value.fields,a.value.identity,a.value.components,...a.value.components,x.value,x.value.components,...x.value.components])assert.ok(Object.isFrozen(item));
  const consumer=path.join(root,'consumer.ts');fs.writeFileSync(consumer,'import type {CustomerSnapshot} from "./'+paths.customer.replace(/\.ts$/,'.js')+'";\nconst forged:CustomerSnapshot = {fields:{id:"a",label:"b",enabled:true}};\n');
  assert.throws(()=>n.compile([consumer]),(e:any)=>/missing|not assignable/.test(String(e.stdout)));
});

test('PCR-06 native construction rejects accessors and extra data; extensions are additive, named and acyclic',t=>{
  const f=fixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sources),root=path.join(f.temp,'extensions');native(root,p.artifacts);
  const {createCustomerFactory}=loadJs(root,paths.customer),{createContactFactory}=loadJs(root,paths.contact);
  for(const [factory,input,baseRules] of [[createCustomerFactory(),customer(),['commerce:valid-id','audit:has-label']],[createContactFactory(),contact(),['audit:has-label']]] as any[]) {
    let reads=0;const getter={...input,get label(){reads++;return 'Alex';}};
    for(const invalid of [null,[],{},Object.create(input),{...input,extra:1},{...input,enabled:'true'},getter,Object.defineProperty({...input},'label',{value:'Alex',enumerable:false})])for(const method of ['create','reconstruct']){const result=factory[method](invalid);assert.equal(result.ok,false);assert.equal(result.value,null);}
    assert.equal(reads,0);
    const source={...input},snapshot=factory.create(source).value;source.label='changed';assert.equal(snapshot.fields.label,input.label);
    const ext=factory.extend('enabled'),twice=ext.extend('visible');assert.deepEqual(factory.extensions,[]);assert.deepEqual(twice.extensions,['enabled','visible']);assert.ok(Object.isFrozen(twice.extensions));
    assert.deepEqual(traceRules(twice.create(input)),[...baseRules,'audit:is-enabled','commerce:is-visible']);
    assert.deepEqual(traceRules(factory.extend('visible').extend('enabled').create(input)),[...baseRules,'commerce:is-visible','audit:is-enabled']);
    assert.equal(factory.create({...input,enabled:false}).ok,true);
    for(const method of ['create','reconstruct']){const failed=ext[method]({...input,enabled:false});assert.equal(failed.ok,false);assert.equal(failed.value,null);assert.deepEqual(failed.trace.phases,['normalize']);assert.deepEqual(traceRules(failed),[...baseRules,'audit:is-enabled']);}
    if('transition' in twice)assert.equal(twice.transition(snapshot,{...input,enabled:false}).ok,false);
    assert.equal(ext.create({...input,label:''}).ok,false,'extension cannot bypass base invariant');
    assert.throws(()=>ext.extend('enabled'),/INVALID_EXTENSION/);assert.throws(()=>factory.extend('unknown'),/INVALID_EXTENSION/);assert.throws(()=>factory.extend(()=>true),/INVALID_EXTENSION/);
    const extended=twice.create(input).value;assert.equal(snapshot.hash(),extended.hash());assert.equal('equals' in snapshot?snapshot.equals(extended):snapshot.sameIdentity(extended),true);
  }
});

test('PCR-06 native observer rejects changed factory exports, bindings, runtime injection and classes',t=>{
  const f=fixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sources),root=path.join(f.temp,'ast'),n=native(root,p.artifacts);
  const file=path.join(root,paths.customer),original=fs.readFileSync(file,'utf8');
  const mutants=[['export bypass',original+'\nexport const bypass = () => true;\n','export-set:'],['runtime injection',original.replace('createCustomerFactory = ():Factory','createCustomerFactory = (extra:any):Factory'),'factory-entry:'],['rebound argument',original.replace('validator3({["value"]:fields["id"]})','validator3({["value"]:fields["label"]})'),'base-binding:'],['wrong import',original.replace('../rules/valid-id.js','../rules/missing.js'),'import-binding:'],['class form',original+'\nclass Bypass {}\n','class-or-function:'],['serialization equality',original.replace('snapshots.get(other)!.key === key','JSON.stringify(other) === JSON.stringify(fields)'),'ambient-or-serialization:']];
  for(const [label,mutant,reason] of mutants){assert.notEqual(original,mutant,label);fs.writeFileSync(file,mutant!);assert.ok(n.observe().errors.some((s:string)=>s.startsWith(reason!)),label);}
  fs.writeFileSync(file,original);assert.equal(n.observe().result,'pass');
});

test('PCR-06 independent behavior catches compiling validation, equality and identity mutants',t=>{
  const f=fixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,sources);
  const cases=[
    {id:'validation',file:paths.customer,rewrite:(s:string)=>s.replace("validator.validate(fields) === true","true"),check:(root:string)=>assert.equal(loadJs(root,paths.customer).createCustomerFactory().create(customer({label:''})).ok,true)},
    {id:'tuple',file:paths.contact,rewrite:(s:string)=>s.replace('snapshots.get(other)!.fields["locale"] === fields["locale"]','true'),check:(root:string)=>{const f=loadJs(root,paths.contact).createContactFactory();assert.equal(f.create(contact()).value.equals(f.create(contact({locale:'pt'})).value),true);}},
    {id:'identity',file:paths.customer,rewrite:(s:string)=>s.replace('snapshots.get(previous)!.key !== key','false'),check:(root:string)=>{const f=loadJs(root,paths.customer).createCustomerFactory();assert.equal(f.transition(f.create(customer()).value,customer({id:'changed'})).ok,true);}}
  ];
  for(const c of cases){const artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===c.file?c.rewrite(a.content):a.content}));assert.notEqual(artifacts.find(a=>a.relative_path===c.file)!.content,p.artifacts.find(a=>a.relative_path===c.file)!.content);const root=path.join(f.temp,c.id);const n=native(root,artifacts);assert.equal(n.observe().result,'pass','bounded structural observation is not a behavior oracle');c.check(root);}
});

test('PCR-06 scalar protocols reject Bool identity and preserve tuple boundaries and exact Strings',t=>{
  const f=fixture(t),entityPath='specs/commerce/nodes/customer.json',rulePath='specs/commerce/nodes/valid-id.json';
  const node=JSON.parse(fs.readFileSync(path.join(f.source,entityPath),'utf8'));
  node.body.typed_contract.properties.find((p:any)=>p.name==='id').type.name='Bool';f.write(entityPath,node);
  const rule=JSON.parse(fs.readFileSync(path.join(f.source,rulePath),'utf8'));
  rule.body.typed_contract.parameters[0].type.name='Bool';rule.body.typed_contract.expression={op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}};f.write(rulePath,rule);
  assert.throws(()=>f.recompile(),/FIELD_IDENTITY_TYPE/,'the checked field contract forbids Bool identity');
  const p=planConfiguredFactories(f.graph,f.fields,f.selection,sources),root=path.join(f.temp,'typed-components');native(root,p.artifacts);
  const ef=loadJs(root,paths.customer).createCustomerFactory(),vf=loadJs(root,paths.contact).createContactFactory();
  const a=ef.create(customer()),b=ef.create(customer({enabled:false}));assert.equal(a.ok,true);assert.equal(b.ok,true);
  assert.equal(a.value.identity.component.tag,'String');assert.equal(b.value.components.find((c:any)=>c.tag==='Bool').value,false);assert.equal(a.value.sameIdentity(b.value),true);assert.equal(a.value.hash(),b.value.hash());
  assert.equal(ef.create(customer({id:true})).ok,false);
  for(const [left,right] of [[contact({label:'a',locale:'bc'}),contact({label:'ab',locale:'c'})],[contact({label:'é'}),contact({label:'e\u0301'})],[contact({label:'a:1\u0000b'}),contact({label:'a',locale:':1\u0000b'})]]) {
    const x=vf.create(left).value,y=vf.create(right).value;assert.equal(x.equals(y),false);assert.notEqual(x.hash(),y.hash());
  }
});

const composedRuleSources={configuration:sources.configuration,base:sources.base,typescript:sources.typescript,
  rule_contract:read(packagePath+'/string-order-rule-contract.json'),collection_contract:read(packagePath+'/rule-collection-value-contract.json'),
  predicate_contract:read(packagePath+'/rule-collection-predicate-contract.json'),numeric_contract:read(packagePath+'/rule-numeric-contract.json')};
const factoryRuleSources={...entityRuleSources,...composedRuleSources,factory_contract:read(packagePath+'/factory-rule-composition-contract.json')};
const composedRuleSelection={schema_version:NUMERIC_RULE_VERSION,value_profile:NUMERIC_RULE_VALUE_PROFILE} as const;
const budgetArguments=['allowed','amount','amounts','cap'];

const exactFieldDescriptor=read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json');
const exactFactorySources={...factoryRuleSources,field_contract:exactFieldDescriptor,factory_contract:read(packagePath+'/exact-factory-contract.json'),
  exact_contract:read(packagePath+'/rule-exact-contract.json'),literal_contract:read(packagePath+'/rule-exact-literal-contract.json')};
const exactFactorySupportHash='1b207847013953e8863b829e3db0d8a721a8b617ca449f23dd51c9ad1a6ea5bc';
const fullMaximum=18446744073709551615n;
function exactFactoryFixture(f:any,version:typeof EXACT_RULE_VERSION|typeof EXACT_LITERAL_RULE_VERSION=EXACT_LITERAL_RULE_VERSION){
  const graph=loadCompiledProjectGraph(f.source),fields=compileSelectedProjectFields(graph,{...f.fields.selection,
    schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,
    graph_sha256:createCompiledProjectCertificate(graph).graph_sha256},exactFieldDescriptor);
  const selection:ConfiguredFactorySelection={...f.selection,schema_version:EXACT_FACTORY_VERSION,field_compilation_sha256:fields.compilation_sha256,
    rule_selection:{schema_version:version,value_profile:EXACT_UINT64_PROFILE}};
  const {literal_contract,...v6Sources}=exactFactorySources;
  return {...f,graph,fields,selection,sources:version===EXACT_RULE_VERSION?v6Sources:exactFactorySources};
}
function exactFactoryExpected(e:any){
  for(const m of e.modules){
    m.collection_support_sha256=exactFactorySupportHash;
    m.reference_bindings??=[];
    if(m.name==='Customer'||m.name==='Account'){m.provider=m.name==='Account'?'audit:account':'commerce:customer';m.entity_provider=true;}
  }
  for(const m of e.enum_components??[])m.contract_sha256=EXACT_FACTORY_CONTRACT_SHA256;
  for(const m of e.sum_modules??[]){m.contract_sha256=EXACT_FACTORY_CONTRACT_SHA256;m.support_sha256=exactFactorySupportHash;}
  return e;
}
const exactPlan=(f:ReturnType<typeof exactFactoryFixture>)=>planConfiguredFactories(f.graph,f.fields,f.selection,f.sources);

function structuredFactoryFixture(t:any){
  const raw=factoryRuleFixture(t),json=(p:string)=>JSON.parse(fs.readFileSync(path.join(raw.source,p),'utf8'));
  const ownerType={kind:'named',selector:'commerce:customer'};
  const p=(root:string,...properties:string[])=>({op:'path',root,properties});
  const equal=(left:any,right:any)=>({op:'eq',left,right});
  const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FACTORY-CHOICE#None',payload:null},{name:'Owner',ontology_variant:'FACTORY-CHOICE#Owner',payload:ownerType}]};
  const types:Record<string,any>={delegate:{kind:'optional',element:ownerType},teams:{kind:'list',element:{kind:'set',element:ownerType}},choice,status:{kind:'named',selector:'commerce:status'}};
  const contactFile='specs/commerce/nodes/contact.json',contact=json(contactFile);
  for(const [name,type] of Object.entries(types)){
    contact.body.fields.push(name);contact.body.typed_contract.properties.push({name,type,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':'one',meaning:name,ontology_property:'FACTORY-CONTACT#'+name});
  }
  raw.write(contactFile,contact);
  raw.write('specs/commerce/nodes/status.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:'status',kind:'Enum',body:{description:'Status',values:['Ready','Waiting'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FACTORY-STATUS',variants:[{name:'Ready',ontology_variant:'FACTORY-STATUS#Ready',payload:null},{name:'Waiting',ontology_variant:'FACTORY-STATUS#Waiting',payload:null}]}}});
  const rule=(id:string,parameters:any[],expression:any)=>raw.write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind:'Rule',body:{description:id,predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FACTORY-'+id.toUpperCase(),parameters,expression}}});
  rule('owner-budget',[{name:'owner',type:ownerType}],{op:'lt',left:p('owner','FIXTURE-CUSTOMER#amount'),right:{op:'literal',type:'UInt64',value:3}});
  rule('structured',[...Object.entries(types).map(([name,type])=>({name,type}))],{op:'all',terms:[
    ...['delegate','teams','choice'].map(name=>equal(p(name),p(name))),
    equal(p('status'),{op:'variant',selector:'FACTORY-STATUS#Ready'})]});
  const feature=json('specs/commerce/feature.json');feature.nodes.push('status','structured');raw.write('specs/commerce/feature.json',feature);
  const f=exactFactoryFixture(raw),selection=structuredClone(f.selection);
  selection.schema_version=STRUCTURED_FACTORY_VERSION;selection.rule_selection={schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE};
  const target=selection.factories.find((f:FactoryBinding)=>f.selector==='commerce:contact')!;
  (target.extensions.find((e:FactoryBinding['extensions'][number])=>e.id==='owner-budget')!.validators as any[])[0]={rule:'commerce:owner-budget',arguments:[{parameter:'owner',field:'owner'}]};
  (target.extensions as any[]).push({id:'structured',validators:[{rule:'commerce:structured',arguments:Object.keys(types).map(parameter=>({parameter,field:parameter}))}]});
  return {...f,selection,sources:{...f.sources,factory_contract:read(packagePath+'/factory-structured-rule-contract.json'),structured_contract:read(packagePath+'/rule-structured-value-contract.json')}};
}
function structuredFactoryRuntime(root:string){
  const cf=loadJs(root,paths.customer).createCustomerFactory(),vf=loadJs(root,paths.contact).createContactFactory();
  const status=loadJs(root,'application/features/commerce/src/domain/enums/status.component.ts').StatusValueComponent;
  const owner=(patch:object={})=>{const r=cf.create(customer({...budgetInput(),...patch}));assert.equal(r.ok,true);return r.value;};
  const fields=(patch:object={})=>contact({...budgetInput(),owner:owner(),delegate:null,teams:[],choice:{variant:'None'},status:status.values.Ready,...patch});
  return {cf,vf,status,owner,fields};
}

test('PCR-06 structured factories explicitly bind Rule v8 and preserve the preceding selection',t=>{
  const f=structuredFactoryFixture(t),p=exactPlan(f);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v12-candidate');
  assert.equal(p.factory_contract_sha256,STRUCTURED_FACTORY_CONTRACT_SHA256);
  assert.deepEqual(exactPlan(f),p);assert.ok(p.modules.every(m=>m.base_validators.every(v=>v.fact_views)));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,rule_selection:{schema_version:EXACT_LITERAL_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE}},f.sources),/unsupported Rule/);
  for(const key of ['factory_contract','structured_contract','field_contract'])assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...f.sources,[key]:(f.sources as any)[key]+' '}),/drift/);
  const bad=structuredClone(f.selection),target=bad.factories.find((f:FactoryBinding)=>f.selector==='commerce:contact')!;
  (target.extensions.find((e:FactoryBinding['extensions'][number])=>e.id==='owner-budget')!.validators as any[])[0].arguments=[{parameter:'owner',path:['delegate','id']}];
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,bad,f.sources),/required owned/);
  const inject=structuredClone(f.selection);
  (inject.factories[0]!.base_validators[0] as any).fact_views={value:'true'};
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,inject,f.sources),/unknown or missing/);
  const prior=exactFactoryFixture(factoryRuleFixture(t)),old=exactPlan(prior);
  assert.equal(old.schema_version,'domainspec.configured-factories-plan/v11-candidate');
  assert.ok(old.modules.every(m=>m.base_validators.every(v=>!Object.hasOwn(v,'fact_views'))));
});

test('PCR-06 native factory views strip owned wrappers after validation for nested Rule values',t=>{
  const f=structuredFactoryFixture(t),p=exactPlan(f),root=path.join(f.temp,'structured-factories');
  native(root,p.artifacts);const r=structuredFactoryRuntime(root),a=r.owner(),b=r.owner({id:'customer-b'});
  const input=r.fields({delegate:a,teams:[[a,b]],choice:{variant:'Owner',payload:a}});
  const factory=r.vf.extend('owner-budget').extend('structured');
  for(const route of ['create','reconstruct']){
    const result=(factory as any)[route](input);assert.equal(result.ok,true);
    assert.equal(result.trace.validators.at(-1).rule,'commerce:structured');assert.ok(result.trace.validators.every((v:any)=>v.outcome==='pass'));
    assert.equal(result.value.fields.delegate,a);assert.equal(result.value.fields.choice.payload,a);
    assert.equal((factory as any)[route](r.fields({status:r.status.values.Waiting})).ok,false);
  }
  assert.equal(factory.create(r.fields()).ok,true,'absent optional fact is preserved');
  assert.equal(r.vf.create(r.fields({status:r.status.values.Waiting})).ok,true,'extension remains local');
  assert.equal(factory.create(r.fields({owner:r.owner({amount:4,allowed:[0,4,10],amounts:[4,10]})})).ok,false,'named Rule reads actual fields');
  const previous=r.cf.create(customer({...budgetInput()}));assert.equal(previous.ok,true);
  assert.equal(r.cf.transition(previous.value,customer({...budgetInput(),label:'Changed'})).ok,true);
  const fake={fields:a.fields};const bad=factory.create(r.fields({delegate:fake}));
  assert.equal(bad.ok,false);assert.deepEqual(bad.trace.validators,[],'ownership rejection precedes Rule evaluation');
  const duplicate=factory.create(r.fields({teams:[[a,a]]}));assert.equal(duplicate.ok,false);assert.deepEqual(duplicate.trace.validators,[]);
  const rule=loadJs(root,'application/features/commerce/src/domain/rules/owner-budget.ts').ruleOwnerBudget;
  assert.equal(rule({owner:a.fields}),true);assert.throws(()=>rule({owner:a}),/RULE_INPUT/,'owned snapshots are not raw Rule facts');
});

test('PCR-06 a compiling factory fact-view mutation is caught by route behavior',t=>{
  const f=structuredFactoryFixture(t),p=exactPlan(f),m=p.modules.find(m=>m.selector==='commerce:contact')!;
  const v=m.extensions.find(e=>e.id==='owner-budget')!.validators[0]!,view=v.fact_views!.owner!;
  assert.ok(view.includes('.fields["amount"]'));
  const bad={...m,extensions:m.extensions.map(e=>e.id==='owner-budget'?{...e,validators:[{...v,fact_views:{owner:view.replace('.fields["amount"]','.fields["cap"]')}}]}:e)};
  const root=path.join(f.temp,'mutated-facts');native(root,p.artifacts.map(a=>a.relative_path===m.relative_path?{...a,content:renderConfiguredFactory(bad)}:a));
  const r=structuredFactoryRuntime(root);
  for(const route of ['create','reconstruct'])assert.equal((r.vf.extend('owner-budget') as any)[route](r.fields()).ok,false);
});

test('PCR-06 optional collection Rule endpoints enforce every Entity construction route',t=>{
  const raw=factoryRuleFixture(t),type={kind:'optional',element:{kind:'list',element:{kind:'scalar',name:'UInt64'}}};
  addReferenceFields(raw,'commerce:customer',{hint:type,expected_hint:type});
  const featurePath='specs/commerce/feature.json',feature=JSON.parse(fs.readFileSync(path.join(raw.source,featurePath),'utf8'));
  feature.nodes.push('hint-matches');raw.write(featurePath,feature);
  raw.write('specs/commerce/nodes/hint-matches.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:'hint-matches',kind:'Rule',body:{description:'Hint matches',predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FACTORY-HINT-MATCHES',parameters:[{name:'hint',type},{name:'expected_hint',type}],expression:{op:'eq',left:{op:'path',root:'hint',properties:[]},right:{op:'path',root:'expected_hint',properties:[]}}}}});
  const f=exactFactoryFixture(raw),selection=structuredClone(f.selection);
  selection.schema_version=STRUCTURED_FACTORY_VERSION;selection.rule_selection={schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE};
  (selection.factories.find((f:FactoryBinding)=>f.selector==='commerce:customer')!.extensions as any[]).push({id:'hint-matches',validators:[{rule:'commerce:hint-matches',arguments:[{parameter:'hint',field:'hint'},{parameter:'expected_hint',field:'expected_hint'}]}]});
  const sources={...f.sources,factory_contract:read(packagePath+'/factory-structured-rule-contract.json'),structured_contract:read(packagePath+'/rule-structured-value-contract.json')};
  const plan=planConfiguredFactories(f.graph,f.fields,selection,sources),root=path.join(f.temp,'optional-routes');native(root,plan.artifacts);
  const base=loadJs(root,paths.customer).createCustomerFactory(),factory=base.extend('hint-matches');
  const input=(patch:object={})=>customer({...budgetInput(),...patch});
  const previous=factory.create(input());assert.equal(previous.ok,true);
  for(const route of ['create','reconstruct','transition']){
    const run=(value:any)=>route==='transition'?factory.transition(previous.value,value):factory[route](value);
    assert.equal(run(input()).ok,true);assert.equal(run(input({hint:null,expected_hint:null})).ok,true);
    assert.equal(run(input({hint:['18446744073709551615'],expected_hint:[18446744073709551615n]})).ok,true);
    const failed=run(input({hint:[],expected_hint:null}));assert.equal(failed.ok,false);
    assert.equal(failed.trace.validators.at(-1).rule,'commerce:hint-matches');assert.equal(failed.trace.validators.at(-1).outcome,'fail');
  }
  assert.equal(base.create(input({hint:[],expected_hint:null})).ok,true);
});

test('PCR-06 owned Value Objects and named sum payloads compose into structural Rule facts',t=>{
  const raw=uintFixture(t),type={kind:'named',selector:'commerce:authorization'};
  const featurePath='specs/commerce/feature.json',feature=JSON.parse(fs.readFileSync(path.join(raw.source,featurePath),'utf8'));
  feature.nodes.push('authorization-matches');raw.write(featurePath,feature);
  raw.write('specs/commerce/nodes/authorization-matches.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:'authorization-matches',kind:'Rule',body:{description:'Matching authorization',predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FACTORY-AUTHORIZATION-MATCHES',parameters:[{name:'left',type},{name:'right',type}],expression:{op:'eq',left:{op:'path',root:'left',properties:[]},right:{op:'path',root:'right',properties:[]}}}}});
  const f=exactFactoryFixture(raw),selection=structuredClone(f.selection);
  selection.schema_version=STRUCTURED_FACTORY_VERSION;selection.rule_selection={schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE};
  (selection.factories.find((f:FactoryBinding)=>f.selector==='commerce:customer')!.extensions as any[]).push({id:'authorization-matches',validators:[{rule:'commerce:authorization-matches',arguments:[{parameter:'left',field:'z_result'},{parameter:'right',path:['contact','z_named']}]}]});
  const sources={...f.sources,factory_contract:read(packagePath+'/factory-structured-rule-contract.json'),structured_contract:read(packagePath+'/rule-structured-value-contract.json')};
  const p=planConfiguredFactories(f.graph,f.fields,selection,sources),root=path.join(f.temp,'named-sum-facts');native(root,p.artifacts);
  const r=uintRuntime(root),factory=loadJs(root,paths.customer).createCustomerFactory().extend('authorization-matches');
  const cases=[{variant:'Cancelled'},{variant:'Text',payload:'18446744073709551615'},{variant:'Maybe',payload:null},
    {variant:'Nested',payload:{variant:'Text',payload:18446744073709551615n}},
    {variant:'Details',payload:r.tf.create({key:'tenant-a'}).value},
    {variant:'Delegated',payload:r.answer.create({variant:'Receipt',payload:'receipt'})},
    {variant:'States',payload:[r.status.values.Draft,r.status.values.Submitted]}];
  for(const value of cases){
    const left=r.sum.create(value),right=r.sum.create(value),contact=r.vf.create(r.base({z_named:right}));assert.equal(contact.ok,true);
    const input=r.input({z_result:left,contact:contact.value}),created=factory.create(input);assert.equal(created.ok,true,value.variant);
    assert.equal(factory.reconstruct(input).ok,true);assert.equal(factory.transition(created.value,input).ok,true);
  }
  const changed=r.vf.create(r.base({z_named:r.sum.create({variant:'Text',payload:1})}));assert.equal(changed.ok,true);
  assert.equal(factory.create(r.input({z_result:r.sum.create({variant:'Text',payload:2}),contact:changed.value})).ok,false);
});

test('PCR-06 exact factories bind explicit field Rule and Enum selections without widening old lanes',t=>{
  const prior=uintFixture(t),legacy=planConfiguredFactories(prior.graph,prior.fields,prior.selection,uintSources),f=exactFactoryFixture(prior),p=exactPlan(f);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v11-candidate');assert.equal(p.factory_contract_sha256,EXACT_FACTORY_CONTRACT_SHA256);
  assert.equal(p.collection_support!.sha256,exactFactorySupportHash);assert.ok(p.modules.every(m=>m.exact_uint64));assert.ok(p.sum_modules!.every(m=>m.exact_uint64));
  assert.deepEqual(planConfiguredFactories(prior.graph,prior.fields,prior.selection,uintSources),legacy);
  const v6=exactFactoryFixture(prior,EXACT_RULE_VERSION),p6=exactPlan(v6);assert.deepEqual(p.artifacts,p6.artifacts);assert.notEqual(p.plan_sha256,p6.plan_sha256);
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));assert.ok(Object.isFrozen(p.modules[0]!.fields));assert.equal(Object.isFrozen(f.selection),false);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},f.sources),p);
  const relocated=path.join(f.temp,'relocated');fs.cpSync(f.source,relocated,{recursive:true});
  const moved=exactFactoryFixture({...prior,source:relocated});assert.deepEqual(exactPlan(moved),p);
  fs.renameSync(f.source,path.join(f.temp,'not-source'));assert.deepEqual(exactPlan(f),p);
  for(const component of p.component_bindings!)assert.equal(component.artifact_sha256,p.artifacts.find(a=>a.relative_path===component.relative_path)!.sha256);
  const enumFields=compileSelectedProjectFields(f.graph,{...f.fields.selection,roots:['commerce:status'],bindings:[]},exactFieldDescriptor);
  const oldEnumFields=compileSelectedProjectFields(f.graph,{...enumFields.selection,schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256},descriptor);
  const enumInputs={configuration:sources.configuration,base:sources.base,typescript:sources.typescript,provider:enumSources.enum_provider};
  const enumSelection={schema_version:EXACT_CONFIGURED_ENUM_VERSION,language:'typescript' as const,module_root:'application',field_compilation_sha256:enumFields.compilation_sha256} satisfies ConfiguredEnumSelection;
  const exactEnum=planConfiguredEnums(enumFields,enumSelection,enumInputs),oldEnum=planConfiguredEnums(oldEnumFields,{...enumSelection,schema_version:CONFIGURED_ENUM_VERSION,field_compilation_sha256:oldEnumFields.compilation_sha256},enumInputs);
  assert.equal(exactEnum.schema_version,'domainspec.configured-enums-plan/v2-candidate');assert.equal(exactEnum.model_sha256,enumFields.model.model_sha256);
  assert.deepEqual(exactEnum.artifacts,oldEnum.artifacts);assert.notEqual(exactEnum.plan_sha256,oldEnum.plan_sha256);
  assert.equal(p.enum_plan_sha256,exactEnum.plan_sha256);assert.equal(p.enum_field_compilation_sha256,enumFields.compilation_sha256);
  assert.throws(()=>planConfiguredEnums(oldEnumFields,enumSelection,enumInputs),/requires exact checked fields/);
  assert.throws(()=>planConfiguredEnums(enumFields,{...enumSelection,schema_version:CONFIGURED_ENUM_VERSION},enumInputs),/explicit exact Enum/);
  assert.throws(()=>planConfiguredEnums(f.fields,{...enumSelection,field_compilation_sha256:f.fields.compilation_sha256},enumInputs),/unsupported declaration kind|payload-bearing/);
});

test('PCR-06 exact factories reject mixed profiles stale sources malformed choices and unsupported Rule endpoints',t=>{
  const prior=factoryRuleFixture(t),f=exactFactoryFixture(prior);
  assert.throws(()=>planConfiguredFactories(f.graph,prior.fields,f.selection,f.sources),/requires exact checked fields/);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,prior.selection,factoryRuleSources),/explicit exact factory/);
  for(const key of ['factory_contract','field_contract','exact_contract','literal_contract','numeric_contract'] as const)
    assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...f.sources,[key]:f.sources[key]+' '}),/drift/);
  for(const rule_selection of [{schema_version:NUMERIC_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE},{schema_version:EXACT_RULE_VERSION,value_profile:NUMERIC_RULE_VALUE_PROFILE},{schema_version:'future',value_profile:EXACT_UINT64_PROFILE}])
    assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,rule_selection} as any,f.sources),/unsupported Rule selection/);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,field_compilation_sha256:'0'.repeat(64)},f.sources),/stale/);
  assert.throws(()=>planConfiguredFactories(f.graph,structuredClone(f.fields),f.selection,f.sources),/PROJECT_FIELD_UNCHECKED/);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'../escape'},f.sources),/unsafe/);
  let reads=0;const bad=Object.defineProperty({...f.selection},'rule_selection',{get(){reads++;return f.selection.rule_selection;}});
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,bad,f.sources),/non-data/);assert.equal(reads,0);
  for(const endpoint of [{kind:'optional',element:ruleScalar('UInt64')},{kind:'list',element:ruleCollection('list','UInt64')}]){
    const raw=factoryRuleFixture(t),file='specs/commerce/nodes/customer.json',node=JSON.parse(fs.readFileSync(path.join(raw.source,file),'utf8'));
    const field=node.body.typed_contract.properties.find((p:any)=>p.name==='amount');field.type=endpoint;field.cardinality=endpoint.kind==='optional'?'optional':'many';raw.write(file,node);
    const changed=exactFactoryFixture(raw);assert.throws(()=>exactPlan(changed),/validator endpoint|field\/type mismatch/);
  }
});

test('PCR-06 exact factories native nested values and sums preserve full-width equality and composite identity',t=>{
  const f=exactFactoryFixture(uintFixture(t)),p=exactPlan(f),e=exactFactoryExpected(uintExpected()),root=path.join(f.temp,'exact-nested');
  e.modules.find((m:any)=>m.name==='Contact').field_types={zz_count:'bigint',zz_list:'ReadonlyArray<bigint>',zz_matrix:'ReadonlyArray<ReadonlyArray<bigint>>',zz_maybe:'(bigint)|null',zz_set:'ReadonlyArray<bigint>'};
  const n=native(root,p.artifacts,e);assert.deepEqual(n.observe().errors,[]);const r=uintRuntime(root);
  const patches=[{}, {zz_count:0n},{zz_count:'0'},{zz_count:fullMaximum},{zz_count:fullMaximum.toString()},{zz_count:fullMaximum-1n},
    {zz_maybe:null},{zz_maybe:0n},{zz_maybe:fullMaximum},{zz_list:[fullMaximum,1]},{zz_list:[1,fullMaximum]},{zz_list:[1n,'1']},
    {zz_set:[fullMaximum,1n]},{zz_set:['1',fullMaximum.toString()]},{zz_matrix:[[1],[fullMaximum]]},{zz_matrix:[[fullMaximum],[1]]},
    {z_named:r.sum.create({variant:'Text',payload:fullMaximum})},{z_named:r.sum.create({variant:'Text',payload:fullMaximum.toString()})},
    {z_named:r.sum.create({variant:'Text',payload:fullMaximum-1n})},{z_named:r.sum.create({variant:'OtherText',payload:fullMaximum.toString()})},
    {z_named:r.sum.create({variant:'Maybe',payload:null})},{z_named:r.sum.create({variant:'Maybe',payload:'0'})},
    {z_named:r.sum.create({variant:'Nested',payload:{variant:'Text',payload:fullMaximum}})}];
  const rows=patches.map(patch=>{const input=r.base(patch),out=r.vf.create(input);assert.equal(out.ok,true);return {value:out.value,key:compiledFieldValueKey(f.fields,'commerce:contact',embeddedWire(input))};});
  for(const a of rows)for(const b of rows){assert.equal(a.value.equals(b.value),a.key===b.key);assert.equal(a.value.hash()===b.value.hash(),a.key===b.key);}
  const values=[fullMaximum,'1'],made=r.vf.create(r.base({zz_list:values,zz_matrix:[values]}));assert.ok(made.ok);values.reverse();
  assert.deepEqual(made.value.fields.zz_list,[fullMaximum,1n]);assert.deepEqual(made.value.fields.zz_matrix,[[fullMaximum,1n]]);assert.ok(Object.isFrozen(made.value.fields.zz_matrix[0]));assert.equal(Object.isFrozen(values),false);
  assert.equal(r.vf.create(r.base({zz_set:[1n,'1']})).ok,false);
  const id=r.makeId(fullMaximum as any),same=r.makeId(fullMaximum.toString() as any),other=r.makeId((fullMaximum-1n) as any);
  assert.ok(id.equals(same));assert.equal(id.equals(other),false);const prior=r.ef.create(r.input({id}));assert.ok(prior.ok);
  assert.ok(r.ef.transition(prior.value,r.input({id:same,label:'Changed'})).ok);assert.deepEqual(r.ef.transition(prior.value,r.input({id:other})).failure_codes,['IDENTITY_CHANGED']);
  for(const bad of [fullMaximum+1n,'18446744073709551616',9007199254740992,-1n,'01','1\n','1\u2028',1.5,true,new Number(1)]){
    for(const patch of [{zz_count:bad},{zz_maybe:bad},{zz_list:[bad]},{zz_matrix:[[bad]]},{zz_set:[bad]}]){
      const out=r.vf.create(r.base(patch));assert.deepEqual(out.failure_codes,['INVALID_FIELDS']);assert.deepEqual(out.trace.validators,[]);
    }
    assert.throws(()=>r.sum.create({variant:'Nested',payload:{variant:'Text',payload:bad}}));
  }
});

test('PCR-06 exact factories native types expose bigint snapshots and accept exact sum input forms',t=>{
  const f=exactFactoryFixture(uintFixture(t)),p=exactPlan(f),root=path.join(f.temp,'exact-types'),e=exactFactoryExpected(uintExpected());
  const answer=e.sum_modules.find((m:any)=>m.name==='Answer');
  answer.input_type='(Readonly<{variant:"Empty"}>|Readonly<{variant:"Receipt";payload:string}>)';
  answer.case_type=answer.input_type+'&Readonly<{[brand]:true}>';
  const n=native(root,p.artifacts,e);assert.deepEqual(n.observe().errors,[]);
  const file=path.join(root,'consumer.ts'),imports='import type {ContactFields} from "./'+paths.contact.replace('.ts','.js')+'";\nimport {AuthorizationValueComponent as choice} from "./'+sumPath().replace('.ts','.js')+'";\n';
  fs.writeFileSync(file,imports+'const number:ContactFields["zz_count"]=18446744073709551615n;\nfor(const payload of [1,1n,"18446744073709551615"]){const value=choice.create({variant:"Text",payload});if(value.variant==="Text"){const exact:bigint=value.payload;}}\n');n.compile([file]);
  for(const body of ['const wrong:ContactFields["zz_count"]=1;','const wrong:ContactFields["zz_count"]="1";','declare const fields:ContactFields;fields.zz_count=2n;','declare const fields:ContactFields;fields.zz_list.push(1n);','choice.create({variant:"Text",payload:true});']){
    fs.writeFileSync(file,imports+body);assert.throws(()=>n.compile([file]),(error:any)=>{assert.match(String(error.stdout),/consumer\.ts.*TS/);return true;});
  }
});

test('PCR-06 exact factories reject hostile numeric inputs before validators without reading coercion hooks',t=>{
  const f=exactFactoryFixture(uintIdentityFixture(t)),p=exactPlan(f),root=path.join(f.temp,'exact-hostile');native(root,p.artifacts,exactFactoryExpected(f.expectation));
  const cf=loadJs(root,paths.customer).createCustomerFactory(),prior=cf.create(customer({id:0n}));assert.ok(prior.ok);
  for(const id of [0,-0,0n,'0',1,1n,'1',9007199254740991,9007199254740992n,fullMaximum,fullMaximum.toString()]){
    const value=cf.create(customer({id}));assert.ok(value.ok);assert.equal(value.value.fields.id,BigInt(id));
  }
  let reads=0;const custom={valueOf(){reads++;return 1;},toString(){reads++;return '1';}};
  const rejected=[9007199254740992,2**64,NaN,Infinity,-Infinity,-1,-1n,0.25,fullMaximum+1n,'18446744073709551616',
    '01','+1','-0','1e0','0x1',' 1','1 ','1\n','1\r\n','1\u2028','1\u2029','',true,null,undefined,new Number(1),new String('1'),custom,[],Symbol('one')];
  for(const id of rejected)for(const method of ['create','reconstruct','transition']){
    const value=customer({id}),out=method==='transition'?cf.transition(prior.value,value):cf[method](value);
    assert.deepEqual(out.failure_codes,['INVALID_FIELDS']);assert.deepEqual(out.trace.validators,[]);
  }
  const getter=Object.defineProperty(customer(),'id',{enumerable:true,get(){reads++;return 1n;}});
  assert.deepEqual(cf.create(getter).failure_codes,['INVALID_FIELDS']);assert.equal(reads,0);
  const hidden=customer({id:1n});Object.defineProperty(hidden,'id',{enumerable:false});assert.equal(cf.create(hidden).ok,false);
  assert.equal(cf.create({...customer({id:1n}),[Symbol('extra')]:1n}).ok,false);
  assert.equal(cf.create(Object.assign(Object.create(null),customer({id:fullMaximum}))).ok,true);
  const original=customer({id:fullMaximum.toString()});assert.ok(cf.create(original).ok);assert.equal(original.id,fullMaximum.toString());assert.equal(Object.isFrozen(original),false);
});

test('PCR-06 exact factories native references and embedded Entities keep identity ownership and no lookup',t=>{
  const f=exactFactoryFixture(embeddedFixture(t)),p=exactPlan(f),root=path.join(f.temp,'exact-entities'),n=native(root,p.artifacts,exactFactoryExpected(embeddedExpected()));
  assert.deepEqual(n.observe().errors,[]);const r=embeddedRuntime(root),a=r.child({id:fullMaximum}),same=r.child({id:fullMaximum.toString(),label:'Other'}),other=r.child({id:fullMaximum-1n});
  assert.ok(a.sameIdentity(same));assert.equal(a.sameIdentity(other),false);
  const rows=[a,same,other].map(child=>{const input=r.input({a_customer:fullMaximum,b_account:fullMaximum-1n,c_same:fullMaximum,d_list:[fullMaximum],e_set:[fullMaximum,1],f_optional:fullMaximum,
    z_entity:child,z_list:[child],z_matrix:[[child]],z_named:r.d.create({variant:'Customer',payload:child}),z_set:[child],z_sum:{variant:'Reference',payload:fullMaximum}});const out=r.vf.create(input);assert.ok(out.ok);return {value:out.value,key:compiledFieldValueKey(f.fields,'commerce:contact',embeddedWire(input))};});
  for(const a of rows)for(const b of rows)assert.equal(a.value.equals(b.value),a.key===b.key);
  assert.equal(r.vf.create(r.input({z_set:[a,same]})).ok,false);assert.equal(r.vf.create(r.input({z_entity:structuredClone(a.fields)})).ok,false);
  assert.equal(r.vf.create(r.input({a_customer:fullMaximum+1n})).ok,false);
  const before=r.cf.create(refCustomer({id:fullMaximum}));assert.ok(before.ok);
  for(const method of ['create','reconstruct','transition']){const input=refCustomer({id:fullMaximum.toString()});const out=method==='transition'?r.cf.transition(before.value,input):r.cf[method](input);assert.ok(out.ok);assert.equal(out.value.fields.id,fullMaximum);}
  const target=p.reference_bindings!.find((b:any)=>b.owner==='commerce:contact'&&b.field==='a_customer')!;assert.equal(target.target,'commerce:customer');assert.ok(target.target_artifact_sha256);
  assert.equal(r.vf.create(r.input({a_customer:fullMaximum})).ok,true,'no matching external Entity is required');
});

test('PCR-06 exact factories native Rules receive normalized full-width values on every construction route',t=>{
  const raw=factoryRuleFixture(t),file='specs/commerce/nodes/owner-budget.json',node=JSON.parse(fs.readFileSync(path.join(raw.source,file),'utf8'));
  node.body.predicate='structured:domainspec.typed-rule/v2';node.body.typed_contract.schema_version='domainspec.typed-rule/v2';
  node.body.typed_contract.expression.terms[1].right.value=fullMaximum.toString();raw.write(file,node);
  const f=exactFactoryFixture(raw),p=exactPlan(f),root=path.join(f.temp,'exact-rules'),e=exactFactoryExpected(factoryRuleExpected()),n=native(root,p.artifacts,e);
  assert.deepEqual(n.observe().errors,[]);assert.deepEqual(observeFactoryRules(root,EXACT_UINT64_PROFILE).errors,[]);
  const cf=loadJs(root,paths.customer).createCustomerFactory(),vf=loadJs(root,paths.contact).createContactFactory();
  const input=(patch:object={})=>customer({...budgetInput(),allowed:[fullMaximum-1n,'1'],amount:(fullMaximum-1n).toString(),amounts:[fullMaximum-1n,'1'],cap:fullMaximum,...patch});
  const prior=cf.create(input());assert.ok(prior.ok);assert.equal(prior.value.fields.amount,fullMaximum-1n);assert.deepEqual(prior.value.fields.amounts,[fullMaximum-1n,1n]);
  for(const method of ['create','reconstruct','transition']){
    const call=(value:object)=>method==='transition'?cf.transition(prior.value,value):cf[method](value);
    assert.ok(call(input()).ok);
    const bad=call(input({amount:fullMaximum}));assert.equal(bad.ok,false);assert.match(bad.failure_codes[0],/RULE_FAIL/);
    const overflow=call(input({cap:fullMaximum+1n}));assert.deepEqual(overflow.failure_codes,['INVALID_FIELDS']);assert.deepEqual(overflow.trace.validators,[]);
    assert.equal(call(input({allowed:[1,1n]})).ok,false);
  }
  const parent=contact({...budgetInput(),allowed:[fullMaximum-1n,1n],amount:fullMaximum-1n,amounts:[fullMaximum-1n,1n],cap:fullMaximum,owner:prior.value});
  assert.ok(vf.extend('owner-budget').create(parent).ok);assert.ok(vf.extend('flags').create(parent).ok);
  assert.equal(cf.extend('enabled').create(input({enabled:false})).ok,false);
  assert.equal(cf.create(input({enabled:false})).ok,true,'extension validation stays local');
  assert.equal(vf.create({...parent,owner:{...prior.value}}).ok,false,'foreign parent object does not carry provider ownership');
  const v6=exactFactoryFixture(raw,EXACT_RULE_VERSION);assert.throws(()=>exactPlan(v6),/v2 requires exact-literal/);
});

test('PCR-06 exact factories native compiling mutants expose precision range and equality-key collapse',t=>{
  const f=exactFactoryFixture(uintIdentityFixture(t)),p=exactPlan(f),e=exactFactoryExpected(f.expectation);
  e.modules.find((m:any)=>m.name==='Customer').field_types={id:'bigint'};
  for(const [id,before,after] of [
    ['precision','return value;','return BigInt(Number(value));'],
    ['range','value > 18446744073709551615n','value > 18446744073709551616n'],
    ['key',"part('UInt64') + part(String(value))","part('UInt64') + part(String(Number(value)))"]]){
    const target=p.artifacts.find(a=>a.relative_path===paths.customer)!;assert.ok(target.content.includes(before!));
    const artifacts=p.artifacts.map(a=>a===target?{...a,content:a.content.replace(before!,after!)}:a),root=path.join(f.temp,id!),n=native(root,artifacts,e);
    assert.equal(n.observe().result,'fail','unchanged independent support identity detects mutation');
    const cf=loadJs(root,paths.customer).createCustomerFactory();
    if(id==='range')assert.equal(cf.create(customer({id:fullMaximum+1n})).ok,true,'mutant accepts overflowing identity');
    else{const a=cf.create(customer({id:fullMaximum})).value,b=cf.create(customer({id:fullMaximum-1n})).value;assert.equal(a.sameIdentity(b),true,'mutant collapses distinct full-width identities');}
  }
});

const budgetBinding=(rule='commerce:budget',prefix:string[]=[])=>({rule,arguments:budgetArguments.map(parameter=>({parameter,path:[...prefix,parameter]}))});
const ruleScalar=(name:string)=>({kind:'scalar',name});
const ruleCollection=(kind:string,name:string)=>({kind,element:ruleScalar(name)});
function composedRuleDefinitions(){
  const value=(root:string)=>({op:'path',root,properties:[]}),literal=(type:string,value:unknown)=>({op:'literal',type,value});
  const eq=(left:unknown,right:unknown)=>({op:'eq',left,right});
  const quantify=(op:string,where:unknown)=>({op,collection:value('amounts'),binding:'item',where});
  const budgetParameters=budgetArguments.map(name=>({name,type:name==='allowed'?ruleCollection('set','UInt64'):name==='amounts'?ruleCollection('list','UInt64'):ruleScalar('UInt64')}));
  return {
    'below':{parameters:['left','right'].map(name=>({name,type:ruleScalar('UInt64')})),expression:{op:'lt',left:value('left'),right:value('right')}},
    'budget':{parameters:budgetParameters,expression:{op:'all',terms:[
      {op:'rule_ref',selector:'commerce:below',arguments:[{parameter:'left',value:value('amount')},{parameter:'right',value:value('cap')}]},
      {op:'contains',left:value('allowed'),right:value('amount')},
      quantify('exists',{op:'lt',left:value('item'),right:value('cap')}),
      quantify('exactly_one',eq(value('item'),value('amount'))),quantify('unique',eq(value('item'),value('item')))]}},
    'owner-budget':{parameters:budgetParameters,expression:{op:'all',terms:[{op:'rule_ref',selector:'commerce:budget',arguments:budgetArguments.map(parameter=>({parameter,value:value(parameter)}))},{op:'lt',left:value('amount'),right:literal('UInt64',3)}]}},
    'ordered':{parameters:['left','right'].map(name=>({name,type:ruleScalar('String')})),expression:{op:'lt',left:value('left'),right:value('right')}},
    'flags':{parameters:[{name:'checks',type:ruleCollection('list','Bool')},{name:'flags',type:ruleCollection('set','Bool')},{name:'items',type:ruleCollection('list','String')},{name:'needle',type:ruleScalar('String')},{name:'tags',type:ruleCollection('set','String')}],expression:{op:'all',terms:[
      {op:'contains',left:value('flags'),right:literal('Bool',true)},
      {op:'exactly_one',collection:value('checks'),binding:'check',where:eq(value('check'),literal('Bool',true))},
      {op:'set_equal',left:{op:'to_set',value:value('items')},right:value('tags')},
      {op:'contains',left:value('items'),right:value('needle')}]}}
  };
}
function factoryRuleFixture(t:any){
  const f=fixture(t),definitions=composedRuleDefinitions(),json=(p:string)=>JSON.parse(fs.readFileSync(path.join(f.source,p),'utf8'));
  const feature=json('specs/commerce/feature.json');feature.nodes.push(...Object.keys(definitions));f.write('specs/commerce/feature.json',feature);
  for(const [node_id,typed] of Object.entries(definitions))f.write(`specs/commerce/nodes/${node_id}.json`,{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id,kind:'Rule',body:{description:node_id,predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FIXTURE-'+node_id.toUpperCase(),...typed}}});
  for(const id of ['customer','contact']){
    const p=`specs/commerce/nodes/${id}.json`,node=json(p);
    const added:any[]=[['allowed',ruleCollection('set','UInt64')],['amount',ruleScalar('UInt64')],['amounts',ruleCollection('list','UInt64')],['cap',ruleScalar('UInt64')],['checks',ruleCollection('list','Bool')],['flags',ruleCollection('set','Bool')],['labels',ruleCollection('list','String')],['tags',ruleCollection('set','String')]];
    if(id==='contact'){added.push(['owner',{kind:'named',selector:'commerce:customer'}]);node.body.invariant_refs.push('commerce:budget');}
    for(const [name,type] of added){node.body.fields.push(name);node.body.typed_contract.properties.push({name,type,identity:false,cardinality:type.kind==='set'?'many-unique':type.kind==='list'?'many':'one',meaning:name,ontology_property:'FIXTURE-'+id.toUpperCase()+'#'+name});}
    f.write(p,node);
  }
  const current=f.recompile(),selection=structuredClone(current.selection) as Omit<ConfiguredFactorySelection,'schema_version'|'factories'>&{
    schema_version:ConfiguredFactorySelection['schema_version'];
    factories:Array<Omit<FactoryBinding,'base_validators'>&{base_validators:FactoryValidatorBinding[]}>;
  };
  selection.schema_version=RULE_COMPOSITION_FACTORY_VERSION;(selection as any).rule_selection=composedRuleSelection;
  selection.factories=selection.factories.map(factory=>{
    const row=structuredClone(factory);row.base_validators.push(budgetBinding());
    (row.extensions as any[]).push({id:'ordered',validators:[{rule:'commerce:ordered',arguments:[{parameter:'left',field:'label'},{parameter:'right',field:row.selector==='commerce:customer'?'id':'locale'}]}]},
      {id:'flags',validators:[{rule:'commerce:flags',arguments:[{parameter:'checks',field:'checks'},{parameter:'flags',field:'flags'},{parameter:'items',field:'labels'},{parameter:'needle',field:'label'},{parameter:'tags',field:'tags'}]}]});
    if(row.selector==='commerce:contact')(row.extensions as any[]).push({id:'owner-budget',validators:[budgetBinding('commerce:owner-budget',['owner'])]});
    return row;
  });
  return {...f,...current,selection};
}
// Exact expectations are authored independently, not copied from the generated plan.
function factoryRuleExpected(){
  const e:any=expected();e.files.push(...['below','budget','flags','ordered','owner-budget'].map(id=>`application/features/commerce/src/domain/rules/${id}.ts`));
  const budgetCall=(rule:string,local:string,prefix='')=>({rule,call:`${local}({["allowed"]:fields${prefix}["allowed"],["amount"]:fields${prefix}["amount"],["amounts"]:fields${prefix}["amounts"],["cap"]:fields${prefix}["cap"]})`});
  for(const m of e.modules){
    const isEntity=m.name==='Customer';m.composed=true;m.provider='commerce:'+(isEntity?'customer':'contact');m.entity_provider=isEntity;m.reference_bindings=[];
    m.collection_support_sha256=entitySupportHash;
    m.collection_protocols=['setValue(uint64Value)','uint64Value','listValue(uint64Value)','uint64Value','listValue(boolValue)','boolValue','setValue(boolValue)',...(isEntity?['stringValue','stringValue','listValue(stringValue)']:['stringValue','listValue(stringValue)','stringValue','ownedEntityValue(component10)']),'setValue(stringValue)'];
    m.imports=m.imports.slice(0,2);
    for(const [i,id] of ['budget','flags','is-visible','ordered',isEntity?'valid-id':'owner-budget'].entries())m.imports.push({path:'../rules/'+id+'.js',symbol:'rule'+id.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join(''),local:'validator'+(i+2)});
    if(!isEntity)m.imports.push({path:'../entities/customer.js',symbol:'CustomerValueComponent',local:'component10'},{path:'../entities/customer.js',symbol:'CustomerSnapshot',local:'component10Type',type_only:true});
    m.base=[...(isEntity?[call('commerce:valid-id','validator6','value','id')]:[]),call('audit:has-label','validator0','label','label'),budgetCall('commerce:budget','validator2')];
    m.extensions=[{id:'enabled',validators:[call('audit:is-enabled','validator1','enabled','enabled')]},
      {id:'flags',validators:[{rule:'commerce:flags',call:'validator3({["checks"]:fields["checks"],["flags"]:fields["flags"],["items"]:fields["labels"],["needle"]:fields["label"],["tags"]:fields["tags"]})'}]},
      {id:'ordered',validators:[{rule:'commerce:ordered',call:`validator5({["left"]:fields["label"],["right"]:fields["${isEntity?'id':'locale'}"]})`}]},
      ...(!isEntity?[{id:'owner-budget',validators:[budgetCall('commerce:owner-budget','validator6','["owner"].fields')]}]:[]),
      {id:'visible',validators:[call('commerce:is-visible','validator4','flag','enabled')]}];
  }
  return e;
}
const budgetInput=(patch:object={})=>({allowed:[0,2,10],amount:2,amounts:[2,10],cap:10,checks:[false,true],flags:[true,false],labels:['Alex','Alex'],tags:['Alex'],...patch});
function factoryRuleRuntime(root:string){
  const customerModule=loadJs(root,paths.customer),contactModule=loadJs(root,paths.contact),cf=customerModule.createCustomerFactory(),vf=contactModule.createContactFactory();
  const entity=(patch:object={})=>customer({...budgetInput(),...patch});
  const child=(patch:object={})=>{const r=cf.create(entity(patch));assert.equal(r.ok,true,JSON.stringify(r));return r.value;};
  const value=(patch:object={})=>contact({...budgetInput(),owner:child(),...patch});
  return {cf,vf,entity,child,value,customerModule};
}
function observeFactoryRules(root:string,valueProfile:string=NUMERIC_RULE_VALUE_PROFILE){
  const pathFor=(selector:string)=>{const [feature,id]=selector.split(':');return `application/features/${feature}/src/domain/rules/${id}.ts`;};
  const symbol=(id:string)=>'rule'+id.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
  const declarations:any={'audit:has-label':[{name:'label',type:'String'}],'audit:is-enabled':[{name:'enabled',type:'Bool'}],'commerce:is-visible':[{name:'flag',type:'Bool'}],'commerce:valid-id':[{name:'value',type:'String'}]};
  for(const [id,contract] of Object.entries(composedRuleDefinitions()))declarations['commerce:'+id]=contract.parameters.map((p:any)=>({name:p.name,type:p.type.kind==='scalar'?p.type.name:`${p.type.kind}<${p.type.element.name}>`}));
  const expected=Object.entries(declarations).map(([selector,parameters])=>{const id=selector.split(':')[1]!,dependency=id==='budget'?'below':id==='owner-budget'?'budget':null;
    return {path:pathFor(selector),callable:symbol(id),value_profile:valueProfile,parameters,imports:dependency?[{path:'./'+dependency+'.js',symbol:symbol(dependency),local:'dependency0'}]:[]};});
  const configPath=path.join(root,'rules-tsconfig.json'),expectedPath=path.join(root,'rules-expected.json');
  fs.writeFileSync(configPath,JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expected.map(row=>row.path)}));fs.writeFileSync(expectedPath,JSON.stringify(expected));
  const image=nativeToolchainImage(JSON.parse(read('../../toolchains/node-typescript/toolchain.json')).container_image);
  const observer=path.join(project,'impl/cli/tools/observe-configured-rule-collections.mjs');
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root},readonly`,'--mount',`type=bind,source=${observer},target=/observer.mjs,readonly`,image,'node','/observer.mjs',configPath,expectedPath];
  try{return JSON.parse(execFileSync('docker',args,{encoding:'utf8',stdio:'pipe'}));}catch(error){const e=error as any;if(e.status===1&&e.stdout)return JSON.parse(e.stdout);throw error;}
}

test('PCR-06 factory Rule composition explicitly binds v5 numeric contracts and preserves old versions',t=>{
  const f=factoryRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,factoryRuleSources);
  assert.equal(p.schema_version,'domainspec.configured-factories-plan/v10-candidate');assert.equal(p.factory_contract_sha256,RULE_COMPOSITION_FACTORY_CONTRACT_SHA256);
  assert.deepEqual(p.selection.rule_selection,composedRuleSelection);assert.equal(p.collection_support!.sha256,entitySupportHash);
  const roots=[...new Set(f.selection.factories.flatMap(f=>[...f.base_validators,...f.extensions.flatMap(e=>e.validators)].map(v=>v.rule)))];
  const rules=planConfiguredRules(f.graph,{...composedRuleSelection,language:'typescript',module_root:'application',roots},composedRuleSources);
  assert.equal(p.rule_plan_sha256,rules.plan_sha256);
  for(const a of rules.artifacts)assert.deepEqual(p.artifacts.find(x=>x.relative_path===a.relative_path),a);
  for(const m of p.modules)for(const v of [...m.base_validators,...m.extensions.flatMap(e=>e.validators)])assert.equal(v.artifact_sha256,rules.artifacts.find(a=>a.relative_path===rules.modules.find(r=>r.selector===v.rule)!.relative_path)!.sha256);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,factories:[...f.selection.factories].reverse()},factoryRuleSources),p);
  assert.deepEqual(planConfiguredFactories(f.graph,f.fields,{...f.selection,module_root:'another'},factoryRuleSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  const old=entityRuleFixture(t),before=planConfiguredFactories(old.graph,old.fields,old.selection,entityRuleSources);
  planConfiguredFactories(old.graph,old.fields,{...old.selection,schema_version:RULE_COMPOSITION_FACTORY_VERSION,rule_selection:composedRuleSelection},factoryRuleSources);
  assert.deepEqual(planConfiguredFactories(old.graph,old.fields,old.selection,entityRuleSources),before);
  fs.renameSync(f.source,path.join(f.temp,'source-removed'));assert.deepEqual(planConfiguredFactories(f.graph,f.fields,f.selection,factoryRuleSources),p);
});

test('PCR-06 factory Rule composition rejects missing selection source drift mismatched types and unsafe paths',t=>{
  const f=factoryRuleFixture(t),run=(selection:any)=>planConfiguredFactories(f.graph,f.fields,selection,factoryRuleSources);
  const {rule_selection,...missing}=f.selection;assert.throws(()=>run(missing),/unknown or missing fields/);
  for(const rule_selection of [{...composedRuleSelection,schema_version:'old'}, {...composedRuleSelection,value_profile:'full-width-uint64'}, {...composedRuleSelection,roots:['commerce:budget']}])assert.throws(()=>run({...f.selection,rule_selection}),/unsupported Rule selection|unknown or missing fields/);
  for(const key of Object.keys(factoryRuleSources))assert.throws(()=>planConfiguredFactories(f.graph,f.fields,f.selection,{...factoryRuleSources,[key]:(factoryRuleSources as any)[key]+' '}));
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...missing,schema_version:ENTITY_RULE_PATH_FACTORY_VERSION},entityRuleSources),/validator path must end at scalar/);
  assert.throws(()=>planConfiguredFactories(f.graph,f.fields,{...f.selection,schema_version:ENTITY_RULE_PATH_FACTORY_VERSION},entityRuleSources),/unknown or missing fields/);
  for(const endpoint of ['amount','amounts','owner','missing']){
    const selected=structuredClone(f.selection),v=selected.factories.find(f=>f.selector==='commerce:contact')!.base_validators.at(-1)!;
    (v.arguments[0] as any).path=[endpoint];assert.throws(()=>run(selected),/validator endpoint|validator field\/type mismatch/);
  }
  for(const segments of [['owner','amounts','0'],['owner','amount','toString'],['owner','missing'],['owner','allowed','0'],['owner']]){
    const selected=structuredClone(f.selection),v=selected.factories.find(f=>f.selector==='commerce:contact')!.extensions.find(e=>e.id==='owner-budget')!.validators[0]!;
    (v.arguments[1] as any).path=segments;assert.throws(()=>run(selected),/DS_CONFIGURED_FACTORY:/);
  }
  const selected=structuredClone(f.selection);(selected.factories.find(f=>f.selector==='commerce:contact')!.base_validators as any[]).pop();assert.throws(()=>run(selected),/authored invariant coverage/);
});

test('PCR-06 factory Rule composition rejects optional and nested endpoints without unwrapping them',t=>{
  for(const type of [{kind:'optional',element:ruleScalar('UInt64')},{kind:'list',element:ruleCollection('list','UInt64')},{kind:'optional',element:{kind:'named',selector:'commerce:customer'}}]){
    const f=factoryRuleFixture(t),file='specs/commerce/nodes/contact.json',node=JSON.parse(fs.readFileSync(path.join(f.source,file),'utf8'));
    node.body.fields.push('unsupported');node.body.typed_contract.properties.push({name:'unsupported',type,identity:false,cardinality:type.kind==='optional'?'optional':'many',meaning:'explicit unsupported endpoint',ontology_property:'FIXTURE-CONTACT#unsupported'});f.write(file,node);
    const current=f.recompile(),selection=structuredClone(f.selection) as any;selection.field_compilation_sha256=current.fields.compilation_sha256;
    const v=selection.factories.find((f:any)=>f.selector==='commerce:contact').base_validators.at(-1);
    v.arguments[0].path=['unsupported'];assert.throws(()=>planConfiguredFactories(current.graph,current.fields,selection,factoryRuleSources),/validator endpoint/);
    if(type.kind==='optional'&&type.element.kind==='named'){v.arguments[0].path=['unsupported','allowed'];assert.throws(()=>planConfiguredFactories(current.graph,current.fields,selection,factoryRuleSources),/validator path must traverse required owned/);}
  }
});

test('PCR-06 factory Rule composition native observers verify exact factories Rules imports and scalar collection bindings',t=>{
  const f=factoryRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,factoryRuleSources),root=path.join(f.temp,'composition-observed');
  const n=native(root,p.artifacts,factoryRuleExpected());assert.deepEqual(n.observe().errors,[]);assert.deepEqual(observeFactoryRules(root).errors,[]);
  const r=factoryRuleRuntime(root);assert.ok(r.cf.create(r.entity()).ok);assert.ok(r.vf.create(r.value()).ok);
  const id=r.child(),next=r.cf.transition(id,r.entity({amount:0,amounts:[0],allowed:[0]}));assert.ok(next.ok);assert.ok(id.sameIdentity(next.value));
  const vo=r.vf.create(r.value()).value,other=r.vf.create(r.value({amount:0,amounts:[0],allowed:[0]})).value;assert.equal(vo.equals(other),false);
});

test('PCR-06 factory Rule composition validates every construction route and normalizes before Rules',t=>{
  const f=factoryRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,factoryRuleSources),root=path.join(f.temp,'composition-routes');native(root,p.artifacts,factoryRuleExpected());const r=factoryRuleRuntime(root),previous=r.child();
  for(const route of ['create','reconstruct','transition']){
    const run=(input:object)=>route==='transition'?r.cf.transition(previous,input):(r.cf as any)[route](input);
    for(const patch of [{amount:10},{allowed:[0]},{amounts:[2,2]},{amounts:[]}]){const failed=run(r.entity(patch));assert.deepEqual(failed.failure_codes,['RULE_FAIL:commerce:budget']);assert.equal(failed.value,null);assert.equal(failed.trace.validators.at(-1).outcome,'fail');}
    for(const patch of [{amount:-1},{amount:9007199254740992},{amount:'2'},{amounts:[NaN]},{allowed:[2,2]},{allowed:[-0,0]},{amounts:Array(1)}]){const failed=run(r.entity(patch));assert.deepEqual(failed.failure_codes,['INVALID_FIELDS']);assert.deepEqual(traceRules(failed),[]);}
    let reads=0;const input=r.entity();Object.defineProperty(input,'amount',{enumerable:true,get(){reads++;return 2;}});assert.deepEqual(run(input).failure_codes,['INVALID_FIELDS']);assert.equal(reads,0);
    const zero=run(r.entity({amount:-0,amounts:[-0],allowed:[-0]}));assert.ok(zero.ok);assert.equal(Object.is(zero.value.fields.amount,-0),false);
    assert.ok(run(r.entity({amount:9007199254740990,cap:9007199254740991,amounts:[9007199254740990],allowed:[9007199254740990]})).ok);
  }
  for(const route of ['create','reconstruct']){assert.ok(r.vf[route](r.value()).ok);assert.deepEqual(r.vf[route](r.value({amount:10})).failure_codes,['RULE_FAIL:commerce:budget']);}
  const input=r.entity(),before=structuredClone(input),made=r.cf.create(input);assert.ok(made.ok);assert.deepEqual(input,before);assert.notEqual(made.value.fields.amounts,input.amounts);assert.ok(Object.isFrozen(made.value.fields.amounts));
});

test('PCR-06 factory Rule composition keeps collection and String extensions additive and child scope local',t=>{
  const f=factoryRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,factoryRuleSources),root=path.join(f.temp,'composition-extensions');native(root,p.artifacts,factoryRuleExpected());const r=factoryRuleRuntime(root);
  const enabled=r.cf.extend('enabled'),flags=r.cf.extend('flags'),ordered=r.cf.extend('ordered');
  assert.ok(flags.create(r.entity()).ok);assert.ok(ordered.create(r.entity()).ok);
  for(const patch of [{flags:[false]},{checks:[true,true]},{tags:['wrong']},{labels:['wrong'],tags:['wrong']}]){
    assert.ok(r.cf.create(r.entity(patch)).ok);assert.deepEqual(flags.create(r.entity(patch)).failure_codes,['RULE_FAIL:commerce:flags']);assert.ok(enabled.create(r.entity(patch)).ok);
  }
  const previous=flags.create(r.entity()).value;
  for(const route of ['create','reconstruct','transition']){
    const input=r.entity({checks:[true,true]}),failed=route==='transition'?flags.transition(previous,input):flags[route](input);
    assert.deepEqual(failed.failure_codes,['RULE_FAIL:commerce:flags']);assert.equal(failed.value,null);
  }
  assert.deepEqual(ordered.create(r.entity({label:'z'})).failure_codes,['RULE_FAIL:commerce:ordered']);
  assert.deepEqual(flags.extend('enabled').create(r.entity({enabled:false})).failure_codes,['RULE_FAIL:audit:is-enabled']);
  assert.ok(flags.create(r.entity({enabled:false})).ok);
  const owner=r.child({enabled:false,flags:[false]}),input=r.value({owner});
  assert.ok(r.vf.extend('owner-budget').create(input).ok,'child extensions are not implicitly adopted');
  const changed=r.child({amount:5,amounts:[2,5],allowed:[2,5]});assert.ok(owner.sameIdentity(changed));
  assert.ok(r.vf.create(r.value({owner:changed})).ok);
  assert.deepEqual(r.vf.extend('owner-budget').create(r.value({owner:changed})).failure_codes,['RULE_FAIL:commerce:owner-budget'],'snapshot state is not identity equality or the parent amount');
  const parent=r.vf.create(input).value;r.cf.transition(owner,r.entity({amount:5,amounts:[2,5],allowed:[2,5]}));assert.equal(parent.fields.owner.fields.amount,2);
  let reads=0;const forged={get fields(){reads++;return owner.fields;}};
  assert.deepEqual(r.vf.extend('owner-budget').create(r.value({owner:forged})).failure_codes,['INVALID_FIELDS']);assert.equal(reads,0);
});

test('PCR-06 factory Rule composition native compiling mutants expose exact path and validation bypass errors',t=>{
  const f=factoryRuleFixture(t),p=planConfiguredFactories(f.graph,f.fields,f.selection,factoryRuleSources),original=p.artifacts.find(a=>a.relative_path===paths.customer)!.content;
  const wrongArgument=original.replace('["amount"]:fields["amount"]','["amount"]:fields["cap"]');assert.notEqual(wrongArgument,original);
  const root=path.join(f.temp,'composition-mutant'),n=native(root,p.artifacts.map(a=>a.relative_path===paths.customer?{...a,content:wrongArgument}:a),factoryRuleExpected());
  assert.ok(n.observe().errors.includes('base-binding:'+paths.customer));const r=factoryRuleRuntime(root);assert.equal(r.cf.create(r.entity()).ok,false,'valid input is rejected by same-type argument substitution');
  const parentSource=p.artifacts.find(a=>a.relative_path===paths.contact)!.content;
  const parentMutation=parentSource.replace('["amount"]:fields["owner"].fields["amount"]','["amount"]:fields["amount"]');assert.notEqual(parentMutation,parentSource);
  const parentRoot=path.join(f.temp,'composition-parent-substitution'),parentNative=native(parentRoot,p.artifacts.map(a=>a.relative_path===paths.contact?{...a,content:parentMutation}:a),factoryRuleExpected());
  assert.ok(parentNative.observe().errors.includes('extension-binding:'+paths.contact));const pr=factoryRuleRuntime(parentRoot);
  assert.ok(pr.vf.extend('owner-budget').create(pr.value({owner:pr.child({amount:5,amounts:[2,5],allowed:[2,5]})})).ok,'same-type parent substitution wrongly accepts child amount 5');
  const bypass=original.replace('validator.validate(fields) === true','true');assert.notEqual(bypass,original);
  const other=path.join(f.temp,'composition-bypass');native(other,p.artifacts.map(a=>a.relative_path===paths.customer?{...a,content:bypass}:a),factoryRuleExpected());
  const b=factoryRuleRuntime(other);assert.ok(b.cf.create(b.entity({amount:10})).ok,'runtime oracle detects invalid input accepted by compiling bypass');
  const broken=p.artifacts.map(a=>a.relative_path.endsWith('/below.ts')?{...a,content:a.content.replace('(p0 < p1)','(p0 > p1)')}:a);
  assert.notDeepEqual(broken,p.artifacts);const reversed=path.join(f.temp,'composition-direction');native(reversed,broken,factoryRuleExpected());
  assert.equal(observeFactoryRules(reversed).result,'pass');const c=factoryRuleRuntime(reversed);assert.equal(c.cf.create(c.entity()).ok,false,'structural Rule pass does not prove correct factory behavior');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
