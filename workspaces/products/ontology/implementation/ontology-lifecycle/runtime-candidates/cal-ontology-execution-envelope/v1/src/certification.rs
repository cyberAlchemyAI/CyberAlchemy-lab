//! Deterministic certification harness for disposable execution-target adapters.
//!
//! Certification is product evidence only. It does not admit an adapter or permit live use.

use crate::{
    EXACT_STEP_ORDER, ExecutionEngine, ExecutionFailure, ExecutionStepId, ExecutionTargetAdapter,
    PrototypeTargetBinding,
};
use cal_ontology_lifecycle::canonical_json;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

pub const CERTIFICATION_CANDIDATE_ID: &str =
    "CAL-D65-EPOCH-002-ADAPTER-CERTIFICATION-PROTOTYPE-003";
pub const L1_BASELINE_COMMIT: &str = "5b665f4dc351853bee777f14e56cccdab6cbfb26";
pub const L1_RECEIPT_DIGEST: &str =
    "802b91186fa6c41b21609bfe63428c3466fbc1519033e3692e39cf65fb00e509";

pub const REQUIRED_VECTOR_IDS: [&str; 18] = [
    "CERT-01-BASELINE",
    "CERT-02-CALL-ORDER",
    "CERT-03-BINDING-IDENTITY",
    "CERT-04-LIVE-BINDING",
    "CERT-05-CREDENTIAL-BINDING",
    "CERT-06-PREIMAGE-DRIFT",
    "CERT-07-STAGE-FAILURE",
    "CERT-08-ACTIVATE-FAILURE",
    "CERT-09-MIGRATE-FAILURE",
    "CERT-10-VERIFY-TARGET-FAILURE",
    "CERT-11-CUTOVER-FAILURE",
    "CERT-12-VERIFY-POSTIMAGE-FAILURE",
    "CERT-13-ROLLBACK-FAILURE",
    "CERT-14-VERIFY-ROLLBACK-FAILURE",
    "CERT-15-REPORT-DETERMINISM",
    "CERT-16-INDEPENDENT-FIXTURE",
    "CERT-17-VECTOR-OMISSION",
    "CERT-18-VECTOR-MUTATION",
];

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum CertificationScenario {
    Baseline,
    CallOrder,
    BindingIdentity,
    LiveBinding,
    CredentialBinding,
    PreimageDrift,
    StageFailure,
    ActivateFailure,
    MigrateFailure,
    VerifyTargetFailure,
    CutoverFailure,
    VerifyPostimageFailure,
    RollbackFailure,
    VerifyRollbackFailure,
    ReportDeterminism,
    IndependentFixture,
    VectorOmission,
    VectorMutation,
}

const REQUIRED_SCENARIOS: [CertificationScenario; 18] = [
    CertificationScenario::Baseline,
    CertificationScenario::CallOrder,
    CertificationScenario::BindingIdentity,
    CertificationScenario::LiveBinding,
    CertificationScenario::CredentialBinding,
    CertificationScenario::PreimageDrift,
    CertificationScenario::StageFailure,
    CertificationScenario::ActivateFailure,
    CertificationScenario::MigrateFailure,
    CertificationScenario::VerifyTargetFailure,
    CertificationScenario::CutoverFailure,
    CertificationScenario::VerifyPostimageFailure,
    CertificationScenario::RollbackFailure,
    CertificationScenario::VerifyRollbackFailure,
    CertificationScenario::ReportDeterminism,
    CertificationScenario::IndependentFixture,
    CertificationScenario::VectorOmission,
    CertificationScenario::VectorMutation,
];

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CertificationVector {
    pub vector_id: String,
    pub scenario: CertificationScenario,
    pub expected_execution_result: String,
    pub expected_failure_code: Option<String>,
    pub state_invariant: String,
    pub external_effects: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct VectorOutcome {
    pub vector_id: String,
    pub result: String,
    pub observed_execution_result: String,
    pub failure_code: Option<String>,
    pub observed_call_order: Vec<String>,
    pub preimage_digest: String,
    pub final_state_digest: String,
    pub exact_preimage: bool,
    pub external_effects: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CertificationReportBody {
    pub schema_version: String,
    pub candidate_id: String,
    pub baseline_commit: String,
    pub baseline_receipt_digest: String,
    pub fixture_id: String,
    pub adapter_binding: PrototypeTargetBinding,
    pub vector_set_digest: String,
    pub outcomes: Vec<VectorOutcome>,
    pub observed_call_order: Vec<String>,
    pub preimage_digest: String,
    pub final_state_digest: String,
    pub passed_vectors: usize,
    pub total_vectors: usize,
    pub result: String,
    pub external_effects: bool,
    pub authority_effect: String,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CertificationReport {
    #[serde(flatten)]
    pub body: CertificationReportBody,
    pub report_digest: String,
}

impl CertificationReport {
    pub fn canonical_json(&self) -> Result<String, ExecutionFailure> {
        canonical_json(self).map_err(|error| {
            ExecutionFailure::new("CERTIFICATION_SERIALIZATION_FAILED", error.to_string())
        })
    }
}

/// Factory and observation surface used by the certification harness.
///
/// A fixture is test evidence, not a runtime target binding. The independent-source assertion is
/// paired with a source-level non-delegation check in the public certification contract.
pub trait CertificationFixture {
    type Adapter: ExecutionTargetAdapter;

    fn fixture_id(&self) -> &str;
    fn build(&self, scenario: CertificationScenario) -> Self::Adapter;
    fn state_digest(&self, adapter: &Self::Adapter) -> String;
    fn observed_call_order(&self, adapter: &Self::Adapter) -> Vec<String>;
    fn external_effects(&self, adapter: &Self::Adapter) -> bool;
    fn independently_authored(&self) -> bool;
}

#[derive(Clone, Copy, Debug, Default)]
pub struct CertificationHarness;

impl CertificationHarness {
    pub fn certify_twice<F: CertificationFixture>(
        &self,
        fixture: &F,
        vectors: &[CertificationVector],
    ) -> Result<CertificationReport, ExecutionFailure> {
        validate_vector_set(vectors)?;
        let run_a = self.run_once(fixture, vectors)?;
        let run_b = self.run_once(fixture, vectors)?;
        if run_a != run_b {
            return Err(ExecutionFailure::new(
                "CERTIFICATION_RUN_NONDETERMINISTIC",
                fixture.fixture_id(),
            ));
        }

        let deterministic = meta_outcome("CERT-15-REPORT-DETERMINISM", true);
        let mut outcomes = run_a;
        outcomes.insert(14, deterministic);
        let passed_vectors = outcomes
            .iter()
            .filter(|outcome| outcome.result == "PASS")
            .count();
        let baseline = outcomes
            .first()
            .ok_or_else(|| ExecutionFailure::new("CERTIFICATION_REPORT_EMPTY", "baseline"))?;
        let observed_call_order = baseline.observed_call_order.clone();
        let preimage_digest = baseline.preimage_digest.clone();
        let final_state_digest = baseline.final_state_digest.clone();
        let vector_set_digest = digest_value(&vectors)?;
        let adapter_binding = fixture.build(CertificationScenario::Baseline).binding();
        let external_effects = outcomes.iter().any(|outcome| outcome.external_effects);
        let body = CertificationReportBody {
            schema_version: "cal.d65-adapter-certification-report/v1".to_owned(),
            candidate_id: CERTIFICATION_CANDIDATE_ID.to_owned(),
            baseline_commit: L1_BASELINE_COMMIT.to_owned(),
            baseline_receipt_digest: L1_RECEIPT_DIGEST.to_owned(),
            fixture_id: fixture.fixture_id().to_owned(),
            adapter_binding,
            vector_set_digest,
            outcomes,
            observed_call_order,
            preimage_digest,
            final_state_digest,
            passed_vectors,
            total_vectors: REQUIRED_VECTOR_IDS.len(),
            result: if passed_vectors == REQUIRED_VECTOR_IDS.len() && !external_effects {
                "PASS".to_owned()
            } else {
                "BLOCK".to_owned()
            },
            external_effects,
            authority_effect: "none".to_owned(),
        };
        let report_digest = digest_value(&body)?;
        Ok(CertificationReport {
            body,
            report_digest,
        })
    }

    fn run_once<F: CertificationFixture>(
        &self,
        fixture: &F,
        vectors: &[CertificationVector],
    ) -> Result<Vec<VectorOutcome>, ExecutionFailure> {
        vectors
            .iter()
            .filter(|vector| vector.scenario != CertificationScenario::ReportDeterminism)
            .map(|vector| match vector.scenario {
                CertificationScenario::IndependentFixture => Ok(meta_outcome(
                    &vector.vector_id,
                    fixture.independently_authored(),
                )),
                CertificationScenario::VectorOmission | CertificationScenario::VectorMutation => {
                    Ok(meta_outcome(&vector.vector_id, true))
                }
                _ => self.run_execution_vector(fixture, vector),
            })
            .collect()
    }

    fn run_execution_vector<F: CertificationFixture>(
        &self,
        fixture: &F,
        vector: &CertificationVector,
    ) -> Result<VectorOutcome, ExecutionFailure> {
        let mut adapter = fixture.build(vector.scenario);
        let preimage_digest = fixture.state_digest(&adapter);
        let execution =
            ExecutionEngine.execute(&crate::ExecutionEnvelope::exact_prototype(), &mut adapter);
        let (observed_execution_result, failure_code, trace_exact) = match execution {
            Ok(receipt) => (
                "PASS".to_owned(),
                None,
                receipt
                    .trace
                    .iter()
                    .map(|step| step.step_id)
                    .eq(EXACT_STEP_ORDER),
            ),
            Err(failure) => ("BLOCK".to_owned(), Some(failure.code), true),
        };
        let final_state_digest = fixture.state_digest(&adapter);
        let observed_call_order = fixture.observed_call_order(&adapter);
        let external_effects = fixture.external_effects(&adapter);
        let exact_preimage = preimage_digest == final_state_digest;
        let expected_call_order = canonical_adapter_call_order();
        let call_order_exact = !matches!(
            vector.scenario,
            CertificationScenario::Baseline | CertificationScenario::CallOrder
        ) || observed_call_order == expected_call_order;
        let passed = observed_execution_result == vector.expected_execution_result
            && failure_code == vector.expected_failure_code
            && vector.state_invariant == "exact-preimage"
            && exact_preimage
            && !vector.external_effects
            && !external_effects
            && trace_exact
            && call_order_exact;
        Ok(VectorOutcome {
            vector_id: vector.vector_id.clone(),
            result: if passed { "PASS" } else { "BLOCK" }.to_owned(),
            observed_execution_result,
            failure_code,
            observed_call_order,
            preimage_digest,
            final_state_digest,
            exact_preimage,
            external_effects,
        })
    }
}

pub fn validate_vector_set(vectors: &[CertificationVector]) -> Result<(), ExecutionFailure> {
    if vectors.len() != REQUIRED_VECTOR_IDS.len() {
        return Err(vector_set_failure("vector-count"));
    }
    let unique: BTreeSet<_> = vectors
        .iter()
        .map(|vector| vector.vector_id.as_str())
        .collect();
    if unique.len() != REQUIRED_VECTOR_IDS.len() {
        return Err(vector_set_failure("duplicate-vector"));
    }
    for (position, vector) in vectors.iter().enumerate() {
        let (expected_result, expected_failure) = expected_execution(vector.scenario);
        if vector.vector_id != REQUIRED_VECTOR_IDS[position]
            || vector.scenario != REQUIRED_SCENARIOS[position]
            || vector.expected_execution_result != expected_result
            || vector.expected_failure_code.as_deref() != expected_failure
            || vector.state_invariant != "exact-preimage"
            || vector.external_effects
        {
            return Err(vector_set_failure(&vector.vector_id));
        }
    }
    Ok(())
}

fn expected_execution(scenario: CertificationScenario) -> (&'static str, Option<&'static str>) {
    match scenario {
        CertificationScenario::Baseline | CertificationScenario::CallOrder => ("PASS", None),
        CertificationScenario::BindingIdentity
        | CertificationScenario::LiveBinding
        | CertificationScenario::CredentialBinding => {
            ("BLOCK", Some("PROTOTYPE_TARGET_BOUNDARY_VIOLATION"))
        }
        CertificationScenario::PreimageDrift => ("BLOCK", Some("TARGET_PREIMAGE_MISMATCH")),
        CertificationScenario::StageFailure
        | CertificationScenario::ActivateFailure
        | CertificationScenario::MigrateFailure
        | CertificationScenario::VerifyTargetFailure
        | CertificationScenario::CutoverFailure
        | CertificationScenario::VerifyPostimageFailure
        | CertificationScenario::RollbackFailure
        | CertificationScenario::VerifyRollbackFailure => {
            ("BLOCK", Some("INJECTED_CERTIFICATION_FAILURE"))
        }
        CertificationScenario::ReportDeterminism
        | CertificationScenario::IndependentFixture
        | CertificationScenario::VectorOmission
        | CertificationScenario::VectorMutation => ("META", None),
    }
}

fn canonical_adapter_call_order() -> Vec<String> {
    EXACT_STEP_ORDER
        .iter()
        .map(|step| match step {
            ExecutionStepId::Preflight => "preflight",
            ExecutionStepId::CapturePreimage => "capture-preimage",
            ExecutionStepId::Stage => "stage",
            ExecutionStepId::Activate => "activate",
            ExecutionStepId::Migrate => "migrate",
            ExecutionStepId::VerifyTarget => "verify-target",
            ExecutionStepId::Cutover => "cutover",
            ExecutionStepId::VerifyPostimage => "verify-postimage",
            ExecutionStepId::Rollback => "rollback",
            ExecutionStepId::VerifyRollback => "verify-rollback",
        })
        .map(str::to_owned)
        .collect()
}

fn meta_outcome(vector_id: &str, passed: bool) -> VectorOutcome {
    VectorOutcome {
        vector_id: vector_id.to_owned(),
        result: if passed { "PASS" } else { "BLOCK" }.to_owned(),
        observed_execution_result: "META".to_owned(),
        failure_code: None,
        observed_call_order: Vec::new(),
        preimage_digest: String::new(),
        final_state_digest: String::new(),
        exact_preimage: true,
        external_effects: false,
    }
}

fn vector_set_failure(detail: &str) -> ExecutionFailure {
    ExecutionFailure::new("CERTIFICATION_VECTOR_SET_MISMATCH", detail)
}

fn digest_value<T: Serialize>(value: &T) -> Result<String, ExecutionFailure> {
    let serialized = canonical_json(value).map_err(|error| {
        ExecutionFailure::new("CERTIFICATION_SERIALIZATION_FAILED", error.to_string())
    })?;
    Ok(format!("{:x}", Sha256::digest(serialized.as_bytes())))
}
