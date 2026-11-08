import { describe, expect, it } from "vitest";

import { buildOrderStatusProof } from "./run-proof.js";

describe("complete OrderStatus architecture realization proof", () => {
  it("joins positive, causal mutation, and independent replay under the bounded claim", async () => {
    const result = await buildOrderStatusProof();
    expect(result.state.current).toBe("proof-complete");
    expect(result.positive.evaluation).toMatchObject({
      verdict: "pass",
      obligation_accounting: { declared: 1, passed: 1, failed: 0, unaccounted: 0 },
    });
    expect(result.mutation.compile.exit_status).toBe(0);
    expect(result.mutation.evaluation.findings).toEqual([expect.objectContaining({
      code: "ARCH_ENUM_MEMBER_MISSING",
      member_id: "status.paid",
    })]);
    expect(result.replay).toMatchObject({ status: "pass", authority_effect: "none" });
    expect(result.proofReceipt).toMatchObject({
      state: "proof-complete",
      mutations: { declared: 1, killed: 1, survived: 0 },
      claim_ceiling: "one candidate-local direct TypeScript Enum proof",
      authority_effect: "none",
    });
    expect(Object.keys(result.artifacts)).toHaveLength(17);
    expect(JSON.stringify(result.artifacts)).not.toMatch(/canonical promotion|python|rust|deployment/u);
  }, 30_000);
});
