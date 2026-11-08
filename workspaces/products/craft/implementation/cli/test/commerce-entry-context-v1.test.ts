/** Original .alch source/codec/native Auth custody; no effect or JWT claim.
 * Open Questions: docs/COMMERCE-AUTH-READY-BRIDGE-V1.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,cpSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {produceCommerceAuthNativeOwnerV1,type CommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1,assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceAuthActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';
const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),evidence=path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC11'),candidate=path.join(repo,'examples/ecommerce-target-candidate'),wire=(v:unknown)=>Buffer.from(JSON.stringify(v));
let native:CommerceAuthNativeOwnerV1,owner:CommerceEntryContextOwnerV1,sources:any,capture:any,stage:any,source:any,domain:any,baseline:any,fixture:ReturnType<typeof seedCommerceAuthFixtureDatabaseV1>,customer:CommerceAuthActorV1,service:CommerceAuthActorV1;
let place:any,get:any,catalog:any;
let otherOwner:CommerceEntryContextOwnerV1,root:string,privateCandidate:string;
before(async()=>{
 root=mkdtempSync(path.join(evidence,'entry-context-controls-'));native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native'));privateCandidate=path.join(root,'source');cpSync(candidate,privateCandidate,{recursive:true,errorOnExist:true,force:false});
 sources=createCoreCommerceSourceOwner();capture=sources.prepare(privateCandidate);const data=sources.inspect(capture),paths=new Set(data.reconstruction.modules.map((m:any)=>m.path)),texts=data.files.filter((f:any)=>paths.has(f.path)),limits=JSON.parse(readFileSync(path.join(repo,'implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/pure-producer-model-09.json'),'utf8')).limits;
 stage=createCoreCommerceStageSourceOwner(sources,createCoreCommerceSemanticOwner(sources));source=await stage.prepare(privateCandidate,'application.alch');domain=createCommerceComputationDomainOwner(stage,source);baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 owner=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'context'));
 otherOwner=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'other-context'));
 place=owner.bindEntry('Orders.PlaceOrderEntry');get=owner.bindEntry('Orders.GetOrderEntry');catalog=owner.bindEntry('Catalog.ReadQuoteEntry');
 fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:'customer-1',evidence:'customer-evidence',session:'customer-session',routes:[{entry:'Orders.PlaceOrderEntry',permission:owner.inspectEntry(place).access.auth_permission},{entry:'Orders.GetOrderEntry',permission:owner.inspectEntry(get).access.auth_permission}]});
 customer=registerCommerceEntryFixtureActorV1(owner,fixture.handle,{subject:'customer-1',evidence:'customer-evidence',principal_kind:'customer',service_id:null,scope:'commerce-shop'});
 const f=seedCommerceAuthFixtureDatabaseV1(native,{subject:'service-orders',evidence:'orders-evidence',session:'orders-session',routes:[{entry:'Catalog.ReadQuoteEntry',permission:owner.inspectEntry(catalog).access.auth_permission}]});
 service=registerCommerceEntryFixtureActorV1(owner,f.handle,{subject:'service-orders',evidence:'orders-evidence',principal_kind:'service',service_id:'orders',scope:'commerce-shop'});
});
after(async()=>{owner?.dispose();otherOwner?.dispose();await native?.dispose();});
const input=()=>owner.prepareInput(place,wire({quoteId:'quote-1',checkoutKey:'checkout-1'}));
const allowed=async()=>{const i=input(),r=await owner.authorizeCommerceEntry(customer,place,i);assert.equal(r.ok,true);if(!r.ok)throw new Error(r.code);return {i,context:r.value};};
const code=(value:string)=>(e:any)=>e.code===value;
test('entry, schema, input and exact inline permission come from original checked source',()=>{
 assertCommerceEntryContextOwnerV1(owner);const a=input(),b=owner.prepareInput(place,Buffer.from('{"checkoutKey":"checkout-1", "quoteId":"quote-1"}'));assert.equal(owner.inspectInput(a).canonical_sha256,owner.inspectInput(b).canonical_sha256);assert.deepEqual(owner.inspectEntry(place).access.auth_permission,{resource:'orders',action:'place',scope:'commerce-shop'});assert.throws(()=>owner.prepareInput(place,wire({quoteId:'quote-1',checkoutKey:'checkout-1',authorized:true})),code('InputRejected'));assert.throws(()=>owner.prepareInput(place,wire({quoteId:'',checkoutKey:'checkout-1'})),code('InputRejected'));assert.throws(()=>owner.inspectEntry({...place}),code('ForeignOwner'));
});
test('native customer allow becomes one-use entry/input-bound customer and resource facets',async()=>{
 const {i,context}=await allowed(),invocation=await owner.consumeCommerceEntryContext(context,place,i),p=owner.inspectScope(owner.principalScope(invocation)),resource=owner.inspectScope(owner.resourceScope(invocation));assert.equal(p.customerId,'customer-1');assert.equal(p.logicalEntryId,'Orders.PlaceOrderEntry');assert.equal(p.currentActionAllowed,true);assert.equal(resource.resource,'orders');assert.equal(resource.scope,'commerce-shop');assert.equal(owner.inspectInvocation(invocation).actual_business_resource_owners_qualified,false);await assert.rejects(owner.consumeCommerceEntryContext(context,place,i),code('AlreadyConsumed'));assert.throws(()=>owner.inspectScope({...owner.principalScope(invocation)}),code('ForeignOwner'));assert.throws(()=>owner.inspectInvocation({...invocation}),code('ForeignOwner'));
});
test('JSON principal and authorization-context lookalikes are not credentials',async()=>{
 const i=input();assert.deepEqual(await owner.authorizeCommerceEntry({kind:customer.kind}as any,place,i),{ok:false,code:'unauthorized',status:401});const {context}=await allowed();await assert.rejects(owner.consumeCommerceEntryContext({...context},place,i),code('ForeignOwner'));assert.throws(()=>assertCommerceEntryContextOwnerV1({}as any),code('ForeignOwner'));
});
test('another actual source/native context factory cannot adopt original entry input actor or authorization',async()=>{
 const foreignEntry=otherOwner.bindEntry('Orders.PlaceOrderEntry'),foreignInput=otherOwner.prepareInput(foreignEntry,wire({quoteId:'quote-1',checkoutKey:'checkout-1'})),{i,context}=await allowed();
 assert.throws(()=>otherOwner.inspectEntry(place),code('ForeignOwner'));assert.throws(()=>otherOwner.inspectInput(i),code('ForeignOwner'));await assert.rejects(otherOwner.consumeCommerceEntryContext(context,foreignEntry,foreignInput),code('ForeignOwner'));assert.deepEqual(await otherOwner.authorizeCommerceEntry(customer,foreignEntry,foreignInput),{ok:false,code:'unauthorized',status:401});
});
test('wrong customer subject, tenant and service principal deny before any invocation',async()=>{
 for(const assignment of [{subject:'customer-2',evidence:'customer-evidence',principal_kind:'customer' as const,service_id:null,scope:'commerce-shop'},{subject:'customer-1',evidence:'customer-evidence',principal_kind:'customer' as const,service_id:null,scope:'other-tenant'},{subject:'customer-1',evidence:'customer-evidence',principal_kind:'service' as const,service_id:'orders',scope:'commerce-shop'}]){const a=registerCommerceEntryFixtureActorV1(owner,fixture.handle,assignment);assert.deepEqual(await owner.authorizeCommerceEntry(a,place,input()),{ok:false,code:'forbidden',status:403});}
});
test('service caller remains distinct from target and required causal resource owners remain explicit',async()=>{
 const i=owner.prepareInput(catalog,wire({quoteId:'quote-1',customerId:'customer-1'})),r=await owner.authorizeCommerceEntry(service,catalog,i);assert.equal(r.ok,true);if(!r.ok)return;const v=await owner.consumeCommerceEntryContext(r.value,catalog,i),p=owner.inspectScope(owner.principalScope(v));assert.equal(p.serviceId,'orders');assert.equal(p.targetServiceId,'catalog');assert.equal(p.currentEntryId,'Catalog.ReadQuoteEntry');const inspection=owner.inspectInvocation(v);assert.equal(inspection.actual_business_resource_owners_qualified,false);assert.ok((inspection.business_resource_requirements as any[]).some(x=>x.origin.kind==='parent-customer-delegation'));
});
test('a different logical entry or original input object retires the authorization',async()=>{
 const one=await allowed(),other=owner.prepareInput(get,wire({orderId:'order-1'}));await assert.rejects(owner.consumeCommerceEntryContext(one.context,get,other),code('Forbidden'));await assert.rejects(owner.consumeCommerceEntryContext(one.context,place,one.i),code('AlreadyConsumed'));
 const two=await allowed();await assert.rejects(owner.consumeCommerceEntryContext(two.context,place,input()),code('Forbidden'));
});
test('parallel consumption cannot reuse the original decision seal',async()=>{
 const {i,context}=await allowed();const results=await Promise.allSettled([owner.consumeCommerceEntryContext(context,place,i),owner.consumeCommerceEntryContext(context,place,i)]);assert.equal(results.filter(r=>r.status==='fulfilled').length,1);const rejected=results.find(r=>r.status==='rejected');assert.equal(rejected?.status==='rejected'&&rejected.reason.code,'AlreadyConsumed');
});
test('revocation and still-allowing policy changes invalidate prior snapshot before consumption',async()=>{
 const one=await allowed();fixture.mutate('UPDATE auth_authentication_evidence SET revoked=1');await assert.rejects(owner.consumeCommerceEntryContext(one.context,place,one.i),code('Forbidden'));fixture.mutate('UPDATE auth_authentication_evidence SET revoked=0');
 const two=await allowed();fixture.mutate('UPDATE auth_route_authorization_bindings SET binding_revision=6');await assert.rejects(owner.consumeCommerceEntryContext(two.context,place,two.i),code('Forbidden'));fixture.mutate('UPDATE auth_route_authorization_bindings SET binding_revision=5');
});
test('disposed actor/input/context cannot supply a current invocation',async()=>{
 const one=await allowed();owner.disposeInput(one.i);await assert.rejects(owner.consumeCommerceEntryContext(one.context,place,one.i),code('DisposedOwner'));
 const two=await allowed();owner.disposeCommerceEntryContext(two.context);await assert.rejects(owner.consumeCommerceEntryContext(two.context,place,two.i),code('DisposedOwner'));
 const temporary=registerCommerceEntryFixtureActorV1(owner,fixture.handle,{subject:'customer-1',evidence:'customer-evidence',principal_kind:'customer',service_id:null,scope:'commerce-shop'});const i=input(),r=await owner.authorizeCommerceEntry(temporary,place,i);assert.equal(r.ok,true);owner.disposeActor(temporary);if(r.ok)await assert.rejects(owner.consumeCommerceEntryContext(r.value,place,i),code('DisposedOwner'));
});
test('owned generated codec replacement invalidates only its original context factory',()=>{
 const file=((owner.inspect().physical_codec_members as any[])[0]).path;writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>owner.assertCurrent(),code('StaleOwner'));otherOwner.assertCurrent();native.assertCurrent();
});
test('changed actual captured Auth profile invalidates remaining context and input before native work',async()=>{
 const entry=otherOwner.bindEntry('Orders.PlaceOrderEntry'),i=otherOwner.prepareInput(entry,wire({quoteId:'quote-1',checkoutKey:'checkout-1'})),file=path.join(privateCandidate,'profiles/auth-bridge.json');
 writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>otherOwner.assertCurrent(),code('StaleOwner'));await assert.rejects(otherOwner.authorizeCommerceEntry(null,entry,i),code('StaleOwner'));native.assertCurrent();assert.deepEqual(native.inspectWork(),{active:0,queued:0,unsettled:0});
});
