/** Tests source-positioned typed data, not native/runtime execution.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {reconstructCoreCommerceModule,reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.js';
import {parseCoreExpressionValue} from '../../src/commerce/commerce-core-expression.js';
import {coreSourceChild,CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {createCoreValueTypes,CORE_UINT64,CORE_BOOL,type CoreValueType} from '../../src/commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../../src/commerce/commerce-core-context.js';
import {createCoreFlowExpressionChecker,type CoreFlowScope} from '../../src/commerce/commerce-core-flow-expression.js';
import type {CoreFlowEvaluation} from '../../src/commerce/commerce-core-flow-evaluation.js';
const source=`module Demo version 1
value-object Item:
  count UInt64
value-object Pair:
  first UInt64
  second UInt64
enum Choice:
  variant Found item Item
  variant Missing key UInt64
enum PairResult:
  variant Pair first UInt64 second UInt64
calculation Difference:
  pure
  input first UInt64
  input second UInt64
  result UInt64
  expression first - second
interface Native:
  kind native-producer
  abi craft.fixture/v1-candidate
  custody private-registered-source-profile-callsite
  fields context.json#/identity_producers/properties
  signatures context.json#/identity_producers/methods
interface Application:
  kind application-composition
  formal-claims optional
`;
const contract={source_module:'Demo@1',identity_producers:{abi:'craft.fixture/v1-candidate',service_ids:['demo'],properties:{tenantId:'UInt64',item:'optional<Item>'},methods:{first:{parameters:[],result:'UInt64'},second:{parameters:[],result:'UInt64'},allowed:{parameters:['UInt64'],result:'Bool'},maybe:{parameters:[],result:'optional<Item>'},pair:{parameters:[{name:'first',type:'UInt64'},{name:'second',type:'UInt64'}],result:'UInt64'},service:{parameters:['ServiceId'],result:'UInt64'}}}};
const setup=()=>{
 const model=reconstructCoreCommerceSources([{path:'application.alch',text:source}]),types=createCoreValueTypes(model),catalog=createCoreContextCatalog(types,[{path:'context.json',text:JSON.stringify(contract)}]),context=catalog.require(types.resolve('Demo','Native',model.modules[0]!.syntax));
 const checker=createCoreFlowExpressionChecker(types,catalog),env=new Map<string,CoreValueType>([['items',{kind:'List',value:{kind:'record',name:'Demo.Item'},maximum:10}],['choice',{kind:'enum',name:'Demo.Choice'}],['service',{kind:'literal',value:'demo'}]]),scope:CoreFlowScope={module:'Demo',env,contexts:new Map([['native',context]])};
 const parse=(value:string)=>{const module=reconstructCoreCommerceModule(`module Probe version 1\ncalculation Read:\n  pure\n  result UInt64\n  expression ${value}\n`,'probe.alch');return parseCoreExpressionValue(coreSourceChild(module.declarations[0]!.syntax,'expression-value'));};
 return {checker,scope,parse,check:(value:string,expected?:CoreValueType)=>checker.check(parse(value),scope,expected)};
};
const calls=(value:unknown):string[]=>{if(!value||typeof value!=='object')return [];const v=value as Record<string,unknown>;return [...(v.op==='native_observation'?[String(v.method)]:[]),...Object.values(v).flatMap(calls)];};
const native=(value:CoreFlowEvaluation,method:string)=>{assert.equal(value.op,'native_observation');if(value.op!=='native_observation')assert.fail('native observation expected');assert.equal(value.method,method);return value;};
test('native leaves contain no executable owner or free placeholder',()=>{const r=setup().check('native.first()',CORE_UINT64),e=native(r.evaluation,'first');assert.equal(e.custody,'required-from-original-native-owner');assert.equal(e.placement,'original-source-expression-callsite');assert.equal(Object.hasOwn(e,'owner'),false);assert.equal(JSON.stringify(r.evaluation).includes('core_native_result_'),false);assert.ok(Object.isFrozen(e));});
for(const [value,operator]of [['false and native.allowed(1)','and'],['true or native.allowed(1)','or']]as const)test('native short circuit position: '+value,()=>{const e=setup().check(value,CORE_BOOL).evaluation;assert.equal(e.op,'binary');if(e.op==='binary'){assert.equal(e.operator,operator);assert.deepEqual(calls(e.left),[]);assert.deepEqual(calls(e.right),['allowed']);}});
test('Boolean match preserves condition and distinct lazy native alternatives',()=>{const e=setup().check('match native.allowed(1) true => native.first() else native.second()',CORE_UINT64).evaluation;assert.equal(e.op,'if');if(e.op==='if'){native(e.condition,'allowed');native(e.then,'first');native(e.else,'second');}});
test('nested native arguments remain inside the original outer call',()=>{const e=native(setup().check('native.allowed(native.first())',CORE_BOOL).evaluation,'allowed');assert.equal(e.arguments.length,1);native(e.arguments[0]!.value,'first');});
test('native named arguments evaluate in source order with original parameter identities',()=>{const e=native(setup().check('native.pair(second=native.second(),first=native.first())',CORE_UINT64).evaluation,'pair');assert.deepEqual(e.arguments.map(a=>a.parameter),['second','first']);native(e.arguments[0]!.value,'second');native(e.arguments[1]!.value,'first');});
for(const constructor of ['Pair','PairResult.Pair','Difference'])test(constructor+' preserves named constructor or pure-call argument order',()=>{const e=setup().check(`${constructor}(second=native.second(),first=native.first())`).evaluation;assert.equal(e.op,'let');if(e.op==='let'){native(e.value,'second');assert.equal(e.body.op,'let');if(e.body.op==='let'){native(e.body.value,'first');const body=e.body.body;if(body.op==='call')assert.equal(body.declaration,'Demo.Difference');else if(body.op==='record'||body.op==='enum_value')assert.deepEqual(Object.keys(body.fields),['first','second']);else assert.fail('ordered construction expected');}}});
test('optional native match subject is captured once and payload call stays guarded',()=>{const e=setup().check('match native.maybe() some(found) => native.allowed(found.count) else false',CORE_BOOL).evaluation;assert.equal(e.op,'let');if(e.op==='let'){native(e.value,'maybe');assert.equal(e.body.op,'if');if(e.body.op==='if'){assert.deepEqual(calls(e.body.else),[]);assert.deepEqual(calls(e.body.then),['allowed']);}}assert.equal(calls(e).filter(x=>x==='maybe').length,1);});
test('enum payload observations remain in their matching branch',()=>{const e=setup().check('match choice Found(found) => native.allowed(found.count) else false',CORE_BOOL).evaluation;assert.equal(e.op,'match_variant');if(e.op==='match_variant'){assert.equal(e.cases[0]!.variant,'Found');assert.equal(e.cases[0]!.binding,'found');native(e.cases[0]!.then,'allowed');assert.deepEqual(calls(e.otherwise),[]);}});
for(const [value,op,child]of [
 ['map(items,item:Item => native.allowed(item.count))','map','body'],
 ['filter(items,item:Item => native.allowed(item.count))','filter','predicate'],
 ['fold(items,0,total:UInt64,item:Item => total + native.first())','fold','body'],
 ['indexed-fold(items,0,total:UInt64,item:Item,index:UInt64 => total + native.first())','indexed_fold','body'],
 ['repeat(2,max 10,0,total:UInt64,index:UInt64 => total + native.first())','repeat','body'],
 ['while-bounded(max 10,0,total:UInt64,native.allowed(total) => total + native.first())','while_bounded','guard'],
 ['until-bounded(max 10,0,total:UInt64,native.allowed(total) => total + native.first())','until_bounded','guard'],
]as const)test(op+' preserves observation inside its checked iteration scope',()=>{const e=setup().check(value).evaluation;assert.equal(e.op,op);assert.ok(calls((e as unknown as Record<string,unknown>)[child]).length>0);assert.deepEqual(calls((e as unknown as Record<string,unknown>).source),[]);});
test('sort-key observation remains under the selected item binder',()=>{const e=setup().check('sort(items,item:Item => [native.pair(first=item.count,second=0) descending numeric])').evaluation;assert.equal(e.op,'sort');if(e.op==='sort'){assert.equal(e.item.name,'item');assert.equal(e.keys[0]!.mode,'numeric');native(e.keys[0]!.value,'pair');assert.deepEqual(calls(e.source),[]);}});
test('finite native text domain remains attached to its exact argument',()=>{const e=native(setup().check('native.service(service)',CORE_UINT64).evaluation,'service');assert.deepEqual(e.arguments[0]!.allowed_text,['demo']);assert.deepEqual(e.arguments[0]!.value,{op:'var',name:'service'});});
test('private field projection retains exact captured context fields and custody',()=>{const e=setup().check('native.tenantId',CORE_UINT64).evaluation;assert.equal(e.op,'field');if(e.op==='field'){assert.equal(e.field,'tenantId');assert.equal(e.value.op,'private_context');if(e.value.op==='private_context'){assert.equal(e.value.source_type,'Demo.Native');assert.equal(e.value.public_constructor,false);assert.equal(e.value.custody,'required-from-original-native-owner');assert.deepEqual(e.value.fields.map(f=>f.name),['tenantId','item']);assert.deepEqual(e.value.fields[1]!.type,{kind:'optional',value:{kind:'record',name:'Demo.Item'}});}}});
test('reachable nested source-local records retain fields without leaking unrelated records',()=>{const f=setup(),where={path:'application.alch',start:0,end:0},child=f.checker.registerRecord('Demo.PrivateChild',[{name:'version',type:CORE_UINT64}],where),root=f.checker.registerRecord('Demo.PrivateRoot',[{name:'child',type:{kind:'optional',value:child}}],where);f.checker.registerRecord('Demo.Unrelated',[{name:'secret',type:CORE_BOOL}],where);const env=new Map([...f.scope.env,['row',root]as const]),r=f.checker.check(f.parse('row'),{...f.scope,env});assert.deepEqual(r.local_records.map(r=>r.name),['Demo.PrivateChild','Demo.PrivateRoot']);assert.ok(r.local_records.every(r=>r.public_constructor===false));assert.deepEqual(r.local_records[0]!.fields,[{name:'version',type:CORE_UINT64}]);});
test('local projection requirements survive nested native argument checking',()=>{const f=setup(),where={path:'application.alch',start:0,end:0},row=f.checker.registerRecord('Demo.PrivateRow',[{name:'count',type:CORE_UINT64}],where),env=new Map([...f.scope.env,['row',row]as const]),r=f.checker.check(f.parse('native.allowed(row.count)'),{...f.scope,env},CORE_BOOL);native(r.evaluation,'allowed');assert.deepEqual(r.local_records.map(r=>r.name),['Demo.PrivateRow']);});
test('unknown private fields still reject before evaluation data is emitted',()=>{assert.throws(()=>setup().check('native.missing'),(e:unknown)=>e instanceof CoreCommerceSourceError&&e.diagnostics[0]!.code==='UnknownReference');});
