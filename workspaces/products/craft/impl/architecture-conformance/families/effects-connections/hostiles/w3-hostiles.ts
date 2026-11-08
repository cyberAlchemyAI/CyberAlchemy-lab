import type {
  EventObservation,
  InterfaceObservation,
  MappingObservation,
  OperationObservation,
  W3Descriptor,
  W3FindingCode,
  W3Observation,
} from "../contracts/w3-contracts.js";

export type W3HostileCase = Readonly<{
  mutant_id: string;
  observation: W3Observation;
  expected_codes: readonly W3FindingCode[];
}>;

export const buildW3Hostiles = (
  descriptor: W3Descriptor,
  observation: W3Observation,
): readonly W3HostileCase[] => {
  if (descriptor.kind === "Mapping" && observation.kind === "Mapping") {
    const base = observation as MappingObservation;
    return Object.freeze([
      {mutant_id: "mapping-endpoints-reversed", observation: {...base, source_contract_id: base.target_contract_id, target_contract_id: base.source_contract_id}, expected_codes: ["ARCH_MAPPING_ENDPOINT_DRIFT"]},
      {mutant_id: "mapping-correspondence-omitted", observation: {...base, observed_correspondence: base.observed_correspondence.slice(0, -1)}, expected_codes: ["ARCH_MAPPING_CORRESPONDENCE_DRIFT"]},
      {mutant_id: "mapping-direction-drift", observation: {...base, direction: base.direction === "forward" ? "reverse" : "forward"}, expected_codes: ["ARCH_MAPPING_DIRECTION_DRIFT"]},
      {mutant_id: "mapping-totality-drift", observation: {...base, totality: base.totality === "total" ? "partial-fallible" : "total"}, expected_codes: ["ARCH_MAPPING_TOTALITY_DRIFT"]},
      {mutant_id: "mapping-undeclared-effect", observation: {...base, effects: ["network:undeclared"]}, expected_codes: ["ARCH_MAPPING_EFFECT_UNDECLARED"]},
    ]);
  }
  if (descriptor.kind === "Interface" && observation.kind === "Interface") {
    const base = observation as InterfaceObservation;
    return Object.freeze([
      {mutant_id: "interface-version-drift", observation: {...base, version: "2"}, expected_codes: ["ARCH_INTERFACE_CONTRACT_DRIFT"]},
      {mutant_id: "interface-extra-exposure", observation: {...base, exposed_bindings: [...base.exposed_bindings, {binding_id: "adminDelete", kind: "Operation"}]}, expected_codes: ["ARCH_INTERFACE_EXPOSURE_DRIFT"]},
      {mutant_id: "interface-compatibility-inflation", observation: {...base, compatibility_checks: base.compatibility_checks.map((item) => ({...item, accepted: true}))}, expected_codes: ["ARCH_INTERFACE_COMPATIBILITY_DRIFT"]},
    ]);
  }
  if (descriptor.kind === "Event" && observation.kind === "Event") {
    const base = observation as EventObservation;
    return Object.freeze([
      {mutant_id: "event-present-tense", observation: {...base, tense: "present"}, expected_codes: ["ARCH_EVENT_NOT_PAST_FACT"]},
      {mutant_id: "event-ambiguous-checkpoint", observation: {...base, durable_checkpoints: [descriptor.fact_checkpoint, descriptor.fact_checkpoint]}, expected_codes: ["ARCH_EVENT_CHECKPOINT_INVALID"]},
      {mutant_id: "event-payload-version-drift", observation: {...base, payload_version: "2"}, expected_codes: ["ARCH_EVENT_PAYLOAD_DRIFT", "ARCH_EVENT_CONSUMER_VERSION_DRIFT"]},
      {mutant_id: "event-duplicate-occurrence", observation: {...base, duplicate_occurrence_observed: true}, expected_codes: ["ARCH_EVENT_OCCURRENCE_DUPLICATE"]},
      {mutant_id: "event-duplicate-publication-attempt", observation: {...base, publication_attempt_ids: ["attempt-1", "attempt-1"]}, expected_codes: ["ARCH_EVENT_PUBLICATION_ATTEMPT_DUPLICATE"]},
      {mutant_id: "event-publication-before-durability", observation: {...base, lifecycle_trace: ["constructed", "publish-attempted", "durable-fact"]}, expected_codes: ["ARCH_EVENT_PUBLICATION_ORDER_DRIFT"]},
      {mutant_id: "event-consumer-version-rejected", observation: {...base, consumer_payload_checks: base.consumer_payload_checks.map((item) => ({...item, accepted: false}))}, expected_codes: ["ARCH_EVENT_CONSUMER_VERSION_DRIFT"]},
      {mutant_id: "event-exactly-once-inflation", observation: {...base, distributed_exactly_once_claim: true}, expected_codes: ["ARCH_EVENT_EXACTLY_ONCE_INFLATION"]},
    ]);
  }
  if (descriptor.kind === "Operation" && observation.kind === "Operation") {
    const base = observation as OperationObservation;
    return Object.freeze([
      {mutant_id: "operation-read-omitted", observation: {...base, reads: []}, expected_codes: ["ARCH_OPERATION_EFFECT_INCOMPLETE"]},
      {mutant_id: "operation-effect-undeclared", observation: {...base, external_effects: [...base.external_effects, "network:undeclared"]}, expected_codes: ["ARCH_OPERATION_EFFECT_UNDECLARED"]},
      {mutant_id: "operation-atomic-partial", observation: {...base, writes: base.writes.map((item) => ({...item, state: "partial" as const}))}, expected_codes: ["ARCH_OPERATION_ATOMICITY_DRIFT"]},
      {mutant_id: "operation-order-inverted", observation: {...base, trace: [...base.trace].reverse()}, expected_codes: ["ARCH_OPERATION_ORDER_DRIFT"]},
      {mutant_id: "operation-guard-ignored", observation: {...base, guard_results: base.guard_results.map((item) => ({...item, decision_used: false}))}, expected_codes: ["ARCH_OPERATION_GUARD_INVALID"]},
      {mutant_id: "operation-event-omitted", observation: {...base, emitted_events: []}, expected_codes: ["ARCH_OPERATION_EVENT_DRIFT"]},
      {mutant_id: "operation-outcome-drift", observation: {...base, outcome_id: "settlement-unknown"}, expected_codes: ["ARCH_OPERATION_OUTCOME_DRIFT", "ARCH_OPERATION_FAILURE_DRIFT"]},
      {mutant_id: "operation-continuation-boundary-drift", observation: {...base, continuation_boundary: "declared-background-handoff"}, expected_codes: ["ARCH_OPERATION_CONTINUATION_DRIFT"]},
      {mutant_id: "operation-continuation-open", observation: {...base, continuation_closed: false}, expected_codes: ["ARCH_OPERATION_CONTINUATION_OPEN"]},
    ]);
  }
  return Object.freeze([]);
};
