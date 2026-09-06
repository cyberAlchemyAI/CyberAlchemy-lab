//! Candidate-local native Rust witness for WP-RMT-002 Mapping.
#[derive(Debug,Clone,PartialEq,Eq)] pub struct Field {pub source:String,pub target:String,pub required:bool}
#[derive(Debug,Clone,PartialEq,Eq)] pub struct FailureOutcome {pub status:String,pub code:Option<String>,pub details:Vec<String>}
#[derive(Debug,Clone,PartialEq,Eq)] pub struct MappingDescriptor {pub source_contract_id:String,pub target_contract_id:String,pub direction:String,pub correspondence:Vec<Field>,pub totality:String,pub effect_policy:String}
#[derive(Debug,Clone,PartialEq,Eq)] pub struct MappingObservation {pub source_contract_id:String,pub target_contract_id:String,pub direction:String,pub observed_correspondence:Vec<Field>,pub missing_required_fields:Vec<String>,pub undeclared_extra_fields:Vec<String>,pub totality:String,pub coercions:Vec<String>,pub effect_policy:String,pub effects:Vec<String>,pub failure_outcome:FailureOutcome}
pub fn evaluate_mapping(descriptor:&MappingDescriptor,observed:&MappingObservation)->Vec<&'static str>{
 let mut findings=Vec::new();
 if (observed.source_contract_id.as_str(),observed.target_contract_id.as_str())!=(descriptor.source_contract_id.as_str(),descriptor.target_contract_id.as_str()){findings.push("RMT_MAP_SOURCE_TARGET_SWAP");}
 if observed.direction!=descriptor.direction{findings.push("RMT_MAP_DIRECTION_FLIP");}
 if !observed.missing_required_fields.is_empty(){findings.push("RMT_MAP_MISSING_REQUIRED_FIELD");}
 if !observed.undeclared_extra_fields.is_empty(){findings.push("RMT_MAP_UNDECLARED_EXTRA_FIELD");}
 if observed.observed_correspondence!=descriptor.correspondence{findings.push("RMT_MAP_CORRESPONDENCE_DRIFT");}
 if observed.totality!=descriptor.totality{findings.push("RMT_MAP_TOTALITY_OVERCLAIM");}
 if !observed.coercions.is_empty(){findings.push("RMT_MAP_SILENT_COERCION");}
 if observed.effect_policy!=descriptor.effect_policy||!observed.effects.is_empty(){findings.push("RMT_MAP_EFFECT_POLICY_VIOLATION");}
 if observed.failure_outcome.status!="failure"{findings.push("RMT_MAP_FAILURE_AS_SUCCESS");}
 else if observed.failure_outcome.code.as_ref().map_or(true,|value|value.is_empty())||observed.failure_outcome.details.is_empty(){findings.push("RMT_MAP_FAILURE_DETAIL_LOSS");}
 findings
}
