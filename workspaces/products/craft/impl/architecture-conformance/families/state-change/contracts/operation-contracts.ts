export type OperationObservationV1 = Readonly<{
  schema_version: "OperationObservation/v1";
  binding_id: string;
  binding_source_sha256: string;
  execution_source_sha256: string;
  mutation_id: string | null;
  payout_ids: readonly string[];
  events: readonly string[];
  trace: readonly string[];
  authority_effect: "none";
}>;

export type OperationEvaluationV1 = Readonly<{
  schema_version: "OperationEvaluation/v1";
  verdict: "pass" | "fail";
  findings: readonly Readonly<{
    code: "OP_BINDING_STALE" | "OP_STATE_CHANGE_MISSING" | "OP_POSTCONDITION_MISSING";
    expected: unknown;
    observed: unknown;
  }>[];
  authority_effect: "none";
}>;
