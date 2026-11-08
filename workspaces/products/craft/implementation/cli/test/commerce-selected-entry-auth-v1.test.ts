/** A selected Commerce Entry uses actual Auth and source invocation owners. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../src/commerce/commerce-binding-assembly-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1,assertCommerceSelectedEntryAuthOwnerV1} from '../src/commerce/commerce-selected-entry-auth-v1.js';
import {qualifiesCommerceEffectIntentV1} from '../src/commerce/commerce-effect-intent-qualifier-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('selected source Entry admits checked effect intent and denies missing causal owners',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-selected-entry-auth-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined,auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined,selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined;
 try{
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth'));
  await assert.rejects(createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,{...assembly} as any,auth,path.join(root,'foreign')),code('ForeignOwner'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  assertCommerceSelectedEntryAuthOwnerV1(selected);
  selected.assertAssembly(assemblyOwner,assembly);assert.throws(()=>selected!.assertAssembly(assemblyOwner,{...assembly} as any),code('ForeignOwner'));
  const inspection=selected.inspect();assert.equal(inspection.entries,22);assert.equal(inspection.native_basis_qualified,false);assert.equal(inspection.bound_application_qualified,false);
  const entryId='Orders.PlaceOrderEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='customer-one',evidence='selected-entry-evidence';
  const placePlan=plans.inspectOperation(plans.bindOperation('Orders.PlaceOrder')).plan;
  assert.equal(qualifiesCommerceEffectIntentV1(definition,placePlan,{kind:'customer',customerId:subject}),true);
  const altered=structuredClone(placePlan) as any;
  const accept=altered.body.find((step:any)=>step.kind==='transaction'&&step.transaction.name==='AcceptCheckout');
  const order=accept.transaction.body.find((step:any)=>step.kind==='mutation'&&step.binding==='order');
  const customerField=order.fields.find((field:any)=>field.name==='customerId');
  customerField.value.expression={op:'var',name:'quoteId'};
  assert.equal(qualifiesCommerceEffectIntentV1(definition,altered,{kind:'customer',customerId:subject}),false,
   'a source assignment that no longer preserves the native context must not qualify');
  assert.equal(qualifiesCommerceEffectIntentV1(definition,placePlan,{kind:'service',customerId:subject}),false);
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'selected-entry-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'customer',service_id:null,scope:definition.access.auth_permission.scope});
  const parameters={quoteId:'quote-one',checkoutKey:'checkout-one'},wire=Buffer.from(JSON.stringify(parameters));
  await assert.rejects(selected.begin(actor,'Not.An.Entry',wire,parameters),code('ForeignOwner'));
  const denied=await selected.begin(null,entryId,wire,parameters);assert.equal(denied.ok,false);if(!denied.ok)assert.equal(denied.status,401);
  const placed=await selected.begin(actor,entryId,wire,parameters);
  assert.equal(placed.ok,true,'the checked AcceptCheckout/order assignment preserves the native customer identity');
  if(placed.ok){
   const view=selected.inspectInvocation(placed.invocation);
   assert.equal(view.operation,'Orders.PlaceOrder');assert.equal(view.actual_business_resource_owners_qualified,true);
   assert.deepEqual({...selected.parameters(placed.invocation)},parameters);
   assert.throws(()=>selected!.inspectInvocation({...placed.invocation} as any),code('ForeignOwner'));
   const catalogId='Catalog.ReadQuoteEntry',catalogEntry=auth.bindEntry(catalogId),catalogDefinition=auth.inspectEntry(catalogEntry);
   const catalogSubject='service-'+catalogDefinition.access.caller,catalogEvidence='selected-catalog-evidence';
   const catalogFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:catalogSubject,evidence:catalogEvidence,session:'selected-catalog-session',routes:[{entry:catalogId,permission:catalogDefinition.access.auth_permission}]});
   const catalogActor=registerCommerceEntryFixtureActorV1(auth,catalogFixture.handle,{subject:catalogSubject,evidence:catalogEvidence,principal_kind:'service',service_id:catalogDefinition.access.caller,scope:catalogDefinition.access.auth_permission.scope});
   try{
    const catalogInput={quoteId:parameters.quoteId,customerId:subject},catalogWire=Buffer.from(JSON.stringify(catalogInput));
    assert.deepEqual(await selected.begin(catalogActor,catalogId,catalogWire,catalogInput),{ok:false,code:'forbidden',status:403},
     'service Auth alone cannot establish original customer delegation');
    const readPath=selected.delegatedReadCallPath(placed.invocation,catalogId),foreign={kind:'original-selected-customer-delegation/v1-candidate'} as any;
    await assert.rejects(selected.begin(catalogActor,catalogId,catalogWire,catalogInput,undefined,foreign),code('ForeignOwner'));
    const wrong=selected.issueDelegatedRead(placed.invocation,readPath);
    assert.deepEqual(await selected.begin(catalogActor,catalogId,Buffer.from(JSON.stringify({...catalogInput,customerId:'foreign-customer'})),{...catalogInput,customerId:'foreign-customer'},undefined,wrong),
     {ok:false,code:'forbidden',status:403});
    const delegation=selected.issueDelegatedRead(placed.invocation,readPath),catalog=await selected.begin(catalogActor,catalogId,catalogWire,catalogInput,undefined,delegation);
    assert.equal(catalog.ok,true,'original parent read arguments and native customer context authorize the scoped Query stage');
    if(catalog.ok){assert.equal(selected.inspectInvocation(catalog.invocation).actual_business_resource_owners_qualified,false,
      'scoped row is still required before QuoteView projection');assert.deepEqual({...selected.scopedDelegation(catalog.invocation)},{customerId:subject});selected.retire(catalog.invocation);}
    await assert.rejects(selected.begin(catalogActor,catalogId,catalogWire,catalogInput,undefined,delegation),code('ForeignOwner'));
    await assert.rejects(selected.beginDelegatedQuery(placed.invocation,readPath),code('MissingMapping'),
     'the generated read cannot manufacture a native service identity');
    assert.throws(()=>selected!.registerServiceActor(catalogId,actor),code('ForeignOwner'),
     'the customer root actor cannot stand in for the Orders service caller');
    selected.registerServiceActor(catalogId,catalogActor);
    const generatedRead=await selected.beginDelegatedQuery(placed.invocation,readPath);
    assert.equal(generatedRead.ok,true,'generated read supplies its checked wire and retained native service actor internally');
    if(generatedRead.ok){assert.deepEqual({...selected.parameters(generatedRead.invocation)},catalogInput);selected.retire(generatedRead.invocation);}
   }finally{auth.disposeActor(catalogActor);auth.disposeEntry(catalogEntry);}
   selected.retire(placed.invocation);assert.throws(()=>selected!.inspectInvocation(placed.invocation),code('ForeignOwner'));
  }
  auth.disposeActor(actor);auth.disposeEntry(entry);
  const paymentEntryId='Payments.CapturePaymentEntry',paymentEntry=auth.bindEntry(paymentEntryId),paymentDefinition=auth.inspectEntry(paymentEntry),paymentSubject='service-'+paymentDefinition.access.caller,paymentEvidence='selected-payment-evidence';
  const paymentFixture=seedCommerceAuthFixtureDatabaseV1(native,{subject:paymentSubject,evidence:paymentEvidence,session:'selected-payment-session',routes:[{entry:paymentEntryId,permission:paymentDefinition.access.auth_permission}]});
  const paymentActor=registerCommerceEntryFixtureActorV1(auth,paymentFixture.handle,{subject:paymentSubject,evidence:paymentEvidence,principal_kind:'service',service_id:paymentDefinition.access.caller,scope:paymentDefinition.access.auth_permission.scope});
  const paymentInput={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'},paymentWire=Buffer.from(JSON.stringify(paymentInput,(_key,value)=>typeof value==='bigint'?String(value):value));
  const payment=await selected.begin(paymentActor,paymentEntryId,paymentWire,paymentInput);
  assert.deepEqual(payment,{ok:false,code:'forbidden',status:403},
   'a valid service actor cannot replace the Orders Checkout causal Capture call');
  auth.disposeActor(paymentActor);auth.disposeEntry(paymentEntry);
  const nativeBinary=(native.inspect().binary as {path:string}).path;
  writeFileSync(nativeBinary,Buffer.concat([readFileSync(nativeBinary),Buffer.from([0])]));
  assert.throws(()=>selected!.assertCurrent(),code('StaleOwner'),
   'selected Entry/Auth custody must still detect a changed native Auth binary through its original invocation owner');
 }finally{selected?.dispose();auth?.dispose();await native?.dispose();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
