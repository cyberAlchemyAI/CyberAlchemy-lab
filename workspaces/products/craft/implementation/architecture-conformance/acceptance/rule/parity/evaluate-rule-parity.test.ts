import { describe, expect, it } from "vitest";

import { evaluateRuleParity } from "./evaluate-rule-parity.js";

describe("TypeScript, Python, and Rust Rule semantic parity", () => {
  it("joins normalized outcomes and findings while excluding target diagnostics", async () => {
    const observations = [
      { case_id: "duplicate-payout-denied", outcome: false, observed_effect_count: 0 },
      { case_id: "first-payout-allowed", outcome: true, observed_effect_count: 0 },
      { case_id: "zero-amount-denied", outcome: false, observed_effect_count: 0 },
    ];
    const summary = {
      rule_id: "can-settle-payout",
      positive: observations.map(({ case_id }) => ({ case_id, status: "passed" })),
      mutations: [
        { mutation_id: "wrong-result", case_id: "first-payout-allowed",
          finding_code: "RULE_OUTCOME_MISMATCH", status: "killed" },
        { mutation_id: "bypass-check", case_id: "duplicate-payout-denied",
          finding_code: "RULE_OUTCOME_MISMATCH", status: "killed" },
        { mutation_id: "observable-effect", case_id: "first-payout-allowed",
          finding_code: "RULE_EFFECT_OBSERVED", status: "killed" },
      ],
    };
    const source = (semantic_sha256: string) => ({ summary, observations, semantic_sha256 });
    const result = await evaluateRuleParity({
      typescript: source("1".repeat(64)),
      python: source("2".repeat(64)),
      rust: source("3".repeat(64)),
    });
    expect(result.result).toBe("pass");
    expect(result.diagnostics).toEqual([]);
    expect(result.semantic_projection.cases).toEqual([
      { case_id: "duplicate-payout-denied", outcome: false, observed_effect_count: 0 },
      { case_id: "first-payout-allowed", outcome: true, observed_effect_count: 0 },
      { case_id: "zero-amount-denied", outcome: false, observed_effect_count: 0 },
    ]);
    expect(result.semantic_projection.mutations).toHaveLength(3);
    expect(result.excluded_target_diagnostics).toContain("compiler paths and versions");
    expect(result.parity_sha256).toMatch(/^[a-f0-9]{64}$/u);
  });
});
