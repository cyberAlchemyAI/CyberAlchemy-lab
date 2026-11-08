import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {selectSettlementRoute} from "./policy-v1.js";

const here = dirname(fileURLToPath(import.meta.url));

describe("TypeScript bound Policy target", () => {
  it.each([
    [5000, 10000, false, false, "settlement.route.standard"],
    [5000, 10000, true, false, "settlement.route.expedited"],
    [5000, 10000, true, true, "settlement.route.manual-review"],
    [15000, 10000, true, false, "settlement.route.standard"],
    [5000, 4000, true, false, "settlement.route.standard"],
  ])("returns one strategy identity", (
    amountMinor,
    expediteLimitMinor,
    expediteRequested,
    manualReviewRequired,
    expected,
  ) => {
    const selected = selectSettlementRoute({
      amount_minor: amountMinor,
      expedite_limit_minor: expediteLimitMinor,
      expedite_requested: expediteRequested,
      manual_review_required: manualReviewRequired,
    });
    expect(selected).toBe(expected);
    expect(typeof selected).toBe("string");
  });

  it("is one exported synchronous arrow over explicit inputs", async () => {
    const source = await readFile(resolve(here, "policy-v1.ts"), "utf8");
    expect(source).toContain("export const selectSettlementRoute = (");
    expect(source).not.toMatch(/\bfunction\b/u);
    expect(source).not.toMatch(/\basync\b/u);
    expect(source).not.toMatch(/\b(?:Date|Math|process|globalThis|fetch|Promise)\b/u);
    expect(source).not.toMatch(/\b(?:import|require|new)\b/u);
  });
});
