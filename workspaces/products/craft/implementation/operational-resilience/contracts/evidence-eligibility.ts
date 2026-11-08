import type { LegacyV1NormalizationResult } from "./legacy-v1-adapter.js";
import type { ToolEvidenceProfileNormalizationResult } from "./tool-evidence-profile-replay.js";
import type {
  AuthorityEffect,
  ControlReceipt,
  DerivedControlSetResult,
  EvaluationBinding,
  EvidenceLane,
  FoundationalControlId,
  OperationalObservation,
} from "./operational-evidence.js";

export const EVIDENCE_ELIGIBILITY_DECISIONS = Object.freeze([
  "replay-only",
  "runtime-eligible",
  "rejected",
] as const);

export type EvidenceEligibilityDecision =
  (typeof EVIDENCE_ELIGIBILITY_DECISIONS)[number];

export type LegacyV1EligibilityEvaluationContext = Readonly<{
  binding: EvaluationBinding;
  controls: readonly ControlReceipt[];
}>;

export type LegacyV1EligibilityReplayRequest = Readonly<{
  schema_version: "domainspec.orodi.eligibility-replay-request/v1";
  evidence_lane: EvidenceLane;
  replay_id: string;
  normalizations: readonly LegacyV1NormalizationResult[];
  evaluation_context: LegacyV1EligibilityEvaluationContext;
  evaluated_at: string;
  authority_effect: AuthorityEffect;
}>;

export type EvidenceEligibilityFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type EvidenceEligibilityReceipt = Readonly<{
  schema_version: "domainspec.orodi.evidence-eligibility-receipt/v1";
  observation_id: string;
  source_shape_id: string;
  decision: EvidenceEligibilityDecision;
  eligible_controls: readonly FoundationalControlId[];
  ineligible_controls: readonly FoundationalControlId[];
  reason_codes: readonly string[];
  authority_effect: AuthorityEffect;
}>;

export type EvidenceEligibilityResult = Readonly<{
  schema_version: "domainspec.orodi.evidence-eligibility-result/v1";
  gate_id: "domainspec.orodi.legacy-v1-evidence-eligibility";
  gate_version: "1.0.0-candidate-local";
  evidence_lane: EvidenceLane;
  replay_id: string;
  evaluated_at: string;
  decision: EvidenceEligibilityDecision;
  runtime_admission: "denied";
  replay_observations: readonly OperationalObservation[];
  runtime_admitted_observations: readonly OperationalObservation[];
  eligibility_receipts: readonly EvidenceEligibilityReceipt[];
  derived_result: DerivedControlSetResult | null;
  findings: readonly EvidenceEligibilityFinding[];
  authority_effect: AuthorityEffect;
}>;

export type ToolProfileEvidenceEligibilityEvaluationContext = Readonly<{
  binding: EvaluationBinding;
  controls: readonly ControlReceipt[];
}>;

export type ToolProfileEvidenceEligibilityReceipt = Readonly<{
  schema_version: "domainspec.orodi.tool-profile-evidence-eligibility-receipt/v1";
  observation_id: string;
  profile_id: string;
  family_id: string;
  decision: "replay-only";
  eligible_controls: readonly [];
  ineligible_controls: readonly FoundationalControlId[];
  reason_codes: readonly string[];
  authority_effect: AuthorityEffect;
}>;

export type ToolProfileEvidenceEligibilityResult = Readonly<{
  schema_version: "domainspec.orodi.tool-profile-evidence-eligibility-result/v1";
  gate_id: "domainspec.orodi.tool-profile-replay-evidence-eligibility";
  gate_version: "1.0.0-candidate-local";
  evidence_lane: EvidenceLane;
  replay_id: string;
  profile_id: string;
  profile_version: string;
  family_id: string;
  descriptor_sha256: string;
  normalization_sha256: string;
  evaluated_at: string;
  decision: "replay-only" | "rejected";
  runtime_admission: "denied";
  referent_trust: "unverified";
  replay_observations: readonly OperationalObservation[];
  runtime_admitted_observations: readonly [];
  eligibility_receipts: readonly ToolProfileEvidenceEligibilityReceipt[];
  derived_result: DerivedControlSetResult | null;
  findings: readonly EvidenceEligibilityFinding[];
  authority_effect: AuthorityEffect;
}>;

export type ToolProfileEvidenceEligibilityCandidate = Readonly<{
  normalization: ToolEvidenceProfileNormalizationResult;
  evaluation_context: ToolProfileEvidenceEligibilityEvaluationContext;
  evaluated_at: string;
}>;
