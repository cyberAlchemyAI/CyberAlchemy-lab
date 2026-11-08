import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { test } from 'node:test';
import { DurableWriteIntentStore } from '../../src/generic/durable-write-intent-store.ts';

const sha = value => createHash('sha256').update(value).digest('hex');
const fixture = (request = 'POST /capture original bytes') => {
  const effect_canonical_json = '{"ordinal":0,"parent":"original-root","site":"capture"}';
  const payload_canonical_json = '{"amount":42,"currency":"USD"}';
  const binding_canonical_json = '{"profile":"selected-capture-inspect-v1"}';
  return {
    effect_canonical_json, effect_sha256: sha(effect_canonical_json),
    payload_canonical_json, payload_sha256: sha(payload_canonical_json),
    binding_canonical_json, binding_sha256: sha(binding_canonical_json),
    request_bytes: Buffer.from(request),
  };
};
const withStore = async callback => {
  const directory = mkdtempSync(join(tmpdir(), 'c11-intent-'));
  const path = join(directory, 'intent.sqlite');
  const db = new DatabaseSync(path);
  try { await callback({ path, db, store: new DurableWriteIntentStore(db) }); }
  finally { db.close(); rmSync(directory, { recursive: true, force: true }); }
};

test('intent is committed before dispatch, and reopen requires original inspection', async () => {
  await withStore(({ path, db, store }) => {
    const input = fixture();
    const first = store.prepare(input);
    assert.equal(first.kind, 'new');
    assert.throws(() => store.recordCheckedObservation(input, '{"kind":"Captured","receipt":"r-1"}'),
      /C11_FOREIGN_NATIVE_OBSERVATION/);
    const peer = new DatabaseSync(path);
    try {
      peer.exec('BEGIN IMMEDIATE');
      assert.equal(peer.prepare('SELECT state FROM _craft_external_write_intents_v1').get().state, 'prepared');
      peer.exec('COMMIT');
    } finally { peer.close(); }
    assert.deepEqual(store.prepare(input), { kind: 'inspect-required', state: 'prepared' });
    const reopened = new DurableWriteIntentStore(db);
    assert.deepEqual(reopened.prepare(input), { kind: 'inspect-required', state: 'prepared' });
    store.markDispatched(first.dispatch);
    assert.throws(() => store.markDispatched(first.dispatch), /C11_FOREIGN_OR_USED_DISPATCH/);
    assert.deepEqual(reopened.prepare(input), { kind: 'inspect-required', state: 'dispatched' });
  });
});

test('same effect cannot change payload, selected binding or original request bytes', async () => {
  await withStore(({ store }) => {
    const input = fixture();
    store.prepare(input);
    const alteredPayload = '{"amount":43,"currency":"USD"}';
    assert.throws(() => store.prepare({ ...input, payload_canonical_json: alteredPayload,
      payload_sha256: sha(alteredPayload) }), /C11_EFFECT_IDENTITY_CONFLICT/);
    const changedBinding = '{"profile":"different"}';
    assert.throws(() => store.prepare({ ...input, binding_canonical_json: changedBinding,
      binding_sha256: sha(changedBinding) }), /C11_EFFECT_IDENTITY_CONFLICT/);
    assert.throws(() => store.prepare(fixture('POST /capture changed')), /C11_EFFECT_IDENTITY_CONFLICT/);
    assert.equal(store.inspect(input).state, 'prepared');
  });
});

test('ambiguous result remains unresolved and definite observation is quarantined', async () => {
  await withStore(({ path, db, store }) => {
    const input = fixture();
    const first = store.prepare(input);
    store.markDispatched(first.dispatch);
    store.retainUnknown(input);
    assert.deepEqual(store.prepare(input), { kind: 'inspect-required', state: 'unknown' });
    const peer = new DatabaseSync(path);
    const reopened = new DurableWriteIntentStore(peer);
    try {
      assert.deepEqual(reopened.prepare(input), { kind: 'inspect-required', state: 'unknown' });
      assert.throws(() => reopened.recordCheckedObservation(input, '{"kind":"UnknownKey"}'),
        /C11_FOREIGN_NATIVE_OBSERVATION/);
      assert.throws(() => reopened.recordCheckedObservation(input, '{"kind":"Captured","receipt":"r-1"}'),
        /C11_FOREIGN_NATIVE_OBSERVATION/);
    } finally { peer.close(); }
    assert.deepEqual(store.prepare(input), { kind: 'inspect-required', state: 'unknown' });
    assert.equal(db.prepare('SELECT observation FROM _craft_external_write_intents_v1').get().observation, null);
    store.retainUnknown(input);
  });
});

test('prepared cannot become unknown then forged Captured without dispatch or proven inspection', async () => {
  await withStore(({ store }) => {
    const input = fixture();
    assert.equal(store.prepare(input).kind, 'new');
    assert.throws(() => store.retainUnknown(input), /C11_DISPATCH_OR_PROVEN_INSPECTION_REQUIRED/);
    assert.throws(() => store.recordCheckedObservation(input, '{"kind":"Captured","receipt":"forged"}'),
      /C11_FOREIGN_NATIVE_OBSERVATION/);
    assert.deepEqual(store.prepare(input), { kind: 'inspect-required', state: 'prepared' });
  });
});

test('same-schema AFTER UPDATE trigger cannot erase intent and mint a new permit', async () => {
  await withStore(({ db, store }) => {
    const input = fixture();
    const first = store.prepare(input);
    db.exec(`CREATE TRIGGER erase_c11_intent AFTER UPDATE ON _craft_external_write_intents_v1
      BEGIN DELETE FROM _craft_external_write_intents_v1 WHERE effect_sha256=NEW.effect_sha256; END`);
    assert.throws(() => store.markDispatched(first.dispatch), /C11_INTENT_SCHEMA_CONFLICT/);
    assert.equal(db.prepare('SELECT state FROM _craft_external_write_intents_v1').get().state, 'prepared');
    assert.throws(() => store.prepare(input), /C11_INTENT_SCHEMA_CONFLICT/);
    db.exec('DROP TRIGGER erase_c11_intent');
    assert.deepEqual(store.prepare(input), { kind: 'inspect-required', state: 'prepared' });
  });
});

test('preexisting incompatible table is refused instead of silently adopted', async () => {
  await withStore(({ db }) => {
    db.exec('DROP TABLE _craft_external_write_intents_v1');
    db.exec('CREATE TABLE _craft_external_write_intents_v1 (effect_sha256 TEXT PRIMARY KEY)');
    assert.throws(() => new DurableWriteIntentStore(db), /C11_INTENT_SCHEMA_CONFLICT/);
  });
});

test('stored identity corruption fails closed before replay or disclosure', async () => {
  await withStore(({ db, store }) => {
    const input = fixture();
    store.prepare(input);
    db.prepare('UPDATE _craft_external_write_intents_v1 SET request_sha256=? WHERE effect_sha256=?')
      .run('0'.repeat(64), input.effect_sha256);
    assert.throws(() => store.prepare(input), /C11_STORED_INTENT_INVALID/);
    assert.throws(() => store.inspect(input), /C11_STORED_INTENT_INVALID/);
  });
});

test('invalid canonical identity is rejected before durable intent', async () => {
  await withStore(({ store }) => {
    const input = fixture();
    assert.throws(() => store.prepare({ ...input, effect_canonical_json: '{"z":1,"a":2}',
      effect_sha256: sha('{"z":1,"a":2}') }), /C11_EFFECT_NONCANONICAL/);
    assert.throws(() => store.prepare({ ...input, effect_sha256: '0'.repeat(64) }), /C11_EFFECT_IDENTITY/);
    assert.equal(store.inspect(input), null);
  });
});

test('dispatch custody rejects deleted, changed or foreign intent before native invocation', async () => {
  await withStore(({ db, store }) => {
    const input=fixture();
    const result=store.prepare(input);
    const custody=store.markDispatched(result.dispatch);
    store.assertDispatchCurrent(custody,input);
    assert.throws(()=>store.assertDispatchCurrent({kind:'private-c11-dispatch-custody/v1-candidate'},input),/C11_FOREIGN_DISPATCH_CUSTODY/);
    db.prepare('UPDATE _craft_external_write_intents_v1 SET request_sha256=? WHERE effect_sha256=?')
      .run('0'.repeat(64),input.effect_sha256);
    assert.throws(()=>store.assertDispatchCurrent(custody,input),/C11_STORED_INTENT_INVALID/);
    db.prepare('DELETE FROM _craft_external_write_intents_v1 WHERE effect_sha256=?').run(input.effect_sha256);
    assert.throws(()=>store.assertDispatchCurrent(custody,input),/C11_DISPATCH_NOT_CURRENT/);
  });
});
