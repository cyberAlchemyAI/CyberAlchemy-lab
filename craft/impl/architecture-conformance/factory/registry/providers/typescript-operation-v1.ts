import { buildDirectOperationProof } from "../../../acceptance/operation/typescript/run-direct-operation-proof.js";
import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";

export const typeScriptOperationV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-operation-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(["definition", "binding", "source"]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-operation-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/operation/typescript/run-direct-operation-proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/state-change/evaluator/evaluate-operation.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/operation/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/operation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    const proof = await buildDirectOperationProof(rawInputs as Parameters<
      typeof buildDirectOperationProof
    >[0]);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-operation-v1",
      semantic_output: proof,
      accounting: Object.freeze({
        positives_declared: 1,
        positives_passed: proof.result === "pass" ? 1 : 0,
        mutants_declared: proof.mutations.length,
        mutants_killed: proof.mutations.filter(({ status }) => status === "killed").length,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none",
    });
  },
});
