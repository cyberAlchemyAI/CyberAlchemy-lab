#[path = "../src/remaining_types/event_v1.rs"]
mod event_v1;
use event_v1::*;

fn baseline() -> (EventDescriptor, EventObservation) {
    let descriptor = EventDescriptor { event_name: "SettlementCreated".into(), payload_version: "1".into(), persistence_checkpoint: "durable-outbox-append".into(), consumer_contract_ids: vec!["SettlementProjectionConsumer/v1".into()] };
    let observed = EventObservation {
        event_name: "SettlementCreated".into(), tense: "past".into(), payload_version: "1".into(), payload_mutable: false,
        occurrence_id: "settlement:req-1".into(), occurrence_id_stable: true, occurrence_id_reused: false,
        durable_checkpoints: vec!["durable-outbox-append".into()], publication_after_commit: true,
        consumer_contract_ids: vec!["SettlementProjectionConsumer/v1".into()],
        consumer_payload_checks: vec![ConsumerCheck { consumer_contract_id: "SettlementProjectionConsumer/v1".into(), payload_version: "1".into(), accepted: true }],
        distributed_exactly_once_claim: false,
        durable_occurrence: DurableOccurrence { occurrence_id: "settlement:req-1".into(), persistence_checkpoint: "durable-outbox-append".into(), publication_attempt_id: "publish:req-1:1".into(), acknowledgement_state: "unknown".into(), delivery_observation: "at-least-once-observed".into(), consumption_observation: "accepted".into() },
        s1_observation: None,
    };
    (descriptor, observed)
}

#[test]
fn native_event_passes_and_handle_is_separate() {
    let (descriptor, observed) = baseline();
    assert_eq!(evaluate_event(&descriptor, &observed), Ok(Vec::<&str>::new()));
    assert!(durable_handle_is_coherent(&descriptor, &observed));
    let mut incoherent = observed.clone(); incoherent.durable_occurrence.occurrence_id = "other".into();
    assert_eq!(evaluate_event(&descriptor, &incoherent), Err("RMT_EVENT_DURABLE_HANDLE_INVALID"));
    assert!(!observed.distributed_exactly_once_claim);
}

#[test]
fn kills_all_ten_base_semantic_controls_as_singletons() {
    let (descriptor, baseline) = baseline();
    let mut cases: Vec<(&str, EventObservation)> = Vec::new();
    let mut value = baseline.clone(); value.event_name = "CreateSettlement".into(); value.tense = "present".into(); cases.push(("RMT_EVENT_NON_PAST_TENSE", value));
    let mut value = baseline.clone(); value.payload_mutable = true; cases.push(("RMT_EVENT_MUTABLE_PAYLOAD", value));
    let mut value = baseline.clone(); value.occurrence_id_stable = false; cases.push(("RMT_EVENT_UNSTABLE_OCCURRENCE_ID", value));
    let mut value = baseline.clone(); value.occurrence_id_reused = true; cases.push(("RMT_EVENT_REUSED_OCCURRENCE_ID", value));
    let mut value = baseline.clone(); value.durable_checkpoints.clear(); cases.push(("RMT_EVENT_CHECKPOINT_MISSING", value));
    let mut value = baseline.clone(); value.durable_checkpoints.push("durable-outbox-append".into()); cases.push(("RMT_EVENT_CHECKPOINT_DUPLICATE", value));
    let mut value = baseline.clone(); value.publication_after_commit = false; cases.push(("RMT_EVENT_PUBLISH_BEFORE_COMMIT", value));
    let mut value = baseline.clone(); value.distributed_exactly_once_claim = true; cases.push(("RMT_EVENT_EXACTLY_ONCE_OVERCLAIM", value));
    let mut value = baseline.clone(); value.consumer_contract_ids.push("UndeclaredConsumer/v1".into()); cases.push(("RMT_EVENT_CONSUMER_OVERCLAIM", value));
    let mut value = baseline.clone(); value.payload_version = "2".into(); cases.push(("RMT_EVENT_SCHEMA_VERSION_DRIFT", value));
    assert_eq!(cases.len(), 10);
    for (expected, observed) in cases { assert_eq!(evaluate_event(&descriptor, &observed), Ok(vec![expected]), "{expected}"); }
}

fn s1_cases() -> Vec<(&'static str, EventS1Observation, Option<DurableOccurrence>)> {
    let id = "settlement:req-1".to_string();
    vec![
        ("RMT_S1_AFTER_OUTBOX_BEFORE_PUBLISH_FAILURE", EventS1Observation::AfterOutboxBeforePublishFailure { occurrence_id: id.clone(), transaction_committed: true, state_preserved: true, outbox_occurrence_present: true, publication_attempted: false, publication_attempt_id: None }, Some(DurableOccurrence { occurrence_id: id.clone(), persistence_checkpoint: "durable-outbox-append".into(), publication_attempt_id: "".into(), acknowledgement_state: "unknown".into(), delivery_observation: "not-observed".into(), consumption_observation: "not-observed".into() })),
        ("RMT_S1_SEND_FAILURE", EventS1Observation::SendFailure { occurrence_id: id.clone(), transaction_committed: true, state_preserved: true, outbox_occurrence_present: true, publication_attempted: true, publication_succeeded: false, publication_attempt_id: "publish:req-1:1".into(), retry_occurrence_id: id.clone(), durable_rollback: false }, Some(DurableOccurrence { occurrence_id: id.clone(), persistence_checkpoint: "durable-outbox-append".into(), publication_attempt_id: "publish:req-1:1".into(), acknowledgement_state: "failed".into(), delivery_observation: "not-observed".into(), consumption_observation: "not-observed".into() })),
        ("RMT_S1_ACKNOWLEDGEMENT_AMBIGUOUS", EventS1Observation::SuccessAckTimeout { occurrence_id: id.clone(), transaction_committed: true, state_preserved: true, publication_attempted: true, publication_succeeded: true, acknowledgement_ambiguous: true, retry_occurrence_id: id.clone(), reconciliation: "idempotent-retry".into() }, None),
        ("RMT_S1_DUPLICATE_REORDERED_DELIVERY", EventS1Observation::DuplicateReorderedDelivery { occurrence_id: id.clone(), delivery_trace: vec!["delivery:2".into(), "delivery:1".into(), "delivery:2".into()], consumer_effect_count: 1, idempotent_consume: true, history_rewritten: false }, Some(DurableOccurrence { occurrence_id: id.clone(), persistence_checkpoint: "durable-outbox-append".into(), publication_attempt_id: "publish:req-1:1".into(), acknowledgement_state: "acknowledged".into(), delivery_observation: "at-least-once-observed".into(), consumption_observation: "accepted".into() })),
        ("RMT_S1_POISON_OCCURRENCE", EventS1Observation::PoisonOccurrence { occurrence_id: id.clone(), transaction_committed: true, outbox_occurrence_present: true, poison_kind: "unconsumable".into(), handling: "quarantine".into(), durable_history_preserved: true }, Some(DurableOccurrence { occurrence_id: id.clone(), persistence_checkpoint: "durable-outbox-append".into(), publication_attempt_id: "publish:req-1:1".into(), acknowledgement_state: "acknowledged".into(), delivery_observation: "at-least-once-observed".into(), consumption_observation: "rejected".into() })),
        ("RMT_S1_RECOVERY_REPLAY_MISMATCH", EventS1Observation::RecoveryReplay { occurrence_id: id.clone(), fresh_process_restart: true, outbox_recovered: true, prior_occurrence_id: id.clone(), recovered_occurrence_id: id.clone(), prior_outcome: "committed".into(), recovered_outcome: "committed".into() }, None),
        ("RMT_S1_FUTURE_VERSION", EventS1Observation::FutureVersion { occurrence_id: id.clone(), occurrence_schema_version: 2, supported_schema_version: 1, decode_status: "rejected".into(), closed_decode: true }, None),
        ("RMT_S1_OCCURRENCE_REUSE", EventS1Observation::OccurrenceReuse { occurrence_id: id.clone(), existing_fact_fingerprint: "settlement-created:amount=10".into(), distinct_fact_fingerprint: "settlement-created:amount=11".into(), reused_occurrence_id: id.clone(), reuse_rejected: true }, None),
        ("RMT_S1_NON_IDEMPOTENT_RETRY", EventS1Observation::NonIdempotentRetry { occurrence_id: id.clone(), original_occurrence_id: id.clone(), retry_occurrence_id: "settlement:req-2".into(), consumer_effect_count: 2, retry_rejected: true }, None),
    ]
}

#[test]
fn kills_all_nine_s1_controls_with_required_residue() {
    let (descriptor, baseline) = baseline();
    let cases = s1_cases();
    assert_eq!(cases.len(), 9);
    for (expected, s1, handle) in cases {
        let mut observed = baseline.clone(); observed.s1_observation = Some(s1); if let Some(value) = handle { observed.durable_occurrence = value; }
        assert_eq!(evaluate_event(&descriptor, &observed), Ok(vec![expected]), "{expected}");
    }
}

#[test]
fn rejects_incoherent_s1_recovery_and_retry_residue() {
    let (descriptor, mut observed) = baseline();
    observed.s1_observation = Some(EventS1Observation::RecoveryReplay { occurrence_id: "settlement:req-1".into(), fresh_process_restart: true, outbox_recovered: true, prior_occurrence_id: "settlement:req-1".into(), recovered_occurrence_id: "settlement:req-2".into(), prior_outcome: "committed".into(), recovered_outcome: "committed".into() });
    assert_eq!(evaluate_event(&descriptor, &observed), Err("RMT_EVENT_S1_OBSERVATION_INVALID"));
    observed.s1_observation = Some(EventS1Observation::NonIdempotentRetry { occurrence_id: "settlement:req-1".into(), original_occurrence_id: "settlement:req-1".into(), retry_occurrence_id: "settlement:req-1".into(), consumer_effect_count: 1, retry_rejected: true });
    assert_eq!(evaluate_event(&descriptor, &observed), Err("RMT_EVENT_S1_OBSERVATION_INVALID"));
}
