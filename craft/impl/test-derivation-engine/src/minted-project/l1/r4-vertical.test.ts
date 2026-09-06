import { describe, expect, it } from "vitest";

import { assertBindingRefs, deriveUnit, L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { runR4, type R4FixtureDocument } from "./r4.js";

const repoRoot = repositoryRoot();

describe("EVF L1 Financial Settlement R4 vertical", () => {
  it("derives the distinct R4 obligation on the frozen two-rule graph", () => {
    const p4 = deriveUnit(repoRoot, "P4");
    const r4 = deriveUnit(repoRoot, "R4");
    expect(r4.comparison).toBe("equal");
    expect(r4.O_spec).toEqual(r4.O_gen);
    expect(r4.identity.rule_id).not.toBe(p4.identity.rule_id);
    expect(r4.identity.edge_id).not.toBe(p4.identity.edge_id);
    expect(r4.graph_handle.handle_digest).toBe(p4.graph_handle.handle_digest);
  });

  it("resolves the R4 pure-decision binding exactly", () => {
    const binding = readJson<Record<string, unknown>>(repoRoot, L1_PATHS.r4Binding);
    expect(() => assertBindingRefs(repoRoot, binding, "R4")).not.toThrow();
    expect(binding.decision_field).toBe("shouldCreateMakeupAppliedEvent");
  });

  it("executes five actual pure-decision cases without a side-effect claim", () => {
    const derivation = deriveUnit(repoRoot, "R4");
    const fixture = readJson<R4FixtureDocument>(repoRoot, L1_PATHS.r4Fixture);
    const result = runR4(fixture, derivation.O_spec);
    expect(result.observations).toHaveLength(5);
    expect(result.observations.every((entry) => entry.actual === entry.expected)).toBe(true);
    expect(result.side_effect_observation).toBe("none-pure-decision-only");
  });
});
