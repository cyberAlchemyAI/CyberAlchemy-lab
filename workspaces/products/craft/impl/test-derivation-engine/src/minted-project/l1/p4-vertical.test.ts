import { describe, expect, it } from "vitest";

import { assertBindingRefs, deriveUnit, L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { runP4, type P4FixtureDocument } from "./p4.js";

const repoRoot = repositoryRoot();

describe("EVF L1 Financial Settlement P4 vertical", () => {
  it("keeps O_spec and O_gen equal over one exact enforces edge", () => {
    const derivation = deriveUnit(repoRoot, "P4");
    expect(derivation.comparison).toBe("equal");
    expect(derivation.O_spec).toEqual(derivation.O_gen);
    expect(derivation.identity.rule_id).toBe("financial-settlement.PayoutEligibilityRule");
    expect(derivation.identity.edge_id).toBe("financial-settlement.edge.payout-rule-enforces-generation");
  });

  it("resolves every P4 binding ref exactly", () => {
    const binding = readJson<Record<string, unknown>>(repoRoot, L1_PATHS.p4Binding);
    expect(() => assertBindingRefs(repoRoot, binding, "P4")).not.toThrow();
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
