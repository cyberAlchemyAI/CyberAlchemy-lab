import { describe, expect, it } from "vitest";

import { deriveUnit } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { verifyUnitReceipt } from "./receipt.js";
import { L1Error, type UnitReceipt } from "./types.js";

const repoRoot = repositoryRoot();
const HISTORICAL_RECEIPT =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-003-R4/attempt-001/evolvable-validation-receipt.json";

function historicalReceipt(): UnitReceipt {
  return readJson<UnitReceipt>(repoRoot, HISTORICAL_RECEIPT);
}

describe("EVF L1 R4 historical receipt", () => {
  it("rejects the predecessor manifest against current authored source", () => {
    expect(() => deriveUnit(repoRoot, "R4"))
      .toThrowError(expect.objectContaining({ code: "SOURCE_MANIFEST_INCOMPLETE" }));
  });

  it("rejects the persisted v1 receipt against the changed graph source", () => {
    const candidate = historicalReceipt();
    expect(candidate.claim_ceiling).toContain("pure-duplicate-makeup-decision-only");
    expect(() => verifyUnitReceipt(repoRoot, candidate))
      .toThrowError(expect.objectContaining({ code: "SOURCE_GRAPH_DIGEST_STALE" }));
  });

  it("rejects persisted receipt tamper before evaluating stale source refs", () => {
    const candidate = structuredClone(historicalReceipt()) as UnitReceipt & { receipt_digest: string };
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
