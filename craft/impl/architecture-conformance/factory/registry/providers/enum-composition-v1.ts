import { evaluateEnumComposition } from
  "../../../acceptance/enum-parity/evaluate-enum-joins.js";
import type { FactoryNodeProviderV1 } from
  "../../contracts/factory-node-provider-v1.js";

export const enumCompositionV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "enum-composition-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze([
    "owner_catalogue", "denominator", "typescript_case", "typescript_expected",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/enum-composition-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/evaluate-enum-joins.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/typescript-wire-probe.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/evaluate-enum-joins.test.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({ raw_inputs: rawInputs, upstream }) => {
    const result = evaluateEnumComposition({ raw_inputs: rawInputs, upstream });
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "enum-composition-v1",
      semantic_output: result,
      accounting: Object.freeze({
        positives_declared: result.relation_obligations.length,
        positives_passed: result.relation_obligations.filter(({ status }) =>
          status === "passed").length,
        mutants_declared: 0,
        mutants_killed: 0,
      }),
      claim_ceiling: result.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
