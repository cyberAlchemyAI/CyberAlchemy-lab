import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

import { planInstantiation } from "../dist/generation/plan-instantiation.js";
import { decodeBody } from "../dist/input/project-model.js";
import { FROZEN_META_TYPE_CATALOG } from "../dist/meta-types/catalog.js";
import { compileSystemIntegrationManifest, renderSystemIntegrationContract } from "../dist/system-integration/compiler.js";

const samples = {
  Entity: { description: "Entity", identity_field: "entity-id", fields: [{ field_id: "entity-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, { field_id: "value", type_ref: { kind: "primitive", name: "string" }, required: true }] },
  "Value Object": { description: "Value", fields: [{ field_id: "value", type_ref: { kind: "primitive", name: "string" }, required: true }], invariant_refs: ["feature:valid-value"] },
  Enum: { description: "Enum", values: ["one", "two"] },
  Operation: { description: "Operation", reads: ["entity"], writes: ["entity.state"], effects: ["Changed"], guard: "allowed", failure_continuation: "return-error" },
  Query: { description: "Query", reads: ["entity"] },
  Calculation: { description: "Calculation", inputs: ["left", "right"] },
  Rule: { description: "Rule", predicate: "candidate" },
  Policy: { description: "Policy", strategies: ["first"] },
  Workflow: { description: "Workflow", steps: ["operate"], compensations: ["undo"] },
  Interface: { description: "Interface", boundary_kind: "internal", version: "1", compatibility: "exact", operations: [{ operation_id: "operate", operation_ref: "feature:operate", request: [{ field_id: "entity-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }], result: [{ field_id: "accepted", type_ref: { kind: "primitive", name: "boolean" }, required: true }] }] },
  Event: { description: "Event", event_type: "event", version: "1", occurrence_id: { field_id: "occurrence-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, occurred_at_policy: "required", payload: [{ field_id: "entity-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }] },
  Mapping: { description: "Mapping", source: "Source", target: "Target" },
  "State Machine": { description: "Machine", states: ["new", "done"], initial: "new", transitions: [{ transition_id: "finish", source_state: "new", target_state: "done", guard_ref: null, effect_event_ref: null }] },
};

const sourceManifest = Object.freeze({
  schema_version: "domainspec.stable-foundation-cli.source-manifest/v1",
  project_id: "rust-validation",
  source_count: 1,
  total_size_bytes: 1,
  sources: [],
  aggregate_sha256: "0".repeat(64),
  authority_effect: "none",
  manifest_sha256: "1".repeat(64),
});

const root = fs.mkdtempSync(path.join(os.tmpdir(), "mtcli-rust-validation-"));
try {
  const compiled = [];
  for (const metaType of FROZEN_META_TYPE_CATALOG.backend_meta_types) {
    const nodeId = metaType.label.toLowerCase().replaceAll(" ", "-");
    const relationships = metaType.label === "Workflow" ? Object.freeze([
      Object.freeze({ edge_id: "workflow-operate", relationship: "orchestrates", scope: "feature", source: Object.freeze({ feature_id: "feature", node_id: nodeId, kind: "Workflow" }), target: Object.freeze({ feature_id: "feature", node_id: "operate", kind: "Operation" }) }),
      Object.freeze({ edge_id: "workflow-undo", relationship: "orchestrates", scope: "feature", source: Object.freeze({ feature_id: "feature", node_id: nodeId, kind: "Workflow" }), target: Object.freeze({ feature_id: "feature", node_id: "undo", kind: "Operation" }) }),
    ]) : metaType.label === "Interface" ? Object.freeze([
      Object.freeze({ edge_id: "interface-exposes-operate", relationship: "exposes", scope: "feature", source: Object.freeze({ feature_id: "feature", node_id: nodeId, kind: "Interface" }), target: Object.freeze({ feature_id: "feature", node_id: "operate", kind: "Operation" }) }),
    ]) : Object.freeze([]);
    const plan = planInstantiation(Object.freeze({
      project_root: "/synthetic-read-only",
      project_id: "rust-validation",
      feature_id: "feature",
      node_id: nodeId,
      kind: metaType.label,
      meta_type_id: metaType.id,
      body: decodeBody(metaType.label, samples[metaType.label]),
      relationships,
      source_manifest: sourceManifest,
    }), "rust");
    const source = path.join(root, `${nodeId}.rs`);
    const output = path.join(root, `${nodeId}.rlib`);
    fs.writeFileSync(source, plan.artifacts[0].content);
    const result = spawnSync("rustc", ["--edition", "2021", "--crate-type", "lib", "--crate-name", nodeId.replaceAll("-", "_"), source, "-o", output], { encoding: "utf8" });
    assert.equal(result.status, 0, `${metaType.label}\n${result.stdout}\n${result.stderr}`);
    compiled.push(Object.freeze({ meta_type_id: metaType.id, artifact_sha256: plan.artifacts[0].sha256 }));
  }
  const integrationFixture = JSON.parse(fs.readFileSync(path.resolve("../system-integration/fixtures/provider-neutral-v1/settlement-runtime.json"), "utf8"));
  const integrationManifest = compileSystemIntegrationManifest(integrationFixture, "rust");
  const integrationSource = path.join(root, "settlement-runtime.rs");
  const integrationOutput = path.join(root, "settlement-runtime.rlib");
  fs.writeFileSync(integrationSource, renderSystemIntegrationContract(integrationManifest));
  const integrationResult = spawnSync("rustc", ["--edition", "2024", "--crate-type", "lib", "--crate-name", "settlement_runtime", integrationSource, "-o", integrationOutput], { encoding: "utf8" });
  assert.equal(integrationResult.status, 0, `System Integration\n${integrationResult.stdout}\n${integrationResult.stderr}`);
  process.stdout.write(`${JSON.stringify({ schema_version: "domainspec.generated-rust-validation/v1", result: "pass", compiler: spawnSync("rustc", ["--version"], { encoding: "utf8" }).stdout.trim(), compiled, system_integration: { profile_id: integrationManifest.profile.profile_id, binding_digest: integrationManifest.binding_digest, runtime_guarantees_observed: integrationManifest.runtime_guarantees_observed }, authority_effect: "none" }, null, 2)}\n`);
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
