import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { runCli } from "../../src/cli/main.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const canonical = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");

export const L1_QUERY = {
  schema_version: "domainspec.typed-query/v1", ontology_query: "BACKEND-QUERY-CUSTOMER", source: "alpha:customer",
  inputs: [{ name: "customer_id", type: { kind: "scalar", name: "String" } }],
  filter: { op: "eq", left: { kind: "field", name: "customer_id" }, right: { kind: "parameter", name: "customer_id" } },
  projection: ["customer_id", "settlement_details"], order_by: { field: "customer_id", direction: "asc" }, limit: 1,
};
export const L1_CALCULATION = {
  schema_version: "domainspec.typed-calculation/v1", ontology_calculation: "BACKEND-CALCULATION-TOTAL",
  inputs: ["subtotal", "fee", "divisor"].map((name) => ({ name, type: { kind: "scalar", name: "UInt64" } })),
  result: { kind: "scalar", name: "UInt64" }, division_rounding: "ceil",
  expression: { op: "divide", left: { op: "add", left: { op: "input", name: "subtotal" }, right: { op: "input", name: "fee" } }, right: { op: "input", name: "divisor" } },
};
export const L1_MAPPING = {
  schema_version: "domainspec.typed-mapping/v1", ontology_mapping: "BACKEND-MAPPING-CUSTOMER", source: "alpha:customer", target: "alpha:customer", total: true,
  fields: [
    { target: "customer_id", source: "customer_id", default: null },
    { target: "settlement_details", source: "settlement_details", default: null },
    { target: "preferred_method", source: "preferred_method", default: { type: "String", value: "standard" } },
  ],
};
export const L1_POLICY = {
  schema_version: "domainspec.typed-policy/v1", ontology_policy: "BACKEND-POLICY-SETTLEMENT",
  inputs: [{ name: "amount", type: { kind: "scalar", name: "UInt64" } }],
  cases: [{ target: "alpha:total-cost", when: { op: "gt", left: { kind: "parameter", name: "amount" }, right: { kind: "literal", type: "UInt64", value: 100 } } }],
  default_target: "alpha:settle",
};

function readJson(file: string): Record<string, unknown> { return JSON.parse(fs.readFileSync(file, "utf8")) as Record<string, unknown>; }
function writeJson(file: string, value: unknown): void { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`); }

function add(root: string, kind: string, name: string, contract: unknown): void {
  const errors: string[] = [];
  const calculationTarget = kind === "calculation" ? ["--calculates", "settle"] : [];
  const result = runCli(["add", kind, root, "--feature", "alpha", "--name", name, "--description", `L1 ${kind} fixture.`, "--contract-json", JSON.stringify(contract), ...calculationTarget], { stdout: () => undefined, stderr: (entry) => errors.push(entry) });
  assert.equal(result, 0, errors.at(-1));
}

function appendFeature(root: string, featureId: string, nodes: readonly string[], edges: readonly string[]): void {
  const file = path.join(root, `specs/${featureId}/feature.json`);
  const feature = readJson(file) as { nodes: string[]; edges: string[] } & Record<string, unknown>;
  feature.nodes.push(...nodes); feature.nodes.sort();
  feature.edges.push(...edges); feature.edges.sort();
  writeJson(file, feature);
}

function featureEdge(root: string, featureId: string, edgeId: string, relationship: string, source: string, target: string): void {
  writeJson(path.join(root, `specs/${featureId}/edges/${edgeId}.json`), { schema_version: "domainspec.edge/v1", edge_id: edgeId, feature_id: featureId, relationship, source_node_id: source, target_node_id: target, scope: "feature" });
}

function projectEdge(root: string, edgeId: string, relationship: string, sourceFeature: string, source: string, targetFeature: string, target: string): void {
  writeJson(path.join(root, `edges/${edgeId}.json`), { schema_version: "domainspec.edge/v1", edge_id: edgeId, source_feature_id: sourceFeature, source_node_id: source, target_feature_id: targetFeature, target_node_id: target, relationship, scope: "project" });
  const file = path.join(root, "project.json");
  const project = readJson(file) as { cross_feature_edges: string[] } & Record<string, unknown>;
  project.cross_feature_edges.push(edgeId); project.cross_feature_edges.sort(); writeJson(file, project);
}

export function createCompleteL1Project(): { readonly root: string; readonly parent: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l1-"));
  const root = path.join(parent, "source");
  fs.cpSync(canonical, root, { recursive: true });
  const rulePath = path.join(root, "specs/beta/nodes/can-complete-settlement.json");
  const rule = readJson(rulePath);
  rule.body = {
    description: "Settlement may complete when the requested amount is below its limit.",
    predicate: "structured:domainspec.typed-rule/v1",
    typed_contract: {
      schema_version: "domainspec.typed-rule/v1", ontology_rule: "SETTLEMENT-RULE-CAN-COMPLETE",
      parameters: [{ name: "amount", type: { kind: "scalar", name: "UInt64" } }],
      expression: { op: "lt", left: { op: "path", root: "amount", properties: [] }, right: { op: "literal", type: "UInt64", value: 100 } },
    },
  };
  writeJson(rulePath, rule);
  add(root, "query", "find-customer", L1_QUERY);
  add(root, "calculation", "total-cost", L1_CALCULATION);
  add(root, "mapping", "normalize-customer", L1_MAPPING);
  add(root, "policy", "settlement-policy", L1_POLICY);
  writeJson(path.join(root, "specs/alpha/nodes/settlement-flow.json"), {
    schema_version: "domainspec.node/v1", node_id: "settlement-flow", feature_id: "alpha", kind: "Workflow",
    body: { description: "L1 workflow fixture.", steps: ["settle"], compensations: [], compensation_dependencies: [] },
  });
  writeJson(path.join(root, "specs/alpha/nodes/settlement-requested.json"), {
    schema_version: "domainspec.node/v1", node_id: "settlement-requested", feature_id: "alpha", kind: "Event",
    body: { description: "L1 produced event fixture.", event_type: "settlement-requested", version: "1", occurrence_id: { field_id: "occurrence-id", type_ref: { kind: "primitive", name: "uuid" }, required: true }, occurred_at_policy: "generated", payload: [] },
  });
  writeJson(path.join(root, "specs/beta/nodes/record-settlement-request.json"), {
    schema_version: "domainspec.node/v1", node_id: "record-settlement-request", feature_id: "beta", kind: "Operation",
    body: { description: "Consume one settlement request Event idempotently.", reads: ["settlement-inbox"], writes: ["settlement-audit"], effects: [], guard: "message-id-not-processed", failure_continuation: "retry" },
  });
  const alphaEdges = [
    ["settle-produces-settlement-requested", "produces", "settle", "settlement-requested"],
    ["settlement-flow-orchestrates-settle", "orchestrates", "settlement-flow", "settle"],
  ] as const;
  for (const [edgeId, relationship, source, target] of alphaEdges) featureEdge(root, "alpha", edgeId, relationship, source, target);
  appendFeature(root, "alpha", ["settlement-flow", "settlement-requested"], alphaEdges.map(([id]) => id));
  const betaEdges = [
    ["audit-contains-settlement-details", "contains", "audit", "settlement-details"],
    ["settled-emits-settlement-completed", "emits", "settled", "settlement-completed"],
  ] as const;
  for (const [edgeId, relationship, source, target] of betaEdges) featureEdge(root, "beta", edgeId, relationship, source, target);
  appendFeature(root, "beta", ["record-settlement-request"], betaEdges.map(([id]) => id));
  projectEdge(root, "settle-produces-for-settled", "produces-for", "alpha", "settle", "beta", "settled");
  projectEdge(root, "can-complete-enforces-settle", "enforces", "beta", "can-complete-settlement", "alpha", "settle");
  projectEdge(root, "settlement-requested-triggers-record", "triggers-cross", "alpha", "settlement-requested", "beta", "record-settlement-request");
  const integrationPath = path.join(root, "integrations/settle-runtime.json");
  const integration = readJson(integrationPath);
  integration.message_channels = [
    { channel_id: "settlement-events", purpose: "delivery", allowed_event_refs: ["alpha:settlement-requested"], publisher_operation_refs: ["alpha:settle"], consumer_operation_refs: ["beta:record-settlement-request"], evidence_boundary: "formation-only-no-delivery-claim" },
    { channel_id: "settlement-events-dead-letter", purpose: "dead-letter", allowed_event_refs: ["alpha:settlement-requested"], publisher_operation_refs: [], consumer_operation_refs: [], evidence_boundary: "terminal-route-configuration-only" },
  ];
  integration.delivery_policies = [{ policy_id: "settlement-delivery", semantics: "at-least-once", acknowledgement_boundary: "provider-accepted", ordering_scope: "none", visibility_timeout_seconds: 60, retention_seconds: 345600, max_receive_count: 5, dead_letter_channel_ref: "settlement-events-dead-letter", deduplication_owner_ref: "consumer:inbox-message-id", evidence_boundary: "provider-acceptance-is-not-application-commit" }];
  integration.transport_failure_policies = [{ policy_id: "settlement-transport-failure", retry_eligibility: "idempotent-message-id-only", max_attempts: 5, backoff: "exponential-bounded", unknown_outcome: "reconcile-by-message-id", terminal_action: "dead-letter", evidence_boundary: "bounded-attempt-observation-only" }];
  integration.transport_bindings = [{ binding_id: "settlement-message-transport", mode: "message", direction: "publish-subscribe", operation_ref: "alpha:settle", event_ref: "alpha:settlement-requested", channel_ref: "settlement-events", delivery_policy_ref: "settlement-delivery", failure_policy_ref: "settlement-transport-failure", envelope_profile_ref: "envelope:domainspec-event-json-v1", evidence_boundary: "intent-send-acceptance-delivery-and-commit-remain-distinct" }];
  writeJson(integrationPath, integration);
  return Object.freeze({ root, parent });
}

export function completeL2Invocation(): Record<string, unknown> {
  return {
    schema_version: "domainspec.runtime-invocation/v1", invocation_id: "complete-backend", provider: "in-memory-v1",
    steps: [
      { step_id: "customer", selector: "alpha:customer", input: { record: { "customer-id": "customer-1", "settlement-details": "details-1", "preferred-method": "card" } } },
      { step_id: "settle", selector: "alpha:settle", input: { state: { customer: "customer-1", "customer.settlement-status": "pending" }, changes: { "customer.settlement-status": "settled" }, guard: true } },
      { step_id: "record-settlement-request", selector: "beta:record-settlement-request", input: { state: { "settlement-inbox": "message-1" }, changes: { "settlement-audit": "recorded" }, guard: true } },
      { step_id: "api", selector: "alpha:settlement-api", input: { requested_version: "1" } },
      { step_id: "query", selector: "alpha:find-customer", input: { rows: [{ customer_id: "b", settlement_details: "B" }, { customer_id: "a", settlement_details: "A" }], parameters: { customer_id: "a" } } },
      { step_id: "calculation", selector: "alpha:total-cost", input: { inputs: { subtotal: 10, fee: 1, divisor: 2 } } },
      { step_id: "mapping", selector: "alpha:normalize-customer", input: { source: { customer_id: "a", settlement_details: "A" } } },
      { step_id: "policy", selector: "alpha:settlement-policy", input: { parameters: { amount: 101 } } },
      { step_id: "workflow", selector: "alpha:settlement-flow", input: {} },
      { step_id: "requested-event", selector: "alpha:settlement-requested", input: { occurrence_id: "event-1", occurred_at: "2026-09-03T00:00:00.000Z", payload: {} } },
      { step_id: "audit", selector: "beta:audit", input: { record: { "audit-id": "audit-1" } } },
      { step_id: "settled", selector: "beta:settled", input: { record: { "settled-id": "settled-1" } } },
      { step_id: "rule", selector: "beta:can-complete-settlement", input: { parameters: { amount: 50 } } },
      { step_id: "completed-event", selector: "beta:settlement-completed", input: { occurrence_id: "event-2", occurred_at: "2026-09-03T00:00:01.000Z", payload: { "customer-id": "customer-1", details: "details-1" } } },
      { step_id: "details", selector: "beta:settlement-details", input: { left: { amount: 10, method: "card" }, right: { amount: 10, method: "card" } } },
      { step_id: "method", selector: "beta:settlement-method", input: { value: "card" } },
      { step_id: "state", selector: "beta:settlement-status", input: { current_state: "pending", transition_id: "complete-settlement", guards: { "beta:can-complete-settlement": true } } },
    ],
  };
}
