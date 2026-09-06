import {proveQueryParity} from
  "../../../acceptance/query/evaluate-query-parity.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const queryParityV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "query-parity-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze([
    "definition",
    "denominator",
    "mutations",
    "descriptor",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/query-parity-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/query/evaluate-query-parity.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/query/evaluate-query-parity.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({raw_inputs: rawInputs, upstream}) => {
    const proof = proveQueryParity(upstream, rawInputs);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "query-parity-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.obligations.length,
        positives_passed: proof.obligations.filter(({status}) =>
          status === "passed").length,
        mutants_declared: proof.hostile_mutations.length,
        mutants_killed: proof.hostile_mutations.filter(({status}) =>
          status === "killed").length,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
