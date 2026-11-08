import {
  STRATEGY_MEMBERSHIP_DECISIONS,
  type StrategyMembershipDecisionId,
  type StrategyMembershipEvaluationInputV1,
  type StrategyMembershipEvaluationV1,
  type StrategyMembershipFindingCode,
  type StrategyMembershipFindingV1,
} from "../contracts/strategy-selection-contracts.js";
import {
  canonicalStrategySelectionJson,
  computeStrategyCatalogueSha256,
  computeStrategyMembershipDenominatorSha256,
  sha256StrategySelectionBytes,
} from "../providers/decode-strategy-selection.js";

const decisionForCode: Readonly<Record<StrategyMembershipFindingCode,
StrategyMembershipDecisionId>> = Object.freeze({
  FAMILY_POLICY_CATALOGUE_PROVENANCE_INVALID: "owner-catalogue-provenance",
  FAMILY_POLICY_STRATEGY_SET_EMPTY: "non-empty-strategy-set",
  FAMILY_POLICY_STRATEGY_ID_DUPLICATE: "unique-stable-strategy-identities",
  FAMILY_POLICY_EXECUTABLE_MEMBER_FORBIDDEN: "data-only-strategy-members",
  FAMILY_POLICY_STRATEGY_SET_DIGEST_STALE: "exact-content-addressed-set",
  FAMILY_POLICY_DESCRIPTOR_BINDING_STALE: "owner-catalogue-provenance",
  FAMILY_POLICY_DENOMINATOR_BINDING_STALE: "current-catalogue-binding",
  FAMILY_POLICY_FOREIGN_CATALOGUE: "current-catalogue-binding",
  FAMILY_POLICY_UNKNOWN_STRATEGY: "exact-current-membership",
  FAMILY_POLICY_CURRENT_MEMBERSHIP_MISSING: "exact-current-membership",
  FAMILY_POLICY_MEMBERSHIP_COLLAPSE: "membership-not-selection-or-execution",
});
const finding = (
  code: StrategyMembershipFindingCode,
  expected: string | null = null,
  observed: string | null = null,
): StrategyMembershipFindingV1 => Object.freeze({
  code,
  decision_id: decisionForCode[code],
  expected,
  observed,
});

export const evaluateStrategyMembership = (
  input: StrategyMembershipEvaluationInputV1,
): StrategyMembershipEvaluationV1 => {
  const {catalogue, denominator, observation} = input;
  const findings: StrategyMembershipFindingV1[] = [];
  if (catalogue.authorship !== "owner-authored-admission-input"
      || catalogue.derivation_policy
        !== "implementation-and-generated-members-forbidden-as-authority") {
    findings.push(finding("FAMILY_POLICY_CATALOGUE_PROVENANCE_INVALID"));
  }
  if (catalogue.members.length === 0) {
    findings.push(finding("FAMILY_POLICY_STRATEGY_SET_EMPTY"));
  }
  const ids = catalogue.members.map(({strategy_id: id}) => id);
  if (new Set(ids).size !== ids.length) {
    findings.push(finding("FAMILY_POLICY_STRATEGY_ID_DUPLICATE"));
  }
  if (catalogue.members.some(({executable}) => executable !== false)) {
    findings.push(finding("FAMILY_POLICY_EXECUTABLE_MEMBER_FORBIDDEN"));
  }
  const {catalogue_sha256: _catalogueSha256, ...catalogueBody} = catalogue;
  if (computeStrategyCatalogueSha256(catalogueBody) !== catalogue.catalogue_sha256) {
    findings.push(finding("FAMILY_POLICY_STRATEGY_SET_DIGEST_STALE"));
  }
  if (!/^[a-f0-9]{64}$/u.test(catalogue.descriptor_ref.sha256)) {
    findings.push(finding("FAMILY_POLICY_DESCRIPTOR_BINDING_STALE"));
  }
  const {denominator_sha256: _denominatorSha256, ...denominatorBody} = denominator;
  if (computeStrategyMembershipDenominatorSha256(denominatorBody)
        !== denominator.denominator_sha256
      || denominator.owner_catalogue_ref.catalogue_id !== catalogue.catalogue_id
      || denominator.owner_catalogue_ref.catalogue_sha256 !== catalogue.catalogue_sha256) {
    findings.push(finding("FAMILY_POLICY_DENOMINATOR_BINDING_STALE"));
  }
  if (observation.catalogue_ref.catalogue_id !== catalogue.catalogue_id
      || observation.catalogue_ref.catalogue_sha256 !== catalogue.catalogue_sha256) {
    findings.push(finding("FAMILY_POLICY_FOREIGN_CATALOGUE"));
  }
  if (!ids.includes(observation.strategy_id)) {
    findings.push(finding("FAMILY_POLICY_UNKNOWN_STRATEGY",
      "current catalogue member", observation.strategy_id));
  }
  if (observation.membership !== "member") {
    findings.push(finding("FAMILY_POLICY_CURRENT_MEMBERSHIP_MISSING",
      "member", observation.membership));
  }
  if (observation.selection_claim !== "none" || observation.execution_claim !== "none") {
    findings.push(finding("FAMILY_POLICY_MEMBERSHIP_COLLAPSE",
      "membership-only", `${observation.selection_claim}:${observation.execution_claim}`));
  }
  const normalized = Object.freeze([...findings].sort((left, right) =>
    Buffer.from(`${left.code}\u0000${left.observed ?? ""}`)
      .compare(Buffer.from(`${right.code}\u0000${right.observed ?? ""}`))));
  const failedDecisions = new Set(normalized.map(({decision_id: id}) => id));
  const declared = STRATEGY_MEMBERSHIP_DECISIONS.length;
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation.observation_id,
    observation_sha256: observation.observation_sha256,
  });
  const evaluationId = sha256StrategySelectionBytes(canonicalStrategySelectionJson({
    denominatorRef,
    observationRef,
    findings: normalized,
  }));
  return Object.freeze({
    schema_version: "StrategyMembershipEvaluation/v1" as const,
    evaluation_id: `evaluation.strategy-membership.${evaluationId}`,
    denominator_ref: denominatorRef,
    observation_ref: observationRef,
    verdict: normalized.length === 0 ? "pass" as const : "fail" as const,
    findings: normalized,
    positive_decision_accounting: Object.freeze({
      declared,
      passed: declared - failedDecisions.size,
      failed: failedDecisions.size,
      unaccounted: 0 as const,
    }),
    portable_claim: "owner-bound-current-data-only-strategy-membership" as const,
    authority_effect: "none" as const,
  });
};
