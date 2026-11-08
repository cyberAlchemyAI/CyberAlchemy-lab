/** Original application selection to one actual service SQLite transaction. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createCoreCommerceSourceOwner} from '../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../src/commerce/commerce-binding-assembly-v1.js';
import {createCommerceServiceStorageOwnerV1,assertCommerceServiceStorageOwnerV1} from '../src/commerce/commerce-service-storage-v1.js';
import {deriveCommerceCommandTransactionNamespaceV1} from '../src/commerce/commerce-command-identity-binding-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('selected original service executes one real source transaction and replays the persisted command after reopen',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-service-storage-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined;
 try{
  await assert.rejects(createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,{...assembly} as any,'payments',path.join(root,'foreign-storage')),code('ForeignOwner'));
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'payments',path.join(root,'storage'));
  assertCommerceServiceStorageOwnerV1(storage);
  const inspection=storage.inspect();assert.equal(inspection.service,'payments');assert.equal(inspection.family_sha256,assemblyOwner.inspect(assembly).selected_family_sha256);
  assert.equal(inspection.native_basis_qualified,false);assert.equal(inspection.imported_output_qualified,false);assert.equal(inspection.bound_application_qualified,false);
  await assert.rejects(storage.bindTransaction('Orders.PlaceOrder','AcceptCheckout','Orders.PlaceOrderEntry'),code('ForeignOwner'));
  await assert.rejects(storage.bindTransaction('Payments.CapturePayment','PrepareCapture','Orders.PlaceOrderEntry'),code('ForeignOwner'));
  const tx=await storage.bindTransaction('Payments.CapturePayment','PrepareCapture','Payments.CapturePaymentEntry');
  const key={logicalEntryId:'Payments.CapturePaymentEntry',principalId:'component-service-principal',commandId:'component-command-one',fingerprint:'a'.repeat(64),transactionNamespace:deriveCommerceCommandTransactionNamespaceV1('Payments.CapturePayment','PrepareCapture')};
  const frame={orderId:'payment-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD',requestFingerprint:'a'.repeat(64)};
  assert.throws(()=>storage!.apply({...tx},key,frame),code('ForeignOwner'));
  assert.throws(()=>storage!.apply(tx,{...key,logicalEntryId:'Orders.PlaceOrderEntry'},frame),code('ForeignOwner'));
  let touched=0;const accessor=Object.defineProperty({...key},'fingerprint',{get(){touched++;return key.fingerprint;},enumerable:true});
  assert.throws(()=>storage!.apply(tx,accessor,frame),code('InvalidContract'));assert.equal(touched,0);
  const applied=storage.apply(tx,key,frame);assert.equal(applied.kind,'applied');if(applied.kind!=='applied')return;
  assert.equal(applied.outcome.kind,'committed');
  const row=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:'attempt-one'}) as any;
  assert.ok(row);assert.equal(row.orderId,'payment-one');assert.equal(row.amountMinor,25n);assert.equal(row.status,'Intent');
  await storage.reopen();assert.equal(storage.inspect().store_id,inspection.store_id);
  const replay=storage.apply(tx,key,frame);assert.equal(replay.kind,'not-claimed');if(replay.kind==='not-claimed')assert.equal(replay.claim.kind,'recorded');
  assert.equal((storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:'attempt-one'}) as any).version,1n);
  const physical=new DatabaseSync(path.join(root,'storage/store.sqlite'));
  try{physical.prepare('UPDATE _craft_native_store_v1 SET store_id=? WHERE id=1').run('foreign-store-id');}finally{physical.close();}
  await assert.rejects(storage.reopen(),code('StaleOwner'));
 }finally{storage?.close();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
