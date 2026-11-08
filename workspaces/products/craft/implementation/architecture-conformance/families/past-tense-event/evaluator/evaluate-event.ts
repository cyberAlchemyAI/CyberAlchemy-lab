import type {
  EventEvaluation,
  EventFindingCode,
  EventRelationAssertion,
  EventS1Observation,
  PastTenseEventDescriptor,
  PastTenseEventObservation,
} from "../contracts/event-contracts.js";

type Finding = EventEvaluation["findings"][number];

const finding = (code: EventFindingCode, expected: unknown, observed: unknown): Finding => ({code, expected, observed});
const failS1 = (): never => { throw new Error("RMT_EVENT_S1_OBSERVATION_INVALID"); };
const sameSet = (a: readonly string[], b: readonly string[]) =>
  a.length === new Set(a).size && b.length === new Set(b).size &&
  JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
const finish = (descriptor_id: string, findings: Finding[]): EventEvaluation => Object.freeze({
  schema_version: "domainspec.past-tense-event-evaluation/v1",
  descriptor_id,
  verdict: findings.length ? "reject" : "pass",
  findings: Object.freeze(findings),
  authority_effect: "none",
});

const classifyS1 = (observed: PastTenseEventObservation, s1: EventS1Observation): EventFindingCode => {
  if (s1.schema_version !== "durable-occurrence-fault-observation/v1" || s1.occurrence_id !== observed.occurrence_id) failS1();
  switch (s1.scenario) {
    case "after-outbox-before-publish-failure":
      if (!(s1.transaction_committed && s1.state_preserved && s1.outbox_occurrence_present && !s1.publication_attempted && s1.publication_attempt_id === null)) failS1();
      return "RMT_S1_AFTER_OUTBOX_BEFORE_PUBLISH_FAILURE";
    case "send-failure":
      if (!(s1.transaction_committed && s1.state_preserved && s1.outbox_occurrence_present && s1.publication_attempted && !s1.publication_succeeded && s1.publication_attempt_id.length > 0 && s1.retry_occurrence_id === s1.occurrence_id && !s1.durable_rollback)) failS1();
      return "RMT_S1_SEND_FAILURE";
    case "success-ack-timeout":
      if (!(s1.transaction_committed && s1.state_preserved && s1.publication_attempted && s1.publication_succeeded && s1.acknowledgement_ambiguous && s1.retry_occurrence_id === s1.occurrence_id && ["idempotent-retry", "same-occurrence-reconcile"].includes(s1.reconciliation))) failS1();
      return "RMT_S1_ACKNOWLEDGEMENT_AMBIGUOUS";
    case "duplicate-reordered-delivery": {
      const duplicate = new Set(s1.delivery_trace).size < s1.delivery_trace.length;
      const reordered = JSON.stringify(s1.delivery_trace) !== JSON.stringify([...s1.delivery_trace].sort());
      if (!(s1.delivery_trace.length >= 2 && (duplicate || reordered) && s1.consumer_effect_count === 1 && s1.idempotent_consume && !s1.history_rewritten)) failS1();
      return "RMT_S1_DUPLICATE_REORDERED_DELIVERY";
    }
    case "poison-occurrence":
      if (!(s1.transaction_committed && s1.outbox_occurrence_present && ["unpublishable", "unconsumable"].includes(s1.poison_kind) && ["quarantine", "forward"].includes(s1.handling) && s1.durable_history_preserved)) failS1();
      return "RMT_S1_POISON_OCCURRENCE";
    case "recovery-replay":
      if (!(s1.fresh_process_restart && s1.outbox_recovered && s1.prior_occurrence_id === s1.occurrence_id && s1.recovered_occurrence_id === s1.prior_occurrence_id && s1.prior_outcome === "committed" && s1.recovered_outcome === s1.prior_outcome)) failS1();
      return "RMT_S1_RECOVERY_REPLAY_MISMATCH";
    case "future-version":
      if (!(Number.isInteger(s1.occurrence_schema_version) && s1.occurrence_schema_version > s1.supported_schema_version && s1.supported_schema_version === 1 && s1.decode_status === "rejected" && s1.closed_decode)) failS1();
      return "RMT_S1_FUTURE_VERSION";
    case "occurrence-reuse":
      if (!(s1.existing_fact_fingerprint.length > 0 && s1.distinct_fact_fingerprint.length > 0 && s1.existing_fact_fingerprint !== s1.distinct_fact_fingerprint && s1.reused_occurrence_id === s1.occurrence_id && s1.reuse_rejected)) failS1();
      return "RMT_S1_OCCURRENCE_REUSE";
    case "non-idempotent-retry":
      if (!(s1.original_occurrence_id === s1.occurrence_id && (s1.retry_occurrence_id !== s1.original_occurrence_id || s1.consumer_effect_count > 1) && s1.retry_rejected)) failS1();
      return "RMT_S1_NON_IDEMPOTENT_RETRY";
  }
};

const durableHandleIsCoherent = (descriptor: PastTenseEventDescriptor, observed: PastTenseEventObservation): boolean => {
  const handle = observed.durable_occurrence;
  if (handle.occurrence_id !== observed.occurrence_id || handle.persistence_checkpoint !== descriptor.persistence_checkpoint) return false;
  const s1 = observed.s1_observation;
  if (s1 === null) return handle.publication_attempt_id.length > 0 && handle.acknowledgement_state === "unknown" && handle.delivery_observation === "at-least-once-observed" && handle.consumption_observation === "accepted";
  switch (s1.scenario) {
    case "after-outbox-before-publish-failure":
      return handle.publication_attempt_id === "" && handle.acknowledgement_state === "unknown" && handle.delivery_observation === "not-observed" && handle.consumption_observation === "not-observed";
    case "send-failure":
      return handle.publication_attempt_id === s1.publication_attempt_id && handle.acknowledgement_state === "failed" && handle.delivery_observation === "not-observed" && handle.consumption_observation === "not-observed";
    case "success-ack-timeout":
      return handle.publication_attempt_id.length > 0 && handle.acknowledgement_state === "unknown";
    case "duplicate-reordered-delivery":
      return handle.publication_attempt_id.length > 0 && handle.acknowledgement_state === "acknowledged" && handle.delivery_observation === "at-least-once-observed" && handle.consumption_observation === "accepted";
    case "poison-occurrence":
      return s1.poison_kind === "unconsumable" && handle.publication_attempt_id.length > 0 && handle.acknowledgement_state === "acknowledged" && handle.delivery_observation === "at-least-once-observed" && handle.consumption_observation === "rejected";
    default:
      return handle.publication_attempt_id.length > 0 && handle.acknowledgement_state === "unknown" && handle.delivery_observation === "at-least-once-observed" && handle.consumption_observation === "accepted";
  }
};

export const evaluatePastTenseEvent = (descriptor: PastTenseEventDescriptor, observed: PastTenseEventObservation): EventEvaluation => {
  const findings: Finding[] = [];
  if (observed.tense !== "past" || !descriptor.event_name.endsWith("ed") || observed.event_name !== descriptor.event_name) findings.push(finding("RMT_EVENT_NON_PAST_TENSE", descriptor.event_name, observed.event_name));
  if (observed.payload_mutable) findings.push(finding("RMT_EVENT_MUTABLE_PAYLOAD", false, true));
  if (!observed.occurrence_id || !observed.occurrence_id_stable) findings.push(finding("RMT_EVENT_UNSTABLE_OCCURRENCE_ID", "stable non-empty", {id: observed.occurrence_id, stable: observed.occurrence_id_stable}));
  if (observed.occurrence_id_reused) findings.push(finding("RMT_EVENT_REUSED_OCCURRENCE_ID", false, true));
  if (observed.durable_checkpoints.length === 0) findings.push(finding("RMT_EVENT_CHECKPOINT_MISSING", [descriptor.persistence_checkpoint], []));
  else if (observed.durable_checkpoints.length !== 1) findings.push(finding("RMT_EVENT_CHECKPOINT_DUPLICATE", [descriptor.persistence_checkpoint], observed.durable_checkpoints));
  if (!observed.publication_after_commit) findings.push(finding("RMT_EVENT_PUBLISH_BEFORE_COMMIT", true, false));
  if (observed.distributed_exactly_once_claim) findings.push(finding("RMT_EVENT_EXACTLY_ONCE_OVERCLAIM", false, true));
  if (!sameSet(descriptor.consumer_contract_ids, observed.consumer_contract_ids) || observed.consumer_payload_checks.some(({consumer_contract_id, accepted}) => !descriptor.consumer_contract_ids.includes(consumer_contract_id) || !accepted)) findings.push(finding("RMT_EVENT_CONSUMER_OVERCLAIM", descriptor.consumer_contract_ids, observed.consumer_contract_ids));
  if (observed.payload_version !== descriptor.payload_version || observed.consumer_payload_checks.some(({payload_version}) => payload_version !== descriptor.payload_version)) findings.push(finding("RMT_EVENT_SCHEMA_VERSION_DRIFT", descriptor.payload_version, {payload: observed.payload_version, consumers: observed.consumer_payload_checks}));
  if (!durableHandleIsCoherent(descriptor, observed)) throw new Error("RMT_EVENT_DURABLE_HANDLE_INVALID");
  if (observed.s1_observation !== null) findings.push(finding(classifyS1(observed, observed.s1_observation), "S1-required durable residue", observed.s1_observation));
  return finish(descriptor.descriptor_id, findings);
};

const endpoints = (id: EventRelationAssertion["contract_id"]) => id === "event/emitted-by-operation"
  ? {source: ["architecture.OperationImplementation"], target: ["architecture.EventImplementation"]}
  : {source: ["architecture.ArchitectureElement"], target: ["architecture.EventImplementation"]};

export const evaluateEventRelation = (assertion: EventRelationAssertion): EventEvaluation => {
  const findings: Finding[] = [];
  const allowed = endpoints(assertion.contract_id);
  if (assertion.owner_evidence_sha256 !== assertion.current_owner_evidence_sha256) findings.push(finding("RMT_RELATION_OWNER_EVIDENCE_STALE", assertion.current_owner_evidence_sha256, assertion.owner_evidence_sha256));
  if (!allowed.source.includes(assertion.source_type)) findings.push(finding("RMT_RELATION_SOURCE_ENDPOINT_MISMATCH", allowed.source, assertion.source_type));
  if (!allowed.target.includes(assertion.target_type)) findings.push(finding("RMT_RELATION_TARGET_ENDPOINT_MISMATCH", allowed.target, assertion.target_type));
  if (assertion.mode === "materialized" && !assertion.exact_assertion_id) findings.push(finding("RMT_RELATION_ASSERTION_REQUIRED", "non-empty exact assertion id", assertion.exact_assertion_id));
  return finish(assertion.contract_id, findings);
};
