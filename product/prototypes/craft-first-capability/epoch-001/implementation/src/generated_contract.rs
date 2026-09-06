// GENERATED FILE: edit upstream JSON and run ../p2-build.py.
pub const SYSTEM_ONTOLOGY_SHA256: &str = "5686221538535dcff6ba1a0454d3c480fbe2c83b0ebae3af4292af946c1c87fa";
pub const SMOKE_PAYLOAD: &str = r#"{"authority_effect":"none","capability_id":"CAL-PROTOTYPE-CAPABILITY-DEFINITION-SNAPSHOT-CONSTRUCTION","legacy_id":"DS-D1.1","result_kind":"definition_snapshot_witness","system_ontology_sha256":"5686221538535dcff6ba1a0454d3c480fbe2c83b0ebae3af4292af946c1c87fa","term":"Entity"}"#;
pub const SYSTEM_ONTOLOGY: &str = include_str!("../../compiled/system-ontology.json");

pub fn verify_contract() -> bool {
    SYSTEM_ONTOLOGY.contains("CAL-P2-SYSTEM-ONTOLOGY-DEFINITION-SNAPSHOT-CONSTRUCTION")
        && SYSTEM_ONTOLOGY.contains("CAL-P2-OBLIGATION-STABLE-ID")
        && SYSTEM_ONTOLOGY.contains("CAL-P2-OBLIGATION-EXACT-SOURCE")
        && SYSTEM_ONTOLOGY.contains("CAL-P2-OBLIGATION-ENTITY-CRITERION")
        && SYSTEM_ONTOLOGY.contains("CAL-P2-OBLIGATION-NO-AUTHORITY")
        && SYSTEM_ONTOLOGY.contains("\"authority_effect\": \"none\"")
}

pub fn smoke_payload() -> &'static str {
    SMOKE_PAYLOAD
}
