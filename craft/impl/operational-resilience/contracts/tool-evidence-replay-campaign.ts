import type {
  ToolEvidenceProfileReplayFamily,
  ToolEvidenceProfileReplayInputs,
} from "./tool-evidence-profile-replay.js";
import type { ToolProfileEvidenceEligibilityReceipt } from "./evidence-eligibility.js";
import type {
  DerivedControlSetResult,
  OperationalObservation,
} from "./operational-evidence.js";

export const TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_ID =
  "domainspec.orodi.tool-evidence-replay-campaign-composer" as const;

export const TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_VERSION =
  "1.0.0-candidate-local" as const;

export type ToolEvidenceReplayCampaignFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type ToolEvidenceReplayCampaignItemInput = Readonly<{
  item_id: string;
  replay_inputs: ToolEvidenceProfileReplayInputs;
  supplied_result_bytes: Uint8Array | string;
  supplied_result_sha256: string;
}>;

export type ToolEvidenceReplayCampaignInputs = Readonly<{
  campaign_id: string;
  evaluated_at: string;
  items: readonly ToolEvidenceReplayCampaignItemInput[];
  authority_effect: "none";
}>;

export type ToolEvidenceReplayCampaignFixture = Readonly<{
  case_id: string;
  campaign_id: string;
  item_case_ids: readonly string[];
}>;

export type ToolEvidenceReplayCampaignFixtureBundle = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-fixture/v1";
  evaluated_at: string;
  campaigns: readonly ToolEvidenceReplayCampaignFixture[];
  authority_effect: "none";
}>;

export type ToolEvidenceReplayCampaignHostileCase = Readonly<{
  case_id: string;
  required_code: string;
}>;

export type ToolEvidenceReplayCampaignHostileCaseBundle = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-hostile-cases/v1";
  cases: readonly ToolEvidenceReplayCampaignHostileCase[];
  authority_effect: "none";
}>;

export type ToolEvidenceReplayCampaignExpectedResultBundle = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-expected-results/v1";
  results: readonly ToolEvidenceReplayCampaignHostileCase[];
  authority_effect: "none";
}>;

export type ToolEvidenceReplayCampaignItemReceipt = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-item-receipt/v1";
  item_id: string;
  replay_id: string;
  profile_id: string;
  profile_version: string;
  family_id: ToolEvidenceProfileReplayFamily;
  binding_id: string;
  invalidation_key_digest: string;
  observation_id: string;
  supplied_result_sha256: string;
  recomputed_result_sha256: string;
  eligibility_decision: "replay-only";
  runtime_admission: "denied";
  referent_trust: "unverified";
  authority_effect: "none";
}>;

export type ToolEvidenceReplayCampaignDerivedPartition = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-derived-partition/v1";
  item_id: string;
  replay_id: string;
  binding_id: string;
  invalidation_key_digest: string;
  derived_result: DerivedControlSetResult;
  authority_effect: "none";
}>;

export type ToolEvidenceReplayCampaignResult = Readonly<{
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-result/v1";
  composer_id: typeof TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_ID;
  composer_version: typeof TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_VERSION;
  evidence_lane: "candidate-local-prototype";
  campaign_id: string;
  evaluated_at: string;
  input_manifest_sha256: string;
  item_receipts: readonly ToolEvidenceReplayCampaignItemReceipt[];
  replay_observations: readonly OperationalObservation[];
  eligibility_receipts: readonly ToolProfileEvidenceEligibilityReceipt[];
  per_binding_derived_results: readonly ToolEvidenceReplayCampaignDerivedPartition[];
  runtime_admitted_observations: readonly [];
  eligible_controls: readonly [];
  verdict: "composed" | "rejected";
  findings: readonly ToolEvidenceReplayCampaignFinding[];
  runtime_admission: "denied";
  referent_trust: "unverified";
  authority_effect: "none";
}>;
