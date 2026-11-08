import { describe, expect, it } from "vitest";
import type { ConceptGraph } from "../ir/types.js";
import { derive } from "../rules/index.js";

describe("local relationship freshness", () => {
  const invariant = { id: "invariant#1", source_anchor: "invariant#1", type: "Invariant" as const,
    fields: { id: "I1", formal: "x >= 0" } };
  const operation = { id: "operation#1", source_anchor: "operation#1", type: "Operation" as const,
    fields: { id: "O1" } };
  const base: ConceptGraph = { nodes: [invariant, operation], edges: [] };
  const key = (graph: ConceptGraph) => derive(graph).find((obligation) => obligation.source_anchor === invariant.source_anchor)!.obligation_key;

  it("retires the old key when an incident admitted graph relation changes", () => {
    const linked: ConceptGraph = { ...base, edges: [{ from: operation.id, to: invariant.id, type: "enforces" }] };
    expect(key(linked)).not.toBe(key(base));
    expect(key(linked)).toBe(key({ ...linked, edges: [...linked.edges] }));
    const changedNeighbor: ConceptGraph = { ...linked, nodes: [invariant,
      { ...operation, fields: { id: "O2" } }] };
    expect(key(changedNeighbor)).not.toBe(key(linked));
  });

  it("preserves a local key when only an unrelated graph island changes", () => {
    const unrelated: ConceptGraph = { ...base, nodes: [...base.nodes,
      { id: "other#1", source_anchor: "other#1", type: "Operation", fields: { id: "Other" } }] };
    expect(key(unrelated)).toBe(key(base));
  });
});
