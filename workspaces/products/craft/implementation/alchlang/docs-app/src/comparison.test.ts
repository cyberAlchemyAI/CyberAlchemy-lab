import { describe, expect, it } from "vitest";
import {
  canonicalJson,
  comparisonEvidence,
  comparisonPairs,
  comparisonParetoLayers,
  createComparisonPairs,
  observationComplete,
  preferenceDimensions,
  reviewComplete,
  scoreObservations,
  type PairObservation,
} from "./comparison";

function completeObservation(pairId: string, choice: "left" | "tie" | "right"): PairObservation {
  return {
    pairId,
    choices: Object.fromEntries(preferenceDimensions.map((dimension) => [dimension, choice])),
    note: "",
  };
}

describe("human comparison model", () => {
  it("creates all six pairs and alternates display order", () => {
    expect(createComparisonPairs()).toHaveLength(6);
    expect(comparisonPairs.map((pair) => pair.id)).toEqual([
      "baseline--compact-spacing",
      "baseline--progressive-reference",
      "baseline--task-first",
      "compact-spacing--progressive-reference",
      "compact-spacing--task-first",
      "progressive-reference--task-first",
    ]);
    expect(comparisonPairs[1]).toMatchObject({ left: "progressive-reference", right: "baseline" });
  });

  it("requires every dimension in every pair", () => {
    expect(observationComplete({ pairId: comparisonPairs[0].id, choices: { overall: "tie" }, note: "" })).toBe(false);
    const observations = Object.fromEntries(comparisonPairs.map((pair) => [pair.id, completeObservation(pair.id, "tie")]));
    expect(reviewComplete(observations)).toBe(true);
  });

  it("scores displayed sides correctly and gives ties half a point", () => {
    const first = comparisonPairs[0];
    const second = comparisonPairs[1];
    const scores = scoreObservations({
      [first.id]: completeObservation(first.id, "left"),
      [second.id]: completeObservation(second.id, "tie"),
    });
    expect(scores.baseline.readability).toBe(1.5);
    expect(scores["compact-spacing"].readability).toBe(0);
    expect(scores["progressive-reference"].readability).toBe(0.5);
  });

  it("keeps trade-offs on the frontier and layers dominated treatments", () => {
    const scores = scoreObservations({});
    scores.baseline = { readability: 3, navigation: 3, density: 3, task_completion: 3, overall: 3 };
    scores["compact-spacing"] = { readability: 2, navigation: 2, density: 2, task_completion: 2, overall: 2 };
    scores["progressive-reference"] = { readability: 4, navigation: 1, density: 4, task_completion: 1, overall: 4 };
    scores["task-first"] = { readability: 1, navigation: 4, density: 1, task_completion: 4, overall: 1 };
    expect(comparisonParetoLayers(scores)).toEqual([
      ["baseline", "progressive-reference", "task-first"],
      ["compact-spacing"],
    ]);
  });

  it("emits canonical, claim-bounded evidence only when complete", () => {
    const incomplete = comparisonEvidence({});
    expect(incomplete.status).toBe("incomplete");
    expect(incomplete.pareto_layers).toEqual([]);
    expect(canonicalJson({ z: 1, a: [2, 3] })).toBe('{"a":[2,3],"z":1}');
  });
});

