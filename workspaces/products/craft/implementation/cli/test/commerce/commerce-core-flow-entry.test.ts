/** Inline permissions and private projection source requirements, no allow.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {auditCoreCommerceEntrySources,checkCoreCommerceEntrySources,checkCoreCommerceEntryProposal} from '../../src/commerce/commerce-core-flow-entry.js';
const declarations=`module Demo version 1
value-object Identifier:
  carrier String
  representation transparent-scalar
  utf8-bytes 1..64
entity Order:
  id Identifier
  ownerId Identifier
  version UInt64
  identity id
  immutable id, ownerId
value-object View:
  id Identifier
  ownerId Identifier
event Started:
  version 1
  id Identifier
interface Customer:
  kind trusted-context
  abi craft.test-customer/v1-candidate
  custody private-registered-entry-auth-owner
  fields context.json#/contexts/Customer/properties
  methods context.json#/contexts/Customer/methods
  serializable false
  public-constructor forbidden
interface Service:
  kind trusted-context
  abi craft.test-service/v1-candidate
  custody private-registered-service-entry-owner
  fields context.json#/contexts/Service/properties
  serializable false
  public-constructor forbidden
interface Worker:
  kind trusted-context
  abi craft.test-worker/v1-candidate
  custody private-registered-local-worker-owner
  fields context.json#/contexts/Worker/properties
  serializable false
  public-constructor forbidden
interface Causal:
  kind trusted-context
  abi craft.commerce-causal-call/v1-candidate
  custody private-registered-parent-call-store-worker-or-event-owner
  variants profiles/auth.json#/causal_contexts
  serializable false
  public-constructor forbidden
interface Auth:
  kind native-auth-owner
  abi craft.test-auth/v1-candidate
  admission auth-foundation-authorization-admission-service
  decision auth-foundation-authorization-ready-decision.authorize
  binding profiles/auth.json
  on-unresolved reject NativeImplementationUnavailable
operation Create:
  input id Identifier
  context customer Customer
  output View
  transaction New:
    atomic-participants Order
    create order Order:
      id <- id
      ownerId <- customer.customerId
      version <- 1
  return View(id=order.id,ownerId=order.ownerId)
query Read:
  input id Identifier
  context customer Customer
  source order Order
  output View
  where order.id == id
  project View(id=order.id,ownerId=order.ownerId)
  on-missing fail missing
operation Echo:
  input id Identifier
  context service Service
  output Identifier
  return id
operation Work:
  input id Identifier
  context worker Worker
  output Bool
  return true
operation Handle:
  input started Started
  context service Service
  output Identifier
  return started.id
interface Internal:
  kind internal
  exposes Create, Read, Echo, Work, Handle
interface Application:
  kind application-composition
  service demo module Demo
  formal-claims optional
`;
const customer=`entry Demo.CreateEntry:
  invokes Demo.Create
  interaction request-response
  access:
    authenticated customer
    permission demo.create
    auth-resource demo
    auth-action create
    auth-scope test
    auth-route test:Demo.CreateEntry
    caller self
    context Customer
    native-requires craft.context.current-owner/v1-candidate
    current-action before replay-and-effects
    resource-binding customer Customer from craft.test-customer/v1-candidate#current-invocation
    resource-binding planned Order from craft.effect-intent/v1-candidate#Demo.Create/New/order
    resource-condition planned.ownerId == customer.customerId
    on-resource-false reject forbidden before effects
    principal-from registered authenticated subject, never request fields
`;
const read=customer.replaceAll('CreateEntry','ReadEntry').replaceAll('Demo.Create','Demo.Read').replace('permission demo.create','permission demo.read').replace('auth-action create','auth-action read').replace('resource-binding planned Order from craft.effect-intent/v1-candidate#Demo.Read/New/order','resource-binding planned Order from craft.scoped-query-row/v1-candidate#Demo.Read/order').replace('on-resource-false reject forbidden before effects','on-resource-missing-or-false missing resource-not-found before projection');
const service=`entry Demo.EchoEntry:
  invokes Demo.Echo
  interaction request-response
  access:
    authenticated service
    permission demo.echo
    auth-resource demo
    auth-action echo
    auth-scope test
    auth-route test:Demo.EchoEntry
    caller demo
    context Service
    native-requires craft.context.current-owner/v1-candidate
    current-action before replay-and-effects
`;
const causal=service+`    resource-binding causal Parent from craft.commerce-causal-call/v1-candidate#parent-customer-delegation
    resource-condition input.id == causal.ownerId
    on-resource-false reject forbidden before effects
`;
const worker=service.replaceAll('EchoEntry','WorkEntry').replaceAll('Demo.Echo','Demo.Work').replaceAll('demo.echo','demo.work').replace('auth-action echo','auth-action work').replace('context Service','context Worker')+`    resource-binding causal Observation from craft.commerce-causal-call/v1-candidate#Demo.Order/original-worker-observation
    resource-condition input.id == causal.row.id
    on-resource-false reject forbidden before effects
    worker-from original registered local lifecycle owner
    invocation-decision fresh and separate from worker lifetime capability
`;
const event=service.replaceAll('EchoEntry','HandleEntry').replaceAll('Demo.Echo','Demo.Handle').replaceAll('demo.echo','demo.handle').replace('auth-action echo','auth-action handle').replace('interaction request-response','interaction event')+`    producer demo
    occurrence-from original registered event ingress
    acknowledge after committed inbox-and-result
`;
const contextDoc={source_module:'Demo@1',contexts:{Customer:{abi:'craft.test-customer/v1-candidate',properties:{customerId:'Identifier'},methods:{allowed:{parameters:['Identifier'],result:'Bool'}}},Service:{abi:'craft.test-service/v1-candidate',properties:{serviceId:'Identifier'}},Worker:{abi:'craft.test-worker/v1-candidate',properties:{workerId:'Identifier'}}}};
const authDoc={abi:'craft.test-auth/v1-candidate',source_module:'Demo@1',policy_template_mapping:{entry_route:'test:logicalEntryId'},causal_contexts:{Parent:{kind:'opaque-private-projection',projection_family:false,fields:{ownerId:'Identifier'}},Family:{kind:'opaque-private-projection',projection_family:true,fields:{ownerId:'Identifier',version:'UInt64'}},Observation:{kind:'opaque-private-projection',projection_family:false,fields:{row:'Demo.Order'}}}};
const fixture=(access=customer,decl=declarations,auth:unknown=authDoc,context:unknown=contextDoc)=>({sources:[{path:'application.alch',text:decl+access}],assets:[{path:'context.json',text:JSON.stringify(context)},{path:'profiles/auth.json',text:JSON.stringify(auth)}]});
const check=(access=customer,decl=declarations,auth:unknown=authDoc,context:unknown=contextDoc)=>{const f=fixture(access,decl,auth,context);return checkCoreCommerceEntrySources(f.sources,f.assets);};
const one=(access=customer)=>check(access).entries[0]!;
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
function historicalSource(){const owner=createCoreCommerceSourceOwner(),handle=owner.prepare(fileURLToPath(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/binding-repair-before/',import.meta.url)).replace(/\/$/,'')),capture=owner.inspect(handle),paths=new Set(capture.reconstruction.modules.map(m=>m.path));return {owner,handle,sources:capture.files.filter(f=>paths.has(f.path)),assets:capture.files.filter(f=>f.path.endsWith('.json'))};}
test('preserved pre-repair commerce checks four entries and exposes the absent causal schema namespace for eighteen',()=>{const f=historicalSource(),r=auditCoreCommerceEntrySources(f.sources,f.assets);assert.equal(r.complete,false);assert.equal(r.entries.length,4);assert.equal(r.diagnostics.length,18);assert.ok(r.diagnostics.every(d=>d.diagnostics[0]!.code==='UnknownReference'&&d.diagnostics[0]!.message.includes('source_module@1')));f.owner.assertCurrent(f.handle);f.owner.dispose(f.handle);});
test('isolated explicit causal schema namespace checks all 22 original entries without mutating source',()=>{const f=historicalSource(),assets=f.assets.map(a=>{if(a.path!=='profiles/auth-bridge.json')return a;const doc=JSON.parse(a.text);doc.source_module='Shop.Values@1';return {...a,text:JSON.stringify(doc)};}),r=checkCoreCommerceEntrySources(f.sources,assets);assert.equal(r.entries.length,22);assert.ok(r.entries.every(e=>e.qualification==='typed-entry-source-only'));const reserve=r.entries.find(e=>e.id==='Inventory.ReserveStockEntry')!.access.resource_bindings[0]!;assert.deepEqual(reserve.required_fields,['lines','orderId','reserveCommandId']);assert.ok(!reserve.fields.some(f=>f.name==='reservationVersion'));f.owner.assertCurrent(f.handle);f.owner.dispose(f.handle);});
test('inline permission binds resource, action, scope and exact logical entry route',()=>{const r=one();assert.deepEqual(r.access.auth_permission,{resource:'demo',action:'create',scope:'test'});assert.equal(r.access.auth_route_id,'test:Demo.CreateEntry');assert.equal(r.access.current_action,'before-replay-and-effects');assert.equal(r.result!.kind,'record');});
test('fresh intent binds its exact original transaction create alias and retains replay separation',()=>{const r=one(),b=r.access.resource_bindings[1]!;assert.equal(b.origin.kind,'fresh-effect-intent');assert.equal(b.origin.transaction,'New');assert.equal(b.origin.binding,'order');assert.equal(r.access.resource_phase,'fresh-intent-before-effects');assert.equal(r.access.matching_replay_resource_check,'trusted-scope-only');assert.ok(r.native_requirements.includes('matching-replay-never-runs-fresh-intent-id-clock-or-quote-work'));});
test('scoped reads bind an independently checked Query source and preserve foreign-resource 404',()=>{const r=one(read);assert.equal(r.access.resource_phase,'scoped-read-before-response');assert.equal(r.access.on_resource_missing_or_false,'resource-not-found');assert.equal(r.access.resource_bindings[1]!.origin.kind,'scoped-query-row');});
test('permission-only entries need no artificial business Rule or resource condition',()=>{const r=one(service);assert.equal(r.access.resource_condition,null);assert.equal(r.access.resource_bindings.length,0);assert.equal(r.access.principal_kind,'service');assert.equal(r.authority_effect,undefined);assert.equal(Object.hasOwn(r,'authorized'),false);});
test('private causal data remains a projection requirement with no public constructor',()=>{const b=one(causal).access.resource_bindings[0]!;assert.equal(b.kind,'private-projection');assert.equal(b.origin.kind,'parent-customer-delegation');assert.equal(b.source_document,'profiles/auth.json');assert.equal(b.public_constructor,'forbidden');assert.equal(b.custody,'required-from-original-registered-owner');});
test('family projections materialize only required fields without inventing future-stage values',()=>{const r=one(causal.replace('causal Parent','causal Family')),b=r.access.resource_bindings[0]!;assert.equal(b.projection_family,true);assert.deepEqual(b.fields.map(f=>f.name),['ownerId']);assert.deepEqual(b.required_fields,['ownerId']);});
test('whole-family comparisons explicitly require all fields',()=>{const r=one(causal.replace('causal Parent','causal Family').replace('input.id == causal.ownerId','causal == causal'));assert.deepEqual(r.access.resource_bindings[0]!.required_fields,['ownerId','version']);});
test('worker lifetime and the fresh one-entry decision remain separate obligations',()=>{const r=one(worker);assert.equal(r.access.worker_lifetime,'requires-original-local-worker-owner');assert.equal(r.access.invocation_decision,'fresh-separate-original-entry-decision');assert.equal(r.access.resource_bindings[0]!.origin.kind,'worker-observation');});
test('event ingress retains exact producer, payload role and original committed consumer acknowledgement',()=>{const r=one(event);assert.equal(r.event_argument,'started');assert.equal(r.access.producer,'demo');assert.equal(r.access.event_completion,'requires-original-consumer-inbox-and-result-commit');assert.equal(r.access.matching_replay_resource_check,'not-applicable');});
test('duplicate provenance flags reject even where they are not required for that principal kind',()=>failure(()=>check(service+'    principal-from registered authenticated subject, never request fields\n    principal-from registered authenticated subject, never request fields\n'),'DuplicateSymbol'));
test('direct Bool resource expressions use actual declared fields without a claim or separate Rule',()=>assert.equal(one(causal).access.resource_condition!.type.kind,'Bool'));
for(const [label,access,code]of [
 ['permission/resource/action mismatch',customer.replace('permission demo.create','permission demo.other'),'InvalidContract'],
 ['wrong logical entry route',customer.replace('auth-route test:Demo.CreateEntry','auth-route test:Demo.ReadEntry'),'InvalidContract'],
 ['wrong route prefix',customer.replace('auth-route test:','auth-route other:'),'InvalidContract'],
 ['missing customer principal origin',customer.replace('    principal-from registered authenticated subject, never request fields\n',''),'MissingMapping'],
 ['customer caller supplied as service',customer.replace('caller self','caller demo'),'InvalidContract'],
 ['unknown service caller',service.replace('caller demo','caller other'),'InvalidContract'],
 ['service caller self',service.replace('caller demo','caller self'),'InvalidContract'],
 ['customer/service context mismatch',customer.replace('context Customer','context Service'),'InvalidContract'],
 ['target invocation context mismatch',service.replace('context Service','context Worker')+'    worker-from original registered local lifecycle owner\n    invocation-decision fresh and separate from worker lifetime capability\n','TypeMismatch'],
 ['data record as entry context',customer.replace('context Customer','context Order'),'TypeMismatch'],
 ['unregistered current-owner ABI',customer.replace('craft.context.current-owner/v1-candidate','craft.context.foreign/v1-candidate'),'UnsupportedCapability'],
 ['missing current action',customer.replace('    current-action before replay-and-effects\n',''),'MissingMapping'],
 ['missing native requirement',customer.replace('    native-requires craft.context.current-owner/v1-candidate\n',''),'MissingMapping'],
 ['missing resource outcome',causal.replace('    on-resource-false reject forbidden before effects\n',''),'MissingMapping'],
 ['outcome without condition',service+'    on-resource-false reject forbidden before effects\n','InvalidContract'],
 ['conflicting resource outcomes',causal+'    on-resource-missing-or-false missing resource-not-found before projection\n','DuplicateSymbol'],
 ['duplicate resource condition',causal+'    resource-condition true\n','DuplicateSymbol'],
 ['nonBool resource condition',causal.replace('input.id == causal.ownerId','input.id'),'TypeMismatch'],
 ['caller-supplied authorization field',causal.replace('input.id == causal.ownerId','input.authorized'),'UnknownReference'],
 ['unknown input field',causal.replace('input.id == causal.ownerId','input.missing == causal.ownerId'),'UnknownReference'],
 ['unknown causal field',causal.replace('causal.ownerId','causal.missing'),'UnknownReference'],
 ['unused causal binding',causal.replace('input.id == causal.ownerId','true'),'InvalidContract'],
 ['duplicate resource alias',customer.replace('resource-binding planned Order','resource-binding customer Order'),'DuplicateSymbol'],
 ['input alias overwritten',causal.replace('resource-binding causal Parent','resource-binding input Parent'),'DuplicateSymbol'],
 ['causal owner missing selector',causal.replace('#parent-customer-delegation',''),'InvalidContract'],
 ['causal selector has extra fragment',causal.replace('#parent-customer-delegation','#parent-customer-delegation#other'),'InvalidContract'],
 ['unknown causal variant',causal.replace('causal Parent','causal Unknown'),'InvalidContract'],
 ['unknown causal selector',causal.replace('parent-customer-delegation','unregistered'),'UnsupportedCapability'],
 ['missing causal Workflow selector',causal.replace('parent-customer-delegation','Demo.Absent/original-step-journal'),'UnknownReference'],
 ['unknown causal selector slot',causal.replace('parent-customer-delegation','Demo.Order/unknown-slot'),'UnsupportedCapability'],
 ['worker observation without worker',causal.replace('causal Parent','causal Observation').replace('parent-customer-delegation','Demo.Order/original-worker-observation').replace('causal.ownerId','causal.row.id'),'InvalidContract'],
 ['wrong fresh intent Operation',customer.replace('#Demo.Create/New/order','#Demo.Echo/New/order'),'InvalidContract'],
 ['unknown fresh transaction',customer.replace('#Demo.Create/New/order','#Demo.Create/Absent/order'),'UnknownReference'],
 ['unknown fresh alias',customer.replace('#Demo.Create/New/order','#Demo.Create/New/absent'),'UnknownReference'],
 ['wrong resource role',customer.replace('planned Order from','planned View from'),'InvalidContract'],
 ['current-context ABI mismatch',customer.replace('from craft.test-customer/v1-candidate','from craft.other-customer/v1-candidate'),'InvalidContract'],
 ['current-context selector mismatch',customer.replace('#current-invocation','#foreign-invocation'),'InvalidContract'],
 ['wrong scoped Query selector',read.replace('#Demo.Read/order','#Demo.Create/order'),'InvalidContract'],
 ['unknown scoped Query alias',read.replace('#Demo.Read/order','#Demo.Read/absent'),'UnknownReference'],
 ['scoped row 404 replaced with 403',read.replace('on-resource-missing-or-false missing resource-not-found before projection','on-resource-false reject forbidden before effects'),'InvalidContract'],
 ['missing worker lifetime',worker.replace('    worker-from original registered local lifecycle owner\n',''),'MissingMapping'],
 ['missing fresh worker decision',worker.replace('    invocation-decision fresh and separate from worker lifetime capability\n',''),'MissingMapping'],
 ['worker lifetime on service context',service+'    worker-from original registered local lifecycle owner\n','InvalidContract'],
 ['event producer differs from caller',event.replace('producer demo','producer other'),'InvalidContract'],
 ['missing event occurrence',event.replace('    occurrence-from original registered event ingress\n',''),'MissingMapping'],
 ['missing event commit acknowledgement',event.replace('    acknowledge after committed inbox-and-result\n',''),'MissingMapping'],
 ['event provenance on request-response',service+'    producer demo\n','InvalidContract'],
 ['event with scalar input',event.replace('invokes Demo.Handle','invokes Demo.Echo'),'TypeMismatch'],
 ['event with Query target',read.replace('interaction request-response','interaction event'),'TypeMismatch'],
]as const)test('rejects '+label,()=>failure(()=>check(access),code));
test('public/serializable private contexts cannot be entry authorities',()=>{
 failure(()=>check(customer,declarations.replaceAll('serializable false','serializable true')),'Syntax');
 failure(()=>check(customer,declarations.replace('  serializable false\n','')),'MissingMapping');
 failure(()=>check(customer,declarations.replace('  public-constructor forbidden\n','')),'MissingMapping');
});
test('resource guards cannot execute native methods through a private context projection',()=>failure(()=>check(customer.replace('planned.ownerId == customer.customerId','planned.ownerId == customer.customerId and customer.allowed(customer.customerId)')),'InvalidContract'));
for(const [label,mutate,code]of [
 ['absent explicit namespace',(d:any)=>{delete d.source_module;},'UnknownReference'],
 ['uncaptured source module',(d:any)=>{d.source_module='Unknown@1';},'UnknownReference'],
 ['wrong source version',(d:any)=>{d.source_module='Demo@2';},'UnknownReference'],
 ['invalid field type',(d:any)=>{d.causal_contexts.Parent.fields.ownerId='Missing';},'UnknownReference'],
 ['wrong declared private kind',(d:any)=>{d.causal_contexts.Parent.kind='public-record';},'InvalidContract'],
 ['implicit family status',(d:any)=>{delete d.causal_contexts.Parent.projection_family;},'InvalidContract'],
 ['missing required projection field',(d:any)=>{d.causal_contexts.Parent.fields={other:'Identifier'};},'UnknownReference'],
 ['malformed annotation',(d:any)=>{d.causal_contexts.Parent.fields.ownerId=true;},'InvalidContract'],
 ['different Auth ABI',(d:any)=>{d.abi='craft.foreign-auth/v1-candidate';},'InvalidContract'],
 ['unregistered route template',(d:any)=>{d.policy_template_mapping.entry_route='arbitrary expression';},'UnsupportedCapability'],
]as const)test('rejects causal/Auth contract '+label,()=>{const copy=JSON.parse(JSON.stringify(authDoc));mutate(copy);failure(()=>check(causal,declarations,copy),code);});
test('even unused family field schemas are statically validated without materializing their values',()=>{const copy=JSON.parse(JSON.stringify(authDoc));copy.causal_contexts.Family.fields.version='Unknown';failure(()=>check(causal.replace('causal Parent','causal Family'),declarations,copy),'UnknownReference');});
test('an unqualified causal field cannot use a globally unique unrelated type fallback',()=>{const copy=JSON.parse(JSON.stringify(authDoc));copy.causal_contexts.Parent.fields.ownerId='OutsideOnly';const f=fixture(causal,declarations,copy);f.sources.push({path:'outside.alch',text:'module Other version 1\nvalue-object OutsideOnly:\n  carrier String\n  representation transparent-scalar\n  utf8-bytes 1..64\n'});failure(()=>checkCoreCommerceEntrySources(f.sources,f.assets),'UnknownReference');});
test('binding another captured current context cannot satisfy this entry context identity',()=>failure(()=>check(customer.replace('customer Customer from craft.test-customer','customer Service from craft.test-service')),'InvalidContract'));
test('opaque causal Interface also forbids public/serializable construction',()=>failure(()=>check(causal,declarations.replace('  variants profiles/auth.json#/causal_contexts\n  serializable false','  variants profiles/auth.json#/causal_contexts')),'MissingMapping'));
test('Auth source owner and binding are explicit requirements',()=>failure(()=>check(customer,declarations.replace('  binding profiles/auth.json\n','')),'MissingMapping'));
test('multiple Auth owner candidates do not silently select one',()=>{const other='interface OtherAuth:\n  kind native-auth-owner\n  abi craft.test-auth/v1-candidate\n  binding profiles/auth.json\n';failure(()=>check(customer,declarations+other),'MissingMapping');});
test('the same target Operation may have distinct logical entries and permissions',()=>{const second=customer.replaceAll('CreateEntry','OtherEntry').replace('permission demo.create','permission demo.other').replace('auth-action create','auth-action other');const r=check(customer+second);assert.equal(r.entries.length,2);assert.equal(r.entries[0]!.invokes,r.entries[1]!.invokes);assert.notEqual(r.entries[0]!.access.auth_route_id,r.entries[1]!.access.auth_route_id);});
test('whole entry proposal is independently reconstructed and supplies no allow or private owner',()=>{const f=fixture(),proposal=JSON.parse(JSON.stringify(check()));const r=checkCoreCommerceEntryProposal(f.sources,f.assets,proposal);assert.notEqual(r,proposal);assert.equal(r.authority_effect,'none');assert.equal(Object.hasOwn(r,'authorized'),false);assert.equal(Object.hasOwn(r,'accepted'),false);});
for(const field of ['principal_kind','caller','permission','auth_permission','auth_route_id','context','decision','native_requires','current_action','resource_bindings','resource_condition','resource_phase','matching_replay_resource_check','on_resource_missing_or_false','producer','worker_lifetime','invocation_decision','event_completion'])test('rejects entry access proposal forgery '+field,()=>{const f=fixture(),proposal=JSON.parse(JSON.stringify(check()));proposal.entries[0].access[field]='forged';failure(()=>checkCoreCommerceEntryProposal(f.sources,f.assets,proposal),'InvalidContract');});
test('resource custody requirements cannot be erased from a matching entry proposal',()=>{const f=fixture(),proposal=JSON.parse(JSON.stringify(check()));proposal.entries[0].native_requirements=[];failure(()=>checkCoreCommerceEntryProposal(f.sources,f.assets,proposal),'InvalidContract');});
test('entry proposal accessors reject without executing them',()=>{const f=fixture();let called=false;failure(()=>checkCoreCommerceEntryProposal(f.sources,f.assets,{get entries(){called=true;return [];}}),'InvalidContract');assert.equal(called,false);});
