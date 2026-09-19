import {readFileSync} from "node:fs";
import {resolve, sep} from "node:path";

import {
  appendReasoningStateReduction,
  createReasoningStateBranch,
  verifyReasoningStateEpoch,
} from "../reasoning-state-runtime/index.mjs";
import {
  canonicalJson,
  canonicalizeJson,
  deepFreeze,
  sha256HexText,
} from "../intent-route-resolver/index.mjs";

export const REASONING_POLICY_PROFILE_SCHEMA = "are.reasoning-policy-profile/v1";
export const REASONING_EVOLUTION_DECISION_SCHEMA = "are.reasoning-evolution-decision/v1";
export const CONTEXT_REDUCTION_PLAN_SCHEMA = "are.context-reduction-plan/v1";
export const REASONING_EVOLUTION_RESULT_SCHEMA = "are.reasoning-evolution-result/v1";

const ACTIONS = new Set(["reuse-current", "create-successor", "create-branch", "reduce-successor", "block"]);
const LANES = new Set(["plan-bound", "interaction-bound"]);

function freeze(value) {
  return deepFreeze(canonicalizeJson(value));
}

function digest(value) {
  return sha256HexText(canonicalJson(canonicalizeJson(value)));
}

function record(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function text(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function failure(stage, reasonCodes, residue = []) {
  return freeze({
    schema_version: REASONING_EVOLUTION_RESULT_SCHEMA,
    ok: false,
    disposition: "block",
    stage,
    reason_codes: [...new Set(reasonCodes)].sort(),
    residue,
    authority_effect: "none",
  });
}

function withinRoot(root, path) {
  return path === root || path.startsWith(`${root}${sep}`);
}

function validateProfile(profile) {
  const reasons = [];
  if (!record(profile) || profile.schema_version !== REASONING_POLICY_PROFILE_SCHEMA) reasons.push("reasoning-policy.schema-invalid");
  if (!text(profile?.profile_id)) reasons.push("reasoning-policy.profile-id-required");
  if (!Number.isSafeInteger(profile?.maximum_event_count) || profile.maximum_event_count < 2) reasons.push("reasoning-policy.maximum-event-count-invalid");
  if (!Array.isArray(profile?.mandatory_event_kinds) || profile.mandatory_event_kinds.some((value) => !text(value))) reasons.push("reasoning-policy.mandatory-event-kinds-invalid");
  for (const field of ["interaction_bound_action", "selected_dependency_drift_action", "exploration_action", "overflow_action", "stable_plan_action"]) {
    if (!ACTIONS.has(profile?.[field])) reasons.push(`reasoning-policy.${field.replaceAll("_", "-")}-invalid`);
  }
  if (profile?.reduction?.method !== "deterministic-event-selection-no-summary" || profile?.reduction?.mandatory_overflow !== "block") reasons.push("reasoning-policy.reduction-policy-invalid");
  if (!text(profile?.claim_ceiling) || profile?.authority_effect !== "none") reasons.push("reasoning-policy.authority-posture-invalid");
  return reasons;
}

export function loadReasoningPolicy(profilePath, repositoryRoot) {
  const root = resolve(repositoryRoot);
  const path = resolve(root, profilePath);
  if (!withinRoot(root, path)) return failure("policy-load", ["reasoning-policy.path-outside-repository"]);
  let profile;
  try {
    profile = JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return failure("policy-load", ["reasoning-policy.profile-unreadable"]);
  }
  const reasons = validateProfile(profile);
  if (reasons.length > 0) return failure("policy-load", reasons);
  const value = freeze(profile);
  return freeze({ok: true, value, digest: digest(value), path, authority_effect: "none"});
}

function requireProfile(profile) {
  const reasons = validateProfile(profile);
  return reasons.length === 0 ? null : reasons;
}

function selectedDrift(refresh) {
  const value = refresh?.value ?? refresh;
  return Array.isArray(value?.changed_selected_dependencies) && value.changed_selected_dependencies.length > 0;
}

function sameContext(currentEpoch, candidateEpoch) {
  return currentEpoch?.context_envelope_digest === candidateEpoch?.context_envelope_digest
    && digest(currentEpoch?.selected_dependencies ?? []) === digest(candidateEpoch?.selected_dependencies ?? []);
}

function refreshDisposition(refresh) {
  return (refresh?.value ?? refresh)?.disposition ?? null;
}

export function materializeContextReductionPlan(input = {}) {
  const profileReasons = requireProfile(input.profile);
  if (profileReasons) return failure("reduction-plan", profileReasons);
  const sourceEpoch = input.source_epoch;
  if (!verifyReasoningStateEpoch(sourceEpoch).ok) return failure("reduction-plan", ["reasoning-policy.source-epoch-invalid"]);
  const byDigest = new Map((Array.isArray(input.events) ? input.events : []).map((event) => [event?.event_digest, event]));
  const selectedEvents = sourceEpoch.event_digests.map((eventDigest) => byDigest.get(eventDigest));
  if (selectedEvents.some((event) => !record(event))) return failure("reduction-plan", ["reasoning-policy.source-event-missing"]);
  const mandatoryKinds = new Set(input.profile.mandatory_event_kinds);
  const mandatory = selectedEvents.filter((event) => mandatoryKinds.has(event.event_kind));
  if (mandatory.length > input.profile.maximum_event_count) {
    return failure("reduction-plan", ["reasoning-policy.mandatory-event-budget-exceeded"], [{mandatory_event_count: mandatory.length, maximum_event_count: input.profile.maximum_event_count}]);
  }
  const mandatoryDigests = new Set(mandatory.map((event) => event.event_digest));
  const capacity = input.profile.maximum_event_count - mandatory.length;
  const optional = selectedEvents.filter((event) => !mandatoryDigests.has(event.event_digest));
  const latestOptional = input.profile.reduction.retain_latest_nonmandatory === true ? optional.slice(-capacity) : optional.slice(0, capacity);
  const retainedSet = new Set([...mandatory, ...latestOptional].map((event) => event.event_digest));
  const retained = sourceEpoch.event_digests.filter((eventDigest) => retainedSet.has(eventDigest));
  const omitted = sourceEpoch.event_digests.filter((eventDigest) => !retainedSet.has(eventDigest));
  const material = freeze({
    schema_version: CONTEXT_REDUCTION_PLAN_SCHEMA,
    profile_id: input.profile.profile_id,
    source_epoch_id: sourceEpoch.epoch_id,
    source_epoch_digest: sourceEpoch.epoch_digest,
    retained_event_digests: retained,
    omitted_event_digests: omitted,
    mandatory_event_digests: sourceEpoch.event_digests.filter((eventDigest) => mandatoryDigests.has(eventDigest)),
    destructive: false,
    generative_summary: false,
    claim_ceiling: input.profile.claim_ceiling,
    authority_effect: "none",
  });
  return freeze({ok: true, value: {...material, plan_digest: digest(material)}, authority_effect: "none"});
}

export function assessReasoningEvolution(input = {}) {
  const profileReasons = requireProfile(input.profile);
  if (profileReasons) return failure("evolution-assessment", profileReasons);
  if (!LANES.has(input.lane)) return failure("evolution-assessment", ["reasoning-policy.lane-invalid"]);
  if (!verifyReasoningStateEpoch(input.candidate_epoch).ok) return failure("evolution-assessment", ["reasoning-policy.candidate-epoch-invalid"]);
  if (input.current_epoch !== null && input.current_epoch !== undefined && !verifyReasoningStateEpoch(input.current_epoch).ok) return failure("evolution-assessment", ["reasoning-policy.current-epoch-invalid"]);
  const current = input.current_epoch ?? null;
  const drift = selectedDrift(input.refresh_assessment);
  const exploration = input.exploration === true;
  const overflow = input.candidate_epoch.event_digests.length > input.profile.maximum_event_count;
  let action = "create-successor";
  const reasons = [];
  if (!current) reasons.push("reasoning-policy.initial-epoch");
  else if (drift) {
    action = input.profile.selected_dependency_drift_action;
    reasons.push("reasoning-policy.selected-dependency-drift");
  } else if (exploration) {
    action = input.profile.exploration_action;
    reasons.push("reasoning-policy.explicit-exploration");
  } else if (overflow) {
    action = input.profile.overflow_action;
    reasons.push("reasoning-policy.event-budget-exceeded");
  } else if (input.lane === "interaction-bound") {
    action = input.profile.interaction_bound_action;
    reasons.push("reasoning-policy.interaction-successor-required");
  } else if (refreshDisposition(input.refresh_assessment) === "reuse-current" || sameContext(current, input.candidate_epoch)) {
    action = input.profile.stable_plan_action;
    reasons.push("reasoning-policy.stable-plan-compatible");
  } else {
    reasons.push("reasoning-policy.context-successor-required");
  }
  if (!ACTIONS.has(action) || action === "block") return failure("evolution-assessment", ["reasoning-policy.transition-blocked", ...reasons]);
  const material = freeze({
    schema_version: REASONING_EVOLUTION_DECISION_SCHEMA,
    profile_id: input.profile.profile_id,
    action,
    lane: input.lane,
    current_epoch_digest: current?.epoch_digest ?? null,
    candidate_epoch_digest: input.candidate_epoch.epoch_digest,
    selected_dependency_drift: drift,
    exploration,
    event_budget_exceeded: overflow,
    maximum_event_count: input.profile.maximum_event_count,
    reason_codes: reasons,
    claim_ceiling: input.profile.claim_ceiling,
    authority_effect: "none",
  });
  return freeze({ok: true, value: {...material, decision_digest: digest(material)}, authority_effect: "none"});
}

export function composeReasoningEvolution(input = {}) {
  const assessment = assessReasoningEvolution(input);
  if (!assessment.ok) return assessment;
  const decision = assessment.value;
  let epoch = input.candidate_epoch;
  let operation = null;
  if (decision.action === "reuse-current") {
    epoch = input.current_epoch;
  } else if (decision.action === "create-branch") {
    const currentSet = new Set(input.current_epoch.event_digests);
    const additional = input.candidate_epoch.event_digests.filter((eventDigest) => !currentSet.has(eventDigest));
    operation = createReasoningStateBranch(input.ledger, {
      base_epoch: input.current_epoch,
      branch_ref: input.branch_ref ?? `request:${input.candidate_epoch.request_ref ?? input.candidate_epoch.epoch_digest}`,
      additional_event_digests: additional,
      branch_basis: {reasoning_policy_decision_digest: decision.decision_digest},
      consumer_ref: input.candidate_epoch.consumer_ref,
      request_ref: input.candidate_epoch.request_ref,
      selected_dependencies: input.candidate_epoch.selected_dependencies,
      context_envelope_digest: input.candidate_epoch.context_envelope_digest,
    });
    if (!operation.ok) return failure("evolution-execution", operation.reason_codes, operation.residue);
    epoch = operation.epoch;
  } else if (decision.action === "reduce-successor") {
    const reductionPlan = materializeContextReductionPlan({profile: input.profile, source_epoch: input.candidate_epoch, events: input.events});
    if (!reductionPlan.ok) return reductionPlan;
    operation = appendReasoningStateReduction(input.ledger, {
      source_epoch: input.candidate_epoch,
      retained_event_digests: reductionPlan.value.retained_event_digests,
      reduction_basis: {plan_digest: reductionPlan.value.plan_digest, reason_codes: decision.reason_codes},
      consumer_ref: input.candidate_epoch.consumer_ref,
      request_ref: input.candidate_epoch.request_ref,
    });
    if (!operation.ok) return failure("evolution-execution", operation.reason_codes, operation.residue);
    epoch = operation.epoch;
  }
  const material = freeze({
    schema_version: REASONING_EVOLUTION_RESULT_SCHEMA,
    ok: true,
    disposition: decision.action,
    decision,
    input_epoch_digest: input.candidate_epoch.epoch_digest,
    output_epoch_digest: epoch.epoch_digest,
    operation_digest: operation?.reduction?.reduction_digest ?? operation?.branch?.branch_digest ?? null,
    authority_effect: "none",
  });
  return freeze({...material, result_digest: digest(material), epoch, operation});
}
