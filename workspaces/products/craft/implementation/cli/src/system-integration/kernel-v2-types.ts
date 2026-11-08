export const INTEGRATION_CONCERNS = ["persistence", "messaging", "external-api", "observation"] as const;
export type IntegrationConcern = (typeof INTEGRATION_CONCERNS)[number];

export const INTEGRATION_DIRECTIONS = ["inbound", "outbound", "bidirectional"] as const;
export type IntegrationDirection = (typeof INTEGRATION_DIRECTIONS)[number];

export const INTEGRATION_OBSERVATION_STAGES = [
  "request-formed",
  "adapter-invoked",
  "provider-accepted",
  "transport-delivered",
  "application-committed",
  "business-completed",
  "failed",
] as const;
export type IntegrationObservationStage = (typeof INTEGRATION_OBSERVATION_STAGES)[number];

export interface IntegrationBindingV2 {
  readonly binding_id: string;
  readonly concern: IntegrationConcern;
  readonly direction: IntegrationDirection;
  readonly logical_boundary_ref: string;
  readonly contract_ref: string | null;
  readonly provider_realization_ref: string;
  readonly policy_refs: readonly string[];
  readonly serialization_profile_ref: string | null;
  readonly failure_mapping_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface ProviderProfileV1 {
  readonly profile_id: string;
  readonly concern: IntegrationConcern;
  readonly provider_kind: string;
  readonly capability_set: readonly string[];
  readonly configuration_schema_ref: string;
  readonly secret_slot_refs: readonly string[];
  readonly compatibility_constraints: readonly string[];
  readonly authority_effect: "none";
}

export interface ProviderRealizationV1 {
  readonly realization_id: string;
  readonly provider_profile_ref: string;
  readonly adapter_ref: string;
  readonly resource_ref: string;
  readonly configuration_ref: string;
  readonly credential_binding_ref: string | null;
  readonly deployment_ref: string | null;
  readonly evidence_boundary: string;
  readonly runtime_observed: false;
  readonly authority_effect: "none";
}

export interface SerializationProfileV1 {
  readonly profile_id: string;
  readonly logical_type_ref: string;
  readonly format: "json" | "avro" | "protobuf" | "text" | "binary" | "provider-native";
  readonly schema_ref: string;
  readonly version: string;
  readonly compatibility_policy: "none" | "backward" | "forward" | "full";
  readonly encoding_options: Readonly<Record<string, string | number | boolean>>;
  readonly authority_effect: "none";
}

export interface FailureMappingCaseV1 {
  readonly provider_failure_matcher: string;
  readonly failure_outcome_ref: string;
  readonly outcome_class: "retryable" | "non-retryable" | "unknown";
}

export interface IntegrationFailureMappingV1 {
  readonly mapping_id: string;
  readonly boundary_ref: string;
  readonly cases: readonly FailureMappingCaseV1[];
  readonly unknown_failure_outcome_ref: string;
  readonly continuation_owner_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface IntegrationRuntimeReceiptV1 {
  readonly receipt_id: string;
  readonly binding_ref: string;
  readonly operation_ref: string | null;
  readonly observed_at: string;
  readonly observed_stage: IntegrationObservationStage;
  readonly outcome: "accepted" | "rejected" | "failed" | "unknown";
  readonly provider_evidence_ref: string | null;
  readonly correlation_ref: string | null;
  readonly claim_ceiling: IntegrationObservationStage;
  readonly authority_effect: "none";
}

export interface IntegrationKernelV2 {
  readonly schema_version: "domainspec.integration-kernel/v2-candidate";
  readonly kernel_id: string;
  readonly definition_pack_sha256: string;
  readonly integration_bindings: readonly IntegrationBindingV2[];
  readonly provider_profiles: readonly ProviderProfileV1[];
  readonly provider_realizations: readonly ProviderRealizationV1[];
  readonly serialization_profiles: readonly SerializationProfileV1[];
  readonly failure_mappings: readonly IntegrationFailureMappingV1[];
  readonly runtime_receipts: readonly IntegrationRuntimeReceiptV1[];
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
}

export interface CompiledIntegrationKernelV2 extends IntegrationKernelV2 {
  readonly kernel_digest: string;
}
