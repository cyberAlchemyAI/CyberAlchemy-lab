import {
  canonicalJson,
  canonicalizeJson,
  deepFreeze,
  sha256HexText,
} from "../../intent-route-resolver/index.mjs";

export const DECISION_PROFILE_SCHEMA_VERSION = "are.decision-profile/v1";
const SHA256 = /^[a-f0-9]{64}$/;

function plainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function stringArray(value, path, reasons) {
  if (!Array.isArray(value)) {
    reasons.push(`${path}.expected-array`);
    return [];
  }
  const normalized = value.map((item) => String(item).trim()).filter(Boolean);
  if (normalized.length !== value.length) reasons.push(`${path}.invalid-string`);
  if (new Set(normalized).size !== normalized.length) reasons.push(`${path}.duplicate`);
  return [...new Set(normalized)].sort();
}

function profileMaterial(profile) {
  const material = {...profile};
  delete material.profile_digest;
  delete material.routes;
  const normalize = (value) => [...new Set(Array.isArray(value) ? value.map((item) => String(item).trim()).filter(Boolean) : [])].sort();
  if (Array.isArray(material.route_policies)) {
    material.route_policies = material.route_policies.map((policy) => ({
      ...policy,
      objective_kinds: normalize(policy.objective_kinds),
      effect_classes: normalize(policy.effect_classes),
      signal_additions: normalize(policy.signal_additions),
      exclusion_additions: normalize(policy.exclusion_additions),
      provenance_ids: normalize(policy.provenance_ids),
    })).sort((left, right) => String(left.route_id).localeCompare(String(right.route_id)));
  }
  if (material.consequence) {
    material.consequence = {
      ...material.consequence,
      safe_effects: normalize(material.consequence.safe_effects),
      consequential_effects: normalize(material.consequence.consequential_effects),
      protected_effects: normalize(material.consequence.protected_effects),
    };
  }
  return canonicalizeJson(material);
}

export function computeDecisionProfileDigest(profile) {
  return sha256HexText(canonicalJson(profileMaterial(profile)));
}

export function admitDecisionProfile(input) {
  const reasons = [];
  if (!plainObject(input)) return deepFreeze({ok: false, reason_codes: ["profile.expected-object"]});
  if (input.schema_version !== DECISION_PROFILE_SCHEMA_VERSION) reasons.push("profile.unsupported-version");
  if (input.authority_effect !== "none") reasons.push("profile.authority-effect-forbidden");
  for (const key of ["profile_id", "profile_version"]) {
    if (typeof input[key] !== "string" || !input[key].trim()) reasons.push(`profile.${key}.required`);
  }
  if (!Array.isArray(input.provenance) || input.provenance.length === 0) reasons.push("profile.provenance.required");
  const provenanceIds = [];
  for (const [index, source] of (input.provenance ?? []).entries()) {
    if (!plainObject(source)) {
      reasons.push(`profile.provenance[${index}].expected-object`);
      continue;
    }
    provenanceIds.push(source.id);
    if (typeof source.id !== "string" || !source.id) reasons.push(`profile.provenance[${index}].id.required`);
    if (typeof source.path !== "string" || !source.path) reasons.push(`profile.provenance[${index}].path.required`);
    if (typeof source.sha256 !== "string" || !SHA256.test(source.sha256)) reasons.push(`profile.provenance[${index}].sha256.invalid`);
  }
  if (new Set(provenanceIds).size !== provenanceIds.length) reasons.push("profile.provenance.duplicate-id");
  const knownProvenance = new Set(provenanceIds);
  if (!Array.isArray(input.route_policies) || input.route_policies.length === 0) reasons.push("profile.route-policies.required");
  const routeIds = [];
  const routePolicies = [];
  for (const [index, policy] of (input.route_policies ?? []).entries()) {
    if (!plainObject(policy)) {
      reasons.push(`profile.route-policies[${index}].expected-object`);
      continue;
    }
    routeIds.push(policy.route_id);
    if (typeof policy.route_id !== "string" || !policy.route_id) reasons.push(`profile.route-policies[${index}].route_id.required`);
    if (policy.owner_gate_ref !== null && (typeof policy.owner_gate_ref !== "string" || !policy.owner_gate_ref.trim())) {
      reasons.push(`profile.route-policies[${index}].owner_gate_ref.invalid`);
    }
    const provenance = stringArray(policy.provenance_ids, `profile.route-policies[${index}].provenance_ids`, reasons);
    const missing = provenance.filter((id) => !knownProvenance.has(id));
    if (missing.length > 0) reasons.push(`profile.route-policies[${index}].provenance_ids.unknown:${missing.join(",")}`);
    if (!provenance.includes("route-registry")) reasons.push(`profile.route-policies[${index}].route-registry-provenance.required`);
    routePolicies.push(canonicalizeJson({
      ...policy,
      objective_kinds: stringArray(policy.objective_kinds, `profile.route-policies[${index}].objective_kinds`, reasons).map((item) => item.toLowerCase()),
      effect_classes: stringArray(policy.effect_classes, `profile.route-policies[${index}].effect_classes`, reasons).map((item) => item.toLowerCase()),
      signal_additions: stringArray(policy.signal_additions, `profile.route-policies[${index}].signal_additions`, reasons).map((item) => item.toLowerCase()),
      exclusion_additions: stringArray(policy.exclusion_additions, `profile.route-policies[${index}].exclusion_additions`, reasons).map((item) => item.toLowerCase()),
      provenance_ids: provenance,
    }));
  }
  if (new Set(routeIds).size !== routeIds.length) reasons.push("profile.route-policies.duplicate-id");
  if (!plainObject(input.consequence)) reasons.push("profile.consequence.required");
  const consequence = input.consequence ?? {};
  const safeEffects = stringArray(consequence.safe_effects, "profile.consequence.safe_effects", reasons);
  const consequentialEffects = stringArray(consequence.consequential_effects, "profile.consequence.consequential_effects", reasons);
  const protectedEffects = stringArray(consequence.protected_effects, "profile.consequence.protected_effects", reasons);
  const effectSet = [...safeEffects, ...consequentialEffects, ...protectedEffects];
  if (new Set(effectSet).size !== effectSet.length) reasons.push("profile.consequence.effect-classes-overlap");
  if (!plainObject(consequence.owner_gate_by_effect)) reasons.push("profile.consequence.owner-gate-map.required");
  for (const effect of protectedEffects) {
    if (typeof consequence.owner_gate_by_effect?.[effect] !== "string" || !consequence.owner_gate_by_effect[effect].trim()) reasons.push(`profile.consequence.owner-gate-missing:${effect}`);
  }
  if (!["gate"].includes(consequence.unknown_effect_behavior)) reasons.push("profile.consequence.unknown-effect-behavior");
  if (consequence.multiple_admissible_behavior !== "gate") reasons.push("profile.consequence.multiple-admissible-behavior");
  if (!Number.isInteger(consequence.max_direct_steps) || consequence.max_direct_steps < 1) reasons.push("profile.consequence.max-direct-steps");
  if (typeof input.profile_digest !== "string" || !SHA256.test(input.profile_digest)) reasons.push("profile.profile-digest.invalid");
  else if (computeDecisionProfileDigest(input) !== input.profile_digest) reasons.push("profile.profile-digest.mismatch");
  if (reasons.length > 0) return deepFreeze({ok: false, reason_codes: [...new Set(reasons)].sort()});
  return deepFreeze({ok: true, value: canonicalizeJson({...input, route_policies: routePolicies})});
}
