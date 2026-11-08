import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {evaluateRuleV1, RULE_V1_DELEGATE} from "./rule-v1.js";

const here = dirname(fileURLToPath(import.meta.url));

describe("WP-RMT-002 TypeScript Rule adapter", () => {
  it("delegates all three declared cases to the existing bound Rule", () => {
    const cases = [
      [{requestId: "request-001", amount: 12500,
        existingSettlementId: null}, true],
      [{requestId: "request-002", amount: 12500,
        existingSettlementId: "settlement-001"}, false],
      [{requestId: "request-003", amount: 0,
        existingSettlementId: null}, false],
    ] as const;
    for (const [input, expected] of cases) {
      const snapshot = JSON.stringify(input);
      expect(evaluateRuleV1(input)).toBe(expected);
      expect(evaluateRuleV1(input)).toBe(expected);
      expect(JSON.stringify(input)).toBe(snapshot);
      expect(typeof evaluateRuleV1(input)).toBe("boolean");
    }
  });

  it("declares the existing outcome-function realization as its delegate", () => {
    expect(RULE_V1_DELEGATE).toEqual({
      rule_id: "can-settle-payout",
      realization_id: "rule.typescript.bound-arrow-function-v1",
      provider_id: "typescript-rule-v1",
      authority_effect: "none",
    });
  });

  it("contains no ambient effect or Operation invocation surface", async () => {
    const source = await readFile(resolve(here, "rule-v1.ts"), "utf8");
    for (const forbidden of [
      "fetch(", "node:fs", "node:net", "process.env", "Date.now(",
      "Math.random(", "completeSettlementOperation(",
    ]) {
      expect(source).not.toContain(forbidden);
    }
  });
});
