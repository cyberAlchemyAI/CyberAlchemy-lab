import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {test} from 'node:test';
import {GenericWorkflowStore,deriveWorkflowInstance} from '../../src/generic/workflow-store.ts';

const hash=value=>createHash('sha256').update(value).digest('hex');
const owner={store_id:'reviewdesk-workflows',owner_service:'ReviewDeskService',compatibility_sha256:hash('source-profile-v1')};
const identity=(suffix='one')=>({
  workflow_id:'ReviewDesk.ApprovalFlow',owner_service:'ReviewDeskService',
  source_capture_sha256:hash('source-v1'),profile_sha256:hash('profile-v1'),
  contract_sha256:hash('workflow-v1'),correlation_name:'requestId',
  correlation_canonical_json:JSON.stringify(`request-${suffix}`),
  start_client_key:`start-${suffix}`,
  start_command_tuple_sha256:hash(`start-${suffix}`),input_canonical_json:JSON.stringify({requestId:`request-${suffix}`}),
  steps:[
    {name:'charge',entry_id:'Payments.Charge',entry_contract_sha256:hash('charge-entry'),kind:'provider',binding_sha256:hash('write-binding'),
      compensation_entry_id:'Payments.Refund',compensation_contract_sha256:hash('refund-entry')},
    {name:'approve',entry_id:'ReviewDesk.Approve',entry_contract_sha256:hash('approve-entry'),kind:'operation',
      compensation_entry_id:'ReviewDesk.Revoke',compensation_contract_sha256:hash('revoke-entry')},
    {name:'notify',entry_id:'ReviewDesk.ReceiveNotification',entry_contract_sha256:hash('event-entry'),kind:'event',binding_sha256:hash('event-binding')}
  ]
});
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));

test('C13 immutable run/source/step identities and fenced ordered progress',async()=>{
  const db=new DatabaseSync(':memory:');
  try{
    const store=new GenericWorkflowStore(db,owner);
    const source=identity();
    const id=deriveWorkflowInstance(source);
    assert.deepEqual(store.schedule(source),{instance_sha256:id,created:true});
    assert.deepEqual(store.schedule(source),{instance_sha256:id,created:false});
    assert.throws(()=>store.schedule({...source,input_canonical_json:'{"extra":"changed","requestId":"request-one"}'}),/INSTANCE_COLLISION/);
    assert.throws(()=>store.schedule({...source,input_canonical_json:'{"requestId":"changed"}'}),/CORRELATION_INPUT/);
    const first=store.claimNext(100);
    assert.equal(first.instance_sha256,id);
    assert.equal(store.inspect(id).state,'claimed');
    assert.throws(()=>store.prepareStep(first,'approve',hash('wrong'),hash('input')),/STEP_ORDER/);
    store.prepareStep(first,'charge',hash('charge-original-command'),hash('charge-input'));
    assert.equal(store.inspect(id).state,'step-prepared');
    assert.throws(()=>store.prepareStep(first,'charge',hash('new-command'),hash('charge-input')),/TRANSITION/);
    await pause(110);
    const second=store.claimNext(1000);
    assert.equal(second.fence,first.fence+1);
    assert.equal(store.inspect(id).state,'step-prepared');
    assert.throws(()=>store.commitStep(first,hash('success')),/STALE_CLAIM/);
    store.suspendUnknown(second);
    assert.equal(store.inspect(id).state,'suspended-unknown');
    store.commitStep(second,hash('original-provider-result'));
    store.prepareStep(second,'approve',hash('approve-original-command'),hash('approve-input'));
    store.commitStep(second,hash('approve-result'));
    store.waitForEvent(second,'notify');
    assert.throws(()=>store.complete(second),/TRANSITION/);
    store.commitEvent(second,hash('event-occurrence'),hash('consumer-command'));
    store.complete(second);
    assert.equal(store.inspect(id).state,'completed');
    assert.equal(store.inspect(id).lease_until_ms,0);
    assert.equal(store.claimNext(1000),null);
  }finally{db.close();}
});

test('C13 crash/reopen preserves prepared compensation and rejects new tuple',async()=>{
  const dir=mkdtempSync(join(tmpdir(),'c13-workflow-store-'));
  const file=join(dir,'journal.sqlite');
  try{
    const db=new DatabaseSync(file);
    const store=new GenericWorkflowStore(db,owner);
    const id=store.schedule(identity('compensation')).instance_sha256;
    const claim=store.claimNext(100);
    store.prepareStep(claim,'charge',hash('charge-command'),hash('charge-input'));
    store.commitStep(claim,hash('charge-result'));
    store.beginCompensation(claim);
    store.prepareCompensation(claim,'charge',hash('refund-command'),hash('refund-input'));
    db.close();
    const reopenedDb=new DatabaseSync(file);
    try{
      const reopened=new GenericWorkflowStore(reopenedDb,owner);
      assert.equal(reopened.inspect(id).state,'compensating');
      assert.equal(JSON.parse(reopened.inspect(id).history.at(-1).commitment_json).command_tuple_sha256,
        hash('refund-command'));
      await pause(110);
      const resumed=reopened.claimNext(1000);
      assert.equal(resumed.fence,claim.fence+1);
      assert.throws(()=>reopened.prepareCompensation(resumed,'charge',hash('second-refund'),hash('input')),
        /COMPENSATION_PENDING/);
      reopened.commitCompensation(resumed,hash('refund-result'));
      reopened.finishCompensation(resumed);
      assert.equal(reopened.inspect(id).state,'compensated');
      assert.throws(()=>new GenericWorkflowStore(reopenedDb,{...owner,compatibility_sha256:hash('other')}),
        /EPOCH_IDENTITY/);
    }finally{reopenedDb.close();}
  }finally{rmSync(dir,{recursive:true,force:true});}
});

test('C13 changed physical journal is rejected before a further transition',()=>{
  const db=new DatabaseSync(':memory:');
  try{
    const store=new GenericWorkflowStore(db,owner);
    const id=store.schedule(identity('tamper')).instance_sha256;
    db.prepare('UPDATE _craft_workflow_instances_v1 SET state=? WHERE instance_sha256=?').run('completed',id);
    assert.throws(()=>store.inspect(id),/STORED_STATE|HISTORY_MISMATCH|EPOCH_DRIFT/);
    assert.throws(()=>store.claimNext(1000),/STORED_STATE|HISTORY_MISMATCH|EPOCH_DRIFT/);
  }finally{db.close();}
});

test('C13 lease renewal invalidates the old handle and compensation reverses committed commands',()=>{
  const db=new DatabaseSync(':memory:');
  try{
    const store=new GenericWorkflowStore(db,owner);
    const id=store.schedule(identity('reverse')).instance_sha256;
    let claim=store.claimNext(1000);
    const renewed=store.renewClaim(claim,1000);
    assert.equal(renewed.fence,claim.fence);
    assert.ok(renewed.lease_until_ms>claim.lease_until_ms);
    assert.throws(()=>store.prepareStep(claim,'charge',hash('old'),hash('input')),/STALE_CLAIM/);
    claim=renewed;
    store.prepareStep(claim,'charge',hash('charge-command'),hash('charge-input'));
    store.commitStep(claim,hash('charge-result'));
    store.prepareStep(claim,'approve',hash('approve-command'),hash('approve-input'));
    store.commitStep(claim,hash('approve-result'));
    store.waitForEvent(claim,'notify');
    store.beginCompensation(claim);
    assert.equal(store.inspect(id).step_index,1);
    assert.throws(()=>store.prepareCompensation(claim,'charge',hash('refund'),hash('input')),
      /COMPENSATION_ORDER/);
    store.prepareCompensation(claim,'approve',hash('revoke-command'),hash('revoke-input'));
    store.commitCompensation(claim,hash('revoke-result'));
    assert.equal(store.inspect(id).step_index,0);
    store.prepareCompensation(claim,'charge',hash('refund-command'),hash('refund-input'));
    store.commitCompensation(claim,hash('refund-result'));
    store.finishCompensation(claim);
    assert.equal(store.inspect(id).state,'compensated');
  }finally{db.close();}
});

test('C13 one long step continues only with its refreshed fenced lease',()=>{
  const db=new DatabaseSync(':memory:');
  const originalNow=Date.now;
  let now=originalNow();
  Date.now=()=>now;
  try{
    const store=new GenericWorkflowStore(db,owner);
    const id=store.schedule(identity('long-step')).instance_sha256;
    const initial=store.claimNext(1000);
    now+=900;
    const beforePrepare=store.renewClaim(initial,1000);
    assert.equal(beforePrepare.fence,initial.fence);
    assert.throws(()=>store.prepareStep(initial,'charge',hash('command'),hash('input')),/STALE_CLAIM/);
    store.prepareStep(beforePrepare,'charge',hash('command'),hash('input'));
    now+=900;
    const beforeCommit=store.renewClaim(beforePrepare,1000);
    assert.equal(beforeCommit.fence,initial.fence);
    assert.throws(()=>store.commitStep(beforePrepare,hash('result')),/STALE_CLAIM/);
    store.commitStep(beforeCommit,hash('result'));
    assert.equal(store.inspect(id).state,'step-committed');
  }finally{Date.now=originalNow;db.close();}
});

test('C13 skips a noncompensable provider step in needed-compensations-only recovery',()=>{
  const db=new DatabaseSync(':memory:');
  try{
    const store=new GenericWorkflowStore(db,owner);
    const source=identity('provider-failed');
    const steps=source.steps.map(step=>step.name==='approve'?{
      name:'capture',entry_id:'Payments.Capture',entry_contract_sha256:hash('capture-entry'),kind:'provider',binding_sha256:hash('capture-binding')
    }:step);
    const id=store.schedule({...source,steps}).instance_sha256;
    const claim=store.claimNext(1000);
    store.prepareStep(claim,'charge',hash('reserve-command'),hash('reserve-input'));
    store.commitStep(claim,hash('reserve-result'));
    store.prepareStep(claim,'capture',hash('provider-command'),hash('provider-input'));
    store.definiteStepFailure(claim,hash('definite-provider-failure'));
    assert.equal(store.inspect(id).step_index,0);
    store.prepareCompensation(claim,'charge',hash('release-command'),hash('release-input'));
    store.commitCompensation(claim,hash('release-result'));
    store.finishCompensation(claim);
    assert.equal(store.inspect(id).state,'compensated');
  }finally{db.close();}
});

test('native no-effect waits release only their quiescent lease and resume the same step under a fresh due fence',()=>{
 const realNow=Date.now;let clock=1000;Date.now=()=>clock;const db=new DatabaseSync(':memory:');
 try{const store=new GenericWorkflowStore(db,owner),id=store.schedule(identity('native-wait')).instance_sha256,first=store.claimNext(1000);store.prepareStep(first,'charge',hash('same-command'),hash('same-input'));store.waitNativeRetry(first,{original_attempt:'original-effect-A',not_before_ms:2000,deadline_ms:5000});assert.equal(store.inspect(id).lease_until_ms,0);assert.equal(store.claimNext(1000),null);assert.throws(()=>store.resumeNativeRetry(first),/STALE_CLAIM/);clock=2000;const second=store.claimNext(1000);assert.equal(second.fence,2);clock=1900;store.releaseNativeRetry(second);assert.equal(store.claimNext(1000),null);clock=2000;const third=store.claimNext(1000);assert.equal(third.fence,3);store.resumeNativeRetry(third);assert.equal(store.inspect(id).state,'step-prepared');const history=store.inspect(id).history.map(row=>JSON.parse(row.commitment_json));assert.equal(history.filter(row=>row.kind==='prepare-step').length,1);assert.equal(history.filter(row=>row.kind==='retry-stage').length,0);assert.equal(history.find(row=>row.kind==='native-retry-resume').original_attempt,'original-effect-A');store.commitStep(third,hash('original-native-result'));assert.equal(store.inspect(id).state,'step-committed');
 }finally{Date.now=realNow;db.close();}
});
