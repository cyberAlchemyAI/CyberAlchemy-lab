import test from 'node:test';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {inspectCommerceWorkflowObservationPlanV1,
 CommerceWorkflowObservationProposalErrorV1} from '../../src/commerce/commerce-workflow-observation-proposal-v1.js';
import {createCommerceWorkflowObservationAdmissionV1,
 assertCommerceWorkflowObservationAdmissionV1,
 CommerceWorkflowObservationAdmissionErrorV1} from '../../src/commerce/commerce-workflow-observation-admission-v1.js';

test('copied admission methods cannot become an original admission owner',()=>{
 const copied={inspect(){return {} as any;},assertCurrent(){}};
 assert.throws(()=>assertCommerceWorkflowObservationAdmissionV1(copied),
  (error:unknown)=>error instanceof CommerceWorkflowObservationAdmissionErrorV1&&error.code==='ForeignOwner');
});

test('observation admission rejects a foreign source binding before inspecting any proposal',()=>{
 const foreign={} as any;
 assert.throws(()=>createCommerceWorkflowObservationAdmissionV1(foreign,foreign,foreign,
  foreign,foreign,foreign,foreign,foreign),
  (error:unknown)=>error instanceof CoreCommerceSourceError&&error.diagnostics[0]?.code==='ForeignOwner');
});

test('checked Orders observation plan binds the original worker observation and exact input ABI',async()=>{
 const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),
  semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),
  stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 try{
  const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout'),
   workflow=binding.inspect().workflow,
   entry=semantics.inspect(semantic).entries.find(row=>row.id==='Orders.RecordCheckoutObservationEntry');
  assert.ok(entry);
  const plan=inspectCommerceWorkflowObservationPlanV1(workflow,entry);
  assert.equal(workflow.durable_state,'Orders.CheckoutProgress');
  assert.equal(plan.entry_id,'Orders.RecordCheckoutObservationEntry');
  assert.equal(plan.target,'Orders.RecordCheckoutObservation');
  assert.deepEqual(plan.parameters,['orderId','expectedOrderVersion','expectedProgressVersion','observation']);
  assert.deepEqual(plan.causal_fields,['progress']);
  assert.equal(plan.causal_binding,'causal');
  assert.throws(()=>inspectCommerceWorkflowObservationPlanV1(workflow,
   {...entry,access:{...entry.access,resource_bindings:[{...entry.access.resource_bindings[0]!,
    origin:{...entry.access.resource_bindings[0]!.origin,kind:'workflow-journal'}}]}} as typeof entry),
   (error:unknown)=>error instanceof CommerceWorkflowObservationProposalErrorV1&&
    error.code==='UnsupportedObservationCausalBinding');
 }finally{semantics.dispose(semantic);sources.dispose(capture);}
});
