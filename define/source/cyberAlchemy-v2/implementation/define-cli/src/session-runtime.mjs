import {canonicalize, digest, stableUniqueStrings} from "./canonical.mjs";
import {execute as executeCompiledDisposition} from "../generated/define-service/entries/ConceptDisposition/app/function/behavior.mjs";
import {execute as executeCompiledPackReadiness} from "../generated/define-service/entries/PackReadiness/app/function/behavior.mjs";

const ACTIONS = new Set(["reuse", "specialize", "propose", "open", "defer", "refuse"]);

function normalizeConcept(concept, index) {
  if (typeof concept === "string") {
    const term = concept.trim();
    return {concept_id: `concept:${digest(term).slice(0, 16)}`, term, question: `What should ${term} mean for this goal?`, owner_route: "Definitions Governance owner", index};
  }
  const term = String(concept?.term ?? "").trim();
  return {
    concept_id: String(concept?.concept_id ?? `concept:${digest(term).slice(0, 16)}`).trim(),
    term,
    question: String(concept?.question ?? `What should ${term} mean for this goal?`).trim(),
    owner_route: String(concept?.owner_route ?? "Definitions Governance owner").trim(),
    index,
  };
}

function dispositionFor(concept, response) {
  const action = String(response?.action ?? "open").trim().toLowerCase();
  const payload = response?.payload ?? {};
  const definitionRef = String(payload.definition_ref ?? "").trim();
  const baseRef = String(payload.base_definition_ref ?? "").trim();
  const scope = String(payload.scope ?? "").trim();
  const statement = String(payload.definition ?? payload.formal_statement ?? "").trim();
  const decision = executeCompiledDisposition({input: {
    action: ACTIONS.has(action) ? action : "unsupported",
    definition_reference_present: Boolean(definitionRef),
    base_reference_present: Boolean(baseRef),
    specialization_scope_present: Boolean(scope),
    proposal_present: Boolean(statement),
  }}, {});
  if (decision.status === "block") {
    const code = {
      "unsupported-action": `define-session.unsupported-action:${action}`,
      "definition-reference": `define-session.reuse-reference-required:${concept.concept_id}`,
      specialization: `define-session.specialization-required:${concept.concept_id}`,
      proposal: `define-session.proposal-required:${concept.concept_id}`,
    }[decision.repair_focus];
    throw new Error(code ?? `define-session.disposition-blocked:${concept.concept_id}`);
  }
  if (decision.disposition === "reuse") {
    return {concept_id: concept.concept_id, term: concept.term, disposition: "reuse", definition_ref: definitionRef, owner_route: concept.owner_route};
  }
  if (decision.disposition === "specialize") {
    return {concept_id: concept.concept_id, term: concept.term, disposition: "specialize", base_definition_ref: baseRef, scope, owner_route: concept.owner_route};
  }
  if (decision.disposition === "propose") {
    return {
      concept_id: concept.concept_id,
      term: concept.term,
      disposition: "propose",
      candidate_definition: {
        normative_voice: statement,
        plain_language_voice: String(payload.plain_explanation ?? statement).trim(),
        boundary: String(payload.boundary ?? "Candidate meaning only; it is not canonical or effect-authorizing.").trim(),
        status: "candidate",
      },
      owner_route: concept.owner_route,
    };
  }
  const reason = String(payload.reason ?? `${action} recorded without inferred meaning`).trim();
  return {
    concept_id: concept.concept_id,
    term: concept.term,
    disposition: "open",
    open_question: {
      question: concept.question,
      reason,
      response_kind: action,
      blocking: true,
      next_action: String(payload.next_action ?? `Resolve with ${concept.owner_route}`).trim(),
    },
    owner_route: concept.owner_route,
  };
}

export function validateDefinitionPack(pack) {
  const reasons = [];
  if (pack?.schema_version !== "cav2.definition-pack-candidate/v1") reasons.push("pack.unsupported-version");
  if (!pack?.pack_id || !pack?.session_id || !pack?.context_envelope_ref) reasons.push("pack.identity-incomplete");
  if (!pack?.goal || !pack?.intent || !pack?.context || !pack?.consumer) reasons.push("pack.scope-incomplete");
  if (!Array.isArray(pack?.required_concepts) || pack.required_concepts.length === 0) reasons.push("pack.required-concepts-empty");
  const conceptIds = new Set((pack?.required_concepts ?? []).map((concept) => concept.concept_id));
  const dispositionIds = (pack?.concept_dispositions ?? []).map((item) => item.concept_id);
  for (const id of conceptIds) if (dispositionIds.filter((candidate) => candidate === id).length !== 1) reasons.push(`pack.exact-disposition-required:${id}`);
  for (const id of dispositionIds) if (!conceptIds.has(id)) reasons.push(`pack.undeclared-concept:${id}`);
  if (pack?.authority?.authority_effect !== "none") reasons.push("pack.authority-effect-must-be-none");
  if (pack?.language_quality_evaluation && pack.language_quality_evaluation.status !== "pass") reasons.push("pack.language-quality-must-pass");
  if (pack?.language_quality_evaluation && (!pack.language_scope || !pack.language_quality_evidence)) reasons.push("pack.language-quality-evidence-required");
  const reasonCodes = stableUniqueStrings(reasons);
  const compiled = executeCompiledPackReadiness({input: {
    version_supported: pack?.schema_version === "cav2.definition-pack-candidate/v1",
    identity_complete: Boolean(pack?.pack_id && pack?.session_id && pack?.context_envelope_ref),
    scope_complete: Boolean(pack?.goal && pack?.intent && pack?.context && pack?.consumer),
    concepts_present: Array.isArray(pack?.required_concepts) && pack.required_concepts.length > 0,
    dispositions_exact: !reasonCodes.some((reason) => reason.startsWith("pack.exact-disposition-required:")),
    dispositions_declared: !reasonCodes.some((reason) => reason.startsWith("pack.undeclared-concept:")),
    authority_none: pack?.authority?.authority_effect === "none",
    language_quality_pass: !pack?.language_quality_evaluation || pack.language_quality_evaluation.status === "pass",
    language_evidence_complete: !pack?.language_quality_evaluation || Boolean(pack.language_scope && pack.language_quality_evidence),
    open_questions_empty: (pack?.open_questions ?? []).length === 0,
  }}, {});
  return canonicalize({
    schema_version: "cav2.definition-pack-validation/v1",
    valid: compiled.valid,
    reason_codes: reasonCodes,
    open_question_count: (pack?.open_questions ?? []).length,
    handoff_ready: compiled.handoff_ready,
    session_state: compiled.session_state,
    validation_scope: pack?.language_quality_evaluation ? "deterministic-structure-and-language-quality" : "deterministic-structure-only",
    authority_effect: "none",
  });
}

export function runDefineSession(input) {
  const reasons = [];
  for (const key of ["goal", "intent", "context", "consumer"]) if (!String(input?.[key] ?? "").trim()) reasons.push(`define-session.${key}-required`);
  const concepts = (Array.isArray(input?.concepts) ? input.concepts : []).map(normalizeConcept);
  if (concepts.length === 0) reasons.push("define-session.required-concepts-required");
  if (concepts.some((concept) => !concept.term || !concept.concept_id)) reasons.push("define-session.concept-invalid");
  if (!input?.context_result?.ok) reasons.push("define-session.context-envelope-required");
  if (reasons.length > 0) return {ok: false, stage: "session-intake", reason_codes: stableUniqueStrings(reasons), authority_effect: "none"};

  const responseById = new Map((Array.isArray(input.responses) ? input.responses : []).map((response) => [String(response.concept_id ?? "").trim(), response]));
  let dispositions;
  try {
    dispositions = concepts.map((concept) => dispositionFor(concept, responseById.get(concept.concept_id)));
  } catch (error) {
    return {ok: false, stage: "disposition", reason_codes: [error.message], authority_effect: "none"};
  }
  dispositions.sort((left, right) => left.concept_id.localeCompare(right.concept_id));
  const scope = canonicalize({goal: input.goal.trim(), intent: input.intent.trim(), context: input.context.trim(), consumer: input.consumer.trim()});
  const sessionId = `define-session:${digest(scope)}`;
  const openQuestions = dispositions.filter((item) => item.disposition === "open").map((item) => ({concept_id: item.concept_id, term: item.term, ...item.open_question, owner_route: item.owner_route}));
  const packMaterial = canonicalize({
    schema_version: "cav2.definition-pack-candidate/v1",
    session_id: sessionId,
    goal: scope.goal,
    intent: scope.intent,
    context: scope.context,
    consumer: scope.consumer,
    source_epoch: input.context_result.source_epoch,
    context_envelope_ref: input.context_result.context_envelope.context_epoch_id,
    context_envelope_digest: input.context_result.context_envelope_digest,
    required_concepts: concepts.map(({index, ...concept}) => concept).sort((a, b) => a.concept_id.localeCompare(b.concept_id)),
    concept_dispositions: dispositions,
    evidence: [{kind: "context-envelope", ref: input.context_result.context_envelope.context_epoch_id, digest: input.context_result.context_envelope_digest}],
    ...(input.language_scope ? {language_scope: input.language_scope} : {}),
    ...(input.language_quality_evidence ? {language_quality_evidence: input.language_quality_evidence} : {}),
    ...(input.language_quality_evaluation ? {language_quality_evaluation: input.language_quality_evaluation} : {}),
    typed_relationships: [],
    open_questions: openQuestions,
    exclusions: ["solution-selection", "canonical-promotion", "implementation-authority", "effect-authority"],
    allowed_uses: ["review", "meaning-refinement", "named-consumer-input-after-open-questions-resolve"],
    blocked_actions: ["treat-candidate-as-canonical", "infer-downstream-authority", "hide-open-questions"],
    authority: {
      status: "candidate",
      authority_effect: "none",
      claim_ceiling: "Bounded candidate semantic coverage only.",
      next_responsible_owner: openQuestions.length > 0 ? openQuestions[0].owner_route : "Owner of the named intended use",
    },
  });
  const packId = `definition-pack:${digest(packMaterial)}`;
  const pack = canonicalize({...packMaterial, pack_id: packId});
  const validation = validateDefinitionPack(pack);
  return canonicalize({
    ok: validation.valid,
    schema_version: "cav2.define-cli-result/v1",
    route: {route_id: input.context_result.route_decision.selected.route_id, decision_digest: input.context_result.route_decision.decision_digest},
    context: {
      context_epoch_id: input.context_result.context_envelope.context_epoch_id,
      envelope_digest: input.context_result.context_envelope_digest,
      inline_bytes: input.context_result.context_envelope.inline_bytes,
      included_item_count: input.context_result.context_envelope.included_items.length,
      freshness_state: input.context_result.context_envelope.freshness_state,
    },
    session: {session_id: sessionId, state: validation.session_state, durable: false},
    definition_pack: pack,
    validation,
    authority_effect: "none",
  });
}
