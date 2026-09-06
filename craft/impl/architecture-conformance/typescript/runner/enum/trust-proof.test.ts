import { describe, expect, it } from "vitest";

import { buildTrustArtifacts, renderTrustArtifact, verifyTrustArtifacts } from "./index.js";

const repositoryRoot = process.cwd();

describe("TypeScript Enum trust proof", () => {
  it("executes, kills the exact mutant denominator, replays, and freezes deterministically", async () => {
    const first = await buildTrustArtifacts(repositoryRoot);
    const second = await buildTrustArtifacts(repositoryRoot);
    expect(verifyTrustArtifacts(first)).toEqual([]);
    expect(first.execution).toEqual(expect.objectContaining({ declared_case_count: 13, accounted_case_count: 13, result: "pass" }));
    expect(first.mutation).toEqual(expect.objectContaining({ declared_mutant_count: 12, killed_mutant_count: 12, survived_mutant_count: 0, result: "pass" }));
    expect(first.replay).toEqual(expect.objectContaining({ byte_identical: true, independent_recomposition: true, result: "pass" }));
    expect(first.freeze).toEqual(expect.objectContaining({ frozen: true, authority_effect: "none" }));
    expect(renderTrustArtifact(first.execution)).toBe(renderTrustArtifact(second.execution));
    expect(renderTrustArtifact(first.freeze)).toBe(renderTrustArtifact(second.freeze));
  });

  it("rejects proof bytes that no longer match the frozen digest", async () => {
    const artifacts = await buildTrustArtifacts(repositoryRoot);
    const tampered = structuredClone(artifacts);
    (tampered.execution as { result: string }).result = "block";
    expect(verifyTrustArtifacts(tampered)).toEqual([
      "APE_TS_FREEZE_EXECUTION_DRIFT",
      "APE_TS_PROOF_EXECUTION_BLOCKED",
    ]);
  });
});
