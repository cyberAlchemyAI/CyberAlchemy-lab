import { describe, expect, it } from "vitest";

import type { TlaCaseV1 } from "../tla/contracts/tla-case-manifest-v1.js";
import type { TlcProcessObservationV1 } from "../tla/contracts/tlc-outcome-classification-v1.js";
import { classifyTlcOutcomeV1 } from "../tla/classify-tlc-outcome-v1.js";

const boundedCase: TlaCaseV1 = Object.freeze({
  case_id: "example.corpus.base",
  accounting_id: "example.corpus.base",
  proof_role: "obligation",
  module_paths: Object.freeze(["models/Example.tla"]),
  config_path: "models/Example.cfg",
  spec_name: "Spec",
  expected_class: "BOUNDED_NO_COUNTEREXAMPLE",
  expected_exit_status: 0,
  expected_property: null,
  required_trace_markers: Object.freeze([]),
  finding_code: null,
  timeout_ms: 120_000,
  output_limit_bytes: 1_048_576,
  state_limit: 100_000,
});

const counterexampleCase: TlaCaseV1 = Object.freeze({
  ...boundedCase,
  case_id: "example.corpus.mutant",
  accounting_id: "example.corpus.mutant",
  proof_role: "mutant",
  expected_class: "EXPECTED_NAMED_COUNTEREXAMPLE",
  expected_exit_status: 12,
  expected_property: "ExpectedInvariant",
  required_trace_markers: Object.freeze(["RequiredAction"]),
  finding_code: "FINDING_EXAMPLE",
});

const observation = (
  stdout: string,
  overrides: Partial<TlcProcessObservationV1> = {},
): TlcProcessObservationV1 => Object.freeze({
  exit_status: 0,
  signal: null,
  timed_out: false,
  output_limited: false,
  spawn_error: null,
  stdout,
  stderr: "",
  ...overrides,
});

const completed = [
  "123 states generated, 45 distinct states found, 0 states left on queue.",
  "End of statistics.",
  "Finished in 01s at (2026-08-24 12:00:00)",
].join("\n");

const clean = [
  "Model checking completed. No error has been found.",
  completed,
].join("\n");

const counterexample = (property = "ExpectedInvariant", marker = "RequiredAction") => [
  `Error: Invariant ${property} is violated.`,
  "Behavior up to this point:",
  "State 1: <Initial predicate>",
  `/\\ action = "${marker}"`,
  completed,
].join("\n");

describe("TLC total outcome classification", () => {
  it("accepts only exact bounded no-counterexample completion", () => {
    const result = classifyTlcOutcomeV1(boundedCase, observation(clean));
    expect(result).toMatchObject({
      observed_class: "BOUNDED_NO_COUNTEREXAMPLE",
      diagnostic_code: null,
      matches_expectation: true,
      exit_class: "zero",
      state_statistics: { generated: 123, distinct: 45 },
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.completion)).toBe(true);
    expect(Object.isFrozen(result.observed_properties)).toBe(true);
  });

  it("accepts only the exact declared named counterexample", () => {
    const result = classifyTlcOutcomeV1(
      counterexampleCase,
      observation(counterexample(), { exit_status: 12 }),
    );
    expect(result).toMatchObject({
      observed_class: "EXPECTED_NAMED_COUNTEREXAMPLE",
      diagnostic_code: null,
      matches_expectation: true,
      observed_properties: ["ExpectedInvariant"],
      violation_count: 1,
      behavior_trace_present: true,
      required_trace_markers_present: true,
      exit_class: "nonzero",
    });
  });

  it("rejects truncated apparent success before lower-precedence checks", () => {
    const result = classifyTlcOutcomeV1(
      boundedCase,
      observation("Model checking completed. No error has been found."),
    );
    expect(result).toMatchObject({
      observed_class: "INCOMPLETE_OUTPUT",
      diagnostic_code: "FACTORY_TLC_INCOMPLETE_OUTPUT",
      matches_expectation: false,
    });
  });

  it("rejects missing behavior traces and required markers", () => {
    const missingTrace = counterexample("ExpectedInvariant", "RequiredAction")
      .replace("Behavior up to this point:\n", "");
    const missingMarker = counterexample("ExpectedInvariant", "OtherAction");
    for (const output of [missingTrace, missingMarker]) {
      expect(classifyTlcOutcomeV1(
        counterexampleCase,
        observation(output, { exit_status: 12 }),
      )).toMatchObject({
        observed_class: "MISSING_TRACE_MARKER",
        diagnostic_code: "FACTORY_TLC_TRACE_MARKER_MISSING",
        matches_expectation: false,
      });
    }
  });

  it("rejects wrong and multiple violated properties", () => {
    const wrong = counterexample("OtherInvariant");
    const multiple = [
      counterexample(),
      "Error: Invariant OtherInvariant is violated.",
    ].join("\n");
    for (const output of [wrong, multiple]) {
      expect(classifyTlcOutcomeV1(
        counterexampleCase,
        observation(output, { exit_status: 12 }),
      )).toMatchObject({
        observed_class: "WRONG_PROPERTY",
        diagnostic_code: "FACTORY_TLC_WRONG_PROPERTY",
        matches_expectation: false,
      });
    }
  });

  it("lets SANY and fatal text outrank apparent terminal success", () => {
    const sany = `${clean}\nSANY Error: semantic analysis failed`;
    expect(classifyTlcOutcomeV1(boundedCase, observation(sany))).toMatchObject({
      observed_class: "SANY_OR_PARSE_ERROR",
      diagnostic_code: "FACTORY_TLC_TOOL_ERROR",
      matches_expectation: false,
    });

    const fatal = `${counterexample()}\nFatal: TLC threw an unexpected exception`;
    expect(classifyTlcOutcomeV1(
      counterexampleCase,
      observation(fatal, { exit_status: 12 }),
    )).toMatchObject({
      observed_class: "TOOL_ERROR",
      diagnostic_code: "FACTORY_TLC_TOOL_ERROR",
      matches_expectation: false,
    });
  });

  it("gives timeout, output limit, signal, and spawn failure highest precedence", () => {
    const vectors: readonly [Partial<TlcProcessObservationV1>, string][] = [
      [{ timed_out: true }, "TIMEOUT"],
      [{ output_limited: true }, "OUTPUT_LIMIT"],
      [{ exit_status: null, signal: "SIGKILL" }, "TOOL_ERROR"],
      [{ exit_status: null, spawn_error: "ENOENT" }, "TOOL_ERROR"],
    ];
    for (const [override, observedClass] of vectors) {
      expect(classifyTlcOutcomeV1(boundedCase, observation(clean, override))).toMatchObject({
        observed_class: observedClass,
        diagnostic_code: "FACTORY_TLC_TIMEOUT_OR_LIMIT",
        matches_expectation: false,
      });
    }
  });

  it("never converts an unexpected counterexample or wrong exit into passing evidence", () => {
    expect(classifyTlcOutcomeV1(
      boundedCase,
      observation(counterexample(), { exit_status: 12 }),
    )).toMatchObject({
      observed_class: "UNEXPECTED_COUNTEREXAMPLE",
      diagnostic_code: "FACTORY_TLC_UNEXPECTED_COUNTEREXAMPLE",
      matches_expectation: false,
    });

    expect(classifyTlcOutcomeV1(
      counterexampleCase,
      observation(counterexample(), { exit_status: 1 }),
    )).toMatchObject({
      observed_class: "TOOL_ERROR",
      diagnostic_code: "FACTORY_TLC_TOOL_ERROR",
      matches_expectation: false,
    });
  });
});
