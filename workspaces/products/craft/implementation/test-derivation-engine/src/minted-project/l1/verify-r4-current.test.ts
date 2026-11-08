import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { digestValue, exactRef, readJson } from "./exact-ref.js";
import { L1Error } from "./types.js";
import { loadCurrentR4Binding, R4_CURRENT_ATTEMPT, R4_CURRENT_BINDING,
  replayStoredCurrentR4Receipt, runCurrentR4Verification,
  verifyCurrentR4Receipt, type CurrentR4Receipt } from "./verify-r4-current.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));
const receiptPath = `${R4_CURRENT_ATTEMPT}/terminal-receipt.json`;

function resign(receipt: CurrentR4Receipt): CurrentR4Receipt {
  const { receipt_digest: _ignored, ...unsigned } = receipt;
  return { ...unsigned, receipt_digest: digestValue(unsigned) };
}

describe("current R4 composite terminal candidate", () => {
  it("reproduces the persisted current R4 receipt and full P4 graph handle", async () => {
    const result = await runCurrentR4Verification(repoRoot);
    expect(result.status).toBe("pass");
    expect(result.mutation_count).toBe(15);
    expect(result.receipt_ref).toEqual(exactRef(repoRoot, receiptPath));
    const receipt = readJson<CurrentR4Receipt>(repoRoot, receiptPath);
    expect(receipt.graph_handle.handle_digest).toBe(result.graph_handle_digest);
    expect(receipt.acceptance_vector).toMatchObject({
      p4_prerequisite_replayed: 1, eligible_execution_cases: 5, mutants_killed: 15,
      targets: 19, target_denominator_scope: "selected-nonrecursive-inputs",
      tests_passed: 6, writes_observed: 0, events_observed: 0,
    });
    expect(receipt.claim_ceiling).toContain("not-application-equivalence-or-side-effects");
  }, 120_000);

  it("replays the persisted six-file receipt", async () => {
    await replayStoredCurrentR4Receipt(repoRoot, exactRef(repoRoot, receiptPath));
  }, 120_000);

  it("rejects a tampered full receipt even when fields retain the right shape", async () => {
    const receipt = readJson<CurrentR4Receipt>(repoRoot, receiptPath);
    const tampered = { ...receipt, acceptance_vector: { ...receipt.acceptance_vector,
      eligible_execution_cases: 4 as 5 } };
    await expect(verifyCurrentR4Receipt(repoRoot, tampered)).rejects.toMatchObject({
      name: "L1Error", code: "RECEIPT_TAMPERED",
    });
  });

  it("rejects a recomputed-digest evidence-role swap", async () => {
    const receipt = readJson<CurrentR4Receipt>(repoRoot, receiptPath);
    const swapped = resign({ ...receipt, evidence: { ...receipt.evidence,
      derivation_ref: receipt.evidence.execution_ref,
      execution_ref: receipt.evidence.derivation_ref } });
    await expect(verifyCurrentR4Receipt(repoRoot, swapped)).rejects.toMatchObject({
      name: "L1Error", code: "RECEIPT_TAMPERED",
    });
  });

  it("rejects a recomputed-digest P4 prerequisite substitution", async () => {
    const receipt = readJson<CurrentR4Receipt>(repoRoot, receiptPath);
    const substituted = resign({ ...receipt,
      p4_terminal_receipt_ref: receipt.evidence.derivation_ref });
    await expect(verifyCurrentR4Receipt(repoRoot, substituted)).rejects.toMatchObject({
      name: "L1Error", code: "RECEIPT_TAMPERED",
    });
  });

  it("rejects a recomputed-digest graph-handle mismatch after P4 replay", async () => {
    const receipt = readJson<CurrentR4Receipt>(repoRoot, receiptPath);
    const changed = resign({ ...receipt, graph_handle: { ...receipt.graph_handle,
      relationships_digest: "0".repeat(64) } });
    await expect(verifyCurrentR4Receipt(repoRoot, changed)).rejects.toMatchObject({
      name: "L1Error", code: "SOURCE_GRAPH_DIGEST_STALE",
    });
  }, 120_000);

  it("rejects a stale or redirected selected binding", () => {
    for (const bad of [
      { ...exactRef(repoRoot, R4_CURRENT_BINDING), sha256: "0".repeat(64) },
      { ...exactRef(repoRoot, R4_CURRENT_BINDING), path: receiptPath },
    ]) {
      try { loadCurrentR4Binding(repoRoot, bad); }
      catch (error) {
        expect(error).toBeInstanceOf(L1Error);
        expect((error as L1Error).code).toBe("BINDING_DIGEST_STALE");
        continue;
      }
      throw new Error("expected stale or redirected binding rejection");
    }
  });
});
