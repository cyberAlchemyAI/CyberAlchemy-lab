use cal_ontology_execution_envelope::stateful_sandbox_target::{
    L3_FILESYSTEM_RECEIPT_DIGEST, STATEFUL_SANDBOX_CANDIDATE_ID, STATEFUL_SANDBOX_IDENTITY,
    SandboxActivationHarness, SandboxActivationRequest, StatefulSandboxTarget,
    rehearse_stateful_sandbox,
};
use cal_ontology_execution_envelope::{
    EventCut, ExecutionEngine, ExecutionEnvelope, ExecutionMode, ExecutionStepId,
    ExecutionTargetAdapter, PrototypeTargetBinding,
};
use serde_json::Value;

const CONTRACT: &str = include_str!("fixtures/stateful-sandbox.json");
const SCHEMA: &str = include_str!("../schemas/stateful-sandbox.schema.json");

#[test]
fn stateful_sandbox_contract_has_exact_seven_invariants() {
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
            "SBX-01-NEW-IDENTITY",
            "SBX-02-PATH-CONFINEMENT",
            "SBX-03-STATE-SURVIVES-OBSERVATION",
            "SBX-04-EXPLICIT-TEARDOWN",
            "SBX-05-LIVE-REFUSAL",
            "SBX-06-ENGINE-SUBSTITUTION-REFUSAL",
            "SBX-07-DETERMINISTIC-REPORT",
        ]
    );
    assert_eq!(schema["properties"]["invariants"]["minItems"], 7);
    assert_eq!(schema["properties"]["invariants"]["maxItems"], 7);
}

#[test]
fn activation_state_survives_until_explicit_teardown() {
    let mut target = StatefulSandboxTarget::new().unwrap();
    let root = target.root().to_path_buf();
    let preimage = target.state_bytes().unwrap();
    let observation = SandboxActivationHarness
        .activate(&SandboxActivationRequest::exact(), &mut target)
        .unwrap();
    assert!(root.is_dir());
    assert!(root.join("sandbox-state.json").is_file());
    assert_ne!(target.state_bytes().unwrap(), preimage);
    assert!(observation.state_survives_observation);
    assert!(observation.sandbox_activation_observed);
    assert!(observation.active_cut_unchanged);
    assert!(observation.staged_cut_exact);
    assert!(!observation.migration_performed);
    assert!(!observation.cutover_performed);
    assert!(!observation.runtime_activated);

    let state = target.state().unwrap();
    assert_eq!(state.active_cut, EventCut::exact_source());
    assert_eq!(state.staged_cut, Some(EventCut::exact_target()));
    assert_eq!(state.runtime.runtime_state, "prototype-sandbox-active");
    assert_eq!(state.runtime.traffic_target, "epoch-001");

    let teardown = target.teardown().unwrap();
    assert!(teardown.restored_preimage_exact);
    assert!(teardown.cleanup_verified);
    assert!(!root.exists());
}

#[test]
fn target_owns_its_process_temporary_root() {
    let target = StatefulSandboxTarget::new().unwrap();
    let root = target.root().to_path_buf();
    assert_eq!(root.parent(), Some(std::env::temp_dir().as_path()));
    assert!(
        root.file_name()
            .unwrap()
            .to_string_lossy()
            .starts_with("cal-d65-state-bearing-sandbox-")
    );
    target.teardown().unwrap();
    assert!(!root.exists());
}

#[test]
fn live_mode_is_refused_before_sandbox_mutation() {
    let mut request = SandboxActivationRequest::exact();
    request.mode = ExecutionMode::Live;
    let mut target = StatefulSandboxTarget::new().unwrap();
    let root = target.root().to_path_buf();
    let preimage = target.capture_preimage();
    let failure = SandboxActivationHarness
        .activate(&request, &mut target)
        .unwrap_err();
    assert_eq!(failure.code, "STATEFUL_SANDBOX_LIVE_MODE_FORBIDDEN");
    assert_eq!(target.capture_preimage(), preimage);
    target.teardown().unwrap();
    assert!(!root.exists());
}

#[test]
fn selection_digest_mismatch_is_refused_before_mutation() {
    let mut request = SandboxActivationRequest::exact();
    request.decision_digest = "0".repeat(64);
    let mut target = StatefulSandboxTarget::new().unwrap();
    let preimage = target.capture_preimage();
    let failure = SandboxActivationHarness
        .activate(&request, &mut target)
        .unwrap_err();
    assert_eq!(failure.code, "STATEFUL_SANDBOX_REQUEST_MISMATCH");
    assert_eq!(target.capture_preimage(), preimage);
    target.teardown().unwrap();
}

#[test]
fn activation_failure_restores_exact_preimage() {
    let mut target = StatefulSandboxTarget::with_fault(ExecutionStepId::Activate).unwrap();
    let root = target.root().to_path_buf();
    let preimage = target.capture_preimage();
    let failure = SandboxActivationHarness
        .activate(&SandboxActivationRequest::exact(), &mut target)
        .unwrap_err();
    assert_eq!(failure.code, "INJECTED_STATEFUL_SANDBOX_FAILURE");
    assert_eq!(target.capture_preimage(), preimage);
    let teardown = target.teardown().unwrap();
    assert!(teardown.cleanup_verified);
    assert!(!root.exists());
}

#[test]
fn existing_execution_engine_refuses_the_l4_binding() {
    let mut target = StatefulSandboxTarget::new().unwrap();
    let preimage = target.capture_preimage();
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.target = PrototypeTargetBinding::exact_stateful_sandbox();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "PROTOTYPE_TARGET_BOUNDARY_VIOLATION");
    assert_eq!(target.capture_preimage(), preimage);
    assert_eq!(target.binding().identity, STATEFUL_SANDBOX_IDENTITY);
    target.teardown().unwrap();
}

#[test]
fn stateful_sandbox_report_is_byte_deterministic() {
    let run_a = rehearse_stateful_sandbox().unwrap();
    let run_b = rehearse_stateful_sandbox().unwrap();
    let json_a = run_a.canonical_json().unwrap();
    let json_b = run_b.canonical_json().unwrap();
    assert_eq!(json_a, json_b);
    assert_eq!(run_a.body.result, "PASS");
    assert_eq!(run_a.body.candidate_id, STATEFUL_SANDBOX_CANDIDATE_ID);
    assert_eq!(
        run_a.body.predecessor_receipt_digest,
        L3_FILESYSTEM_RECEIPT_DIGEST
    );
    assert!(run_a.body.observation.state_survives_observation);
    assert!(run_a.body.teardown.cleanup_verified);
    assert!(!run_a.body.live_execution_ready);
    assert!(!run_a.body.product_approved);
    assert!(!run_a.body.adapter_admitted);
    println!("STATEFUL_SANDBOX_REPORT_JSON={json_a}");
}
