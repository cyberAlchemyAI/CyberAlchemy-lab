import path from "node:path";

import { decodeBody, type DecodedProjectNode } from "../../src/input/project-model.ts";
import type { SourceManifestV1 } from "../../src/input/source-manifest.ts";
import { FROZEN_META_TYPE_CATALOG } from "../../src/meta-types/catalog.ts";
import type { SupportedLanguage } from "../../src/meta-types/types.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";

const sourceManifest = Object.freeze({
  schema_version: "domainspec.stable-foundation-cli.source-manifest/v1",
  project_id: "test-project",
  source_count: 1,
  total_size_bytes: 1,
  sources: [],
  aggregate_sha256: "0".repeat(64),
  authority_effect: "none",
  manifest_sha256: "1".repeat(64),
}) as unknown as SourceManifestV1;

const samples: Readonly<Record<string, Record<string, unknown>>> = {
  Entity: { description: "Entity", identity_field: "account-id", fields: [{ field_id: "account-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, { field_id: "value", type_ref: { kind: "primitive", name: "string" }, required: true }] },
  Operation: { description: "Operation", reads: ["account"], writes: ["account.status"], effects: ["AccountChanged"], guard: "account-is-open", failure_continuation: "return-account-error" },
  Workflow: { description: "Workflow", steps: ["change-account"], compensations: ["restore-account"] },
  "State Machine": { description: "Account status", states: ["open", "changed"], initial: "open", transitions: [{ transition_id: "record-change", source_state: "open", target_state: "changed", guard_ref: null, effect_event_ref: "accounts:account-changed" }] },
};

export function testPlan(kind: "Entity" | "Operation" | "Workflow" | "State Machine", language: SupportedLanguage = "typescript") {
  const metaType = FROZEN_META_TYPE_CATALOG.backend_meta_types.find(({ label }) => label === kind);
  if (!metaType) throw new Error(`missing test meta-type:${kind}`);
  const node: DecodedProjectNode = Object.freeze({
    project_root: path.resolve("/tmp/test-project"),
    project_id: "test-project",
    feature_id: "accounts",
    node_id: kind === "Entity" ? "account" : kind === "Operation" ? "change-account" : kind === "Workflow" ? "account-workflow" : "account-status",
    kind,
    meta_type_id: metaType.id,
    body: decodeBody(kind, samples[kind]),
    relationships: Object.freeze(kind === "Operation" ? [{
      edge_id: "operation-creates-account",
      relationship: "creates",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "accounts", node_id: "change-account", kind: "Operation" }),
      target: Object.freeze({ feature_id: "accounts", node_id: "account", kind: "Entity" }),
    }, {
      edge_id: "operation-produces-event",
      relationship: "produces",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "accounts", node_id: "change-account", kind: "Operation" }),
      target: Object.freeze({ feature_id: "accounts", node_id: "account-changed", kind: "Event" }),
    }] : kind === "Workflow" ? [{
      edge_id: "workflow-orchestrates-compensation-operation",
      relationship: "orchestrates",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "accounts", node_id: "account-workflow", kind: "Workflow" }),
      target: Object.freeze({ feature_id: "accounts", node_id: "restore-account", kind: "Operation" }),
    }, {
      edge_id: "workflow-orchestrates-forward-operation",
      relationship: "orchestrates",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "accounts", node_id: "account-workflow", kind: "Workflow" }),
      target: Object.freeze({ feature_id: "accounts", node_id: "change-account", kind: "Operation" }),
    }] : kind === "State Machine" ? [{
      edge_id: "account-changed-transitions-account-status",
      relationship: "transitions",
      scope: "feature" as const,
      source: Object.freeze({ feature_id: "accounts", node_id: "account-changed", kind: "Event" }),
      target: Object.freeze({ feature_id: "accounts", node_id: "account-status", kind: "State Machine" }),
    }] : []),
    source_manifest: sourceManifest,
  });
  return planInstantiation(node, language);
}
