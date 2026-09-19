import {canonicalJson, canonicalizeJson, deepFreeze, sha256HexText} from "../../intent-route-resolver/index.mjs";

export const REQUEST_CONTEXT_SCHEMA_VERSION = "are.request-context/v1";

function list(value) {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.map((item) => String(item).trim()).filter(Boolean))].sort();
}

export function admitRequestContext(input) {
  const reasons = [];
  if (!input || typeof input !== "object" || Array.isArray(input)) return deepFreeze({ok: false, reason_codes: ["context.expected-object"]});
  if (input.schema_version !== REQUEST_CONTEXT_SCHEMA_VERSION) reasons.push("context.unsupported-version");
  if (typeof input.request_id !== "string" || !input.request_id.trim()) reasons.push("context.request-id-required");
  if (typeof input.raw_request !== "string" || !input.raw_request.trim()) reasons.push("context.raw-request-required");
  if (input.objective_kind !== null && input.objective_kind !== undefined && (typeof input.objective_kind !== "string" || !input.objective_kind.trim())) reasons.push("context.objective-kind-invalid");
  const postureValues = new Set(["explicit", "inferred", "unknown", "absent"]);
  const postureKeys = ["request_id", "raw_request", "objective_kind", "requested_effects", "target_refs", "constraints", "evidence_refs"];
  if (input.field_postures !== undefined && (!input.field_postures || typeof input.field_postures !== "object" || Array.isArray(input.field_postures))) reasons.push("context.field-postures-invalid");
  if (input.field_postures) for (const key of postureKeys) {
    if (!postureValues.has(input.field_postures[key])) reasons.push(`context.field-posture-invalid:${key}`);
  }
  if (reasons.length > 0) return deepFreeze({ok: false, reason_codes: reasons.sort()});
  const value = canonicalizeJson({
    schema_version: REQUEST_CONTEXT_SCHEMA_VERSION,
    request_id: input.request_id.trim(),
    raw_request: input.raw_request,
    objective_kind: input.objective_kind ? input.objective_kind.trim().toLowerCase() : null,
    requested_effects: list(input.requested_effects),
    target_refs: list(input.target_refs),
    constraints: list(input.constraints),
    evidence_refs: list(input.evidence_refs),
    field_postures: Object.fromEntries(postureKeys.map((key) => [key, input.field_postures?.[key] ?? "unknown"])),
  });
  return deepFreeze({ok: true, value, digest: sha256HexText(canonicalJson(value))});
}
