/** Protected Capture's fail-closed boundary; the separate assembly test
 * exercises the genuine generated transaction-to-provider join. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
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
import {createCommerceServiceStorageOwnerV1} from '../src/commerce/commerce-service-storage-v1.js';
import {createCommerceDemoPaySourceSiteOwnerV1} from '../src/commerce/commerce-demopay-source-site-v1.js';
import {createCommerceDemoPayDispatchOwnerV1} from '../src/commerce/commerce-demopay-dispatch-v1.js';
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1} from '../src/commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceGeneratedOperationRuntimeV1} from '../src/commerce/commerce-generated-operation-runtime-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('Capture accepts no forged, copied, foreign or reused permit and never sends without fresh commit',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-dispatch-negative-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined,native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined;
 let auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined,selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined;
 let runtime:Awaited<ReturnType<typeof createCommerceGeneratedOperationRuntimeV1>>|undefined;
 const sites=createCommerceDemoPaySourceSiteOwnerV1(sources,capture,semantics,semantic,stage,source,plans,assemblyOwner,assembly);
 let sent=0;const port={async exchange(){sent++;throw Error('Capture must not be sent');}};
 try{
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'payments',path.join(root,'storage'));
  const captureParent=plans.bindOperation('Payments.DispatchOriginalCapture'),inspectParent=plans.bindOperation('Payments.ReconcilePayment');
  const captureSite=sites.bind(captureParent,sites.paths(captureParent)[0]!),inspectSite=sites.bind(inspectParent,sites.paths(inspectParent)[0]!);
  assert.throws(()=>createCommerceDemoPayDispatchOwnerV1(sources,capture,plans,sites,inspectSite,captureSite,storage!,port),code('ForeignSite'));
  const dispatch=createCommerceDemoPayDispatchOwnerV1(sources,capture,plans,sites,captureSite,inspectSite,storage,port);
  const foreign=createCommerceDemoPayDispatchOwnerV1(sources,capture,plans,sites,captureSite,inspectSite,storage,port);
  try{
   assert.throws(()=>dispatch.send({kind:'original-demopay-capture-dispatch-permit/v1-candidate'}),code('ForeignPermit'));
   native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
   auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth'));
   selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
   const entryId='Payments.CapturePaymentEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='service-'+definition.access.caller,evidence='dispatch-negative-evidence';
   const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'dispatch-negative-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
   const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
   const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'},wire=Buffer.from(JSON.stringify(input,(_k,v)=>typeof v==='bigint'?String(v):v));
   const started=await selected.begin(actor,entryId,wire,input);assert.equal(started.ok,true);if(!started.ok)return;
   runtime=await createCommerceGeneratedOperationRuntimeV1(sources,capture,stage,source,domain,baseline,plans,selected,storage,started.invocation,path.join(root,'runtime'));
   const callPath=selected.localCallPath(started.invocation,'Payments.DispatchOriginalCapture');
   const child=selected.deriveLocalCall(started.invocation,callPath,{orderId:input.orderId,attemptKey:input.attemptKey,requestFingerprint:'a'.repeat(64)});
   const txPath=plans.inspectOperation(selected.operation(child)).transactions.find(t=>t.plan.name==='MarkDispatched')?.path;assert.ok(txPath);
   const unownedExecution={kind:'applied',outcome:{kind:'committed',receipt:{kind:'observed-native-sqlite-commit/v1-candidate'},result:{kind:'Pending',attemptKey:input.attemptKey}},authority_effect:'local-source-transaction-only'} as any;
   assert.throws(()=>dispatch.prepare(unownedExecution,runtime!,selected!,started.invocation,txPath),code('ForeignOwner'));
   assert.throws(()=>dispatch.prepare(unownedExecution,runtime!,selected!,child,'$.body[0].transaction'),code('ForeignInvocation'));
   const permit=dispatch.prepare(unownedExecution,runtime,selected,child,txPath);
   assert.throws(()=>dispatch.send({...permit}),code('ForeignPermit'));
   assert.throws(()=>foreign.send(permit),code('ForeignPermit'));
   assert.throws(()=>dispatch.send(permit),code('ForeignOwner'));
   assert.throws(()=>dispatch.send(permit),code('ForeignPermit'));
   assert.equal(sent,0);
   selected.retire(child);selected.retire(started.invocation);auth.disposeActor(actor);auth.disposeEntry(entry);
  }finally{foreign.dispose();dispatch.dispose();}
 }finally{runtime?.dispose();selected?.dispose();auth?.dispose();await native?.dispose();storage?.close();sites.dispose();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
