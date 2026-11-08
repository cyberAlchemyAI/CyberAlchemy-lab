import { proveEnumParity } from
  "../../../acceptance/enum-parity/evaluate-enum-joins.js";
import type { FactoryNodeProviderV1 } from
  "../../contracts/factory-node-provider-v1.js";

export const enumParityV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "enum-parity-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze([]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/enum-parity-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/evaluate-enum-joins.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/typescript-wire-probe.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/evaluate-enum-joins.test.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({ upstream }) => {
    const result = proveEnumParity(upstream);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "enum-parity-v1",
      semantic_output: result,
      accounting: Object.freeze({
        positives_declared: result.parity.portable_obligations.length,
        positives_passed: result.parity.portable_obligations.filter(({ status }) =>
          status === "passed").length,
        mutants_declared: result.mutants.length,
        mutants_killed: result.mutants.filter(({ status }) => status === "killed").length,
      }),
      claim_ceiling: result.parity.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
