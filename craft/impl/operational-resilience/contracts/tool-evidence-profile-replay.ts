import type {
  RoleBoundReference,
  ToolEvidenceProfile,
  ToolEvidenceProfileAttributePolicy,
  ToolEvidenceProfileFamily,
  ToolEvidenceProfileFamilyInventory,
  ToolEvidenceProfileFinding,
  ToolEvidenceProfileReferentInventory,
  ToolEvidenceProfileValidationResult,
} from "./tool-evidence-profile.js";
import type {
  EvaluationBinding,
  OperationalObservation,
} from "./operational-evidence.js";
import type {
  ToolProfileEvidenceEligibilityEvaluationContext,
  ToolProfileEvidenceEligibilityResult,
} from "./evidence-eligibility.js";

export type ToolEvidenceProfileNormalizerInput = Readonly<{
  replay_id: string;
  profile: ToolEvidenceProfile;
  fixture: ToolEvidenceProfileReplayFixture;
  selected_value: unknown;
  selected_value_sha256: string;
  registry_entry: ToolEvidenceProfileNormalizerRegistryEntry;
}>;

export type ToolEvidenceProfileReplayExpectedResult = Readonly<{
  case_id: string;
  expected_code: string;
}>;

export type ToolEvidenceProfileReplayTestContext = Readonly<{
  context_id: string;
  family_id: ToolEvidenceProfileReplayFamily;
  evaluation_context: ToolProfileEvidenceEligibilityEvaluationContext;
}>;

export type ToolEvidenceProfileReplayTestContextBundle = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-replay-contexts/v1";
  contexts: readonly ToolEvidenceProfileReplayTestContext[];
  authority_effect: "none";
}>;

export type ToolProfileNormalizerCandidateValidation = Readonly<{
  observation: OperationalObservation | null;
  findings: readonly ToolEvidenceProfileFinding[];
}>;

export type ToolProfileEligibilityCandidate = Readonly<{
  normalization: ToolEvidenceProfileNormalizationResult;
  evaluation_context: ToolProfileEvidenceEligibilityEvaluationContext;
  evaluated_at: string;
}>;

export type ToolProfileReplayBinding = EvaluationBinding;

export type ToolEvidenceProfileNormalizerOutput = Readonly<{
  observation: OperationalObservation;
  selected_value_sha256: string;
}>;

export type ToolEvidenceProfileReplayGoldenCase = Readonly<{
  case_id: string;
  family_id: ToolEvidenceProfileReplayFamily;
  descriptor_ref: string;
  context_id: string;
  fixture: ToolEvidenceProfileReplayFixture;
  expected_observation_kind: OperationalObservation["kind"];
}>;

export type ToolEvidenceProfileReplayCaseBundle = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-replay-cases/v1";
  evaluated_at: string;
  cases: readonly ToolEvidenceProfileReplayGoldenCase[];
  authority_effect: "none";
}>;

export type ToolEvidenceProfileReplayHostileCase = Readonly<{
  case_id: string;
  surface: "replay" | "registry" | "normalizer-output" | "eligibility";
  expected_code: string;
}>;
export const TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES = Object.freeze([
  "telemetry",
  "health-failure",
  "workload",
  "fault",
  "canary-analysis",
  "deployment-observation",
  "rollback-observation",
] as const);

export type ToolEvidenceProfileReplayFamily =
  (typeof TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES)[number];

export type ToolEvidenceProfileReplayFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type ToolEvidenceProfileReplayFixture = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-replay-fixture/v1";
  fixture_id: string;
  profile_id: string;
  profile_version: string;
  family_id: ToolEvidenceProfileFamily;
  producer: RoleBoundReference;
  source_bytes_utf8: string;
  source_sha256: string;
  replayed_at: string;
  invalidation_key_digest: string;
  execution_mode: "offline-fixture-only";
  runtime_admission: "denied";
  authority_effect: "none";
}>;

export type ToolEvidenceProfileNormalizerRegistryEntry = Readonly<{
  family_id: ToolEvidenceProfileReplayFamily;
  normalizer: Readonly<{
    ref: "orodi://normalizer/pure-profile/v1";
    version: "1.0.0";
    sha256: "d6a45d4e99806fca19e5d683d9fc0c7b216f9d57706a87ae5112b32dbabe92ca";
  }>;
  normalizer_id: string;
  normalizer_version: "1.0.0-candidate-local";
  observation_kind: OperationalObservation["kind"];
}>;

export type ToolEvidenceProfileNormalizationResult = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-normalization-result/v1";
  normalizer_id: string;
  normalizer_version: "1.0.0-candidate-local";
  registry_entry: ToolEvidenceProfileNormalizerRegistryEntry | null;
  replay_id: string;
  profile_id: string;
  profile_version: string;
  family_id: string;
  fixture_id: string;
  descriptor_sha256: string;
  wp5_result_sha256: string;
  source_sha256: string;
  selected_value_sha256: string | null;
  invalidation_key_digest: string;
  replayed_at: string;
  verdict: "normalized" | "rejected";
  observations: readonly OperationalObservation[];
  findings: readonly ToolEvidenceProfileReplayFinding[];
  runtime_admission: "denied";
  referent_trust: "unverified";
  authority_effect: "none";
}>;

export type ToolEvidenceProfileReplayInputs = Readonly<{
  replay_id: string;
  descriptor: Uint8Array | string;
  family_inventory: Uint8Array | string;
  attribute_policy: Uint8Array | string;
  referent_inventory: Uint8Array | string;
  wp5_validation_result: Uint8Array | string;
  fixture: Uint8Array | string;
  evaluation_context: Uint8Array | string;
  evaluated_at: string;
}>;

export type ToolEvidenceProfileReplayInputDigests = Readonly<{
  descriptor_sha256: string;
  family_inventory_sha256: string;
  attribute_policy_sha256: string;
  referent_inventory_sha256: string;
  wp5_result_sha256: string;
  fixture_sha256: string;
  evaluation_context_sha256: string;
}>;

export type ToolEvidenceProfileReplayResult = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-profile-replay-result/v1";
  replayer_id: "domainspec.orodi.tool-evidence-profile-replayer";
  replayer_version: "1.0.0-candidate-local";
  evidence_lane: "candidate-local-prototype";
  replay_id: string;
  evaluated_at: string;
  input_digests: ToolEvidenceProfileReplayInputDigests;
  wp5_validation: ToolEvidenceProfileValidationResult;
  normalization: ToolEvidenceProfileNormalizationResult;
  eligibility: ToolProfileEvidenceEligibilityResult | null;
  verdict: "replayed" | "rejected";
  runtime_admission: "denied";
  referent_trust: "unverified";
  findings: readonly ToolEvidenceProfileReplayFinding[];
  authority_effect: "none";
}>;

export type DecodedToolEvidenceProfileReplayInputs = Readonly<{
  descriptor: ToolEvidenceProfile;
  family_inventory: ToolEvidenceProfileFamilyInventory;
  attribute_policy: ToolEvidenceProfileAttributePolicy;
  referent_inventory: ToolEvidenceProfileReferentInventory;
  wp5_validation_result: ToolEvidenceProfileValidationResult;
  fixture: ToolEvidenceProfileReplayFixture;
  evaluation_context: ToolProfileEvidenceEligibilityEvaluationContext;
}>;
