import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';
import { test } from 'node:test';
import { DurableWriteIntentStore } from '../../src/generic/durable-write-intent-store.ts';
import { buildDemoPayCaptureRequest, createDemoPayNativeWriteAdapter,
  demoPayAttemptKey, readCheckedDemoPayObservation } from '../../src/generic/external-write-runtime.ts';

const sha = value => createHash('sha256').update(value).digest('hex');
const reply = (status, body, headers = {
  'content-type': 'application/json; charset=utf-8', 'demopay-protocol': '1',
}) => ({ status, headers, body: Buffer.from(JSON.stringify(body)) });
function fixture(amountMinor = '42') {
  const effect_canonical_json = '{"operation":"capture","root":"test"}';
  const payload_canonical_json = `{"amountMinor":"${amountMinor}","currency":"USD"}`;
  const binding_canonical_json = '{"protocol":"DemoPay-v1"}';
  const effect_sha256 = sha(effect_canonical_json);
  return { effect_canonical_json, effect_sha256, payload_canonical_json,
    payload_sha256: sha(payload_canonical_json), binding_canonical_json,
    binding_sha256: sha(binding_canonical_json),
    request_bytes: buildDemoPayCaptureRequest(effect_sha256, 'order-7', amountMinor, 'USD') };
}
function storeFixture() {
  const db = new DatabaseSync(':memory:');
  return { db, store: new DurableWriteIntentStore(db) };
}
function retired(store, input) {
  const prepared = store.prepare(input);
  assert.equal(prepared.kind, 'new');
  return store.markDispatched(prepared.dispatch);
}

test('capture uses exact persisted key and bytes; inspection reuses them without capture', async () => {
  const { db, store } = storeFixture();
  try {
    const input = fixture();
    const custody = retired(store, input);
    const calls = [];
    const port = { async exchange(request) {
      calls.push(request);
      const body = JSON.parse(Buffer.from(request.body).toString('utf8'));
      return reply(200, { ...body, status: 'Captured', providerReference: 'receipt-1' });
    } };
    const adapter = createDemoPayNativeWriteAdapter({ protocol_id: 'DemoPay-v1' }, port);
    const capture = await adapter.capture(store, custody, input);
    assert.equal(capture.kind, 'observed');
    assert.equal(capture.result.status, 'Captured');
    assert.equal(capture.matches_request, true);
    assert.equal(readCheckedDemoPayObservation(capture.checked, input).providerReference, 'receipt-1');
    assert.throws(() => readCheckedDemoPayObservation({ kind: capture.checked.kind }, input),
      /C11_FOREIGN_NATIVE_OBSERVATION/);
    const inspect = await adapter.inspect(store, input);
    assert.equal(inspect.kind, 'observed');
    assert.deepEqual(calls.map(x => x.path), ['/v1/capture', '/v1/capture/inspect']);
    assert.deepEqual(calls.map(x => Buffer.from(x.body).toString('hex')),
      [Buffer.from(input.request_bytes).toString('hex'), Buffer.from(input.request_bytes).toString('hex')]);
    assert.equal(JSON.parse(Buffer.from(calls[1].body).toString('utf8')).attemptKey,
      demoPayAttemptKey(input.effect_sha256));
    assert.throws(() => adapter.capture(store, custody, input), /C11_CAPTURE_ALREADY_SENT_INSPECT_REQUIRED/);
    assert.equal(calls.length, 2);
    store.recordCheckedObservation(input, capture.checked);
    assert.equal(store.inspect(input).state, 'observed');
    assert.throws(() => store.recordCheckedObservation(input, { kind: capture.checked.kind }),
      /C11_FOREIGN_NATIVE_OBSERVATION/);
  } finally { db.close(); }
});

test('timeout, 503, malformed bytes and wrong protocol header remain unknown', async () => {
  const cases = [
      [{ async exchange() { return new Promise(() => {}); } }, 'timeout'],
      [{ async exchange() { return reply(503, { kind: 'error', code: 'provider-unavailable' }); } }, 'unavailable'],
      [{ async exchange() { return { status: 200, headers: reply(200, {}).headers,
        body: Buffer.from('{"status":"Captured","status":"DefinitivelyDeclined"}') }; } }, 'malformed'],
      [{ async exchange() { return reply(200, {}, { 'content-type': 'application/json', 'demopay-protocol': '1' }); } }, 'malformed'],
    ];
  for (const [port, reason] of cases) {
    const { db, store } = storeFixture();
    try {
      const input = fixture();
      const custody = retired(store, input);
      const adapter = createDemoPayNativeWriteAdapter({ protocol_id: 'DemoPay-v1' }, port, 5);
      assert.deepEqual(await adapter.capture(store, custody, input), { kind: 'unknown', reason });
      assert.throws(() => adapter.capture(store, custody, input), /C11_CAPTURE_ALREADY_SENT_INSPECT_REQUIRED/);
    } finally { db.close(); }
  }
});

test('same effect with changed payload or request cannot dispatch or inspect', async () => {
  const { db, store } = storeFixture();
  try {
    const input = fixture();
    const custody = retired(store, input);
    let calls = 0;
    const adapter = createDemoPayNativeWriteAdapter({ protocol_id: 'DemoPay-v1' },
      { async exchange() { calls++; return reply(409, { kind: 'error', code: 'attempt-key-conflict' }); } });
    const changed = fixture('43');
    assert.throws(() => adapter.capture(store, custody, changed), /C11_EFFECT_IDENTITY_CONFLICT/);
    assert.throws(() => adapter.inspect(store, changed), /C11_EFFECT_IDENTITY_CONFLICT/);
    assert.equal(calls, 0);
    assert.deepEqual(await adapter.capture(store, custody, input),
      { kind: 'conflict', reason: 'attempt-key-conflict' });
    assert.equal(calls, 1);
  } finally { db.close(); }
});

test('well-typed mismatched provider identity does not mint checked observation', async () => {
  const { db, store } = storeFixture();
  try {
    const input = fixture();
    const custody = retired(store, input);
    const adapter = createDemoPayNativeWriteAdapter({ protocol_id: 'DemoPay-v1' },
      { async exchange(request) { const body = JSON.parse(Buffer.from(request.body).toString('utf8'));
        return reply(200, { ...body, amountMinor: '44', status: 'Captured', providerReference: 'receipt-2' }); } });
    const outcome = await adapter.capture(store, custody, input);
    assert.equal(outcome.kind, 'observed');
    assert.equal(outcome.matches_request, false);
    assert.equal(outcome.checked, null);
  } finally { db.close(); }
});
