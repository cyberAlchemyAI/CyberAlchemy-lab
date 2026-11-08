/** Original selected Query execution with real generated SQLite rows. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
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
import {createCommerceSourceQueryRuntimeV1,assertCommerceSourceQueryRuntimeV1} from '../src/commerce/commerce-source-query-runtime-v1.js';
import {createCommerceSourceQueryOutputCodecV1} from '../src/commerce/commerce-source-query-output-codec-v1.js';
import {deriveCommerceCommandTransactionNamespaceV1} from '../src/commerce/commerce-command-identity-binding-v1.js';
const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url)),candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;
const structural=(value:any):any=>Array.isArray(value)?value.map(structural):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([key,child])=>[key,structural(child)])):value;
test('selected local Query reads one actual payment row and keeps WorkerContext fail-closed',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-source-query-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture),paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline),models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models),assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let payments:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined,orders:typeof payments;
 try{
  payments=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'payments',path.join(root,'payments'));
  const read=plans.bindRead('Payments.ReadPayment'),codec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,read),query=createCommerceSourceQueryRuntimeV1(stage,source,plans,read,domain,baseline,payments,codec);
  assertCommerceSourceQueryRuntimeV1(query);assert.throws(()=>assertCommerceSourceQueryRuntimeV1({...query}),code('ForeignOwner'));
  assert.deepEqual(query.execute({orderId:'order-one',attemptKey:'attempt-one'}),{kind:'returned',value:{kind:'none'},qualification:'source-selected-internal-query-result;entry-and-worker-custody-separate'});
  assert.throws(()=>query.execute({orderId:'order-one',attemptKey:'attempt-one',sql:'DROP TABLE x'} as any),code('InputType'));
  assert.throws(()=>payments!.executeSourceQuery({...read},{}),code('ForeignOwner'));
  const tx=await payments.bindTransaction('Payments.CapturePayment','PrepareCapture','Payments.CapturePaymentEntry'),key={logicalEntryId:'Payments.CapturePaymentEntry',principalId:'query-fixture',commandId:'prepare-one',fingerprint:'a'.repeat(64),transactionNamespace:deriveCommerceCommandTransactionNamespaceV1('Payments.CapturePayment','PrepareCapture')},frame={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD',requestFingerprint:'a'.repeat(64)},committed=payments.apply(tx,key,frame);
  assert.equal(committed.kind,'applied');if(committed.kind==='applied')assert.equal(committed.outcome.kind,'committed');
  const result=query.execute({orderId:'order-one',attemptKey:'attempt-one'});assert.equal(result.kind,'returned');if(result.kind==='returned'){assert.equal((result.value as any).kind,'some');assert.deepEqual(structural((result.value as any).value),{attemptKey:'attempt-one',orderId:'order-one',amountMinor:25n,currency:'USD',requestFingerprint:'a'.repeat(64),status:'Intent',providerReference:{kind:'none'},version:1n});}
  assert.equal(query.execute({orderId:'wrong-order',attemptKey:'attempt-one'}).kind,'returned');
  orders=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'orders',path.join(root,'orders'));
  const workerRead=plans.bindRead('Orders.ReadCheckoutSnapshot'),workerCodec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,workerRead),workerQuery=createCommerceSourceQueryRuntimeV1(stage,source,plans,workerRead,domain,baseline,orders,workerCodec);
  assert.throws(()=>workerQuery.execute({orderId:'order-one'}),code('NativeContextCustodyRequired'));
  assert.throws(()=>createCommerceSourceQueryRuntimeV1(stage,source,plans,read,domain,baseline,orders!,codec),code('ForeignOwner'));
  workerQuery.dispose();query.dispose();assert.throws(()=>query.execute({orderId:'order-one',attemptKey:'attempt-one'}),code('DisposedOwner'));workerCodec.dispose();codec.dispose();
 }finally{orders?.close();payments?.close();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
