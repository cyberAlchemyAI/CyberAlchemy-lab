import type {EventS1Observation, PastTenseEventObservation} from "../contracts/event-contracts.js";

const isRecord = (value: unknown): value is Record<string, unknown> => value !== null && typeof value === "object" && !Array.isArray(value);
const exactKeys = (value: Record<string, unknown>, expected: readonly string[]): boolean =>
  JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...expected].sort());
const strings = (value: unknown): value is string[] => Array.isArray(value) && value.every(item => typeof item === "string");

const commonS1Keys = ["schema_version", "scenario", "occurrence_id"] as const;
const scenarioKeys: Readonly<Record<EventS1Observation["scenario"], readonly string[]>> = Object.freeze({
  "after-outbox-before-publish-failure": [...commonS1Keys, "transaction_committed", "state_preserved", "outbox_occurrence_present", "publication_attempted", "publication_attempt_id"],
  "send-failure": [...commonS1Keys, "transaction_committed", "state_preserved", "outbox_occurrence_present", "publication_attempted", "publication_succeeded", "publication_attempt_id", "retry_occurrence_id", "durable_rollback"],
  "success-ack-timeout": [...commonS1Keys, "transaction_committed", "state_preserved", "publication_attempted", "publication_succeeded", "acknowledgement_ambiguous", "retry_occurrence_id", "reconciliation"],
  "duplicate-reordered-delivery": [...commonS1Keys, "delivery_trace", "consumer_effect_count", "idempotent_consume", "history_rewritten"],
  "poison-occurrence": [...commonS1Keys, "transaction_committed", "outbox_occurrence_present", "poison_kind", "handling", "durable_history_preserved"],
  "recovery-replay": [...commonS1Keys, "fresh_process_restart", "outbox_recovered", "prior_occurrence_id", "recovered_occurrence_id", "prior_outcome", "recovered_outcome"],
  "future-version": [...commonS1Keys, "occurrence_schema_version", "supported_schema_version", "decode_status", "closed_decode"],
  "occurrence-reuse": [...commonS1Keys, "existing_fact_fingerprint", "distinct_fact_fingerprint", "reused_occurrence_id", "reuse_rejected"],
  "non-idempotent-retry": [...commonS1Keys, "original_occurrence_id", "retry_occurrence_id", "consumer_effect_count", "retry_rejected"],
});

export const decodeEventS1Observation = (value: unknown): EventS1Observation | null => {
  if (value === null) return null;
  if (!isRecord(value) || value.schema_version !== "durable-occurrence-fault-observation/v1" || typeof value.scenario !== "string" || !(value.scenario in scenarioKeys) || !exactKeys(value, scenarioKeys[value.scenario as EventS1Observation["scenario"]]!)) throw new Error("RMT_EVENT_S1_DECODE_INVALID");
  for (const [key, item] of Object.entries(value)) {
    if (["schema_version", "scenario", "occurrence_id", "publication_attempt_id", "retry_occurrence_id", "reconciliation", "poison_kind", "handling", "prior_occurrence_id", "recovered_occurrence_id", "prior_outcome", "recovered_outcome", "decode_status", "existing_fact_fingerprint", "distinct_fact_fingerprint", "reused_occurrence_id", "original_occurrence_id"].includes(key)) {
      if (item !== null && typeof item !== "string") throw new Error("RMT_EVENT_S1_DECODE_INVALID");
    } else if (key === "delivery_trace") {
      if (!strings(item)) throw new Error("RMT_EVENT_S1_DECODE_INVALID");
    } else if (["consumer_effect_count", "occurrence_schema_version", "supported_schema_version"].includes(key)) {
      if (!Number.isInteger(item)) throw new Error("RMT_EVENT_S1_DECODE_INVALID");
    } else if (typeof item !== "boolean") throw new Error("RMT_EVENT_S1_DECODE_INVALID");
  }
  return value as unknown as EventS1Observation;
};

const observationKeys = ["event_name", "tense", "payload_contract_id", "payload_version", "payload_mutable", "occurrence_identity_contract_id", "occurrence_id", "occurrence_id_stable", "occurrence_id_reused", "durable_checkpoints", "publication_policy_id", "publication_after_commit", "consumer_contract_ids", "consumer_payload_checks", "distributed_exactly_once_claim", "durable_occurrence", "s1_observation"] as const;
const handleKeys = ["occurrence_id", "persistence_checkpoint", "publication_attempt_id", "acknowledgement_state", "delivery_observation", "consumption_observation"] as const;
const consumerKeys = ["consumer_contract_id", "payload_version", "accepted"] as const;

export const decodePastTenseEventObservation = (value: unknown): PastTenseEventObservation => {
  if (!isRecord(value) || !exactKeys(value, observationKeys) || !isRecord(value.durable_occurrence) || !exactKeys(value.durable_occurrence, handleKeys) || !strings(value.durable_checkpoints) || !strings(value.consumer_contract_ids) || !Array.isArray(value.consumer_payload_checks)) throw new Error("RMT_EVENT_OBSERVATION_DECODE_INVALID");
  const stringKeys = ["event_name", "tense", "payload_contract_id", "payload_version", "occurrence_identity_contract_id", "occurrence_id", "publication_policy_id"];
  const booleanKeys = ["payload_mutable", "occurrence_id_stable", "occurrence_id_reused", "publication_after_commit", "distributed_exactly_once_claim"];
  if (stringKeys.some(key => typeof value[key] !== "string") || booleanKeys.some(key => typeof value[key] !== "boolean")) throw new Error("RMT_EVENT_OBSERVATION_DECODE_INVALID");
  if (Object.values(value.durable_occurrence).some(item => typeof item !== "string")) throw new Error("RMT_EVENT_OBSERVATION_DECODE_INVALID");
  if (value.consumer_payload_checks.some(item => !isRecord(item) || !exactKeys(item, consumerKeys) || typeof item.consumer_contract_id !== "string" || typeof item.payload_version !== "string" || typeof item.accepted !== "boolean")) throw new Error("RMT_EVENT_OBSERVATION_DECODE_INVALID");
  return {...value, s1_observation: decodeEventS1Observation(value.s1_observation)} as unknown as PastTenseEventObservation;
};
