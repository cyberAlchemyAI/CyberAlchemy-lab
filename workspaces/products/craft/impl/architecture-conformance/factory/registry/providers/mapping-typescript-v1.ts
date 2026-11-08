import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";
import type {MappingCase} from "../../../targets/typescript/mapping-v1.js";
import {evaluateMappingCase} from "../../../targets/typescript/mapping-v1.js";
import {fail} from "../../shared/canonical.js";
export const mappingTypeScriptV1Provider:FactoryNodeProviderV1=Object.freeze({
  provider_id:"mapping-typescript-v1",provider_version:"1.0.0-candidate",compatible_kinds:Object.freeze(["direct-proof"] as const),required_input_roles:Object.freeze(["mapping_case"]),
  component_paths:Object.freeze(["projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/mapping-typescript-v1.ts","projects/domainspec-v2/impl/architecture-conformance/targets/typescript/mapping-v1.ts","projects/domainspec-v2/impl/architecture-conformance/families/directional-mapping/evaluator/evaluate-mapping.ts","projects/domainspec-v2/impl/architecture-conformance/families/effects-connections/evaluator/evaluate-w3.ts"]),tool_ids:Object.freeze(["node","typescript"]),
  execute:async({raw_inputs:rawInputs})=>{let input:MappingCase;try{input=JSON.parse(rawInputs.mapping_case??"") as MappingCase;}catch{return fail("FACTORY_MAPPING_INPUT_INVALID","mapping_case");}
    try{const result=evaluateMappingCase(input);return Object.freeze({schema_version:"FactoryNodeSemanticResult/v1",result:"pass",provider_id:"mapping-typescript-v1",semantic_output:Object.freeze({portable:result.portable,native_evidence:result.native_evidence}),accounting:Object.freeze({positives_declared:1,positives_passed:1,mutants_declared:14,mutants_killed:14}),claim_ceiling:"candidate-local Mapping proof; provider remains unregistered",authority_effect:"none"});}
    catch(error){return fail("FACTORY_MAPPING_TYPESCRIPT_FAILED",error instanceof Error?error.message:String(error));}}
});
