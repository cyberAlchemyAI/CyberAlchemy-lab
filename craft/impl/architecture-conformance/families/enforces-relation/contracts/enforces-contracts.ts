export type EnforcesRelationDefinitionV1 = Readonly<{
  schema_version: "EnforcesRelationDefinition/v1";
  relation_id: string;
  semantic_edge: Readonly<{
    definition_id: "DS-D2";
    source_meta_type: "Rule";
    source_id: string;
    predicate: "enforces";
    target_meta_type: "Operation";
    target_id: string;
  }>;
  definition_sha256: string;
  authority_ref: string;
  authority_status: "candidate-fixture";
  authority_effect: "none";
}>;

export type EnforcesObservationV1 = Readonly<{
  schema_version: "EnforcesObservation/v1";
  semantic_edge: EnforcesRelationDefinitionV1["semantic_edge"];
  architecture_facts: Readonly<{
    rule_call_count: number;
    operation_call_count: number;
    trace: readonly ("rule-call" | "operation-call" | "payout-write" | "payout-created-event")[];
  }>;
  mutation_id: string | null;
  authority_effect: "none";
}>;

export type EnforcesFindingCode =
  | "REL_SEMANTIC_EDGE_STALE"
  | "REL_RULE_BYPASSED"
  | "REL_OPERATION_MISSING"
  | "REL_ORDER_INVALID";

export type EnforcesEvaluationV1 = Readonly<{
  schema_version: "EnforcesEvaluation/v1";
  verdict: "pass" | "fail";
  findings: readonly Readonly<{
    code: EnforcesFindingCode;
    expected: unknown;
    observed: unknown;
  }>[];
  authority_effect: "none";
}>;
