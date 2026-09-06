export const TLC_OUTCOME_CLASSES_V1 = Object.freeze([
  "BOUNDED_NO_COUNTEREXAMPLE",
  "EXPECTED_NAMED_COUNTEREXAMPLE",
  "UNEXPECTED_COUNTEREXAMPLE",
  "WRONG_PROPERTY",
  "MISSING_TRACE_MARKER",
  "INCOMPLETE_OUTPUT",
  "SANY_OR_PARSE_ERROR",
  "TOOL_ERROR",
  "TIMEOUT",
  "OUTPUT_LIMIT",
] as const);

export type TlcOutcomeClassV1 = typeof TLC_OUTCOME_CLASSES_V1[number];

export type TlcSuccessfulOutcomeClassV1 = Extract<
  TlcOutcomeClassV1,
  "BOUNDED_NO_COUNTEREXAMPLE" | "EXPECTED_NAMED_COUNTEREXAMPLE"
>;

export type TlcOutcomeDiagnosticV1 =
  | "FACTORY_TLC_INCOMPLETE_OUTPUT"
  | "FACTORY_TLC_TRACE_MARKER_MISSING"
  | "FACTORY_TLC_WRONG_PROPERTY"
  | "FACTORY_TLC_TOOL_ERROR"
  | "FACTORY_TLC_TIMEOUT_OR_LIMIT"
  | "FACTORY_TLC_UNEXPECTED_COUNTEREXAMPLE";

export type TlcProcessObservationV1 = Readonly<{
  exit_status: number | null;
  signal: string | null;
  timed_out: boolean;
  output_limited: boolean;
  spawn_error: string | null;
  stdout: string;
  stderr: string;
}>;

export type TlcCompletionPredicatesV1 = Readonly<{
  no_counterexample_sentence: boolean;
  end_of_statistics: boolean;
  finished: boolean;
}>;

export type TlcStateStatisticsV1 = Readonly<{
  generated: number | null;
  distinct: number | null;
}>;

export type TlcOutcomeClassificationV1 = Readonly<{
  schema_version: "TlcOutcomeClassification/v1";
  case_id: string;
  expected_class: TlcSuccessfulOutcomeClassV1;
  observed_class: TlcOutcomeClassV1;
  diagnostic_code: TlcOutcomeDiagnosticV1 | null;
  matches_expectation: boolean;
  observed_properties: readonly string[];
  violation_count: number;
  behavior_trace_present: boolean;
  required_trace_markers_present: boolean;
  completion: TlcCompletionPredicatesV1;
  exit_class: "zero" | "nonzero" | "signal" | "spawn-error" | "missing";
  state_statistics: TlcStateStatisticsV1;
  authority_effect: "none";
}>;
