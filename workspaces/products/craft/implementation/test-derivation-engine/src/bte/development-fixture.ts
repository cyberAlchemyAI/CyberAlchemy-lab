import {
  BACKEND_RELATIONSHIPS,
  DEVELOPMENT_PROFILE_ID,
  type BackendKind,
  type DevelopmentEdge,
  type DevelopmentNode,
  type DevelopmentProject,
} from "./development-engine.js";

function node(
  suffix: string,
  kind: BackendKind,
  body: Record<string, unknown>,
  featureId = "core",
): DevelopmentNode {
  return {
    node_id: `${featureId}.${suffix}`,
    feature_id: featureId,
    kind,
    intent: `Development proof node for ${kind}.`,
    body,
  };
}

export function createCompleteDevelopmentProject(): DevelopmentProject {
  const nodes: DevelopmentNode[] = [
    node("Account", "Entity", {
      fields: [{ name: "account_id", type: "string", identity: true }],
    }),
    node("RemoteAccount", "Entity", {
      fields: [{ name: "account_id", type: "string", identity: true }],
    }, "external"),
    node("Money", "Value Object", {
      fields: [{ name: "amount", type: "decimal", identity: false }],
      equality: { strategy: "field-tuple", fields: ["amount"] },
    }),
    node("Status", "Enum", { values: ["pending", "active"] }),
    node("ChangeAccount", "Operation", { state_change: "yes" }),
    node("RemoteChange", "Operation", { state_change: "yes" }, "external"),
    node("GetAccount", "Query", { state_change: "no" }),
    node("Fee", "Calculation", { formal_return_type: "value" }),
    node("CanChange", "Rule", { formal_return_type: "boolean" }),
    node("Retry", "Policy", { formal_return_type: "strategy" }),
    node("AccountFlow", "Workflow", {
      scope: "intra-feature",
      steps: ["core.ChangeAccount"],
    }),
    node("AccountApi", "Interface", { interface_kind: "internal" }),
    node("AccountChanged", "Event", { temporal: "past" }),
    node("AccountMapper", "Mapping", { direction: "bidirectional" }),
    node("AccountState", "State Machine", {
      has_transitions: "yes",
      states: ["pending", "active"],
    }),
  ];
  const edges: DevelopmentEdge[] = [
    { edge_id: "edge-performs", family: "performs", from: "core.Account", to: "core.ChangeAccount" },
    { edge_id: "edge-produces", family: "produces", from: "core.ChangeAccount", to: "core.AccountChanged" },
    { edge_id: "edge-produces-for", family: "produces-for", from: "core.ChangeAccount", to: "external.RemoteAccount" },
    { edge_id: "edge-creates", family: "creates", from: "core.ChangeAccount", to: "core.Account" },
    { edge_id: "edge-triggers-cross", family: "triggers-cross", from: "core.AccountChanged", to: "external.RemoteChange" },
    { edge_id: "edge-enforces", family: "enforces", from: "core.CanChange", to: "core.ChangeAccount" },
    { edge_id: "edge-calculates", family: "calculates", from: "core.Fee", to: "core.ChangeAccount" },
    { edge_id: "edge-transitions", family: "transitions", from: "core.AccountChanged", to: "core.AccountState" },
    { edge_id: "edge-exposes", family: "exposes", from: "core.AccountApi", to: "core.GetAccount" },
    { edge_id: "edge-orchestrates", family: "orchestrates", from: "core.AccountFlow", to: "core.ChangeAccount", ordinal: 0 },
    { edge_id: "edge-applies", family: "applies", from: "core.Retry", to: "core.Fee" },
    { edge_id: "edge-maps", family: "maps", from: "core.AccountMapper", to: "core.Account" },
    { edge_id: "edge-contains", family: "contains", from: "core.Account", to: "core.Money" },
    { edge_id: "edge-reads", family: "reads", from: "core.GetAccount", to: "core.Account" },
    { edge_id: "edge-emits", family: "emits", from: "core.Account", to: "core.AccountChanged" },
    { edge_id: "edge-owns", family: "owns", from: "core.Account", to: "external.RemoteAccount" },
    { edge_id: "edge-belongs-to", family: "belongs-to", from: "external.RemoteAccount", to: "core.Account" },
  ];
  if (edges.map(({ family }) => family).join("|") !== BACKEND_RELATIONSHIPS.join("|")) {
    throw new Error("complete development fixture relationship order drifted");
  }
  return {
    schema_version: "bte-development-project/v1",
    project_id: "bte-development-complete",
    profile_id: DEVELOPMENT_PROFILE_ID,
    nodes,
    edges,
  };
}
