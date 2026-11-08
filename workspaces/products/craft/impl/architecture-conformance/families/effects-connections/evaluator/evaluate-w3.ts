import type {
  EventDescriptor,
  EventObservation,
  InterfaceDescriptor,
  InterfaceObservation,
  MappingDescriptor,
  MappingObservation,
  OperationDescriptor,
  OperationObservation,
  W3Descriptor,
  W3Evaluation,
  W3FindingCode,
  W3Observation,
} from "../contracts/w3-contracts.js";

type Finding = W3Evaluation["findings"][number];

const SHA256 = /^[a-f0-9]{64}$/;
const same = (left: unknown, right: unknown): boolean => JSON.stringify(left) === JSON.stringify(right);
const finding = (code: W3FindingCode, expected: unknown, observed: unknown): Finding => ({code, expected, observed});
const sameStringSet = (left: readonly string[], right: readonly string[]): boolean =>
  left.length === new Set(left).size
    && right.length === new Set(right).size
    && same([...left].sort(), [...right].sort());
const sameObjectSet = (left: readonly unknown[], right: readonly unknown[]): boolean =>
  sameStringSet(left.map((item) => JSON.stringify(item)), right.map((item) => JSON.stringify(item)));

const validateBinding = (descriptor: W3Descriptor): Finding[] => {
  const refs = Object.values(descriptor.binding).filter((value): value is {id: string; sha256: string} =>
    typeof value === "object" && value !== null && "id" in value && "sha256" in value,
  );
  return descriptor.binding.protocol_id === "domainspec.w3-descriptor-binding/v1"
    && refs.length === 6
    && refs.every((ref) => ref.id.length > 0 && SHA256.test(ref.sha256))
    ? []
    : [finding("ARCH_W3_BINDING_INVALID", "six exact content-addressed refs", descriptor.binding)];
};

const evaluateMapping = (descriptor: MappingDescriptor, observed: MappingObservation): Finding[] => {
  const findings: Finding[] = [];
  if (descriptor.source_contract_id !== observed.source_contract_id || descriptor.target_contract_id !== observed.target_contract_id) {
    findings.push(finding("ARCH_MAPPING_ENDPOINT_DRIFT", [descriptor.source_contract_id, descriptor.target_contract_id], [observed.source_contract_id, observed.target_contract_id]));
  }
  if (descriptor.direction !== observed.direction) {
    findings.push(finding("ARCH_MAPPING_DIRECTION_DRIFT", descriptor.direction, observed.direction));
  }
  if (!sameObjectSet(descriptor.correspondence, observed.observed_correspondence)) {
    findings.push(finding("ARCH_MAPPING_CORRESPONDENCE_DRIFT", descriptor.correspondence, observed.observed_correspondence));
  }
  if (descriptor.totality !== observed.totality) {
    findings.push(finding("ARCH_MAPPING_TOTALITY_DRIFT", descriptor.totality, observed.totality));
  }
  if (descriptor.failure_contract_id !== observed.failure_contract_id || (descriptor.totality === "total" && observed.failure_observed)) {
    findings.push(finding("ARCH_MAPPING_FAILURE_DRIFT", descriptor.failure_contract_id, {failure_contract_id: observed.failure_contract_id, failure_observed: observed.failure_observed}));
  }
  if (descriptor.totality === "partial-fallible" && (!descriptor.failure_contract_id || !observed.failure_observed)) {
    findings.push(finding("ARCH_MAPPING_FAILURE_HIDDEN", descriptor.failure_contract_id, observed.failure_observed));
  }
  if (descriptor.effect_policy !== observed.effect_policy) {
    findings.push(finding("ARCH_MAPPING_EFFECT_POLICY_DRIFT", descriptor.effect_policy, observed.effect_policy));
  }
  if (descriptor.effect_policy === "none" && observed.effects.length > 0) {
    findings.push(finding("ARCH_MAPPING_EFFECT_UNDECLARED", [], observed.effects));
  }
  if (descriptor.direction === "bidirectional" && (!descriptor.reverse_contract_id || !observed.reverse_contract_complete)) {
    findings.push(finding("ARCH_MAPPING_REVERSE_INCOMPLETE", descriptor.reverse_contract_id, observed.reverse_contract_complete));
  }
  return findings;
};

const evaluateInterface = (descriptor: InterfaceDescriptor, observed: InterfaceObservation): Finding[] => {
  const findings: Finding[] = [];
  if (descriptor.boundary_kind !== observed.boundary_kind || descriptor.contract_id !== observed.contract_id || descriptor.exact_version !== observed.version || descriptor.compatibility_policy_id !== observed.compatibility_policy_id) {
    findings.push(finding("ARCH_INTERFACE_CONTRACT_DRIFT", [descriptor.boundary_kind, descriptor.contract_id, descriptor.exact_version, descriptor.compatibility_policy_id], [observed.boundary_kind, observed.contract_id, observed.version, observed.compatibility_policy_id]));
  }
  if (!sameObjectSet(descriptor.exposed_bindings, observed.exposed_bindings)) {
    findings.push(finding("ARCH_INTERFACE_EXPOSURE_DRIFT", descriptor.exposed_bindings, observed.exposed_bindings));
  }
  const compatibilityValid = observed.compatibility_checks.length >= 2
    && observed.compatibility_checks.some(({requested_version, accepted}) => requested_version === descriptor.exact_version && accepted)
    && observed.compatibility_checks.every(({requested_version, accepted}) => {
      const expected = descriptor.compatibility_policy_id === "exact-major/v1"
        ? requested_version.split(".")[0] === descriptor.exact_version.split(".")[0]
        : requested_version === descriptor.exact_version;
      return accepted === expected;
    })
    && observed.compatibility_checks.some(({requested_version, accepted}) => requested_version.split(".")[0] !== descriptor.exact_version.split(".")[0] && !accepted);
  if (!compatibilityValid) {
    findings.push(finding("ARCH_INTERFACE_COMPATIBILITY_DRIFT", {version: descriptor.exact_version, policy: descriptor.compatibility_policy_id}, observed.compatibility_checks));
  }
  return findings;
};

const evaluateEvent = (descriptor: EventDescriptor, observed: EventObservation): Finding[] => {
  const findings: Finding[] = [];
  if (observed.tense !== "past") findings.push(finding("ARCH_EVENT_NOT_PAST_FACT", "past", observed.tense));
  if (observed.durable_checkpoints.length !== 1 || observed.durable_checkpoints[0] !== descriptor.fact_checkpoint) {
    findings.push(finding("ARCH_EVENT_CHECKPOINT_INVALID", [descriptor.fact_checkpoint], observed.durable_checkpoints));
  }
  if (descriptor.payload_contract_id !== observed.payload_contract_id || descriptor.payload_version !== observed.payload_version
      || descriptor.occurrence_identity_contract_id !== observed.occurrence_identity_contract_id || observed.occurrence_id.length === 0) {
    findings.push(finding("ARCH_EVENT_PAYLOAD_DRIFT", [descriptor.payload_contract_id, descriptor.payload_version, descriptor.occurrence_identity_contract_id, "non-empty-occurrence"], [observed.payload_contract_id, observed.payload_version, observed.occurrence_identity_contract_id, observed.occurrence_id]));
  }
  if (observed.duplicate_occurrence_observed) {
    findings.push(finding("ARCH_EVENT_OCCURRENCE_DUPLICATE", false, true));
  }
  if (descriptor.publication_policy_id !== observed.publication_policy_id) {
    findings.push(finding("ARCH_EVENT_PUBLICATION_POLICY_DRIFT", descriptor.publication_policy_id, observed.publication_policy_id));
  }
  if (observed.publication_attempt_ids.some((id) => id.length === 0)
      || new Set(observed.publication_attempt_ids).size !== observed.publication_attempt_ids.length) {
    findings.push(finding("ARCH_EVENT_PUBLICATION_ATTEMPT_DUPLICATE", "distinct non-empty attempt identities", observed.publication_attempt_ids));
  }
  const durableIndex = observed.lifecycle_trace.indexOf("durable-fact");
  const firstPublicationIndex = observed.lifecycle_trace.indexOf("publish-attempted");
  if (durableIndex < 0 || observed.lifecycle_trace.filter((state) => state === "durable-fact").length !== 1
      || (firstPublicationIndex >= 0 && firstPublicationIndex < durableIndex)) {
    findings.push(finding("ARCH_EVENT_PUBLICATION_ORDER_DRIFT", "one durable-fact before publication", observed.lifecycle_trace));
  }
  if (!sameStringSet(descriptor.consumer_contract_ids, observed.consumer_contract_ids)) {
    findings.push(finding("ARCH_EVENT_CONSUMER_DRIFT", descriptor.consumer_contract_ids, observed.consumer_contract_ids));
  }
  const consumerChecksValid = sameStringSet(
    descriptor.consumer_contract_ids,
    observed.consumer_payload_checks.map(({consumer_contract_id}) => consumer_contract_id),
  ) && observed.consumer_payload_checks.every(({payload_version, accepted}) =>
    payload_version === descriptor.payload_version && payload_version === observed.payload_version && accepted,
  );
  if (!consumerChecksValid) {
    findings.push(finding("ARCH_EVENT_CONSUMER_VERSION_DRIFT", {consumers: descriptor.consumer_contract_ids, payload_version: descriptor.payload_version}, observed.consumer_payload_checks));
  }
  if (descriptor.distributed_exactly_once_claim !== false || observed.distributed_exactly_once_claim) {
    findings.push(finding("ARCH_EVENT_EXACTLY_ONCE_INFLATION", false, observed.distributed_exactly_once_claim));
  }
  return findings;
};

const evaluateOperation = (descriptor: OperationDescriptor, observed: OperationObservation): Finding[] => {
  const findings: Finding[] = [];
  const observedWriteIds = observed.writes.map(({id}) => id);
  if (descriptor.input_contract_id !== observed.input_contract_id) {
    findings.push(finding("ARCH_OPERATION_INPUT_DRIFT", descriptor.input_contract_id, observed.input_contract_id));
  }
  const hasUndeclaredEffect = !observed.reads.every((item) => descriptor.declared_reads.includes(item))
    || !observedWriteIds.every((item) => descriptor.declared_writes.includes(item))
    || !observed.external_effects.every((item) => descriptor.declared_external_effects.includes(item));
  if (hasUndeclaredEffect) {
    findings.push(finding("ARCH_OPERATION_EFFECT_UNDECLARED", [descriptor.declared_reads, descriptor.declared_writes, descriptor.declared_external_effects], [observed.reads, observedWriteIds, observed.external_effects]));
  }
  if (!sameStringSet(descriptor.declared_reads, observed.reads)
      || !sameStringSet(descriptor.declared_writes, observedWriteIds)
      || !sameStringSet(descriptor.declared_external_effects, observed.external_effects)) {
    findings.push(finding("ARCH_OPERATION_EFFECT_INCOMPLETE", [descriptor.declared_reads, descriptor.declared_writes, descriptor.declared_external_effects], [observed.reads, observedWriteIds, observed.external_effects]));
  }
  if (observed.writes.some(({state}) => state === "restored")) {
    findings.push(finding("ARCH_OPERATION_WRITE_RESTORE", "no hidden write-restore", observed.writes));
  }
  const successful = observed.outcome_id === descriptor.outcome_contract_id && observed.failure_id === null;
  const failed = observed.outcome_id === null && observed.failure_id === descriptor.failure_contract_id;
  const atomicStateValid = descriptor.atomicity === observed.atomicity && (descriptor.atomicity !== "atomic"
    || (successful && observed.writes.every(({state}) => state === "committed"))
    || (failed && observed.writes.every(({state}) => state === "rolled-back")));
  if (!atomicStateValid) {
    findings.push(finding("ARCH_OPERATION_ATOMICITY_DRIFT", {atomicity: descriptor.atomicity, success_state: "committed", failure_state: "rolled-back"}, {atomicity: observed.atomicity, writes: observed.writes, outcome_id: observed.outcome_id, failure_id: observed.failure_id}));
  }
  if (!same(descriptor.ordered_checkpoints, observed.trace)) {
    findings.push(finding("ARCH_OPERATION_ORDER_DRIFT", descriptor.ordered_checkpoints, observed.trace));
  }
  const expectedGuards = descriptor.guard_bindings.map(({rule_id, state_version, controlled_effect}) => ({
    rule_id,
    invoked: true,
    decision_used: true,
    state_version,
    controlled_effect,
  }));
  const guardsValid = sameObjectSet(expectedGuards, observed.guard_results);
  if (!guardsValid) findings.push(finding("ARCH_OPERATION_GUARD_INVALID", descriptor.guard_bindings, observed.guard_results));
  if (!sameObjectSet(descriptor.emitted_event_bindings, observed.emitted_events)) {
    findings.push(finding("ARCH_OPERATION_EVENT_DRIFT", descriptor.emitted_event_bindings, observed.emitted_events));
  }
  if (observed.outcome_id !== null && descriptor.outcome_contract_id !== observed.outcome_id) {
    findings.push(finding("ARCH_OPERATION_OUTCOME_DRIFT", descriptor.outcome_contract_id, observed.outcome_id));
  }
  if (!successful && !failed) {
    findings.push(finding("ARCH_OPERATION_FAILURE_DRIFT", {outcome: descriptor.outcome_contract_id, failure: descriptor.failure_contract_id}, {outcome: observed.outcome_id, failure: observed.failure_id}));
  }
  if (descriptor.continuation_boundary !== observed.continuation_boundary) {
    findings.push(finding("ARCH_OPERATION_CONTINUATION_DRIFT", descriptor.continuation_boundary, observed.continuation_boundary));
  }
  if (!observed.continuation_closed) findings.push(finding("ARCH_OPERATION_CONTINUATION_OPEN", true, false));
  return findings;
};

export const evaluateW3 = (descriptor: W3Descriptor, observation: W3Observation | null): W3Evaluation => {
  let findings = validateBinding(descriptor);
  let verdict: W3Evaluation["verdict"] = "pass";

  if (observation === null) {
    verdict = "unsupported";
    findings = [...findings, finding("ARCH_W3_OBSERVER_UNSUPPORTED", descriptor.kind, null)];
  } else if (descriptor.kind !== observation.kind) {
    verdict = "indeterminate";
    findings = [...findings, finding("ARCH_W3_OBSERVATION_INCOMPLETE", descriptor.kind, observation.kind)];
  } else {
    if (descriptor.kind === "Mapping") findings = [...findings, ...evaluateMapping(descriptor, observation as MappingObservation)];
    if (descriptor.kind === "Interface") findings = [...findings, ...evaluateInterface(descriptor, observation as InterfaceObservation)];
    if (descriptor.kind === "Event") findings = [...findings, ...evaluateEvent(descriptor, observation as EventObservation)];
    if (descriptor.kind === "Operation") findings = [...findings, ...evaluateOperation(descriptor, observation as OperationObservation)];
    verdict = findings.length === 0 ? "pass" : "reject";
  }

  return Object.freeze({
    schema_version: "domainspec.w3-evaluation/v1",
    descriptor_id: descriptor.descriptor_id,
    verdict,
    findings: Object.freeze(findings.map((item) => Object.freeze({...item}))),
    authority_effect: "none",
  });
};
