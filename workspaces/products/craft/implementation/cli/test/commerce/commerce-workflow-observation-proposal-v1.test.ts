import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {inspectCommerceWorkflowObservationPlanV1,
 createCommerceWorkflowObservationProposalOwnerV1,
 CommerceWorkflowObservationProposalErrorV1} from '../../src/commerce/commerce-workflow-observation-proposal-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
const code=(expected:string)=>(error:unknown)=>error instanceof CommerceWorkflowObservationProposalErrorV1&&error.code===expected;

test('original observation Entry plan preserves worker snapshot versions and rejects unowned result evidence',async()=>{
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),
  semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),
  stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 try{
  const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout'),
   workflow=binding.inspect().workflow,
   entry=semantics.inspect(semantic).entries.find(row=>row.id==='Orders.RecordCheckoutObservationEntry');
  assert.ok(entry);
  const plan=inspectCommerceWorkflowObservationPlanV1(workflow,entry);
  assert.equal(plan.entry_id,'Orders.RecordCheckoutObservationEntry');
  assert.equal(plan.target,'Orders.RecordCheckoutObservation');
  assert.equal(plan.snapshot_binding,'snapshot');
  assert.deepEqual(plan.parameters,['orderId','expectedOrderVersion','expectedProgressVersion','observation']);
  assert.equal(plan.causal_binding,'causal');
  assert.deepEqual(plan.causal_fields,['progress']);
  assert.equal(plan.authority_effect,'none');
  assert.throws(()=>inspectCommerceWorkflowObservationPlanV1(workflow,
   {...entry,access:{...entry.access,resource_bindings:[]}}),code('InvalidContract'));
  assert.throws(()=>createCommerceWorkflowObservationProposalOwnerV1(binding,semantics,semantic,
   {} as any,{} as any,{} as any,{} as any,{} as any,{} as any),
   (error:unknown)=>!!error&&typeof error==='object'&&'code'in error&&error.code==='ForeignOwner');
 }finally{semantics.dispose(semantic);sources.dispose(capture);}
});
