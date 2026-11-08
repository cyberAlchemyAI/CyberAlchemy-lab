/** Resume selections are original-source, inert handles, never dispatch permits.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1} from '../../src/commerce/commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../../src/profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from '../../src/commerce/commerce-binding-assembly-v1.js';
import {createCommerceServiceStorageOwnerV1} from '../../src/commerce/commerce-service-storage-v1.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkerContextOwnerV1} from '../../src/commerce/commerce-worker-context-v1.js';
import {createCommerceWorkflowResumeSelectorV1,assertCommerceWorkflowResumeSelectorV1} from '../../src/commerce/commerce-workflow-resume-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
const code=(name:string)=>(error:any)=>error?.code===name||error?.diagnostics?.[0]?.code===name;

test('checked Workflow resume cases retain source order while a foreign worker cannot select',async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-workflow-resume-'));
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
  const worker=createCommerceWorkerContextOwnerV1(binding,storage),selector=createCommerceWorkflowResumeSelectorV1(binding,worker);
  try{
   assertCommerceWorkflowResumeSelectorV1(selector);
   assert.throws(()=>assertCommerceWorkflowResumeSelectorV1({...selector}),code('ForeignOwner'));
   assert.throws(()=>createCommerceWorkflowResumeSelectorV1({...binding},worker),code('ForeignOwner'));
   assert.throws(()=>createCommerceWorkflowResumeSelectorV1(binding,{...worker}),code('ForeignOwner'));
   const cases=selector.inspectSourceCases();
   assert.equal(cases.length,16);
   assert.deepEqual(cases.slice(2,5).map(row=>({state:row.state,guarded:row.guarded,action:row.action})),[
    {state:'AwaitingPayment',guarded:true,action:{kind:'step',target:'mark-capture-dispatched'}},
    {state:'AwaitingPayment',guarded:true,action:{kind:'step',target:'capture'}},
    {state:'AwaitingPayment',guarded:true,action:{kind:'step',target:'reconcile-payment'}},
   ]);
   const fake={workerId:'forged',owns:()=>true,isOrdersWorker:()=>true,provesVacantOrQuiescentPredecessor:()=>true,provesNeverDispatched:()=>true};
   assert.throws(()=>selector.select({order:{id:'order-one'},progress:{orderId:'order-one',state:'AwaitingStock',version:1n,workerOwner:{kind:'some',value:'forged'},workerEpoch:1n}},fake),code('ForeignOwner'));
   assert.throws(()=>selector.inspectSelection({kind:'source-selected-workflow-resume/v1-candidate'}),code('ForeignOwner'));
   selector.dispose();assert.throws(()=>selector.assertCurrent(),code('DisposedOwner'));
  }finally{worker.dispose();}
 }finally{storage?.close();assemblies.dispose();plans.dispose();models.dispose(model);semantics.dispose(semantic);sources.dispose(capture);rmSync(root,{recursive:true,force:true});}
});
