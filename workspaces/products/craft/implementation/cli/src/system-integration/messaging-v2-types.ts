import type { CompiledIntegrationKernelV2, IntegrationKernelV2 } from "./kernel-v2-types.js";

export interface MessageTypeV1 {
  readonly message_type_id: string;
  readonly message_kind: "event-notification" | "command-request" | "query-request" | "query-response" | "integration-document";
  readonly logical_payload_ref: string;
  readonly serialization_profile_ref: string;
  readonly version: string;
}

export interface InboundMappingInputV1 {
  readonly parameter: string;
  readonly path: readonly string[];
}

export interface OperationRequestParameterV1 {
  readonly parameter: string;
  readonly source: Readonly<
    | { readonly kind: "mapping-result"; readonly path: readonly string[] }
    | { readonly kind: "source-body"; readonly path: readonly string[] }
  >;
}

export interface MessageMappingV1 {
  readonly mapping_id: string;
  readonly mapper_ref: string;
  readonly direction: "logical-to-message" | "message-to-application";
  readonly source_ref: string;
  readonly target_ref: string;
  readonly total: boolean;
  readonly input_paths?: readonly InboundMappingInputV1[];
  readonly request_parameters?: readonly OperationRequestParameterV1[];
}

interface MessageChannelBaseV1 {
  readonly channel_id: string;
  readonly accepted_message_type_refs: readonly string[];
  readonly owner_ref: string;
  readonly lifecycle_policy_ref: string;
  readonly provider_name: string | null;
}

export interface QueueChannelV1 extends MessageChannelBaseV1 {
  readonly channel_kind: "queue";
  readonly consumption_model: "competing-consumers";
}

export interface TopicChannelV1 extends MessageChannelBaseV1 {
  readonly channel_kind: "topic";
  readonly consumption_model: "fan-out-subscriptions";
}

export interface StreamChannelV1 extends MessageChannelBaseV1 {
  readonly channel_kind: "stream";
  readonly consumption_model: "retained-log";
  readonly cursor_model_ref: string;
  readonly ordering_scope_ref: string;
}

export interface DeadLetterChannelV1 extends MessageChannelBaseV1 {
  readonly channel_kind: "dead-letter";
  readonly source_channel_ref: string;
  readonly terminal_failure_classes: readonly string[];
  readonly retention_policy_ref: string;
  readonly redrive_policy_ref: string;
}

export type MessageChannelV2 = QueueChannelV1 | TopicChannelV1 | StreamChannelV1 | DeadLetterChannelV1;

export interface DeliveryPolicyV2 {
  readonly policy_id: string;
  readonly guarantee: "at-most-once" | "at-least-once";
  readonly retry_schedule_ref: string | null;
  readonly max_attempts: number | null;
  readonly lease_or_visibility_ref: string | null;
  readonly terminal_disposition: "drop" | "dead-letter" | "retain";
  readonly dead_letter_channel_ref: string | null;
}

export interface ProducerAcceptanceBoundaryV1 {
  readonly boundary_id: string;
  readonly publication_binding_ref: string;
  readonly condition: "provider-accepted" | "transport-persisted";
  readonly observation_boundary: string;
  readonly claim_ceiling: "provider-accepted";
}

export interface AcknowledgementBoundaryV1 {
  readonly boundary_id: string;
  readonly subscription_binding_ref: string;
  readonly condition: "consumer-handler-returned" | "application-committed";
  readonly failure_before_ack: string;
  readonly failure_after_ack: string;
  readonly evidence_boundary: string;
}

export interface OrderingPolicyV1 {
  readonly policy_id: string;
  readonly mode: "unordered" | "key-ordered" | "globally-ordered";
  readonly key_expression: string | null;
  readonly observation_boundary: string;
  readonly disorder_handling: "reject" | "buffer" | "accept-and-observe";
}

export interface DeduplicationPolicyV1 {
  readonly policy_id: string;
  readonly key_expression: string;
  readonly owner_ref: string;
  readonly retention_window_ref: string;
  readonly transaction_binding_ref: string | null;
  readonly duplicate_outcome: "ignore" | "return-recorded-result" | "reject";
}

export interface PublicationBindingV1 {
  readonly binding_id: string;
  readonly integration_binding_ref: string;
  readonly producer_contract_ref: string;
  readonly logical_source_ref: string;
  readonly message_type_ref: string;
  readonly mapper_ref: string;
  readonly channel_ref: string;
  readonly delivery_policy_ref: string;
  readonly producer_acceptance_boundary_ref: string;
  readonly provider_realization_ref: string;
  readonly failure_mapping_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface SubscriptionBindingV1 {
  readonly binding_id: string;
  readonly integration_binding_ref: string;
  readonly channel_ref: string;
  readonly subscription_id: string;
  readonly message_type_ref: string;
  readonly mapper_ref: string;
  readonly operation_ref: string;
  readonly acknowledgement_boundary_ref: string;
  readonly delivery_policy_ref: string;
  readonly ordering_policy_ref: string;
  readonly deduplication_policy_ref: string;
  readonly failure_mapping_ref: string;
  readonly provider_realization_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface MessagingCompositionV2 {
  readonly schema_version: "domainspec.messaging-composition/v2-candidate";
  readonly composition_id: string;
  readonly integration_kernel: IntegrationKernelV2;
  readonly message_types: readonly MessageTypeV1[];
  readonly message_mappings: readonly MessageMappingV1[];
  readonly channels: readonly MessageChannelV2[];
  readonly delivery_policies: readonly DeliveryPolicyV2[];
  readonly producer_acceptance_boundaries: readonly ProducerAcceptanceBoundaryV1[];
  readonly acknowledgement_boundaries: readonly AcknowledgementBoundaryV1[];
  readonly ordering_policies: readonly OrderingPolicyV1[];
  readonly deduplication_policies: readonly DeduplicationPolicyV1[];
  readonly publication_bindings: readonly PublicationBindingV1[];
  readonly subscription_bindings: readonly SubscriptionBindingV1[];
  readonly runtime_delivery_observed: false;
  readonly authority_effect: "none";
}

export interface CompiledMessagingCompositionV2 extends Omit<MessagingCompositionV2, "integration_kernel"> {
  readonly integration_kernel: CompiledIntegrationKernelV2;
  readonly composition_digest: string;
}

export interface LegacyMessagingProjectionV2 {
  readonly schema_version: "domainspec.messaging-legacy-projection/v2-candidate";
  readonly source_schema_version: "domainspec.binding-set/v1-candidate";
  readonly source_digest: string;
  readonly retained_event_refs: readonly string[];
  readonly retained_operation_refs: readonly string[];
  readonly channel_classification: "legacy-undifferentiated";
  readonly producer_acceptance: "provider-accepted-unclassified";
  readonly message_types_inferred: false;
  readonly subscriptions_inferred: false;
  readonly consumer_acknowledgement_inferred: false;
  readonly application_commit_inferred: false;
  readonly exactly_once_inferred: false;
  readonly authority_effect: "none";
}
