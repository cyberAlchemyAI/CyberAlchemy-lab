import {
  proveEntityRelations,
  ENTITY_RELATION_RAW_PATHS,
} from "../../../acceptance/entity/evaluate-entity-joins.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const entityRelationsV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "entity-relations-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(ENTITY_RELATION_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/entity-relations-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/entity/evaluate-entity-joins.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/entity/evaluate-entity-joins.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({raw_inputs: rawInputs, upstream}) => {
    const proof = proveEntityRelations(upstream, rawInputs);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "entity-relations-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.obligations.length,
        positives_passed: proof.obligations.length,
        mutants_declared: proof.hostile_mutations.length,
        mutants_killed: proof.hostile_mutations.length,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
