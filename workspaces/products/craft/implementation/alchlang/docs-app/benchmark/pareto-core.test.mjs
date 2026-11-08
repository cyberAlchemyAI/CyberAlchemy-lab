import { describe, expect, it } from "vitest";
import { dominates, paretoLayers, roundRobin } from "./pareto-core.mjs";

const objectives = [
  { id: "length", direction: "min", epsilon: 1 },
  { id: "coverage", direction: "max", epsilon: 0.02 },
];

describe("Pareto tournament core", () => {
  it("preserves trade-offs and removes dominated candidates", () => {
    const candidates = [
      { id: "complete", values: { length: 20, coverage: 1 } },
      { id: "minimal", values: { length: 10, coverage: 0.7 } },
      { id: "worse", values: { length: 30, coverage: 0.7 } },
    ];
    expect(paretoLayers(candidates, objectives)).toEqual([["complete", "minimal"], ["worse"]]);
    expect(dominates(candidates[0], candidates[2], objectives)).toBe(true);
  });

  it("treats differences inside epsilon as practical ties", () => {
    const left = { id: "left", values: { length: 20, coverage: 1 } };
    const right = { id: "right", values: { length: 20.5, coverage: 0.99 } };
    expect(dominates(left, right, objectives)).toBe(false);
    expect(dominates(right, left, objectives)).toBe(false);
  });

  it("creates a complete tie-aware round robin", () => {
    expect(roundRobin(["c", "a", "b"])).toEqual([
      { left: "a", right: "b", randomize_order: true, allow_tie: true },
      { left: "a", right: "c", randomize_order: true, allow_tie: true },
      { left: "b", right: "c", randomize_order: true, allow_tie: true },
    ]);
  });
});
