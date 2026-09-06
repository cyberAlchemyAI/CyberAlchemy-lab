import type { EnforcesObservationV1 } from "../contracts/enforces-contracts.js";

export type EnforcesMutantV1 = Readonly<{
  mutation_id: "bypass-rule/complete-settlement" | "mutation-before-rule/complete-settlement";
  defect: "bypass-rule" | "mutation-before-rule";
  expected_finding_code: "REL_RULE_BYPASSED" | "REL_ORDER_INVALID";
}>;

export const applyEnforcesMutant = (
  observation: EnforcesObservationV1,
  mutant: EnforcesMutantV1,
): EnforcesObservationV1 => mutant.defect === "bypass-rule"
  ? Object.freeze({
      ...observation,
      architecture_facts: Object.freeze({
        ...observation.architecture_facts,
        rule_call_count: 0,
        trace: Object.freeze(observation.architecture_facts.trace.filter(
          (item) => item !== "rule-call",
        )),
      }),
      mutation_id: mutant.mutation_id,
    })
  : Object.freeze({
      ...observation,
      architecture_facts: Object.freeze({
        ...observation.architecture_facts,
        trace: Object.freeze([
          "operation-call", "payout-write", "payout-created-event", "rule-call",
        ] as const),
      }),
      mutation_id: mutant.mutation_id,
    });
