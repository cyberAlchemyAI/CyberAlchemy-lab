import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { exactRef, loadEvfS1Bundle } from "./derive.js";
import { executeEnforcesCases } from "./enforces-execution.js";
import {
  buildNegativeReceipt,
  buildPositiveReceipt,
  receiptDigest,
  verifyReceipt,
  verifyReceiptCurrent,
  type EvolvableValidationReceipt,
} from "./evolvable-validation-receipt.js";
import {
  ACCEPTANCE_VECTOR,
  EVF_PATHS,
  EXECUTION_CARDINALITY,
  EvfS1Error,
} from "./types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));

describe("EVF S1 non-admitting receipts", () => {
  it("builds and replays the bounded positive proof receipt", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const observations = executeEnforcesCases(
      bundle.predicate.predicate.ast,
      bundle.fixtures.cases,
    );
    const receipt = buildPositiveReceipt({
      exactRefs: [exactRef(REPO_ROOT, EVF_PATHS.validationContract)],
      observations,
    });
    const digest = receiptDigest(receipt);

    expect(() => verifyReceipt(receipt, digest)).not.toThrow();
    expect(receipt.acceptance_vector).toEqual(ACCEPTANCE_VECTOR);
    expect(receipt.execution_cardinality).toEqual(EXECUTION_CARDINALITY);
    expect(receipt.runtime_observations).toEqual(observations);
    expect(receipt.release_admission).toBe("not-granted");
    expect(receipt.claim_ceiling).toBe(
      "candidate-local-SWU-GCP-001-causal-proof-only",
    );
  });

  it("keeps a negative-control receipt non-positive and non-admitting", () => {
    const receipt = buildNegativeReceipt({
      mutantId: "M01-predicate-operator-ne",
      stableCode: "PREDICATE_OPERATOR_UNSUPPORTED",
      exactRefs: [exactRef(REPO_ROOT, EVF_PATHS.validationContract)],
    });

    expect(() => verifyReceipt(receipt)).not.toThrow();
    expect(receipt.positive_receipt_issued).toBe(false);
    expect(receipt.result).toBe("killed");
    expect(receipt.release_admission).toBe("not-granted");
    expect("acceptance_vector" in receipt).toBe(false);
  });

  it("rejects a receipt changed after its digest was retained", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const receipt = buildPositiveReceipt({
      exactRefs: [exactRef(REPO_ROOT, EVF_PATHS.validationContract)],
      observations: executeEnforcesCases(
        bundle.predicate.predicate.ast,
        bundle.fixtures.cases,
      ),
    });
    const digest = receiptDigest(receipt);
    const tampered = structuredClone(receipt) as unknown as {
      acceptance_vector: { mutants_killed: number };
    };
    tampered.acceptance_vector.mutants_killed = 15;

    try {
      verifyReceipt(tampered as unknown as EvolvableValidationReceipt, digest);
    } catch (error) {
      expect(error).toBeInstanceOf(EvfS1Error);
      expect((error as EvfS1Error).code).toBe("RECEIPT_TAMPERED");
      return;
    }
    throw new Error("expected receipt tamper rejection");
  });

  it("rejects a structurally valid receipt whose referenced bytes are stale", () => {
    const current = exactRef(REPO_ROOT, EVF_PATHS.validationContract);
    const receipt = buildNegativeReceipt({
      mutantId: "M01-predicate-operator-ne",
      stableCode: "PREDICATE_OPERATOR_UNSUPPORTED",
      exactRefs: [{ ...current, sha256: "0".repeat(64) }],
    });
    expect(() => verifyReceipt(receipt)).not.toThrow();
    try {
      verifyReceiptCurrent(receipt, REPO_ROOT, receipt.exact_refs);
    } catch (error) {
      expect(error).toBeInstanceOf(EvfS1Error);
      expect((error as EvfS1Error).code).toBe("ARTIFACT_STALE");
      return;
    }
    throw new Error("expected stale receipt ref rejection");
  });

  it("rejects a current but incomplete positive evidence set", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const observations = executeEnforcesCases(bundle.predicate.predicate.ast, bundle.fixtures.cases);
    const expectedRefs = [
      exactRef(REPO_ROOT, EVF_PATHS.validationContract),
      exactRef(REPO_ROOT, EVF_PATHS.binding),
    ];
    const receipt = buildPositiveReceipt({ exactRefs: expectedRefs.slice(0, 1), observations });
    try {
      verifyReceiptCurrent(receipt, REPO_ROOT, expectedRefs, observations);
    } catch (error) {
      expect(error).toBeInstanceOf(EvfS1Error);
      expect((error as EvfS1Error).code).toBe("RECEIPT_TAMPERED");
      return;
    }
    throw new Error("expected omitted evidence rejection");
  });
});
