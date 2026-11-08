import { evaluateBooleanEquality } from "./typed-predicate.js";
import {
  fail,
  type BooleanEqualityNode,
  type KeyDoorCase,
  type KeyDoorInput,
  type KeyDoorOutput,
  type RuntimeObservation,
} from "./types.js";
import { attemptUnlock } from "./fixtures/key-door-runtime.js";

export type UnlockRuntime = (input: KeyDoorInput) => unknown;

function isExactOutput(value: unknown): value is KeyDoorOutput {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const output = value as Record<string, unknown>;
  const keys = Object.keys(output).sort();
  return (
    keys.length === 2 &&
    keys[0] === "door_locked" &&
    keys[1] === "status" &&
    (output.status === "unlocked" || output.status === "denied") &&
    typeof output.door_locked === "boolean"
  );
}

export function validateRuntimeObservation(
  value: unknown,
  input: KeyDoorInput,
): { output: KeyDoorOutput; observed: boolean } {
  if (!isExactOutput(value)) {
    fail("RUNTIME_OUTPUT_INVALID", "runtime output does not have the exact admitted shape");
  }
  if (input.door_locked !== true) {
    fail("FIXTURE_INPUT_INVALID", "EVF S1 runtime is admitted only for locked-door inputs");
  }
  const isAllowedTransition =
    (value.status === "unlocked" && value.door_locked === false) ||
    (value.status === "denied" && value.door_locked === true);
  if (!isAllowedTransition) {
    fail("RUNTIME_OUTPUT_INVALID", "runtime output is not one of the two exact admitted transitions");
  }
  return {
    output: value,
    observed: value.status === "unlocked" && value.door_locked === false,
  };
}

function validateCases(cases: readonly KeyDoorCase[]): asserts cases is readonly [KeyDoorCase, KeyDoorCase] {
  if (
    cases.length !== 2 ||
    cases[0]?.case_id !== "has-key-locked" ||
    cases[1]?.case_id !== "no-key-locked-control"
  ) {
    fail("FIXTURE_INPUT_INVALID", "fixture cases must be the exact ordered true/false pair");
  }
  for (const item of cases) {
    if (
      item.call_arg.door_locked !== true ||
      item.call_arg.has_key !== item.vars.has_key ||
      Object.keys(item.vars).length !== 1 ||
      Object.keys(item.call_arg).sort().join(",") !== "door_locked,has_key"
    ) {
      fail("FIXTURE_INPUT_INVALID", `invalid expected-free fixture case ${item.case_id}`);
    }
  }
}

export function executeEnforcesCases(
  ast: BooleanEqualityNode,
  cases: readonly KeyDoorCase[],
  runtime: UnlockRuntime = attemptUnlock,
): readonly [RuntimeObservation, RuntimeObservation] {
  validateCases(cases);
  const observations = cases.map((item): RuntimeObservation => {
    const expected = evaluateBooleanEquality(ast, item.vars);
    let raw: unknown;
    try {
      raw = runtime(item.call_arg);
    } catch (error) {
      fail(
        "RUNTIME_EXECUTION_FAILED",
        `runtime threw for ${item.case_id}: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
    const { output, observed } = validateRuntimeObservation(raw, item.call_arg);
    if (expected !== observed) {
      fail("RUNTIME_RESULT_MISMATCH", `expected/observed mismatch for ${item.case_id}`);
    }
    return {
      case_id: item.case_id,
      expected_boolean: expected,
      observed_boolean: observed,
      output,
    };
  });
  return observations as unknown as readonly [RuntimeObservation, RuntimeObservation];
}
