import {
  buildTypeScriptQueryProof,
  TYPESCRIPT_QUERY_RAW_PATHS,
  type TypeScriptQueryRawInputs,
} from "../../../realizations/query/typescript/read-model-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const typeScriptQueryV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-query-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(TYPESCRIPT_QUERY_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-query-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/typescript/read-model-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/typescript/read-model-v1/closed-subset.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/typescript/read-model-v1/typescript-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/query-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const proof = await buildTypeScriptQueryProof(
      rawInputs as TypeScriptQueryRawInputs,
    );
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "typescript-query-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.accounting.positives.declared,
        positives_passed: proof.accounting.positives.passed,
        mutants_declared: proof.accounting.source_hostiles.declared,
        mutants_killed: proof.accounting.source_hostiles.killed,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
