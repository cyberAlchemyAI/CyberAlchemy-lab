import type { CompiledIntegrationKernelV2, IntegrationKernelV2 } from "./kernel-v2-types.js";
import type { InboundMappingInputV1, OperationRequestParameterV1 } from "./messaging-v2-types.js";

export interface ExternalApiOperationV1 {
  readonly operation_id: string;
  readonly request_type_ref: string;
  readonly result_type_ref: string;
  readonly failure_outcome_refs: readonly string[];
  readonly safety: "safe" | "idempotent" | "unsafe";
}

export interface ExternalApiContractV1 {
  readonly contract_id: string;
  readonly concern: "external-api";
  readonly consumer_role_refs: readonly string[];
  readonly operations: readonly ExternalApiOperationV1[];
  readonly authority_effect: "none";
}

export interface ApiMappingV1 {
  readonly mapping_id: string;
  readonly mapper_ref: string;
  readonly direction: "protocol-to-application" | "application-to-protocol";
  readonly source_ref: string;
  readonly target_ref: string;
  readonly total: boolean;
  readonly input_paths?: readonly InboundMappingInputV1[];
  readonly request_parameters?: readonly OperationRequestParameterV1[];
}

export interface AuthenticationBindingV1 {
  readonly binding_id: string;
  readonly integration_boundary_ref: string;
  readonly scheme: "api-key" | "basic" | "bearer" | "oauth2-client-credentials" | "mutual-tls" | "signed-request";
  readonly credential_slot_refs: readonly string[];
  readonly credential_provider_ref: string;
  readonly rotation_policy_ref: string | null;
  readonly evidence_boundary: string;
  readonly contains_secret_values: false;
  readonly authority_effect: "none";
}

export interface ApiResiliencePolicyV1 {
  readonly policy_id: string;
  readonly timeout_ms: number;
  readonly max_attempts: number;
  readonly backoff_ref: string | null;
  readonly concurrency_policy_ref: string | null;
  readonly circuit_policy_ref: string | null;
  readonly retry_safety: "safe-operation" | "idempotency-key-required" | "retry-forbidden";
  readonly idempotency_key_expression: string | null;
  readonly evidence_boundary: string;
}

export interface ApiFailureCaseV1 {
  readonly category: "protocol" | "provider" | "authentication" | "timeout" | "malformed-response";
  readonly matcher_ref: string;
  readonly failure_outcome_ref: string;
}

export interface ApiFailureMappingV1 {
  readonly mapping_id: string;
  readonly external_api_contract_ref: string;
  readonly kernel_failure_mapping_ref: string;
  readonly cases: readonly ApiFailureCaseV1[];
  readonly unknown_fallback_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface InboundEndpointBindingV1 {
  readonly binding_id: string;
  readonly integration_binding_ref: string;
  readonly protocol_operation_ref: string;
  readonly request_mapper_ref: string;
  readonly operation_ref: string;
  readonly response_mapper_ref: string;
  readonly authentication_binding_ref: string | null;
  readonly failure_mapping_ref: string;
  readonly provider_realization_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface ExternalApiBindingV1 {
  readonly binding_id: string;
  readonly integration_binding_ref: string;
  readonly external_api_contract_ref: string;
  readonly contract_operation_ref: string;
  readonly provider_operation_ref: string;
  readonly request_mapper_ref: string;
  readonly response_mapper_ref: string;
  readonly authentication_binding_ref: string | null;
  readonly resilience_policy_ref: string;
  readonly failure_mapping_ref: string;
  readonly provider_realization_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface WebhookBindingV1 {
  readonly binding_id: string;
  readonly inbound_endpoint_binding_ref: string;
  readonly sender_verification_ref: string;
  readonly replay_protection_ref: string;
  readonly external_event_id_expression: string;
  readonly acknowledgement_policy: "ack-after-verification" | "ack-after-application-commit";
  readonly application_completion_inferred: false;
  readonly authority_effect: "none";
}

export interface ExternalApiCompositionV2 {
  readonly schema_version: "domainspec.external-api-composition/v2-candidate";
  readonly composition_id: string;
  readonly integration_kernel: IntegrationKernelV2;
  readonly external_api_contracts: readonly ExternalApiContractV1[];
  readonly api_mappings: readonly ApiMappingV1[];
  readonly authentication_bindings: readonly AuthenticationBindingV1[];
  readonly resilience_policies: readonly ApiResiliencePolicyV1[];
  readonly api_failure_mappings: readonly ApiFailureMappingV1[];
  readonly inbound_endpoint_bindings: readonly InboundEndpointBindingV1[];
  readonly external_api_bindings: readonly ExternalApiBindingV1[];
  readonly webhook_bindings: readonly WebhookBindingV1[];
  readonly runtime_calls_observed: false;
  readonly authority_effect: "none";
}

export interface CompiledExternalApiCompositionV2 extends Omit<ExternalApiCompositionV2, "integration_kernel"> {
  readonly integration_kernel: CompiledIntegrationKernelV2;
  readonly composition_digest: string;
}
