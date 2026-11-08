import { describe, expect, it } from "vitest";

import { deriveUnit, L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { historicalR4Obligation } from "./historical-r4-obligation.js";
import { runR4, type R4FixtureDocument } from "./r4.js";
import { L1Error } from "./types.js";

const repoRoot = repositoryRoot();
const fixture = readJson<R4FixtureDocument>(repoRoot, L1_PATHS.r4Fixture);
const obligation = historicalR4Obligation();

function code(mutant: string): string {
  try {
    runR4(fixture, obligation, mutant);
    return "NO_FAILURE";
  } catch (error) {
    if (error instanceof L1Error) return error.code;
    throw error;
  }
}

describe("EVF L1 R4 predicate mutations", () => {
  it("does not treat the historical contract as a current graph derivation", () => {
    expect(() => deriveUnit(repoRoot, "R4"))
      .toThrowError(expect.objectContaining({ code: "SOURCE_MANIFEST_INCOMPLETE" }));
  });
  const cases = [
    ["R4-M01-always-false", "R4_RESULT_MISMATCH"],
    ["R4-M02-always-true", "R4_RESULT_MISMATCH"],
    ["R4-M03-wrong-date-filter", "R4_RESULT_MISMATCH"],
    ["R4-M04-wrong-type-filter", "R4_RESULT_MISMATCH"],
    ["R4-M05-wrong-count-threshold", "R4_RESULT_MISMATCH"],
    ["R4-M06-count-all-dates", "R4_CONTROL_MISMATCH"],
    ["R4-M07-count-all-types", "R4_CONTROL_MISMATCH"],
  ] as const;

  for (const [mutant, stableCode] of cases) {
    it(`kills ${mutant} with ${stableCode}`, () => {
      expect(code(mutant)).toBe(stableCode);
    });
  }
});
