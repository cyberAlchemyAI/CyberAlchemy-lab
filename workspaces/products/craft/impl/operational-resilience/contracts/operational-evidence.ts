export const CONTROL_IDS = Object.freeze([
  "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
  "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
] as const);

export type ControlId = (typeof CONTROL_IDS)[number];

export const FOUNDATIONAL_CONTROL_IDS = Object.freeze([
  "C01", "C05", "C11", "C12", "C14", "C15",
] as const);

export type FoundationalControlId = (typeof FOUNDATIONAL_CONTROL_IDS)[number];

export const EVIDENCE_STATES = Object.freeze([
  "passed",
  "failed",
  "missing",
  "invalid",
  "inconclusive",
  "stale",
  "not-run",
] as const);

export type EvidenceState = (typeof EVIDENCE_STATES)[number];
export type EvidenceLane = "candidate-local-prototype";
export type AuthorityEffect = "none";

export type BoundReference = Readonly<{
  ref: string;
  version: string;
  sha256: string;
}>;

export type EvaluationOwners = Readonly<{
  semantic: string;
  integration: string;
  evidence: string;
  privacy: string;
  evaluator: string;
}>;

export type CandidateProfileBinding = Readonly<{
  role: string;
  profile_id: string;
  version: string;
  sha256: string;
  status: "candidate-local";
}>;

export type PolicyBinding = Readonly<{
  role: string;
  policy_id: string;
  version: string;
  sha256: string;
  enabled: true;
}>;

export type EvaluationBinding = Readonly<{
  schema_version: "domainspec.orodi.evaluation-binding/v1";
  binding_id: string;
  subject: BoundReference;
  environment: BoundReference;
  stable_artifact: BoundReference;
  candidate_artifact: BoundReference;
  configuration: BoundReference;
  topology: BoundReference;
  fixture: BoundReference;
  evaluator: BoundReference;
  receipt_schema: BoundReference;
  owners: EvaluationOwners;
  profiles: readonly CandidateProfileBinding[];
  policies: readonly PolicyBinding[];
  invalidation_key_digest: string;
  created_at: string;
  expires_at: string;
}>;

export type TelemetryAccounting = Readonly<{
  offered: number;
  queued: number;
  exported: number;
  rejected: number;
  dropped: number;
  pending: number;
  partial_success: number;
}>;

export type OperationalObservation = Readonly<{
  schema_version: "domainspec.orodi.observation/v1";
  observation_id: string;
  plane: "product" | "workflow";
  kind: "metric" | "trace" | "log" | "health" | "deployment-effect" | "rollback-effect";
  mode: "simulation" | "live";
  correlation_id: string;
  attributes: Readonly<Record<string, string>>;
  attribute_allowlist: readonly string[];
  cardinality: Readonly<{ observed: number; budget: number }>;
  telemetry: TelemetryAccounting;
  deployment_effect: boolean;
  independently_observed: boolean;
  observed_at: string;
  invalidation_key_digest: string;
}>;

export type ControlReceipt = Readonly<{
  schema_version: "domainspec.orodi.control-receipt/v1";
  control_id: ControlId;
  state: EvidenceState;
  observation_refs: readonly string[];
  evaluated_at: string;
  expires_at: string;
  invalidation_key_digest: string;
  authority_effect: AuthorityEffect;
}>;

export type EvaluationClaim = Readonly<{
  claim_id: string;
  required_controls: readonly ControlId[];
}>;

export type OperationalEvaluationBundle = Readonly<{
  schema_version: "domainspec.orodi.evaluation-bundle/v1";
  evidence_lane: EvidenceLane;
  binding: EvaluationBinding;
  observations: readonly OperationalObservation[];
  controls: readonly ControlReceipt[];
  claim: EvaluationClaim;
  authority_effect: AuthorityEffect;
}>;

export type EvaluationFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type ControlStateEntry = Readonly<{
  control_id: ControlId;
  state: EvidenceState;
}>;

export type OperationalEvaluationResult = Readonly<{
  schema_version: "domainspec.orodi.evaluation-result/v1";
  validator_id: "domainspec.orodi.generic-validator";
  validator_version: "1.0.0-candidate-local";
  evidence_lane: EvidenceLane;
  binding_id: string;
  claim_id: string;
  evaluated_at: string;
  verdict: "pass" | "reject";
  claim_state: EvidenceState;
  required_control_states: readonly ControlStateEntry[];
  findings: readonly EvaluationFinding[];
  authority_effect: AuthorityEffect;
}>;

export type DerivedControlFinding = Readonly<{
  code: string;
  detail: string;
}>;

export type DerivedControlReceipt = Readonly<{
  schema_version: "domainspec.orodi.derived-control-receipt/v1";
  control_id: FoundationalControlId;
  state: EvidenceState;
  evaluator_id: string;
  rule_version: "1.0.0-candidate-local";
  observation_refs: readonly string[];
  evaluated_at: string;
  expires_at: string;
  invalidation_key_digest: string;
  findings: readonly DerivedControlFinding[];
  authority_effect: AuthorityEffect;
}>;

export type DerivedControlMismatch = Readonly<{
  control_id: FoundationalControlId;
  claimed_state: EvidenceState | null;
  derived_state: EvidenceState;
  code: string;
}>;

export type DerivedControlSetResult = Readonly<{
  schema_version: "domainspec.orodi.derived-control-set-result/v1";
  validator_id: "domainspec.orodi.foundational-derived-validator";
  validator_version: "1.0.0-candidate-local";
  evidence_lane: EvidenceLane;
  binding_id: string;
  evaluated_at: string;
  verdict: "pass" | "reject";
  comparison: "match" | "mismatch" | "unavailable";
  derived_controls: readonly DerivedControlReceipt[];
  mismatches: readonly DerivedControlMismatch[];
  findings: readonly EvaluationFinding[];
  authority_effect: AuthorityEffect;
}>;
