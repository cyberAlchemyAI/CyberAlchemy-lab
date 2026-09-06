import type {
  PureBooleanRuleEvaluationV1,
  PureBooleanRuleProfileV1,
  RuleHostileCode,
} from "../contracts/pure-boolean-rule-contracts.js";

const allowedGuardTarget = new Set([
  "architecture.OperationImplementation",
  "architecture.StateMachineImplementation",
]);

export const PURE_BOOLEAN_RULE_BASELINE: PureBooleanRuleProfileV1 =
  Object.freeze({
    schema_version: "PureBooleanRuleProfile/v1" as const,
    output_type: "boolean" as const,
    state_mutation_count: 0,
    external_effects: Object.freeze([]),
    enforces_edges: Object.freeze([
      Object.freeze({
        source_type: "architecture.RuleImplementation" as const,
        target_type: "architecture.OperationImplementation" as const,
      }),
    ]),
    declared_dependencies: Object.freeze(["settlement-input"]),
    observed_dependencies: Object.freeze(["settlement-input"]),
    operation_invocation_count: 0,
    evaluation_order: "bind-then-evaluate" as const,
    stable_input_binding: true,
    exception_policy: "propagate" as const,
    relation_evidence: Object.freeze({
      owner_status: "current" as const,
      declared_source_type: "architecture.RuleImplementation" as const,
      observed_source_type: "architecture.RuleImplementation" as const,
      declared_target_type: "architecture.OperationImplementation" as const,
      observed_target_type: "architecture.OperationImplementation" as const,
      assertion_present: true,
    }),
    authority_effect: "none" as const,
  });

export const evaluatePureBooleanRuleProfile = (
  profile: PureBooleanRuleProfileV1,
): PureBooleanRuleEvaluationV1 => {
  const codes: RuleHostileCode[] = [];
  if (profile.output_type !== "boolean") {
    codes.push("RMT_RULE_NON_BOOLEAN_RETURN");
  }
  if (profile.state_mutation_count !== 0) {
    codes.push("RMT_RULE_HIDDEN_MUTATION");
  }
  if (profile.external_effects.length !== 0) {
    codes.push("RMT_RULE_EXTERNAL_EFFECT");
  }
  const inverseEdge = profile.enforces_edges.some(({source_type, target_type}) =>
    allowedGuardTarget.has(source_type) &&
    target_type === "architecture.RuleImplementation");
  if (inverseEdge) {
    codes.push("RMT_RULE_INVERSE_ENFORCES_EDGE");
  } else if (!profile.enforces_edges.some(({source_type, target_type}) =>
    source_type === "architecture.RuleImplementation" &&
    allowedGuardTarget.has(target_type))) {
    codes.push("RMT_RULE_MISSING_ENFORCES_EDGE");
  }
  const declared = new Set(profile.declared_dependencies);
  if (profile.observed_dependencies.some((dependency) =>
    !declared.has(dependency))) {
    codes.push("RMT_RULE_UNDECLARED_DEPENDENCY");
  }
  if (profile.operation_invocation_count !== 0) {
    codes.push("RMT_RULE_RULE_CALLS_OPERATION");
  }
  if (profile.evaluation_order !== "bind-then-evaluate") {
    codes.push("RMT_RULE_EVALUATION_ORDER_DEPENDENCE");
  }
  if (!profile.stable_input_binding) {
    codes.push("RMT_RULE_UNSTABLE_INPUT_BINDING");
  }
  if (profile.exception_policy !== "propagate") {
    codes.push("RMT_RULE_EXCEPTION_AS_FALSE");
  }
  if (profile.relation_evidence.owner_status !== "current") {
    codes.push("RMT_RELATION_OWNER_EVIDENCE_STALE");
  }
  if (profile.relation_evidence.observed_source_type !==
      profile.relation_evidence.declared_source_type) {
    codes.push("RMT_RELATION_SOURCE_ENDPOINT_MISMATCH");
  }
  if (profile.relation_evidence.observed_target_type !==
      profile.relation_evidence.declared_target_type) {
    codes.push("RMT_RELATION_TARGET_ENDPOINT_MISMATCH");
  }
  if (!profile.relation_evidence.assertion_present) {
    codes.push("RMT_RELATION_ASSERTION_REQUIRED");
  }
  return Object.freeze({
    schema_version: "PureBooleanRuleEvaluation/v1" as const,
    verdict: codes.length === 0 ? "pass" as const : "fail" as const,
    findings: Object.freeze(codes.map((code) => Object.freeze({code}))),
    authority_effect: "none" as const,
  });
};
