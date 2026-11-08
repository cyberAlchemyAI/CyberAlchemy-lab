import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { loadEvfS1Bundle } from "./derive.js";
import {
  executeEnforcesCases,
  validateRuntimeObservation,
} from "./enforces-execution.js";
import { EvfS1Error, type EvfFailureCode } from "./types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));

function expectEvfCode(action: () => unknown, code: EvfFailureCode): void {
  try {
    action();
  } catch (error) {
    expect(error).toBeInstanceOf(EvfS1Error);
    expect((error as EvfS1Error).code).toBe(code);
    return;
  }
  throw new Error(`expected EVF failure ${code}`);
}

describe("EVF S1 independent expected-observed execution", () => {
  it("observes the exact true and false runtime transitions", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const observations = executeEnforcesCases(
      bundle.predicate.predicate.ast,
      bundle.fixtures.cases,
    );

    expect(observations).toEqual([
      {
        case_id: "has-key-locked",
        expected_boolean: true,
        observed_boolean: true,
        output: { status: "unlocked", door_locked: false },
      },
      {
        case_id: "no-key-locked-control",
        expected_boolean: false,
        observed_boolean: false,
        output: { status: "denied", door_locked: true },
      },
    ]);
  });

  it("rejects malformed and impossible runtime outputs before projection", () => {
    const input = loadEvfS1Bundle(REPO_ROOT).fixtures.cases[0].call_arg;

    expectEvfCode(
      () => validateRuntimeObservation(
        { status: "unlocked", door_locked: false, expected: true },
        input,
      ),
      "RUNTIME_OUTPUT_INVALID",
    );
    expectEvfCode(
      () => validateRuntimeObservation({ status: "unlocked", door_locked: true }, input),
      "RUNTIME_OUTPUT_INVALID",
    );
    expectEvfCode(
      () => validateRuntimeObservation({ status: "denied", door_locked: false }, input),
      "RUNTIME_OUTPUT_INVALID",
    );
  });

  it("rejects valid-shaped outputs that disagree with the predicate", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);

    expectEvfCode(
      () => executeEnforcesCases(
        bundle.predicate.predicate.ast,
        bundle.fixtures.cases,
        () => ({ status: "unlocked", door_locked: false }),
      ),
      "RUNTIME_RESULT_MISMATCH",
    );
    expectEvfCode(
      () => executeEnforcesCases(
        bundle.predicate.predicate.ast,
        bundle.fixtures.cases,
        () => ({ status: "denied", door_locked: true }),
      ),
      "RUNTIME_RESULT_MISMATCH",
    );
  });

  it("normalizes a thrown adapter error to the stable execution code", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);

    expectEvfCode(
      () => executeEnforcesCases(
        bundle.predicate.predicate.ast,
        bundle.fixtures.cases,
        () => {
          throw new Error("synthetic adapter failure");
        },
      ),
      "RUNTIME_EXECUTION_FAILED",
    );
  });
});
