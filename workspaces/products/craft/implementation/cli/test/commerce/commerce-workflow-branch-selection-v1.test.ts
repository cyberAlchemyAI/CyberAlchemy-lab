import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {createCommerceWorkflowCoordinationBindingV1} from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import {createCommerceWorkflowBranchSelectionOwnerV1,CommerceWorkflowBranchSelectionErrorV1}
 from '../../src/commerce/commerce-workflow-branch-selection-v1.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');
const rejected=(code:string)=>({kind:'Rejected',value:{commandId:'command-one',orderId:'order-one',
 requestFingerprint:'a'.repeat(64),code}});

test('original Workflow branch order selects distinct guarded results and suspends on unmatched or invalid data',async()=>{
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),captured=sources.inspect(capture);
 const paths=new Set(captured.reconstruction.modules.map(row=>row.path)),texts=captured.files.filter(row=>paths.has(row.path));
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),
  stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch'),
  domain=createCommerceComputationDomainOwner(stage,source),
  limits=JSON.parse(readFileSync(path.join(candidate,'contracts/compute-bounds.json'),'utf8')).computation.limits,
  baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',limits)),
  binding=createCommerceWorkflowCoordinationBindingV1(sources,capture,stage,source,'Orders.Checkout.Checkout'),
  owner=createCommerceWorkflowBranchSelectionOwnerV1(binding,semantics,semantic,domain,baseline);
 try{
  const reserve=owner.plans().find(row=>row.step_name==='reserve');
  assert.ok(reserve);
  assert.equal(reserve.branches[1]?.guard_path,'$.steps[0].branches[1].guard');
  assert.equal(reserve.branches[1]?.observe_path,'$.steps[0].branches[1].observe');
  assert.equal(reserve.branches[2]?.channel,'variant');

  const context={snapshot:{progress:{reserveCommandId:'command-one'}}};
  const matched=owner.interpret('reserve',{channel:'result',value:rejected('StockUnavailable')},context);
  assert.equal(matched.outcome,'selected');
  assert.equal(matched.branch_index,1);
  assert.deepEqual(matched.action,{kind:'step',target:'cancel-stock'});
  assert.deepEqual(JSON.parse(JSON.stringify(matched.observation)),
   {kind:'ReserveRejected',rejection:rejected('StockUnavailable').value});
  assert.equal(matched.authority_effect,'none');

  const fallback=owner.interpret('reserve',{channel:'result',value:rejected('ReservationConflict')},context);
  assert.equal(fallback.outcome,'selected');
  assert.equal(fallback.branch_index,2);
  assert.deepEqual(fallback.action,{kind:'step',target:'review'});
  assert.equal((fallback.observation as {kind:string}).kind,'EvidenceConflict');

  const failed=owner.interpret('reserve',{channel:'call-failure'},context);
  assert.equal(failed.outcome,'selected');
  assert.equal(failed.channel,'call-failure');
  assert.deepEqual(failed.action,{kind:'step',target:'reconcile-stock'});
  assert.deepEqual(JSON.parse(JSON.stringify(failed.observation)),{kind:'ReserveUnknown',commandId:'command-one'});

  const invalid=owner.interpret('reserve',{channel:'result',value:{kind:'Rejected',value:{code:'StockUnavailable'}}},context);
  assert.equal(invalid.outcome,'suspend-same-persisted-state');
  assert.equal(invalid.reason,'invalid-result');
  assert.equal(invalid.action,null);
  assert.equal(invalid.original_journal,'retain');
  const privateShape=owner.interpret('reserve',{channel:'result',value:{kind:'Rejected',fields:{value:rejected('StockUnavailable').value}}},context);
  assert.equal(privateShape.outcome,'suspend-same-persisted-state');
  assert.equal(privateShape.reason,'invalid-result');
  const unhandled=owner.interpret('reserve',{channel:'unavailable'},context);
  assert.equal(unhandled.outcome,'suspend-same-persisted-state');
  assert.equal(unhandled.reason,'unhandled-result');
  assert.equal(unhandled.action,null);
  const orderView={id:'order-one',customerId:'customer-one',quoteId:'quote-one',
   currency:'USD',payableMinor:10n,lines:[{sku:'sku-one',quantity:1n}],
   status:'Confirmed',version:3n};
  const confirmed=owner.interpret('confirm',{channel:'result',value:orderView},{});
  assert.equal(confirmed.outcome,'selected');
  assert.deepEqual(confirmed.action,{kind:'finish',target:'confirmed'});
  assert.equal(confirmed.observation,null);
  const wrongStatus=owner.interpret('confirm',{channel:'result',value:{...orderView,status:'Cancelled'}},{});
  assert.equal(wrongStatus.outcome,'suspend-same-persisted-state');
  assert.equal(wrongStatus.reason,'failed-require');
  const cancelled=owner.interpret('cancel-payment',
   {channel:'result',value:{...orderView,status:'Cancelled'}},{});
  assert.equal(cancelled.outcome,'selected');
  assert.deepEqual(cancelled.action,{kind:'finish',target:'cancelled'});
  assert.equal(cancelled.observation,null);
  assert.throws(()=>owner.interpret('unknown',{channel:'call-failure'},context),
   (error:unknown)=>error instanceof CommerceWorkflowBranchSelectionErrorV1&&error.code==='UnknownReference');
 }finally{owner.dispose();semantics.dispose(semantic);sources.dispose(capture);}
});
