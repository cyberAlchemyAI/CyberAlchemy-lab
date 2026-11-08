import test from 'node:test';
import assert from 'node:assert/strict';
import {createCommerceWorkflowDispatchTransitionV1,projectCommerceWorkflowDispatchedRowV1,
 CommerceWorkflowDispatchTransitionErrorV1}
 from '../../src/commerce/commerce-workflow-dispatch-transition-v1.js';
import {CommerceWorkflowPreparedJournalProjectionErrorV1}
 from '../../src/commerce/commerce-workflow-prepared-journal-projection-v1.js';
import type {CommerceWorkflowCoordinationBindingV1}
 from '../../src/commerce/commerce-workflow-coordination-binding-v1.js';
import type {CommerceServiceStorageOwnerV1,CommerceWorkflowStepJournalV1}
 from '../../src/commerce/commerce-service-storage-v1.js';
import type {CommerceWorkflowStepIdentityOwnerV1,CommerceWorkflowStepIdentityHandleV1}
 from '../../src/commerce/commerce-workflow-step-identity-v1.js';

const immutable={consumerEntryId:'Orders.CheckoutStartEntry',occurrenceId:'event-one',orderId:'order-one',
 stepName:'reserve',commandId:'reserve-original',targetEntryId:'Inventory.ReserveStockEntry',
 requestFingerprint:'a'.repeat(64)};
const worker={id:'worker-original',epoch:3n};
const prepared={...immutable,phase:'Prepared',workerOwner:worker.id,workerEpoch:worker.epoch,
 observation:{kind:'none'},version:1n};
const transitionCode=(code:string)=>(error:unknown)=>error instanceof CommerceWorkflowDispatchTransitionErrorV1&&error.code===code;
const rowCode=(code:string)=>(error:unknown)=>error instanceof CommerceWorkflowPreparedJournalProjectionErrorV1&&error.code===code;

test('Prepared row projects exact immutable Dispatched row and version-only native update data',()=>{
 const projected=projectCommerceWorkflowDispatchedRowV1(immutable,worker,prepared);
 assert.deepEqual(projected.old,prepared);
 assert.deepEqual(projected.next,{...prepared,phase:'Dispatched',version:2n});
 assert.deepEqual(projected.changes,{phase:'Dispatched',version:2n});
 assert.equal(projected.expected_version,1n);
 assert.equal(projected.authority_effect,'none');
 assert.equal(Object.isFrozen(projected.next),true);
});

test('transition refuses stale phase, version, worker fence and forged immutable request',()=>{
 assert.throws(()=>projectCommerceWorkflowDispatchedRowV1(immutable,worker,
  {...prepared,phase:'Dispatched'}),transitionCode('StaleJournal'));
 assert.throws(()=>projectCommerceWorkflowDispatchedRowV1(immutable,worker,
  {...prepared,version:2n}),transitionCode('StaleJournal'));
 assert.throws(()=>projectCommerceWorkflowDispatchedRowV1(immutable,worker,
  {...prepared,workerOwner:'worker-other'}),transitionCode('StaleOwner'));
 assert.throws(()=>projectCommerceWorkflowDispatchedRowV1(immutable,worker,
  {...prepared,workerEpoch:4n}),transitionCode('StaleOwner'));
 assert.throws(()=>projectCommerceWorkflowDispatchedRowV1(immutable,worker,
  {...prepared,requestFingerprint:'b'.repeat(64)}),rowCode('JournalConflict'));
 assert.throws(()=>projectCommerceWorkflowDispatchedRowV1(immutable,worker,
  {...prepared,extra:'forged'}),rowCode('InvalidJournalRow'));
});

test('a shaped binding inspection cannot substitute for a genuine source binding',()=>{
 const forgedBinding={inspect(){throw Error('forged inspection must not run');},assertCurrent(){}} as unknown as CommerceWorkflowCoordinationBindingV1;
 assert.throws(()=>createCommerceWorkflowDispatchTransitionV1(forgedBinding,
  {} as CommerceServiceStorageOwnerV1,{} as CommerceWorkflowStepJournalV1,
  {} as CommerceWorkflowStepIdentityOwnerV1,{} as CommerceWorkflowStepIdentityHandleV1),
  (error:unknown)=>error instanceof Error&&/original Workflow coordination binding required/.test(error.message));
});
