import type { TlcSuccessfulOutcomeClassV1 } from "./tlc-outcome-classification-v1.js";

export type TlaProofRoleV1 = "obligation" | "mutant";

export type TlaExecutionPolicyV1 = Readonly<{
  worker_count: 1;
  fingerprint_index: number | null;
  seed: number | null;
  network_access: "forbidden";
  environment: readonly string[];
}>;

export type TlaCaseV1 = Readonly<{
  case_id: string;
  accounting_id: string;
  proof_role: TlaProofRoleV1;
  module_paths: readonly string[];
  config_path: string;
  spec_name: string;
  expected_class: TlcSuccessfulOutcomeClassV1;
  expected_exit_status: number;
  expected_property: string | null;
  required_trace_markers: readonly string[];
  finding_code: string | null;
  timeout_ms: 120_000;
  output_limit_bytes: number;
  state_limit: number;
}>;

export type TlaCaseManifestV1 = Readonly<{
  schema_version: "TlaCaseManifest/v1";
  manifest_id: string;
  corpus_id: string;
  corpus_version: string;
  model_bundle_sha256: string;
  execution_policy: TlaExecutionPolicyV1;
  cases: readonly TlaCaseV1[];
  claim_ceiling: string;
  authority_effect: "none";
}>;
