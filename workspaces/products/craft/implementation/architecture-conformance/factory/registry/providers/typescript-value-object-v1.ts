import {
  buildTypeScriptValueObjectProof,
  TYPESCRIPT_VALUE_OBJECT_RAW_PATHS,
  type TypeScriptValueObjectRawInputs,
} from "../../../realizations/value-object/typescript/complete-value-v1/index.js";
import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";

export const typeScriptValueObjectV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-value-object-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(TYPESCRIPT_VALUE_OBJECT_RAW_PATHS)),
  component_paths: Object.freeze(Object.values(TYPESCRIPT_VALUE_OBJECT_RAW_PATHS)),
  tool_ids: Object.freeze(["node", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const proof = await buildTypeScriptValueObjectProof(
      rawInputs as TypeScriptValueObjectRawInputs);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "typescript-value-object-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.accounting.positives.declared,
        positives_passed: proof.accounting.positives.passed,
        mutants_declared: proof.accounting.predecessor_family_controls.declared,
        mutants_killed: proof.accounting.predecessor_family_controls.killed,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
