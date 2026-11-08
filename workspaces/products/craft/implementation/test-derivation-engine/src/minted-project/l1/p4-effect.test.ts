import { beforeAll, describe, expect, it } from "vitest";

import { L1_PATHS } from "./derive.js";
import { readJson, repositoryRoot } from "./exact-ref.js";
import {
  mutateP4Execution,
  runP4,
  validateP4Execution,
  type P4FixtureDocument,
} from "./p4.js";
import { L1Error, type P4Execution } from "./types.js";

const repoRoot = repositoryRoot();
let execution: P4Execution;

function code(action: () => unknown): string {
  try {
    action();
    return "NO_FAILURE";
  } catch (error) {
    if (error instanceof L1Error) return error.code;
    throw error;
  }
}

describe("EVF L1 P4 effect observation mutations", () => {
  beforeAll(async () => {
    execution = await runP4(readJson<P4FixtureDocument>(repoRoot, L1_PATHS.p4Fixture));
  });

  const cases = [
    ["P4-M01-missing-write", "P4_WRITE_MISSING"],
    ["P4-M02-missing-event", "P4_EVENT_MISSING"],
    ["P4-M03-wrong-write-amount", "P4_WRITE_AMOUNT_MISMATCH"],
    ["P4-M04-wrong-event-amount", "P4_EVENT_AMOUNT_MISMATCH"],
    ["P4-M05-wrong-write-date", "P4_WRITE_DATE_MISMATCH"],
    ["P4-M06-wrong-event-date", "P4_EVENT_DATE_MISMATCH"],
    ["P4-M07-event-before-write", "P4_EFFECT_ORDER_MISMATCH"],
    ["P4-M08-extra-effect", "P4_EFFECT_CARDINALITY_MISMATCH"],
  ] as const;

  for (const [mutant, stableCode] of cases) {
    it(`kills ${mutant} with ${stableCode}`, () => {
      expect(code(() => validateP4Execution(mutateP4Execution(execution, mutant)))).toBe(stableCode);
    });
  }
});
