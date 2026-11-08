import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { deriveUnit, L1_CURRENT_PROJECTION, L1_PATHS } from "./derive.js";
import { readJson } from "./exact-ref.js";
import type { SettlementDecisionInput } from "./standalone-settlement-decision.js";
import {
  assertStandaloneR4Contract,
  loadStandaloneR4Decision,
  R4_STANDALONE_CONTRACT,
  type StandaloneR4Contract,
} from "./standalone-r4-runtime.js";
import { L1Error } from "./types.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));
type Fixture = {
  readonly expected_values_forbidden: true;
  readonly cases: readonly {
    readonly case_id: string;
    readonly input: SettlementDecisionInput;
  }[];
};

describe("candidate-local R4 pure decision", () => {
  it("matches the selected five-case obligation without fixture expected values", async () => {
    const decideStandaloneMakeupApplied = await loadStandaloneR4Decision(repoRoot);
    const fixture = readJson<Fixture>(repoRoot, L1_PATHS.r4Fixture);
    const obligation = deriveUnit(repoRoot, "R4", { projection: L1_CURRENT_PROJECTION }).O_spec;
    const rows = (obligation.semantic_contract as {
      truth_table: readonly { case_id: string; expected: boolean }[];
    }).truth_table;
    expect(fixture.expected_values_forbidden).toBe(true);
    expect(rows).toHaveLength(5);
    expect(fixture.cases.map((entry) => entry.case_id)).toEqual(rows.map((row) => row.case_id));
    for (const [index, entry] of fixture.cases.entries()) {
      expect(decideStandaloneMakeupApplied(entry.input))
        .toBe(rows[index]!.expected);
    }
  });

  it("rejects nonpositive makeup and ignores an unrelated payout record", async () => {
    const decideStandaloneMakeupApplied = await loadStandaloneR4Decision(repoRoot);
    const input: SettlementDecisionInput = {
      existingTransactions: [],
      periodEnd: "2024-01-31",
      totalAppliedMakeup: 0,
      totalPayout: 50,
    };
    expect(decideStandaloneMakeupApplied(input)).toBe(false);
    expect(decideStandaloneMakeupApplied({
      ...input,
      totalAppliedMakeup: -1,
      existingTransactions: [{ type: "PAYOUT", date: input.periodEnd }],
    })).toBe(false);
    expect(decideStandaloneMakeupApplied({
      ...input,
      totalAppliedMakeup: 1,
      existingTransactions: [{ type: "PAYOUT", date: input.periodEnd }],
    })).toBe(true);
  });

  it("rejects stale or redirected runtime bytes before import", () => {
    const contract = readJson<StandaloneR4Contract>(repoRoot, R4_STANDALONE_CONTRACT);
    for (const runtimeRef of [
      { ...contract.runtime_source_ref, sha256: "0".repeat(64) },
      { ...contract.runtime_source_ref, path: L1_PATHS.r4Semantic },
    ]) {
      try {
        assertStandaloneR4Contract(repoRoot, { ...contract, runtime_source_ref: runtimeRef });
      } catch (error) {
        expect(error).toBeInstanceOf(L1Error);
        expect((error as L1Error).code).toBe("BINDING_DIGEST_STALE");
        continue;
      }
      throw new Error("expected stale or redirected runtime rejection");
    }
  });
});
