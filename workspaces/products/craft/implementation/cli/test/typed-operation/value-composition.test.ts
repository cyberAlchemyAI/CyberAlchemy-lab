import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { decodeOperationValueComposition, OPERATION_VALUE_COMPOSITION_VERSION } from '../../src/typed-operation/value-composition.ts';
import { decodeOperationActionBindings } from '../../src/typed-operation/action-bindings.ts';

const at = (root: string) => ({ op: 'path', root, properties: [] });
const fixture = () => ({ schema_version: OPERATION_VALUE_COMPOSITION_VERSION, operation_ref: 'commerce:submit', bindings: [
  { kind: 'mapping', name: 'summary', selector: 'commerce:to-summary', arguments: [{ parameter: 'order', value: at('current') }] },
  { kind: 'query', name: 'current', selector: 'commerce:find-order', source_slot: 'commerce:order', arguments: [{ parameter: 'id', value: at('request') }], absence: 'preserve' },
] });

test('value composition preserves named calls, explicit absence and deterministic dependency data', () => {
  const source = fixture(), before = JSON.stringify(source), value = decodeOperationValueComposition(source);
  assert.equal(JSON.stringify(source), before);
  assert.equal(Object.isFrozen(source), false);
  assert.ok(Object.isFrozen(value) && Object.isFrozen(value.bindings) && Object.isFrozen(value.bindings[0]!.arguments));
  assert.equal(value.bindings[0]!.kind, 'query');
  assert.equal(value.bindings[1]!.selector, 'commerce:to-summary');
  assert.deepEqual(decodeOperationValueComposition({ ...source, bindings: [...source.bindings].reverse() }), value);
  const required = fixture(); required.bindings[1]!.absence = 'require-present';
  assert.notDeepEqual(decodeOperationValueComposition(required), value);
  assert.throws(() => decodeOperationActionBindings(source), /OPERATION_ACTION_/);
  const contract = JSON.parse(readFileSync(path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/operation-value-composition-contract.json'), 'utf8'));
  assert.equal(contract.bindings_schema, OPERATION_VALUE_COMPOSITION_VERSION);
  assert.equal(contract.authority_effect, 'none');
});

test('value composition rejects malformed, duplicate, cyclic and executable inputs', () => {
  const cases: Array<(v: any) => void> = [
    v => { v.extra = true; }, v => { v.schema_version = 'unknown'; },
    v => { v.operation_ref = 'commerce:submit\n'; },
    v => { v.bindings[0].kind = 'call'; },
    v => { v.bindings[0].source_slot = 'unexpected'; },
    v => { delete v.bindings[1].absence; },
    v => { v.bindings[1].absence = 'first-match'; },
    v => { v.bindings[1].source_slot = ''; },
    v => { v.bindings[1].source_slot = 'unsafe\nslot'; },
    v => { v.bindings[1].arguments[0].value = { op: 'eval', code: 'run()' }; },
    v => { v.bindings[1].arguments.push(v.bindings[1].arguments[0]); },
    v => { v.bindings[1].name = 'summary'; },
    v => { v.bindings[1].arguments[0].value = at('summary'); },
    v => { v.bindings[0].arguments[0].value = { op: 'to_set', value: at('summary') }; },
    v => { v.bindings = Array.from({ length: 257 }, () => v.bindings[0]); },
  ];
  for (const mutate of cases) { const value = fixture(); mutate(value); assert.throws(() => decodeOperationValueComposition(value)); }
});

test('value composition preflight does not execute getters or coerce values', () => {
  let calls = 0;
  const value = fixture();
  Object.defineProperty(value.bindings[0], 'selector', { enumerable: true, get() { calls++; return 'commerce:to-summary'; } });
  assert.throws(() => decodeOperationValueComposition(value)); assert.equal(calls, 0);
  assert.throws(() => decodeOperationValueComposition({ ...fixture(), operation_ref: { toString() { calls++; return 'commerce:submit'; } } }));
  assert.equal(calls, 0);
  const sparse = fixture(); delete sparse.bindings[0];
  assert.throws(() => decodeOperationValueComposition(sparse));
});
