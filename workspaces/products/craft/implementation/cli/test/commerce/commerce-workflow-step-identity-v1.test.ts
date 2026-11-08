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
import {createCommerceWorkflowStepIdentityOwnerV1,CommerceWorkflowStepIdentityErrorV1} from '../../src/commerce/commerce-workflow-step-identity-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');

test('all checked remote Workflow steps have one source-derived stable identity companion',async()=>{
 const directory=mkdtempSync(path.join(tmpdir(),'workflow-step-identity-'));
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
  const owner=await createCommerceWorkflowStepIdentityOwnerV1(binding,semantics,semantic,calls,stage,source,domain,baseline,directory);
  try{
   const plans=owner.plans();
   assert.equal(plans.length,13);
   assert.equal(new Set(plans.map(plan=>plan.step_name)).size,13);
   assert.deepEqual(plans.find(plan=>plan.step_name==='reserve')?.identity_source_step,'reconcile-stock');
   assert.deepEqual(plans.find(plan=>plan.step_name==='confirm')?.identity_source_step,'inspect-confirm');
   assert.deepEqual(plans.find(plan=>plan.step_name==='cancel-stock')?.identity_source_step,'inspect-cancel');
   assert.deepEqual(plans.find(plan=>plan.step_name==='cancel-payment')?.identity_source_step,'inspect-cancel');
   assert.equal(plans.find(plan=>plan.step_name==='confirm')?.direct_command_argument_path,null);
   assert.equal(plans.find(plan=>plan.step_name==='reserve')?.direct_command_argument_path,
    '$.steps[0].call.arguments[1].value');
   assert.ok(plans.every(plan=>plan.command_argument_path!==plan.fingerprint_argument_path&&
    plan.order_argument_path!==plan.command_argument_path&&plan.authority_effect==='none'));
   assert.throws(()=>owner.inspect({kind:'original-workflow-step-identity/v1-candidate'}),
    (error:unknown)=>error instanceof CommerceWorkflowStepIdentityErrorV1&&error.code==='ForeignOwner');
  }finally{owner.dispose();}
 }finally{semantics.dispose(semantic);sources.dispose(capture);rmSync(directory,{recursive:true,force:true});}
});
