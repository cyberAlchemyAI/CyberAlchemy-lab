import {
  buildTypeScriptOperationProof,
  TYPESCRIPT_OPERATION_RAW_PATHS,
  type TypeScriptOperationRawInputs,
} from "../../../realizations/operation/typescript/state-changing-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {fail} from "../../shared/canonical.js";

export const operationTypeScriptV1Provider:
FactoryNodeProviderV1 = Object.freeze({
  provider_id: "operation-typescript-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(
    Object.keys(TYPESCRIPT_OPERATION_RAW_PATHS),
  ),
  component_paths: Object.freeze([
    ...new Set(Object.values(TYPESCRIPT_OPERATION_RAW_PATHS)),
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const roles = Object.keys(TYPESCRIPT_OPERATION_RAW_PATHS) as readonly (
      keyof typeof TYPESCRIPT_OPERATION_RAW_PATHS
    )[];
    const actualRoles = Object.keys(rawInputs).sort();
    const expectedRoles = [...roles].sort();
    if (JSON.stringify(actualRoles) !== JSON.stringify(expectedRoles)) {
      return fail("TS_OP_PROVIDER_INPUT_ROLES_INVALID");
    }
    const snapshot = Object.freeze(Object.fromEntries(
      roles.map((role) => [
        role,
        `${rawInputs[role] ?? fail(
          "TS_OP_PROVIDER_INPUT_ROLES_INVALID",
          role,
        )}`,
      ]),
    )) as TypeScriptOperationRawInputs;
    const proof = await buildTypeScriptOperationProof(snapshot);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "operation-typescript-v1",
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
