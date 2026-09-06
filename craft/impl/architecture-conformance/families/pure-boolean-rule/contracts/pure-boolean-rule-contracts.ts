export type RuleEndpointType =
  | "architecture.RuleImplementation"
  | "architecture.OperationImplementation"
  | "architecture.StateMachineImplementation"
  | "architecture.ValueObjectFactoryProvider"
  | "architecture.EntityFactoryProvider";

export type PureBooleanRuleProfileV1 = Readonly<{
  schema_version: "PureBooleanRuleProfile/v1";
  output_type: "boolean" | "string";
  state_mutation_count: number;
  external_effects: readonly string[];
  enforces_edges: readonly Readonly<{
    source_type: RuleEndpointType;
    target_type: RuleEndpointType;
  }>[];
  declared_dependencies: readonly string[];
  observed_dependencies: readonly string[];
  operation_invocation_count: number;
  evaluation_order: "bind-then-evaluate" | "evaluate-before-bind";
  stable_input_binding: boolean;
  exception_policy: "propagate" | "coerce-false";
  relation_evidence: Readonly<{
    owner_status: "current" | "stale";
    declared_source_type: RuleEndpointType;
    observed_source_type: RuleEndpointType;
    declared_target_type: RuleEndpointType;
    observed_target_type: RuleEndpointType;
    assertion_present: boolean;
  }>;
  authority_effect: "none";
}>;
export type RuleHostileCode =
  | "RMT_RULE_NON_BOOLEAN_RETURN"
  | "RMT_RULE_HIDDEN_MUTATION"
  | "RMT_RULE_EXTERNAL_EFFECT"
  | "RMT_RULE_MISSING_ENFORCES_EDGE"
  | "RMT_RULE_INVERSE_ENFORCES_EDGE"
  | "RMT_RULE_UNDECLARED_DEPENDENCY"
  | "RMT_RULE_RULE_CALLS_OPERATION"
  | "RMT_RULE_EVALUATION_ORDER_DEPENDENCE"
  | "RMT_RULE_UNSTABLE_INPUT_BINDING"
  | "RMT_RULE_EXCEPTION_AS_FALSE"
  | "RMT_RELATION_OWNER_EVIDENCE_STALE"
  | "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"
  | "RMT_RELATION_TARGET_ENDPOINT_MISMATCH"
  | "RMT_RELATION_ASSERTION_REQUIRED";

export type RuleHostileMutationPath =
  | "output_type"
  | "state_mutation_count"
  | "external_effects"
  | "enforces_edges"
  | "inverse_enforces_edge"
  | "observed_dependencies"
  | "operation_invocation_count"
  | "evaluation_order"
  | "stable_input_binding"
  | "exception_policy"
  | "relation_evidence.owner_status"
  | "relation_evidence.observed_source_type"
  | "relation_evidence.observed_target_type"
  | "relation_evidence.assertion_present";

export type RuleHostileFixtureV1 = Readonly<{
  schema_version: "RmtRuleHostile/v1";
  hostile_id: string;
  hostile_class: "type-semantic" | "rel-a-evidence";
  mutation: Readonly<{
    path: RuleHostileMutationPath;
    value: unknown;
  }>;
  expected_code: RuleHostileCode;
  authority_effect: "none";
}>;

export type PureBooleanRuleEvaluationV1 = Readonly<{
  schema_version: "PureBooleanRuleEvaluation/v1";
  verdict: "pass" | "fail";
  findings: readonly Readonly<{code: RuleHostileCode}>[];
  authority_effect: "none";
}>;
