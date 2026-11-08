import { buildShipmentPrioritySemanticSliceProof } from
  "../../../acceptance/enum-regression/shipment-priority/run-shipment-priority-semantic-slice-proof.js";
import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";

export const typeScriptEnumShipmentPrioritySemanticSliceV1Provider:
FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-enum-shipment-priority-semantic-slice-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze([
    "case", "expected", "ontology_slice", "typescript_profile_slice", "provider",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-enum-shipment-priority-semantic-slice-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-regression/shipment-priority/run-shipment-priority-semantic-slice-proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-regression/shipment-priority/run-shipment-priority-proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/registration.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    const proof = await buildShipmentPrioritySemanticSliceProof(rawInputs as Parameters<
      typeof buildShipmentPrioritySemanticSliceProof
    >[0]);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-enum-shipment-priority-semantic-slice-v1",
      semantic_output: proof,
      accounting: Object.freeze({
        positives_declared: 1,
        positives_passed: proof.positive_verdict === "pass" ? 1 : 0,
        mutants_declared: 1,
        mutants_killed: proof.mutation.status === "killed" ? 1 : 0,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none",
    });
  },
});
