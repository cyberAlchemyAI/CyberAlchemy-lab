/** Typed native callsite obligations only. No live native/context is acquired.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {reconstructCoreCommerceModule,reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.js';
import {coreSourceChild,CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {parseCoreExpressionValue} from '../../src/commerce/commerce-core-expression.js';
import {createCoreValueTypes,CORE_BOOL,CORE_UINT64,type CoreValueType} from '../../src/commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../../src/commerce/commerce-core-context.js';
import {createCoreFlowExpressionChecker,type CoreFlowScope} from '../../src/commerce/commerce-core-flow-expression.js';
const source=`module Demo version 1
value-object Item:
  count UInt64
value-object Holder:
  item optional<Item>
enum Choice:
  variant Found value Item
  variant Missing key UInt64
interface Native:
  kind native-producer
  abi craft.fixture-native/v1-candidate
  custody private-registered-source-profile-callsite
  signatures context.json#/identity_producers/methods
interface Application:
  kind application-composition
  source events/model.alch
  formal-claims optional
`;
const events='module Demo.Events version 1\nvalue-object Metadata:\n  count UInt64\nevent Happened:\n  version 1\n  count UInt64\nenum CancellationReason:\n  value Changed\n';
const native={source_module:'Demo@1',identity_producers:{abi:'craft.fixture-native/v1-candidate',service_ids:['demo'],command_namespaces:['demo.run'],methods:{allowed:{parameters:['UInt64'],result:'Bool'},clockEpochMs:{parameters:[],result:'UInt64'},mix:{parameters:[{name:'first',type:'UInt64'},{name:'second',type:'Bool'}],result:'UInt64'},service:{parameters:['ServiceId'],result:'UInt64'},command:{parameters:['CommandNamespace'],result:'UInt64'},stock:{parameters:['StockCommandKindName'],result:'UInt64',kind_values:['reserve','release']},event:{parameters:['selected-schema:Demo.Events.Event@1'],result:'UInt64'},metadata:{parameters:['UInt64'],result:'schema:Demo.Events.Metadata@1'},late:{parameters:['optional<CancellationReason>'],result:'Bool'}}}};
const setup=(value=native)=>{
 const r=reconstructCoreCommerceSources([{path:'application.alch',text:source},{path:'events/model.alch',text:events}]),types=createCoreValueTypes(r),catalog=createCoreContextCatalog(types,[{path:'context.json',text:JSON.stringify(value)}]),context=catalog.require(types.resolve('Demo','Native',r.modules[0]!.syntax)),checker=createCoreFlowExpressionChecker(types,catalog);
 const env=new Map<string,CoreValueType>([['items',{kind:'List',value:{kind:'record',name:'Demo.Item'},maximum:10}],['item',{kind:'record',name:'Demo.Item'}],['holder',{kind:'record',name:'Demo.Holder'}],['choice',{kind:'enum',name:'Demo.Choice'}],['event',{kind:'record',name:'Demo.Events.Happened'}]]),scope:CoreFlowScope={module:'Demo',env,contexts:new Map([['native',context]])};
 return {checker,scope,types,catalog,context};
};
const expression=(value:string)=>{const m=reconstructCoreCommerceModule(`module Expression version 1\ncalculation Probe:\n  pure\n  result Bool\n  expression ${value}\n`,'expression.alch');return parseCoreExpressionValue(coreSourceChild(m.declarations[0]!.syntax,'expression-value'));};
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(error:unknown)=>error instanceof CoreCommerceSourceError&&(!code||error.diagnostics[0]!.code===code));
test('native result is a typed source requirement with no real native custody',()=>{const f=setup(),r=f.checker.check(expression('native.allowed(1)'),f.scope,CORE_BOOL);assert.equal(r.native_calls.length,1);assert.equal(r.native_calls[0]!.result.kind,'Bool');assert.equal(r.native_calls[0]!.custody,'required-from-original-native-owner');assert.equal(r.source.kind,'invoke');assert.equal(Object.hasOwn(r,'native_owner'),false);});
test('native short-circuit callsites are retained and never described as an eager prelude',()=>{const f=setup(),r=f.checker.check(expression('true or native.allowed(1)'),f.scope,CORE_BOOL);assert.equal(r.expression.op,'binary');assert.equal(r.source.kind,'binary');if(r.source.kind==='binary')assert.equal(r.source.right.kind,'invoke');assert.equal(r.native_calls[0]!.placement,'original-source-expression-callsite');});
test('nested native calls keep their own argument expression facets and order',()=>{const f=setup(),r=f.checker.check(expression('native.allowed(native.clockEpochMs())'),f.scope,CORE_BOOL);assert.equal(r.native_calls[0]!.method,'allowed');assert.equal(r.native_calls[0]!.arguments[0]!.value.native_calls[0]!.method,'clockEpochMs');});
test('named native arguments retain source order with exact parameter identities',()=>{const f=setup(),r=f.checker.check(expression('native.mix(second=true,first=1)'),f.scope,CORE_UINT64);assert.deepEqual(r.native_calls[0]!.arguments.map(a=>a.parameter),['second','first']);});
test('finite native text annotations come from exact selected contract arrays',()=>{const f=setup();for(const e of ['native.service("demo")','native.command("demo.run")','native.stock("reserve")']){const r=f.checker.check(expression(e),f.scope,CORE_UINT64);assert.ok(r.native_calls[0]!.arguments[0]!.allowed_text!.length);}});
test('selected Event annotation requires actual closed Event in the declared module',()=>{const f=setup(),r=f.checker.check(expression('native.event(event)'),f.scope,CORE_UINT64);assert.equal(r.native_calls[0]!.arguments[0]!.value.type.kind,'record');failure(()=>f.checker.check(expression('native.event(item)'),f.scope),'TypeMismatch');});
test('explicit schema result type resolves exact module/version',()=>{const f=setup(),r=f.checker.check(expression('native.metadata(1).count'),f.scope,CORE_UINT64);assert.equal(r.expression.op,'field');assert.deepEqual(r.native_calls[0]!.result,{kind:'record',name:'Demo.Events.Metadata'});});
test('native calls under map binders use actual item types',()=>{const f=setup(),scope={...f.scope,env:new Map([...f.scope.env].filter(([n])=>n!=='item'))},r=f.checker.check(expression('map(items,item:Item => native.allowed(item.count))'),scope,{kind:'List',value:CORE_BOOL,maximum:10});assert.equal(r.source.kind,'map');assert.equal(r.native_calls[0]!.arguments[0]!.value.type.kind,'UInt64');});
test('native sort keys retain their per-item source location and numeric type',()=>{const f=setup(),scope={...f.scope,env:new Map([...f.scope.env].filter(([n])=>n!=='item'))},r=f.checker.check(expression('sort(items,item:Item => [native.clockEpochMs() ascending numeric])'),scope);assert.equal(r.source.kind,'sort');assert.equal(r.native_calls.length,1);assert.equal(r.native_calls[0]!.placement,'original-source-expression-callsite');});
test('native calls in optional payload branches see only the actual narrowed binder',()=>{const f=setup(),r=f.checker.check(expression('match holder.item some(found) => native.allowed(found.count) else false'),f.scope,CORE_BOOL);assert.equal(r.native_calls[0]!.arguments[0]!.value.type.kind,'UInt64');});
test('native arguments receive only valid short-circuit optional narrowing',()=>{const f=setup();for(const e of ['present(holder.item) and native.allowed(holder.item.count)','absent(holder.item) or native.allowed(holder.item.count)','match present(holder.item) true => native.allowed(holder.item.count) else false'])assert.equal(f.checker.check(expression(e),f.scope,CORE_BOOL).type.kind,'Bool');failure(()=>f.checker.check(expression('present(holder.item) or native.allowed(holder.item.count)'),f.scope),'TypeMismatch');});
test('grouped enum native calls are independently checked per actual payload',()=>{const f=setup();failure(()=>f.checker.check(expression('match choice Found(value), Missing(value) => native.allowed(value.count) else false'),f.scope),'TypeMismatch');});
test('generated native binding cannot capture an authored unresolved variable',()=>{const f=setup();failure(()=>f.checker.check(expression('native.clockEpochMs() + core_native_result_1'),f.scope),'UnknownReference');});
test('source-local read-set record facets can be typed without adding a new meta-type',()=>{const f=setup(),type=f.checker.registerRecord('Demo.LocalRows',[{name:'count',type:CORE_UINT64}],{path:'application.alch',start:0,end:0}),scope={...f.scope,env:new Map([...f.scope.env,['row',type]as const])};assert.equal(f.checker.check(expression('row.count'),scope,CORE_UINT64).type.kind,'UInt64');failure(()=>f.checker.registerRecord('Demo.Item',[],{path:'application.alch',start:0,end:0}),'DuplicateSymbol');});
test('a failed source expression does not poison the reusable component checker',()=>{const f=setup();failure(()=>f.checker.check(expression('native.allowed(true)'),f.scope),'TypeMismatch');assert.equal(f.checker.check(expression('native.allowed(1)'),f.scope,CORE_BOOL).type.kind,'Bool');});
for(const [name,value,code]of [
 ['unknown method','native.missing()','UnknownReference'],['wrong arity','native.allowed()','MissingMapping'],['wrong parameter','native.mix(unknown=1,second=true)','UnknownReference'],['duplicate named parameter','native.mix(first=1,first=2)','MissingMapping'],['native Bool as arithmetic','native.allowed(1) + 2','TypeMismatch'],['bad finite service','native.service("other")','InvalidContract'],['bad finite command namespace','native.command("other.run")','InvalidContract'],['bad finite action kind','native.stock("allocate")','InvalidContract'],['unresolved late type cannot use a globally unique enum fallback','native.late(none)','UnknownReference'],
]as const)test('rejects '+name,()=>{const f=setup();failure(()=>f.checker.check(expression(value),f.scope),code);});
test('late annotation works only after an explicit exact schema binding is provided',()=>{const copy=JSON.parse(JSON.stringify(native));copy.identity_producers.methods.late.parameters=['optional<Demo.Events.CancellationReason>'];const f=setup(copy);assert.equal(f.checker.check(expression('native.late(none)'),f.scope,CORE_BOOL).type.kind,'Bool');});
test('unknown result schema version is unsupported',()=>{const copy=JSON.parse(JSON.stringify(native));copy.identity_producers.methods.metadata.result='schema:Demo.Events.Metadata@2';const f=setup(copy);failure(()=>f.checker.check(expression('native.metadata(1)'),f.scope),'UnsupportedCapability');});
test('unknown selected schema role cannot silently become an Event union',()=>{const copy=JSON.parse(JSON.stringify(native));copy.identity_producers.methods.event.parameters=['selected-schema:Demo.Events.Item@1'];const f=setup(copy);failure(()=>f.checker.check(expression('native.event(event)'),f.scope),'UnsupportedCapability');});
test('native ABI mismatch cannot be disguised by a method signature',()=>{const copy=JSON.parse(JSON.stringify(native));copy.identity_producers.methods.allowed.abi='craft.foreign/v1';failure(()=>setup(copy),'InvalidContract');});
test('unknown source_module never resolves against globally unique type names',()=>{const copy=JSON.parse(JSON.stringify(native));copy.source_module='Missing@1';failure(()=>setup(copy),'UnknownReference');});
test('duplicate or omitted signature parameters reject',()=>{const copy=JSON.parse(JSON.stringify(native));copy.identity_producers.methods.mix.parameters=[{name:'same',type:'UInt64'},{name:'same',type:'Bool'}];failure(()=>setup(copy),'InvalidContract');});
