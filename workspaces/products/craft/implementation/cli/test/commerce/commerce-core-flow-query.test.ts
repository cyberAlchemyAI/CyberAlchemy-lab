/** Source read-role checks, not native storage/provider/entry execution.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {checkCoreCommerceQuerySources,checkCoreCommerceQueryProposal,type CoreQuerySemantics} from '../../src/commerce/commerce-core-flow-query.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const model=`module Demo version 1
entity Item:
  id UInt64
  tenant UInt64
  count UInt64
  version UInt64
  identity id
entity Details:
  itemId UInt64
  amount UInt64
  identity itemId
value-object View:
  id UInt64
  count UInt64
mapping ToView:
  input item Item
  target View
  total true
  field id <- item.id
  field count <- item.count
interface Customer:
  kind trusted-context
  abi craft.fixture-context/v1-candidate
  fields context.json#/contexts/Customer/properties
  methods context.json#/contexts/Customer/methods
  serializable false
  public-constructor forbidden
interface Application:
  kind application-composition
  service demo module Demo
  formal-claims optional
`;
const contract={source_module:'Demo@1',contexts:{Customer:{abi:'craft.fixture-context/v1-candidate',serializable:false,public_constructor:false,properties:{tenantId:'UInt64',currentActionAllowed:'Bool'},methods:{allowed:{parameters:['UInt64'],result:'Bool'}}}}};
const assets=(value=contract)=>[{path:'context.json',text:JSON.stringify(value)}];
const query=`
query Read:
  input id UInt64
  context customer Customer
  source item Item
  output optional<View>
  where item.id == id and item.tenant == customer.tenantId and customer.allowed(item.id)
  project ToView(item)
  on-missing return none
  on-unavailable fail read-unavailable
`;
const sources=(extra=query,base=model)=>[{path:'application.alch',text:base+extra}];
const check=(extra=query,base=model,a=assets())=>checkCoreCommerceQuerySources(sources(extra,base),a);
const local=(q:CoreQuerySemantics)=>{assert.equal(q.kind,'local');if(q.kind!=='local')assert.fail('local Query expected');return q;};
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(error:unknown)=>error instanceof CoreCommerceSourceError&&(!code||error.diagnostics[0]!.code===code));
test('all 13 original commerce queries independently reconstruct from original Core capture',()=>{
 const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),owner=createCoreCommerceSourceOwner(),h=owner.prepare(root),capture=owner.inspect(h),paths=new Set(capture.reconstruction.modules.map(m=>m.path));
 const data=checkCoreCommerceQuerySources(capture.files.filter(f=>paths.has(f.path)),capture.files.filter(f=>f.path.endsWith('.json')));owner.assertCurrent(h);
 assert.equal(data.queries.length,13);assert.equal(data.queries.filter(q=>q.kind==='local').length,9);assert.equal(data.queries.filter(q=>q.kind==='delegated').length,3);assert.equal(data.queries.filter(q=>q.kind==='native-protocol').length,1);assert.ok(data.queries.every(q=>q.effects==='none'&&q.qualification==='typed-query-source-only'));
 const snapshot=local(data.queries.find(q=>q.name==='Orders.ReadCheckoutSnapshot')!);assert.equal(snapshot.sources.length,2);assert.deepEqual(snapshot.sources.map(s=>s.lookup_key),[['id'],['orderId']]);assert.equal(snapshot.predicate.native_calls[0]!.method,'isOrdersWorker');assert.equal(snapshot.predicate.native_calls[0]!.custody,'required-from-original-native-owner');owner.dispose(h);
});
test('single-key local read retains checked projection, default cardinality and optional wrapping',()=>{const q=local(check().queries[0]!);assert.deepEqual(q.sources[0]!.lookup_key,['id']);assert.equal(q.max_rows,4096);assert.equal(q.wrap_projection_some,true);assert.equal(q.projection.expression.op,'call');assert.equal(q.on_missing.kind,'return');assert.equal(q.on_unavailable.kind,'fail');});
test('native source observations remain positioned at their original expression callsite',()=>{const q=local(check().queries[0]!),call=q.predicate.native_calls[0]!;assert.equal(call.placement,'original-source-expression-callsite');assert.equal(call.context,'customer');assert.equal(call.source_type,'Demo.Customer');assert.equal(call.result.kind,'Bool');assert.equal(call.arguments[0]!.value.type.kind,'UInt64');assert.equal(q.predicate.source.kind,'binary');assert.equal(q.predicate.qualification,'typed-source-expression-only');});
test('source-only context is recorded as an original-owner requirement, never a grant',()=>{const q=local(check().queries[0]!);assert.deepEqual(q.contexts,[{binding:'customer',source_type:'Demo.Customer',abi:'craft.fixture-context/v1-candidate'}]);assert.equal(Object.hasOwn(q,'accepted'),false);assert.equal(Object.hasOwn(q,'native_owner'),false);});
test('a Query may use a declared unique key instead of primary identity',()=>{const q=local(check(query.replace('item.id == id','item.tenant == id'),model.replace('  identity id','  identity id\n  unique tenant')).queries[0]!);assert.deepEqual(q.sources[0]!.lookup_key,['tenant']);});
test('a complete compound primary key is required',()=>{const compound=model.replace('  identity id','  identity id, tenant'),q=local(check(query,compound).queries[0]!);assert.deepEqual(q.sources[0]!.lookup_key,['id','tenant']);failure(()=>check(query.replace(' and item.tenant == customer.tenantId',''),compound),'InvalidContract');});
test('join keys propagate from the actual keyed row and retain typed join predicates',()=>{const extra=query.replace('source item Item','source item Item join details Details on details.itemId == item.id').replace('project ToView(item)','project View(item.id,details.amount)'),q=local(check(extra).queries[0]!);assert.equal(q.sources.length,2);assert.deepEqual(q.sources[1]!.lookup_key,['itemId']);assert.equal(q.sources[1]!.join!.type.kind,'Bool');});
test('source whitespace changes capture facets but preserves executable Query subject',()=>{const first=check(),second=check(query.replace('item.id == id','item.id  ==  id'),model+'\n# extra comment\n');assert.equal(first.query_subject_sha256,second.query_subject_sha256);assert.notEqual(first.source_facet_sha256,second.source_facet_sha256);});
test('Query subject binds the independent pure dependency closure',()=>{assert.notEqual(check().query_subject_sha256,check(query,model.replace('field count <- item.count','field count <- item.count + 1')).query_subject_sha256);});
test('Query subject changes when tenant scope, result, handler or lookup changes',()=>{const first=check().query_subject_sha256;for(const extra of [query.replace(' and item.tenant == customer.tenantId',''),query.replace('fail read-unavailable','fail outcome-unknown'),query.replace('project ToView(item)','project View(item.id,0)')])assert.notEqual(check(extra).query_subject_sha256,first);});
test('an explicitly optional projection is not wrapped twice',()=>{const q=local(check(query.replace('project ToView(item)','project some(ToView(item))')).queries[0]!);assert.equal(q.wrap_projection_some,false);assert.equal(q.projection.type.kind,'optional');});
test('optional projection and missing defaults remain typed without inventing row data',()=>{const q=local(check(query.replace('  on-missing return none\n','').replace('  on-unavailable fail read-unavailable\n','')).queries[0]!);assert.equal(q.on_missing.kind,'return');assert.deepEqual(q.on_unavailable,{kind:'fail',code:'outcome-unknown'});});
test('require guards have rows on the present path and typed failure actions',()=>{const q=local(check(query.replace('  project ToView(item)','  require item.count > 0 else reject empty-item\n  project ToView(item)')).queries[0]!);assert.equal(q.guards.length,1);assert.equal(q.guards[0]!.condition.type.kind,'Bool');assert.deepEqual(q.guards[0]!.otherwise,{kind:'reject',code:'empty-item'});});
test('delegated Query arguments preserve source order and exact typed forwarding',()=>{const extra=query+'\nquery Wrapper:\n  input id UInt64\n  context customer Customer\n  delegates Read(id=id)\n  output optional<View>\n  effects none\n',d=check(extra).queries.find(q=>q.name==='Demo.Wrapper')!;assert.equal(d.kind,'delegated');if(d.kind==='delegated'){assert.equal(d.target,'Demo.Read');assert.deepEqual(d.forwarded_contexts,[{parameter:'customer',binding:'customer',source_type:'Demo.Customer'}]);}});
for(const [name,extra,base,code] of [
 ['numeric where predicate',query.replace('where item.id == id and item.tenant == customer.tenantId and customer.allowed(item.id)','where 1'),model,'TypeMismatch'],
 ['missing key lookup',query.replace('item.id == id and ',''),model,'InvalidContract'],
 ['self key lookup',query.replace('item.id == id','item.id == item.id'),model,'InvalidContract'],
 ['row-based lookup expression',query.replace('item.id == id','item.id == item.count'),model,'InvalidContract'],
 ['OR lookup is not a declared bounded key set',query.replace('item.id == id and item.tenant == customer.tenantId and customer.allowed(item.id)','item.id == id or item.count == 0'),model,'InvalidContract'],
 ['unknown table field',query.replace('item.tenant','item.missing'),model,'UnknownReference'],
 ['unknown context field',query.replace('customer.tenantId','customer.missing'),model,'UnknownReference'],
 ['unknown private context method',query.replace('customer.allowed','customer.unknown'),model,'UnknownReference'],
 ['wrong native method arity',query.replace('customer.allowed(item.id)','customer.allowed()'),model,'MissingMapping'],
 ['wrong native method argument type',query.replace('customer.allowed(item.id)','customer.allowed(true)'),model,'TypeMismatch'],
 ['native result temporary cannot capture an authored free variable',query.replace('customer.allowed(item.id)','customer.allowed(item.id) and core_native_result_1'),model,'UnknownReference'],
 ['row alias shadows input',query.replace('input id UInt64','input item UInt64'),model,'DuplicateSymbol'],
 ['row alias shadows context',query.replace('context customer Customer','context item Customer').replaceAll('customer.','item.'),model,'DuplicateSymbol'],
 ['duplicate projection',query.replace('  project ToView(item)','  project ToView(item)\n  project ToView(item)'),model,'DuplicateSymbol'],
 ['missing projection',query.replace('  project ToView(item)\n',''),model,'MissingMapping'],
 ['wrong projection type',query.replace('project ToView(item)','project 1'),model,'TypeMismatch'],
 ['missing-row handler cannot read row aliases',query.replace('on-missing return none','on-missing return some(ToView(item))'),model,'UnknownReference'],
 ['unavailable handler cannot project a missing row',query.replace('on-unavailable fail read-unavailable','on-unavailable return some(ToView(item))'),model,'UnknownReference'],
 ['duplicate missing handler',query.replace('  on-missing return none','  on-missing return none\n  on-missing return none'),model,'DuplicateSymbol'],
 ['duplicate unavailable handler',query.replace('  on-unavailable fail read-unavailable','  on-unavailable fail read-unavailable\n  on-unavailable fail outcome-unknown'),model,'DuplicateSymbol'],
 ['nonoptional Query needs an explicit missing action',query.replace('output optional<View>','output View').replace('  on-missing return none\n',''),model,'MissingMapping'],
 ['require condition is Bool',query.replace('  project ToView(item)','  require item.count else reject invalid\n  project ToView(item)'),model,'TypeMismatch'],
 ['require failure return type',query.replace('  project ToView(item)','  require item.count > 0 else return 1\n  project ToView(item)'),model,'TypeMismatch'],
 ['Query cannot invoke an Operation',query.replace('project ToView(item)','project Write(item)'),model+'\noperation Write:\n  input item Item\n  output View\n  return ToView(item)\n','UnsupportedCapability'],
 ['duplicate native Context binding',query.replace('  context customer Customer','  context customer Customer\n  context customer Customer'),model,'DuplicateSymbol'],
 ['context parameter cannot be a data record',query.replace('context customer Customer','context customer View'),model,'TypeMismatch'],
]as const)test('rejects '+name,()=>failure(()=>check(extra,base),code));
test('cross-module private table access cannot become a Query scan',()=>{const s=sources(query.replace('source item Item','source item Other.Secret'));s.push({path:'other.alch',text:'module Other version 1\nentity Secret:\n  id UInt64\n  tenant UInt64\n  count UInt64\n  identity id\n'});failure(()=>checkCoreCommerceQuerySources(s,assets()),'InvalidContract');});
test('unknown captured signature assets reject rather than inventing private fields',()=>failure(()=>check(query,model,[]),'UnknownReference'));
test('source context ABI and captured signature ABI must agree',()=>{const copy=JSON.parse(JSON.stringify(contract));copy.contexts.Customer.abi='craft.other-context/v1-candidate';failure(()=>check(query,model,assets(copy)),'InvalidContract');});
test('captured context cannot switch to public serialization or construction',()=>{for(const key of ['serializable','public_constructor']){const copy=JSON.parse(JSON.stringify(contract));copy.contexts.Customer[key]=true;failure(()=>check(query,model,assets(copy)),'InvalidContract');}});
test('private source context cannot become a Query return type',()=>failure(()=>check(query.replace('output optional<View>','output Customer').replace('project ToView(item)','project customer')),'TypeMismatch'));
test('native context method label Bool cannot override its actual captured return type',()=>{const copy=JSON.parse(JSON.stringify(contract));copy.contexts.Customer.methods.allowed.result='UInt64';failure(()=>check(query,model,assets(copy)),'TypeMismatch');});
test('native method parameter spelling resolves against exact declared source_module',()=>{const copy=JSON.parse(JSON.stringify(contract));copy.source_module='Missing@1';failure(()=>check(query,model,assets(copy)),'UnknownReference');});
const delegate='\nquery Wrapper:\n  input id UInt64\n  context customer Customer\n  output optional<View>\n  delegates Read(id=id)\n  effects none\n';
for(const [name,change,code]of [
 ['wrong argument type',delegate.replace('Read(id=id)','Read(id=true)'),'TypeMismatch'],
 ['missing argument',delegate.replace('Read(id=id)','Read()'),'MissingMapping'],
 ['unknown argument',delegate.replace('Read(id=id)','Read(unknown=id)'),'UnknownReference'],
 ['wrong result type',delegate.replace('output optional<View>','output UInt64'),'TypeMismatch'],
 ['missing forwarded context',delegate.replace('  context customer Customer\n',''),'MissingMapping'],
]as const)test('delegation rejects '+name,()=>failure(()=>check(query+change),code));
test('recursive read delegation cannot be admitted by matching signatures',()=>{const extra='\nquery First:\n  output UInt64\n  delegates Second()\n\nquery Second:\n  output UInt64\n  delegates First()\n';failure(()=>check(extra),'InvalidContract');});
test('Query proposal is independently rebuilt and matching JSON remains data',()=>{const input=sources(),r=checkCoreCommerceQuerySources(input,assets()),proposed=JSON.parse(JSON.stringify(r)),checked=checkCoreCommerceQueryProposal(input,assets(),proposed);assert.notEqual(checked,proposed);assert.equal(checked.query_subject_sha256,r.query_subject_sha256);});
for(const field of ['sources','predicate','projection','wrap_projection_some','guards','on_missing','on_unavailable','contexts','effects','max_rows'])test('Query proposal forgery rejects '+field+' with unchanged digest',()=>{const input=sources(),r=JSON.parse(JSON.stringify(checkCoreCommerceQuerySources(input,assets())));r.queries[0][field]='forged';failure(()=>checkCoreCommerceQueryProposal(input,assets(),r),'InvalidContract');});
test('extra claimed native ownership cannot enter a Query proposal',()=>{const input=sources(),r={...checkCoreCommerceQuerySources(input,assets()),native_owner:{accepted:true}};failure(()=>checkCoreCommerceQueryProposal(input,assets(),r),'InvalidContract');});
test('Query proposal accessors reject without invoking them',()=>{let invoked=false;const proposal={get queries(){invoked=true;return [];}};failure(()=>checkCoreCommerceQueryProposal(sources(),assets(),proposal),'InvalidContract');assert.equal(invoked,false);});
const protocol=`
value-object Request:
  id UInt64
value-object Result:
  id UInt64
rule SameRequest:
  input first Request
  input second Request
  expression first.id == second.id
interface Provider:
  kind external
  protocol Fixture-v1
  exposes Inspect
  request Request
  result Result
  binding native/protocol.json
query Inspect:
  input id UInt64
  output Result
  native-protocol Provider.Inspect
  compare original request using SameRequest
  on-existing returns current original-attempt status
  on-missing returns UnknownKey with exact supplied identity and no reference
  on-conflict fails ProviderRequestConflict
  effects none
`;
const protocolAssets=[...assets(),{path:'native/protocol.json',text:'{"qualification":"source requirement only"}'}];
test('native Query binds exact external request/result/comparison contracts but no producer',()=>{const q=check(protocol,model,protocolAssets).queries[0]!;assert.equal(q.kind,'native-protocol');if(q.kind==='native-protocol'){assert.equal(q.interface,'Demo.Provider');assert.equal(q.method,'Inspect');assert.equal(q.compare_rule,'Demo.SameRequest');assert.equal(q.native_qualification,'requires-original-producer-and-profile');}});
for(const [name,extra,code]of [
 ['unexposed native method',protocol.replace('exposes Inspect','exposes Missing'),'TypeMismatch'],
 ['wrong native method identity',protocol.replace('Provider.Inspect','Provider.Missing'),'TypeMismatch'],
 ['wrong native parameter type',protocol.replace('query Inspect:\n  input id UInt64','query Inspect:\n  input id Bool'),'TypeMismatch'],
 ['wrong native result contract',protocol.replace('query Inspect:\n  input id UInt64\n  output Result','query Inspect:\n  input id UInt64\n  output Request'),'TypeMismatch'],
 ['wrong request comparison signature',protocol.replace('input second Request','input second Result'),'TypeMismatch'],
 ['scalar native request',protocol.replace('  request Request','  request UInt64'),'TypeMismatch'],
 ['private Interface cannot become native protocol',protocol.replace('  kind external','  kind internal'),'TypeMismatch'],
]as const)test('native protocol rejects '+name,()=>failure(()=>check(extra,model,protocolAssets),code));
test('native Query cannot invent an absent provider binding file',()=>failure(()=>check(protocol,model,assets()),'UnknownReference'));
test('separate private field and method contracts retain their own source namespaces',()=>{
 const extended=model.replace('methods context.json#/contexts/Customer/methods','methods signatures/methods.json#/methods')+'\nvalue-object Token:\n  count UInt64\n',s=sources(query.replace('customer.allowed(item.id)','customer.allowed(Token(1))'),extended);
 s.push({path:'foreign.alch',text:'module Foreign version 1\nvalue-object Token:\n  count UInt64\n'});
 const files=[...assets(),{path:'signatures/methods.json',text:JSON.stringify({source_module:'Foreign@1',abi:'craft.fixture-context/v1-candidate',methods:{allowed:{parameters:['Token'],result:'Bool'}}})}];
 failure(()=>checkCoreCommerceQuerySources(s,files),'TypeMismatch');
 const explicit=s.map(f=>({...f,text:f.text.replace('customer.allowed(Token(1))','customer.allowed(Foreign.Token(1))')}));assert.equal(checkCoreCommerceQuerySources(explicit,files).queries.length,1);
});
