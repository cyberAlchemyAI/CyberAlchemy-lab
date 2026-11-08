import type {DirectionalMappingDescriptor, DirectionalMappingObservation, MappingRelationAssertion} from "../contracts/mapping-contracts.js";

export const settlementMappingDescriptor: DirectionalMappingDescriptor = Object.freeze({
  schema_version:"domainspec.directional-mapping/v1", descriptor_id:"mapping.settlement-record-to-response-v1",
  source_contract_id:"SettlementRecord/v1",target_contract_id:"SettlementResponse/v1",direction:"forward",
  correspondence:Object.freeze([
    Object.freeze({source:"id",target:"settlement_id",required:true}),
    Object.freeze({source:"player_id",target:"player_id",required:true}),
    Object.freeze({source:"amount",target:"amount",required:true}),
  ]), required_source_fields:Object.freeze(["id","player_id","amount"]),allowed_source_fields:Object.freeze(["id","player_id","amount"]),
  totality:"partial-fallible",failure_contract_id:"MappingFailure/v1",coercion_policy:"reject-silent",effect_policy:"none",
  admission_status:"candidate",authority_effect:"none",
});
export const settlementMappingObservation = (): DirectionalMappingObservation => ({
  source_contract_id:"SettlementRecord/v1",target_contract_id:"SettlementResponse/v1",direction:"forward",
  observed_correspondence:settlementMappingDescriptor.correspondence.map((item)=>({...item})),missing_required_fields:[],undeclared_extra_fields:[],
  totality:"partial-fallible",coercions:[],effect_policy:"none",effects:[],
  failure_outcome:{status:"failure",code:"MAPPING_INPUT_INVALID",details:["missing:id"]},
});
export const mappingRelationAssertion=(contract_id:MappingRelationAssertion["contract_id"]="mapping/maps-source-to-maps-from"):MappingRelationAssertion=>({
  contract_id,mode:"blueprint-only",owner_evidence_sha256:"a".repeat(64),current_owner_evidence_sha256:"a".repeat(64),
  source_type:"architecture.MappingImplementation",target_type:"architecture.DataShapeContract",exact_assertion_id:null,
});
