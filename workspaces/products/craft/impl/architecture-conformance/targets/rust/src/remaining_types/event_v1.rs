//! Candidate-local native Rust witness for WP-RMT-002 Event.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ConsumerCheck {
    pub consumer_contract_id: String,
    pub payload_version: String,
    pub accepted: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DurableOccurrence {
    pub occurrence_id: String,
    pub persistence_checkpoint: String,
    pub publication_attempt_id: String,
    pub acknowledgement_state: String,
    pub delivery_observation: String,
    pub consumption_observation: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EventS1Observation {
    AfterOutboxBeforePublishFailure { occurrence_id: String, transaction_committed: bool, state_preserved: bool, outbox_occurrence_present: bool, publication_attempted: bool, publication_attempt_id: Option<String> },
    SendFailure { occurrence_id: String, transaction_committed: bool, state_preserved: bool, outbox_occurrence_present: bool, publication_attempted: bool, publication_succeeded: bool, publication_attempt_id: String, retry_occurrence_id: String, durable_rollback: bool },
    SuccessAckTimeout { occurrence_id: String, transaction_committed: bool, state_preserved: bool, publication_attempted: bool, publication_succeeded: bool, acknowledgement_ambiguous: bool, retry_occurrence_id: String, reconciliation: String },
    DuplicateReorderedDelivery { occurrence_id: String, delivery_trace: Vec<String>, consumer_effect_count: u32, idempotent_consume: bool, history_rewritten: bool },
    PoisonOccurrence { occurrence_id: String, transaction_committed: bool, outbox_occurrence_present: bool, poison_kind: String, handling: String, durable_history_preserved: bool },
    RecoveryReplay { occurrence_id: String, fresh_process_restart: bool, outbox_recovered: bool, prior_occurrence_id: String, recovered_occurrence_id: String, prior_outcome: String, recovered_outcome: String },
    FutureVersion { occurrence_id: String, occurrence_schema_version: u32, supported_schema_version: u32, decode_status: String, closed_decode: bool },
    OccurrenceReuse { occurrence_id: String, existing_fact_fingerprint: String, distinct_fact_fingerprint: String, reused_occurrence_id: String, reuse_rejected: bool },
    NonIdempotentRetry { occurrence_id: String, original_occurrence_id: String, retry_occurrence_id: String, consumer_effect_count: u32, retry_rejected: bool },
}

impl EventS1Observation {
    pub fn occurrence_id(&self) -> &str {
        match self {
            Self::AfterOutboxBeforePublishFailure { occurrence_id, .. }
            | Self::SendFailure { occurrence_id, .. }
            | Self::SuccessAckTimeout { occurrence_id, .. }
            | Self::DuplicateReorderedDelivery { occurrence_id, .. }
            | Self::PoisonOccurrence { occurrence_id, .. }
            | Self::RecoveryReplay { occurrence_id, .. }
            | Self::FutureVersion { occurrence_id, .. }
            | Self::OccurrenceReuse { occurrence_id, .. }
            | Self::NonIdempotentRetry { occurrence_id, .. } => occurrence_id,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EventDescriptor {
    pub event_name: String,
    pub payload_version: String,
    pub persistence_checkpoint: String,
    pub consumer_contract_ids: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EventObservation {
    pub event_name: String,
    pub tense: String,
    pub payload_version: String,
    pub payload_mutable: bool,
    pub occurrence_id: String,
    pub occurrence_id_stable: bool,
    pub occurrence_id_reused: bool,
    pub durable_checkpoints: Vec<String>,
    pub publication_after_commit: bool,
    pub consumer_contract_ids: Vec<String>,
    pub consumer_payload_checks: Vec<ConsumerCheck>,
    pub distributed_exactly_once_claim: bool,
    pub durable_occurrence: DurableOccurrence,
    pub s1_observation: Option<EventS1Observation>,
}

pub fn evaluate_s1(observed_id: &str, s1: &EventS1Observation) -> Result<&'static str, &'static str> {
    if s1.occurrence_id() != observed_id { return Err("RMT_EVENT_S1_OBSERVATION_INVALID"); }
    let (valid, code) = match s1 {
        EventS1Observation::AfterOutboxBeforePublishFailure { transaction_committed, state_preserved, outbox_occurrence_present, publication_attempted, publication_attempt_id, .. } =>
            (*transaction_committed && *state_preserved && *outbox_occurrence_present && !*publication_attempted && publication_attempt_id.is_none(), "RMT_S1_AFTER_OUTBOX_BEFORE_PUBLISH_FAILURE"),
        EventS1Observation::SendFailure { transaction_committed, state_preserved, outbox_occurrence_present, publication_attempted, publication_succeeded, publication_attempt_id, retry_occurrence_id, durable_rollback, occurrence_id } =>
            (*transaction_committed && *state_preserved && *outbox_occurrence_present && *publication_attempted && !*publication_succeeded && !publication_attempt_id.is_empty() && retry_occurrence_id == occurrence_id && !*durable_rollback, "RMT_S1_SEND_FAILURE"),
        EventS1Observation::SuccessAckTimeout { transaction_committed, state_preserved, publication_attempted, publication_succeeded, acknowledgement_ambiguous, retry_occurrence_id, reconciliation, occurrence_id } =>
            (*transaction_committed && *state_preserved && *publication_attempted && *publication_succeeded && *acknowledgement_ambiguous && retry_occurrence_id == occurrence_id && matches!(reconciliation.as_str(), "idempotent-retry" | "same-occurrence-reconcile"), "RMT_S1_ACKNOWLEDGEMENT_AMBIGUOUS"),
        EventS1Observation::DuplicateReorderedDelivery { delivery_trace, consumer_effect_count, idempotent_consume, history_rewritten, .. } => {
            let mut unique = delivery_trace.clone(); unique.sort(); unique.dedup();
            let mut sorted = delivery_trace.clone(); sorted.sort();
            (delivery_trace.len() >= 2 && (unique.len() < delivery_trace.len() || sorted != *delivery_trace) && *consumer_effect_count == 1 && *idempotent_consume && !*history_rewritten, "RMT_S1_DUPLICATE_REORDERED_DELIVERY")
        },
        EventS1Observation::PoisonOccurrence { transaction_committed, outbox_occurrence_present, poison_kind, handling, durable_history_preserved, .. } =>
            (*transaction_committed && *outbox_occurrence_present && matches!(poison_kind.as_str(), "unpublishable" | "unconsumable") && matches!(handling.as_str(), "quarantine" | "forward") && *durable_history_preserved, "RMT_S1_POISON_OCCURRENCE"),
        EventS1Observation::RecoveryReplay { fresh_process_restart, outbox_recovered, prior_occurrence_id, recovered_occurrence_id, prior_outcome, recovered_outcome, occurrence_id } =>
            (*fresh_process_restart && *outbox_recovered && prior_occurrence_id == occurrence_id && recovered_occurrence_id == prior_occurrence_id && prior_outcome == "committed" && recovered_outcome == prior_outcome, "RMT_S1_RECOVERY_REPLAY_MISMATCH"),
        EventS1Observation::FutureVersion { occurrence_schema_version, supported_schema_version, decode_status, closed_decode, .. } =>
            (*occurrence_schema_version > *supported_schema_version && *supported_schema_version == 1 && decode_status == "rejected" && *closed_decode, "RMT_S1_FUTURE_VERSION"),
        EventS1Observation::OccurrenceReuse { existing_fact_fingerprint, distinct_fact_fingerprint, reused_occurrence_id, reuse_rejected, occurrence_id } =>
            (!existing_fact_fingerprint.is_empty() && !distinct_fact_fingerprint.is_empty() && existing_fact_fingerprint != distinct_fact_fingerprint && reused_occurrence_id == occurrence_id && *reuse_rejected, "RMT_S1_OCCURRENCE_REUSE"),
        EventS1Observation::NonIdempotentRetry { original_occurrence_id, retry_occurrence_id, consumer_effect_count, retry_rejected, occurrence_id } =>
            (original_occurrence_id == occurrence_id && (retry_occurrence_id != original_occurrence_id || *consumer_effect_count > 1) && *retry_rejected, "RMT_S1_NON_IDEMPOTENT_RETRY"),
    };
    if valid { Ok(code) } else { Err("RMT_EVENT_S1_OBSERVATION_INVALID") }
}

pub fn durable_handle_is_coherent(descriptor: &EventDescriptor, observed: &EventObservation) -> bool {
    let handle = &observed.durable_occurrence;
    if handle.occurrence_id != observed.occurrence_id || handle.persistence_checkpoint != descriptor.persistence_checkpoint { return false; }
    match &observed.s1_observation {
        None => !handle.publication_attempt_id.is_empty() && handle.acknowledgement_state == "unknown" && handle.delivery_observation == "at-least-once-observed" && handle.consumption_observation == "accepted",
        Some(EventS1Observation::AfterOutboxBeforePublishFailure { .. }) => handle.publication_attempt_id.is_empty() && handle.acknowledgement_state == "unknown" && handle.delivery_observation == "not-observed" && handle.consumption_observation == "not-observed",
        Some(EventS1Observation::SendFailure { publication_attempt_id, .. }) => handle.publication_attempt_id == *publication_attempt_id && handle.acknowledgement_state == "failed" && handle.delivery_observation == "not-observed" && handle.consumption_observation == "not-observed",
        Some(EventS1Observation::SuccessAckTimeout { .. }) => !handle.publication_attempt_id.is_empty() && handle.acknowledgement_state == "unknown",
        Some(EventS1Observation::DuplicateReorderedDelivery { .. }) => !handle.publication_attempt_id.is_empty() && handle.acknowledgement_state == "acknowledged" && handle.delivery_observation == "at-least-once-observed" && handle.consumption_observation == "accepted",
        Some(EventS1Observation::PoisonOccurrence { poison_kind, .. }) => poison_kind == "unconsumable" && !handle.publication_attempt_id.is_empty() && handle.acknowledgement_state == "acknowledged" && handle.delivery_observation == "at-least-once-observed" && handle.consumption_observation == "rejected",
        Some(_) => !handle.publication_attempt_id.is_empty() && handle.acknowledgement_state == "unknown" && handle.delivery_observation == "at-least-once-observed" && handle.consumption_observation == "accepted",
    }
}

pub fn evaluate_event(descriptor: &EventDescriptor, observed: &EventObservation) -> Result<Vec<&'static str>, &'static str> {
    if !durable_handle_is_coherent(descriptor, observed) { return Err("RMT_EVENT_DURABLE_HANDLE_INVALID"); }
    let mut findings = Vec::new();
    if observed.tense != "past" || !descriptor.event_name.ends_with("ed") || observed.event_name != descriptor.event_name { findings.push("RMT_EVENT_NON_PAST_TENSE"); }
    if observed.payload_mutable { findings.push("RMT_EVENT_MUTABLE_PAYLOAD"); }
    if observed.occurrence_id.is_empty() || !observed.occurrence_id_stable { findings.push("RMT_EVENT_UNSTABLE_OCCURRENCE_ID"); }
    if observed.occurrence_id_reused { findings.push("RMT_EVENT_REUSED_OCCURRENCE_ID"); }
    if observed.durable_checkpoints.is_empty() { findings.push("RMT_EVENT_CHECKPOINT_MISSING"); } else if observed.durable_checkpoints.len() != 1 { findings.push("RMT_EVENT_CHECKPOINT_DUPLICATE"); }
    if !observed.publication_after_commit { findings.push("RMT_EVENT_PUBLISH_BEFORE_COMMIT"); }
    if observed.distributed_exactly_once_claim { findings.push("RMT_EVENT_EXACTLY_ONCE_OVERCLAIM"); }
    let mut expected = descriptor.consumer_contract_ids.clone(); let mut actual = observed.consumer_contract_ids.clone(); expected.sort(); actual.sort();
    if expected != actual || observed.consumer_payload_checks.iter().any(|check| !descriptor.consumer_contract_ids.contains(&check.consumer_contract_id) || !check.accepted) { findings.push("RMT_EVENT_CONSUMER_OVERCLAIM"); }
    if observed.payload_version != descriptor.payload_version || observed.consumer_payload_checks.iter().any(|check| check.payload_version != descriptor.payload_version) { findings.push("RMT_EVENT_SCHEMA_VERSION_DRIFT"); }
    if let Some(s1) = &observed.s1_observation { findings.push(evaluate_s1(&observed.occurrence_id, s1)?); }
    Ok(findings)
}
