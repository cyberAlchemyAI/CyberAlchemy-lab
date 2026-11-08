import assert from 'node:assert/strict';
import test from 'node:test';
import {createHttpInvocation} from '../src/http-invocation-adapter.js';
import {createOutbound} from '../src/outbound-runtime.js';

const binding = {id: 'fixture-provider', version: 'v1', model: 'model-a', url: 'https://provider.example.test/invoke', secret: 'fixture-secret'};
const control = () => ({deadline: performance.now() + 1000, signal: new AbortController().signal});

test('HTTP adapter rejects a wrong model before fetch, including a missing model', () => {
  let fetchCount = 0;
  const adapter = createHttpInvocation({bindings: [binding], fetchImpl: async () => {
    fetchCount++;
    return new Response('{}');
  }});
  for (const model of ['model-b', undefined]) {
    assert.throws(() => adapter.http.sendOnce({id: binding.id, version: binding.version, model} as {id: string; version: string; model: string}, {}, control()), /BINDING_MISMATCH/);
  }
  assert.equal(fetchCount, 0);
});

test('outbound invocation preserves selected model through the HTTP adapter', async () => {
  let fetchCount = 0;
  const adapter = createHttpInvocation({bindings: [binding], fetchImpl: async (_url: string, request: RequestInit) => {
    fetchCount++;
    assert.equal(request.method, 'POST');
    return new Response(JSON.stringify({result: 'ok'}), {headers: {'content-type': 'application/json'}});
  }});
  const contract = {
    modules: {},
    limits: {deadline_ms: 1000, max_bytes: 1024, max_concurrent: 1},
    steps: [
      {id: 'binding', kind: 'binding', binding_id: 'input.id', version: 'input.version', model: 'input.model', policy: 'input.policy'},
      {id: 'response', kind: 'http', binding: 'binding', body: 'input.body', omit: [], stream: 'input.stream'}
    ],
    output: 'response'
  };
  const invoke = createOutbound(contract, {}, adapter);
  assert.deepEqual(await invoke({id: binding.id, version: binding.version, model: binding.model, body: {prompt: 'hi'}, stream: false}), {result: 'ok'});
  assert.equal(fetchCount, 1);
});
