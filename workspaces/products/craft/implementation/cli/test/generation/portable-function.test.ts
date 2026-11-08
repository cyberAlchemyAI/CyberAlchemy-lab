import test from 'node:test';
import assert from 'node:assert/strict';
import {portablePattern,validatePortableSource} from '../../src/typed-backend/portable-function.js';
test('portable regex grammar excludes host dependent and unbounded features',()=>{
 for(const pattern of ['^[a-z]{3}$','^[A-Za-z]{3}$','^(quoted|no_price|ambiguous_price)$','^[0-9]{1,18}$'])assert.equal(portablePattern(pattern),true,pattern);
 for(const pattern of ['[a-z]','^.*$','^\\w+$','^(?=a)a$','^(a+)+$','^[a-z]{1001}$','^a{3,1}$','^a|$','^[z-a]$'])assert.equal(portablePattern(pattern),false,pattern);
});
test('nonportable Rust rejection carries field source and portable literals reject unpaired surrogates',()=>{
 const source:any={model:{endpoint:{target:'rust-http'},schemas:{Input:{id:{pattern:'^\\w+$'}}}},ontology:{source:{path:'/fixture.alch'},nodes:[{name:'Input',source:{line:4},properties:[{name:'id',line:7}]}]},contract:{}};
 assert.throws(()=>validatePortableSource(source),/\/fixture.alch:7: Input.id: unsupported Rust pattern/);
 source.model.schemas={};source.model.portability='node-rust-v1';source.contract={literal:'\ud800'};assert.throws(()=>validatePortableSource(source),/unpaired Unicode surrogate/);
});

import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.js';
test('numeric grammar rejects trailing line terminators and observations retain calculation failures',async()=>{
 const lit=(value:any)=>({op:'literal',value}),call=(name:string,...args:any[])=>({op:'call',name,args});
 const contract:any={schema_version:'domainspec.declarative-function/v1',portability:'node-rust-v1',records:{Input:{},Output:{amount:'String'}},roots:{input:'Input'},calculations:{Amount:['a','b']},nodes:[{id:'Response',kind:'Mapping',ontology:'TEST-RESPONSE',meaning:'Exact amount.',target:'Output',fields:{amount:call('text',call('Amount',call('uint64',lit('1')),call('uint64',lit('2'))))}}],assertions:[],results:[{condition:lit(true),value:{op:'path',path:['Response']}}],output:'Output'};
 const load=async()=>import('data:text/javascript;base64,'+Buffer.from(compileDeclarativeFunction(contract).source).toString('base64'));
 const api=await load();
 for(const code of ['CALCULATION_UNDERFLOW','CALCULATION_DIVIDE_BY_ZERO','CALCULATION_INEXACT','CALCULATION_OVERFLOW']){const events:any[]=[];assert.throws(()=>(/* generated */api).execute({input:{}},{evaluateCalculation(){throw Error(code);}},(e:any)=>events.push(e)),new RegExp(code));assert.ok(events.some(e=>e.kind==='node-error'&&e.node_kind==='Calculation'&&e.code===code));}
 for(const [name,code]of [['decimal','FUNCTION_DECIMAL'],['uint64','FUNCTION_UINT64']])for(const suffix of ['\n','\r','\u2028','\u2029']){contract.nodes[0].fields.amount=call('text',call(name,lit('1'+suffix),...(name==='decimal'?[lit(2)]:[])));const generated=await load();assert.throws(()=>generated.execute({input:{}},{}),new RegExp(code));}
});

test('calculation arguments fail before the invocation observation begins',async()=>{
 const lit=(value:any)=>({op:'literal',value}),call=(name:string,...args:any[])=>({op:'call',name,args});
 const contract:any={schema_version:'domainspec.declarative-function/v1',portability:'node-rust-v1',records:{Input:{},Output:{amount:'String'}},roots:{input:'Input'},calculations:{Amount:['a']},nodes:[{id:'Response',kind:'Mapping',ontology:'TEST-RESPONSE',meaning:'Exact amount.',target:'Output',fields:{amount:call('text',call('Amount',call('uint64',lit('-1'))))}}],assertions:[],results:[{condition:lit(true),value:{op:'path',path:['Response']}}],output:'Output'};
 const api=await import('data:text/javascript;base64,'+Buffer.from(compileDeclarativeFunction(contract).source).toString('base64')),events:any[]=[];
 assert.throws(()=>api.execute({input:{}},{evaluateCalculation(){assert.fail('invalid argument must prevent call');}},(e:any)=>events.push(e)),/FUNCTION_UINT64/);
 assert.equal(events.some(e=>e.node_kind==='Calculation'),false);
});
