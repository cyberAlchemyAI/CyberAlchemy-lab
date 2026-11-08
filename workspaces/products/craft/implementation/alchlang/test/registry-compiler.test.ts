import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { compileOperationPatternRegistry, compileRegistryConfig } from "../src/index.js";

const configPath = path.resolve(import.meta.dirname, "../../extensions/generatable-operation-patterns-v1/registry/registry-compiler.config.json");

test("registry compiler replays deterministically from exact sources", () => {
  const first = compileRegistryConfig(configPath);
  const second = compileRegistryConfig(configPath);
  assert.deepEqual(first, second);
  assert.equal(first.registry.patterns.length, 2);
  assert.equal(first.registry.patterns.find((row) => row.pattern_id === "operation-port")?.availability, "available");
});

test("registry closure fails closed independently for each prerequisite", () => {
  const base = {
    admitted_meta_types: ["DS-D1.4"],
    pattern_intents: [{ pattern_id: "p", architecture_pattern_status: "candidate" as const, meta_type_ref: "DS-D1.4", integration_binding_ref: "b", generator_ref: "g", conformance_ref: "c", generated_artifacts: ["x"] }],
    integration_bindings: [{ binding_id: "b", status: "closed" as const, manifest_ref: "b.json", manifest_sha256: "binding" }],
    generators: [{ generator_id: "g", status: "closed" as const, source_refs: ["g.ts"], source_tree_sha256: "generator" }],
    conformance: [{ conformance_id: "c", status: "PASS" as const, generator_ref: "g", generator_sha256: "generator", binding_ref: "b", binding_sha256: "binding" }],
    resolved_binding_digests: { b: "binding" },
    resolved_generator_digests: { g: "generator" }
  };
  assert.equal(compileOperationPatternRegistry(base).patterns[0].availability, "available");
  const drifted = compileOperationPatternRegistry({ ...base, resolved_generator_digests: { g: "drift" } }).patterns[0];
  assert.equal(drifted.availability, "blocked");
  assert.deepEqual(drifted.blockers, ["GENERATOR_DIGEST_DRIFT:g", "CONFORMANCE_EVIDENCE_STALE:c"]);
  assert.throws(() => compileOperationPatternRegistry({ ...base, pattern_intents: [...base.pattern_intents, ...base.pattern_intents] }), /REGISTRY_DUPLICATE/);
});
