import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { lowerComputationSource, serializeComputationCompanion, COMPUTATION_CAPABILITY } from "../src/index.js";
import type { ComputationCompanionIdentityKind, LoweredComputationSource } from "../src/index.js";

const source = readFileSync(new URL("../examples/computation/summary.alch", import.meta.url), "utf8");
const companion = readFileSync(new URL("../examples/computation/summary.alch.computation.json", import.meta.url), "utf8");
const options = { capability: COMPUTATION_CAPABILITY };
const sha = (text: string) => createHash("sha256").update(Buffer.from(text, "utf8")).digest("hex");

test("raw companion identity preserves exact formatting, line endings and trailing bytes", () => {
  const variants = [companion, companion.replaceAll("\n", "\r\n"), JSON.stringify(JSON.parse(companion)), " \n" + companion + "\t\n"];
  const semantic = lowerComputationSource(source, companion, options);
  const hashes = new Set<string>();
  for (const text of variants) {
    const result: LoweredComputationSource = lowerComputationSource(source, text, options);
    const kind: ComputationCompanionIdentityKind = result.companion_identity_kind;
    assert.equal(kind, "raw-utf8");
    assert.equal(result.companion_text, text);
    assert.equal(result.companion_sha256, sha(text));
    assert.deepEqual(result.contract, semantic.contract);
    assert.deepEqual(result.source_binding, semantic.source_binding);
    hashes.add(result.companion_sha256);
  }
  assert.equal(hashes.size, variants.length);
  assert.equal(semantic.companion_sha256, "ce63aad30cd45577ed3ccba7b1bb99b0b59cfae82af627fc500b592169803b50");
  assert.notEqual(semantic.companion_sha256, "80f02baf0ffcf11a592313de6e44e64399d074805dbde9073505207e341fe2f1");
});

test("object identity is deterministic and materialized text establishes the same file digest", () => {
  const original = JSON.parse(companion);
  const reversed = Object.assign(Object.create(null), Object.fromEntries(Object.entries(original).reverse()));
  reversed.declarations = Object.fromEntries(Object.entries(original.declarations).reverse().map(([name, row]) => [name, Object.fromEntries(Object.entries(row as object).reverse())]));
  const result = lowerComputationSource(source, original, options);
  assert.deepEqual(lowerComputationSource(source, reversed, options), result);
  assert.equal(result.companion_identity_kind, "canonical-json");
  assert.equal(result.companion_text, serializeComputationCompanion(original));
  assert.equal(result.companion_text.endsWith("\n"), false);
  assert.equal(result.companion_sha256, sha(result.companion_text));
  const materialized = lowerComputationSource(source, result.companion_text, options);
  assert.equal(materialized.companion_identity_kind, "raw-utf8");
  assert.equal(materialized.companion_sha256, result.companion_sha256);
  assert.deepEqual(materialized.contract, result.contract);
  assert.deepEqual(materialized.source_binding, result.source_binding);
});

test("public serializer emits the selected exact compact representation", () => {
  const value = { owner: "team", source_sha256: "0".repeat(64), semantics: "domainspec.iteration-expression/v1-candidate", schema_version: "alchlang.computation-bindings/v1-candidate", declarations: { alpha: { source_sha256: "1".repeat(64), meaning: "one", kind: "Calculation" } }, capability: COMPUTATION_CAPABILITY };
  const expected = '{"capability":"alchlang.computation/v1-candidate","declarations":{"alpha":{"kind":"Calculation","meaning":"one","source_sha256":"' + "1".repeat(64) + '"}},"owner":"team","schema_version":"alchlang.computation-bindings/v1-candidate","semantics":"domainspec.iteration-expression/v1-candidate","source_sha256":"' + "0".repeat(64) + '"}';
  assert.equal(serializeComputationCompanion(value), expected);
  assert.equal(serializeComputationCompanion(JSON.parse(expected)), expected);
});

test("serializer validates standalone companion shape and values without asserting source coverage", () => {
  const value = () => JSON.parse(companion);
  const edits = [
    (v: any) => { v.extra = true; }, (v: any) => { delete v.owner; },
    (v: any) => { v.schema_version = "old"; }, (v: any) => { v.owner = "bad owner"; },
    (v: any) => { v.source_sha256 = "not-a-hash"; }, (v: any) => { v.declarations = []; },
    (v: any) => { v.declarations = {}; }, (v: any) => { v.declarations.main.extra = true; },
    (v: any) => { v.declarations.main.kind = "Operation"; }, (v: any) => { v.declarations.main.meaning = "  "; },
    (v: any) => { v.declarations.main.source_sha256 = "Z".repeat(64); },
    (v: any) => { v.declarations.Main = v.declarations.main; delete v.declarations.main; },
  ];
  for (const edit of edits) { const v = value(); edit(v); assert.throws(() => serializeComputationCompanion(v), /COMPUTATION_BINDING_(SHAPE|SOURCE|DECLARATION)/); }
  assert.throws(() => serializeComputationCompanion(companion), /COMPUTATION_BINDING_SHAPE/);
  const phantom = value(); phantom.declarations.phantom = phantom.declarations.main;
  const proposed = serializeComputationCompanion(phantom);
  assert.throws(() => lowerComputationSource(source, proposed, options), /COMPUTATION_BINDING_SHAPE/);
});

test("serialization and lowering never invoke original accessors or toJSON", () => {
  let calls = 0;
  for (const nested of [false, true]) {
    const binding = JSON.parse(companion);
    const container = nested ? binding.declarations.main : binding;
    const key = nested ? "meaning" : "owner", original = container[key];
    Object.defineProperty(container, key, { enumerable: true, get() { calls++; return original; } });
    assert.throws(() => serializeComputationCompanion(binding), /COMPUTATION_BINDING_DATA/);
    assert.throws(() => lowerComputationSource(source, binding, options), /COMPUTATION_BINDING_DATA/);
  }
  const binding = JSON.parse(companion); binding.toJSON = () => { calls++; return {}; };
  assert.throws(() => serializeComputationCompanion(binding), /COMPUTATION_BINDING_DATA/);
  assert.equal(calls, 0);
});
