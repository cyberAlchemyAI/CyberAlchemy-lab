import {canonicalJson, canonicalizeJson, deepFreeze, sha256HexText} from "../../intent-route-resolver/index.mjs";
import {isVerifiedDecisionProfile} from "./verified-profile.mjs";

function finalize(material) {
  const normalized = canonicalizeJson(material);
  return deepFreeze(canonicalizeJson({...normalized, decision_digest: sha256HexText(canonicalJson(normalized))}));
}

function optionTrace(option, profile) {
  const candidate = option && typeof option === "object" && !Array.isArray(option) ? option : {};
  const rejectionReasons = [...new Set(Array.isArray(candidate.rejection_reasons) ? candidate.rejection_reasons.map(String) : [])].sort();
  if (candidate !== option) rejectionReasons.push("option.expected-object");
  if (typeof candidate.option_id !== "string" || !candidate.option_id.trim()) rejectionReasons.push("option.id-required");
  if (typeof candidate.route_id !== "string" || !candidate.route_id.trim()) rejectionReasons.push("option.route-required");
  if (!Array.isArray(candidate.effect_classes) || candidate.effect_classes.length === 0) rejectionReasons.push("option.effect-classes-required");
  if (typeof candidate.reversible !== "boolean") rejectionReasons.push("option.reversibility-required");
  if (candidate.owner_gate_ref !== null && candidate.owner_gate_ref !== undefined && (typeof candidate.owner_gate_ref !== "string" || !candidate.owner_gate_ref.trim())) rejectionReasons.push("option.owner-gate-invalid");
  const effectClasses = [...new Set((Array.isArray(candidate.effect_classes) ? candidate.effect_classes : []).map(String))].sort();
  const protectedEffects = effectClasses.filter((effect) => profile.consequence.protected_effects.includes(effect));
  const consequentialEffects = effectClasses.filter((effect) => profile.consequence.consequential_effects.includes(effect));
  const knownEffects = new Set([...profile.consequence.safe_effects, ...profile.consequence.consequential_effects, ...profile.consequence.protected_effects]);
  const unknownEffects = effectClasses.filter((effect) => !knownEffects.has(effect));
  const requiredOwnerGates = [...new Set([
    ...(candidate.owner_gate_ref ? [candidate.owner_gate_ref] : []),
    ...protectedEffects.map((effect) => profile.consequence.owner_gate_by_effect[effect]).filter(Boolean),
  ])].sort();
  if (candidate.structurally_admissible === false) rejectionReasons.push("option.structurally-inadmissible");
  if (protectedEffects.length > 0 && requiredOwnerGates.length === 0) rejectionReasons.push("option.protected-owner-gate-missing");
  const route = profile.routes.find((routeCandidate) => routeCandidate.route_id === candidate.route_id);
  if (!route) rejectionReasons.push("option.route-unknown");
  else if (route.lifecycle_state === "blocked") rejectionReasons.push("option.route-blocked");
  const consequential = candidate.reversible !== true || protectedEffects.length > 0 || consequentialEffects.length > 0 || unknownEffects.length > 0 || requiredOwnerGates.length > 0;
  return canonicalizeJson({option_id: candidate.option_id ?? null, route_id: candidate.route_id ?? null, effect_classes: effectClasses, reversible: candidate.reversible === true, protected_effects: protectedEffects, consequential_effects: consequentialEffects, unknown_effects: unknownEffects, required_owner_gate_refs: requiredOwnerGates, consequential, posture: rejectionReasons.length === 0 ? "admissible" : "rejected", rejection_reasons: [...new Set(rejectionReasons)].sort()});
}

export function evaluateContinuation(input, profile) {
  if (!isVerifiedDecisionProfile(profile)) return finalize({schema_version: "are.continuation-decision/v1", kind: "block", completion_digest: null, decision_profile_digest: null, options: [], selected_option_id: null, owner_gate_refs: [], provenance: [], reason_codes: ["profile.unverified"], authority_effect: "none"});
  const completion = input?.completion ?? {};
  const options = Array.isArray(input?.options) ? input.options : [];
  const evidenceRefs = Array.isArray(completion.evidence_refs) ? completion.evidence_refs.map(String) : [];
  const completionMaterial = canonicalizeJson({completion_id: completion.completion_id ?? null, status: completion.status ?? null, continuation_required: completion.continuation_required === true, evidence_refs: [...new Set(evidenceRefs)].sort()});
  const traces = options.map((option) => optionTrace(option, profile)).sort((a, b) => String(a.option_id).localeCompare(String(b.option_id)));
  const admissible = traces.filter((trace) => trace.posture === "admissible");
  const base = {schema_version: "are.continuation-decision/v1", completion_digest: sha256HexText(canonicalJson(completionMaterial)), decision_profile_digest: profile.profile_digest, options: traces, provenance: profile.provenance, authority_effect: "none"};
  if (!["completed"].includes(completion.status)) return finalize({...base, kind: "block", selected_option_id: null, owner_gate_refs: [], reason_codes: ["continuation.completion-not-successful"]});
  if (!completion.continuation_required && options.length === 0) return finalize({...base, kind: "complete", selected_option_id: null, owner_gate_refs: [], reason_codes: ["continuation.none-required"]});
  if (admissible.length === 0) return finalize({...base, kind: "block", selected_option_id: null, owner_gate_refs: [], reason_codes: ["continuation.zero-admissible"]});
  const ownerGates = [...new Set(admissible.flatMap((trace) => trace.required_owner_gate_refs))].sort();
  if (admissible.length > 1) return finalize({...base, kind: "gate", selected_option_id: null, owner_gate_refs: ownerGates, reason_codes: ["continuation.multiple-admissible"]});
  const selected = admissible[0];
  if (selected.consequential) return finalize({...base, kind: "gate", selected_option_id: selected.option_id, owner_gate_refs: selected.required_owner_gate_refs, reason_codes: ["continuation.consequential"]});
  return finalize({...base, kind: "direct", selected_option_id: selected.option_id, owner_gate_refs: [], reason_codes: ["continuation.sole-nonconsequential"]});
}

export function advanceUntilGate(sequence, profile) {
  if (!isVerifiedDecisionProfile(profile)) return deepFreeze({kind: "block", traversed: [], decision: null, reason_codes: ["profile.unverified"], authority_effect: "none"});
  const traversed = [];
  for (const step of sequence) {
    if (traversed.length >= profile.consequence.max_direct_steps) return deepFreeze({kind: "block", traversed, decision: null, reason_codes: ["continuation.step-cap-reached"], authority_effect: "none"});
    const decision = evaluateContinuation(step, profile);
    traversed.push({completion_id: step.completion?.completion_id ?? null, decision_digest: decision.decision_digest, kind: decision.kind, selected_option_id: decision.selected_option_id});
    if (decision.kind !== "direct") return deepFreeze({kind: decision.kind, traversed, decision, reason_codes: decision.reason_codes, authority_effect: "none"});
  }
  return deepFreeze({kind: "block", traversed, decision: null, reason_codes: ["continuation.sequence-exhausted-before-terminal"], authority_effect: "none"});
}
