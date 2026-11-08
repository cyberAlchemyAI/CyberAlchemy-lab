import { createHash } from "node:crypto";

import {
  readValidatedHandle,
  type ValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import type {
  RuleEvaluationV1,
  RuleObservationV1,
  RuleObligationCatalogueV1,
  RuleObligationCode,
} from "../contracts/rule-contracts.js";
import type { NormalizedRulePackageV1 } from "../providers/decode-rule-contracts.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

type Finding = RuleEvaluationV1["findings"][number];
const finding = (
  code: RuleObligationCode,
  caseId: string | null = null,
  expected: boolean | null = null,
  observed: Finding["observed"] = null,
): Finding => Object.freeze({ code, case_id: caseId, expected, observed });

export const evaluateRule = (input: Readonly<{
  rule: ValidatedHandle<NormalizedRulePackageV1>;
  obligations: ValidatedHandle<RuleObligationCatalogueV1>;
  observation: ValidatedHandle<RuleObservationV1>;
}>): RuleEvaluationV1 => {
  const rule = readValidatedHandle(input.rule);
  const obligations = readValidatedHandle(input.obligations);
  const observation = readValidatedHandle(input.observation);
  const findings: Finding[] = [];
  if (observation.binding_id === null || observation.source_sha256 === null ||
      observation.symbol_name === null) {
    findings.push(finding("RULE_BINDING_MISSING"));
  } else if (observation.binding_id !== rule.binding.binding_id ||
      observation.source_sha256 !== rule.binding.source_ref.sha256 ||
      observation.symbol_name !== rule.binding.symbol_name) {
    findings.push(finding("RULE_BINDING_STALE"));
  }
  if (observation.unsupported.length > 0) {
    findings.push(finding("RULE_OBSERVATION_UNSUPPORTED"));
  }
  const counts = new Map<string, number>();
  for (const item of observation.case_observations) {
    counts.set(item.case_id, (counts.get(item.case_id) ?? 0) + 1);
  }
  for (const [caseId, count] of counts) {
    if (count > 1) findings.push(finding("RULE_OUTCOME_DUPLICATE", caseId));
  }
  const expectedCaseIds = new Set(rule.cases.cases.map(({ case_id: id }) => id));
  for (const item of observation.case_observations) {
    if (!expectedCaseIds.has(item.case_id)) {
      findings.push(finding("RULE_OUTCOME_UNEXPECTED", item.case_id, null, item.outcome));
    }
  }
  const outcomeObligations = obligations.obligations.filter(
    (obligation) => obligation.kind === "case-outcome-exact",
  );
  const effectCases = new Set(obligations.obligations
    .filter((obligation) => obligation.kind === "effect-free")
    .map(({ case_id: caseId }) => caseId));
  for (const obligation of outcomeObligations) {
    const observed = observation.case_observations.filter(
      ({ case_id: id }) => id === obligation.case_id,
    );
    if (observed.length === 0) {
      findings.push(finding("RULE_OUTCOME_MISSING", obligation.case_id));
      continue;
    }
    if (observed.length > 1) continue;
    const result = observed[0]!;
    if (typeof result.outcome !== "boolean") {
      findings.push(finding(
        "RULE_OUTCOME_NON_BOOLEAN",
        obligation.case_id,
        obligation.expected_outcome,
        result.outcome,
      ));
    } else if (result.outcome !== obligation.expected_outcome) {
      findings.push(finding(
        "RULE_OUTCOME_MISMATCH",
        obligation.case_id,
        obligation.expected_outcome,
        result.outcome,
      ));
    }
    if (effectCases.has(obligation.case_id) && result.observed_effect_count !== 0) {
      findings.push(finding(
        "RULE_EFFECT_OBSERVED", obligation.case_id, null,
        result.observed_effect_count,
      ));
    }
  }
  const normalized = [...findings].sort((left, right) => compareUtf8(
    `${left.code}\u0000${left.case_id ?? ""}`,
    `${right.code}\u0000${right.case_id ?? ""}`,
  ));
  return Object.freeze({
    schema_version: "RuleEvaluation/v1" as const,
    evaluation_id: `evaluation.rule.${sha256(JSON.stringify({
      rule: rule.definition.definition_sha256,
      obligations: obligations.catalogue_sha256,
      observation: observation.observation_sha256,
      findings: normalized,
    }))}`,
    verdict: normalized.length === 0 ? "pass" as const : "fail" as const,
    findings: Object.freeze(normalized),
    authority_effect: "none" as const,
  });
};
