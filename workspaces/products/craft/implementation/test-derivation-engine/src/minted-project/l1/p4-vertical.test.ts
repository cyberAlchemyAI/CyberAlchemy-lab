import { describe, expect, it } from "vitest";

import { assertBindingRefs, deriveUnit, L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { runP4, type P4FixtureDocument } from "./p4.js";

const repoRoot = repositoryRoot();

describe("EVF L1 Financial Settlement P4 vertical", () => {
  it("rejects predecessor graph derivation with its stale source manifest", () => {
    expect(() => deriveUnit(repoRoot, "P4"))
      .toThrowError(expect.objectContaining({ code: "SOURCE_MANIFEST_INCOMPLETE" }));
  });

  it("rejects the old P4 binding path even though historical source is imported as a fixture", () => {
    const binding = readJson<Record<string, unknown>>(repoRoot, L1_PATHS.p4Binding);
    expect((binding.runtime_source_ref as { path: string }).path).toBe(
      "validation/poker-team/backend/src/domain/__derived__/financial-settlement.sfol.adapter.ts",
    );
    expect(() => assertBindingRefs(repoRoot, binding, "P4"))
      .toThrowError(expect.objectContaining({ code: "TARGET_BASELINE_DRIFT" }));
  });

  it("executes the real use case and observes one ordered payout write and event", async () => {
    const fixture = readJson<P4FixtureDocument>(repoRoot, L1_PATHS.p4Fixture);
    const result = await runP4(fixture);
    expect(result.status).toBe("pass");
    expect(result.effects.map((effect) => `${effect.kind}:${effect.name}`)).toEqual([
      "write:PAYOUT",
      "event:PayoutCreated",
    ]);
    expect(result.effects[0]!.amount).toBe(result.antecedent.total_payout);
    expect(result.effects[1]!.date).toBe(result.antecedent.end_date);
    expect(result.resources.closed).toHaveLength(3);
  });
});
