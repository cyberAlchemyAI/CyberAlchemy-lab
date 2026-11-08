import {describe, expect, it} from "vitest";

import {readCompleteSettlement} from "./query-v1.js";

describe("TypeScript complete-settlement Query target", () => {
  it("performs the two declared reads in order and returns the closed view", async () => {
    const calls: string[] = [];
    const result = await readCompleteSettlement(
      {settlement_id: "settlement-001"},
      async (targetId, settlementId) => {
        calls.push(`${targetId}:${settlementId}`);
        return targetId === "settlement.read.settlement-by-id"
          ? {
            settlement_status: "complete",
            gross_amount_minor: 125000,
            payout_id: "unused",
            payout_status: "unused",
          }
          : {
            settlement_status: "unused",
            gross_amount_minor: 0,
            payout_id: "payout-001",
            payout_status: "recorded",
          };
      },
    );
    expect(calls).toEqual([
      "settlement.read.settlement-by-id:settlement-001",
      "settlement.read.payout-by-settlement:settlement-001",
    ]);
    expect(result).toEqual({
      settlement_id: "settlement-001",
      settlement_status: "complete",
      gross_amount_minor: 125000,
      payout_id: "payout-001",
      payout_status: "recorded",
    });
  });
});
