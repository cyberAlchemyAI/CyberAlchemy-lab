use cal_ontology_execution_envelope::{
    D65CUT_DECISION_DIGEST, EventCut, ExecutionEngine, ExecutionEnvelope, ExecutionMode,
    ExecutionStepId, InMemoryTarget, PrototypeTargetBinding, SOURCE_EVENT_SET_DIGEST,
    TARGET_EVENT_SET_DIGEST, TARGET_PROJECTION_DIGEST,
};

#[test]
fn exact_prototype_executes_ten_steps_and_rolls_back() {
    let envelope = ExecutionEnvelope::exact_prototype();
    let mut target = InMemoryTarget::new();
    let preimage = target.snapshot();
    let receipt = ExecutionEngine.execute(&envelope, &mut target).unwrap();
    assert_eq!(receipt.result, "PASS");
    assert_eq!(receipt.trace.len(), 10);
    assert_eq!(receipt.source_event_count, 7);
    assert_eq!(receipt.source_event_set_digest, SOURCE_EVENT_SET_DIGEST);
    assert_eq!(receipt.target_event_count, 11);
    assert_eq!(receipt.target_event_set_digest, TARGET_EVENT_SET_DIGEST);
    assert_eq!(receipt.target_projection_digest, TARGET_PROJECTION_DIGEST);
    assert_eq!(receipt.rollback_result, "PASS");
    assert!(!receipt.live_execution_ready);
    assert!(!receipt.runtime_activated);
    assert!(!receipt.migration_performed);
    assert!(!receipt.cutover_performed);
    assert!(!receipt.external_effects);
    assert_eq!(receipt.authority_effect, "none");
    assert_eq!(target.snapshot(), preimage);
}

#[test]
fn live_mode_fails_before_any_target_mutation() {
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.mode = ExecutionMode::Live;
    let mut target = InMemoryTarget::new();
    let preimage = target.snapshot();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "LIVE_BINDINGS_MISSING");
    assert_eq!(target.snapshot(), preimage);
}

#[test]
fn stale_decision_digest_is_rejected() {
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.decision_digest = "0".repeat(64);
    let mut target = InMemoryTarget::new();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "AUTHORIZATION_BINDING_MISMATCH");
    assert_eq!(D65CUT_DECISION_DIGEST.len(), 64);
}

#[test]
fn reordered_migration_and_verification_are_rejected() {
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.step_order.swap(4, 5);
    let mut target = InMemoryTarget::new();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "EXECUTION_POLICY_MISMATCH");
}

#[test]
fn credential_injection_is_rejected() {
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.target.credential_kind = "token".into();
    let mut target = InMemoryTarget::new();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "PROTOTYPE_TARGET_BOUNDARY_VIOLATION");
}

#[test]
fn live_or_external_target_injection_is_rejected() {
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.target = PrototypeTargetBinding {
        live: true,
        external_effects: true,
        ..PrototypeTargetBinding::exact()
    };
    let mut target = InMemoryTarget::new();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "PROTOTYPE_TARGET_BOUNDARY_VIOLATION");
}

#[test]
fn target_verification_failure_restores_preimage() {
    let envelope = ExecutionEnvelope::exact_prototype();
    let mut target = InMemoryTarget::with_fault(ExecutionStepId::VerifyTarget);
    let preimage = target.snapshot();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "INJECTED_PROTOTYPE_FAILURE");
    assert_eq!(target.snapshot(), preimage);
}

#[test]
fn substituted_event_cut_is_rejected_before_transition() {
    let mut envelope = ExecutionEnvelope::exact_prototype();
    envelope.target_cut = EventCut {
        event_count: 10,
        event_set_digest: "0".repeat(64),
        projection_digest: "0".repeat(64),
        canonical_replay_source: true,
    };
    let mut target = InMemoryTarget::new();
    let preimage = target.snapshot();
    let failure = ExecutionEngine.execute(&envelope, &mut target).unwrap_err();
    assert_eq!(failure.code, "EVENT_CUT_BINDING_MISMATCH");
    assert_eq!(target.snapshot(), preimage);
}
