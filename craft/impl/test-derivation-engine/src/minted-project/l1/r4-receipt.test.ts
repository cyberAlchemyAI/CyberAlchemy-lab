import { describe, expect, it } from "vitest";

import { deriveUnit, L1_PATHS } from "./derive.js";
import { exactRef, repositoryRoot } from "./exact-ref.js";
import { buildUnitReceipt, verifyUnitReceipt } from "./receipt.js";
import { L1Error, type UnitReceipt } from "./types.js";

const repoRoot = repositoryRoot();

function receipt(): UnitReceipt {
  const derivation = deriveUnit(repoRoot, "R4");
  return buildUnitReceipt({
    unit: "R4",
    graphHandle: derivation.graph_handle,
    evidenceRefs: [
      exactRef(repoRoot, L1_PATHS.r4Semantic),
      exactRef(repoRoot, L1_PATHS.r4Obligation),
      exactRef(repoRoot, L1_PATHS.r4Runtime),
      exactRef(repoRoot, L1_PATHS.r4Fixture),
      exactRef(repoRoot, L1_PATHS.r4Binding),
    ],
    acceptanceVector: { truth_table_cases: 5, mutants_required: 15, mutants_killed: 15, side_effects: 0 },
  });
}

describe("EVF L1 R4 receipt", () => {
  it("replays a pure-decision-only receipt", () => {
    const candidate = receipt();
    expect(() => verifyUnitReceipt(repoRoot, candidate)).not.toThrow();
    expect(candidate.claim_ceiling).toContain("pure-duplicate-makeup-decision-only");
  });

  it("rejects receipt tamper", () => {
    const candidate = structuredClone(receipt()) as UnitReceipt & { receipt_digest: string };
    candidate.receipt_digest = "0".repeat(64);
    try {
      verifyUnitReceipt(repoRoot, candidate);
      throw new Error("tamper survived");
    } catch (error) {
      expect(error).toBeInstanceOf(L1Error);
      expect((error as L1Error).code).toBe("RECEIPT_TAMPERED");
    }
  });
});
