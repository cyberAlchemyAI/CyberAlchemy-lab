/** An authorized local child can name its original source transaction, but
 * cannot use the component storage apply path as a command authority. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
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
import {createCommerceSelectedEntryAuthOwnerV1} from '../src/commerce/commerce-selected-entry-auth-v1.js';
import {createCommerceServiceStorageOwnerV1} from '../src/commerce/commerce-service-storage-v1.js';
import {seedCommerceAuthFixtureDatabaseV1} from './support/commerce-auth-fixture-provider-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;
function callPath(plan:unknown,target:string):string {
 let result:string|undefined;
 const walk=(v:any,at:string)=>{if(!v||typeof v!=='object'||result)return;if(v.target===target&&v.authorization==='original-local-context-forwarding-required'){result=at;return;}if(Array.isArray(v))v.forEach((x,i)=>walk(x,at+'['+i+']'));else for(const [k,x] of Object.entries(v))walk(x,at+'.'+k);};
 walk(plan,'$');assert.ok(result);return result;
}

test('selected Auth child binds its local storage transaction without gaining command authority',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-local-storage-'));
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
  native=await produceCommerceAuthNativeOwnerV1(path.join(root,'native-auth'));
  auth=await createCommerceEntryContextOwnerV1(sources,capture,stage,source,domain,baseline,native,path.join(root,'auth'));
  selected=await createCommerceSelectedEntryAuthOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,assemblyOwner,assembly,auth,path.join(root,'selected'));
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblyOwner,assembly,'payments',path.join(root,'storage'));
  const entryId='Payments.CapturePaymentEntry',entry=auth.bindEntry(entryId),definition=auth.inspectEntry(entry),subject='service-'+definition.access.caller,evidence='local-storage-evidence';
  const fixture=seedCommerceAuthFixtureDatabaseV1(native,{subject,evidence,session:'local-storage-session',routes:[{entry:entryId,permission:definition.access.auth_permission}]});
  const actor=registerCommerceEntryFixtureActorV1(auth,fixture.handle,{subject,evidence,principal_kind:'service',service_id:definition.access.caller,scope:definition.access.auth_permission.scope});
  const input={orderId:'order-one',attemptKey:'attempt-one',amountMinor:25n,currency:'USD'},wire=Buffer.from(JSON.stringify(input,(_k,v)=>typeof v==='bigint'?String(v):v));
  const started=await selected.begin(actor,entryId,wire,input);assert.equal(started.ok,true,JSON.stringify(started));if(!started.ok)return;
  const child=selected.deriveLocalCall(started.invocation,callPath(plans.inspectOperation(selected.operation(started.invocation)).plan,'Payments.DispatchOriginalCapture'),{orderId:'order-one',attemptKey:'attempt-one',requestFingerprint:'a'.repeat(64)});
  await assert.rejects(storage.bindLocalTransaction(selected,started.invocation,'PrepareCapture'),code('ForeignOwner'));
  await assert.rejects(storage.bindLocalTransaction(selected,{...child} as any,'MarkDispatched'),code('ForeignOwner'));
  await assert.rejects(storage.bindLocalTransaction(selected,child,'NoSuchTransaction'),code('UnknownReference'));
  const bound=await storage.bindLocalTransaction(selected,child,'MarkDispatched'),view=storage.inspectLocalTransaction(bound);
  assert.equal(view.operation,'Payments.DispatchOriginalCapture');assert.equal(view.root_entry,entryId);assert.equal(view.transaction,'MarkDispatched');assert.equal(view.local_depth,1);
  assert.equal(view.authority_effect,'none');assert.equal(view.source_capture_sha256,storage.inspect().source_capture_sha256);
  assert.throws(()=>storage!.inspectLocalTransaction({...bound}),code('ForeignOwner'));
  assert.throws(()=>storage!.apply(bound as any,{logicalEntryId:entryId,principalId:'service-orders',commandId:'forbidden',fingerprint:'a'.repeat(64),transactionNamespace:'1'.repeat(64)},{}),code('ForeignOwner'));
  await storage.reopen();assert.equal(storage.inspectLocalTransaction(bound).transaction,'MarkDispatched');
  selected.retire(child);assert.throws(()=>storage!.inspectLocalTransaction(bound),code('ForeignOwner'));
  selected.retire(started.invocation);auth.disposeActor(actor);auth.disposeEntry(entry);
  // Same-size write and restore still changes the captured physical identity.
  const generated=path.join(root,'storage/repository/service-repositories.js'),before=readFileSync(generated);
  const changed=Buffer.from(before);changed[0]=changed[0]===32?33:32;writeFileSync(generated,changed);
  assert.throws(()=>storage!.assertCurrent(),code('StaleOwner'));
  writeFileSync(generated,before);assert.throws(()=>storage!.assertCurrent(),code('StaleOwner'));
 }finally{storage?.close();selected?.dispose();auth?.dispose();await native?.dispose();assemblyOwner.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
