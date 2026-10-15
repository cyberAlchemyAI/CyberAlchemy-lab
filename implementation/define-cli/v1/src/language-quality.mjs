import {canonicalize, stableUniqueStrings} from "./canonical.mjs";
import {execute as executeCompiledGrounding} from "../generated/define-service/entries/SemanticGrounding/app/function/behavior.mjs";
import {execute as executeCompiledGroundingEvidence} from "../generated/define-service/entries/GroundingEvidence/app/function/behavior.mjs";
import {execute as executeCompiledNonCollapse} from "../generated/define-service/entries/NonCollapse/app/function/behavior.mjs";
import {execute as executeCompiledNonCollapseEvidence} from "../generated/define-service/entries/NonCollapseEvidence/app/function/behavior.mjs";
import {execute as executeCompiledOrthogonality} from "../generated/define-service/entries/Orthogonality/app/function/behavior.mjs";
import {execute as executeCompiledOrthogonalityEvidence} from "../generated/define-service/entries/OrthogonalityEvidence/app/function/behavior.mjs";
import {execute as executeCompiledReadiness} from "../generated/define-service/entries/LanguageReadiness/app/function/behavior.mjs";
import {containsPhrase, semanticKey} from "../vendor/semantic-contract/consumer-runtime.mjs";

const LANGUAGE_FIELDS = Object.freeze(["terms", "distinctions", "relationships", "constraints", "owners", "open_questions"]);
const GROUNDING_POSTURES = new Set(["direct", "candidate-inference", "user-corrected"]);
const NON_COLLAPSE_STATUSES = new Set(["distinct", "related", "collapsed", "unresolved"]);
const AXIS_STATUSES = new Set(["independent", "coupled", "redundant", "unresolved"]);

function text(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function normalized(value) {
  return semanticKey(value);
}

function pairKey(left, right) {
  return left < right ? `${left}:${right}` : `${right}:${left}`;
}

function expectedPairs(length) {
  const pairs = new Set();
  for (let left = 0; left < length; left += 1) {
    for (let right = left + 1; right < length; right += 1) pairs.add(pairKey(left, right));
  }
  return pairs;
}

function evaluateGrounding(language, quality, reasons, reviewReasons) {
  const phrases = Array.isArray(language?.user_phrases) ? language.user_phrases : [];
  const expected = new Set();
  for (const field of LANGUAGE_FIELDS) {
    const values = Array.isArray(language?.[field]) ? language[field] : [];
    const normalizedValues = values.map(normalized);
    if (new Set(normalizedValues).size !== normalizedValues.length) reasons.push(`quality.grounding-duplicate-item:${field}`);
    for (let index = 0; index < values.length; index += 1) expected.add(`${field}:${index}`);
  }
  const observed = new Set();
  for (const item of Array.isArray(quality?.grounding) ? quality.grounding : []) {
    const key = `${item?.field}:${item?.item_index}`;
    if (!LANGUAGE_FIELDS.includes(item?.field) || !Number.isSafeInteger(item?.item_index) || !expected.has(key)) {
      reasons.push(`quality.grounding-invalid-target:${key}`);
      continue;
    }
    if (observed.has(key)) reasons.push(`quality.grounding-duplicate:${key}`);
    observed.add(key);
    const decision = executeCompiledGroundingEvidence({input: {
      posture: GROUNDING_POSTURES.has(item.posture) ? item.posture : "unsupported",
      rationale_present: text(item.rationale),
    }}, {});
    if (!Number.isSafeInteger(item.source_phrase_index) || item.source_phrase_index < 0 || item.source_phrase_index >= phrases.length) {
      reasons.push(`quality.grounding-source-missing:${key}`);
    } else if (decision.requires_direct_match) {
      const languageItem = normalized(language[item.field][item.item_index]);
      const sourcePhrase = normalized(phrases[item.source_phrase_index]);
      if (!containsPhrase(sourcePhrase, languageItem)) reasons.push(`quality.grounding-direct-mismatch:${key}`);
    }
    if (decision.repair_focus === "evidence") reasons.push(`quality.grounding-evidence-invalid:${key}`);
    if (decision.repair_focus === "user-confirmation") reviewReasons.push(`quality.grounding-needs-confirmation:${key}`);
  }
  for (const key of expected) if (!observed.has(key)) reasons.push(`quality.grounding-missing:${key}`);
}

function evaluateNonCollapse(language, quality, candidateOptions, reasons) {
  const terms = Array.isArray(language?.terms) ? language.terms : [];
  const normalizedTerms = terms.map(normalized);
  if (normalizedTerms.some((term) => !term)) reasons.push("quality.term-empty");
  if (new Set(normalizedTerms).size !== normalizedTerms.length) reasons.push("quality.term-normalized-collision");
  const expected = expectedPairs(terms.length);
  const observed = new Set();
  for (const item of Array.isArray(quality?.non_collapse) ? quality.non_collapse : []) {
    const left = item?.left_term_index;
    const right = item?.right_term_index;
    const key = pairKey(left, right);
    if (!Number.isSafeInteger(left) || !Number.isSafeInteger(right) || left < 0 || right < 0 || left >= terms.length || right >= terms.length || left === right || !expected.has(key)) {
      reasons.push(`quality.non-collapse-invalid-pair:${key}`);
      continue;
    }
    if (observed.has(key)) reasons.push(`quality.non-collapse-duplicate-pair:${key}`);
    observed.add(key);
    const decision = executeCompiledNonCollapseEvidence({input: {
      relation: NON_COLLAPSE_STATUSES.has(item.status) ? item.status : "unsupported",
      difference_present: text(item.difference),
    }}, {});
    if (decision.repair_focus === "evidence") reasons.push(`quality.non-collapse-evidence-invalid:${key}`);
    if (decision.repair_focus === "collapsed") reasons.push(`quality.non-collapse-collapsed:${key}`);
    if (decision.repair_focus === "unresolved") reasons.push(`quality.non-collapse-unresolved:${key}`);
  }
  for (const key of expected) if (!observed.has(key)) reasons.push(`quality.non-collapse-missing-pair:${key}`);
  if (candidateOptions.length > 0) {
    const optionTerms = candidateOptions.map((option) => normalized(option?.term));
    if (optionTerms.length !== normalizedTerms.length || optionTerms.some((term) => !normalizedTerms.includes(term))) {
      reasons.push("quality.non-collapse-option-term-coverage-mismatch");
    }
    const definitions = candidateOptions
      .map((option, index) => ({index, value: normalized(option?.candidate_definition)}))
      .filter((item) => item.value);
    const firstByDefinition = new Map();
    for (const definition of definitions) {
      if (firstByDefinition.has(definition.value)) {
        reasons.push(`quality.non-collapse-definition-collision:${firstByDefinition.get(definition.value)}:${definition.index}`);
      } else firstByDefinition.set(definition.value, definition.index);
    }
  }
}

function evaluateOrthogonality(quality, reasons) {
  const orthogonality = quality?.orthogonality;
  const axes = Array.isArray(orthogonality?.axes) ? orthogonality.axes : [];
  const axisIds = axes.map((axis) => String(axis?.axis_id ?? "").trim());
  if (axisIds.some((id) => !id) || new Set(axisIds).size !== axisIds.length) reasons.push("quality.orthogonality-axis-identity-invalid");
  for (const axis of axes) {
    if (!text(axis.label) || !text(axis.unique_question) || !Array.isArray(axis.values) || axis.values.length === 0 || axis.values.some((value) => !text(value))) {
      reasons.push(`quality.orthogonality-axis-invalid:${axis.axis_id ?? "unknown"}`);
    }
    if (Array.isArray(axis.values) && new Set(axis.values.map(normalized)).size !== axis.values.length) reasons.push(`quality.orthogonality-axis-value-collision:${axis.axis_id ?? "unknown"}`);
  }
  if (!text(orthogonality?.rationale)) reasons.push("quality.orthogonality-rationale-required");
  if (orthogonality?.applicability === "not-applicable") {
    if (axes.length >= 2) reasons.push("quality.orthogonality-not-applicable-with-multiple-axes");
    if ((orthogonality?.pair_checks ?? []).length > 0) reasons.push("quality.orthogonality-not-applicable-with-pairs");
    return;
  }
  if (orthogonality?.applicability !== "applicable") {
    reasons.push("quality.orthogonality-applicability-invalid");
    return;
  }
  if (axes.length < 2) reasons.push("quality.orthogonality-applicable-without-multiple-axes");
  const indexById = new Map(axisIds.map((id, index) => [id, index]));
  const expected = expectedPairs(axes.length);
  const observed = new Set();
  for (const item of Array.isArray(orthogonality?.pair_checks) ? orthogonality.pair_checks : []) {
    const left = indexById.get(item?.left_axis_id);
    const right = indexById.get(item?.right_axis_id);
    const key = pairKey(left, right);
    if (left === undefined || right === undefined || left === right || !expected.has(key)) {
      reasons.push(`quality.orthogonality-invalid-pair:${item?.left_axis_id ?? "unknown"}:${item?.right_axis_id ?? "unknown"}`);
      continue;
    }
    if (observed.has(key)) reasons.push(`quality.orthogonality-duplicate-pair:${key}`);
    observed.add(key);
    const decision = executeCompiledOrthogonalityEvidence({input: {
      relation: AXIS_STATUSES.has(item.status) ? item.status : "unsupported",
      difference_present: text(item.difference),
      coupling_named: text(item.coupling_type) && text(item.coupling_owner) && text(item.coupling_effect),
    }}, {});
    if (decision.repair_focus === "evidence") reasons.push(`quality.orthogonality-evidence-invalid:${key}`);
    if (decision.repair_focus === "redundant") reasons.push(`quality.orthogonality-redundant:${key}`);
    if (decision.repair_focus === "unresolved") reasons.push(`quality.orthogonality-unresolved:${key}`);
    if (decision.repair_focus === "coupling") reasons.push(`quality.orthogonality-unnamed-coupling:${key}`);
  }
  for (const key of expected) if (!observed.has(key)) reasons.push(`quality.orthogonality-missing-pair:${key}`);
}

export function evaluateDefineLanguageQuality(scope, candidateOptions = [], settings = {}) {
  if (!Array.isArray(candidateOptions)) {
    settings = candidateOptions ?? {};
    candidateOptions = [];
  }
  const reasons = [];
  const reviewReasons = [];
  const quality = scope?.language_quality;
  if (quality?.schema_version !== "cav2.define-language-quality/v1") reasons.push("quality.schema-version-invalid");
  evaluateGrounding(scope?.language, quality, reasons, reviewReasons);
  evaluateNonCollapse(scope?.language, quality, candidateOptions, reasons);
  evaluateOrthogonality(quality, reasons);
  const confirmed = settings.user_confirmed === true;
  const reasonCodes = stableUniqueStrings(reasons);
  const pendingReview = confirmed ? [] : stableUniqueStrings(reviewReasons);
  const hasReason = (prefix) => reasonCodes.some((reason) => reason.startsWith(prefix));
  const grounding = executeCompiledGrounding({input: {
    schema_valid: quality?.schema_version === "cav2.define-language-quality/v1",
    targets_valid: !hasReason("quality.grounding-invalid-target") && !hasReason("quality.grounding-duplicate-item") && !hasReason("quality.grounding-duplicate:"),
    coverage_complete: !hasReason("quality.grounding-missing:"),
    sources_present: !hasReason("quality.grounding-source-missing:"),
    direct_matches: !hasReason("quality.grounding-direct-mismatch:"),
    evidence_valid: !hasReason("quality.grounding-evidence-invalid:"),
    candidate_inference_present: reviewReasons.length > 0,
    user_confirmed: confirmed,
  }}, {});
  const nonCollapse = executeCompiledNonCollapse({input: {
    terms_valid: !reasonCodes.includes("quality.term-empty"),
    pair_targets_valid: !hasReason("quality.non-collapse-invalid-pair:") && !hasReason("quality.non-collapse-duplicate-pair:"),
    pair_coverage_complete: !hasReason("quality.non-collapse-missing-pair:"),
    evidence_valid: !hasReason("quality.non-collapse-evidence-invalid:"),
    terms_distinct: !reasonCodes.includes("quality.term-normalized-collision") && !hasReason("quality.non-collapse-collapsed:"),
    pairs_resolved: !hasReason("quality.non-collapse-unresolved:"),
    option_coverage_complete: !reasonCodes.includes("quality.non-collapse-option-term-coverage-mismatch"),
    definitions_distinct: !hasReason("quality.non-collapse-definition-collision:"),
  }}, {});
  const orthogonality = executeCompiledOrthogonality({input: {
    applicability_valid: !reasonCodes.includes("quality.orthogonality-applicability-invalid"),
    axis_identity_valid: !reasonCodes.includes("quality.orthogonality-axis-identity-invalid"),
    axis_structure_valid: !hasReason("quality.orthogonality-axis-invalid:") && !hasReason("quality.orthogonality-axis-value-collision:"),
    rationale_present: !reasonCodes.includes("quality.orthogonality-rationale-required"),
    cardinality_valid: !reasonCodes.includes("quality.orthogonality-not-applicable-with-multiple-axes") && !reasonCodes.includes("quality.orthogonality-not-applicable-with-pairs") && !reasonCodes.includes("quality.orthogonality-applicable-without-multiple-axes"),
    pair_targets_valid: !hasReason("quality.orthogonality-invalid-pair:") && !hasReason("quality.orthogonality-duplicate-pair:"),
    pair_coverage_complete: !hasReason("quality.orthogonality-missing-pair:"),
    pair_evidence_valid: !hasReason("quality.orthogonality-evidence-invalid:"),
    axes_non_redundant: !hasReason("quality.orthogonality-redundant:"),
    pairs_resolved: !hasReason("quality.orthogonality-unresolved:"),
    couplings_named: !hasReason("quality.orthogonality-unnamed-coupling:"),
  }}, {});
  const checks = {
    semantic_grounding: grounding.status,
    non_collapse: nonCollapse.status,
    orthogonality: orthogonality.status,
  };
  const compiled = executeCompiledReadiness({input: {...checks, user_confirmed: confirmed}}, {});
  return canonicalize({
    schema_version: "cav2.define-language-quality-evaluation/v1",
    status: compiled.status,
    repair_focus: compiled.repair_focus,
    checks,
    reason_codes: [...reasonCodes, ...pendingReview],
    user_confirmation_applied: confirmed,
    claim_ceiling: "Deterministic coverage and contradiction checks over agent-proposed evidence; user confirmation resolves candidate inference posture but does not prove canonical meaning.",
    authority_effect: "none",
  });
}
