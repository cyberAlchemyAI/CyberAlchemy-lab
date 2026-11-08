use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};
use serde_json::Value;

pub const STAGE_IDS: [&str; 13] = [
    "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12",
];

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Route {
    Executable,
    Theorem,
    MultiProvider,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum StageState {
    Passed,
    Failed,
    Blocked,
    Indeterminate,
    NotApplicable,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum RefLocation {
    Repository,
    Host,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExactRef {
    pub path: String,
    pub sha256: String,
    pub size_bytes: u64,
    pub location: RefLocation,
    pub current: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StageRequirement {
    pub stage_id: String,
    pub required: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct IsolationSpec {
    pub mechanism: String,
    pub unshare_ref: ExactRef,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeSpec {
    pub executable_ref: ExactRef,
    pub tool_refs: Vec<ExactRef>,
    pub argv: Vec<String>,
    pub working_directory: String,
    pub environment: BTreeMap<String, String>,
    pub timeout_ms: u64,
    pub max_output_bytes: u64,
    pub network: String,
    pub isolation: IsolationSpec,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CheckSpec {
    pub check_id: String,
    pub provider_id: String,
    pub runtime: RuntimeSpec,
    pub input_ref: ExactRef,
    pub expected_output: Value,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct MutationSpec {
    pub mutant_id: String,
    pub check_id: String,
    pub input_ref: ExactRef,
    pub expected_output: Value,
    pub expected_rejection_code: String,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CompositionSpec {
    pub mode: String,
    pub provider_ids: Vec<String>,
    pub compare_fields: Vec<String>,
    pub comparability_refs: Vec<ExactRef>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct VerifierSpec {
    pub executable_ref: ExactRef,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProducerSpec {
    pub executable_ref: ExactRef,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EnforcementProfile {
    pub schema_version: String,
    pub profile_id: String,
    pub subject: String,
    pub route: Route,
    pub stages: Vec<StageRequirement>,
    pub semantic_refs: Vec<ExactRef>,
    pub obligation_ids: Vec<String>,
    pub obligation_denominator: usize,
    pub binding_refs: Vec<ExactRef>,
    pub checks: Vec<CheckSpec>,
    pub mutations: Vec<MutationSpec>,
    pub composition: CompositionSpec,
    pub producer: ProducerSpec,
    pub verifier: VerifierSpec,
    pub repetitions: usize,
    pub claim_ceiling: String,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProviderObservation {
    pub check_id: String,
    pub provider_id: String,
    pub exit_code: Option<i32>,
    pub timed_out: bool,
    pub stdout_sha256: String,
    pub stderr_sha256: String,
    pub output: Value,
    pub matched_expected: bool,
    pub error_code: Option<String>,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct MutationObservation {
    pub mutant_id: String,
    pub check_id: String,
    pub expected_rejection_code: String,
    pub observations: Vec<ProviderObservation>,
    pub killed_for_declared_cause: bool,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct StageReceipt {
    pub schema_version: String,
    pub stage_id: String,
    pub profile_id: String,
    pub route: Route,
    pub state: StageState,
    pub input_stage_receipt_digests: BTreeMap<String, String>,
    pub evidence_refs: Vec<ExactRef>,
    pub reason_codes: Vec<String>,
    pub residue: Vec<String>,
    pub details: BTreeMap<String, Value>,
    pub claim_ceiling: String,
    pub authority_effect: String,
    pub receipt_payload_digest: String,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationReceipt {
    pub schema_version: String,
    pub verdict: String,
    pub verified_stage_ids: Vec<String>,
    pub all_refs_current: bool,
    pub replay_equal: bool,
    pub recomputed_aggregate_state: StageState,
    pub reason_codes: Vec<String>,
    pub authority_effect: String,
    pub receipt_payload_digest: String,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Denominator {
    pub stages: usize,
    pub checks: usize,
    pub mutations: usize,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProvisionalBundle {
    pub schema_version: String,
    pub profile: EnforcementProfile,
    pub profile_ref: ExactRef,
    pub stage_receipts: Vec<StageReceipt>,
    pub producer_aggregate_state: StageState,
    pub denominator: Denominator,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AggregateReceipt {
    pub schema_version: String,
    pub receipt_id: String,
    pub profile_id: String,
    pub route: Route,
    pub profile_ref: ExactRef,
    pub stage_receipts: Vec<StageReceipt>,
    pub aggregate_state: StageState,
    pub all_required_stages_present: bool,
    pub denominator: Denominator,
    pub verification_receipt: VerificationReceipt,
    pub evidence_payload_digest: String,
    pub authority_effect: String,
    pub release_admission: String,
    pub claim_ceiling: String,
}
