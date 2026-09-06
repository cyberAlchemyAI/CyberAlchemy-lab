import type {MappingDescriptor,MappingObservation} from "../../families/effects-connections/contracts/w3-contracts.js";
import {evaluateW3} from "../../families/effects-connections/evaluator/evaluate-w3.js";
import type {DirectionalMappingDescriptor,DirectionalMappingObservation} from "../../families/directional-mapping/contracts/mapping-contracts.js";
import {evaluateDirectionalMapping} from "../../families/directional-mapping/evaluator/evaluate-mapping.js";
import {settlementMappingDescriptor,settlementMappingObservation} from "../../families/directional-mapping/fixtures/settlement-mapping.js";

export type MappingPortableResult=Readonly<{
  schema_version:"domainspec.mapping-portable-result/v1";result:"pass";meta_type:"Mapping";
  source_contract_id:string;target_contract_id:string;direction:"forward"|"reverse"|"bidirectional";
  correspondence:readonly string[];totality:"total"|"partial-fallible";failure_contract_id:string;
  structured_failure_preserved:true;silent_coercion_rejected:true;effect_policy:"none"|"declared-read-only";authority_effect:"none";
}>;
export type MappingCase=Readonly<{w3_descriptor:MappingDescriptor;w3_observation:MappingObservation;descriptor:DirectionalMappingDescriptor;observation:DirectionalMappingObservation}>;
const ref=(id:string)=>({id,sha256:"a".repeat(64)});
export const makeSettlementMappingCase=():MappingCase=>({
  w3_descriptor:{schema_version:"domainspec.w3-descriptor/v1",descriptor_id:"mapping.settlement-record-to-response-v1",language:"typescript",
    binding:{protocol_id:"domainspec.w3-descriptor-binding/v1",concept_ref:ref("DS-D1.13"),decision_ref:ref("WP-RMT-002"),profile_ref:ref("typescript"),provider_ref:ref("typescript-w3-effects-connections-v1"),source_ref:ref("financial-settlement.ts"),fixture_ref:ref("mapping-case")},
    claim_ceiling:"candidate-local-exact-fixture",authority_effect:"none",kind:"Mapping",source_contract_id:"SettlementRecord/v1",target_contract_id:"SettlementResponse/v1",direction:"forward",
    correspondence:[{source:"id",target:"settlement_id",mode:"direct"},{source:"player_id",target:"player_id",mode:"direct"},{source:"amount",target:"amount",mode:"direct"}],
    totality:"partial-fallible",failure_contract_id:"MappingFailure/v1",effect_policy:"none",reverse_contract_id:null},
  w3_observation:{kind:"Mapping",source_contract_id:"SettlementRecord/v1",target_contract_id:"SettlementResponse/v1",direction:"forward",
    observed_correspondence:[{source:"id",target:"settlement_id",mode:"direct"},{source:"player_id",target:"player_id",mode:"direct"},{source:"amount",target:"amount",mode:"direct"}],
    totality:"partial-fallible",failure_contract_id:"MappingFailure/v1",failure_observed:true,effect_policy:"none",effects:[],reverse_contract_complete:false},
  descriptor:settlementMappingDescriptor,observation:settlementMappingObservation(),
});
export const evaluateMappingCase=(input:MappingCase):Readonly<{portable:MappingPortableResult;native_evidence:Readonly<{language:"typescript";mechanism:"readonly-correspondence-and-structured-result-union"}>}>=>{
  const w3=evaluateW3(input.w3_descriptor,input.w3_observation);const extension=evaluateDirectionalMapping(input.descriptor,input.observation);
  if(w3.verdict!=="pass"||extension.verdict!=="pass") throw new Error(`RMT_MAP_TYPESCRIPT_REJECTED:${JSON.stringify({w3:w3.findings,extension:extension.findings})}`);
  return Object.freeze({portable:Object.freeze({schema_version:"domainspec.mapping-portable-result/v1",result:"pass",meta_type:"Mapping",
    source_contract_id:input.descriptor.source_contract_id,target_contract_id:input.descriptor.target_contract_id,direction:input.descriptor.direction,
    correspondence:Object.freeze(input.descriptor.correspondence.map(({source,target,required})=>`${source}->${target}:${required?"required":"optional"}`).sort()),
    totality:input.descriptor.totality,failure_contract_id:input.descriptor.failure_contract_id,structured_failure_preserved:true,silent_coercion_rejected:true,
    effect_policy:input.descriptor.effect_policy,authority_effect:"none"}),native_evidence:Object.freeze({language:"typescript",mechanism:"readonly-correspondence-and-structured-result-union"})});
};
