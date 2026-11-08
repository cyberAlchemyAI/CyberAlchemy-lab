import assert from 'node:assert/strict';
import test from 'node:test';
import {compileDeclarativeFunction,DECLARATIVE_FUNCTION_PROFILE,type DeclarativeFunctionContract,type DeclarativeExpression as E} from '../../src/typed-backend/declarative-function.js';
const path=(...path:string[]):E=>({op:'path',path});
const lit=(value:string|boolean|number|null):E=>({op:'literal',value});
const call=(name:string,...args:E[]):E=>({op:'call',name,args});
function fixture():DeclarativeFunctionContract {return {
 schema_version:DECLARATIVE_FUNCTION_PROFILE,
 records:{Input:{rows:'Row[]'},Row:{id:'String',amount:'UInt64'},Output:{ids:'String[]',unique:'Bool'}},roots:{input:'Input'},calculations:{},
 nodes:[
  {id:'Minimum',kind:'Query',ontology:'TEST-MINIMUM',meaning:'All minimal rows.',binding:'p',source:path('input','rows'),where:call('not',{op:'exists',binding:'q',collection:path('input','rows'),where:call('lt',path('q','amount'),path('p','amount'))}),select:path('p')},
  {id:'Unique',kind:'Rule',ontology:'TEST-UNIQUE',meaning:'Exactly one minimum.',expression:{op:'exactly_one',binding:'p',collection:path('Minimum'),where:lit(true)}},
  {id:'Result',kind:'Mapping',ontology:'TEST-RESULT',meaning:'Observed minimal identities.',target:'Output',fields:{ids:call('sort',call('column',path('Minimum'),lit('id'))),unique:path('Unique')}}
 ],assertions:[],results:[{condition:lit(true),value:path('Result')}],output:'Output'
};}
const load=async(c:DeclarativeFunctionContract)=>import('data:text/javascript;base64,'+Buffer.from(compileDeclarativeFunction(c).source).toString('base64'));
test('DomainSpec emits deterministic exact collection semantics without an AST interpreter',async()=>{
 const c=fixture(),compiled=compileDeclarativeFunction(c);assert.deepEqual(compiled,compileDeclarativeFunction(structuredClone(c)));
 assert.ok(!compiled.source.includes('expression.op'));
 const api=await load(c),min=9007199254740993n;
 assert.deepEqual(api.execute({input:{rows:[{id:'a',amount:min+1n},{id:'b',amount:min}]}},{}),{ids:['b'],unique:true});
 assert.deepEqual(api.execute({input:{rows:[{id:'b',amount:18446744073709551615n},{id:'a',amount:18446744073709551615n}]}},{}),{ids:['a','b'],unique:false});
 assert.deepEqual(api.execute({input:{rows:[]}},{}),{ids:[],unique:false});
});
test('contract validation rejects extra syntax, invalid types, collisions, cycles and unsafe paths',()=>{
 for(const mutate of [
  (c:any)=>c.source='return eval(input)',
  (c:any)=>c.nodes[0].source=path('Minimum'),
  (c:any)=>c.nodes[0].where=lit(1),
  (c:any)=>c.nodes[0].select=path('p','missing'),
  (c:any)=>c.nodes[2].fields.ids=lit('wrong'),
  (c:any)=>c.nodes[2].fields.extra=lit(true),
  (c:any)=>delete c.nodes[2].fields.ids,
  (c:any)=>c.nodes.push(c.nodes[0]),
  (c:any)=>c.nodes[2].fields.ids=path('input','constructor'),
  (c:any)=>c.nodes[1].expression={op:'raw',source:'true'},
  (c:any)=>c.nodes[0].where=call('lt',path('p','amount'),lit(1)),
  (c:any)=>c.nodes[2].fields.ids=call('decimal',lit('1'),lit(19)),
 ]){const c=fixture();mutate(c);assert.throws(()=>compileDeclarativeFunction(c),/DS_DECLARATIVE/);}
});
test('result selection requires exactly one matching case and computes only that value',async()=>{
 const c=fixture();c.results.push({condition:lit(false),value:call('Result')});
 const api=await load(c);assert.deepEqual(api.execute({input:{rows:[]}},{}),{ids:[],unique:false});
 c.results[1]!.condition=lit(true);assert.throws((await load(c)).execute.bind(null,{input:{rows:[]}},{}),/DS_RESULT_CARDINALITY/);
 c.results.forEach(r=>r.condition=lit(false));assert.throws((await load(c)).execute.bind(null,{input:{rows:[]}},{}),/DS_RESULT_CARDINALITY/);
});

test('optional observations preserve results and expose evaluated query decisions',async()=>{
 const c=fixture(),api=await load(c),rows=[{id:'a',amount:9007199254740994n},{id:'b',amount:9007199254740993n}],events:any[]=[];
 const ordinary=api.execute({input:{rows}},{}),traced=api.execute({input:{rows}},{},(e:any)=>events.push(e));assert.deepEqual(traced,ordinary);
 assert.deepEqual(events.filter(e=>e.kind==='query-row').map(e=>[e.index,e.accepted]),[[0,false],[1,true]]);
 assert.equal(events.filter(e=>e.kind==='node-start'&&e.declaration==='Minimum').length,1);
 assert.ok(events.some(e=>e.kind==='node-result'&&e.declaration==='Unique'&&e.value===true));
 assert.deepEqual(api.execute({input:{rows}},{},()=>{throw Error('observer failed');}),ordinary);
 assert.deepEqual(api.execute({input:{rows}},{},(e:any)=>{if(e.row)e.row.amount=0n;if(e.value&&Array.isArray(e.value.ids))e.value.ids.push('injected');}),ordinary);
 assert.equal(rows[0]!.amount,9007199254740994n);
});


test('first selects a scalar list head and rejects empty lists or scalar input',async()=>{
 const c:DeclarativeFunctionContract={schema_version:DECLARATIVE_FUNCTION_PROFILE,records:{Input:{ids:'String[]'},Output:{id:'String'}},roots:{input:'Input'},calculations:{},nodes:[{id:'Result',kind:'Mapping',ontology:'TEST-FIRST',meaning:'Select the sorted first identifier.',target:'Output',fields:{id:call('first',call('sort',path('input','ids')))}}],assertions:[],results:[{condition:lit(true),value:path('Result')}],output:'Output'};
 const api=await load(c);
 assert.deepEqual(api.execute({input:{ids:['b','a']}},{}),{id:'a'});
 assert.deepEqual(api.execute({input:{ids:['a']}},{}),{id:'a'});
 assert.throws(()=>api.execute({input:{ids:[]}},{}),/DS_QUERY_EMPTY/);
 const invalid=structuredClone(c);(invalid.nodes[0] as any).fields.id=call('first',lit('abc'));
 assert.throws(()=>compileDeclarativeFunction(invalid));
});
