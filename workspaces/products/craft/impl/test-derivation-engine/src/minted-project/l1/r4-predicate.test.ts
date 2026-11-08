import { describe, expect, it } from "vitest";

import { deriveUnit, L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import { runR4, type R4FixtureDocument } from "./r4.js";
import { L1Error } from "./types.js";

const repoRoot = repositoryRoot();
const derivation = deriveUnit(repoRoot, "R4");
const fixture = readJson<R4FixtureDocument>(repoRoot, L1_PATHS.r4Fixture);

function code(mutant: string): string {
  try {
    runR4(fixture, derivation.O_spec, mutant);
    return "NO_FAILURE";
  } catch (error) {
    if (error instanceof L1Error) return error.code;
    throw error;
  }
}

describe("EVF L1 R4 predicate mutations", () => {
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
