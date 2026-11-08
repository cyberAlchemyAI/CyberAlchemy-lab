import { describe, expect, it } from "vitest";

import { exactRef, readJson, repositoryRoot } from "./exact-ref.js";
import {
  buildCompositeReceipt,
  verifyCompositeReceipt,
} from "./receipt.js";
import { L1Error, type UnitReceipt } from "./types.js";

const repoRoot = repositoryRoot();
const p4Validation =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-002-P4/attempt-001/validation-receipt.json";
const r4Validation =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-003-R4/attempt-001/validation-receipt.json";
const p4ReceiptPath =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-002-P4/attempt-001/evolvable-validation-receipt.json";
const r4ReceiptPath =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-GCP-003-R4/attempt-001/evolvable-validation-receipt.json";

function build(p4 = readJson<UnitReceipt>(repoRoot, p4ReceiptPath), r4 = readJson<UnitReceipt>(repoRoot, r4ReceiptPath)) {
  return buildCompositeReceipt({
    p4,
    r4,
    p4Ref: exactRef(repoRoot, p4Validation),
    r4Ref: exactRef(repoRoot, r4Validation),
  });
}

describe("EVF L1 P4/R4 composite", () => {
  it("joins two distinct unit receipts on one graph/source handle", () => {
    const receipt = build();
    expect(() => verifyCompositeReceipt(receipt)).not.toThrow();
    expect(receipt.identity_denominators.rule_ids).toHaveLength(2);
    expect(new Set(receipt.identity_denominators.rule_ids).size).toBe(2);
    expect(receipt.join_checks.semantic_merge_forbidden).toBe(true);
  });

  it("rejects a different graph/source handle", () => {
    const r4 = structuredClone(readJson<UnitReceipt>(repoRoot, r4ReceiptPath)) as UnitReceipt & {
      graph_handle: UnitReceipt["graph_handle"] & { handle_digest: string };
    };
    r4.graph_handle.handle_digest = "0".repeat(64);
    expect(() => build(undefined, r4)).toThrowError(
      expect.objectContaining({ code: "SOURCE_GRAPH_DIGEST_STALE" }),
    );
  });

  it("rejects composite receipt tamper", () => {
    const receipt = structuredClone(build()) as ReturnType<typeof build> & { receipt_digest: string };
    receipt.receipt_digest = "0".repeat(64);
    try {
      verifyCompositeReceipt(receipt);
      throw new Error("tamper survived");
    } catch (error) {
      expect(error).toBeInstanceOf(L1Error);
      expect((error as L1Error).code).toBe("RECEIPT_TAMPERED");
    }
  });
});
