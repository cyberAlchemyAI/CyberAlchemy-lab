import { canonicalJson, sha256 } from "../input/source-manifest.js";
import {
  INTEGRATION_CONCERNS,
  INTEGRATION_DIRECTIONS,
  INTEGRATION_OBSERVATION_STAGES,
  type CompiledIntegrationKernelV2,
  type FailureMappingCaseV1,
  type IntegrationBindingV2,
  type IntegrationConcern,
  type IntegrationFailureMappingV1,
  type IntegrationKernelV2,
  type IntegrationRuntimeReceiptV1,
  type ProviderProfileV1,
  type ProviderRealizationV1,
  type SerializationProfileV1,
} from "./kernel-v2-types.js";

export const SYSTEM_INTEGRATION_DEFINITION_PACK_SHA256 = "cc93b59b68cbb016fdab6b0b4a476e69d1e0e6df99df1d94ca1c48fb7ff16c2a";
const REF = /^[A-Za-z][A-Za-z0-9]*(?:[-.:/][A-Za-z0-9]+)*$/;
const SHA256 = /^[a-f0-9]{64}$/;

type UnknownRecord = Record<string, unknown>;

export class IntegrationKernelError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "IntegrationKernelError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new IntegrationKernelError(code, pointer, message);
}

function object(value: unknown, pointer: string): asserts value is UnknownRecord {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("IK_SCHEMA", pointer, "expected object");
}

function exact(value: unknown, fields: readonly string[], pointer: string): asserts value is UnknownRecord {
  object(value, pointer);
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...fields].sort())) fail("IK_SCHEMA", pointer, "unexpected or missing member");
}

function reference(value: unknown, pointer: string): string {
  if (typeof value !== "string" || !REF.test(value) || /(^|[-.:/])Port($|[-.:/])/i.test(value)) fail("IK_REFERENCE", pointer, "invalid reference or forbidden universal Port");
  return value;
}

function text(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.trim().length === 0) fail("IK_SCHEMA", pointer, "expected non-empty text");
  return value;
}

function nullableReference(value: unknown, pointer: string): string | null {
  return value === null ? null : reference(value, pointer);
}

function stringSet(value: unknown, pointer: string, allowEmpty = true): readonly string[] {
  if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("IK_SCHEMA", pointer, "expected string array");
  const normalized = value.map((entry, index) => reference(entry, `${pointer}/${index}`));
  if (new Set(normalized).size !== normalized.length) fail("IK_DUPLICATE", pointer, "duplicate reference");
  return Object.freeze([...normalized].sort());
}

function records(value: unknown, pointer: string): readonly unknown[] {
  if (!Array.isArray(value)) fail("IK_SCHEMA", pointer, "expected array");
  return value;
}

function identitySet<T extends Record<K, string>, K extends keyof T>(values: readonly T[], key: K, pointer: string): ReadonlyMap<string, T> {
  const result = new Map<string, T>();
  for (const item of values) {
    const id = item[key];
    if (result.has(id)) fail("IK_DUPLICATE", pointer, `duplicate identity:${id}`);
    result.set(id, item);
  }
  return result;
}

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
  }
  return value;
}

function providerProfile(value: unknown, pointer: string): ProviderProfileV1 {
  exact(value, ["profile_id", "concern", "provider_kind", "capability_set", "configuration_schema_ref", "secret_slot_refs", "compatibility_constraints", "authority_effect"], pointer);
  if (!INTEGRATION_CONCERNS.includes(value.concern as IntegrationConcern)) fail("IK_CONCERN", `${pointer}/concern`, "unknown concern");
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  const providerKind = reference(value.provider_kind, `${pointer}/provider_kind`);
  return Object.freeze({
    profile_id: reference(value.profile_id, `${pointer}/profile_id`), concern: value.concern as IntegrationConcern,
    provider_kind: providerKind, capability_set: stringSet(value.capability_set, `${pointer}/capability_set`, false),
    configuration_schema_ref: reference(value.configuration_schema_ref, `${pointer}/configuration_schema_ref`),
    secret_slot_refs: stringSet(value.secret_slot_refs, `${pointer}/secret_slot_refs`),
    compatibility_constraints: stringSet(value.compatibility_constraints, `${pointer}/compatibility_constraints`), authority_effect: "none",
  });
}

function providerRealization(value: unknown, pointer: string): ProviderRealizationV1 {
  exact(value, ["realization_id", "provider_profile_ref", "adapter_ref", "resource_ref", "configuration_ref", "credential_binding_ref", "deployment_ref", "evidence_boundary", "runtime_observed", "authority_effect"], pointer);
  if (value.runtime_observed !== false) fail("IK_RUNTIME_CLAIM", `${pointer}/runtime_observed`, "configuration is not runtime observation");
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({
    realization_id: reference(value.realization_id, `${pointer}/realization_id`), provider_profile_ref: reference(value.provider_profile_ref, `${pointer}/provider_profile_ref`),
    adapter_ref: reference(value.adapter_ref, `${pointer}/adapter_ref`), resource_ref: reference(value.resource_ref, `${pointer}/resource_ref`),
    configuration_ref: reference(value.configuration_ref, `${pointer}/configuration_ref`), credential_binding_ref: nullableReference(value.credential_binding_ref, `${pointer}/credential_binding_ref`),
    deployment_ref: nullableReference(value.deployment_ref, `${pointer}/deployment_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), runtime_observed: false, authority_effect: "none",
  });
}

function serializationProfile(value: unknown, pointer: string): SerializationProfileV1 {
  exact(value, ["profile_id", "logical_type_ref", "format", "schema_ref", "version", "compatibility_policy", "encoding_options", "authority_effect"], pointer);
  const formats = ["json", "avro", "protobuf", "text", "binary", "provider-native"] as const;
  const compatibility = ["none", "backward", "forward", "full"] as const;
  if (!formats.includes(value.format as typeof formats[number])) fail("IK_SERIALIZATION", `${pointer}/format`, "unsupported format");
  if (!compatibility.includes(value.compatibility_policy as typeof compatibility[number])) fail("IK_SERIALIZATION", `${pointer}/compatibility_policy`, "unsupported compatibility policy");
  object(value.encoding_options, `${pointer}/encoding_options`);
  const options: Record<string, string | number | boolean> = {};
  for (const key of Object.keys(value.encoding_options).sort()) {
    const option = value.encoding_options[key];
    if (!["string", "number", "boolean"].includes(typeof option) || (typeof option === "number" && !Number.isFinite(option))) fail("IK_SERIALIZATION", `${pointer}/encoding_options/${key}`, "encoding option must be scalar");
    options[key] = option as string | number | boolean;
  }
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ profile_id: reference(value.profile_id, `${pointer}/profile_id`), logical_type_ref: reference(value.logical_type_ref, `${pointer}/logical_type_ref`), format: value.format as SerializationProfileV1["format"], schema_ref: reference(value.schema_ref, `${pointer}/schema_ref`), version: reference(value.version, `${pointer}/version`), compatibility_policy: value.compatibility_policy as SerializationProfileV1["compatibility_policy"], encoding_options: Object.freeze(options), authority_effect: "none" });
}

function failureCase(value: unknown, pointer: string): FailureMappingCaseV1 {
  exact(value, ["provider_failure_matcher", "failure_outcome_ref", "outcome_class"], pointer);
  if (!["retryable", "non-retryable", "unknown"].includes(String(value.outcome_class))) fail("IK_FAILURE", `${pointer}/outcome_class`, "invalid outcome class");
  return Object.freeze({ provider_failure_matcher: reference(value.provider_failure_matcher, `${pointer}/provider_failure_matcher`), failure_outcome_ref: reference(value.failure_outcome_ref, `${pointer}/failure_outcome_ref`), outcome_class: value.outcome_class as FailureMappingCaseV1["outcome_class"] });
}

function failureMapping(value: unknown, pointer: string): IntegrationFailureMappingV1 {
  exact(value, ["mapping_id", "boundary_ref", "cases", "unknown_failure_outcome_ref", "continuation_owner_ref", "evidence_boundary", "authority_effect"], pointer);
  const rawCases = records(value.cases, `${pointer}/cases`);
  if (rawCases.length === 0) fail("IK_FAILURE", `${pointer}/cases`, "at least one classification case required");
  const cases = rawCases.map((entry, index) => failureCase(entry, `${pointer}/cases/${index}`)).sort((left, right) => left.provider_failure_matcher.localeCompare(right.provider_failure_matcher));
  if (new Set(cases.map((entry) => entry.provider_failure_matcher)).size !== cases.length) fail("IK_DUPLICATE", `${pointer}/cases`, "duplicate provider failure matcher");
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ mapping_id: reference(value.mapping_id, `${pointer}/mapping_id`), boundary_ref: reference(value.boundary_ref, `${pointer}/boundary_ref`), cases: Object.freeze(cases), unknown_failure_outcome_ref: reference(value.unknown_failure_outcome_ref, `${pointer}/unknown_failure_outcome_ref`), continuation_owner_ref: reference(value.continuation_owner_ref, `${pointer}/continuation_owner_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function integrationBinding(value: unknown, pointer: string): IntegrationBindingV2 {
  exact(value, ["binding_id", "concern", "direction", "logical_boundary_ref", "contract_ref", "provider_realization_ref", "policy_refs", "serialization_profile_ref", "failure_mapping_ref", "evidence_boundary", "authority_effect"], pointer);
  if (!INTEGRATION_CONCERNS.includes(value.concern as IntegrationConcern)) fail("IK_CONCERN", `${pointer}/concern`, "unknown concern");
  if (!INTEGRATION_DIRECTIONS.includes(value.direction as IntegrationBindingV2["direction"])) fail("IK_DIRECTION", `${pointer}/direction`, "unknown direction");
  const contractRef = nullableReference(value.contract_ref, `${pointer}/contract_ref`);
  if (value.direction !== "inbound" && contractRef === null) fail("IK_CONTRACT", `${pointer}/contract_ref`, "outbound and bidirectional bindings require a concern-specific contract");
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: reference(value.binding_id, `${pointer}/binding_id`), concern: value.concern as IntegrationConcern, direction: value.direction as IntegrationBindingV2["direction"], logical_boundary_ref: reference(value.logical_boundary_ref, `${pointer}/logical_boundary_ref`), contract_ref: contractRef, provider_realization_ref: reference(value.provider_realization_ref, `${pointer}/provider_realization_ref`), policy_refs: stringSet(value.policy_refs, `${pointer}/policy_refs`), serialization_profile_ref: nullableReference(value.serialization_profile_ref, `${pointer}/serialization_profile_ref`), failure_mapping_ref: reference(value.failure_mapping_ref, `${pointer}/failure_mapping_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function runtimeReceipt(value: unknown, pointer: string): IntegrationRuntimeReceiptV1 {
  exact(value, ["receipt_id", "binding_ref", "operation_ref", "observed_at", "observed_stage", "outcome", "provider_evidence_ref", "correlation_ref", "claim_ceiling", "authority_effect"], pointer);
  if (!INTEGRATION_OBSERVATION_STAGES.includes(value.observed_stage as IntegrationRuntimeReceiptV1["observed_stage"])) fail("IK_RECEIPT", `${pointer}/observed_stage`, "unknown observation stage");
  if (value.claim_ceiling !== value.observed_stage) fail("IK_RECEIPT_CLAIM", `${pointer}/claim_ceiling`, "receipt claim ceiling must equal the bounded observed stage");
  if (!["accepted", "rejected", "failed", "unknown"].includes(String(value.outcome))) fail("IK_RECEIPT", `${pointer}/outcome`, "unknown receipt outcome");
  const observedAt = text(value.observed_at, `${pointer}/observed_at`);
  if (!Number.isFinite(Date.parse(observedAt))) fail("IK_RECEIPT", `${pointer}/observed_at`, "invalid timestamp");
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ receipt_id: reference(value.receipt_id, `${pointer}/receipt_id`), binding_ref: reference(value.binding_ref, `${pointer}/binding_ref`), operation_ref: nullableReference(value.operation_ref, `${pointer}/operation_ref`), observed_at: observedAt, observed_stage: value.observed_stage as IntegrationRuntimeReceiptV1["observed_stage"], outcome: value.outcome as IntegrationRuntimeReceiptV1["outcome"], provider_evidence_ref: nullableReference(value.provider_evidence_ref, `${pointer}/provider_evidence_ref`), correlation_ref: nullableReference(value.correlation_ref, `${pointer}/correlation_ref`), claim_ceiling: value.claim_ceiling as IntegrationRuntimeReceiptV1["claim_ceiling"], authority_effect: "none" });
}

export function validateIntegrationKernelV2(value: unknown): IntegrationKernelV2 {
  exact(value, ["schema_version", "kernel_id", "definition_pack_sha256", "integration_bindings", "provider_profiles", "provider_realizations", "serialization_profiles", "failure_mappings", "runtime_receipts", "runtime_guarantees_observed", "authority_effect"], "/");
  if (value.schema_version !== "domainspec.integration-kernel/v2-candidate") fail("IK_SCHEMA", "/schema_version", "unsupported schema");
  if (typeof value.definition_pack_sha256 !== "string" || !SHA256.test(value.definition_pack_sha256) || value.definition_pack_sha256 !== SYSTEM_INTEGRATION_DEFINITION_PACK_SHA256) fail("IK_DEFINITION_DRIFT", "/definition_pack_sha256", "definition pack digest drift");
  if (value.runtime_guarantees_observed !== false) fail("IK_RUNTIME_CLAIM", "/runtime_guarantees_observed", "kernel formation is not runtime evidence");
  if (value.authority_effect !== "none") fail("IK_AUTHORITY", "/authority_effect", "authority growth forbidden");

  const providerProfiles = records(value.provider_profiles, "/provider_profiles").map((entry, index) => providerProfile(entry, `/provider_profiles/${index}`)).sort((left, right) => left.profile_id.localeCompare(right.profile_id));
  const providerRealizations = records(value.provider_realizations, "/provider_realizations").map((entry, index) => providerRealization(entry, `/provider_realizations/${index}`)).sort((left, right) => left.realization_id.localeCompare(right.realization_id));
  const serializationProfiles = records(value.serialization_profiles, "/serialization_profiles").map((entry, index) => serializationProfile(entry, `/serialization_profiles/${index}`)).sort((left, right) => left.profile_id.localeCompare(right.profile_id));
  const failureMappings = records(value.failure_mappings, "/failure_mappings").map((entry, index) => failureMapping(entry, `/failure_mappings/${index}`)).sort((left, right) => left.mapping_id.localeCompare(right.mapping_id));
  const integrationBindings = records(value.integration_bindings, "/integration_bindings").map((entry, index) => integrationBinding(entry, `/integration_bindings/${index}`)).sort((left, right) => left.binding_id.localeCompare(right.binding_id));
  const runtimeReceipts = records(value.runtime_receipts, "/runtime_receipts").map((entry, index) => runtimeReceipt(entry, `/runtime_receipts/${index}`)).sort((left, right) => left.receipt_id.localeCompare(right.receipt_id));

  const profileById = identitySet(providerProfiles, "profile_id", "/provider_profiles");
  const realizationById = identitySet(providerRealizations, "realization_id", "/provider_realizations");
  const serializationById = identitySet(serializationProfiles, "profile_id", "/serialization_profiles");
  const failureById = identitySet(failureMappings, "mapping_id", "/failure_mappings");
  const bindingById = identitySet(integrationBindings, "binding_id", "/integration_bindings");
  identitySet(runtimeReceipts, "receipt_id", "/runtime_receipts");

  for (const realization of providerRealizations) if (!profileById.has(realization.provider_profile_ref)) fail("IK_REFERENCE_UNRESOLVED", "/provider_realizations", `provider profile unresolved:${realization.provider_profile_ref}`);
  for (const binding of integrationBindings) {
    const realization = realizationById.get(binding.provider_realization_ref);
    if (!realization) fail("IK_REFERENCE_UNRESOLVED", "/integration_bindings", `provider realization unresolved:${binding.provider_realization_ref}`);
    const profile = profileById.get(realization.provider_profile_ref)!;
    if (profile.concern !== binding.concern) fail("IK_CONCERN_MISMATCH", "/integration_bindings", `binding/provider concern mismatch:${binding.binding_id}`);
    if (!failureById.has(binding.failure_mapping_ref)) fail("IK_REFERENCE_UNRESOLVED", "/integration_bindings", `failure mapping unresolved:${binding.failure_mapping_ref}`);
    if (binding.serialization_profile_ref !== null && !serializationById.has(binding.serialization_profile_ref)) fail("IK_REFERENCE_UNRESOLVED", "/integration_bindings", `serialization profile unresolved:${binding.serialization_profile_ref}`);
  }
  for (const receipt of runtimeReceipts) if (!bindingById.has(receipt.binding_ref)) fail("IK_REFERENCE_UNRESOLVED", "/runtime_receipts", `binding unresolved:${receipt.binding_ref}`);

  return deepFreeze({ schema_version: "domainspec.integration-kernel/v2-candidate", kernel_id: reference(value.kernel_id, "/kernel_id"), definition_pack_sha256: value.definition_pack_sha256, integration_bindings: Object.freeze(integrationBindings), provider_profiles: Object.freeze(providerProfiles), provider_realizations: Object.freeze(providerRealizations), serialization_profiles: Object.freeze(serializationProfiles), failure_mappings: Object.freeze(failureMappings), runtime_receipts: Object.freeze(runtimeReceipts), runtime_guarantees_observed: false, authority_effect: "none" });
}

export function compileIntegrationKernelV2(value: unknown): CompiledIntegrationKernelV2 {
  const kernel = validateIntegrationKernelV2(value);
  return deepFreeze({ ...kernel, kernel_digest: sha256(canonicalJson(kernel)) });
}
