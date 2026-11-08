import test from 'node:test';
import assert from 'node:assert/strict';
import {compileDeclarativeFunction,type DeclarativeFunctionContract as C,type DeclarativeExpression as E} from '../../src/typed-backend/declarative-function.js';
const p=(...path:string[]):E=>({op:'path',path}),lit=(value:string|boolean):E=>({op:'literal',value}),call=(name:string,...args:E[]):E=>({op:'call',name,args});
function fixture():C{return {schema_version:'domainspec.declarative-function/v1',records:{Input:{ok:'Bool'},Price:{ok:'Bool'},Ship:{ok:'Bool'},Output:{ok:'Bool'}},roots:{input:'Input',pricing:'Price',shipping:'Ship'},calculations:{},bindings:[{name:'pricing'},{name:'shipping',condition:p('HasPrice')}],nodes:[
 {id:'HasPrice',kind:'Rule',ontology:'TEST-PRICE',meaning:'Usable price.',expression:p('pricing','ok')},
 {id:'Quoted',kind:'Rule',ontology:'TEST-QUOTED',meaning:'Both quotes.',expression:call('and',p('HasPrice'),p('shipping','ok'))},
 {id:'Yes',kind:'Mapping',ontology:'TEST-YES',meaning:'Shipping answer.',target:'Output',fields:{ok:p('shipping','ok')}},
 {id:'No',kind:'Mapping',ontology:'TEST-NO',meaning:'No price.',target:'Output',fields:{ok:lit(false)}}],assertions:[],results:[{condition:p('Quoted'),value:p('Yes')},{condition:call('not',p('HasPrice')),value:p('No')}],output:'Output'};}
test('guards compile as generated predicates; named rule implication protects selected mappings',async()=>{
 const c=fixture(),compiled=compileDeclarativeFunction(c),api=await import('data:text/javascript;base64,'+Buffer.from(compiled.source).toString('base64'));
 assert.equal(api.execute({input:{ok:true},pricing:{ok:false}},{},undefined,'shipping'),false);
 assert.deepEqual(api.execute({input:{ok:true},pricing:{ok:false}},{}),{ok:false});
 assert.equal(api.execute({input:{ok:true},pricing:{ok:true}},{},undefined,'shipping'),true);
 assert.deepEqual(api.execute({input:{ok:true},pricing:{ok:true},shipping:{ok:true}},{}),{ok:true});
 assert.deepEqual((compiled.trace as any).bindings,c.bindings);
});
test('unsafe reads, forward binding dependencies and invalid guards fail at compilation',()=>{
 for(const mutate of [
  (c:C)=>c.nodes[1]!.expression=p('shipping','ok'),
  (c:C)=>c.nodes[1]!.expression=call('and',p('shipping','ok'),p('HasPrice')),
  (c:C)=>c.nodes[1]!.expression=call('or',p('HasPrice'),p('shipping','ok')),
  (c:C)=>c.results[1]!.value=p('Yes'),
  (c:C)=>c.assertions.push({condition:p('shipping','ok'),code:'UNSAFE'}),
  (c:C)=>c.bindings![0]!.condition=p('shipping','ok'),
  (c:C)=>c.bindings!.reverse(),
  (c:C)=>c.nodes[0]!.expression=p('Quoted'),
  (c:C)=>c.bindings![1]!.condition=lit('true'),
  (c:C)=>c.bindings![1]!.condition=null as any,
  (c:C)=>c.bindings!.pop(),
 ]){const c=fixture();mutate(c);assert.throws(()=>compileDeclarativeFunction(c),/DS_DECLARATIVE/);}
});
test('short circuit implication supports assertion disjunction, nested guards and quantifiers',()=>{
 const c=fixture();c.assertions.push({condition:call('or',call('not',p('HasPrice')),p('shipping','ok')),code:'SHIPPING_INVALID'});
 c.records.Input!.rows='Ship[]';c.nodes[1]!.expression=call('and',p('HasPrice'),{op:'forall',binding:'row',collection:p('input','rows'),where:call('eq',p('row','ok'),p('shipping','ok'))});
 compileDeclarativeFunction(c);
 c.bindings!.push({name:'final',condition:p('Quoted')});c.roots.final='Ship';c.results[0]!.value=p('final');c.output='Ship';c.nodes[3]!.target='Ship';compileDeclarativeFunction(c);
 c.bindings![2]!.condition=p('shipping','ok');assert.throws(()=>compileDeclarativeFunction(c),/unguarded binding output/);
});
test('guard errors propagate instead of being treated as false',async()=>{
 const c=fixture();c.records.Input!.amount='String';c.nodes[0]!.expression=call('eq',call('uint64',p('input','amount')),call('uint64',lit('1')));
 const api=await import('data:text/javascript;base64,'+Buffer.from(compileDeclarativeFunction(c).source).toString('base64'));
 assert.throws(()=>api.execute({input:{ok:true,amount:'invalid'}},{},undefined,'shipping'),/FUNCTION_UINT64/);
});

test('typed input mappings compile separately and inherit only their own binding guard',async()=>{
 const c=fixture();c.nodes.push({id:'ShippingInput',kind:'Mapping',ontology:'TEST-SHIPPING-INPUT',meaning:'Create a shipping argument.',target:'Ship',fields:{ok:p('pricing','ok')}});c.bindings![1]!.input={mapping:'ShippingInput',type:'Ship'};
 const compiled=compileDeclarativeFunction(c),api=await import('data:text/javascript;base64,'+Buffer.from(compiled.source).toString('base64'));
 assert.deepEqual(api.execute({input:{ok:true},pricing:{ok:true}},{},undefined,'shipping','input'),{ok:true});
 for(const mutate of [
  (c:C)=>c.bindings![1]!.input!.type='Output',
  (c:C)=>c.bindings![1]!.input!.mapping='HasPrice',
  (c:C)=>c.bindings![1]!.input!.mapping='Missing',
  (c:C)=>c.nodes.at(-1)!.fields!.ok=p('shipping','ok'),
  (c:C)=>c.nodes.at(-1)!.input={name:'row',type:'Price'},
  (c:C)=>{c.bindings![0]!.condition=p('input','ok');},
 ]){const changed=structuredClone(c);mutate(changed);assert.throws(()=>compileDeclarativeFunction(changed),/DS_DECLARATIVE/);}
 const unconditional=structuredClone(c);delete unconditional.bindings![1]!.condition;compileDeclarativeFunction(unconditional);
 c.bindings![0]!.condition=p('input','ok');c.bindings![1]!.condition=call('and',p('input','ok'),p('HasPrice'));
 // The final result graph must guard pricing too, independently of the input mapping.
 c.nodes[0]!.expression=call('and',p('input','ok'),p('pricing','ok'));
 compileDeclarativeFunction(c);
});
