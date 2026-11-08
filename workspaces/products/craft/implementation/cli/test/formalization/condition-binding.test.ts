import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import { canonicalJson, sha256 } from "../../src/input/source-manifest.ts";
import { compileFormalConditionBindings, CONDITION_BINDING_VERSION } from "../../src/formalization/condition-binding.ts";

const graph = loadCompiledProjectGraph(new URL("../../fixtures/input-roots/canonical-project/", import.meta.url).pathname);
const rule = "beta:can-complete-settlement";
// Reuse the formalization package's synthetic v4 contract fixture; no real acceptance is asserted.
const fixtureRegistry = JSON.parse(readFileSync(new URL("../../../../formalization/fixtures/contract-fixtures.json", import.meta.url), "utf8"));
function findClaim(value: unknown): any {
  if (!value || typeof value !== "object") return undefined;
  if ((value as any).schema_version === "domainspec-v2.formal-claim-source/v4-candidate") return value;
  for (const child of Object.values(value)) { const found = findClaim(child); if (found) return found; }
}
function fixture() {
  const claim = JSON.parse(JSON.stringify(findClaim(fixtureRegistry)).replaceAll("@digest", "a".repeat(64)));
  const bytes = Buffer.from(canonicalJson(claim));
  const ref = { path: "claims/eligible.json", sha256: sha256(bytes), size_bytes: bytes.length,
    claim_id: claim.claim.claim_id, claim_version: claim.claim.claim_version,
    identity_inputs_digest: claim.claim.identity_inputs_digest };
  return { sources: new Map([[ref.path, bytes]]), input: { schema_version: CONDITION_BINDING_VERSION,
    rules: [rule], bindings: [{ binding_id: "eligible", relationship: "condition-bound-to", rule_ref: rule,
      claim_ref: ref, source_pointer: "commerce.alch:12" }], authority_effect: "none" } };
}

test("joins an exact qualified Rule to a separately owned claim deterministically", () => {
  const { input, sources } = fixture();
  const a = compileFormalConditionBindings(graph, input, sources);
  assert.deepEqual(a, compileFormalConditionBindings(graph, structuredClone(input), sources));
  assert.equal(a.bindings[0]?.rule_ref, rule);
  assert.equal(a.bindings[0]?.claim_ref.claim_id, "FormalClaim:fixture");
  assert.equal(a.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
  assert.ok(Object.isFrozen(a.bindings[0]?.claim_ref));
  assert.equal(graph.nodes.some(node => node.kind === "FormalClaim"), false);
});

test("rejects endpoint, multiplicity, version and relationship mutations", () => {
  const mutations: Array<[string, (input: ReturnType<typeof fixture>["input"]) => void]> = [
    ["CONDITION_SOURCE_KIND", input => { input.rules[0] = "alpha:customer"; }],
    ["CONDITION_SOURCE_KIND", input => { input.rules[0] = "can-complete-settlement"; }],
    ["CONDITION_MULTIPLICITY", input => { input.bindings.push(structuredClone(input.bindings[0]!)); }],
    ["CONDITION_MULTIPLICITY", input => { input.bindings.push({ ...structuredClone(input.bindings[0]!), binding_id: "second" }); }],
    ["CONDITION_MISSING", input => { input.bindings = []; }],
    ["CONDITION_RELATIONSHIP", input => { input.bindings[0]!.relationship = "proves"; }],
    ["CONDITION_CLAIM_IDENTITY", input => { input.bindings[0]!.claim_ref.claim_version = "wrong"; }],
    ["CONDITION_CLAIM_IDENTITY", input => { input.bindings[0]!.claim_ref.identity_inputs_digest = "b".repeat(64); }],
    ["CONDITION_SOURCE_PATH", input => { input.bindings[0]!.claim_ref.path = "../claim.json"; }],
  ];
  for (const [code, mutate] of mutations) {
    const { input, sources } = fixture(); mutate(input);
    assert.throws(() => compileFormalConditionBindings(graph, input, sources), { code });
  }
});

test("dereferences exact bytes and rejects unavailable, stale or wrong-kind sources", () => {
  for (const mode of ["missing", "stale", "wrong-kind", "superseded"]) {
    const { input, sources } = fixture();
    const ref = input.bindings[0]!.claim_ref;
    if (mode === "missing") sources.clear();
    if (mode === "stale") sources.set(ref.path, Buffer.from("{}"));
    if (mode === "wrong-kind" || mode === "superseded") {
      const value = JSON.parse(sources.get(ref.path)!.toString());
      if (mode === "wrong-kind") value.schema_version = "domainspec.node/v1";
      else value.claim.currentness = "superseded";
      const bytes = Buffer.from(canonicalJson(value)); sources.set(ref.path, bytes);
      ref.sha256 = sha256(bytes); ref.size_bytes = bytes.length;
    }
    const code = { missing: "CONDITION_SOURCE_MISSING", stale: "CONDITION_SOURCE_STALE", "wrong-kind": "CONDITION_TARGET_KIND", superseded: "CONDITION_CLAIM_IDENTITY" }[mode];
    assert.throws(() => compileFormalConditionBindings(graph, input, sources), { code });
  }
});

test("provider and evaluation metadata cannot become relationship or claim identity fields", () => {
  const { input, sources } = fixture();
  assert.throws(() => compileFormalConditionBindings(graph, { ...input, provider: "smt" }, sources), { code: "CONDITION_SCHEMA" });
  const changed = structuredClone(input);
  Object.assign(changed.bindings[0]!.claim_ref, { interpretation_model: "model-a" });
  assert.throws(() => compileFormalConditionBindings(graph, changed, sources), { code: "CONDITION_SCHEMA" });
});
