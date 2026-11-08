import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import test from 'node:test';
import {compileFieldReferenceModel, fieldValueKey, FieldReferenceError, EXACT_FIELD_MODEL_VERSION, EXACT_FIELD_VALUE_PROFILE} from '../../src/input/field-reference-model.ts';
import {decodeTypedType} from '../../src/typed-operation/contracts.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const fixture = () => JSON.parse(fs.readFileSync(new URL('../fixtures/field-reference-model/commerce.json', import.meta.url), 'utf8'));
const record = (m:any, selector:string) => m.declarations.find((d:any) => d.selector === 'commerce:' + selector);
const property = (m:any, owner:string, name:string) => record(m, owner).contract.properties.find((p:any) => p.name === name);
const scalar = (name='String') => ({kind:'scalar', name});
const named = (selector:string) => ({kind:'named',selector:'commerce:'+selector});
const wrap = (kind:string,element:any) => ({kind,element});
function field(name:string,type:any) {
  return {ontology_property:'COMMERCE-TEST#'+name,name,type,cardinality:({optional:'optional',list:'many',set:'many-unique'} as any)[type.kind]??'one',identity:false,meaning:name};
}
function box(type:any) {
  const input=fixture(); input.declarations.push({selector:'commerce:box',kind:'Value Object',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'COMMERCE-BOX',properties:[field('value',type)]},invariant_refs:['commerce:valid-value']});
  const model=compileFieldReferenceModel(input);
  return (value:unknown) => fieldValueKey(model,'commerce:box',{value});
}
function expect(code:string,fn:()=>unknown) {assert.throws(fn,(e:any)=>e.code===code);}
const money = (amount=10) => ({amount,currency:'GBP'});
const customer = (id='customer-a',name='Alex') => ({id,name});
const order = () => ({id:{tenant:'shop',number:1},customer:customer(),customer_id:'customer-a',customer_name:'Alex',lines:[money()],tags:['gift'],status:{variant:'Draft'}});

test('DSR-009 candidate keeps declared meanings and produces a deterministic immutable model',()=>{
  const input=fixture(),before=JSON.stringify(input),model=compileFieldReferenceModel(input);
  assert.equal(model.authority_effect,'none'); assert.equal(model.declarations.length,5);
  assert.deepEqual(model.declarations.map(d=>d.kind),['Entity','Value Object','Entity','Value Object','Enum']);
  assert.equal(JSON.stringify(input),before);
  const reversed=fixture(); reversed.declarations.reverse();reversed.bindings.reverse();
  assert.deepEqual(compileFieldReferenceModel(reversed),model);
  const {model_sha256,...body}=model;assert.equal(model_sha256,sha256(canonicalJson(body)));
  input.declarations[0].kind='Entity';assert.ok(Object.isFrozen(model.declarations[0]!.contract));
  expect('FIELD_UNCHECKED',()=>fieldValueKey(structuredClone(model),'commerce:money',money()));
});

test('V11 list ordering, set uniqueness, empty collections and optional absence are explicit',()=>{
  const list=box(wrap('list',scalar())),set=box(wrap('set',scalar()));
  assert.notEqual(list(['a','b']),list(['b','a']));assert.doesNotThrow(()=>list(['a','a']));
  assert.equal(set(['a','b']),set(['b','a']));expect('FIELD_SET_DUPLICATE',()=>set(['a','a']));
  assert.doesNotThrow(()=>list([]));assert.doesNotThrow(()=>set([]));
  const input=fixture(),model=compileFieldReferenceModel(input);
  assert.equal(fieldValueKey(model,'commerce:customer',customer()),fieldValueKey(model,'commerce:customer',{...customer(),favorite_order:null}));
  const optional=box(wrap('optional',scalar()));assert.doesNotThrow(()=>optional(null));
  const optionalVO=fixture();record(optionalVO,'money').contract.properties.push(field('memo',wrap('optional',scalar())));
  const optionalModel=compileFieldReferenceModel(optionalVO);
  assert.equal(fieldValueKey(optionalModel,'commerce:money',money()),fieldValueKey(optionalModel,'commerce:money',{...money(),memo:null}));
  assert.notEqual(fieldValueKey(optionalModel,'commerce:money',money()),fieldValueKey(optionalModel,'commerce:money',{...money(),memo:''}));
  expect('FIELD_VALUE_TYPE',()=>box(scalar())(null));expect('FIELD_JSON',()=>optional(undefined));
  for(const kind of ['list','set','optional']) expect('MTCLI_TYPED_TYPE',()=>decodeTypedType(wrap(kind,wrap('optional',scalar()))));
  const bad=fixture();property(bad,'order','tags').cardinality='many';expect('MTCLI_TYPED_CARDINALITY',()=>compileFieldReferenceModel(bad));
});

test('V11 UInt64 input envelope rejects lossy numbers instead of claiming full numeric parity',()=>{
  const key=box(scalar('UInt64'));
  assert.doesNotThrow(()=>key(0));assert.doesNotThrow(()=>key(Number.MAX_SAFE_INTEGER));
  for(const value of [-1,0.5,Number.MAX_SAFE_INTEGER+1,'18446744073709551615',true])expect('FIELD_VALUE_TYPE',()=>key(value));
  for(const value of [NaN,Infinity,1n])expect('FIELD_JSON',()=>key(value));
});

test('V11 sum discrimination and payload shape do not collapse into an untagged union',()=>{
  const model=compileFieldReferenceModel(fixture()),key=(v:unknown)=>fieldValueKey(model,'commerce:status',v);
  assert.notEqual(key({variant:'Draft'}),key({variant:'Paid',payload:money()}));
  expect('FIELD_VARIANT',()=>key({variant:'Missing'}));
  expect('FIELD_SHAPE',()=>key({variant:'Paid'}));expect('FIELD_SHAPE',()=>key({variant:'Draft',payload:null}));
  expect('FIELD_VALUE_TYPE',()=>key({variant:'Paid',payload:{amount:'10',currency:'GBP'}}));
  const bad=fixture();record(bad,'status').contract.variants.push(record(bad,'status').contract.variants[0]);expect('MTCLI_TYPED_DUPLICATE',()=>compileFieldReferenceModel(bad));
});

test('V12 Entity identity and Value Object equality remain observably different',()=>{
  const model=compileFieldReferenceModel(fixture());
  assert.equal(fieldValueKey(model,'commerce:customer',customer('a','Alex')),fieldValueKey(model,'commerce:customer',customer('a','Changed')));
  assert.notEqual(fieldValueKey(model,'commerce:customer',customer('a')),fieldValueKey(model,'commerce:customer',customer('b')));
  assert.equal(fieldValueKey(model,'commerce:money',money()),fieldValueKey(model,'commerce:money',{currency:'GBP',amount:10}));
  assert.notEqual(fieldValueKey(model,'commerce:money',money()),fieldValueKey(model,'commerce:money',money(11)));
  expect('FIELD_SET_DUPLICATE',()=>box(wrap('set',named('customer')))([customer('a','Alex'),customer('a','Changed')]));
  expect('FIELD_SET_DUPLICATE',()=>box(wrap('set',named('money')))([money(),money()]));
  const first=order(),second={...order(),id:{tenant:'other',number:1}};
  assert.notEqual(fieldValueKey(model,'commerce:order',first),fieldValueKey(model,'commerce:order',second));
  const changed={...first,lines:[]};assert.equal(fieldValueKey(model,'commerce:order',first),fieldValueKey(model,'commerce:order',changed));
  expect('FIELD_VALUE_TYPE',()=>fieldValueKey(model,'commerce:order',{...first,lines:[{amount:false,currency:'GBP'}]}));
});

test('V12 embedded Entity, identity reference and field projection have separate obligations',()=>{
  const input=fixture(),model=compileFieldReferenceModel(input);
  assert.doesNotThrow(()=>fieldValueKey(model,'commerce:order',order()));
  expect('FIELD_SHAPE',()=>fieldValueKey(model,'commerce:order',{...order(),customer:'customer-a'}));
  expect('FIELD_VALUE_TYPE',()=>fieldValueKey(model,'commerce:order',{...order(),customer_id:customer()}));
  const noBindings={...input,bindings:[]},plain=compileFieldReferenceModel(noBindings);
  assert.equal(fieldValueKey(plain,'commerce:order',order()),fieldValueKey(model,'commerce:order',order()));
  assert.notEqual(plain.model_sha256,model.model_sha256);
  assert.equal('relationships' in model,false);assert.equal('storage' in model,false);
  const wrongTarget=fixture();wrongTarget.bindings[0].target='commerce:missing';expect('FIELD_DANGLING',()=>compileFieldReferenceModel(wrongTarget));
  const wrongProjection=fixture();wrongProjection.bindings[1].projection=['missing'];expect('FIELD_PROJECTION',()=>compileFieldReferenceModel(wrongProjection));
  const notIdentity=fixture();notIdentity.bindings[0].projection=['name'];expect('FIELD_REFERENCE_IDENTITY',()=>compileFieldReferenceModel(notIdentity));
  const wrongType=fixture();property(wrongType,'order','customer_id').type=scalar('UInt64');expect('FIELD_REFERENCE_TYPE',()=>compileFieldReferenceModel(wrongType));
  const deep=fixture();deep.bindings[1]={...deep.bindings[1],target:'commerce:order',projection:['customer','name']};assert.doesNotThrow(()=>compileFieldReferenceModel(deep));
  const optionalPath=fixture();optionalPath.bindings[1]={...optionalPath.bindings[1],target:'commerce:customer',projection:['favorite_order','tenant']};expect('FIELD_PROJECTION',()=>compileFieldReferenceModel(optionalPath));
});

test('V12 embedding cycles fail while identity-reference cycles need no recursive object expansion',()=>{
  assert.doesNotThrow(()=>compileFieldReferenceModel(fixture()),'Order to Customer to Order references are finite');
  const cycle=fixture();record(cycle,'customer').contract.properties.push(field('back',named('order')));expect('FIELD_EMBEDDING_CYCLE',()=>compileFieldReferenceModel(cycle));
  const dangling=fixture();property(dangling,'order','customer').type=named('missing');expect('FIELD_DANGLING',()=>compileFieldReferenceModel(dangling));
  const projections=fixture();projections.bindings.push({owner:'commerce:customer',field:'name',kind:'field-projection',target:'commerce:order',projection:['customer_name']});expect('FIELD_REFERENCE_CYCLE',()=>compileFieldReferenceModel(projections));
  const identity=fixture();identity.bindings.push({owner:'commerce:customer',field:'id',kind:'field-projection',target:'commerce:order',projection:['customer_id']});expect('FIELD_IDENTITY_BINDING',()=>compileFieldReferenceModel(identity));
});

test('V13 shapes, declarations, names, identity and open-content limits fail closed',()=>{
  const model=compileFieldReferenceModel(fixture());
  expect('FIELD_EXTRA',()=>fieldValueKey(model,'commerce:money',{...money(),extra:1}));expect('FIELD_MISSING',()=>fieldValueKey(model,'commerce:money',{amount:10}));
  for(const mutate of [(m:any)=>m.declarations.push(m.declarations[0]),(m:any)=>m.bindings.push(m.bindings[0])]){const m=fixture();mutate(m);expect('FIELD_DUPLICATE',()=>compileFieldReferenceModel(m));}
  const duplicate=fixture();record(duplicate,'money').contract.properties.push(record(duplicate,'money').contract.properties[0]);expect('MTCLI_TYPED_DUPLICATE',()=>compileFieldReferenceModel(duplicate));
  const bad=fixture();property(bad,'money','amount').identity=true;expect('FIELD_IDENTITY',()=>compileFieldReferenceModel(bad));
  const noId=fixture();property(noId,'order','id').identity=false;expect('FIELD_IDENTITY',()=>compileFieldReferenceModel(noId));
  const arrayId=fixture();property(arrayId,'order','id').type={kind:'sum',variants:[{ontology_variant:'COMMERCE-ID#One',name:'One',payload:null}]};expect('FIELD_IDENTITY_TYPE',()=>compileFieldReferenceModel(arrayId));
  const open=fixture();record(open,'money').open=true;expect('FIELD_SHAPE',()=>compileFieldReferenceModel(open));
  const unknown=fixture();record(unknown,'money').kind='record';expect('FIELD_KIND',()=>compileFieldReferenceModel(unknown));
  let nested:any=scalar();for(let i=0;i<18;i++)nested=wrap('list',nested);expect('MTCLI_TYPED_DEPTH',()=>decodeTypedType(nested));
});

test('V13 non-JSON input and accessors cannot silently change candidate values',()=>{
  const model=compileFieldReferenceModel(fixture());let reads=0;
  expect('FIELD_JSON',()=>fieldValueKey(model,'commerce:money',{get amount(){reads++;return 10;},currency:'GBP'}));assert.equal(reads,0);
  expect('FIELD_JSON',()=>fieldValueKey(model,'commerce:money',Object.create({amount:10,currency:'GBP'})));
  expect('FIELD_JSON',()=>box(wrap('list',scalar()))(new Array(2)));
  assert.throws(()=>fieldValueKey(model,'commerce:money',null),FieldReferenceError);
});

test('DSR-009 published candidate descriptor matches the exercised version and limits',()=>{
  const contract=JSON.parse(fs.readFileSync(new URL('../../../../development/reconciliation-v1/contracts/field-and-reference-model.json',import.meta.url),'utf8'));
  const input=fixture();assert.equal(contract.input_schema_version,input.schema_version);assert.equal(contract.value_profile,input.value_profile);
  assert.deepEqual(contract.constructors,['scalar','named','optional','list','set','sum']);
  assert.equal(contract.values.uint64_max,Number.MAX_SAFE_INTEGER);assert.equal(contract.authority_effect,'none');
  assert.equal(contract.values.type_nesting_limit,16);assert.equal(contract.values.projection_depth_limit,16);
  const max=Array.from({length:16}).reduce<any>(t=>wrap('list',t),scalar());assert.doesNotThrow(()=>decodeTypedType(max));
  expect('MTCLI_TYPED_DEPTH',()=>decodeTypedType(wrap('list',max)));
  const chain=(length:number)=>({...fixture(),bindings:[],declarations:Array.from({length:length+1},(_,i)=>({selector:`commerce:chain-${i}`,kind:'Value Object',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'COMMERCE-CHAIN',properties:[field('next',i===length?scalar():named(`chain-${i+1}`))]},invariant_refs:['commerce:valid-value']}))});
  assert.doesNotThrow(()=>compileFieldReferenceModel(chain(32)));expect('FIELD_DEPTH',()=>compileFieldReferenceModel(chain(33)));
  const model=compileFieldReferenceModel(input);assert.doesNotThrow(()=>fieldValueKey(model,'commerce:money',money(contract.values.uint64_max)));
});

const maximum=18446744073709551615n;
const exactFixture=()=>({...fixture(),schema_version:EXACT_FIELD_MODEL_VERSION,value_profile:EXACT_FIELD_VALUE_PROFILE});
function exactBox(type:any) {
  const input=exactFixture();input.declarations.push({selector:'commerce:box',kind:'Value Object',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'COMMERCE-BOX',properties:[field('value',type)]},invariant_refs:['commerce:valid-value']});
  const model=compileFieldReferenceModel(input);
  return {input,model,key:(value:unknown)=>fieldValueKey(model,'commerce:box',{value})};
}

test('PCR-06 exact field values select a distinct neutral profile without widening v1',()=>{
  const input=exactFixture(),before=canonicalJson(input),model=compileFieldReferenceModel(input);
  assert.equal(model.schema_version,EXACT_FIELD_MODEL_VERSION);assert.equal(model.value_profile,'exact-uint64/v1-candidate');
  assert.equal(canonicalJson(input),before);assert.ok(Object.isFrozen(model.declarations[0]!.contract));
  const reordered=exactFixture();reordered.declarations.reverse();reordered.bindings.reverse();assert.deepEqual(compileFieldReferenceModel(reordered),model);
  const {model_sha256,...body}=model;assert.equal(model_sha256,sha256(canonicalJson(body)));
  for(const invalid of [{...input,schema_version:'future'},{...input,value_profile:'json-safe-uint64/v1-candidate'},{...fixture(),value_profile:EXACT_FIELD_VALUE_PROFILE}])expect('FIELD_VERSION',()=>compileFieldReferenceModel(invalid));
  const legacy=compileFieldReferenceModel(fixture());assert.notEqual(legacy.model_sha256,model.model_sha256);
  assert.deepEqual(legacy.declarations,model.declarations);assert.deepEqual(legacy.bindings,model.bindings);
  assert.deepEqual(JSON.parse(fieldValueKey(legacy,'commerce:money',money(10))),['Value Object','commerce:money',[['amount',['UInt64',10]],['currency',['String','GBP']]]]);
  expect('FIELD_VALUE_TYPE',()=>fieldValueKey(legacy,'commerce:money',{amount:maximum.toString(),currency:'GBP'}));
  expect('FIELD_JSON',()=>fieldValueKey(legacy,'commerce:money',{amount:maximum,currency:'GBP'}));
  expect('FIELD_UNCHECKED',()=>fieldValueKey(structuredClone(model),'commerce:money',money()));
  const bad=exactFixture();bad.declarations[0].contract.ontology_node=1n;expect('FIELD_JSON',()=>compileFieldReferenceModel(bad));
});

test('PCR-06 exact field values retain all UInt64 bits and only normalize numeric positions',()=>{
  const numeric=exactBox(scalar('UInt64')),text=exactBox(scalar('String')),boolean=exactBox(scalar('Bool'));
  const values=[0n,1n,2n,10n,9007199254740991n,9007199254740992n,maximum-1n,maximum];
  const representations=(value:bigint):unknown[]=>[value,value.toString(),...(value<=9007199254740991n?[Number(value)]:[])];
  for(const value of values)for(const input of representations(value)){
    assert.deepEqual(JSON.parse(numeric.key(input)),['Value Object','commerce:box',[['value',['UInt64',value.toString()]]]]);
    for(const other of values)for(const compared of representations(other))assert.equal(numeric.key(input)===numeric.key(compared),value===other);
  }
  assert.equal(numeric.key(-0),numeric.key('0'));assert.notEqual(numeric.key('10'),text.key('10'));
  assert.notEqual(text.key('01'),text.key('1'));assert.notEqual(text.key('é'),text.key('e\u0301'));
  assert.notEqual(boolean.key(true),numeric.key(1));expect('FIELD_VALUE_TYPE',()=>boolean.key(1n));expect('FIELD_VALUE_TYPE',()=>text.key(1n));
  for(const input of [-1,-1n,0.5,9007199254740992,maximum+1n,'18446744073709551616','00','01','+1','-0','-1','1.0','1e1','0x10',' 1','1 ','',true,null,'9'.repeat(200)])expect('FIELD_VALUE_TYPE',()=>numeric.key(input));
  for(const suffix of ['\n','\r','\r\n','\t','\0','\u2028','\u2029'])expect('FIELD_VALUE_TYPE',()=>numeric.key('1'+suffix));
  for(const input of [NaN,Infinity,-Infinity,undefined,new Number(1),new String('1')])expect('FIELD_JSON',()=>numeric.key(input));
});

test('PCR-06 exact field values preserve collection order occurrences uniqueness and nested normalization',()=>{
  const list=exactBox(wrap('list',scalar('UInt64'))),set=exactBox(wrap('set',scalar('UInt64')));
  const alphabet=[0n,2n,10n,maximum-1n,maximum],lists:bigint[][]=[[]];
  for(let length=1;length<=3;length++)for(const prefix of lists.filter(x=>x.length===length-1))for(const value of alphabet)lists.push([...prefix,value]);
  for(const values of lists){const mixed=values.map((x,i)=>i%2?x.toString():x),key=list.key(mixed);
    assert.equal(key,list.key(values));assert.equal(key===list.key([...mixed].reverse()),values.every((x,i)=>x===values[values.length-1-i]));
    const unique=new Set(values);if(unique.size!==values.length)expect('FIELD_SET_DUPLICATE',()=>set.key(mixed));else assert.equal(set.key(mixed),set.key([...mixed].reverse()));
  }
  expect('FIELD_SET_DUPLICATE',()=>set.key([2,'2',2n]));assert.notEqual(list.key([2]),list.key([2,2]));
  const nested=exactBox(wrap('list',wrap('set',scalar('UInt64'))));
  assert.equal(nested.key([[maximum,2n],[0n]]),nested.key([['2',maximum.toString()],[0]]));
  expect('FIELD_SET_DUPLICATE',()=>nested.key([[maximum,maximum.toString()]]));
  const setsOfLists=exactBox(wrap('set',wrap('list',scalar('UInt64'))));
  assert.doesNotThrow(()=>setsOfLists.key([[2,10],[10,2]]));expect('FIELD_SET_DUPLICATE',()=>setsOfLists.key([[2,10],['2',10n]]));
  const setsOfSets=exactBox(wrap('set',wrap('set',scalar('UInt64'))));expect('FIELD_SET_DUPLICATE',()=>setsOfSets.key([[2,10],['10',2n]]));
});

test('PCR-06 exact field values keep optional absence sums and payload variants distinct',()=>{
  const optional=exactBox(wrap('optional',scalar('UInt64'))),model=optional.model;
  assert.equal(fieldValueKey(model,'commerce:box',{}),optional.key(null));assert.notEqual(optional.key(null),optional.key('0'));
  const inline={kind:'sum',variants:[{ontology_variant:'COMMERCE-CHOICE#First',name:'First',payload:scalar('UInt64')},{ontology_variant:'COMMERCE-CHOICE#Second',name:'Second',payload:scalar('UInt64')},{ontology_variant:'COMMERCE-CHOICE#None',name:'None',payload:null}]};
  const sum=exactBox(inline),sumKey=(variant:string,payload:unknown)=>sum.key({variant,payload});
  assert.equal(sumKey('First',maximum),sumKey('First',maximum.toString()));assert.notEqual(sumKey('First',maximum),sumKey('Second',maximum));
  assert.notEqual(sumKey('First',maximum-1n),sumKey('First',maximum));assert.doesNotThrow(()=>sum.key({variant:'None'}));
  expect('FIELD_SHAPE',()=>sum.key({variant:'None',payload:null}));expect('FIELD_VALUE_TYPE',()=>sumKey('First',maximum+1n));
  const status=compileFieldReferenceModel(exactFixture()),key=(payload:unknown)=>fieldValueKey(status,'commerce:status',{variant:'Paid',payload});
  assert.equal(key({amount:maximum,currency:'GBP'}),key({amount:maximum.toString(),currency:'GBP'}));
  expect('FIELD_VALUE_TYPE',()=>key({amount:maximum+1n,currency:'GBP'}));
  const wrapped=exactBox(wrap('optional',wrap('list',inline)));
  assert.equal(wrapped.key([{variant:'First',payload:maximum}]),wrapped.key([{variant:'First',payload:maximum.toString()}]));
});

test('PCR-06 exact field values preserve Entity identity Value Object equality and full state validation',()=>{
  const input=exactFixture();property(input,'customer','id').type=scalar('UInt64');property(input,'order','customer_id').type=scalar('UInt64');
  const model=compileFieldReferenceModel(input),key=(selector:string,value:unknown)=>fieldValueKey(model,'commerce:'+selector,value);
  const first={...order(),id:{tenant:'shop',number:maximum},customer:{id:maximum,name:'Alex'},customer_id:maximum,lines:[{amount:maximum,currency:'GBP'}]};
  const same={...first,id:{tenant:'shop',number:maximum.toString()},customer:{id:0,name:'Changed'},customer_id:0,lines:[]};
  assert.equal(key('order',first),key('order',same));assert.notEqual(key('order',first),key('order',{...first,id:{tenant:'shop',number:maximum-1n}}));
  assert.notEqual(key('order',first),key('order',{...first,id:{tenant:'other',number:maximum}}));
  assert.equal(key('customer',{id:maximum,name:'Alex'}),key('customer',{id:maximum.toString(),name:'Different'}));
  assert.notEqual(key('money',{amount:maximum,currency:'GBP'}),key('money',{amount:maximum,currency:'USD'}));
  expect('FIELD_VALUE_TYPE',()=>key('order',{...first,lines:[{amount:maximum+1n,currency:'GBP'}]}));
  expect('FIELD_VALUE_TYPE',()=>key('order',{...first,customer:{id:maximum+1n,name:'Alex'}}));
  const boxes={...input,declarations:[...input.declarations,{selector:'commerce:box',kind:'Value Object',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'COMMERCE-BOX',properties:[field('value',wrap('set',named('customer')))]},invariant_refs:['commerce:valid-value']}]};
  const withBox=compileFieldReferenceModel(boxes);expect('FIELD_SET_DUPLICATE',()=>fieldValueKey(withBox,'commerce:box',{value:[{id:maximum,name:'A'},{id:maximum.toString(),name:'B'}]}));
});

test('PCR-06 exact field values preserve reference targets projections and no-lookup semantics',()=>{
  const input=exactFixture();property(input,'customer','id').type=scalar('UInt64');property(input,'order','customer_id').type=scalar('UInt64');
  const model=compileFieldReferenceModel(input),plain=compileFieldReferenceModel({...input,bindings:[]});
  const value={...order(),customer:{id:maximum,name:'Alex'},customer_id:maximum-1n};
  assert.doesNotThrow(()=>fieldValueKey(model,'commerce:order',value),'target identity existence is not inferred');
  assert.equal(fieldValueKey(model,'commerce:order',value),fieldValueKey(plain,'commerce:order',value));assert.notEqual(model.model_sha256,plain.model_sha256);
  const wrong=exactFixture();property(wrong,'order','customer_id').type=scalar('UInt64');expect('FIELD_REFERENCE_TYPE',()=>compileFieldReferenceModel(wrong));
  const boundIdentity=exactFixture();boundIdentity.bindings.push({owner:'commerce:customer',field:'id',kind:'field-projection',target:'commerce:order',projection:['customer_name']});expect('FIELD_IDENTITY_BINDING',()=>compileFieldReferenceModel(boundIdentity));
  const cycle=exactFixture();property(cycle,'customer','favorite_order').type=wrap('optional',named('order'));cycle.bindings=[];expect('FIELD_EMBEDDING_CYCLE',()=>compileFieldReferenceModel(cycle));
  const badIdentity=exactFixture();property(badIdentity,'customer','id').type=scalar('Bool');expect('FIELD_IDENTITY_TYPE',()=>compileFieldReferenceModel(badIdentity));
});

test('PCR-06 exact field values reject hostile containers before reading data and do not mutate callers',()=>{
  const numeric=exactBox(scalar('UInt64')),list=exactBox(wrap('list',scalar('UInt64')));let reads=0;
  expect('FIELD_JSON',()=>fieldValueKey(numeric.model,'commerce:box',{get value(){reads++;return 1n;}}));
  const getter=[1n];Object.defineProperty(getter,'0',{enumerable:true,get(){reads++;return 1n;}});expect('FIELD_JSON',()=>list.key(getter));assert.equal(reads,0);
  const hidden={};Object.defineProperty(hidden,'value',{value:1n,enumerable:false});expect('FIELD_JSON',()=>fieldValueKey(numeric.model,'commerce:box',hidden));
  for(const value of [Object.assign([1n],{extra:2n}),new Array(1),Object.setPrototypeOf([1n],{}),Object.assign([1n],{[Symbol('extra')]:2n})])expect('FIELD_JSON',()=>list.key(value));
  const cycle:any={};cycle.value=cycle;expect('FIELD_DEPTH',()=>fieldValueKey(numeric.model,'commerce:box',cycle));
  const value={value:[maximum,'2',0]},copy=structuredClone(value);fieldValueKey(list.model,'commerce:box',value);assert.deepEqual(value,copy);assert.equal(Object.isFrozen(value.value),false);
  assert.doesNotThrow(()=>fieldValueKey(numeric.model,'commerce:box',Object.assign(Object.create(null),{value:maximum})));
  expect('FIELD_EXTRA',()=>fieldValueKey(numeric.model,'commerce:box',{value:1n,extra:2n}));expect('FIELD_JSON',()=>list.key([maximum,undefined]));
});

test('PCR-06 exact field values executable mutants expose precision identity and duplicate collapse',async t=>{
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'exact-field-mutants-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=fs.readFileSync(new URL('../../src/input/field-reference-model.ts',import.meta.url),'utf8')
    .replace("'../typed-operation/contracts.js'",JSON.stringify(fileURLToPath(new URL('../../src/typed-operation/contracts.ts',import.meta.url))))
    .replace("'./source-manifest.js'",JSON.stringify(fileURLToPath(new URL('../../src/input/source-manifest.ts',import.meta.url))));
  const mutations=[
    ['precision',"['UInt64', normalized.toString()]","['UInt64', String(Number(normalized))]"],
    ['identity',"d.kind === 'Entity' ? fields.find","false ? fields.find"],
    ['duplicates',"if (type.kind === 'set' && new Set(keys).size !== keys.length)","if (false)"]
  ];
  for(const [id,before,after] of mutations){assert.ok(source.includes(before!));const file=path.join(temp,id+'.ts');fs.writeFileSync(file,source.replace(before!,after!));
    const changed=await import(pathToFileURL(file).href),model=changed.compileFieldReferenceModel(exactFixture());
    if(id==='precision')assert.equal(changed.fieldValueKey(model,'commerce:money',{amount:maximum,currency:'GBP'}),changed.fieldValueKey(model,'commerce:money',{amount:maximum-1n,currency:'GBP'}),'mutant wrongly equates adjacent maximum values');
    if(id==='identity')assert.notEqual(changed.fieldValueKey(model,'commerce:customer',customer('a','A')),changed.fieldValueKey(model,'commerce:customer',customer('a','B')),'mutant wrongly uses whole-record Entity equality');
    if(id==='duplicates'){const b=exactBox(wrap('set',scalar('UInt64'))),m=changed.compileFieldReferenceModel(b.input);assert.doesNotThrow(()=>changed.fieldValueKey(m,'commerce:box',{value:[2n,'2']}),'mutant wrongly accepts normalized duplicates');}
  }
});
