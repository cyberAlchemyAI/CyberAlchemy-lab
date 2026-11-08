import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { compileIntegrationKernelV2, validateIntegrationKernelV2 } from "./kernel-v2.js";
import type {
  ApiFailureCaseV1,
  ApiFailureMappingV1,
  ApiMappingV1,
  ApiResiliencePolicyV1,
  AuthenticationBindingV1,
  CompiledExternalApiCompositionV2,
  ExternalApiBindingV1,
  ExternalApiCompositionV2,
  ExternalApiContractV1,
  ExternalApiOperationV1,
  InboundEndpointBindingV1,
  WebhookBindingV1,
} from "./external-api-v2-types.js";

const REF = /^[A-Za-z][A-Za-z0-9]*(?:[-.:/#][A-Za-z0-9]+)*$/;
type UnknownRecord = Record<string, unknown>;

export class ExternalApiCompositionError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) { super(message); this.name = "ExternalApiCompositionError"; }
}

function fail(code: string, pointer: string, message: string): never { throw new ExternalApiCompositionError(code, pointer, message); }
function object(value: unknown, pointer: string): asserts value is UnknownRecord { if (value === null || typeof value !== "object" || Array.isArray(value)) fail("API_SCHEMA", pointer, "expected object"); }
function exact(value: unknown, fields: readonly string[], pointer: string): asserts value is UnknownRecord { object(value, pointer); if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...fields].sort())) fail("API_SCHEMA", pointer, "unexpected or missing member"); }
function ref(value: unknown, pointer: string): string { if (typeof value !== "string" || !REF.test(value)) fail("API_REFERENCE", pointer, "invalid reference"); return value; }
function text(value: unknown, pointer: string): string { if (typeof value !== "string" || !value.trim()) fail("API_SCHEMA", pointer, "expected non-empty text"); return value; }
function bool(value: unknown, pointer: string): boolean { if (typeof value !== "boolean") fail("API_SCHEMA", pointer, "expected boolean"); return value; }
function integer(value: unknown, pointer: string, minimum: number): number { if (!Number.isSafeInteger(value) || (value as number) < minimum) fail("API_SCHEMA", pointer, `expected integer >= ${minimum}`); return value as number; }
function oneOf<T extends string>(value: unknown, allowed: readonly T[], pointer: string): T { if (!allowed.includes(value as T)) fail("API_SCHEMA", pointer, `expected one of:${allowed.join(",")}`); return value as T; }
function records(value: unknown, pointer: string, allowEmpty = true): readonly unknown[] { if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("API_SCHEMA", pointer, "expected record array"); return value; }
function refs(value: unknown, pointer: string, allowEmpty = true): readonly string[] { if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("API_SCHEMA", pointer, "expected reference array"); const result = value.map((item, index) => ref(item, `${pointer}/${index}`)); if (new Set(result).size !== result.length) fail("API_DUPLICATE", pointer, "duplicate reference"); return Object.freeze([...result].sort()); }
function nullableRef(value: unknown, pointer: string): string | null { return value === null ? null : ref(value, pointer); }
function identities<T>(values: readonly T[], select: (value: T) => string, pointer: string): ReadonlyMap<string, T> { const result = new Map<string, T>(); for (const value of values) { const id = select(value); if (result.has(id)) fail("API_DUPLICATE", pointer, `duplicate identity:${id}`); result.set(id, value); } return result; }
function freeze<T>(value: T): T { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; }
function member(value: unknown, pointer: string): string { if (typeof value !== "string" || !/^[A-Za-z][A-Za-z0-9_]*$/.test(value)) fail("API_SCHEMA", pointer, "invalid member name"); return value; }
function pathMembers(value: unknown, pointer: string): readonly string[] { if (!Array.isArray(value) || value.length > 64) fail("API_SCHEMA", pointer, "expected bounded member path"); return Object.freeze(value.map((item, index) => member(item, `${pointer}/${index}`))); }
function inputPaths(value: unknown, pointer: string) {
  const rows = records(value, pointer, false).map((entry, index) => { const p = `${pointer}/${index}`; exact(entry, ["parameter", "path"], p); return Object.freeze({ parameter: member(entry.parameter, `${p}/parameter`), path: pathMembers(entry.path, `${p}/path`) }); });
  identities(rows, item => item.parameter, pointer); return Object.freeze(rows);
}
function requestParameters(value: unknown, pointer: string) {
  const rows = records(value, pointer, false).map((entry, index) => {
    const p = `${pointer}/${index}`; exact(entry, ["parameter", "source"], p); object(entry.source, `${p}/source`); exact(entry.source, ["kind", "path"], `${p}/source`);
    const kind = oneOf(entry.source.kind, ["mapping-result", "source-body"] as const, `${p}/source/kind`);
    return Object.freeze({ parameter: member(entry.parameter, `${p}/parameter`), source: Object.freeze({ kind, path: pathMembers(entry.source.path, `${p}/source/path`) }) });
  });
  identities(rows, item => item.parameter, pointer);
  if (!rows.some(item => item.source.kind === "mapping-result")) fail("API_REQUEST_COMPOSITION", pointer, "request must include a Mapping result");
  return Object.freeze(rows);
}

function operation(value: unknown, pointer: string): ExternalApiOperationV1 {
  exact(value, ["operation_id", "request_type_ref", "result_type_ref", "failure_outcome_refs", "safety"], pointer);
  return Object.freeze({ operation_id: ref(value.operation_id, `${pointer}/operation_id`), request_type_ref: ref(value.request_type_ref, `${pointer}/request_type_ref`), result_type_ref: ref(value.result_type_ref, `${pointer}/result_type_ref`), failure_outcome_refs: refs(value.failure_outcome_refs, `${pointer}/failure_outcome_refs`, false), safety: oneOf(value.safety, ["safe", "idempotent", "unsafe"] as const, `${pointer}/safety`) });
}

function contract(value: unknown, pointer: string): ExternalApiContractV1 {
  exact(value, ["contract_id", "concern", "consumer_role_refs", "operations", "authority_effect"], pointer);
  if (value.concern !== "external-api" || value.authority_effect !== "none") fail("API_CONTRACT", pointer, "external API contract concern or authority invalid");
  const operations = records(value.operations, `${pointer}/operations`, false).map((entry, index) => operation(entry, `${pointer}/operations/${index}`)).sort((a, b) => a.operation_id.localeCompare(b.operation_id));
  identities(operations, item => item.operation_id, `${pointer}/operations`);
  return Object.freeze({ contract_id: ref(value.contract_id, `${pointer}/contract_id`), concern: "external-api", consumer_role_refs: refs(value.consumer_role_refs, `${pointer}/consumer_role_refs`, false), operations: Object.freeze(operations), authority_effect: "none" });
}

function mapping(value: unknown, pointer: string): ApiMappingV1 {
  object(value, pointer);
  const direction = oneOf(value.direction, ["protocol-to-application", "application-to-protocol"] as const, `${pointer}/direction`);
  const target = ref(value.target_ref, `${pointer}/target_ref`);
  const request = direction === "protocol-to-application" && target.endsWith("#request");
  exact(value, request ? ["mapping_id", "mapper_ref", "direction", "source_ref", "target_ref", "total", "input_paths", "request_parameters"] : ["mapping_id", "mapper_ref", "direction", "source_ref", "target_ref", "total"], pointer);
  return Object.freeze({ mapping_id: ref(value.mapping_id, `${pointer}/mapping_id`), mapper_ref: ref(value.mapper_ref, `${pointer}/mapper_ref`), direction, source_ref: ref(value.source_ref, `${pointer}/source_ref`), target_ref: target, total: bool(value.total, `${pointer}/total`), ...(request ? { input_paths: inputPaths(value.input_paths, `${pointer}/input_paths`), request_parameters: requestParameters(value.request_parameters, `${pointer}/request_parameters`) } : {}) });
}

function authentication(value: unknown, pointer: string): AuthenticationBindingV1 {
  exact(value, ["binding_id", "integration_boundary_ref", "scheme", "credential_slot_refs", "credential_provider_ref", "rotation_policy_ref", "evidence_boundary", "contains_secret_values", "authority_effect"], pointer);
  if (value.contains_secret_values !== false) fail("API_SECRET_VALUE", `${pointer}/contains_secret_values`, "authentication bindings contain references, never secret values");
  if (value.authority_effect !== "none") fail("API_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: ref(value.binding_id, `${pointer}/binding_id`), integration_boundary_ref: ref(value.integration_boundary_ref, `${pointer}/integration_boundary_ref`), scheme: oneOf(value.scheme, ["api-key", "basic", "bearer", "oauth2-client-credentials", "mutual-tls", "signed-request"] as const, `${pointer}/scheme`), credential_slot_refs: refs(value.credential_slot_refs, `${pointer}/credential_slot_refs`, false), credential_provider_ref: ref(value.credential_provider_ref, `${pointer}/credential_provider_ref`), rotation_policy_ref: nullableRef(value.rotation_policy_ref, `${pointer}/rotation_policy_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), contains_secret_values: false, authority_effect: "none" });
}

function resilience(value: unknown, pointer: string): ApiResiliencePolicyV1 {
  exact(value, ["policy_id", "timeout_ms", "max_attempts", "backoff_ref", "concurrency_policy_ref", "circuit_policy_ref", "retry_safety", "idempotency_key_expression", "evidence_boundary"], pointer);
  const retrySafety = oneOf(value.retry_safety, ["safe-operation", "idempotency-key-required", "retry-forbidden"] as const, `${pointer}/retry_safety`);
  const key = value.idempotency_key_expression === null ? null : text(value.idempotency_key_expression, `${pointer}/idempotency_key_expression`);
  const maxAttempts = integer(value.max_attempts, `${pointer}/max_attempts`, 1);
  if (retrySafety === "idempotency-key-required" && key === null) fail("API_RETRY_SAFETY", `${pointer}/idempotency_key_expression`, "idempotent retry requires a key");
  if (retrySafety !== "idempotency-key-required" && key !== null) fail("API_RETRY_SAFETY", `${pointer}/idempotency_key_expression`, "key is only valid for idempotency-key retries");
  if (retrySafety === "retry-forbidden" && maxAttempts !== 1) fail("API_RETRY_SAFETY", `${pointer}/max_attempts`, "retry-forbidden requires one attempt");
  return Object.freeze({ policy_id: ref(value.policy_id, `${pointer}/policy_id`), timeout_ms: integer(value.timeout_ms, `${pointer}/timeout_ms`, 1), max_attempts: maxAttempts, backoff_ref: nullableRef(value.backoff_ref, `${pointer}/backoff_ref`), concurrency_policy_ref: nullableRef(value.concurrency_policy_ref, `${pointer}/concurrency_policy_ref`), circuit_policy_ref: nullableRef(value.circuit_policy_ref, `${pointer}/circuit_policy_ref`), retry_safety: retrySafety, idempotency_key_expression: key, evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`) });
}

function failureCase(value: unknown, pointer: string): ApiFailureCaseV1 {
  exact(value, ["category", "matcher_ref", "failure_outcome_ref"], pointer);
  return Object.freeze({ category: oneOf(value.category, ["protocol", "provider", "authentication", "timeout", "malformed-response"] as const, `${pointer}/category`), matcher_ref: ref(value.matcher_ref, `${pointer}/matcher_ref`), failure_outcome_ref: ref(value.failure_outcome_ref, `${pointer}/failure_outcome_ref`) });
}

function failureMapping(value: unknown, pointer: string): ApiFailureMappingV1 {
  exact(value, ["mapping_id", "external_api_contract_ref", "kernel_failure_mapping_ref", "cases", "unknown_fallback_ref", "evidence_boundary", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("API_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  const cases = records(value.cases, `${pointer}/cases`, false).map((entry, index) => failureCase(entry, `${pointer}/cases/${index}`)).sort((a, b) => `${a.category}:${a.matcher_ref}`.localeCompare(`${b.category}:${b.matcher_ref}`));
  identities(cases, item => `${item.category}:${item.matcher_ref}`, `${pointer}/cases`);
  return Object.freeze({ mapping_id: ref(value.mapping_id, `${pointer}/mapping_id`), external_api_contract_ref: ref(value.external_api_contract_ref, `${pointer}/external_api_contract_ref`), kernel_failure_mapping_ref: ref(value.kernel_failure_mapping_ref, `${pointer}/kernel_failure_mapping_ref`), cases: Object.freeze(cases), unknown_fallback_ref: ref(value.unknown_fallback_ref, `${pointer}/unknown_fallback_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function inbound(value: unknown, pointer: string): InboundEndpointBindingV1 {
  exact(value, ["binding_id", "integration_binding_ref", "protocol_operation_ref", "request_mapper_ref", "operation_ref", "response_mapper_ref", "authentication_binding_ref", "failure_mapping_ref", "provider_realization_ref", "evidence_boundary", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("API_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: ref(value.binding_id, `${pointer}/binding_id`), integration_binding_ref: ref(value.integration_binding_ref, `${pointer}/integration_binding_ref`), protocol_operation_ref: ref(value.protocol_operation_ref, `${pointer}/protocol_operation_ref`), request_mapper_ref: ref(value.request_mapper_ref, `${pointer}/request_mapper_ref`), operation_ref: ref(value.operation_ref, `${pointer}/operation_ref`), response_mapper_ref: ref(value.response_mapper_ref, `${pointer}/response_mapper_ref`), authentication_binding_ref: nullableRef(value.authentication_binding_ref, `${pointer}/authentication_binding_ref`), failure_mapping_ref: ref(value.failure_mapping_ref, `${pointer}/failure_mapping_ref`), provider_realization_ref: ref(value.provider_realization_ref, `${pointer}/provider_realization_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function outbound(value: unknown, pointer: string): ExternalApiBindingV1 {
  exact(value, ["binding_id", "integration_binding_ref", "external_api_contract_ref", "contract_operation_ref", "provider_operation_ref", "request_mapper_ref", "response_mapper_ref", "authentication_binding_ref", "resilience_policy_ref", "failure_mapping_ref", "provider_realization_ref", "evidence_boundary", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("API_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: ref(value.binding_id, `${pointer}/binding_id`), integration_binding_ref: ref(value.integration_binding_ref, `${pointer}/integration_binding_ref`), external_api_contract_ref: ref(value.external_api_contract_ref, `${pointer}/external_api_contract_ref`), contract_operation_ref: ref(value.contract_operation_ref, `${pointer}/contract_operation_ref`), provider_operation_ref: ref(value.provider_operation_ref, `${pointer}/provider_operation_ref`), request_mapper_ref: ref(value.request_mapper_ref, `${pointer}/request_mapper_ref`), response_mapper_ref: ref(value.response_mapper_ref, `${pointer}/response_mapper_ref`), authentication_binding_ref: nullableRef(value.authentication_binding_ref, `${pointer}/authentication_binding_ref`), resilience_policy_ref: ref(value.resilience_policy_ref, `${pointer}/resilience_policy_ref`), failure_mapping_ref: ref(value.failure_mapping_ref, `${pointer}/failure_mapping_ref`), provider_realization_ref: ref(value.provider_realization_ref, `${pointer}/provider_realization_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function webhook(value: unknown, pointer: string): WebhookBindingV1 {
  exact(value, ["binding_id", "inbound_endpoint_binding_ref", "sender_verification_ref", "replay_protection_ref", "external_event_id_expression", "acknowledgement_policy", "application_completion_inferred", "authority_effect"], pointer);
  if (value.application_completion_inferred !== false) fail("API_WEBHOOK_CLAIM", `${pointer}/application_completion_inferred`, "webhook acknowledgement is not application completion");
  if (value.authority_effect !== "none") fail("API_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: ref(value.binding_id, `${pointer}/binding_id`), inbound_endpoint_binding_ref: ref(value.inbound_endpoint_binding_ref, `${pointer}/inbound_endpoint_binding_ref`), sender_verification_ref: ref(value.sender_verification_ref, `${pointer}/sender_verification_ref`), replay_protection_ref: ref(value.replay_protection_ref, `${pointer}/replay_protection_ref`), external_event_id_expression: text(value.external_event_id_expression, `${pointer}/external_event_id_expression`), acknowledgement_policy: oneOf(value.acknowledgement_policy, ["ack-after-verification", "ack-after-application-commit"] as const, `${pointer}/acknowledgement_policy`), application_completion_inferred: false, authority_effect: "none" });
}

export function validateExternalApiCompositionV2(value: unknown): ExternalApiCompositionV2 {
  exact(value, ["schema_version", "composition_id", "integration_kernel", "external_api_contracts", "api_mappings", "authentication_bindings", "resilience_policies", "api_failure_mappings", "inbound_endpoint_bindings", "external_api_bindings", "webhook_bindings", "runtime_calls_observed", "authority_effect"], "/");
  if (value.schema_version !== "domainspec.external-api-composition/v2-candidate") fail("API_SCHEMA", "/schema_version", "unsupported schema");
  if (value.runtime_calls_observed !== false) fail("API_RUNTIME_CLAIM", "/runtime_calls_observed", "formation is not API-call evidence");
  if (value.authority_effect !== "none") fail("API_AUTHORITY", "/authority_effect", "authority growth forbidden");
  const kernel = validateIntegrationKernelV2(value.integration_kernel);
  // Inbound endpoints do not acquire an unrelated outbound contract.
  // Outbound bindings below still require their exact referenced contract.
  const contracts = records(value.external_api_contracts, "/external_api_contracts").map((entry, index) => contract(entry, `/external_api_contracts/${index}`)).sort((a, b) => a.contract_id.localeCompare(b.contract_id));
  const mappings = records(value.api_mappings, "/api_mappings", false).map((entry, index) => mapping(entry, `/api_mappings/${index}`)).sort((a, b) => a.mapping_id.localeCompare(b.mapping_id));
  const auth = records(value.authentication_bindings, "/authentication_bindings").map((entry, index) => authentication(entry, `/authentication_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const resiliencePolicies = records(value.resilience_policies, "/resilience_policies").map((entry, index) => resilience(entry, `/resilience_policies/${index}`)).sort((a, b) => a.policy_id.localeCompare(b.policy_id));
  const failureMappings = records(value.api_failure_mappings, "/api_failure_mappings").map((entry, index) => failureMapping(entry, `/api_failure_mappings/${index}`)).sort((a, b) => a.mapping_id.localeCompare(b.mapping_id));
  const inboundBindings = records(value.inbound_endpoint_bindings, "/inbound_endpoint_bindings").map((entry, index) => inbound(entry, `/inbound_endpoint_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const outboundBindings = records(value.external_api_bindings, "/external_api_bindings").map((entry, index) => outbound(entry, `/external_api_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const webhooks = records(value.webhook_bindings, "/webhook_bindings").map((entry, index) => webhook(entry, `/webhook_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const contractById = identities(contracts, item => item.contract_id, "/external_api_contracts");
  identities(mappings, item => item.mapping_id, "/api_mappings"); const mappingByMapper = identities(mappings, item => item.mapper_ref, "/api_mappings");
  const authById = identities(auth, item => item.binding_id, "/authentication_bindings"); const resilienceById = identities(resiliencePolicies, item => item.policy_id, "/resilience_policies");
  const apiFailureById = identities(failureMappings, item => item.mapping_id, "/api_failure_mappings"); const inboundById = identities(inboundBindings, item => item.binding_id, "/inbound_endpoint_bindings");
  identities(outboundBindings, item => item.binding_id, "/external_api_bindings"); identities(webhooks, item => item.binding_id, "/webhook_bindings");
  const integrationById = identities(kernel.integration_bindings, item => item.binding_id, "/integration_kernel/integration_bindings"); const realizationById = identities(kernel.provider_realizations, item => item.realization_id, "/integration_kernel/provider_realizations"); const kernelFailureById = identities(kernel.failure_mappings, item => item.mapping_id, "/integration_kernel/failure_mappings");
  for (const item of failureMappings) { const contractValue = contractById.get(item.external_api_contract_ref); const kernelFailure = kernelFailureById.get(item.kernel_failure_mapping_ref); if (!contractValue || !kernelFailure) fail("API_REFERENCE_UNRESOLVED", "/api_failure_mappings", `failure mapping dependency unresolved:${item.mapping_id}`); const outcomes = new Set(contractValue.operations.flatMap(operationValue => operationValue.failure_outcome_refs)); for (const failureCaseValue of item.cases) if (!outcomes.has(failureCaseValue.failure_outcome_ref)) fail("API_FAILURE_SURFACE", "/api_failure_mappings", `outcome outside contract:${failureCaseValue.failure_outcome_ref}`); if (item.unknown_fallback_ref !== kernelFailure.unknown_failure_outcome_ref) fail("API_FAILURE_SURFACE", "/api_failure_mappings", `unknown fallback disagrees with D48:${item.mapping_id}`); }
  for (const binding of inboundBindings) {
    const integration = integrationById.get(binding.integration_binding_ref); const request = mappingByMapper.get(binding.request_mapper_ref); const response = mappingByMapper.get(binding.response_mapper_ref); const authValue = binding.authentication_binding_ref === null ? null : authById.get(binding.authentication_binding_ref);
    if (!integration || integration.concern !== "external-api" || integration.direction === "outbound" || !realizationById.has(binding.provider_realization_ref) || !kernelFailureById.has(binding.failure_mapping_ref)) fail("API_REFERENCE_UNRESOLVED", "/inbound_endpoint_bindings", `inbound dependency unresolved:${binding.binding_id}`);
    if (!request || request.direction !== "protocol-to-application" || request.source_ref !== `${binding.protocol_operation_ref}#request` || request.target_ref !== `${binding.operation_ref}#request` || !response || response.direction !== "application-to-protocol" || response.source_ref !== `${binding.operation_ref}#result` || response.target_ref !== `${binding.protocol_operation_ref}#response`) fail("API_MAPPING_COLLAPSE", "/inbound_endpoint_bindings", `protocol/application mapping invalid:${binding.binding_id}`);
    if (binding.authentication_binding_ref !== null && (!authValue || authValue.integration_boundary_ref !== binding.binding_id)) fail("API_AUTH_BINDING", "/inbound_endpoint_bindings", `authentication reference missing or boundary mismatch:${binding.binding_id}`);
  }
  for (const binding of outboundBindings) {
    const integration = integrationById.get(binding.integration_binding_ref); const contractValue = contractById.get(binding.external_api_contract_ref); const operationValue = contractValue?.operations.find(item => binding.contract_operation_ref === `${contractValue.contract_id}#${item.operation_id}`); const failureValue = apiFailureById.get(binding.failure_mapping_ref); const request = mappingByMapper.get(binding.request_mapper_ref); const response = mappingByMapper.get(binding.response_mapper_ref); const policy = resilienceById.get(binding.resilience_policy_ref); const authValue = binding.authentication_binding_ref === null ? null : authById.get(binding.authentication_binding_ref);
    if (!integration || integration.concern !== "external-api" || integration.direction === "inbound" || integration.contract_ref !== binding.external_api_contract_ref || !operationValue || !policy || !realizationById.has(binding.provider_realization_ref) || (!failureValue || failureValue.external_api_contract_ref !== binding.external_api_contract_ref)) fail("API_REFERENCE_UNRESOLVED", "/external_api_bindings", `outbound dependency unresolved:${binding.binding_id}`);
    if (!request || request.direction !== "application-to-protocol" || request.source_ref !== operationValue.request_type_ref || request.target_ref !== `${binding.provider_operation_ref}#request` || !response || response.direction !== "protocol-to-application" || response.source_ref !== `${binding.provider_operation_ref}#response` || response.target_ref !== operationValue.result_type_ref) fail("API_MAPPING_COLLAPSE", "/external_api_bindings", `contract/provider mapping invalid:${binding.binding_id}`);
    if ((operationValue.safety === "unsafe" && policy.retry_safety === "safe-operation") || (policy.max_attempts > 1 && operationValue.safety === "unsafe" && policy.retry_safety !== "idempotency-key-required")) fail("API_RETRY_SAFETY", "/external_api_bindings", `unsafe operation retry is not idempotency-bound:${binding.binding_id}`);
    if (binding.authentication_binding_ref !== null && (!authValue || authValue.integration_boundary_ref !== binding.binding_id)) fail("API_AUTH_BINDING", "/external_api_bindings", `authentication reference missing or boundary mismatch:${binding.binding_id}`);
  }
  for (const item of webhooks) { const endpoint = inboundById.get(item.inbound_endpoint_binding_ref); if (!endpoint) fail("API_REFERENCE_UNRESOLVED", "/webhook_bindings", `inbound endpoint unresolved:${item.inbound_endpoint_binding_ref}`); if (endpoint.authentication_binding_ref === null) fail("API_WEBHOOK_AUTH", "/webhook_bindings", `webhook sender authenticity is unbound:${item.binding_id}`); }
  return freeze({ schema_version: "domainspec.external-api-composition/v2-candidate", composition_id: ref(value.composition_id, "/composition_id"), integration_kernel: kernel, external_api_contracts: Object.freeze(contracts), api_mappings: Object.freeze(mappings), authentication_bindings: Object.freeze(auth), resilience_policies: Object.freeze(resiliencePolicies), api_failure_mappings: Object.freeze(failureMappings), inbound_endpoint_bindings: Object.freeze(inboundBindings), external_api_bindings: Object.freeze(outboundBindings), webhook_bindings: Object.freeze(webhooks), runtime_calls_observed: false, authority_effect: "none" });
}

export function compileExternalApiCompositionV2(value: unknown): CompiledExternalApiCompositionV2 {
  const composition = validateExternalApiCompositionV2(value); const compiled = { ...composition, integration_kernel: compileIntegrationKernelV2(composition.integration_kernel) };
  return freeze({ ...compiled, composition_digest: sha256(canonicalJson(compiled)) });
}
