import type { TlaCaseV1 } from "./contracts/tla-case-manifest-v1.js";
import type {
  TlcOutcomeClassificationV1,
  TlcOutcomeClassV1,
  TlcOutcomeDiagnosticV1,
  TlcProcessObservationV1,
} from "./contracts/tlc-outcome-classification-v1.js";

const noCounterexampleSentence = "Model checking completed. No error has been found.";
const endOfStatistics = "End of statistics.";
const finishedMarker = "Finished in";
const behaviorTraceMarker = "Behavior up to this point:";

const sanyOrParsePatterns = Object.freeze([
  /SANY Error/iu,
  /Parse Error/iu,
  /Parsing or semantic analysis failed/iu,
  /Semantic errors?/iu,
  /Lexical error/iu,
]);

const fatalPatterns = Object.freeze([
  /\bFatal:/iu,
  /\bException in thread\b/u,
  /\bjava\.[A-Za-z0-9_.]+(?:Error|Exception)\b/u,
  /\bTLC threw an unexpected exception\b/iu,
  /\bOutOfMemoryError\b/u,
]);

const violatedPropertyPattern = /\bInvariant\s+([A-Za-z][A-Za-z0-9_]*)\s+is violated\./gu;
const stateStatisticsPattern = /([0-9]+)\s+states generated,\s+([0-9]+)\s+distinct states found/iu;

const observedProperties = (output: string): readonly string[] => {
  const properties = [...output.matchAll(violatedPropertyPattern)].map((match) => match[1]!);
  return Object.freeze([...new Set(properties)].sort((left, right) =>
    Buffer.from(left).compare(Buffer.from(right))));
};

const violationCount = (output: string): number =>
  [...output.matchAll(violatedPropertyPattern)].length;

const exitClass = (
  observation: TlcProcessObservationV1,
): TlcOutcomeClassificationV1["exit_class"] => {
  if (observation.spawn_error !== null) return "spawn-error";
  if (observation.signal !== null) return "signal";
  if (observation.exit_status === null) return "missing";
  return observation.exit_status === 0 ? "zero" : "nonzero";
};

const classify = (
  caseContract: TlaCaseV1,
  observation: TlcProcessObservationV1,
  output: string,
  properties: readonly string[],
  count: number,
  completion: TlcOutcomeClassificationV1["completion"],
  behaviorTracePresent: boolean,
  requiredTraceMarkersPresent: boolean,
): readonly [TlcOutcomeClassV1, TlcOutcomeDiagnosticV1 | null] => {
  if (observation.timed_out) return ["TIMEOUT", "FACTORY_TLC_TIMEOUT_OR_LIMIT"];
  if (observation.output_limited) return ["OUTPUT_LIMIT", "FACTORY_TLC_TIMEOUT_OR_LIMIT"];
  if (observation.signal !== null || observation.spawn_error !== null) {
    return ["TOOL_ERROR", "FACTORY_TLC_TIMEOUT_OR_LIMIT"];
  }
  if (sanyOrParsePatterns.some((pattern) => pattern.test(output))) {
    return ["SANY_OR_PARSE_ERROR", "FACTORY_TLC_TOOL_ERROR"];
  }
  if (fatalPatterns.some((pattern) => pattern.test(output))) {
    return ["TOOL_ERROR", "FACTORY_TLC_TOOL_ERROR"];
  }
  if (!completion.end_of_statistics || !completion.finished) {
    return ["INCOMPLETE_OUTPUT", "FACTORY_TLC_INCOMPLETE_OUTPUT"];
  }

  if (caseContract.expected_class === "BOUNDED_NO_COUNTEREXAMPLE") {
    if (count > 0 || behaviorTracePresent) {
      return ["UNEXPECTED_COUNTEREXAMPLE", "FACTORY_TLC_UNEXPECTED_COUNTEREXAMPLE"];
    }
    if (observation.exit_status !== caseContract.expected_exit_status ||
        !completion.no_counterexample_sentence) {
      return ["TOOL_ERROR", "FACTORY_TLC_TOOL_ERROR"];
    }
    return ["BOUNDED_NO_COUNTEREXAMPLE", null];
  }

  if (count !== 1 || properties.length !== 1 || properties[0] !== caseContract.expected_property) {
    return count === 0
      ? ["UNEXPECTED_COUNTEREXAMPLE", "FACTORY_TLC_UNEXPECTED_COUNTEREXAMPLE"]
      : ["WRONG_PROPERTY", "FACTORY_TLC_WRONG_PROPERTY"];
  }
  if (!behaviorTracePresent || !requiredTraceMarkersPresent) {
    return ["MISSING_TRACE_MARKER", "FACTORY_TLC_TRACE_MARKER_MISSING"];
  }
  if (observation.exit_status !== caseContract.expected_exit_status) {
    return ["TOOL_ERROR", "FACTORY_TLC_TOOL_ERROR"];
  }
  return ["EXPECTED_NAMED_COUNTEREXAMPLE", null];
};

export const classifyTlcOutcomeV1 = (
  caseContract: TlaCaseV1,
  observation: TlcProcessObservationV1,
): TlcOutcomeClassificationV1 => {
  const output = `${observation.stdout}\n${observation.stderr}`;
  const properties = observedProperties(output);
  const count = violationCount(output);
  const behaviorTracePresent = output.includes(behaviorTraceMarker);
  const requiredTraceMarkersPresent = caseContract.required_trace_markers.every((marker) =>
    output.includes(marker));
  const completion = Object.freeze({
    no_counterexample_sentence: output.includes(noCounterexampleSentence),
    end_of_statistics: output.includes(endOfStatistics),
    finished: output.includes(finishedMarker),
  });
  const statisticsMatch = output.match(stateStatisticsPattern);
  const stateStatistics = Object.freeze({
    generated: statisticsMatch === null ? null : Number(statisticsMatch[1]),
    distinct: statisticsMatch === null ? null : Number(statisticsMatch[2]),
  });
  const [observedClass, diagnosticCode] = classify(
    caseContract,
    observation,
    output,
    properties,
    count,
    completion,
    behaviorTracePresent,
    requiredTraceMarkersPresent,
  );
  return Object.freeze({
    schema_version: "TlcOutcomeClassification/v1",
    case_id: caseContract.case_id,
    expected_class: caseContract.expected_class,
    observed_class: observedClass,
    diagnostic_code: diagnosticCode,
    matches_expectation: observedClass === caseContract.expected_class && diagnosticCode === null,
    observed_properties: properties,
    violation_count: count,
    behavior_trace_present: behaviorTracePresent,
    required_trace_markers_present: requiredTraceMarkersPresent,
    completion,
    exit_class: exitClass(observation),
    state_statistics: stateStatistics,
    authority_effect: "none",
  });
};
