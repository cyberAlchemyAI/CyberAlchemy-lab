import {
  POLICY_RELATION_RAW_PATHS,
  provePolicySelectsStrategyRelation,
} from "../../../acceptance/policy/evaluate-policy-joins.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const policySelectsStrategyV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "policy-selects-strategy-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(POLICY_RELATION_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/policy-selects-strategy-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/policy/evaluate-policy-joins.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/policy/evaluate-policy-joins.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({raw_inputs: rawInputs, upstream}) => {
    const proof = provePolicySelectsStrategyRelation(upstream, rawInputs);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "policy-selects-strategy-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.obligations.length +
          proof.membership_evaluations.length * 8,
        positives_passed: proof.obligations.length +
          proof.membership_evaluations.length * 8,
        mutants_declared: proof.hostile_mutations.length +
          proof.membership_mutations.length,
        mutants_killed: proof.hostile_mutations.length +
          proof.membership_mutations.length,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
