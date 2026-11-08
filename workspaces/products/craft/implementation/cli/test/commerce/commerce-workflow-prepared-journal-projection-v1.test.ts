import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectCommerceWorkflowJournalRowDataV1,assertCommerceWorkflowJournalProgressVersionV1,
 CommerceWorkflowPreparedJournalProjectionErrorV1}
 from '../../src/commerce/commerce-workflow-prepared-journal-projection-v1.js';

const immutable={consumerEntryId:'Orders.CheckoutStartEntry',occurrenceId:'event-one',orderId:'order-one',
 stepName:'reserve',commandId:'reserve-original',targetEntryId:'Inventory.ReserveStockEntry',
 requestFingerprint:'a'.repeat(64)};
const currentWorker={id:'worker-new',epoch:3n};
const prepared={...immutable,phase:'Prepared',workerOwner:'worker-new',workerEpoch:3n,
 observation:{kind:'none'},version:1n};
const code=(expected:string)=>(error:unknown)=>error instanceof CommerceWorkflowPreparedJournalProjectionErrorV1&&
 error.code===expected;

test('recovered StepJournal row preserves original request identity without conferring dispatch authority',()=>{
 const fresh=inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,prepared);
 assert.equal(fresh.phase,'Prepared');assert.equal(fresh.same_current_worker,true);
 assert.equal(fresh.authority_effect,'none');
 const previous={...prepared,phase:'Dispatched',workerOwner:'worker-old',workerEpoch:2n,version:2n};
 const recovered=inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,previous);
 assert.equal(recovered.phase,'Dispatched');assert.equal(recovered.same_current_worker,false);
 assert.equal(recovered.authority_effect,'none');
 assert.throws(()=>inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,
  {...previous,requestFingerprint:'b'.repeat(64)}),code('JournalConflict'));
 assert.throws(()=>inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,
  {...prepared,observation:{kind:'some',value:{kind:'ReserveApplied'}}}),code('InvalidJournalRow'));
 assert.throws(()=>inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,
  {...prepared,phase:'Ready'}),code('InvalidJournalRow'));
 assert.throws(()=>inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,
  {...prepared,version:0n}),code('InvalidJournalRow'));
 const getter=Object.defineProperty({...prepared},'commandId',{get(){throw Error('must not run');},enumerable:true});
 assert.throws(()=>inspectCommerceWorkflowJournalRowDataV1(immutable,currentWorker,getter),code('InvalidJournalRow'));
 assert.doesNotThrow(()=>assertCommerceWorkflowJournalProgressVersionV1(5n,6n));
 assert.throws(()=>assertCommerceWorkflowJournalProgressVersionV1(5n,4n),code('StaleOwner'));
});
