import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {compileSelectedProjectFields, compiledFieldValueKey, FIELD_CONTRACT_SHA256, PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../../src/input/compiled-field-model.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileFieldReferenceModel, fieldValueKey, EXACT_FIELD_MODEL_VERSION, EXACT_FIELD_VALUE_PROFILE} from '../../src/input/field-reference-model.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {planConfiguredFactories} from '../../src/generation/configured-factories.ts';
import {planConfiguredEnums} from '../../src/generation/configured-enums.ts';

const descriptor=fs.readFileSync(new URL('../../../../development/reconciliation-v1/contracts/field-and-reference-model.json',import.meta.url),'utf8');
const exactDescriptor=fs.readFileSync(new URL('../../../../development/reconciliation-v1/contracts/exact-field-and-reference-model.json',import.meta.url),'utf8');
const dataFixture=()=>JSON.parse(fs.readFileSync(new URL('../fixtures/field-reference-model/commerce.json',import.meta.url),'utf8'));
function fixture(t:any, data=dataFixture()) {
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'dsr009-checked-fields-'));
  t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');
  const write=(relative:string,value:unknown)=>{const file=path.join(source,relative);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
  const features=[...new Set(['commerce',...data.declarations.map((d:any)=>d.selector.split(':')[0])])].sort();
  write('project.json',{schema_version:'domainspec.project/v1',project_id:'field-integration',features,cross_feature_edges:[]});
  for(const feature of features)write(`specs/${feature}/feature.json`,{schema_version:'domainspec.feature/v1',feature_id:feature,nodes:[...data.declarations.filter((d:any)=>d.selector.startsWith(feature+':')).map((d:any)=>d.selector.split(':')[1]),...(feature==='commerce'?['valid-value','unselected']:[])],edges:[]});
  for(const d of data.declarations) {
    const [feature_id,node_id]=d.selector.split(':');
    const body={description:d.selector,typed_contract:d.contract,...(d.kind==='Enum'?{values:d.contract.variants.map((v:any)=>v.name)}:{fields:d.contract.properties.map((p:any)=>p.name)}),...(d.kind==='Value Object'?{invariant_refs:d.invariant_refs}:{})};
    write(`specs/${feature_id}/nodes/${node_id}.json`,{schema_version:'domainspec.node/v1',feature_id,node_id,kind:d.kind,body});
  }
  write('specs/commerce/nodes/valid-value.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:'valid-value',kind:'Rule',body:{description:'Invariant target fixture only; this integration does not execute it.',predicate:'fixture'}});
  write('specs/commerce/nodes/unselected.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:'unselected',kind:'Entity',body:{description:'Valid untyped entity outside selected closure.',identity_field:'id',fields:[{field_id:'id',type_ref:{kind:'primitive',name:'string'},required:true}]}});
  const graph=loadCompiledProjectGraph(source);
  const selection={schema_version:PROJECT_FIELD_SELECTION_VERSION,contract_sha256:FIELD_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,roots:['commerce:order'],bindings:data.bindings};
  return {temp,source,write,data,graph,selection};
}
function expect(code:string,fn:()=>unknown){assert.throws(fn,(e:any)=>e.code===code);}
const money=(amount=10)=>({amount,currency:'GBP'});
const order=()=>({id:{tenant:'shop',number:1},customer:{id:'customer-a',name:'Alex'},customer_id:'customer-a',customer_name:'Alex',lines:[money()],tags:['gift'],status:{variant:'Draft'}});

test('checked-project adapter derives the exact field model from real DomainSpec sources',t=>{
  const f=fixture(t),before=canonicalJson(f.graph),fields=compileSelectedProjectFields(f.graph,f.selection,descriptor);
  assert.deepEqual(fields.model,compileFieldReferenceModel(f.data));
  assert.deepEqual(fields.invariant_references,['commerce:valid-value']);assert.equal(fields.invariant_execution,'not-performed');
  assert.deepEqual(fields.unselected_node_selectors,['commerce:unselected','commerce:valid-value']);
  assert.equal(fields.authority_effect,'none');assert.deepEqual(fields.certificate,createCompiledProjectCertificate(f.graph));
  assert.equal(canonicalJson(f.graph),before);assert.ok(Object.isFrozen(fields.certificate.compiler));
  const {compilation_sha256,...body}=fields;assert.equal(compilation_sha256,sha256(canonicalJson(body)));
  assert.deepEqual(compileSelectedProjectFields(f.graph,f.selection,descriptor),fields);
  assert.equal(compiledFieldValueKey(fields,'commerce:order',order()),fieldValueKey(fields.model,'commerce:order',order()));
  expect('FIELD_VALUE_TYPE',()=>compiledFieldValueKey(fields,'commerce:order',{...order(),customer_id:42}));
  expect('PROJECT_FIELD_UNCHECKED',()=>compiledFieldValueKey(structuredClone(fields),'commerce:order',order()));
});

test('selection closure follows named types and explicit references without swallowing unused bindings',t=>{
  const f=fixture(t);
  const customerOnly=compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:customer'],bindings:[]},descriptor);
  assert.deepEqual(customerOnly.model.declarations.map(d=>d.selector),['commerce:customer','commerce:order-id']);
  const referenced=compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:customer']},descriptor);
  assert.equal(referenced.model.declarations.length,5,'reference target and its typed dependencies enter closure');
  expect('PROJECT_FIELD_UNUSED_BINDING',()=>compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:money']},descriptor));
  const moneyOnly=compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:money'],bindings:[]},descriptor);
  assert.deepEqual(moneyOnly.model.declarations.map(d=>d.selector),['commerce:money']);
  expect('FIELD_DANGLING',()=>compiledFieldValueKey(moneyOnly,'commerce:order',order()));
});

test('graph and contract binding reject stale selections while checked snapshots require no disk reread',t=>{
  const f=fixture(t),fields=compileSelectedProjectFields(f.graph,f.selection,descriptor);
  expect('PROJECT_FIELD_CONTRACT',()=>compileSelectedProjectFields(f.graph,f.selection,descriptor+' '));
  expect('PROJECT_FIELD_CONTRACT',()=>compileSelectedProjectFields(f.graph,{...f.selection,contract_sha256:'0'.repeat(64)},descriptor));
  expect('PROJECT_FIELD_STALE',()=>compileSelectedProjectFields(f.graph,{...f.selection,graph_sha256:'0'.repeat(64)},descriptor));
  const file=path.join(f.source,'specs/commerce/nodes/order.json'),node=JSON.parse(fs.readFileSync(file,'utf8'));
  node.body.description='changed source';f.write('specs/commerce/nodes/order.json',node);
  const changed=loadCompiledProjectGraph(f.source);
  expect('PROJECT_FIELD_STALE',()=>compileSelectedProjectFields(changed,f.selection,descriptor));
  fs.renameSync(f.source,path.join(f.temp,'moved-source'));
  assert.deepEqual(compileSelectedProjectFields(f.graph,f.selection,descriptor),fields);
  expect('MTCLI_COMPILED_SNAPSHOT',()=>compileSelectedProjectFields(structuredClone(f.graph),f.selection,descriptor));
});

test('closed selection cannot redefine declarations, skip invariant targets or silently select unsupported nodes',t=>{
  const f=fixture(t);
  for(const extra of [{declarations:[]},{value_profile:'full-uint64'},{ignore_blockers:true}])expect('PROJECT_FIELD_SELECTION',()=>compileSelectedProjectFields(f.graph,{...f.selection,...extra},descriptor));
  expect('PROJECT_FIELD_VERSION',()=>compileSelectedProjectFields(f.graph,{...f.selection,schema_version:'future'},descriptor));
  for(const roots of [[],['commerce:order','commerce:order']])expect('PROJECT_FIELD_ROOTS',()=>compileSelectedProjectFields(f.graph,{...f.selection,roots},descriptor));
  expect('PROJECT_FIELD_KIND',()=>compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:valid-value'],bindings:[]},descriptor));
  expect('PROJECT_FIELD_UNTYPED',()=>compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:unselected'],bindings:[]},descriptor));
  expect('PROJECT_FIELD_MISSING',()=>compileSelectedProjectFields(f.graph,{...f.selection,roots:['commerce:missing'],bindings:[]},descriptor));
  const missingInvariant=JSON.parse(fs.readFileSync(path.join(f.source,'specs/commerce/nodes/money.json'),'utf8'));
  missingInvariant.body.invariant_refs=['commerce:missing'];f.write('specs/commerce/nodes/money.json',missingInvariant);
  expect('MTCLI_VALUE_OBJECT_INVARIANT_REFERENCE',()=>loadCompiledProjectGraph(f.source));
});

test('reference metadata is type checked and never becomes a semantic relationship or automatic lookup',t=>{
  const f=fixture(t),original=canonicalJson(f.graph.relationships),bindings=structuredClone(f.selection.bindings);
  bindings[0].projection=['name'];expect('FIELD_REFERENCE_IDENTITY',()=>compileSelectedProjectFields(f.graph,{...f.selection,bindings},descriptor));
  bindings[0].projection=['id'];bindings[0].target='commerce:missing';expect('PROJECT_FIELD_MISSING',()=>compileSelectedProjectFields(f.graph,{...f.selection,bindings},descriptor));
  const fields=compileSelectedProjectFields(f.graph,f.selection,descriptor),plain=compileSelectedProjectFields(f.graph,{...f.selection,bindings:[]},descriptor);
  assert.notEqual(fields.compilation_sha256,plain.compilation_sha256);
  assert.equal(compiledFieldValueKey(fields,'commerce:order',order()),compiledFieldValueKey(plain,'commerce:order',order()));
  assert.equal(canonicalJson(f.graph.relationships),original);assert.equal('relationships' in fields.model,false);
  assert.doesNotThrow(()=>compiledFieldValueKey(fields,'commerce:order',{...order(),customer_id:'not-looked-up'}));
});

test('cross-feature typed dependencies retain selectors and source relocation does not change compilation identity',t=>{
  const data=JSON.parse(JSON.stringify(dataFixture()).replaceAll('commerce:money','finance:money'));
  const f=fixture(t,data),fields=compileSelectedProjectFields(f.graph,f.selection,descriptor);
  assert.ok(fields.model.declarations.some(d=>d.selector==='finance:money'));
  assert.equal(fields.model.declarations.some(d=>d.selector==='commerce:money'),false);
  assert.doesNotThrow(()=>compiledFieldValueKey(fields,'finance:money',money()));
  const moved=path.join(f.temp,'second-root');fs.cpSync(f.source,moved,{recursive:true});
  assert.deepEqual(compileSelectedProjectFields(loadCompiledProjectGraph(moved),f.selection,descriptor),fields);
  const reversed={...f.selection,roots:['finance:money','commerce:order'],bindings:[...f.selection.bindings].reverse()};
  assert.deepEqual(compileSelectedProjectFields(f.graph,reversed,descriptor),compileSelectedProjectFields(f.graph,{...reversed,roots:[...reversed.roots].reverse(),bindings:f.selection.bindings},descriptor));
});

const maximum=18446744073709551615n;
const exactSelection=(f:ReturnType<typeof fixture>)=>({...f.selection,schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256});

test('PCR-06 exact checked fields bind the neutral profile to the unchanged checked declaration graph',t=>{
  const f=fixture(t),before=canonicalJson(f.graph),selection=exactSelection(f),fields=compileSelectedProjectFields(f.graph,selection,exactDescriptor);
  const contract=JSON.parse(exactDescriptor);
  assert.equal(sha256(exactDescriptor),EXACT_FIELD_CONTRACT_SHA256);
  assert.equal(contract.input_schema_version,EXACT_FIELD_MODEL_VERSION);assert.equal(contract.value_profile,EXACT_FIELD_VALUE_PROFILE);
  assert.equal(contract.selection_schema_version,EXACT_PROJECT_FIELD_SELECTION_VERSION);
  assert.equal(fields.schema_version,'domainspec.compiled-project-fields/v2-candidate');
  assert.deepEqual(fields.model,compileFieldReferenceModel({...f.data,schema_version:EXACT_FIELD_MODEL_VERSION,value_profile:EXACT_FIELD_VALUE_PROFILE}));
  assert.deepEqual(fields.invariant_references,['commerce:valid-value']);assert.equal(fields.invariant_execution,'not-performed');assert.equal(fields.authority_effect,'none');
  assert.equal(canonicalJson(f.graph),before);assert.deepEqual(fields.certificate,createCompiledProjectCertificate(f.graph));
  assert.ok(Object.isFrozen(fields.selection.bindings));assert.ok(Object.isFrozen(fields.model.declarations));
  const {compilation_sha256,...body}=fields;assert.equal(compilation_sha256,sha256(canonicalJson(body)));
  assert.deepEqual(JSON.parse(compiledFieldValueKey(fields,'commerce:money',{amount:maximum,currency:'GBP'})),
    ['Value Object','commerce:money',[['amount',['UInt64','18446744073709551615']],['currency',['String','GBP']]]]);
  const legacy=compileSelectedProjectFields(f.graph,f.selection,descriptor);
  assert.deepEqual(legacy.model.declarations,fields.model.declarations);assert.deepEqual(legacy.model.bindings,fields.model.bindings);
  assert.notEqual(legacy.model.model_sha256,fields.model.model_sha256);assert.notEqual(legacy.compilation_sha256,compilation_sha256);
  expect('FIELD_JSON',()=>compiledFieldValueKey(legacy,'commerce:money',{amount:maximum,currency:'GBP'}));
  expect('FIELD_VALUE_TYPE',()=>compiledFieldValueKey(legacy,'commerce:money',{amount:maximum.toString(),currency:'GBP'}));
});

test('PCR-06 exact checked fields reject mismatched versions stale evidence and forged checked objects',t=>{
  const f=fixture(t),selection=exactSelection(f),fields=compileSelectedProjectFields(f.graph,selection,exactDescriptor);
  for(const [selected,source] of [[f.selection,exactDescriptor],[selection,descriptor],[{...selection,contract_sha256:FIELD_CONTRACT_SHA256},exactDescriptor],[selection,exactDescriptor+' ']] as const)
    expect('PROJECT_FIELD_CONTRACT',()=>compileSelectedProjectFields(f.graph,selected,source));
  expect('PROJECT_FIELD_SELECTION',()=>compileSelectedProjectFields(f.graph,{...selection,value_profile:EXACT_FIELD_VALUE_PROFILE},exactDescriptor));
  expect('PROJECT_FIELD_STALE',()=>compileSelectedProjectFields(f.graph,{...selection,graph_sha256:'0'.repeat(64)},exactDescriptor));
  expect('MTCLI_COMPILED_SNAPSHOT',()=>compileSelectedProjectFields(structuredClone(f.graph),selection,exactDescriptor));
  expect('PROJECT_FIELD_UNCHECKED',()=>compiledFieldValueKey(structuredClone(fields),'commerce:money',money()));
  const node=JSON.parse(fs.readFileSync(path.join(f.source,'specs/commerce/nodes/money.json'),'utf8'));
  node.body.description='Changed checked source';f.write('specs/commerce/nodes/money.json',node);
  expect('PROJECT_FIELD_STALE',()=>compileSelectedProjectFields(loadCompiledProjectGraph(f.source),selection,exactDescriptor));
});

test('PCR-06 exact checked fields retain full-width references identity and relocation without runtime lookup',t=>{
  const data=dataFixture(),property=(node:string,name:string)=>data.declarations.find((d:any)=>d.selector==='commerce:'+node).contract.properties.find((p:any)=>p.name===name);
  property('customer','id').type={kind:'scalar',name:'UInt64'};property('order','customer_id').type={kind:'scalar',name:'UInt64'};
  const f=fixture(t,data),selection=exactSelection(f),fields=compileSelectedProjectFields(f.graph,selection,exactDescriptor),edges=canonicalJson(f.graph.relationships);
  const value={...order(),id:{tenant:'shop',number:maximum},customer:{id:maximum,name:'Alex'},customer_id:maximum-1n,lines:[{amount:maximum,currency:'GBP'}],status:{variant:'Paid',payload:{amount:maximum,currency:'GBP'}}};
  const key=compiledFieldValueKey(fields,'commerce:order',value);
  assert.equal(key,compiledFieldValueKey(fields,'commerce:order',{...value,id:{tenant:'shop',number:maximum.toString()}}));
  assert.notEqual(key,compiledFieldValueKey(fields,'commerce:order',{...value,id:{tenant:'shop',number:maximum-1n}}));
  expect('FIELD_VALUE_TYPE',()=>compiledFieldValueKey(fields,'commerce:order',{...value,customer_id:maximum+1n}));
  expect('FIELD_VALUE_TYPE',()=>compiledFieldValueKey(fields,'commerce:order',{...value,status:{variant:'Paid',payload:{amount:maximum+1n,currency:'GBP'}}}));
  const plain=compileSelectedProjectFields(f.graph,{...selection,bindings:[]},exactDescriptor);
  assert.equal(key,compiledFieldValueKey(plain,'commerce:order',value));assert.notEqual(fields.compilation_sha256,plain.compilation_sha256);
  assert.equal(canonicalJson(f.graph.relationships),edges);
  const moved=path.join(f.temp,'relocated');fs.renameSync(f.source,moved);
  assert.deepEqual(compileSelectedProjectFields(f.graph,selection,exactDescriptor),fields,'checked snapshot needs no disk reread');
  assert.deepEqual(compileSelectedProjectFields(loadCompiledProjectGraph(moved),selection,exactDescriptor),fields);
  const multiple={...selection,roots:['commerce:order','commerce:money']};
  assert.deepEqual(compileSelectedProjectFields(f.graph,multiple,exactDescriptor),compileSelectedProjectFields(f.graph,{...multiple,roots:[...multiple.roots].reverse(),bindings:[...multiple.bindings].reverse()},exactDescriptor));
  const invalid=dataFixture();invalid.declarations.find((d:any)=>d.selector==='commerce:order').contract.properties.find((p:any)=>p.name==='customer_id').type={kind:'scalar',name:'UInt64'};
  const wrong=fixture(t,invalid);expect('FIELD_REFERENCE_TYPE',()=>compileSelectedProjectFields(wrong.graph,exactSelection(wrong),exactDescriptor));
});

test('PCR-06 exact checked fields cannot enter old factory or Enum generation through structural compatibility',t=>{
  const f=fixture(t),fields=compileSelectedProjectFields(f.graph,exactSelection(f),exactDescriptor);
  let reads=0;const poison=Object.defineProperty({},'schema_version',{get(){reads++;throw new Error('generation selection read');}});
  assert.throws(()=>planConfiguredFactories(f.graph,fields,poison as any,{} as any),/exact field values require an explicit exact factory realization/);
  assert.throws(()=>planConfiguredEnums(fields,poison as any,{} as any),/exact field values require an explicit exact Enum realization/);
  assert.equal(reads,0,'reject at checked field profile boundary before generator planning or output');
});
