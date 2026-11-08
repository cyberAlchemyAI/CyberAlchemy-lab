import { describe, expect, it } from "vitest";
import { derive } from "../rules/index.js";

describe("current obligation key freshness", () => {
  it("invalidates when the selected rule set or source formula changes", () => {
    const graph = {
      nodes: [{ id: "calc#1", source_anchor: "calc#1", type: "Calculation" as const, fields: { id: "C1", formula: "sum(records.profit)" } }],
      edges: [],
    };
    const original = derive(graph, { version: "delta-1" })[0]!.obligation_key;
    expect(derive(graph, { version: "delta-2" })[0]!.obligation_key).not.toBe(original);
    const changed = {
      ...graph,
      nodes: [{ ...graph.nodes[0]!, fields: { id: "C1", formula: "sum(records.rakeback)" } }],
    };
    expect(derive(changed, { version: "delta-1" })[0]!.obligation_key).not.toBe(original);
    expect(derive(graph, { version: "delta-1" })[0]!.obligation_key).toBe(original);
  });
});
