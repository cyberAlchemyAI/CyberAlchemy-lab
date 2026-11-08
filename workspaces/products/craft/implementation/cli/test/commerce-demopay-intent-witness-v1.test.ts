/** A source-bound DemoPay attempt is observed from real committed Payments SQLite. */
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
import {deriveCommerceCommandTransactionNamespaceV1} from '../src/commerce/commerce-command-identity-binding-v1.js';
import {createCommerceDemoPaySourceSiteOwnerV1} from '../src/commerce/commerce-demopay-source-site-v1.js';
import {createCommerceDemoPayIntentWitnessOwnerV1,assertCommerceDemoPayIntentWitnessOwnerV1} from '../src/commerce/commerce-demopay-intent-witness-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('committed Prepared intent joins exact Capture site, survives reopen, and grants no dispatch authority',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-demopay-intent-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblies=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblies.assembly();
 let storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined;
 try{
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblies,assembly,'payments',path.join(root,'payments'));
  const sites=createCommerceDemoPaySourceSiteOwnerV1(sources,capture,semantics,semantic,stage,source,plans,assemblies,assembly);
  const parent=plans.bindOperation('Payments.DispatchOriginalCapture'),site=sites.bind(parent,sites.paths(parent)[0]!);
  const witnesses=createCommerceDemoPayIntentWitnessOwnerV1(sites,storage);
  assertCommerceDemoPayIntentWitnessOwnerV1(witnesses);
  const request={attemptKey:'attempt-one',orderId:'order-one',amountMinor:25n,currency:'USD' as const,requestFingerprint:'a'.repeat(64)};
  assert.throws(()=>witnesses.observe(site,request,'Prepared'),code('MissingIntent'));
  const tx=await storage.bindTransaction('Payments.CapturePayment','PrepareCapture','Payments.CapturePaymentEntry');
  const key={logicalEntryId:'Payments.CapturePaymentEntry',principalId:'component-service-principal',commandId:'component-command-one',fingerprint:request.requestFingerprint,transactionNamespace:deriveCommerceCommandTransactionNamespaceV1('Payments.CapturePayment','PrepareCapture')};
  const applied=storage.apply(tx,key,{...request});assert.equal(applied.kind,'applied');if(applied.kind!=='applied')return;assert.equal(applied.outcome.kind,'committed');
  const witness=witnesses.observe(site,request,'Prepared'),view=witnesses.inspect(witness);
  assert.equal(view.target,'Shop.DemoPay.Capture');assert.equal(view.dispatch_state,'Prepared');assert.equal(view.version,1n);
  assert.match(view.qualification,/no-command-owner-or-provider-dispatch-permit/);
  assert.throws(()=>witnesses.inspect({...witness}),code('ForeignWitness'));
  assert.throws(()=>witnesses.observe({...site},request,'Prepared'),code('ForeignSite'));
  assert.throws(()=>witnesses.observe(site,{...request,amountMinor:26n},'Prepared'),code('ForeignRequest'));
  assert.throws(()=>witnesses.observe(site,{...request,requestFingerprint:'b'.repeat(64)},'Prepared'),code('ForeignRequest'));
  assert.throws(()=>witnesses.observe(site,request,'Dispatched'),code('WrongDispatchState'));
  const replay=storage.apply(tx,key,{...request});assert.equal(replay.kind,'not-claimed');if(replay.kind==='not-claimed')assert.equal(replay.claim.kind,'recorded');
  assert.equal(witnesses.inspect(witness).version,1n);
  await storage.reopen();assert.equal(witnesses.inspect(witness).version,1n);
  storage.close();assert.throws(()=>witnesses.inspect(witness),code('DisposedOwner'));
 }finally{storage?.close();assemblies.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
