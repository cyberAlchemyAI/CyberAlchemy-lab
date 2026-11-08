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
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceIdentityCallOwner} from '../../src/commerce/commerce-identity-call-owner.js';
import {createCommerceWorkflowCausalProjectionOwnerV1,CommerceWorkflowCausalProjectionErrorV1,
 assertOriginalCausalFingerprintFieldsV1} from
 '../../src/commerce/commerce-workflow-causal-projection-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');

test('protected Workflow steps select only their checked per-Entry causal fields',async()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'workflow-causal-projection-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(m=>m.path)),texts=captured.files.filter(f=>paths.has(f.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 const domain=createCommerceComputationDomainOwner(stage,source);
 const limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits;
 const baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits));
 const binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout');
 const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline);
 try{
  const owner=await createCommerceWorkflowCausalProjectionOwnerV1(binding,semantics,semantic,calls,stage,source,domain,baseline,directory);
  try{
   const plans=owner.plans();
   assert.equal(plans.length,13);
   assert.equal(new Set(plans.map(plan=>plan.step_name)).size,13);
   const reserve=plans.find(plan=>plan.step_name==='reserve');
   assert.equal(reserve?.entry_id,'Inventory.ReserveStockEntry');
   assert.deepEqual(reserve?.required_fields,['lines','orderId','reserveCommandId']);
   const capture=plans.find(plan=>plan.step_name==='capture');
   assert.equal(capture?.entry_id,'Payments.CapturePaymentEntry');
   assert.deepEqual(capture?.required_fields,['captureAttemptKey','currency','orderId','payableMinor']);
   const confirm=plans.find(plan=>plan.step_name==='confirm');
   assert.equal(confirm?.entry_id,'Orders.ConfirmOrderEntry');
   assert.deepEqual(confirm?.required_fields,['commandId','confirmCommandId','orderId']);
   assert.ok(plans.every(plan=>plan.binding_name==='causal'&&plan.authority_effect==='none'));
   const checked=semantics.inspect(semantic),entry=checked.entries.find(row=>row.id==='Payments.ReconcilePaymentEntry'),
    causal=entry?.access.resource_bindings[0],fingerprintTypes=new Set(domain.inspect(baseline).contract.values.refinements
     .filter(row=>row.carrier.kind==='string'&&row.min_utf8_bytes===64&&row.max_utf8_bytes===64&&
      row.pattern==='^[a-f0-9]{64}$').map(row=>row.name));
   assert.ok(causal);
   const fingerprintField=Object.entries(causal.fields).find(([,type])=>type.kind==='refinement'&&
    fingerprintTypes.has(type.name))?.[0];
   assert.ok(fingerprintField);
   const originalFingerprint='a'.repeat(64),otherFingerprint='b'.repeat(64);
   assert.doesNotThrow(()=>assertOriginalCausalFingerprintFieldsV1(causal.fields,fingerprintTypes,
    {[fingerprintField]:originalFingerprint},originalFingerprint));
   assert.throws(()=>assertOriginalCausalFingerprintFieldsV1(causal.fields,fingerprintTypes,
    {[fingerprintField]:otherFingerprint},originalFingerprint),
    (error:unknown)=>error instanceof CommerceWorkflowCausalProjectionErrorV1&&error.code==='ForeignOwner');
   assert.throws(()=>owner.inspect({kind:'original-workflow-causal-projection/v1-candidate'}),
    (error:unknown)=>error instanceof CommerceWorkflowCausalProjectionErrorV1&&error.code==='ForeignOwner');
  }finally{owner.dispose();}
 }finally{semantics.dispose(semantic);sources.dispose(capture);rmSync(directory,{recursive:true,force:true});}
});
