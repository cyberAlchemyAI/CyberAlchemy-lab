import { describe, expect, it } from "vitest";

import { extractFacts } from "./extract.js";
import { validateProjection } from "./validate-facts.js";
import type { MintedGraph, PropertyDefinition } from "./types.js";

export function fixtureProperty(): PropertyDefinition {
  return {
    schema_version: "evf.graph-law-property/v1",
    property_id: "evf.l2.financial-settlement.rule-to-payout-event-reachability",
    property_version: "1",
    property_class: "reachability",
    result_semantics: "universal-via-violation-query",
    evaluation_mode: "exact-instance",
    selected_relation_digest: "52d5af6defbb4c3ebd3a77c2da847f73e830cf1a428da05bd2fe4c26a1b0bda5",
    selected_relation_digest_material: {
      closure: "non-reflexive-transitive-one-or-more",
      directed: true,
      required_sources: [
        "financial-settlement.NoDuplicateMakeupRule",
        "financial-settlement.PayoutEligibilityRule",
      ],
      selected_predicates: ["enforces", "produces"],
      target: "financial-settlement.PayoutCreatedEvent",
    },
    subject: {
      project_id: "financial-settlement",
      required_sources: [
        "financial-settlement.NoDuplicateMakeupRule",
        "financial-settlement.PayoutEligibilityRule",
      ],
      target: "financial-settlement.PayoutCreatedEvent",
      selected_predicates: ["enforces", "produces"],
    },
    claim_ceiling:
      "candidate-local-structural-reachability-over-one-exact-financial-settlement-graph-only",
    authority_effect: "none",
    release_admission: "not-granted",
  };
}

export function fixtureGraph(): MintedGraph {
  return {
    schema_version: "minted-graph/v1",
    authority: "generated-semantic-read-model",
    project_id: "financial-settlement",
    source_set_digest: "1".repeat(64),
    language: {
      profile_digest: "2".repeat(64),
      kinds_digest: "3".repeat(64),
      relationships_digest: "4".repeat(64),
    },
    nodes: [
      { node_id: "financial-settlement.PayoutEligibilityRule", feature_id: "financial-settlement", kind: "Rule" },
      { node_id: "financial-settlement.GenerateSettlement", feature_id: "financial-settlement", kind: "Operation" },
      { node_id: "financial-settlement.PayoutCreatedEvent", feature_id: "financial-settlement", kind: "Event" },
      { node_id: "financial-settlement.NoDuplicateMakeupRule", feature_id: "financial-settlement", kind: "Rule" },
      { node_id: "financial-settlement.DealSplitCalculation", feature_id: "financial-settlement", kind: "Calculation" },
    ],
    edges: [
      { edge_id: "e4", type: "enforces", from: "financial-settlement.PayoutEligibilityRule", to: "financial-settlement.GenerateSettlement" },
      { edge_id: "e2", type: "produces", from: "financial-settlement.GenerateSettlement", to: "financial-settlement.PayoutCreatedEvent" },
      { edge_id: "e1", type: "calculates", from: "financial-settlement.DealSplitCalculation", to: "financial-settlement.GenerateSettlement" },
      { edge_id: "e3", type: "enforces", from: "financial-settlement.NoDuplicateMakeupRule", to: "financial-settlement.GenerateSettlement" },
    ],
  };
}

describe("EVF L2 graph extraction", () => {
  it("projects the exact denominator deterministically with no body or inverse facts", () => {
    const first = extractFacts(fixtureGraph(), fixtureProperty());
    const reordered = fixtureGraph();
    const second = extractFacts(
      { ...reordered, nodes: [...reordered.nodes].reverse(), edges: [...reordered.edges].reverse() },
      fixtureProperty(),
    );
    expect(first).toEqual(second);
    expect(first.nodes).toHaveLength(5);
    expect(first.edges).toHaveLength(4);
    expect(first.selected_edges).toEqual([
      ["financial-settlement.GenerateSettlement", "financial-settlement.PayoutCreatedEvent"],
      ["financial-settlement.NoDuplicateMakeupRule", "financial-settlement.GenerateSettlement"],
      ["financial-settlement.PayoutEligibilityRule", "financial-settlement.GenerateSettlement"],
    ]);
    expect(Object.keys(first.nodes[0]!)).toEqual(["node_id", "feature_id", "kind"]);
  });

  it("rejects duplicate identities before sorting", () => {
    const graph = fixtureGraph();
    expect(() => extractFacts({ ...graph, nodes: [...graph.nodes, graph.nodes[0]!] }, fixtureProperty()))
      .toThrowError(expect.objectContaining({ code: "FACT_NODE_ID_DUPLICATE" }));
    expect(() => extractFacts({ ...graph, edges: [...graph.edges, graph.edges[0]!] }, fixtureProperty()))
      .toThrowError(expect.objectContaining({ code: "FACT_EDGE_ID_DUPLICATE" }));
  });

  it("rejects a missing endpoint", () => {
    const graph = fixtureGraph();
    const edges = [...graph.edges];
    edges[0] = { ...edges[0]!, to: "missing.Node" };
    expect(() => extractFacts({ ...graph, edges }, fixtureProperty()))
      .toThrowError(expect.objectContaining({ code: "FACT_ENDPOINT_MISSING" }));
  });

  it("independently rejects omitted, invented, or digest-stale projections", () => {
    const graph = fixtureGraph();
    const projection = extractFacts(graph, fixtureProperty());
    expect(() => validateProjection(graph, fixtureProperty(), {
      ...projection,
      edges: projection.edges.slice(1),
    })).toThrowError(expect.objectContaining({ code: "FACT_PROJECTION_DRIFT" }));
    expect(() => validateProjection(graph, fixtureProperty(), {
      ...projection,
      facts_digest: "0".repeat(64),
    })).toThrowError(expect.objectContaining({ code: "FACT_DIGEST_MISMATCH" }));
  });
});
