import {OUTCOMES} from "../../semantic-judgment-evaluator/index.mjs";
import {canonicalizeJson, digestValue, freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";
import {
  CODEX_REASONING_RECEIPT_BINDING_SCHEMA,
  CODEX_SEMANTIC_COMPLETION_SCHEMA,
  isVerifiedSemanticCompletion,
} from "./semantic-completion.mjs";

export const REASONING_RECEIPT_CONSTRAINT_SCHEMA = "are.reasoning-receipt-continuation-constraints/v1";

const verifiedConstraintSets = new WeakSet();

function seal(material) {
  const value = freezeResult({...material, constraint_digest: digestValue(material)});
  verifiedConstraintSets.add(value);
  return value;
}

export function isVerifiedReasoningReceiptConstraints(value) {
  return isRecord(value)
    && value.schema_version === REASONING_RECEIPT_CONSTRAINT_SCHEMA
    && verifiedConstraintSets.has(value);
}

function dependentProposals(proposals) {
  return (Array.isArray(proposals) ? proposals : [])
    .filter((proposal) => isRecord(proposal?.semantic_dependency))
    .sort((left, right) => String(left.proposal_id).localeCompare(String(right.proposal_id)));
}

function proposalConstraint(proposal, constraintKind, reasonCodes, binding = null) {
  return canonicalizeJson({
    proposal_id: proposal.proposal_id ?? null,
    proposal_digest: proposal.proposal_digest ?? null,
    constraint_kind: constraintKind,
    reason_codes: [...new Set(reasonCodes)].sort(),
    owner_gate_ref: constraintKind === "gate"
      ? (binding?.owner_ref ?? proposal.owner_gate_ref ?? "Owner of the selected semantic domain")
      : null,
    authority_effect: "none",
  });
}

function result(disposition, semantic, constraints, reasons = []) {
  const binding = semantic?.reasoning_receipt_binding ?? null;
  const material = canonicalizeJson({
    schema_version: REASONING_RECEIPT_CONSTRAINT_SCHEMA,
    disposition,
    semantic_completion_digest: semantic?.summary_digest ?? null,
    semantic_outcome: semantic?.semantic_outcome ?? null,
    reasoning_receipt_digest: binding?.reasoning_receipt_digest ?? null,
    receipt_binding_digest: binding?.binding_digest ?? null,
    proposal_constraints: constraints,
    reason_codes: [...new Set(reasons)].sort(),
    claim_ceiling: "Semantic outcomes may constrain continuation eligibility; they never grant effect or continuation authority.",
    authority_effect: "none",
  });
  return seal(material);
}

function constrainAll(proposals, kind, code, semantic, disposition = kind) {
  const binding = semantic?.reasoning_receipt_binding ?? null;
  return result(
    disposition,
    semantic,
    proposals.map((proposal) => proposalConstraint(proposal, kind, [code], binding)),
    [code],
  );
}

function receiptBindingIsCurrent(semantic, turnIdentity) {
  const binding = semantic.reasoning_receipt_binding;
  return isRecord(binding)
    && binding.schema_version === CODEX_REASONING_RECEIPT_BINDING_SCHEMA
    && nonEmptyString(binding.binding_digest)
    && digestValue(canonicalizeJson(Object.fromEntries(Object.entries(binding).filter(([key]) => key !== "binding_digest")))) === binding.binding_digest
    && binding.thread_id === turnIdentity?.thread_id
    && binding.turn_id === turnIdentity?.turn_id
    && binding.semantic_outcome === semantic.semantic_outcome
    && binding.reasoning_receipt_digest === semantic.reasoning_receipt_digest;
}

export function deriveReasoningReceiptConstraints(input = {}) {
  const proposals = dependentProposals(input.plan_bound);
  const semantic = input.semantic_completion;
  if (proposals.length === 0) return result("no-dependent-proposals", semantic, []);
  if (!isVerifiedSemanticCompletion(semantic) || semantic.schema_version !== CODEX_SEMANTIC_COMPLETION_SCHEMA) {
    return constrainAll(proposals, "ineligible", "continuation.semantic-completion-unverified", semantic, "block");
  }
  if (["disabled", "not-applicable"].includes(semantic.disposition)) {
    return constrainAll(proposals, "unchanged", `continuation.semantic-${semantic.disposition}`, semantic, "no-op");
  }
  if (semantic.disposition !== "evaluated") {
    return constrainAll(proposals, "ineligible", "continuation.semantic-materialization-blocked", semantic, "block");
  }
  if (!receiptBindingIsCurrent(semantic, input.turn_identity)) {
    return constrainAll(proposals, "ineligible", "continuation.semantic-receipt-binding-invalid", semantic, "block");
  }
  const binding = semantic.reasoning_receipt_binding;
  const mismatched = proposals.filter((proposal) =>
    (nonEmptyString(proposal.semantic_dependency.binding_id) && proposal.semantic_dependency.binding_id !== binding.binding_id)
    || (nonEmptyString(proposal.semantic_dependency.conclusion_domain) && proposal.semantic_dependency.conclusion_domain !== binding.conclusion_domain));
  const matching = proposals.filter((proposal) => !mismatched.includes(proposal));
  const constraints = mismatched.map((proposal) => proposalConstraint(proposal, "ineligible", ["continuation.semantic-domain-mismatch"], binding));
  let disposition = "advisory";
  let code = "continuation.semantic-recommendation-advisory-only";
  let kind = "advisory";
  if ([OUTCOMES.INVALID_INPUT, OUTCOMES.UNAUTHORIZED_CATALOG, OUTCOMES.DEFEATED, OUTCOMES.INSUFFICIENT, OUTCOMES.INVALIDATED].includes(semantic.semantic_outcome)) {
    disposition = "block";
    kind = "ineligible";
    code = `continuation.semantic-outcome:${semantic.semantic_outcome}`;
  } else if (semantic.semantic_outcome === OUTCOMES.ESCALATE_OWNER) {
    disposition = "gate";
    kind = "gate";
    code = "continuation.semantic-owner-gate-required";
  } else if (semantic.semantic_outcome === OUTCOMES.OUT_OF_DOMAIN) {
    disposition = "no-op";
    kind = "unchanged";
    code = "continuation.semantic-out-of-domain";
  } else if (semantic.semantic_outcome !== OUTCOMES.RECOMMENDED) {
    disposition = "block";
    kind = "ineligible";
    code = "continuation.semantic-outcome-unknown";
  }
  constraints.push(...matching.map((proposal) => proposalConstraint(proposal, kind, [code], binding)));
  if (mismatched.length > 0 && disposition === "advisory") disposition = "mixed";
  return result(disposition, semantic, constraints, constraints.flatMap((constraint) => constraint.reason_codes));
}
