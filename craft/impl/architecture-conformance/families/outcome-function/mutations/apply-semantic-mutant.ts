import { createHash } from "node:crypto";

import type {
  RuleObservationV1,
  RuleSemanticMutantV1,
} from "../contracts/rule-contracts.js";
import { canonicalRuleJson } from "../providers/decode-rule-contracts.js";

const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

const observationDigest = (
  value: Omit<RuleObservationV1, "observation_sha256">,
): string => createHash("sha256")
  .update(canonicalRuleJson(value), "utf8")
  .digest("hex");

export const applyRuleSemanticMutant = (
  observation: RuleObservationV1,
  mutant: RuleSemanticMutantV1,
): RuleObservationV1 => {
  let matched = 0;
  const cases = observation.case_observations.map((item) => {
    if (item.case_id !== mutant.case_id) return item;
    matched += 1;
    if (mutant.defect === "observable-effect") {
      return Object.freeze({ ...item, observed_effect_count: item.observed_effect_count + 1 });
    }
    if (typeof item.outcome !== "boolean") {
      return fail("RULE_MUTATION_OUTCOME_NOT_BOOLEAN");
    }
    return Object.freeze({
      ...item,
      outcome: mutant.defect === "bypass-check" ? true : !item.outcome,
    });
  });
  if (matched !== 1) return fail("RULE_MUTATION_CASE_CARDINALITY");
  const body = Object.freeze({
    ...observation,
    case_observations: Object.freeze(cases),
  });
  const { observation_sha256: _priorDigest, ...digestBody } = body;
  return Object.freeze({
    ...digestBody,
    observation_sha256: observationDigest(digestBody),
  });
};
