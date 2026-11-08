import { buildOrderStatusProof } from "../../../typescript/realization-tests/enum/run-proof.js";
import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";

export const typeScriptEnumOrderStatusV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-enum-order-status-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze([
    "ontology",
    "base_profile",
    "typescript_profile",
    "definition",
    "realization_spec",
    "catalogue",
    "catalogue_predecessor",
    "binding",
    "provider",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-enum-order-status-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/realization-tests/enum/run-proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/registration.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realization/evaluator/evaluate-enum-bijection.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realization/replay/replay-enum-proof.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    const proof = await buildOrderStatusProof(rawInputs as Parameters<
      typeof buildOrderStatusProof
    >[0]);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-enum-order-status-v1",
      semantic_output: Object.freeze({
        case: proof.realizationCase,
        receipt: Object.freeze({
          state: proof.proofReceipt.state,
          positive: proof.proofReceipt.positive,
          mutations: proof.proofReceipt.mutations,
          exact_mutation_failure: proof.proofReceipt.exact_mutation_failure,
          claim_ceiling: proof.proofReceipt.claim_ceiling,
          authority_effect: proof.proofReceipt.authority_effect,
        }),
        positive_verdict: proof.positive.evaluation.verdict,
        mutation_findings: proof.mutation.evaluation.findings,
        replay_status: proof.replay.status,
      }),
      accounting: Object.freeze({
        positives_declared: proof.proofReceipt.positive.declared,
        positives_passed: proof.proofReceipt.positive.passed,
        mutants_declared: proof.proofReceipt.mutations.declared,
        mutants_killed: proof.proofReceipt.mutations.killed,
      }),
      claim_ceiling: proof.proofReceipt.claim_ceiling,
      authority_effect: "none",
    });
  },
});
