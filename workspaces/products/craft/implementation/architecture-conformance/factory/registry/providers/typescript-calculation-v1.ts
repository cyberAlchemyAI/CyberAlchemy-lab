import {
  buildTypeScriptCalculationProof,
  TYPESCRIPT_CALCULATION_RAW_PATHS,
  type TypeScriptCalculationRawInputs,
} from "../../../realizations/calculation/typescript/value-computation-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const typeScriptCalculationV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-calculation-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(TYPESCRIPT_CALCULATION_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-calculation-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/typescript/value-computation-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/typescript/value-computation-v1/closed-subset.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/calculation/typescript/value-computation-v1/typescript-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/calculation-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const proof = await buildTypeScriptCalculationProof(
      rawInputs as TypeScriptCalculationRawInputs,
    );
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "typescript-calculation-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.accounting.positives.declared,
        positives_passed: proof.accounting.positives.passed,
        mutants_declared: proof.accounting.mutants.declared,
        mutants_killed: proof.accounting.mutants.killed,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
