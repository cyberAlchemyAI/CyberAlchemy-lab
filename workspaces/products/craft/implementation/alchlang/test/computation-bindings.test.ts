import { test } from "node:test";
import assert from "node:assert/strict";
import { CompilationRejected } from "../src/model.js";
import { snapshotComputationBindings } from "../src/computation-bindings.js";
import { parseComputationCompanion } from "../src/computation-source.js";

const reject = (value: unknown, path = "$bindings") => assert.throws(() => snapshotComputationBindings(value), (error: unknown) => {
  assert.ok(error instanceof CompilationRejected);
  assert.match(error.message, /COMPUTATION_BINDING_DATA/);
  assert.ok(error.message.includes(path));
  return true;
});

test("descriptor admission rejects top-level/nested getters and toJSON without invocation", () => {
  let calls = 0;
  const getter = { get owner() { calls++; return "owner"; } };
  reject(getter, "$bindings/owner");
  reject({ declarations: getter }, "$bindings/declarations/owner");
  reject({ toJSON() { calls++; return {}; } }, "$bindings/toJSON");
  const array = [0]; Object.defineProperty(array, "0", { get() { calls++; return 0; }, enumerable: true });
  reject(array, "$bindings/0");
  const setter = {}; Object.defineProperty(setter, "owner", { set(_value) { calls++; }, enumerable: true });
  reject(setter, "$bindings/owner");
  assert.equal(calls, 0);
});

test("snapshot is detached and deeply frozen, with null-prototype and dangerous keys preserved", () => {
  const child = Object.assign(Object.create(null), { meaning: "reviewed", list: [1, "🌱", true, null] });
  const input = { declarations: child };
  const snapshot = snapshotComputationBindings(input) as any;
  assert.notEqual(snapshot, input); assert.notEqual(snapshot.declarations, child);
  assert.ok(Object.isFrozen(snapshot)); assert.ok(Object.isFrozen(snapshot.declarations)); assert.ok(Object.isFrozen(snapshot.declarations.list));
  child.meaning = "changed"; child.list[0] = 9;
  assert.equal(snapshot.declarations.meaning, "reviewed"); assert.equal(snapshot.declarations.list[0], 1);
  assert.throws(() => { snapshot.declarations.meaning = "mutated"; }, TypeError);
  const safe = parseComputationCompanion('{"__proto__":{"owner":"ordinary"},"constructor":"data","toJSON":"data"}') as any;
  assert.equal(Object.getPrototypeOf(safe), null);
  assert.equal(safe.__proto__.owner, "ordinary");
  assert.equal(JSON.stringify(safe), '{"__proto__":{"owner":"ordinary"},"constructor":"data","toJSON":"data"}');
});

test("unsupported prototypes, hidden/symbol members and non-JSON leaves reject pathfully", () => {
  for (const value of [undefined, () => 1, 1n, NaN, Infinity, -Infinity, Symbol("x")]) reject({ value }, "$bindings/value");
  for (const value of [new Date(), new Map(), new Set(), new Number(1), Object.create({ inherited: true }), new (class Data {})()]) reject({ value }, "$bindings/value");
  reject({ [Symbol("key")]: 1 });
  const hidden = {}; Object.defineProperty(hidden, "secret", { value: true }); reject(hidden, "$bindings/secret");
  const cyclic: any = {}; cyclic.self = cyclic; reject(cyclic, "$bindings/self");
  const shared = { a: 1 }; assert.equal(JSON.stringify(snapshotComputationBindings({ left: shared, right: shared })), '{"left":{"a":1},"right":{"a":1}}');
});

test("only ordinary dense arrays without extra members are admitted", () => {
  reject(Array(1));
  const hole = [1, 2]; delete hole[0]; reject(hole);
  const extra: any = [1]; extra.extra = 2; reject(extra);
  const symbol = [1]; Object.defineProperty(symbol, Symbol("extra"), { value: 2 }); reject(symbol);
  const hidden = [1]; Object.defineProperty(hidden, "0", { enumerable: false }); reject(hidden, "$bindings/0");
  reject(new (class Data extends Array {})());
  reject(Object.setPrototypeOf([1], null));
  assert.equal(JSON.stringify(snapshotComputationBindings([1, null, { x: false }])), '[1,null,{"x":false}]');
});

test("invalid Unicode keys/values reject equally after strict JSON parsing", () => {
  for (const value of ["\ud800", "\udfff", "x\ud800y"]) {
    reject({ value }, "$bindings/value");
    assert.throws(() => parseComputationCompanion(JSON.stringify({ value })), /COMPUTATION_BINDING_DATA.*\$bindings\/value/);
    reject({ [value]: 1 });
    assert.throws(() => parseComputationCompanion(JSON.stringify({ [value]: 1 })), /COMPUTATION_BINDING_DATA/);
  }
  assert.throws(() => parseComputationCompanion('{"x":1e400}'), /COMPUTATION_BINDING_DATA.*\$bindings\/x/);
});

test("depth, traversal and compact JSON byte limits reject before unbounded copying", () => {
  const nest = (count: number) => { let value: unknown = null; for (let i = 0; i < count; i++) value = { x: value }; return value; };
  snapshotComputationBindings(nest(31)); reject(nest(32));
  reject(Array(262144));
  reject({ ["x".repeat(262145)]: 1 }); reject({ x: "x".repeat(262145) });
  const exact = { x: "a".repeat(262136) }; assert.equal(Buffer.byteLength(JSON.stringify(exact)), 262144);
  snapshotComputationBindings(exact); reject({ x: "a".repeat(262137) });
  // Control-character escaping and multibyte UTF-8 count toward the serialized cap.
  reject({ x: "\u0000".repeat(43691) }); reject({ x: "🌱".repeat(65535) });
  // Individual members fit but the complete compact representation does not.
  reject({ a: "a".repeat(131070), b: "b".repeat(131070) });
  const nearCapArray = Array(131070).fill(0);
  assert.equal(Buffer.byteLength(JSON.stringify(nearCapArray)), 262141);
  assert.equal(JSON.stringify(snapshotComputationBindings(nearCapArray)), JSON.stringify(nearCapArray));
  const compact = JSON.stringify(Array(60000).fill(0));
  assert.ok(Buffer.byteLength(JSON.stringify(JSON.parse(compact), null, 2)) > 262144);
  assert.equal(JSON.stringify(parseComputationCompanion(compact)), compact);
});

test("strict JSON duplicate/syntax/depth and raw byte admission remain separate", () => {
  for (const text of ['{"x":1,"\\u0078":2}', '{"x":}', '{"x":1} trailing', '[1,]', "[".repeat(33) + "0" + "]".repeat(33)]) {
    assert.throws(() => parseComputationCompanion(text), /COMPUTATION_BINDING_JSON/);
  }
  assert.throws(() => parseComputationCompanion(" ".repeat(262145)), /COMPUTATION_BINDING_BOUND/);
  const ordinary = { alpha: [null, 0, "🌱"], z: { value: true } };
  const nullPrototype = Object.assign(Object.create(null), ordinary);
  assert.equal(JSON.stringify(snapshotComputationBindings(ordinary)), JSON.stringify(snapshotComputationBindings(nullPrototype)));
  assert.equal(JSON.stringify(snapshotComputationBindings(ordinary)), JSON.stringify(parseComputationCompanion(JSON.stringify(ordinary))));
});
