import { describe, expect, it } from "vitest";

import { assertBindingRefs, deriveUnit, L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { historicalR4Obligation } from "./historical-r4-obligation.js";
import { runR4, type R4FixtureDocument } from "./r4.js";

const repoRoot = repositoryRoot();

describe("EVF L1 Financial Settlement R4 vertical", () => {
  it("rejects predecessor graph derivation with its stale source manifest", () => {
    expect(() => deriveUnit(repoRoot, "R4"))
      .toThrowError(expect.objectContaining({ code: "SOURCE_MANIFEST_INCOMPLETE" }));
  });

  it("rejects the old R4 binding path despite the exact historical source bytes", () => {
    const binding = readJson<Record<string, unknown>>(repoRoot, L1_PATHS.r4Binding);
    expect((binding.runtime_source_ref as { path: string }).path).toBe(
      "validation/poker-team/backend/src/domain/settlement/settlement.service.ts",
    );
    expect(() => assertBindingRefs(repoRoot, binding, "R4"))
      .toThrowError(expect.objectContaining({ code: "TARGET_BASELINE_DRIFT" }));
    expect(binding.decision_field).toBe("shouldCreateMakeupAppliedEvent");
  });

  it("executes five contract-only historical decisions without a side-effect claim", () => {
    const fixture = readJson<R4FixtureDocument>(repoRoot, L1_PATHS.r4Fixture);
    const result = runR4(fixture, historicalR4Obligation());
    expect(result.observations).toHaveLength(5);
    expect(result.observations.every((entry) => entry.actual === entry.expected)).toBe(true);
    expect(result.side_effect_observation).toBe("none-pure-decision-only");
  });
});
