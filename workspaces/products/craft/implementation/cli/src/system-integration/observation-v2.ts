import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { INTEGRATION_OBSERVATION_STAGES, type IntegrationRuntimeReceiptV1 } from "./kernel-v2-types.js";

type AttributeValue = string | number | boolean;
type UnknownRecord = Record<string, unknown>;

export interface IntegrationDisclosurePolicyV1 {
  readonly policy_id: string;
  readonly allowed_attribute_keys: readonly string[];
  readonly max_attribute_count: number;
  readonly max_string_length: number;
  readonly forbidden_key_fragments: readonly string[];
  readonly authority_effect: "none";
}

export interface OrodiObservationBindingV1 {
  readonly binding_id: string;
  readonly observation_selector: string;
  readonly projection_mapper_ref: string;
  readonly orodi_adapter_ref: string;
  readonly evaluator_ref: string;
  readonly disclosure_policy_ref: string;
  readonly edge_sequence: readonly ["runtime", "observer", "orodi-adapter", "orodi-evaluator"];
  readonly return_edge: "prohibited";
  readonly runtime_control_capabilities: Readonly<{ select_retries: false; write_provider_state: false; call_apis: false; deploy: false; enact_business_effects: false }>;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface IntegrationObservationV1 {
  readonly schema_version: "domainspec.integration-observation/v1-candidate";
  readonly observation_id: string;
  readonly source_receipt_digest: string;
  readonly binding_ref: string;
  readonly operation_ref: string | null;
  readonly stage: IntegrationRuntimeReceiptV1["observed_stage"];
  readonly outcome: IntegrationRuntimeReceiptV1["outcome"];
  readonly observed_at: string;
  readonly duration_ms: number | null;
  readonly correlation_ref: string | null;
  readonly sanitized_attributes: Readonly<Record<string, AttributeValue>>;
  readonly evidence_refs: readonly string[];
  readonly claim_ceiling: IntegrationRuntimeReceiptV1["claim_ceiling"];
  readonly orodi_binding_ref: string;
  readonly immutable: true;
  readonly authority_effect: "none";
}

export class IntegrationObservationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) { super(message); this.name = "IntegrationObservationError"; }
}

function fail(code: string, pointer: string, message: string): never { throw new IntegrationObservationError(code, pointer, message); }
function object(value: unknown, pointer: string): asserts value is UnknownRecord { if (value === null || typeof value !== "object" || Array.isArray(value)) fail("OBS_SCHEMA", pointer, "expected object"); }
function exact(value: unknown, fields: readonly string[], pointer: string): asserts value is UnknownRecord { object(value, pointer); if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...fields].sort())) fail("OBS_SCHEMA", pointer, "unexpected or missing member"); }
function text(value: unknown, pointer: string): string { if (typeof value !== "string" || !value.trim()) fail("OBS_SCHEMA", pointer, "expected non-empty text"); return value; }
function integer(value: unknown, pointer: string, minimum = 0): number { if (!Number.isSafeInteger(value) || (value as number) < minimum) fail("OBS_SCHEMA", pointer, `expected integer >= ${minimum}`); return value as number; }
function texts(value: unknown, pointer: string): readonly string[] { if (!Array.isArray(value)) fail("OBS_SCHEMA", pointer, "expected text array"); const result = value.map((item, index) => text(item, `${pointer}/${index}`)); if (new Set(result).size !== result.length) fail("OBS_DUPLICATE", pointer, "duplicate value"); return Object.freeze([...result].sort()); }
function freeze<T>(value: T): T { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; }

export function validateOrodiObservationBindingV1(value: unknown): OrodiObservationBindingV1 {
  exact(value, ["binding_id", "observation_selector", "projection_mapper_ref", "orodi_adapter_ref", "evaluator_ref", "disclosure_policy_ref", "edge_sequence", "return_edge", "runtime_control_capabilities", "evidence_boundary", "authority_effect"], "/orodi_binding");
  if (canonicalJson(value.edge_sequence) !== canonicalJson(["runtime", "observer", "orodi-adapter", "orodi-evaluator"]) || value.return_edge !== "prohibited") fail("OBS_RETURN_EDGE", "/orodi_binding", "ORODI projection must be one-way");
  exact(value.runtime_control_capabilities, ["select_retries", "write_provider_state", "call_apis", "deploy", "enact_business_effects"], "/orodi_binding/runtime_control_capabilities");
  if (Object.values(value.runtime_control_capabilities).some(item => item !== false)) fail("OBS_ACTUATION", "/orodi_binding/runtime_control_capabilities", "ORODI cannot actuate runtime or provider behavior");
  if (value.authority_effect !== "none") fail("OBS_AUTHORITY", "/orodi_binding/authority_effect", "authority growth forbidden");
  return freeze({ binding_id: text(value.binding_id, "/orodi_binding/binding_id"), observation_selector: text(value.observation_selector, "/orodi_binding/observation_selector"), projection_mapper_ref: text(value.projection_mapper_ref, "/orodi_binding/projection_mapper_ref"), orodi_adapter_ref: text(value.orodi_adapter_ref, "/orodi_binding/orodi_adapter_ref"), evaluator_ref: text(value.evaluator_ref, "/orodi_binding/evaluator_ref"), disclosure_policy_ref: text(value.disclosure_policy_ref, "/orodi_binding/disclosure_policy_ref"), edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: text(value.evidence_boundary, "/orodi_binding/evidence_boundary"), authority_effect: "none" });
}

export function validateIntegrationDisclosurePolicyV1(value: unknown): IntegrationDisclosurePolicyV1 {
  exact(value, ["policy_id", "allowed_attribute_keys", "max_attribute_count", "max_string_length", "forbidden_key_fragments", "authority_effect"], "/disclosure_policy");
  if (value.authority_effect !== "none") fail("OBS_AUTHORITY", "/disclosure_policy/authority_effect", "authority growth forbidden");
  const allowed = texts(value.allowed_attribute_keys, "/disclosure_policy/allowed_attribute_keys"); const forbidden = texts(value.forbidden_key_fragments, "/disclosure_policy/forbidden_key_fragments").map(item => item.toLowerCase());
  if (allowed.some(key => forbidden.some(fragment => key.toLowerCase().includes(fragment)))) fail("OBS_DISCLOSURE", "/disclosure_policy/allowed_attribute_keys", "allowlist contains a forbidden key fragment");
  return freeze({ policy_id: text(value.policy_id, "/disclosure_policy/policy_id"), allowed_attribute_keys: allowed, max_attribute_count: integer(value.max_attribute_count, "/disclosure_policy/max_attribute_count", 1), max_string_length: integer(value.max_string_length, "/disclosure_policy/max_string_length", 1), forbidden_key_fragments: Object.freeze(forbidden), authority_effect: "none" });
}

export function projectIntegrationObservation(input: {
  readonly observation_id: string;
  readonly receipt: IntegrationRuntimeReceiptV1;
  readonly duration_ms: number | null;
  readonly attributes: Readonly<Record<string, unknown>>;
  readonly evidence_refs: readonly string[];
  readonly disclosure_policy: IntegrationDisclosurePolicyV1;
  readonly orodi_binding: OrodiObservationBindingV1;
}): IntegrationObservationV1 {
  const policy = validateIntegrationDisclosurePolicyV1(input.disclosure_policy); const binding = validateOrodiObservationBindingV1(input.orodi_binding);
  if (binding.disclosure_policy_ref !== policy.policy_id) fail("OBS_REFERENCE_UNRESOLVED", "/orodi_binding/disclosure_policy_ref", "disclosure policy mismatch");
  if (input.receipt.claim_ceiling !== input.receipt.observed_stage || !INTEGRATION_OBSERVATION_STAGES.includes(input.receipt.observed_stage)) fail("OBS_CLAIM", "/receipt/claim_ceiling", "receipt claim is not bounded to its observed stage");
  const keys = Object.keys(input.attributes).sort(); if (keys.length > policy.max_attribute_count) fail("OBS_DISCLOSURE", "/attributes", "attribute count exceeds policy");
  const allowed = new Set(policy.allowed_attribute_keys); const sanitized: Record<string, AttributeValue> = {};
  for (const key of keys) { if (!allowed.has(key) || policy.forbidden_key_fragments.some(fragment => key.toLowerCase().includes(fragment))) fail("OBS_DISCLOSURE", `/attributes/${key}`, "attribute key is not disclosure-safe"); const value = input.attributes[key]; if (!["string", "number", "boolean"].includes(typeof value) || (typeof value === "number" && !Number.isFinite(value)) || (typeof value === "string" && value.length > policy.max_string_length)) fail("OBS_DISCLOSURE", `/attributes/${key}`, "attribute value is not disclosure-safe"); sanitized[key] = value as AttributeValue; }
  const duration = input.duration_ms === null ? null : integer(input.duration_ms, "/duration_ms"); const evidence = texts(input.evidence_refs, "/evidence_refs");
  return freeze({ schema_version: "domainspec.integration-observation/v1-candidate", observation_id: text(input.observation_id, "/observation_id"), source_receipt_digest: sha256(canonicalJson(input.receipt)), binding_ref: input.receipt.binding_ref, operation_ref: input.receipt.operation_ref, stage: input.receipt.observed_stage, outcome: input.receipt.outcome, observed_at: input.receipt.observed_at, duration_ms: duration, correlation_ref: input.receipt.correlation_ref, sanitized_attributes: Object.freeze(sanitized), evidence_refs: evidence, claim_ceiling: input.receipt.claim_ceiling, orodi_binding_ref: binding.binding_id, immutable: true, authority_effect: "none" });
}
