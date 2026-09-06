use cal_ontology_active_runtime::{
    ACTIVE_RUNTIME_CANDIDATE_ID, ACTIVE_RUNTIME_IDENTITY, ActiveRuntime, CANONICAL_CURSOR,
    CANONICAL_EVENT_COUNT, CANONICAL_EVENT_SET_DIGEST, CANONICAL_SUBJECT_COUNT,
    L4_ADAPTER_ADMISSION_DECISION_DIGEST, L4_ADAPTER_ADMISSION_VALIDATION_DIGEST,
    L4_PRODUCT_APPROVAL_DECISION_DIGEST, L4_PRODUCT_APPROVAL_VALIDATION_DIGEST,
    RuntimeActivationContract, canonical_w7_event_paths, rehearse_active_runtime,
};
use std::fs;

#[test]
fn exact_contract_binds_admitted_l4_and_canonical_event_cut() {
    let contract = RuntimeActivationContract::exact();
    assert_eq!(contract.candidate_id, ACTIVE_RUNTIME_CANDIDATE_ID);
    assert_eq!(contract.runtime_identity, ACTIVE_RUNTIME_IDENTITY);
    assert_eq!(
        contract.l4_product_approval_decision_digest,
        L4_PRODUCT_APPROVAL_DECISION_DIGEST
    );
    assert_eq!(
        contract.l4_product_approval_validation_digest,
        L4_PRODUCT_APPROVAL_VALIDATION_DIGEST
    );
    assert_eq!(
        contract.l4_adapter_admission_decision_digest,
        L4_ADAPTER_ADMISSION_DECISION_DIGEST
    );
    assert_eq!(
        contract.l4_adapter_admission_validation_digest,
        L4_ADAPTER_ADMISSION_VALIDATION_DIGEST
    );
    assert_eq!(contract.semantic_cursor, CANONICAL_CURSOR);
    assert_eq!(contract.source_event_count, CANONICAL_EVENT_COUNT);
    assert_eq!(contract.subject_count, CANONICAL_SUBJECT_COUNT);
    assert_eq!(contract.source_event_set_digest, CANONICAL_EVENT_SET_DIGEST);
    assert!(!contract.live);
    assert!(!contract.network);
    assert_eq!(contract.credential_kind, "none");
    assert!(!contract.external_effects);
    assert_eq!(contract.authority_effect, "none");
}

#[test]
fn runtime_stays_active_across_status_and_projection_until_stop() {
    let runtime = ActiveRuntime::start_canonical().unwrap();
    let root = runtime.sandbox_root().unwrap().to_path_buf();
    let first = runtime.status().unwrap();
    let second = runtime.status().unwrap();
    assert_eq!(first, second);
    assert!(first.prototype_runtime_active);
    assert!(first.calculated_projection_available);
    assert!(first.state_survives_commands);
    assert!(first.explicit_stop_required);
    assert_eq!(runtime.projection().semantic_cursor, CANONICAL_CURSOR);
    assert_eq!(runtime.projection().subjects.len(), CANONICAL_SUBJECT_COUNT);
    assert!(root.join("calculated-projection.json").is_file());

    let stop = runtime.stop().unwrap();
    assert!(stop.prototype_runtime_was_active);
    assert!(stop.restored_preimage_exact);
    assert!(stop.cleanup_verified);
    assert!(!root.exists());
}

#[test]
fn projection_is_calculated_from_the_exact_event_history() {
    let runtime = ActiveRuntime::start_canonical().unwrap();
    let projection = runtime.projection();
    assert_eq!(projection.semantic_cursor, 47);
    assert_eq!(projection.source_event_count, 47);
    assert_eq!(projection.subjects.len(), 47);
    assert_eq!(
        projection.source_event_set_digest,
        CANONICAL_EVENT_SET_DIGEST
    );
    assert_eq!(
        serde_json::from_str::<serde_json::Value>(runtime.projection_json()).unwrap(),
        serde_json::to_value(projection).unwrap()
    );
    runtime.stop().unwrap();
}

#[test]
fn event_corpus_drift_fails_before_sandbox_activation() {
    let temporary = tempfile::tempdir().unwrap();
    let semantic = temporary.path().join("semantic");
    let governance = temporary.path().join("governance");
    fs::create_dir_all(&semantic).unwrap();
    fs::create_dir_all(&governance).unwrap();
    let failure = match ActiveRuntime::start(&semantic, &governance, 47) {
        Ok(_) => panic!("empty event corpus must fail"),
        Err(failure) => failure,
    };
    assert_eq!(failure.code, "ACTIVE_RUNTIME_PROJECTION_FAILED");
}

#[test]
fn drop_performs_exact_cleanup_when_stop_is_not_called() {
    let root = {
        let runtime = ActiveRuntime::start_canonical().unwrap();
        runtime.sandbox_root().unwrap().to_path_buf()
    };
    assert!(!root.exists());
}

#[test]
fn canonical_paths_are_the_existing_w7_event_directories() {
    let (semantic, governance) = canonical_w7_event_paths();
    assert!(semantic.is_dir());
    assert!(governance.is_dir());
    assert_eq!(fs::read_dir(semantic).unwrap().count(), 47);
    assert_eq!(fs::read_dir(governance).unwrap().count(), 47);
}

#[test]
fn active_runtime_report_is_byte_deterministic() {
    let run_a = rehearse_active_runtime().unwrap();
    let run_b = rehearse_active_runtime().unwrap();
    let json_a = run_a.canonical_json().unwrap();
    let json_b = run_b.canonical_json().unwrap();
    assert_eq!(json_a, json_b);
    assert_eq!(run_a.result, "PASS");
    assert!(run_a.active_status.prototype_runtime_active);
    assert!(run_a.projection_matches_canonical_fixture);
    assert!(run_a.repeated_status_is_stable);
    assert!(run_a.stop.cleanup_verified);
    assert!(!run_a.active_status.governed_runtime_activated);
    println!("ACTIVE_RUNTIME_REPORT_JSON={json_a}");
}
