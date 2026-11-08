import {proveCalculationParity} from
  "../../../acceptance/calculation/evaluate-calculation-parity.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const calculationParityV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "calculation-parity-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze([
    "definition",
    "denominator",
    "mutations",
    "descriptor",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/calculation-parity-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/calculation/evaluate-calculation-parity.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/calculation/evaluate-calculation-parity.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({raw_inputs: rawInputs, upstream}) => {
    const proof = proveCalculationParity(upstream, rawInputs);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "calculation-parity-v1",
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
