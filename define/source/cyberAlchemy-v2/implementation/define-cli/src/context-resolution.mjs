import {evaluateSemanticJudgment} from "../../agent-reasoning-engine/packages/semantic-judgment-evaluator/src/reducer.mjs";

import {canonicalize, digest} from "./canonical.mjs";

const SOURCE_ORDER = ["explicit-user", "related-reference", "current-window", "saved-session"];

function text(value) {
  return String(value ?? "").trim();
}

function rows(value) {
  return Array.isArray(value) ? value : [];
}

export function resolveDefineContextCandidates(input = {}) {
  const groups = {
    "explicit-user": rows(input.explicit_user),
    "related-reference": rows(input.related_references),
    "current-window": rows(input.current_window),
    "saved-session": rows(input.saved_session),
  };
  const candidates = [];
  const winnerByKey = new Map();
  const conflicts = [];
  for (const sourceKind of SOURCE_ORDER) {
    for (const [index, row] of groups[sourceKind].entries()) {
      const content = text(row?.content);
      if (!content) continue;
      const contextKey = text(row.context_key) || `content:${digest(content).slice(0, 20)}`;
      const material = {source_kind: sourceKind, source_ref: text(row.source_ref) || `${sourceKind}:${index}`, context_key: contextKey, content_digest: digest(content)};
      const candidate = canonicalize({
        candidate_id: text(row.candidate_id) || `context-candidate:${digest(material)}`,
        source_kind: sourceKind,
        source_ref: material.source_ref,
        context_key: contextKey,
        content,
        content_digest: material.content_digest,
        derivation_posture: sourceKind === "explicit-user" || sourceKind === "related-reference" ? "provided" : "candidate-inference",
        confidence: row.confidence ?? (sourceKind === "explicit-user" ? 1 : null),
        user_disposition: text(row.user_disposition) || "unreviewed",
        precedence: SOURCE_ORDER.indexOf(sourceKind),
      });
      const winner = winnerByKey.get(contextKey);
      if (!winner) winnerByKey.set(contextKey, candidate);
      else if (winner.content_digest !== candidate.content_digest) {
        conflicts.push(canonicalize({
          context_key: contextKey,
          winner_candidate_id: winner.candidate_id,
          conflicting_candidate_id: candidate.candidate_id,
          resolution: "earlier-source-precedence-with-user-correction-visible",
        }));
      }
      candidates.push(candidate);
    }
  }
  return canonicalize({
    schema_version: "cav2.define-context-resolution/v1",
    source_order: SOURCE_ORDER,
    candidates,
    selected_candidate_ids: [...winnerByKey.values()].map((row) => row.candidate_id),
    conflicts,
    user_correction_required: conflicts.length > 0,
    authority_effect: "none",
  });
}

function mapOutcome(outcome) {
  if (outcome === "RecommendedUnderSnapshot") return "sufficient";
  if (outcome === "Deferred.Insufficient") return "insufficient";
  return "indeterminate";
}

export function createDefineContextSufficiencyAdapter({evaluate = evaluateSemanticJudgment} = {}) {
  const cache = new Map();
  return Object.freeze({
    evaluate(frozenRequest) {
      const request = canonicalize(frozenRequest);
      const requestDigest = digest(request);
      if (cache.has(requestDigest)) return JSON.parse(cache.get(requestDigest));
      const telemetry = {};
      const semantic = canonicalize(evaluate(request, telemetry));
      const result = canonicalize({
        evaluation_id: `define-context-evaluation:${requestDigest}`,
        status: mapOutcome(semantic.outcome),
        derivation: (semantic.derivation ?? []).join(" | ") || `semantic-outcome:${semantic.outcome ?? "missing"}`,
        residue: [...(semantic.residue ?? [])].map(String).sort(),
        evaluator_receipt_ref: `define-evaluator-receipt:${digest({request_digest: requestDigest, semantic})}`,
        evaluator_version: "semantic-judgment-evaluator@1/define-adapter-v1",
        request_digest: requestDigest,
        semantic_outcome: semantic.outcome ?? "InvalidInput",
        evaluator_calls: telemetry.evaluator_calls ?? 0,
        replayed: false,
        authority_effect: "none",
      });
      cache.set(requestDigest, JSON.stringify(result));
      return result;
    },
    replay(frozenRequest) {
      const requestDigest = digest(canonicalize(frozenRequest));
      if (!cache.has(requestDigest)) return null;
      return JSON.parse(cache.get(requestDigest));
    },
  });
}
