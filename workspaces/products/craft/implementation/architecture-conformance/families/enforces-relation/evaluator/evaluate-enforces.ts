import type {
  EnforcesEvaluationV1,
  EnforcesObservationV1,
  EnforcesRelationDefinitionV1,
} from "../contracts/enforces-contracts.js";

export const evaluateEnforces = (input: Readonly<{
  definition: EnforcesRelationDefinitionV1;
  observation: EnforcesObservationV1;
}>): EnforcesEvaluationV1 => {
  const findings: EnforcesEvaluationV1["findings"][number][] = [];
  if (JSON.stringify(input.observation.semantic_edge) !==
      JSON.stringify(input.definition.semantic_edge)) {
    findings.push({
      code: "REL_SEMANTIC_EDGE_STALE",
      expected: input.definition.semantic_edge,
      observed: input.observation.semantic_edge,
    });
  }
  const facts = input.observation.architecture_facts;
  if (facts.rule_call_count !== 1) {
    findings.push({ code: "REL_RULE_BYPASSED", expected: 1, observed: facts.rule_call_count });
  }
  if (facts.operation_call_count !== 1) {
    findings.push({ code: "REL_OPERATION_MISSING", expected: 1, observed: facts.operation_call_count });
  }
  const ruleIndex = facts.trace.indexOf("rule-call");
  const operationIndex = facts.trace.indexOf("operation-call");
  const writeIndex = facts.trace.indexOf("payout-write");
  if (ruleIndex < 0 || operationIndex < 0 || writeIndex < 0 ||
      !(ruleIndex < operationIndex && operationIndex < writeIndex)) {
    findings.push({
      code: "REL_ORDER_INVALID",
      expected: ["rule-call", "operation-call", "payout-write"],
      observed: facts.trace,
    });
  }
  return Object.freeze({
    schema_version: "EnforcesEvaluation/v1" as const,
    verdict: findings.length === 0 ? "pass" as const : "fail" as const,
    findings: Object.freeze(findings.map((item) => Object.freeze({ ...item }))),
    authority_effect: "none" as const,
  });
};
