/** A direct service grant cannot create a fresh workflow-protected transaction. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {DatabaseSync} from 'node:sqlite';
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
import {produceCommerceAuthNativeOwnerV1} from '../src/commerce/commerce-auth-ready-bridge-v1.js';
import {createCommerceEntryContextOwnerV1,registerCommerceEntryFixtureActorV1} from '../src/commerce/commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1} from '../src/commerce/commerce-selected-entry-auth-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');

test('a direct CapturePayment service grant leaves fresh storage and command journal empty',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-fresh-generated-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map((m:any)=>m.path)),texts=captured.files.filter((f:any)=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source),limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch'),families=createCommerceFamilyOwnerV5(models);
 const assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblyOwner.assembly();
 let native:Awaited<ReturnType<typeof produceCommerceAuthNativeOwnerV1>>|undefined,auth:Awaited<ReturnType<typeof createCommerceEntryContextOwnerV1>>|undefined;
 let selected:Awaited<ReturnType<typeof createCommerceSelectedEntryAuthOwnerV1>>|undefined,storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined;
 try{
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'payments',path.join(root,'storage'));
  const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'};
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  const entryId='Payments.CapturePaymentEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='service-'+definition.access.caller,evidence='generated-operation-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'generated-operation-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  const wire=Buffer.from(JSON.stringify(input,(_key,value)=>typeof value==='bigint'?String(value):value));
  const started=await selected.begin(actor,entryId,wire,input);
  assert.deepEqual(started,{ok:false,code:'forbidden',status:403});
  const journal=(file:string)=>{const db=new DatabaseSync(file,{readOnly:true});try{
   const table=db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='_craft_native_commands_v1'").get();
   return table?db.prepare('SELECT fingerprint,attempt,state FROM _craft_native_commands_v1').all():[];
  }finally{db.close();}};
  const storeFile=path.join(root,'storage/store.sqlite');
  assert.equal(storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:input.attemptKey}),null);
  assert.deepEqual(journal(storeFile),[]);
  await storage.reopen();
  assert.equal(storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:input.attemptKey}),null);
  assert.deepEqual(journal(storeFile),[]);
  auth.disposeActor(actor);auth.disposeEntry(entry);
 }finally{selected?.dispose();auth?.dispose();await native?.dispose();storage?.close();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
