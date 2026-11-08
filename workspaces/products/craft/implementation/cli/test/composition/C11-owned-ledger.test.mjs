import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { test } from 'node:test';
import { DurableWriteIntentStore,externalWriteIntentSchemaSQL,externalWriteIntentEpochSchemaSQL,
  externalWriteIntentGuardSQL,emptyExternalWriteIntentDigest } from '../../src/generic/durable-write-intent-store.ts';
import { buildDemoPayCaptureRequest,createDemoPayNativeWriteAdapter }
  from '../../src/generic/external-write-runtime.ts';
const sha=x=>createHash('sha256').update(x).digest('hex');
const input=()=>{
  const effect_canonical_json='{"ordinal":0,"parent":"original-root","site":"capture"}';
  const payload_canonical_json='{"amount":42,"currency":"USD"}';
  const binding_canonical_json='{"profile":"selected-capture-inspect-v1"}';
  return {effect_canonical_json,effect_sha256:sha(effect_canonical_json),
    payload_canonical_json,payload_sha256:sha(payload_canonical_json),
    binding_canonical_json,binding_sha256:sha(binding_canonical_json),
    request_bytes:Buffer.from('POST /capture original bytes')};
};
const owned={store_id:'11111111-1111-4111-8111-111111111111',compatibility_sha256:'a'.repeat(64)};
const setup=()=>{
  const dir=mkdtempSync(join(tmpdir(),'c11-owned-')),path=join(dir,'store.sqlite'),db=new DatabaseSync(path);
  db.exec(externalWriteIntentSchemaSQL+';'+externalWriteIntentEpochSchemaSQL+';'+externalWriteIntentGuardSQL+';');
  db.prepare('INSERT INTO _craft_external_write_epoch_v1 VALUES(1,?,?,0,?)')
    .run(owned.store_id,owned.compatibility_sha256,emptyExternalWriteIntentDigest);
  return {dir,path,db,store:new DurableWriteIntentStore(db,owned)};
};

test('owned epoch and immutable guards keep causal intent after second connection and reopen',()=>{
  const c=setup(),v=input();
  try{
    const first=c.store.prepare(v);assert.equal(first.kind,'new');
    const peer=new DatabaseSync(c.path);
    try{
      assert.throws(()=>peer.prepare('DELETE FROM _craft_external_write_intents_v1').run(),/C11_INTENT_DELETE_FORBIDDEN/);
      assert.throws(()=>peer.prepare('UPDATE _craft_external_write_intents_v1 SET payload_sha256=?').run('0'.repeat(64)),/C11_INTENT_UPDATE_FORBIDDEN/);
      // Rewriting the epoch alone cannot authorize a changed ledger.
      peer.prepare('UPDATE _craft_external_write_epoch_v1 SET intent_sha256=?').run('0'.repeat(64));
      assert.throws(()=>c.store.markDispatched(first.dispatch),/C11_INTENT_EPOCH_CONFLICT/);
      peer.close();
      c.db.close();
      const reopened=new DatabaseSync(c.path);
      assert.throws(()=>new DurableWriteIntentStore(reopened,owned),/C11_INTENT_EPOCH_CONFLICT/);
      // Repair only the exact original digest, as a controlled test reset.
      reopened.prepare('UPDATE _craft_external_write_epoch_v1 SET intent_sha256=?').run(sha(JSON.stringify([[
        v.effect_sha256,v.effect_canonical_json,v.payload_sha256,v.payload_canonical_json,
        v.binding_sha256,v.binding_canonical_json,sha(v.request_bytes),v.request_bytes.toString('hex'),'prepared',null
      ]])));
      const recovered=new DurableWriteIntentStore(reopened,owned);
      assert.deepEqual(recovered.prepare(v),{kind:'inspect-required',state:'prepared'});
      reopened.close();
    }finally{if(peer.isOpen)peer.close();}
  }finally{if(c.db.isOpen)c.db.close();rmSync(c.dir,{recursive:true,force:true});}
});

test('schema/trigger change is detected before retirement even when later restored',()=>{
  const c=setup(),v=input();
  try{
    const first=c.store.prepare(v),peer=new DatabaseSync(c.path);
    try{
      peer.exec('DROP TRIGGER _craft_external_write_no_delete_v1');
      assert.throws(()=>c.store.markDispatched(first.dispatch),/C11_INTENT_SCHEMA_EPOCH_CHANGED/);
      peer.exec(externalWriteIntentGuardSQL.split('CREATE TRIGGER _craft_external_write_guard_update_v1')[0]);
      assert.throws(()=>c.store.markDispatched(first.dispatch),/C11_INTENT_SCHEMA_EPOCH_CHANGED/);
      assert.equal(c.db.prepare('SELECT state FROM _craft_external_write_intents_v1').get().state,'prepared');
    }finally{peer.close();}
  }finally{c.db.close();rmSync(c.dir,{recursive:true,force:true});}
});

test('rewriting intent and epoch after dropping guards remains an explicit reopen gap',()=>{
  const c=setup(),v=input();
  try{
    c.store.prepare(v);const peer=new DatabaseSync(c.path);
    try{
      peer.exec('DROP TRIGGER _craft_external_write_no_delete_v1; DROP TRIGGER _craft_external_write_guard_update_v1;');
      peer.prepare('DELETE FROM _craft_external_write_intents_v1').run();
      peer.prepare('UPDATE _craft_external_write_epoch_v1 SET intent_count=0,intent_sha256=?').run(emptyExternalWriteIntentDigest);
      peer.exec(externalWriteIntentGuardSQL+';');
      assert.throws(()=>c.store.prepare(v),/C11_INTENT_SCHEMA_EPOCH_CHANGED/);
    }finally{peer.close();}
    c.db.close();
    const reopened=new DatabaseSync(c.path);
    try{
      const fresh=new DurableWriteIntentStore(reopened,owned);
      // The repository must refuse effect execution until external custody of
      // the store epoch across crashes is implemented. This is a known gap.
      assert.equal(fresh.prepare(v).kind,'new');
    }finally{reopened.close();}
  }finally{if(c.db.isOpen)c.db.close();rmSync(c.dir,{recursive:true,force:true});}
});

test('post-check-to-send interval is still vulnerable to a DDL-capable peer and remains unexecutable',()=>{
  const c=setup(),v=input();
  try{
    const first=c.store.prepare(v),custody=c.store.markDispatched(first.dispatch);
    c.store.assertDispatchCurrent(custody,v); // last synchronous check
    const peer=new DatabaseSync(c.path);
    try{
      peer.exec('DROP TRIGGER _craft_external_write_no_delete_v1; DROP TRIGGER _craft_external_write_guard_update_v1;');
      peer.prepare('DELETE FROM _craft_external_write_intents_v1').run();
      peer.prepare('UPDATE _craft_external_write_epoch_v1 SET intent_count=0,intent_sha256=?').run(emptyExternalWriteIntentDigest);
      peer.exec(externalWriteIntentGuardSQL+';');
      assert.equal(peer.prepare('SELECT count(*) AS n FROM _craft_external_write_intents_v1').get().n,0);
      assert.throws(()=>c.store.assertDispatchCurrent(custody,v),/C11_INTENT_SCHEMA_EPOCH_CHANGED/);
      // No provider call follows the prior check in this candidate; the
      // original runtime still refuses V3 rather than treating it as custody.
    }finally{peer.close();}
  }finally{c.db.close();rmSync(c.dir,{recursive:true,force:true});}
});

test('a definite checked observation survives store reopen with the original effect identity',async()=>{
  const c=setup();
  const effect_canonical_json='{"operation":"capture","root":"restart-test"}';
  const payload_canonical_json='{"amountMinor":"42","currency":"USD"}';
  const binding_canonical_json='{"protocol":"DemoPay-v1"}';
  const effect_sha256=sha(effect_canonical_json);
  const v={effect_canonical_json,effect_sha256,payload_canonical_json,
    payload_sha256:sha(payload_canonical_json),binding_canonical_json,
    binding_sha256:sha(binding_canonical_json),
    request_bytes:buildDemoPayCaptureRequest(effect_sha256,'order-restart','42','USD')};
  try{
    const prepared=c.store.prepare(v);assert.equal(prepared.kind,'new');
    const custody=c.store.markDispatched(prepared.dispatch);
    const adapter=createDemoPayNativeWriteAdapter({protocol_id:'DemoPay-v1'},
      {async exchange(request){const body=JSON.parse(Buffer.from(request.body).toString('utf8'));
        return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},
          body:Buffer.from(JSON.stringify({...body,status:'Captured',providerReference:'receipt-restart'}))};}});
    const outcome=await adapter.capture(c.store,custody,v);
    assert.equal(outcome.kind,'observed');
    c.store.recordCheckedObservation(v,outcome.checked);
    c.db.close();
    const reopened=new DatabaseSync(c.path);
    try{
      const store=new DurableWriteIntentStore(reopened,owned);
      const recovered=store.recover(effect_sha256);
      assert.equal(recovered.state,'observed');
      assert.deepEqual(recovered.observation,{kind:'Captured',providerReference:'receipt-restart'});
      assert.deepEqual(Buffer.from(recovered.input.request_bytes),Buffer.from(v.request_bytes));
      assert.deepEqual(store.readObserved(v),{kind:'Captured',providerReference:'receipt-restart'});
      assert.deepEqual(store.prepare(v),{kind:'observed'});
    }finally{reopened.close();}
  }finally{if(c.db.isOpen)c.db.close();rmSync(c.dir,{recursive:true,force:true});}
});
