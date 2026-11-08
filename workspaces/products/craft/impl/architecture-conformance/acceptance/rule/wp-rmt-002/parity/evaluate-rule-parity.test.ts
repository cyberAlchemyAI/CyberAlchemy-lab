import {describe, expect, it} from "vitest";

import {evaluateRuleParity} from "../../parity/evaluate-rule-parity.js";

describe("WP-RMT-002 Rule parity normalization", () => {
  it("delegates portable comparison to the existing Rule parity evaluator", async () => {
    const observations = [
      {case_id: "first-payout-allowed", outcome: true,
        observed_effect_count: 0},
      {case_id: "duplicate-payout-denied", outcome: false,
        observed_effect_count: 0},
      {case_id: "zero-amount-denied", outcome: false,
        observed_effect_count: 0},
    ];
    const summary = {
      rule_id: "can-settle-payout",
      positive: observations.map(({case_id}) => ({case_id, status: "passed"})),
      mutations: [],
    };
    const source = (semantic_sha256: string) => ({
      summary, observations, semantic_sha256,
    });
    const result = await evaluateRuleParity({
      typescript: source("1".repeat(64)),
      python: source("2".repeat(64)),
      rust: source("3".repeat(64)),
    });
    expect(result.result).toBe("pass");
    expect(result.targets).toEqual(["typescript", "python", "rust"]);
    expect(result.excluded_target_diagnostics)
      .toContain("source and binding digests");
  });
});
