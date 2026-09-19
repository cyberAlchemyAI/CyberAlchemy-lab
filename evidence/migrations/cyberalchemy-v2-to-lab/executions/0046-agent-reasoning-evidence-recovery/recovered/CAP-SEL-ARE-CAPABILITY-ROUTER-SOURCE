import {canonicalJson, canonicalizeJson, deepFreeze, sha256HexText} from "../../intent-route-resolver/index.mjs";
import {admitRequestContext} from "./context.mjs";
import {isVerifiedDecisionProfile} from "./verified-profile.mjs";

function includesUnnegatedSignal(text, signal) {
  let offset = 0;
  while (offset <= text.length - signal.length) {
    const index = text.indexOf(signal, offset);
    if (index < 0) return false;
    const prefix = text.slice(Math.max(0, index - 32), index);
    if (!/\b(?:do\s+not|don't|never|without)\s+$/.test(prefix)) return true;
    offset = index + signal.length;
  }
  return false;
}

function finalize(material) {
  const normalized = canonicalizeJson(material);
  return deepFreeze(canonicalizeJson({...normalized, decision_digest: sha256HexText(canonicalJson(normalized))}));
}

export function routeRequest(input, profile) {
  if (!isVerifiedDecisionProfile(profile)) return finalize({schema_version: "are.capability-selection/v1", kind: "block", request_id: input?.request_id ?? null, request_context_digest: null, decision_profile_digest: null, selected: null, candidates: [], evaluated_routes: [], provenance: [], reason_codes: ["profile.unverified"], authority_effect: "none"});
  const admitted = admitRequestContext(input);
  if (!admitted.ok) return finalize({schema_version: "are.capability-selection/v1", kind: "block", request_id: input?.request_id ?? null, request_context_digest: null, decision_profile_digest: profile.profile_digest, selected: null, candidates: [], evaluated_routes: [], provenance: profile.provenance, reason_codes: admitted.reason_codes, authority_effect: "none"});
  const context = admitted.value;
  const routingText = [context.raw_request, ...context.requested_effects, ...context.target_refs, ...context.constraints].join("\n").toLowerCase();
  const traces = profile.routes.map((route) => {
    const excluded = route.exclusions.filter((signal) => includesUnnegatedSignal(routingText, signal));
    const objectiveMatch = context.objective_kind !== null && route.objective_kinds.includes(context.objective_kind);
    const matchedSignals = route.signals.filter((signal) => includesUnnegatedSignal(routingText, signal));
    const matchedEffects = route.effect_classes.filter((effect) => context.requested_effects.includes(effect));
    let posture = "rejected";
    const reasons = [];
    if (route.lifecycle_state === "blocked") reasons.push("route.lifecycle-blocked");
    else if (excluded.length > 0) reasons.push("route.explicit-exclusion");
    else if (objectiveMatch) {
      posture = "eligible";
      reasons.push("route.explicit-objective-match");
    } else if (matchedSignals.length > 0 || matchedEffects.length > 0) {
      posture = "eligible";
      if (matchedSignals.length > 0) reasons.push("route.lexical-signal-match");
      if (matchedEffects.length > 0) reasons.push("route.requested-effect-match");
    } else reasons.push("route.no-match");
    return canonicalizeJson({route_id: route.route_id, posture, objective_match: objectiveMatch, matched_signals: matchedSignals, matched_effects: matchedEffects, matched_exclusions: excluded, reason_codes: reasons});
  }).sort((a, b) => a.route_id.localeCompare(b.route_id));
  const eligible = traces.filter((trace) => trace.posture === "eligible");
  const explicitObjectiveEligible = eligible.filter((trace) => trace.objective_match);
  const structuredEffectEligible = eligible.filter((trace) => trace.matched_effects.length > 0);
  const selectedEligible = explicitObjectiveEligible.length > 0
    ? eligible.filter((trace) => trace.objective_match || structuredEffectEligible.some((effectTrace) => effectTrace.route_id === trace.route_id))
    : eligible;
  const suppressedLexicalCandidates = explicitObjectiveEligible.length > 0
    ? eligible.filter((trace) => !selectedEligible.some((selectedTrace) => selectedTrace.route_id === trace.route_id)).map((trace) => trace.route_id)
    : [];
  const byId = new Map(profile.routes.map((route) => [route.route_id, route]));
  let kind = "block";
  let selected = null;
  let reasons = ["selection.no-match"];
  if (selectedEligible.length === 1) {
    kind = "direct";
    const route = byId.get(selectedEligible[0].route_id);
    selected = canonicalizeJson({route_id: route.route_id, capability_ref: route.capability_ref, label: route.label, owner_gate_ref: route.owner_gate_ref, provenance_ids: route.provenance_ids});
    reasons = suppressedLexicalCandidates.length > 0 ? ["selection.explicit-objective-priority"] : ["selection.unique-capability"];
  } else if (selectedEligible.length > 1) {
    kind = "gate";
    reasons = ["selection.multiple-capabilities"];
  }
  const candidateDetails = selectedEligible.map((trace) => {
    const route = byId.get(trace.route_id);
    return canonicalizeJson({
      route_id: trace.route_id,
      capability_ref: route.capability_ref,
      owner_gate_ref: route.owner_gate_ref,
      reason_codes: trace.reason_codes,
      provenance_ids: route.provenance_ids,
      matched_signals: trace.matched_signals,
      matched_effects: trace.matched_effects,
    });
  });
  return finalize({schema_version: "are.capability-selection/v1", kind, request_id: context.request_id, request_context_digest: admitted.digest, decision_profile_digest: profile.profile_digest, selected, candidates: selectedEligible.map((trace) => trace.route_id), suppressed_lexical_candidates: suppressedLexicalCandidates, candidate_details: candidateDetails, evaluated_routes: traces, evaluated_context_fields: ["raw_request", "objective_kind", "requested_effects", "target_refs", "constraints"], provenance: profile.provenance, reason_codes: reasons, authority_effect: "none"});
}
