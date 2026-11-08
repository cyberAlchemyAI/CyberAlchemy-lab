use cal_ontology_execution_envelope::filesystem_target::{
    DisposableFilesystemTarget, FILESYSTEM_REHEARSAL_CANDIDATE_ID, L2_CERTIFICATION_RECEIPT_DIGEST,
    rehearse_disposable_filesystem,
};
use cal_ontology_execution_envelope::{
    ExecutionEngine, ExecutionEnvelope, ExecutionMode, ExecutionStepId, ExecutionTargetAdapter,
    InMemoryTarget, PrototypeTargetBinding,
};
use serde_json::Value;
use std::fs;

const CONTRACT: &str = include_str!("fixtures/filesystem-rehearsal.json");
const SCHEMA: &str = include_str!("../schemas/filesystem-rehearsal.schema.json");

#[test]
fn filesystem_contract_has_exact_six_invariants() {
    let contract: Value = serde_json::from_str(CONTRACT).unwrap();
    let schema: Value = serde_json::from_str(SCHEMA).unwrap();
    let ids: Vec<_> = contract["invariants"]
        .as_array()
        .unwrap()
        .iter()
        .map(|invariant| invariant["invariant_id"].as_str().unwrap())
        .collect();
    assert_eq!(
        ids,
        [
            "FSR-01-PATH-CONFINEMENT",
            "FSR-02-EXACT-BINDING",
            "FSR-03-BYTE-PREIMAGE",
            "FSR-04-FAILURE-RESTORATION",
            "FSR-05-CLEANUP",
            "FSR-06-DETERMINISTIC-REPORT",
        ]
    );
    assert_eq!(schema["properties"]["invariants"]["minItems"], 6);
    assert_eq!(schema["properties"]["invariants"]["maxItems"], 6);
}

#[test]
fn filesystem_rehearsal_report_is_byte_deterministic() {
    let run_a = rehearse_disposable_filesystem().unwrap();
    let run_b = rehearse_disposable_filesystem().unwrap();
    let json_a = run_a.canonical_json().unwrap();
    let json_b = run_b.canonical_json().unwrap();
    assert_eq!(json_a, json_b);
    assert_eq!(run_a.body.result, "PASS");
    assert_eq!(run_a.body.candidate_id, FILESYSTEM_REHEARSAL_CANDIDATE_ID);
    assert_eq!(
        run_a.body.baseline_receipt_digest,
        L2_CERTIFICATION_RECEIPT_DIGEST
    );
    assert!(run_a.body.rollback_exact);
    assert!(run_a.body.cleanup_verified);
    assert!(run_a.body.disposable_local_filesystem_effects);
    assert!(!run_a.body.external_effects);
    println!("FILESYSTEM_REHEARSAL_REPORT_JSON={json_a}");
}

#[test]
fn target_creates_only_an_adapter_owned_temporary_root() {
    let target = DisposableFilesystemTarget::new().unwrap();
    let root = target.root().to_path_buf();
    assert_eq!(root.parent(), Some(std::env::temp_dir().as_path()));
    assert!(
        root.file_name()
            .unwrap()
            .to_string_lossy()
            .starts_with("cal-d65-filesystem-rehearsal-")
    );
    assert!(root.join("target-state.json").is_file());
    target.cleanup().unwrap();
    assert!(!root.exists());
}

#[test]
fn cutover_failure_restores_exact_filesystem_bytes() {
    let mut target = DisposableFilesystemTarget::with_fault(ExecutionStepId::Cutover).unwrap();
    let root = target.root().to_path_buf();
    let preimage = target.state_bytes().unwrap();
    let failure = ExecutionEngine
        .execute(
            &ExecutionEnvelope::exact_filesystem_rehearsal(),
            &mut target,
        )
        .unwrap_err();
    assert_eq!(failure.code, "INJECTED_FILESYSTEM_REHEARSAL_FAILURE");
    assert_eq!(target.state_bytes().unwrap(), preimage);
    target.cleanup().unwrap();
    assert!(!root.exists());
}

#[test]
fn tampered_preimage_is_rejected_before_transition() {
    let mut target = DisposableFilesystemTarget::new().unwrap();
    let root = target.root().to_path_buf();
    fs::write(root.join("target-state.json"), b"{}").unwrap();
    let tampered = target.state_bytes().unwrap();
    let failure = ExecutionEngine
        .execute(
            &ExecutionEnvelope::exact_filesystem_rehearsal(),
            &mut target,
        )
        .unwrap_err();
    assert_eq!(failure.code, "DECODE_TARGET_STATE_FAILED");
    assert_eq!(target.state_bytes().unwrap(), tampered);
    target.cleanup().unwrap();
    assert!(!root.exists());
}

#[test]
fn filesystem_and_in_memory_bindings_cannot_be_substituted() {
    let mut filesystem = DisposableFilesystemTarget::new().unwrap();
    let failure = ExecutionEngine
        .execute(&ExecutionEnvelope::exact_prototype(), &mut filesystem)
        .unwrap_err();
    assert_eq!(failure.code, "PROTOTYPE_TARGET_BOUNDARY_VIOLATION");
    filesystem.cleanup().unwrap();

    let mut memory = InMemoryTarget::new();
    let failure = ExecutionEngine
        .execute(
            &ExecutionEnvelope::exact_filesystem_rehearsal(),
            &mut memory,
        )
        .unwrap_err();
    assert_eq!(failure.code, "PROTOTYPE_TARGET_BOUNDARY_VIOLATION");
    assert_eq!(
        PrototypeTargetBinding::exact_filesystem().credential_kind,
        "none"
    );
}

#[test]
fn live_mode_is_rejected_before_filesystem_mutation() {
    let mut envelope = ExecutionEnvelope::exact_filesystem_rehearsal();
    envelope.mode = ExecutionMode::Live;
    let mut target = DisposableFilesystemTarget::new().unwrap();
    let root = target.root().to_path_buf();
    let preimage = target.capture_preimage();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "LIVE_BINDINGS_MISSING");
    assert_eq!(target.capture_preimage(), preimage);
    target.cleanup().unwrap();
    assert!(!root.exists());
}
