export type W3Language = "typescript" | "python" | "rust";

export type ContentRef = Readonly<{
  id: string;
  sha256: string;
}>;

export type W3Binding = Readonly<{
  protocol_id: "domainspec.w3-descriptor-binding/v1";
  concept_ref: ContentRef;
  decision_ref: ContentRef;
  profile_ref: ContentRef;
  provider_ref: ContentRef;
  source_ref: ContentRef;
  fixture_ref: ContentRef;
}>;

type W3DescriptorBase = Readonly<{
  schema_version: "domainspec.w3-descriptor/v1";
  descriptor_id: string;
  language: W3Language;
  binding: W3Binding;
  claim_ceiling: "candidate-local-exact-fixture";
  authority_effect: "none";
}>;

export type MappingDescriptor = W3DescriptorBase & Readonly<{
  kind: "Mapping";
  source_contract_id: string;
  target_contract_id: string;
  direction: "forward" | "reverse" | "bidirectional";
  correspondence: readonly Readonly<{
    source: string | null;
    target: string | null;
    mode: "direct" | "ignored" | "synthesized" | "defaulted";
  }>[];
  totality: "total" | "partial-fallible";
  failure_contract_id: string | null;
  effect_policy: "none" | "declared-read-only";
  reverse_contract_id: string | null;
}>;

export type InterfaceDescriptor = W3DescriptorBase & Readonly<{
  kind: "Interface";
  boundary_kind: "internal" | "external";
  contract_id: string;
  exact_version: string;
  compatibility_policy_id: string;
  exposed_bindings: readonly Readonly<{
    binding_id: string;
    kind: "Operation" | "Query";
  }>[];
  admission_status: "candidate";
}>;

export type EventDescriptor = W3DescriptorBase & Readonly<{
  kind: "Event";
  tense: "past";
  payload_contract_id: string;
  payload_version: string;
  occurrence_identity_contract_id: string;
  fact_checkpoint: "domain-state-commit" | "durable-event-store-append" | "durable-outbox-append";
  publication_policy_id: string;
  consumer_contract_ids: readonly string[];
  distributed_exactly_once_claim: false;
}>;

export type OperationDescriptor = W3DescriptorBase & Readonly<{
  kind: "Operation";
  input_contract_id: string;
  declared_reads: readonly string[];
  declared_writes: readonly string[];
  declared_external_effects: readonly string[];
  outcome_contract_id: string;
  failure_contract_id: string;
  atomicity: "atomic" | "compensating";
  ordered_checkpoints: readonly string[];
  guard_bindings: readonly Readonly<{
    rule_id: string;
    state_version: string;
    controlled_effect: string;
  }>[];
  emitted_event_bindings: readonly Readonly<{
    event_id: string;
    checkpoint: EventDescriptor["fact_checkpoint"];
    after_outcome: string;
  }>[];
  continuation_boundary: "synchronous-return" | "awaited-settlement" | "declared-background-handoff";
}>;

export type W3Descriptor = MappingDescriptor | InterfaceDescriptor | EventDescriptor | OperationDescriptor;

export type MappingObservation = Readonly<{
  kind: "Mapping";
  source_contract_id: string;
  target_contract_id: string;
  direction: MappingDescriptor["direction"];
  observed_correspondence: MappingDescriptor["correspondence"];
  totality: MappingDescriptor["totality"];
  failure_contract_id: string | null;
  failure_observed: boolean;
  effect_policy: MappingDescriptor["effect_policy"];
  effects: readonly string[];
  reverse_contract_complete: boolean;
}>;

export type InterfaceObservation = Readonly<{
  kind: "Interface";
  boundary_kind: InterfaceDescriptor["boundary_kind"];
  contract_id: string;
  version: string;
  compatibility_policy_id: string;
  exposed_bindings: InterfaceDescriptor["exposed_bindings"];
  compatibility_checks: readonly Readonly<{
    requested_version: string;
    accepted: boolean;
  }>[];
}>;

export type EventObservation = Readonly<{
  kind: "Event";
  tense: "past" | "present";
  payload_contract_id: string;
  payload_version: string;
  occurrence_identity_contract_id: string;
  occurrence_id: string;
  duplicate_occurrence_observed: boolean;
  durable_checkpoints: readonly EventDescriptor["fact_checkpoint"][];
  publication_policy_id: string;
  publication_attempt_ids: readonly string[];
  consumer_contract_ids: readonly string[];
  consumer_payload_checks: readonly Readonly<{
    consumer_contract_id: string;
    payload_version: string;
    accepted: boolean;
  }>[];
  lifecycle_trace: readonly ("constructed" | "durable-fact" | "outbox-appended" | "publish-attempted" | "acknowledged" | "failed")[];
  distributed_exactly_once_claim: boolean;
}>;

export type OperationObservation = Readonly<{
  kind: "Operation";
  input_contract_id: string;
  reads: readonly string[];
  writes: readonly Readonly<{ id: string; state: "attempted" | "committed" | "rolled-back" | "restored" | "deferred" | "partial" }>[];
  external_effects: readonly string[];
  atomicity: OperationDescriptor["atomicity"];
  trace: readonly string[];
  guard_results: readonly Readonly<{
    rule_id: string;
    invoked: boolean;
    decision_used: boolean;
    state_version: string;
    controlled_effect: string;
  }>[];
  emitted_events: readonly Readonly<{
    event_id: string;
    checkpoint: EventDescriptor["fact_checkpoint"];
    after_outcome: string;
  }>[];
  outcome_id: string | null;
  failure_id: string | null;
  continuation_boundary: OperationDescriptor["continuation_boundary"];
  continuation_closed: boolean;
}>;

export type W3Observation = MappingObservation | InterfaceObservation | EventObservation | OperationObservation;

export type W3FindingCode =
  | "ARCH_W3_BINDING_INVALID"
  | "ARCH_W3_OBSERVER_UNSUPPORTED"
  | "ARCH_W3_OBSERVATION_INCOMPLETE"
  | "ARCH_MAPPING_ENDPOINT_DRIFT"
  | "ARCH_MAPPING_DIRECTION_DRIFT"
  | "ARCH_MAPPING_CORRESPONDENCE_DRIFT"
  | "ARCH_MAPPING_TOTALITY_DRIFT"
  | "ARCH_MAPPING_FAILURE_DRIFT"
  | "ARCH_MAPPING_FAILURE_HIDDEN"
  | "ARCH_MAPPING_EFFECT_POLICY_DRIFT"
  | "ARCH_MAPPING_EFFECT_UNDECLARED"
  | "ARCH_MAPPING_REVERSE_INCOMPLETE"
  | "ARCH_INTERFACE_CONTRACT_DRIFT"
  | "ARCH_INTERFACE_EXPOSURE_DRIFT"
  | "ARCH_INTERFACE_COMPATIBILITY_DRIFT"
  | "ARCH_EVENT_NOT_PAST_FACT"
  | "ARCH_EVENT_CHECKPOINT_INVALID"
  | "ARCH_EVENT_PAYLOAD_DRIFT"
  | "ARCH_EVENT_OCCURRENCE_DUPLICATE"
  | "ARCH_EVENT_PUBLICATION_POLICY_DRIFT"
  | "ARCH_EVENT_PUBLICATION_ATTEMPT_DUPLICATE"
  | "ARCH_EVENT_PUBLICATION_ORDER_DRIFT"
  | "ARCH_EVENT_CONSUMER_DRIFT"
  | "ARCH_EVENT_CONSUMER_VERSION_DRIFT"
  | "ARCH_EVENT_EXACTLY_ONCE_INFLATION"
  | "ARCH_OPERATION_INPUT_DRIFT"
  | "ARCH_OPERATION_EFFECT_UNDECLARED"
  | "ARCH_OPERATION_EFFECT_INCOMPLETE"
  | "ARCH_OPERATION_ATOMICITY_DRIFT"
  | "ARCH_OPERATION_WRITE_RESTORE"
  | "ARCH_OPERATION_ORDER_DRIFT"
  | "ARCH_OPERATION_GUARD_INVALID"
  | "ARCH_OPERATION_EVENT_DRIFT"
  | "ARCH_OPERATION_OUTCOME_DRIFT"
  | "ARCH_OPERATION_FAILURE_DRIFT"
  | "ARCH_OPERATION_CONTINUATION_DRIFT"
  | "ARCH_OPERATION_CONTINUATION_OPEN";

export type W3Evaluation = Readonly<{
  schema_version: "domainspec.w3-evaluation/v1";
  descriptor_id: string;
  verdict: "pass" | "reject" | "unsupported" | "indeterminate";
  findings: readonly Readonly<{ code: W3FindingCode; expected: unknown; observed: unknown }>[];
  authority_effect: "none";
}>;
