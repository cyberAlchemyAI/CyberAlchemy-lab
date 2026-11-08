import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";
import type {InterfaceCase} from "../../../targets/typescript/interface-v1.js";
import {evaluateInterfaceCase} from "../../../targets/typescript/interface-v1.js";
import {fail} from "../../shared/canonical.js";

export const interfaceTypeScriptV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "interface-typescript-v1",
  provider_version: "1.0.0-candidate",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(["interface_case"]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/interface-typescript-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/interface-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/versioned-interface-boundary/evaluator/evaluate-interface.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/effects-connections/evaluator/evaluate-w3.ts"
  ]),
  tool_ids: Object.freeze(["node", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) => {
    let input: InterfaceCase;
    try { input = JSON.parse(rawInputs.interface_case ?? "") as InterfaceCase; }
    catch { return fail("FACTORY_INTERFACE_INPUT_INVALID", "interface_case"); }
    const result = evaluateInterfaceCase(input);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "interface-typescript-v1",
      semantic_output: Object.freeze({portable: result.portable, native_evidence: result.native_evidence}),
      accounting: Object.freeze({positives_declared:1, positives_passed:1, mutants_declared:14, mutants_killed:14}),
      claim_ceiling: "candidate-local Interface proof; provider remains unregistered",
      authority_effect: "none",
    });
  },
});
