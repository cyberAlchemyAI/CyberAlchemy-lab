export type DurableOccurrenceObservation = Readonly<{
  occurrence_id: string;
  persistence_checkpoint: string;
  publication_attempt_id: string;
  acknowledgement_state: "unknown" | "acknowledged" | "failed";
  delivery_observation: "not-observed" | "at-least-once-observed";
  consumption_observation: "not-observed" | "accepted" | "rejected";
}>;

type EventS1Common<S extends string> = Readonly<{
  schema_version: "durable-occurrence-fault-observation/v1";
  scenario: S;
  occurrence_id: string;
}>;

export type EventS1Observation =
  | (EventS1Common<"after-outbox-before-publish-failure"> & Readonly<{
      transaction_committed: true;
      state_preserved: true;
      outbox_occurrence_present: true;
      publication_attempted: false;
      publication_attempt_id: null;
    }>)
  | (EventS1Common<"send-failure"> & Readonly<{
      transaction_committed: true;
      state_preserved: true;
      outbox_occurrence_present: true;
      publication_attempted: true;
      publication_succeeded: false;
      publication_attempt_id: string;
      retry_occurrence_id: string;
      durable_rollback: false;
    }>)
  | (EventS1Common<"success-ack-timeout"> & Readonly<{
      transaction_committed: true;
      state_preserved: true;
      publication_attempted: true;
      publication_succeeded: true;
      acknowledgement_ambiguous: true;
      retry_occurrence_id: string;
      reconciliation: "idempotent-retry" | "same-occurrence-reconcile";
    }>)
  | (EventS1Common<"duplicate-reordered-delivery"> & Readonly<{
      delivery_trace: readonly string[];
      consumer_effect_count: 1;
      idempotent_consume: true;
      history_rewritten: false;
    }>)
  | (EventS1Common<"poison-occurrence"> & Readonly<{
      transaction_committed: true;
      outbox_occurrence_present: true;
      poison_kind: "unpublishable" | "unconsumable";
      handling: "quarantine" | "forward";
      durable_history_preserved: true;
    }>)
  | (EventS1Common<"recovery-replay"> & Readonly<{
      fresh_process_restart: true;
      outbox_recovered: true;
      prior_occurrence_id: string;
      recovered_occurrence_id: string;
      prior_outcome: "committed";
      recovered_outcome: "committed" | "missing" | "changed";
    }>)
  | (EventS1Common<"future-version"> & Readonly<{
      occurrence_schema_version: number;
      supported_schema_version: 1;
      decode_status: "rejected" | "accepted";
      closed_decode: boolean;
    }>)
  | (EventS1Common<"occurrence-reuse"> & Readonly<{
      existing_fact_fingerprint: string;
      distinct_fact_fingerprint: string;
      reused_occurrence_id: string;
      reuse_rejected: boolean;
    }>)
  | (EventS1Common<"non-idempotent-retry"> & Readonly<{
      original_occurrence_id: string;
      retry_occurrence_id: string;
      consumer_effect_count: number;
      retry_rejected: boolean;
    }>);

export type PastTenseEventDescriptor = Readonly<{
  schema_version: "domainspec.past-tense-event/v1";
  descriptor_id: string;
  semantic_plan_epoch_id: "WP-RMT-002/S1/2026-08-16";
  semantic_contract_digest: "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7";
  event_name: string;
  tense: "past";
  payload_contract_id: string;
  payload_version: string;
  payload_immutable: true;
  occurrence_identity_contract_id: string;
  persistence_checkpoint: "durable-outbox-append";
  publication_policy_id: string;
  consumer_contract_ids: readonly string[];
  distributed_exactly_once_claim: false;
  durable_handle: "durable-occurrence/v1";
  admission_status: "candidate";
  authority_effect: "none";
}>;

export type PastTenseEventObservation = Readonly<{
  event_name: string;
  tense: "past" | "present";
  payload_contract_id: string;
  payload_version: string;
  payload_mutable: boolean;
  occurrence_identity_contract_id: string;
  occurrence_id: string;
  occurrence_id_stable: boolean;
  occurrence_id_reused: boolean;
  durable_checkpoints: readonly string[];
  publication_policy_id: string;
  publication_after_commit: boolean;
  consumer_contract_ids: readonly string[];
  consumer_payload_checks: readonly Readonly<{
    consumer_contract_id: string;
    payload_version: string;
    accepted: boolean;
  }>[];
  distributed_exactly_once_claim: boolean;
  durable_occurrence: DurableOccurrenceObservation;
  s1_observation: EventS1Observation | null;
}>;

export type EventRelationAssertion = Readonly<{
  contract_id: "event/emitted-by-operation" | "event/consumed-by-element";
  mode: "blueprint-only" | "materialized";
  owner_evidence_sha256: string;
  current_owner_evidence_sha256: string;
  source_type: string;
  target_type: string;
  exact_assertion_id: string | null;
}>;

export type EventFindingCode =
  | "RMT_EVENT_NON_PAST_TENSE"
  | "RMT_EVENT_MUTABLE_PAYLOAD"
  | "RMT_EVENT_UNSTABLE_OCCURRENCE_ID"
  | "RMT_EVENT_REUSED_OCCURRENCE_ID"
  | "RMT_EVENT_CHECKPOINT_MISSING"
  | "RMT_EVENT_CHECKPOINT_DUPLICATE"
  | "RMT_EVENT_PUBLISH_BEFORE_COMMIT"
  | "RMT_EVENT_EXACTLY_ONCE_OVERCLAIM"
  | "RMT_EVENT_CONSUMER_OVERCLAIM"
  | "RMT_EVENT_SCHEMA_VERSION_DRIFT"
  | "RMT_S1_AFTER_OUTBOX_BEFORE_PUBLISH_FAILURE"
  | "RMT_S1_SEND_FAILURE"
  | "RMT_S1_ACKNOWLEDGEMENT_AMBIGUOUS"
  | "RMT_S1_DUPLICATE_REORDERED_DELIVERY"
  | "RMT_S1_POISON_OCCURRENCE"
  | "RMT_S1_RECOVERY_REPLAY_MISMATCH"
  | "RMT_S1_FUTURE_VERSION"
  | "RMT_S1_OCCURRENCE_REUSE"
  | "RMT_S1_NON_IDEMPOTENT_RETRY"
  | "RMT_RELATION_OWNER_EVIDENCE_STALE"
  | "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"
  | "RMT_RELATION_TARGET_ENDPOINT_MISMATCH"
  | "RMT_RELATION_ASSERTION_REQUIRED";

export type EventEvaluation = Readonly<{
  schema_version: "domainspec.past-tense-event-evaluation/v1";
  descriptor_id: string;
  verdict: "pass" | "reject";
  findings: readonly Readonly<{code: EventFindingCode; expected: unknown; observed: unknown}>[];
  authority_effect: "none";
}>;
