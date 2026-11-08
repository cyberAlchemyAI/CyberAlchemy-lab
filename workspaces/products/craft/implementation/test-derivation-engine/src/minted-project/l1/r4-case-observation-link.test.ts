import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { exactRef, readJson, digestValue } from "./exact-ref.js";
import { compareR4CaseObservations, deriveR4CaseObservationLink,
  replayR4CaseObservationLink } from "./r4-case-observation-link.js";
import { deriveR4CaseProjection } from "./r4-case-projection.js";
import { L1Error } from "./types.js";
import { R4_CURRENT_ATTEMPT } from "./verify-r4-current.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));
const receiptPath = `${R4_CURRENT_ATTEMPT}/terminal-receipt.json`;
const executionPath = `${R4_CURRENT_ATTEMPT}/observed-decision.json`;

function expectObservationTamper(projection: ReturnType<typeof deriveR4CaseProjection>,
  observation: Parameters<typeof compareR4CaseObservations>[1]): void {
  try {
    compareR4CaseObservations(projection, observation);
  } catch (error) {
    expect(error).toBeInstanceOf(L1Error);
    expect((error as L1Error).code).toBe("OBSERVATION_TAMPERED");
    return;
  }
  throw new Error("expected R4 case-observation mismatch");
}

describe("R4 authored case to current standalone observation link", () => {
  it("matches exact projected cases to the replayed current R4 receipt without widening the claim", async () => {
    const receiptRef = exactRef(repoRoot, receiptPath);
    const result = await deriveR4CaseObservationLink(repoRoot, receiptRef);
    expect(result.cases).toHaveLength(5);
    expect(result.matched_cases).toBe(5);
    expect(result.cases.map(item => item.expected_boolean)).toEqual([true, false, false, true, true]);
    expect(result.cases.every(item => item.expected_boolean === item.observed_boolean)).toBe(true);
    expect(result.authority_effect).toBe("none");
    expect(result.claim_ceiling).toContain("standalone-pure-decision-only");
    expect(result.link_digest).toMatch(/^[a-f0-9]{64}$/);
    expect("formal_claim_ref" in result).toBe(false);
    expect("can_satisfy_obligation" in result).toBe(false);
    expect(await replayR4CaseObservationLink(repoRoot, result, receiptRef)).toEqual(result);
    await expect(replayR4CaseObservationLink(repoRoot,
      { ...result, link_digest: "0".repeat(64) }, receiptRef)).rejects.toMatchObject({ code: "RECEIPT_TAMPERED" });
    await expect(deriveR4CaseObservationLink(repoRoot,
      { ...receiptRef, sha256: "0".repeat(64) })).rejects.toMatchObject({ code: "RECEIPT_TAMPERED" });
  }, 180_000);

  it("rejects missing, extra, reordered, changed-input, changed-oracle and changed-actual cases", () => {
    const projection = deriveR4CaseProjection(repoRoot);
    const execution = readJson<Parameters<typeof compareR4CaseObservations>[1]>(repoRoot, executionPath);
    expect(compareR4CaseObservations(projection, execution)).toHaveLength(5);
    const changes: ((item: any) => void)[] = [
      item => { item.observations.pop(); },
      item => { item.observations.push(item.observations[0]); },
      item => { [item.observations[0], item.observations[1]] = [item.observations[1], item.observations[0]]; },
      item => { item.observations[0].case_id = "another-case"; },
      item => { item.observations[0].control_class = "other-date"; },
      item => { item.observations[0].input_digest = "0".repeat(64); },
      item => { item.observations[0].expected = !item.observations[0].expected; },
      item => { item.observations[0].actual = !item.observations[0].actual; },
      item => { item.fixture_ref.sha256 = "0".repeat(64); },
    ];
    for (const change of changes) {
      const mutated = structuredClone(execution) as any;
      change(mutated);
      mutated.observations_digest = digestValue(mutated.observations);
      expectObservationTamper(projection, mutated);
    }
  });
});
