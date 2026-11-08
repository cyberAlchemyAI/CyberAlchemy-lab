import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { digestValue, readJson } from "./exact-ref.js";
import {
  loadCurrentP4Binding,
  P4_CURRENT_ATTEMPT,
  P4_CURRENT_BINDING,
  replayStoredCurrentP4Receipt,
  runCurrentP4Verification,
  verifyCurrentP4Receipt,
  type CurrentP4Receipt,
} from "./verify-p4-current.js";
import { L1Error } from "./types.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));

describe("candidate-local current P4 terminal successor", () => {
  it("runs selected current graph, observed ports and all sixteen negative controls reproducibly", async () => {
    const first = await runCurrentP4Verification(repoRoot);
    const second = await runCurrentP4Verification(repoRoot);
    expect(first).toEqual(second);
    expect(first.status).toBe("pass");
    expect(first.mutation_count).toBe(16);
    const receipt = readJson<CurrentP4Receipt>(repoRoot, first.receipt_ref.path);
    await replayStoredCurrentP4Receipt(repoRoot, first.receipt_ref);
    expect(receipt.graph_handle.handle_digest).toBe(first.graph_handle_digest);
    expect(receipt.evidence.binding_ref.path).toBe(P4_CURRENT_BINDING);
    expect(first.receipt_ref.path).toBe(`${P4_CURRENT_ATTEMPT}/terminal-receipt.json`);
  }, 120_000);

  it("rejects stale or redirected exact binding selection", () => {
    const binding = loadCurrentP4Binding(repoRoot);
    expect(binding.graph_ref.path).toContain("generated-current-20261002/graph.json");
    for (const ref of [
      { path: P4_CURRENT_BINDING, sha256: "0".repeat(64), size_bytes: 1 },
      { ...binding.graph_ref, path: binding.fixture_ref.path },
    ]) {
      try {
        loadCurrentP4Binding(repoRoot, ref);
      } catch (error) {
        expect(error).toBeInstanceOf(L1Error);
        expect((error as L1Error).code).toBe("BINDING_DIGEST_STALE");
        continue;
      }
      throw new Error("expected binding selection rejection");
    }
  });

  it("rejects receipt tamper and changed evidence role despite a recomputed digest", async () => {
    const result = await runCurrentP4Verification(repoRoot);
    const receipt = readJson<CurrentP4Receipt>(repoRoot, result.receipt_ref.path);
    const badDigest = { ...receipt, receipt_digest: "0".repeat(64) };
    await expect(verifyCurrentP4Receipt(repoRoot, badDigest)).rejects.toMatchObject({ code: "RECEIPT_TAMPERED" });
    const roleSwapped = { ...receipt, evidence: { ...receipt.evidence,
      execution_ref: receipt.evidence.derivation_ref } };
    // The public verifier must not accept a role swap even if an attacker recomputes the receipt digest.
    const { receipt_digest: _old, ...unsigned } = roleSwapped;
    const recomputed = { ...unsigned, receipt_digest: digestValue(unsigned) };
    await expect(verifyCurrentP4Receipt(repoRoot, recomputed)).rejects.toMatchObject({ code: "RECEIPT_TAMPERED" });
  }, 120_000);
});
