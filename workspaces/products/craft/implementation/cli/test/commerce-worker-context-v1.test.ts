/** WorkerContext accepts only the original committed schedule claim. */
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
import {createCommerceServiceStorageOwnerV1,type CommerceWorkScheduleClaimV1} from '../src/commerce/commerce-service-storage-v1.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkerContextOwnerV1,assertCommerceWorkerContextOwnerV1} from '../src/commerce/commerce-worker-context-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(6),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('private WorkerContext rejects unissued schedule claims and cloned owners',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-worker-context-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(module=>module.path)),texts=captured.files.filter(file=>paths.has(file.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source);
 const limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
 const models=createCommerceTechnicalModelOwnerV5(),model=await models.checkTechnicalSource(candidate,'profiles/implementation.alch');
 const families=createCommerceFamilyOwnerV5(models),assemblies=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families),assembly=assemblies.assembly();
 const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
 let storage:Awaited<ReturnType<typeof createCommerceServiceStorageOwnerV1>>|undefined;
 try{
  storage=await createCommerceServiceStorageOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline,plans,families,assemblies,assembly,'orders',path.join(root,'orders'));
  const worker=createCommerceWorkerContextOwnerV1(binding,storage);
  assertCommerceWorkerContextOwnerV1(worker);
  assert.throws(()=>assertCommerceWorkerContextOwnerV1({...worker}),code('ForeignOwner'));
  assert.throws(()=>createCommerceWorkerContextOwnerV1(binding,{...storage!}),code('ForeignOwner'));
  assert.throws(()=>worker.registerCommittedClaim(Object.freeze({kind:'original-committed-work-schedule-claim/v1-candidate'}) as CommerceWorkScheduleClaimV1),code('ForeignOwner'));
  const forged={workerId:'forged',owns:()=>true,isOrdersWorker:()=>true,provesVacantOrQuiescentPredecessor:()=>true,provesNeverDispatched:()=>true};
  assert.throws(()=>worker.inspectContext(forged),code('ForeignOwner'));
  assert.throws(()=>worker.assertOrder(forged,'order-one'),code('ForeignOwner'));
  worker.dispose();assert.throws(()=>worker.assertCurrent(),code('DisposedOwner'));
 }finally{storage?.close();assemblies.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
